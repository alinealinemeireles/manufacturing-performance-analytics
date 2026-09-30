"""RG-SGQ-03 — Liderança, política da qualidade, funções e autoridades, cultura da qualidade e comportamento ético.
ISO 9001:2026 5.1.1 a)–l) (novo: i) cultura da qualidade e comportamento ético; l) prestar contas), 5.1.2, 5.2, 5.3 a)–f), 7.3 e).
Avaliação da cultura com base na ISO 10010:2022 (autoavaliação de maturidade)."""
from sgqlib import *
from dimsq import *

POLITICA = [
    "A Plasticom projeta e fabrica embalagens plásticas para cosmética, alimentar e farmacêutico. Para cumprir o nosso propósito — proteger o que os nossos clientes "
    "colocam nas mãos das pessoas — comprometemo-nos a:",
    "1. Cumprir os requisitos dos clientes e os requisitos legais e regulamentares aplicáveis aos nossos produtos, incluindo os de materiais em contacto com alimentos e de embalagem farmacêutica.",
    "2. Fazer bem à primeira: controlar os processos pela variação (capacidade, SPC e prevenção do erro humano) e não pela inspeção.",
    "3. Ouvir o cliente — reclamações, satisfação e requisitos futuros — e responder com rapidez e transparência, incluindo em situações de disrupção.",
    "4. Escolher e desenvolver fornecedores que partilhem estes compromissos.",
    "5. Promover uma cultura da qualidade e um comportamento ético em que ninguém é pressionado a libertar produto duvidoso e em que relatar um problema é reconhecido.",
    "6. Gerir riscos e oportunidades, incluindo os associados às alterações climáticas, para garantir a continuidade do fornecimento.",
    "7. Melhorar continuamente a eficácia do sistema de gestão da qualidade, com objetivos mensuráveis revistos pela gestão.",
    "Esta política é comunicada a todos os colaboradores, está disponível às partes interessadas em plasticom.pt e é revista anualmente na revisão pela gestão.",
    "Marinha Grande, 28 de setembro de 2026 — Diretor Geral",
]

REQ_POL = [
    ("5.2.1 a)", "Apropriada ao propósito e ao contexto da organização", "Propósito e setores explícitos na introdução", "Evidenciado"),
    ("5.2.1 b)", "Proporciona um enquadramento para os objetivos da qualidade", "Cada objetivo OBJ-Q-nn liga a um compromisso (RG-SGQ-05 coluna Compromisso_Politica)", "Evidenciado"),
    ("5.2.1 c)", "Inclui o compromisso de cumprir os requisitos aplicáveis", "Compromisso 1", "Evidenciado"),
    ("5.2.1 d)", "Inclui o compromisso de melhoria contínua do SGQ", "Compromisso 7", "Evidenciado"),
    ("5.2.1 e)", "Tem em conta o contexto e apoia a orientação estratégica (novo 2026)", "Compromissos 1, 5 e 6 ligados às fatores PESQ-01, SWTQ-W02 e PESQ-06/07 (RG-SGQ-01)", "Evidenciado"),
    ("5.2.2 a)", "Disponível como informação documentada", "POL-SGQ-01 rev. 01 na lista mestra (RG-SGQ-08)", "Evidenciado"),
    ("5.2.2 b)", "Comunicada dentro da organização", "Afixada nos 4 pavilhões; sessão de consciencialização CON-26-01 (RG-SGQ-07)", "Evidenciado"),
    ("5.2.2 c)", "Disponível às partes interessadas, conforme apropriado", "Publicada no site; anexa aos acordos de qualidade", "Evidenciado"),
    ("5.2.2 d)", "Implementada, compreendida e aplicada", "Entrevistas na auditoria AUD-Q-26-03: 7 de 10 operadores explicam o compromisso 2", "Parcial"),
]

