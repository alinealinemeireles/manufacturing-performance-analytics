import datetime as dt
import numpy as np
import pandas as pd
from sgalib import *
import sga_extra as X
from dims import *
from envdata import ambiente, PARAMS

d = lambda s: dt.date.fromisoformat(s) if s else None

MED = [
    ("MED-01", "Eletricidade total e por processo", "kWh (total e por processo); kWh/1.000 un; tCO2e", "Medir",
     "Leitura do contador geral (fatura) + analisadores de energia por quadro (em serviço desde 15/12/2026; até lá rateio por horas de marcha)", "EQP-01; EQP-03", "Mensal, no último dia útil (fatura) e diária (analisadores)",
     "Gerente de Manutenção", "KPI-01; KPI-08", "Meta OBJ-01: ≤ 101 kWh/1.000 un até 12/2027", "AA-007; AA-010; AA-030"),
    ("MED-02", "Ar comprimido: caudal e fugas", "Nm³/min; % fugas em teste de vazio", "Medir",
     "Medidor de caudal na saída dos compressores; teste de vazio ao domingo; detetor ultrassónico", "EQP-04; EQP-05", "Mensal (teste de vazio) e trimestral (campanha ultrassom)",
     "Técnico de Manutenção", "KPI-01", "Fugas < 10% do caudal", "AA-021"),
    ("MED-03", "Scrap gerado e reintegrado", "kg/mês por processo; kg/1.000 un; % reintegração", "Medir",
     "Pesagem das caixas de scrap na balança de piso de cada área e dos moinhos", "EQP-06", "Diária (registo por turno), consolidação mensal",
     "Gerente de Produção", "KPI-03; KPI-04", "Meta OBJ-02: ≤ 0,423 kg/1.000 un até 06/2027", "AA-008; AA-011; AA-020"),
    ("MED-04", "Resíduos por código LER e destino", "kg/mês por LER; % valorização; kg perigosos", "Medir",
     "Pesagem na balança de plataforma do parque antes de cada recolha; conferência com e-GAR", "EQP-02", "Em cada recolha; consolidação mensal; MIRR anual",
     "Responsável de Armazém e Logística", "KPI-05; KPI-07", "Valorização ≥ 80%; 100% e-GAR confirmadas", "AA-004; AA-016; AA-029"),
    ("MED-05", "Polímero consumido e conteúdo reciclado", "kg/mês; % PCR", "Medir", "Inventário de matérias-primas (entradas − stock) e declarações dos fornecedores", "EQP-06", "Mensal",
     "Responsável de Compras", "—", "% PCR a reportar a clientes", "AA-001"),
    ("MED-06", "Solvente de limpeza na serigrafia", "kg/mês; kg/1.000 peças serigrafadas", "Medir",
     "Balanço de inventário (compras − stock) e, desde 08/09/2026, pesagem diária dos dispensadores por máquina e turno", "EQP-07", "Mensal (inventário) e diária (pesagem)",
     "Gestor do SGA / EHS (Responsável Ambiental)", "KPI-06", "Meta OBJ-03: ≤ 0,128 kg/1.000 peças até 06/2027", "AA-014; AA-006"),
    ("MED-07", "Ruído ambiente no recetor sensível", "dB(A); critério de incomodidade", "Medir", "Ensaio acústico por laboratório acreditado (sonómetro classe 1 calibrado)", "EXT-01", "Após alterações e trianual",
     "Gestor do SGA / EHS (Responsável Ambiental)", "—", "Critério de incomodidade noturno ≤ 3 dB(A)", "AA-022"),
    ("MED-08", "Água de rede e água da torre", "m³/mês; m³/1.000 un; condutividade da purga", "Medir",
     "Contador geral (fatura) + contadores parciais da torre e sanitária (a partir de 12/2026); condutivímetro da purga", "EQP-08; EQP-09", "Mensal (fatura); semanal (leitura dos contadores parciais)",
     "Técnico de Utilidades", "KPI-02", "Meta OBJ-05: -10% até 12/2027 (normalizado pela temperatura)", "AA-023"),
    ("MED-09", "Perdas de granulado", "kg recolhidos/mês; n.º sarjetas com grânulos", "Monitorizar",
     "Inspeção visual semanal das sarjetas e pesagem do granulado recolhido", "EQP-06", "Semanal", "Gestor do SGA / EHS (Responsável Ambiental)", "KPI-13", "0 sarjetas com grânulos", "AA-003"),
    ("MED-10", "Estado dos controlos operacionais", "% pontos conformes nas rondas; n.º incidentes", "Monitorizar", "Ronda ambiental com checklist (RG-SGA-10)", "—", "Semanal",
     "Gestor do SGA / EHS (Responsável Ambiental)", "KPI-10; KPI-11", "≥ 90% pontos conformes", "AA-005; AA-016"),
    ("MED-11", "Qualidade do efluente (purga da torre)", "pH, CQO, SST (mg/L)", "Medir", "Colheita e análise por laboratório acreditado", "EXT-02", "Semestral",
     "Gerente de Manutenção", "—", "Abaixo dos VLE do regulamento municipal", "AA-024"),
    ("MED-12", "Conformidade PPWR por família", "% famílias com declaração UE", "Monitorizar", "Revisão do dossier técnico de produto", "—", "Mensal", "Responsável de R&D", "KPI-12", "100% até 31/12/2026", "AA-038"),
]

