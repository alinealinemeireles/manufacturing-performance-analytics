import datetime as dt
from sgalib import *
import sga_extra as X
from dims import *

d = lambda s: dt.date.fromisoformat(s) if s else None

# (ID, Tipo, Cenario, O_Que, A_Quem, Quando, Como, Porque, Resp, Clausula, Feedback, Evidencia, Prevista, Realizada, AlcPrev, AlcReal)
COM = [
    ("COM-01", "Interna", "Divulgar a nova Política Ambiental (rev. 02, 2026)",
     "O que muda na Política Ambiental rev. 02: 7 compromissos (incluindo perdas de granulado, biodiversidade e ciclo de vida) e o que cada trabalhador pode fazer no seu posto.",
     "Todos os trabalhadores dos 3 turnos, temporários e prestadores de serviços residentes (≈ 160 pessoas).",
     "Na semana seguinte à aprovação (22–26/06/2026); depois no acolhimento de cada novo trabalhador e sempre que a política for revista.",
     "Sessões de 10 min no início de cada turno (toolbox), cartaz A3 em cada área e na cantina, publicação no ecrã da entrada e intranet, e cópia no manual de acolhimento.",
     "Garantir que todos conhecem a política e o seu papel (7.3) e recolher ideias de melhoria (7.4, ISO 14001:2026).",
     "Gestor do SGA / EHS (Responsável Ambiental)", "5.2; 7.3; 7.4",
     "Caixa de sugestões e QR code no cartaz para ideias Kaizen; 3 perguntas de compreensão no fim da sessão.",
     "Folhas de presença por turno; fotografias dos cartazes; resultados do questionário.", "2026-06-26", "2026-06-26", 160, 149),
    ("COM-02", "Interna", "Resultados ambientais mensais", "KPI de energia, água, scrap, resíduos e solvente; ações do PAM em atraso.",
     "Gerência, chefias de produção, qualidade, manutenção e SGA.", "Reunião mensal de desempenho (2.ª terça-feira).", "Painel Power BI e ata da reunião.",
     "Decidir com base em dados (9.1.1).", "Gestor do SGA / EHS (Responsável Ambiental)", "7.4; 9.1.1", "Decisões e responsáveis registados em ata.",
     "Atas mensais.", "2026-09-08", "2026-09-08", 9, 9),
    ("COM-03", "Interna", "Alerta de desvio (solvente +15%)", "Desvio do consumo de solvente, práticas corretas e pedido de colaboração.",
     "Operadores e chefe de serigrafia (3 turnos).", "Imediatamente após a deteção do desvio.", "Toolbox de 10 min no posto e aviso no quadro da serigrafia.",
     "Conter o desvio (PAM-26-07) e envolver os operadores na investigação.", "Gestor do SGA / EHS (Responsável Ambiental)", "7.4; 10.2",
     "Operadores indicaram 3 causas prováveis (registadas no RG-SGA-13).", "Folha de presença; registo das sugestões.", "2026-09-09", "2026-09-10", 7, 7),
    ("COM-04", "Externa", "Requisitos ambientais a fornecedores críticos", "Critérios ambientais de compra (certificação do conteúdo reciclado, ISO 14001, Operation Clean Sweep).",
     "10 fornecedores de resina e masterbatch.", "Na homologação e na revisão anual.", "Carta de requisitos + questionário ESG online.",
     "Controlar/influenciar processos e produtos fornecidos externamente (8.1, ISO 14001:2026).", "Responsável de Compras", "7.4; 8.1",
     "Respostas ao questionário (RG-SGA-11).", "Questionários respondidos.", "2026-06-30", "2026-07-15", 10, 8),
    ("COM-05", "Externa", "Resposta a reclamação da vizinhança (ruído)", "Receção da reclamação, medidas em curso e prazo da avaliação acústica.",
     "Reclamante e Junta de Freguesia.", "Resposta em ≤ 5 dias úteis; fecho após o relatório acústico.", "Carta/e-mail e contacto telefónico.",
     "Manter a relação com a comunidade (4.2) e demonstrar tratamento.", "Gestor do SGA / EHS (Responsável Ambiental)", "7.4; 9.1.2",
     "Pedido de feedback ao reclamante após a resposta.", "Registo de reclamação REC-2026-03.", "2026-09-19", "2026-09-18", 2, 2),
    ("COM-06", "Externa", "Reporte a autoridades", "MIRR anual, controlo de fugas de gases fluorados, relatório SGCIE.",
     "APA / DGEG.", "Nos prazos legais (calendário RG-SGA-04).", "Plataformas SILiAmb e SGCIE.", "Cumprir obrigações de conformidade.",
     "Gestor do SGA / EHS (Responsável Ambiental)", "6.1.3; 7.4", "—", "Comprovativos de submissão.", "2026-03-31", "2026-03-18", 1, 1),
    ("COM-07", "Externa", "Emergência ambiental com impacte externo", "Tipo de ocorrência, medidas tomadas e riscos para o exterior.",
     "112 / bombeiros, entidade gestora de águas residuais, APA e vizinhos.", "Imediatamente (≤ 1 h) após ativação do plano de emergência.",
     "Telefone (lista de contactos da IT-SGA-01) e comunicado escrito posterior.", "Limitar consequências (8.2).",
     "Diretor Industrial", "7.4; 8.2", "Relatório pós-emergência.", "Registo de comunicações do incidente.", "", "", 0, 0),
    ("COM-08", "Interna", "Caixa de sugestões ambientais (Kaizen)", "Convite a propor pequenas melhorias ambientais com poupança.",
     "Todos os trabalhadores.", "Permanente; revisão mensal das ideias.", "Caixa física + QR code; reconhecimento mensal da melhor ideia.",
     "Permitir que os trabalhadores contribuam para a melhoria contínua (7.4, ISO 14001:2026).", "Gerente de Produção", "7.4; 10.1",
     "Ideias registadas no RG-SGA-16.", "Registo de ideias KZ.", "2026-09-30", "2026-10-01", 160, 142),
]

