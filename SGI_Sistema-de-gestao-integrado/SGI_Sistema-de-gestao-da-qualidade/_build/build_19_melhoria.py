"""RG-SGQ-19 — Melhoria contínua e custo da qualidade (ISO 9001:2026 10.1 a)–c), 9.1.3, 5.1.1 g)).
Projetos com os resultados do notebook do projeto (datasets/silver/*_summary.json); custo da qualidade mensal pelo modelo
PAF (prevenção, avaliação, falhas internas e externas) com parâmetros explícitos e factos mensais do dataset."""
import json
import os
import datetime as dt
import pandas as pd
from openpyxl.chart import BarChart, Reference
from sgqlib import *
from dimsq import *
import qdata as Q
import build_05_objetivos as B5

J = lambda n: json.load(open(os.path.join(Q.SILVER, n), encoding="utf-8"))

PARAMS = [
    ("PRECO_MEDIO", 0.1284, "€/un", "Preço médio de venda por unidade (dataset: Σ valor ÷ Σ unidades expedidas)"),
    ("CUSTO_UN_REJ", 0.06, "€/un", "Custo de uma unidade rejeitada (material não recuperado + tempo de máquina); regrind recupera parte do polímero"),
    ("CUSTO_LOTE_RETRAB", 180.0, "€/lote", "Triagem 100% / retrabalho de um lote (horas de inspeção e manuseamento)"),
    ("CUSTO_LOTE_SEGREG", 95.0, "€/lote", "Segregação, identificação e armazenagem de um lote rejeitado"),
    ("CUSTO_NC_MP", 220.0, "€/lote", "Lote de MP rejeitado/derrogado: reensaio, devolução, gestão da SCAR"),
    ("CUSTO_CONCESSAO", 60.0, "€/concessão", "Gestão de uma concessão (análise, pedido ao cliente, identificação)"),
    ("CUSTO_AMOSTRA", 0.06, "€/unidade inspecionada", "Custo médio por unidade inspecionada (maioria visual rápida; ensaios destrutivos incluídos)"),
    ("INSPETORES_MES", 14500.0, "€/mês", "Custo fixo de 5 inspetores + técnica de laboratório (parte não variável)"),
    ("CALIBRACAO_MES", 1400.0, "€/mês", "Calibração e verificação (média mensal do plano)"),
    ("AUDITORIA_MES", 900.0, "€/mês", "Auditorias internas e de fornecedores (média mensal)"),
    ("FORMACAO_MES", 2200.0, "€/mês", "Formação em qualidade (plano de formação)"),
    ("PLANEAMENTO_Q_MES", 1800.0, "€/mês", "Planeamento da qualidade: PFMEA, planos de controlo, MSA, revisão de requisitos"),
]

