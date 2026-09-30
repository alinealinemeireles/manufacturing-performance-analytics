"""Dimensões partilhadas por todos os registos do SGQ (chaves comuns do modelo de dados).

Os códigos de processo produtivo e de suporte são os MESMOS do SGA (dims.py) para que SGQ e SGA se juntem
no SGI pelo mesmo código; o SGQ acrescenta os processos de gestão e de relação com o cliente que o SGA não usa.
"""

# (código, processo, tipo ISO 9001 (gestão / realização / suporte), dono (função), máquinas do dataset)
PROCESSOS = [
    ("GES", "Gestão estratégica e revisão pela gestão", "Gestão", "Diretor Geral (Gestão de Topo)", "—"),
    ("QUA", "Gestão da qualidade (SGQ, auditorias, melhoria, CAPA)", "Gestão", "Gerente da Qualidade", "—"),
    ("COM", "Comercial: requisitos do cliente, propostas, encomendas e satisfação", "Realização", "Diretor Comercial", "—"),
    ("RD", "Design e desenvolvimento de produto (R&D)", "Realização", "Responsável de R&D", "—"),
    ("PCP", "Planeamento e controlo da produção", "Realização", "Gerente de Produção", "—"),
    ("CMP", "Compras e gestão de fornecedores", "Realização", "Responsável de Compras", "—"),
    ("REC", "Receção, inspeção de receção e armazenagem de matérias-primas", "Realização", "Responsável de Armazém e Logística", "—"),
    ("INJ", "Injeção de tampas e potes", "Realização", "Gerente de Produção", "IM-001 a IM-008"),
    ("SOP", "Sopro de frascos (ISBM)", "Realização", "Gerente de Produção", "ISBM-001 a ISBM-010"),
    ("SER", "Serigrafia (decoração)", "Realização", "Gerente de Produção", "SS-001, SS-002"),
    ("HFS", "Hot foil stamping (decoração)", "Realização", "Gerente de Produção", "HF-001, HF-002"),
    ("LAB", "Controlo da qualidade e laboratório (inspeção, ensaios, libertação)", "Realização", "Gerente da Qualidade", "—"),
    ("EXP", "Embalagem, armazém de produto acabado e expedição", "Realização", "Responsável de Armazém e Logística", "—"),
    ("MAN", "Manutenção de máquinas e moldes", "Suporte", "Gerente de Manutenção", "Oficina e ferramentaria"),
    ("MET", "Metrologia (calibração, verificação e MSA)", "Suporte", "Gerente da Qualidade", "Laboratório"),
    ("RH", "Recursos humanos, competência e formação", "Suporte", "Responsável de Recursos Humanos", "—"),
    ("TI", "Sistemas de informação e dados (ERP, MES, data warehouse)", "Suporte", "Gerente de Dados / TI", "—"),
    ("DOC", "Controlo da informação documentada", "Suporte", "Gerente da Qualidade", "—"),
]
PROC_CODES = [p[0] for p in PROCESSOS]
PROC_NAME = {p[0]: p[1] for p in PROCESSOS}
PROC_DATASET = {"Injection Molding": "INJ", "Blow Molding": "SOP", "Screen Printing": "SER", "Hot Foil Stamping": "HFS"}