EQP = [
    ("EQP-01", "Contador geral de eletricidade (operador de rede)", "MED-01", "Verificação metrológica pelo operador de rede", "2024-05-10", 60, "Operador de rede", "Certificado do operador"),
    ("EQP-02", "Balança de plataforma do parque de resíduos (3.000 kg)", "MED-04", "Verificação com massas-padrão", "2026-10-23", 12, "Entidade acreditada", "Certificado VB-2026-10 (PAM-26-20; NC-SGA-26-07 fechada)"),
    ("EQP-03", "Analisadores de energia (6 un.)", "MED-01", "Verificação inicial na instalação", "2026-12-15", 24, "Instalador certificado", "Relatório de comissionamento RC-2026-12 (PAM-26-02)"),
    ("EQP-04", "Medidor de caudal de ar comprimido", "MED-02", "Calibração", "2025-10-15", 24, "Laboratório acreditado", "Certificado CAL-2025-331"),
    ("EQP-05", "Detetor ultrassónico de fugas", "MED-02", "Verificação funcional", "2026-07-01", 12, "Fornecedor", "Relatório de verificação"),
    ("EQP-06", "Balanças de piso das áreas (5 un.)", "MED-03; MED-05; MED-09", "Verificação com massas-padrão", "2026-11-18", 12, "Entidade acreditada", "Certificados VB-2026-11"),
    ("EQP-07", "Balança de bancada da serigrafia (30 kg)", "MED-06", "Verificação com massas-padrão", "2026-09-05", 12, "Interna (massas-padrão calibradas)", "Registo interno VI-2026-09"),
    ("EQP-08", "Contador geral de água (entidade gestora)", "MED-08", "Verificação metrológica pela entidade gestora", "2022-06-01", 96, "Entidade gestora", "Selo do contador"),
    ("EQP-09", "Condutivímetro da purga da torre", "MED-08; MED-11", "Calibração com soluções-padrão", "2026-12-09", 6, "Técnico de Utilidades", "Registo CAL-TR-2026-12"),
    ("EXT-01", "Sonómetro classe 1 (laboratório externo)", "MED-07", "Calibração (responsabilidade do laboratório)", "2026-02-18", 12, "Laboratório acreditado", "Certificado anexo ao relatório de ensaio"),
    ("EXT-02", "Equipamento analítico do laboratório externo", "MED-11", "Acreditação do laboratório", "2026-01-10", 12, "IPAC / laboratório", "Anexo técnico de acreditação"),
]

