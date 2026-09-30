"""RG-SGQ-08 — Controlo da informação documentada e comunicação.
ISO 9001:2026 7.5.1–7.5.3 (documentos internos e externos, proteção, retenção, eliminação), 7.4 a)–e), 8.2.1 a)–e) (2026: e) contingência).
Boas práticas: ISO 10013 (orientação para informação documentada), APG 'Documented information'."""
import datetime as dt
from sgqlib import *
from dimsq import *

d = lambda s: dt.date.fromisoformat(s) if s else None
# (código, título, tipo, processo, versão, data aprovação, elaborado, aprovado, estado, periodicidade (meses), distribuição, suporte, exigido pela ISO?)
DOCS = [
    ("POL-SGQ-01", "Política da qualidade", "Política", "GES", "01", "2026-09-28", GQ, DG, "Em vigor", 12, "Afixada; intranet; site", "Eletrónico + afixado", "Sim (5.2.2 a)"),
    ("AMB-SGQ-01", "Âmbito do SGQ (RG-SGQ-01 tbl_ambito)", "Âmbito", "GES", "01", "2026-09-28", GQ, DG, "Em vigor", 12, "Intranet; organismo de certificação", "Eletrónico", "Sim (4.3)"),
    ("PR-SGQ-01", "Contexto, planeamento estratégico e revisão pela gestão", "Procedimento", "GES", "01", "2026-09-28", GQ, DG, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-02", "Controlo da informação documentada", "Procedimento", "DOC", "02", "2026-09-28", GQ, DG, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-03", "Planeamento e controlo de alterações (MOC)", "Procedimento", "QUA", "01", "2026-09-22", GQ, DIND, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-04", "Gestão de riscos e oportunidades (remete para PG-SGI-006 / PR-SGA-02)", "Procedimento", "QUA", "01", "2026-09-24", GQ, DG, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-05", "Auditoria interna (ISO 19011:2026)", "Procedimento", "QUA", "03", "2026-09-22", GQ, DG, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-06", "Não conformidade, ação corretiva e 8D", "Procedimento", "QUA", "03", "2026-04-10", GQ, DIND, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-07", "Monitorização, medição, análise de dados e melhoria", "Procedimento", "QUA", "01", "2025-06-15", GQ, DIND, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-08", "Revisão de requisitos, propostas e encomendas", "Procedimento", "COM", "02", "2025-11-03", DCOM, DG, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-09", "Tratamento de reclamações e satisfação do cliente (ISO 10002 / 10004)", "Procedimento", "COM", "02", "2026-03-02", DCOM, DG, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-10", "Design e desenvolvimento de produto", "Procedimento", "RD", "02", "2026-02-20", RD_, DIND, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-11", "Planeamento e controlo da produção", "Procedimento", "PCP", "02", "2026-12-15", GPROD, DIND, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-12", "Compras, avaliação e desenvolvimento de fornecedores", "Procedimento", "CMP", "03", "2026-04-15", CMP_, DIND, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-13", "Inspeção, ensaio e libertação de produto", "Procedimento", "LAB", "04", "2026-06-20", GQ, DIND, "Em vigor", 24, "Intranet; laboratório", "Eletrónico + papel controlado", "Não (C)"),
    ("PR-SGQ-14", "Controlo de saídas não conformes e concessões", "Procedimento", "LAB", "02", "2026-07-25", GQ, DIND, "Em vigor", 24, "Intranet; laboratório", "Eletrónico", "Não (C)"),
    ("PR-SGQ-15", "Manutenção de máquinas e moldes", "Procedimento", "MAN", "03", "2026-11-20", GMAN, DIND, "Em vigor", 24, "Intranet; oficina", "Eletrónico", "Não (C)"),
    ("PR-SGQ-16", "Gestão da medição: calibração, verificação e MSA (ISO 10012:2026)", "Procedimento", "MET", "02", "2026-05-05", GQ, DIND, "Em vigor", 24, "Intranet; laboratório", "Eletrónico", "Não (C)"),
    ("PR-SGQ-17", "Competência, formação e consciencialização", "Procedimento", "RH", "02", "2025-09-01", RH_, DG, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PR-SGQ-18", "Sistemas de informação, cópias de segurança e validação de folhas de cálculo", "Procedimento", "TI", "02", "2026-12-11", TI_, DIND, "Em vigor", 24, "Intranet", "Eletrónico", "Não (C)"),
    ("PC-SOP-01", "Plano de controlo — sopro de frascos", "Plano de controlo", "SOP", "04", "2026-06-25", GQ, DIND, "Em vigor", 12, "Postos ISBM; laboratório", "Eletrónico (terminal no posto)", "Sim (8.5.1 a)"),
    ("PC-INJ-01", "Plano de controlo — injeção de tampas e potes", "Plano de controlo", "INJ", "06", "2026-09-22", GQ, DIND, "Em vigor", 12, "Postos IM; laboratório", "Eletrónico (terminal no posto)", "Sim (8.5.1 a)"),
    ("PC-DEC-01", "Plano de controlo — serigrafia e hot foil", "Plano de controlo", "SER", "03", "2026-08-05", GQ, DIND, "Em vigor", 12, "Postos SS/HF", "Eletrónico (terminal no posto)", "Sim (8.5.1 a)"),
    ("PC-MP-01", "Plano de controlo — receção de matérias-primas", "Plano de controlo", "REC", "06", "2026-05-02", GQ, DIND, "Em vigor", 12, "Laboratório de receção", "Eletrónico", "Sim (8.4.2 d)"),
    ("IT-INJ-01", "Setup e arranque de injetora", "Instrução de trabalho", "INJ", "03", "2025-10-14", EPROC, GPROD, "Em vigor", 24, "Postos IM", "Papel controlado", "Não (C)"),
    ("IT-INJ-02", "Parâmetros validados IM-002 (DOE)", "Instrução de trabalho", "INJ", "03", "2026-01-15", EPROC, GPROD, "Em vigor", 24, "Posto IM-002", "Papel controlado", "Não (C)"),
    ("IT-INJ-04", "Injeção de tampas farma TE-012 (anel de inviolabilidade)", "Instrução de trabalho", "INJ", "01", "2026-06-29", EPROC, GPROD, "Em vigor", 24, "Postos IM-007/008", "Papel controlado", "Não (C)"),
    ("IT-SOP-01", "Setup e arranque de ISBM", "Instrução de trabalho", "SOP", "04", "2025-12-01", EPROC, GPROD, "Em vigor", 24, "Postos ISBM", "Papel controlado", "Não (C)"),
    ("IT-SOP-03", "Linha farmacêutica e alimentar ISBM-009/010 (higiene e segregação)", "Instrução de trabalho", "SOP", "01", "2026-06-29", EPROC, GPROD, "Em vigor", 24, "Postos ISBM-009/010", "Papel controlado", "Não (C)"),
    ("IT-SER-02", "Ensaio de aderência (fita) e cura UV", "Instrução de trabalho", "SER", "03", "2026-08-05", GQ, GPROD, "Em vigor", 24, "Postos SS", "Papel controlado", "Não (C)"),
    ("IT-HFS-01", "Setup de hot foil (temperatura, pressão, velocidade)", "Instrução de trabalho", "HFS", "03", "2026-12-04", EPROC, GPROD, "Em vigor", 24, "Postos HF", "Papel controlado", "Não (C)"),
    ("IT-REC-01", "Receção, quarentena e libertação de matéria-prima", "Instrução de trabalho", "REC", "03", "2026-08-20", GQ, LOG, "Em vigor", 24, "Armazém; laboratório", "Papel controlado", "Não (C)"),
    ("IT-EXP-02", "Carga e expedição com leitura de código de barras", "Instrução de trabalho", "EXP", "02", "2026-08-03", LOG, DIND, "Em revisão", 24, "Cais de expedição", "Papel controlado", "Não (C)"),
    ("IT-GER-01", "Parar para corrigir (andon) e retenção de produto suspeito", "Instrução de trabalho", "QUA", "01", "2026-02-11", GQ, DIND, "Em vigor", 24, "Todos os postos", "Afixado", "Não (C)"),
    ("LAB-M-12", "Método de ensaio do anel de inviolabilidade (força de rotura das pontes)", "Método de ensaio", "LAB", "01", "2026-06-24", "Técnico(a) de Laboratório", GQ, "Em vigor", 24, "Laboratório", "Eletrónico", "Não (C)"),
    ("LAB-M-15", "Ensaio de migração global — EN 1186-3 (simulantes A e B)", "Método de ensaio", "LAB", "01", "2026-06-24", "Técnico(a) de Laboratório", GQ, "Em vigor", 24, "Laboratório", "Eletrónico", "Não (C)"),
    ("ESP-TP-013", "Especificação — tampa de pote 70 mm (força de remoção)", "Especificação", "RD", "01", "2026-09-22", RD_, GQ, "Em vigor", 36, "ERP; laboratório", "Eletrónico", "Sim (8.3.5; 8.5.1 a)"),
    ("CQ-02", "Modelo de certificado de lote (inclui resultado do anel para farma)", "Modelo", "LAB", "03", "2026-09-14", GQ, GQ, "Em vigor", 36, "ERP", "Eletrónico", "Não (C)"),
    ("IT-SOP-02", "Setup ISBM — versão 2019 (substituída pela IT-SOP-01 rev. 04)", "Instrução de trabalho", "SOP", "02", "2019-05-06", EPROC, GPROD, "Obsoleto", 24, "Arquivo de obsoletos", "Eletrónico (arquivo)", "Não (C)"),
]

EXT = [
    ("EXT-01", "ISO 9001:2026 — Sistemas de gestão da qualidade — Requisitos", "Norma", "6.ª edição, set/2026", "Todos", "Norma licenciada (versão oficial ES) na pasta de interpretação"),
    ("EXT-02", "ISO 9000:2026 — Fundamentos e vocabulário", "Norma", "2026", "QUA", "Termos e definições"),
    ("EXT-03", "ISO 19011:2026 — Diretrizes para auditorias de sistemas de gestão", "Norma", "4.ª edição, mai/2026", "QUA", "PR-SGQ-05"),
    ("EXT-04", "ISO 10012:2026 — Sistemas de gestão da medição", "Norma", "fev/2026", "MET", "PR-SGQ-16"),
    ("EXT-05", "ISO 2859-1:2026 — Amostragem por atributos", "Norma", "2026", "LAB", "PC-*"),
    ("EXT-06", "ISO 3951-1 — Amostragem por variáveis", "Norma", "2022", "LAB", "PC-*"),
    ("EXT-07", "ISO 10002:2018 — Tratamento de reclamações", "Norma", "2018", "COM", "PR-SGQ-09"),
    ("EXT-08", "ISO 10004:2018 — Monitorização e medição da satisfação", "Norma", "2018", "COM", "PR-SGQ-09"),
    ("EXT-09", "ISO 10015:2019 — Gestão de competências", "Norma", "2019", "RH", "PR-SGQ-17"),
    ("EXT-10", "ISO 10010:2022 — Cultura da qualidade", "Norma", "2022", "GES", "RG-SGQ-03"),
    ("EXT-11", "ISO 10007:2017 — Gestão da configuração", "Norma", "2017", "QUA", "PR-SGQ-03"),
    ("EXT-12", "ISO 10009:2024 — Ferramentas da qualidade", "Norma", "2024", "QUA", "PR-SGQ-06/07"),
    ("EXT-13", "Regulamento (CE) 1935/2004 — materiais em contacto com alimentos", "Legislação", "versão consolidada", "RD; LAB", "Requisitos CUST-015/016"),
    ("EXT-14", "Regulamento (UE) 10/2011 — materiais plásticos em contacto com alimentos", "Legislação", "versão consolidada 2025", "RD; LAB", "LAB-M-15"),
    ("EXT-15", "Regulamento (CE) 2023/2006 — boas práticas de fabrico (FCM)", "Legislação", "versão consolidada", "PCP; EXP", "IT-SOP-03"),
    ("EXT-16", "Regulamento (UE) 2025/40 — embalagens (PPWR)", "Legislação", "aplicável desde 12/08/2026", "RD", "RG-SGA-20"),
    ("EXT-17", "21 CFR 211.132 — embalagens com evidência de violação (referência de clientes farma)", "Requisito de cliente / regulamento", "atual", "INJ; LAB", "LAB-M-12"),
    ("EXT-18", "EN 1186-3:2022 — ensaio de migração global (imersão)", "Norma", "2022", "LAB", "LAB-M-15"),
    ("EXT-19", "ASTM D2463-23 — resistência à queda de frascos", "Norma", "2023", "LAB", "PC-SOP-01"),
    ("EXT-20", "ASTM D3359 — aderência por fita", "Norma", "atual", "SER", "IT-SER-02"),
    ("EXT-21", "ISO 1133 / ASTM D1238 — índice de fluidez", "Norma", "atual", "REC", "PC-MP-01"),
    ("EXT-22", "ISO 8573-1 — qualidade do ar comprimido", "Norma", "2010", "MAN", "MOC-Q-26-11"),
    ("EXT-23", "Especificações e acordos de qualidade de clientes (CUST-001 a 018)", "Requisito de cliente", "por cliente", "COM", "RG-SGQ-10"),
    ("EXT-24", "Certificados de análise e fichas técnicas de fornecedores (SUP-001 a 010)", "Documento de fornecedor", "por lote", "REC", "PC-MP-01"),
]

REGISTOS = [
    ("RG-SGQ-01", "Contexto, partes interessadas e âmbito", "4.1–4.3", "Obrigatório (4.3 âmbito)", "Até substituição + 5 anos", "Excel no repositório SGQ", "Edição só pelo Gerente da Qualidade"),
    ("RG-SGQ-03", "Política, liderança e cultura", "5.1–5.3", "Obrigatório (5.2.2 a política)", "Até substituição + 5 anos", "Excel no repositório SGQ", "Edição só pela Direção"),
    ("RG-SGQ-05", "Objetivos, KPI e monitorização", "6.2; 9.1.1", "Obrigatório (6.2.1 g; 9.1.1 resultados)", "5 anos", "Excel + data warehouse", "Dados de origem imutáveis (bronze)"),
    ("RG-SGQ-06", "Alterações (MOC)", "6.3; 8.5.6", "Obrigatório (8.5.6 evidência)", "Vida do produto + 5 anos", "Excel no repositório SGQ", "Assinatura eletrónica da autorização"),
    ("RG-SGQ-07", "Competências e formação", "7.2", "Obrigatório (7.2 evidência da competência)", "Duração do contrato + 5 anos", "Excel + plataforma de RH", "Dados pessoais — acesso restrito (RGPD)"),
    ("RG-SGQ-09", "Metrologia e MSA", "7.1.5", "Obrigatório (7.1.5.1; 7.1.5.2 a)", "Vida do equipamento + 5 anos", "Excel + certificados PDF", "Certificados em só leitura"),
    ("RG-SGQ-10", "Revisão de requisitos e encomendas", "8.2.3", "Obrigatório (8.2.3.2)", "10 anos (farma) / 5 anos", "ERP + Excel", "Registo automático no ERP"),
    ("RG-SGQ-11", "Design e desenvolvimento", "8.3", "Obrigatório (8.3.3–8.3.6)", "Vida do produto + 10 anos", "Repositório de projeto", "Versões congeladas por fase"),
    ("RG-SGQ-12", "Avaliação de fornecedores", "8.4", "Obrigatório (8.4.1)", "5 anos", "Excel + ERP", "—"),
    ("RG-SGQ-13", "Libertação e rastreabilidade", "8.5.2; 8.6", "Obrigatório (8.5.2 d; 8.6)", "Validade do produto do cliente + 1 ano (mín. 5; farma 10)", "MES/ERP + Excel", "Registos de lote imutáveis após libertação"),
    ("RG-SGQ-14", "Saídas não conformes", "8.7", "Obrigatório (8.7.2)", "5 anos (farma 10)", "Excel + MES", "—"),
    ("RG-SGQ-15", "Reclamações e satisfação", "9.1.2; 8.2.1", "Evidência (9.1.2 métodos)", "5 anos", "Excel + CRM", "Dados de contacto — acesso restrito"),
    ("RG-SGQ-16", "Auditoria interna", "9.2", "Obrigatório (9.2.2)", "2 ciclos de certificação", "Excel no repositório SGQ", "—"),
    ("RG-SGQ-17", "Revisão pela gestão", "9.3", "Obrigatório (9.3.3)", "10 anos", "Excel + ata assinada", "Ata em PDF assinada"),
    ("RG-SGQ-18", "NC e ações corretivas", "10.2", "Obrigatório (10.2.2)", "5 anos", "Excel + software de CAPA", "—"),
    ("REG-OP-01", "Registos de autocontrolo e SPC no posto", "8.5.1", "Necessário (8.5.1 c)", "5 anos", "MES", "Recolha automática quando possível"),
]

COMUNIC = [
    ("COM-Q-01", "Desempenho da qualidade (KPI, objetivos)", "Mensal", "Todos os colaboradores", "Quadros de KPI por área; reunião geral trimestral", GQ, "Interna"),
    ("COM-Q-02", "Política da qualidade e alterações", "Na aprovação e anual", "Todos; partes interessadas", "Afixação; intranet; site", DG, "Interna/externa"),
    ("COM-Q-03", "Alertas de qualidade (defeito recorrente, reclamação crítica)", "No próprio turno", "Operadores e chefias da área", "Alerta de qualidade no posto + reunião de arranque", GQ, "Interna"),
    ("COM-Q-04", "Resultados de auditorias internas", "Após cada auditoria", "Dono do processo; Direção", "Relatório de auditoria", "Auditor(a) Interno(a) do SGQ", "Interna"),
    ("COM-Q-05", "Alterações a processos e documentos", "Antes da implementação", "Pessoas afetadas", "Formação no posto; nota de alteração", GQ, "Interna"),
    ("COM-Q-06", "Requisitos de qualidade a fornecedores", "Na encomenda e na alteração", "Fornecedores", "Encomenda + especificação + acordo de qualidade", CMP_, "Externa"),
    ("COM-Q-07", "Desempenho do fornecedor (scorecard)", "Trimestral", "Fornecedores", "Relatório de scorecard; reunião", CMP_, "Externa"),
    ("COM-Q-08", "Notificação ao organismo de certificação de alterações significativas", "Por ocorrência", "Organismo de certificação", "Correio eletrónico formal", GQ, "Externa"),
]

COM_CLIENTE = [
    ("COMC-01", "a) Informação sobre produtos", "Fichas técnicas, especificações, declarações de conformidade (FCM, PPWR)", "Portal do cliente; correio eletrónico", DCOM, "Por pedido e em cada revisão"),
    ("COMC-02", "b) Consultas, contratos e encomendas, incluindo alterações", "Propostas, confirmação de encomenda com revisão de requisitos", "ERP (confirmação automática)", "Gestor(a) de Cliente (Key Account)", "Por encomenda"),
    ("COMC-03", "c) Feedback, incluindo reclamações", "Reclamações (ISO 10002), inquérito semestral, reuniões de conta", "Portal; correio; reuniões", DCOM, "Contínuo / semestral"),
    ("COMC-04", "d) Propriedade do cliente", "Moldes, artwork e ficheiros de cor do cliente: receção, estado, perdas/danos", "Correio eletrónico + registo RG-SGQ-10", GQ, "Por ocorrência"),
    ("COMC-05", "e) Ações de contingência (novo 2026)", "Plano de contingência por cliente: stock de segurança, moldes alternativos, aviso prévio de disrupção", "Acordo de qualidade + notificação em 24 h", DCOM, "Anual e por ocorrência"),
    ("COMC-06", "e) Notificação de disrupção", "Ex.: falta de resina (R15), avaria prolongada (ISBM-005), onda de calor — nova data e medidas", "Telefone + correio eletrónico em 24 h", "Gestor(a) de Cliente (Key Account)", "Por ocorrência"),
]


def build(out):
    b = Book("RG-SGQ-08", "Informação Documentada e Comunicação",
             activities="Controlar documentos internos e externos, registos (retenção, proteção, eliminação) e planear a comunicação interna, externa e com o cliente.",
             clauses="7.5.1 a) b); 7.5.2 identificação, formato, revisão e aprovação; 7.5.3.1 disponibilidade e proteção; 7.5.3.2 a)–d), documentos externos e proteção da evidência contra alterações não intencionais; 7.4 a)–e); 8.2.1 a)–e) (2026: e) contingência)",
             purpose="Lista mestra dos documentos do SGQ com revisão calculada, documentos de origem externa com verificação da atualidade, tabela de retenção de registos e matrizes de comunicação interna/externa e com o cliente (incluindo ações de contingência — novo na ISO 9001:2026).",
             links=[("RG-SGA-09", "Lista mestra do SGA — o SGI usa a mesma estrutura de controlo documental."), ("SGQ-00 Matriz mestra", "Classificação A/B/C da informação documentada exigida pela norma.")],
             guidance=[("ISO/TC 176 APG — Documented information", "A norma não exige manual nem procedimentos para cada requisito; a extensão depende da organização (7.5.1 Nota). Coluna Exigido_ISO separa o obrigatório do escolhido (C)."),
                       ("ISO 10013 (orientação)", "Identificação, formato, revisão e aprovação; retenção e eliminação definidas por registo."),
                       ("iso9001help.co.uk — Documented information", "Controlo de documentos externos por verificação periódica da edição em vigor.")])
    b.add_list("TipoDoc", ["Política", "Âmbito", "Procedimento", "Plano de controlo", "Instrução de trabalho", "Método de ensaio", "Especificação", "Modelo"])
    b.add_list("EstadoDoc", ["Em vigor", "Em revisão", "Obsoleto"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Funcao", FUNC_NAMES + ["Técnico(a) de Laboratório"])
    b.add_list("TipoExt", ["Norma", "Legislação", "Requisito de cliente", "Requisito de cliente / regulamento", "Documento de fornecedor"])
    b.add_list("EstadoExt", ["Atual", "Por verificar", "Substituído"])
    b.add_list("Direcao", ["Interna", "Externa", "Interna/externa"])

    # mesmos nomes de coluna do RG-SGA-09 tbl_lista_mestra (Aprovador, Localizacao, Ponto_de_Uso); colunas só do SGQ no fim
    cols = [col("Codigo", 11, key="PK", desc="Código do documento."), col("Titulo", 48, desc="Título."), col("Tipo", 14, dv="TipoDoc", desc="Tipo."),
            col("Versao", 6, desc="Revisão."), col("Data_Aprovacao", 11, "date", desc="Data de aprovação."),
            col("Aprovador", 22, dv="Funcao", desc="Quem aprovou (7.5.2 c)."), col("Estado", 10, dv="EstadoDoc", desc="Estado."),
            col("Localizacao", 18, desc="Formato e suporte (7.5.2 b)."), col("Ponto_de_Uso", 24, desc="Onde está disponível (7.5.3.2 a)."),
            col("Proxima_Revisao", 11, "date", f='=IF(OR(@Codigo@="",@Estado@="Obsoleto"),"",EDATE(@Data_Aprovacao@,@Periodicidade_Meses@))', desc="Data de aprovação + periodicidade."),
            col("Alerta", 14, f='=IF(@Codigo@="","",IF(@Estado@="Obsoleto","Arquivo",IF(@Proxima_Revisao@<DataRef,"Revisão vencida",IF(@Proxima_Revisao@<DataRef+60,"Rever em 60 dias","OK"))))', desc="Alerta de revisão."),
            col("Processo", 7, dv="Processo", desc="[Só SGQ] Processo."), col("Elaborado", 22, dv="Funcao", desc="[Só SGQ] Quem elaborou."),
            col("Periodicidade_Meses", 9, "int", desc="[Só SGQ] Periodicidade da revisão."),
            col("Exigido_ISO", 16, desc="[Só SGQ] Exigido pela ISO 9001:2026 ou (C) determinado pela organização (7.5.1 b).")]
    DOC_N = ["Codigo", "Titulo", "Tipo", "Processo", "Versao", "Data_Aprovacao", "Elaborado", "Aprovador", "Estado", "Periodicidade_Meses", "Ponto_de_Uso",
             "Localizacao", "Exigido_ISO"]
    b.table("Lista_Mestra", "tbl_lista_mestra", cols, rows_from(DOC_N, DOCS, dates=("Data_Aprovacao",)),
            "Lista mestra de documentos do SGQ (7.5.2, 7.5.3).", title="LISTA MESTRA DE DOCUMENTOS DO SGQ (7.5)",
            subtitle="A ISO 9001:2026 não exige manual nem procedimentos por requisito — 'Não (C)' = documento que a Plasticom determinou necessário · Próxima revisão e alerta calculados",
            cf=[("Alerta", {"vencida": "red", "60 dias": "orange", "OK": "green", "Arquivo": "gray"}), ("Estado", {"Obsoleto": "gray", "Em revisão": "yellow"}), ("Exigido_ISO", {"Sim": "blue"})],
            row_height=30, freeze_col=2, extra_rows=10)

    ecols = [col("ID_Externo", 8, key="PK", desc="Documento externo."), col("Documento", 54, desc="Título."), col("Tipo", 18, dv="TipoExt", desc="Tipo."),
             col("Edicao", 22, desc="Edição / versão em uso."), col("Processos", 10, desc="Processos que o usam."), col("Onde_Aplicado", 28, desc="Documento interno que o aplica."),
             col("Data_Verificacao", 11, "date", desc="Última verificação da atualidade."), col("Estado", 11, dv="EstadoExt", desc="Estado."),
             col("Proxima_Verificacao", 11, "date", f='=EDATE(@Data_Verificacao@,12)', desc="Verificação anual."),
             col("Alerta", 12, f='=IF(@Estado@<>"Atual","Rever",IF(@Proxima_Verificacao@<DataRef,"Verificar","OK"))', desc="Alerta.")]
    erows = rows_from(input_names(ecols)[:6], EXT)
    for k, r in enumerate(erows):
        r["Data_Verificacao"] = DATA_REF if k < 12 else dt.date(2026, 3, 16) if k < 22 else dt.date(2025, 8, 20)
        r["Estado"] = "Atual" if k != 21 else "Por verificar"
    b.table("Documentos_Externos", "tbl_doc_externos", ecols, erows, "Documentos de origem externa identificados e controlados (7.5.3.2).",
            title="DOCUMENTOS DE ORIGEM EXTERNA (7.5.3.2)", cf=[("Alerta", {"Verificar": "orange", "Rever": "red", "OK": "green"})], row_height=30)

    rcols = [col("Registo", 10, key="PK", desc="Registo."), col("Descricao", 36, desc="Conteúdo."), col("Clausulas", 10, desc="Cláusulas."),
             col("Exigencia", 34, desc="Obrigatório pela norma ou necessário à eficácia."), col("Retencao", 30, desc="Tempo de conservação (7.5.3.2 d)."),
             col("Local_Suporte", 26, desc="Armazenamento e preservação (7.5.3.2 b)."), col("Protecao", 34, desc="Proteção contra alterações não intencionais e acesso (7.5.3.1 b).")]
    b.table("Retencao_Registos", "tbl_retencao", rcols, rows_from(input_names(rcols), REGISTOS),
            "Retenção, preservação e proteção dos registos do SGQ (7.5.3).", title="RETENÇÃO E PROTEÇÃO DOS REGISTOS (7.5.3)", row_height=30)

    # mesmos nomes de coluna do RG-SGA-09 tbl_comunicacao
    ccols = [col("ID_Comunicacao", 9, key="PK", desc="Comunicação."), col("Tipo", 12, dv="Direcao", desc="Interna / externa."),
             col("O_Que_Mensagem", 42, desc="a) o que comunicar."), col("A_Quem_Publico", 26, desc="c) a quem."),
             col("Quando_Momento", 20, desc="b) quando."), col("Como_Canal", 36, desc="d) como."), col("Responsavel", 24, dv="Funcao", desc="e) quem comunica.")]
    COM_N = ["ID_Comunicacao", "O_Que_Mensagem", "Quando_Momento", "A_Quem_Publico", "Como_Canal", "Responsavel", "Tipo"]
    b.table("Matriz_Comunicacao", "tbl_comunicacao", ccols, rows_from(COM_N, COMUNIC), "Comunicações internas e externas pertinentes para o SGQ (7.4 a–e) — mesma estrutura do RG-SGA-09.",
            title="MATRIZ DE COMUNICAÇÃO DO SGQ (7.4)", row_height=30)
    kcols = [col("ID", 8, key="PK", desc="Linha."), col("Alinea_8_2_1", 30, desc="Alínea de 8.2.1."), col("Conteudo", 50, desc="O que se comunica."),
             col("Canal", 30, desc="Canal."), col("Responsavel", 26, desc="Responsável."), col("Frequencia", 18, desc="Frequência.")]
    b.table("Comunicacao_Cliente", "tbl_comunicacao_cliente", kcols, rows_from(input_names(kcols), COM_CLIENTE),
            "Comunicação com o cliente (8.2.1 a–e), incluindo ações de contingência e disrupções (novo 2026).",
            title="COMUNICAÇÃO COM O CLIENTE (8.2.1)", subtitle="ISO 9001:2026 8.2.1 e): informação sobre ações de contingência, incluindo disrupções no fornecimento", row_height=34)

    ws = b.sheet("Resumo_Documentos", "Resumo calculado do estado documental.")
    title(ws, "ESTADO DA INFORMAÇÃO DOCUMENTADA — calculado")
    header_row(ws, 3, ["Indicador", "Valor"], widths=[50, 10])
    L = lambda c_: f"tbl_lista_mestra[{c_}]"
    ind = [("Documentos em vigor", f'=COUNTIF({L("Estado")},"Em vigor")'), ("Documentos em revisão", f'=COUNTIF({L("Estado")},"Em revisão")'),
           ("Documentos obsoletos arquivados", f'=COUNTIF({L("Estado")},"Obsoleto")'), ("Documentos com revisão vencida", f'=COUNTIF({L("Alerta")},"Revisão vencida")'),
           ("Documentos a rever nos próximos 60 dias", f'=COUNTIF({L("Alerta")},"Rever em 60 dias")'),
           ("Documentos exigidos pela ISO 9001:2026", f'=COUNTIF({L("Exigido_ISO")},"Sim*")'),
           ("Documentos determinados pela organização (C)", f'=COUNTIF({L("Exigido_ISO")},"Não*")'),
           ("Documentos externos a verificar/rever", '=COUNTIF(tbl_doc_externos[Alerta],"<>OK")')]
    for k, (a, f) in enumerate(ind):
        cell(ws, 4 + k, 1, a)
        cell(ws, 4 + k, 2, f, fmt="0")
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
