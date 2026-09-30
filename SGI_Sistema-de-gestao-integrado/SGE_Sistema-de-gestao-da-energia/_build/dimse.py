"""Dimensões partilhadas por todos os registos do SGE (chaves comuns do modelo de dados).

Os códigos de uso de energia são os MESMOS da base ambiental do SGA (envdata.py / RG-SGA-13: INJ, SOP, SER, HFS, UTL-AR,
UTL-FRIO, GER) para que SGE e SGA se juntem no SGI pelo mesmo código; o SGE acrescenta os usos de gasóleo (FRO, GER-EMG).
"""
import datetime as dt

# Usos de energia (código, uso, tipo de energia, processo SGA, equipamentos, variável relevante candidata)
USOS = [
    ("SOP", "Sopro de frascos (ISBM): aquecimento de pré-formas, sopro, hidráulica", "Eletricidade", "SOP", "ISBM-001 a ISBM-010", "Horas de marcha; unidades produzidas"),
    ("INJ", "Injeção de tampas e potes: aquecimento do canhão, hidráulica/servo, extração", "Eletricidade", "INJ", "IM-001 a IM-009", "Horas de marcha; unidades produzidas"),
    ("UTL-AR", "Ar comprimido (compressores CMP-01/02 de velocidade variável desde 02/2026, secadores)", "Eletricidade", "UTL", "CMP-01, CMP-02", "Procura de ar das máquinas; fugas"),
    ("UTL-FRIO", "Arrefecimento de moldes e óleo (chiller CH-01, torre TR-01, bombas)", "Eletricidade", "UTL", "CH-01, TR-01, bombas de circulação", "Carga térmica dos moldes; temperatura exterior"),
    ("GER", "Serviços gerais: iluminação, AVAC, escritórios, armazéns, laboratório", "Eletricidade", "GER", "QGBT serviços", "Temperatura exterior; dias úteis"),
    ("SER", "Serigrafia (decoração) com cura UV/IR", "Eletricidade", "SER", "SS-001, SS-002", "Horas de marcha"),
    ("HFS", "Hot foil stamping (decoração)", "Eletricidade", "HFS", "HF-001, HF-002", "Horas de marcha"),
    ("FRO", "Frota: 2 viaturas de serviço e 1 carrinha", "Gasóleo rodoviário", "GER", "Viaturas VS-01, VS-02, CR-01", "km percorridos"),
    ("GER-EMG", "Gerador de emergência GE-01 (testes mensais)", "Gasóleo", "GER", "GE-01", "Horas de teste"),
]
USO_CODES = [u[0] for u in USOS]
USO_NAME = {u[0]: u[1] for u in USOS}
USOS_ELET = [u[0] for u in USOS if u[2] == "Eletricidade"]

TIPOS_ENERGIA = [
    # (código, tipo, origem, unidade de compra, fator kWh/unidade, kgep/unidade (Despacho 17313/2008), kgCO2e/unidade (SGCIE), kgCO2e/unidade (GEE, RG-SGA-19), dentro do âmbito)
    ("TE-01", "Eletricidade da rede (média tensão)", "Comercializador ENE-01 (RG-SGA-11); 55% com garantias de origem", "kWh", 1.0, 0.215, 0.47, 0.110, "Sim"),
    ("TE-02", "Gasóleo rodoviário (frota)", "Cartão de frota", "L", 10.0, 0.864, 2.68, 2.66, "Sim"),
    ("TE-03", "Gasóleo do gerador de emergência", "Fornecedor de combustíveis", "L", 10.0, 0.864, 2.68, 2.66, "Sim"),
    ("TE-04", "Eletricidade solar fotovoltaica de autoconsumo (UPAC ≈ 1 MWp)", "Produção própria — prevista 2027 (ALT-2026-07)", "kWh", 1.0, 0.215, 0.0, 0.0, "Futuro"),
    ("TE-05", "Ar comprimido (vetor energético produzido internamente)", "Produzido pelos compressores CMP-01/02", "Nm³", None, None, None, None, "Sim (vetor interno)"),
]

