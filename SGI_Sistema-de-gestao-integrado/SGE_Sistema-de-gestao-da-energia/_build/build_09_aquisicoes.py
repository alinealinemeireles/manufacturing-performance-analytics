"""RG-SGE-09 — Projeto (design), aquisições com critérios de desempenho energético, custo do ciclo de vida, compra de energia e faturas.
ISO 50001:2018 8.2, 8.3 a)–b) · EN 17463:2021 (VALERI — avaliação de investimentos em energia) · Reg. (UE) 2019/1781 (motores)."""
from sgelib import *
from dimse import *
import edata

PROJETOS = [
    ("PRJ-E-01", "Linhas alimentar e farmacêutica: IM-007/008 e ISBM-009/010 (ALT-2026-03)", "Novo", "Sim", "Máquinas totalmente elétricas e ISBM com recuperação de ar escolhidas",
     "Não documentado (sem critérios de standby nem medição por máquina)", "Parcial: escolha tecnológica eficiente, mas sem avaliação do desempenho energético ao longo da vida nem LCC", "Não", "Atas do projeto; propostas dos fornecedores", "Concluído", "ALT-2026-03"),
    ("PRJ-E-02", "Central fotovoltaica de autoconsumo UPAC ≈ 1 MWp (ALT-2026-07)", "Novo", "Sim", "Autoconsumo ≈ 1 400 MWh/ano; perfil de carga 24/5 favorável",
     "Gestão da injeção na rede e da potência", "Estudo de viabilidade encomendado (RG-26-D04 do SGA)", "Sim", "Estudo de viabilidade (em curso)", "Em estudo", "ALT-2026-07"),
    ("PRJ-E-03", "Substituição do chiller CH-01 (R410A) por chiller de baixo GWP com free-cooling integrado", "Renovado", "Sim", "SEER/SEPR mínimos, free-cooling, VSD nos compressores do chiller",
     "Setpoint ajustável e medição de energia térmica", "Especificação técnica com SEPR ≥ 6,5 e free-cooling", "Sim", "Caderno de encargos CE-2027-03 (rascunho)", "Em estudo", "—"),
    ("PRJ-E-04", "Novo molde de potes PT-013 com câmara quente", "Modificado", "Não", "Menos gito e tempo de ciclo mais curto (−8% kWh/peça estimado)", "Temperaturas por zona na ficha do molde",
     "Avaliado na revisão de design do RG-SGQ-11", "Sim", "RG-SGQ-11 DD-2026-04", "Concluído", "—"),
    ("PRJ-E-05", "Iluminação LED da nova zona de expedição", "Renovado", "Não", "LED 150 lm/W com sensores", "Horário e sensores", "Critérios aplicados", "Sim", "Encomenda EC-2026-311", "Concluído", "—"),
]

CRIT_AQ = [
    ("CAQ-01", "Máquinas de injeção e sopro", "Totalmente elétricas ou servo; kWh/kg declarado (EUROMAP 60.1/60.2) no ciclo de referência; standby automático", "Ficha EUROMAP; ensaio de receção com PA-01", "LCC obrigatório (> € 50 000)"),
    ("CAQ-02", "Compressores de ar", "Velocidade variável; potência específica (ISO 1217 anexo E) ≤ 6,0 kW/(m³/min) a 7 bar; recuperação de calor", "Ficha CAGI/ISO 1217", "LCC obrigatório"),
    ("CAQ-03", "Chillers e bombas de calor", "SEPR (Reg. (UE) 2016/2281) ≥ 6,5; free-cooling; fluido de baixo GWP", "Ficha Eurovent", "LCC obrigatório"),
    ("CAQ-04", "Motores e variadores", "Motores IE3 (≥ 0,75 kW) / IE4 (75–200 kW) conforme Reg. (UE) 2019/1781; VSD IE2", "Placa e declaração UE", "—"),
    ("CAQ-05", "Iluminação", "LED ≥ 140 lm/W; sensores de presença/luz natural", "Ficha técnica", "—"),
    ("CAQ-06", "Serviços com impacto nos USE (manutenção de compressores, chiller, moldes)", "Contrato inclui verificação de potência específica, fugas e setpoints; relatório de eficiência", "Relatório de intervenção", "—"),
    ("CAQ-07", "Compra de energia (8.3 b)", "Garantias de origem ≥ 55% (meta 100% em 2028); preço indexado + fixo; dados de 15 min; sem penalização por autoconsumo", "Contrato e rótulo de energia", "Análise anual de tarifas"),
]