# 5.1.1 e 5.1.2 (ID, alínea, compromisso, como a gestão de topo o demonstra, evidência, responsável, estado, frequência)
LIDER = [
    ("LID-01", "5.1.1 a)", "Política e objetivos estabelecidos e compatíveis com a estratégia", "Aprovação da política e dos objetivos 2026 na revisão pela gestão", "Ata RPG-2026-01; RG-SGQ-05", DG, "Evidenciado", "Anual"),
    ("LID-02", "5.1.1 b)", "Integração dos requisitos do SGQ nos processos de negócio", "Revisão de requisitos no ERP bloqueia encomendas sem especificação aprovada; KPI da qualidade no bónus da chefia", "RG-SGQ-10; sistema de incentivos 2026", DG, "Parcial", "Anual"),
    ("LID-03", "5.1.1 c)", "Recursos necessários disponíveis", "Orçamento 2026: visão artificial HF-001, 2 inspetores adicionais no pico, calibração acreditada", "Orçamento 2026; decisões RPG-2026-01 D03–D05", DG, "Evidenciado", "Anual"),
    ("LID-04", "5.1.1 d)", "Comunicar a importância de uma gestão da qualidade eficaz", "Reunião trimestral com todos os turnos; mensagem do DG no lançamento das linhas alimentar/farma", "Atas das reuniões gerais T1–T3/2026", DG, "Evidenciado", "Trimestral"),
    ("LID-05", "5.1.1 e)", "Assegurar que o SGQ atinge os resultados pretendidos", "Painel mensal de KPI revisto no comité de direção", "RG-SGQ-05 Painel; atas do comité", DIND, "Evidenciado", "Mensal"),
    ("LID-06", "5.1.1 f)", "Envolver, orientar e apoiar as pessoas", "Gemba walks semanais da direção (tbl_gemba); caixa de sugestões com resposta em 15 dias", "RG-SGQ-03 tbl_gemba; RG-SGQ-19 sugestões", DIND, "Evidenciado", "Semanal"),
    ("LID-07", "5.1.1 g)", "Promover a melhoria contínua", "Patrocínio dos projetos DMAIC IM-002, SMED e visão artificial", "RG-SGQ-19 tbl_projetos", DG, "Evidenciado", "Trimestral"),
    ("LID-08", "5.1.1 h)", "Apoiar outras funções de gestão a demonstrar liderança", "Chefes de turno com objetivos de qualidade e formação em liderança de equipas", "RG-SGQ-07 FOR-Q-12", DIND, "Parcial", "Semestral"),
    ("LID-09", "5.1.1 i)", "Promover a cultura da qualidade e o comportamento ético (novo 2026)", "Código de conduta com cláusula 'nunca libertar produto duvidoso'; canal de relato; avaliação ISO 10010 da cultura", "RG-SGQ-03 tbl_cultura, tbl_relatos_etica", DG, "Parcial", "Semestral"),
    ("LID-10", "5.1.1 j)", "Promover a abordagem por processos", "Donos de processo nomeados com KPI (RG-SGQ-02)", "RG-SGQ-02 tbl_processos", GQ, "Evidenciado", "Anual"),
    ("LID-11", "5.1.1 k)", "Promover o pensamento baseado em riscos e em oportunidades", "Registo de riscos corporativo único com donos de risco da direção", "RG-SGA-02; RG-SGQ-04", DG, "Evidenciado", "Trimestral"),
    ("LID-12", "5.1.1 l)", "Prestar contas pela eficácia do SGQ", "DG assina a conclusão sobre a eficácia do SGQ na ata da revisão pela gestão", "RG-SGQ-17 Ata", DG, "Evidenciado", "Anual"),
    ("LID-13", "5.1.2 a)", "Requisitos do cliente e legais determinados, compreendidos e cumpridos", "Revisão de requisitos antes de cada encomenda; matriz de requisitos por cliente", "RG-SGQ-10", DCOM, "Evidenciado", "Por encomenda"),
    ("LID-14", "5.1.2 b)", "Riscos e oportunidades que afetam a conformidade e a satisfação determinados", "Riscos R16, R21 e O12 com dono na direção", "RG-SGQ-04", DG, "Evidenciado", "Trimestral"),
    ("LID-15", "5.1.2 c)", "Foco no aumento da satisfação do cliente", "Inquérito semestral; objetivo de CSI e NPS; visita anual aos 5 maiores clientes", "RG-SGQ-15; RG-SGQ-05 OBJ-Q-06", DCOM, "Evidenciado", "Semestral"),
]

