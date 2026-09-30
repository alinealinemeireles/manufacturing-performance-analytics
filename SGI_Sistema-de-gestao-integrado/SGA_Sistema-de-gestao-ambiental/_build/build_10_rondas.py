import datetime as dt
import numpy as np
from sgalib import *
import sga_extra as X
from dims import *

CATS = ["1. Gestão de Produtos Químicos", "2. Eficiência e Manutenção", "3. Emergência", "4. Gestão de Resíduos", "5. Perdas de granulado e energia (extra)"]

# (ID, Categoria, Area, Ponto, Criterio, Metodo, Frequencia, Resp, Aspeto, Clausula, Selecionado)
PONTOS = [
    ("RON-01", CATS[0], "SER", "Recipientes de tinta e solvente no posto de serigrafia.",
     "Todos os recipientes fechados quando não estão em uso imediato; rótulo CLP legível; solvente só em dispensador de segurança.", "Observação direta", "Semanal", "Gestor do SGA / EHS (Responsável Ambiental)", "AA-014", "8.1", "Sim"),
    ("RON-02", CATS[0], "ARQ", "Armazenagem de bidões e embalagens de químicos no armazém.",
     "100% dos recipientes > 20 L sobre bacia de retenção (capacidade ≥ maior recipiente); incompatíveis separados; FDS acessíveis.", "Observação + contagem", "Semanal", "Responsável de Armazém e Logística", "AA-005", "8.1", "Sim"),
    ("RON-03", CATS[1], "UTL", "Rede de ar comprimido (ligações rápidas, mangueiras, purgadores).",
     "Sem silvos (fugas audíveis); cada fuga detetada tem etiqueta e ordem de trabalho com prazo ≤ 15 dias.", "Escuta + detetor ultrassónico mensal", "Semanal", "Técnico de Manutenção", "AA-021", "8.1", "Sim"),
    ("RON-04", CATS[1], "INJ", "Máquinas de injeção/sopro: fugas de óleo e água e registos de manutenção.",
     "Piso seco sob as máquinas; tabuleiros de retenção sem óleo acumulado; plano de manutenção preventiva sem atrasos > 7 dias.", "Observação + consulta do registo de manutenção", "Semanal", "Técnico de Manutenção", "AA-009", "8.1", "Sim"),
    ("RON-05", CATS[2], "GER", "Válvula de corte da rede pluvial e sarjetas.",
     "Válvula acessível, sinalizada e operacional (manobra de teste); sarjetas sem obstrução; bacias de retenção secas, limpas e sem lixo.", "Manobra de teste + observação", "Mensal", "Técnico de Utilidades", "AA-034", "8.2", "Sim"),
    ("RON-06", CATS[2], "GER", "Kits antipoluição (KIT-01 a KIT-05).",
     "Selo intacto com n.º registado; conteúdo completo (12 almofadas, 2 barreiras, luvas, óculos, sacos, instrução IT-SGA-01); acessível e sinalizado.", "Verificação do selo e do conteúdo", "Semanal (mensal até set/2026)", "Responsável de Armazém e Logística", "AA-005", "8.2", "Sim"),
    ("RON-07", CATS[3], "PRS", "Segregação e identificação dos resíduos no parque e nas áreas.",
     "Cada contentor com etiqueta de código LER; sem mistura de fluxos; scrap limpo separado por cor/polímero.", "Observação", "Semanal", "Responsável de Armazém e Logística", "AA-029", "8.1", "Sim"),
    ("RON-08", CATS[3], "PRS", "Acondicionamento dos resíduos perigosos.",
     "Contentores fechados com tampa, identificados, em bacia e sob cobertura; zona limpa; e-GAR do último envio confirmada.", "Observação + SILiAmb", "Semanal", "Responsável de Armazém e Logística", "AA-016", "8.1", "Sim"),
    ("RON-09", CATS[4], "REC", "Perdas de granulado nos silos, zona de descarga e sarjetas exteriores.",
     "Sem grânulos visíveis no pavimento exterior nem nos filtros das sarjetas; tabuleiros de descarga em uso.", "Observação", "Semanal", "Operador de Armazém / Empilhador", "AA-003", "8.1", "Não"),
    ("RON-11", CATS[0], "GER", "Armazenagem de químicos fora do armazém (torre TR-01, oficina, parque de gases, depósito de gasóleo, laboratório, sala de baterias).",
     "Recipientes em bacia com capacidade suficiente; incompatíveis separados (hipoclorito × ácidos; oxigénio × gases inflamáveis); kit acessível; FDS disponíveis; sem fugas.",
     "Observação + contagem (locais ARM-04 a ARM-09 do RG-SGA-21)", "Mensal", "Responsável de Armazém e Logística", "AA-005", "8.1", "Não"),
    ("RON-10", CATS[4], "INJ", "Máquinas e iluminação em paragens.",
     "Máquinas paradas > 30 min em standby; iluminação desligada em zonas sem atividade.", "Observação", "Semanal", "Chefe de Turno", "AA-007", "8.1", "Não"),
]