DOCS = [
    ("POL-SGA", "Política Ambiental", "Política", "01", "2024-03-10", "Diretor Geral", "Obsoleto", "", "Arquivo SGA (carimbo 'OBSOLETO')", "Retirada dos quadros em 26/06/2026", "5.2"),
    ("POL-SGA", "Política Ambiental", "Política", "02", "2026-06-19", "Diretor Geral", "Em vigor", "rev. 01", "Intranet; cartazes em todas as áreas", "Todas as áreas", "5.2"),
    ("PR-SGA-01", "Identificação e avaliação de aspetos ambientais (base PR.G.01.01)", "Procedimento", "01", "2026-05-15", "Diretor Geral", "Em vigor", "rev. 00", "Intranet SGA", "SGA; chefias", "6.1.2"),
    ("PR-SGA-02", "Gestão de riscos e oportunidades (base PG-SGI-006)", "Procedimento", "00", "2026-04-10", "Diretor Geral", "Em vigor", "", "Intranet SGA", "SGA; chefias", "6.1.4; 6.1.5"),
    ("PR-SGA-03", "Obrigações de conformidade e avaliação da conformidade", "Procedimento", "00", "2026-04-10", "Diretor Geral", "Em vigor", "", "Intranet SGA", "SGA", "6.1.3; 9.1.2"),
    ("PR-SGA-04", "Gestão de resíduos", "Procedimento", "02", "2025-11-20", "Diretor Industrial", "Em vigor", "rev. 01", "Intranet; parque de resíduos", "Armazém; produção", "8.1"),
    ("PR-SGA-05", "Preparação e resposta a emergências", "Procedimento", "01", "2025-10-05", "Diretor Industrial", "Em revisão", "rev. 00", "Intranet SGA", "Todas as áreas", "8.2"),
    ("MAN-SGA-01", "Manual do SGA — âmbito, estrutura e correspondência com a ISO 14001:2026", "Manual", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "SGA; chefias; partes interessadas (âmbito)", "4.3; 4.4"),
    ("PR-SGA-06", "Planeamento de alterações (gestão de mudanças)", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "Todas as áreas", "6.3"),
    ("PR-SGA-07", "Competência, consciencialização e comunicação", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "RH; chefias; SGA", "7.2; 7.3; 7.4"),
    ("PR-SGA-08", "Controlo da informação documentada", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "SGA", "7.5"),
    ("PR-SGA-09", "Controlo operacional e processos externos", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "Produção; utilidades; compras", "8.1"),
    ("PR-SGA-10", "Monitorização, medição, análise, avaliação e calibração", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "SGA; manutenção", "9.1.1"),
    ("PR-SGA-11", "Auditoria interna e revisão pela gestão", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "SGA; gerência", "9.2; 9.3"),
    ("PR-SGA-12", "Incidentes, não conformidades, ação corretiva e melhoria contínua", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "Todas as áreas", "10.1; 10.2"),
    ("PR-SGA-13", "Inventário de GEE e indicadores ESG ambientais", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "SGA; finanças; compras", "9.1.1; 6.2"),
    ("PR-SGA-14", "Alegações ambientais e declarações de produto", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "R&D; comercial", "7.4; 8.1"),
    ("PR-SGA-15", "Conceção para reciclagem e conformidade de embalagens (PPWR, RecyClass)", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "R&D; qualidade; compras; comercial", "8.1; 6.1.3"),
    ("PR-SGA-16", "Gestão de produtos químicos — REACH, CLP, SVHC e risco químico", "Procedimento", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "Engenharia; produção; manutenção; compras; armazém; R&D", "6.1.3; 8.1; 9.1.2"),
    ("PL-SGA-01", "Plano de transição climática 2026–2030", "Plano", "00", "2026-10-15", "Diretor Geral", "Em vigor", "", "Documentos_SGA_Plasticom", "Gerência", "6.2; 4.1"),
    ("IT-SGA-01", "Resposta a derrames de produtos químicos", "Instrução de trabalho", "01", "2026-10-29", "Gestor do SGA", "Em vigor", "rev. 00", "Junto a cada kit de derrame", "Armazém; serigrafia; injeção; manutenção", "8.2"),
    ("IT-SGA-02", "Resposta a incêndio com retenção das águas de combate", "Instrução de trabalho", "00", "2026-02-10", "Diretor Industrial", "Em vigor", "", "Portaria; armazém de MP", "Chefes de turno; portaria", "8.2"),
    ("IT-SER-03", "Limpeza de ecrãs e rodos na serigrafia", "Instrução de trabalho", "02", "2026-11-10", "Gerente de Produção", "Em vigor", "rev. 01", "Posto SS-001 e SS-002", "Serigrafia", "8.1"),
    ("RG-SGA-01", "Contexto — PESTEL, SWOT, partes interessadas, 5 forças e TOWS (SGA e SGI)", "Registo", "02", "2026-09-24", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "4.1"),
    ("RG-SGA-02", "Riscos e oportunidades — registo corporativo (política, apetite, riscos, planos SGI, KRI, BowTie, auditorias SGI)", "Registo", "03", "2026-09-24", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "6.1.4"),
    ("RG-SGA-03", "Matriz de aspetos e impactes (Mod.G.07.00)", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "6.1.2"),
    ("RG-SGA-04", "Requisitos legais e conformidade (Mod.G.06.02)", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "6.1.3; 9.1.2"),
    ("RG-SGA-05", "Objetivos, metas e KPI", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "6.2"),
    ("RG-SGA-06", "Plano de Ações de Melhoria (Mod.G.10.00)", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "6.1.5; 10"),
    ("RG-SGA-07", "Não conformidades e incidentes (RNC)", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "10.2"),
    ("RG-SGA-08", "Matriz de competências", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA; RH", "7.2; 7.3"),
    ("RG-SGA-09", "Comunicação e controlo documental", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "7.4; 7.5"),
    ("RG-SGA-10", "Controlo operacional — rondas ambientais", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA; produção", "8.1"),
    ("RG-SGA-11", "Fornecedores e ciclo de vida", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "Compras", "8.1"),
    ("RG-SGA-12", "Emergências ambientais", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "8.2"),
    ("RG-SGA-13", "Monitorização, medição e desempenho", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "9.1.1"),
    ("RG-SGA-14", "Auditoria interna", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "9.2"),
    ("RG-SGA-15", "Revisão pela gestão", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "Gerência", "9.3"),
    ("RG-SGA-16", "Melhoria contínua — Kaizen e EMAS", "Registo", "01", "2026-09-23", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA", "10.1"),
    ("RG-SGA-17", "Análise de dupla materialidade", "Registo", "02", "2026-09-24", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA; gerência", "4.1; 4.2; 6.1"),
    ("RG-SGA-18", "Planeamento de alterações", "Registo", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "Todas as áreas", "6.3"),
    ("RG-SGA-19", "ESG ambiental — calculadora de GEE, metas, pegada e indicadores", "Registo", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "SGA; gerência; comercial", "9.1.1; 6.2"),
    ("RG-SGA-21", "Gestão de produtos químicos (REACH, CLP, SVHC e risco químico)", "Registo", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "Engenharia; produção; manutenção; compras; armazém", "6.1.3; 8.1; 9.1.2"),
    ("RG-SGA-20", "Reciclabilidade e conformidade de embalagens (RecyClass / PPWR)", "Registo", "00", "2026-09-24", "Diretor Geral", "Em vigor", "", "Registos_SGA_Plasticom", "R&D; qualidade; compras; comercial", "8.1; 6.1.3; 7.4"),
]

ELEMENTOS = [
    ("EL-01", "Identificação: título e código únicos", "Sim", "Garante que se sabe exatamente que documento é e que não é confundido com outro."),
    ("EL-02", "Estado de revisão: n.º de versão/revisão e data de emissão", "Sim", "Permite confirmar que é a versão mais recente (comparar com a lista mestra)."),
    ("EL-03", "Aprovação: quem aprovou e quando (assinatura/validação eletrónica)", "Sim", "Só documentos aprovados por pessoa autorizada podem ser usados."),
    ("EL-04", "Indicação 'Em vigor' e distribuição controlada no ponto de uso", "Não", "A cópia no posto deve ser a da lista mestra; cópias impressas não controladas marcadas como tal."),
    ("EL-05", "Legibilidade, formato e meio adequados", "Não", "Documento legível e utilizável no local."),
    ("EL-06", "Proteção e retenção (obsoletos retirados ou identificados)", "Não", "Versões antigas retiradas dos pontos de uso ou carimbadas 'OBSOLETO'."),
]

VERIF = [  # (ID_Verificacao, Data, Documento, Local, Versao encontrada, {EL: OK/NOK}, Obs)
    ("VD-01", "2026-09-15", "PR-SGA-04", "Parque de resíduos", "02", {"EL-01": "OK", "EL-02": "OK", "EL-03": "OK", "EL-04": "OK", "EL-05": "OK", "EL-06": "OK"}, "Conforme."),
    ("VD-02", "2026-09-15", "IT-SGA-01", "Kit KIT-03 (injeção/serigrafia)", "00", {"EL-01": "OK", "EL-02": "OK", "EL-03": "OK", "EL-04": "OK", "EL-05": "NOK", "EL-06": "OK"}, "Folha plastificada ilegível (manchas); conteúdo sem etapa pós-uso (ver NC-SGA-26-03)."),
    ("VD-03", "2026-09-16", "IT-SER-03", "Posto SS-001", "00", {"EL-01": "OK", "EL-02": "NOK", "EL-03": "OK", "EL-04": "NOK", "EL-05": "OK", "EL-06": "NOK"}, "Versão 00 (obsoleta) no posto; a lista mestra indica rev. 01 em vigor. Retirada e substituída."),
    ("VD-04", "2026-09-16", "POL-SGA", "Cantina", "02", {"EL-01": "OK", "EL-02": "OK", "EL-03": "OK", "EL-04": "OK", "EL-05": "OK", "EL-06": "OK"}, "Conforme; cartaz rev. 01 já retirado."),
    ("VD-05", "2026-09-16", "PR-SGA-05", "Portaria", "01", {"EL-01": "OK", "EL-02": "OK", "EL-03": "NOK", "EL-04": "OK", "EL-05": "OK", "EL-06": "OK"}, "Cópia impressa sem assinatura de aprovação."),
]


def build(out):
    b = Book("RG-SGA-09", "Comunicação Ambiental e Controlo da Informação Documentada",
             activities="Atividade 4.2 — Planeamento da Comunicação (4 Q's, cenário COM-01: divulgar a nova Política Ambiental) e Controlo Documental (3 elementos obrigatórios). A reflexão 'Documento obsoleto vs em vigor' está no documento Word.",
             clauses="7.4 Comunicação (ISO 14001:2026: permitir que os trabalhadores contribuam para a melhoria contínua); 7.5 Informação documentada (disponível / retida)",
             purpose="Planear as comunicações internas e externas pela regra dos 4 Q (O quê, A quem, Quando, Como) e medir o alcance; manter a lista mestra de documentos com estado (em vigor, obsoleto, em revisão) e registar verificações documentais no terreno com os elementos obrigatórios de controlo.",
             links=[("RG-SGA-16 Kaizen", "COM-08 alimenta a caixa de sugestões."), ("RG-SGA-07 NC", "Verificações NOK podem originar NC.")])
    b.add_list("Tipo", ["Interna", "Externa"])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("TipoDoc", ["Política", "Procedimento", "Instrução de trabalho", "Registo", "Plano", "Modelo"])
    b.add_list("EstadoDoc", ["Em vigor", "Em revisão", "Obsoleto"])
    b.add_list("OKNOK", ["OK", "NOK"])
    b.add_list("SimNao", ["Sim", "Não"])

    ccols = [
        col("ID_Comunicacao", 10, desc="Identificador.", key="PK"), col("Tipo", 9, dv="Tipo", desc="Interna ou externa."),
        col("Cenario", 30, desc="Cenário de comunicação."), col("O_Que_Mensagem", 48, desc="O quê? (mensagem)"),
        col("A_Quem_Publico", 34, desc="A quem? (público)"), col("Quando_Momento", 34, desc="Quando? (momento)"),
        col("Como_Canal", 40, desc="Como? (canal)"), col("Porque_Objetivo", 36, desc="Porquê? (objetivo da comunicação)"),
        col("Responsavel", 24, dv="Funcao", desc="Quem comunica."), col("Clausula", 10, desc="Requisito ISO."),
        col("Participacao_Feedback", 36, desc="Como se recolhe feedback/participação (7.4, 2026)."),
        col("Evidencia", 30, desc="Registo que prova a comunicação."),
        col("Data_Prevista", 11, "date", desc="Data prevista.", req=False), col("Data_Realizada", 11, "date", desc="Data realizada.", req=False),
        col("Alcance_Previsto", 9, "int", desc="N.º de destinatários previsto."), col("Alcance_Real", 9, "int", desc="N.º de destinatários atingidos."),
        col("Taxa_Alcance", 9, "pct", f='=IF(@Alcance_Previsto@=0,"",@Alcance_Real@/@Alcance_Previsto@)', desc="Alcance real ÷ previsto."),
        col("Estado", 12, f='=IF(@Data_Prevista@="","Por ocorrência",IF(@Data_Realizada@<>"",IF(@Data_Realizada@<=@Data_Prevista@,"Realizada","Realizada c/ atraso"),IF(@Data_Prevista@<DataRef,"Atrasada","Planeada")))', desc="Estado calculado."),
        col("Selecionado_Atv_4_2", 10, dv="SimNao", desc="Cenário da Atividade 4.2."),
    ]
    cn = [c["name"] for c in ccols if not c["f"]]
    crow = []
    for c in COM:
        dd = dict(zip(cn[:-1], c))
        dd["Data_Prevista"], dd["Data_Realizada"] = d(dd["Data_Prevista"]), d(dd["Data_Realizada"])
        dd["Selecionado_Atv_4_2"] = "Sim" if c[0] == "COM-01" else "Não"
        crow.append(dd)
    b.table("Matriz_Comunicacao", "tbl_comunicacao", ccols, crow, "Matriz de comunicação (regra dos 4 Q + porquê, responsável, evidência e alcance).",
            title="MATRIZ DE COMUNICAÇÃO AMBIENTAL — REGRA DOS 4 Q", subtitle="O quê? · A quem? · Quando? · Como? — mais Porquê, Responsável, Evidência e Alcance (calculado)",
            cf=[("Estado", {"Atrasada": "red", "atraso": "orange", "Realizada": "green", "Planeada": "yellow"}), ("Selecionado_Atv_4_2", {"Sim": "purple"})],
            row_height=95, freeze_col=3)

    dcols = [
        col("Codigo", 10, desc="Código do documento.", key="PK (com Versao)"), col("Titulo", 44, desc="Título."),
        col("Tipo", 16, dv="TipoDoc", desc="Tipo."), col("Versao", 7, desc="Versão/revisão."),
        col("Data_Aprovacao", 11, "date", desc="Data de aprovação.", req=False), col("Aprovador", 16, desc="Quem aprovou.", req=False),
        col("Estado", 11, dv="EstadoDoc", desc="Em vigor / Em revisão / Obsoleto."), col("Substitui", 9, desc="Versão substituída.", req=False),
        col("Localizacao", 28, desc="Onde está disponível."), col("Ponto_de_Uso", 26, desc="Onde é usado."), col("Clausula", 10, desc="Requisito ISO."),
        col("Proxima_Revisao", 11, "date", f='=IF(OR(@Estado@="Obsoleto",@Data_Aprovacao@=""),"",EDATE(@Data_Aprovacao@,24))', desc="Revisão a cada 24 meses."),
        col("Alerta", 20, f='=IF(@Estado@="Obsoleto","Retirar dos pontos de uso",IF(@Data_Aprovacao@="","Sem aprovação",IF(@Proxima_Revisao@<DataRef,"Revisão vencida",IF(@Estado@="Em revisão","Em revisão","OK"))))', desc="Alerta automático."),
    ]
    dn = [c["name"] for c in dcols if not c["f"]]
    drow = []
    for x in DOCS:
        dd = dict(zip(dn, x))
        dd["Data_Aprovacao"] = d(dd["Data_Aprovacao"])
        for k in ("Aprovador", "Substitui"):
            dd[k] = dd[k] or None
        drow.append(dd)
    b.table("Lista_Mestra", "tbl_lista_mestra", dcols, drow, "Lista mestra de documentos e registos do SGA (estado, versão, aprovação, revisão).",
            cf=[("Estado", {"Obsoleto": "gray", "Em revisão": "yellow", "Em vigor": "green"}),
                ("Alerta", {"vencida": "red", "Sem aprovação": "red", "Retirar": "orange", "Em revisão": "yellow", "OK": "green"})], row_height=30)

    ecols = [col("ID_Elemento", 9, desc="Elemento de controlo.", key="PK"), col("Elemento", 50, desc="O que verificar no documento."),
             col("Obrigatorio_Atv_4_2", 11, dv="SimNao", desc="Um dos 3 elementos indicados na Atividade 4.2."), col("Porque", 60, desc="Porque garante que o documento está válido para uso.")]
    b.table("Elementos_Controlo", "tbl_elementos", ecols, [dict(zip([c["name"] for c in ecols], e)) for e in ELEMENTOS],
            "Elementos obrigatórios de controlo documental (checklist).", cf=[("Obrigatorio_Atv_4_2", {"Sim": "purple"})], row_height=30)

    vrows = []
    for vid, dat, doc, loc, ver, res, obs in VERIF:
        for el, r in res.items():
            vrows.append(dict(ID_Verificacao=vid, Data=d(dat), Codigo_Documento=doc, Local=loc, Versao_Encontrada=ver, ID_Elemento=el, Resultado=r, Observacao=obs if r == "NOK" else None))
    vcols = [col("ID_Verificacao", 10, desc="Verificação no terreno.", key="PK (com ID_Elemento)"), col("Data", 11, "date", desc="Data."),
             col("Codigo_Documento", 11, desc="Documento verificado.", key="FK → tbl_lista_mestra"), col("Local", 26, desc="Ponto de uso."),
             col("Versao_Encontrada", 9, desc="Versão encontrada no local."),
             col("Versao_Em_Vigor", 9, f='=IFERROR(INDEX(tbl_lista_mestra[Versao],MATCH(1,INDEX((tbl_lista_mestra[Codigo]=@Codigo_Documento@)*(tbl_lista_mestra[Estado]<>"Obsoleto"),0),0)),"")', desc="Versão em vigor segundo a lista mestra."),
             col("Versao_Correta", 9, f='=IF(@Versao_Em_Vigor@="","?",IF(@Versao_Encontrada@=@Versao_Em_Vigor@,"Sim","Não"))', desc="A versão no local é a em vigor?"),
             col("ID_Elemento", 9, desc="Elemento verificado.", key="FK → tbl_elementos"), col("Resultado", 9, dv="OKNOK", desc="OK / NOK."),
             col("Observacao", 50, desc="Descrição do desvio.", req=False)]
    b.table("Verificacao_Documental", "tbl_verif_documental", vcols, vrows, "Resultados de verificações documentais no terreno (formato longo: documento × elemento).",
            cf=[("Resultado", {"NOK": "red", "OK": "green"}), ("Versao_Correta", {"Não": "red", "Sim": "green"})], row_height=30)

    ws = b.sheet("Resumo_Atividade_4_2", "Ficha da Atividade 4.2: os 4 Q do cenário COM-01 e os 3 elementos obrigatórios de controlo documental (calculado).", tab_color="7030A0")
    ws["A1"] = "ATIVIDADE 4.2 — COMUNICAÇÃO (4 Q) E CONTROLO DOCUMENTAL"
    ws["A1"].font = F_TITLE
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 100
    T = lambda f: b.ref("tbl_comunicacao", f)
    m = f'MATCH("COM-01",{T("ID_Comunicacao")},0)'
    r = 3
    ws.cell(row=r, column=1, value="1. COMUNICAÇÃO").font = F_BOLD
    r += 1
    for lab, fld in [("Cenário", "Cenario"), ("O Quê? (mensagem)", "O_Que_Mensagem"), ("A Quem? (público)", "A_Quem_Publico"),
                     ("Quando? (momento)", "Quando_Momento"), ("Como? (canal)", "Como_Canal"), ("Porquê? (objetivo)", "Porque_Objetivo"),
                     ("Responsável", "Responsavel"), ("Participação / feedback", "Participacao_Feedback"), ("Evidência", "Evidencia"), ("Alcance atingido", "Taxa_Alcance")]:
        c = form_block(ws, r, lab, f'=INDEX({T(fld)},{m})', vw=1, height=40 if fld not in ("Cenario", "Responsavel", "Taxa_Alcance") else None)
        if fld == "Taxa_Alcance":
            c.number_format = "0%"
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="2. CONTROLO DOCUMENTAL — 3 elementos obrigatórios (ex.: Procedimento de Resíduos PR-SGA-04)").font = F_BOLD
    r += 1
    for k in range(1, 4):
        form_block(ws, r, f'=INDEX(tbl_elementos[Elemento],{k})', f'=INDEX(tbl_elementos[Porque],{k})', vw=1, height=32)
        r += 1
    X.extra_09(b)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
