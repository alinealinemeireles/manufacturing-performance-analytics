"""RG-SGQ-16 — Auditoria interna do SGQ (ISO 9001:2026 9.2.1, 9.2.2 a)–d); ISO 19011:2026; ISO/TC 176 APG 'Internal audits').
Programa baseado no risco: importância do processo, resultados de auditorias anteriores e alterações (9.2.2) + NC e reclamações do dataset.
As constatações da auditoria integrada de set/2026 correspondem a problemas reais encontrados nos outros registos do SGQ."""
import datetime as dt
from sgqlib import *
from dimsq import *
import qdata as Q

AUDITORES = [
    ("AUD-01", "Gerente da Qualidade", GQ, "Auditor coordenador (ISO 19011:2026, 40 h)", "ISO 9001:2026; 8D; estatística", "Todos os processos", 28, 4.6, "QUA; DOC", "Sim", "2026-09-22"),
    ("AUD-02", "Ana Silva", INSP, "Auditor interno (ISO 19011:2026, 16 h — FOR-Q-02)", "Inspeção; ISO 2859-1; laboratório", "Produção; compras; receção", 9, 4.2, "LAB; MET", "Sim", "2026-09-22"),
    ("AUD-03", "Carlos Mendes", INSP, "Auditor interno (ISO 19011:2026, 16 h — FOR-Q-02)", "Inspeção; SPC", "Produção; expedição", 11, 4.0, "LAB", "Sim", "2026-09-22"),
    ("AUD-04", "Elena Santos", "Técnico(a) de Laboratório", "Auditor interno (ISO 19011:2026, 16 h — FOR-Q-02)", "Ensaios FCM e farma; metrologia", "Design; fornecedores; clientes farma", 6, 4.4, "LAB; MET", "Sim", "2026-09-22"),
    ("AUD-05", "Auditor externo (consultor)", "Auditor(a) Interno(a) do SGQ", "Auditor coordenador IRCA ISO 9001", "Sistemas de gestão; setor de embalagem", "QUA; DOC; GES (independência da Qualidade)", 60, 4.7, "—", "Sim", "2026-03-15"),
    ("AUD-06", "Gestor do SGA / EHS", "Gestor do SGA / EHS (Responsável Ambiental)", "Auditor ISO 14001:2026 e ISO 19011:2026", "Ambiente; químicos; resíduos", "Auditorias integradas SGI (aspetos ambientais)", 14, 4.1, "—", "Sim", "2026-09-22"),
]

# priorização por risco: (processo, importância 1–3, resultado auditoria anterior 1–3, requisitos legais/cliente críticos 1–3, última auditoria)
PRIOR = {"GES": (3, 1, 2, "2026-12-09"), "QUA": (3, 3, 2, "2026-11-17"), "COM": (3, 2, 2, "2026-10-20"), "RD": (3, 2, 3, "2026-10-20"), "PCP": (2, 2, 1, "2026-11-24"),
         "CMP": (3, 3, 3, "2026-03-10"), "REC": (2, 2, 2, "2026-03-10"), "INJ": (3, 2, 3, "2026-11-24"), "SOP": (3, 2, 3, "2026-11-24"), "SER": (3, 3, 2, "2026-09-16"),
         "HFS": (2, 2, 1, "2025-12-09"), "LAB": (3, 3, 3, "2026-09-16"), "EXP": (3, 3, 2, "2026-09-17"), "MAN": (2, 2, 1, "2026-09-17"), "MET": (3, 3, 2, "2026-09-16"),
         "RH": (2, 2, 1, "2026-11-17"), "TI": (2, 1, 1, "2026-11-17"), "DOC": (2, 2, 1, "2026-11-17")}   # datas da última auditoria em 31/12/2026