# Funções (código, designação, área) — os nomes coincidem com o SGA/SGQ quando existem lá
FUNCOES = [
    ("FE-01", "Diretor Geral (Gestão de Topo)", "GES"),
    ("FE-02", "Diretor Industrial", "GES"),
    ("FE-03", "Gestor(a) de Energia (líder da equipa de gestão de energia)", "UTL"),
    ("FE-04", "Gerente de Manutenção", "MAN"),
    ("FE-05", "Gerente de Produção", "PCP"),
    ("FE-06", "Técnico de Utilidades", "UTL"),
    ("FE-07", "Gestor do SGA / EHS (Responsável Ambiental)", "GES"),
    ("FE-08", "Gerente da Qualidade", "QUA"),
    ("FE-09", "Diretor Financeiro", "GES"),
    ("FE-10", "Responsável de Compras", "CMP"),
    ("FE-11", "Responsável de R&D", "RD"),
    ("FE-12", "Responsável de Recursos Humanos", "RH"),
    ("FE-13", "Gerente de Dados / TI", "TI"),
    ("FE-14", "Engenheiro(a) de Processo", "PCP"),
    ("FE-15", "Chefe de Turno", "PCP"),
    ("FE-16", "Operador de Injeção", "INJ"),
    ("FE-17", "Operador de Sopro (ISBM)", "SOP"),
    ("FE-18", "Operador de Serigrafia", "SER"),
    ("FE-19", "Operador de Hot Foil", "HFS"),
    ("FE-20", "Técnico de Manutenção", "MAN"),
    ("FE-21", "Auditor(a) Interno(a) do SGE", "QUA"),
    ("FE-22", "Responsável de Armazém e Logística", "EXP"),
]
FUNC_NAMES = [f[1] for f in FUNCOES]
F = {c: n for c, n, _ in FUNCOES}
DG, DIND, GE, GMAN, GPROD, TUTL, GSGA, GQ, DFIN, CMP_, RD_, RH_, TI_, EPROC, CTURNO = (F[f"FE-{i:02d}"] for i in range(1, 16))
AUD = F["FE-21"]

# Cláusulas da ISO 50001:2018 + Amd 1:2024 (texto NBR ISO 50001:2018 da pasta de interpretação, adaptado a PT-PT)
# (cláusula, título, informação documentada exigida: "Manter" / "Reter" / "—", alterada pela Amd 1:2024)
CLAUSULAS = [
    ("4.1", "Compreender a organização e o seu contexto", "—", "Sim"),
    ("4.2", "Compreender as necessidades e expectativas das partes interessadas", "—", "Sim"),
    ("4.3", "Determinar o âmbito do SGE", "Manter (âmbito e fronteiras)", "Não"),
    ("4.4", "Sistema de gestão da energia", "—", "Não"),
    ("5.1", "Liderança e compromisso", "—", "Não"),
    ("5.2", "Política energética", "Manter (disponível)", "Não"),
    ("5.3", "Funções, responsabilidades e autoridades (equipa de gestão de energia)", "—", "Não"),
    ("6.1", "Ações para tratar riscos e oportunidades", "—", "Não"),
    ("6.2", "Objetivos, metas energéticas e planeamento para os atingir", "Reter (objetivos, metas e planos de ação)", "Não"),
    ("6.3", "Revisão energética", "Manter (métodos e critérios); Reter (resultados)", "Não"),
    ("6.4", "Indicadores de desempenho energético (IDE)", "Manter (metodologia); Reter (valores dos IDE)", "Não"),
    ("6.5", "Linha de base energética (LBE)", "Reter (LBE, variáveis relevantes, alterações)", "Não"),
    ("6.6", "Planeamento da recolha de dados energéticos", "Reter (dados recolhidos; exatidão e repetibilidade)", "Não"),
    ("7.1", "Recursos", "—", "Não"),
    ("7.2", "Competência", "Reter (evidência de competência)", "Não"),
    ("7.3", "Consciencialização", "—", "Não"),
    ("7.4", "Comunicação (incl. sugestões de melhoria)", "Considerar reter (sugestões)", "Não"),
    ("7.5", "Informação documentada", "—", "Não"),
    ("8.1", "Planeamento e controlo operacional", "Manter (na medida necessária)", "Não"),
    ("8.2", "Projeto (design)", "Reter (atividades de projeto)", "Não"),
    ("8.3", "Aquisição (compras)", "—", "Não"),
    ("9.1.1", "Monitorização, medição, análise e avaliação — generalidades", "Reter (resultados; investigação de desvios significativos)", "Não"),
    ("9.1.2", "Avaliação da conformidade com requisitos legais e outros requisitos", "Reter (resultados e ações)", "Não"),
    ("9.2", "Auditoria interna", "Reter (programa e resultados)", "Não"),
    ("9.3", "Revisão pela gestão", "Reter (resultados)", "Não"),
    ("10.1", "Não conformidade e ação corretiva", "Reter (natureza, ações, resultados)", "Não"),
    ("10.2", "Melhoria contínua", "—", "Não"),
]
CLAUSE_CODES = [c[0] for c in CLAUSULAS]

