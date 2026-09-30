"""RG-SGE-05 — Indicadores de desempenho energético (IDE), linhas de base energéticas (LBE), normalização, objetivos,
metas energéticas e planos de ação.
ISO 50001:2018 6.2, 6.4, 6.5, 9.1.1 (IDE vs LBE) · ISO 50006:2023 (5 a 10 e anexos D–F).
O modelo da LBE é calculado no próprio Excel (LINEST) sobre os 12 meses de referência; a validade estatística segue os
critérios do 50001 Ready / EnPI Lite (LBNL) e da ASHRAE Guideline 14 — orientação, não requisito da ISO."""
import numpy as np
from openpyxl.chart import LineChart, BarChart, Reference
from sgelib import *
from dimse import *
import edata

LBE_ROWS = N_LBE          # 12 meses de referência
TOL_DOMINIO = 0.10        # tolerância do domínio de validade do modelo (±10% fora do intervalo de referência)

# catálogo de IDE e KPI do SGE. Mesmas colunas do RG-SGA-05 tbl_kpi (Tipo_ISO14031 → Tipo_IDE_ISO50006); colunas só do SGE no fim.
# (ID, nome, fórmula, unidade, polaridade, tipo ISO 50006, frequência, fonte, responsável, ID_OBJ, ID_MED, fronteira, USE, variáveis relevantes,
#  fatores estáticos, normalização, ID_LBE, utilizadores (ISO 50006 tab. 1), coluna em tbl_ide_mensal, meta, ligação ao SGA/SGQ, qualidade dos dados)
KPIS = [
    ("IDE-01", "Melhoria do desempenho energético da instalação (consumo normalizado)", "(kWh esperado pelo modelo da LBE − kWh real ajustado) ÷ kWh esperado",
     "%", "Maior", "Modelo estatístico (regressão linear múltipla)", "Mensal", "RG-SGA-13 (fatura) + dataset de produção + IPMA", GE, "OBJ-E-01", "DAD-01; DAD-02; DAD-06",
     "Instalação da Unidade 1 sem as 4 máquinas novas de 07/2026 (ajuste não rotineiro ALE-01)", "Todos", "Unidades INJ+SOP (mil); graus-dia de arrefecimento base 15 °C",
     "N.º de máquinas; turnos 3×8 em 5 dias; mix de produto; área; tipo de energia", "Sim — modelo da LBE aplicado às condições do mês (ISO 50006 §8)", "LBE-01",
     "Gestão de topo; equipa de gestão de energia; auditores do SGE; certificação ISO 50003", "—", 0.05, "SGA OBJ-01 (mesma intenção; SGE mede normalizado)", "Medido (fatura) + variáveis medidas"),
    ("IDE-02", "Consumo específico de eletricidade da instalação (SEC)", "kWh total ÷ unidades INJ + SOP × 1 000", "kWh/1.000 un", "Menor", "Rácio de valores medidos",
     "Mensal", "RG-SGA-13 + dataset", GMAN, "OBJ-E-01", "DAD-01; DAD-02", "Instalação completa", "Todos", "— (rácio simples; não corrige a carga de base nem o clima)",
     "Idem IDE-01", "Não — rácio; a comparação exige cautela (Kent: o SEC mensal engana quando a produção varia)", "LBE-02",
     "Relato externo (SGA KPI-01, ESRS E1-5, EMAS); SGCIE (consumo específico)", "SEC_Real", 101.0, "SGA KPI-01 (mesmo cálculo)", "Medido"),
    ("IDE-03", "Consumo específico do sopro (ISBM)", "kWh do sopro ÷ frascos × 1 000", "kWh/1.000 frascos", "Menor", "Rácio (numerador estimado)", "Mensal",
     "RG-SGA-13 (rateio por horas) + dataset; analisador QGBT-SOP a partir de 12/2026", GPROD, "OBJ-E-01", "DAD-03", "Máquinas ISBM-001 a 010", "SOP",
     "Frascos produzidos; horas de marcha", "Tecnologia das máquinas; massa média do frasco", "Não (até haver submedição)", "LBE-03", "Produção; engenharia de processo", "SEC_SOP", None, "—", "Estimado (rateio)"),
    ("IDE-04", "Consumo específico da injeção", "kWh da injeção ÷ tampas e potes × 1 000", "kWh/1.000 un", "Menor", "Rácio (numerador estimado)", "Mensal",
     "RG-SGA-13 (rateio por horas) + dataset; analisador QGBT-INJ a partir de 12/2026", GPROD, "OBJ-E-01", "DAD-03", "Máquinas IM-001 a 008", "INJ",
     "Peças produzidas; horas de marcha", "Tecnologia das máquinas; mix tampas/potes", "Não (até haver submedição)", "LBE-04", "Produção; engenharia de processo", "SEC_INJ", None, "—", "Estimado (rateio)"),
    ("IDE-05", "Carga de base (energia não associada à produção)", "Coeficiente independente do modelo da LBE ÷ kWh real do mês", "%", "Menor", "Modelo estatístico (termo independente)", "Mensal",
     "Modelo LBE-01", GE, "OBJ-E-03", "DAD-01", "Instalação", "Todos", "—", "Idem IDE-01", "Derivado do modelo", "LBE-01", "Gestão; operação e manutenção",
     "Carga_Base_Pct", 0.14, "—", "Calculado"),
    ("IDE-06", "Rácio de arrefecimento (frio ÷ energia de injeção + sopro)", "kWh chiller/torre ÷ (kWh INJ + kWh SOP)", "fração", "Menor", "Rácio (estimado)", "Mensal",
     "RG-SGA-13 (rateio com fator de temperatura)", TUTL, "OBJ-E-04", "DAD-04", "Sistema de arrefecimento CH-01/TR-01", "UTL-FRIO", "Temperatura exterior; carga térmica",
     "Setpoint da água gelada; n.º de moldes", "Não — rácio sazonal: comparar o mesmo mês do ano ou normalizar por graus-dia (ISO 50006 §8); o reporte mar–ago contra a média anual penaliza o IDE", "LBE-05", "Utilidades; manutenção", "Racio_Frio", 0.095, "—", "Estimado"),
    ("IDE-07", "Rácio de ar comprimido (ar ÷ energia dos processos)", "kWh ar comprimido ÷ kWh (INJ+SOP+SER+HFS)", "fração", "Menor", "Rácio (estimado — fator fixo)", "Mensal",
     "RG-SGA-13 (AR_FRAC = 0,19 fixo)", TUTL, "OBJ-E-02", "DAD-05", "Central de ar comprimido", "UTL-AR", "—", "—",
     "Não — o valor é constante por construção: NÃO serve para demonstrar melhoria (substituído pelo IDE-08)", "—", "Utilidades", "Racio_Ar", None, "—", "Estimado (fator fixo)"),
    ("IDE-08", "Potência específica da central de ar comprimido", "kWh dos compressores ÷ Nm³ de ar produzido (semana de medição)", "kWh/Nm³", "Menor", "Rácio de valores medidos (fronteira de medida)",
     "Mensal a partir de 12/2026; antes, campanhas", "RG-SGE-11 tbl_ar_mv (PA-01 + caudalímetro EQP-04)", TUTL, "OBJ-E-02", "DAD-05", "Compressores CMP-01/02 + secadores", "UTL-AR",
     "Nm³ produzidos; pressão", "Pressão de serviço; n.º de compressores", "Sim — mesma semana-tipo com produção (ISO 50015 / IPMVP opção B)", "LBE-06",
     "Utilidades; engenheiros (M&V)", "—", 0.105, "SGA-10 OT-2026-02 (instalação dos VSD)", "Medido (campanha)"),
    ("IDE-09", "Consumo de energia final (eletricidade + gasóleo)", "kWh elétricos + L gasóleo × 10 kWh/L", "MWh", "Menor", "Valor de energia medido", "Mensal",
     "RG-SGA-13 + RG-SGA-19 (gasóleo)", GE, "OBJ-E-05", "DAD-01; DAD-07", "Instalação + frota", "Todos", "—", "—", "Não (valor absoluto)", "LBE-07",
     "SGCIE; ESRS E1-5; EMAS; gestão de topo", "Energia_Final_MWh", None, "SGA ESG-E01; EMAS-01", "Medido"),
    ("IDE-10", "Quota de eletricidade renovável (garantias de origem + autoconsumo)", "kWh renováveis ÷ kWh totais", "%", "Maior", "Rácio de valores medidos", "Anual",
     "Rótulo de energia do comercializador; UPAC (2027)", DFIN, "OBJ-E-05", "DAD-08", "Instalação", "Todos", "—", "—", "Não", "LBE-08", "Gestão de topo; clientes; ESG",
     "—", 0.80, "SGA KPI-09; MET-03", "Medido"),
    ("KPI-E-01", "Consumo de eletricidade medido por submedição (não estimado)", "kWh medidos por analisador fixo ÷ kWh totais", "%", "Maior", "KPI do sistema (não é IDE)", "Mensal",
     "RG-SGE-06 tbl_contadores", GE, "OBJ-E-06", "DAD-01", "Instalação", "—", "—", "—", "—", "—", "Equipa de gestão de energia", "—", 0.90, "SGA R35 / PAM-26-02", "Medido"),
    ("KPI-E-02", "Desvios significativos investigados em ≤ 30 dias", "Desvios investigados no prazo ÷ desvios detetados", "%", "Maior", "KPI do sistema (não é IDE)", "Mensal",
     "RG-SGE-11 tbl_desvios", GE, "OBJ-E-06", "—", "—", "—", "—", "—", "—", "—", "Equipa de gestão de energia", "—", 1.0, "—", "Registo"),
    ("KPI-E-03", "Ações dos planos de ação energéticos no prazo", "Ações no prazo ÷ ações com prazo vencido ou concluídas", "%", "Maior", "KPI do sistema (não é IDE)", "Mensal",
     "RG-SGE-05 tbl_planos_acao", GE, "OBJ-E-06", "—", "—", "—", "—", "—", "—", "—", "Gestão de topo", "—", 0.85, "—", "Registo"),
]

