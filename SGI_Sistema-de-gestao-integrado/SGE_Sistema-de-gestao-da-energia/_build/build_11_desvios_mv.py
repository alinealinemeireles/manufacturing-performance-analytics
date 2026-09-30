"""RG-SGE-11 — Desvios significativos do desempenho energético (investigação e resposta) e medição e verificação (M&V) das poupanças.
ISO 50001:2018 9.1.1 (investigar e responder a desvios significativos — reter), 6.2.3 (método de verificação), 10.2 ·
ISO 50015:2014 (M&V) · ISO 50047:2016 (determinação de poupanças) · EVO IPMVP (opções A–D) · ISO 50006:2023 §10."""
from sgelib import *
from dimse import *
import edata

DESVIOS = [
    ("DSV-26-01", "2026-09-08", "2026-08-01", "IDE-01 (LBE-01)", "Mês fora do domínio: CDD₁₅ = 279 (> 276 aceite) e +18 MWh face ao esperado",
     "Onda de calor (+2,2 °C) e arranque das linhas novas; o modelo extrapola", "Mês excluído da demonstração; registar para a LBE-01b; reforçar CO-13/14 no verão", "2026-09-22", GE, "—"),
    ("DSV-26-02", "2026-09-05", "2026-08-01", "Potência tomada (fatura)", "1 429 kW > 1 400 kW contratados (102%)",
     "Arranque simultâneo das ISBM após a paragem de 15/08 + chiller no máximo + máquinas novas", "Pedido de aumento para 1 550 kW; alarme a 90% nos analisadores; arranque escalonado (SUGE-13)", "2026-10-02", DFIN, "NCE-26-04"),
    ("DSV-26-03", "2026-08-19", "2026-08-01", "CO-13 setpoint do chiller (ronda)", "Setpoint a 6 °C durante 9 dias (critério ≥ 7 °C na altura)",
     "Operador baixou o setpoint para resolver empenos num molde (ANI-02)", "Reposto; causa do empeno tratada com a qualidade; alarme de alteração de setpoint (SUGE-12)", "2026-08-28", TUTL, "NCE-26-03"),
    ("DSV-26-04", "2025-12-02", "2025-11-01", "Reconciliação leitura interna × fatura", "+1,8% (critério ±1%)",
     "Erro de transcrição na leitura interna de nov/2025 (dígito trocado)", "Corrigido; leitura por fotografia a partir de 01/2026; desde 15/12/2026 leitura automática", "2025-12-03", TUTL, "—"),
    ("DSV-26-05", "2026-11-10", "2026-10-01", "IDE-01 (LBE-01)", "Poupança de 24,9 MWh face ao esperado (−4,2%) — desvio favorável",
     "Standby obrigatório desde 05/10 e início do programa de fugas", "Confirmado pela M&V por ação (MV-02, MV-03); sem ação corretiva", "2026-11-20", GE, "—"),
    ("DSV-26-06", "2026-12-31", "2026-12-01", "IDE-01 (LBE-01)", "Poupança de 27,8 MWh (−4,6%) — desvio favorável",
     "Efeito pleno do standby e das fugas/pressão 6,8 bar", "Confirmado pela M&V por ação; incluir na revisão pela gestão", None, GE, "—"),
]

