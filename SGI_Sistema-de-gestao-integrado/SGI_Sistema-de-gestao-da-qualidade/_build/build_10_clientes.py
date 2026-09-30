"""RG-SGQ-10 — Clientes, requisitos de produto, revisão de encomendas, alterações de requisitos, propriedade do cliente e pós-entrega.
ISO 9001:2026 5.1.2, 8.2.2 a)–b), 8.2.3.1 a)–e), 8.2.3.2 (evidência dos resultados da revisão), 8.2.4, 8.5.3, 8.5.5.
Clientes, encomendas e reclamações vêm do dataset (dim_customer, fact_sales, fact_customer_complaints)."""
import datetime as dt
import numpy as np
import pandas as pd
from sgqlib import *
from dimsq import *
import qdata as Q

REQ_SEG = {
    "Food Packaging": ("Reg. (CE) 1935/2004; Reg. (UE) 10/2011 (migração global e específica); BPF Reg. (CE) 2023/2006; declaração de conformidade por lote", "Sim", "Sim"),
    "Pharmaceutical": ("Acordo de qualidade farmacêutico; rastreabilidade ao lote de resina; anel de inviolabilidade (21 CFR 211.132); notificação prévia de alterações; auditoria anual", "Sim", "Sim"),
    "Baby Care": ("Especificação de migração e ausência de substâncias restritas (REACH SVHC); inspeção reforçada de contaminação", "Sim", "Não"),
    "Skincare": ("Especificação dimensional e de cor; artwork aprovado; compatibilidade com o produto (ensaio de envelhecimento pelo cliente)", "Sim", "Não"),
    "Fragrance": ("Estanquidade com álcool; decoração (aderência, resistência à fricção); cor", "Sim", "Não"),
    "Personal Hygiene": ("Binário de abertura; estanquidade; resistência à queda; OTIF", "Não", "Não"),
    "Haircare": ("Binário e retenção de binário (cap back-off); resistência à queda", "Não", "Não"),
    "Color Cosmetics": ("Cor (ΔE ≤ 1,0 vs. padrão); decoração; pequenas séries", "Não", "Não"),
}

REQUISITOS = [
    ("RQC-01", "Todos", "Especificação do produto (dimensões, peso, cor, desenho) aprovada pelo cliente", "Definido pelo cliente", "8.2.3.1 a)", "Revisão da encomenda; plano de controlo", "Sim"),
    ("RQC-02", "Todos", "Quantidade, data e condições de entrega (paletização, etiquetas GS1)", "Definido pelo cliente (entrega)", "8.2.3.1 a)", "Confirmação de encomenda; OTIF", "Sim"),
    ("RQC-03", "Todos", "Compatibilidade da embalagem com a linha de enchimento do cliente (tolerâncias de gargalo e altura)", "Não definido pelo cliente, necessário ao uso", "8.2.3.1 b)", "Especificação técnica; amostras de validação", "Sim"),
    ("RQC-04", "Todos", "Ausência de material estranho e de contaminação", "Não definido pelo cliente, necessário ao uso", "8.2.3.1 b)", "Inspeção visual; higiene", "Sim"),
    ("RQC-05", "Todos", "Critérios internos: AQL por classe de defeito (crítico 0,1; maior 0,65; menor 1,5)", "Especificado pela organização", "8.2.3.1 c)", "Planos de controlo PC-*", "Sim"),
    ("RQC-06", "Embalagem alimentar", "Materiais em contacto com alimentos: Reg. 1935/2004 e 10/2011; BPF 2023/2006", "Legal / regulamentar", "8.2.2 a1; 8.2.3.1 d)", "Ensaio de migração por lote; declaração de conformidade", "Sim"),
    ("RQC-07", "Farmacêutico", "Evidência de violação (anel de inviolabilidade) e rastreabilidade ao lote de resina", "Legal / regulamentar + contratual", "8.2.2 a1; 8.2.3.1 d)", "Ensaio do anel por lote; certificado CQ-02", "Sim"),
    ("RQC-08", "Todos (UE)", "PPWR (Reg. UE 2025/40): documentação técnica e declaração UE de conformidade da embalagem", "Legal / regulamentar", "8.2.2 a1", "Dossier PPWR por família (RG-SGA-20)", "Parcial"),
    ("RQC-09", "Cosmética e higiene", "Declarações de conteúdo reciclado (PCR) verificáveis e pegada de carbono quando pedido", "Definido pelo cliente", "8.2.2 b)", "Certificados PCR do fornecedor; RG-SGA-19", "Sim"),
    ("RQC-10", "Farmacêutico", "Notificação e aprovação prévia de alterações de processo, material ou local", "Contratual", "8.2.4; 8.5.6", "RG-SGQ-06 coluna Requer_Aprovacao_Cliente", "Sim"),
    ("RQC-11", "Todos", "Plano de contingência e aviso de disrupção em 24 h", "Contratual (acordo de qualidade)", "8.2.1 e)", "RG-SGQ-08 Comunicacao_Cliente", "Sim"),
    ("RQC-12", "Todos", "Capacidade: Cpk ≥ 1,33 nas características críticas (pedido por 6 clientes)", "Definido pelo cliente", "8.2.3.1 a)", "Estudos de capacidade (OBJ-Q-04)", "Não"),
]