AUTORIDADES = [
    ("AUT-01", "5.3 a)", "Assegurar que o SGQ está conforme com a ISO 9001:2026", GQ, "Nomeação escrita do DG (02/01/2026)"),
    ("AUT-02", "5.3 b)", "Reportar o desempenho do SGQ à gestão de topo", GQ, "Relatório mensal de KPI e entradas da revisão pela gestão"),
    ("AUT-03", "5.3 c)", "Assegurar que os processos produzem as saídas pretendidas", "Donos de processo (RG-SGQ-02)", "Descrição de funções atualizada em 2026"),
    ("AUT-04", "5.3 d)", "Promover o foco no cliente em toda a organização", DCOM, "Descrição de funções"),
    ("AUT-05", "5.3 e)", "Reportar oportunidades de melhoria", GQ, "Revisão pela gestão; carteira de projetos"),
    ("AUT-06", "5.3 f)", "Manter a integridade do SGQ quando se planeiam e implementam alterações", GQ, "Aprovação obrigatória no pedido de alteração MOC (RG-SGQ-06)"),
    ("AUT-07", "8.6 / 8.7", "Autoridade para libertar lotes e decidir sobre saídas não conformes", "Técnico(a) da Qualidade / Inspetor(a) (lotes conformes); Gerente da Qualidade (concessões)", "Matriz de autoridades de libertação"),
    ("AUT-08", "8.7", "Autoridade para parar a linha por problema de qualidade", "Qualquer operador ou inspetor (andon)", "Instrução IT-GER-01 'Parar para corrigir'"),
    ("AUT-09", "8.7.1 d)", "Autoridade para pedir concessão ao cliente", DCOM + " + " + GQ, "Formulário de concessão; aceitação escrita do cliente"),
]

RACI_ATIV = [
    ("Rever a política e os objetivos da qualidade", {"DG": "A", "DIND": "R", "GQ": "R", "GPROD": "C", "DCOM": "C", "RH": "I"}),
    ("Revisão de requisitos e aceitação de encomendas", {"DCOM": "A", "KAM": "R", "GQ": "C", "GPROD": "C", "RD": "C"}),
    ("Design e desenvolvimento de novos produtos", {"DIND": "A", "RD": "R", "GQ": "C", "GPROD": "C", "DCOM": "C", "CMP": "C"}),
    ("Aprovação e avaliação de fornecedores", {"CMP": "A", "GQ": "R", "RD": "C", "DIND": "I"}),
    ("Planeamento da produção", {"GPROD": "A", "PLAN": "R", "DCOM": "C", "GMAN": "C"}),
    ("Setup e arranque de ordem de fabrico", {"GPROD": "A", "CT": "R", "OPER": "R", "INSP": "C"}),
    ("Inspeção e libertação de lote", {"GQ": "A", "INSP": "R", "GPROD": "I", "LOG": "I"}),
    ("Decisão sobre saída não conforme / concessão", {"GQ": "A", "INSP": "R", "DCOM": "C", "GPROD": "C", "DG": "I"}),
    ("Tratamento de reclamação de cliente (8D)", {"GQ": "A", "KAM": "R", "INSP": "C", "GPROD": "C", "DCOM": "I"}),
    ("Calibração e MSA", {"GQ": "A", "TMET": "R", "INSP": "C"}),
    ("Planeamento de alterações (MOC)", {"DIND": "A", "GQ": "R", "EPROC": "R", "RD": "C", "DCOM": "C", "RH": "C"}),
    ("Auditoria interna", {"GQ": "A", "AUD": "R", "DG": "I"}),
    ("Revisão pela gestão", {"DG": "A", "GQ": "R", "DIND": "R", "DCOM": "C", "CMP": "C", "RH": "C"}),
    ("Formação e avaliação de competências", {"RH": "A", "GPROD": "R", "GQ": "C", "OPER": "I"}),
    ("Manutenção de máquinas e moldes", {"GMAN": "A", "TMAN": "R", "GPROD": "C", "GQ": "I"}),
    ("Controlo de documentos e registos", {"GQ": "A", "DOC": "R", "TI": "C"}),
]
# colunas de função com os MESMOS nomes do RG-SGA-08 tbl_raci quando a função existe nos dois sistemas; as funções só do SGQ vêm depois
RACI_COLS = [("Diretor_Geral", "DG", DG), ("Diretor_Industrial", "DIND", DIND), ("Gerente_Producao", "GPROD", GPROD), ("Gerente_Manutencao", "GMAN", GMAN),
             ("Gerente_Qualidade", "GQ", GQ), ("Resp_Armazem_Logistica", "LOG", LOG), ("Resp_Compras", "CMP", CMP_), ("Resp_RD", "RD", RD_), ("Resp_RH", "RH", RH_),
             ("Chefes_Turno", "CT", CTURNO), ("Operadores", "OPER", "Operadores"),
             ("Diretor_Comercial", "DCOM", DCOM), ("Gestor_Cliente_KAM", "KAM", "Gestor(a) de Cliente (Key Account)"), ("Planeador_Producao", "PLAN", "Planeador(a) de Produção"),
             ("Gerente_Dados_TI", "TI", TI_), ("Engenheiro_Processo", "EPROC", EPROC), ("Inspetores_Qualidade", "INSP", INSP),
             ("Tecnico_Metrologia", "TMET", "Técnico(a) de Metrologia"), ("Tecnico_Manutencao", "TMAN", "Técnico(a) de Manutenção"),
             ("Auditor_Interno_SGQ", "AUD", "Auditor(a) Interno(a) do SGQ"), ("Gestor_Documental", "DOC", "Gestor(a) documental")]
