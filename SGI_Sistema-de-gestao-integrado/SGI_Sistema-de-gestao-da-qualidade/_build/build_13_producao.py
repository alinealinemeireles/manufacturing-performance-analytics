"""RG-SGQ-13 — Controlo da produção, plano de controlo, libertação de lotes, rastreabilidade, validação de processos, prevenção do erro humano e preservação.
ISO 9001:2026 8.1, 8.5.1 a)–h) (g: ações para prevenir o erro humano; f: validação), 8.5.2 a)–d), 8.5.4, 8.6 a)–b).
Planos de controlo (dim_*_control_plan) e decisões de libertação de TODOS os lotes do período (fact_*_disposition_lot) vêm do dataset."""
import datetime as dt
import pandas as pd
from sgqlib import *
from dimsq import *
import qdata as Q

HFS_PLANO = [("Hot Foil Stamping", "Production", "Foil Transfer", "Critical", "Attribute", "Visual", "D65 Light Booth", "ISO 2859-1", 0.1, "Every 30 min", "Operator", "Adjust Speed"),
             ("Hot Foil Stamping", "Production", "Foil Adhesion", "Critical", "Attribute", "Tape Test", "ASTM D3359 Kit", "ISO 2859-1", 0.1, "Per lot", "Laboratory", "Block Lot"),
             ("Hot Foil Stamping", "Production", "Coverage", "Major", "Attribute", "Visual", "D65 Light Booth", "ISO 2859-1", 0.65, "Every 30 min", "Operator", "Adjust Ink/Pressure"),
             ("Hot Foil Stamping", "Production", "Edge Definition", "Major", "Attribute", "Visual", "Lupa 10x", "ISO 2859-1", 0.65, "Every 30 min", "Operator", "Adjust Pressure"),
             ("Hot Foil Stamping", "Production", "Rub Resistance", "Major", "Attribute", "Rub Test", "MEK Rub Test", "ISO 2859-1", 0.65, "Per lot", "Laboratory", "Block Lot")]
EXTRA_T = {"Edge Definition": "Definição de contornos", "Rub Resistance": "Resistência à fricção"}

RASTREIO = [
    ("RST-26-01", "2026-01-08", "Para trás (reclamação)", "Reclamação CC-20181 (CUST-012): rótulo ilegível em FR-004-rPET-330", "WO-13716 · HF-001 · LotId 2544525011371679",
     "Reclamação → ordem WO-13716 → máquina HF-001 → lote; taxa de rejeição da ordem 6,3% (característica não era crítica no AQL)", "Reclamação sem encomenda de venda (SalesOrderId vazio): não foi possível confirmar que outras entregas receberam o mesmo lote",
     5.5, 0.72, "Parcial"),
    ("RST-26-02", "2026-07-20", "Simulação de recolha (para a frente e para trás)", "Lote LOTE-M-SOP-030-3000 (FA-030-HDPE-FG-1000, linha alimentar)", "WO-16095 · ISBM-009 · LotId 2628131091609501",
     "Para a frente: 724 un produzidas → SO-18007 (CUST-016, 561 un) + 163 un em stock. Para trás: masterbatch COL-COR-008-001", "O registo de consumo só identifica o lote de masterbatch; o lote de resina HDPE-FG (SUP-010) teve de ser deduzido pelo FIFO do armazém",
     3.0, 1.0, "Parcial"),
    ("RST-26-03", "2026-08-25", "Simulação de recolha (farmacêutico)", "Lote LOTE-M-INJ-012-3000 (TE-012-PP-PG-24410)", "WO-16872 · IM-008 · LotId 2628112081687201",
     "Ordem → masterbatch COL-COR-009-001 → resina PP-PG (SUP-009) por FIFO; lote ainda não expedido", "Registo de consumo do masterbatch com peso final (133,73 kg) superior ao inicial (129,84 kg): integridade de dados a corrigir",
     2.5, 1.0, "Parcial"),
]