PROGRAMA = [
    ("AUD-Q-25-03", "Produção (INJ, SOP, SER, HFS) e laboratório", "Verificar o controlo da produção e a libertação", "ISO 9001:2015; PC-*; PR-SGQ-13", "Presencial", "AUD-02; AUD-03", "2025-12-09", "2025-12-09", "Realizada"),
    ("AUD-Q-26-01", "Compras, fornecedores e receção (CMP, REC)", "Avaliar o controlo de fornecedores externos após reclamações de MP", "ISO 9001:2015 8.4; PR-SGQ-12; PC-MP-01", "Híbrida (fornecedor remoto)", "AUD-01; AUD-04", "2026-03-10", "2026-03-10", "Realizada"),
    ("AUD-Q-26-02", "Injeção e sopro, incl. arranque das linhas novas (INJ, SOP, PCP)", "Verificar os arranques de ISBM-009/010 e IM-007/008", "ISO 9001:2015 8.5; MOC-Q-26-02/03", "Presencial", "AUD-02; AUD-03", "2026-05-12", "2026-05-12", "Realizada"),
    ("AUD-Q-26-03", "Auditoria integrada SGI: liderança, SER, LAB, EXP, MAN, MET (qualidade + ambiente)", "Conformidade com a ISO 9001:2026 (transição) e eficácia; integrar com a auditoria SGA", "ISO 9001:2026; ISO 14001:2026; requisitos internos", "Presencial", "AUD-01; AUD-04; AUD-06", "2026-09-16", "2026-09-16", "Realizada"),
    ("AUD-Q-26-04", "Comercial e design (COM, RD) — requisitos alimentar/farma", "Verificar revisão de requisitos e projetos DD-26-01 a 06", "ISO 9001:2026 8.2, 8.3", "Presencial", "AUD-05; AUD-04", "2026-10-20", "2026-10-20", "Realizada"),
    ("AUD-Q-26-05", "Gestão da qualidade, documentação, TI e RH (QUA, DOC, TI, RH)", "Independência: auditor externo audita a função Qualidade", "ISO 9001:2026 7, 9, 10", "Híbrida", "AUD-05", "2026-11-17", "2026-11-17", "Realizada"),
    ("AUD-Q-26-06", "Gestão de topo (GES) — liderança, cultura e revisão pela gestão", "Evidência de 5.1.1 i), l) e 9.3", "ISO 9001:2026 5, 6, 9.3", "Presencial", "AUD-05", "2026-12-09", "2026-12-09", "Realizada"),
    ("AUD-Q-26-07", "Injeção e sopro (INJ, SOP, PCP) — seguimento semestral exigido pela priorização por risco", "Verificar a estabilização das linhas novas e o seguimento da CON-Q-26-02", "ISO 9001:2026 7.2, 8.5.1", "Presencial", "AUD-02; AUD-03", "2026-11-24", "2026-11-24", "Realizada"),
    ("AUD-Q-27-01", "Auditoria de transição ISO 9001:2026 (organismo de certificação)", "Transição da certificação para a edição 2026", "ISO 9001:2026", "Presencial", "Organismo externo", "2027-03-09", None, "Planeada"),
]

RISCOS_PROG = [
    ("RP-01", "Risco", "Indisponibilidade dos auditores internos (inspetores) no pico set–nov", "Auditorias adiadas; programa não cumprido", "Planear auditorias fora do pico; auditor externo de reserva"),
    ("RP-02", "Risco", "Falta de independência ao auditar a função Qualidade", "Constatações enviesadas", "Auditor externo (AUD-05) para QUA, DOC e GES"),
    ("RP-03", "Risco", "Competência insuficiente em requisitos farmacêuticos e alimentares", "Não detetar incumprimentos legais", "AUD-04 com formação FCM/farma; especialista técnico convidado"),
    ("RP-04", "Risco", "Auditorias remotas a fornecedores sem acesso a evidência suficiente (19011:2026)", "Conclusões sem evidência", "Remoto só para revisão documental; visita no local para processo"),
    ("RP-05", "Risco", "Segurança da informação na partilha de documentos de clientes em auditoria remota", "Violação de confidencialidade", "Plataforma aprovada pela TI; acesso só de leitura"),
    ("RP-06", "Oportunidade", "Auditorias integradas SGQ + SGA (menos interrupções, visão por processo)", "—", "Equipa mista na AUD-Q-26-03"),
    ("RP-07", "Oportunidade", "Usar os dados do data warehouse para escolher amostras (lotes, ordens, reclamações)", "—", "Amostragem baseada em risco com dados reais"),
]

# checklist das auditorias do 4.º trimestre (cláusula, processo, questão, evidência, resultado, auditoria)
CHECK_Q4 = [
    ("8.2.3", "COM", "As encomendas são revistas antes do compromisso (após a CAPA-Q-26-13)?", "40 encomendas de out/2026: 0 exceções; checklist no ERP", "C", "AUD-Q-26-04"),
    ("8.3.4", "RD", "A verificação e validação do design dos SKU farmacêuticos está registada?", "DD-26-05: validação da estanquidade do pote PT-015 com o cliente sem registo", "NC", "AUD-Q-26-04"),
    ("8.3.5", "RD", "As saídas do design incluem as características de inspeção corretas?", "Auditoria da configuração dos 17 SKU novos sem desvios (CAPA-Q-26-11)", "C", "AUD-Q-26-04"),
    ("7.5.3", "DOC", "Os documentos em uso estão dentro do prazo de revisão?", "3 documentos com revisão vencida (PR-SGQ-11, PR-SGQ-18, IT-HFS-01)", "OBS", "AUD-Q-26-05"),
    ("10.2", "QUA", "O comité de CAPA reduziu as NC maiores sem ação e as vencidas?", "CAPA vencidas de 49% para 31%; 17% das NC maiores de out–nov ainda sem CAPA", "NC", "AUD-Q-26-05"),
    ("7.2", "RH", "A eficácia da formação é avaliada?", "Registo com níveis N1–N4 (ISO 10015)", "C", "AUD-Q-26-05"),
    ("5.1.1 l)", "GES", "A gestão de topo presta contas da eficácia do SGQ?", "Ata RPG-2026-01 assinada; seguimento mensal das decisões", "C", "AUD-Q-26-06"),
    ("9.3", "GES", "A revisão pela gestão cobre os 3 sistemas do SGI de forma coerente?", "SGQ e SGA revistos em set/2026; SGE em 18/12/2026 — agendas separadas", "OM", "AUD-Q-26-06"),
    ("7.2; 8.5.1 e)", "INJ", "Os operadores das máquinas novas estão validados no posto?", "IM-007/008: 6 operadores validados; tutor documentado", "C", "AUD-Q-26-07"),
    ("8.5.1", "SOP", "Os parâmetros das ISBM-009/010 estão estabilizados e registados?", "Fichas de parâmetros rev. 02; Cpk do peso 1,18 (meta 1,33)", "OBS", "AUD-Q-26-07"),
]