AQUISICOES = [
    ("AQE-26-01", "2026-01-12", "Compressores de velocidade variável CMP-01/02", "CAQ-02", 96000, "Sim", "Sim", "Sim", "OT-2026-02 (RG-SGA-10); ALT-2026-01"),
    ("AQE-26-02", "2026-03-30", "4 máquinas das linhas novas (IM-007/008, ISBM-009/010)", "CAQ-01", 1480000, "Sim", "Sim", "Não", "ALT-2026-03 — sem LCC documentado"),
    ("AQE-26-03", "2026-05-20", "Analisador portátil PA-01", "—", 6500, "N/A", "N/A", "N/A", "EQE-01"),
    ("AQE-26-04", "2026-06-15", "Contrato de manutenção do chiller CH-01 (2026–2028)", "CAQ-06", 14400, "Não", "Não", "N/A", "Contrato sem cláusulas de eficiência (constatação CONE-A-26-04)"),
    ("AQE-26-05", "2026-09-10", "Iluminação LED da expedição (PRJ-E-05)", "CAQ-05", 18500, "Sim", "Sim", "N/A", "EC-2026-311"),
    ("AQE-26-06", "2026-09-20", "6 analisadores de energia (PA-E-01)", "—", 38000, "N/A", "N/A", "N/A", "PAM-26-02"),
    ("AQE-26-07", "2026-02-20", "Motor de 55 kW do moinho MOA-02 (substituição por avaria)", "CAQ-04", 4800, "Não", "Sim", "N/A", "Motor IE3 (mínimo legal); IE4 não avaliado"),
    ("AQE-26-08", "2026-11-05", "Retrofit servo-bomba IM-002 e IM-004 (PA-E-04) — consulta", "CAQ-01", 56000, "Sim", "Sim", "Sim", "LCC-01 a 03; decisão em 01/2027"),
    ("AQE-26-09", "2026-12-02", "Contrato de manutenção do chiller — aditamento com cláusulas de eficiência", "CAQ-06", 0, "Sim", "Sim", "N/A", "Correção da constatação CONE-A-26-04"),
]