# objetivos energéticos e SGE (6.2.1/6.2.2). Mesmas colunas do RG-SGA-05 tbl_objetivos (ordem e nomes).
# (ID, política, origem tipo, origem IDs, origem descrição, declaração, KPI, meta tipo, meta valor (texto), meta numérica, prazo, RH, materiais, €,
#  responsável, planos, considera USE (6.2.2 d), oportunidade (6.2.2 e), requisitos (6.2.2 c), comunicado, ligação SGA)
OBJETIVOS = [
    ("OBJ-E-01", "POL-E-01", "Revisão energética", "USE-01; USE-02; USE-03; OPE-01; OPE-03; OPE-05; OPE-06", "Injeção, sopro e ar comprimido somam 81% da eletricidade; melhoria só demonstrada após as ações de out–dez/2026.",
     "Melhorar em 5% o desempenho energético normalizado da instalação (IDE-01) até 31/12/2027, face à LBE-01 (mar/2025–fev/2026).", "IDE-01", "Relativa", "+5% vs LBE-01",
     0.05, "2027-12-31", "Equipa de gestão de energia (6 pessoas, 10% do tempo)", "Analisadores (PAM-26-02), detetor de fugas", 185000, GE, "PA-E-01; PA-E-02; PA-E-03; PA-E-04",
     "USE-01, USE-02, USE-03", "OPE-01 a OPE-07", "LEG-08 SGCIE (−6% CEE até 2030); ISO 50003 (melhoria demonstrada)", "Quadro de energia + reunião mensal de desempenho", "OBJ-01 (−8% kWh/1.000 un até 12/2027)"),
    ("OBJ-E-02", "POL-E-02", "Revisão energética", "USE-03; OPE-01; OPE-02; OPE-04", "Ar comprimido com fugas ≈ 25% e pressão de 7,4 bar; compressores VSD desde 02/2026.",
     "Reduzir a potência específica da central de ar comprimido para ≤ 0,105 kWh/Nm³ e as fugas para ≤ 10% até 30/06/2027.", "IDE-08", "Absoluta", "≤ 0,105 kWh/Nm³",
     0.105, "2027-06-30", "Técnico de Utilidades + manutenção (2 h/semana)", "Detetor ultrassónico EQP-05; etiquetas de fugas", 18000, TUTL, "PA-E-02; PA-E-05",
     "USE-03", "OPE-01; OPE-02; OPE-04", "—", "Ronda de fugas mensal + quadro da manutenção", "SGA KZ-04; PAM-26-01"),
    ("OBJ-E-03", "POL-E-01", "Revisão energética", "OPE-03; KZ-01", "Máquinas em espera aquecida nas pausas e paragens; carga de base 16% do consumo.",
     "Reduzir a carga de base (IDE-05) para ≤ 14% até 31/03/2027 com o modo standby nas pausas e paragens > 30 min.", "IDE-05", "Absoluta", "≤ 14%",
     0.14, "2027-03-31", "Chefes de turno; operadores", "Etiquetas e checklist de pausa", 0, GPROD, "PA-E-03",
     "USE-01; USE-02", "OPE-03", "—", "Formação no posto + checklist do chefe de turno", "SGA PAM-26-06 (KZ-01)"),
    ("OBJ-E-04", "POL-E-01", "Revisão energética", "USE-04; OPE-08; OPE-09", "Chiller com setpoint de 7 °C e sem free-cooling; verões mais quentes (PES-08).",
     "Reduzir o rácio de arrefecimento (IDE-06) para ≤ 0,095 até 31/12/2027 (setpoint 10–12 °C e free-cooling).", "IDE-06", "Absoluta", "≤ 0,095",
     0.095, "2027-12-31", "Técnico de Utilidades; engenharia de processo", "Permutador de free-cooling", 42000, TUTL, "PA-E-06",
     "USE-04", "OPE-08; OPE-09", "Reg. (UE) 2024/573 (gases fluorados — manutenção do chiller)", "Quadro das utilidades", "SGA OBJ-05 (água do arrefecimento)"),
    ("OBJ-E-05", "POL-E-03", "Contexto / partes interessadas", "PES-01; O15; ALT-2026-07", "Clientes e PL-SGA-01 pedem eletricidade renovável; UPAC ≈ 1 MWp aprovada para estudo.",
     "Atingir ≥ 80% de eletricidade renovável (garantias de origem + autoconsumo) em 2028.", "IDE-10", "Absoluta", "≥ 80%",
     0.80, "2028-12-31", "Diretor Financeiro; Gestor(a) de Energia", "UPAC ≈ 1 MWp", 850000, DFIN, "PA-E-07",
     "—", "OPE-12", "DL 15/2022 alterado pelo DL 130/2026 (autoconsumo)", "Relatório de sustentabilidade; site", "SGA MET-03; PL-SGA-01"),
    ("OBJ-E-06", "POL-E-04", "Requisito do SGE", "R35; ALE-03", "Consumos por uso são estimados (rateio); sem submedição não há IDE por USE nem prova de melhoria (ISO 50003).",
     "Medir por analisador fixo ≥ 90% da eletricidade (KPI-E-01) até 31/03/2027 e investigar 100% dos desvios significativos em ≤ 30 dias.", "KPI-E-01", "Absoluta", "≥ 90%",
     0.90, "2027-03-31", "Gerente de Dados / TI; instalador", "6 analisadores + integração no BI", 38000, TI_, "PA-E-01",
     "Todos", "—", "ISO 50001 6.6 (exatidão e repetibilidade); ISO 50003", "Reunião da equipa de gestão de energia", "SGA R35; PAM-26-02; RG-26-D03"),
]

# metas energéticas (6.2.1 — "a organização deve estabelecer metas energéticas"): (ID, objetivo, KPI, descrição, meta, prazo)
METAS = [
    ("MET-E-01", "OBJ-E-01", "IDE-01", "Melhoria normalizada da instalação — etapa 2026", 0.02, "2026-12-31"),
    ("MET-E-02", "OBJ-E-01", "IDE-01", "Melhoria normalizada da instalação — meta 2027", 0.05, "2027-12-31"),
    ("MET-E-03", "OBJ-E-01", "IDE-02", "SEC da instalação (alinhado com SGA OBJ-01: −8%)", 101.0, "2027-12-31"),
    ("MET-E-04", "OBJ-E-02", "IDE-08", "Potência específica do ar comprimido", 0.105, "2027-06-30"),
    ("MET-E-05", "OBJ-E-03", "IDE-05", "Carga de base", 0.14, "2027-03-31"),
    ("MET-E-06", "OBJ-E-04", "IDE-06", "Rácio de arrefecimento", 0.095, "2027-12-31"),
    ("MET-E-07", "OBJ-E-05", "IDE-10", "Eletricidade renovável", 0.80, "2028-12-31"),
    ("MET-E-08", "OBJ-E-06", "KPI-E-01", "Eletricidade medida por submedição", 0.90, "2027-03-31"),
]

# planos de ação (6.2.3): (ID, objetivo, o que fazer, recursos, custo €, responsável, início, prazo, como avaliar, método de verificação (9.1),
#  poupança prevista MWh/ano, estado, integração no negócio, PAM do SGA, oportunidade)
PLANOS = [
    ("PA-E-01", "OBJ-E-06", "Instalar 6 analisadores de energia (QGBT-INJ, QGBT-SOP, QGBT-DEC, Q-AR, Q-FRIO, Q-SERV) e ligar ao BI; rever a LBE por USE com 12 meses medidos.",
     "Analisadores classe 0,5S, TI de medida, integração BI", 38000, TI_, "2026-10-01", "2026-12-15", "Cobertura medida ≥ 90% (KPI-E-01) e reconciliação mensal com a fatura (±2%)",
     "Reconciliação Σ analisadores vs contador geral EQP-01", 0, "Concluído", "Orçamento CAPEX 2026 (RG-26-D03)", "PAM-26-02", "—"),
    ("PA-E-02", "OBJ-E-02", "Campanha de fugas com ultrassom (mensal), reparação em ≤ 5 dias, teste de vazio ao domingo e redução da pressão para 6,8 bar.",
     "Detetor EQP-05; 2 h/semana do Técnico de Utilidades; peças", 6000, TUTL, "2026-10-01", "2027-06-30", "Fugas ≤ 10% no teste de vazio; IDE-08 ≤ 0,105 kWh/Nm³",
     "IPMVP opção B na fronteira da central (PA-01 + EQP-04), semana-tipo", 145, "Em curso", "Plano de manutenção preventiva (SAP PM)", "—", "OPE-01; OPE-02"),
    ("PA-E-03", "OBJ-E-03", "Modo standby nas pausas do 3.º turno e nas paragens > 30 min (resistências a 60%, bomba desligada); checklist do chefe de turno.",
     "Formação no posto (30 min/operador); etiquetas", 0, GPROD, "2026-10-05", "2026-12-31", "IDE-05 ≤ 14%; poupança medida por analisador no QGBT-INJ/SOP",
     "IPMVP opção A (kW medido em espera × horas registadas) até haver analisadores", 190, "Concluído", "Standard work do turno (SQDC)", "PAM-26-06", "OPE-03"),
    ("PA-E-04", "OBJ-E-01", "Servo-bomba nas injetoras hidráulicas IM-002 e IM-004 e isolamento térmico dos canhões de todas as injetoras.",
     "Retrofit servo (2 × €28 000); mantas (8 × €900)", 63200, GMAN, "2027-01-15", "2027-06-30", "SEC por máquina (analisador) −30% nas IM-002/004",
     "IPMVP opção B por máquina (analisador portátil antes/depois, mesmo molde)", 210, "Planeado", "Plano de investimento 2027", "—", "OPE-05; OPE-06"),
    ("PA-E-05", "OBJ-E-02", "Recuperação de calor dos compressores para pré-aquecimento de águas sanitárias e AVAC dos balneários.",
     "Permutador e tubagem", 14000, TUTL, "2027-03-01", "2027-09-30", "kWh térmicos recuperados (contador de energia térmica)",
     "Medição direta (contador de entalpia) — ISO 50015", 60, "Planeado", "Plano de investimento 2027", "—", "OPE-13"),
    ("PA-E-06", "OBJ-E-04", "Subir o setpoint da água gelada de 7 °C para 11 °C (validado com a qualidade dos moldes) e instalar free-cooling na torre.",
     "Ensaio DOE com a engenharia de processo; permutador", 42000, TUTL, "2026-11-01", "2027-10-31", "IDE-06 ≤ 0,095 normalizado pela temperatura",
     "IPMVP opção B (analisador Q-FRIO) com ajuste por graus-dia", 120, "Em curso", "Validação de processo (RG-SGQ-13)", "—", "OPE-08; OPE-09"),
    ("PA-E-07", "OBJ-E-05", "UPAC ≈ 1 MWp na cobertura (≈ 1 400 MWh/ano) e contrato de garantias de origem para o restante.",
     "EPC fotovoltaico; licenciamento DGEG", 850000, DFIN, "2027-01-01", "2027-12-31", "IDE-10 ≥ 80% em 2028; produção UPAC medida",
     "Contador da UPAC + rótulo de energia (não é poupança: substitui a origem)", 0, "Em estudo", "Plano de transição climática PL-SGA-01", "—", "OPE-12"),
]

# alterações às LBE e fatores estáticos (6.5 — reter a informação das modificações)
ALT_LBE = [
    ("ALE-01", "2026-07-01", "Fator estático", "Entrada em produção de 4 máquinas novas (IM-007, IM-008, ISBM-009, ISBM-010) — ALT-2026-03 (linhas alimentar e farmacêutica).",
     "LBE-01", "Ajuste não rotineiro (ISO 50006 §9.2): a energia atribuível às máquinas novas (horas × kW do RG-SGA-13 + quota de ar e frio) é retirada do real e as suas unidades das variáveis; fronteira do IDE-01 = instalação existente.",
     "Criar LBE-01b com 12 meses após a estabilização (07/2027) incluindo as máquinas novas.", "Aprovado", GE, "2026-09-15"),
    ("ALE-02", "2026-02-01", "Ação de melhoria (não é fator estático)", "Substituição dos compressores CMP-01/02 por unidades de velocidade variável (ALT-2026-01).",
     "LBE-01; LBE-06", "Sem ajuste: é uma melhoria a demonstrar. A LBE-01 termina em fev/2026 para que o reporte (mar–dez/2026) inclua o efeito dos VSD.",
     "—", "Aprovado", GE, "2026-09-15"),
    ("ALE-03", "2026-12-15", "Método de medição", "Início da submedição por 6 analisadores (PA-E-01, em serviço desde 15/12/2026): os consumos por USE deixam de ser rateio.",
     "LBE-03; LBE-04; LBE-05", "Revisão da LBE decidida (6.5 a): os IDE por USE estimados deixam de representar o desempenho; LBE atuais mantidas até haver 12 meses medidos.",
     "Nova LBE por USE com 12 meses medidos (01–12/2027).", "Aprovado", GE, "2026-12-18"),
    ("ALE-04", "2027-06-30", "Tipo de energia", "Entrada em serviço da UPAC ≈ 1 MWp (ALT-2026-07).",
     "LBE-07; LBE-08", "Sem ajuste ao IDE-01 (mede consumo, não a origem); o IDE-10 passa a incluir autoconsumo.", "—", "Planeado", DFIN, None),
]

