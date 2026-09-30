"""RG-SGQ-12 — Fornecedores externos: aprovação, tipo e extensão do controlo, desempenho mensal, reavaliação e reclamações (SCAR).
ISO 9001:2026 8.4.1 (critérios de avaliação, seleção, monitorização do desempenho e reavaliação — evidência), 8.4.2 a)–d), 8.4.3 a)–f), 9.1.3 g).
Desempenho a partir do dataset: fact_raw_material_lot_disposition (receções) e fact_supplier_complaints (SCAR)."""
import datetime as dt
import pandas as pd
from sgqlib import *
from dimsq import *
import qdata as Q

EXTERNOS = [
    ("EXT-LAB-01", "Laboratório de calibração acreditado (IPAC L0045/L0112/L0203)", "Portugal", "Calibração de equipamentos", "Serviço", "8.4.1 c) processo externo",
     "Acreditação ISO/IEC 17025 com âmbito adequado; certificados com incerteza", "Verificação de cada certificado (erro + U ≤ EMA)", "ISO/IEC 17025", 95, 100),
    ("EXT-LAB-02", "Laboratório de ensaios de migração acreditado", "Espanha", "Ensaios de migração de confirmação (FCM)", "Serviço", "8.4.1 c) processo externo",
     "Acreditação 17025 para EN 1186 e simulantes", "Revisão técnica do relatório", "ISO/IEC 17025", 95, 100),
    ("EXT-MOL-01", "Ferramentaria (construção e reforma de moldes)", "Portugal (Marinha Grande)", "Moldes novos e reformas (M-SOP-007, M-INJ-012)", "Serviço", "8.4.1 c) processo externo",
     "Capacidade técnica; relatório dimensional; prazos", "Primeira peça (FAI) e capacidade antes da aceitação", "ISO 9001", 80, 90),
    ("EXT-TRP-01", "Transportadora rodoviária", "Portugal", "Transporte para clientes ibéricos e UE", "Serviço", "8.4.1 b) fornecido diretamente ao cliente",
     "Cumprimento de janelas; manuseamento; limpeza da caixa (alimentar)", "Reclamações de transporte; checklist de carga", "ISO 9001", 85, 92),
    ("EXT-EMB-01", "Fornecedor de cartão, filme e paletes", "Portugal", "Material de embalagem de expedição", "Produto", "8.4.1 a) incorporado na entrega",
     "Especificação de resistência; higiene para linhas alimentares", "Inspeção visual na receção", "ISO 9001; FSC", 80, 95),
]

# pontos de certificação/sistema (0–100) e OTIF do fornecedor (simulado — não existe no dataset) para o critério C5/C6
CERT = {"SUP-001": ("ISO 9001", 80), "SUP-002": ("ISO 9001; ISO 14001", 90), "SUP-003": ("ISO 9001", 80), "SUP-004": ("ISO 9001; EuCertPlast (PCR)", 90),
        "SUP-005": ("Sem certificação válida", 30), "SUP-006": ("ISO 9001; ISO 14001", 90), "SUP-007": ("ISO 9001", 80), "SUP-008": ("ISO 9001", 80),
        "SUP-009": ("ISO 9001; ISO 15378 (em curso)", 70), "SUP-010": ("ISO 9001; FSSC 22000", 100)}
OTIF = {"SUP-001": 0.93, "SUP-002": 0.96, "SUP-003": 0.95, "SUP-004": 0.88, "SUP-005": 0.82, "SUP-006": 0.94, "SUP-007": 0.97, "SUP-008": 0.98, "SUP-009": 0.85, "SUP-010": 0.93}

