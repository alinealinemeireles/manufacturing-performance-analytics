"""RG-SGA-17 — Análise de Dupla Materialidade (DMA) da Plasticom.

Modelo de dados (tabelas Excel, uma linha = um registo):
  tbl_dma_temas       temas de sustentabilidade (matérias ESRS / específicas) com a materialidade agregada (calculada)
  tbl_dma_iro         impactos, riscos e oportunidades (IRO) — unidade de avaliação, com pontuação de impacto ou financeira
  tbl_dma_evidencias  evidências quantitativas/qualitativas por IRO (instantâneo dos registos do SGA)
  tbl_dma_consultas   contributos das partes interessadas por tema (formato longo)
  tbl_dma_escalas / tbl_dma_parametros  critérios, escalas e limiares (folha Listas) lidos pelas fórmulas
O Painel tem filtros (listas pendentes), matriz, ranking, gráfico de dispersão dinâmico e, após o pós-processamento
no Excel (postprocess), uma tabela dinâmica com segmentações de dados.
Metodologia inspirada na EFRAG IG 1 (materialidade) e IG 2 (cadeia de valor); escalas e limiares são escolhas internas
documentadas, não valores impostos pelos ESRS.
"""
import datetime as dt
import os
from openpyxl.chart import ScatterChart, Reference, Series
from sgalib import *
from dims import *
import build_20_reciclabilidade as R20
import build_19_esg_ambiental as _G19
import build_21_quimicos as _Q21
G19 = _G19.totais_gee()   # fonte unica dos GEE (RG-SGA-19)
Q21 = _Q21.resumo()        # fonte unica dos COV (RG-SGA-21)
_RZ = R20.resumo()

D_AVAL = dt.date(2026, 9, 24)
FILE = "SGA-17_Dupla_Materialidade.xlsx"
CORP = "SGA-02_Gestao_Riscos_Oportunidades.xlsx (registo corporativo)"

PILARES = ["Ambiental", "Social", "Governança"]
ESRS = ["E1 Alterações climáticas", "E2 Poluição", "E3 Água e recursos marinhos", "E4 Biodiversidade e ecossistemas",
        "E5 Uso de recursos e economia circular", "S1 Trabalhadores próprios", "S2 Trabalhadores da cadeia de valor",
        "S3 Comunidades afetadas", "S4 Consumidores e utilizadores finais", "G1 Conduta empresarial", "Específico da entidade"]
TIPOS = ["Impacto negativo", "Impacto positivo", "Risco", "Oportunidade"]
UP, OP, DD, DU, DF = ("Upstream — fornecedores", "Operações próprias", "Downstream — distribuição",
                      "Downstream — utilização", "Downstream — fim de vida")
ETAPAS = [UP, OP, DD, DU, DF]
HC, HM, HL = "Curto prazo (≤ 1 ano)", "Médio prazo (1–5 anos)", "Longo prazo (> 5 anos)"
HORIZ = [HC, HM, HL]
RUBRICAS = ["Receitas", "Custos de energia e matérias-primas", "Outros custos operacionais", "CAPEX / ativos",
            "Multas, passivos e litígios", "Financiamento e seguros"]
PARTES = ["Colaboradores", "Clientes", "Fornecedores", "Autoridades (APA / CCDR / ACT)", "Comunidade / vizinhança",
          "Acionistas / Direção", "Operadores de gestão de resíduos", "Seguradoras / bancos"]
F_GER, F_IND, F_SGA, F_PRO, F_MAN, F_QUA, F_LOG, F_CMP, F_RD, F_RH, F_FIN = FUNC_NAMES[:11]

# ------------------------------------------------------------------------------------------- temas
# (ID, Pilar, Tópico ESRS, Subtópico, Tema, Descrição, GRI, Relevância setorial, Fonte da identificação, Dono, Justificação)
TEMAS_DMA = [
    ("DM-01", "Ambiental", ESRS[0], "Mitigação das alterações climáticas", "Emissões de GEE (âmbitos 1, 2 e 3)",
     "Emissões diretas e indiretas de gases com efeito de estufa na operação e na cadeia de valor (polímeros, transporte).",
     "GRI 305", "Alta", "RG-SGA-03 (AA-002, AA-007, AA-010, AA-040); PES-01; tbl_emas EMAS-06", F_SGA,
     "Processo 100% elétrico (≈ 7,8 GWh/ano) e 712 t/ano de polímero virgem: as emissões do âmbito 3 a montante superam as do âmbito 2; clientes europeus começam a pedir pegada de carbono."),
    ("DM-02", "Ambiental", ESRS[0], "Energia", "Consumo e eficiência energética",
     "Consumo de eletricidade da injeção, sopro, compressores e utilidades; quota renovável e autoconsumo.",
     "GRI 302", "Alta", "RG-SGA-03 (AA-007, AA-010, AA-021, AA-030); PES-02; SWT-F02; SWT-W01", F_IND,
     "A eletricidade é o 2.º maior custo variável; sem submedição por processo, a eficiência não é demonstrável."),
    ("DM-03", "Ambiental", ESRS[0], "Adaptação às alterações climáticas", "Resiliência a ondas de calor, seca e incêndio",
     "Riscos físicos agudos e crónicos sobre a operação: carga térmica, água de arrefecimento, incêndio rural.",
     "GRI 201-2", "Média", "PES-08; PES-09; PES-10; SWT-T01; RO-04; RO-08", F_IND,
     "Verões de 2025 e 2026 com anomalia de +1,6 a +2,2 °C; proximidade ao Pinhal de Leiria."),
    ("DM-04", "Ambiental", ESRS[1], "Poluição do ar", "Emissões de COV da serigrafia",
     "Emissão difusa de compostos orgânicos voláteis na limpeza de ecrãs e na impressão serigráfica.",
     "GRI 305-7", "Média", "RG-SGA-03 (AA-014 — AAS, AA-006); LEG-04; OBJ-03", F_SGA,
     f"Único aspeto ambiental significativo de processo (IRA 40); {Q21['cov_t']:.2f} t de COV/ano (balanço do RG-SGA-21).".replace(".", ",", 1)),
    ("DM-05", "Ambiental", ESRS[1], "Poluição da água e do solo", "Derrames e descargas",
     "Derrames de tintas, solventes e óleos; purga da torre de arrefecimento; águas de combate a incêndio.",
     "GRI 303-4; GRI 306-3", "Média", "RG-SGA-03 (AA-005, AA-009, AA-013, AA-024); RO-10; NC-SGA-26-03", F_SGA,
     "NC do kit antipoluição em 2026 mostra fragilidade de controlo, mas os volumes em causa são pequenos e contidos."),
    ("DM-06", "Ambiental", ESRS[1], "Microplásticos", "Perdas de granulado de plástico",
     "Perdas de pellets na descarga de silos e big bags que podem chegar à rede pluvial e ao meio aquático.",
     "GRI 306", "Alta", "RG-SGA-03 (AA-003); PES-11; PES-13; RO-07; OBJ-06", F_SGA,
     "Impacto persistente e novo regulamento europeu de perdas de granulado; só 43% dos pontos críticos têm contenção."),
    ("DM-07", "Ambiental", ESRS[1], "Substâncias que suscitam preocupação", "Substâncias perigosas em tintas e aditivos",
     "Uso de tintas, solventes e aditivos classificados (CLP) e restrições a substâncias em embalagens (PPWR, REACH).",
     "GRI 416", "Média", "RG-SGA-03 (AA-015); LEG-06; LEG-09; PES-12", F_RD,
     "Quantidades baixas (≈ 1,1 t de tinta/ano) e FDS disponíveis; vigiar restrições PFAS em contacto alimentar."),
    ("DM-08", "Ambiental", ESRS[2], "Água", "Consumo de água",
     "Água de rede para reposição da torre de arrefecimento e uso sanitário, numa região com seca sazonal.",
     "GRI 303", "Média", "RG-SGA-03 (AA-023, AA-035); PES-09; OBJ-05; tbl_emas EMAS-03", F_MAN,
     "9.384 m³/ano, dos quais 81% na torre; consumo cresce com a temperatura."),
    ("DM-09", "Ambiental", ESRS[3], "Biodiversidade e ecossistemas", "Ocupação do solo e plástico no meio natural",
     "Impermeabilização do terreno e escape de embalagens para o meio natural e marinho no fim de vida.",
     "GRI 304", "Média", "RG-SGA-03 (AA-033, AA-043); PES-10; tbl_emas EMAS-05", F_SGA,
     "O impacto relevante está a jusante (lixo plástico), não no local."),
    ("DM-10", "Ambiental", ESRS[4], "Entradas de recursos", "Polímeros virgens e conteúdo reciclado",
     "Dependência de polímeros de origem fóssil; acesso a PCR/rPET de qualidade; reintegração de scrap.",
     "GRI 301", "Alta", "RG-SGA-03 (AA-001, AA-020); SWT-W02; SWT-T02; PES-03; RO-05; RO-11", F_CMP,
     "88% do polímero é virgem; metas de conteúdo reciclado do PPWR para 2030."),
    ("DM-11", "Ambiental", ESRS[4], "Saídas de recursos — produtos e embalagens", "Reciclabilidade e conformidade PPWR das embalagens",
     "Design for recycling, reciclabilidade, documentação técnica e declaração UE de conformidade das embalagens.",
     "GRI 301-3", "Alta", "RG-SGA-03 (AA-037, AA-038 — AAS, AA-043); PES-04; PES-07; PES-12; SWT-O01; RO-03; RO-06", F_RD,
     "Aspeto de maior IRA do SGA (60); só 41% das famílias com documentação PPWR."),
    ("DM-12", "Ambiental", ESRS[4], "Resíduos", "Resíduos da produção",
     "Scrap, embalagens de matérias-primas, resíduos perigosos (tintas, óleos) e indiferenciados.",
     "GRI 306", "Média", "RG-SGA-03 (AA-004, AA-008, AA-011, AA-016, AA-026, AA-028, AA-029); PES-14", F_SGA,
     "130,6 t/ano com valorização elevada; 2,1 t de perigosos."),
    ("DM-13", "Social", ESRS[5], "Saúde e segurança", "Saúde e segurança no trabalho",
     "Riscos mecânicos na troca de molde e setup; exposição a solventes; ruído; turnos.",
     "GRI 403", "Alta", "Registo corporativo R28, R29; tbPartesInteressadas (Colaboradores)", F_RH,
     "Riscos de lesão grave e irreversível: a gravidade prevalece sobre a probabilidade (direitos humanos)."),
    ("DM-14", "Social", ESRS[5], "Condições de trabalho", "Condições de trabalho e disponibilidade de pessoas",
     "Trabalho por turnos, fadiga, retenção e indisponibilidade de operadores.",
     "GRI 401", "Média", "Registo corporativo R9, R23; tbl_producao_mensal (paragens)", F_RH,
     "Indisponibilidade de operadores é a 1.ª causa de paragem não planeada."),
    ("DM-15", "Social", ESRS[5], "Formação e desenvolvimento de competências", "Formação e competências",
     "Competências técnicas, ambientais e de qualidade dos trabalhadores próprios.",
     "GRI 404", "Média", "RG-SGA-08 (matriz de competências, registo de formação)", F_RH,
     "Matriz de competências em vigor; polivalência ainda limitada."),
    ("DM-16", "Social", ESRS[5], "Igualdade de tratamento e oportunidades", "Igualdade e não discriminação",
     "Igualdade salarial, representação em chefias, inclusão.",
     "GRI 405", "Baixa", "Checklist ESRS S1 (sem dados internos)", F_RH,
     "Lacuna de dados: sem indicadores de disparidade salarial nem de representação."),
    ("DM-17", "Social", ESRS[6], "Condições de trabalho na cadeia de valor", "Trabalhadores da cadeia de valor",
     "Condições de trabalho na recolha e triagem de resíduos plásticos (PCR) e na logística subcontratada.",
     "GRI 414", "Média", "RG-SGA-11 (fornecedores); SWT-T02", F_CMP,
     "Sem diligência devida sobre a origem do PCR: impacto potencial com dados insuficientes."),
    ("DM-18", "Social", ESRS[7], "Comunidades locais", "Relação com a comunidade local",
     "Ruído, tráfego, risco de incêndio e emprego local na Marinha Grande.",
     "GRI 413", "Média", "RG-SGA-03 (AA-022 — AAS, AA-034); PES-05; RO-12; RO-08", F_SGA,
     "Habitações a ~250 m; compressores novos sem avaliação acústica; ≈ 150 postos de trabalho locais."),
    ("DM-19", "Social", ESRS[8], "Saúde e segurança dos consumidores", "Segurança do produto (contacto alimentar, farmacêutico e cosmético)",
     "Migração de substâncias, contaminação e conformidade de materiais em contacto com alimentos e medicamentos.",
     "GRI 416", "Alta", "Registo corporativo R11, R16; expansão das linhas alimentar e farmacêutica", F_QUA,
     "Consumidores finais expostos; a expansão para alimentar e farmacêutico aumenta a exigência."),
    ("DM-20", "Social", ESRS[8], "Informação aos consumidores", "Alegações ambientais e informação ao cliente",
     "Veracidade de alegações de reciclabilidade e conteúdo reciclado (Diretiva (UE) 2024/825).",
     "GRI 417", "Média", "PES-15; RO-05; registo corporativo R36", F_RD,
     "Alegações de PCR sem certificação de fornecedores spot."),
    ("DM-21", "Governança", ESRS[9], "Cultura empresarial e conformidade", "Conformidade legal e conduta ética",
     "Cumprimento das obrigações de conformidade ambiental e de SST, anticorrupção e cultura de integridade.",
     "GRI 2-27; GRI 205", "Média", "RG-SGA-04 (14 diplomas); registo corporativo R31, R32", F_GER,
     "Título de recursos hídricos por confirmar e fiscalização de resíduos reforçada."),
    ("DM-22", "Governança", ESRS[9], "Gestão das relações com fornecedores", "Gestão e avaliação de fornecedores",
     "Qualificação, avaliação ESG, dependência de fornecedores spot e práticas de pagamento.",
     "GRI 308; GRI 414", "Média", "RG-SGA-11; SWT-W02; RO-05; registo corporativo R13", F_CMP,
     "Lotes fora de especificação do SUP-005 e compras spot sem avaliação ambiental."),
    ("DM-23", "Governança", ESRS[10], "Qualidade e fiabilidade do produto", "Qualidade do produto e custo da não-qualidade",
     "Rejeição, refação de lotes, reclamações e capacidade de processo.",
     "—", "Alta", "Registo corporativo R16, R17, R24; raio-X analítico (datasets/silver)", F_QUA,
     "Taxa de rejeição 2,39% contra meta de 2,0%; 0% dos grupos com Cpk ≥ 1,33."),
    ("DM-24", "Governança", ESRS[10], "Dados, digitalização e cibersegurança", "Dados industriais e cibersegurança",
     "Disponibilidade e integridade do warehouse de dados, sistemas OT e uso de dados para decisões ESG.",
     "GRI 418", "Média", "SWT-F01; RO-01; registo corporativo R26, O3", F_GER,
     "Força de dados industriais; dependência crescente do pipeline de dados."),
]

# ------------------------------------------------------------------------------------------- IRO
IRO_ROWS = []


def imp(key, tema, tipo, nat, etapa, hz, mag, alc, irr=None, prob=None, dh="Não", **kw):
    IRO_ROWS.append(dict(key=key, ID_Tema=tema, Tipo_IRO=tipo, Natureza=nat, Etapa_Cadeia_Valor=etapa, Horizonte=hz,
                         Direitos_Humanos=dh, Magnitude=mag, Alcance=alc, Irremediabilidade=irr, Probabilidade=prob, **kw))


def fin(key, tema, tipo, etapa, hz, eur, pf, rub, **kw):
    IRO_ROWS.append(dict(key=key, ID_Tema=tema, Tipo_IRO=tipo, Etapa_Cadeia_Valor=etapa, Horizonte=hz,
                         Efeito_Financeiro_EUR_Ano=eur, Probabilidade_Financeira=pf, Rubrica_Financeira=rub, **kw))


# DM-01 GEE
imp("GEE2", "DM-01", "Impacto negativo", "Real", OP, HC, 3, 4, 4,
    Descricao="Emissões de GEE do âmbito 2 (≈ 860 tCO2e em 2026, location-based) associadas ao consumo de 7,8 GWh de eletricidade e fugas de R410A.",
    Afetados="Clima global; sociedade", Evidencia_Resumo=f"EMAS-06 ({G19['S1'] + G19['S2LB']:.0f} tCO2e, âmbitos 1 + 2 LB); fator 0,110 kgCO2e/kWh; fuga de 3,2 kg de R410A", Qualidade_Evidencia="Alta",
    IDs_Contexto="PES-01", IDs_Aspetos="AA-007; AA-010; AA-021; AA-025", ID_Legal="LEG-08; LEG-07", ID_OBJ="OBJ-01", ID_KPI="KPI-08", ID_PAM="PAM-26-01",
    Resposta_Gestao="Eficiência energética (OBJ-01), garantias de origem renováveis e autoconsumo fotovoltaico.", Responsavel=F_SGA)
