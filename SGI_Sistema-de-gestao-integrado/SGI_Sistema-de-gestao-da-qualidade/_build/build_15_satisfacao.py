"""RG-SGQ-15 — Reclamações de clientes (ISO 10002:2018) e monitorização da satisfação do cliente (ISO 10004:2018).
ISO 9001:2026 8.2.1 c), 9.1.2 (métodos para obter, monitorizar e rever a informação), 9.1.3 b), 10.2 Nota (reclamações como fonte de NC).
Reclamações reais do dataset (fact_customer_complaints) com o ciclo de tratamento da ISO 10002; inquérito semestral simulado coerente com as reclamações."""
import datetime as dt
import numpy as np
import pandas as pd
from sgqlib import *
from dimsq import *
import qdata as Q

ATRIB = [("AT-1", "Qualidade do produto (conformidade, defeitos)"), ("AT-2", "Cumprimento de prazos e quantidades"), ("AT-3", "Resposta a reclamações"),
         ("AT-4", "Apoio técnico e desenvolvimento"), ("AT-5", "Documentação e certificados (FCM, PPWR, CoC)"), ("AT-6", "Comunicação comercial"), ("AT-7", "Preço / valor")]
IMP = {"AT-1": 4.9, "AT-2": 4.6, "AT-3": 4.2, "AT-4": 3.8, "AT-5": 4.0, "AT-6": 3.5, "AT-7": 4.1}
OITO_D = {"CC-20000": "8D-26-01", "CC-20114": "8D-26-02", "CC-20071": "8D-26-03", "CC-20113": "8D-26-04", "CC-20090": "8D-26-05"}

FONTES = [
    ("FB-01", "Inquérito semestral (CSI, NPS, CES)", "ISO 10004 — medição direta", "Semestral", DCOM, "tbl_inquerito"),
    ("FB-02", "Reclamações de clientes", "ISO 10002 — feedback não solicitado", "Contínua", DCOM, "tbl_reclamacoes"),
    ("FB-03", "Scorecards enviados pelos clientes (CUST-001: 82/100; CUST-007: 'B'; CUST-002: 76/100)", "Avaliação do cliente", "Trimestral", "Gestor(a) de Cliente (Key Account)", "Arquivo comercial"),
    ("FB-04", "Reuniões de conta e visitas aos 5 maiores clientes", "Reunião direta", "Semestral", DCOM, "Atas de reunião"),
    ("FB-05", "Auditorias de clientes (CUST-015 out/2026; CUST-017 set/2026)", "Auditoria de 2.ª parte", "Anual", GQ, "RG-SGQ-16"),
    ("FB-06", "Elogios e reconhecimentos (ex.: CUST-013 elogiou a rapidez do 8D em jan/2026)", "Feedback positivo", "Contínua", DCOM, "CRM"),
    ("FB-07", "Devoluções e notas de crédito", "Dados de faturação", "Mensal", "Diretor Financeiro", "ERP"),
    ("FB-08", "Quota de mercado e perda/ganho de referências", "Análise de mercado", "Anual", DCOM, "Plano estratégico"),
]


