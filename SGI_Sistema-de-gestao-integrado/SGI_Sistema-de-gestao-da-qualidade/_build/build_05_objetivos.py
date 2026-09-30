"""RG-SGQ-05 — Objetivos da qualidade, catálogo de KPI, base mensal de desempenho e plano de monitorização e medição.
ISO 9001:2026 6.2.1 a)–h), 6.2.2 a)–e), 9.1.1 a)–d), 9.1.3.
A base mensal (tbl_base_mensal) é agregada do dataset; TODOS os KPI mensais são fórmulas sobre essa base."""
import numpy as np
import pandas as pd
from openpyxl.chart import LineChart, BarChart, Reference
from sgqlib import *
from dimsq import *
import qdata as Q

# catálogo de KPI: (ID, nome, coluna em tbl_kpi_mensal, unidade, polaridade, meta, frequência, processo, dono, fonte, fórmula (texto), formato)
KPIS = [
    ("KPI-Q-01", "Taxa de rejeição interna", "Taxa_Rejeicao", "%", "Menor", 0.020, "Mensal", "PCP", GPROD, "fact_production (RejectedQty, ProducedQty)", "Rejeitado ÷ produzido", "pct1"),
    ("KPI-Q-02", "Lotes aprovados à primeira (FPY de lote)", "FPY_Lotes", "%", "Maior", 0.92, "Mensal", "LAB", GQ, "disposição de lotes (frasco, tampa, decoração)", "Lotes 'Aprovado à primeira' ÷ lotes decididos", "pct1"),
    ("KPI-Q-03", "PPM de cliente", "PPM_Cliente", "ppm", "Menor", 150, "Mensal", "COM", DCOM, "reclamações (QtyAffected) e vendas (ShippedQty)", "Quantidade afetada reclamada ÷ quantidade expedida × 10⁶", "num0"),
    ("KPI-Q-04", "Reclamações por milhão de unidades expedidas (CPMU)", "CPMU", "rec./milhão", "Menor", 3.0, "Mensal", "COM", DCOM, "reclamações e vendas", "N.º de reclamações ÷ unidades expedidas × 10⁶", "num"),
    ("KPI-Q-05", "Reclamações de serviço / logística", "Reclamacoes_Servico", "n.º", "Menor", 5, "Mensal", "EXP", LOG, "reclamações (atraso, quantidade, produto trocado, rótulo)", "Contagem", "num0"),
    ("KPI-Q-06", "Tempo médio de resolução de reclamações", "Dias_Resolucao", "dias", "Menor", 20, "Mensal", "COM", DCOM, "reclamações resolvidas no mês", "Σ dias até resolução ÷ reclamações resolvidas", "num1"),
    ("KPI-Q-07", "OEE médio", "OEE", "%", "Maior", 0.805, "Mensal", "PCP", GPROD, "fact_production (OEE por ordem)", "Média do OEE das ordens do mês", "pct1"),
    ("KPI-Q-08", "Lotes de matéria-prima aceites sem derrogação", "Lotes_MP_Aceites", "%", "Maior", 0.95, "Mensal", "CMP", CMP_, "disposição de lotes de MP", "Lotes 'Accepted' ÷ lotes recebidos", "pct1"),
    ("KPI-Q-09", "Tempo de resposta dos fornecedores a reclamações (SCAR)", "Dias_Resposta_SCAR", "dias", "Menor", 7, "Mensal", "CMP", CMP_, "reclamações a fornecedores", "Média dos dias até resposta", "num1"),
    ("KPI-Q-10", "CAPA fechadas no prazo", "CAPA_No_Prazo", "%", "Maior", 0.85, "Mensal", "QUA", GQ, "CAPA com prazo no mês", "CAPA com prazo no mês fechadas até ao prazo ÷ CAPA com prazo no mês", "pct1"),
    ("KPI-Q-11", "Eficácia das CAPA", "CAPA_Eficacia", "%", "Maior", 0.80, "Mensal", "QUA", GQ, "CAPA fechadas no mês com eficácia avaliada", "Eficazes ÷ (eficazes + não eficazes)", "pct1"),
    ("KPI-Q-12", "Lotes libertados por concessão", "Taxa_Concessao", "%", "Menor", 0.010, "Mensal", "LAB", GQ, "disposição de lotes", "Lotes 'Aprovado por concessão' ÷ lotes decididos", "pct1"),
    ("KPI-Q-13", "Subgrupos SPC com Cpk ≥ 1,00", "Pct_Cpk_1", "%", "Maior", 0.70, "Mensal", "LAB", GQ, "inspeção por variáveis (frascos e tampas)", "Subgrupos com Cpk ≥ 1,00 ÷ subgrupos (meta de longo prazo: Cpk ≥ 1,33)", "pct1"),
    ("KPI-Q-14", "Índice de satisfação do cliente (CSI)", "—", "%", "Maior", 0.80, "Semestral", "COM", DCOM, "RG-SGQ-15 inquérito", "Satisfação ponderada pela importância", "pct1"),
    ("KPI-Q-15", "Net Promoter Score (NPS)", "—", "pontos", "Maior", 30, "Semestral", "COM", DCOM, "RG-SGQ-15 inquérito", "% promotores − % detratores", "num0"),
    ("KPI-Q-16", "Custo das falhas (interna + externa) em % do valor da produção", "—", "%", "Menor", 0.030, "Mensal", "GES", DG, "RG-SGQ-19 COQ", "(Falha interna + externa) ÷ (produzido × preço médio)", "pct1"),
    ("KPI-Q-17", "Equipamentos de medição com confirmação metrológica válida", "—", "%", "Maior", 1.0, "Mensal", "MET", GQ, "RG-SGQ-09", "Equipamentos válidos ÷ equipamentos em uso", "pct1"),
    ("KPI-Q-18", "Cumprimento do plano de formação", "—", "%", "Maior", 0.90, "Trimestral", "RH", RH_, "RG-SGQ-07", "Ações realizadas ÷ planeadas", "pct1"),
    ("KPI-Q-19", "Cumprimento do programa de auditorias", "—", "%", "Maior", 1.0, "Trimestral", "QUA", GQ, "RG-SGQ-16", "Auditorias realizadas ÷ planeadas até à data", "pct1"),
    ("KPI-Q-20", "Entregas completas e no prazo (OTIF)", "OTIF", "%", "Maior", 0.97, "Mensal", "EXP", LOG, "ERP (simulado — o dataset não tem datas prometidas)", "Linhas entregues completas e na data ÷ linhas", "pct1"),
]