# Máquinas do dataset (ID, processo, ano de instalação, tecnologia de acionamento — simulada coerente com o ano)
MAQUINAS = [
    ("ISBM-001", "SOP", 2023, "ISBM elétrica com recuperação de ar"), ("ISBM-002", "SOP", 2014, "ISBM hidráulica"),
    ("ISBM-003", "SOP", 2012, "ISBM hidráulica"), ("ISBM-004", "SOP", 2024, "ISBM elétrica com recuperação de ar"),
    ("ISBM-005", "SOP", 2011, "ISBM hidráulica"), ("ISBM-006", "SOP", 2015, "ISBM hidráulica"),
    ("ISBM-007", "SOP", 2018, "ISBM híbrida (servo)"), ("ISBM-008", "SOP", 2012, "ISBM hidráulica"),
    ("ISBM-009", "SOP", 2026, "ISBM elétrica com recuperação de ar"), ("ISBM-010", "SOP", 2026, "ISBM elétrica com recuperação de ar"),
    ("IM-001", "INJ", 2023, "Injetora totalmente elétrica"), ("IM-002", "INJ", 2011, "Injetora hidráulica de bomba fixa"),
    ("IM-003", "INJ", 2021, "Injetora servo-hidráulica"), ("IM-004", "INJ", 2012, "Injetora hidráulica de bomba fixa"),
    ("IM-005", "INJ", 2022, "Injetora servo-hidráulica"), ("IM-006", "INJ", 2022, "Injetora servo-hidráulica"),
    ("IM-007", "INJ", 2026, "Injetora totalmente elétrica"), ("IM-008", "INJ", 2026, "Injetora totalmente elétrica"),
    ("IM-009", "INJ", 2026, "Injetora totalmente elétrica (linha dedicada a contacto alimentar)"),
    ("SS-001", "SER", 2013, "Serigrafia com cura UV"), ("SS-002", "SER", 2013, "Serigrafia com cura UV"),
    ("HF-001", "HFS", 2023, "Hot foil"), ("HF-002", "HFS", 2021, "Hot foil"),
]
MAQ_NOVAS_2026 = ["ISBM-009", "ISBM-010", "IM-007", "IM-008", "IM-009"]   # alteração de fator estático (ALT-2026-03) em 07/2026
PROC_DATASET = {"Injection Molding": "INJ", "Blow Molding": "SOP", "Screen Printing": "SER", "Hot Foil Stamping": "HFS"}

MESES = [dt.date(2025, m, 1) for m in range(3, 13)] + [dt.date(2026, m, 1) for m in range(1, 13)]
N_LBE = 12   # meses do período de referência (mar/2025–fev/2026)

ESTADO = ["Conforme", "Parcial", "Lacuna"]
SIMNAO = ["Sim", "Não"]