ERRO_HUMANO = [
    ("EH-01", "EXP", "Produto errado expedido / quantidade errada", "Leitura obrigatória de código de barras na carga e conferência por balança", "Deteção (poka-yoke)", "Em implementação", "MOC-Q-26-10", "KPI-Q-05"),
    ("EH-02", "HFS", "Rótulo/decoração ilegível não detetado", "Visão artificial na HF-001 (inspeção a 100%)", "Deteção automática", "Aprovada", "MOC-Q-26-12", "KPI-Q-04"),
    ("EH-03", "SOP", "Registo de peso copiado (REL-26-02)", "Captura automática da balança para o MES", "Eliminação do registo manual", "Implementada", "O3", "—"),
    ("EH-04", "REC", "Uso de MP em quarentena (etiqueta caída)", "Bloqueio no ERP + zona de quarentena fechada", "Prevenção (bloqueio)", "Implementada", "CAPA-Q-26-05", "KPI-Q-08"),
    ("EH-05", "INJ", "Parâmetros alterados fora da janela validada", "Limites do DOE bloqueados no controlador da IM-002 (acesso por password de engenharia)", "Prevenção (bloqueio)", "Implementada", "MOC-Q-26-05", "KPI-Q-01"),
    ("EH-06", "LAB", "Lote libertado sem ensaio de fuga", "Etiqueta verde só é impressa com o resultado do ensaio no sistema", "Prevenção (interlock)", "Implementada", "REL-26-01", "KPI-Q-02"),
    ("EH-07", "SER", "Ensaio de aderência feito só no fim do lote", "Pedido de ensaio automático no arranque e a meio do lote (MES)", "Lembrete / sequência obrigatória", "Implementada", "GW-26-05", "KPI-Q-01"),
    ("EH-08", "LAB", "Calibre de gargalo errado usado no posto", "Calibres com código de cor por dimensão (24/410 azul, 28/410 verde, 28/415 laranja)", "Gestão visual", "Implementada", "—", "—"),
    ("EH-09", "PCP", "Erros na passagem de turno (turno 2)", "Checklist de passagem de turno digital com estado de moldes e lotes retidos", "Padronização", "Em implementação", "GW-26-02", "KPI-Q-01"),
]

VALIDACAO = [
    ("VP-01", "Migração global (contacto alimentar) — FA-030/031, TA-014, PT (versão alimentar)", "SOP; INJ", "Ensaio destrutivo e por amostragem: a conformidade de cada peça não é verificável", "IQ/OQ/PQ da ISBM-009 e IM-008 com resina FG; 3 lotes de PQ com migração ≤ 10 mg/dm²", "2026-06-26", "Validado", 12, "Mudança de resina, molde ou parâmetro crítico"),
    ("VP-02", "Anel de inviolabilidade TE-012", "INJ", "Ensaio destrutivo", "Revalidação após retificação das pontes (DC-26-02): PQ 3 lotes; 0 falhas em 192 amostras; restrição levantada", "2026-12-14", "Validado", 6, "PFMEA S = 10; retificação das pontes (DC-26-02)"),
    ("VP-03", "Cura UV da serigrafia", "SER", "Ensaio MEK destrutivo por amostragem", "Revalidação anual: mapa de potência UV e velocidade após troca de lâmpadas; PQ 3 lotes; MEK ≥ 100 duplos esfregaços", "2026-11-18", "Validado", 12, "Troca de lâmpadas UV ou de tinta"),
    ("VP-04", "Estanquidade de frascos (linhas sem leak tester 100%)", "SOP", "Verificação por amostragem AQL 0,1", "Validação da janela de sopro (espessura mínima) por DOE; revalidação após reforma de molde", "2026-03-10", "Validado", 12, "Reforma de molde; nova resina"),
    ("VP-05", "Soldadura por indução do selo (futuro, linha farma)", "INJ", "Não verificável sem destruir", "Planeado para 2027", None, "Planeado", 12, "—"),
]