def reclamacoes_rows():
    c = Q.complaints()
    rng = np.random.default_rng(10002)
    out = []
    for r in c.sort_values("Date").itertuples():
        d0 = dt.date.fromisoformat(r.Date)
        ack = d0 + dt.timedelta(days=int(rng.choice([0, 1, 1, 2, 2, 3, 4])))
        res = r.Res.date() if pd.notna(r.Res) else None
        prim = d0 + dt.timedelta(days=int(rng.integers(3, 12)))
        if res and prim > res:
            prim = res
        if prim > dt.date(2026, 12, 31):
            prim = None   # primeira resposta ainda pendente em 31/12/2026
        proc = Q.NATUREZA[r.DefectType]
        decisao = "Procedente" if rng.random() > 0.08 else "Improcedente"
        acao_cli = {"Produto": "Substituição do lote e crédito", "Serviço / logística": "Entrega complementar / troca"}[proc] if decisao == "Procedente" else "Explicação técnica com evidência"
        sat = int(rng.choice([2, 3, 3, 4, 4, 4, 5, 5])) if res else None
        custo = round(float(r.QtyAffected) * 0.25 + (350 if r.Severity == "Critical" else 120 if r.Severity == "Major" else 40), 2)
        out.append(dict(ID_Reclamacao=r.ComplaintId, Data_Rececao=d0, Mes=r.Date[:7], ID_Cliente=r.CustomerId, Canal=str(rng.choice(["Portal do cliente", "Correio eletrónico", "Key Account"])),
                        Produto=r.ProductId, Processo=Q.T_PROC[r.Process], Ordem=r.WorkOrder, Encomenda=None if pd.isna(r.SalesOrderId) else r.SalesOrderId,
                        Tipo_Defeito=Q.T_DEFEITO[r.DefectType], Natureza=proc, Severidade=Q.T_SEV[r.Severity], Qtd_Afetada=int(r.QtyAffected),
                        Data_Acusacao_Rececao=ack, Data_Primeira_Resposta=prim, Decisao=decisao, Acao_Cliente=acao_cli, ID_8D=OITO_D.get(r.ComplaintId),
                        Data_Fecho=res, Satisfacao_Tratamento=sat, Custo_EUR=custo))
    return out


def inquerito_rows():
    c = Q.complaints()
    s = Q.sales()
    cust = Q.customers()
    cp = (c.groupby("CustomerId").size() / s.groupby("CustomerId").ShippedQty.sum() * 1e6).reindex(cust.CustomerId).fillna(0)
    serv = c[c.DefectType.map(Q.NATUREZA) == "Serviço / logística"].groupby("CustomerId").size().reindex(cust.CustomerId).fillna(0)
    rng = np.random.default_rng(10004)
    rows, nps = [], []
    for onda, off in (("2025-12", 0.0), ("2026-06", 0.15)):
        for cid in cust.CustomerId:
            if cid in ("CUST-015", "CUST-016", "CUST-017", "CUST-018") and onda == "2025-12":
                continue
            if cid in ("CUST-004", "CUST-011") and onda == "2026-06":      # não responderam
                continue
            if cid == "CUST-010" and onda == "2025-12":
                continue
            base = 4.3 + off - 0.12 * cp[cid]
            for a, _ in ATRIB:
                v = base + rng.normal(0, 0.25)
                if a == "AT-2":
                    v -= 0.1 * serv[cid]
                if a == "AT-3":
                    v -= 0.2
                if a == "AT-5" and cid in ("CUST-015", "CUST-016", "CUST-017", "CUST-018"):
                    v -= 0.5
                rows.append(dict(Onda=onda, ID_Cliente=cid, ID_Atributo=a, Importancia=int(np.clip(round(IMP[a] + rng.normal(0, 0.4)), 1, 5)),
                                 Satisfacao=int(np.clip(round(v), 1, 5))))
            n = int(np.clip(round(8.8 + off - 0.25 * cp[cid] + rng.normal(0, 0.9)), 0, 10))
            ces = int(np.clip(round(5.4 + off * 2 - 0.15 * cp[cid] + rng.normal(0, 0.7)), 1, 7))
            nps.append(dict(Onda=onda, ID_Cliente=cid, Nota_Recomendacao_0_10=n, CES_1_7=ces, Comentario=None))
    nps[3]["Comentario"] = "Precisamos de resposta mais rápida às reclamações de rótulo."
    nps[-1]["Comentario"] = "Documentação de conformidade alimentar demorou a chegar."
    return rows, nps


