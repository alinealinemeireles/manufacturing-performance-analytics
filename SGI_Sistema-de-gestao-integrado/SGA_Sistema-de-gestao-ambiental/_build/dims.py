"""Dimensões partilhadas por todos os registos do SGA (chaves comuns para o modelo de dados)."""

# Processos / áreas da Plasticom (código, nome, tipo, máquinas do dataset, fase de ciclo de vida principal)
PROCESSOS = [
    ("REC", "Receção e armazenagem de matérias-primas", "Suporte", "—", "Aquisição"),
    ("ARQ", "Armazém de produtos químicos (tintas, solventes, óleos)", "Suporte", "—", "Produção"),
    ("INJ", "Injeção de tampas", "Produtivo", "IM-001 a IM-009", "Produção"),
    ("SOP", "Sopro de frascos (ISBM)", "Produtivo", "ISBM-001 a ISBM-010", "Produção"),
    ("SER", "Serigrafia (decoração)", "Produtivo", "SS-001, SS-002", "Produção"),
    ("HFS", "Hot foil stamping (decoração)", "Produtivo", "HF-001, HF-002", "Produção"),
    ("MOA", "Moagem e reintegração de scrap (regrind)", "Suporte", "Moinhos junto às máquinas", "Produção"),
    ("UTL", "Utilidades (ar comprimido, torre de arrefecimento, chiller, AVAC)", "Suporte", "CMP-01/02, TR-01, CH-01", "Produção"),
    ("MAN", "Manutenção (mecânica e elétrica)", "Suporte", "Oficina", "Produção"),
    ("PRS", "Parque de resíduos", "Suporte", "—", "Fim de vida"),
    ("EXP", "Embalagem, armazém de produto acabado e expedição", "Suporte", "—", "Distribuição"),
    ("LAB", "Laboratório de qualidade", "Suporte", "—", "Produção"),
    ("RD", "Design e desenvolvimento de produto (R&D)", "Gestão", "—", "Design e Conceção"),
    ("CMP", "Compras e fornecedores", "Gestão", "—", "Aquisição"),
    ("ADM", "Administrativos e gestão", "Gestão", "—", "Produção"),
    ("GER", "Geral (toda a instalação)", "Transversal", "—", "Produção"),
]
PROC_CODES = [p[0] for p in PROCESSOS]
PROC_NAME = {p[0]: p[1] for p in PROCESSOS}

# Funções (código, designação, área)
FUNCOES = [
    ("FUN-01", "Diretor Geral (Gestão de Topo)", "ADM"),
    ("FUN-02", "Diretor Industrial", "ADM"),
    ("FUN-03", "Gestor do SGA / EHS (Responsável Ambiental)", "ADM"),
    ("FUN-04", "Gerente de Produção", "ADM"),
    ("FUN-05", "Gerente de Manutenção", "MAN"),
    ("FUN-06", "Gerente da Qualidade", "LAB"),
    ("FUN-07", "Responsável de Armazém e Logística", "EXP"),
    ("FUN-08", "Responsável de Compras", "CMP"),
    ("FUN-09", "Responsável de R&D", "RD"),
    ("FUN-10", "Responsável de Recursos Humanos", "ADM"),
    ("FUN-11", "Diretor Financeiro", "ADM"),
    ("FUN-12", "Operador de Serigrafia", "SER"),
    ("FUN-13", "Operador de Injeção", "INJ"),
    ("FUN-14", "Operador de Sopro (ISBM)", "SOP"),
    ("FUN-15", "Operador de Hot Foil", "HFS"),
    ("FUN-16", "Técnico de Manutenção", "MAN"),
    ("FUN-17", "Técnico de Utilidades", "UTL"),
    ("FUN-18", "Operador de Armazém / Empilhador", "REC"),
    ("FUN-19", "Chefe de Turno", "GER"),
    ("FUN-20", "Auditor Interno do SGA", "ADM"),
    ("FUN-21", "Representante dos Trabalhadores (SST/Ambiente)", "GER"),
    ("FUN-22", "Técnico de Qualidade/Ambiente", "LAB"),
]
FUNC_NAMES = [f[1] for f in FUNCOES]

# Cláusulas da ISO 14001:2026 (estrutura harmonizada 2.ª versão)
CLAUSULAS = [
    ("4.1", "Compreender a organização e o seu contexto (inclui condições ambientais: clima, poluição, recursos, biodiversidade, ecossistemas)"),
    ("4.2", "Necessidades e expectativas das partes interessadas"),
    ("4.3", "Âmbito do SGA (com perspetiva de ciclo de vida)"),
    ("4.4", "Sistema de gestão ambiental"),
    ("5.1", "Liderança e compromisso"),
    ("5.2", "Política ambiental"),
    ("5.3", "Funções, responsabilidades e autoridades"),
    ("6.1.1", "Ações para tratar riscos e oportunidades — Generalidades"),
    ("6.1.2", "Aspetos ambientais (incl. situações de emergência potenciais)"),
    ("6.1.3", "Obrigações de conformidade"),
    ("6.1.4", "Riscos e oportunidades"),
    ("6.1.5", "Planeamento de ações"),
    ("6.2", "Objetivos ambientais e planeamento para os atingir"),
    ("6.3", "Planeamento de alterações"),
    ("7.1", "Recursos"),
    ("7.2", "Competência"),
    ("7.3", "Consciencialização"),
    ("7.4", "Comunicação"),
    ("7.5", "Informação documentada"),
    ("8.1", "Planeamento e controlo operacional (incl. processos, produtos e serviços de fornecedores externos)"),
    ("8.2", "Preparação e resposta a emergências"),
    ("9.1.1", "Monitorização, medição, análise e avaliação — Generalidades"),
    ("9.1.2", "Avaliação da conformidade"),
    ("9.2", "Auditoria interna"),
    ("9.3", "Revisão pela gestão (9.3.1 Generalidades, 9.3.2 Entradas, 9.3.3 Resultados)"),
    ("10.1", "Melhoria contínua"),
    ("10.2", "Não conformidade e ação corretiva"),
]
CLAUSE_CODES = [c[0] for c in CLAUSULAS]
CLAUSE_LABELS = [f"{c} {t.split(' (')[0]}" for c, t in CLAUSULAS]

FASES_CV = ["Aquisição", "Design e Conceção", "Produção", "Distribuição", "Uso (Consumidor Final)", "Fim de Vida"]
ESG = ["E", "E + S", "E + G", "E + S + G", "S + G"]
TEMAS = ["Energia", "Água e efluentes", "Resíduos", "Emissões atmosféricas / COV", "Clima / GEE",
         "Materiais e circularidade", "Produtos químicos", "Ruído", "Solo e águas subterrâneas",
         "Biodiversidade e ecossistemas", "Perdas de granulado (microplásticos)", "Emergência",
         "Legal / conformidade", "Governação e dados", "Cadeia de valor / fornecedores", "Produto / embalagem"]