CHECK = [
    ("5.1.1 i)", "LID", "A gestão promove a cultura da qualidade e o comportamento ético? Como?", "Entrevista ao DG; canal de relatos (4 casos); inquérito ISO 10010", "C"),
    ("5.2.2 d)", "LID", "A política é compreendida? (entrevistar 10 operadores)", "7 de 10 explicam 'fazer bem à primeira'", "OBS"),
    ("6.1.2", "QUA", "As ações para riscos são proporcionais e a eficácia é avaliada?", "RG-SGQ-04: R3, R13, R20 com eficácia 'Não eficaz' e ação replaneada", "C"),
    ("6.3", "MAN", "As alterações são planeadas (a–g) antes da implementação?", "Compressores substituídos em fev/2026 sem MOC (autorizado em set/2026)", "NC"),
    ("7.1.5.2", "MET", "Os equipamentos em uso têm confirmação válida e identificação do estado?", "EQM-022 e EQM-031 com confirmação vencida em uso", "NC"),
    ("7.1.5.2", "MET", "Quando um equipamento está fora de tolerância, avaliam-se os resultados anteriores?", "OOT-26-01 com avaliação retrospetiva completa", "C"),
    ("7.2", "SER", "O operador da SS-001 turno 2 tem competência validada?", "Validado (FOR-Q-09, nível 3)", "C"),
    ("7.3 e)", "SER", "As pessoas conhecem a cultura da qualidade e o canal de relatos?", "Sessão CON-26-03 com 86% de cobertura", "C"),
    ("8.5.1 g)", "EXP", "Que ações previnem o erro humano na expedição?", "Leitura de código de barras em implementação (EH-01); 29 reclamações de produto trocado", "OBS"),
    ("8.5.2", "LAB", "É possível rastrear um lote até ao lote de resina?", "RST-26-02: resina deduzida por FIFO — consumo só regista masterbatch", "OBS"),
    ("8.6", "LAB", "A libertação tem evidência de conformidade e de quem autorizou?", "Amostra de 20 lotes de ago/2026: todos com inspetor e decisão", "C"),
    ("8.7", "LAB", "As concessões têm aprovação do cliente?", "9 concessões sem aprovação do cliente (tbl_concessoes); REL-26-03", "NC"),
    ("8.7", "LAB", "Lotes retrabalhados são reverificados?", "Amostra de 5 lotes retrabalhados: reinspeção registada", "C"),
    ("8.3.6", "LAB", "As características de inspeção dos produtos novos estão corretas?", "TP-013 (tampa de encaixe) inspecionada à 'rosca'; 7 lotes rejeitados por característica inexistente", "NC"),
    ("9.1.1", "LAB", "Os resultados de monitorização são analisados?", "Painel de KPI mensal revisto no comité", "C"),
    ("10.2", "QUA", "As NC maiores têm ação corretiva e a eficácia é verificada?", "272 NC maiores sem CAPA; eficácia das CAPA 56%", "NC"),
    ("8.2.3", "COM", "As encomendas são revistas antes do compromisso?", "539 encomendas de ago/2026: 3 exceções (1 revisão tardia, 1 sem requisitos legais, 1 sem capacidade)", "NC"),
    ("9.1.2", "COM", "A satisfação é monitorizada e usada?", "Inquérito semestral; AT-2 prazos com a maior lacuna (1,9)", "OM"),
    ("7.1.4", "PCP", "O ambiente de operação é controlado (calor, fadiga)?", "Registo de temperatura da nave; checklist de passagem de turno em implementação", "C"),
    ("9.2.2", "QUA", "O programa de auditoria considera importância, resultados anteriores e alterações?", "Priorização por risco (tbl_priorizacao)", "C"),
]