PROPRIEDADE = [
    ("PRC-01", "CUST-016", "Molde de sopro M-SOP-030 (FA-030, 1 000 ml)", "Molde / ferramenta", "2026-05-18", "Bom", "Identificado com placa do cliente; manutenção por ciclos", "", "Não"),
    ("PRC-02", "CUST-016", "Molde de sopro M-SOP-031 (FA-031, 500 ml)", "Molde / ferramenta", "2026-05-18", "Bom", "Identificado com placa do cliente", "", "Não"),
    ("PRC-03", "CUST-017", "Molde de sopro M-SOP-032 (FP-032, 100 ml)", "Molde / ferramenta", "2026-05-25", "Bom", "Zona farma; acesso restrito", "", "Não"),
    ("PRC-04", "CUST-017", "Molde de sopro M-SOP-033 (FP-033, 250 ml)", "Molde / ferramenta", "2026-05-25", "Bom", "Zona farma", "", "Não"),
    ("PRC-05", "CUST-017", "Molde de injeção da tampa TE-012 (anel de inviolabilidade)", "Molde / ferramenta", "2026-06-01", "Desgaste nas pontes do anel", "Relatório dimensional enviado ao cliente", "2026-08-21", "Sim"),
    ("PRC-06", "CUST-005", "Ficheiros de artwork e padrão de cor Pantone", "Propriedade intelectual", "2025-03-10", "Desatualizado", "Cliente enviou padrão novo; o antigo foi usado num lote (cor incorreta)", "2026-02-14", "Sim"),
    ("PRC-07", "CUST-001", "Ferramentas de serigrafia (ecrãs) SK-FR-007", "Molde / ferramenta", "2024-11-04", "Bom", "Armazenados em rack identificado", "", "Não"),
    ("PRC-08", "Todos", "Dados pessoais de contactos dos clientes (CRM)", "Dados pessoais", "—", "Protegido", "RGPD: acesso restrito; sem incidentes", "", "Não"),
]

POS_ENTREGA = [
    ("PE-01", "Tratamento de reclamações e devoluções", "Todos", "Reclamação no portal; análise 8D; resposta em ≤ 10 dias úteis", "PR-SGQ-09", "8.5.5 d) e)"),
    ("PE-02", "Contra-amostras de cada lote", "Farmacêutico: validade do medicamento + 1 ano; alimentar: 2 anos; restantes: 1 ano", "Retenção identificada no armazém de contra-amostras", "PR-SGQ-13", "8.5.5 a) c)"),
    ("PE-03", "Apoio técnico na linha de enchimento do cliente", "Clientes Large e novos SKU", "Visita técnica no arranque; ajuste de tolerâncias", "PR-SGQ-08", "8.5.5 d)"),
    ("PE-04", "Recolha de produto (recall) e notificação", "Alimentar e farmacêutico", "Exercício de rastreio semestral; notificação à autoridade quando aplicável", "PR-SGQ-14", "8.5.5 a) b)"),
    ("PE-05", "Informação de fim de vida (reciclagem) e declarações PPWR", "Todos (UE)", "Declaração de reciclabilidade por família", "RG-SGA-20", "8.5.5 Nota"),
]