PROJETOS = [
    ("PRJ-Q-01", "DMAIC — short shot e peso na IM-002", "DMAIC (Six Sigma)", "a) melhorar processos e produtos", "Fechado", GPROD, EPROC, "2025-12-01", "2026-05-31",
     "Taxa de defeito 1,352% (3,71 σ; DPMO 13 516)", "0,384%", "Janela validada por DOE 2³ (temperatura × velocidade); ≈ 1 044 defeitos evitados", 18500, 6000, "R4; O1", "MOC-Q-26-05"),
    ("PRJ-Q-02", "PFMEA e reforma do molde M-SOP-007", "Projeto de fiabilidade", "c) corrigir e prevenir efeitos indesejados", "Fechado", GMAN, "Sandra Reis", "2026-01-15", "2026-06-05",
     "RPN 280", "RPN ≤ 150", "RPN 120; leakage < 300 ppm", 9200, 0, "R2", "MOC-Q-26-07"),
    ("PRJ-Q-03", "SMED nas trocas de molde (injeção e sopro)", "Lean (SMED)", "b) necessidades futuras (lotes pequenos alimentar/farma)", "Em curso", DIND, EPROC, "2026-06-01", "2026-12-31",
     "Troca média 95 min", "≤ 70 min", "Fase de análise: separação interna/externa em 4 moldes", 0, 22000, "O9", ""),
    ("PRJ-Q-04", "Visão artificial na decoração HF-001", "Inovação / investimento", "a) melhorar processos (inspeção a 100%)", "Aprovado", TI_, GQ, "2026-10-01", "2027-06-30",
     "Reclamações de decoração/rótulo: 32 em 14 meses (jul/2025–ago/2026)", "−50%", "Investimento de € 85 000 aprovado (RPG-2026-01-D05)", 0, 30000, "O13; R8", "MOC-Q-26-12"),
    ("PRJ-Q-05", "Teoria das Restrições — injeção como restrição (11 de 14 meses até ago/2026)", "TOC", "a) melhorar processos", "Em curso", DIND, GPROD, "2026-03-01", "2026-11-30",
     "Utilização média da injeção 81,7%; fábrica escondida € 9 090 (8 refações)", "Refações = 0; +5% de throughput na restrição", "Subordinação do planeamento à IM; buffer antes da serigrafia", 9090, 15000, "O11; O14", ""),
    ("PRJ-Q-06", "Rastreabilidade do lote de resina no MES", "Projeto de sistemas", "c) corrigir (lacuna de rastreio)", "Aprovado", TI_, "Gerente de Dados / TI", "2026-10-15", "2027-03-31",
     "Rastreio parcial (FIFO) em 3 de 3 exercícios", "Rastreio completo ≤ 4 h", "—", 0, 12000, "R18; O12", "RPG-2026-01-D07"),
    ("PRJ-Q-07", "Leak testers em linha nas ISBM-003/005", "Investimento", "c) prevenir escapes (fuga)", "Aprovado", DIND, GQ, "2026-11-01", "2027-01-31",
     "Fuga: 359 ppm na inspeção; 11 reclamações de fuga", "Reclamações de fuga = 0", "—", 0, 25000, "R16", "RPG-2026-01-D04"),
    ("PRJ-Q-08", "Kaizen — passagem de turno (turno 2)", "Kaizen", "a) melhorar processos", "Em curso", GPROD, CTURNO, "2026-06-15", "2026-10-31",
     "Prémio de defeito do turno 2", "Diferença ≤ 0,2 pp", "Checklist digital em piloto na injeção", 0, 8000, "R9", "GW-26-02"),
]

SUGESTOES = [
    ("SUG-26-01", "2026-02-03", "OP-SOP-002", "SOP", "Marcar os moldes com o número de ciclos desde a última limpeza", "Implementada", "O2"),
    ("SUG-26-02", "2026-03-18", "OP-SK-001", "SER", "Suporte fixo para o ensaio de fita junto à SS-001 (evita ir ao laboratório)", "Implementada", "EH-07"),
    ("SUG-26-03", "2026-05-06", "Carlos Mendes", "LAB", "Catálogo fotográfico de defeitos na cabine D65", "Em curso", "FOR-Q-14"),
    ("SUG-26-04", "2026-06-30", "OP-INJ-004", "INJ", "Cor de etiqueta diferente por material (PP, PETG, PCR)", "Implementada", "CAPA-Q-26-02"),
    ("SUG-26-05", "2026-08-12", "Operador de armazém", "EXP", "Balança no cais para conferir o peso da palete antes da carga", "Implementada", "EH-01"),
    ("SUG-26-06", "2026-09-02", "Patrícia Lima", "MAN", "Kit de peças críticas da ISBM-005 junto à máquina", "Implementada", "R3"),
    ("SUG-26-07", "2026-10-14", "OP-INJ-002", "INJ", "Lista de verificação de arranque das IM-007/008 no HMI (em vez de papel)", "Implementada", "CON-Q-26-02"),
    ("SUG-26-08", "2026-11-09", "Ana Silva", "LAB", "Amostras-padrão de cor por cliente na cabine D65 (evita disputas de cor)", "Em curso", "O13"),
    ("SUG-26-09", "2026-12-03", "OP-SOP-005", "SOP", "Ecrã com o Cpk do peso por turno junto às ISBM-009/010", "Em análise", "CON-Q-26-18"),
]