imp("GEE3a", "DM-01", "Impacto negativo", "Real", UP, HC, 4, 4, 4,
    Descricao="Emissões do âmbito 3 a montante na produção de ≈ 712 t/ano de polímeros virgens (≈ 1.350 tCO2e/ano, estimativa por fator médio 1,9 kgCO2e/kg).",
    Afetados="Clima global", Evidencia_Resumo="AA-001 (712,4 t/ano); fator médio de literatura — estimativa não verificada", Qualidade_Evidencia="Baixa",
    IDs_Contexto="PES-01; SWT-T02", IDs_Aspetos="AA-001", Resposta_Gestao="Inventário do âmbito 3 (categoria 1) com fatores de fornecedores; aumentar PCR e lightweighting.",
    Responsavel=F_SGA, Notas="Principal fonte de emissões da cadeia de valor; exige dados primários de fornecedores.")
imp("GEE3d", "DM-01", "Impacto negativo", "Real", DD, HC, 2, 2, 3,
    Descricao="Emissões do transporte rodoviário de matérias-primas e de produto acabado a clientes.",
    Afetados="Clima global; qualidade do ar local", Evidencia_Resumo="AA-002, AA-040 (sem quantificação de t.km)", Qualidade_Evidencia="Baixa",
    IDs_Aspetos="AA-002; AA-040", Resposta_Gestao="Recolher t.km por cliente/fornecedor e otimizar cargas.", Responsavel=F_LOG)