# objetivos da qualidade (6.2): (ID, objetivo, compromisso da política, KPI, meta, prazo, o que fazer (a), recursos (b), responsável (c), quando (d), como avaliar (e), processo, funções/níveis)
OBJETIVOS = [
    ("OBJ-Q-01", "Reduzir a taxa de rejeição interna de 2,3% para 2,0%", "2. Fazer bem à primeira", "KPI-Q-01", 0.020, "2026-12-31",
     "DMAIC IM-002 replicado à injeção; SPC de espessura no sopro; manutenção de moldes por ciclos", "€ 45 000 (DOE, contadores, formação); 1 engenheiro de processo", GPROD, "Mensal até dez/2026",
     "Média móvel de 3 meses ≤ 2,0% no painel", "PCP", "Produção; Engenharia de processo"),
    ("OBJ-Q-02", "Aumentar os lotes aprovados à primeira para ≥ 92%", "2. Fazer bem à primeira", "KPI-Q-02", 0.92, "2026-12-31",
     "Leak tester 100% nas ISBM; ensaio de aderência no arranque; safe launch dos SKU novos", "€ 60 000 (leak testers); 2 inspetores no pico", GQ, "Mensal",
     "FPY de lote do mês ≥ 92% em 3 meses consecutivos", "LAB", "Qualidade; Produção"),
    ("OBJ-Q-03", "Reduzir as reclamações para ≤ 3,0 por milhão de unidades expedidas", "3. Ouvir o cliente", "KPI-Q-04", 3.0, "2027-06-30",
     "8D em todas as reclamações críticas; poka-yoke na expedição; visão artificial na HF-001", "€ 85 000 (visão); equipa 8D", DCOM, "Mensal",
     "CPMU médio de 6 meses ≤ 3,0", "COM", "Comercial; Qualidade; Logística"),
    ("OBJ-Q-04", "Atingir Cpk ≥ 1,00 em 70% dos subgrupos (hoje 46%; etapa para Cpk ≥ 1,33)", "2. Fazer bem à primeira", "KPI-Q-13", 0.70, "2027-03-31",
     "Estudos de capacidade por característica crítica; centragem de processo; MSA nas características sem estudo", "Software SPC; técnico de metrologia", GQ, "Mensal",
     "% de subgrupos com Cpk ≥ 1,00", "LAB", "Qualidade; Engenharia de processo"),
    ("OBJ-Q-05", "Fechar ≥ 85% das CAPA no prazo e ter ≥ 80% eficazes", "7. Melhorar continuamente", "KPI-Q-10", 0.85, "2026-12-31",
     "Revisão semanal de CAPA; 8D para NC maiores; verificação de eficácia aos 90 dias", "4 h/semana do comité de CAPA", GQ, "Semanal / mensal",
     "KPI-Q-10 e KPI-Q-11 no painel", "QUA", "Todos os donos de CAPA"),
    ("OBJ-Q-06", "Atingir CSI ≥ 80% e NPS ≥ 30 no inquérito de clientes", "3. Ouvir o cliente", "KPI-Q-14", 0.80, "2027-01-31",
     "Plano de ação por atributo com lacuna; visita anual aos 5 maiores clientes", "Tempo do Key Account", DCOM, "Semestral",
     "Resultado do inquérito de dez/2026", "COM", "Comercial"),
    ("OBJ-Q-07", "Aumentar os lotes de MP aceites sem derrogação para ≥ 95%", "4. Fornecedores", "KPI-Q-08", 0.95, "2026-12-31",
     "Aprovação condicional do SUP-005; scorecard mensal; auditorias a SUP-004 e SUP-009", "Auditor de fornecedores; ensaios", CMP_, "Mensal",
     "Lotes aceites ≥ 95% em 3 meses", "CMP", "Compras; Qualidade"),
    ("OBJ-Q-08", "Entregar ≥ 97% das linhas completas e no prazo (OTIF)", "3. Ouvir o cliente", "KPI-Q-20", 0.97, "2026-12-31",
     "Plano de capacidade set–nov; leitura de código de barras na carga; stock de segurança de resinas", "Planeador adicional no pico", LOG, "Mensal",
     "OTIF mensal ≥ 97%", "EXP", "Logística; Planeamento"),
]