def execucoes():
    rng = np.random.default_rng(4300)
    rows = []
    start = dt.date(2026, 1, 5)
    wk = 0
    while True:
        dia = start + dt.timedelta(weeks=wk)
        if dia > dt.date(2026, 12, 28):   # rondas semanais até ao fim de 2026
            break
        wk += 1
        rid = f"RND-26-{wk:02d}"
        for p in PONTOS:
            pid = p[0]
            if pid == "RON-11" and dia < dt.date(2026, 10, 1):
                continue                                      # ponto criado em 24/09/2026 (PAM-26-33): 1.ª ronda em outubro
            monthly = pid in ("RON-05", "RON-06")
            if monthly and dia.day > 7 and dia != dt.date(2026, 9, 14):
                continue
            prob = {"RON-01": 0.12, "RON-02": 0.15, "RON-03": 0.35, "RON-04": 0.12, "RON-05": 0.10, "RON-06": 0.0,
                    "RON-07": 0.10, "RON-08": 0.03, "RON-09": 0.40, "RON-10": 0.30, "RON-11": 0.08}[pid]
            if pid == "RON-01" and dt.date(2026, 6, 1) <= dia <= dt.date(2026, 8, 31):
                prob = 0.45                                   # coerente com o desvio de solvente (5.2)
            if pid == "RON-03" and dia >= dt.date(2026, 7, 13):
                prob = 0.18                                   # campanha de fugas PAM-26-01
            if pid == "RON-09" and dia >= dt.date(2026, 7, 1):
                prob = 0.22 if dia < dt.date(2026, 10, 15) else 0.10   # programa OCS PAM-26-11 (filtros em todas as sarjetas em out/2026)
            if pid == "RON-01" and dia >= dt.date(2026, 11, 10):
                prob = 0.05                                   # dispensadores de segurança (PAM-26-08)
            if pid == "RON-03" and dia >= dt.date(2026, 11, 16):
                prob = 0.08                                   # programa de fugas + 6,8 bar (SGE PA-E-02)
            if pid == "RON-10" and dia >= dt.date(2026, 10, 5):
                prob = 0.07                                   # standby obrigatório (PAM-26-06 / SGE PA-E-03)
            nc = rng.random() < prob
            obs, idnc = None, None
            if pid == "RON-06" and dia == dt.date(2026, 9, 14):
                nc, obs, idnc = True, "KIT-03 com selo partido e quase vazio, sem registo de utilização.", "NC-SGA-26-03"
            elif nc:
                obs = {"RON-01": "Lata(s) de solvente aberta(s) no posto.", "RON-02": "Recipiente fora de bacia.", "RON-03": "Fuga audível sem etiqueta.",
                       "RON-04": "Óleo acumulado no tabuleiro.", "RON-05": "Sarjeta parcialmente obstruída.", "RON-07": "Contentor sem etiqueta LER / mistura.",
                       "RON-08": "Contentor de perigosos sem tampa.", "RON-09": "Grânulos no pavimento junto aos silos.", "RON-10": "Máquina parada sem standby.",
                       "RON-11": "Bidões incompatíveis na mesma bacia."}[pid]
            rows.append(dict(ID_Ronda=rid, Data=dia, Turno=int(rng.choice([1, 2, 3], p=[0.6, 0.3, 0.1])), ID_Ponto=pid,
                             Resultado="Não conforme" if nc else "Conforme", Observacao=obs,
                             Acao_Imediata=("Corrigido no momento" if nc and pid in ("RON-01", "RON-10") else ("Pedido de reposição / ordem de trabalho" if nc else None)),
                             ID_NC=idnc, Evidencia_Foto=f"{rid}-{pid}.jpg" if nc else None,
                             Verificador="Gestor do SGA / EHS (Responsável Ambiental)" if wk % 2 else "Chefe de Turno"))
    # data real da ronda do kit: 15/09 (ronda mensal)
    for r in rows:
        if r["ID_NC"] == "NC-SGA-26-03":
            r["Data"] = dt.date(2026, 9, 15)
    return rows