def build(out):
    b = Book("RG-SGE-09", "Projeto, Aquisições, Custo do Ciclo de Vida e Compra de Energia",
             activities="Considerar oportunidades de melhoria do desempenho energético e o controlo operacional nos projetos; estabelecer critérios de avaliação do desempenho energético "
                        "ao longo da vida útil nas aquisições; informar os fornecedores; especificar a compra de energia; analisar faturas, tarifas e potência.",
             clauses="8.2 (projeto de instalações, equipamentos, sistemas e processos novos, modificados e renovados; resultados incorporados na especificação — reter); "
                     "8.3 (critérios ao longo da vida útil; informar os fornecedores; especificações a) do desempenho energético dos equipamentos e serviços e b) da compra de energia); 5.2 f), g).",
             purpose="Registo de projetos com a avaliação energética (8.2), critérios de aquisição por categoria, registo das aquisições de 2026 com o cumprimento de 8.3, LCC calculado "
                     "(três alternativas para a IM-002), especificação da compra de energia e faturas mensais simuladas com custo, preço médio e utilização da potência.",
             links=[("RG-SGA-18 / RG-SGQ-11", "Alterações e design (os projetos PRJ-E ligam a ALT-xx e DD-xx)."), ("RG-SGA-11", "Fornecedor de eletricidade ENE-01 (fonte única dos fornecedores)."),
                    ("RG-SGE-04", "Oportunidades de investimento (OPE-xx) avaliadas pelo LCC."), ("RG-SGE-05", "Preço médio usado nas poupanças (tbl_parametros).")],
             guidance=[("EN 17463:2021 (VALERI)", "Avaliação de investimentos em energia pelo valor atual líquido e pelo custo do ciclo de vida."),
                       ("ISO 50004:2020 §8.2–8.3", "Critérios de projeto e de compra com desempenho energético."),
                       ("EUROMAP 60.1 / 60.2", "Declaração do consumo específico de injetoras e máquinas de sopro."),
                       ("ISO 1217 (anexo E) e CAGI", "Potência específica de compressores."),
                       ("Kent/BPF", "Máquinas modernas ≥ 20% mais eficientes; totalmente elétricas até 60% menos que hidráulicas de 1996.")],
             legal=[("Reg. (UE) 2019/1781 (conceção ecológica de motores e variadores)", "Classe mínima IE3 (0,75–1 000 kW) e IE4 (75–200 kW) desde 07/2023; VSD IE2."),
                    ("Reg. (UE) 2016/2281 (chillers — SEPR)", "Eficiência mínima de chillers de processo."),
                    ("DL 15/2022 alterado pelo DL 130/2026 (Sistema Elétrico Nacional; autoconsumo)", "Licenciamento e regras da UPAC (PRJ-E-02); em vigor desde 27/08/2026."),
                    ("Regulamento Tarifário e de Relações Comerciais (ERSE)", "Estrutura das faturas de MT: períodos horários, potência em horas de ponta, potência contratada, energia reativa.")])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("SimNaoNA", ["Sim", "Não", "N/A"])

    PAR = [("PRECO_MEDIO", edata.preco_medio(), "€/kWh", "Preço médio (energia + redes) jan–dez/2026 — calculado das faturas", "tbl_faturas"),
           ("TAXA_DESCONTO", 0.06, "fração", "Taxa de atualização para o LCC", "Diretor Financeiro (WACC)"),
           ("ESCALADA_ENERGIA", 0.02, "fração/ano", "Crescimento anual do preço da eletricidade no LCC", "Pressuposto — sensibilidade na folha LCC"),
           ("PRECO_REATIVA", 0.0080, "€/kvarh", "Preço da energia reativa faturada", "Tarifário ERSE (simulado)")]
    parcols = [col("Codigo", 18, key="PK", desc="Parâmetro."), col("Valor", 10, "num3", desc="Valor."), col("Unidade", 10, desc="Unidade."), col("Descricao", 60, desc="Descrição."), col("Fonte", 30, desc="[Só SGE] Origem.")]
    b.table("Parametros", "tbl_parametros", parcols, [dict(zip(["Codigo", "Valor", "Unidade", "Descricao", "Fonte"], p_)) for p_ in PAR], "Parâmetros financeiros.", title="PARÂMETROS", row_height=18)
    tp = b.tables["tbl_parametros"]
    for i, p_ in enumerate(PAR):
        b.wb.defined_names[p_[0].lower()] = DefinedName(p_[0].lower(), attr_text=f"Parametros!${tp['colmap']['Valor']}${tp['first'] + i}")

    pcols = [col("ID_Projeto", 9, key="PK", desc="Projeto."), col("Projeto", 44, desc="Projeto."), col("Tipo", 10, desc="Novo / modificado / renovado."),
             col("Impacto_Significativo", 9, dv="SimNaoNA", desc="Pode ter impacto significativo no desempenho energético ao longo da vida?"),
             col("Oportunidades_Consideradas", 36, desc="Oportunidades de melhoria do desempenho energético consideradas (8.2)."),
             col("Controlo_Operacional_Considerado", 30, desc="Controlo operacional considerado (8.2)."), col("Resultado_Avaliacao", 40, desc="Resultado da avaliação do desempenho energético."),
             col("Incorporado_Especificacao", 9, dv="SimNaoNA", desc="Resultados incorporados na especificação, projeto e compra?"), col("Evidencia", 26, desc="Evidência (reter)."),
             col("Estado", 10, desc="Estado."), col("ID_Alteracao_SGI", 11, desc="Alteração no RG-SGA-18.", req=False),
             col("Conformidade_8_2", 12, f='=IF(@ID_Projeto@="","",IF(@Impacto_Significativo@="Não","N/A",IF(@Incorporado_Especificacao@="Sim","Conforme","Não conforme")))', desc="Cumpre 8.2?")]
    b.table("Projetos", "tbl_projetos", pcols, rows_from(input_names(pcols), PROJETOS), "Atividades de projeto relativas ao desempenho energético (8.2 — reter).",
            title="PROJETO (DESIGN) E DESEMPENHO ENERGÉTICO (8.2)", cf=[("Conformidade_8_2", {"Não conforme": "red", "Conforme": "green"})], row_height=48, freeze_col=2)
    b.table("Criterios_Aquisicao", "tbl_criterios_aquisicao",
            [col("ID_Criterio", 8, key="PK"), col("Categoria", 30), col("Criterio_Energetico", 60), col("Evidencia_Exigida", 28), col("Avaliacao_Economica", 22)],
            [dict(zip(["ID_Criterio", "Categoria", "Criterio_Energetico", "Evidencia_Exigida", "Avaliacao_Economica"], c_)) for c_ in CRIT_AQ],
            "Critérios de avaliação do desempenho energético nas aquisições (8.3).", title="CRITÉRIOS ENERGÉTICOS DE AQUISIÇÃO (8.3)", row_height=36)
    acols = [col("ID_Aquisicao", 9, key="PK", desc="Aquisição."), col("Data", 11, "date", desc="Data da consulta."), col("Descricao", 44, desc="Produto / serviço."),
             col("ID_Criterio", 8, desc="Critério aplicável.", key="FK → tbl_criterios_aquisicao"), col("Valor_EUR", 11, "eur", desc="Valor."),
             col("Fornecedor_Informado", 9, dv="SimNaoNA", desc="Fornecedores informados de que o desempenho energético é critério (8.3)?"),
             col("Criterio_Aplicado", 9, dv="SimNaoNA", desc="Critério energético aplicado na avaliação?"), col("LCC_Realizado", 9, dv="SimNaoNA", desc="LCC realizado (quando obrigatório)?"),
             col("Nota", 36, desc="Evidência / nota."),
             col("Conformidade_8_3", 12, f='=IF(@ID_Aquisicao@="","",IF(@ID_Criterio@="—","N/A",IF(AND(@Fornecedor_Informado@<>"Não",@Criterio_Aplicado@<>"Não",@LCC_Realizado@<>"Não"),"Conforme","Não conforme")))', desc="Cumpre 8.3?")]
    b.table("Aquisicoes_2026", "tbl_aquisicoes", acols, rows_from(input_names(acols), AQUISICOES, dates=("Data",)), "Aquisições de 2026 com impacto nos USE e cumprimento de 8.3.",
            title="AQUISIÇÕES DE 2026 COM IMPACTO NO DESEMPENHO ENERGÉTICO (8.3)", cf=[("Conformidade_8_3", {"Não conforme": "red", "Conforme": "green"})], row_height=30, freeze_col=2)

    # LCC (EN 17463)
    camp = edata.campanha().set_index("ID_Maquina")
    em = edata.energia_maquinas()
    k12 = float(em[(em["MachineId"] == "IM-002") & (em["Mes"] >= dt.date(2026, 1, 1))]["kWh_Rateado"].sum())
    LCC = [("LCC-01", "IM-002 — A) manter a injetora hidráulica de bomba fixa (2011)", 0, round(k12), 6000, 12, "Consumo = rateio de 2026 (RG-SGE-04)"),
           ("LCC-02", "IM-002 — B) retrofit com servo-bomba", 28000, round(k12 * 0.70), 4500, 12, "−30% (servo; campanha: IM-003/005/006 ≈ 41 kW vs 60,7 kW)"),
           ("LCC-03", "IM-002 — C) nova injetora totalmente elétrica", 185000, round(k12 * 0.52), 2500, 15, "−48% (IM-001 30,6 kW; menor espera)")]
    lcols = [col("ID_LCC", 8, key="PK", desc="Alternativa."), col("Alternativa", 50, desc="Alternativa avaliada."), col("Investimento_EUR", 11, "eur", desc="Investimento inicial."),
             col("kWh_Ano", 11, "kwh", desc="Consumo anual previsto."), col("Manutencao_EUR_Ano", 10, "eur", desc="Manutenção anual."), col("Vida_Anos", 7, "int", desc="Vida útil considerada."),
             col("Pressuposto", 40, desc="Base da estimativa."),
             col("Custo_Energia_Ano1", 11, "eur", f='=IF(@ID_LCC@="","",@kWh_Ano@*preco_medio)', desc="Custo da energia no 1.º ano."),
             col("VA_Energia", 11, "eur", f='=IF(@ID_LCC@="","",@Custo_Energia_Ano1@*(1-((1+escalada_energia)/(1+taxa_desconto))^@Vida_Anos@)/(taxa_desconto-escalada_energia))', desc="Valor atual da energia (com escalada)."),
             col("VA_Manutencao", 11, "eur", f='=IF(@ID_LCC@="","",@Manutencao_EUR_Ano@*(1-(1+taxa_desconto)^(-@Vida_Anos@))/taxa_desconto)', desc="Valor atual da manutenção."),
             col("LCC_EUR", 11, "eur", f='=IF(@ID_LCC@="","",@Investimento_EUR@+@VA_Energia@+@VA_Manutencao@)', desc="Custo do ciclo de vida (valor atual)."),
             col("LCC_Anual_Equivalente", 11, "eur", f='=IF(@ID_LCC@="","",@LCC_EUR@*taxa_desconto/(1-(1+taxa_desconto)^(-@Vida_Anos@)))', desc="Custo anual equivalente (compara vidas diferentes)."),
             col("Melhor_Opcao", 9, f='=IF(@ID_LCC@="","",IF(@LCC_Anual_Equivalente@=MIN(#LCC_Anual_Equivalente#),"Melhor",""))', desc="Menor custo anual equivalente.")]
    b.table("LCC", "tbl_lcc", lcols, rows_from(["ID_LCC", "Alternativa", "Investimento_EUR", "kWh_Ano", "Manutencao_EUR_Ano", "Vida_Anos", "Pressuposto"], LCC),
            "Custo do ciclo de vida de alternativas de investimento (8.3; EN 17463).", title="CUSTO DO CICLO DE VIDA — IM-002 (EN 17463)",
            subtitle="LCC = investimento + VA(energia com escalada) + VA(manutenção) · Custo anual equivalente para comparar vidas diferentes · Parâmetros em tbl_parametros",
            cf=[("Melhor_Opcao", {"Melhor": "green"})], row_height=30)

    ESPEC = [("Tipo de contrato", "Média tensão, ciclo semanal opcional, 4 períodos horários", "Em vigor (2025–2027)"),
             ("Potência contratada", "1 400 kW ultrapassada em ago/2026 (1 429 kW): aumento para 1 550 kW pedido em 10/2026, efetivo em 01/2027 + deslastre (RE-03)", "Pedido feito"),
             ("Origem", "Garantias de origem ≥ 55% (2026); 100% renovável em 2028 (GO + UPAC)", "Parcial"),
             ("Preço", "Energia indexada ao OMIE + margem fixa em 60% do volume; 40% a preço fixo", "Em vigor"),
             ("Dados", "Diagrama de carga de 15 min disponibilizado mensalmente", "Em vigor desde 11/2026"),
             ("Autoconsumo", "Sem penalização por redução de consumo com a UPAC; compra do excedente", "A negociar (2027)")]
    b.table("Compra_Energia", "tbl_compra_energia", [col("Elemento", 22, key="PK"), col("Especificacao", 70), col("Estado", 16)],
            [dict(Elemento=a, Especificacao=c_, Estado=e) for a, c_, e in ESPEC], "Especificação da compra de energia (8.3 b).", title="ESPECIFICAÇÃO DA COMPRA DE ENERGIA (8.3 b)", row_height=20)

    PRE = [dict(Ano=y, **{k: v for k, v in p_.items()}) for y, p_ in edata.PRECOS.items()]
    prcols = [col("Ano", 6, "int", key="PK", desc="Ano.")] + [col(k, 10, "num3" if "Pot" not in k else "num3", desc=f"Preço {k} ({'€/kW.dia' if 'Pot' in k else '€/kWh'}).") for k in edata.PRECOS[2025]]
    b.table("Precos", "tbl_precos", prcols, PRE, "Preços simulados (energia + redes) por período e potência.", title="PREÇOS DA ELETRICIDADE (simulados)", row_height=16)

    fat = edata.faturas()
    bm = edata.base_mensal().set_index("Mes")
    frows = []
    for r in fat.to_dict("records"):
        r["kWh_RG_SGA_13"] = int(bm.loc[r["Mes"], "kWh_Total"])
        frows.append(r)
    P_ = lambda c_: f"INDEX(tbl_precos[{c_}],MATCH(YEAR(@Mes@),tbl_precos[Ano],0))"
    fcols = [col("ID_Fatura", 10, key="PK", desc="Fatura."), col("Mes", 11, "date", desc="Mês."), col("kWh_Ponta", 10, "kwh", desc="kWh em ponta."), col("kWh_Cheia", 10, "kwh", desc="kWh em cheia."),
             col("kWh_Vazio", 10, "kwh", desc="kWh em vazio normal."), col("kWh_Super_Vazio", 10, "kwh", desc="kWh em super vazio."),
             col("kW_Potencia_Horas_Ponta", 9, "num0", desc="Potência média em horas de ponta faturada."), col("kW_Potencia_Tomada_Max", 9, "num0", desc="Máxima potência tomada (15 min)."),
             col("kW_Potencia_Contratada", 9, "num0", desc="Potência contratada."), col("kvarh_Reativa_Faturada", 9, "num0", desc="Energia reativa faturada."),
             col("kWh_RG_SGA_13", 11, "kwh", desc="kWh da base ambiental (fonte única) — verificação."),
             col("kWh_Total", 11, "kwh", f='=IF(@ID_Fatura@="","",@kWh_Ponta@+@kWh_Cheia@+@kWh_Vazio@+@kWh_Super_Vazio@)', desc="Σ períodos."),
             col("Verif_Fonte_Unica", 9, f='=IF(@ID_Fatura@="","",IF(ABS(@kWh_Total@-@kWh_RG_SGA_13@)<=5,"OK","Diferença"))', desc="Σ períodos = RG-SGA-13?"),
             col("Custo_Energia_EUR", 11, "eur", f=f'=IF(@ID_Fatura@="","",@kWh_Ponta@*{P_("Ponta")}+@kWh_Cheia@*{P_("Cheia")}+@kWh_Vazio@*{P_("Vazio")}+@kWh_Super_Vazio@*{P_("Super_Vazio")})', desc="Energia + redes."),
             col("Custo_Potencia_EUR", 10, "eur", f=f'=IF(@ID_Fatura@="","",(@kW_Potencia_Horas_Ponta@*{P_("Pot_Ponta")}+@kW_Potencia_Contratada@*{P_("Pot_Contratada")})*DAY(EOMONTH(@Mes@,0)))', desc="Potência."),
             col("Custo_Reativa_EUR", 9, "eur", f='=IF(@ID_Fatura@="","",@kvarh_Reativa_Faturada@*preco_reativa)', desc="Energia reativa."),
             col("Custo_Total_EUR", 11, "eur", f='=IF(@ID_Fatura@="","",@Custo_Energia_EUR@+@Custo_Potencia_EUR@+@Custo_Reativa_EUR@)', desc="Total sem IVA."),
             col("EUR_por_kWh", 8, "num3", f='=IF(@ID_Fatura@="","",@Custo_Total_EUR@/@kWh_Total@)', desc="Preço médio total."),
             col("Pct_Ponta", 8, "pct1", f='=IF(@ID_Fatura@="","",@kWh_Ponta@/@kWh_Total@)', desc="Quota de ponta."),
             col("Utilizacao_Potencia", 8, "pct", f='=IF(@ID_Fatura@="","",@kW_Potencia_Tomada_Max@/@kW_Potencia_Contratada@)', desc="Tomada ÷ contratada."),
             col("Alerta_Potencia", 10, f='=IF(@ID_Fatura@="","",IF(@Utilizacao_Potencia@>0.95,"Crítico",IF(@Utilizacao_Potencia@>0.9,"Atenção","OK")))', desc="> 95% crítico (RE-03).")]
    b.table("Faturas", "tbl_faturas", fcols, frows, "Faturas mensais de eletricidade (simuladas) — custos, preço médio e potência.",
            title="FATURAS DE ELETRICIDADE — PERÍODOS, CUSTOS E POTÊNCIA (simuladas)", subtitle="kWh totais = RG-SGA-13 (fonte única; coluna de verificação) · Repartição horária, potência e reativa simuladas",
            cf=[("Alerta_Potencia", {"Crítico": "red", "Atenção": "orange", "OK": "green"}), ("Verif_Fonte_Unica", {"Diferença": "red"})], row_height=16, freeze_col=2)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