INFO = [
    ("INF-01", "Resinas e masterbatch (SUP-001 a SUP-010)", "a) Especificação por material (MFI, densidade, humidade, contaminação) e certificado de análise por lote",
     "b1) Aprovação do material por lote de qualificação; b3) libertação pelo fornecedor com CoA", "c) —", "d) Contacto técnico com o laboratório de receção",
     "e) Scorecard trimestral e SCAR com 8D", "f) Auditoria de processo ao fornecedor quando classe C/D"),
    ("INF-02", "Resinas de grau alimentar e farmacêutico (SUP-009, SUP-010)", "a) Declaração de conformidade FCM / Ph. Eur.; rastreabilidade ao lote de produção",
     "b2) Notificação prévia de alterações de processo/local (espelho do acordo com clientes farma)", "c) Pessoal com formação BPF", "d) Clientes farmacêuticos podem auditar o fornecedor",
     "e) Scorecard trimestral", "f) Auditoria anual (CUST-017 pode acompanhar)"),
    ("INF-03", "Laboratórios externos (EXT-LAB-01/02)", "a) Gama, pontos, incerteza requerida e regra de decisão", "b2) Métodos acreditados", "c) Acreditação ISO/IEC 17025",
     "d) —", "e) Revisão de cada certificado", "f) —"),
    ("INF-04", "Ferramentaria (EXT-MOL-01)", "a) Desenho do molde, cavidades, materiais e tolerâncias", "b1) Aprovação por FAI e estudo de capacidade", "c) —",
     "d) Reuniões de projeto com R&D; para moldes de clientes, o cliente pode participar", "e) Prazo e FAI à primeira", "f) Ensaio do molde (T1) nas instalações do fornecedor"),
    ("INF-05", "Transportadora (EXT-TRP-01)", "a) Janelas, cuidados de manuseamento, limpeza para cargas alimentares", "b3) —", "c) Motoristas instruídos", "d) Contacto direto com clientes na entrega",
     "e) Reclamações de transporte", "f) —"),
]

AUDITS = [
    ("AF-26-01", "SUP-005", "2026-10-20", None, "Processo (VDA 6.3 simplificado)", "Classe D: 25% dos lotes com derrogação/rejeição", "Planeada", None),
    ("AF-26-02", "SUP-009", "2026-04-08", "2026-04-08", "Qualificação (sistema + produto)", "Novo fornecedor farmacêutico", "Realizada", "Aprovado condicional: 2 NC menores (rastreabilidade de aditivos)"),
    ("AF-26-03", "SUP-010", "2026-04-09", "2026-04-09", "Qualificação (sistema + produto)", "Novo fornecedor alimentar", "Realizada", "Aprovado: FSSC 22000 válida"),
    ("AF-26-04", "SUP-004", "2026-11-12", None, "Processo PCR", "Variação de qualidade do HDPE-PCR (R14)", "Planeada", None),
    ("AF-26-05", "EXT-MOL-01", "2026-02-24", "2026-02-24", "Processo", "Reforma do M-SOP-007", "Realizada", "Conforme"),
]


def mensal():
    lots = Q.rm_lots()
    lots["Mes"] = Q.monthly(lots, "Date")
    g = lots.groupby(["SupplierId", "Mes"]).agg(Lotes=("MaterialLotId", "count"), Aceites=("FinalDecision", lambda x: (x == "Accepted").sum()),
                                               Derrogacao=("FinalDecision", lambda x: (x == "Accepted With Deviation").sum()),
                                               Rejeitados=("FinalDecision", lambda x: (x == "Rejected").sum()), Kg=("ReceivedQtyKg", "sum"))
    sc = Q.supplier_complaints()
    sc["Mes"] = Q.monthly(sc, "Date")
    sc["Res30"] = sc["Res"].notna() & ((sc["Res"] - pd.to_datetime(sc["Date"])).dt.days <= 30)
    s = sc.groupby(["SupplierId", "Mes"]).agg(SCAR=("SupplierComplaintId", "count"), Dias_Resposta_Soma=("ResponseDays", "sum"), SCAR_Resolvidas_30d=("Res30", "sum"))
    df = g.join(s, how="outer").fillna(0).reset_index()
    rows = []
    for r in df.sort_values(["SupplierId", "Mes"]).itertuples():
        rows.append(dict(ID_Fornecedor=r.SupplierId, Mes=r.Mes, Mes_Num=int(r.Mes.replace("-", "")), Lotes=int(r.Lotes), Aceites=int(r.Aceites), Derrogacao=int(r.Derrogacao),
                         Rejeitados=int(r.Rejeitados), Kg_Recebidos=round(float(r.Kg), 1), SCAR=int(r.SCAR), Dias_Resposta_Soma=int(r.Dias_Resposta_Soma),
                         SCAR_Resolvidas_30d=int(r.SCAR_Resolvidas_30d)))
    return rows


def scar_rows():
    sc = Q.supplier_complaints()
    out = []
    for r in sc.itertuples():
        dd = dt.date.fromisoformat(r.Date)
        resp = Q.to_date(r.DateSupplierResponded)
        if resp and resp > DATA_REF:
            resp = None   # resposta ainda pendente em 31/12/2026
        res = r.Res.date() if pd.notna(r.Res) else None
        out.append(dict(ID_SCAR=r.SupplierComplaintId, Data=dd, ID_Fornecedor=r.SupplierId, Material=r.Material, Lote_MP=r.MaterialLotId, Encomenda=r.PurchaseOrderId,
                        Problema="Resultado de ensaio fora de especificação", Pedido_8D="Sim", Data_Resposta=resp, Data_Resolucao=res,
                        Contencao="Lote em quarentena; devolução ou utilização por derrogação aprovada pela Qualidade"))
    return out