# Funções (código, designação, processo) — as 11 primeiras coincidem com o SGA (dims.FUNCOES) quando existem lá
FUNCOES = [
    ("FQ-01", "Diretor Geral (Gestão de Topo)", "GES"),
    ("FQ-02", "Diretor Industrial", "GES"),
    ("FQ-03", "Gerente da Qualidade", "QUA"),
    ("FQ-04", "Gerente de Produção", "PCP"),
    ("FQ-05", "Gerente de Manutenção", "MAN"),
    ("FQ-06", "Diretor Comercial", "COM"),
    ("FQ-07", "Responsável de Compras", "CMP"),
    ("FQ-08", "Responsável de R&D", "RD"),
    ("FQ-09", "Responsável de Armazém e Logística", "EXP"),
    ("FQ-10", "Responsável de Recursos Humanos", "RH"),
    ("FQ-11", "Gerente de Dados / TI", "TI"),
    ("FQ-12", "Técnico(a) da Qualidade / Inspetor(a)", "LAB"),
    ("FQ-13", "Técnico(a) de Laboratório", "LAB"),
    ("FQ-14", "Engenheiro(a) de Processo", "PCP"),
    ("FQ-15", "Chefe de Turno", "PCP"),
    ("FQ-16", "Operador(a) de Injeção", "INJ"),
    ("FQ-17", "Operador(a) de Sopro (ISBM)", "SOP"),
    ("FQ-18", "Operador(a) de Serigrafia", "SER"),
    ("FQ-19", "Operador(a) de Hot Foil", "HFS"),
    ("FQ-20", "Técnico(a) de Manutenção", "MAN"),
    ("FQ-21", "Técnico(a) de Metrologia", "MET"),
    ("FQ-22", "Auditor(a) Interno(a) do SGQ", "QUA"),
    ("FQ-23", "Gestor(a) de Cliente (Key Account)", "COM"),
    ("FQ-24", "Planeador(a) de Produção", "PCP"),
    ("FQ-25", "Operador(a) de Armazém / Empilhador", "EXP"),
    ("FQ-26", "Gestor do SGA / EHS (Responsável Ambiental)", "GES"),
]
FUNC_NAMES = [f[1] for f in FUNCOES]
F = {code: name for code, name, _ in FUNCOES}
DG, DIND, GQ, GPROD, GMAN, DCOM, CMP_, RD_, LOG, RH_, TI_ = (F[f"FQ-{i:02d}"] for i in range(1, 12))
INSP, TLAB, EPROC, CTURNO = F["FQ-12"], F["FQ-13"], F["FQ-14"], F["FQ-15"]

# Pessoas: nomes vindos do dataset (inspetores, técnicos de manutenção, operadores) + funções de gestão sem nome
# (ID, nome, função, processo, data de admissão, vínculo)
PESSOAS = [
    ("P-001", "Ana Silva", INSP, "LAB", "2016-03-01", "Efetivo"),
    ("P-002", "Beatriz Costa", INSP, "LAB", "2019-09-16", "Efetivo"),
    ("P-003", "Carlos Mendes", INSP, "LAB", "2014-02-03", "Efetivo"),
    ("P-004", "Diogo Ferreira", INSP, "LAB", "2021-05-10", "Efetivo"),
    ("P-005", "Elena Santos", "Técnico(a) de Laboratório", "LAB", "2012-10-01", "Efetivo"),
    ("P-006", "Sandra Reis", "Técnico(a) de Manutenção", "MAN", "2013-06-17", "Efetivo"),
    ("P-007", "Hugo Marques", "Técnico(a) de Manutenção", "MAN", "2018-01-08", "Efetivo"),
    ("P-008", "Patrícia Lima", "Técnico(a) de Manutenção", "MAN", "2015-04-20", "Efetivo"),
    ("P-009", "José Pinto", "Técnico(a) de Manutenção", "MAN", "2020-11-02", "Efetivo"),
    ("P-010", "Vitor Sousa", "Técnico(a) de Manutenção", "MAN", "2011-09-05", "Efetivo"),
    ("P-011", "Camila Duarte", "Técnico(a) de Manutenção", "MAN", "2022-02-14", "Efetivo"),
    ("P-012", "Rui Fonseca", "Técnico(a) de Manutenção", "MAN", "2010-07-12", "Efetivo"),
    ("P-013", "Marta Nogueira", "Técnico(a) de Manutenção", "MAN", "2017-03-27", "Efetivo"),
    ("OP-INJ-001", "OP-INJ-001", "Operador(a) de Injeção", "INJ", "2019-04-01", "Efetivo"),
    ("OP-INJ-002", "OP-INJ-002", "Operador(a) de Injeção", "INJ", "2021-01-11", "Efetivo"),
    ("OP-INJ-003", "OP-INJ-003", "Operador(a) de Injeção", "INJ", "2025-02-03", "Temporário"),
    ("OP-INJ-004", "OP-INJ-004", "Operador(a) de Injeção", "INJ", "2016-06-06", "Efetivo"),
    ("OP-INJ-005", "OP-INJ-005", "Operador(a) de Injeção", "INJ", "2026-06-15", "Temporário"),
    ("AUX-INJ-001", "AUX-INJ-001", "Operador(a) de Injeção", "INJ", "2024-09-02", "Efetivo"),
    ("OP-SOP-001", "OP-SOP-001", "Operador(a) de Sopro (ISBM)", "SOP", "2015-10-12", "Efetivo"),
    ("OP-SOP-002", "OP-SOP-002", "Operador(a) de Sopro (ISBM)", "SOP", "2018-05-21", "Efetivo"),
    ("OP-SOP-003", "OP-SOP-003", "Operador(a) de Sopro (ISBM)", "SOP", "2020-02-17", "Efetivo"),
    ("OP-SOP-004", "OP-SOP-004", "Operador(a) de Sopro (ISBM)", "SOP", "2023-03-06", "Efetivo"),
    ("OP-SOP-005", "OP-SOP-005", "Operador(a) de Sopro (ISBM)", "SOP", "2026-06-15", "Temporário"),
    ("OP-SOP-006", "OP-SOP-006", "Operador(a) de Sopro (ISBM)", "SOP", "2026-06-15", "Temporário"),
    ("OP-SK-001", "OP-SK-001", "Operador(a) de Serigrafia", "SER", "2014-09-01", "Efetivo"),
    ("OP-SK-002", "OP-SK-002", "Operador(a) de Serigrafia", "SER", "2025-11-03", "Temporário"),
    ("OP-HF-001", "OP-HF-001", "Operador(a) de Hot Foil", "HFS", "2017-01-16", "Efetivo"),
    ("OP-HF-002", "OP-HF-002", "Operador(a) de Hot Foil", "HFS", "2022-08-29", "Efetivo"),
]
PESSOA_IDS = [p[0] for p in PESSOAS]