HIP = [
    ("H1", "Método", "Latas e recipientes de solvente deixados abertos no posto (evaporação).", "Rondas RON-01 de jun–ago; observação nos 3 turnos.",
     "RON-01 não conforme em 45% das rondas de jun–ago/2026 (vs 12% no resto do ano).", "Confirmada", "PAM-26-08"),
    ("H2", "Máquina", "Após o overhaul da SS-001 (jul/2026) a nova rasqueta/tela obriga a mais limpezas.", "Pesagem diária do solvente por máquina (8–22/09).",
     "SS-001 consome ≈ 30% mais solvente por 1.000 peças do que a SS-002 (ver Pesagem_Solvente).", "Confirmada", "PAM-26-08"),
    ("H3", "Mão de obra", "Operador temporário no turno 2 sem formação na IT de limpeza.", "Matriz de competências; pesagem por turno.",
     "Operador OP-SK-T01 sem FOR-02 (NC-SGA-26-08); turno 2 com o maior consumo por 1.000 peças.", "Confirmada", "PAM-26-08"),
    ("H4", "Material", "Novo lote/tinta de secagem mais rápida exige mais limpezas.", "Lotes e fornecedor da tinta; consumo de tinta por 1.000 peças.",
     "Mesmo fornecedor e referência desde abril; consumo de tinta por 1.000 peças estável (±3%).", "Descartada", ""),
    ("H5", "Medição", "Erro de inventário (compra de junho lançada em duplicado).", "Reconciliação faturas × entradas × stock físico.",
     "Reconciliação sem diferenças.", "Descartada", ""),
    ("H6", "Meio ambiente", "Calor de verão aumenta a evaporação do solvente.", "Comparar jun–ago/2026 com jun–ago/2025 (mesma estação).",
     "Temperatura +1,6 °C face a 2025; efeito estimado 3-4% — não explica +15%. A subida também existe face ao verão de 2025.", "Parcial", ""),
    ("H7", "Método", "Mais mudanças de cor (mix com mais cores) → mais limpezas.", "N.º de ordens e de cores por ordem na serigrafia (dataset).",
     "N.º de ordens e de cores por peça estável em jun–ago.", "Descartada", ""),
]


def pesagens():
    rng = np.random.default_rng(52)
    rows = []
    feriados = {dt.date(2026, 10, 5), dt.date(2026, 12, 1), dt.date(2026, 12, 8), dt.date(2026, 12, 25)}
    for k in range((dt.date(2026, 12, 31) - dt.date(2026, 9, 8)).days + 1):   # desde a investigação (08/09) até ao fecho do ano
        dia = dt.date(2026, 9, 8) + dt.timedelta(days=k)
        if dia.weekday() >= 5 or dia in feriados:
            continue
        for maq in ("SS-001", "SS-002"):
            for turno in (1, 2, 3):
                pecas = int(rng.normal(6200, 500))
                base = 0.158
                f = (1.30 if maq == "SS-001" else 1.0) * (1.18 if turno == 2 else 1.0)
                if dia >= dt.date(2026, 9, 17):          # latas fechadas após toolbox (PAM-26-07)
                    f *= 0.93
                if dia >= dt.date(2026, 11, 10):         # dispensadores de segurança e norma de limpeza (PAM-26-08)
                    f *= 0.88 if turno == 2 else 0.95
                if maq == "SS-001" and dia >= dt.date(2026, 12, 17):   # mesa aspirante na SS-001 (PAM-26-31)
                    f *= 0.92
                kg = pecas / 1000 * base * f * rng.normal(1, 0.06)
                rows.append(dict(Data=dia, Maquina=maq, Turno=turno, Pecas_Serigrafadas=pecas, Solvente_kg=round(kg, 3)))
    return rows