# plano de monitorização e medição (9.1.1): (ID, o que monitorizar (a), método (b), quando medir (c), quando analisar (d), responsável, registo, KPI)
PLANO_MM = [
    ("PMM-01", "Características do produto (dimensionais, peso, espessura)", "Inspeção por variáveis ISO 3951; cartas X̄-R; Cpk", "A cada 30 min – 2 h (plano de controlo)", "Por turno (reação) e mensal (capacidade)", INSP, "RG-SGQ-13 / SPC", "KPI-Q-13"),
    ("PMM-02", "Características por atributos (visuais, fuga, rosca, anel)", "Amostragem ISO 2859-1:2026, nível II, AQL por classe", "Por lote", "Por lote (libertação) e mensal (ppm)", INSP, "RG-SGQ-13 tbl_libertacao", "KPI-Q-02"),
    ("PMM-03", "Parâmetros de processo críticos (temperatura, velocidade, arrefecimento)", "Registo automático no MES; limites do DOE", "Contínuo", "Diário", EPROC, "fact_process_parameters", "KPI-Q-01"),
    ("PMM-04", "Rejeição e sucata por máquina", "Contagem no MES", "Por ordem de fabrico", "Diário (reunião de produção) e mensal", GPROD, "fact_production", "KPI-Q-01"),
    ("PMM-05", "OEE e paragens", "MES (disponibilidade, desempenho, qualidade)", "Contínuo", "Diário e mensal", GPROD, "fact_production / fact_downtime", "KPI-Q-07"),
    ("PMM-06", "Matéria-prima recebida", "Ensaios de receção (MFI, densidade, humidade)", "Por lote recebido", "Mensal (scorecard)", TLAB, "RG-SGQ-12", "KPI-Q-08"),
    ("PMM-07", "Satisfação do cliente", "Inquérito CSI/NPS/CES + reclamações + reuniões", "Semestral (inquérito); contínuo (reclamações)", "Semestral e revisão pela gestão", DCOM, "RG-SGQ-15", "KPI-Q-14"),
    ("PMM-08", "Reclamações de cliente", "Registo ISO 10002; 8D", "Por ocorrência", "Mensal (Pareto, CPMU)", DCOM, "RG-SGQ-15", "KPI-Q-04"),
    ("PMM-09", "Desempenho dos fornecedores", "Scorecard ponderado", "Mensal", "Semestral (reavaliação)", CMP_, "RG-SGQ-12", "KPI-Q-08"),
    ("PMM-10", "Eficácia das ações corretivas", "Verificação de eficácia aos 90 dias", "Por CAPA", "Mensal", GQ, "RG-SGQ-18", "KPI-Q-11"),
    ("PMM-11", "Eficácia das ações para riscos e oportunidades", "Método definido em cada risco/oportunidade", "Conforme a ação", "Trimestral e revisão pela gestão", GQ, "RG-SGQ-04", "—"),
    ("PMM-12", "Estado metrológico dos equipamentos", "Calibração/verificação e MSA", "Conforme intervalo", "Mensal", "Técnico(a) de Metrologia", "RG-SGQ-09", "KPI-Q-17"),
    ("PMM-13", "Custo da qualidade", "Método PAF (prevenção, avaliação, falhas)", "Mensal", "Trimestral", DG, "RG-SGQ-19", "KPI-Q-16"),
    ("PMM-14", "Eficácia do SGQ (auditorias)", "Auditoria interna ISO 19011:2026", "Programa anual", "Após cada auditoria e anual", GQ, "RG-SGQ-16", "KPI-Q-19"),
]