def build(out):
    b = Book("RG-SGQ-12", "Fornecedores Externos: Aprovação, Desempenho e Reavaliação",
             activities="Determinar os controlos sobre fornecedores e processos externos, avaliar e selecionar, monitorizar o desempenho mensal, reavaliar semestralmente e gerir reclamações a fornecedores (SCAR).",
             clauses="8.4.1 a)–c) e critérios de avaliação, seleção, monitorização e reavaliação (informação documentada como evidência); 8.4.2 a)–d); 8.4.3 a)–f); 9.1.3 g); 9.3.2 d7)",
             purpose=f"Registo dos 10 fornecedores de resinas/masterbatch do dataset e de 5 prestadores de processos externos, com o tipo de controlo, o desempenho mensal ({PER_INI[:7]} a {PER_FIM[:7]}) calculado a partir das receções e SCAR reais, a reavaliação semestral por scorecard ponderado (classes A–D e decisão), os requisitos comunicados (8.4.3) e o programa de auditorias a fornecedores.",
             links=[("RG-SGA-11", "Avaliação ambiental dos mesmos fornecedores (SGI): mesmo ID_Fornecedor."), ("RG-SGQ-05 KPI-Q-08/09", "Indicadores de fornecedores."),
                    ("RG-SGA-02 R13, R14, R36; O8", "Riscos e oportunidades de fornecedores.")],
             guidance=[("Academy — cap. 99–100 (Gestão de fornecedores, controlo de material)", "Scorecard quantitativo (ppm, entregas, resposta) para escolher fornecedores com base em dados; qualificação por pesquisa/auditoria."),
                       ("ManualdeFornecedoreseSubcontratadosSICI.pdf (pasta de interpretação)", "Estrutura de requisitos comunicados a fornecedores e subcontratados."),
                       ("ISO/TC 176 APG — External providers", "O auditor procura critérios definidos, evidência da reavaliação e ações quando o desempenho é fraco (SUP-005)."),
                       ("iso9001help.co.uk — Purchasing / 8.4", "Aprovação baseada em desempenho anterior, auditorias ou questionários; lista de fornecedores aprovados.")])
    b.add_list("TipoFornec", ["Produto", "Serviço"])
    b.add_list("Controlo841", ["8.4.1 a) incorporado no produto", "8.4.1 a) incorporado na entrega", "8.4.1 b) fornecido diretamente ao cliente", "8.4.1 c) processo externo"])
    b.add_list("EstadoAprov", ["Aprovado", "Aprovado condicional", "Em qualificação", "Suspenso"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("EstadoAud", ["Planeada", "Realizada", "Adiada"])

    sup = Q.suppliers()
    frows = []
    estado = {"SUP-005": "Aprovado condicional", "SUP-009": "Aprovado condicional", "SUP-004": "Aprovado"}
    for r in sup.itertuples():
        frows.append(dict(ID_Fornecedor=r.SupplierId, Nome=r.SupplierName, Pais=r.Country, Materiais=r.MaterialsSupplied, Tipo="Produto", Controlo_841="8.4.1 a) incorporado no produto",
                          Tipo_Controlo="CoA por lote; especificação; SCAR com 8D", Extensao_Controlo="Inspeção de receção por lote (PC-MP-01): MFI, densidade, humidade, contaminação",
                          Certificacao=CERT[r.SupplierId][0], Tipo_Contrato=r.ContractType, Anos_Fornecedor=int(r.YearsAsSupplier), Estado_Aprovacao=estado.get(r.SupplierId, "Aprovado"),
                          Data_Aprovacao=dt.date(2026, 4, 15) if r.SupplierId in ("SUP-009", "SUP-010") else dt.date(2026 - min(int(r.YearsAsSupplier), 10), 3, 1)))
    for e in EXTERNOS:
        frows.append(dict(ID_Fornecedor=e[0], Nome=e[1], Pais=e[2], Materiais=e[3], Tipo=e[4], Controlo_841=e[5], Tipo_Controlo=e[6], Extensao_Controlo=e[7],
                          Certificacao=e[8], Tipo_Contrato="Contrato de prestação", Anos_Fornecedor=5, Estado_Aprovacao="Aprovado", Data_Aprovacao=dt.date(2024, 1, 15)))
    # mesmos nomes de coluna do RG-SGA-11 tbl_fornecedores (Nome, Materiais, Tipo_Contrato, Anos_Fornecedor, Classe, Decisao, Tipo_Controlo, Extensao_Controlo)
    fcols = [col("ID_Fornecedor", 11, key="PK", desc="ID (SUP-* do dataset; EXT-* prestadores)."), col("Nome", 34, desc="Nome do fornecedor."), col("Pais", 12, desc="País."),
             col("Materiais", 30, desc="Materiais / serviços."), col("Tipo", 8, dv="TipoFornec", desc="Produto / serviço."), col("Controlo_841", 26, dv="Controlo841", desc="Porque é controlado (8.4.1 a–c)."),
             col("Tipo_Controlo", 40, desc="Tipo de controlo aplicado ao fornecedor (8.4.2 b)."), col("Extensao_Controlo", 40, desc="Extensão do controlo às saídas / verificação (8.4.2 b, d)."),
             col("Certificacao", 22, desc="Sistema/certificação."), col("Tipo_Contrato", 16, desc="Tipo de contrato (dataset)."), col("Anos_Fornecedor", 7, "int", desc="Anos como fornecedor."),
             col("Estado_Aprovacao", 14, dv="EstadoAprov", desc="Estado na lista de fornecedores aprovados."), col("Data_Aprovacao", 11, "date", desc="Data da aprovação/última reavaliação formal."),
             col("Classe", 8, f='=IFERROR(INDEX(tbl_avaliacao[Classe],MATCH(@ID_Fornecedor@&"|ATUAL",tbl_avaliacao[Chave],0)),"—")', desc="Classe do período atual (S1-2026; JA-2026 para fornecedores novos)."),
             col("Decisao", 18, f='=IFERROR(INDEX(tbl_avaliacao[Decisao],MATCH(@ID_Fornecedor@&"|ATUAL",tbl_avaliacao[Chave],0)),"Avaliação qualitativa")', desc="Decisão da reavaliação."),
             col("Coerencia", 16, f='=IF(@ID_Fornecedor@="","",IF(AND(@Decisao@="Suspender",@Estado_Aprovacao@="Aprovado"),"Rever estado",IF(AND(@Classe@="C",@Estado_Aprovacao@="Aprovado"),"Rever estado","OK")))',
                 desc="Estado de aprovação coerente com a reavaliação?")]
    b.table("Fornecedores", "tbl_fornecedores", fcols, frows, "Lista de fornecedores e prestadores externos com o tipo e extensão do controlo (8.4.1, 8.4.2).",
            title="FORNECEDORES EXTERNOS APROVADOS E TIPO DE CONTROLO (8.4.1 · 8.4.2)",
            subtitle="10 fornecedores de matéria-prima do dataset + 5 prestadores de processos/serviços externos · Classe e decisão lidas do período marcado 'Atual' na reavaliação",
            cf=[("Estado_Aprovacao", {"condicional": "orange", "Suspenso": "red", "Aprovado": "green"}), ("Classe", {"D": "red", "C": "orange", "B": "yellow", "A": "green"}),
                ("Coerencia", {"Rever": "red", "OK": "green"})], row_height=45, freeze_col=2)

    mcols = [col("ID_Fornecedor", 10, desc="Fornecedor.", key="FK → tbl_fornecedores"), col("Mes", 8, desc="Mês."), col("Mes_Num", 8, "int", desc="aaaamm (para filtros por período)."),
             col("Lotes", 7, "int", desc="Lotes recebidos."), col("Aceites", 7, "int", desc="Aceites sem derrogação."), col("Derrogacao", 8, "int", desc="Aceites com derrogação."),
             col("Rejeitados", 8, "int", desc="Rejeitados."), col("Kg_Recebidos", 11, "num0", desc="kg recebidos."), col("SCAR", 6, "int", desc="Reclamações ao fornecedor."),
             col("Dias_Resposta_Soma", 8, "int", desc="Σ dias até resposta."), col("SCAR_Resolvidas_30d", 8, "int", desc="SCAR resolvidas em ≤ 30 dias."),
             col("Pct_Aceites", 8, "pct1", f='=IFERROR(@Aceites@/@Lotes@,"")', desc="% aceites sem derrogação.")]
    b.table("Desempenho_Mensal", "tbl_desempenho_forn", mcols, mensal(), "Desempenho mensal por fornecedor (dataset: receções de MP e SCAR).", row_height=15)

    D = lambda c_: f"tbl_desempenho_forn[{c_}]"
    S = lambda c_, a: f'SUMIFS({D(c_)},{D("ID_Fornecedor")},@ID_Fornecedor@,{D("Mes_Num")},">="&@Mes_Ini@,{D("Mes_Num")},"<="&@Mes_Fim@)'
    acols = [col("ID_Fornecedor", 10, desc="Fornecedor.", key="FK"), col("Periodo", 9, desc="Semestre."), col("Atual", 6, dv="SimNao", desc="Sim = período usado como classificação atual do fornecedor."),
             col("Chave", 16, f='=@ID_Fornecedor@&"|"&IF(@Atual@="Sim","ATUAL",@Periodo@)', desc="Chave técnica."),
             col("Mes_Ini", 8, "int", desc="aaaamm inicial."), col("Mes_Fim", 8, "int", desc="aaaamm final."),
             col("Lotes", 7, "int", f=f"={S('Lotes', 0)}", desc="Lotes no período."), col("Aceites", 7, "int", f=f"={S('Aceites', 0)}", desc="Aceites."),
             col("Rejeitados", 8, "int", f=f"={S('Rejeitados', 0)}", desc="Rejeitados."), col("SCAR", 6, "int", f=f"={S('SCAR', 0)}", desc="SCAR."),
             col("Dias_Resposta_Medio", 8, "num1", f=f'=IFERROR({S("Dias_Resposta_Soma", 0)}/@SCAR@,"")', desc="Dias médios de resposta."),
             col("Resolvidas_30d", 8, "int", f=f"={S('SCAR_Resolvidas_30d', 0)}", desc="SCAR resolvidas em 30 dias."),
             col("Pontos_Certificacao", 8, "int", desc="C5: sistema/certificação (0–100)."), col("OTIF_Fornecedor", 8, "pct", desc="C6: entregas a tempo (ERP — simulado)."),
             col("C1_Qualidade", 8, "num0", f='=IFERROR(MAX(0,MIN(100,(@Aceites@/@Lotes@-0.8)/(0.98-0.8)*100)),"")', desc="C1 (40%): % aceites, 80% → 0 pts, 98% → 100 pts."),
             col("C2_Rejeicao", 8, "num0", f='=IFERROR(MAX(0,100-@Rejeitados@/@Lotes@*1000),"")', desc="C2 (15%): 100 − 10 pts por 1% de lotes rejeitados."),
             col("C3_Resposta", 8, "num0", f='=IF(@SCAR@=0,100,MAX(0,MIN(100,100-(@Dias_Resposta_Medio@-5)*10)))', desc="C3 (15%): ≤ 5 dias = 100; −10 pts/dia."),
             col("C4_Resolucao", 8, "num0", f='=IF(@SCAR@=0,100,@Resolvidas_30d@/@SCAR@*100)', desc="C4 (10%): % SCAR resolvidas em 30 dias."),
             col("C5_Certificacao", 8, "num0", f='=@Pontos_Certificacao@', desc="C5 (10%)."), col("C6_Entrega", 8, "num0", f='=MAX(0,MIN(100,(@OTIF_Fornecedor@-0.8)/(0.98-0.8)*100))', desc="C6 (10%)."),
             col("Pontuacao", 9, "num1", f='=IFERROR(0.4*@C1_Qualidade@+0.15*@C2_Rejeicao@+0.15*@C3_Resposta@+0.1*@C4_Resolucao@+0.1*@C5_Certificacao@+0.1*@C6_Entrega@,"")', desc="Pontuação ponderada 0–100."),
             col("Classe", 6, f='=IF(@Pontuacao@="","",IF(@Pontuacao@>=85,"A",IF(@Pontuacao@>=70,"B",IF(@Pontuacao@>=50,"C","D"))))', desc="A ≥ 85 · B ≥ 70 · C ≥ 50 · D < 50."),
             col("Decisao", 16, f='=IF(@Classe@="","",IF(@Lotes@<15,"Em qualificação (amostra < 15 lotes)",CHOOSE(MATCH(@Classe@,{"A","B","C","D"},0),"Manter","Manter + plano","Aprovação condicional","Suspender")))',
                 desc="Decisão da reavaliação (ação necessária, 8.4.1).")]
    arows = []
    for s in list(sup.SupplierId):
        novo = s in ("SUP-009", "SUP-010")
        for per, a, z in (("S2-2025", 202507, 202512), ("S1-2026", 202601, 202606), ("JA-2026", 202607, 202608)):
            if novo and per != "JA-2026":
                continue
            atual = "Sim" if (per == "JA-2026") == novo and per != "S2-2025" else "Não"
            arows.append(dict(ID_Fornecedor=s, Periodo=per, Atual=atual, Mes_Ini=a, Mes_Fim=z, Pontos_Certificacao=CERT[s][1], OTIF_Fornecedor=OTIF[s]))
    b.table("Reavaliacao_Semestral", "tbl_avaliacao", acols, arows, "Reavaliação semestral por scorecard ponderado (critérios 8.4.1), calculada a partir do desempenho mensal.",
            title="REAVALIAÇÃO SEMESTRAL DE FORNECEDORES — SCORECARD (8.4.1)",
            subtitle="Pesos: C1 qualidade 40% · C2 rejeição 15% · C3 resposta 15% · C4 resolução 10% · C5 certificação 10% · C6 entrega 10% · Tudo calculado com SUMIFS sobre tbl_desempenho_forn",
            cf=[("Classe", {"D": "red", "C": "orange", "B": "yellow", "A": "green"}), ("Decisao", {"Suspender": "red", "condicional": "orange", "plano": "yellow", "Manter": "green"})],
            row_height=16, freeze_col=2)

    scols = [col("ID_SCAR", 9, key="PK", desc="Reclamação ao fornecedor (dataset)."), col("Data", 11, "date", desc="Data."), col("ID_Fornecedor", 9, desc="Fornecedor.", key="FK"),
             col("Material", 10, desc="Material."), col("Lote_MP", 16, desc="Lote de MP."), col("Encomenda", 9, desc="Encomenda."), col("Problema", 30, desc="Problema."),
             col("Pedido_8D", 7, dv="SimNao", desc="8D pedido ao fornecedor."), col("Contencao", 40, desc="Contenção."), col("Data_Resposta", 11, "date", desc="Resposta do fornecedor (dataset).", req=False),
             col("Data_Resolucao", 11, "date", desc="Resolução (vazia se posterior à data de referência).", req=False),
             col("Dias_Resposta", 7, "int", f='=IF(@Data_Resposta@="","",@Data_Resposta@-@Data@)', desc="Dias até resposta."),
             col("Estado", 10, f='=IF(@ID_SCAR@="","",IF(@Data_Resolucao@<>"","Fechada",IF(DataRef-@Data@>30,"Atrasada","Aberta")))', desc="Estado à data de referência.")]
    b.table("Reclamacoes_Fornecedor", "tbl_scar", scols, scar_rows(), "Reclamações a fornecedores (SCAR) do dataset com estado à data de referência.",
            cf=[("Estado", {"Atrasada": "red", "Aberta": "orange", "Fechada": "green"})], row_height=15)

    icols = [col("ID", 7, key="PK", desc="Linha."), col("Aplica_a", 30, desc="Fornecedores."), col("a_Processos_Produtos", 44, desc="8.4.3 a)."), col("b_Aprovacoes", 40, desc="8.4.3 b)."),
             col("c_Competencia", 22, desc="8.4.3 c)."), col("d_Interacoes", 36, desc="8.4.3 d)."), col("e_Controlo_Desempenho", 26, desc="8.4.3 e)."), col("f_Verificacao_Local", 34, desc="8.4.3 f).")]
    b.table("Informacao_Fornecedores", "tbl_info_fornecedores", icols, rows_from(input_names(icols), INFO), "Requisitos comunicados aos fornecedores externos (8.4.3 a–f).", row_height=45)
    ucols = [col("ID_Auditoria", 9, key="PK", desc="Auditoria a fornecedor."), col("ID_Fornecedor", 10, desc="Fornecedor."), col("Data_Planeada", 11, "date", desc="Planeada."),
             col("Data_Real", 11, "date", desc="Realizada.", req=False), col("Tipo", 26, desc="Tipo."), col("Motivo", 40, desc="Motivo (risco)."), col("Estado", 10, dv="EstadoAud", desc="Estado."),
             col("Resultado", 44, desc="Resultado.", req=False)]
    b.table("Auditorias_Fornecedores", "tbl_auditorias_forn", ucols, rows_from(input_names(ucols), AUDITS, dates=("Data_Planeada", "Data_Real")),
            "Programa de auditorias a fornecedores (8.4.3 f).", row_height=30)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