# Cláusulas da ISO 9001:2026 (texto oficial em espanhol da pasta de interpretação, traduzido para PT-PT)
# (cláusula, título, novo/alterado em 2026, nota da alteração)
CLAUSULAS = [
    ("4.1", "Compreender a organização e o seu contexto", "Sim", "Determinar se as alterações climáticas são uma questão pertinente (Amd 1:2024 integrada); notas sobre contexto interno (valores, cultura, conhecimento)"),
    ("4.2", "Compreender as necessidades e expectativas das partes interessadas", "Sim", "Nota: as partes interessadas podem ter requisitos relacionados com as alterações climáticas"),
    ("4.3", "Determinar o âmbito do SGQ", "Não", ""),
    ("4.4", "Sistema de gestão da qualidade e respetivos processos", "Sim", "4.4.2 informação documentada 'disponível' (substitui manter/reter)"),
    ("5.1.1", "Liderança e compromisso — generalidades", "Sim", "i) promover a cultura da qualidade e o comportamento ético; l) prestar contas da eficácia do SGQ"),
    ("5.1.2", "Foco no cliente", "Não", ""),
    ("5.2", "Política da qualidade", "Sim", "Deve ter em conta o contexto e apoiar a orientação estratégica; 'disponível como informação documentada'"),
    ("5.3", "Funções, responsabilidades e autoridades", "Sim", "f) manter a integridade do SGQ, incluindo quando se planeiam e implementam alterações"),
    ("6.1.1", "Determinação de riscos e oportunidades", "Sim", "6.1 dividido em 6.1.1 / 6.1.2 / 6.1.3"),
    ("6.1.2", "Ações para tratar os riscos", "Sim", "Determinar, analisar e avaliar riscos; ações proporcionais; Nota 1 disrupção; Nota 2 opções de tratamento"),
    ("6.1.3", "Ações para tratar as oportunidades", "Sim", "Novo subcapítulo: determinar, analisar e avaliar oportunidades e avaliar a eficácia das ações"),
    ("6.2", "Objetivos da qualidade e planeamento para os atingir", "Não", ""),
    ("6.3", "Planeamento de alterações", "Sim", "Considerar também como monitorizar e avaliar a eficácia (f) e como rever os resultados (g)"),
    ("7.1.1", "Recursos — generalidades", "Não", ""),
    ("7.1.2", "Pessoas", "Não", ""),
    ("7.1.3", "Infraestrutura", "Sim", "Nota: trabalho presencial, remoto ou híbrido; TIC"),
    ("7.1.4", "Ambiente para a operação dos processos", "Sim", "Fatores sociais, psicológicos e físicos; influência da cultura da qualidade e do comportamento ético"),
    ("7.1.5.1", "Recursos de monitorização e medição — generalidades", "Não", ""),
    ("7.1.5.2", "Rastreabilidade da medição", "Não", ""),
    ("7.1.6", "Conhecimento organizacional", "Sim", "Nota com as formas do conhecimento (experiência, formação, métodos, sistemas digitais)"),
    ("7.2", "Competência", "Não", ""),
    ("7.3", "Consciencialização", "Sim", "e) cultura da qualidade organizacional e comportamento ético"),
    ("7.4", "Comunicação", "Não", ""),
    ("7.5", "Informação documentada", "Sim", "Terminologia única 'disponível' / 'disponível como evidência'"),
    ("8.1", "Planeamento e controlo operacional", "Não", ""),
    ("8.2.1", "Comunicação com o cliente", "Sim", "e) informação sobre ações de contingência, incluindo disrupções no fornecimento"),
    ("8.2.2", "Determinação dos requisitos relativos a produtos e serviços", "Não", ""),
    ("8.2.3", "Revisão dos requisitos relativos a produtos e serviços", "Não", ""),
    ("8.2.4", "Alterações aos requisitos de produtos e serviços", "Não", ""),
    ("8.3", "Design e desenvolvimento de produtos e serviços", "Sim", "Notas sobre abordagem iterativa (ciclos de revisão, verificação, validação)"),
    ("8.4", "Controlo dos processos, produtos e serviços de fornecedores externos", "Não", ""),
    ("8.5.1", "Controlo da produção e da prestação do serviço", "Não", "g) ações para prevenir o erro humano"),
    ("8.5.2", "Identificação e rastreabilidade", "Não", ""),
    ("8.5.3", "Propriedade dos clientes ou de fornecedores externos", "Não", ""),
    ("8.5.4", "Preservação", "Não", ""),
    ("8.5.5", "Atividades pós-entrega", "Não", ""),
    ("8.5.6", "Controlo de alterações", "Não", ""),
    ("8.6", "Libertação de produtos e serviços", "Não", ""),
    ("8.7", "Controlo de saídas não conformes", "Não", ""),
    ("9.1.1", "Monitorização, medição, análise e avaliação — generalidades", "Não", ""),
    ("9.1.2", "Satisfação do cliente", "Não", ""),
    ("9.1.3", "Análise e avaliação", "Sim", "e) e f) eficácia das ações para riscos e, separadamente, para oportunidades"),
    ("9.2", "Auditoria interna", "Sim", "Referência à ISO 19011 (edição 2026)"),
    ("9.3", "Revisão pela gestão", "Sim", "Entradas g) e h) separadas para riscos e oportunidades; alinhamento com a orientação estratégica"),
    ("10.1", "Melhoria contínua", "Sim", "Integra a antiga 10.1 geral; mudança incremental ou disruptiva, inovação"),
    ("10.2", "Não conformidade e ação corretiva", "Não", "Nota: as reclamações de clientes podem ser fonte de NC"),
]
CLAUSE_CODES = [c[0] for c in CLAUSULAS]