CONST = [
    # constatações das auditorias do 4.º trimestre (fecho do ano)
    ("CON-Q-26-13", "AUD-Q-26-04", "8.3.4", "NC menor", "RD", "Validação da estanquidade do pote farmacêutico PT-015 feita com o cliente sem registo da validação nem dos critérios de aceitação.", "DD-26-05; correio eletrónico do cliente", "CAPA-Q-26-14", "2026-12-15", "Fechada", "2026-12-10"),
    ("CON-Q-26-14", "AUD-Q-26-04", "8.2.3", "Boa prática", "COM", "Checklist de revisão de encomendas no ERP eliminou as exceções (0 em 40 encomendas de out/2026).", "tbl_revisao_encomendas; ERP", None, None, "Fechada", "2026-10-20"),
    ("CON-Q-26-15", "AUD-Q-26-05", "7.5.3", "Observação", "DOC", "3 documentos com revisão vencida em uso (PR-SGQ-11, PR-SGQ-18, IT-HFS-01).", "tbl_lista_mestra", None, None, "Fechada", "2026-12-15"),
    ("CON-Q-26-16", "AUD-Q-26-05", "10.2.1", "NC menor", "QUA", "17% das NC maiores de out–nov/2026 ainda sem CAPA (melhoria face a set/2026, mas a decisão RPG-2026-01-D01 não está cumprida).", "tbl_snc; tbl_capa", "CAPA-Q-26-12", "2026-12-31", "Em tratamento", None),
    ("CON-Q-26-17", "AUD-Q-26-06", "9.3", "Oportunidade de melhoria", "GES", "Integrar as revisões pela gestão do SGQ, do SGA e do SGE numa única agenda anual do SGI.", "Atas RPG-2026-01, RG-2026 e RD-E-2026-01", None, None, "Aberta", None),
    ("CON-Q-26-18", "AUD-Q-26-07", "8.5.1", "Observação", "SOP", "Cpk do peso nas ISBM-009/010 em 1,18 (meta 1,33): estabilização ainda em curso.", "SPC dez/2026", None, None, "Aberta", None),
    ("CON-Q-26-01", "AUD-Q-26-01", "8.4.1", "NC menor", "CMP", "SUP-005 com 74% de lotes aceites mantido como aprovado condicional sem plano de ação documentado nem prazo.", "Scorecard S2-2025 (classe D); lista de fornecedores aprovados",
     "CAPA-Q-26-05", "2026-06-30", "Fechada", "2026-06-20"),
    ("CON-Q-26-02", "AUD-Q-26-02", "7.2; 8.5.1 e)", "NC menor", "INJ", "Operador temporário a trabalhar sozinho na IM-008 sem validação no posto.", "Matriz de competências; observação no posto (GW-26-07)", "CAPA-Q-26-06", "2026-07-31", "Fechada", "2026-07-25"),
    ("CON-Q-26-03", "AUD-Q-26-03", "8.7.1 d); 8.6", "NC maior", "LAB", "Concessões libertadas para clientes sem aprovação do cliente (9 casos no período), incluindo lotes com defeitos críticos na amostra.",
     "tbl_concessoes (RG-SGQ-14); relato REL-26-03", "CAPA-Q-26-08", "2026-10-31", "Fechada", "2026-10-30"),
    ("CON-Q-26-04", "AUD-Q-26-03", "7.1.5.2 a) b)", "NC menor", "MET", "Dois equipamentos com confirmação metrológica vencida em uso (EQM-022, EQM-031).", "Inventário; etiquetas; OOT-26-02/03", "CAPA-Q-26-09", "2026-10-15", "Fechada", "2026-10-14"),
    ("CON-Q-26-05", "AUD-Q-26-03", "6.3; 8.5.6", "NC menor", "MAN", "Substituição dos compressores sem planeamento da alteração (consequências na qualidade do ar de sopro não avaliadas).", "MOC-Q-26-11 retroativo; NC-SGA-26-06 (SGA)",
     "CAPA-Q-26-10", "2026-11-30", "Fechada", "2026-11-25"),
    ("CON-Q-26-06", "AUD-Q-26-03", "8.3.6; 8.5.1 a)", "NC menor", "LAB", "Característica 'rosca' aplicada à tampa de encaixe TP-013 no plano de inspeção por atributos; 7 lotes rejeitados por uma característica inexistente.",
     "Dataset de inspeção por atributos (TP-013, 85 inspeções de rosca); DC-26-01", "CAPA-Q-26-11", "2026-10-31", "Fechada", "2026-10-29"),
    ("CON-Q-26-07", "AUD-Q-26-03", "10.2.1 b) d)", "NC maior", "QUA", "Ação corretiva não sistemática: 272 NC maiores/críticas sem CAPA; 44% das CAPA avaliadas não eficazes; 49% vencidas.",
     "RG-SGQ-14 tbl_snc; RG-SGQ-18 tbl_capa", "CAPA-Q-26-12", "2026-12-31", "Em tratamento", None),
    ("CON-Q-26-08", "AUD-Q-26-03", "8.5.2 d)", "Observação", "LAB", "Rastreabilidade ao lote de resina depende do FIFO: o consumo só regista o lote de masterbatch.", "RST-26-02/03", None, None, "Aberta", None),
    ("CON-Q-26-09", "AUD-Q-26-03", "7.3 a); 5.2.2 d)", "Observação", "SER", "3 de 10 operadores entrevistados não explicam como a política se aplica ao seu trabalho.", "Entrevistas", None, None, "Fechada", "2026-11-04"),
    ("CON-Q-26-10", "AUD-Q-26-03", "9.1.2", "Oportunidade de melhoria", "COM", "Cumprimento de prazos é o atributo com maior lacuna de satisfação (importância 4,7 vs. satisfação 2,8).", "tbl_atributos (RG-SGQ-15)", None, None, "Aberta", None),
    ("CON-Q-26-11", "AUD-Q-26-03", "7.1.5.1", "Boa prática", "MET", "Estudo Gage R&R calculado por fórmulas sobre os dados brutos, com critérios AIAG e decisão rastreável.", "GRR_Calculo (RG-SGQ-09)", None, None, "Fechada", "2026-09-16"),
    ("CON-Q-26-12", "AUD-Q-26-03", "8.2.3.1", "NC menor", "COM", "Encomendas aceites com revisão depois do compromisso, sem verificação de requisitos legais (alimentar) e sem capacidade confirmada.", "tbl_revisao_encomendas (3 exceções em 539)",
     "CAPA-Q-26-13", "2026-11-15", "Fechada", "2026-11-12"),
]