def base_mensal():
    p = Q.production()
    p["Mes"] = Q.monthly(p, "Date")
    prod = p.groupby("Mes").agg(Produzido=("ProducedQty", "sum"), Rejeitado=("RejectedQty", "sum"), OEE_Soma=("OEE", "sum"), Ordens=("WorkOrder", "count"))
    lots = Q.lot_dispositions()
    lots["Mes"] = Q.monthly(lots, "ProductionDate")
    lt = lots.groupby("Mes").agg(Lotes_Decididos=("Lote", "count"), Lotes_1a=("DispositionDetail", lambda s: (s == "Approved - First Pass").sum()),
                                 Lotes_Concessao=("DispositionDetail", lambda s: (s == "Approved - Released on Deviation").sum()),
                                 Lotes_Rejeitados=("FinalLotDecision", lambda s: (s == "Rejected").sum()))
    s = Q.sales()
    s["Mes"] = Q.monthly(s, "Date")
    sl = s.groupby("Mes").agg(Expedido=("ShippedQty", "sum"), Vendas_EUR=("TotalValueEUR", "sum"), Linhas_Expedidas=("SalesOrderId", "count"))
    c = Q.complaints()
    c["Mes"] = Q.monthly(c, "Date")
    c["Serv"] = c["DefectType"].map(Q.NATUREZA).eq("Serviço / logística")
    cl = c.groupby("Mes").agg(Reclamacoes=("ComplaintId", "count"), Reclamacoes_Servico=("Serv", "sum"), Qtd_Afetada=("QtyAffected", "sum"),
                              Reclamacoes_Criticas=("Severity", lambda x: (x == "Critical").sum()))
    c2 = c[c["Res"].notna()].copy()
    c2["MesR"] = c2["Res"].dt.strftime("%Y-%m")
    c2["Dias"] = (c2["Res"] - pd.to_datetime(c2["Date"])).dt.days
    cr = c2.groupby("MesR").agg(Reclamacoes_Resolvidas=("ComplaintId", "count"), Dias_Resolucao_Soma=("Dias", "sum"))
    rm = Q.rm_lots()
    rm["Mes"] = Q.monthly(rm, "Date")
    rl = rm.groupby("Mes").agg(Lotes_MP=("MaterialLotId", "count"), Lotes_MP_Aceites=("FinalDecision", lambda x: (x == "Accepted").sum()))
    sc = Q.supplier_complaints()
    sc["Mes"] = Q.monthly(sc, "Date")
    scl = sc.groupby("Mes").agg(SCAR=("SupplierComplaintId", "count"), Dias_Resposta_SCAR_Soma=("ResponseDays", "sum"))
    k = Q.capa()
    k["MesDue"] = k["Due"].dt.strftime("%Y-%m")
    k["NoPrazo"] = k["Close"].notna() & (k["Close"] <= k["Due"])
    kd = k.groupby("MesDue").agg(CAPA_Com_Prazo=("CAPAId", "count"), CAPA_Fechadas_No_Prazo=("NoPrazo", "sum"))
    kc = k[k["Close"].notna()].copy()
    kc["MesC"] = kc["Close"].dt.strftime("%Y-%m")
    ke = kc.groupby("MesC").agg(CAPA_Eficazes=("EffectivenessCheck", lambda x: (x == "Effective").sum()),
                                CAPA_Nao_Eficazes=("EffectivenessCheck", lambda x: (x == "Not Effective").sum()))
    vv = []
    for f in ("fact_bottle_inspection_variables_cq_processed.csv", "fact_cap_inspection_variable_cq_processed.csv"):
        v = Q.periodo(Q.rd(f, usecols=["ProductionDate", "Cpk"]), "ProductionDate")
        vv.append(v)
    v = pd.concat(vv)
    v["Mes"] = Q.monthly(v, "ProductionDate")
    vl = v.groupby("Mes").agg(Subgrupos_SPC=("Cpk", "count"), Subgrupos_Cpk_1=("Cpk", lambda x: (x >= 1.0).sum()))
    df = pd.DataFrame(index=MESES)
    for t in (prod, lt, sl, cl, cr, rl, scl, kd, ke, vl):
        df = df.join(t)
    df = df.fillna(0)
    # OTIF simulado (o dataset não tem datas prometidas): 97,5% base, −0,5 pp por reclamação de atraso/quantidade no mês
    late = c[c["DefectType"].isin(["Late Delivery", "Short Shipment (Quantity Shortfall)"])].groupby("Mes").size().reindex(MESES).fillna(0)
    rng = np.random.default_rng(9001)
    df["Linhas_OTIF"] = (df["Linhas_Expedidas"] * (0.975 - 0.005 * late.values + rng.normal(0, 0.003, len(MESES)))).round()
    df.index.name = "Mes"
    return df.reset_index()