def build(out):
    b = Book("RG-SGQ-15", "Reclamações de Clientes e Satisfação do Cliente",
             activities="Receber, acusar, avaliar, investigar, responder e fechar reclamações (ISO 10002); medir e analisar a satisfação por inquérito semestral e outras fontes (ISO 10004); usar a informação na revisão pela gestão.",
             clauses="8.2.1 c) feedback e reclamações; 9.1.2 satisfação do cliente (métodos para obter, monitorizar e rever); 9.1.3 b); 9.3.2 d4); 10.2 Nota (reclamações como fonte de NC)",
             purpose=f"Registo das {len(Q.complaints())} reclamações reais do dataset ({PER_INI} a {PER_FIM}) com as etapas da ISO 10002 e controlo de prazos; inquérito de satisfação de 2 ondas (dez/2025 e jun/2026) com importância × satisfação por atributo, CSI, NPS e CES calculados por fórmula; outras fontes de perceção do cliente.",
             links=[("RG-SGQ-18 tbl_8d", "Investigação 8D das reclamações críticas (ID_8D)."), ("RG-SGQ-10 tbl_clientes", "Clientes, segmentos e CPMU."),
                    ("RG-SGQ-05 KPI-Q-03/04/05/06/14/15", "Indicadores do cliente.")],
             guidance=[("ISO 10002:2018 (pasta de interpretação)", "Processo: receção → acusação da receção → avaliação inicial → investigação → resposta → comunicação da decisão → fecho; monitorização da satisfação do reclamante com o tratamento."),
                       ("ISO 10004:2018", "Identificar atributos que o cliente valoriza, medir importância e satisfação, analisar lacunas e agir; combinar medição direta e indireta."),
                       ("Academy — cap. 157 (VoC, NPS, CSAT, CES)", "NPS = %promotores (9–10) − %detratores (0–6); CES 2.0 escala 1–7 (maior = mais fácil); matriz importância × desempenho."),
                       ("ISO/TC 176 APG — Customer feedback / complaints", "O auditor verifica se o feedback é analisado e usado para melhorar, não apenas recolhido.")])
    b.add_list("Natureza", ["Produto", "Serviço / logística"])
    b.add_list("Severidade", ["Crítica", "Maior", "Menor"])
    b.add_list("Decisao", ["Procedente", "Improcedente"])
    b.add_list("Canal", ["Portal do cliente", "Correio eletrónico", "Key Account", "Telefone"])
    b.add_list("Onda", ["2025-12", "2026-06"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Funcao", FUNC_NAMES + ["Diretor Financeiro"])

    cols = [col("ID_Reclamacao", 10, key="PK", desc="Reclamação (dataset)."), col("Data_Rececao", 11, "date", desc="Receção (ISO 10002 8.2)."), col("Mes", 8, desc="aaaa-mm."),
            col("ID_Cliente", 9, desc="Cliente.", key="FK → RG-SGQ-10"), col("Canal", 14, dv="Canal", desc="Canal de receção."), col("Produto", 20, desc="Produto (dataset)."),
            col("Processo", 7, dv="Processo", desc="Processo de origem."), col("Ordem", 9, desc="Ordem de fabrico (rastreio)."), col("Encomenda", 9, desc="Encomenda (vazia = lacuna de rastreio).", req=False),
            col("Tipo_Defeito", 30, desc="Tipo (dataset, traduzido)."), col("Natureza", 14, dv="Natureza", desc="Produto ou serviço/logística."), col("Severidade", 8, dv="Severidade", desc="Severidade (avaliação inicial)."),
            col("Qtd_Afetada", 8, "num0", desc="Unidades afetadas."), col("Data_Acusacao_Rececao", 11, "date", desc="Acusação da receção ao cliente (ISO 10002 8.3)."),
            col("Data_Primeira_Resposta", 11, "date", desc="Resposta com contenção (ISO 10002 8.6)."), col("Decisao", 11, dv="Decisao", desc="Procedente / improcedente."),
            col("Acao_Cliente", 26, desc="Ação para o cliente (8.7.1 c)."), col("ID_8D", 9, desc="Investigação 8D (RG-SGQ-18).", key="FK → RG-SGQ-18", req=False),
            col("Data_Fecho", 11, "date", desc="Fecho (vazio se aberta à data de referência).", req=False), col("Satisfacao_Tratamento", 9, "int", desc="Satisfação do reclamante com o tratamento (1–5).", req=False),
            col("Custo_EUR", 9, "eur", desc="Custo estimado (crédito, transporte, triagem, horas)."),
            col("Dias_Acusacao", 7, "int", f='=IF(@ID_Reclamacao@="","",NETWORKDAYS(@Data_Rececao@,@Data_Acusacao_Rececao@)-1)', desc="Dias úteis até acusar a receção (meta ≤ 2)."),
            col("Dias_Resolucao", 7, "int", f='=IF(@ID_Reclamacao@="","",IF(@Data_Fecho@="",DataRef-@Data_Rececao@,@Data_Fecho@-@Data_Rececao@))', desc="Dias até ao fecho (ou até à data de referência)."),
            col("Estado", 10, f='=IF(@ID_Reclamacao@="","",IF(@Data_Fecho@<>"","Fechada",IF(@Dias_Resolucao@>30,"Atrasada","Aberta")))', desc="Estado."),
            col("Controlo_Qualidade", 22, f=('=IF(@ID_Reclamacao@="","",IF(@Dias_Acusacao@>2,"Acusação tardia",IF(AND(@Severidade@="Crítica",@ID_8D@=""),"Crítica sem 8D",'
                                   'IF(@Encomenda@="","Sem encomenda (rastreio)","OK"))))'), desc="Regras ISO 10002 e de rastreio.")]
    rows = reclamacoes_rows()
    b.table("Reclamacoes", "tbl_reclamacoes", cols, rows, "Reclamações de clientes com o ciclo de tratamento da ISO 10002.",
            title="RECLAMAÇÕES DE CLIENTES — TRATAMENTO ISO 10002", subtitle=f"{len(rows)} reclamações reais do dataset · Datas de acusação e resposta simuladas · Prazos, estado e controlo calculados",
            cf=[("Estado", {"Atrasada": "red", "Aberta": "orange", "Fechada": "green"}), ("Severidade", {"Crítica": "red", "Maior": "orange"}),
                ("Controlo_Qualidade", {"tardia": "orange", "sem 8D": "red", "Sem encomenda": "yellow", "OK": "green"})], row_height=15, freeze_col=1)

    irows, nrows = inquerito_rows()
    icols = [col("Onda", 8, dv="Onda", desc="Onda do inquérito."), col("ID_Cliente", 9, desc="Cliente.", key="FK"), col("ID_Atributo", 7, desc="Atributo.", key="FK → tbl_atributos"),
             col("Atributo", 36, f='=IFERROR(INDEX(tbl_atributos[Atributo],MATCH(@ID_Atributo@,tbl_atributos[ID_Atributo],0)),"")', desc="Descrição."),
             col("Importancia", 8, "int", desc="Importância 1–5."), col("Satisfacao", 8, "int", desc="Satisfação 1–5."),
             col("Lacuna", 7, "int", f='=@Importancia@-@Satisfacao@', desc="Importância − satisfação (ISO 10004)."),
             col("Ponderado", 8, "int", f='=@Importancia@*@Satisfacao@', desc="Importância × satisfação (numerador do CSI).")]
    b.table("Inquerito_Respostas", "tbl_inquerito", icols, irows, "Respostas ao inquérito de satisfação por atributo (formato longo).", row_height=15)
    acols = [col("ID_Atributo", 7, key="PK", desc="Atributo."), col("Atributo", 44, desc="Atributo que o cliente valoriza (ISO 10004)."),
             col("Importancia_Media", 9, "num", f='=AVERAGEIFS(tbl_inquerito[Importancia],tbl_inquerito[ID_Atributo],@ID_Atributo@,tbl_inquerito[Onda],"2026-06")', desc="Importância média (jun/2026)."),
             col("Satisfacao_2025_12", 9, "num", f='=AVERAGEIFS(tbl_inquerito[Satisfacao],tbl_inquerito[ID_Atributo],@ID_Atributo@,tbl_inquerito[Onda],"2025-12")', desc="Satisfação média dez/2025."),
             col("Satisfacao_2026_06", 9, "num", f='=AVERAGEIFS(tbl_inquerito[Satisfacao],tbl_inquerito[ID_Atributo],@ID_Atributo@,tbl_inquerito[Onda],"2026-06")', desc="Satisfação média jun/2026."),
             col("Evolucao", 8, "num", f='=@Satisfacao_2026_06@-@Satisfacao_2025_12@', desc="Variação."),
             col("Lacuna", 8, "num", f='=@Importancia_Media@-@Satisfacao_2026_06@', desc="Importância − satisfação."),
             col("Quadrante", 22, f='=IF(@Importancia_Media@>=4,IF(@Satisfacao_2026_06@<4,"Prioridade de melhoria","Manter o desempenho"),IF(@Satisfacao_2026_06@<4,"Baixa prioridade","Possível excesso"))',
                 desc="Matriz importância × desempenho.")]
    b.table("Atributos", "tbl_atributos", acols, [dict(ID_Atributo=a, Atributo=t) for a, t in ATRIB], "Análise importância × satisfação por atributo (ISO 10004).",
            title="SATISFAÇÃO POR ATRIBUTO — IMPORTÂNCIA × DESEMPENHO (ISO 10004)", cf=[("Quadrante", {"Prioridade": "red", "Manter": "green", "excesso": "yellow"}), ("Evolucao", "@<0", "orange")], row_height=20)
    ncols = [col("Onda", 8, dv="Onda", desc="Onda."), col("ID_Cliente", 9, desc="Cliente."), col("Nota_Recomendacao_0_10", 11, "int", desc="Probabilidade de recomendar (0–10)."),
             col("Categoria_NPS", 10, f='=IF(@Nota_Recomendacao_0_10@>=9,"Promotor",IF(@Nota_Recomendacao_0_10@>=7,"Neutro","Detrator"))', desc="Promotor 9–10; neutro 7–8; detrator 0–6."),
             col("CES_1_7", 7, "int", desc="'A Plasticom facilitou a resolução?' (1–7, maior = mais fácil)."), col("Comentario", 44, desc="Comentário livre.", req=False)]
    b.table("NPS_CES", "tbl_nps", ncols, nrows, "Recomendação (NPS) e esforço (CES) por cliente e onda.", row_height=15)

    fcols = [col("ID_Fonte", 7, key="PK", desc="Fonte."), col("Fonte", 60, desc="Fonte de informação sobre a satisfação (9.1.2 Nota)."), col("Tipo", 26, desc="Tipo."),
             col("Frequencia", 11, desc="Frequência."), col("Responsavel", 26, dv="Funcao", desc="Responsável."), col("Registo", 18, desc="Onde está registada.")]
    b.table("Fontes_Satisfacao", "tbl_fontes_satisfacao", fcols, rows_from(input_names(fcols), FONTES), "Métodos para obter e monitorizar a informação sobre a satisfação (9.1.2).", row_height=30)

    ws = b.sheet("Indices_Satisfacao", "Índices calculados por onda: CSI, NPS, CES, taxa de resposta; indicadores ISO 10002 e Pareto das reclamações.", tab_color="C00000")
    title(ws, "ÍNDICES DE SATISFAÇÃO E DESEMPENHO DO TRATAMENTO DE RECLAMAÇÕES — calculado", "CSI = Σ(importância × satisfação) ÷ Σ(importância × 5) · NPS = %promotores − %detratores")
    header_row(ws, 4, ["Indicador", "2025-12", "2026-06", "Meta"], widths=[50, 12, 12, 10])
    I = lambda c_: f"tbl_inquerito[{c_}]"
    N = lambda c_: f"tbl_nps[{c_}]"
    ind = [("CSI — índice de satisfação ponderado (KPI-Q-14)", lambda o: f'=SUMIFS({I("Ponderado")},{I("Onda")},"{o}")/(5*SUMIFS({I("Importancia")},{I("Onda")},"{o}"))', "0.0%", 0.80),
           ("NPS (KPI-Q-15)", lambda o: f'=(COUNTIFS({N("Onda")},"{o}",{N("Categoria_NPS")},"Promotor")-COUNTIFS({N("Onda")},"{o}",{N("Categoria_NPS")},"Detrator"))/COUNTIF({N("Onda")},"{o}")*100', "0", 30),
           ("CES médio (1–7)", lambda o: f'=AVERAGEIFS({N("CES_1_7")},{N("Onda")},"{o}")', "0.0", 5.5),
           ("Clientes que responderam", lambda o: f'=COUNTIF({N("Onda")},"{o}")', "0", None),
           ("Taxa de resposta (clientes ativos: 14 em dez/2025, 18 em jun/2026)", lambda o: f'=COUNTIF({N("Onda")},"{o}")/{14 if o == "2025-12" else 18}', "0%", 0.8)]
    for k, (lab, f, fmt, meta) in enumerate(ind):
        r = 5 + k
        cell(ws, r, 1, lab)
        cell(ws, r, 2, f("2025-12"), fmt=fmt)
        cell(ws, r, 3, f("2026-06"), fmt=fmt)
        cell(ws, r, 4, meta, fmt=fmt)
    R = lambda c_: f"tbl_reclamacoes[{c_}]"
    header_row(ws, 12, ["Tratamento de reclamações (ISO 10002)", "Valor", "", "Meta"])
    ind2 = [("Reclamações no período", f"=COUNTA({R('ID_Reclamacao')})", "0", None),
            ("% com receção acusada em ≤ 2 dias úteis", f'=COUNTIFS({R("Dias_Acusacao")},"<=2",{R("ID_Reclamacao")},"<>")/COUNTA({R("ID_Reclamacao")})', "0%", 0.95),
            ("Tempo médio de resolução das fechadas (dias)", f'=AVERAGEIFS({R("Dias_Resolucao")},{R("Estado")},"Fechada")', "0.0", 20),
            ("Reclamações abertas / atrasadas à data de referência", f'=COUNTIF({R("Estado")},"Aberta")+COUNTIF({R("Estado")},"Atrasada")', "0", None),
            ("Satisfação média com o tratamento (1–5)", f"=AVERAGE({R('Satisfacao_Tratamento')})", "0.0", 4),
            ("% de reclamações de serviço / logística", f'=COUNTIF({R("Natureza")},"Serviço / logística")/COUNTA({R("ID_Reclamacao")})', "0%", None),
            ("Custo total estimado das reclamações (€)", f"=SUM({R('Custo_EUR')})", "#,##0 €", None)]
    for k, (lab, f, fmt, meta) in enumerate(ind2):
        r = 13 + k
        cell(ws, r, 1, lab)
        cell(ws, r, 2, f, fmt=fmt)
        cell(ws, r, 4, meta, fmt=fmt)
    header_row(ws, 22, ["Pareto — tipo de defeito", "N.º", "% acumulada", "Natureza"])
    c = Q.complaints()
    order = c.DefectType.map(Q.T_DEFEITO).value_counts().index.tolist()
    for k, t in enumerate(order):
        r = 23 + k
        cell(ws, r, 1, t)
        cell(ws, r, 2, f'=COUNTIF({R("Tipo_Defeito")},A{r})', fmt="0")
        cell(ws, r, 3, f"=SUM($B$23:B{r})/SUM($B$23:$B${22 + len(order)})", fmt="0%")
        cell(ws, r, 4, f'=IFERROR(INDEX({R("Natureza")},MATCH(A{r},{R("Tipo_Defeito")},0)),"")')
    from openpyxl.chart import BarChart, Reference
    ch = BarChart()
    ch.type, ch.title, ch.height, ch.width = "bar", "Pareto das reclamações por tipo", 9, 14
    ch.add_data(Reference(ws, min_col=2, min_row=22, max_row=22 + len(order)), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=23, max_row=22 + len(order)))
    ch.y_axis.majorGridlines = None
    ch.legend = None
    ch.x_axis.scaling.orientation = "maxMin"
    fix_chart(ch)
    ws.add_chart(ch, "F4")
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
