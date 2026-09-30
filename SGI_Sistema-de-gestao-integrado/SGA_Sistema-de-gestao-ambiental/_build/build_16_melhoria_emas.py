import datetime as dt
import os
import pandas as pd
from sgalib import *
from dims import *
from envdata import ambiente, anual, SILVER, P
import build_19_esg_ambiental as _G19
import build_21_quimicos as _Q21
# totais com fonte unica: GEE do inventario do RG-SGA-19 e COV do inventario de quimicos do RG-SGA-21
G19 = _G19.totais_gee()
Q21 = _Q21.resumo()

d = dt.date.fromisoformat


def pausas_turno3():
    dd = pd.read_csv(os.path.join(SILVER, "fact_downtime_processed.csv"), low_memory=False, usecols=["Date", "StoppageReason"])
    dd = dd[dd.StoppageReason.astype(str).str.startswith("Meal Break (Shift 3")]
    dd["Mes"] = dd.Date.astype(str).str[:7]
    m = dd[(dd.Mes >= "2026-01") & (dd.Mes <= "2026-12")].groupby("Mes").size()
    return round(m.mean())


def build(out):
    prod, mm, fact, res = ambiente()
    A = anual(fact, res, prod)
    pr = prod.copy()
    pr["Mes"] = pd.to_datetime(pr["Mes"])
    p12 = pr[(pr.Mes >= "2026-01-01") & (pr.Mes <= "2026-12-01")]
    t_prod = (p12[p12.Processo == "SOP"].Unid.sum() * P["G_FRASCO"] + p12[p12.Processo == "INJ"].Unid.sum() * P["G_TAMPA"]) / 1e6
    solv_m = A["solvente_kg"] / 12
    scrap_m = (fact[(fact.Variavel == "SCRAP_KG") & fact.Processo.isin(["INJ", "SOP"])].Valor.sum()) / fact.Mes.nunique()
    n_pausas = pausas_turno3()

    b = Book("RG-SGA-16", "Melhoria Contínua — Registo de Ideias Kaizen e Indicadores EMAS",
             activities="Atividade 6.2 (Tarefa 1: ideia Kaizen KZ-01 e benefício duplo; Tarefa 2: registo no PAM como PAM-26-06). Atividade 6.3 (indicadores principais EMAS e transparência vs risco).",
             clauses="10.1 Melhoria contínua (ISO 14001:2026); 7.4 (participação dos trabalhadores); Regulamento (CE) n.º 1221/2009 (EMAS), Anexo IV",
             purpose="Registar as ideias de melhoria dos trabalhadores com o cálculo do benefício ambiental e económico (poupança, payback e tCO2e evitadas por fórmula), e preparar os indicadores principais da Declaração Ambiental EMAS (valor anual A, produção B e rácio R = A/B) com a criticidade para a Plasticom.",
             links=[("RG-SGA-06 PAM", "KZ-01 → PAM-26-06 (Tipo M)."), ("RG-SGA-13 Monitorização", "Valores anuais do EMAS = soma jan–dez/2026 da base de dados mensal.")])
    b.add_list("EstadoKZ", ["Proposta", "Aprovada", "Em implementação", "Implementada", "Rejeitada"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Escala15", [1, 2, 3, 4, 5])

    K = [
        ("KZ-01", "2026-09-18", "Chefe de turno 3 (Injeção)", "INJ", "Standby das máquinas na pausa de refeição do turno 3",
         "Na pausa de 80 min do turno 3 (sem equipa de rendição), pôr as injetoras e ISBM em modo standby (resistências a 60%, bomba hidráulica desligada) em vez de ficarem aquecidas em vazio.",
         "Menos eletricidade em vazio → menos emissões de GEE (âmbito 2) e menos calor para o chiller.", "Menos kWh na fatura; custo zero (só procedimento e etiqueta).",
         "kWh", n_pausas, 11, 0.14, 300, "Implementada", "PAM-26-06", "Sim",
         "Driver: n.º médio de pausas de turno 3 por mês (dataset de paragens, jan–dez/2026). Fator: kWh evitados por pausa (estimativa 60 min × ≈ 11 kW de aquecimento/hidráulica em vazio)."),
        ("KZ-02", "2026-09-10", "Operador de serigrafia (turno 1)", "SER", "Regra 'tampa fechada' e solvente só no dispensador",
         "Fechar sempre a lata/dispensador de solvente após cada limpeza e nunca deixar panos embebidos abertos.",
         "Menos evaporação de COV (poluição do ar) e menos resíduo perigoso.", "Menos solvente comprado.",
         "kg solvente", round(solv_m, 1), 0.10, 4.5, 0, "Implementada", "PAM-26-08", "Não",
         "Driver: solvente consumido por mês. Fator: 10% de perdas por evaporação evitadas."),
        ("KZ-03", "2026-07-02", "Operador de sopro (turno 2)", "SOP", "Caixas coloridas por cor/polímero para o scrap",
         "Segregar o scrap limpo na fonte em caixas de cor por polímero e cor, para poder ser moído e reintegrado sem contaminação.",
         "Menos polímero virgem e menos resíduo plástico (circularidade interna).", "Menos compra de resina.",
         "kg polímero", round(scrap_m), 0.08, 1.35, 450, "Em implementação", "PAM-26-12", "Não",
         "Driver: scrap de injeção + sopro por mês. Fator: +8 p.p. de reintegração."),
        ("KZ-04", "2026-08-20", "Técnico de manutenção", "UTL", "Fechar os ramais de ar comprimido sem produção ao fim de semana",
         "Fechar as válvulas de isolamento dos ramais de ar comprimido das áreas paradas ao fim de semana (fugas deixam de ser alimentadas).",
         "Menos energia dos compressores.", "Menos kWh.", "kWh", 4.3, 180, 0.14, 0, "Implementada", "PAM-26-01", "Não",
         "Driver: fins de semana por mês. Fator: kWh consumidos pelas fugas num fim de semana (teste de vazio)."),
    ]
    kcols = [col("ID_KZ", 7, desc="Ideia.", key="PK"), col("Data", 11, "date", desc="Data da proposta."), col("Proponente", 24, desc="Quem propôs (função/turno)."),
             col("Area", 7, dv="Processo", desc="Área."), col("Titulo", 36, desc="Ideia (curta)."), col("Descricao", 50, desc="Mudança de rotina/organização/comportamento."),
             col("Beneficio_Ambiental", 36, desc="Como ajuda o ambiente."), col("Beneficio_Economico", 30, desc="Como poupa dinheiro."),
             col("Unidade_Poupanca", 11, desc="Unidade do recurso poupado."), col("Driver_Mensal", 10, "num1", desc="Quantidade de base por mês (ver Pressupostos)."),
             col("Fator_Poupanca", 10, "num3", desc="Poupança por unidade de driver."), col("Custo_Unitario_EUR", 10, "num", desc="€ por unidade de recurso."),
             col("Custo_Implementacao_EUR", 11, "eur", desc="Custo de implementação."), col("Estado", 13, dv="EstadoKZ", desc="Estado."),
             col("ID_PAM", 10, desc="Ação no PAM.", key="FK → RG-SGA-06", req=False), col("Selecionado_Atv_6_2", 9, dv="SimNao", desc="Ideia da Atividade 6.2."),
             col("Pressupostos", 50, desc="Origem do driver e do fator."),
             col("Poupanca_Anual_Qtd", 12, "num0", f="=@Driver_Mensal@*@Fator_Poupanca@*12", desc="Recurso poupado por ano."),
             col("Poupanca_Anual_EUR", 12, "eur", f="=@Poupanca_Anual_Qtd@*@Custo_Unitario_EUR@", desc="Poupança anual (€)."),
             col("Payback_Meses", 9, "num1", f='=IF(@Poupanca_Anual_EUR@=0,"",@Custo_Implementacao_EUR@/@Poupanca_Anual_EUR@*12)', desc="Retorno (meses)."),
             col("tCO2e_Evitadas_Ano", 10, "num1", f=f'=IF(@Unidade_Poupanca@="kWh",@Poupanca_Anual_Qtd@*{P["FE_ELET"]}/1000,IF(@Unidade_Poupanca@="kg polímero",@Poupanca_Anual_Qtd@*1.8/1000,0))', desc="Emissões evitadas (kWh × 0,110 kgCO2e/kWh; polímero × 1,8 kgCO2e/kg)."),
             col("Custo_Zero", 9, f='=IF(@Custo_Implementacao_EUR@<=500,"Sim","Não")', desc="Custo zero ou quase zero (≤ 500 €)?")]
    kn = [c["name"] for c in kcols if not c["f"]]
    order = ["ID_KZ", "Data", "Proponente", "Area", "Titulo", "Descricao", "Beneficio_Ambiental", "Beneficio_Economico", "Unidade_Poupanca", "Driver_Mensal",
             "Fator_Poupanca", "Custo_Unitario_EUR", "Custo_Implementacao_EUR", "Estado", "ID_PAM", "Selecionado_Atv_6_2", "Pressupostos"]
    krows = []
    for k in K:
        dd = dict(zip(order, k))
        dd["Data"] = d(dd["Data"])
        dd["ID_PAM"] = dd["ID_PAM"] or None
        krows.append(dd)
    b.table("Ideias_Kaizen", "tbl_kaizen", kcols, krows, "Banco de ideias Kaizen com benefício ambiental e económico calculado.",
            title="REGISTO DE IDEIAS KAIZEN — PEQUENAS MUDANÇAS, GRANDE IMPACTO", subtitle="Poupança = driver mensal × fator × 12 · € = quantidade × custo unitário · tCO2e com o fator da eletricidade 0,110 kgCO2e/kWh",
            cf=[("Selecionado_Atv_6_2", {"Sim": "purple"}), ("Custo_Zero", {"Sim": "green"})], row_height=80, freeze_col=1)

    ws = b.sheet("Resumo_Atividade_6_2", "Ficha da Atividade 6.2 (Tarefa 1 e Tarefa 2) para a ideia KZ-01.", tab_color="7030A0")
    ws["A1"] = "ATIVIDADE 6.2 — KAIZEN: BENEFÍCIO DUPLO E REGISTO NO PLANO DE AÇÕES"
    ws["A1"].font = F_TITLE
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 100
    T = lambda f: b.ref("tbl_kaizen", f)
    m = f'MATCH("KZ-01",{T("ID_KZ")},0)'
    r = 3
    ws.cell(row=r, column=1, value="TAREFA 1 — A ideia Kaizen e o benefício duplo").font = F_BOLD
    r += 1
    for lab, fld, fmt in [("Pequena mudança (custo ≈ zero)", "Descricao", None), ("Ajuda o ambiente porque…", "Beneficio_Ambiental", None),
                          ("Poupa dinheiro porque…", "Beneficio_Economico", None), ("Poupança anual (kWh)", "Poupanca_Anual_Qtd", "#,##0"),
                          ("Poupança anual (€)", "Poupanca_Anual_EUR", "#,##0 €"), ("Emissões evitadas (tCO2e/ano)", "tCO2e_Evitadas_Ano", "0.0"),
                          ("Custo de implementação (€)", "Custo_Implementacao_EUR", "#,##0 €"), ("Payback (meses)", "Payback_Meses", "0.0")]:
        c = form_block(ws, r, lab, f"=INDEX({T(fld)},{m})", vw=1, height=40 if fmt is None else None)
        if fmt:
            c.number_format = fmt
            c.alignment = Alignment(horizontal="left")
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="TAREFA 2 — Registo no Plano de Ações (Mod.G.10.00) — PAM-26-06").font = F_BOLD
    r += 1
    for lab, txt in [("Fonte / Doc. Afeto", "Caixa de Sugestões / Kaizen (ideia KZ-01, proposta pelo chefe de turno 3 em 18/09/2026) — oportunidade 10.1"),
                     ("Oportunidade de Melhoria", "Na pausa de refeição de 80 min do turno 3, as injetoras e ISBM ficam aquecidas e em vazio; passar a modo standby."),
                     ("Ações a implementar / Tipo (M)", "(M) 1) Definir o modo standby de cada máquina com a manutenção (resistências a 60%, bomba hidráulica desligada, chiller em eco). 2) Colocar a etiqueta 'Pausa 3.º turno' no painel de cada máquina. 3) Criar o checklist de pausa assinado pelo chefe de turno. 4) Formar os operadores do turno 3 (10 min). 5) Medir a poupança com os analisadores de energia (PAM-26-02) e reportar na reunião mensal."),
                     ("Responsável", "Gerente de Produção (implementação); Chefe de turno 3 (execução diária); Gestor do SGA (monitorização da poupança)"),
                     ("Prazo", "30/11/2026 (100% a funcionar); avaliação da eficácia em 28/02/2027 (≥ 90% das pausas com standby e ≥ 1.500 kWh/mês poupados)")]:
        form_block(ws, r, lab, txt, vw=1, height=60 if lab.startswith("Ações") else 32)
        r += 1

    # EMAS
    EM = [
        ("EMAS-01", "Eficiência energética", "Consumo total direto de energia", round(A["ene_total_kwh"] / 1000, 1), "MWh", 5,
         "É o 1.º custo ambiental e a origem de ≈ 99% das emissões de GEE: injeção e sopro são eletrointensivos (≈ 7,8 GWh/ano, instalação SGCIE)."),
        ("EMAS-01b", "Eficiência energética", "Energia renovável (garantias de origem)", round(A["ene_total_kwh"] / 1000 * P["REN_SHARE"], 1), "MWh", 5,
         "Quota renovável de 55%; a UPAC em estudo pode acrescentar ≈ 1.400 MWh/ano."),
        ("EMAS-02", "Eficiência dos materiais", "Fluxo mássico de materiais (polímero, tintas, solvente, foil)", round((A["polimero_kg"] + A["tinta_kg"] + A["solvente_kg"] + A["foil_kg"]) / 1000, 1), "t", 5,
         "O polímero é o maior fluxo de matéria (≈ 810 t/ano) e define a pegada do produto, o scrap e a conformidade PPWR (conteúdo reciclado)."),
        ("EMAS-03", "Água", "Consumo total anual de água", round(A["agua_total"]), "m³", 3,
         "Relevante mas moderado (≈ 9.400 m³): 80% é a torre de arrefecimento; sensível às secas e ao calor."),
        ("EMAS-04", "Resíduos", "Produção total anual de resíduos", round(A["res_total"] / 1000, 1), "t", 4,
         "Scrap e embalagens são os maiores fluxos; a taxa de valorização (≈ 80%) é um indicador de circularidade valorizado pelos clientes."),
        ("EMAS-04b", "Resíduos", "Resíduos perigosos", round(A["res_perig"] / 1000, 2), "t", 4,
         "Pouca quantidade (≈ 2 t) mas com gravidade alta (tintas, solventes, óleos)."),
        ("EMAS-05", "Biodiversidade", "Utilização total do solo", 45000, "m²", 2,
         "Terreno de ≈ 4,5 ha em zona industrial, mas vizinho do Pinhal de Leiria: o risco de perdas de granulado e de incêndio liga a instalação à biodiversidade."),
        ("EMAS-05b", "Biodiversidade", "Área impermeabilizada", 32000, "m²", 2, "71% do terreno impermeabilizado; áreas verdes com espécies nativas em estudo."),
        ("EMAS-05c", "Biodiversidade", "Área orientada para a natureza no local", 3500, "m²", 2, "Faixa arborizada a norte (gestão de combustível e habitat)."),
        ("EMAS-06", "Emissões", "Emissões anuais de GEE (âmbitos 1 + 2 location-based — RG-SGA-19)", round(G19["S1"] + G19["S2LB"], 1), "tCO2e", 4,
         f"Mesmo cálculo do inventário de GEE (RG-SGA-19): âmbito 2 {G19['S2LB']:.0f} tCO2e da eletricidade + âmbito 1 {G19['S1']:.1f} tCO2e (gasóleo e fuga de R410A de nov/2025)."),
        ("EMAS-06b", "Emissões", "Emissões de COV (balanço do inventário de químicos — RG-SGA-21)", Q21["cov_t"], "t", 4,
         "Aspeto significativo (IRA 40); inclui solvente de limpeza, tintas, diluente, retardador, isopropanol e aerossóis; abaixo do limiar legal de 5 t/ano."),
    ]
    ecols = [col("ID_EMAS", 9, desc="Indicador.", key="PK"), col("Dominio", 20, desc="Domínio-chave do Anexo IV EMAS."),
             col("Indicador", 50, desc="Indicador."), col("Valor_A", 12, "num1", desc="A: impacto/consumo total anual (jan–dez/2026)."),
             col("Unidade_A", 8, desc="Unidade de A."), col("Producao_B_t", 12, "num1", desc="B: produção anual total (t de produto: frascos + tampas)."),
             col("Racio_R", 12, "num3", f="=IF(@Producao_B_t@=0,\"\",@Valor_A@/@Producao_B_t@)", desc="R = A / B (por tonelada de produto)."),
             col("Unidade_R", 12, f='=@Unidade_A@&"/t"', desc="Unidade de R."),
             col("Criticidade_1a5", 10, "int", dv="Escala15", desc="Criticidade para a Plasticom (5 = mais crítico)."),
             col("Ranking", 8, "int", f='=IF(RIGHT(@ID_EMAS@,1)="b","",IF(RIGHT(@ID_EMAS@,1)="c","",COUNTIFS(#Criticidade_1a5#,">"&@Criticidade_1a5@,#ID_EMAS#,"<>*b",#ID_EMAS#,"<>*c")+1))', desc="Posição do domínio (indicadores principais)."),
             col("Justificacao", 70, desc="Justificação com base na atividade da Plasticom.")]
    erows = [dict(ID_EMAS=i, Dominio=dm, Indicador=ind, Valor_A=v, Unidade_A=u, Producao_B_t=round(t_prod, 1), Criticidade_1a5=c, Justificacao=j) for i, dm, ind, v, u, c, j in EM]
    b.table("EMAS_Indicadores", "tbl_emas", ecols, erows, "Indicadores principais EMAS (Anexo IV): A, B, R = A/B e criticidade — Atividade 6.3 (Q1).",
            title="DECLARAÇÃO AMBIENTAL EMAS — INDICADORES PRINCIPAIS (PREPARAÇÃO 2027)", subtitle="R = A / B · B = toneladas de produto (frascos + tampas) · Período jan–dez/2026 · Criticidade: 5 = mais crítico",
            cf=[("Criticidade_1a5", "@>=5", "red"), ("Criticidade_1a5", "@=4", "orange")], row_height=48, freeze_col=2)

    TR = [
        ("TR-01", "Publicar a subida de 15% do solvente e a NC de ruído pode ser usado por concorrentes e prejudicar a imagem junto de clientes e vizinhos.",
         "Os clientes (cosmética, alimentar, farmacêutica) e as autoridades já pedem estes dados; publicar dados verificados com o plano de ação mostra controlo e credibilidade, enquanto esconder expõe a acusações de greenwashing (Diretiva (UE) 2024/825). Uma tendência negativa com ação explicada é mais credível do que números sempre perfeitos.",
         "Publicar sempre o dado com contexto (causa, ação, meta e prazo) e mostrar a série de 3 anos; a verificação pelo verificador acreditado garante que o dado é justo e comparável."),
        ("TR-02", "Custo e trabalho de preparar e verificar a Declaração Ambiental todos os anos.",
         "Os dados já existem no painel ambiental (RG-SGA-13) e nos registos do SGA; a declaração reutiliza-os. O registo EMAS pode reduzir inspeções/taxas e dá acesso a concursos públicos e clientes que exigem EMAS.",
         "Automatizar a Declaração a partir do modelo de dados; começar pela declaração simplificada nos anos intermédios quando aplicável."),
        ("TR-03", "Obrigação de 'tolerância zero' legal: as NC legais de ruído e PPWR impedem o registo.",
         "É verdade: por isso o plano é resolver as 2 NC até 31/12/2026 e pedir o registo em 2027. Esta exigência reforça a gestão da conformidade (valor para o negócio).",
         "Incluir o fecho das NC legais como pré-requisito no plano EMAS (decisão RG-26-D04)."),
    ]
    tcols = [col("ID", 7, desc="Tema.", key="PK"), col("Receio_Gestao_Topo", 50, desc="Receio de publicar os dados."),
             col("Argumento_Transparencia", 70, desc="Porque a transparência compensa o risco."), col("Mitigacao", 50, desc="Como reduzir o risco.")]
    b.table("EMAS_Transparencia", "tbl_emas_transparencia", tcols, [dict(ID=a, Receio_Gestao_Topo=r_, Argumento_Transparencia=g, Mitigacao=mi) for a, r_, g, mi in TR],
            "Atividade 6.3 (Q2): receios da gestão de topo em publicar dados e argumentos a favor da transparência.", row_height=110)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