# Temas da qualidade para o contexto (RG-SGQ-01). Os temas partilhados com o SGA (dims.TEMAS) têm a MESMA grafia
# para que tbl_pestel / tbl_swot do SGQ e do SGA se juntem por tema no modelo do SGI.
TEMAS_Q = ["Cliente / mercado", "Produto / embalagem", "Legal / conformidade", "Cadeia de valor / fornecedores", "Processo / capacidade",
           "Pessoas / competências", "Conhecimento", "Infraestrutura / equipamentos", "Medição / metrologia", "Cultura da qualidade",
           "Custo da qualidade", "Governação e dados", "Clima / GEE"]
ESG = ["E", "E + S", "E + G", "E + S + G", "S + G", "S", "G"]   # mesmos valores do SGA + S e G isolados

MESES = [f"{y}-{m:02d}" for y, m in [(2025, m) for m in range(7, 13)] + [(2026, m) for m in range(1, 13)]]

SEG_PT = {"Skincare": "Cuidado da pele", "Fragrance": "Fragrâncias", "Personal Hygiene": "Higiene pessoal", "Haircare": "Cuidado capilar",
          "Color Cosmetics": "Maquilhagem", "Baby Care": "Cuidado infantil", "Food Packaging": "Embalagem alimentar", "Pharmaceutical": "Farmacêutico"}