PRESERV = [
    ("PRE-01", "Identificação", "Etiqueta de palete com lote, ordem e código de barras; estado (verde libertado / amarelo retido / vermelho rejeitado)", "8.5.2 b)"),
    ("PRE-02", "Manuseamento", "Empilhamento máximo por formato; cantoneiras; empilhadores com garfos protegidos", "8.5.4"),
    ("PRE-03", "Controlo de contaminação", "Linhas alimentar/farma: sacos fechados, paletes de plástico, sem madeira nem vidro na zona (AMB-04)", "8.5.4"),
    ("PRE-04", "Embalagem", "Filme retrátil e caixas conforme especificação do cliente (ALR-26-04)", "8.5.4"),
    ("PRE-05", "Armazenamento", "FIFO por lote; resinas higroscópicas com HR ≤ 60%; prazo de validade das resinas PCR 12 meses", "8.5.4"),
    ("PRE-06", "Transporte", "Caixa limpa e seca para alimentar/farma; verificação na carga", "8.5.4; 8.4 (EXT-TRP-01)"),
]


def plano_rows():
    rows = []
    specs = [("dim_bottle_control_plan_cq.csv", "SOP", "Frasco"), ("dim_cap_control_plan_cq.csv", "INJ", "Tampa / pote"), ("dim_ink_control_plan_cq.csv", "SER", "Decoração")]
    k = 0
    for f, proc, fam in specs:
        d = Q.rd(f, Q.DIM)
        for r in d.itertuples():
            k += 1
            pr = Q.T_PROC.get(r.Process, proc)
            rows.append(dict(ID_Controlo=f"PC-{k:03d}", Processo=pr, Familia=fam, Caracteristica=Q.T_CARACT.get(r.Characteristic, r.Characteristic), Classe=Q.T_CLASSE.get(r.Class, r.Class),
                             Tipo_Inspecao="Variáveis" if r.InspectionType == "Variable" else "Atributos", Metodo=r.Method, Equipamento=Q.T_EQUIP.get(r.Equipment, r.Equipment),
                             Norma=r.Standard, AQL=(float(r.AQL) if str(r.AQL).replace(".", "", 1).isdigit() else None), Frequencia=Q.T_FREQ.get(r.Frequency, r.Frequency),
                             Responsavel=Q.T_OWNER.get(r.Owner, r.Owner), Plano_Reacao=Q.T_REACAO.get(r.ReactionPlan, r.ReactionPlan)))
    for r in HFS_PLANO:
        k += 1
        rows.append(dict(ID_Controlo=f"PC-{k:03d}", Processo="HFS", Familia="Decoração", Caracteristica=Q.T_CARACT.get(r[2], EXTRA_T.get(r[2], r[2])), Classe=Q.T_CLASSE[r[3]],
                         Tipo_Inspecao="Atributos", Metodo=r[5], Equipamento=Q.T_EQUIP.get(r[6], r[6]), Norma=r[7], AQL=r[8], Frequencia=Q.T_FREQ.get(r[9], r[9]),
                         Responsavel=Q.T_OWNER[r[10]], Plano_Reacao=Q.T_REACAO.get(r[11], r[11])))
    return rows


def libertacao_rows():
    l = Q.lot_dispositions()
    out = []
    for r in l.itertuples():
        out.append(dict(Lote=r.Lote, Ordem=r.WorkOrder, Data_Producao=dt.date.fromisoformat(str(r.ProductionDate)[:10]), Mes=str(r.ProductionDate)[:7],
                        Turno=str(r.Shift).replace("Shift ", "T"), Maquina=r.MachineId, Familia=r.Familia, Produto=r.Produto, Tamanho_Lote=int(r.LotSize), Letra_Codigo=r.CodeLetter,
                        Amostra=int(r.SampleSize), Defeitos_Criticos=int(r.CriticalDefects), Defeitos_Maiores=int(r.MajorDefects), Defeitos_Menores=int(r.MinorDefects),
                        Decisao_Variaveis={"Conforming": "Conforme", "Nonconforming": "Não conforme", "N/A": "N.A."}.get(r.VariablesDecision, r.VariablesDecision),
                        Decisao_Atributos={"Approved": "Aprovado", "Rejected": "Rejeitado"}.get(r.AttributesDecision, r.AttributesDecision),
                        Decisao_Final={"Approved": "Libertado", "Rejected": "Rejeitado"}[r.FinalLotDecision], Disposicao=Q.T_DISP.get(r.DispositionDetail, r.DispositionDetail),
                        Data_Hora_Decisao=pd.Timestamp(r.LotDecisionDateTime).to_pydatetime().replace(microsecond=0), Observacao=None if r.Remarks == "—" else r.Remarks,
                        Autorizado_Por=r.Inspector))
    return out