MV = [
    ("MV-01", "ALT-2026-01", "Compressores de velocidade variável CMP-01/02", "Central de ar comprimido (compressores + secadores): kWh (PA-01) e Nm³ (EQP-04)", "B — isolamento da medida, todos os parâmetros medidos",
     "12–18/01/2026 (compressores antigos)", "15–21/06/2026 e 07–13/12/2026", "Normalizado por Nm³ produzido (kWh/Nm³ × Nm³ do período de reporte)", "kWh, Nm³, pressão", "—",
     "PA-01 (±2%); EQP-04 (±2%)", "±3% na potência específica (combinação quadrática)", TUTL),
    ("MV-02", "PA-E-03", "Standby nas pausas e paragens > 30 min (injeção e sopro)", "Máquinas IM e ISBM: kW em espera aquecida vs kW em standby", "A — parâmetro-chave medido (kW), horas estimadas",
     "Campanha jun–jul/2026 (kW em espera aquecida)", "Out–dez/2026", "Horas de pausa (turno 3) e de paragem > 30 min do MES × taxa de adesão das rondas", "kW (amostra de 6 máquinas em 10/2026)",
     "Horas em standby (MES + checklist)", "PA-01 (±2%)", "±15% (horas estimadas)", GPROD),
    ("MV-03", "PA-E-02", "Fugas de ar e pressão de 6,8 bar", "Central de ar comprimido", "B — teste de vazio (fugas) + kWh/Nm³ medido",
     "Teste de vazio de 21/06/2026 (25% de fugas)", "Out–dez/2026 (teste de vazio mensal; 14% em dez)", "Poupança = redução do caudal de fugas × horas × potência específica; pressão: −7% por bar",
     "Nm³ em vazio, kWh/Nm³", "Horas de funcionamento da rede", "EQP-04 (±2%); PA-01", "±10%", TUTL),
    ("MV-04", "OBJ-E-01", "Todas as ações — nível da instalação", "Fronteira do IDE-01 (instalação sem as máquinas novas)", "C — instalação completa (modelo da LBE-01)",
     "Mar/2025–fev/2026", "Mar–dez/2026 e out–dez/2026", "Unidades INJ+SOP e graus-dia (LINEST); ajuste não rotineiro ALE-01", "kWh da fatura; unidades; temperatura", "kWh das máquinas novas (rateio)",
     "M00 (0,5S)", "t × erro-padrão × √m (≈ 61 MWh em 3 meses)", GE),
]