def prior_rows():
    nc = Q.nonconformance()
    ncp = nc["Process"].map(Q.T_PROC).value_counts()
    c = Q.complaints()
    cp = c["Process"].map(Q.T_PROC).value_counts()
    moc = {"QUA": 1, "SOP": 2, "INJ": 3, "RD": 2, "CMP": 2, "EXP": 1, "MAN": 2, "LAB": 1, "COM": 1, "PCP": 1}
    rows = []
    for code, name, *_ in PROCESSOS:
        imp, prev, req, last = PRIOR[code]
        rows.append(dict(Processo=code, Nome=name, Importancia=imp, NC_Periodo=int(ncp.get(code, 0)), Reclamacoes_Periodo=int(cp.get(code, 0)),
                         Alteracoes_2026=moc.get(code, 0), Resultado_Auditoria_Anterior=prev, Requisitos_Criticos=req, Ultima_Auditoria=dt.date.fromisoformat(last)))
    return rows


def build(out):
    b = Book("RG-SGQ-16", "Auditoria Interna do SGQ — Programa, Execução e Constatações",
             activities="Planear o programa de auditoria com base no risco, qualificar auditores independentes, gerir os riscos do programa, executar auditorias com checklist, registar constatações e acompanhar as ações sem demora injustificada.",
             clauses="9.2.1 a) b); 9.2.2 frequência, métodos, responsabilidades, planeamento e relato; importância dos processos, resultados anteriores e alterações; a)–d) objetivos/critérios/âmbito, objetividade e imparcialidade, relato à gestão, correções e ações corretivas; informação documentada da implementação e dos resultados",
             purpose="Programa de auditoria 2025–2026 com priorização por risco calculada (importância, NC e reclamações reais do dataset, alterações, resultados anteriores, requisitos críticos), auditores com competência e independência, riscos e oportunidades do programa (ISO 19011:2026), checklist e constatações da auditoria integrada SGI de set/2026 e avaliação do programa.",
             links=[("RG-SGQ-18", "CAPA das constatações (ID_CAPA)."), ("RG-SGA-14", "Programa de auditorias do SGA — auditoria integrada AUD-Q-26-03 partilhada."),
                    ("RG-SGQ-17", "Resultados das auditorias como entrada da revisão pela gestão (9.3.2 d3).")],
             guidance=[("ISO 19011:2026 (Academy cap. 92–93)", "Programa → planeamento → execução → evidência → conclusões → relato → acompanhamento → melhoria do programa; riscos e oportunidades do programa; auditoria remota só com evidência suficiente."),
                       ("ISO/TC 176 APG — Internal audits", "Prioridade aos processos críticos para a qualidade, complexos, com problemas passados, que exigem validação ou qualificação; competência e imparcialidade; uso dos resultados para melhorar (tbl_priorizacao)."),
                       ("ISO/TC 176 APG — Nonconformity documenting", "Constatação = requisito + evidência objetiva + condição encontrada; sem prescrever a solução."),
                       ("iso9001help.co.uk — Internal audit", "Programa anual, planos, checklists como apoio (não substituem o julgamento) e relatório.")])
    b.add_list("Processo", PROC_CODES + ["LID"])
    b.add_list("Metodo", ["Presencial", "Remota", "Híbrida", "Híbrida (fornecedor remoto)"])
    b.add_list("EstadoAud", ["Planeada", "Realizada", "Adiada", "Cancelada"])
    b.add_list("TipoConst", ["NC maior", "NC menor", "Observação", "Oportunidade de melhoria", "Boa prática"])
    b.add_list("EstadoConst", ["Aberta", "Em tratamento", "Fechada"])
    b.add_list("ResChk", ["C", "NC", "OBS", "OM"])
    b.add_list("RO", ["Risco", "Oportunidade"])
    b.add_list("SimNao", ["Sim", "Não"])

    acols = [col("ID_Auditor", 7, key="PK", desc="Auditor."), col("Nome", 22, desc="Nome (dataset) ou função."), col("Funcao", 24, desc="Função."),
             col("Qualificacao", 36, desc="Formação em auditoria (ISO 19011:2026)."), col("Conhecimento_Tecnico", 30, desc="Conhecimento do setor/processo."),
             col("Pode_Auditar", 30, desc="Âmbito de atuação."), col("Horas_Auditoria", 8, "int", desc="Horas de auditoria acumuladas."),
             col("Avaliacao_Desempenho", 9, "num1", desc="Avaliação de desempenho (1–5) pelo coordenador (19011 7.6)."), col("Nao_Pode_Auditar", 14, desc="Processos onde trabalha (independência, 9.2.2 b)."),
             col("Competencia_Remota", 9, dv="SimNao", desc="Competente em auditoria remota/híbrida (19011:2026)."), col("Ultima_Formacao", 11, "date", desc="Última formação."),
             col("Qualificado", 9, f='=IF(@ID_Auditor@="","",IF(AND(@Horas_Auditoria@>=6,@Avaliacao_Desempenho@>=3.5),"Sim","Em observação"))', desc="Critério: ≥ 6 h e avaliação ≥ 3,5.")]
    b.table("Auditores", "tbl_auditores", acols, rows_from(input_names(acols), AUDITORES, dates=("Ultima_Formacao",)),
            "Auditores internos: competência, desempenho e independência (9.2.2 b; ISO 19011:2026 cap. 7).", title="AUDITORES INTERNOS — COMPETÊNCIA E IMPARCIALIDADE",
            cf=[("Qualificado", {"Sim": "green", "observação": "orange"})], row_height=30)

    pcols = [col("Processo", 7, key="PK", dv="Processo", desc="Processo."), col("Nome", 40, desc="Processo."),
             col("Importancia", 8, "int", desc="Importância para a conformidade do produto e a satisfação (1–3)."),
             col("NC_Periodo", 8, "int", desc="NC do processo no período (dataset)."), col("Reclamacoes_Periodo", 9, "int", desc="Reclamações atribuídas ao processo (dataset)."),
             col("Alteracoes_2026", 8, "int", desc="Alterações (MOC) que afetam o processo."), col("Resultado_Auditoria_Anterior", 9, "int", desc="1 sem NC · 2 NC menores · 3 NC maior/recorrente."),
             col("Requisitos_Criticos", 8, "int", desc="Requisitos legais/cliente críticos (1–3)."), col("Ultima_Auditoria", 11, "date", desc="Data da última auditoria."),
             col("Pts_NC", 6, "int", f='=IF(@NC_Periodo@>=300,3,IF(@NC_Periodo@>=50,2,IF(@NC_Periodo@>0,1,0)))', desc="0–3 pontos pelas NC."),
             col("Pts_Reclamacoes", 7, "int", f='=IF(@Reclamacoes_Periodo@>=40,3,IF(@Reclamacoes_Periodo@>=10,2,IF(@Reclamacoes_Periodo@>0,1,0)))', desc="0–3 pontos pelas reclamações."),
             col("Pts_Alteracoes", 7, "int", f='=MIN(3,@Alteracoes_2026@)', desc="0–3 pontos pelas alterações."),
             col("Score_Risco", 7, "int", f='=@Importancia@*2+@Pts_NC@+@Pts_Reclamacoes@+@Pts_Alteracoes@+@Resultado_Auditoria_Anterior@+@Requisitos_Criticos@', desc="Pontuação de risco para o programa."),
             col("Frequencia_Meses", 9, "int", f='=IF(@Score_Risco@>=16,6,IF(@Score_Risco@>=11,12,18))', desc="≥ 16 → semestral · 11–15 → anual · ≤ 10 → 18 meses."),
             col("Proxima_Auditoria", 11, "date", f='=EDATE(@Ultima_Auditoria@,@Frequencia_Meses@)', desc="Próxima auditoria requerida."),
             col("Coberto_Programa", 12, f='=IF(COUNTIF(tbl_programa_auditorias[Ambito],"*("&@Processo@&"*")+COUNTIF(tbl_programa_auditorias[Ambito],"* "&@Processo@&",*")+COUNTIF(tbl_programa_auditorias[Ambito],"* "&@Processo@&")*")+COUNTIF(tbl_programa_auditorias[Ambito],"* "&@Processo@&" *")>0,"Sim","Verificar")',
                 desc="O processo aparece no âmbito de alguma auditoria do programa?"),
             col("Alerta", 12, f='=IF(@Proxima_Auditoria@<DataRef,"Auditoria vencida",IF(@Proxima_Auditoria@<DataRef+90,"Nos próximos 90 d","OK"))', desc="Alerta.")]
    b.table("Priorizacao_Risco", "tbl_priorizacao", pcols, prior_rows(), "Priorização do programa de auditoria por risco (9.2.2; APG): importância, NC, reclamações, alterações e resultados anteriores.",
            title="PROGRAMA DE AUDITORIA BASEADO NO RISCO — PRIORIZAÇÃO POR PROCESSO (9.2.2)",
            subtitle="NC e reclamações do dataset por processo · Score = 2×importância + NC + reclamações + alterações + resultado anterior + requisitos críticos · Frequência calculada",
            cf=[("Frequencia_Meses", "@=6", "red"), ("Alerta", {"vencida": "red", "90 d": "orange", "OK": "green"})], row_height=18, freeze_col=2)

    # nomes de coluna comuns ao RG-SGA-14 (tbl_programa_auditorias, tbl_constatacoes): Equipa_Auditora, Processo_Auditado, Clausula,
    # Questao_Auditoria, Evidencia_Objetiva, Classificacao, Controlo_Qualidade
    gcols = [col("ID_Auditoria", 11, key="PK", desc="Auditoria."), col("Ambito", 44, desc="Âmbito e processos (9.2.2 a)."), col("Objetivo", 40, desc="Objetivo (9.2.2 a)."),
             col("Criterios", 30, desc="Critérios (9.2.2 a)."), col("Metodo", 14, dv="Metodo", desc="Presencial / remota / híbrida (19011:2026)."), col("Equipa_Auditora", 16, desc="Auditores (IDs)."),
             col("Data_Planeada", 11, "date", desc="Data planeada."), col("Data_Real", 11, "date", desc="Data de realização.", req=False), col("Estado", 10, dv="EstadoAud", desc="Estado."),
             col("N_Constatacoes", 8, "int", f='=COUNTIF(tbl_constatacoes[ID_Auditoria],@ID_Auditoria@)', desc="Constatações registadas."),
             col("N_NC", 6, "int", f='=COUNTIFS(tbl_constatacoes[ID_Auditoria],@ID_Auditoria@,tbl_constatacoes[Classificacao],"NC*")', desc="NC maiores e menores."),
             col("Relatorio_Emitido", 9, f='=IF(@Estado@<>"Realizada","",IF(@N_Constatacoes@>0,"Sim","Verificar"))', desc="Relatório entregue ao dono do processo e à gestão (9.2.2 c).")]
    b.table("Programa_Auditorias", "tbl_programa_auditorias", gcols, rows_from(input_names(gcols), PROGRAMA, dates=("Data_Planeada", "Data_Real")),
            "Programa de auditorias internas 2025–2026 (9.2.2).", title="PROGRAMA DE AUDITORIAS INTERNAS 2025–2026",
            cf=[("Estado", {"Realizada": "green", "Planeada": "blue", "Adiada": "orange"})], row_height=40)

    rcols = [col("ID", 6, key="PK", desc="Risco/oportunidade do programa."), col("Tipo", 11, dv="RO", desc="Risco ou oportunidade."), col("Descricao", 56, desc="Descrição (ISO 19011:2026 5.3)."),
             col("Efeito", 30, desc="Efeito no programa."), col("Tratamento", 50, desc="Tratamento.")]
    b.table("Riscos_Programa", "tbl_riscos_programa", rcols, rows_from(input_names(rcols), RISCOS_PROG), "Riscos e oportunidades do próprio programa de auditoria (ISO 19011:2026).",
            cf=[("Tipo", {"Risco": "orange", "Oportunidade": "green"})], row_height=30)

    kcols = [col("ID_Pergunta", 9, f='="CHK-"&TEXT(ROW()-1,"00")', desc="Pergunta."), col("ID_Auditoria", 11, desc="Auditoria.", key="FK → tbl_programa_auditorias"),
             col("Clausula", 9, desc="Cláusula."), col("Processo_Auditado", 6, dv="Processo", desc="Processo."), col("Questao_Auditoria", 56, desc="Pergunta de auditoria (apoio à memória, não substitui o julgamento)."),
             col("Evidencia_Objetiva", 60, desc="Evidência objetiva recolhida (entrevista, observação, registo, dado)."), col("Resultado", 6, dv="ResChk", desc="C conforme · NC · OBS · OM.")]
    b.table("Checklist_Auditorias", "tbl_checklist_aud", kcols, [dict(ID_Auditoria="AUD-Q-26-03", Clausula=c, Processo_Auditado=p, Questao_Auditoria=q, Evidencia_Objetiva=e, Resultado=r) for c, p, q, e, r in CHECK] + [dict(ID_Auditoria=a_, Clausula=c, Processo_Auditado=p, Questao_Auditoria=q, Evidencia_Objetiva=e, Resultado=r) for c, p, q, e, r, a_ in CHECK_Q4],
            "Checklist e evidências da auditoria integrada AUD-Q-26-03 (16–18/09/2026).", cf=[("Resultado", {"NC": "red", "OBS": "orange", "OM": "blue", "C": "green"})], row_height=30)

    ccols = [col("ID_Constatacao", 11, key="PK", desc="Constatação."), col("ID_Auditoria", 11, desc="Auditoria.", key="FK → tbl_programa_auditorias"), col("Clausula", 14, desc="Requisito ISO 9001:2026."),
             col("Classificacao", 14, dv="TipoConst", desc="Classificação."), col("Processo_Auditado", 6, dv="Processo", desc="Processo."), col("Constatacao", 60, desc="Condição encontrada."),
             col("Evidencia_Objetiva", 40, desc="Evidência objetiva."), col("ID_CAPA", 11, desc="Ação corretiva (RG-SGQ-18).", key="FK → RG-SGQ-18", req=False),
             col("Prazo", 11, "date", desc="Prazo.", req=False), col("Estado", 12, dv="EstadoConst", desc="Estado."), col("Data_Fecho", 11, "date", desc="Fecho.", req=False),
             col("Controlo_Qualidade", 20, f=('=IF(@ID_Constatacao@="","",IF(AND(LEFT(@Classificacao@,2)="NC",@ID_CAPA@=""),"FALTA CAPA (9.2.2 d)",IF(AND(@Estado@<>"Fechada",@Prazo@<>"",@Prazo@<DataRef),"Atrasada","OK")))'),
                 desc="NC exigem ação corretiva sem demora injustificada.")]
    b.table("Constatacoes", "tbl_constatacoes", ccols, rows_from(input_names(ccols), CONST, dates=("Prazo", "Data_Fecho")),
            "Constatações das auditorias internas com ligação às ações corretivas.", title="CONSTATAÇÕES DE AUDITORIA E ACOMPANHAMENTO (9.2.2 c–d)",
            subtitle="As constatações de set/2026 correspondem a problemas reais visíveis nos registos RG-SGQ-06, 09, 10, 11, 14 e 18",
            cf=[("Classificacao", {"maior": "red", "menor": "orange", "Observação": "yellow", "Oportunidade": "blue", "Boa": "green"}), ("Controlo_Qualidade", {"FALTA": "red", "Atrasada": "red", "OK": "green"})],
            row_height=45, extra_rows=5)

    ws = b.sheet("Avaliacao_Programa", "Avaliação do programa de auditoria (19011:2026 5.7) e KPI-Q-19.")
    title(ws, "AVALIAÇÃO DO PROGRAMA DE AUDITORIA — calculado")
    header_row(ws, 3, ["Indicador", "Valor"], widths=[60, 12])
    P = lambda c_: f"tbl_programa_auditorias[{c_}]"
    K = lambda c_: f"tbl_constatacoes[{c_}]"
    ind = [("Auditorias planeadas até à data de referência", f'=COUNTIFS({P("Data_Planeada")},"<="&DataRef)', "0"),
           ("Auditorias realizadas", f'=COUNTIF({P("Estado")},"Realizada")', "0"), ("KPI-Q-19 — cumprimento do programa", "=IFERROR(B5/B4,\"\")", "0%"),
           ("Constatações totais", f"=COUNTA({K('ID_Constatacao')})", "0"), ("  NC maiores", f'=COUNTIF({K("Classificacao")},"NC maior")', "0"), ("  NC menores", f'=COUNTIF({K("Classificacao")},"NC menor")', "0"),
           ("  observações e oportunidades", f'=COUNTIF({K("Classificacao")},"Observação")+COUNTIF({K("Classificacao")},"Oportunidade de melhoria")', "0"),
           ("Constatações fechadas", f'=COUNTIF({K("Estado")},"Fechada")', "0"), ("NC sem CAPA", f'=COUNTIF({K("Controlo_Qualidade")},"FALTA*")', "0"),
           ("Processos com auditoria vencida", '=COUNTIF(tbl_priorizacao[Alerta],"Auditoria vencida")', "0"),
           ("Auditores qualificados", '=COUNTIF(tbl_auditores[Qualificado],"Sim")', "0")]
    for k, (a, f, fmt) in enumerate(ind):
        cell(ws, 4 + k, 1, a, bold=not a.startswith("  "))
        cell(ws, 4 + k, 2, f, fmt=fmt)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