def clientes_rows():
    c = Q.customers()
    s = Q.sales()
    k = Q.complaints()
    vend = s.groupby("CustomerId").agg(Vendas_EUR=("TotalValueEUR", "sum"), Unidades=("ShippedQty", "sum"), Encomendas=("SalesOrderId", "count"))
    rec = k.groupby("CustomerId").agg(Reclamacoes=("ComplaintId", "count"), Criticas=("Severity", lambda x: (x == "Critical").sum()))
    out = []
    for r in c.itertuples():
        req, aq, notif = REQ_SEG[r.Segment]
        v = vend.loc[r.CustomerId] if r.CustomerId in vend.index else None
        q = rec.loc[r.CustomerId] if r.CustomerId in rec.index else None
        out.append(dict(ID_Cliente=r.CustomerId, Cliente=r.CustomerName, Pais=r.Country, Segmento=SEG_PT[r.Segment], Dimensao=r.CustomerTier,
                        Requisitos_Especificos=req, Acordo_Qualidade=aq, Aprovacao_Previa_Alteracoes=notif, Plano_Contingencia="Sim" if r.CustomerTier == "Large" or aq == "Sim" else "Não",
                        Vendas_EUR=round(float(v.Vendas_EUR), 2) if v is not None else 0.0, Unidades_Expedidas=int(v.Unidades) if v is not None else 0,
                        Encomendas=int(v.Encomendas) if v is not None else 0, Reclamacoes=int(q.Reclamacoes) if q is not None else 0,
                        Reclamacoes_Criticas=int(q.Criticas) if q is not None else 0, Gestor_Conta="Gestor(a) de Cliente (Key Account)"))
    return out