def build(out):
    prod, mm, fact, res = ambiente()
    b = Book("RG-SGA-13", "Plano de Monitorização e Medição e Avaliação do Desempenho Ambiental",
             activities="Atividade 5.1 — Plano de Monitorização e Medição (o quê, como, quando, quem) e equipamentos a calibrar/verificar. Atividade 5.2 Parte 1 — análise do desvio de +15% no solvente de limpeza da serigrafia (18 meses de dados).",
             clauses="9.1.1 Monitorização, medição, análise e avaliação (avaliar o desempenho ambiental E a eficácia do SGA — ISO 14001:2026); 9.1.2; 7.1 (equipamentos calibrados/verificados)",
             purpose="Base de dados ambiental mensal de mar/2025 a dez/2026 (22 meses) em formato longo, derivada da produção real da fábrica simulada e de fatores documentados; plano de monitorização com responsáveis e frequências; controlo de calibração; indicadores mensais calculados; e análise do desvio do solvente com hipóteses verificadas por dados.",
             links=[("Dataset da fábrica", "Produção, rejeições, horas de marcha e mudanças de molde de datasets/silver (jul/2025–dez/2026); mar–jun/2025 reconstruídos (marcados)."),
                    ("RG-SGA-05 Objetivos", "Os KPI (KPI-xx) estão definidos no catálogo do RG-SGA-05."),
                    ("RG-SGA-16 EMAS", "Os totais anuais alimentam os indicadores principais do EMAS.")])
    b.add_list("Tipo", ["Medir", "Monitorizar"])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("EstadoHip", ["Confirmada", "Parcial", "Descartada", "Em verificação"])
    b.add_list("Cat6M", ["Método", "Máquina", "Material", "Mão de obra", "Medição", "Meio ambiente"])
    b.add_list("Processo", PROC_CODES + ["UTL-AR", "UTL-FRIO"])
    b.add_list("Qualidade", ["Medido", "Estimado", "Calculado"])

    mcols = [col("ID_MED", 8, desc="Parâmetro monitorizado.", key="PK"), col("O_Que_Medir", 30, desc="O quê medir (indicador exato)."),
             col("Unidade", 26, desc="Unidade."), col("Tipo", 11, dv="Tipo", desc="Medir (valor quantitativo) ou Monitorizar (verificação de estado)."),
             col("Como_Medir", 50, desc="Método/equipamento."), col("Equipamentos", 12, desc="Equipamentos usados.", key="FK → tbl_equipamentos"),
             col("Quando_Medir", 30, desc="Frequência."), col("Quem_Mede", 26, dv="Funcao", desc="Responsável pela recolha."),
             col("ID_KPI", 12, desc="KPI alimentado.", key="FK → RG-SGA-05"), col("Criterio_Meta", 30, desc="Critério/meta."),
             col("IDs_Aspetos", 16, desc="Aspetos ambientais monitorizados.", key="FK → RG-SGA-03"),
             col("Estado_Equipamentos", 16, f='=IF(@Equipamentos@="—","Não aplicável",IF(SUMPRODUCT(ISNUMBER(SEARCH(tbl_equipamentos[ID_Equipamento],@Equipamentos@))*(tbl_equipamentos[Estado]<>"Válido"))>0,"Equipamento a regularizar","OK"))', desc="Alerta se algum equipamento associado não está válido.")]
    mn = [c["name"] for c in mcols if not c["f"]]
    b.table("Plano_Monitorizacao", "tbl_plano_monitorizacao", mcols, [dict(zip(mn, m)) for m in MED],
            "Plano de monitorização e medição (o quê, como, quando, quem) — Atividade 5.1.",
            title="PLANO DE MONITORIZAÇÃO E MEDIÇÃO — PLASTICOM", subtitle="Monitorizar = verificar o estado · Medir = obter um valor quantitativo com equipamento calibrado/verificado",
            cf=[("Tipo", {"Monitorizar": "blue"}), ("Estado_Equipamentos", {"regularizar": "red", "OK": "green"})], row_height=60, freeze_col=2)

    ecols = [col("ID_Equipamento", 9, desc="Equipamento.", key="PK"), col("Equipamento", 40, desc="Descrição."), col("IDs_MED", 16, desc="Parâmetros em que é usado."),
             col("Tipo_Controlo", 30, desc="Calibração ou verificação."), col("Ultima_Calibracao", 11, "date", desc="Data da última calibração/verificação.", req=False),
             col("Periodicidade_Meses", 9, "int", desc="Periodicidade."), col("Entidade", 26, desc="Quem calibra/verifica."), col("Evidencia", 34, desc="Certificado/registo."),
             col("Proxima_Calibracao", 11, "date", f='=IF(@Ultima_Calibracao@="","",EDATE(@Ultima_Calibracao@,@Periodicidade_Meses@))', desc="Data da próxima."),
             col("Estado", 14, f='=IF(@Ultima_Calibracao@="","Por verificar",IF(@Proxima_Calibracao@<DataRef,"Vencido",IF(@Proxima_Calibracao@-DataRef<=45,"A vencer","Válido")))', desc="Estado calculado.")]
    en = [c["name"] for c in ecols if not c["f"]]
    erows = []
    for e in EQP:
        dd = dict(zip(en, e))
        dd["Ultima_Calibracao"] = d(dd["Ultima_Calibracao"])
        erows.append(dd)
    b.table("Equipamentos_Calibracao", "tbl_equipamentos", ecols, erows, "Equipamentos de monitorização que exigem calibração/verificação (Atividade 5.1, ponto 3).",
            cf=[("Estado", {"Vencido": "red", "Por verificar": "orange", "A vencer": "yellow", "Válido": "green"})], row_height=30)

    # parâmetros do modelo de dados
    pcols = [col("Codigo", 12, desc="Parâmetro.", key="PK"), col("Valor", 10, "num3", desc="Valor."), col("Unidade", 12, desc="Unidade."), col("Descricao", 80, desc="Descrição e origem.")]
    b.table("Parametros", "tbl_parametros", pcols, [dict(Codigo=a, Valor=v, Unidade=u, Descricao=t) for a, v, u, t in PARAMS],
            "Fatores usados para derivar os dados ambientais a partir da produção (transparência do modelo; alterar aqui não recalcula a base de dados).")

    X.dim_mes(b, mm)

    prcols = [col("Mes", 11, "date", desc="Mês.", key="PK (com Processo)"), col("Processo", 8, dv="Processo", desc="Processo."),
              col("Unid", 12, "num0", desc="Unidades produzidas."), col("Rej", 10, "num0", desc="Unidades rejeitadas."),
              col("Horas", 10, "num0", desc="Horas de marcha (soma das máquinas)."), col("Setups", 8, "num0", desc="Mudanças de molde."),
              col("Taxa_Rejeicao", 9, "pct1", f='=IF(@Unid@=0,"",@Rej@/@Unid@)', desc="Rejeitadas ÷ produzidas."),
              col("Fonte", 36, desc="Origem.")]
    b.table("Producao_Mensal", "tbl_producao_mensal", prcols, prod[["Mes", "Processo", "Unid", "Rej", "Horas", "Setups", "Fonte"]].to_dict("records"),
            "Produção mensal por processo (denominadores dos indicadores).")

    fcols = [col("Mes", 11, "date", desc="Mês.", key="PK (com Processo, Variavel)"), col("Processo", 9, dv="Processo", desc="Processo/uso."),
             col("Variavel", 13, desc="Código da variável (ENE_TOTAL, ENE_PROC, AGUA_TOTAL, AGUA_USO, SCRAP_KG, REGRIND_KG, POLIMERO_KG, PCR_KG, TINTA_KG, SOLVENTE_KG, FOIL_KG, GRANULADO_KG, FGAS_KG)."),
             col("Descricao", 44, desc="Descrição."), col("Valor", 12, "num", desc="Valor."), col("Unidade", 8, desc="Unidade."),
             col("Fonte", 30, desc="Fonte do dado."), col("Qualidade_Dado", 10, dv="Qualidade", desc="Medido / Estimado / Calculado.")]
    b.table("Dados_Ambientais", "tbl_dados_ambientais", fcols, fact.to_dict("records"),
            "Base de dados ambiental mensal em formato longo (1 linha = mês × processo × variável) — pronta para análise e ML.")

    rcols = [col("Mes", 11, "date", desc="Mês."), col("Codigo_LER", 10, desc="Código LER (* = perigoso)."), col("Descricao", 44, desc="Descrição."),
             col("Perigoso", 8, desc="Sim/Não."), col("Quantidade_kg", 11, "num1", desc="Quantidade (kg)."), col("Operacao_Destino", 9, desc="Operação R/D."),
             col("Operador", 30, desc="Operador de gestão de resíduos."),
             col("Valorizado", 9, f='=IF(LEFT(@Operacao_Destino@,1)="R","Sim","Não")', desc="Destino de valorização (operação R).")]
    b.table("Residuos_Mensais", "tbl_residuos", rcols, res.to_dict("records"), "Resíduos mensais por código LER, destino e operador (base do MIRR).")

    # indicadores mensais (wide) calculados por fórmulas
    ws = b.sheet("Indicadores_Mensais", "Indicadores mensais calculados com SUMIFS sobre as tabelas de dados (KPI-01 a KPI-08, KPI-16).")
    heads = ["Mês", "Temp. (°C)", "Unid. INJ+SOP", "kWh total", "KPI-01 kWh/1.000 un", "m³ água", "KPI-02 m³/1.000 un", "Scrap (kg)", "KPI-03 kg/1.000 un",
             "KPI-04 % reintegração", "Resíduos (kg)", "KPI-05 % valorização", "KPI-07 perigosos (kg)", "Peças serigrafadas", "Solvente (kg)", "KPI-06 kg/1.000 peças", "KPI-08 tCO2e (âmbito 2)"]
    ws["A1"] = "INDICADORES AMBIENTAIS MENSAIS — calculados"
    ws["A1"].font = F_TITLE
    header_row(ws, 3, heads, widths=[11, 8, 13, 12, 11, 10, 11, 10, 11, 11, 11, 11, 11, 12, 10, 12, 12])
    DF = lambda f: b.ref("tbl_dados_ambientais", f)
    PR = lambda f: b.ref("tbl_producao_mensal", f)
    RS = lambda f: b.ref("tbl_residuos", f)
    fe_row = next(i for i, p in enumerate(PARAMS) if p[0] == "FE_ELET")
    fe = f"INDEX({b.ref('tbl_parametros', 'Valor')},{fe_row + 1})"
    for k, mrow in enumerate(mm.to_dict("records")):
        r = 4 + k
        vals = [f"=INDEX({b.ref('tbl_meses', 'Mes')},{k + 1})", f"=INDEX({b.ref('tbl_meses', 'Temp_Media_C')},{k + 1})",
                f'=SUMIFS({PR("Unid")},{PR("Mes")},$A{r},{PR("Processo")},"INJ")+SUMIFS({PR("Unid")},{PR("Mes")},$A{r},{PR("Processo")},"SOP")',
                f'=SUMIFS({DF("Valor")},{DF("Mes")},$A{r},{DF("Variavel")},"ENE_TOTAL")', f"=D{r}/C{r}*1000",
                f'=SUMIFS({DF("Valor")},{DF("Mes")},$A{r},{DF("Variavel")},"AGUA_TOTAL")', f"=F{r}/C{r}*1000",
                f'=SUMIFS({DF("Valor")},{DF("Mes")},$A{r},{DF("Variavel")},"SCRAP_KG")', f"=H{r}/C{r}*1000",
                f'=SUMIFS({DF("Valor")},{DF("Mes")},$A{r},{DF("Variavel")},"REGRIND_KG")/H{r}',
                f'=SUMIFS({RS("Quantidade_kg")},{RS("Mes")},$A{r})', f'=SUMIFS({RS("Quantidade_kg")},{RS("Mes")},$A{r},{RS("Valorizado")},"Sim")/K{r}',
                f'=SUMIFS({RS("Quantidade_kg")},{RS("Mes")},$A{r},{RS("Perigoso")},"Sim")',
                f'=SUMIFS({PR("Unid")},{PR("Mes")},$A{r},{PR("Processo")},"SER")',
                f'=SUMIFS({DF("Valor")},{DF("Mes")},$A{r},{DF("Variavel")},"SOLVENTE_KG")', f"=O{r}/N{r}*1000",
                f"=D{r}*{fe}/1000"]
        fmts = ["yyyy-mm", "0.0", "#,##0", "#,##0", "0.0", "#,##0", "0.000", "#,##0", "0.000", "0%", "#,##0", "0%", "#,##0", "#,##0", "#,##0.0", "0.000", "#,##0.0"]
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=j + 1, value=v)
            c.number_format = fmts[j]
            c.font, c.border = F_BASE, BORDER
    ws.freeze_panes = "B4"
    last = 3 + len(mm)
    ws.conditional_formatting.add(f"P4:P{last}", FormulaRule(formula=[f"P4>AVERAGE($P$4:$P${last - 3})*1.1"], fill=PatternFill("solid", fgColor=CF_COLORS["red"][0])))

    # análise do desvio 5.2
    ws = b.sheet("Analise_Desvio_5_2", "Atividade 5.2 Parte 1: cenário de desvio do solvente (+15% nos últimos 3 meses com produção estável), comparações calculadas, hipóteses e ações.", tab_color="7030A0")
    ws["A1"] = "ATIVIDADE 5.2 — ANÁLISE DE DESVIO: SOLVENTE DE LIMPEZA NA SERIGRAFIA (KPI-06)"
    ws["A1"].font = F_TITLE
    ws.column_dimensions["A"].width = 46
    for L in "BCDE":
        ws.column_dimensions[L].width = 18
    ws["A3"] = "Indicador crítico escolhido: KPI-06 — kg de solvente de limpeza por 1.000 peças serigrafadas (aspeto AA-014, AAS de COV; objetivo OBJ-03)."
    ws["A3"].font = F_BOLD
    I = "Indicadores_Mensais"
    first = 4
    lst = 4 + [str(x)[:7] for x in mm["Mes"]].index("2026-08")   # a análise da Atividade 5.2 foi feita com os dados até ago/2026
    rows = [
        ("Média do KPI-06 — jun–ago/2026 (últimos 3 meses)", f"=AVERAGE('{I}'!P{lst - 2}:P{lst})", "0.000"),
        ("Média do KPI-06 — mar–mai/2026 (3 meses anteriores)", f"=AVERAGE('{I}'!P{lst - 5}:P{lst - 3})", "0.000"),
        ("Variação do indicador (últimos 3 vs anteriores)", "=B5/B6-1", "+0.0%;-0.0%"),
        ("Peças serigrafadas — jun–ago/2026", f"=SUM('{I}'!N{lst - 2}:N{lst})", "#,##0"),
        ("Peças serigrafadas — mar–mai/2026", f"=SUM('{I}'!N{lst - 5}:N{lst - 3})", "#,##0"),
        ("Variação da produção", "=B8/B9-1", "+0.0%;-0.0%"),
        ("Média do KPI-06 — jun–ago/2025 (mesma estação do ano anterior)", f"=AVERAGE('{I}'!P{first + 3}:P{first + 5})", "0.000"),
        ("Variação face ao mesmo período de 2025", "=B5/B11-1", "+0.0%;-0.0%"),
        ("Solvente em excesso no período (kg)", f"=SUM('{I}'!O{lst - 2}:O{lst})-B6*B8/1000", "#,##0"),
        ("Média do KPI-06 — out–dez/2026 (após PAM-26-07 e PAM-26-08)", f"=AVERAGE('{I}'!P{lst + 2}:P{lst + 4})", "0.000"),
        ("Variação out–dez/2026 face a mar–mai/2026 (antes do desvio)", "=B14/B6-1", "+0.0%;-0.0%"),
        ("Leitura automática", '=IF(AND(B7>=0.1,ABS(B10)<0.05),"DESVIO REAL: o indicador subiu "&FIXED(B7*100,1)&"% com a produção estável ("&FIXED(B10*100,2)&"%) → investigar causas operacionais/técnicas.",IF(B7>=0.1,"Subida acompanhada de variação de produção: normalizar antes de concluir.","Sem desvio relevante."))', "General"),
    ]
    for k, (lab, f, fmt) in enumerate(rows):
        r = 5 + k
        a = ws.cell(row=r, column=1, value=lab)
        a.font, a.border, a.fill = F_BOLD, BORDER, FILL_BAND
        c = ws.cell(row=r, column=2, value=f)
        c.number_format, c.border, c.font = fmt, BORDER, F_BOLD
        if k == len(rows) - 1:
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
            c.alignment = WRAP_TOP
            ws.row_dimensions[r].height = 45
    r = 5 + len(rows) + 1
    ws.cell(row=r, column=1, value="Cenário (enunciado)").font = F_BOLD
    c = ws.cell(row=r, column=2, value=("Os dados de mar/2025 a ago/2026 (18 meses) mostraram que o consumo específico de solvente de limpeza na serigrafia subiu cerca de 15% "
                                        "em jun–ago/2026 face aos 3 meses anteriores, com a produção de peças serigrafadas estável. A Gestão de Topo pediu "
                                        "justificação e soluções. A investigação (PAM-26-07) testou 7 hipóteses: 3 confirmadas, 1 parcial e 3 descartadas (folha Hipoteses_Desvio)."))
    c.alignment = WRAP_TOP
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
    ws.row_dimensions[r].height = 75
    r += 2
    ws.cell(row=r, column=1, value="Ações imediatas").font = F_BOLD
    for t in ["PAM-26-07 (C1): pesagem diária por máquina e turno, fechar e identificar todos os recipientes, observar a limpeza nos 3 turnos, reconciliar o inventário.",
              "PAM-26-08 (C2): dispensadores de segurança, norma de limpeza, afinação da rasqueta da SS-001 e formação dos operadores (incl. temporários).",
              "PAM-26-13 (M, decisão da Revisão pela Gestão): unidade de recuperação de solvente.",
              "COM-03: toolbox com os operadores para partilhar o desvio e recolher as causas prováveis."]:
        r += 1
        c = ws.cell(row=r, column=2, value="• " + t)
        c.alignment = WRAP_TOP
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
        ws.row_dimensions[r].height = 32

    hcols = [col("ID_Hipotese", 8, desc="Hipótese.", key="PK"), col("Categoria_6M", 12, dv="Cat6M", desc="Categoria Ishikawa."),
             col("Hipotese", 46, desc="Causa provável."), col("Como_Verificar", 40, desc="Teste/dado usado para verificar."),
             col("Evidencia_Obtida", 50, desc="Resultado da verificação."), col("Estado", 12, dv="EstadoHip", desc="Confirmada / Parcial / Descartada."),
             col("ID_PAM", 10, desc="Ação.", key="FK → RG-SGA-06", req=False)]
    b.table("Hipoteses_Desvio", "tbl_hipoteses", hcols, [dict(zip([c["name"] for c in hcols], h)) for h in HIP],
            "Hipóteses (causas prováveis) do desvio do solvente e resultado da verificação com dados.",
            cf=[("Estado", {"Confirmada": "red", "Parcial": "orange", "Descartada": "gray"})], row_height=48)

    scols = [col("Data", 11, "date", desc="Dia."), col("Maquina", 8, desc="Máquina (SS-001/SS-002)."), col("Turno", 6, "int", desc="Turno."),
             col("Pecas_Serigrafadas", 10, "num0", desc="Peças."), col("Solvente_kg", 10, "num3", desc="Solvente pesado (kg)."),
             col("kg_por_1000", 10, "num3", f="=@Solvente_kg@/@Pecas_Serigrafadas@*1000", desc="kg por 1.000 peças.")]
    b.table("Pesagem_Solvente", "tbl_pesagem_solvente", scols, pesagens(), "Pesagem diária de solvente por máquina e turno (investigação PAM-26-07 desde 08/09/2026 e acompanhamento das ações até 31/12/2026).")
    ws = b.tables["tbl_pesagem_solvente"]["ws"]
    S = lambda f: b.ref("tbl_pesagem_solvente", f, sheet=False)
    ws["I1"] = "Resumo (kg por 1.000 peças)"
    ws["I1"].font = F_BOLD
    header_row_at = 2
    for j, t in enumerate(["", "Turno 1", "Turno 2", "Turno 3", "Total"]):
        c = ws.cell(row=header_row_at, column=9 + j, value=t)
        c.font, c.fill = F_HEAD, FILL_HEAD
    for i, maq in enumerate(["SS-001", "SS-002"]):
        r = 3 + i
        ws.cell(row=r, column=9, value=maq).font = F_BOLD
        for j, t in enumerate([1, 2, 3]):
            c = ws.cell(row=r, column=10 + j, value=f'=SUMIFS({S("Solvente_kg")},{S("Maquina")},"{maq}",{S("Turno")},{t})/SUMIFS({S("Pecas_Serigrafadas")},{S("Maquina")},"{maq}",{S("Turno")},{t})*1000')
            c.number_format = "0.000"
        c = ws.cell(row=r, column=13, value=f'=SUMIFS({S("Solvente_kg")},{S("Maquina")},"{maq}")/SUMIFS({S("Pecas_Serigrafadas")},{S("Maquina")},"{maq}")*1000')
        c.number_format = "0.000"
    for L, w in zip("IJKLM", (10, 10, 10, 10, 10)):
        ws.column_dimensions[L].width = w
    X.extra_13(b)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