FATORES_ESTATICOS = [
    ("FEST-01", "N.º de máquinas produtivas", "18 (8 ISBM, 6 IM, 2 SS, 2 HF)", "22 desde 07/2026", "Alterado", "ALE-01"),
    ("FEST-02", "Regime de trabalho", "3 turnos × 8 h, 5 dias/semana; fins de semana só em picos", "Igual", "Sem alteração", "—"),
    ("FEST-03", "Mix de produto (famílias)", "Cosmética + alimentar (frascos, tampas)", "Acrescentados potes e tampas alimentar/farma (17 SKU)", "Alterado", "ALE-01"),
    ("FEST-04", "Área e edifícios", "Terreno 45 000 m², naves de produção e armazéns", "Igual", "Sem alteração", "—"),
    ("FEST-05", "Tipos de energia", "Eletricidade da rede; gasóleo (frota, gerador)", "Igual (UPAC prevista 2027)", "Sem alteração", "ALE-04"),
    ("FEST-06", "Central de ar comprimido", "2 compressores de velocidade fixa (carga/vazio)", "2 compressores VSD desde 02/2026", "Alteração = ação de melhoria", "ALE-02"),
    ("FEST-07", "Setpoint da água gelada", "7 °C", "Igual", "Sem alteração", "—"),
]


def model_np(b):
    """Mesmo modelo que o Excel calcula (para textos e para os registos que usam o valor à data de referência)."""
    y = (b["kWh_Total"] - b["kWh_Maquinas_Novas"]).to_numpy(float)
    x1 = ((b["Unid_INJ"] + b["Unid_SOP"] - b["Unid_Maquinas_Novas"]) / 1000).to_numpy(float)
    x2 = b["CDD_15"].to_numpy(float)
    X = np.column_stack([np.ones(len(b)), x1, x2])
    co, *_ = np.linalg.lstsq(X[:LBE_ROWS], y[:LBE_ROWS], rcond=None)
    return co, y, X @ co