def build(out):
    b = Book("RG-SGE-11", "Desvios Significativos e Medição e Verificação das Poupanças",
             activities="Investigar e responder aos desvios significativos do desempenho energético; planear e executar a medição e verificação (M&V) das poupanças das ações, "
                        "confirmando a coerência entre a poupança por ação e a melhoria ao nível da instalação.",
             clauses="9.1.1 (investigar e responder a desvios significativos — reter resultados; avaliar a melhoria comparando IDE e LBE); 6.2.3 (método para verificar a melhoria); "
                     "10.2 (demonstrar melhoria contínua do desempenho energético).",
             purpose="Registo de 6 desvios (desfavoráveis e favoráveis) com causa, resposta e prazo; 4 planos de M&V (IPMVP A, B e C); dados diários dos compressores em 3 fases com a "
                     "potência específica calculada; poupanças verificadas out–dez/2026 por ação e comparação com a melhoria normalizada da instalação (RG-SGE-05).",
             links=[("RG-SGE-05", "IDE mensais, limite de desvio significativo e demonstração da melhoria (LBE_Modelo)."), ("RG-SGE-08", "Não conformidades das rondas (CO-xx) que originam desvios."),
                    ("RG-SGE-14", "NC abertas a partir dos desvios (NCE-xx)."), ("RG-SGA-10", "OT-2026-02 — instalação dos compressores VSD.")],
             guidance=[("ISO 50015:2014", "Plano de M&V: fronteira, período de referência e de reporte, variáveis, ajustes, incerteza, responsabilidades."),
                       ("ISO 50047:2016", "Determinação das poupanças: consumo evitado face à LBE ajustada às condições do reporte."),
                       ("EVO — IPMVP Core Concepts", "Opções A (parâmetro-chave), B (todos os parâmetros), C (instalação), D (simulação calibrada)."),
                       ("ISO 50006:2023 §10", "Monitorização, reporte e demonstração da melhoria; desvios a investigar."),
                       ("ASHRAE Guideline 14", "Incerteza da poupança a 95% com modelos mensais."),
                       ("ISO 11011:2013", "Medição da central de ar comprimido (kWh, Nm³, teste de vazio).")],
             legal=[("Regulamentos dos avisos de financiamento (Portugal 2030 / Fundo Ambiental)", "Exigem M&V das poupanças financiadas (PIE-09).")])
    b.add_list("Funcao", FUNC_NAMES)

    dcols = [col("ID_Desvio", 9, key="PK", desc="Desvio."), col("Data_Detecao", 11, "date", desc="Data de deteção."), col("Mes_Referencia", 11, "date", desc="Mês a que respeita."),
             col("IDE_ou_Controlo", 22, desc="IDE, controlo ou dado onde foi detetado."), col("Descricao", 44, desc="Desvio observado."), col("Causa", 40, desc="Resultado da investigação."),
             col("Resposta", 44, desc="Resposta / ação."), col("Data_Resposta", 11, "date", desc="Data da resposta.", req=False), col("Responsavel", 22, dv="Funcao", desc="Responsável."),
             col("ID_NC", 10, desc="NC aberta.", key="FK → RG-SGE-14 tbl_nc", req=False),
             col("Dias_Resposta", 8, "int", f='=IF(@ID_Desvio@="","",IF(@Data_Resposta@="",DataRef-@Data_Detecao@,@Data_Resposta@-@Data_Detecao@))', desc="Dias até à resposta (ou até hoje)."),
             col("No_Prazo_30d", 9, f='=IF(@ID_Desvio@="","",IF(@Data_Resposta@="",IF(@Dias_Resposta@<=30,"Em curso","Atrasado"),IF(@Dias_Resposta@<=30,"Sim","Não")))', desc="Resposta em ≤ 30 dias (KPI-E-02)?")]
    b.table("Desvios_Significativos", "tbl_desvios", dcols, rows_from(input_names(dcols), DESVIOS, dates=("Data_Detecao", "Mes_Referencia", "Data_Resposta")),
            "Investigação e resposta a desvios significativos (9.1.1 — reter).", title="DESVIOS SIGNIFICATIVOS DO DESEMPENHO ENERGÉTICO (9.1.1)",
            subtitle="Limite mensal do IDE-01 = t × erro-padrão da LBE-01 (RG-SGE-05) · Também se investigam desvios favoráveis para confirmar as causas",
            cf=[("No_Prazo_30d", {"Atrasado": "red", "Não": "orange", "Sim": "green", "Em curso": "blue"})], row_height=45, freeze_col=2)
    ws = b.wb["Desvios_Significativos"]
    td = b.tables["tbl_desvios"]
    r = td["last"] + 2
    cell(ws, r, 1, "KPI-E-02", bold=True)
    cell(ws, r, 2, "Desvios respondidos em ≤ 30 dias ÷ desvios com resposta", border=False)
    cell(ws, r, 5, '=IFERROR(COUNTIF(tbl_desvios[No_Prazo_30d],"Sim")/(COUNTIF(tbl_desvios[No_Prazo_30d],"Sim")+COUNTIF(tbl_desvios[No_Prazo_30d],"Não")),"")', fmt="0%", bold=True)

    mcols = [col("ID_MV", 7, key="PK", desc="Plano de M&V."), col("ID_Origem", 10, desc="Plano de ação / alteração."), col("Medida", 36, desc="Medida de melhoria."),
             col("Fronteira_Medicao", 40, desc="Fronteira de medição (ISO 50015)."), col("Opcao_IPMVP", 26, desc="Opção IPMVP."), col("Periodo_Referencia", 24, desc="Período de referência."),
             col("Periodo_Reporte", 24, desc="Período de reporte."), col("Ajustes_Normalizacao", 40, desc="Variáveis e ajustes."), col("Parametros_Medidos", 22, desc="Medidos."),
             col("Parametros_Estimados", 22, desc="Estimados (opção A)."), col("Instrumentos", 22, desc="Instrumentos (RG-SGE-06)."), col("Incerteza", 22, desc="Incerteza."),
             col("Responsavel", 22, dv="Funcao", desc="Responsável.")]
    b.table("Planos_MV", "tbl_mv_planos", mcols, rows_from(input_names(mcols), MV), "Planos de medição e verificação (ISO 50015; IPMVP).",
            title="PLANOS DE MEDIÇÃO E VERIFICAÇÃO (ISO 50015 / IPMVP)", row_height=45, freeze_col=2)

    comp = edata.compressores()
    ccols = [col("Fase", 26, desc="Fase de medição."), col("Data", 11, "date", desc="Dia.", key="PK"), col("Dia_Semana", 6, desc="Dia."), col("Producao", 7, desc="Dia com produção?"),
             col("Nm3_Dia", 10, "num0", desc="Ar produzido (EQP-04)."), col("kWh_Dia", 10, "kwh", desc="Energia dos compressores e secadores (PA-01)."),
             col("Pressao_Media_bar", 8, "num", desc="Pressão média."), col("Fuga_Teste_Vazio", 8, "pct", desc="Fugas no teste de vazio (domingo).", req=False),
             col("kWh_por_Nm3", 9, "num3", f='=IF(@Data@="","",@kWh_Dia@/@Nm3_Dia@)', desc="Potência específica diária.")]
    b.table("Ar_Comprimido_MV", "tbl_ar_mv", ccols, comp.to_dict("records"), "Dados diários da central de ar em 3 semanas de medição (simulados).",
            title="CENTRAL DE AR COMPRIMIDO — 3 SEMANAS DE MEDIÇÃO (MV-01, MV-03) — SIMULADAS", row_height=15)
    ws = b.wb["Ar_Comprimido_MV"]
    ta = b.tables["tbl_ar_mv"]
    r0 = ta["last"] + 2
    header_row(ws, r0, ["Fase", "kWh/Nm³ (semana)", "Fugas", "Pressão", "Variação vs antes", "Poupança anual extrapolada (MWh)", "Leitura"])
    fases = list(dict.fromkeys(comp["Fase"]))
    A = lambda c_: f"tbl_ar_mv[{c_}]"
    for i, f_ in enumerate(fases):
        r = r0 + 1 + i
        cell(ws, r, 1, f_, bold=True)
        cell(ws, r, 2, f'=SUMIFS({A("kWh_Dia")},{A("Fase")},A{r})/SUMIFS({A("Nm3_Dia")},{A("Fase")},A{r})', fmt="0.0000")
        cell(ws, r, 3, f'=IFERROR(AVERAGEIFS({A("Fuga_Teste_Vazio")},{A("Fase")},A{r}),"")', fmt="0%")
        cell(ws, r, 4, f'=AVERAGEIFS({A("Pressao_Media_bar")},{A("Fase")},A{r})', fmt="0.00")
        cell(ws, r, 5, "" if i == 0 else f"=B{r}/B{r0 + 1}-1", fmt="0.0%")
        cell(ws, r, 6, "" if i == 0 else f'=(B{r0 + 1}*SUMIFS({A("Nm3_Dia")},{A("Fase")},A{r})-SUMIFS({A("kWh_Dia")},{A("Fase")},A{r}))*52/1000', fmt="#,##0")
        cell(ws, r, 7, ["Referência (LBE-06)", "Efeito dos VSD (MV-01)", "VSD + fugas + pressão (MV-01 + MV-03); menos ar produzido (−10%) pela redução das fugas"][i])
    cell(ws, r0 + 5, 1, "Nota", bold=True)
    cell(ws, r0 + 5, 2, "Poupança anual extrapolada = (kWh/Nm³ de janeiro × Nm³ da semana − kWh reais) × 52: mede só a eficiência da central (VSD e pressão). A menor procura de ar por redução das fugas é poupança adicional, verificada no MV-03.", border=False)

    ef = edata.efeito_acoes()
    fac = {"MV-02": (0.95, 1.04, 0.97), "MV-03": (1.05, 0.93, 1.02)}
    prow = []
    for k, (mes, d) in enumerate(sorted(ef.items())):
        if mes.month < 10:
            continue
        i = mes.month - 10
        prow.append(dict(ID_Poupanca=f"POU-{mes:%Y%m}-02", ID_MV="MV-02", Mes=mes, kWh_Poupados=round(d["Standby"] * fac["MV-02"][i]),
                         Metodo="Opção A: (kW espera − kW standby) × horas em standby registadas × adesão das rondas", Incerteza_Pct=0.15, Evidencia="Checklists de pausa; MES; campanha PA-01"))
        prow.append(dict(ID_Poupanca=f"POU-{mes:%Y%m}-03", ID_MV="MV-03", Mes=mes, kWh_Poupados=round(d["Ar"] * fac["MV-03"][i]),
                         Metodo="Opção B: redução do caudal de fugas (teste de vazio) × horas × kWh/Nm³ + efeito da pressão", Incerteza_Pct=0.10, Evidencia="Testes de vazio mensais; EQP-04; PA-01"))
    pcols = [col("ID_Poupanca", 14, key="PK", desc="Registo de poupança."), col("ID_MV", 7, desc="Plano de M&V.", key="FK → tbl_mv_planos"), col("Mes", 11, "date", desc="Mês."),
             col("kWh_Poupados", 10, "kwh", desc="Poupança verificada (kWh)."), col("Metodo", 60, desc="Cálculo."), col("Incerteza_Pct", 8, "pct", desc="Incerteza relativa."),
             col("Evidencia", 34, desc="Evidência."), col("Incerteza_kWh", 9, "kwh", f='=IF(@ID_Poupanca@="","",@kWh_Poupados@*@Incerteza_Pct@)', desc="Incerteza absoluta.")]
    b.table("Poupancas_Verificadas", "tbl_poupancas", pcols, prow, "Poupanças verificadas por ação out–dez/2026 (ISO 50047; simuladas).",
            title="POUPANÇAS VERIFICADAS POR AÇÃO — OUT–DEZ/2026 (ISO 50047)", row_height=30)
    ws = b.wb["Poupancas_Verificadas"]
    tpp = b.tables["tbl_poupancas"]
    r = tpp["last"] + 2
    lines = [("Σ poupanças verificadas por ação (MV-02 + MV-03)", "=SUM(tbl_poupancas[kWh_Poupados])", "#,##0"),
             ("Incerteza combinada (raiz da soma dos quadrados)", "=SQRT(SUMSQ(tbl_poupancas[Incerteza_kWh]))", "#,##0"),
             ("Melhoria normalizada da instalação out–dez/2026 (MV-04, RG-SGE-05 LBE_Modelo)", 91930, "#,##0"),
             ("Diferença (instalação − ações)", f"=D{r + 2}-D{r}", "#,##0"),
             ("Coerência (diferença dentro das incertezas?)", f'=IF(ABS(D{r + 3})<=D{r + 1}+61121,"Coerente","Investigar")', None)]
    for i, (lab, f_, fmt) in enumerate(lines):
        cell(ws, r + i, 1, lab, bold=True)
        ws.merge_cells(start_row=r + i, start_column=1, end_row=r + i, end_column=3)
        cell(ws, r + i, 4, f_, fmt=fmt, bold=True)
    cell(ws, r + 5, 1, "Valor da instalação copiado do RG-SGE-05 à data de referência (91 930 kWh; incerteza 61 121 kWh). A diferença de ≈ 21 MWh face às ações verificadas cabe na incerteza e corresponde a medidas não verificadas individualmente (água gelada a 10 °C, rondas de energia). A coerência entre a opção C e as opções A/B reforça a demonstração para a ISO 50003.", border=False)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