def coq_base():
    df = B5.base_mensal().set_index("Mes")
    lots = Q.lot_dispositions()
    lots["Mes"] = Q.monthly(lots, "ProductionDate")
    g = lots.groupby("Mes").agg(Lotes_Retrabalhados=("DispositionDetail", lambda s: (s == "Approved - Reworked").sum()),
                                Lotes_Rejeitados=("FinalLotDecision", lambda s: (s == "Rejected").sum()), Amostras=("SampleSize", "sum"))
    rm = Q.rm_lots()
    rm["Mes"] = Q.monthly(rm, "Date")
    rmn = rm.groupby("Mes").FinalDecision.apply(lambda s: (s != "Accepted").sum()).rename("Lotes_MP_NC")
    c = Q.complaints()
    c["Mes"] = Q.monthly(c, "Date")
    cc = c.groupby("Mes").apply(lambda x: (x.QtyAffected * 0.25).sum() + x.Severity.map({"Critical": 350, "Major": 120, "Minor": 40}).sum()).rename("Custo_Reclamacoes")
    out = df[["Produzido", "Rejeitado", "Lotes_Concessao", "Vendas_EUR"]].join(g).join(rmn).join(cc).fillna(0).reset_index()
    return [dict(Mes=r.Mes, Produzido=int(r.Produzido), Rejeitado=int(r.Rejeitado), Lotes_Retrabalhados=int(r.Lotes_Retrabalhados), Lotes_Rejeitados=int(r.Lotes_Rejeitados), Lotes_MP_NC=int(r.Lotes_MP_NC),
                 Concessoes=int(r.Lotes_Concessao), Unidades_Inspecionadas=int(r.Amostras), Custo_Reclamacoes=round(float(r.Custo_Reclamacoes), 2), Vendas_EUR=round(float(r.Vendas_EUR), 2))
            for r in out.itertuples()]