def build(out):
    b = Book("RG-SGA-10", "Controlo Operacional — Checklist de Supervisão e Registo de Rondas Ambientais",
             activities="Atividade 4.3 — Criação de Checklist de Supervisão Operacional (Ronda Ambiental): 4 categorias × 2 pontos de controlo (+ 2 pontos extra).",
             clauses="8.1 Planeamento e controlo operacional; 8.2 (meios de emergência); 9.1.1 (monitorização)",
             purpose="Definir os pontos de controlo com critério de aceitação objetivo (quando está OK?) e registar cada ronda ponto a ponto, com evidência e ligação às NC. O histórico semanal de 2026 permite medir a taxa de conformidade por ponto, área e mês e prever onde os desvios vão ocorrer.",
             links=[("RG-SGA-03 Aspetos", "ID_Aspeto: aspeto que o ponto controla."), ("RG-SGA-07 NC", "ID_NC: não conformidade aberta a partir da ronda.")])
    b.add_list("Categoria", CATS)
    b.add_list("Processo", PROC_CODES)
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Resultado", ["Conforme", "Não conforme", "Não aplicável"])
    b.add_list("SimNao", ["Sim", "Não"])
    pcols = [col("ID_Ponto", 8, desc="Ponto de controlo.", key="PK"), col("Categoria", 24, dv="Categoria", desc="Categoria de inspeção."),
             col("Area", 7, dv="Processo", desc="Área/processo."), col("Ponto_Controlo", 40, desc="O que verificar?"),
             col("Criterio_Aceitacao", 56, desc="Quando está OK? (critério objetivo)"), col("Metodo", 22, desc="Como verificar."),
             col("Frequencia", 14, desc="Frequência."), col("Responsavel", 24, dv="Funcao", desc="Quem verifica."),
             col("ID_Aspeto", 8, desc="Aspeto controlado.", key="FK → RG-SGA-03"), col("Clausula", 7, desc="Requisito."),
             col("Selecionado_Atv_4_3", 10, dv="SimNao", desc="Ponto da checklist da Atividade 4.3."),
             col("N_Verificacoes", 9, "int", f='=COUNTIF(tbl_execucao_rondas[ID_Ponto],@ID_Ponto@)', desc="N.º de verificações em 2026."),
             col("Taxa_Conformidade", 10, "pct", f='=IFERROR(COUNTIFS(tbl_execucao_rondas[ID_Ponto],@ID_Ponto@,tbl_execucao_rondas[Resultado],"Conforme")/@N_Verificacoes@,"")', desc="% conforme em 2026."),
             col("Taxa_Ultimas_8", 10, "pct", f='=IFERROR(COUNTIFS(tbl_execucao_rondas[ID_Ponto],@ID_Ponto@,tbl_execucao_rondas[Resultado],"Conforme",tbl_execucao_rondas[Data],">="&(DataRef-56))/COUNTIFS(tbl_execucao_rondas[ID_Ponto],@ID_Ponto@,tbl_execucao_rondas[Data],">="&(DataRef-56)),"")', desc="% conforme nas últimas 8 semanas."),
             col("Tendencia", 12, f='=IF(OR(@Taxa_Ultimas_8@="",@Taxa_Conformidade@=""),"",IF(@Taxa_Ultimas_8@-@Taxa_Conformidade@>=0.05,"▲ Melhoria",IF(@Taxa_Conformidade@-@Taxa_Ultimas_8@>=0.05,"▼ Degradação","≈ Estável")))', desc="Comparação últimas 8 semanas vs ano.")]
    pn = [c["name"] for c in pcols if not c["f"]]
    b.table("Pontos_Controlo", "tbl_pontos", pcols, [dict(zip(pn, p)) for p in PONTOS],
            "Checklist de supervisão: pontos de controlo e critérios de aceitação, com desempenho calculado.",
            title="CHECKLIST DE SUPERVISÃO OPERACIONAL (RONDA AMBIENTAL) — PLASTICOM",
            subtitle="Categoria → Ponto de controlo (o que verificar?) → Critério de aceitação (quando está OK?) · Desempenho calculado a partir das rondas de 2026",
            cf=[("Tendencia", {"Melhoria": "green", "Degradação": "red", "Estável": "yellow"}),
                ("Taxa_Conformidade", "AND(ISNUMBER(@),@<0.8)", "red"), ("Categoria", {"extra": "gray"})],
            row_height=62, freeze_col=1)

    ex = execucoes()
    ecols = [col("ID_Ronda", 10, desc="Ronda (semana).", key="PK (com ID_Ponto)"), col("Data", 11, "date", desc="Data da ronda."),
             col("Ano_Mes", 8, "int", f='=YEAR(@Data@)*100+MONTH(@Data@)', desc="Mês AAAAMM (chave numérica para agregação, independente do idioma do Excel)."), col("Turno", 6, "int", desc="Turno em que foi feita."),
             col("ID_Ponto", 8, desc="Ponto verificado.", key="FK → tbl_pontos"),
             col("Categoria", 24, f='=IFERROR(INDEX(tbl_pontos[Categoria],MATCH(@ID_Ponto@,tbl_pontos[ID_Ponto],0)),"")', desc="Categoria do ponto."),
             col("Resultado", 12, dv="Resultado", desc="Conforme / Não conforme / Não aplicável."), col("Observacao", 40, desc="Descrição do desvio.", req=False),
             col("Acao_Imediata", 28, desc="Ação no momento.", req=False), col("ID_NC", 12, desc="NC aberta.", key="FK → RG-SGA-07", req=False),
             col("Evidencia_Foto", 18, desc="Ficheiro de fotografia.", req=False), col("Verificador", 26, dv="Funcao", desc="Quem fez a ronda."),
             col("NC_Flag", 7, "int", f='=IF(@Resultado@="Não conforme",1,0)', desc="1 = não conforme (variável alvo para modelos).")]
    b.table("Execucao_Rondas", "tbl_execucao_rondas", ecols, ex, "Registo das rondas (1 linha por ronda × ponto) — série temporal para análise.",
            cf=[("Resultado", {"Não conforme": "red", "Conforme": "green"})])

    # indicadores mensais por categoria
    ws = b.sheet("Indicadores_Mensais", "Taxa de conformidade mensal por categoria (calculada) — KPI-10.")
    ws["A1"] = "TAXA DE CONFORMIDADE DAS RONDAS POR MÊS E CATEGORIA (KPI-10)"
    ws["A1"].font = F_TITLE
    meses = [202600 + m for m in range(1, 13)]
    header_row(ws, 3, ["Categoria"] + [f"2026-{m % 100:02d}" for m in meses] + ["2026"], widths=[36] + [9] * 13)
    E = lambda f: b.ref("tbl_execucao_rondas", f)
    for k, c in enumerate(CATS + ["TOTAL"]):
        r = 4 + k
        ws.cell(row=r, column=1, value=c).font = F_BOLD if c == "TOTAL" else F_BASE
        crit = "" if c == "TOTAL" else f',{E("Categoria")},"{c}"'
        for j, m in enumerate(meses + [None]):
            mc = "" if m is None else f',{E("Ano_Mes")},{m}'
            f = f'=IFERROR(COUNTIFS({E("Resultado")},"Conforme"{crit}{mc})/COUNTIFS({E("Resultado")},"<>Não aplicável"{crit}{mc}),"")'
            cc = ws.cell(row=r, column=2 + j, value=f)
            cc.number_format = "0%"
            cc.border = BORDER
    rng = f"B4:N{4 + len(CATS)}"
    ws.conditional_formatting.add(rng, FormulaRule(formula=["AND(ISNUMBER(B4),B4<0.8)"], fill=PatternFill("solid", fgColor=CF_COLORS["red"][0])))
    ws.conditional_formatting.add(rng, FormulaRule(formula=["AND(ISNUMBER(B4),B4>=0.9)"], fill=PatternFill("solid", fgColor=CF_COLORS["green"][0])))

    # formulário de ronda para o terreno
    ws = b.sheet("Checklist_Ronda_Impressao", "Checklist de ronda para imprimir e levar para o terreno (pontos e critérios calculados a partir da tabela).", tab_color="7030A0")
    heads = ["Categoria", "Ponto de controlo (O que verificar?)", "Critério de aceitação (Quando está OK?)", "C", "NC", "NA", "Observação / evidência / ação"]
    doc_header(ws, "RG-SGA-10", "CHECKLIST DE SUPERVISÃO OPERACIONAL — RONDA AMBIENTAL", "Mod. RON-SGA", len(heads))
    ws.cell(row=4, column=1, value="Data: ____/____/______     Turno: ____     Verificador: ______________________     Ronda n.º: RND-26-____").font = F_BASE
    header_row(ws, 5, heads, widths=[24, 38, 56, 5, 5, 5, 40])
    P = lambda f: b.ref("tbl_pontos", f)
    for k in range(len(PONTOS)):
        r = 6 + k
        for j, fld in enumerate(["Categoria", "Ponto_Controlo", "Criterio_Aceitacao"]):
            c = ws.cell(row=r, column=j + 1, value=f'=INDEX({P(fld)},{k + 1})')
            c.font, c.alignment, c.border = Font(name=FONT, size=9), WRAP_TOP, BORDER
        for j in range(3, 7):
            ws.cell(row=r, column=j + 1).border = BORDER
        ws.row_dimensions[r].height = 58
    r = 7 + len(PONTOS)
    ws.cell(row=r, column=1, value="Regra: qualquer 'NC' exige ação imediata registada e, se não for corrigível no momento, abertura de RNC (RG-SGA-07).").font = F_SUB
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToHeight = 0
    X.extra_10(b)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