def build(out):
    b = Book("RG-SGQ-13", "Controlo da Produção, Libertação e Rastreabilidade",
             activities="Controlar a produção em condições controladas (plano de controlo), validar processos especiais, prevenir o erro humano, libertar lotes com evidência de conformidade e de quem autorizou, e demonstrar rastreabilidade.",
             clauses="8.1 b)–d); 8.5.1 a)–h) (2026 g: prevenir o erro humano; f: validação e revalidação); 8.5.2 a)–d) (informação documentada para a rastreabilidade); 8.5.4 preservação; 8.6 (evidência de conformidade com critérios de aceitação e rastreabilidade às pessoas que autorizam)",
             purpose=f"Plano de controlo consolidado ({'frascos, tampas/potes, serigrafia e hot foil'}) a partir do dataset; registo de libertação de TODOS os lotes decididos entre {PER_INI} e {PER_FIM} (dataset) com critérios, disposição e inspetor que autorizou; exercícios de rastreio com casos reais; validação de processos especiais; medidas contra o erro humano; regras de preservação.",
             links=[("RG-SGQ-14", "Lotes rejeitados, segregados, retrabalhados e libertados por concessão."), ("RG-SGQ-09", "Equipamentos de medição do plano de controlo."),
                    ("RG-SGQ-04 PFMEA", "Características e severidades."), ("dataset", "dim_*_control_plan_cq, fact_*_disposition_lot_cq, fact_material_consumption, fact_sales.")],
             guidance=[("ISO 2859-1:2026 / ISO 3951 (Academy cap. 63–64, 141–142)", "Letra de código, tamanho da amostra e Ac/Re por AQL; decisões de lote registadas por inspetor."),
                       ("ISO/TC 176 APG — Product release / traceability", "O auditor escolhe um lote expedido e segue até às inspeções, ao inspetor que libertou e às matérias-primas (exercícios RST)."),
                       ("Academy — cap. 26 (Jidoka e Poka-Yoke)", "Hierarquia contra o erro humano: eliminar > prevenir (bloqueio) > detetar > alertar (tbl_erro_humano)."),
                       ("GHTF/SG3 — validação de processos (referência farma)", "IQ/OQ/PQ e revalidação para saídas não verificáveis (8.5.1 f).")])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Classe", ["Crítica", "Maior", "Menor"])
    b.add_list("Resultado", ["Completo", "Parcial", "Falhou"])
    b.add_list("TipoEH", ["Eliminação do registo manual", "Prevenção (bloqueio)", "Prevenção (interlock)", "Deteção (poka-yoke)", "Deteção automática", "Lembrete / sequência obrigatória", "Gestão visual", "Padronização"])
    b.add_list("EstadoEH", ["Planeada", "Aprovada", "Em implementação", "Implementada"])
    b.add_list("EstadoVal", ["Planeado", "Validado", "Validado com restrições", "Revalidação vencida"])

    pcols = [col("ID_Controlo", 8, key="PK", desc="Linha do plano de controlo."), col("Processo", 7, dv="Processo", desc="Processo."), col("Familia", 11, desc="Família."),
             col("Caracteristica", 26, desc="Característica (dataset, traduzida)."), col("Classe", 8, dv="Classe", desc="Classe."), col("Tipo_Inspecao", 10, desc="Variáveis / atributos."),
             col("Metodo", 18, desc="Método."), col("Equipamento", 30, desc="Equipamento de medição (RG-SGQ-09)."), col("Norma", 24, desc="Norma / critério."),
             col("AQL", 6, "num", desc="AQL (atributos).", req=False), col("Frequencia", 20, desc="Frequência."), col("Responsavel", 11, desc="Quem mede."), col("Plano_Reacao", 24, desc="Plano de reação.")]
    b.table("Plano_Controlo", "tbl_plano_controlo", pcols, plano_rows(), "Plano de controlo consolidado (8.5.1 a–c): características, métodos, critérios, frequência e reação.",
            title="PLANO DE CONTROLO CONSOLIDADO (8.5.1)", subtitle="Fonte: planos de controlo do dataset (frascos, tampas/potes, serigrafia) + hot foil · Critérios de aceitação por AQL/ISO 3951",
            cf=[("Classe", {"Crítica": "red", "Maior": "orange", "Menor": "gray"})], row_height=16, freeze_col=4)

    lcols = [col("Lote", 22, key="PK", desc="Lote (ProductBatch / PrintLot do dataset)."), col("Ordem", 9, desc="Ordem de fabrico."), col("Data_Producao", 11, "date", desc="Data de produção."),
             col("Mes", 8, desc="aaaa-mm."), col("Turno", 5, desc="Turno."), col("Maquina", 9, desc="Máquina."), col("Familia", 11, desc="Frasco / tampa-pote / decoração."),
             col("Produto", 20, desc="Produto."), col("Tamanho_Lote", 9, "num0", desc="Tamanho do lote."), col("Letra_Codigo", 5, desc="Letra de código ISO 2859-1."),
             col("Amostra", 7, "int", desc="Tamanho da amostra."), col("Defeitos_Criticos", 6, "int", desc="Críticos na amostra."), col("Defeitos_Maiores", 6, "int", desc="Maiores."),
             col("Defeitos_Menores", 6, "int", desc="Menores."), col("Decisao_Variaveis", 10, desc="Decisão por variáveis (ISO 3951)."), col("Decisao_Atributos", 10, desc="Decisão por atributos (ISO 2859-1)."),
             col("Decisao_Final", 9, desc="Libertado / rejeitado (8.6 a)."), col("Disposicao", 24, desc="Disposição detalhada."), col("Data_Hora_Decisao", 16, "date", desc="Data/hora da decisão."),
             col("Observacao", 18, desc="Característica que falhou (Ac/Re).", req=False), col("Autorizado_Por", 14, desc="Inspetor que autorizou a libertação (8.6 b)."),
             col("Horas_Ate_Decisao", 8, "num1", f='=IF(@Lote@="","",(@Data_Hora_Decisao@-@Data_Producao@)*24)', desc="Horas entre o início do dia de produção e a decisão."),
             col("Controlo_Qualidade", 16, f='=IF(@Lote@="","",IF(@Autorizado_Por@="","FALTA autorizador",IF(@Disposicao@="Aprovado por concessão","Ver concessão (RG-SGQ-14)",IF(@Disposicao@="Aprovado após retrabalho","Retrabalho: confirmar reinspeção (8.7.1)",IF(AND(@Decisao_Final@="Libertado",@Defeitos_Criticos@>0),"Crítico libertado sem tratamento","OK")))))',
                 desc="Regras de libertação (8.6).")]
    lrows = libertacao_rows()
    b.table("Libertacao_Lotes", "tbl_libertacao", lcols, lrows, "Registo de libertação de todos os lotes decididos no período (evidência de 8.6 a–b).",
            title="LIBERTAÇÃO DE LOTES (8.6) — TODOS OS LOTES DO PERÍODO", subtitle=f"{len(lrows)} lotes do dataset ({PER_INI} a {PER_FIM}) · Autorizado_Por = inspetor que decidiu · Controlo calculado",
            cf=[("Decisao_Final", {"Rejeitado": "red", "Libertado": "green"}), ("Controlo_Qualidade", {"FALTA": "red", "Crítico": "red", "concessão": "orange", "Retrabalho": "yellow"})], row_height=14, freeze_col=1)
    ws = b.wb["Libertacao_Lotes"]
    t = b.tables["tbl_libertacao"]
    L = t["colmap"]["Data_Hora_Decisao"]
    for rr in range(t["first"], t["last"] + 1):
        ws[f"{L}{rr}"].number_format = "yyyy-mm-dd hh:mm"

    rcols = [col("ID_Rastreio", 9, key="PK", desc="Exercício de rastreio."), col("Data", 11, "date", desc="Data."), col("Tipo", 22, desc="Tipo de exercício."),
             col("Objeto", 44, desc="O que foi rastreado."), col("IDs_Dataset", 34, desc="IDs reais do dataset."), col("Resultado_Rastreio", 50, desc="Cadeia encontrada."),
             col("Lacunas", 50, desc="Lacunas de rastreabilidade encontradas."), col("Horas", 6, "num1", desc="Tempo para completar (h)."), col("Pct_Quantidade_Reconciliada", 9, "pct", desc="% da quantidade reconciliada."),
             col("Resultado", 9, dv="Resultado", desc="Completo / parcial / falhou."),
             col("Cumpre_Meta", 9, f='=IF(@ID_Rastreio@="","",IF(AND(@Horas@<=4,@Pct_Quantidade_Reconciliada@>=0.99,@Resultado@="Completo"),"Sim","Não"))', desc="Meta: ≤ 4 h, ≥ 99% reconciliado, cadeia completa.")]
    b.table("Exercicios_Rastreio", "tbl_rastreio", rcols, rows_from(input_names(rcols), RASTREIO, dates=("Data",)),
            "Exercícios de rastreabilidade e simulação de recolha com casos reais do dataset (8.5.2).",
            title="RASTREABILIDADE — EXERCÍCIOS COM CASOS REAIS (8.5.2)", subtitle="Lacunas encontradas nos dados: consumo sem lote de resina; reclamação sem encomenda; pesos de consumo incoerentes (ver risco R18)",
            cf=[("Cumpre_Meta", {"Não": "red", "Sim": "green"}), ("Resultado", {"Parcial": "orange", "Falhou": "red"})], row_height=60)

    hcols = [col("ID_Medida", 7, key="PK", desc="Medida contra o erro humano."), col("Processo", 7, dv="Processo", desc="Processo."), col("Erro_Humano_Alvo", 36, desc="Erro a prevenir."),
             col("Medida", 50, desc="Medida implementada (8.5.1 g)."), col("Tipo", 22, dv="TipoEH", desc="Nível na hierarquia (eliminar > prevenir > detetar > alertar)."),
             col("Estado", 13, dv="EstadoEH", desc="Estado."), col("Ligacao", 14, desc="Origem (CAPA, MOC, relato).", req=False), col("KPI", 9, desc="KPI que mostra o efeito.", req=False),
             col("Forca_Medida", 10, f='=IF(@ID_Medida@="","",IF(OR(LEFT(@Tipo@,4)="Elim",LEFT(@Tipo@,4)="Prev"),"Forte",IF(LEFT(@Tipo@,4)="Dete","Média","Fraca")))', desc="Força da medida.")]
    b.table("Prevencao_Erro_Humano", "tbl_erro_humano", hcols, rows_from(input_names(hcols), ERRO_HUMANO),
            "Ações para prevenir o erro humano (8.5.1 g — reforçado na ISO 9001:2026).", title="PREVENÇÃO DO ERRO HUMANO (8.5.1 g)",
            cf=[("Forca_Medida", {"Forte": "green", "Média": "yellow", "Fraca": "orange"}), ("Estado", {"Implementada": "green", "implementação": "yellow"})], row_height=30)

    vcols = [col("ID_Validacao", 7, key="PK", desc="Processo especial."), col("Processo_Especial", 44, desc="Processo cuja saída não é verificável a posteriori."), col("Processos", 8, desc="Processos."),
             col("Porque_Nao_Verificavel", 32, desc="Justificação (8.5.1 f)."), col("Validacao_Realizada", 50, desc="IQ/OQ/PQ e resultado."), col("Data_Validacao", 11, "date", desc="Data.", req=False),
             col("Estado", 16, dv="EstadoVal", desc="Estado."), col("Revalidacao_Meses", 8, "int", desc="Periodicidade da revalidação."), col("Gatilhos_Revalidacao", 34, desc="O que obriga a revalidar."),
             col("Proxima_Revalidacao", 11, "date", f='=IF(@Data_Validacao@="","",EDATE(@Data_Validacao@,@Revalidacao_Meses@))', desc="Próxima revalidação periódica."),
             col("Alerta", 12, f='=IF(@Proxima_Revalidacao@="","",IF(@Proxima_Revalidacao@<DataRef,"Vencida",IF(@Proxima_Revalidacao@<DataRef+60,"Em 60 dias","OK")))', desc="Alerta.")]
    b.table("Validacao_Processos", "tbl_validacao", vcols, rows_from(input_names(vcols), VALIDACAO, dates=("Data_Validacao",)),
            "Validação e revalidação periódica de processos cujas saídas não podem ser verificadas (8.5.1 f).", title="VALIDAÇÃO DE PROCESSOS ESPECIAIS (8.5.1 f)",
            cf=[("Alerta", {"Vencida": "red", "60 dias": "orange", "OK": "green"}), ("Estado", {"restrições": "orange", "Planeado": "gray"})], row_height=40)

    ecols = [col("ID", 7, key="PK", desc="Regra."), col("Aspeto", 22, desc="Aspeto da preservação (8.5.4 Nota)."), col("Regra", 90, desc="Regra aplicada."), col("Clausula", 16, desc="Cláusula.")]
    b.table("Preservacao", "tbl_preservacao", ecols, rows_from(input_names(ecols), PRESERV), "Preservação das saídas (8.5.4).", row_height=30)

    ws = b.sheet("Resumo_Libertacao", "Resumo mensal calculado da libertação por família: lotes, % libertados à primeira, concessões, rejeições e tempo de decisão.")
    title(ws, "RESUMO MENSAL DA LIBERTAÇÃO DE LOTES — calculado", "Contagens sobre tbl_libertacao (dataset) · FPY = aprovados à primeira ÷ decididos")
    fams = ["Frasco", "Tampa / pote", "Decoração"]
    heads = ["Mês"] + [f"{f} — {m}" for f in fams for m in ("lotes", "FPY")] + ["Concessões (todas)", "Rejeitados (todos)", "Horas médias até decisão"]
    header_row(ws, 4, heads, widths=[9] + [11] * 6 + [12, 12, 13])
    T = lambda c_: f"tbl_libertacao[{c_}]"
    for i, m in enumerate(MESES):
        r = 5 + i
        cell(ws, r, 1, m)
        for j, f in enumerate(fams):
            cell(ws, r, 2 + 2 * j, f'=COUNTIFS({T("Mes")},$A{r},{T("Familia")},"{f}")', fmt="0")
            cell(ws, r, 3 + 2 * j, f'=IFERROR(COUNTIFS({T("Mes")},$A{r},{T("Familia")},"{f}",{T("Disposicao")},"Aprovado à primeira")/{get_column_letter(2 + 2 * j)}{r},"")', fmt="0.0%")
        cell(ws, r, 8, f'=COUNTIFS({T("Mes")},$A{r},{T("Disposicao")},"Aprovado por concessão")', fmt="0")
        cell(ws, r, 9, f'=COUNTIFS({T("Mes")},$A{r},{T("Decisao_Final")},"Rejeitado")', fmt="0")
        cell(ws, r, 10, f'=IFERROR(AVERAGEIFS({T("Horas_Ate_Decisao")},{T("Mes")},$A{r}),"")', fmt="0.0")
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