def build(out):
    dm, adv, toc = J("dmaic_im002_summary.json"), J("advanced_quality_tools_summary.json"), J("toc_kaizen_summary.json")
    b = Book("RG-SGQ-19", "Melhoria Contínua e Custo da Qualidade",
             activities="Determinar e tratar oportunidades de melhoria a partir dos dados e da revisão pela gestão; acompanhar projetos (DMAIC, Lean, TOC, Kaizen, inovação) e o custo da qualidade (PAF).",
             clauses="10.1 a) melhorar processos, produtos e serviços, b) considerar necessidades e expectativas futuras, c) corrigir, prevenir ou reduzir efeitos indesejados (Nota: incremental ou disruptiva, inovação); 9.1.3 (técnicas estatísticas); 5.1.1 g)",
             purpose=f"Carteira de projetos de melhoria com resultados reais do notebook do projeto (DMAIC IM-002: {dm['problem_baseline_rate'] * 100:.2f}% → meta {dm['target_rate'] * 100:.2f}%, PFMEA M-SOP-007 RPN {adv['msop007_rpn_before']} → {adv['msop007_rpn_after']}, TOC com fábrica escondida € {toc['hidden_factory_cost_eur']:,.0f}), custo da qualidade mensal PAF calculado por fórmulas (parâmetros explícitos × factos do dataset) e sugestões dos colaboradores.",
             links=[("RG-SGQ-17 decisões", "Projetos aprovados na revisão pela gestão."), ("RG-SGQ-04", "Oportunidades O-nn que originam projetos."),
                    ("RG-SGA-16", "Kaizen e melhoria ambiental do SGI."), ("manufacturing_performance_analytics.ipynb", "Análises DMAIC, DOE, FMEA, TOC do projeto.")],
             guidance=[("Academy — cap. 7 (Custo da Qualidade)", "Categorias PAF; atacar falhas, investir em prevenção, reduzir avaliação à medida que a qualidade melhora; hard vs. soft savings."),
                       ("Academy — cap. 33–38 (DMAIC), 24 (SMED), 182 (TOC)", "Métodos da carteira de projetos."),
                       ("ISO 10014 (benefícios financeiros e económicos) — referência", "Ligar melhoria da qualidade a resultados financeiros."),
                       ("ISO/TC 176 APG — Improvement", "O auditor procura melhoria baseada em análise de dados e em decisões da revisão pela gestão, não só ações corretivas.")])
    b.add_list("TipoProj", ["DMAIC (Six Sigma)", "Projeto de fiabilidade", "Lean (SMED)", "Inovação / investimento", "TOC", "Projeto de sistemas", "Investimento", "Kaizen"])
    b.add_list("Alinea101", ["a) melhorar processos e produtos", "a) melhorar processos", "a) melhorar processos (inspeção a 100%)", "b) necessidades futuras (lotes pequenos alimentar/farma)",
                             "c) corrigir e prevenir efeitos indesejados", "c) corrigir (lacuna de rastreio)", "c) prevenir escapes (fuga)"])
    b.add_list("EstadoProj", ["Proposto", "Aprovado", "Em curso", "Fechado", "Cancelado"])
    b.add_list("EstadoSug", ["Em análise", "Em curso", "Implementada", "Rejeitada"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Funcao", FUNC_NAMES)

    pcols = [col("ID_Projeto", 9, key="PK", desc="Projeto."), col("Titulo", 40, desc="Título."), col("Tipo", 18, dv="TipoProj", desc="Método."), col("Alinea_10_1", 28, dv="Alinea101", desc="10.1 a)–c)."),
             col("Estado", 10, dv="EstadoProj", desc="Estado."), col("Patrocinador", 22, dv="Funcao", desc="Patrocinador (gestão de topo)."), col("Lider", 20, desc="Líder."),
             col("Inicio", 11, "date", desc="Início."), col("Fim_Planeado", 11, "date", desc="Fim planeado."), col("Baseline", 34, desc="Situação inicial (dados)."), col("Meta", 18, desc="Meta."),
             col("Resultado", 40, desc="Resultado obtido."), col("Hard_Savings_EUR", 10, "eur", desc="Poupança realizada (hard savings)."), col("Soft_Savings_EUR", 10, "eur", desc="Poupança esperada/evitada (soft savings)."),
             col("Riscos_Oport", 12, desc="R/O ligados.", key="FK → RG-SGA-02", req=False), col("Ligacao", 18, desc="MOC, decisão ou CAPA.", req=False),
             col("Alerta", 12, f='=IF(@ID_Projeto@="","",IF(AND(@Estado@<>"Fechado",@Fim_Planeado@<DataRef),"Atrasado","OK"))', desc="Alerta.")]
    # fecho do ano (31/12/2026): estado dos projetos com fim planeado até dezembro ou iniciados no 4.º trimestre
    FECHO_PRJ = {"PRJ-Q-03": "Fechado", "PRJ-Q-04": "Em curso", "PRJ-Q-05": "Fechado", "PRJ-Q-06": "Em curso", "PRJ-Q-07": "Em curso", "PRJ-Q-08": "Fechado"}
    PROJ_F = [p[:4] + (FECHO_PRJ.get(p[0], p[4]),) + p[5:] for p in PROJETOS]
    b.table("Projetos_Melhoria", "tbl_projetos_melhoria", pcols, rows_from(input_names(pcols), PROJ_F, dates=("Inicio", "Fim_Planeado")),
            "Carteira de projetos de melhoria contínua (10.1) com resultados reais do notebook do projeto.", title="CARTEIRA DE PROJETOS DE MELHORIA CONTÍNUA (10.1)",
            cf=[("Estado", {"Fechado": "green", "Em curso": "yellow", "Aprovado": "blue"}), ("Alerta", {"Atrasado": "red"})], row_height=45, freeze_col=2)

    kcols = [col("Parametro", 18, key="PK", desc="Parâmetro de custo."), col("Valor", 10, "num", desc="Valor (editar para simular)."), col("Unidade", 16, desc="Unidade."), col("Descricao", 80, desc="Base do valor (estimativa didática).")]
    b.table("Parametros_COQ", "tbl_param_coq", kcols, [dict(zip(input_names(kcols), p)) for p in PARAMS], "Parâmetros do modelo de custo da qualidade (estimativas didáticas, editáveis).",
            title="PARÂMETROS DO CUSTO DA QUALIDADE (modelo PAF)", subtitle="Valores estimados para a fábrica simulada · Alterar aqui atualiza o COQ mensal", row_height=30)
    P = lambda k: f'INDEX(tbl_param_coq[Valor],MATCH("{k}",tbl_param_coq[Parametro],0))'
    ccols = [col("Mes", 8, key="PK", desc="Mês."), col("Produzido", 11, "num0", desc="Unidades produzidas (dataset)."), col("Rejeitado", 9, "num0", desc="Unidades rejeitadas (dataset)."), col("Lotes_Retrabalhados", 9, "int", desc="Lotes retrabalhados (dataset)."),
             col("Lotes_Rejeitados", 9, "int", desc="Lotes rejeitados (dataset)."), col("Lotes_MP_NC", 9, "int", desc="Lotes de MP rejeitados/derrogados (dataset)."), col("Concessoes", 8, "int", desc="Lotes por concessão (dataset)."),
             col("Unidades_Inspecionadas", 11, "num0", desc="Unidades inspecionadas nas amostras (dataset)."), col("Custo_Reclamacoes", 10, "eur", desc="Custo das reclamações do mês (mesma regra do RG-SGQ-15)."),
             col("Vendas_EUR", 11, "eur", desc="Vendas registadas no dataset (cobrem ≈ 40% das unidades produzidas)."),
             col("Valor_Producao_EUR", 12, "eur", f=f'=@Produzido@*{P("PRECO_MEDIO")}', desc="Valor da produção = produzido × preço médio (denominador do COQ)."),
             col("Prevencao", 10, "eur", f=f'={P("FORMACAO_MES")}+{P("PLANEAMENTO_Q_MES")}', desc="Formação + planeamento da qualidade."),
             col("Avaliacao", 10, "eur", f=f'={P("INSPETORES_MES")}+{P("CALIBRACAO_MES")}+{P("AUDITORIA_MES")}+@Unidades_Inspecionadas@*{P("CUSTO_AMOSTRA")}', desc="Inspeção, ensaios, calibração, auditorias."),
             col("Falha_Interna", 10, "eur", f=f'=@Rejeitado@*{P("CUSTO_UN_REJ")}+@Lotes_Retrabalhados@*{P("CUSTO_LOTE_RETRAB")}+@Lotes_Rejeitados@*{P("CUSTO_LOTE_SEGREG")}+@Lotes_MP_NC@*{P("CUSTO_NC_MP")}+@Concessoes@*{P("CUSTO_CONCESSAO")}',
                 desc="Sucata, retrabalho, segregação, MP não conforme, concessões."),
             col("Falha_Externa", 10, "eur", f='=@Custo_Reclamacoes@', desc="Reclamações (créditos, trocas, transporte, 8D)."),
             col("COQ_Total", 10, "eur", f='=@Prevencao@+@Avaliacao@+@Falha_Interna@+@Falha_Externa@', desc="Custo total da qualidade."),
             col("COQ_Pct_Producao", 8, "pct1", f='=IFERROR(@COQ_Total@/@Valor_Producao_EUR@,"")', desc="COQ em % do valor da produção."),
             col("Falhas_Pct_Producao", 8, "pct1", f='=IFERROR((@Falha_Interna@+@Falha_Externa@)/@Valor_Producao_EUR@,"")', desc="KPI-Q-16: falhas em % do valor da produção (meta ≤ 3%).")]
    b.table("COQ_Mensal", "tbl_coq", ccols, coq_base(), "Custo da qualidade mensal (PAF) calculado: factos do dataset × parâmetros.",
            title="CUSTO DA QUALIDADE MENSAL — MODELO PAF", subtitle="Factos do dataset (rejeições, lotes, amostras, reclamações, vendas) × parâmetros editáveis · KPI-Q-16 = falhas ÷ valor da produção",
            cf=[("Falhas_Pct_Producao", "AND(@<>\"\",@>0.03)", "red")], row_height=15)

    ws = b.sheet("Painel_COQ", "Resumo do custo da qualidade (12 meses) e gráfico mensal por categoria.", tab_color="C00000")
    title(ws, "CUSTO DA QUALIDADE — RESUMO DOS ÚLTIMOS 12 MESES — calculado", "Juran: 'ouro na mina' — atacar as falhas, investir em prevenção, depois reduzir a avaliação")
    header_row(ws, 4, ["Categoria", "€ (12 meses)", "% do COQ", "% do valor produzido"], widths=[26, 14, 10, 12])
    n = len(MESES)
    rng12 = lambda c_: f"INDEX(tbl_coq[{c_}],{n - 11}):INDEX(tbl_coq[{c_}],{n})"
    cats = [("Prevenção", "Prevencao"), ("Avaliação", "Avaliacao"), ("Falha interna", "Falha_Interna"), ("Falha externa", "Falha_Externa")]
    for k, (lab, c_) in enumerate(cats):
        r = 5 + k
        cell(ws, r, 1, lab)
        cell(ws, r, 2, f"=SUM({rng12(c_)})", fmt="#,##0 €")
        cell(ws, r, 3, f"=B{r}/$B$9", fmt="0.0%")
        cell(ws, r, 4, f"=B{r}/SUM({rng12('Valor_Producao_EUR')})", fmt="0.0%")
    cell(ws, 9, 1, "Total", bold=True)
    cell(ws, 9, 2, "=SUM(B5:B8)", fmt="#,##0 €", bold=True)
    cell(ws, 9, 3, "=SUM(C5:C8)", fmt="0.0%", bold=True)
    cell(ws, 9, 4, "=SUM(D5:D8)", fmt="0.0%", bold=True)
    cell(ws, 11, 1, "Poupanças da carteira de projetos (hard)", bold=True)
    cell(ws, 11, 2, "=SUM(tbl_projetos_melhoria[Hard_Savings_EUR])", fmt="#,##0 €")
    cell(ws, 12, 1, "Poupanças esperadas (soft)", bold=True)
    cell(ws, 12, 2, "=SUM(tbl_projetos_melhoria[Soft_Savings_EUR])", fmt="#,##0 €")
    cws = b.wb["COQ_Mensal"]
    t = b.tables["tbl_coq"]
    ch = BarChart()
    ch.type, ch.grouping, ch.overlap = "col", "stacked", 100
    ch.title, ch.height, ch.width = "Custo da qualidade por mês (PAF)", 8, 18
    for cname in ("Prevencao", "Avaliacao", "Falha_Interna", "Falha_Externa"):
        ci = list(t["colmap"]).index(cname) + 1
        ch.add_data(Reference(cws, min_col=ci, min_row=t["hr"], max_row=t["last"]), titles_from_data=True)
    ch.set_categories(Reference(cws, min_col=1, min_row=t["first"], max_row=t["last"]))
    ch.y_axis.numFmt = "#,##0"
    fix_chart(ch)
    ch.legend.position = "b"
    ws.add_chart(ch, "F4")

    scols = [col("ID_Sugestao", 9, key="PK", desc="Sugestão."), col("Data", 11, "date", desc="Data."), col("Proponente", 16, desc="Quem propõe (mesmo nome do RG-SGA-16 tbl_kaizen)."), col("Processo", 7, dv="Processo", desc="Processo."),
             col("Sugestao", 56, desc="Ideia."), col("Estado", 11, dv="EstadoSug", desc="Estado."), col("Ligacao", 14, desc="Ligação.", req=False),
             col("Dias_Resposta", 7, "int", f='=IF(@ID_Sugestao@="","",IF(@Estado@="Em análise",DataRef-@Data@,""))', desc="Dias em análise (meta ≤ 15).")]
    b.table("Sugestoes", "tbl_sugestoes", scols, rows_from(input_names(scols), SUGESTOES, dates=("Data",)), "Sugestões de melhoria dos colaboradores (envolvimento das pessoas, 5.1.1 f).",
            cf=[("Estado", {"Implementada": "green", "análise": "yellow"}), ("Dias_Resposta", "AND(@<>\"\",@>15)", "red")], row_height=20, extra_rows=10)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