RACI_CLAUSULA = ["5.2; 6.2", "8.2", "8.3", "8.4", "8.1; 8.5.1", "8.5.1", "8.6", "8.7", "9.1.2; 10.2", "7.1.5", "6.3; 8.5.6", "9.2", "9.3", "7.2; 7.3", "7.1.3", "7.5"]

# ISO 10010:2022 — autoavaliação da cultura da qualidade (jun/2026, escala 1–5, média das respostas por área)
DIM_CULT = [
    ("CUL-01", "Propósito, visão e valores partilhados", "As pessoas conhecem o propósito e os valores e agem de acordo"),
    ("CUL-02", "Liderança e exemplo da gestão", "A gestão decide a favor da qualidade mesmo sob pressão de prazo"),
    ("CUL-03", "Foco no cliente", "Cada pessoa sabe quem é o cliente do seu trabalho e o que ele valoriza"),
    ("CUL-04", "Envolvimento e empoderamento das pessoas", "As pessoas podem parar a linha e propor melhorias"),
    ("CUL-05", "Decisões baseadas em evidência", "Decisões apoiadas em dados (SPC, AQL, KPI) e não em opinião"),
    ("CUL-06", "Aprendizagem e melhoria", "Os erros são analisados pela causa do sistema e as lições partilhadas"),
    ("CUL-07", "Comportamento ético e integridade", "Ninguém é pressionado a aceitar, registar ou libertar algo não conforme"),
    ("CUL-08", "Comunicação aberta", "Os problemas sobem rapidamente sem medo de culpa"),
]
AREAS = ["Produção", "Qualidade", "Manutenção", "Comercial", "Logística"]
# médias por área (Produção, Qualidade, Manutenção, Comercial, Logística)
NOTAS = {"CUL-01": (3.1, 3.9, 3.4, 3.8, 3.2), "CUL-02": (2.6, 3.3, 3.0, 3.4, 2.9), "CUL-03": (2.9, 3.8, 2.8, 4.2, 3.3),
         "CUL-04": (2.7, 3.6, 3.3, 3.5, 2.8), "CUL-05": (3.0, 4.1, 3.5, 3.1, 2.7), "CUL-06": (2.5, 3.2, 3.1, 3.0, 2.6),
         "CUL-07": (2.8, 3.4, 3.5, 3.6, 3.1), "CUL-08": (2.4, 3.3, 3.0, 3.4, 2.7)}
N_RESP = (96, 12, 14, 9, 18)