def build(out):
    b = Book("RG-SGQ-05", "Objetivos da Qualidade, KPI e Plano de Monitorização e Medição",
             activities="Estabelecer objetivos da qualidade mensuráveis e o planeamento para os atingir; definir o que se monitoriza, como, quando se mede e quando se analisa; acompanhar os KPI mensais.",
             clauses="6.2.1 a)–h) Objetivos da qualidade (disponíveis como informação documentada); 6.2.2 a)–e) planeamento; 9.1.1 a)–d) monitorização e medição (evidência dos resultados); 9.1.3 análise e avaliação; 5.1.1 e)",
             purpose=f"Base mensal de desempenho da qualidade {PER_INI[:7]} a {PER_FIM[:7]} agregada do dataset (produção, lotes, vendas, reclamações, matérias-primas, fornecedores, CAPA, SPC) e 13 KPI mensais calculados por fórmula, com painel de estado face às metas, objetivos SMART com o plano 6.2.2 e o plano de monitorização e medição 9.1.1.",
             links=[("RG-SGQ-03 Política", "Cada objetivo liga a um compromisso da política (6.2.1 a)."), ("RG-SGQ-04", "KPI usados para avaliar a eficácia das ações de risco."),
                    ("RG-SGQ-15 / RG-SGQ-19", "KPI semestrais (CSI, NPS) e custo da qualidade."), ("RG-SGA-05", "Objetivos ambientais do SGI (mesma estrutura SMART).")],
             guidance=[("ISO/TC 176 APG — Policy and objectives", "Objetivos mensuráveis, com responsável, prazo, recursos e método de avaliação — tbl_objetivos colunas 6.2.2 a)–e)."),
                       ("Academy — cap. 157 (VoC → CTQ → KPI) e cap. 180 (DPU, DPMO, FPY)", "Ligação cliente → CTQ → KPI → meta; métricas de rendimento."),
                       ("iso9001help.co.uk — Monitoring and measurement", "Plano de monitorização com o quê/como/quando medir/quando analisar e registo da evidência.")])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Polaridade", ["Maior", "Menor"])
    b.add_list("Frequencia", ["Mensal", "Trimestral", "Semestral", "Anual"])

    df = base_mensal()
    bcols = [col("Mes", 8, desc="Mês (aaaa-mm).", key="PK")]
    fmts = {"OEE_Soma": "num", "Vendas_EUR": "eur"}
    desc = {"Produzido": "Unidades produzidas", "Rejeitado": "Unidades rejeitadas", "OEE_Soma": "Soma do OEE das ordens", "Ordens": "N.º de ordens de fabrico",
            "Lotes_Decididos": "Lotes com decisão de libertação", "Lotes_1a": "Lotes aprovados à primeira", "Lotes_Concessao": "Lotes aprovados por concessão",
            "Lotes_Rejeitados": "Lotes rejeitados", "Expedido": "Unidades expedidas", "Vendas_EUR": "Vendas (€)", "Linhas_Expedidas": "Linhas de encomenda expedidas",
            "Reclamacoes": "Reclamações recebidas", "Reclamacoes_Servico": "Reclamações de serviço/logística", "Qtd_Afetada": "Unidades afetadas reclamadas",
            "Reclamacoes_Criticas": "Reclamações críticas", "Reclamacoes_Resolvidas": "Reclamações resolvidas no mês", "Dias_Resolucao_Soma": "Σ dias de resolução",
            "Lotes_MP": "Lotes de MP recebidos", "Lotes_MP_Aceites": "Lotes de MP aceites sem derrogação", "SCAR": "Reclamações a fornecedores",
            "Dias_Resposta_SCAR_Soma": "Σ dias de resposta dos fornecedores", "CAPA_Com_Prazo": "CAPA com prazo no mês", "CAPA_Fechadas_No_Prazo": "CAPA fechadas até ao prazo",
            "CAPA_Eficazes": "CAPA fechadas eficazes", "CAPA_Nao_Eficazes": "CAPA fechadas não eficazes", "Subgrupos_SPC": "Subgrupos SPC (variáveis)",
            "Subgrupos_Cpk_1": "Subgrupos com Cpk ≥ 1,00", "Linhas_OTIF": "Linhas entregues completas e no prazo (SIMULADO)"}
    for c_ in df.columns[1:]:
        bcols.append(col(c_, 11, fmts.get(c_, "num0"), desc=desc.get(c_, c_) + " — agregado do dataset." if c_ != "Linhas_OTIF" else desc[c_]))
    rows = df.to_dict("records")
    for r in rows:
        for k_, v_ in r.items():
            if k_ != "Mes":
                r[k_] = float(v_) if k_ in ("OEE_Soma", "Vendas_EUR") else int(v_)
    b.table("Base_Mensal", "tbl_base_mensal", bcols, rows, "Base mensal de desempenho agregada do dataset (factos de entrada dos KPI).",
            title="BASE MENSAL DE DESEMPENHO DA QUALIDADE — dados do dataset",
            subtitle=f"{PER_INI} a {PER_FIM} · Uma linha por mês · Linhas_OTIF é simulado (o dataset não tem data prometida)", row_height=16)

    B = lambda c_: f"INDEX(tbl_base_mensal[{c_}],MATCH(@Mes@,tbl_base_mensal[Mes],0))"
    kcols = [col("Mes", 8, desc="Mês.", key="PK / FK → tbl_base_mensal"),
             col("Taxa_Rejeicao", 9, "pct1", f=f'=IFERROR({B("Rejeitado")}/{B("Produzido")},"")', desc="KPI-Q-01."),
             col("FPY_Lotes", 9, "pct1", f=f'=IFERROR({B("Lotes_1a")}/{B("Lotes_Decididos")},"")', desc="KPI-Q-02."),
             col("PPM_Cliente", 9, "num0", f=f'=IFERROR({B("Qtd_Afetada")}/{B("Expedido")}*1000000,"")', desc="KPI-Q-03."),
             col("CPMU", 8, "num", f=f'=IFERROR({B("Reclamacoes")}/{B("Expedido")}*1000000,"")', desc="KPI-Q-04."),
             col("Reclamacoes_Servico", 9, "num0", f=f'={B("Reclamacoes_Servico")}', desc="KPI-Q-05."),
             col("Dias_Resolucao", 9, "num1", f=f'=IFERROR({B("Dias_Resolucao_Soma")}/{B("Reclamacoes_Resolvidas")},"")', desc="KPI-Q-06."),
             col("OEE", 8, "pct1", f=f'=IFERROR({B("OEE_Soma")}/{B("Ordens")},"")', desc="KPI-Q-07."),
             col("Lotes_MP_Aceites", 9, "pct1", f=f'=IFERROR({B("Lotes_MP_Aceites")}/{B("Lotes_MP")},"")', desc="KPI-Q-08."),
             col("Dias_Resposta_SCAR", 9, "num1", f=f'=IFERROR({B("Dias_Resposta_SCAR_Soma")}/{B("SCAR")},"")', desc="KPI-Q-09."),
             col("CAPA_No_Prazo", 9, "pct1", f=f'=IFERROR({B("CAPA_Fechadas_No_Prazo")}/{B("CAPA_Com_Prazo")},"")', desc="KPI-Q-10."),
             col("CAPA_Eficacia", 9, "pct1", f=f'=IFERROR({B("CAPA_Eficazes")}/({B("CAPA_Eficazes")}+{B("CAPA_Nao_Eficazes")}),"")', desc="KPI-Q-11."),
             col("Taxa_Concessao", 9, "pct1", f=f'=IFERROR({B("Lotes_Concessao")}/{B("Lotes_Decididos")},"")', desc="KPI-Q-12."),
             col("Pct_Cpk_1", 9, "pct1", f=f'=IFERROR({B("Subgrupos_Cpk_1")}/{B("Subgrupos_SPC")},"")', desc="KPI-Q-13."),
             col("OTIF", 8, "pct1", f=f'=IFERROR({B("Linhas_OTIF")}/{B("Linhas_Expedidas")},"")', desc="KPI-Q-20 (simulado).")]
    b.table("KPI_Mensal", "tbl_kpi_mensal", kcols, [dict(Mes=m) for m in MESES], "KPI mensais calculados por fórmula a partir da base mensal (9.1.1 — evidência dos resultados).",
            title="KPI MENSAIS DA QUALIDADE — calculados", subtitle="Todas as colunas são fórmulas sobre tbl_base_mensal · Metas e estado no Painel_KPI", row_height=16)

    tk = b.tables["tbl_kpi_mensal"]
    lc = get_column_letter(len(tk["colmap"]))
    hdr = f"KPI_Mensal!$A${tk['hr']}:${lc}${tk['hr']}"
    doze = f"KPI_Mensal!$A${tk['first']}:${lc}${tk['first'] + 11}"   # 12 primeiros meses (o nome da tabela sozinho dá #NAME? em ficheiros gerados)
    BASE_F = f'=IF(OR(@ID_KPI@="",@Coluna_Mensal@="—"),"",IFERROR(AVERAGE(INDEX({doze},0,MATCH(@Coluna_Mensal@,{hdr},0))),""))'
    # mesmos nomes de coluna do RG-SGA-05 tbl_kpi (Nome, Formula_Calculo, Responsavel, ID_OBJ, ID_MED); colunas só do SGQ no fim
    ccols = [col("ID_KPI", 9, key="PK", desc="Identificador do indicador."), col("Nome", 38, desc="Nome do indicador."),
             col("Formula_Calculo", 40, desc="Fórmula de cálculo (definição operacional)."), col("Unidade", 9, desc="Unidade."),
             col("Polaridade", 8, dv="Polaridade", desc="Maior ou menor é melhor."), col("Frequencia", 10, dv="Frequencia", desc="Frequência de cálculo."),
             col("Fonte_Dados", 32, desc="Origem dos dados."), col("Responsavel", 24, dv="Funcao", desc="Responsável pelo indicador."),
             col("Meta", 8, "num", desc="Meta (percentagens como fração)."),
             col("Baseline", 9, "num", f=BASE_F, desc="Linha de base: média dos 12 primeiros meses do dataset (jul/2025–jun/2026) em tbl_kpi_mensal; vazio para KPI de outros registos."),
             col("ID_OBJ", 9, f='=IFERROR(INDEX(tbl_objetivos[ID_OBJ],MATCH(@ID_KPI@,tbl_objetivos[ID_KPI],0)),"")', desc="Objetivo que o indicador mede (1.º encontrado).", key="FK → tbl_objetivos"),
             col("ID_MED", 8, f='=IFERROR(INDEX(tbl_plano_monitorizacao[ID_MED],MATCH(@ID_KPI@,tbl_plano_monitorizacao[ID_KPI],0)),"")', desc="Linha do plano de monitorização que alimenta o KPI.", key="FK → tbl_plano_monitorizacao"),
             col("Processo", 7, dv="Processo", desc="[Só SGQ] Processo."),
             col("Coluna_Mensal", 16, desc="[Só SGQ] Coluna em tbl_kpi_mensal ('—' se vem de outro registo).")]
    krows = [dict(ID_KPI=k[0], Nome=k[1], Coluna_Mensal=k[2], Unidade=k[3], Polaridade=k[4], Meta=k[5], Frequencia=k[6], Processo=k[7], Responsavel=k[8],
                  Fonte_Dados=k[9], Formula_Calculo=k[10]) for k in KPIS]
    b.table("Catalogo_KPI", "tbl_kpi", ccols, krows, "Catálogo de indicadores do SGQ (definição, meta, dono, fonte).", row_height=30)

    ws = b.sheet("Painel_KPI", "Painel calculado: último mês, média de 12 meses, tendência de 6 meses e estado face à meta de cada KPI mensal; gráficos.", tab_color="C00000")
    title(ws, "PAINEL DE KPI DA QUALIDADE — calculado", f"Último mês = {MESES[-1]} · Estado: verde cumpre a meta; vermelho não cumpre · Tendência = declive dos últimos 6 meses (por mês)")
    heads = ["ID_KPI", "KPI", "Meta", "Último mês", "Média 12 meses", "Tendência 6 m", "Polaridade", "Estado", "A melhorar?"]
    header_row(ws, 4, heads, widths=[10, 44, 10, 11, 12, 12, 10, 12, 12])
    mens = [k for k in KPIS if k[2] != "—"]
    n = len(MESES)
    for i, k in enumerate(mens):
        r = 5 + i
        fmt = NUMFMT[k[11]]
        colref = f"tbl_kpi_mensal[{k[2]}]"
        cell(ws, r, 1, k[0])
        cell(ws, r, 2, k[1])
        cell(ws, r, 3, f'=INDEX(tbl_kpi[Meta],MATCH(A{r},tbl_kpi[ID_KPI],0))', fmt=fmt)
        cell(ws, r, 4, f'=INDEX({colref},{n})', fmt=fmt)
        cell(ws, r, 5, f'=AVERAGE(INDEX({colref},{n - 11}):INDEX({colref},{n}))', fmt=fmt)
        cell(ws, r, 6, f'=SLOPE(INDEX({colref},{n - 5}):INDEX({colref},{n}),{{1;2;3;4;5;6}})', fmt="0.0000" if fmt.endswith("%") else "0.00")
        cell(ws, r, 7, f'=INDEX(tbl_kpi[Polaridade],MATCH(A{r},tbl_kpi[ID_KPI],0))')
        cell(ws, r, 8, f'=IF(G{r}="Maior",IF(D{r}>=C{r},"Cumpre","Não cumpre"),IF(D{r}<=C{r},"Cumpre","Não cumpre"))')
        cell(ws, r, 9, f'=IF(G{r}="Maior",IF(F{r}>0,"A melhorar","A piorar"),IF(F{r}<0,"A melhorar","A piorar"))')
    last = 4 + len(mens)
    for L, spec in (("H", {"Não cumpre": "red", "Cumpre": "green"}), ("I", {"A piorar": "orange", "A melhorar": "green"})):
        for txt, colr in spec.items():
            bg, fg = CF_COLORS[colr]
            ws.conditional_formatting.add(f"{L}5:{L}{last}", FormulaRule(formula=[f'ISNUMBER(SEARCH("{txt}",{L}5))'], fill=PatternFill("solid", fgColor=bg), font=Font(name=FONT, color=fg, bold=True)))
    cell(ws, last + 1, 1, "KPI semestrais / de outros registos: KPI-Q-14 e KPI-Q-15 (RG-SGQ-15), KPI-Q-16 (RG-SGQ-19), KPI-Q-17 (RG-SGQ-09), KPI-Q-18 (RG-SGQ-07), KPI-Q-19 (RG-SGQ-16).",
         border=False, wrap=False).font = F_SUB
    # gráficos (séries da tabela de KPI mensais)
    kws = b.wb["KPI_Mensal"]
    t = b.tables["tbl_kpi_mensal"]
    cats = Reference(kws, min_col=1, min_row=t["first"], max_row=t["last"])
    for pos, (cname, ttl, yfmt) in zip((f"A{last + 3}", f"F{last + 3}"), (("Taxa_Rejeicao", "Taxa de rejeição interna (meta 2,0%)", "0.00%"), ("CPMU", "Reclamações por milhão expedido (meta 3,0)", "0.0"))):
        ch = LineChart()
        ch.title, ch.height, ch.width = ttl, 7, 13
        ci = list(t["colmap"]).index(cname) + 1
        ch.add_data(Reference(kws, min_col=ci, min_row=t["hr"], max_row=t["last"]), titles_from_data=True)
        ch.set_categories(cats)
        ch.y_axis.numFmt = yfmt
        ch.legend = None
        fix_chart(ch)
        ws.add_chart(ch, pos)

    # mesmos nomes de coluna do RG-SGA-05 tbl_objetivos (ID_OBJ, Declaracao_Objetivo, Indicador_KPI, Meta_Numerica, Dias_ate_Prazo...)
    ocols = [col("ID_OBJ", 9, key="PK", desc="Identificador do objetivo da qualidade."),
             col("Compromisso_Politica", 20, desc="Compromisso da política a que dá corpo (6.2.1 a)."),
             col("Declaracao_Objetivo", 42, desc="Objetivo mensurável (6.2.1 b): verbo + indicador + meta + prazo."),
             col("ID_KPI", 9, desc="Indicador (régua).", key="FK → tbl_kpi"),
             col("Indicador_KPI", 26, f='=IFERROR(INDEX(tbl_kpi[Nome],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0))&" ("&INDEX(tbl_kpi[Unidade],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0))&")","")', desc="Nome e unidade do KPI."),
             col("Baseline", 9, "num", f='=IF(@ID_OBJ@="","",IFERROR(INDEX(tbl_kpi[Baseline],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0)),""))', desc="Linha de base (do catálogo de KPI)."),
             col("Meta_Numerica", 9, "num", desc="Valor numérico do KPI a atingir (percentagens como fração)."),
             col("Prazo", 11, "date", desc="Quando será concluído (6.2.2 d)."),
             col("O_que_Fazer", 44, desc="O que vai ser feito (6.2.2 a)."), col("Recursos", 30, desc="Recursos (6.2.2 b)."),
             col("Responsavel", 24, dv="Funcao", desc="Quem é responsável (6.2.2 c)."),
             col("Estado", 12, f='=IF(@ID_OBJ@="","",IF(ISNUMBER(@Valor_Atual@),IF(@Polaridade@="Maior",IF(@Valor_Atual@>=@Meta_Numerica@,"Atingido","Em curso"),IF(@Valor_Atual@<=@Meta_Numerica@,"Atingido","Em curso")),"Semestral"))',
                 desc="Estado face à meta."),
             col("Valor_Atual", 10, "num", f='=IF(@ID_OBJ@="","",IFERROR(INDEX(Painel_KPI!$D:$D,MATCH(@ID_KPI@,Painel_KPI!$A:$A,0)),"ver registo"))', desc="Último valor do painel."),
             col("Progresso", 9, "pct", f='=IF(@ID_OBJ@="","",IF(OR(NOT(ISNUMBER(@Valor_Atual@)),NOT(ISNUMBER(@Baseline@)),@Meta_Numerica@=""),"",IF(@Meta_Numerica@=@Baseline@,"",MAX(-1,MIN(1,(@Valor_Atual@-@Baseline@)/(@Meta_Numerica@-@Baseline@))))))',
                 desc="Percentagem do caminho baseline → meta já percorrido (negativo = afastou-se)."),
             col("Dias_ate_Prazo", 9, "int", f='=IF(@ID_OBJ@="","",@Prazo@-DataRef)', desc="Dias até ao prazo."),
             col("S_Especifico", 8, f='=IF(@ID_OBJ@="","",IF(AND(LEN(@Declaracao_Objetivo@)>40,@ID_KPI@<>""),"✔","✘"))', desc="S: declaração clara e ligada a um indicador."),
             col("M_Mensuravel", 8, f='=IF(@ID_OBJ@="","",IF(ISNUMBER(@Meta_Numerica@),"✔","✘"))', desc="M: meta numérica."),
             col("A_Atingivel", 8, f='=IF(@ID_OBJ@="","",IF(AND(@Recursos@<>"",@Responsavel@<>"",@O_que_Fazer@<>""),"✔","✘"))', desc="A: recursos, responsável e ações planeadas (6.2.2 a–c)."),
             col("R_Relevante", 8, f='=IF(@ID_OBJ@="","",IF(AND(@Compromisso_Politica@<>"",@Processo@<>""),"✔","✘"))', desc="R: nasce da política e de um processo."),
             col("T_Temporal", 8, f='=IF(@ID_OBJ@="","",IF(ISNUMBER(@Prazo@),"✔","✘"))', desc="T: data limite (6.2.2 d)."),
             col("Validacao_SMART", 12, f='=IF(@ID_OBJ@="","",IF((@S_Especifico@="✔")+(@M_Mensuravel@="✔")+(@A_Atingivel@="✔")+(@R_Relevante@="✔")+(@T_Temporal@="✔")=5,"SMART","Rever"))',
                 desc="SMART se os 5 critérios estiverem cumpridos."),
             col("Quando_Acompanhar", 16, desc="[Só SGQ] Frequência de acompanhamento."), col("Como_Avaliar", 30, desc="[Só SGQ] Como os resultados são avaliados (6.2.2 e)."),
             col("Processo", 7, dv="Processo", desc="[Só SGQ] Processo."), col("Funcoes_Niveis", 22, desc="[Só SGQ] Funções e níveis a que se aplica (6.2.1)."),
             col("Polaridade", 8, f='=IF(@ID_OBJ@="","",IFERROR(INDEX(tbl_kpi[Polaridade],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0)),""))', desc="Da definição do KPI."),
             col("Comunicado", 10, desc="[Só SGQ] Como foi comunicado (6.2.1 e)."), col("Data_Revisao", 11, "date", desc="Última atualização (6.2.1 f).")]
    OBJ_N = ["ID_OBJ", "Declaracao_Objetivo", "Compromisso_Politica", "ID_KPI", "Meta_Numerica", "Prazo", "O_que_Fazer", "Recursos", "Responsavel",
             "Quando_Acompanhar", "Como_Avaliar", "Processo", "Funcoes_Niveis", "Comunicado", "Data_Revisao"]
    orows = rows_from(OBJ_N, [o + ("Quadro de KPI por área + reunião geral", "2026-09-28") for o in OBJETIVOS], dates=("Prazo", "Data_Revisao"))
    b.table("Objetivos_Qualidade", "tbl_objetivos", ocols, orows, "Objetivos da qualidade e planeamento para os atingir (6.2.1 e 6.2.2).",
            title="OBJETIVOS DA QUALIDADE 2026–2027 E PLANEAMENTO (6.2)", subtitle="Disponíveis como informação documentada (6.2.1 g) · Valor atual e estado calculados a partir do Painel_KPI",
            cf=[("Estado", {"Atingido": "green", "Em curso": "orange", "Semestral": "gray"}), ("Validacao_SMART", {"SMART": "green", "Rever": "red"})], row_height=48, freeze_col=2)

    # mesmos nomes de coluna do RG-SGA-13 tbl_plano_monitorizacao (ID_MED, O_Que_Medir, Como_Medir, Quando_Medir, Quem_Mede, ID_KPI)
    pcols = [col("ID_MED", 8, key="PK", desc="Linha do plano de monitorização."), col("O_Que_Medir", 40, desc="O que monitorizar e medir (9.1.1 a)."),
             col("Como_Medir", 40, desc="Métodos de monitorização, medição, análise e avaliação (9.1.1 b)."),
             col("Quando_Medir", 26, desc="Quando monitorizar e medir (9.1.1 c)."), col("Quem_Mede", 24, dv="Funcao", desc="Responsável pela recolha."),
             col("ID_KPI", 9, desc="KPI alimentado.", key="FK → tbl_kpi", req=False),
             col("Quando_Analisar", 26, desc="[Só SGQ] Quando analisar e avaliar os resultados (9.1.1 d)."),
             col("Registo_Evidencia", 24, desc="[Só SGQ] Onde fica a evidência dos resultados.")]
    PMM_N = ["ID_MED", "O_Que_Medir", "Como_Medir", "Quando_Medir", "Quando_Analisar", "Quem_Mede", "Registo_Evidencia", "ID_KPI"]
    b.table("Plano_Monitorizacao", "tbl_plano_monitorizacao", pcols, rows_from(PMM_N, PLANO_MM),
            "Plano de monitorização, medição, análise e avaliação (9.1.1 a–d) — mesma estrutura do RG-SGA-13.", title="PLANO DE MONITORIZAÇÃO E MEDIÇÃO (9.1.1)", row_height=32)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