def build(out):
    b = Book("RG-SGE-05", "IDE, Linhas de Base Energéticas, Normalização, Objetivos, Metas e Planos de Ação",
             activities="Definir os indicadores de desempenho energético e as linhas de base; normalizar pelas variáveis relevantes; comparar os IDE com as LBE todos os meses; "
                        "demonstrar (ou não) a melhoria do desempenho energético; estabelecer objetivos, metas energéticas e planos de ação.",
             clauses="6.2.1 objetivos e metas energéticas; 6.2.2 a)–h) (reter); 6.2.3 planos de ação (o quê, recursos, quem, quando, como avaliar, método de verificação — reter); "
                     "6.4 IDE (metodologia mantida; valores retidos; considerar variáveis relevantes); 6.5 LBE (normalização; revisão nos casos a)–c); reter LBE, variáveis e modificações); "
                     "9.1.1 (melhoria avaliada comparando IDE com LBE); 5.1 l) (IDE representam o desempenho); 10.2 (demonstrar melhoria contínua do desempenho energético).",
             purpose=f"Base mensal de energia {PER_INI[:7]} a {PER_FIM[:7]} (fonte única RG-SGA-13) com as variáveis relevantes; modelo estatístico da LBE-01 calculado por LINEST "
                     f"sobre {LBE_INI[:7]}–{LBE_FIM[:7]} com testes de validade; IDE mensais por fórmula (esperado, diferença, CUSUM, domínio de validade); catálogo de IDE; "
                     "registo das LBE e das suas alterações; fatores estáticos; objetivos, metas energéticas e planos de ação ligados aos IDE.",
             links=[("RG-SGA-13", "Fonte única da eletricidade mensal por uso (tbl_dados_ambientais) — alterar lá, não aqui."),
                    ("RG-SGA-05", "OBJ-01 e KPI-01 (SEC) — o SGE mede o mesmo desempenho normalizado (IDE-01) e em rácio (IDE-02)."),
                    ("RG-SGE-04", "USE e oportunidades (OPE-xx) que originam os objetivos e planos."),
                    ("RG-SGE-06", "Plano de recolha de dados (DAD-xx) que alimenta os IDE."),
                    ("RG-SGE-11", "Desvios significativos (9.1.1) e M&V das poupanças por ação (ISO 50015 / IPMVP)."),
                    ("RG-SGE-02", "Compromissos da política energética (POL-E-xx) a que os objetivos dão corpo.")],
             guidance=[("ISO 50006:2023 §5.2–5.3 e tabela 1", "Utilizadores e fronteira de cada IDE (colunas Utilizadores e Fronteira do tbl_kpi)."),
                       ("ISO 50006:2023 §6.2 (tipos de IDE)", "Valor medido (IDE-09), rácio (IDE-02 a 04, 06 a 08, 10) e modelo estatístico (IDE-01, IDE-05)."),
                       ("ISO 50006:2023 §7.2 (período de referência)", "12 meses (mar/2025–fev/2026) para cobrir o ciclo completo da temperatura; termina antes dos compressores VSD."),
                       ("ISO 50006:2023 §8 e anexos D–F (normalização)", "Energia esperada = modelo da LBE aplicado às variáveis do mês; comparação sob condições equivalentes."),
                       ("ISO 50006:2023 §9.2 (fatores estáticos)", "Ajuste não rotineiro ALE-01 (4 máquinas novas em 07/2026) e tbl_fatores_estaticos."),
                       ("ISO 50006:2023 §10.3 (demonstrar melhoria)", "Soma do período de reporte dentro do domínio, comparada com a incerteza do modelo."),
                       ("LBNL — EnPI Lite 'Valid model requirements' / 50001 Ready M&V Protocol", "R² ≥ 0,5; p < 0,2 em todas as variáveis e < 0,1 em pelo menos uma; teste F com p < 0,1 (folha LBE_Modelo)."),
                       ("ASHRAE Guideline 14 (dados mensais)", "CV(RMSE) ≤ 15% e NMBE ±5%; R² recomendado > 0,75; incerteza da poupança a 95%."),
                       ("EVO — IPMVP Core Concepts (opções A–D)", "Método de verificação de cada plano de ação (6.2.3) e ajustes não rotineiros."),
                       ("Kent, R. — Energy Management in Plastics Processing (BPF/Tangram)", "'Impressão digital' energética: carga de base (IDE-05, típico 20–40%) + consumo proporcional à produção; o SEC mensal engana quando a produção varia.")],
             legal=[("DL 71/2008 (SGCIE) — LEG-08", "Consumo específico e intensidade energética são indicadores do PREn (RG-SGE-10); o IDE-02 e o IDE-09 alimentam-nos.")])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Polaridade", ["Maior", "Menor"])
    b.add_list("Periodo", ["Referência (LBE)", "Reporte"])
    b.add_list("EstadoPlano", ["Em estudo", "Planeado", "Em curso", "Concluído", "Cancelado"])
    b.add_list("EstadoLBE", ["Em vigor", "Planeado", "Substituída"])
    b.add_list("TipoIDE", ["Valor de energia medido", "Rácio de valores medidos", "Rácio (numerador estimado)", "Rácio (estimado)", "Rácio (estimado — fator fixo)",
                           "Rácio de valores medidos (fronteira de medida)", "Modelo estatístico (regressão linear múltipla)", "Modelo estatístico (termo independente)",
                           "Modelo de engenharia", "KPI do sistema (não é IDE)"])

    bm = edata.base_mensal()
    co, y_np, e_np = model_np(bm)

    # ------------------------------------------------------------------ base mensal (factos de entrada)
    D = {"Mes": ("date", "Mês (1.º dia).", "PK"), "Periodo": ("text", "Referência (LBE) = mar/2025–fev/2026; Reporte = mar–ago/2026.", ""),
         "Qualidade_Producao": ("text", "Dataset = produção real do dataset; Reconstruído = mar–jun/2025, anterior ao dataset (RG-SGA-13).", ""),
         "Fonte_Energia": ("text", "RG-SGA-13 (fatura), fonte única mar/2025–dez/2026, já com o efeito das ações de out–dez/2026.", ""),
         "Dias_Calendario": ("int", "Dias do mês.", ""), "Dias_Uteis": ("int", "Dias úteis (RG-SGA-13).", ""), "Temp_Media_C": ("num1", "Temperatura média exterior (°C) — RG-SGA-13 (IPMA).", ""),
         "CDD_15": ("num1", "Graus-dia de arrefecimento base 15 °C = max(0; T − 15) × dias.", ""), "kWh_Total": ("kwh", "Eletricidade total da fatura (RG-SGA-13, medido).", ""),
         "kWh_SOP": ("kwh", "Eletricidade do sopro (rateio RG-SGA-13).", ""), "kWh_INJ": ("kwh", "Eletricidade da injeção (rateio).", ""),
         "kWh_UTL_AR": ("kwh", "Ar comprimido (rateio: 19% dos processos).", ""), "kWh_UTL_FRIO": ("kwh", "Arrefecimento (rateio com fator de temperatura).", ""),
         "kWh_GER": ("kwh", "Serviços gerais (base + AVAC).", ""), "kWh_SER": ("kwh", "Serigrafia (rateio).", ""), "kWh_HFS": ("kwh", "Hot foil (rateio).", ""),
         "Unid_INJ": ("num0", "Tampas e potes produzidos (dataset).", ""), "Unid_SOP": ("num0", "Frascos produzidos (dataset).", ""),
         "Unid_SER": ("num0", "Peças serigrafadas.", ""), "Unid_HFS": ("num0", "Peças com hot foil.", ""),
         "Horas_INJ": ("num1", "Horas de marcha da injeção.", ""), "Horas_SOP": ("num1", "Horas de marcha do sopro.", ""), "Horas_SER": ("num1", "Horas de marcha da serigrafia.", ""),
         "Horas_HFS": ("num1", "Horas de marcha do hot foil.", ""), "Unid_Maquinas_Novas": ("num0", "Unidades das 4 máquinas novas (07/2026) — ALE-01.", ""),
         "kWh_Maquinas_Novas": ("kwh", "Eletricidade atribuível às máquinas novas: horas × kW do RG-SGA-13 + quota de ar e frio (ALE-01).", ""),
         "L_Gasoleo_Frota": ("num1", "Gasóleo da frota (L) — RG-SGA-19 S1-01.", ""), "L_Gasoleo_Gerador": ("num1", "Gasóleo do gerador (L) — RG-SGA-19 S1-02.", "")}
    bcols = [col(k, 11 if k not in ("Periodo", "Qualidade_Producao", "Fonte_Energia") else 18, t, desc=d, key=kk) for k, (t, d, kk) in D.items()]
    bcols += [col("Verif_Soma_Usos", 10, "kwh", f='=IF(@Mes@="","",@kWh_SOP@+@kWh_INJ@+@kWh_UTL_AR@+@kWh_UTL_FRIO@+@kWh_GER@+@kWh_SER@+@kWh_HFS@-@kWh_Total@)',
                  desc="Σ usos − total (deve ser ≈ 0: arredondamentos)."),
              col("Energia_Final_MWh", 10, "num1", f='=IF(@Mes@="","",(@kWh_Total@+(@L_Gasoleo_Frota@+@L_Gasoleo_Gerador@)*10)/1000)',
                  desc="Energia final: eletricidade + gasóleo × 10 kWh/L (PCI ≈ 35,9 MJ/L).")]
    rows = bm.to_dict("records")
    b.table("Base_Mensal", "tbl_base_energia", bcols, rows, "Base mensal de energia e variáveis relevantes (RG-SGA-13, dataset, RG-SGA-19).",
            title="BASE MENSAL DE ENERGIA E VARIÁVEIS RELEVANTES", subtitle=f"{PER_INI} a {PER_FIM} · Eletricidade: RG-SGA-13 (fonte única, mar/2025–dez/2026) · Referência = 12 primeiros meses · Reporte = mar–dez/2026",
            cf=[("Periodo", {"Referência": "blue", "Reporte": "green"}), ("Qualidade_Producao", {"Reconstruído": "orange"}), ("Fonte_Energia", {"simulado": "yellow"})], row_height=16, freeze_col=2)

    # ------------------------------------------------------------------ IDE mensais (calculados)
    B = lambda c_: f"INDEX(tbl_base_energia[{c_}],MATCH(@Mes@,tbl_base_energia[Mes],0))"
    hr, first = 4, 5
    last_lbe = first + LBE_ROWS - 1
    icols = [col("Mes", 11, "date", desc="Mês.", key="PK / FK → tbl_base_energia"),
             col("Periodo", 15, f=f'=IF(@Mes@="","",{B("Periodo")})', desc="Referência (LBE) ou Reporte."),
             col("Y_kWh_Ajustado", 12, "kwh", f=f'=IF(@Mes@="","",{B("kWh_Total")}-{B("kWh_Maquinas_Novas")})', desc="Variável dependente: eletricidade real sem as máquinas novas (ALE-01)."),
             col("X1_Unid_mil", 11, "num0", f=f'=IF(@Mes@="","",({B("Unid_INJ")}+{B("Unid_SOP")}-{B("Unid_Maquinas_Novas")})/1000)', desc="Variável relevante 1: milhares de unidades INJ + SOP (sem máquinas novas)."),
             col("X2_CDD", 9, "num1", f=f'=IF(@Mes@="","",{B("CDD_15")})', desc="Variável relevante 2: graus-dia de arrefecimento base 15 °C."),
             col("kWh_Esperado", 12, "kwh", f='=IF(@Mes@="","",lbe_a+lbe_b1*@X1_Unid_mil@+lbe_b2*@X2_CDD@)', desc="Energia esperada pelo modelo da LBE-01 nas condições do mês (normalização)."),
             col("Diferenca_kWh", 11, "kwh", f='=IF(@Mes@="","",@Y_kWh_Ajustado@-@kWh_Esperado@)', desc="Real − esperado (negativo = poupança)."),
             col("CUSUM_kWh", 11, "kwh", f="=0", desc="Soma acumulada das diferenças desde o início da LBE (tendência)."),
             col("Melhoria_Pct", 9, "pct1", f='=IF(@Mes@="","",-@Diferenca_kWh@/@kWh_Esperado@)', desc="IDE-01: (esperado − real) ÷ esperado."),
             col("Dentro_Dominio", 12, f='=IF(@Mes@="","",IF(AND(@X1_Unid_mil@>=dom_x1_min,@X1_Unid_mil@<=dom_x1_max,@X2_CDD@>=dom_x2_min,@X2_CDD@<=dom_x2_max),"Sim","Não"))',
                 desc="As variáveis do mês estão dentro do intervalo da LBE (± tolerância)? Fora do domínio o modelo extrapola (ISO 50006 §8.2)."),
             col("Estado_IDE01", 16, f='=IF(@Mes@="","",IF(@Periodo@="Referência (LBE)","Referência",IF(@Dentro_Dominio@="Não","Fora do domínio",IF(@Diferenca_kWh@>lbe_limite,"Desvio significativo",IF(@Diferenca_kWh@<-lbe_limite,"Melhoria significativa","Dentro da incerteza")))))',
                 desc="Classificação do mês: limite = t(95%) × erro-padrão do modelo (9.1.1 — investigar desvios significativos)."),
             col("SEC_Real", 9, "num1", f=f'=IF(@Mes@="","",{B("kWh_Total")}/({B("Unid_INJ")}+{B("Unid_SOP")})*1000)', desc="IDE-02: kWh por 1.000 unidades (rácio, instalação completa)."),
             col("SEC_SOP", 9, "num1", f=f'=IF(@Mes@="","",{B("kWh_SOP")}/{B("Unid_SOP")}*1000)', desc="IDE-03 (estimado)."),
             col("SEC_INJ", 9, "num1", f=f'=IF(@Mes@="","",{B("kWh_INJ")}/{B("Unid_INJ")}*1000)', desc="IDE-04 (estimado)."),
             col("Carga_Base_Pct", 9, "pct1", f='=IF(@Mes@="","",lbe_a/@Y_kWh_Ajustado@)', desc="IDE-05: termo independente do modelo ÷ real do mês."),
             col("Racio_Frio", 8, "num3", f=f'=IF(@Mes@="","",{B("kWh_UTL_FRIO")}/({B("kWh_INJ")}+{B("kWh_SOP")}))', desc="IDE-06."),
             col("Racio_Ar", 8, "num3", f=f'=IF(@Mes@="","",{B("kWh_UTL_AR")}/({B("kWh_INJ")}+{B("kWh_SOP")}+{B("kWh_SER")}+{B("kWh_HFS")}))', desc="IDE-07 (constante por construção)."),
             col("Energia_Final_MWh", 10, "num1", f=f'=IF(@Mes@="","",{B("Energia_Final_MWh")})', desc="IDE-09.")]
    ws = b.table("IDE_Mensal", "tbl_ide_mensal", icols, [dict(Mes=m) for m in MESES],
                 "IDE mensais calculados por fórmula: energia esperada pela LBE, diferença, CUSUM, melhoria normalizada, domínio de validade e rácios.",
                 title="IDE MENSAIS — COMPARAÇÃO COM A LBE (ISO 50001 9.1.1; ISO 50006 §8 e §10)",
                 subtitle="Tudo calculado · kWh_Esperado = LBE-01 aplicada às variáveis do mês · Fora do domínio = variáveis fora do intervalo da referência (não usar para demonstrar melhoria)",
                 cf=[("Estado_IDE01", {"Desvio significativo": "red", "Melhoria significativa": "green", "Dentro da incerteza": "yellow", "Fora do domínio": "orange", "Referência": "gray"}),
                     ("Dentro_Dominio", {"Não": "orange"})], row_height=16, freeze_col=2)
    t = b.tables["tbl_ide_mensal"]
    Ld, Lc = t["colmap"]["Diferenca_kWh"], t["colmap"]["CUSUM_kWh"]
    for k in range(len(MESES)):
        r = first + k
        ws[f"{Lc}{r}"] = f'=IF(A{r}="","",SUM(${Ld}${first}:{Ld}{r}))'
    Y = f"IDE_Mensal!${t['colmap']['Y_kWh_Ajustado']}${first}:${t['colmap']['Y_kWh_Ajustado']}${last_lbe}"
    X = f"IDE_Mensal!${t['colmap']['X1_Unid_mil']}${first}:${t['colmap']['X2_CDD']}${last_lbe}"
    X1 = f"IDE_Mensal!${t['colmap']['X1_Unid_mil']}${first}:${t['colmap']['X1_Unid_mil']}${last_lbe}"
    X2 = f"IDE_Mensal!${t['colmap']['X2_CDD']}${first}:${t['colmap']['X2_CDD']}${last_lbe}"
    DIF_LBE = f"IDE_Mensal!${Ld}${first}:${Ld}${last_lbe}"

    # ------------------------------------------------------------------ modelo da LBE-01 (LINEST) e testes
    ws = b.sheet("LBE_Modelo", "Modelo estatístico da LBE-01 calculado por LINEST, testes de validade, domínio e demonstração da melhoria no período de reporte.", tab_color="C00000")
    title(ws, "LBE-01 — MODELO ESTATÍSTICO, VALIDADE E DEMONSTRAÇÃO DA MELHORIA — calculado",
          f"kWh ajustado = a + b1 × (mil unidades INJ+SOP) + b2 × CDD₁₅ · Referência {LBE_INI} a {LBE_FIM} (12 meses) · LINEST sobre IDE_Mensal")
    for c_, w_ in zip("ABCDEFG", (40, 16, 14, 12, 12, 16, 60)):
        ws.column_dimensions[c_].width = w_
    header_row(ws, 4, ["Termo", "Coeficiente", "Erro-padrão", "t", "p-valor", "Cumpre p < 0,2?", "Interpretação"])
    L = f"LINEST({Y},{X},TRUE,TRUE)"
    terms = [("a — carga de base (kWh/mês)", 3, "lbe_a", "Energia consumida sem produção nem calor: iluminação, AVAC, utilidades em vazio, máquinas em espera (≈ 'base load' de Kent)."),
             ("b1 — kWh por mil unidades (INJ+SOP)", 2, "lbe_b1", "Consumo marginal de produção: cada mil unidades adicionais custam b1 kWh."),
             ("b2 — kWh por grau-dia de arrefecimento", 1, "lbe_b2", "Efeito do calor no arrefecimento de moldes e no AVAC.")]
    for i, (lab, k, nm, txt) in enumerate(terms):
        r = 5 + i
        cell(ws, r, 1, lab, bold=True)
        cell(ws, r, 2, f"=INDEX({L},1,{k})", fmt="#,##0.00")
        cell(ws, r, 3, f"=INDEX({L},2,{k})", fmt="#,##0.00")
        cell(ws, r, 4, f"=IFERROR(B{r}/C{r},\"\")", fmt="0.00")
        cell(ws, r, 5, f"=IFERROR(TDIST(ABS(D{r}),lbe_df,2),\"\")", fmt="0.0000")
        cell(ws, r, 6, f'=IF(E{r}="","",IF(E{r}<0.2,"Sim","Não"))')
        cell(ws, r, 7, txt)
        b.wb.defined_names[nm] = DefinedName(nm, attr_text=f"LBE_Modelo!$B${r}")
    stats = [("R²", f"=INDEX({L},3,1)", "0.000", "lbe_r2"), ("Erro-padrão da estimativa (kWh)", f"=INDEX({L},3,2)", "#,##0", "lbe_sey"),
             ("Estatística F", f"=INDEX({L},4,1)", "0.00", "lbe_f"), ("Graus de liberdade (n − p − 1)", f"=INDEX({L},4,2)", "0", "lbe_df"),
             ("p-valor do teste F", "=FDIST(lbe_f,2,lbe_df)", "0.0000", "lbe_pf"), ("Média de Y na referência (kWh)", f"=AVERAGE({Y})", "#,##0", "lbe_ymed"),
             ("CV(RMSE)", "=lbe_sey/lbe_ymed", "0.0%", "lbe_cv"), ("NMBE", f"=SUM({DIF_LBE})/((COUNT({Y})-3)*lbe_ymed)", "0.00%", "lbe_nmbe"),
             ("t(95%; gl)", "=TINV(0.05,lbe_df)", "0.000", "lbe_t"), ("Limite de desvio significativo mensal (kWh) = t × erro-padrão", "=lbe_t*lbe_sey", "#,##0", "lbe_limite"),
             ("Carga de base em % do consumo médio", "=lbe_a/lbe_ymed", "0.0%", "lbe_base_pct")]
    header_row(ws, 9, ["Estatística do modelo", "Valor", "", "", "", "", ""])
    for i, (lab, f_, fmt, nm) in enumerate(stats):
        r = 10 + i
        cell(ws, r, 1, lab, bold=True)
        cell(ws, r, 2, f_, fmt=fmt)
        b.wb.defined_names[nm] = DefinedName(nm, attr_text=f"LBE_Modelo!$B${r}")
    r0 = 10 + len(stats) + 1
    header_row(ws, r0, ["Teste de validade", "Valor", "Critério", "Resultado", "", "Fonte do critério", "Leitura"])
    tests = [("R² (EnPI Lite)", "=lbe_r2", "≥ 0,50", "=IF(lbe_r2>=0.5,\"Cumpre\",\"Não cumpre\")", "LBNL EnPI Lite / 50001 Ready M&V", "Fração da variação mensal explicada pelas variáveis."),
             ("R² (ASHRAE 14, recomendado)", "=lbe_r2", "> 0,75", "=IF(lbe_r2>0.75,\"Cumpre\",\"Não cumpre\")", "ASHRAE Guideline 14", "Recomendação para modelos mensais; valores perto do limite pedem mais dados medidos."),
             ("p-valor de todas as variáveis", "=MAX(E6:E7)", "< 0,20", "=IF(MAX(E6:E7)<0.2,\"Cumpre\",\"Não cumpre\")", "LBNL EnPI Lite", "Cada variável relevante tem efeito estatisticamente distinguível."),
             ("p-valor de pelo menos uma variável", "=MIN(E6:E7)", "< 0,10", "=IF(MIN(E6:E7)<0.1,\"Cumpre\",\"Não cumpre\")", "LBNL EnPI Lite", ""),
             ("p-valor do teste F", "=lbe_pf", "< 0,10", "=IF(lbe_pf<0.1,\"Cumpre\",\"Não cumpre\")", "LBNL EnPI Lite", "O modelo no seu conjunto é significativo."),
             ("CV(RMSE)", "=lbe_cv", "≤ 15%", "=IF(lbe_cv<=0.15,\"Cumpre\",\"Não cumpre\")", "ASHRAE Guideline 14 (mensal)", "Dispersão do modelo face à média — base da incerteza da poupança."),
             ("NMBE", "=lbe_nmbe", "entre −5% e +5%", "=IF(ABS(lbe_nmbe)<=0.05,\"Cumpre\",\"Não cumpre\")", "ASHRAE Guideline 14", "Sem enviesamento sistemático (≈ 0 por construção em mínimos quadrados).")]
    for i, (lab, v, crit, res, src, rd) in enumerate(tests):
        r = r0 + 1 + i
        cell(ws, r, 1, lab, bold=True)
        cell(ws, r, 2, v, fmt="0.000" if "p-valor" in lab or "R²" in lab else "0.0%")
        cell(ws, r, 3, crit)
        cell(ws, r, 4, res)
        cell(ws, r, 6, src)
        cell(ws, r, 7, rd)
    rv = r0 + 1 + len(tests)
    cell(ws, rv, 1, "Modelo válido para a LBE-01?", bold=True)
    cell(ws, rv, 2, f'=IF(COUNTIF(D{r0 + 1}:D{rv - 1},"Não cumpre")=0,"Válido",IF(COUNTIF(D{r0 + 1}:D{rv - 1},"Não cumpre")=1,"Válido com reserva","Não válido"))', bold=True)
    for txt, color in (("Válido com reserva", "orange"), ("Não válido", "red"), ("Válido", "green")):
        bg, fg = CF_COLORS[color]
        ws.conditional_formatting.add(f"B{rv}", FormulaRule(formula=[f'B{rv}="{txt}"'], fill=PatternFill("solid", fgColor=bg), font=Font(name=FONT, color=fg, bold=True)))
    for L_ in ("D",):
        for txt, color in (("Não cumpre", "red"), ("Cumpre", "green")):
            bg, fg = CF_COLORS[color]
            ws.conditional_formatting.add(f"{L_}{r0 + 1}:{L_}{rv - 1}", FormulaRule(formula=[f'{L_}{r0 + 1}="{txt}"'], fill=PatternFill("solid", fgColor=bg), font=Font(name=FONT, color=fg, bold=True)))

    # domínio de validade
    rd0 = rv + 2
    header_row(ws, rd0, ["Domínio de validade (ISO 50006 §8.2)", "Mínimo", "Máximo", "Tolerância", "Mín. aceite", "Máx. aceite", "Nota"])
    cell(ws, rd0 + 1, 1, "X1 — mil unidades INJ+SOP", bold=True)
    cell(ws, rd0 + 2, 1, "X2 — CDD₁₅", bold=True)
    for k, (rng_, nmin, nmax) in enumerate(((X1, "dom_x1_min", "dom_x1_max"), (X2, "dom_x2_min", "dom_x2_max"))):
        r = rd0 + 1 + k
        cell(ws, r, 2, f"=MIN({rng_})", fmt="#,##0.0")
        cell(ws, r, 3, f"=MAX({rng_})", fmt="#,##0.0")
        cell(ws, r, 4, TOL_DOMINIO, fmt="0%")
        cell(ws, r, 5, f"=B{r}*(1-D{r})", fmt="#,##0.0")
        cell(ws, r, 6, f"=C{r}*(1+D{r})", fmt="#,##0.0")
        cell(ws, r, 7, "Fora destes limites o modelo extrapola: o mês não entra na demonstração da melhoria." if k == 0 else "Com CDD = 0 no inverno, o mínimo aceite é 0.")
        b.wb.defined_names[nmin] = DefinedName(nmin, attr_text=f"LBE_Modelo!$E${r}")
        b.wb.defined_names[nmax] = DefinedName(nmax, attr_text=f"LBE_Modelo!$F${r}")

    # demonstração da melhoria no período de reporte
    rr = rd0 + 5
    header_row(ws, rr, ["Demonstração da melhoria (ISO 50001 9.1.1 e 10.2; ISO 50006 §10.3)", "Valor", "", "", "", "", "Leitura"])
    I = lambda c_: f"tbl_ide_mensal[{c_}]"
    dem = [("Meses de reporte", f'=COUNTIF({I("Periodo")},"Reporte")', "0", ""),
           ("Meses de reporte dentro do domínio (m)", f'=COUNTIFS({I("Periodo")},"Reporte",{I("Dentro_Dominio")},"Sim")', "0", "Só estes meses servem para demonstrar melhoria."),
           ("Σ kWh esperado (dentro do domínio)", f'=SUMIFS({I("kWh_Esperado")},{I("Periodo")},"Reporte",{I("Dentro_Dominio")},"Sim")', "#,##0", ""),
           ("Σ kWh real ajustado (dentro do domínio)", f'=SUMIFS({I("Y_kWh_Ajustado")},{I("Periodo")},"Reporte",{I("Dentro_Dominio")},"Sim")', "#,##0", ""),
           ("Poupança normalizada (kWh) = esperado − real", f"=B{rr + 3}-B{rr + 4}", "#,##0", "Positivo = melhoria; negativo = piorou."),
           ("Melhoria do desempenho energético (%)", f"=IFERROR(B{rr + 5}/B{rr + 3},\"\")", "0.0%", "IDE-01 agregado no período de reporte."),
           ("Incerteza a 95% (kWh) ≈ t × erro-padrão × √m", f"=lbe_t*lbe_sey*SQRT(B{rr + 2})", "#,##0", "Aproximação da ASHRAE 14 sem termos de alavancagem (conservadora para m pequeno)."),
           ("Conclusão", f'=IF(B{rr + 2}=0,"Sem meses válidos",IF(B{rr + 5}>B{rr + 7},"Melhoria DEMONSTRADA (estatisticamente significativa)",IF(B{rr + 5}<-B{rr + 7},"Piorou (desvio significativo)","Melhoria NÃO demonstrada: diferença dentro da incerteza do modelo")))', None,
            "Para a certificação (ISO 50003:2021) a melhoria tem de ser demonstrada; ver RG-SGE-11 (M&V por ação) e PA-E-01 (submedição).")]
    for i, (lab, f_, fmt, rd_) in enumerate(dem):
        r = rr + 1 + i
        cell(ws, r, 1, lab, bold=True)
        cell(ws, r, 2, f_, fmt=fmt, bold=(i == len(dem) - 1))
        cell(ws, r, 7, rd_)
    rc = rr + len(dem)
    # período após as ações (out–dez/2026): mesma lógica, filtrada por data
    rq = rc + 2
    header_row(ws, rq, ["Após as ações de standby e ar comprimido (out–dez/2026)", "Valor", "", "", "", "", "Leitura"])
    D0 = '">="&DATE(2026,10,1)'
    demq = [("Meses dentro do domínio (m)", f'=COUNTIFS({I("Mes")},{D0},{I("Dentro_Dominio")},"Sim")', "0", ""),
            ("Σ kWh esperado", f'=SUMIFS({I("kWh_Esperado")},{I("Mes")},{D0},{I("Dentro_Dominio")},"Sim")', "#,##0", ""),
            ("Σ kWh real ajustado", f'=SUMIFS({I("Y_kWh_Ajustado")},{I("Mes")},{D0},{I("Dentro_Dominio")},"Sim")', "#,##0", ""),
            ("Poupança normalizada (kWh)", f"=B{rq + 2}-B{rq + 3}", "#,##0", "Comparar com a poupança verificada por ação (RG-SGE-11)."),
            ("Melhoria (%)", f"=IFERROR(B{rq + 4}/B{rq + 2},\"\")", "0.0%", ""),
            ("Incerteza a 95% (kWh)", f"=lbe_t*lbe_sey*SQRT(B{rq + 1})", "#,##0", ""),
            ("Conclusão", f'=IF(B{rq + 1}=0,"Sem meses válidos",IF(B{rq + 4}>B{rq + 6},"Melhoria DEMONSTRADA (estatisticamente significativa)",IF(B{rq + 4}<-B{rq + 6},"Piorou (desvio significativo)","Melhoria NÃO demonstrada: diferença dentro da incerteza do modelo")))', None,
             "Evidência para a ISO 50003: melhoria demonstrada depois da implementação das ações (ISO 50006 §10.3).")]
    for i, (lab, f_, fmt, rd_) in enumerate(demq):
        r = rq + 1 + i
        cell(ws, r, 1, lab, bold=True)
        cell(ws, r, 2, f_, fmt=fmt, bold=(i == len(demq) - 1))
        cell(ws, r, 7, rd_)
    rcq = rq + len(demq)
    for rr_ in (rc, rcq):
        for txt, color in (("DEMONSTRADA", "green"), ("NÃO demonstrada", "orange"), ("Piorou", "red")):
            bg, fg = CF_COLORS[color]
            ws.conditional_formatting.add(f"B{rr_}", FormulaRule(formula=[f'ISNUMBER(SEARCH("{txt}",B{rr_}))'], fill=PatternFill("solid", fgColor=bg), font=Font(name=FONT, color=fg, bold=True)))
        ws.merge_cells(start_row=rr_, start_column=2, end_row=rr_, end_column=6)
    b.wb.defined_names["dem_q4_conclusao"] = DefinedName("dem_q4_conclusao", attr_text=f"LBE_Modelo!$B${rcq}")
    b.wb.defined_names["dem_q4_melhoria"] = DefinedName("dem_q4_melhoria", attr_text=f"LBE_Modelo!$B${rq + 5}")
    rc = rcq

    # gráficos: real vs esperado; CUSUM
    iws = b.wb["IDE_Mensal"]
    cats = Reference(iws, min_col=1, min_row=first, max_row=t["last"])
    ch = LineChart()
    ch.title, ch.height, ch.width = "Eletricidade real ajustada vs esperada pela LBE-01 (kWh)", 8, 18
    for cname in ("Y_kWh_Ajustado", "kWh_Esperado"):
        ci = list(t["colmap"]).index(cname) + 1
        ch.add_data(Reference(iws, min_col=ci, min_row=hr, max_row=t["last"]), titles_from_data=True)
    ch.set_categories(cats)
    ch.y_axis.numFmt = "#,##0"
    ch.x_axis.number_format = "mmm-yy"
    fix_chart(ch)
    ws.add_chart(ch, f"A{rc + 3}")
    ch2 = LineChart()
    ch2.title, ch2.height, ch2.width = "CUSUM (kWh): declive negativo = poupança; positivo = desperdício", 8, 18
    ci = list(t["colmap"]).index("CUSUM_kWh") + 1
    ch2.add_data(Reference(iws, min_col=ci, min_row=hr, max_row=t["last"]), titles_from_data=True)
    ch2.set_categories(cats)
    ch2.y_axis.numFmt = "#,##0"
    ch2.legend = None
    fix_chart(ch2)
    ws.add_chart(ch2, f"E{rc + 3}")

    # ------------------------------------------------------------------ variáveis candidatas (6.4 / 6.5 — considerar as variáveis relevantes)
    BR = lambda c_: f"Base_Mensal!${b.tables['tbl_base_energia']['colmap'][c_]}${first}:${b.tables['tbl_base_energia']['colmap'][c_]}${last_lbe}"
    vcols = [col("ID_Variavel", 8, key="PK", desc="Variável candidata."), col("Variavel", 34, desc="Descrição."), col("Coluna_Base", 16, desc="Coluna em tbl_base_energia."),
             col("Fonte", 26, desc="Origem do dado."), col("Unidade", 10, desc="Unidade."),
             col("Correlacao_com_kWh", 10, "num3", f="=0", desc="Coeficiente de correlação (Pearson) com o kWh total nos 12 meses de referência."),
             col("R2_Simples", 9, "num3", f='=IF(@ID_Variavel@="","",IFERROR(@Correlacao_com_kWh@^2,""))', desc="R² da regressão simples."),
             col("Decisao", 16, desc="Relevante (entra no modelo) / Não relevante / Redundante."), col("Justificacao", 60, desc="Porquê (critério: significância estatística e sentido físico).")]
    VAR = [("VAR-01", "Unidades produzidas INJ + SOP", "Unid_INJ", "Dataset (MES)", "un", "Relevante", "Maior correlação com sentido físico; variável de negócio que a produção controla. Entra como X1 (soma INJ+SOP, milhares)."),
           ("VAR-02", "Graus-dia de arrefecimento (base 15 °C)", "CDD_15", "IPMA (via RG-SGA-13)", "°C·dia", "Relevante (com reserva)", "Explica fisicamente o arrefecimento e o AVAC no verão e reduz o erro nos meses quentes, mas p ≈ 0,27 (> 0,2) com 12 meses de rateio. Mantida com reserva registada (LBE válida com reserva); reavaliar com os dados medidos dos analisadores (ALE-03)."),
           ("VAR-03", "Horas de marcha da injeção", "Horas_INJ", "Dataset (MES)", "h", "Redundante", "Muito correlacionada com as unidades (a energia do rateio é horas × kW). Não se usam as duas: preferidas as unidades (saída útil)."),
           ("VAR-04", "Horas de marcha do sopro", "Horas_SOP", "Dataset (MES)", "h", "Redundante", "Correlação mais alta que as unidades (a energia do rateio é horas × kW) e um modelo horas + CDD teria R² ≈ 0,86 — rejeitado: normalizar por horas esconderia as perdas de produtividade (marcha lenta, microparagens) que são desperdício de energia. A ISO 50006 recomenda variáveis de saída útil quando possível."),
           ("VAR-05", "Dias úteis", "Dias_Uteis", "Calendário", "dias", "Excluída", "Efeito já captado pelas unidades produzidas; correlação fraca isoladamente."),
           ("VAR-06", "Temperatura média exterior", "Temp_Media_C", "IPMA", "°C", "Redundante", "Substituída pelos graus-dia (relação não linear: só acima de 15 °C há carga de arrefecimento).")]
    ws_v = b.table("Variaveis_Relevantes", "tbl_variaveis", vcols, [dict(zip(["ID_Variavel", "Variavel", "Coluna_Base", "Fonte", "Unidade", "Decisao", "Justificacao"], v)) for v in VAR],
                   "Seleção das variáveis relevantes (6.4, 6.5; ISO 50006 §5.5 e anexo D).", title="VARIÁVEIS RELEVANTES CANDIDATAS — SELEÇÃO (ISO 50006 §5.5)",
                   subtitle="Correlação calculada nos 12 meses de referência · Critério de relevância: significativa no modelo (p < 0,2) e com explicação física",
                   cf=[("Decisao", {"reserva": "yellow", "Relevante": "green", "Redundante": "yellow", "Excluída": "gray"})], row_height=30)
    tv = b.tables["tbl_variaveis"]
    Lcor = tv["colmap"]["Correlacao_com_kWh"]
    for k, v in enumerate(VAR):
        r = tv["first"] + k
        ws_v[f"{Lcor}{r}"] = f"=CORREL({BR('kWh_Total')},{BR(v[2])})" if v[0] != "VAR-01" else f"=CORREL({BR('kWh_Total')},{BR('Unid_INJ')}+{BR('Unid_SOP')})"
    ws_v[f"{Lcor}{tv['first']}"] = f"=SUMPRODUCT(({BR('Unid_INJ')}+{BR('Unid_SOP')}-AVERAGE({BR('Unid_INJ')})-AVERAGE({BR('Unid_SOP')}))*({BR('kWh_Total')}-AVERAGE({BR('kWh_Total')})))/SQRT(SUMPRODUCT(({BR('Unid_INJ')}+{BR('Unid_SOP')}-AVERAGE({BR('Unid_INJ')})-AVERAGE({BR('Unid_SOP')}))^2)*SUMPRODUCT(({BR('kWh_Total')}-AVERAGE({BR('kWh_Total')}))^2))"

    # ------------------------------------------------------------------ catálogo de IDE / KPI
    doze = f"IDE_Mensal!$A${first}:${get_column_letter(len(t['colmap']))}${last_lbe}"
    seis = f"IDE_Mensal!$A${last_lbe + 1}:${get_column_letter(len(t['colmap']))}${t['last']}"
    hdr = f"IDE_Mensal!$A${hr}:${get_column_letter(len(t['colmap']))}${hr}"
    kcols = [col("ID_KPI", 9, key="PK", desc="IDE-xx = indicador de desempenho energético; KPI-E-xx = indicador do sistema."),
             col("Nome", 40, desc="Nome do indicador."), col("Formula_Calculo", 40, desc="Definição operacional."), col("Unidade", 11, desc="Unidade."),
             col("Polaridade", 8, dv="Polaridade", desc="Maior ou menor é melhor."),
             col("Tipo_IDE_ISO50006", 24, dv="TipoIDE", desc="Tipo de IDE (ISO 50006 §6.2) — posição equivalente ao Tipo_ISO14031 do RG-SGA-05."),
             col("Frequencia", 10, desc="Frequência de cálculo."), col("Fonte_Dados", 32, desc="Origem dos dados."), col("Responsavel", 22, dv="Funcao", desc="Dono do IDE (ISO 50006 tab. 1 — 'EnPI owner')."),
             col("Baseline", 10, "num", f=f'=IF(OR(@ID_KPI@="",@Coluna_Mensal@="—"),@Valor_LBE_Externo@,IFERROR(AVERAGE(INDEX({doze},0,MATCH(@Coluna_Mensal@,{hdr},0))),""))',
                 desc="Valor da LBE: média dos 12 meses de referência (ou valor externo quando o IDE vem de outro registo)."),
             col("ID_OBJ", 9, desc="Objetivo que o indicador mede.", key="FK → tbl_objetivos"), col("ID_MED", 12, desc="Linhas do plano de recolha de dados (RG-SGE-06).", key="FK → RG-SGE-06 tbl_plano_recolha"),
             col("Fronteira", 30, desc="[Só SGE] Fronteira do IDE (ISO 50006 §5.3)."), col("ID_USE", 9, desc="[Só SGE] Uso significativo abrangido."),
             col("Variaveis_Relevantes", 28, desc="[Só SGE] Variáveis relevantes consideradas (6.4)."), col("Fatores_Estaticos", 26, desc="[Só SGE] Fatores estáticos monitorizados."),
             col("Normalizacao", 30, desc="[Só SGE] Se e como é normalizado (6.5; ISO 50006 §8)."), col("ID_LBE", 8, desc="[Só SGE] LBE correspondente.", key="FK → tbl_lbe"),
             col("Utilizadores", 30, desc="[Só SGE] Utilizadores do IDE (ISO 50006 §5.2)."), col("Coluna_Mensal", 16, desc="[Só SGE] Coluna em tbl_ide_mensal ('—' se vem de outro registo)."),
             col("Meta", 8, "num", desc="[Só SGE] Meta energética associada (percentagens como fração).", req=False),
             col("Valor_LBE_Externo", 10, "num", desc="[Só SGE] Valor da LBE quando o IDE é calculado noutro registo (à data de referência).", req=False),
             col("Valor_Reporte_Externo", 10, "num", desc="[Só SGE] Valor atual quando o IDE é calculado noutro registo.", req=False),
             col("Valor_Reporte", 10, "num", f=f'=IF(@ID_KPI@="","",IF(@Coluna_Mensal@="—",@Valor_Reporte_Externo@,IFERROR(AVERAGE(INDEX({seis},0,MATCH(@Coluna_Mensal@,{hdr},0))),"")))',
                 desc="[Só SGE] Média dos meses de reporte mar–dez/2026 (IDE-01: agregado oficial da LBE_Modelo; IDE-08 e KPI-E-01: valor de dez/2026)."),
             col("Variacao_vs_LBE", 9, "pct1", f='=IF(OR(@ID_KPI@="",NOT(ISNUMBER(@Valor_Reporte@)),NOT(ISNUMBER(@Baseline@))),"",IF(ABS(@Baseline@)<0.000001,"",(@Valor_Reporte@-@Baseline@)/ABS(@Baseline@)))',
                 desc="[Só SGE] Variação relativa do reporte face à LBE."),
             col("Estado", 14, f='=IF(@ID_KPI@="","",IF(OR(@Meta@="",NOT(ISNUMBER(@Valor_Reporte@))),"Sem meta / sem dado",IF(@Polaridade@="Maior",IF(@Valor_Reporte@>=@Meta@,"Cumpre","Não cumpre"),IF(@Valor_Reporte@<=@Meta@,"Cumpre","Não cumpre"))))',
                 desc="[Só SGE] Estado face à meta."),
             col("Ligacao_SGI", 26, desc="[Só SGE] Indicador equivalente no SGA/SGQ.", req=False), col("Qualidade_Dados", 16, desc="[Só SGE] Medido / estimado / calculado (EN 17267).")]
    ext = {"IDE-01": (0.0, f"=LBE_Modelo!$B${rr + 6}"), "IDE-08": (0.1337, 0.1064), "IDE-10": (0.55, 0.55), "KPI-E-01": (0.0, 0.954), "KPI-E-02": (None, 1.0), "KPI-E-03": (None, 0.86)}
    krows = []
    for k in KPIS:
        d = dict(zip(["ID_KPI", "Nome", "Formula_Calculo", "Unidade", "Polaridade", "Tipo_IDE_ISO50006", "Frequencia", "Fonte_Dados", "Responsavel", "ID_OBJ", "ID_MED", "Fronteira",
                      "ID_USE", "Variaveis_Relevantes", "Fatores_Estaticos", "Normalizacao", "ID_LBE", "Utilizadores", "Coluna_Mensal", "Meta", "Ligacao_SGI", "Qualidade_Dados"], k))
        if k[0] in ext:
            d["Valor_LBE_Externo"], d["Valor_Reporte_Externo"] = ext[k[0]]
        krows.append(d)
    b.table("Catalogo_IDE", "tbl_kpi", kcols, krows, "Catálogo de IDE e KPI do SGE: tipo, fronteira, variáveis, normalização, LBE, dono e utilizadores (6.4; ISO 50006 §5–6).",
            title="CATÁLOGO DE INDICADORES DE DESEMPENHO ENERGÉTICO (6.4) — ISO 50006", subtitle="Mesmas colunas do RG-SGA-05 tbl_kpi nas primeiras 12 posições · Baseline e valor de reporte calculados a partir de IDE_Mensal",
            cf=[("Estado", {"Não cumpre": "red", "Cumpre": "green", "Sem meta": "gray"}), ("Qualidade_Dados", {"Estimado": "orange"})], row_height=42, freeze_col=2)

    # ------------------------------------------------------------------ registo das LBE
    lcols = [col("ID_LBE", 8, key="PK", desc="Linha de base energética."), col("ID_KPI", 9, desc="IDE que a usa.", key="FK → tbl_kpi"),
             col("Descricao", 40, desc="O que é a LBE."), col("Periodo_Inicio", 11, "date", desc="Início do período de referência."), col("Periodo_Fim", 11, "date", desc="Fim do período de referência."),
             col("N_Meses", 7, "int", f='=IF(@ID_LBE@="","",IF(ISNUMBER(@Periodo_Fim@),DATEDIF(@Periodo_Inicio@,@Periodo_Fim@,"m")+1,""))', desc="Duração (meses)."),
             col("Metodo", 34, desc="Modelo / cálculo."), col("Valor_LBE", 10, "num", f='=IF(@ID_LBE@="","",IFERROR(INDEX(tbl_kpi[Baseline],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0)),""))', desc="Valor da LBE (do catálogo)."),
             col("R2", 7, "num3", desc="R² (só modelos).", req=False), col("Validade_Estatistica", 16, desc="Resultado dos testes (LBE_Modelo).", req=False),
             col("Estado", 10, dv="EstadoLBE", desc="Em vigor / planeado / substituída."), col("Data_Aprovacao", 11, "date", desc="Aprovação pela equipa de gestão de energia.", req=False),
             col("Criterios_Revisao", 44, desc="Quando rever (6.5 a) IDE deixa de representar; b) fatores estáticos; c) método predeterminado)."),
             col("Proxima_Revisao", 11, "date", desc="Revisão prevista.", req=False)]
    CRIT = "a) IDE deixa de refletir o desempenho (ex.: submedição); b) alteração significativa de fatores estáticos (tbl_fatores_estaticos); c) revisão anual com a revisão energética"
    LB = [("LBE-01", "IDE-01", "Modelo de regressão da eletricidade da instalação (sem máquinas novas)", LBE_INI, LBE_FIM, "kWh = a + b1·mil un + b2·CDD₁₅ (LINEST)", "Em vigor", "2026-09-15", "2027-07-31"),
          ("LBE-02", "IDE-02", "SEC médio da instalação", LBE_INI, LBE_FIM, "Média dos rácios mensais", "Em vigor", "2026-09-15", "2027-07-31"),
          ("LBE-03", "IDE-03", "SEC do sopro (estimado)", LBE_INI, LBE_FIM, "Média dos rácios mensais", "Em vigor", "2026-09-15", "2027-12-31"),
          ("LBE-04", "IDE-04", "SEC da injeção (estimado)", LBE_INI, LBE_FIM, "Média dos rácios mensais", "Em vigor", "2026-09-15", "2027-12-31"),
          ("LBE-05", "IDE-06", "Rácio de arrefecimento (estimado)", LBE_INI, LBE_FIM, "Média dos rácios mensais", "Em vigor", "2026-09-15", "2027-12-31"),
          ("LBE-06", "IDE-08", "Potência específica do ar comprimido — compressores antigos", "2026-01-12", "2026-01-18", "Semana de registo PA-01 + EQP-04 (RG-SGE-11)", "Em vigor", "2026-09-15", "2027-06-30"),
          ("LBE-07", "IDE-09", "Energia final mensal média", LBE_INI, LBE_FIM, "Média mensal", "Em vigor", "2026-09-15", "2027-07-31"),
          ("LBE-08", "IDE-10", "Quota renovável 2025/26 (rótulo de energia)", "2025-01-01", "2025-12-31", "Rótulo do comercializador", "Em vigor", "2026-09-15", "2027-06-30")]
    lrows = []
    for x in LB:
        d = dict(zip(["ID_LBE", "ID_KPI", "Descricao", "Periodo_Inicio", "Periodo_Fim", "Metodo", "Estado", "Data_Aprovacao", "Proxima_Revisao"], x))
        for kk in ("Periodo_Inicio", "Periodo_Fim", "Data_Aprovacao", "Proxima_Revisao"):
            d[kk] = dt.date.fromisoformat(d[kk])
        d["Criterios_Revisao"] = CRIT
        if x[0] == "LBE-01":
            d["R2"] = "=lbe_r2"
            d["Validade_Estatistica"] = f"=LBE_Modelo!B{rv}"
        lrows.append(d)
    b.table("Registo_LBE", "tbl_lbe", lcols, lrows, "Registo das LBE (6.5 — reter as LBE, os dados das variáveis relevantes e as modificações).",
            title="REGISTO DAS LINHAS DE BASE ENERGÉTICAS (6.5)", row_height=36, freeze_col=2)
    acols = [col("ID_Alteracao_LBE", 9, key="PK", desc="Alteração/ajuste."), col("Data_Efeito", 11, "date", desc="Data a partir da qual tem efeito."),
             col("Tipo", 18, desc="Fator estático / ação de melhoria / método de medição / tipo de energia."), col("Descricao", 44, desc="O que mudou."),
             col("LBE_Afetadas", 16, desc="LBE afetadas."), col("Tratamento", 56, desc="Ajuste aplicado e justificação (ISO 50006 §9)."),
             col("Acao_Futura", 34, desc="O que falta fazer.", req=False), col("Estado", 10, desc="Aprovado / planeado."), col("Responsavel", 22, dv="Funcao", desc="Responsável."),
             col("Data_Aprovacao", 11, "date", desc="Aprovação.", req=False)]
    b.table("Alteracoes_LBE", "tbl_alteracoes_lbe", acols,
            rows_from(["ID_Alteracao_LBE", "Data_Efeito", "Tipo", "Descricao", "LBE_Afetadas", "Tratamento", "Acao_Futura", "Estado", "Responsavel", "Data_Aprovacao"], ALT_LBE, dates=("Data_Efeito", "Data_Aprovacao")),
            "Modificações às LBE e ajustes não rotineiros (6.5 — reter).", title="ALTERAÇÕES ÀS LBE E AJUSTES NÃO ROTINEIROS (6.5; ISO 50006 §9)", row_height=60, freeze_col=2)
    fcols = [col("ID_Fator", 8, key="PK", desc="Fator estático."), col("Fator_Estatico", 28, desc="Fator que não varia rotineiramente mas afeta o desempenho (ISO 50006 3.1.18)."),
             col("Condicao_Na_LBE", 36, desc="Condição no período de referência."), col("Condicao_Atual", 36, desc="Condição à data de referência."),
             col("Situacao", 18, desc="Sem alteração / alterado."), col("ID_Alteracao_LBE", 10, desc="Tratamento.", key="FK → tbl_alteracoes_lbe", req=False)]
    b.table("Fatores_Estaticos", "tbl_fatores_estaticos", fcols, rows_from(input_names(fcols), FATORES_ESTATICOS),
            "Fatores estáticos monitorizados para decidir revisões da LBE (6.5 b).", title="FATORES ESTÁTICOS MONITORIZADOS (6.5 b; ISO 50006 §9.2)",
            cf=[("Situacao", {"Alterado": "orange", "Sem alteração": "green", "ação de melhoria": "blue"})], row_height=30)

    # ------------------------------------------------------------------ parâmetros (mesmo nome e colunas do RG-SGA-13 tbl_parametros)
    PAR = [("PRECO_MEDIO", edata.preco_medio(), "€/kWh", "Preço médio da eletricidade (energia + redes, sem potência) nos 12 meses set/2025–ago/2026", "RG-SGE-09 tbl_faturas (simulado)"),
           ("KWH_POR_L_GASOLEO", 10.0, "kWh/L", "Poder calorífico inferior do gasóleo ≈ 35,9 MJ/L", "Despacho 17313/2008 / DGEG — confirmar"),
           ("TOL_DOMINIO", TOL_DOMINIO, "fração", "Tolerância do domínio de validade do modelo da LBE-01", "Decisão da equipa de gestão de energia (ISO 50006 §8.2)"),
           ("T_BASE_CDD", edata.T_BASE_CDD, "°C", "Temperatura base dos graus-dia de arrefecimento", "Mesma base do FRIO_TEMP do RG-SGA-13")]
    parcols = [col("Codigo", 18, key="PK", desc="Parâmetro."), col("Valor", 10, "num3", desc="Valor."), col("Unidade", 10, desc="Unidade."),
               col("Descricao", 60, desc="Descrição."), col("Fonte", 40, desc="[Só SGE] Origem do valor.")]
    b.table("Parametros", "tbl_parametros", parcols, [dict(zip(["Codigo", "Valor", "Unidade", "Descricao", "Fonte"], p_)) for p_ in PAR],
            "Parâmetros usados nos cálculos deste registo (mesma estrutura do RG-SGA-13 tbl_parametros).", title="PARÂMETROS DE CÁLCULO", row_height=18)
    tp = b.tables["tbl_parametros"]
    b.wb.defined_names["preco_medio"] = DefinedName("preco_medio", attr_text=f"Parametros!${tp['colmap']['Valor']}${tp['first']}")

    # ------------------------------------------------------------------ objetivos, metas e planos (6.2)
    OBJ_N = ["ID_OBJ", "ID_Politica", "Origem_Tipo", "Origem_IDs", "Origem_Descricao", "Declaracao_Objetivo", "ID_KPI", "Meta_Tipo", "Meta_Valor", "Meta_Numerica", "Prazo",
             "Recursos_Humanos", "Recursos_Materiais", "Recursos_Financeiros_EUR", "Responsavel", "Acoes_PAM", "Considera_USE", "Oportunidades_Revisao", "Requisitos_Aplicaveis",
             "Comunicado", "Ligacao_SGA"]
    orows = rows_from(OBJ_N, OBJETIVOS, dates=("Prazo",))
    for o in orows:
        o["Data_Aprovacao"] = dt.date(2026, 9, 29)
    ocols = [col("ID_OBJ", 9, key="PK", desc="Objetivo energético / do SGE."), col("ID_Politica", 9, desc="Compromisso da política energética (RG-SGE-02).", key="FK → RG-SGE-02 tbl_politica"),
             col("Origem_Tipo", 16, desc="De onde nasce (revisão energética, contexto, requisito)."), col("Origem_IDs", 22, desc="IDs de origem (USE, OPE, riscos)."),
             col("Origem_Descricao", 36, desc="Problema ou oportunidade que justifica o objetivo."), col("Declaracao_Objetivo", 46, desc="Objetivo mensurável (6.2.2 b)."),
             col("ID_KPI", 9, desc="IDE que mede o objetivo.", key="FK → tbl_kpi"),
             col("Indicador_KPI", 28, f='=IFERROR(INDEX(tbl_kpi[Nome],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0))&" ("&INDEX(tbl_kpi[Unidade],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0))&")","")', desc="Nome e unidade do IDE."),
             col("Baseline", 9, "num", f='=IF(@ID_OBJ@="","",IFERROR(INDEX(tbl_kpi[Baseline],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0)),""))', desc="Valor da LBE."),
             col("Meta_Tipo", 9, desc="Absoluta / relativa."), col("Meta_Valor", 14, desc="Meta em texto."), col("Meta_Numerica", 9, "num", desc="Meta numérica (percentagens como fração)."),
             col("Prazo", 11, "date", desc="Prazo."), col("Recursos_Humanos", 26, desc="Pessoas (6.2.3)."), col("Recursos_Materiais", 26, desc="Meios materiais (6.2.3)."),
             col("Recursos_Financeiros_EUR", 11, "eur", desc="Orçamento (6.2.3)."), col("Responsavel", 22, dv="Funcao", desc="Responsável (6.2.3)."),
             col("Acoes_PAM", 20, desc="Planos de ação (tbl_planos_acao) — mesmo nome de coluna do RG-SGA-05.", key="FK → tbl_planos_acao"),
             col("Estado", 11, f='=IF(@ID_OBJ@="","",IF(NOT(ISNUMBER(@Valor_Atual@)),"Sem dado",IF(@Polaridade@="Maior",IF(@Valor_Atual@>=@Meta_Numerica@,"Atingido","Em curso"),IF(@Valor_Atual@<=@Meta_Numerica@,"Atingido","Em curso"))))',
                 desc="Estado face à meta."),
             col("Valor_Atual", 10, "num", f='=IF(@ID_OBJ@="","",IF(@ID_KPI@="IDE-01",IFERROR(LBE_Modelo!$B$' + str(rr + 6) + ',""),IFERROR(INDEX(tbl_kpi[Valor_Reporte],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0)),"")))',
                 desc="Valor do período de reporte (IDE-01: melhoria agregada dentro do domínio, LBE_Modelo)."),
             col("Progresso", 9, "pct", f='=IF(@ID_OBJ@="","",IF(OR(NOT(ISNUMBER(@Valor_Atual@)),NOT(ISNUMBER(@Baseline@))),"",IF(@Meta_Numerica@=@Baseline@,"",MAX(-1,MIN(1,(@Valor_Atual@-@Baseline@)/(@Meta_Numerica@-@Baseline@))))))',
                 desc="Caminho baseline → meta já percorrido."),
             col("Dias_ate_Prazo", 8, "int", f='=IF(@ID_OBJ@="","",@Prazo@-DataRef)', desc="Dias até ao prazo."),
             col("S_Especifico", 7, f='=IF(@ID_OBJ@="","",IF(AND(LEN(@Declaracao_Objetivo@)>40,@ID_KPI@<>""),"✔","✘"))', desc="S."),
             col("M_Mensuravel", 7, f='=IF(@ID_OBJ@="","",IF(ISNUMBER(@Meta_Numerica@),"✔","✘"))', desc="M (6.2.2 b)."),
             col("A_Atingivel", 7, f='=IF(@ID_OBJ@="","",IF(AND(@Recursos_Humanos@<>"",@Responsavel@<>"",@Acoes_PAM@<>""),"✔","✘"))', desc="A (6.2.3)."),
             col("R_Relevante", 7, f='=IF(@ID_OBJ@="","",IF(AND(@ID_Politica@<>"",@Origem_IDs@<>""),"✔","✘"))', desc="R (6.2.2 a, d, e)."),
             col("T_Temporal", 7, f='=IF(@ID_OBJ@="","",IF(ISNUMBER(@Prazo@),"✔","✘"))', desc="T."),
             col("Validacao_SMART", 10, f='=IF(@ID_OBJ@="","",IF((@S_Especifico@="✔")+(@M_Mensuravel@="✔")+(@A_Atingivel@="✔")+(@R_Relevante@="✔")+(@T_Temporal@="✔")=5,"SMART","Rever"))', desc="SMART."),
             col("Data_Aprovacao", 11, "date", desc="Aprovação (revisão pela gestão RD-E-2026-01)."),
             col("Considera_USE", 16, desc="[Só SGE] USE considerados (6.2.2 d)."), col("Oportunidades_Revisao", 18, desc="[Só SGE] Oportunidades da revisão energética (6.2.2 e)."),
             col("Requisitos_Aplicaveis", 28, desc="[Só SGE] Requisitos aplicáveis considerados (6.2.2 c)."), col("Comunicado", 22, desc="[Só SGE] Como é comunicado (6.2.2 g)."),
             col("Ligacao_SGA", 22, desc="[Só SGE] Objetivo/ação equivalente no SGA.", req=False),
             col("Polaridade", 8, f='=IF(@ID_OBJ@="","",IFERROR(INDEX(tbl_kpi[Polaridade],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0)),""))', desc="[Só SGE] Da definição do IDE.")]
    b.table("Objetivos_Energeticos", "tbl_objetivos", ocols, orows, "Objetivos energéticos e do SGE (6.2.1, 6.2.2 a–h) — mesmas colunas do RG-SGA-05 tbl_objetivos.",
            title="OBJETIVOS ENERGÉTICOS 2026–2028 (6.2)", subtitle="Retidos como informação documentada (6.2.2) · Valor atual calculado a partir dos IDE e da LBE_Modelo",
            cf=[("Estado", {"Atingido": "green", "Em curso": "orange", "Sem dado": "gray"}), ("Validacao_SMART", {"SMART": "green", "Rever": "red"})], row_height=60, freeze_col=2)
    mcols = [col("ID_Meta", 9, key="PK", desc="Meta energética (6.2.1)."), col("ID_OBJ", 9, desc="Objetivo.", key="FK → tbl_objetivos"), col("ID_KPI", 9, desc="IDE.", key="FK → tbl_kpi"),
             col("Descricao", 40, desc="Meta."), col("Meta_Numerica", 9, "num", desc="Valor-alvo."), col("Prazo", 11, "date", desc="Prazo."),
             col("Valor_LBE", 9, "num", f='=IF(@ID_Meta@="","",IFERROR(INDEX(tbl_kpi[Baseline],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0)),""))', desc="LBE."),
             col("Valor_Atual", 9, "num", f='=IF(@ID_Meta@="","",IFERROR(INDEX(tbl_objetivos[Valor_Atual],MATCH(@ID_OBJ@,tbl_objetivos[ID_OBJ],0)),""))', desc="Valor atual (do objetivo)."),
             col("Unidade", 11, f='=IF(@ID_Meta@="","",IFERROR(INDEX(tbl_kpi[Unidade],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0)),""))', desc="Unidade.")]
    b.table("Metas_Energeticas", "tbl_metas_energeticas", mcols, rows_from(["ID_Meta", "ID_OBJ", "ID_KPI", "Descricao", "Meta_Numerica", "Prazo"], METAS, dates=("Prazo",)),
            "Metas energéticas quantificadas por IDE (6.2.1 — 'a organização deve estabelecer metas energéticas').", title="METAS ENERGÉTICAS (6.2.1)", row_height=18)
    pcols = [col("ID_Plano", 9, key="PK", desc="Plano de ação."), col("ID_OBJ", 9, desc="Objetivo.", key="FK → tbl_objetivos"),
             col("O_Que_Fazer", 50, desc="O que vai ser feito (6.2.3)."), col("Recursos", 28, desc="Recursos necessários (6.2.3)."), col("Custo_EUR", 10, "eur", desc="Custo previsto."),
             col("Responsavel", 22, dv="Funcao", desc="Quem é responsável (6.2.3)."), col("Inicio", 11, "date", desc="Início."), col("Prazo", 11, "date", desc="Quando será concluído (6.2.3)."),
             col("Como_Avaliar", 36, desc="Como os resultados serão avaliados (6.2.3)."), col("Metodo_Verificacao", 36, desc="Método para verificar a melhoria do desempenho energético (6.2.3 → 9.1; IPMVP/ISO 50015)."),
             col("Poupanca_Prevista_MWh", 10, "num0", desc="Poupança anual prevista (MWh)."), col("Estado", 11, dv="EstadoPlano", desc="Estado."),
             col("Integracao_Negocio", 26, desc="Integração nos processos de negócio (6.2.3)."), col("ID_PAM_SGA", 10, desc="Ação equivalente no PAM do SGA.", req=False),
             col("ID_Oportunidade", 12, desc="Oportunidade da revisão energética (RG-SGE-04).", key="FK → RG-SGE-04 tbl_oportunidades"),
             col("Dias_ate_Prazo", 8, "int", f='=IF(@ID_Plano@="","",@Prazo@-DataRef)', desc="Dias até ao prazo."),
             col("Poupanca_Prevista_EUR", 10, "eur", f='=IF(@ID_Plano@="","",@Poupanca_Prevista_MWh@*1000*preco_medio)', desc="Poupança anual prevista (€) ao preço médio da eletricidade (RG-SGE-09)."),
             col("Payback_Anos", 8, "num1", f='=IF(OR(@ID_Plano@="",@Poupanca_Prevista_EUR@=0),"",@Custo_EUR@/@Poupanca_Prevista_EUR@)', desc="Retorno simples.")]
    b.table("Planos_Acao", "tbl_planos_acao", pcols,
            rows_from(["ID_Plano", "ID_OBJ", "O_Que_Fazer", "Recursos", "Custo_EUR", "Responsavel", "Inicio", "Prazo", "Como_Avaliar", "Metodo_Verificacao", "Poupanca_Prevista_MWh",
                       "Estado", "Integracao_Negocio", "ID_PAM_SGA", "ID_Oportunidade"], PLANOS, dates=("Inicio", "Prazo")),
            "Planos de ação energéticos (6.2.3 — reter).", title="PLANOS DE AÇÃO ENERGÉTICOS (6.2.3)",
            subtitle="Cada plano diz como a melhoria será verificada (9.1) · Preço médio da eletricidade: célula preco_medio (RG-SGE-09, média das faturas de 12 meses)",
            cf=[("Estado", {"Concluído": "green", "Em curso": "blue", "Planeado": "yellow", "Em estudo": "gray"})], row_height=60, freeze_col=2)
    ws = b.sheet("Metodologia_IDE_LBE", "Metodologia para determinar e atualizar IDE e LBE (6.4 — manter como informação documentada; resumo do PR-SGE-03).")
    title(ws, "METODOLOGIA DOS IDE E DAS LBE (6.4 e 6.5 — informação documentada mantida; detalhe no PR-SGE-03)")
    notes(ws, 3, [
        ("1. Fronteiras", "ISO 50006 §5.3: instalação (IDE-01/02/05/09), USE (IDE-03/04/06/07), fronteira de medida da central de ar (IDE-08). A fronteira do IDE-01 exclui as 4 máquinas novas até haver 12 meses (ALE-01)."),
        ("2. Variáveis relevantes", "ISO 50006 §5.5: candidatas em tbl_variaveis; entram no modelo se forem significativas (p < 0,2) e tiverem explicação física. Escolhidas: unidades INJ+SOP e graus-dia base 15 °C."),
        ("3. Tipo de IDE", "ISO 50006 §6.2: modelo estatístico quando há variáveis relevantes (IDE-01); rácio quando há uma entrada e uma saída e poucas variáveis (IDE-02 a 08); valor medido para relato (IDE-09)."),
        ("4. Período de referência", f"ISO 50006 §7.2: {LBE_INI} a {LBE_FIM} — 12 meses para cobrir o ciclo anual de temperatura; termina antes dos compressores VSD para que o efeito apareça no reporte. Meses mar–jun/2025 têm produção reconstruída (qualidade inferior, RG-SGA-13)."),
        ("5. Normalização", "ISO 50006 §8: energia esperada = modelo aplicado às variáveis do mês; melhoria = (esperado − real) ÷ esperado. Não se normaliza fora do domínio (±10% do intervalo de referência)."),
        ("6. Validade estatística", "R² ≥ 0,5 e p-valores (EnPI Lite/LBNL); CV(RMSE) ≤ 15% e NMBE ±5% (ASHRAE 14). O resultado está em LBE_Modelo e em tbl_lbe."),
        ("7. Desvio significativo (9.1.1)", "Mês com |real − esperado| > t(95%) × erro-padrão do modelo: investigar e responder, com registo no RG-SGE-11 tbl_desvios."),
        ("8. Demonstração da melhoria", "ISO 50006 §10.3: soma do reporte dentro do domínio; a melhoria só é declarada se exceder a incerteza a 95%. A ISO 50003:2021 exige melhoria demonstrada para certificar."),
        ("9. Revisão das LBE (6.5)", "a) IDE deixa de representar (submedição 12/2026); b) fatores estáticos (tbl_fatores_estaticos); c) anualmente com a revisão energética. Cada alteração fica em tbl_alteracoes_lbe."),
        ("10. Limitações conhecidas", "O consumo por uso é rateio (horas × kW) até 12/2026: os IDE por USE não mostram ganhos de eficiência das máquinas — por isso a melhoria dos compressores é verificada por medição dedicada (RG-SGE-11, IPMVP opção B)."),
    ])
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