GEMBA = [
    ("GW-26-01", "2026-06-03", DG, "SOP", "Arranque da linha farmacêutica ISBM-009", "Instruções da linha nova ainda em rascunho no posto", "Aprovar IT-SOP-03 antes da produção de série", "MOC-Q-26-03"),
    ("GW-26-02", "2026-06-17", DIND, "INJ", "Turno 2 — passagem de turno", "Passagem verbal, sem registo do estado dos moldes", "Checklist de passagem de turno", "PAQ-26-08"),
    ("GW-26-03", "2026-07-01", GQ, "LAB", "Libertação de lotes no pico", "Fila de lotes a aguardar decisão; pressão para libertar sem leak test", "Reforçar inspetor no turno 2 em jul–nov", "RPG-2026-01 D04"),
    ("GW-26-04", "2026-07-15", DG, "EXP", "Expedição — reclamações de produto trocado", "Etiquetas manuais sem leitura de código de barras na carga", "Leitura obrigatória na carga (poka-yoke)", "CAPA-Q-26-02"),
    ("GW-26-05", "2026-07-29", DIND, "SER", "SS-001 — aderência", "Ensaio de aderência feito só no fim do lote", "Ensaio no arranque + meio do lote", "PC-DEC-01 rev. 03"),
    ("GW-26-06", "2026-08-12", GQ, "REC", "Receção de resina SUP-005", "Lote em quarentena usado por engano (etiqueta caída)", "Zona de quarentena fechada e bloqueio no ERP", "CAPA-Q-26-05"),
    ("GW-26-07", "2026-08-26", DG, "INJ", "Novas máquinas IM-007/IM-008", "Operador temporário sozinho na IM-008 sem validação", "Tutor obrigatório até validação no posto", "RG-SGQ-07"),
    ("GW-26-08", "2026-09-09", DCOM, "LAB", "Visita com cliente CUST-017 (farma)", "Cliente pediu evidência do ensaio do anel de inviolabilidade por lote", "Anexar resultado ao certificado de lote", "RG-SGQ-13"),
    ("GW-26-09", "2026-09-23", DIND, "MAN", "Moldes — contadores de ciclos", "Contadores não registados no MES", "Integrar contadores (O2)", "O2"),
    ("GW-26-10", "2026-10-07", GQ, "COM", "Revisão de encomendas após CAPA-Q-26-13", "Checklist no ERP usada em todas as encomendas observadas", "Manter; medir exceções mensalmente", "CAPA-Q-26-13"),
    ("GW-26-11", "2026-10-21", DG, "SOP", "Pico de encomendas — linhas ISBM-009/010", "Peso fora do alvo no arranque do turno 3; ajuste sem registo", "Registo obrigatório de ajustes no MES", "CON-Q-26-18"),
    ("GW-26-12", "2026-11-04", DIND, "LAB", "Libertação de lotes com o 2.º inspetor", "Fila de lotes reduzida para < 4 h", "Manter reforço até ao fim do pico", "MOC-Q-26-14"),
    ("GW-26-13", "2026-11-18", DCOM, "EXP", "Leitura de código de barras na carga", "Poka-yoke em uso; 0 trocas de produto em nov", "Estender à expedição de amostras", "CAPA-Q-26-02"),
    ("GW-26-14", "2026-12-02", GQ, "REC", "Receção de PP/PVC do fornecedor alternativo", "Certificados por lote completos; zona de quarentena fechada", "Qualificação concluída", "RG-SGQ-12"),
    ("GW-26-15", "2026-12-16", DG, "INJ", "Balanço do ano nas IM-007/008", "Operadores validados; instruções no HMI (SUG-26-07)", "Partilhar prática com a injeção antiga", "SUG-26-07"),
]

RELATOS = [
    ("REL-26-01", "2026-03-11", "Pressão para libertar", "Chefe de turno pediu para registar o lote como aprovado antes do fim do leak test para cumprir a expedição.", "Anónimo", "Investigado",
     "Confirmado. Lote retido até ensaio; conversa com a chefia; regra 'sem ensaio, sem etiqueta verde' reforçada.", "Fechado"),
    ("REL-26-02", "2026-05-06", "Registo incorreto", "Medições de peso copiadas do turno anterior num posto do sopro.", "Inspetor(a)", "Investigado",
     "Confirmado num posto (ISBM-006). Formação em integridade de dados; recolha automática do peso da balança para o MES (O3).", "Fechado"),
    ("REL-26-03", "2026-07-22", "Concessão sem autorização", "Lote de tampas com rosca marginal expedido 'por concessão' sem acordo do cliente.", "Gestor(a) de cliente", "Investigado",
     "Confirmado. Cliente informado (8.7.1 c); concessão formal obtida a posteriori; autoridades de concessão clarificadas (AUT-09).", "Fechado"),
    ("REL-26-04", "2026-09-15", "Segurança do produto", "Operador relatou fragmento de palete de madeira perto da linha alimentar.", "Operador(a)", "Em análise",
     "Zona de embalagem alimentar a rever (AMB-04); reconhecimento público do relato.", "Aberto"),
]