fin("GEEcli", "DM-01", "Risco", DD, HM, 150000, 3, RUBRICAS[0],
    Descricao="Perda ou redução de contratos com marcas europeias que exigem pegada de carbono do produto e metas de redução aos fornecedores.",
    Mecanismo_Financeiro="Receitas: ≈ 4% da faturação (3,68 M€) em clientes com requisitos climáticos em 2027; pressuposto interno.",
    Evidencia_Resumo="PES-04 (clientes pedem dados ambientais); questionários ESG recebidos", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-04; PES-01", ID_Registo_Corporativo="O3", Resposta_Gestao="Cálculo de pegada por família de produto e resposta estruturada a questionários ESG.", Responsavel=F_GER)
# DM-02 Energia
imp("ENimp", "DM-02", "Impacto negativo", "Real", OP, HC, 3, 3, 3,
    Descricao="Consumo de 7.174 MWh/ano de eletricidade, 45% de origem não renovável, com intensidade de 110 kWh por 1.000 unidades.",
    Afetados="Recursos energéticos; clima", Evidencia_Resumo="EMAS-01 (7.173,6 MWh); EMAS-01b (3.945,5 MWh renováveis); KPI-01", Qualidade_Evidencia="Alta",
    IDs_Contexto="SWT-F02; SWT-W01", IDs_Aspetos="AA-007; AA-010; AA-019; AA-021; AA-030", ID_Legal="LEG-08", ID_OBJ="OBJ-01", ID_KPI="KPI-01; KPI-09", ID_PAM="PAM-26-01; PAM-26-02",
    ID_RO="RO-02", ID_Registo_Corporativo="R35", Resposta_Gestao="Submedição por processo (PAM-26-02) e plano de eficiência (OBJ-01).", Responsavel=F_IND)
fin("ENpreco", "DM-02", "Risco", OP, HC, 215000, 4, RUBRICAS[1],
    Descricao="Volatilidade do preço da eletricidade num processo eletrointensivo (≈ 7,8 GWh/ano).",
    Mecanismo_Financeiro="Custos: +0,03 €/kWh × 7,17 GWh ≈ 215 k€/ano de custo adicional, sem repercussão imediata no preço de venda.",
    Evidencia_Resumo="EMAS-01; PES-02; faturas de eletricidade", Qualidade_Evidencia="Alta", IDs_Contexto="PES-02",
    ID_Registo_Corporativo="R25", ID_KPI="KPI-01", Resposta_Gestao="Contrato com preço indexado limitado, eficiência e autoconsumo.", Responsavel=F_FIN)
fin("ENupac", "DM-02", "Oportunidade", OP, HM, 180000, 3, RUBRICAS[1],
    Descricao="Autoconsumo fotovoltaico (UPAC ≈ 1 MWp, ≈ 1.400 MWh/ano) na cobertura de ≈ 9.000 m².",
    Mecanismo_Financeiro="Custos evitados: 1.400 MWh × 0,13 €/kWh ≈ 182 k€/ano; investimento a financiar com apoio público (SWT-O03).",
    Evidencia_Resumo="AA-032 (1.400 MWh/ano, estimativa); estudo de viabilidade em curso", Qualidade_Evidencia="Média",
    IDs_Contexto="SWT-O02; SWT-O03", IDs_Aspetos="AA-031; AA-032", ID_RO="RO-09", ID_Registo_Corporativo="O15",
    Resposta_Gestao="Estudo de viabilidade e candidatura a financiamento (RO-09).", Responsavel=F_FIN)
fin("ENefic", "DM-02", "Oportunidade", OP, HC, 75000, 4, RUBRICAS[1],
    Descricao="Redução de 8% do consumo específico (OBJ-01) e das fugas de ar comprimido com submedição por processo.",
    Mecanismo_Financeiro="Custos evitados: 8% × 7,17 GWh ≈ 574 MWh × 0,13 €/kWh ≈ 75 k€/ano.",
    Evidencia_Resumo="KPI-01 (baseline 109,9 kWh/1.000 un); AA-021 (975 MWh/ano em compressores)", Qualidade_Evidencia="Alta",
    IDs_Aspetos="AA-021", ID_OBJ="OBJ-01", ID_KPI="KPI-01", ID_PAM="PAM-26-01; PAM-26-02", ID_RO="RO-02", ID_Registo_Corporativo="O6",
    Resposta_Gestao="Plano de eficiência energética e deteção de fugas.", Responsavel=F_MAN)
# DM-03 Adaptação
fin("ADcalor", "DM-03", "Risco", OP, HM, 60000, 4, RUBRICAS[2],
    Descricao="Ondas de calor e seca aumentam o consumo de água e energia do arrefecimento, os defeitos e o risco de restrição de água.",
    Mecanismo_Financeiro="Custos: +5% de energia de arrefecimento por °C acima de 15 °C, refugo e horas de paragem no verão ≈ 60 k€/ano.",
    Evidencia_Resumo="Anomalia térmica de +2,2 °C em ago/2026; KPI-16; AA-023", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-08; PES-09; SWT-T01", IDs_Aspetos="AA-023", ID_OBJ="OBJ-05", ID_KPI="KPI-02; KPI-16", ID_RO="RO-04", ID_Registo_Corporativo="R34",
    Resposta_Gestao="Avaliação de cenários climáticos e circuito fechado de arrefecimento (OBJ-05).", Responsavel=F_IND)
fin("ADfogo", "DM-03", "Risco", OP, HL, 400000, 1, RUBRICAS[3],
    Descricao="Incêndio rural na envolvente florestal que atinge o armazém de matérias-primas.",
    Mecanismo_Financeiro="Ativos e paragem: dano estimado ≈ 400 k€; parcialmente transferido para o seguro multirriscos.",
    Evidencia_Resumo="PES-10; plano de emergência (RG-SGA-12)", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-10", IDs_Aspetos="AA-034", ID_Legal="LEG-11", ID_RO="RO-08", ID_Registo_Corporativo="R38",
    Resposta_Gestao="Faixa de gestão de combustível, seguro e simulacro anual.", Responsavel=F_IND)
# DM-04 Ar
imp("COV", "DM-04", "Impacto negativo", "Real", OP, HC, 3, 3, 2,
    Descricao=f"Emissão difusa de ≈ {Q21['cov_t']:.2f} t/ano de COV na serigrafia e manutenção (precursores de ozono troposférico).".replace(".", ",", 1),
    Afetados="Trabalhadores da serigrafia; qualidade do ar local", Evidencia_Resumo=f"EMAS-06b ({Q21['cov_t']:.2f} t COV); AA-014 ({Q21['solvente_kg']} kg de solvente/ano); KPI-06".replace(".", ",", 1), Qualidade_Evidencia="Alta",
    IDs_Aspetos="AA-014; AA-006", ID_Legal="LEG-04; LEG-12", ID_OBJ="OBJ-03", ID_KPI="KPI-06", ID_PAM="PAM-26-07",
    Resposta_Gestao="Reduzir 20% do solvente por peça (OBJ-03); recipientes fechados; avaliar tintas UV sem solvente.", Responsavel=F_PRO)
fin("COVleg", "DM-04", "Risco", OP, HC, 15000, 2, RUBRICAS[4],
    Descricao="Incumprimento do regime de COV (limiar de consumo de solventes e plano de gestão de solventes).",
    Mecanismo_Financeiro="Multas e custos de adaptação: coima e medições adicionais ≈ 15 k€.",
    Evidencia_Resumo="LEG-04 (avaliação de conformidade)", Qualidade_Evidencia="Média", ID_Legal="LEG-04", Responsavel=F_SGA)
# DM-05 Água e solo
imp("DERR", "DM-05", "Impacto negativo", "Potencial", OP, HC, 4, 2, 3, 3,
    Descricao="Derrame de tintas, solventes ou óleos não contido que contamina o solo ou a rede pluvial.",
    Afetados="Solo; águas superficiais", Evidencia_Resumo="NC-SGA-26-03 (kit antipoluição incompleto); AA-005, AA-013", Qualidade_Evidencia="Média",
    IDs_Contexto="SWT-W04", IDs_Aspetos="AA-005; AA-009; AA-013; AA-016; AA-017", ID_Legal="LEG-06", ID_PAM="PAM-26-04; PAM-26-05",
    ID_RO="RO-10", ID_Registo_Corporativo="R30", Resposta_Gestao="Bacias de retenção, kits selados e verificação semanal.", Responsavel=F_SGA)
imp("PURGA", "DM-05", "Impacto negativo", "Real", OP, HC, 2, 2, 2,
    Descricao="Descarga da purga da torre de arrefecimento com biocida e anti-incrustante no coletor.",
    Afetados="Meio recetor", Evidencia_Resumo="AA-024; LEG-03", Qualidade_Evidencia="Média", IDs_Aspetos="AA-024", ID_Legal="LEG-03",
    Resposta_Gestao="Controlo analítico da purga e dosagem otimizada.", Responsavel=F_MAN)
fin("RESPAMB", "DM-05", "Risco", OP, HM, 250000, 1, RUBRICAS[4],
    Descricao="Responsabilidade ambiental e custos de remediação após contaminação do solo.",
    Mecanismo_Financeiro="Passivos: remediação e garantia financeira ≈ 250 k€ num evento grave.",
    Evidencia_Resumo="LEG-14", Qualidade_Evidencia="Baixa", ID_Legal="LEG-14", Responsavel=F_FIN)
# DM-06 Microplásticos
imp("PELLET", "DM-06", "Impacto negativo", "Real", OP, HC, 3, 3, 5,
    Descricao="Perda de granulado de plástico na descarga de silos e big bags para o pavimento e a rede pluvial (persistente no meio aquático).",
    Afetados="Ecossistemas aquáticos; comunidade", Evidencia_Resumo="AA-003 (≈ 100 kg/ano recolhidos; perdas totais não medidas); KPI-13 (43% dos pontos com contenção)", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-11; SWT-W04", IDs_Aspetos="AA-003", ID_Legal="LEG-10", ID_OBJ="OBJ-06", ID_KPI="KPI-13", ID_PAM="PAM-26-11",
    ID_RO="RO-07", ID_Registo_Corporativo="R37", Resposta_Gestao="Operation Clean Sweep: filtros nas sarjetas, bacias e inspeção semanal.", Responsavel=F_SGA)
fin("PELLETleg", "DM-06", "Risco", OP, HM, 30000, 4, RUBRICAS[2],
    Descricao="Obrigações do regulamento europeu de prevenção de perdas de granulados (avaliação de risco, plano, registos).",
    Mecanismo_Financeiro="Custos de conformidade: equipamento de contenção, formação e registos ≈ 30 k€.",
    Evidencia_Resumo="PES-13; LEG-10", Qualidade_Evidencia="Média", IDs_Contexto="PES-13", ID_Legal="LEG-10", ID_OBJ="OBJ-06", ID_PAM="PAM-26-11",
    Resposta_Gestao="Plano de prevenção de perdas integrado no OBJ-06.", Responsavel=F_SGA)
# DM-07 Substâncias
imp("SUBST", "DM-07", "Impacto negativo", "Potencial", OP, HM, 3, 2, 3, 3,
    Descricao="Uso de tintas, solventes e aditivos classificados (CLP) que podem chegar ao ambiente por derrame ou resíduo.",
    Afetados="Ambiente; trabalhadores", Evidencia_Resumo="AA-015 (1.082 kg de tinta/ano); FDS", Qualidade_Evidencia="Média",
    IDs_Aspetos="AA-015", ID_Legal="LEG-06", Resposta_Gestao="Inventário de substâncias e substituição progressiva.", Responsavel=F_RD)
fin("SUBSTleg", "DM-07", "Risco", DU, HM, 40000, 3, RUBRICAS[2],
    Descricao="Restrições a substâncias em embalagens (PFAS em contacto alimentar — PPWR; REACH) obrigam a reformular tintas e aditivos.",
    Mecanismo_Financeiro="Custos: requalificação de materiais e ensaios ≈ 40 k€.", Evidencia_Resumo="PES-12; LEG-09", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-12", ID_Legal="LEG-06; LEG-09", Responsavel=F_RD)
# DM-08 Água
imp("AGUA", "DM-08", "Impacto negativo", "Real", OP, HC, 2, 3, 2,
    Descricao="Consumo de 9.384 m³/ano de água de rede (81% na torre de arrefecimento) numa região com seca sazonal.",
    Afetados="Recursos hídricos locais", Evidencia_Resumo="EMAS-03 (9.384 m³); AA-023 (7.561 m³); KPI-02", Qualidade_Evidencia="Alta",
    IDs_Contexto="PES-09", IDs_Aspetos="AA-023; AA-035", ID_OBJ="OBJ-05", ID_KPI="KPI-02", ID_PAM="PAM-26-14",
    Resposta_Gestao="Reduzir 10% do consumo específico (OBJ-05) com circuito fechado.", Responsavel=F_MAN)
fin("AGUAfin", "DM-08", "Risco", OP, HM, 20000, 3, RUBRICAS[2],
    Descricao="Restrições de uso de água em seca e aumento de tarifas.",
    Mecanismo_Financeiro="Custos: tarifa e cisterna em episódios de restrição ≈ 20 k€/ano.", Evidencia_Resumo="PES-09", Qualidade_Evidencia="Baixa",
    IDs_Contexto="PES-09", ID_OBJ="OBJ-05", Responsavel=F_MAN)
# DM-09 Biodiversidade
imp("SOLO", "DM-09", "Impacto negativo", "Real", OP, HL, 2, 1, 3,
    Descricao="Impermeabilização de 32.000 m² de 45.000 m² de terreno; 3.500 m² de área orientada para a natureza.",
    Afetados="Habitat local", Evidencia_Resumo="EMAS-05 / 05b / 05c", Qualidade_Evidencia="Alta", IDs_Aspetos="AA-033",
    Resposta_Gestao="Manter área verde e avaliar soluções de drenagem sustentável.", Responsavel=F_SGA)
imp("LIXO", "DM-09", "Impacto negativo", "Potencial", DF, HL, 4, 5, 5, 3,
    Descricao="Embalagens que escapam aos sistemas de recolha e chegam ao meio natural e marinho (lixo plástico).",
    Afetados="Ecossistemas terrestres e marinhos", Evidencia_Resumo="AA-043; estatísticas setoriais de fuga de embalagens", Qualidade_Evidencia="Baixa",
    IDs_Aspetos="AA-043", ID_Legal="LEG-09", Resposta_Gestao="Design for recycling e embalagens monomaterial (DM-11).", Responsavel=F_RD)
# DM-10 Entradas de recursos
imp("VIRGEM", "DM-10", "Impacto negativo", "Real", UP, HC, 3, 4, 4,
    Descricao="Consumo de ≈ 712 t/ano de polímeros virgens de origem fóssil (88% do polímero).",
    Afetados="Recursos naturais não renováveis", Evidencia_Resumo="AA-001 (712,4 t); PCR_SHARE = 12%; EMAS-02 (825,5 t de materiais)", Qualidade_Evidencia="Alta",
    IDs_Contexto="SWT-F04", IDs_Aspetos="AA-001", Resposta_Gestao="Aumentar conteúdo reciclado e reduzir peso.", Responsavel=F_CMP)
fin("PCRfin", "DM-10", "Risco", UP, HM, 90000, 4, RUBRICAS[1],
    Descricao="Preço, disponibilidade e qualidade do PCR/rPET e metas de conteúdo reciclado do PPWR para 2030.",
    Mecanismo_Financeiro="Custos: prémio do reciclado (+0,25 €/kg) sobre ≈ 360 t/ano adicionais de PCR em 2030 ≈ 90 k€/ano.",
    Evidencia_Resumo="PES-03; SWT-T02; lotes fora de especificação do SUP-005", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-03; SWT-W02; SWT-T02", ID_RO="RO-05", ID_Registo_Corporativo="R36", ID_PAM="PAM-26-16",
    Resposta_Gestao="Contratos de fornecimento de PCR certificado e avaliação ambiental de fornecedores.", Responsavel=F_CMP)
fin("REGRIND", "DM-10", "Oportunidade", OP, HC, 12000, 4, RUBRICAS[1],
    Descricao="Aumentar a reintegração de scrap limpo segregado por polímero e cor (regrind).",
    Mecanismo_Financeiro="Custos evitados: +9 t/ano de resina × 1,35 €/kg ≈ 12 k€/ano.",
    Evidencia_Resumo="AA-020 (11,6 t/ano reintegradas); AA-011 (31,2 t de scrap)", Qualidade_Evidencia="Alta",
    IDs_Contexto="SWT-F03", IDs_Aspetos="AA-020", ID_OBJ="OBJ-02", ID_KPI="KPI-04", ID_PAM="PAM-26-12", ID_RO="RO-11", ID_Registo_Corporativo="O10",
    Resposta_Gestao="Segregação na fonte e integração no OBJ-02.", Responsavel=F_PRO)
# DM-11 Produtos e embalagens
imp("FIMVIDA", "DM-11", "Impacto negativo", "Real", DF, HM, 3, 4, 3,
    Descricao="Embalagens pós-consumo não recicladas (aterro ou incineração), agravado por decoração e combinações multimaterial.",
    Afetados="Recursos; sistemas de gestão de resíduos", Evidencia_Resumo="AA-043; AA-037; famílias sem avaliação de reciclabilidade", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-07", IDs_Aspetos="AA-043; AA-037", ID_Legal="LEG-09", ID_RO="RO-03", ID_Registo_Corporativo="O5",
    Resposta_Gestao="Avaliação de reciclabilidade por família e redesenho.", Responsavel=F_RD)
imp("D4R", "DM-11", "Impacto positivo", "Potencial", DF, HM, 3, 3, prob=3,
    Descricao="Design for recycling, lightweighting e embalagens monomaterial reduzem resíduos e aumentam a reciclagem.",
    Afetados="Recursos; consumidores", Evidencia_Resumo="PES-07; piloto de embalagens retornáveis (AA-041)", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-07", IDs_Aspetos="AA-037; AA-041", Resposta_Gestao="Programa Design for Recycling.", Responsavel=F_RD)
fin("PPWR", "DM-11", "Risco", DU, HC, 350000, 4, RUBRICAS[0],
    Descricao="Incumprimento do PPWR (documentação técnica, declaração UE de conformidade, reciclabilidade) impede colocar embalagens no mercado UE.",
    Mecanismo_Financeiro="Receitas: ≈ 10% da faturação em famílias sem documentação em risco de suspensão ou perda de cliente ≈ 350 k€/ano.",
    Evidencia_Resumo="KPI-12 (41% das famílias conformes); AA-038 (IRA 60)", Qualidade_Evidencia="Alta",
    IDs_Contexto="PES-12; SWT-T03", IDs_Aspetos="AA-038", ID_Legal="LEG-09", ID_OBJ="OBJ-04", ID_KPI="KPI-12", ID_PAM="PAM-26-10",
    ID_RO="RO-06", ID_Registo_Corporativo="R33", Resposta_Gestao="100% das famílias com documentação e declaração UE (OBJ-04).", Responsavel=F_RD)
fin("PCRmkt", "DM-11", "Oportunidade", DU, HM, 200000, 3, RUBRICAS[0],
    Descricao="Procura de embalagens recicláveis com conteúdo reciclado por marcas europeias de cosmética, alimentar e farmacêutica.",
    Mecanismo_Financeiro="Receitas: novos contratos e prémio de preço nas gamas PCR ≈ 200 k€/ano.",
    Evidencia_Resumo="PES-04; SWT-O01; pedidos de cotação com requisito de PCR", Qualidade_Evidencia="Média",
    IDs_Contexto="SWT-O01; SWT-F04; PES-04", ID_RO="RO-03", ID_Registo_Corporativo="O5",
    Resposta_Gestao="Estudo de mercado e de custo por família (RO-03).", Responsavel=F_GER)
# DM-12 Resíduos
imp("RES", "DM-12", "Impacto negativo", "Real", OP, HC, 2, 2, 2,
    Descricao="Produção de 130,6 t/ano de resíduos, dos quais 2,14 t perigosos (tintas, óleos, embalagens contaminadas).",
    Afetados="Sistemas de gestão de resíduos", Evidencia_Resumo="EMAS-04; EMAS-04b; KPI-05; KPI-07", Qualidade_Evidencia="Alta",
    IDs_Contexto="PES-14", IDs_Aspetos="AA-004; AA-008; AA-011; AA-016; AA-026; AA-029", ID_Legal="LEG-01; LEG-13", ID_KPI="KPI-03; KPI-05; KPI-07",
    Resposta_Gestao="Segregação, valorização e redução de scrap (OBJ-02).", Responsavel=F_SGA)
fin("RESleg", "DM-12", "Risco", OP, HC, 30000, 2, RUBRICAS[4],
    Descricao="Fiscalização de resíduos (classificação LER, e-GAR, MIRR) com coimas por incumprimento.",
    Mecanismo_Financeiro="Multas: coima ambiental ≈ 30 k€.", Evidencia_Resumo="PES-14; LEG-01", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-14", ID_Legal="LEG-01; LEG-13", ID_Registo_Corporativo="R31", Responsavel=F_SGA)
fin("RESval", "DM-12", "Oportunidade", DF, HC, 8000, 4, RUBRICAS[0],
    Descricao="Venda de scrap sujo e embalagens para reciclagem.",
    Mecanismo_Financeiro="Receitas: ≈ 8 k€/ano de venda de materiais recicláveis.", Evidencia_Resumo="AA-028; tbl_residuos", Qualidade_Evidencia="Média",
    IDs_Aspetos="AA-028", Responsavel=F_LOG)
# DM-13 SST
imp("SSTmec", "DM-13", "Impacto negativo", "Potencial", OP, HC, 5, 2, 5, 2, dh="Sim",
    Descricao="Esmagamento de membro superior na troca de molde e setup de máquinas de injeção e sopro.",
    Afetados="Operadores e técnicos de manutenção", Evidencia_Resumo="Registo corporativo R28; avaliação de riscos SST", Qualidade_Evidencia="Média",
    ID_Registo_Corporativo="R28", Resposta_Gestao="LOTO, proteções com encravamento e formação de setup.", Responsavel=F_RH,
    Notas="Gravidade ≥ limiar de direitos humanos: a probabilidade não reduz a pontuação (EFRAG IG 1).")
imp("SSTquim", "DM-13", "Impacto negativo", "Real", OP, HC, 3, 2, 3, dh="Sim",
    Descricao="Exposição de trabalhadores a solventes e COV na serigrafia e no hot stamping.",
    Afetados="Operadores de serigrafia e hot foil", Evidencia_Resumo="Registo corporativo R29; AA-014", Qualidade_Evidencia="Média",
    IDs_Aspetos="AA-014", ID_Registo_Corporativo="R29", Resposta_Gestao="Ventilação localizada, EPI e medições de exposição.", Responsavel=F_RH)
fin("SSTfin", "DM-13", "Risco", OP, HC, 80000, 2, RUBRICAS[4],
    Descricao="Acidente de trabalho grave: paragem, coima da ACT, aumento do prémio de seguro e processo judicial.",
    Mecanismo_Financeiro="Multas, seguros e paragem ≈ 80 k€ por acidente grave.", Evidencia_Resumo="Registo corporativo R28", Qualidade_Evidencia="Média",
    ID_Registo_Corporativo="R28", Responsavel=F_RH)
# DM-14 Condições de trabalho
imp("TURNOS", "DM-14", "Impacto negativo", "Real", OP, HC, 2, 3, 2, dh="Sim",
    Descricao="Trabalho em três turnos com fadiga e passagem de turno deficiente no turno 2.",
    Afetados="≈ 150 trabalhadores", Evidencia_Resumo="Registo corporativo R9 (prémio de defeito no turno 2)", Qualidade_Evidencia="Média",
    ID_Registo_Corporativo="R9", Resposta_Gestao="Rever escalas, pausas e passagem de turno.", Responsavel=F_RH)
fin("OPERADOR", "DM-14", "Risco", OP, HC, 150000, 4, RUBRICAS[2],
    Descricao="Indisponibilidade de operadores (1.ª causa de paragem não planeada) e rotatividade reduzem a produção.",
    Mecanismo_Financeiro="Custos e receitas perdidas: horas de paragem × 350 €/h ≈ 150 k€/ano.",
    Evidencia_Resumo="Registo corporativo R23; tbl_producao_mensal", Qualidade_Evidencia="Alta",
    ID_Registo_Corporativo="R23", Resposta_Gestao="Polivalência, bolsa de substitutos e retenção (O4 corporativo).", Responsavel=F_RH)
# DM-15 Formação
imp("FORM", "DM-15", "Impacto positivo", "Real", OP, HC, 2, 2,
    Descricao="Formação técnica, ambiental e de qualidade reforça as competências e a empregabilidade dos trabalhadores.",
    Afetados="Trabalhadores próprios", Evidencia_Resumo="RG-SGA-08 (registo de formação)", Qualidade_Evidencia="Alta",
    Resposta_Gestao="Plano anual de formação ligado à matriz de competências.", Responsavel=F_RH)
fin("POLIV", "DM-15", "Oportunidade", OP, HM, 40000, 3, RUBRICAS[2],
    Descricao="Polivalência dos operadores reduz paragens e defeitos.",
    Mecanismo_Financeiro="Custos evitados ≈ 40 k€/ano em paragens por falta de operador qualificado.", Evidencia_Resumo="RG-SGA-08; registo corporativo O4",
    Qualidade_Evidencia="Média", ID_Registo_Corporativo="O4", Responsavel=F_RH)
# DM-16 Igualdade
imp("IGUAL", "DM-16", "Impacto negativo", "Potencial", OP, HM, 2, 2, 2, 2, dh="Sim",
    Descricao="Possível disparidade salarial de género e sub-representação em chefias (não medida).",
    Afetados="Trabalhadoras e trabalhadores", Evidencia_Resumo="Sem dados: lacuna identificada", Qualidade_Evidencia="Baixa",
    Resposta_Gestao="Recolher indicadores de igualdade (ESRS S1-16 / VSME) antes da próxima DMA.", Responsavel=F_RH,
    Notas="Classificação provisória por falta de dados.")
# DM-17 Cadeia de valor
imp("S2PCR", "DM-17", "Impacto negativo", "Potencial", UP, HM, 4, 3, 3, 2, dh="Sim",
    Descricao="Condições de trabalho precárias na recolha e triagem de resíduos plásticos que abastecem o PCR.",
    Afetados="Trabalhadores da cadeia de reciclagem", Evidencia_Resumo="Sem diligência devida sobre a origem do PCR", Qualidade_Evidencia="Baixa",
    IDs_Contexto="SWT-T02", Resposta_Gestao="Incluir critérios sociais na avaliação de fornecedores de PCR (RG-SGA-11).", Responsavel=F_CMP)
# DM-18 Comunidades
imp("RUIDO", "DM-18", "Impacto negativo", "Real", OP, HC, 2, 2, 1,
    Descricao="Ruído dos compressores novos percecionado pela vizinhança a ~250 m.",
    Afetados="Comunidade vizinha", Evidencia_Resumo="AA-022 (AAS no SGA); última avaliação acústica em 2023", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-05", IDs_Aspetos="AA-022", ID_Legal="LEG-05", ID_PAM="PAM-26-03", ID_RO="RO-12", ID_Registo_Corporativo="R39",
    Resposta_Gestao="Avaliação acústica acreditada e gatilho de ruído na gestão de mudanças.", Responsavel=F_SGA,
    Notas="Aspeto significativo na ISO 14001 mas não material na DMA: os dois métodos têm critérios e âmbitos diferentes.")
imp("FOGOcom", "DM-18", "Impacto negativo", "Potencial", OP, HM, 4, 3, 4, 2, dh="Sim",
    Descricao="Incêndio na instalação com fumos e águas de combate que afetam a vizinhança e a floresta.",
    Afetados="Comunidade; floresta envolvente", Evidencia_Resumo="AA-034; PES-10; simulacros (RG-SGA-12)", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-10", IDs_Aspetos="AA-034", ID_Legal="LEG-11", ID_RO="RO-08", ID_Registo_Corporativo="R38", Responsavel=F_IND)
imp("EMPREGO", "DM-18", "Impacto positivo", "Real", OP, HC, 3, 2,
    Descricao="Emprego direto de ≈ 150 pessoas e compras a fornecedores locais na Marinha Grande.",
    Afetados="Comunidade local", Evidencia_Resumo="Quadro de pessoal (≈ 150 trabalhadores)", Qualidade_Evidencia="Alta", Responsavel=F_GER)
# DM-19 Segurança do produto
imp("MIGR", "DM-19", "Impacto negativo", "Potencial", DU, HC, 5, 4, 3, 2, dh="Sim",
    Descricao="Migração de substâncias ou contaminação (black specks) em embalagens de contacto alimentar, farmacêutico e cosmético.",
    Afetados="Consumidores finais", Evidencia_Resumo="Registo corporativo R11 (contaminação), R16 (escape de lote)", Qualidade_Evidencia="Média",
    ID_Registo_Corporativo="R11", Resposta_Gestao="Ensaios de migração, BPF (Reg. 2023/2006) e rastreabilidade de lote.", Responsavel=F_QUA,
    Notas="Gravidade ≥ limiar de direitos humanos (saúde): prevalece sobre a probabilidade.")
fin("RECALL", "DM-19", "Risco", DU, HC, 300000, 3, RUBRICAS[0],
    Descricao="Recolha de produto ou perda de cliente por não conformidade de materiais em contacto com alimentos ou medicamentos.",
    Mecanismo_Financeiro="Receitas e custos: recall, indemnização e perda de cliente ≈ 300 k€.",
    Evidencia_Resumo="Registo corporativo R16; linhas alimentar e farmacêutica", Qualidade_Evidencia="Média",
    ID_Registo_Corporativo="R16", Responsavel=F_QUA)
# DM-20 Alegações
imp("ALEG", "DM-20", "Impacto negativo", "Potencial", DU, HC, 2, 4, 1, 3,
    Descricao="Alegações de reciclabilidade ou conteúdo reciclado sem comprovação que induzem clientes e consumidores em erro.",
    Afetados="Clientes; consumidores", Evidencia_Resumo="PES-15; declarações de PCR de fornecedores spot não verificadas", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-15", ID_RO="RO-05", Responsavel=F_RD)
fin("ALEGfin", "DM-20", "Risco", DU, HC, 50000, 3, RUBRICAS[4],
    Descricao="Diretiva (UE) 2024/825: coimas e retirada de alegações ambientais não comprovadas.",
    Mecanismo_Financeiro="Multas e custos de reetiquetagem ≈ 50 k€.", Evidencia_Resumo="PES-15", Qualidade_Evidencia="Média",
    IDs_Contexto="PES-15", ID_RO="RO-05", ID_Registo_Corporativo="R36", ID_PAM="PAM-26-16", Responsavel=F_RD)
# DM-21 Conduta
fin("LEGAL", "DM-21", "Risco", OP, HC, 120000, 3, RUBRICAS[4],
    Descricao="Incumprimento de obrigações de conformidade (título de recursos hídricos, resíduos, ruído) com coima ou suspensão parcial.",
    Mecanismo_Financeiro="Multas e paragem: coima e suspensão parcial ≈ 120 k€.",
    Evidencia_Resumo="RG-SGA-04 (14 diplomas); registo corporativo R32", Qualidade_Evidencia="Alta",
    ID_Legal="LEG-02; LEG-03; LEG-05", ID_KPI="KPI-14", ID_Registo_Corporativo="R32", Resposta_Gestao="Calendário de conformidade e auditoria de evidências.", Responsavel=F_SGA)
imp("CORRUP", "DM-21", "Impacto negativo", "Potencial", UP, HM, 2, 2, 2, 1,
    Descricao="Suborno ou conflitos de interesse em compras e licenciamento.",
    Afetados="Mercado; entidades públicas", Evidencia_Resumo="Sem casos registados; sem código de conduta formal", Qualidade_Evidencia="Baixa",
    Resposta_Gestao="Código de conduta e canal de denúncia.", Responsavel=F_GER)
# DM-22 Fornecedores
fin("SUP005", "DM-22", "Risco", UP, HC, 100000, 3, RUBRICAS[1],
    Descricao="Dependência de fornecedores spot (SUP-005) com lotes fora de especificação que geram scrap e paragens.",
    Mecanismo_Financeiro="Custos: scrap, reprocessamento e paragens ≈ 100 k€/ano.",
    Evidencia_Resumo="Registo corporativo R13; tbl_avaliacao_fornecedor", Qualidade_Evidencia="Alta",
    IDs_Contexto="SWT-W02", ID_RO="RO-05", ID_Registo_Corporativo="R13", ID_PAM="PAM-26-16", Resposta_Gestao="Migrar compras spot para contratos com critérios de qualidade e ambientais.", Responsavel=F_CMP)
imp("SUPesg", "DM-22", "Impacto positivo", "Potencial", UP, HM, 2, 3, prob=3,
    Descricao="A avaliação ambiental de fornecedores críticos eleva as práticas na cadeia de abastecimento.",
    Afetados="Fornecedores e respetivos trabalhadores", Evidencia_Resumo="RG-SGA-11 (avaliação de fornecedores)", Qualidade_Evidencia="Média",
    ID_PAM="PAM-26-16", Responsavel=F_CMP)
# DM-23 Qualidade
fin("NQUAL", "DM-23", "Risco", OP, HC, 180000, 5, RUBRICAS[2],
    Descricao="Custo da não-qualidade: rejeição de 2,39% (meta 2,0%), refação de lotes e reclamações.",
    Mecanismo_Financeiro="Custos: refugo, retrabalho e reclamações ≈ 180 k€/ano.",
    Evidencia_Resumo="Registo corporativo R24, R17; raio-X analítico de 18 meses", Qualidade_Evidencia="Alta",
    IDs_Contexto="SWT-W03", ID_Registo_Corporativo="R24", Resposta_Gestao="Plano de capacidade de processo e CAPA eficazes.", Responsavel=F_QUA)
imp("SCRAPimp", "DM-23", "Impacto negativo", "Real", OP, HC, 2, 2, 2,
    Descricao="Scrap e retrabalho consomem resina e energia adicionais (31,2 t/ano de scrap).",
    Afetados="Recursos; clima", Evidencia_Resumo="AA-011 (31,2 t/ano); KPI-03", Qualidade_Evidencia="Alta",
    IDs_Aspetos="AA-011", ID_OBJ="OBJ-02", ID_KPI="KPI-03", ID_PAM="PAM-26-12", Responsavel=F_PRO)
# DM-24 Dados
fin("DADOSrisk", "DM-24", "Risco", OP, HC, 60000, 2, RUBRICAS[2],
    Descricao="Indisponibilidade ou corrupção do warehouse de dados e dos sistemas OT que sustentam KPIs e decisões.",
    Mecanismo_Financeiro="Custos: paragem e decisões erradas ≈ 60 k€ por incidente.", Evidencia_Resumo="Registo corporativo R26", Qualidade_Evidencia="Média",
    ID_Registo_Corporativo="R26", Responsavel=F_GER)
fin("DADOSopp", "DM-24", "Oportunidade", OP, HC, 50000, 4, RUBRICAS[0],
    Descricao="Usar os dados industriais para um painel ambiental por máquina, turno e lote e responder a questionários ESG de clientes.",
    Mecanismo_Financeiro="Receitas e custos: retenção de clientes e eficiência ≈ 50 k€/ano.",
    Evidencia_Resumo="SWT-F01; 18 meses de dados estruturados", Qualidade_Evidencia="Alta",
    IDs_Contexto="SWT-F01", ID_RO="RO-01", ID_Registo_Corporativo="O3", ID_PAM="PAM-26-09", Resposta_Gestao="Painel ambiental integrado no Power BI (PAM-26-09).", Responsavel=F_SGA)

for n, r in enumerate(IRO_ROWS, start=1):
    r["ID_IRO"] = f"IRO-{n:03d}"
    r.setdefault("Estado_Validacao", "Validado pelo responsável")
    r["Data_Avaliacao"] = D_AVAL
KEY = {r["key"]: r["ID_IRO"] for r in IRO_ROWS}

# ------------------------------------------------------------------------------------------- evidências
# (chave IRO, indicador, valor, unidade, período, registo fonte, ID fonte, tipo de dado, qualidade, observação)
P12 = "2026-01 a 2026-12"
import envdata as _env
_prod, _mm, _fact, _res = _env.ambiente()
_A = _env.anual(_fact, _res, _prod)   # ano civil de 2026 (fonte única RG-SGA-13)
_T = lambda v, n=1: round(v / 1000, n)
EVID = [
    ("GEE2", "Emissões de GEE (âmbitos 1 + 2 location-based)", round(G19["S1"] + G19["S2LB"], 1), "tCO2e", P12, "RG-SGA-19", "tbl_inventario_gee", "Calculado", "Alta", "Mesmo valor do EMAS-06 (RG-SGA-16)."),
    ("GEE2", "Fuga de R410A do chiller CH-01", 3.2, "kg", "2025-11", "RG-SGA-03", "AA-025", "Medido", "Alta", "GWP 2.088 → 6,7 tCO2e."),
    ("GEE3a", "Polímero virgem consumido", _T(_A["polimero_kg"] - _A["pcr_kg"]), "t", P12, "RG-SGA-03", "AA-001", "Calculado", "Alta", None),
    ("GEE3a", "Emissões estimadas da produção do polímero virgem", round((_A["polimero_kg"] - _A["pcr_kg"]) / 1000 * 1.9, 1), "tCO2e", P12, "RG-SGA-17", "—", "Estimado", "Baixa", "Polímero virgem × 1,9 kgCO2e/kg (fator médio de literatura)."),
    ("GEEcli", "Faturação anual", 3680000, "€", "2026", "Registo corporativo", "Histórico", "Medido", "Alta", "Base para estimar a exposição de receitas."),
    ("ENimp", "Consumo total de energia elétrica", _T(_A["ene_total_kwh"]), "MWh", P12, "RG-SGA-16", "EMAS-01", "Calculado", "Alta", None),
    ("ENimp", "Energia renovável (garantias de origem)", _T(_A["ene_total_kwh"] * 0.55), "MWh", P12, "RG-SGA-16", "EMAS-01b", "Calculado", "Alta", "55% do consumo."),
    ("ENimp", "Intensidade energética (baseline)", 109.9, "kWh/1.000 un", "Baseline", "RG-SGA-05", "KPI-01", "Calculado", "Alta", None),
    ("ENpreco", "Custo adicional com +0,03 €/kWh", round(_A["ene_total_kwh"] * 0.03), "€/ano", "Cenário", "RG-SGA-17", "—", "Estimado", "Média", "Consumo de 2026 × 30 €/MWh."),
    ("ENupac", "Produção fotovoltaica prevista", 1400, "MWh/ano", "Estimativa", "RG-SGA-03", "AA-032", "Estimado", "Média", None),
    ("ENefic", "Consumo dos compressores de ar", _T(_A["ene_UTL-AR"]), "MWh", P12, "RG-SGA-03", "AA-021", "Calculado", "Alta", None),
    ("ADcalor", "Anomalia de temperatura em agosto de 2026", 2.2, "°C", "2026-08", "RG-SGA-13", "KPI-16", "Medido", "Alta", "Face à normal de Leiria."),
    ("ADcalor", "Água de reposição da torre", round(_A["agua_torre"]), "m³", P12, "RG-SGA-03", "AA-023", "Calculado", "Alta", None),
    ("COV", "Emissões de COV (balanço de solventes)", Q21["cov_t"], "t", P12, "RG-SGA-21", "tbl_quimicos", "Calculado", "Alta", "Mesmo valor do EMAS-06b (RG-SGA-16) e ESG-E12 (RG-SGA-19)."),
    ("COV", "Solvente de limpeza consumido", Q21["solvente_kg"], "kg", P12, "RG-SGA-03", "AA-014", "Medido", "Alta", "Aspeto ambiental significativo (IRA 40)."),
    ("COV", "Solvente por 1.000 peças serigrafadas (baseline)", 0.1605, "kg/1.000 peças", "Baseline", "RG-SGA-05", "KPI-06", "Calculado", "Alta", None),
    ("DERR", "Não conformidade do kit antipoluição", 1, "n.º", "2026", "RG-SGA-07", "NC-SGA-26-03", "Medido", "Alta", None),
    ("PELLET", "Granulado recolhido nos pontos de contenção", round(_A["granulado_kg"]), "kg/ano", P12, "RG-SGA-03", "AA-003", "Estimado", "Média", "Perdas totais não medidas."),
    ("PELLET", "Pontos críticos de granulado com contenção", 0.4286, "fração", "Baseline", "RG-SGA-05", "KPI-13", "Medido", "Alta", "6 de 14 pontos."),
    ("SUBST", "Tinta de serigrafia consumida", round(_A["tinta_kg"]), "kg", P12, "RG-SGA-03", "AA-015", "Calculado", "Alta", None),
    ("AGUA", "Consumo total de água", round(_A["agua_total"]), "m³", P12, "RG-SGA-16", "EMAS-03", "Medido", "Alta", None),
    ("AGUA", "Intensidade hídrica (baseline)", 0.1423, "m³/1.000 un", "Baseline", "RG-SGA-05", "KPI-02", "Calculado", "Alta", None),
    ("SOLO", "Área impermeabilizada", 32000, "m²", "2026", "RG-SGA-16", "EMAS-05b", "Medido", "Alta", None),
    ("SOLO", "Área orientada para a natureza no local", 3500, "m²", "2026", "RG-SGA-16", "EMAS-05c", "Medido", "Alta", None),
    ("VIRGEM", "Fluxo mássico de materiais", _T(_A["polimero_kg"] + _A["tinta_kg"] + _A["foil_kg"] + _A["solvente_kg"]), "t", P12, "RG-SGA-16", "EMAS-02", "Calculado", "Alta", None),
    ("VIRGEM", "Quota de polímero reciclado (PCR/rPET)", 0.12, "fração", P12, "RG-SGA-13", "PCR_SHARE", "Estimado", "Média", "Parâmetro do modelo ambiental."),
    ("REGRIND", "Scrap limpo reintegrado", _T(_A["regrind_kg"]), "t", P12, "RG-SGA-03", "AA-020", "Calculado", "Alta", None),
    ("SCRAPimp", "Scrap gerado (todos os processos)", _T(_A["scrap_kg"]), "t", P12, "RG-SGA-03", "AA-011", "Calculado", "Alta", None),
    ("FIMVIDA", "SKUs em classe F RecyClass (PVC, PETG, preto de carbono)", _RZ["n_F"], "SKUs", "2026-09", "RG-SGA-20", "tbl_recyclass", "Calculado", "Média", "Autoavaliação com regras simplificadas."),
    ("D4R", "SKUs não isentos com grau PPWR indicativo A–C", round(_RZ["pct_ac_skus"], 4), "fração", "2026-09", "RG-SGA-05", "KPI-18", "Calculado", "Média", "Autoavaliação RecyClass (RG-SGA-20)."),
    ("PPWR", "Massa vendida com grau PPWR A–C (não isentos)", round(_RZ["pct_ac_massa"], 4), "fração", P12, "RG-SGA-05", "KPI-20", "Calculado", "Média", "RG-SGA-20."),
    ("PPWR", "Famílias de embalagem com conformidade PPWR", 0.4091, "fração", "Baseline", "RG-SGA-05", "KPI-12", "Medido", "Alta", "9 de 22 famílias."),
    ("RES", "Resíduos produzidos", _T(_A["res_total"]), "t", P12, "RG-SGA-16", "EMAS-04", "Medido", "Alta", None),
    ("RES", "Resíduos perigosos", _T(_A["res_perig"], 2), "t", P12, "RG-SGA-16", "EMAS-04b", "Medido", "Alta", None),
    ("NQUAL", "Taxa de rejeição", 0.0239, "fração", "22 meses", "datasets/silver", "fact_production", "Medido", "Alta", "Meta 2,0%."),
    ("NQUAL", "Grupos máquina×molde×característica com Cpk ≥ 1,33", 0, "fração", "22 meses", "Registo corporativo", "R17", "Calculado", "Alta", "0 de 190 grupos."),
    ("OPERADOR", "Indisponibilidade de operador como causa de paragem", 1, "posição no ranking", "22 meses", "Registo corporativo", "R23", "Calculado", "Alta", "1.ª causa de paragem não planeada."),
    ("EMPREGO", "Trabalhadores", 150, "n.º", "2026", "RG-SGA-13", "AGUA_SAN", "Estimado", "Média", "Parâmetro do modelo ambiental."),
    ("RUIDO", "Distância às habitações mais próximas", 250, "m", "2026", "RG-SGA-01", "PES-05", "Estimado", "Média", None),
    ("IGUAL", "Indicadores de igualdade disponíveis", 0, "n.º", "2026", "RG-SGA-17", "—", "Qualitativo", "Baixa", "Lacuna de dados."),
]

# ------------------------------------------------------------------------------------------- partes interessadas
# parte -> (data, método, n.º participantes, [(tema, relevância 1-5, tipo de contributo, comentário)])
OPN, EVI = "Opinião / perceção", "Evidência objetiva"
CONS = {
    "Colaboradores": (dt.date(2026, 6, 10), "Workshop", 18, [
        ("DM-13", 5, EVI, "Quase-acidentes na troca de molde relatados nos DDS."),
        ("DM-14", 4, OPN, "Fadiga no turno 2 e falta de substitutos."),
        ("DM-15", 4, OPN, "Pedem formação em setup e qualidade."),
        ("DM-04", 3, OPN, "Cheiro a solvente na serigrafia no verão."),
        ("DM-16", 2, OPN, "Sem perceção de desigualdade; pedem transparência salarial."),
        ("DM-06", 3, OPN, "Granulado no pavimento junto aos silos.")]),
    "Clientes": (dt.date(2026, 5, 20), "Questionário", 9, [
        ("DM-11", 5, EVI, "7 de 9 clientes exigem declaração PPWR e reciclabilidade até 2027."),
        ("DM-10", 5, EVI, "Pedidos de conteúdo reciclado certificado."),
        ("DM-01", 4, EVI, "Questionários de pegada de carbono (EcoVadis/CDP) de 3 marcas."),
        ("DM-19", 5, EVI, "Clientes farmacêuticos exigem BPF e ensaios de migração."),
        ("DM-20", 4, OPN, "Receio de alegações 'verdes' não comprovadas."),
        ("DM-23", 5, EVI, "Reclamações por lote refeito e prazo.")]),
    "Fornecedores": (dt.date(2026, 5, 28), "Reunião", 5, [
        ("DM-10", 4, OPN, "Oferta de PCR limitada e com prémio de preço."),
        ("DM-22", 3, OPN, "Pedem previsibilidade de encomendas."),
        ("DM-17", 3, OPN, "Recicladores com auditorias sociais parciais.")]),
    "Autoridades (APA / CCDR / ACT)": (dt.date(2026, 4, 30), "Análise documental", 1, [
        ("DM-06", 4, EVI, "Novo regulamento de perdas de granulado."),
        ("DM-12", 4, EVI, "Campanha de fiscalização de e-GAR/MIRR."),
        ("DM-21", 4, EVI, "Título de recursos hídricos a regularizar."),
        ("DM-13", 4, EVI, "Campanha ACT sobre máquinas e LOTO.")]),
    "Comunidade / vizinhança": (dt.date(2026, 7, 2), "Canal de reclamações", 3, [
        ("DM-18", 4, EVI, "2 reclamações de ruído noturno após instalação dos compressores."),
        ("DM-03", 3, OPN, "Preocupação com incêndio florestal no verão."),
        ("DM-08", 3, OPN, "Restrições de água no verão de 2025.")]),
    "Acionistas / Direção": (dt.date(2026, 6, 25), "Entrevista", 3, [
        ("DM-02", 5, EVI, "Energia é o 2.º maior custo variável."),
        ("DM-11", 5, OPN, "PPWR condiciona o acesso ao mercado UE."),
        ("DM-23", 5, EVI, "Custo da não-qualidade acima da meta."),
        ("DM-24", 4, OPN, "Dados como vantagem competitiva."),
        ("DM-01", 4, OPN, "Pressão dos clientes para descarbonizar.")]),
    "Operadores de gestão de resíduos": (dt.date(2026, 5, 15), "Reunião", 2, [
        ("DM-12", 3, OPN, "Segregação a melhorar nos contaminados."),
        ("DM-11", 4, OPN, "Decoração e multimaterial dificultam a reciclagem.")]),
    "Seguradoras / bancos": (dt.date(2026, 6, 5), "Entrevista", 2, [
        ("DM-03", 4, OPN, "Risco de incêndio e água de combate na renovação da apólice."),
        ("DM-02", 4, OPN, "Financiamento verde para fotovoltaico e eficiência."),
        ("DM-05", 3, OPN, "Garantia financeira de responsabilidade ambiental.")]),
}


class BookDMA(Book):
    """Book com critérios/parâmetros como tabelas na folha Listas e secção de metodologia no LEIA-ME."""

    def _write_lists(self):
        super()._write_lists()
        ws = self.wb["Listas"]
        self.sheets_info[-1] = ("Listas", "Domínios de validação e, abaixo, as tabelas de critérios (tbl_dma_escalas) e de parâmetros "
                                          "(tbl_dma_parametros) com os limiares lidos pelas fórmulas — alterar aqui recalcula toda a análise.")
        r0 = 3 + max(len(v) for v in self.lists.values()) + 2
        ws.cell(row=r0, column=1, value="CRITÉRIOS DE AVALIAÇÃO (escalas 1–5) — escolha metodológica interna, documentada; não é uma escala imposta pelos ESRS").font = F_BOLD
        esc = [
            ("Magnitude", 1, "Mínima", "Efeito negligenciável / benefício residual", None, None),
            ("Magnitude", 2, "Baixa", "Efeito pequeno e localizado", None, None),
            ("Magnitude", 3, "Média", "Efeito relevante num recurso, grupo ou indicador", None, None),
            ("Magnitude", 4, "Alta", "Efeito grave (dano ambiental relevante, lesão com incapacidade)", None, None),
            ("Magnitude", 5, "Muito alta", "Efeito muito grave (morte, dano ambiental extenso)", None, None),
            ("Alcance", 1, "Pontual", "Posto de trabalho / área restrita", None, None),
            ("Alcance", 2, "Local", "Instalação ou grupo pequeno de pessoas", None, None),
            ("Alcance", 3, "Regional", "Concelho, bacia ou grupo relevante de pessoas", None, None),
            ("Alcance", 4, "Alargado", "Nacional ou vários elos da cadeia de valor", None, None),
            ("Alcance", 5, "Global", "Toda a cadeia de valor / efeito global", None, None),
            ("Irremediabilidade", 1, "Imediatamente reversível", "Reversível sem custo relevante", None, None),
            ("Irremediabilidade", 2, "Reversível < 1 ano", "Reversível em menos de um ano", None, None),
            ("Irremediabilidade", 3, "Reversível com esforço", "Remediação cara ou demorada", None, None),
            ("Irremediabilidade", 4, "Dificilmente reversível", "Remediação parcial", None, None),
            ("Irremediabilidade", 5, "Irreversível", "Sem remediação possível", None, None),
            ("Probabilidade", 1, "Rara", "< 10% no horizonte considerado", None, 0.05),
            ("Probabilidade", 2, "Improvável", "10–30%", None, 0.2),
            ("Probabilidade", 3, "Possível", "30–50%", None, 0.4),
            ("Probabilidade", 4, "Provável", "50–80%", None, 0.65),
            ("Probabilidade", 5, "Quase certa", "> 80% (impacto real = 5)", None, 0.9),
            ("Magnitude financeira", 1, "Muito baixa", "Efeito < 5 k€/ano", 0, None),
            ("Magnitude financeira", 2, "Baixa", "5–25 k€/ano", 5000, None),
            ("Magnitude financeira", 3, "Média", "25–100 k€/ano", 25000, None),
            ("Magnitude financeira", 4, "Alta", "100–300 k€/ano", 100000, None),
            ("Magnitude financeira", 5, "Muito alta", "≥ 300 k€/ano (≈ 8% da faturação)", 300000, None),
        ]
        hr = r0 + 1
        cols = ["Criterio", "Nivel", "Rotulo", "Descricao", "Limite_Inferior_EUR", "Probabilidade_Media"]
        header_row(ws, hr, cols)
        for k, row in enumerate(esc):
            for j, v in enumerate(row):
                c = ws.cell(row=hr + 1 + k, column=1 + j, value=v)
                c.font, c.border = F_BASE, BORDER
        last = hr + len(esc)
        t = Table(displayName="tbl_dma_escalas", ref=f"A{hr}:F{last}")
        t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
        ws.add_table(t)
        pr = [i for i, e in enumerate(esc) if e[0] == "Probabilidade"]
        fr = [i for i, e in enumerate(esc) if e[0] == "Magnitude financeira"]
        self.wb.defined_names["esc_Prob_Media"] = DefinedName("esc_Prob_Media", attr_text=f"Listas!$F${hr + 1 + pr[0]}:$F${hr + 1 + pr[-1]}")
        self.wb.defined_names["esc_Fin_Limite"] = DefinedName("esc_Fin_Limite", attr_text=f"Listas!$E${hr + 1 + fr[0]}:$E${hr + 1 + fr[-1]}")

        r1 = last + 3
        ws.cell(row=r1, column=1, value="PARÂMETROS E LIMIARES (células editáveis; nomes prm_* usados nas fórmulas)").font = F_BOLD
        prm = [
            ("prm_Limiar_Impacto", 12, "pontos (1–25)", "IRO de impacto material se Score_Impacto ≥ limiar", "Decisão interna (DMA 2026)"),
            ("prm_Limiar_Financeiro", 12, "pontos (1–25)", "IRO financeiro material se Score_Financeiro ≥ limiar", "Decisão interna (DMA 2026)"),
            ("prm_Limiar_Alto", 18, "pontos (1–25)", "Banda 'Alta' da matriz", "Decisão interna"),
            ("prm_Limiar_Baixo", 6, "pontos (1–25)", "Abaixo: banda 'Baixa'", "Decisão interna"),
            ("prm_Grav_DH", 4, "gravidade (1–5)", "Impactos potenciais sobre pessoas (direitos humanos) com gravidade ≥ este valor usam probabilidade 5", "EFRAG IG 1 — a gravidade prevalece sobre a probabilidade"),
            ("prm_Relev_Alerta", 4, "relevância (1–5)", "Tema não material com relevância média das partes interessadas ≥ valor gera alerta", "Decisão interna"),
            ("prm_Meses_Rev_Material", 6, "meses", "Revisão dos IRO materiais", "Decisão interna"),
            ("prm_Meses_Rev_Outros", 12, "meses", "Revisão dos restantes IRO", "Decisão interna"),
            ("prm_Faturacao_EUR", 3680000, "€/ano", "Faturação anual (referência para as bandas financeiras)", "Registo corporativo, Histórico 2026"),
            ("prm_Preco_Eletricidade", 0.13, "€/kWh", "Preço médio da eletricidade usado nas estimativas", "Pressuposto — confirmar com faturas"),
            ("prm_Preco_Polimero", 1.35, "€/kg", "Preço médio do polímero usado nas estimativas", "Pressuposto — confirmar com compras"),
            ("prm_Trabalhadores", 150, "n.º", "Trabalhadores próprios", "RG-SGA-13 (parâmetro AGUA_SAN)"),
        ]
        hr2 = r1 + 1
        header_row(ws, hr2, ["Parametro", "Valor", "Unidade", "Descricao", "Fonte"])
        for k, row in enumerate(prm):
            rr = hr2 + 1 + k
            for j, v in enumerate(row):
                c = ws.cell(row=rr, column=1 + j, value=v)
                c.font, c.border = F_BASE, BORDER
            ws.cell(row=rr, column=2).fill = PatternFill("solid", fgColor="FFF2B3")
            self.wb.defined_names[row[0]] = DefinedName(row[0], attr_text=f"Listas!$B${rr}")
        t = Table(displayName="tbl_dma_parametros", ref=f"A{hr2}:E{hr2 + len(prm)}")
        t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
        ws.add_table(t)
        for L, wdt in zip("ABCDEF", (24, 12, 26, 60, 40, 18)):
            ws.column_dimensions[L].width = max(ws.column_dimensions[L].width or 0, wdt)

    def _write_readme(self):
        super()._write_readme()
        ws = self.readme
        r = ws.max_row + 2

        def band(text):
            nonlocal r
            ws.cell(row=r, column=1, value=text).font = F_BOLD
            for c in (1, 2):
                ws.cell(row=r, column=c).fill = FILL_BAND
            r += 1

        def kv(k, v):
            nonlocal r
            a, b = ws.cell(row=r, column=1, value=k), ws.cell(row=r, column=2, value=v)
            a.font, a.alignment, b.font, b.alignment = F_BOLD, WRAP_TOP, F_BASE, WRAP_TOP
            r += 1

        band("METODOLOGIA (EFRAG IG 1 — processo em 4 passos, adaptado ao SGA)")
        kv("1. Contexto e âmbito", "Operações próprias da Unidade 1 e cadeia de valor (fornecedores de polímero, transporte, clientes de cosmética, alimentar e farmacêutica, fim de vida). Período de referência: set/2025 a ago/2026. Finalidade: gestão (SGA, riscos, pedidos ESG de clientes), não reporte obrigatório.")
        kv("2. Identificação", "Lista de temas a partir dos tópicos ESRS (ESRS 1 AR 16) + temas específicos da entidade, cruzada com o contexto (RG-SGA-01), aspetos ambientais (RG-SGA-03), requisitos legais (RG-SGA-04), riscos e oportunidades (RG-SGA-02 e registo corporativo) e consulta às partes interessadas.")
        kv("3. Avaliação", "Cada IRO é avaliado numa só dimensão. Impacto: Gravidade = média de Magnitude, Alcance e Irremediabilidade (esta só nos negativos); Score_Impacto = Gravidade × Probabilidade efetiva (real = 5; direitos humanos com gravidade ≥ prm_Grav_DH = 5). Financeira: Magnitude pelas bandas em € (tbl_dma_escalas); Score_Financeiro = Magnitude × Probabilidade. Material se o score ≥ limiar (prm_Limiar_*).")
        kv("4. Consolidação", "Um tema é material se pelo menos um IRO for material: Dupla materialidade (ambas), Material — impacto, Material — financeira ou Não material. As partes interessadas informam a avaliação mas não entram na fórmula; divergências geram alerta (Alerta_Consistencia).")
        kv("Aplicabilidade legal", "Com ≈ 150 trabalhadores e ≈ 3,7 M€ de faturação, a Plasticom está fora do âmbito obrigatório da CSRD/ESRS; a DMA é voluntária e pode alimentar a norma voluntária para PME (VSME) e os pedidos ESG de clientes. O âmbito da CSRD está a ser alterado pelo processo de simplificação europeu (Omnibus): confirmar a legislação em vigor à data de uso.")
        kv("ISO 14001 ≠ DMA", "A significância dos aspetos ambientais (IRA) e a materialidade de impacto usam critérios e âmbitos diferentes: ex. o ruído dos compressores é aspeto significativo no SGA mas não material na DMA. Os dados são partilhados pelas chaves (IDs_Aspetos, ID_RO, ID_Legal, ID_OBJ, ID_PAM).")
        kv("Referências", "EFRAG IG 1 Materiality Assessment (2024); EFRAG IG 2 Value Chain (2024); ESRS 1 §43–51 e AR 16; GRI 3 Material Topics (2021); IFRS S1 (materialidade financeira); ISO 14001:2026 cláusulas 4.1, 4.2, 6.1.")
        kv("Limitações", "Avaliação simulada da fábrica fictícia Plasticom: pontuações, estimativas em € e contributos das partes interessadas são hipóteses didáticas a validar. Emissões do âmbito 3 estimadas por fator médio. Lacunas de dados sinalizadas com Qualidade_Evidencia = Baixa.")
        kv("Uso em análise de dados", "Juntar tbl_dma_iro a tbl_dma_temas por ID_Tema; tbl_dma_evidencias por ID_IRO; tbl_dma_consultas por ID_Tema. Chaves externas: ID_RO e ID_Registo_Corporativo → RG-SGA-02 (tbRiscos/tbOportunidades); IDs_Aspetos → RG-SGA-03; ID_Legal → RG-SGA-04; ID_OBJ/ID_KPI → RG-SGA-05; ID_PAM → RG-SGA-06. Campos com vários IDs usam ';'.")


def tref(sheet, colnames, n, colname, hr=4):
    """Intervalo absoluto de uma coluna de tabela gerada por Book.table (título → cabeçalho na linha 4)."""
    L = get_column_letter(colnames.index(colname) + 1)
    return f"'{sheet}'!${L}${hr + 1}:${L}${hr + max(n, 1)}"


def build(out):
    b = BookDMA("RG-SGA-17", "Análise de Dupla Materialidade (DMA) — Plasticom", version="02", date=D_AVAL,
                activities="Complemento ESG do SGA (não é atividade do curso): dupla materialidade para priorizar temas, riscos e oportunidades de sustentabilidade.",
                clauses="4.1 Contexto; 4.2 Partes interessadas; 6.1.1–6.1.4 Aspetos, obrigações, riscos e oportunidades (integração)",
                purpose=("Identificar e avaliar os temas de sustentabilidade materiais para a Plasticom nas duas perspetivas — impacto (efeitos da empresa "
                         "sobre pessoas e ambiente, de dentro para fora) e financeira (efeitos dos temas sobre o desempenho e a posição financeira, de fora "
                         "para dentro) — ao nível de cada impacto, risco e oportunidade (IRO), com critérios parametrizados, evidências rastreáveis, "
                         "contributos das partes interessadas e ligação às decisões do SGA. Revisão 02: substitui a folha única 28_Dupla_Materialidade "
                         "(12 temas, sem IRO nem evidências)."),
                links=[("RG-SGA-01 Contexto", "IDs_Contexto → SWOT (SWT-*) e PESTEL (PES-*)."),
                       ("RG-SGA-02 Riscos e oportunidades", "ID_RO → coluna 'ID RO (SGA)' e ID_Registo_Corporativo → coluna 'ID' de tbRiscos / tbOportunidades."),
                       ("RG-SGA-03 Aspetos", "IDs_Aspetos → tbl_aspetos (significância ISO 14001)."),
                       ("RG-SGA-04 Legal", "ID_Legal → tbl_legal."),
                       ("RG-SGA-05 Objetivos e KPI", "ID_OBJ → tbl_objetivos; ID_KPI → tbl_kpi."),
                       ("RG-SGA-06 PAM", "ID_PAM → tbl_pam."),
                       ("RG-SGA-16 EMAS", "Evidências quantitativas (EMAS-*) — instantâneo à data da avaliação."),
                       ("RG-SGA-02 — avaliação corporativa", "Linha equivalente em tbRiscos / tbOportunidades: avaliação 5×5, inerente, BowTie e KRI.")])
    b.add_list("Pilar", PILARES)
    b.add_list("TopicoESRS", ESRS)
    b.add_list("TipoIRO", TIPOS)
    b.add_list("Natureza", ["Real", "Potencial"])
    b.add_list("Etapa", ETAPAS)
    b.add_list("Horizonte", HORIZ)
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("Escala", [1, 2, 3, 4, 5])
    b.add_list("Rubrica", RUBRICAS)
    b.add_list("Qualidade", ["Alta", "Média", "Baixa"])
    b.add_list("TipoDado", ["Medido", "Calculado", "Estimado", "Qualitativo"])
    b.add_list("EstadoValidacao", ["Rascunho", "Validado pelo responsável", "Aprovado pela Direção"])
    b.add_list("RelevanciaSetorial", ["Alta", "Média", "Baixa"])
    b.add_list("Parte", PARTES)
    b.add_list("Metodo", ["Workshop", "Questionário", "Entrevista", "Reunião", "Análise documental", "Canal de reclamações"])
    b.add_list("TipoContributo", [OPN, EVI])
    b.add_list("Funcao", FUNC_NAMES)
    for nm, vals in (("FPilar", PILARES), ("FTopico", ESRS), ("FEtapa", ETAPAS), ("FHorizonte", HORIZ), ("FTipo", TIPOS)):
        b.add_list(nm, ["(Todos)"] + vals)

    painel = b.sheet("Painel", "Painel interativo: filtros, indicadores, matriz de dupla materialidade, gráfico dinâmico, ranking, resumo por tópico ESRS "
                               "e tabela dinâmica com segmentações de dados.", tab_color="7030A0")

    # ---------------- definição das colunas (necessária antes para as referências cruzadas)
    T_EXTRA, I_EXTRA, E_EXTRA, C_EXTRA = 12, 30, 40, 40
    n_ev = len(EVID) + len({r["key"] for r in IRO_ROWS} - {e[0] for e in EVID})
    nT, nI, nE, nC = len(TEMAS_DMA) + T_EXTRA, len(IRO_ROWS) + I_EXTRA, n_ev + E_EXTRA, sum(len(v[3]) for v in CONS.values()) + C_EXTRA
    tcols_names = ["ID_Tema", "Pilar", "ESRS_Topico", "Subtopico_ESRS", "Tema", "Descricao", "Referencia_GRI", "Relevancia_Setorial",
                   "Fonte_Identificacao", "Dono", "Justificacao_Avaliacao", "Data_Avaliacao", "N_IRO", "N_Impactos", "N_Riscos_Oportunidades",
                   "Score_Impacto_Max", "Score_Financeiro_Max", "Material_Impacto", "Material_Financeiro", "Classificacao", "Banda_Impacto",
                   "Banda_Financeira", "Indice_Prioridade", "Ranking", "Exposicao_Risco_EUR", "Potencial_Oportunidade_EUR",
                   "Relevancia_Partes_Interessadas", "N_Contributos", "Cobertura_Evidencia", "Alerta_Consistencia", "Decisao_Gestao"]
    icols_names = ["ID_IRO", "ID_Tema", "Tema", "Pilar", "ESRS_Topico", "Tipo_IRO", "Dimensao", "Descricao", "Natureza", "Etapa_Cadeia_Valor",
                   "Horizonte", "Afetados", "Direitos_Humanos", "Magnitude", "Alcance", "Irremediabilidade", "Probabilidade", "Gravidade",
                   "Probabilidade_Efetiva", "Score_Impacto", "Mecanismo_Financeiro", "Rubrica_Financeira", "Efeito_Financeiro_EUR_Ano",
                   "Probabilidade_Financeira", "Magnitude_Financeira", "Score_Financeiro", "Efeito_Ponderado_EUR", "Score", "Material",
                   "Classificacao_IRO", "Ranking_IRO", "Evidencia_Resumo", "Qualidade_Evidencia", "N_Evidencias", "Controlo_Qualidade",
                   "IDs_Contexto", "ID_RO", "ID_Registo_Corporativo", "IDs_Aspetos", "ID_Legal", "ID_OBJ", "ID_KPI", "ID_PAM",
                   "Resposta_Gestao", "Responsavel", "Estado_Validacao", "Data_Avaliacao", "Proxima_Revisao", "Notas"]
    ecols_names = ["ID_Evidencia", "ID_IRO", "ID_Tema", "Indicador", "Valor", "Unidade", "Periodo", "Registo_Fonte", "ID_Fonte", "Tipo_Dado",
                   "Qualidade", "Observacao"]
    ccols_names = ["ID_Contributo", "Data", "Parte_Interessada", "Metodo", "N_Participantes", "ID_Tema", "Tema", "Relevancia_Percebida",
                   "Tipo_Contributo", "Comentario", "Incorporado_na_Avaliacao"]
    TR = lambda c: tref("Temas", tcols_names, nT, c)
    IR = lambda c: tref("IRO", icols_names, nI, c)
    ER = lambda c: tref("Evidencias", ecols_names, nE, c)
    CR = lambda c: tref("Consultas", ccols_names, nC, c)

    # ---------------- Temas
    tid = "@ID_Tema@"
    tcols = [
        col("ID_Tema", 8, desc="Identificador do tema (DM-nn).", key="PK", dom="DM-nn"),
        col("Pilar", 11, dv="Pilar", desc="Ambiental, Social ou Governança."),
        col("ESRS_Topico", 24, dv="TopicoESRS", desc="Tópico ESRS (E1–G1) ou específico da entidade."),
        col("Subtopico_ESRS", 26, desc="Subtópico ESRS (ESRS 1 AR 16) ou designação interna."),
        col("Tema", 32, desc="Tema de sustentabilidade avaliado."),
        col("Descricao", 46, desc="O que o tema abrange na Plasticom."),
        col("Referencia_GRI", 12, desc="GRI Standard correspondente (interoperabilidade).", req=False),
        col("Relevancia_Setorial", 11, dv="RelevanciaSetorial", desc="Relevância do tema para o setor de embalagens plásticas."),
        col("Fonte_Identificacao", 34, desc="Onde o tema foi identificado (registos do SGA, PESTEL, SWOT, registo corporativo)."),
        col("Dono", 24, dv="Funcao", desc="Responsável pelo tema."),
        col("Justificacao_Avaliacao", 46, desc="Fundamento da avaliação (factos e dados que a sustentam)."),
        col("Data_Avaliacao", 11, "date", desc="Data da avaliação."),
        col("N_IRO", 7, "int", f=f'=IF({tid}="","",COUNTIF({IR("ID_Tema")},{tid}))', desc="N.º de IRO do tema."),
        col("N_Impactos", 8, "int", f=f'=IF({tid}="","",COUNTIFS({IR("ID_Tema")},{tid},{IR("Dimensao")},"Impacto"))', desc="N.º de impactos."),
        col("N_Riscos_Oportunidades", 10, "int", f=f'=IF({tid}="","",COUNTIFS({IR("ID_Tema")},{tid},{IR("Dimensao")},"Financeira"))', desc="N.º de riscos e oportunidades."),
        col("Score_Impacto_Max", 10, "num1", f=f'=IF(OR({tid}="",@N_Impactos@=0),"",_xlfn.MAXIFS({IR("Score_Impacto")},{IR("ID_Tema")},{tid}))', desc="Maior pontuação de impacto dos IRO do tema (1–25)."),
        col("Score_Financeiro_Max", 10, "num1", f=f'=IF(OR({tid}="",@N_Riscos_Oportunidades@=0),"",_xlfn.MAXIFS({IR("Score_Financeiro")},{IR("ID_Tema")},{tid}))', desc="Maior pontuação financeira dos IRO do tema (1–25)."),
        col("Material_Impacto", 9, f=f'=IF({tid}="","",IF(@Score_Impacto_Max@="","Não",IF(@Score_Impacto_Max@>=prm_Limiar_Impacto,"Sim","Não")))', desc="Sim se algum impacto é material."),
        col("Material_Financeiro", 9, f=f'=IF({tid}="","",IF(@Score_Financeiro_Max@="","Não",IF(@Score_Financeiro_Max@>=prm_Limiar_Financeiro,"Sim","Não")))', desc="Sim se algum risco/oportunidade é material."),
        col("Classificacao", 20, f=(f'=IF({tid}="","",IF(AND(@Material_Impacto@="Sim",@Material_Financeiro@="Sim"),"Dupla materialidade",'
                                    'IF(@Material_Impacto@="Sim","Material — impacto",IF(@Material_Financeiro@="Sim","Material — financeira","Não material"))))'),
            desc="Resultado da dupla materialidade do tema."),
        col("Banda_Impacto", 8, "int", f=(f'=IF({tid}="","",IF(@Score_Impacto_Max@="",0,IF(@Score_Impacto_Max@>=prm_Limiar_Alto,4,'
                                          'IF(@Score_Impacto_Max@>=prm_Limiar_Impacto,3,IF(@Score_Impacto_Max@>=prm_Limiar_Baixo,2,1)))))'),
            desc="0 sem impactos · 1 baixa · 2 monitorizar · 3 material · 4 alta (eixo da matriz)."),
        col("Banda_Financeira", 8, "int", f=(f'=IF({tid}="","",IF(@Score_Financeiro_Max@="",0,IF(@Score_Financeiro_Max@>=prm_Limiar_Alto,4,'
                                             'IF(@Score_Financeiro_Max@>=prm_Limiar_Financeiro,3,IF(@Score_Financeiro_Max@>=prm_Limiar_Baixo,2,1)))))'),
            desc="0 sem riscos/oportunidades · 1 baixa · 2 monitorizar · 3 material · 4 alta."),
        col("Indice_Prioridade", 9, "num1", f=f'=IF({tid}="","",N(@Score_Impacto_Max@)+N(@Score_Financeiro_Max@))', desc="Impacto máx. + financeiro máx. (0–50), para ordenar."),
        col("Ranking", 7, "int", f=f'=IF({tid}="","",RANK(@Indice_Prioridade@,#Indice_Prioridade#,0)+COUNTIFS(#Indice_Prioridade#,@Indice_Prioridade@,#ID_Tema#,"<"&{tid}))', desc="Posição por prioridade (1 = mais prioritário)."),
        col("Exposicao_Risco_EUR", 12, "eur", f=f'=IF({tid}="","",-SUMIFS({IR("Efeito_Ponderado_EUR")},{IR("ID_Tema")},{tid},{IR("Tipo_IRO")},"Risco"))', desc="Soma dos efeitos ponderados dos riscos (€/ano, valor positivo)."),
        col("Potencial_Oportunidade_EUR", 12, "eur", f=f'=IF({tid}="","",SUMIFS({IR("Efeito_Ponderado_EUR")},{IR("ID_Tema")},{tid},{IR("Tipo_IRO")},"Oportunidade"))', desc="Soma dos efeitos ponderados das oportunidades (€/ano)."),
        col("Relevancia_Partes_Interessadas", 11, "num", f=f'=IF({tid}="","",IFERROR(ROUND(AVERAGEIFS({CR("Relevancia_Percebida")},{CR("ID_Tema")},{tid}),2),""))', desc="Média da relevância atribuída pelas partes interessadas (1–5)."),
        col("N_Contributos", 9, "int", f=f'=IF({tid}="","",COUNTIF({CR("ID_Tema")},{tid}))', desc="N.º de contributos das partes interessadas."),
        col("Cobertura_Evidencia", 10, "pct", f=(f'=IF(OR({tid}="",N(@N_IRO@)=0),"",(COUNTIFS({IR("ID_Tema")},{tid},{IR("Qualidade_Evidencia")},"Alta")'
                                                 f'+COUNTIFS({IR("ID_Tema")},{tid},{IR("Qualidade_Evidencia")},"Média"))/@N_IRO@)'),
            desc="Fração dos IRO com evidência de qualidade Alta ou Média."),
        col("Alerta_Consistencia", 26, f=(f'=IF({tid}="","",IF(AND(@Relevancia_Partes_Interessadas@<>"",N(@Relevancia_Partes_Interessadas@)>=prm_Relev_Alerta,@Classificacao@="Não material"),'
                                          '"Rever: relevância alta para as partes interessadas",IF(AND(@Classificacao@<>"Não material",@Cobertura_Evidencia@<>"",N(@Cobertura_Evidencia@)<0.5),'
                                          '"Material com evidência fraca","OK")))'),
            desc="Divergência entre partes interessadas e avaliação, ou tema material com evidência fraca."),
        col("Decisao_Gestao", 34, f=(f'=IF({tid}="","",IF(@Classificacao@="Não material","Monitorizar e reavaliar na próxima DMA",'
                                     '"Gerir: política, ações, meta e KPI; divulgar (VSME / ESRS voluntário)"))'),
            desc="Consequência de gestão da classificação."),
    ]
    assert [c["name"] for c in tcols] == tcols_names
    trows = [dict(ID_Tema=t[0], Pilar=t[1], ESRS_Topico=t[2], Subtopico_ESRS=t[3], Tema=t[4], Descricao=t[5], Referencia_GRI=t[6],
                  Relevancia_Setorial=t[7], Fonte_Identificacao=t[8], Dono=t[9], Justificacao_Avaliacao=t[10], Data_Avaliacao=D_AVAL)
             for t in TEMAS_DMA]
    cls_cf = {"Dupla": "red", "impacto": "orange", "financeira": "blue", "Não material": "green"}
    b.table("Temas", "tbl_dma_temas", tcols, trows, "Temas de sustentabilidade com a materialidade agregada a partir dos IRO (1 linha por tema).",
            title="TEMAS DE SUSTENTABILIDADE — MATERIALIDADE AGREGADA",
            subtitle="Um tema é material se pelo menos um IRO for material · Cabeçalho cinzento = calculado · Linhas vazias no fim = reserva para novos temas",
            cf=[("Classificacao", cls_cf), ("Material_Impacto", {"Sim": "red"}), ("Material_Financeiro", {"Sim": "red"}),
                ("Alerta_Consistencia", {"Rever": "orange", "fraca": "yellow", "OK": "green"})],
            row_height=48, freeze_col=2, extra_rows=T_EXTRA)

    # ---------------- IRO
    iid = "@ID_IRO@"
    icols = [
        col("ID_IRO", 8, desc="Identificador do impacto, risco ou oportunidade (IRO-nnn).", key="PK", dom="IRO-nnn"),
        col("ID_Tema", 8, desc="Tema a que o IRO pertence.", key="FK → tbl_dma_temas"),
        col("Tema", 26, f=f'=IF(@ID_Tema@="","",IFERROR(INDEX({TR("Tema")},MATCH(@ID_Tema@,{TR("ID_Tema")},0)),"ID_Tema não encontrado"))', desc="Automático (desnormalizado para análise)."),
        col("Pilar", 10, f=f'=IF(@ID_Tema@="","",IFERROR(INDEX({TR("Pilar")},MATCH(@ID_Tema@,{TR("ID_Tema")},0)),""))', desc="Automático."),
        col("ESRS_Topico", 22, f=f'=IF(@ID_Tema@="","",IFERROR(INDEX({TR("ESRS_Topico")},MATCH(@ID_Tema@,{TR("ID_Tema")},0)),""))', desc="Automático."),
        col("Tipo_IRO", 14, dv="TipoIRO", desc="Impacto negativo, Impacto positivo, Risco ou Oportunidade."),
        col("Dimensao", 10, f='=IF(@Tipo_IRO@="","",IF(LEFT(@Tipo_IRO@,7)="Impacto","Impacto","Financeira"))', desc="Impacto (de dentro para fora) ou Financeira (de fora para dentro)."),
        col("Descricao", 48, desc="Descrição do IRO: o quê, onde e com que efeito."),
        col("Natureza", 9, dv="Natureza", desc="Impactos: Real (já ocorre) ou Potencial.", req=False),
        col("Etapa_Cadeia_Valor", 20, dv="Etapa", desc="Onde ocorre na cadeia de valor (EFRAG IG 2)."),
        col("Horizonte", 16, dv="Horizonte", desc="Horizonte temporal (ESRS 1 §77)."),
        col("Afetados", 24, desc="Pessoas ou elementos do ambiente afetados.", req=False),
        col("Direitos_Humanos", 8, dv="SimNao", desc="Sim se afeta pessoas em direitos humanos (saúde, segurança, trabalho).", req=False),
        col("Magnitude", 7, "int", dv="Escala", desc="Impactos: magnitude 1–5 (tbl_dma_escalas).", req=False),
        col("Alcance", 7, "int", dv="Escala", desc="Impactos: alcance 1–5.", req=False),
        col("Irremediabilidade", 8, "int", dv="Escala", desc="Impactos negativos: irremediabilidade 1–5.", req=False),
        col("Probabilidade", 8, "int", dv="Escala", desc="Impactos potenciais: probabilidade 1–5 (reais = 5 automático).", req=False),
        col("Gravidade", 8, "num", f=('=IF(@Dimensao@<>"Impacto","",IF(@Tipo_IRO@="Impacto negativo",IF(COUNT(@Magnitude@,@Alcance@,@Irremediabilidade@)=3,'
                                      'ROUND(AVERAGE(@Magnitude@,@Alcance@,@Irremediabilidade@),2),""),IF(COUNT(@Magnitude@,@Alcance@)=2,ROUND(AVERAGE(@Magnitude@,@Alcance@),2),"")))'),
            desc="Média de Magnitude, Alcance e Irremediabilidade (negativos) ou de Magnitude e Alcance (positivos)."),
        col("Probabilidade_Efetiva", 9, "int", f=('=IF(OR(@Dimensao@<>"Impacto",@Gravidade@=""),"",IF(@Natureza@="Real",5,IF(AND(@Direitos_Humanos@="Sim",'
                                                  '@Gravidade@>=prm_Grav_DH),5,IF(@Probabilidade@="","",@Probabilidade@))))'),
            desc="5 se real; 5 se direitos humanos com gravidade ≥ prm_Grav_DH; senão a probabilidade."),
        col("Score_Impacto", 8, "num1", f='=IF(OR(@Gravidade@="",@Probabilidade_Efetiva@=""),"",ROUND(@Gravidade@*@Probabilidade_Efetiva@,1))', desc="Gravidade × Probabilidade efetiva (1–25)."),
        col("Mecanismo_Financeiro", 40, desc="Riscos/oportunidades: como o tema afeta receitas, custos, ativos ou financiamento, com os pressupostos da estimativa.", req=False),
        col("Rubrica_Financeira", 20, dv="Rubrica", desc="Rubrica financeira afetada.", req=False),
        col("Efeito_Financeiro_EUR_Ano", 12, "eur", desc="Estimativa do efeito financeiro se ocorrer (€/ano ou por evento).", req=False),
        col("Probabilidade_Financeira", 9, "int", dv="Escala", desc="Probabilidade 1–5 do efeito financeiro.", req=False),
        col("Magnitude_Financeira", 9, "int", f=('=IF(OR(@Dimensao@<>"Financeira",@Efeito_Financeiro_EUR_Ano@=""),"",MATCH(@Efeito_Financeiro_EUR_Ano@,esc_Fin_Limite,1))'),
            desc="Banda 1–5 do efeito em € (tbl_dma_escalas)."),
        col("Score_Financeiro", 8, "num1", f='=IF(OR(@Magnitude_Financeira@="",@Probabilidade_Financeira@=""),"",@Magnitude_Financeira@*@Probabilidade_Financeira@)', desc="Magnitude financeira × Probabilidade (1–25)."),
        col("Efeito_Ponderado_EUR", 12, "eur", f=('=IF(@Score_Financeiro@="","",ROUND(@Efeito_Financeiro_EUR_Ano@*INDEX(esc_Prob_Media,@Probabilidade_Financeira@),0)'
                                                  '*IF(@Tipo_IRO@="Risco",-1,1))'),
            desc="Efeito × probabilidade média (negativo nos riscos, positivo nas oportunidades)."),
        col("Score", 7, "num1", f='=IF(@Dimensao@="","",IF(@Dimensao@="Impacto",@Score_Impacto@,@Score_Financeiro@))', desc="Pontuação única do IRO na sua dimensão (1–25)."),
        col("Material", 8, f=('=IF(OR(@Dimensao@="",@Score@=""),"",IF(@Score@>=IF(@Dimensao@="Impacto",prm_Limiar_Impacto,prm_Limiar_Financeiro),"Sim","Não"))'),
            desc="Sim se o score atinge o limiar da sua dimensão."),
        col("Classificacao_IRO", 18, f='=IF(@Material@="","",IF(@Material@="Sim",IF(@Dimensao@="Impacto","Material — impacto","Material — financeiro"),"Não material"))', desc="Resultado do IRO."),
        col("Ranking_IRO", 7, "int", f=f'=IF(@Score@="","",RANK(@Score@,#Score#,0)+COUNTIFS(#Score#,@Score@,#ID_IRO#,"<"&{iid}))', desc="Posição por score (1 = maior)."),
        col("Evidencia_Resumo", 34, desc="Resumo das evidências (detalhe em tbl_dma_evidencias)."),
        col("Qualidade_Evidencia", 9, dv="Qualidade", desc="Alta (medida/verificada), Média (calculada/parcial) ou Baixa (estimativa ou lacuna)."),
        col("N_Evidencias", 8, "int", f=f'=IF({iid}="","",COUNTIF({ER("ID_IRO")},{iid}))', desc="N.º de evidências registadas."),
        col("Controlo_Qualidade", 20, f=(f'=IF({iid}="","",IF(@Dimensao@="","FALTA tipo de IRO",IF(@Score@="",IF(@Dimensao@="Impacto","FALTA pontuação de impacto",'
                                         '"FALTA estimativa financeira"),IF(@N_Evidencias@=0,"Sem evidência registada","OK"))))'),
            desc="Verificação de completude dos dados."),
        col("IDs_Contexto", 16, desc="Itens SWOT/PESTEL de origem (';').", key="FK → RG-SGA-01", req=False),
        col("ID_RO", 8, desc="Risco/oportunidade do SGA (coluna 'ID RO (SGA)' de tbRiscos/tbOportunidades).", key="FK → RG-SGA-02", req=False),
        col("ID_Registo_Corporativo", 10, desc="ID (R/O) da linha em tbRiscos / tbOportunidades do RG-SGA-02.", key="FK → RG-SGA-02", req=False),
        col("IDs_Aspetos", 18, desc="Aspetos ambientais relacionados (';').", key="FK → RG-SGA-03", req=False),
        col("ID_Legal", 12, desc="Requisitos legais relacionados (';').", key="FK → RG-SGA-04", req=False),
        col("ID_OBJ", 8, desc="Objetivo ambiental.", key="FK → RG-SGA-05", req=False),
        col("ID_KPI", 12, desc="Indicador(es) de desempenho (';').", key="FK → RG-SGA-05", req=False),
        col("ID_PAM", 14, desc="Ações do Plano de Ações de Melhoria (';').", key="FK → RG-SGA-06", req=False),
        col("Resposta_Gestao", 36, desc="Política, ação ou controlo de resposta.", req=False),
        col("Responsavel", 24, dv="Funcao", desc="Responsável pelo IRO."),
        col("Estado_Validacao", 16, dv="EstadoValidacao", desc="Rascunho → Validado pelo responsável → Aprovado pela Direção."),
        col("Data_Avaliacao", 11, "date", desc="Data da avaliação."),
        col("Proxima_Revisao", 11, "date", f='=IF(@Data_Avaliacao@="","",EDATE(@Data_Avaliacao@,IF(@Material@="Sim",prm_Meses_Rev_Material,prm_Meses_Rev_Outros)))', desc="Data da próxima revisão."),
        col("Notas", 30, desc="Notas e pressupostos.", req=False),
    ]
    assert [c["name"] for c in icols] == icols_names
    irows = [{k: v for k, v in r.items() if k != "key"} for r in IRO_ROWS]
    b.table("IRO", "tbl_dma_iro", icols, irows,
            "Impactos, riscos e oportunidades (IRO) — unidade de avaliação da dupla materialidade (1 linha por IRO).",
            title="IMPACTOS, RISCOS E OPORTUNIDADES (IRO) — AVALIAÇÃO DE DUPLA MATERIALIDADE",
            subtitle="Impacto: Gravidade × Probabilidade efetiva · Financeira: Magnitude (€) × Probabilidade · Material se ≥ limiar (folha Listas) · Cinzento = calculado",
            cf=[("Tipo_IRO", {"negativo": "orange", "positivo": "green", "Risco": "red", "Oportunidade": "blue"}),
                ("Material", {"Sim": "red", "Não": "green"}), ("Classificacao_IRO", {"Material": "red", "Não material": "green"}),
                ("Controlo_Qualidade", {"FALTA": "red", "Sem evidência": "orange", "OK": "green"}),
                ("Qualidade_Evidencia", {"Baixa": "orange", "Alta": "green"})],
            row_height=60, freeze_col=2, extra_rows=I_EXTRA)

    # ---------------- Evidências
    ev = list(EVID)
    com_ev = {e[0] for e in EVID}
    for r in IRO_ROWS:  # IRO sem evidência quantitativa: regista a evidência documental citada no próprio IRO
        if r["key"] not in com_ev:
            ev.append((r["key"], "Evidência documental / qualitativa", None, None, "2026", "Ver fontes citadas", None, "Qualitativo",
                       r["Qualidade_Evidencia"], r["Evidencia_Resumo"]))
    erows = [dict(ID_Evidencia=f"EVI-{k:03d}", ID_IRO=KEY[e[0]], Indicador=e[1], Valor=e[2], Unidade=e[3], Periodo=e[4], Registo_Fonte=e[5],
                  ID_Fonte=e[6], Tipo_Dado=e[7], Qualidade=e[8], Observacao=e[9]) for k, e in enumerate(ev, start=1)]
    ecols = [
        col("ID_Evidencia", 9, desc="Identificador da evidência (EVI-nnn).", key="PK"),
        col("ID_IRO", 9, desc="IRO suportado.", key="FK → tbl_dma_iro"),
        col("ID_Tema", 8, f=f'=IF(@ID_IRO@="","",IFERROR(INDEX({IR("ID_Tema")},MATCH(@ID_IRO@,{IR("ID_IRO")},0)),"ID_IRO não encontrado"))', desc="Automático."),
        col("Indicador", 40, desc="O que foi medido ou estimado."),
        col("Valor", 12, "num", desc="Valor numérico (frações em 0–1)."),
        col("Unidade", 14, desc="Unidade do valor."),
        col("Periodo", 14, desc="Período a que o valor se refere."),
        col("Registo_Fonte", 16, desc="Registo de origem (RG-SGA-nn, registo corporativo, datasets)."),
        col("ID_Fonte", 14, desc="ID no registo de origem (EMAS-*, KPI-*, AA-*...).", req=False),
        col("Tipo_Dado", 11, dv="TipoDado", desc="Medido, Calculado, Estimado ou Qualitativo."),
        col("Qualidade", 9, dv="Qualidade", desc="Qualidade da evidência."),
        col("Observacao", 40, desc="Pressupostos e notas.", req=False),
    ]
    assert [c["name"] for c in ecols] == ecols_names
    b.table("Evidencias", "tbl_dma_evidencias", ecols, erows,
            "Evidências quantitativas e qualitativas que sustentam cada IRO (instantâneo dos registos do SGA à data da avaliação).",
            title="EVIDÊNCIAS DA AVALIAÇÃO (rastreabilidade)",
            subtitle="Valores copiados dos registos do SGA em 24/09/2026 (fonte viva indicada em Registo_Fonte / ID_Fonte) · Frações em 0–1",
            cf=[("Qualidade", {"Baixa": "orange", "Alta": "green"}), ("Tipo_Dado", {"Estimado": "yellow"})], row_height=30, freeze_col=2, extra_rows=E_EXTRA)

    # ---------------- Consultas
    crows, k = [], 0
    for parte, (dia, met, npart, lst) in CONS.items():
        for tema, rel, tipo, com in lst:
            k += 1
            crows.append(dict(ID_Contributo=f"CON-{k:03d}", Data=dia, Parte_Interessada=parte, Metodo=met, N_Participantes=npart, ID_Tema=tema,
                              Relevancia_Percebida=rel, Tipo_Contributo=tipo, Comentario=com, Incorporado_na_Avaliacao="Sim"))
    ccols = [
        col("ID_Contributo", 9, desc="Identificador do contributo (CON-nnn).", key="PK"),
        col("Data", 11, "date", desc="Data da consulta."),
        col("Parte_Interessada", 24, dv="Parte", desc="Grupo de partes interessadas (tbPartesInteressadas do registo corporativo)."),
        col("Metodo", 14, dv="Metodo", desc="Método de envolvimento."),
        col("N_Participantes", 9, "int", desc="N.º de participantes."),
        col("ID_Tema", 8, desc="Tema comentado.", key="FK → tbl_dma_temas"),
        col("Tema", 26, f=f'=IF(@ID_Tema@="","",IFERROR(INDEX({TR("Tema")},MATCH(@ID_Tema@,{TR("ID_Tema")},0)),"ID_Tema não encontrado"))', desc="Automático."),
        col("Relevancia_Percebida", 9, "int", dv="Escala", desc="Relevância atribuída pela parte interessada (1–5)."),
        col("Tipo_Contributo", 16, dv="TipoContributo", desc="Opinião / perceção ou evidência objetiva (EFRAG IG 1)."),
        col("Comentario", 46, desc="Síntese do contributo."),
        col("Incorporado_na_Avaliacao", 10, dv="SimNao", desc="Se o contributo foi considerado na avaliação."),
    ]
    assert [c["name"] for c in ccols] == ccols_names
    b.table("Consultas", "tbl_dma_consultas", ccols, crows,
            "Contributos das partes interessadas por tema (1 linha por contributo; formato longo para análise).",
            title="ENVOLVIMENTO DAS PARTES INTERESSADAS",
            subtitle="Contributos simulados (fábrica fictícia) · A relevância informa a avaliação mas não entra na pontuação · Divergências geram alerta em Temas",
            cf=[("Tipo_Contributo", {"Evidência": "blue"})], row_height=30, freeze_col=1, extra_rows=C_EXTRA)

    build_painel(b, painel, TR, IR, nT)
    return b.save(out)


def build_painel(b, ws, TR, IR, nT):
    ws["A1"] = "PAINEL DE DUPLA MATERIALIDADE — PLASTICOM"
    ws["A1"].font = F_TITLE
    ws["A2"] = ("Escolha os filtros nas células amarelas (lista pendente). Indicadores, matriz, resumo e gráfico recalculam-se. "
                "A tabela dinâmica no fim tem segmentações de dados (Dados > Atualizar tudo após editar as tabelas).")
    ws["A2"].font = F_SUB
    widths = {"A": 30, "B": 14, "C": 14, "D": 16, "E": 16, "F": 16, "G": 20, "H": 18, "I": 16, "J": 30}
    for L, w in widths.items():
        ws.column_dimensions[L].width = w

    def band(r, text, ncol=10):
        ws.cell(row=r, column=1, value=text).font = F_BOLD
        for c in range(1, ncol + 1):
            ws.cell(row=r, column=c).fill = FILL_BAND

    def cellf(r, c, v, fmt=None, bold=False, fill=None, center=False):
        x = ws.cell(row=r, column=c, value=v)
        x.font = F_BOLD if bold else F_BASE
        x.border = BORDER
        x.alignment = CENTER if center else WRAP_TOP
        if fmt:
            x.number_format = fmt
        if fill:
            x.fill = PatternFill("solid", fgColor=fill)
        return x

    band(4, "FILTROS  ('(Todos)' = sem filtro · Pilar e Tópico aplicam-se a temas e IRO; Etapa, Horizonte e Tipo só aos IRO)")
    labels = ["Pilar", "Tópico ESRS", "Etapa da cadeia de valor", "Horizonte temporal", "Tipo de IRO"]
    lists = ["FPilar", "FTopico", "FEtapa", "FHorizonte", "FTipo"]
    for j, (lab, ls) in enumerate(zip(labels, lists)):
        c = ws.cell(row=5, column=1 + j, value=lab)
        c.font, c.fill, c.alignment, c.border = F_HEAD, FILL_HEAD, CENTER, BORDER
        sel = cellf(6, 1 + j, "(Todos)", bold=True, fill="FFF2B3", center=True)
        dv = DataValidation(type="list", formula1=f"=lst_{ls}", allow_blank=False)
        ws.add_data_validation(dv)
        dv.add(sel.coordinate)
        crit = ws.cell(row=7, column=1 + j, value=f'=IF({sel.coordinate}="(Todos)","*",{sel.coordinate})')
        crit.font = Font(name=FONT, size=8, color="808080")
    ws["F7"] = "← critérios usados nas fórmulas"
    ws["F7"].font = Font(name=FONT, size=8, italic=True, color="808080")
    fP, fE, fEt, fH, fT = "$A$7", "$B$7", "$C$7", "$D$7", "$E$7"
    tflt = f'{TR("Pilar")},{fP},{TR("ESRS_Topico")},{fE}'
    iflt = f'{IR("Pilar")},{fP},{IR("ESRS_Topico")},{fE},{IR("Etapa_Cadeia_Valor")},{fEt},{IR("Horizonte")},{fH},{IR("Tipo_IRO")},{fT}'

    band(9, "INDICADORES (com filtros)")
    kpis = [
        ("Temas avaliados", f"=COUNTIFS({tflt})", "0"),
        ("Dupla materialidade", f'=COUNTIFS({tflt},{TR("Classificacao")},"Dupla materialidade")', "0"),
        ("Material — impacto", f'=COUNTIFS({tflt},{TR("Classificacao")},"Material — impacto")', "0"),
        ("Material — financeira", f'=COUNTIFS({tflt},{TR("Classificacao")},"Material — financeira")', "0"),
        ("Não material", f'=COUNTIFS({tflt},{TR("Classificacao")},"Não material")', "0"),
        ("IRO avaliados", f"=COUNTIFS({iflt})", "0"),
        ("IRO materiais", f'=COUNTIFS({iflt},{IR("Material")},"Sim")', "0"),
        ("Efeito financeiro ponderado líquido (€/ano)", f'=SUMIFS({IR("Efeito_Ponderado_EUR")},{iflt})', "#,##0 €;-#,##0 €"),
        ("IRO com evidência de qualidade Alta", f'=IFERROR(COUNTIFS({iflt},{IR("Qualidade_Evidencia")},"Alta")/COUNTIFS({iflt}),0)', "0%"),
        ("IRO aprovados pela Direção", f'=IFERROR(COUNTIFS({iflt},{IR("Estado_Validacao")},"Aprovado pela Direção")/COUNTIFS({iflt}),0)', "0%"),
    ]
    for j, (lab, f, fmt) in enumerate(kpis):
        c = ws.cell(row=10, column=1 + j, value=lab)
        c.font, c.fill, c.alignment, c.border = F_HEAD, FILL_HEAD, CENTER, BORDER
        v = cellf(11, 1 + j, f, fmt=fmt, center=True)
        v.font = Font(name=FONT, size=13, bold=True, color=C_TITLE)
    ws.row_dimensions[10].height = 42
    ws.row_dimensions[11].height = 30

    band(13, "MATRIZ DE DUPLA MATERIALIDADE — n.º de temas por banda (filtros Pilar e Tópico)")
    bands_lbl = ['"Sem IRO"', '"Baixa (<"&prm_Limiar_Baixo&")"', '"Monitorizar ("&prm_Limiar_Baixo&"–<"&prm_Limiar_{d}&")"',
                 '"Material ("&prm_Limiar_{d}&"–<"&prm_Limiar_Alto&")"', '"Alta (≥"&prm_Limiar_Alto&")"']
    cellf(14, 1, "Impacto ↓  ·  Financeira →", bold=True, fill="DCEBEF", center=True)
    for j in range(5):
        c = cellf(14, 2 + j, "=" + bands_lbl[j].format(d="Financeiro"), bold=True, fill="DCEBEF", center=True)
    ws.row_dimensions[14].height = 30
    for i, bi in enumerate([4, 3, 2, 1, 0]):
        r = 15 + i
        cellf(r, 1, "=" + bands_lbl[bi].format(d="Impacto"), bold=True, fill="DCEBEF")
        for bj in range(5):
            if bi >= 3 and bj >= 3:
                fill = CF_COLORS["red"][0]
            elif bi >= 3 or bj >= 3:
                fill = CF_COLORS["orange"][0]
            elif bi == 2 or bj == 2:
                fill = CF_COLORS["yellow"][0]
            elif bi == 0 or bj == 0:
                fill = CF_COLORS["gray"][0]
            else:
                fill = CF_COLORS["green"][0]
            f = f'=COUNTIFS({TR("Banda_Impacto")},{bi},{TR("Banda_Financeira")},{bj},{tflt})'
            x = cellf(r, 2 + bj, f, fmt='0;-0;""', bold=True, fill=fill, center=True)
            x.font = Font(name=FONT, size=13, bold=True)
        ws.row_dimensions[r].height = 26
    ws["A19"].value = "Sem IRO de impacto"
    ws["G15"] = "Vermelho = dupla materialidade · laranja = material numa dimensão · amarelo = monitorizar · verde = baixa · cinzento = sem IRO nessa dimensão"
    ws["G15"].font = F_SUB
    ws["G15"].alignment = WRAP_TOP
    ws.merge_cells("G15:J17")

    band(21, "GRÁFICO — MATRIZ DE DUPLA MATERIALIDADE POR TEMA (dinâmico com os filtros Pilar e Tópico; rótulo = ID do tema)")
    RS = 49  # primeira linha do resumo (o gráfico ocupa as linhas 22–47)
    band(RS, "RESUMO POR TÓPICO ESRS")
    hdr = ["Tópico ESRS", "Temas", "Temas materiais", "Dupla materialidade", "Impacto máx.", "Financeiro máx.", "IRO",
           "Exposição a riscos (€/ano)", "Oportunidades (€/ano)", "Relevância média p/ partes interessadas"]
    for j, h in enumerate(hdr):
        c = ws.cell(row=RS + 1, column=1 + j, value=h)
        c.font, c.fill, c.alignment, c.border = F_HEAD, FILL_HEAD, CENTER, BORDER
    ws.row_dimensions[RS + 1].height = 42
    for k, tp in enumerate(ESRS):
        r = RS + 2 + k
        q = f'"{tp}"'
        cellf(r, 1, tp)
        cellf(r, 2, f'=COUNTIFS({TR("ESRS_Topico")},{q})', "0", center=True)
        cellf(r, 3, f'=COUNTIFS({TR("ESRS_Topico")},{q},{TR("Classificacao")},"<>Não material")', '0;-0;"—"', center=True)
        cellf(r, 4, f'=COUNTIFS({TR("ESRS_Topico")},{q},{TR("Classificacao")},"Dupla materialidade")', '0;-0;"—"', center=True)
        cellf(r, 5, f'=_xlfn.MAXIFS({TR("Score_Impacto_Max")},{TR("ESRS_Topico")},{q})', '0.0;-0.0;"—"', center=True)
        cellf(r, 6, f'=_xlfn.MAXIFS({TR("Score_Financeiro_Max")},{TR("ESRS_Topico")},{q})', '0.0;-0.0;"—"', center=True)
        cellf(r, 7, f'=SUMIFS({TR("N_IRO")},{TR("ESRS_Topico")},{q})', "0", center=True)
        cellf(r, 8, f'=SUMIFS({TR("Exposicao_Risco_EUR")},{TR("ESRS_Topico")},{q})', '#,##0 €;-#,##0 €;"—"', center=True)
        cellf(r, 9, f'=SUMIFS({TR("Potencial_Oportunidade_EUR")},{TR("ESRS_Topico")},{q})', '#,##0 €;-#,##0 €;"—"', center=True)
        cellf(r, 10, f'=IFERROR(AVERAGEIFS({TR("Relevancia_Partes_Interessadas")},{TR("ESRS_Topico")},{q}),"—")', "0.0", center=True)
    rT = RS + 2 + len(ESRS)
    cellf(rT, 1, "Total", bold=True)
    for j, L in enumerate("BCDGHI"):
        cellf(rT, "ABCDEFGHIJ".index(L) + 1, f"=SUM({L}{RS + 2}:{L}{rT - 1})", "#,##0 €" if L in "HI" else "0", bold=True, center=True)

    r0 = rT + 2
    band(r0, "TOP 15 TEMAS POR PRIORIDADE (impacto máx. + financeiro máx.; sem filtros)")
    hdr = ["Tema", "ID", "Tópico ESRS", "Pilar", "Impacto máx.", "Financeiro máx.", "Classificação", "Relevância p/ partes",
           "Exposição a riscos (€/ano)", "Alerta de consistência"]
    fields = ["Tema", "ID_Tema", "ESRS_Topico", "Pilar", "Score_Impacto_Max", "Score_Financeiro_Max", "Classificacao",
              "Relevancia_Partes_Interessadas", "Exposicao_Risco_EUR", "Alerta_Consistencia"]
    for j, h in enumerate(hdr):
        c = ws.cell(row=r0 + 1, column=1 + j, value=h)
        c.font, c.fill, c.alignment, c.border = F_HEAD, FILL_HEAD, CENTER, BORDER
    ws.row_dimensions[r0 + 1].height = 30
    for k in range(1, 16):
        r = r0 + 1 + k
        m = f'MATCH({k},{TR("Ranking")},0)'
        for j, fld in enumerate(fields):
            fmt = {"Score_Impacto_Max": "0.0", "Score_Financeiro_Max": "0.0", "Relevancia_Partes_Interessadas": "0.0",
                   "Exposicao_Risco_EUR": '#,##0 €;-#,##0 €;"—"'}.get(fld)
            cellf(r, 1 + j, f'=IFERROR(INDEX({TR(fld)},{m})&"","")' if fmt is None else f'=IFERROR(INDEX({TR(fld)},{m}),"")',
                  fmt, center=j > 0)
        ws.cell(row=r, column=1).value = f'=IFERROR({k}&". "&INDEX({TR("Tema")},{m}),"")'
    rng = f"G{r0 + 2}:G{r0 + 16}"
    for txt, colr in {"Dupla": "red", "impacto": "orange", "financeira": "blue", "Não material": "green"}.items():
        bg, fg = CF_COLORS[colr]
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("{txt}",G{r0 + 2}))'],
                                                       fill=PatternFill("solid", fgColor=bg), font=Font(name=FONT, color=fg, bold=True)))

    r1 = r0 + 18
    band(r1, "IRO MATERIAIS POR ETAPA DA CADEIA DE VALOR × HORIZONTE (filtros Pilar, Tópico e Tipo)")
    hdr = ["Etapa da cadeia de valor"] + HORIZ + ["IRO materiais", "IRO avaliados", "% materiais"]
    for j, h in enumerate(hdr):
        c = ws.cell(row=r1 + 1, column=1 + j, value=h)
        c.font, c.fill, c.alignment, c.border = F_HEAD, FILL_HEAD, CENTER, BORDER
    ws.row_dimensions[r1 + 1].height = 30
    base = f'{IR("Pilar")},{fP},{IR("ESRS_Topico")},{fE},{IR("Tipo_IRO")},{fT}'
    for k, et in enumerate(ETAPAS):
        r = r1 + 2 + k
        cellf(r, 1, et)
        for j, hz in enumerate(HORIZ):
            cellf(r, 2 + j, f'=COUNTIFS({base},{IR("Etapa_Cadeia_Valor")},$A{r},{IR("Horizonte")},"{hz}",{IR("Material")},"Sim")', '0;-0;"—"', center=True)
        cellf(r, 5, f"=SUM(B{r}:D{r})", "0", bold=True, center=True)
        cellf(r, 6, f'=COUNTIFS({base},{IR("Etapa_Cadeia_Valor")},$A{r})', "0", center=True)
        cellf(r, 7, f"=IFERROR(E{r}/F{r},0)", "0%", center=True)

    # ---------------- dados auxiliares do gráfico (dinâmicos com os filtros Pilar e Tópico)
    hx = 4
    aux = ["ID", "Financeira (x)", "Dupla materialidade", "Material — impacto", "Material — financeira", "Não material"]
    for j, h in enumerate(aux):
        c = ws.cell(row=hx, column=26 + j, value=h)
        c.font = Font(name=FONT, size=8, bold=True, color="808080")
    ws.cell(row=hx - 1, column=26, value="Dados auxiliares do gráfico (não editar)").font = Font(name=FONT, size=8, italic=True, color="808080")
    cls = ["Dupla materialidade", "Material — impacto", "Material — financeira", "Não material"]
    for k in range(1, nT + 1):
        r = hx + k
        idx = f"INDEX({TR('ID_Tema')},{k})"
        ok = (f'AND({idx}<>"",OR($A$6="(Todos)",INDEX({TR("Pilar")},{k})=$A$6),'
              f'OR($B$6="(Todos)",INDEX({TR("ESRS_Topico")},{k})=$B$6))')
        ws.cell(row=r, column=26, value=f'=IF({ok},{idx},"")')
        ws.cell(row=r, column=27, value=f'=IF({ok},N(INDEX({TR("Score_Financeiro_Max")},{k})),NA())')
        for j, cl in enumerate(cls):
            ws.cell(row=r, column=28 + j, value=f'=IF(AND({ok},INDEX({TR("Classificacao")},{k})="{cl}"),N(INDEX({TR("Score_Impacto_Max")},{k})),NA())')
        for j in range(6):
            ws.cell(row=r, column=26 + j).font = Font(name=FONT, size=8, color="808080")
    # linhas de limiar
    ly = hx + nT + 3
    ws.cell(row=ly - 1, column=26, value="Limiares").font = Font(name=FONT, size=8, bold=True, color="808080")
    ws.cell(row=ly, column=26, value="=prm_Limiar_Financeiro"); ws.cell(row=ly, column=27, value=0)
    ws.cell(row=ly + 1, column=26, value="=prm_Limiar_Financeiro"); ws.cell(row=ly + 1, column=27, value=25)
    ws.cell(row=ly + 2, column=26, value=0); ws.cell(row=ly + 2, column=27, value="=prm_Limiar_Impacto")
    ws.cell(row=ly + 3, column=26, value=25); ws.cell(row=ly + 3, column=27, value="=prm_Limiar_Impacto")
    for r in range(ly, ly + 4):
        for c in (26, 27):
            ws.cell(row=r, column=c).font = Font(name=FONT, size=8, color="808080")

    ch = ScatterChart()
    ch.title = "Matriz de dupla materialidade (temas)"
    ch.style = 13
    ch.x_axis.title = "Materialidade financeira (score máx. 0–25)"
    ch.y_axis.title = "Materialidade de impacto (score máx. 0–25)"
    for ax in (ch.x_axis, ch.y_axis):
        ax.scaling.min, ax.scaling.max, ax.majorUnit = 0, 25, 5
        ax.delete = False
    xref = Reference(ws, min_col=27, min_row=hx + 1, max_row=hx + nT)
    colors = ["C0392B", "E67E22", "2E75B6", "7F8C8D"]
    for j, cl in enumerate(cls):
        yref = Reference(ws, min_col=28 + j, min_row=hx, max_row=hx + nT)
        s = Series(yref, xref, title_from_data=True)
        s.marker.symbol = "circle"
        s.marker.size = 9
        s.marker.graphicalProperties.solidFill = colors[j]
        s.marker.graphicalProperties.line.solidFill = colors[j]
        s.graphicalProperties.line.noFill = True
        ch.series.append(s)
    for a, bb, t in ((ly, ly + 1, "Limiar financeiro"), (ly + 2, ly + 3, "Limiar de impacto")):
        s = Series(Reference(ws, min_col=27, min_row=a, max_row=bb), Reference(ws, min_col=26, min_row=a, max_row=bb), title=t)
        s.marker.symbol = "none"
        s.graphicalProperties.line.solidFill = "A0A0A0"
        s.graphicalProperties.line.dashStyle = "dash"
        s.graphicalProperties.line.width = 12700
        ch.series.append(s)
    ch.height, ch.width = 13.5, 24
    ch.legend.position = "r"
    ws.add_chart(ch, "A22")
    ws.column_dimensions["K"].width = 3

    rp = r1 + 2 + len(ETAPAS) + 2
    band(rp, "ANÁLISE DINÂMICA — tabela dinâmica de tbl_dma_iro com segmentações de dados (clique nos botões para filtrar)")
    ws["A" + str(rp + 1)] = "Criada no pós-processamento do Excel; se não aparecer, execute: python build_17_dupla_materialidade.py <ficheiro>."
    ws["A" + str(rp + 1)].font = F_SUB
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.orientation = "landscape"
    ws.freeze_panes = "A8"


def postprocess(path):
    """No Excel (COM): rótulos dos pontos do gráfico = ID do tema, tabela dinâmica e segmentações de dados."""
    import win32com.client as w32
    xl = w32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    wb = xl.Workbooks.Open(os.path.abspath(path))
    try:
        ws = wb.Worksheets("Painel")
        # linha de início da tabela dinâmica = 3 linhas abaixo da faixa "ANÁLISE DINÂMICA"
        r = 1
        while not str(ws.Cells(r, 1).Value or "").startswith("ANÁLISE DINÂMICA"):
            r += 1
        prow = r + 3
        # rótulos com o ID do tema
        n_aux = 0
        while ws.Cells(5 + n_aux, 26).HasFormula:
            n_aux += 1
        ch = ws.ChartObjects(1).Chart
        lab_rng = f"='Painel'!$Z$5:$Z${4 + n_aux}"
        for i in range(1, 5):
            s = ch.SeriesCollection(i)
            s.HasDataLabels = True
            dl = s.DataLabels()
            try:
                dl.Format.TextFrame2.TextRange.InsertChartField(7, lab_rng, 0)  # msoChartFieldRange
                dl.ShowRange = True
                dl.ShowValue = False
            except Exception:
                dl.ShowValue = False
            dl.Font.Size = 8
        # tabela dinâmica
        lo = wb.Worksheets("IRO").ListObjects("tbl_dma_iro")
        pc = wb.PivotCaches().Create(1, lo.Name, 6)
        pt = pc.CreatePivotTable(ws.Range(f"A{prow}"), "pvt_dma_iro", True, 6)
        pt.PivotFields("ESRS_Topico").Orientation = 1
        pt.PivotFields("Tema").Orientation = 1
        pt.PivotFields("Classificacao_IRO").Orientation = 2
        pt.AddDataField(pt.PivotFields("ID_IRO"), "N.º de IRO", -4112)
        df = pt.AddDataField(pt.PivotFields("Efeito_Ponderado_EUR"), "Efeito ponderado (€/ano)", -4157)
        df.NumberFormat = "0"  # formato neutro ao idioma do Excel
        for fld in ("ESRS_Topico", "Tema", "Classificacao_IRO"):  # exclui as linhas de reserva vazias da tabela
            for it in pt.PivotFields(fld).PivotItems():
                if it.Name in ("(blank)", "(em branco)", "(vazio)") or not str(it.Value or "").strip():
                    it.Visible = False
        pt.RowAxisLayout(1)  # tabular
        pt.PivotCache().RefreshOnFileOpen = True
        pt.TableStyle2 = "PivotStyleLight16"
        # segmentações
        left = ws.Range("L1").Left
        top = ws.Range(f"L{prow}").Top
        for k, (fld, cap) in enumerate((("Pilar", "Pilar"), ("Etapa_Cadeia_Valor", "Etapa da cadeia de valor"), ("Horizonte", "Horizonte"),
                                         ("Tipo_IRO", "Tipo de IRO"), ("Material", "Material"), ("Qualidade_Evidencia", "Qualidade da evidência"))):
            sc = wb.SlicerCaches.Add2(pt, fld)
            sc.CrossFilterType = 4  # esconde botões sem dados (ex.: '(em branco)')
            col_, row_ = k % 3, k // 3
            sl = sc.Slicers.Add(ws)
            sl.Name, sl.Caption = f"slc_{fld}", cap
            sl.Top, sl.Left, sl.Width, sl.Height = top + row_ * 175, left + col_ * 165, 155, 165
        wb.Worksheets("00_LEIA-ME").Activate()
        wb.Save()
    finally:
        wb.Close(False)
        xl.Quit()


if __name__ == "__main__":
    import sys
    import recalc
    p = build(sys.argv[1])
    recalc.recalc([p])
    postprocess(p)
    n, e = recalc.check(p)
    print(p, n, "fórmulas", len(e), "erros", e[:10])