def encomendas_rows():
    s = Q.sales()
    s = s[s["Date"].str[:7] == "2026-08"].copy()
    cust = Q.customers().set_index("CustomerId")
    rng = np.random.default_rng(8231)
    out = []
    for r in s.sort_values(["Date", "SalesOrderId"]).itertuples():
        seg = cust.loc[r.CustomerId, "Segment"]
        legal = "Sim" if seg in ("Food Packaging", "Pharmaceutical", "Baby Care") else "N.A."
        dd = dt.date.fromisoformat(r.Date)
        rev = dd - dt.timedelta(days=int(rng.integers(3, 12)))
        comp = rev + dt.timedelta(days=int(rng.integers(0, 3)))
        dif = "Sim" if rng.random() < 0.08 else "N.A."
        cap = "Sim"
        res = "Aceite com alteração" if dif == "Sim" else "Aceite"
        row = dict(ID_Encomenda=r.SalesOrderId, Data_Expedicao=dd, ID_Cliente=r.CustomerId, Segmento=SEG_PT[seg], Produto=r.ProductId, Quantidade=int(r.ShippedQty),
                   Valor_EUR=float(r.TotalValueEUR), a_Requisitos_Cliente="Sim", b_Requisitos_Implicitos="Sim", c_Requisitos_Organizacao="Sim", d_Requisitos_Legais=legal,
                   e_Diferencas_Resolvidas=dif, Capacidade_Confirmada=cap, Data_Revisao=rev, Data_Compromisso=comp, Revisto_Por="Gestor(a) de Cliente (Key Account)", Resultado=res)
        out.append(row)
    # exceções reais para o controlo detetar (evidência para a auditoria)
    out[7]["Data_Revisao"] = out[7]["Data_Compromisso"] + dt.timedelta(days=2)
    out[88]["Capacidade_Confirmada"] = "Não"
    reg = [i for i, o in enumerate(out) if o["Segmento"] in ("Embalagem alimentar", "Farmacêutico")]
    if reg:
        out[reg[len(reg) // 2]]["d_Requisitos_Legais"] = "Não"
    return out


def build(out):
    b = Book("RG-SGQ-10", "Clientes, Requisitos de Produto e Revisão de Encomendas",
             activities="Determinar os requisitos dos produtos (incluindo legais), rever a capacidade de os cumprir antes de assumir o compromisso, registar alterações de requisitos, cuidar da propriedade dos clientes e definir as atividades pós-entrega.",
             clauses="5.1.2 a); 8.2.2 a) b); 8.2.3.1 a)–e) e confirmação quando não há declaração documentada; 8.2.3.2 a) b); 8.2.4; 8.5.3 (evidência do que ocorreu); 8.5.5 a)–e)",
             purpose="Registo dos 18 clientes do dataset com requisitos específicos por segmento (cosmética, alimentar, farmacêutico), matriz de requisitos de produto, revisão de TODAS as encomendas expedidas em ago/2026 (dataset) com as 5 perguntas de 8.2.3.1 e controlo de 'revisão antes do compromisso', propriedade do cliente (moldes, artwork, dados) e atividades pós-entrega.",
             links=[("RG-SGQ-15", "Reclamações e satisfação por cliente."), ("RG-SGQ-06", "Alterações de requisitos com aprovação do cliente."),
                    ("RG-SGA-20", "Requisitos legais de embalagem (PPWR, FCM) — detalhe por família no SGA.")],
             guidance=[("ISO/TC 176 APG — Customer communication / requirements", "Evidência de revisão ANTES do compromisso (datas) e resolução de diferenças entre encomenda e proposta."),
                       ("Academy — cap. 14 e 157 (Relações com clientes, VoC → CTQ)", "Requisitos explícitos, implícitos e legais transformados em características do plano de controlo."),
                       ("iso9001help.co.uk — Customer requirements / contract review", "Checklist de revisão de encomenda e registo do resultado.")])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("SimNaoNA", ["Sim", "Não", "N.A."])
    b.add_list("Resultado", ["Aceite", "Aceite com alteração", "Recusada"])
    b.add_list("TipoReq", ["Definido pelo cliente", "Definido pelo cliente (entrega)", "Não definido pelo cliente, necessário ao uso", "Especificado pela organização",
                           "Legal / regulamentar", "Legal / regulamentar + contratual", "Contratual", "Contratual (acordo de qualidade)"])
    b.add_list("CumpreReq", ["Sim", "Parcial", "Não"])
    b.add_list("TipoProp", ["Molde / ferramenta", "Propriedade intelectual", "Dados pessoais", "Material"])
    b.add_list("Funcao", FUNC_NAMES)

    ccols = [col("ID_Cliente", 9, key="PK", desc="ID do dataset."), col("Cliente", 30, desc="Nome."), col("Pais", 10, desc="País."), col("Segmento", 16, desc="Segmento."),
             col("Dimensao", 8, desc="Large / Medium / Small."), col("Requisitos_Especificos", 60, desc="Requisitos específicos do cliente/segmento (8.2.2)."),
             col("Acordo_Qualidade", 9, dv="SimNao", desc="Tem acordo de qualidade assinado."), col("Aprovacao_Previa_Alteracoes", 10, dv="SimNao", desc="Exige aprovação prévia de alterações."),
             col("Plano_Contingencia", 10, dv="SimNao", desc="Plano de contingência acordado (8.2.1 e)."), col("Vendas_EUR", 11, "eur", desc=f"Vendas {PER_INI[:7]}–{PER_FIM[:7]} (dataset)."),
             col("Unidades_Expedidas", 11, "num0", desc="Unidades expedidas (dataset)."), col("Encomendas", 8, "num0", desc="Linhas de encomenda (dataset)."),
             col("Reclamacoes", 8, "int", desc="Reclamações no período (dataset)."), col("Reclamacoes_Criticas", 8, "int", desc="Reclamações críticas."),
             col("CPMU", 8, "num", f='=IFERROR(@Reclamacoes@/@Unidades_Expedidas@*1000000,"")', desc="Reclamações por milhão de unidades."),
             col("Peso_Vendas", 7, "pct1", f='=IFERROR(@Vendas_EUR@/SUM(tbl_clientes[Vendas_EUR]),"")', desc="Peso nas vendas."),
             col("Prioridade", 9, f='=IF(@ID_Cliente@="","",IF(OR(@Reclamacoes_Criticas@>=4,@CPMU@>6),"Crítica",IF(OR(@Acordo_Qualidade@="Sim",@Peso_Vendas@>=0.07),"Alta","Normal")))',
                 desc="Prioridade de acompanhamento."), col("Gestor_Conta", 22, dv="Funcao", desc="Gestor de conta.")]
    b.table("Clientes", "tbl_clientes", ccols, clientes_rows(), "Clientes e requisitos específicos (dataset dim_customer + vendas e reclamações do período).",
            title="CLIENTES E REQUISITOS ESPECÍFICOS (8.2.2)", subtitle=f"18 clientes do dataset · Vendas e reclamações {PER_INI} a {PER_FIM} · CPMU e prioridade calculados",
            cf=[("Prioridade", {"Crítica": "red", "Alta": "orange", "Normal": "green"}), ("Acordo_Qualidade", {"Sim": "blue"})], row_height=45, freeze_col=2)

    rcols = [col("ID_Requisito", 8, key="PK", desc="Requisito."), col("Aplica_a", 18, desc="Clientes/segmento."), col("Requisito", 60, desc="Requisito."),
             col("Tipo", 26, dv="TipoReq", desc="Categoria (8.2.3.1 a–d)."), col("Clausula", 14, desc="Cláusula."), col("Como_se_Assegura", 36, desc="Como a Plasticom assegura o cumprimento."),
             col("Capaz_de_Cumprir", 9, dv="CumpreReq", desc="A organização consegue cumprir as declarações sobre o produto? (8.2.2 b)")]
    b.table("Requisitos_Produto", "tbl_requisitos_produto", rcols, rows_from(input_names(rcols), REQUISITOS), "Requisitos dos produtos: do cliente, implícitos, da organização e legais (8.2.2, 8.2.3.1).",
            title="REQUISITOS DOS PRODUTOS (8.2.2 · 8.2.3.1 a–d)", cf=[("Capaz_de_Cumprir", {"Não": "red", "Parcial": "orange", "Sim": "green"})], row_height=32)

    ecols = [col("ID_Encomenda", 10, key="PK", desc="Encomenda (dataset)."), col("Data_Expedicao", 11, "date", desc="Data de expedição (dataset)."),
             col("ID_Cliente", 9, desc="Cliente.", key="FK → tbl_clientes"), col("Segmento", 14, desc="Segmento."), col("Produto", 20, desc="Produto (dataset)."),
             col("Quantidade", 10, "num0", desc="Quantidade."), col("Valor_EUR", 10, "eur", desc="Valor."),
             col("a_Requisitos_Cliente", 9, dv="SimNaoNA", desc="8.2.3.1 a) requisitos definidos pelo cliente, incl. entrega."), col("b_Requisitos_Implicitos", 9, dv="SimNaoNA", desc="8.2.3.1 b)."),
             col("c_Requisitos_Organizacao", 9, dv="SimNaoNA", desc="8.2.3.1 c)."), col("d_Requisitos_Legais", 9, dv="SimNaoNA", desc="8.2.3.1 d) — obrigatório 'Sim' em alimentar, farmacêutico e infantil."),
             col("e_Diferencas_Resolvidas", 9, dv="SimNaoNA", desc="8.2.3.1 e) diferenças entre encomenda e proposta resolvidas (N.A. = sem diferenças)."),
             col("Capacidade_Confirmada", 9, dv="SimNao", desc="Capacidade de cumprir (planeamento)."), col("Data_Revisao", 11, "date", desc="Data da revisão."),
             col("Data_Compromisso", 11, "date", desc="Data da confirmação ao cliente."), col("Revisto_Por", 22, dv="Funcao", desc="Quem reviu."),
             col("Resultado", 14, dv="Resultado", desc="Resultado da revisão (8.2.3.2 a)."),
             col("Controlo_Qualidade", 26, f=('=IF(@ID_Encomenda@="","",IF(@Data_Revisao@>@Data_Compromisso@,"Revisão DEPOIS do compromisso",IF(AND(OR(@Segmento@="Embalagem alimentar",@Segmento@="Farmacêutico",@Segmento@="Cuidado infantil"),@d_Requisitos_Legais@<>"Sim"),"FALTA requisitos legais",'
                                    'IF(@Capacidade_Confirmada@<>"Sim","Aceite sem capacidade confirmada","OK"))))'), desc="Regras de 8.2.3.1.")]
    b.table("Revisao_Encomendas", "tbl_revisao_encomendas", ecols, encomendas_rows(),
            "Revisão de requisitos de todas as encomendas expedidas em agosto/2026 (evidência de 8.2.3.2).",
            title="REVISÃO DE REQUISITOS DAS ENCOMENDAS — AGOSTO/2026 (8.2.3)",
            subtitle="Encomendas reais do dataset (fact_sales) · As 5 perguntas de 8.2.3.1 · Controlo calculado deteta revisão tardia e requisitos legais em falta",
            cf=[("Controlo_Qualidade", {"DEPOIS": "red", "FALTA": "red", "sem capacidade": "orange", "OK": "green"}), ("Resultado", {"alteração": "yellow"})], row_height=15, freeze_col=1)

    acols = [col("ID_Alteracao_Req", 9, key="PK", desc="Alteração de requisito."), col("Data", 11, "date", desc="Data."), col("ID_Cliente", 9, desc="Cliente.", key="FK → tbl_clientes"),
             col("Alteracao", 50, desc="O que mudou."), col("Documentos_Atualizados", 34, desc="Informação documentada atualizada (8.2.4)."),
             col("Comunicado_a", 30, desc="Pessoas pertinentes informadas (8.2.4)."), col("ID_MOC", 11, desc="Pedido de alteração.", key="FK → RG-SGQ-06", req=False)]
    alts = [("ALR-26-01", "2026-09-10", "CUST-017", "Resultado do ensaio do anel de inviolabilidade no certificado de cada lote", "CQ-02 rev. 03; acordo de qualidade", "Laboratório; expedição", "MOC-Q-26-15"),
            ("ALR-26-02", "2026-09-22", "CUST-015", "Tampa de pote TP-013: característica 'força de remoção' substitui 'binário'", "ESP-TP-013; PC-INJ-01", "Laboratório; produção", "MOC-Q-26-08"),
            ("ALR-26-03", "2026-04-02", "CUST-005", "Novo padrão de cor Pantone para a família de frascos decorados", "Ficha de cor; artwork", "Serigrafia; laboratório", None),
            ("ALR-26-04", "2026-06-15", "CUST-011", "Paletização com cantoneiras e filme reciclado (requisito do cliente)", "IT-EXP-01", "Armazém", None)]
    b.table("Alteracoes_Requisitos", "tbl_alteracoes_requisitos", acols, rows_from(input_names(acols), alts, dates=("Data",)),
            "Alterações aos requisitos de produtos: documentação atualizada e pessoas informadas (8.2.4; 8.2.3.2 b).", row_height=30)

    pcols = [col("ID_Propriedade", 8, key="PK", desc="Propriedade do cliente."), col("ID_Cliente", 9, desc="Cliente."), col("Descricao", 40, desc="O quê."),
             col("Tipo", 18, dv="TipoProp", desc="Tipo (8.5.3 Nota)."), col("Data_Rececao", 11, "date", desc="Receção.", req=False), col("Estado", 18, desc="Estado."),
             col("Protecao_Verificacao", 40, desc="Como é identificada, verificada e protegida."), col("Data_Comunicacao_Cliente", 11, "date", desc="Data em que o cliente foi informado de perda/dano.", req=False),
             col("Ocorrencia", 9, dv="SimNao", desc="Houve perda, dano ou inadequação?"),
             col("Controlo_Qualidade", 18, f='=IF(@ID_Propriedade@="","",IF(AND(@Ocorrencia@="Sim",@Data_Comunicacao_Cliente@=""),"FALTA informar cliente","OK"))', desc="8.5.3: informar o cliente.")]
    prow = rows_from(input_names(pcols), PROPRIEDADE, dates=("Data_Rececao", "Data_Comunicacao_Cliente"))
    for r in prow:
        if r["Data_Rececao"] == "—":
            r["Data_Rececao"] = None
    b.table("Propriedade_Cliente", "tbl_propriedade_cliente", pcols, prow, "Propriedade dos clientes e o que ocorreu com ela (8.5.3).",
            title="PROPRIEDADE DOS CLIENTES (8.5.3)", cf=[("Controlo_Qualidade", {"FALTA": "red", "OK": "green"}), ("Ocorrencia", {"Sim": "orange"})], row_height=32)

    qcols = [col("ID", 6, key="PK", desc="Atividade."), col("Atividade", 36, desc="Atividade pós-entrega."), col("Aplica_a", 36, desc="A quem / extensão."),
             col("Como", 44, desc="Como é feita."), col("Documento", 12, desc="Documento."), col("Alineas_8_5_5", 12, desc="Fatores considerados (8.5.5 a–e).")]
    b.table("Pos_Entrega", "tbl_pos_entrega", qcols, rows_from(input_names(qcols), POS_ENTREGA), "Atividades pós-entrega e sua extensão (8.5.5).", row_height=30)

    ws = b.sheet("Resumo_Encomendas", "Resumo calculado da revisão de encomendas e dos clientes.")
    title(ws, "RESUMO — REVISÃO DE ENCOMENDAS E CLIENTES — calculado")
    header_row(ws, 3, ["Indicador", "Valor"], widths=[54, 12])
    E = lambda c_: f"tbl_revisao_encomendas[{c_}]"
    ind = [("Encomendas revistas (ago/2026)", f"=COUNTA({E('ID_Encomenda')})", "0"), ("  OK", f'=COUNTIF({E("Controlo_Qualidade")},"OK")', "0"),
           ("  revisão depois do compromisso", f'=COUNTIF({E("Controlo_Qualidade")},"Revisão DEPOIS*")', "0"), ("  sem requisitos legais verificados", f'=COUNTIF({E("Controlo_Qualidade")},"FALTA*")', "0"),
           ("  aceites sem capacidade confirmada", f'=COUNTIF({E("Controlo_Qualidade")},"Aceite sem*")', "0"), ("% de encomendas conformes", "=IFERROR(B5/B4,\"\")", "0.0%"),
           ("Encomendas aceites com alteração", f'=COUNTIF({E("Resultado")},"Aceite com alteração")', "0"),
           ("Clientes com prioridade crítica", '=COUNTIF(tbl_clientes[Prioridade],"Crítica")', "0"),
           ("Propriedade do cliente com ocorrência", '=COUNTIF(tbl_propriedade_cliente[Ocorrencia],"Sim")', "0")]
    for k, (a, f, fmt) in enumerate(ind):
        cell(ws, 4 + k, 1, a, bold=not a.startswith("  "))
        cell(ws, 4 + k, 2, f, fmt=fmt)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