def build(out):
    b = Book("RG-SGQ-03", "Liderança, Política da Qualidade, Funções e Cultura da Qualidade",
             activities="Evidenciar a liderança e o compromisso da gestão de topo, a política da qualidade, as funções e autoridades e o estado da cultura da qualidade e do comportamento ético.",
             clauses="5.1.1 a)–l) (2026: i) cultura da qualidade e comportamento ético; l) prestar contas); 5.1.2 Foco no cliente; 5.2 Política da qualidade; 5.3 a)–f); 7.3 e) consciencialização da cultura e ética; 7.1.4",
             purpose="Registo único das evidências de liderança exigidas pela ISO 9001:2026, da política da qualidade aprovada (disponível como informação documentada), da matriz RACI e de autoridades, da autoavaliação da cultura da qualidade (ISO 10010) por área, das gemba walks da direção e do canal de relatos de integridade.",
             links=[("RG-SGQ-05", "Objetivos ligados aos compromissos da política."), ("RG-SGQ-07", "Sessões de consciencialização sobre política, cultura e ética (7.3)."),
                    ("RG-SGQ-17", "A revisão pela gestão avalia a cultura (tbl_cultura) e as evidências de liderança.")],
             guidance=[("ISO 10010:2022 — Quality culture", "Autoavaliação da maturidade da cultura por dimensão e área (tbl_cultura), com lacuna face à meta e ações."),
                       ("ISO/TC 176 APG — Top management / Policy and objectives", "O auditor entrevista a gestão de topo e procura evidência de envolvimento direto (não delegado): LID-nn com evidência objetiva."),
                       ("Academy — cap. 10–13 (Liderança, Ética ASQ)", "Código de ética e cultura justa: relatos de integridade tratados como falha do sistema.")])
    b.add_list("Estado", ["Evidenciado", "Parcial", "Por evidenciar"])
    b.add_list("Funcao", FUNC_NAMES + ["Donos de processo (RG-SGQ-02)"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("RACI", ["R", "A", "C", "I"])
    b.add_list("TipoRelato", ["Pressão para libertar", "Registo incorreto", "Concessão sem autorização", "Segurança do produto", "Outro"])
    b.add_list("EstadoRel", ["Aberto", "Fechado"])
    b.add_list("Area", AREAS)

    ws = b.sheet("Politica_Qualidade", "Política da qualidade POL-SGQ-01 rev. 01 (formato de afixação) — 5.2.", tab_color="1F4E5F")
    doc_header(ws, "POL-SGQ-01", "POLÍTICA DA QUALIDADE", "POL-SGQ-01", 6)
    ws.column_dimensions["A"].width = 24
    for L in "BCDEF":
        ws.column_dimensions[L].width = 22
    for k, t in enumerate(POLITICA):
        c = form_block(ws, 5 + k, "" if 0 < k < len(POLITICA) - 2 else ("Propósito" if k == 0 else ("Divulgação" if k == len(POLITICA) - 2 else "Aprovação")), t, vw=5,
                       height=48 if k == 0 else 32, bold_value=(0 < k < len(POLITICA) - 2))
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    pcols = [col("Requisito", 9, key="PK", desc="Alínea da ISO 9001:2026."), col("Descricao", 46, desc="O que a política deve cumprir."),
             col("Evidencia", 60, desc="Onde/como está cumprido."), col("Estado", 12, dv="Estado", desc="Estado da evidência.")]
    b.table("Verificacao_Politica", "tbl_verif_politica", pcols, [dict(zip(input_names(pcols), r)) for r in REQ_POL],
            "Verificação da política face a 5.2.1 a)–e) e 5.2.2 a)–d).", title="VERIFICAÇÃO DA POLÍTICA DA QUALIDADE (5.2)",
            cf=[("Estado", {"Evidenciado": "green", "Parcial": "orange", "Por": "red"})], row_height=30)

    lcols = [col("ID", 7, key="PK", desc="ID da evidência de liderança."), col("Alinea", 8, desc="5.1.1 a)–l) ou 5.1.2 a)–c)."),
             col("Compromisso", 40, desc="O que a norma exige da gestão de topo."), col("Como_Demonstra", 50, desc="Como a gestão de topo o demonstra na Plasticom."),
             col("Evidencia", 34, desc="Evidência objetiva (registo, ata)."), col("Responsavel", 24, dv="Funcao", desc="Membro da gestão de topo."),
             col("Estado", 12, dv="Estado", desc="Estado da evidência."), col("Frequencia", 11, desc="Frequência."),
             col("Novo_2026", 8, f='=IF(OR(@Alinea@="5.1.1 i)",@Alinea@="5.1.1 l)"),"Sim","Não")', desc="Requisito novo na edição 2026.")]
    b.table("Lideranca_Compromisso", "tbl_lideranca", lcols, rows_from(input_names(lcols), LIDER),
            "Evidências de liderança e compromisso (5.1.1 a–l) e de foco no cliente (5.1.2 a–c).",
            title="LIDERANÇA E COMPROMISSO DA GESTÃO DE TOPO (5.1)", subtitle="ISO 9001:2026 acrescenta i) cultura da qualidade e comportamento ético e l) prestar contas pela eficácia",
            cf=[("Estado", {"Evidenciado": "green", "Parcial": "orange", "Por": "red"}), ("Novo_2026", {"Sim": "blue"})], row_height=45)

    acols = [col("ID", 7, key="PK", desc="ID da autoridade."), col("Referencia", 9, desc="Cláusula."), col("Responsabilidade_Autoridade", 50, desc="Responsabilidade e autoridade atribuída."),
             col("Atribuida_a", 36, desc="Função."), col("Evidencia_Atribuicao", 40, desc="Como foi atribuída e comunicada.")]
    b.table("Funcoes_Autoridades", "tbl_autoridades", acols, [dict(zip(input_names(acols), a)) for a in AUTORIDADES],
            "Responsabilidades e autoridades atribuídas pela gestão de topo (5.3 a–f) e autoridades de libertação e de NC.", row_height=30)

    # mesma estrutura do RG-SGA-08 tbl_raci: ID_Processo, Processo_SGQ (≙ Processo_SGA), Clausula, funções, N_Aprovadores, Controlo_RACI
    first_k, last_k = RACI_COLS[0][0], RACI_COLS[-1][0]
    rcols = [col("ID_Processo", 9, key="PK", desc="Linha da matriz.", dom="RACI-Q-nn"), col("Processo_SGQ", 40, desc="Atividade / processo do SGQ (equivale a Processo_SGA)."),
             col("Clausula", 10, desc="Cláusula ISO 9001:2026.")]
    rcols += [col(k, 7, dv="RACI", desc=f"{n} ({c})", req=False) for k, c, n in RACI_COLS]
    rcols.append(col("N_Aprovadores", 8, "int", f=f'=IF(@ID_Processo@="","",COUNTIF(@{first_k}@:@{last_k}@,"A"))', desc="Número de funções com A (deve ser 1)."))
    rcols.append(col("Controlo_RACI", 12, f=f'=IF(@ID_Processo@="","",IF(COUNTIF(@{first_k}@:@{last_k}@,"A")<>1,"1 A obrigatório",IF(COUNTIF(@{first_k}@:@{last_k}@,"R")=0,"Falta R","OK")))',
                     desc="Exatamente um A (aprova) e pelo menos um R (executa)."))
    code2col = {c: k for k, c, _ in RACI_COLS}
    rrows = []
    for i, (a, m) in enumerate(RACI_ATIV):
        d = {"ID_Processo": f"RACI-Q-{i + 1:02d}", "Processo_SGQ": a, "Clausula": RACI_CLAUSULA[i]}
        d.update({code2col[c]: v for c, v in m.items()})
        rrows.append(d)
    b.table("Matriz_RACI", "tbl_raci", rcols, rrows, "Matriz RACI das atividades do SGQ (R executa, A aprova, C consultado, I informado).",
                  title="MATRIZ RACI DO SGQ (5.3)", subtitle="Legenda das colunas no comentário de cada cabeçalho · R = executa · A = aprova (um só) · C = consultado · I = informado",
                  cf=[("Controlo_RACI", {"OK": "green", "A": "red", "Falta": "red"})], row_height=20)

    ccols = [col("ID_Dimensao", 9, key="PK", desc="Dimensão da cultura (ISO 10010)."), col("Dimensao", 32, desc="Dimensão."), col("Afirmacao_Avaliada", 46, desc="Afirmação do inquérito (escala 1–5).")]
    for a in AREAS:
        ccols.append(col(a, 9, "num1", desc=f"Média das respostas da área {a} (1–5)."))
    A0, A1 = f"@{AREAS[0]}@", f"@{AREAS[-1]}@"
    ccols += [col("Media_Ponderada", 9, "num", f=f'=SUMPRODUCT({A0}:{A1},Respondentes!$B$2:$F$2)/SUM(Respondentes!$B$2:$F$2)',
                  desc="Média ponderada pelo n.º de respondentes de cada área."),
              col("Meta", 6, "num1", desc="Meta de maturidade para 2027."),
              col("Lacuna", 7, "num", f='=@Meta@-@Media_Ponderada@', desc="Meta − média."),
              col("Area_Mais_Fraca", 11, f=f'=INDEX($D$4:$H$4,MATCH(MIN({A0}:{A1}),{A0}:{A1},0))', desc="Área com menor pontuação."),
              col("Nivel_Maturidade", 12, f='=IF(@Media_Ponderada@>=4.5,"5-Excelência",IF(@Media_Ponderada@>=3.5,"4-Proativa",IF(@Media_Ponderada@>=2.5,"3-Definida",IF(@Media_Ponderada@>=1.5,"2-Reativa","1-Inicial"))))',
                  desc="Nível de maturidade (escala de 5 níveis inspirada na ISO 10010 / ISO 9004).")]
    crows = []
    for i, n, a in DIM_CULT:
        d = dict(ID_Dimensao=i, Dimensao=n, Afirmacao_Avaliada=a, Meta=3.5)
        d.update(dict(zip(AREAS, NOTAS[i])))
        crows.append(d)
    b.table("Cultura_Qualidade", "tbl_cultura", ccols, crows,
            "Autoavaliação da cultura da qualidade e do comportamento ético (ISO 10010), inquérito de junho/2026 por área.",
            title="CULTURA DA QUALIDADE E COMPORTAMENTO ÉTICO — AUTOAVALIAÇÃO ISO 10010 (jun/2026)",
            subtitle="Evidência de 5.1.1 i) e 7.3 e) · Escala 1–5 · 149 respondentes (folha Respondentes) · Média ponderada, lacuna e nível calculados",
            cf=[("Nivel_Maturidade", {"2-": "red", "3-": "orange", "4-": "green"}), ("Lacuna", "@>0.5", "red")], row_height=32)
    ws3 = b.sheet("Respondentes", "N.º de respondentes do inquérito de cultura por área (pesos da média ponderada).")
    cell(ws3, 1, 1, "Área", bold=True, fill=FILL_BAND)
    cell(ws3, 2, 1, "Respondentes", bold=True, fill=FILL_BAND)
    for j, (a, n) in enumerate(zip(AREAS, N_RESP)):
        cell(ws3, 1, 2 + j, a, bold=True, fill=FILL_BAND)
        cell(ws3, 2, 2 + j, n, fmt="0")
        ws3.column_dimensions[get_column_letter(2 + j)].width = 12
    ws3.column_dimensions["A"].width = 14
    cell(ws3, 2, 7, "=SUM(B2:F2)", fmt="0", bold=True)
    cell(ws3, 1, 7, "Total", bold=True, fill=FILL_BAND)

    gcols = [col("ID_Gemba", 9, key="PK", desc="Visita ao terreno da gestão."), col("Data", 11, "date", desc="Data."), col("Lider", 26, dv="Funcao", desc="Membro da gestão."),
             col("Processo", 7, dv="Processo", desc="Processo visitado."), col("Tema", 32, desc="Tema da visita."), col("Observacao", 46, desc="O que foi observado."),
             col("Acao_Decidida", 40, desc="Ação decidida no local."), col("Ligacao", 14, desc="ID de CAPA, MOC, ação ou registo.", req=False)]
    b.table("Gemba_Walks", "tbl_gemba", gcols, rows_from(input_names(gcols), GEMBA, dates=("Data",)),
            "Gemba walks da gestão de topo (evidência de 5.1.1 f, h, i).", row_height=40, extra_rows=5)

    ecols = [col("ID_Relato", 10, key="PK", desc="Relato de integridade/ética."), col("Data", 11, "date", desc="Data do relato."), col("Tipo", 22, dv="TipoRelato", desc="Tipo."),
             col("Descricao", 50, desc="Descrição (sem identificar o relator quando anónimo)."), col("Origem", 16, desc="Quem relatou (função ou anónimo)."),
             col("Investigacao", 12, desc="Estado da investigação."), col("Resultado_Acao", 56, desc="Resultado e ação."), col("Estado", 9, dv="EstadoRel", desc="Aberto / fechado."),
             col("Dias", 6, "int", f='=IF(@Data@="","",DataRef-@Data@)', desc="Dias desde o relato.")]
    b.table("Relatos_Integridade", "tbl_relatos_etica", ecols, rows_from(input_names(ecols), RELATOS, dates=("Data",)),
            "Canal de relatos de integridade e comportamento ético relativos à qualidade (5.1.1 i).",
            title="RELATOS DE INTEGRIDADE E COMPORTAMENTO ÉTICO (5.1.1 i)", subtitle="Canal confidencial · Nenhum relator é penalizado · Casos confirmados alimentam a revisão pela gestão",
            cf=[("Estado", {"Aberto": "orange", "Fechado": "green"})], row_height=48, extra_rows=5)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
