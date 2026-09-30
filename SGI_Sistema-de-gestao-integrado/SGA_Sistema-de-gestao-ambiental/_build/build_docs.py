"""Gera os documentos controlados do SGA (Word): Manual, procedimentos PR-SGA-01 a 12 e instruções IT-SGA-02 / IT-SER-03.
Uso: python build_docs.py            → cria só os documentos que ainda não existem (preserva edições manuais)
     python build_docs.py --force    → regenera todos (sobrescreve edições manuais)
Os documentos remetem para os registos (RG-SGA-nn) e para as tabelas (tbl_*) onde fica a evidência.
"""
import os
import re
import unicodedata
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm
from sgalib import EMPRESA, NORMA, AUTOR, APROVADOR

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "Documentos_SGA_Plasticom"))
TEAL = RGBColor(0x1F, 0x4E, 0x5F)


def slug(text, n=55):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_")[:n]


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), hexcolor)
    tcPr.append(sh)


def new_doc(code, title, version, date, state, approver=APROVADOR):
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = "Arial", Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2)
        s.top_margin = s.bottom_margin = Cm(1.8)
        hp = s.header.paragraphs[0]
        hp.text = f"PLASTICOM — Sistema de Gestão Ambiental ({NORMA})    |    {code} rev. {version}"
        hp.runs[0].font.size, hp.runs[0].font.color.rgb = Pt(8), RGBColor(0x60, 0x60, 0x60)
        fp = s.footer.paragraphs[0]
        fp.text = "Documento controlado: a versão eletrónica em Documentos_SGA_Plasticom é a versão em vigor; cópias impressas não são controladas."
        fp.runs[0].font.size, fp.runs[0].font.color.rgb = Pt(7), RGBColor(0x80, 0x80, 0x80)
    p = doc.add_paragraph()
    r = p.add_run(title.upper())
    r.bold, r.font.size, r.font.color.rgb = True, Pt(15), TEAL
    t = doc.add_table(rows=2, cols=6)
    t.style = "Table Grid"
    hdr = ["Código", "Versão", "Data de aprovação", "Elaborado por", "Aprovado por", "Estado"]
    val = [code, version, date, AUTOR, approver, state]
    for i, (h, v) in enumerate(zip(hdr, val)):
        c = t.cell(0, i)
        c.text = h
        c.paragraphs[0].runs[0].bold = True
        c.paragraphs[0].runs[0].font.size = Pt(8)
        shade(c, "DCEBEF")
        t.cell(1, i).text = str(v)
        t.cell(1, i).paragraphs[0].runs[0].font.size = Pt(8)
    doc.add_paragraph()
    return doc


def h(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold, r.font.size, r.font.color.rgb = True, Pt(11.5), TEAL
    p.paragraph_format.space_before = Pt(8)


def para(doc, text):
    doc.add_paragraph(text).paragraph_format.space_after = Pt(4)


def bullets(doc, items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")


def table(doc, header, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    for i, hh in enumerate(header):
        c = t.cell(0, i)
        c.text = hh
        c.paragraphs[0].runs[0].bold = True
        c.paragraphs[0].runs[0].font.size = Pt(8.5)
        shade(c, "1F4E5F")
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = str(v)
            for pr in cells[i].paragraphs:
                for rr in pr.runs:
                    rr.font.size = Pt(8.5)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph()


def history(doc, rows):
    h(doc, "Histórico de revisões")
    table(doc, ["Versão", "Data", "Alteração"], rows, [2, 3, 12])


# ------------------------------------------------------------------------------------------ procedimentos (conteúdo)
# code: (title, version, date, state, objetivo, âmbito, referências, responsabilidades[(função, resp)], passos[str], registos[(registo, onde)], histórico)
PROC = {
    "PR-SGA-01": ("Identificação e avaliação de aspetos ambientais", "01", "2026-05-15", "Em vigor",
                  "Identificar os aspetos ambientais das atividades, produtos e serviços que a Plasticom pode controlar e influenciar, numa perspetiva de ciclo de vida, e determinar os significativos.",
                  "Todas as atividades da Unidade 1, em condições normais, anormais e de emergência, e as fases do ciclo de vida: aquisição, conceção, produção, distribuição, uso e fim de vida.",
                  ["ISO 14001:2026 6.1.2 (base PR.G.01.01)", "PR-SGA-02, PR-SGA-06"],
                  [("Gestor do SGA / EHS", "Coordena o levantamento, aplica os critérios e mantém a matriz."), ("Responsáveis de área", "Participam na identificação e validam os controlos."),
                   ("Diretor Industrial", "Aprova a matriz e os aspetos significativos.")],
                  ["Levantar atividades por processo e fase do ciclo de vida (entradas, saídas, recursos, resíduos, emissões).",
                   "Para cada atividade, descrever o aspeto (causa) e o impacte (efeito), a condição de operação (normal, anormal, emergência) e a temporalidade.",
                   "Pontuar Frequência (F), Magnitude (M), Gravidade (G) e Legislação/partes interessadas (L); calcular IRA = (F + M) × G × L.",
                   "Classificar: AAS se IRA ≥ 40 ou L = 2 (regra de ouro: requisito legal ou parte interessada relevante); Moderado 20–39 (com ação no plano); Não significativo 0–19; Oportunidade tática −1 a −14; AAS benéfico ≤ −15.",
                   "Para cada AAS definir controlo operacional, objetivo ou ação do PAM e monitorização; ligar a requisitos legais e a riscos/oportunidades.",
                   "Rever anualmente e sempre que houver alteração (RG-SGA-18), incidente relevante (RG-SGA-07) ou novo requisito legal."],
                  [("RG-SGA-03", "tbl_aspetos, tbl_impactes, tbl_aspeto_impacte"), ("RG-SGA-18", "tbl_alteracoes (gatilho de revisão)")],
                  [("00", "2025-01-10", "Emissão inicial (base PR.G.01.01)."), ("01", "2026-05-15", "Condição de emergência separada da anormal (ISO 14001:2026); perspetiva de ciclo de vida obrigatória.")]),
    "PR-SGA-02": ("Gestão de riscos e oportunidades", "00", "2026-04-10", "Em vigor",
                  "Determinar os riscos e oportunidades relacionados com aspetos ambientais, obrigações de conformidade e contexto (incluindo condições ambientais) e planear ações para os tratar.",
                  "Riscos e oportunidades do SGA e do registo corporativo multiárea.",
                  ["ISO 14001:2026 6.1.1, 6.1.4, 6.1.5", "PG-SGI-006 (base)", "ISO 31000, IEC 31010"],
                  [("Gestor do SGA / EHS", "Mantém o registo e a metodologia P × S."), ("Donos dos riscos", "Avaliam, tratam e monitorizam."), ("Diretor Geral", "Aprova o apetite ao risco e a aceitação dos riscos significativos.")],
                  ["Identificar riscos e oportunidades a partir do contexto (PESTEL, SWOT), partes interessadas, aspetos significativos e obrigações de conformidade.",
                   "Avaliar com a matriz P × S do curso (P 1–3; S −3 a +3) e, no registo corporativo, com a escala 5×5 (inerente, atual, residual).",
                   "Decidir o tratamento (assumir, monitorizar, mitigar, eliminar, transferir; explorar oportunidades) e transferir as ações para o PAM.",
                   "Definir o critério de eficácia, o KRI e, para riscos Altos/Críticos, a análise BowTie.",
                   "Rever a cada 6 meses os significativos e a cada 12 meses os restantes, ou após alteração ou incidente."],
                  [("RG-SGA-02", "tbRiscos, tbOportunidades, tbKRI, tbBowTie, tbPlanos"), ("RG-SGA-06", "tbl_pam"), ("RG-SGA-17", "tbl_dma_iro (dupla materialidade)")],
                  [("00", "2026-04-10", "Emissão (base PG-SGI-006), separando 6.1.4 (determinar) de 6.1.5 (planear ações).")]),
    "PR-SGA-03": ("Obrigações de conformidade e avaliação da conformidade", "00", "2026-04-10", "Em vigor",
                  "Identificar, aceder e avaliar periodicamente o cumprimento dos requisitos legais e dos outros requisitos que a Plasticom decide cumprir.",
                  "Requisitos ambientais UE, nacionais e municipais; requisitos de clientes e compromissos voluntários (ex.: Operation Clean Sweep).",
                  ["ISO 14001:2026 4.2 c), 6.1.3, 9.1.2"],
                  [("Gestor do SGA / EHS", "Vigilância legislativa mensal e avaliação da conformidade."), ("Responsáveis de área", "Evidências de cumprimento."), ("Diretor Geral", "Recursos para corrigir incumprimentos.")],
                  ["Vigilância legislativa mensal (Diário da República, EUR-Lex, APA, associação setorial) e registo de novos diplomas.",
                   "Decidir, a partir das partes interessadas (tbl_partes_interessadas), que necessidades se tornam obrigações de conformidade.",
                   "Para cada requisito aplicável, definir disposições internas, evidência e periodicidade de avaliação.",
                   "Avaliar a conformidade (C / NC / Futuro) com evidência objetiva; incumprimentos abrem NC e ação no PAM.",
                   "Manter o calendário de obrigações recorrentes (MIRR, e-GAR, F-gas, Legionella, autocontrolo) e reportar à revisão pela gestão."],
                  [("RG-SGA-04", "tbl_legal, tbl_obrigacoes, tbl_hist_conformidade"), ("RG-SGA-01", "tbl_partes_interessadas"), ("RG-SGA-13", "tbl_analises")],
                  [("00", "2026-04-10", "Emissão.")]),
    "PR-SGA-04": ("Gestão de resíduos", "02", "2025-11-20", "Em vigor",
                  "Assegurar a separação, armazenagem, classificação, transporte e encaminhamento dos resíduos para operadores licenciados, privilegiando a valorização.",
                  "Todos os resíduos produzidos na Unidade 1 (scrap, embalagens, perigosos, indiferenciados).",
                  ["RGGR (DL 102-D/2020)", "Portaria 145/2017 (e-GAR)", "ISO 14001:2026 8.1"],
                  [("Responsável de Armazém e Logística", "Parque de resíduos, e-GAR e conferência mensal no SILiAmb."), ("Chefes de turno", "Segregação na origem."), ("Gestor do SGA / EHS", "MIRR anual e avaliação de operadores.")],
                  ["Separar na origem por código LER em contentores identificados; perigosos em bacia e sob cobertura.",
                   "Reintegrar scrap limpo por moagem sempre que a qualidade o permita (regrind).",
                   "Emitir e-GAR antes de cada transporte e confirmar a receção pelo destinatário (conferência mensal).",
                   "Usar apenas operadores com licença válida para os LER entregues (tbl_outros_fornecedores).",
                   "Pesar e registar mensalmente por LER; submeter o MIRR até 31 de março."],
                  [("RG-SGA-13", "tbl_residuos"), ("RG-SGA-11", "tbl_outros_fornecedores (OGR-01, OGR-06)"), ("RG-SGA-10", "tbl_execucao_rondas (RON-07, RON-08)")],
                  [("01", "2024-06-01", "Inclusão do regrind."), ("02", "2025-11-20", "Conferência mensal de e-GAR após NC-SGA-25-02.")]),
    "PR-SGA-05": ("Preparação e resposta a emergências", "01", "2025-10-05", "Em revisão",
                  "Preparar a resposta às situações de emergência com impacte ambiental identificadas na 6.1.2 e testá-la periodicamente.",
                  "Cenários EMG-01 a EMG-06: derrames, incêndio, fuga de óleo, fuga de gás fluorado, descarga anómala e perda massiva de granulado.",
                  ["ISO 14001:2026 6.1.2, 8.2", "Medidas de autoproteção (SCIE)", "IT-SGA-01, IT-SGA-02"],
                  [("Diretor Industrial", "Chefe de emergência."), ("Gestor do SGA / EHS", "Cenários, meios e simulacros ambientais."), ("Todos os trabalhadores", "Alertar e aplicar a IT do posto.")],
                  ["Identificar cenários a partir dos aspetos em condição de emergência e dos riscos (RG-SGA-03, RG-SGA-02).",
                   "Definir para cada cenário a resposta, os meios (kits, válvula de corte, bacia de retenção) e as comunicações externas.",
                   "Inspecionar os meios (rondas RON-05/06; tbl_manutencao_ambiental) e repor após uso.",
                   "Realizar pelo menos um simulacro ambiental por ano, com lições aprendidas e ações no PAM.",
                   "Após qualquer incidente real: registar (tbl_incidentes), rever o cenário e a IT."],
                  [("RG-SGA-12", "tbl_cenarios, tbl_meios, tbl_simulacros, tbl_it_passos"), ("RG-SGA-07", "tbl_incidentes")],
                  [("00", "2024-05-02", "Emissão."), ("01", "2025-10-05", "Cenário de perda massiva de granulado. Em revisão para distinguir condição anormal de emergência (ISO 14001:2026).")]),
    "PR-SGA-06": ("Planeamento de alterações (gestão de mudanças)", "00", "2026-09-24", "Em vigor",
                  "Assegurar que as alterações que afetam ou podem afetar o SGA são planeadas, avaliadas e aprovadas antes da implementação e verificadas depois, para que o SGA continue a atingir os resultados pretendidos.",
                  "Alterações internas e externas: equipamentos, processos, produtos, materiais, infraestruturas, requisitos legais, organização e o próprio SGA.",
                  ["ISO 14001:2026 6.3 (nova) e A.6.3", "NC-SGA-26-01 (origem)"],
                  [("Requerente", "Abre o pedido em RG-SGA-18 antes de comprar ou alterar."), ("Gestor do SGA / EHS", "Aplica a checklist e emite parecer."),
                   ("Diretor Industrial / Diretor Geral", "Aprova conforme o valor e o impacte."), ("Representantes dos trabalhadores", "São consultados quando aplicável.")],
                  ["Registar o pedido em tbl_alteracoes (descrição, motivo, origem interna/externa).",
                   "Responder às 10 perguntas da checklist: aspetos (normal/anormal/emergência), obrigações de conformidade, riscos e oportunidades, licenciamento e comunicação a autoridades, competências, documentos, partes interessadas, controlo operacional e emergência, fornecedores externos, recursos e prazos.",
                   "Nenhuma alteração é aprovada com respostas 'Não' sem ação definida; alterações com impacte em ruído, emissões ou efluentes exigem avaliação legal prévia.",
                   "Aprovar, implementar e verificar a eficácia após a implementação (data e resultado).",
                   "Registar a lição aprendida e atualizar os registos afetados (aspetos, legal, riscos, documentos)."],
                  [("RG-SGA-18", "tbl_alteracoes")],
                  [("00", "2026-09-24", "Emissão (transição para a ISO 14001:2026; ação corretiva da NC-SGA-26-01).")]),
    "PR-SGA-07": ("Competência, consciencialização e comunicação", "00", "2026-09-24", "Em vigor",
                  "Assegurar que quem trabalha sob o controlo da Plasticom é competente e consciente do seu papel no SGA, e que a comunicação interna e externa é planeada, rastreável e permite contribuir para a melhoria.",
                  "Trabalhadores próprios, temporários e prestadores que trabalham nas instalações; comunicação interna e externa.",
                  ["ISO 14001:2026 7.2, 7.3, 7.4"],
                  [("Responsável de Recursos Humanos", "Plano de formação e registo."), ("Chefias", "Avaliam a competência e a eficácia."), ("Gestor do SGA / EHS", "Matriz de comunicação e resposta a comunicações externas.")],
                  ["Definir, por função, a competência necessária para os aspetos significativos (matriz de competências).",
                   "Formar, registar e avaliar a eficácia; acolhimento ambiental para novos trabalhadores e prestadores.",
                   "Consciencializar para a política, os aspetos significativos, as consequências do desvio e o contributo de cada um (Kaizen).",
                   "Planear a comunicação (o quê, a quem, quando, como, porquê) e registar cada comunicação externa recebida ou enviada, com prazo de resposta.",
                   "Responder a reclamações externas em 5 dias úteis e ligá-las a incidentes e NC."],
                  [("RG-SGA-08", "tbl_competencias, tbl_formacoes, tbl_registo_formacao, tbl_raci"), ("RG-SGA-09", "tbl_comunicacao, tbl_comunicacoes_externas")],
                  [("00", "2026-09-24", "Emissão.")]),
    "PR-SGA-08": ("Controlo da informação documentada", "00", "2026-09-24", "Em vigor",
                  "Criar, aprovar, disponibilizar, proteger e reter a informação documentada do SGA, distinguindo a que deve estar disponível (antes 'manter') da que deve estar disponível como evidência (antes 'reter').",
                  "Documentos (política, manual, procedimentos, IT) e registos do SGA, internos e de origem externa.",
                  ["ISO 14001:2026 7.5"],
                  [("Gestor do SGA / EHS", "Lista mestra, codificação e arquivo."), ("Aprovadores", "Revisão e aprovação antes da emissão."), ("Utilizadores", "Usar apenas a versão em vigor.")],
                  ["Codificar: POL (política), MAN (manual), PR (procedimento), IT (instrução), RG (registo).",
                   "Rever e aprovar antes da emissão; registar versão, data, aprovador e alterações no histórico.",
                   "Disponibilizar a versão em vigor nos pontos de uso; retirar e marcar os obsoletos.",
                   "Reter os registos durante 5 anos após substituição (ou o prazo legal, se maior), com cópia de segurança.",
                   "Os registos Excel são tabelas de dados com dicionário de dados; as colunas calculadas não são editadas manualmente."],
                  [("RG-SGA-09", "tbl_lista_mestra, tbl_verif_documental"), ("RG-SGA-00", "Índice e modelo de dados")],
                  [("00", "2026-09-24", "Emissão.")]),
    "PR-SGA-09": ("Controlo operacional e processos externos", "00", "2026-09-24", "Em vigor",
                  "Planear e controlar os processos associados aos aspetos significativos e às obrigações de conformidade, incluindo os processos, produtos e serviços providos externamente e a perspetiva de ciclo de vida.",
                  "Produção (injeção, sopro, serigrafia, hot foil), utilidades, armazém, resíduos, conceção de embalagens e fornecedores externos.",
                  ["ISO 14001:2026 8.1", "PR-SGA-04, IT-SER-03"],
                  [("Diretor Industrial", "Aprova os critérios operacionais."), ("Chefias e operadores", "Aplicam os controlos e as rondas."), ("Responsável de Compras", "Critérios ambientais e controlo de fornecedores.")],
                  ["Definir critérios operacionais para cada aspeto significativo (IT, pontos de controlo das rondas, manutenção ambiental).",
                   "Executar rondas semanais/mensais e registar desvios; desvios repetidos abrem NC.",
                   "Manter os equipamentos com relevância ambiental (F-gas, torre, compressores, exaustão, meios de emergência).",
                   "Para cada processo, produto ou serviço externo, definir o tipo (controlo ou influência) e a extensão do controlo e verificar com a frequência definida.",
                   "Considerar o ciclo de vida: requisitos ambientais na conceção (reciclabilidade, PPWR), nas compras e na informação a clientes sobre uso e fim de vida."],
                  [("RG-SGA-10", "tbl_pontos, tbl_execucao_rondas, tbl_manutencao_ambiental"), ("RG-SGA-11", "tbl_fornecedores, tbl_outros_fornecedores, tbl_avaliacao_fornecedor")],
                  [("00", "2026-09-24", "Emissão.")]),
    "PR-SGA-10": ("Monitorização, medição, análise, avaliação e calibração", "00", "2026-09-24", "Em vigor",
                  "Monitorizar e medir o desempenho ambiental, avaliar a eficácia do SGA e assegurar equipamentos de medição calibrados ou verificados.",
                  "Consumos (energia, água, materiais), resíduos, emissões, efluentes, ruído, Legionella, KPI e objetivos.",
                  ["ISO 14001:2026 9.1.1", "ISO 14031"],
                  [("Gestor do SGA / EHS", "Plano de monitorização, análise mensal e relatório de desempenho."), ("Gerente de Manutenção", "Contadores, calibração e ensaios da torre e do efluente.")],
                  ["Definir no plano o quê, como, quando, quem, método, critério e equipamento para cada parâmetro.",
                   "Recolher mensalmente os dados das faturas e contadores; ensaios com laboratório acreditado nas frequências legais.",
                   "Calibrar ou verificar os equipamentos de medição e registar o estado.",
                   "Analisar tendências e desvios (ex.: análise de desvio de +15%) e avaliar a eficácia do SGA, não só os números.",
                   "Comunicar os resultados à revisão pela gestão e às partes interessadas quando aplicável."],
                  [("RG-SGA-13", "tbl_plano_monitorizacao, tbl_equipamentos, tbl_dados_ambientais, tbl_meses, tbl_analises"), ("RG-SGA-05", "tbl_kpi, tbl_acomp_objetivos")],
                  [("00", "2026-09-24", "Emissão.")]),
    "PR-SGA-11": ("Auditoria interna e revisão pela gestão", "00", "2026-09-24", "Em vigor",
                  "Verificar, com auditorias planeadas, se o SGA cumpre os requisitos e está eficazmente implementado, e rever o SGA na gestão de topo.",
                  "Todos os processos e cláusulas do SGA num ciclo de 3 anos; revisão pela gestão anual.",
                  ["ISO 14001:2026 9.2, 9.3", "ISO 19011"],
                  [("Gestor do SGA / EHS", "Programa de auditorias e preparação da revisão."), ("Auditores internos", "Independentes da área auditada."), ("Diretor Geral", "Conduz a revisão e decide.")],
                  ["Estabelecer o programa considerando a importância ambiental, as alterações e os resultados anteriores.",
                   "Definir para cada auditoria o objetivo, os critérios e o âmbito (novo na 9.2.2).",
                   "Registar constatações com evidência; NC abrem RNC e ação corretiva.",
                   "Preparar a revisão pela gestão com as entradas 9.3.2 a) a g) e registar as saídas 9.3.3 (decisões, recursos, alterações, oportunidades).",
                   "Acompanhar as decisões até à conclusão."],
                  [("RG-SGA-14", "tbl_programa_auditorias, tbl_constatacoes"), ("RG-SGA-15", "tbl_agenda, tbl_decisoes, tbl_conclusoes")],
                  [("00", "2026-09-24", "Emissão.")]),
    "PR-SGA-12": ("Incidentes, não conformidades, ação corretiva e melhoria contínua", "00", "2026-09-24", "Em vigor",
                  "Reagir a incidentes e não conformidades, eliminar as causas, verificar a eficácia e melhorar continuamente o SGA e o desempenho ambiental.",
                  "Incidentes e quase-incidentes ambientais, NC de auditoria, de rondas, legais e de reclamações; ideias de melhoria.",
                  ["ISO 14001:2026 10.1, 10.2", "Análise de incidentes (5 Porquês, Ishikawa, 5W2H)"],
                  [("Quem deteta", "Regista o incidente ou a NC no próprio dia."), ("Gestor do SGA / EHS", "Classifica, coordena a análise de causas e verifica a eficácia."), ("Responsáveis das ações", "Executam no prazo.")],
                  ["Registar todos os incidentes e quase-incidentes (tbl_incidentes); os que exigem ação abrem NC.",
                   "Corrigir (C1) e mitigar as consequências; comunicar a autoridades quando obrigatório.",
                   "Analisar a causa-raiz (5 Porquês / 6M) e definir a ação corretiva (C2) no PAM, com critério de eficácia.",
                   "Verificar a eficácia na data prevista; se não eficaz, reabrir a análise.",
                   "Recolher ideias de melhoria (Kaizen) e priorizá-las com os dados do SGA."],
                  [("RG-SGA-07", "tbl_incidentes, tbl_nc, tbl_5porques"), ("RG-SGA-06", "tbl_pam"), ("RG-SGA-16", "tbl_kaizen")],
                  [("00", "2026-09-24", "Emissão (10.3 integrada em 10.1 e 10.2 na ISO 14001:2026).")]),
    "PR-SGA-13": ("Inventário de gases com efeito de estufa e indicadores ESG ambientais", "00", "2026-09-24", "Em vigor",
                  "Quantificar anualmente as emissões de GEE (âmbitos 1, 2 e 3) e os indicadores ambientais ESG com um método reprodutível, rastreável e comparável entre anos, para metas, clientes (CDP, EcoVadis) e relato voluntário (VSME).",
                  "Unidade 1 da Plasticom (controlo operacional); âmbito 3 com as categorias relevantes (1, 3, 4, 5, 6, 7, 9, 12). Ano de reporte: setembro a agosto; ano-base 2025/26.",
                  ["GHG Protocol Corporate Standard e Scope 2 Guidance", "ISO 14064-1:2018", "EFRAG VSME (módulo básico B3 a B7)", "ESRS E1 a E5; GRI 301–308; SASB RT-CP"],
                  [("Gestor do SGA / EHS", "Responsável pelo inventário, fatores e relatório."), ("Gerente de Manutenção", "Dados de energia, gasóleo e gases fluorados."),
                   ("Responsável de Compras", "Quantidades compradas e PCF de fornecedores."), ("Diretor Financeiro", "Faturação e custos (intensidades)."), ("Diretor Geral", "Aprova o inventário e as metas.")],
                  ["Registar mensalmente os dados de atividade no inventário (tbl_inventario_gee): faturas, cartões de frota, recargas F-gas, compras de materiais, resíduos por destino e pressupostos de deslocações e transporte.",
                   "Usar os fatores de emissão da tbl_fatores_emissao com fonte, ano e qualidade; atualizar anualmente (APA/ERSE, AIB, DEFRA, eco-perfis) e registar a alteração.",
                   "Reportar o âmbito 2 pelos dois métodos (location-based e market-based); as metas usam o market-based; nunca somar os dois.",
                   "Classificar a qualidade de cada dado (medido, calculado, estimado) e substituir progressivamente estimativas do âmbito 3 por dados primários (PCF de fornecedores).",
                   "Recalcular o ano-base se houver alteração estrutural, de método ou erro com efeito ≥ 5% no total.",
                   "Calcular os indicadores ESG (tbl_indicadores_esg) e a pegada por produto (tbl_pegada_produto); rever a matriz de requisitos ESG (tbl_matriz_esg).",
                   "Submeter o inventário à revisão pela gestão e, antes de publicar, a verificação limitada por terceira parte (ISO 14064-3)."],
                  [("RG-SGA-19", "tbl_fatores_emissao, tbl_inventario_gee, Calculadora_GEE, tbl_metas_clima, tbl_pegada_produto, tbl_indicadores_esg, tbl_matriz_esg"),
                   ("RG-SGA-13", "tbl_dados_ambientais, tbl_meses, tbl_residuos"), ("RG-SGA-10", "tbl_manutencao_ambiental (F-gas)")],
                  [("00", "2026-09-24", "Emissão com o ano-base 2025/26.")]),
    "PR-SGA-14": ("Alegações ambientais e declarações de produto", "00", "2026-09-24", "Em vigor",
                  "Assegurar que qualquer alegação ambiental da Plasticom (reciclável, conteúdo reciclado, pegada de carbono, 'sustentável') é específica, verdadeira, comprovada e aprovada antes de ser comunicada.",
                  "Fichas técnicas, site, catálogos, propostas comerciais, respostas a clientes e rotulagem de embalagens.",
                  ["Diretiva (UE) 2024/825 (capacitar os consumidores para a transição ecológica)", "Reg. (UE) 2025/40 (PPWR)", "ISO 14021 (autodeclarações)", "ISO 14067 (pegada de produto)"],
                  [("Responsável de R&D", "Prepara a evidência técnica."), ("Gestor do SGA / EHS", "Verifica a comprovação."), ("Diretor Geral", "Aprova as alegações."), ("Área comercial", "Só usa alegações aprovadas.")],
                  ["Proibir alegações genéricas ('amigo do ambiente', 'verde', 'sustentável') sem desempenho reconhecido que as sustente.",
                   "Conteúdo reciclado: só com certificado de terceira parte por lote (RecyClass, EuCertPlast, ISCC PLUS) e cálculo de balanço de massa.",
                   "Reciclabilidade: só após avaliação por família (classes PPWR) e indicando as condições (ex.: 'reciclável onde existam sistemas de recolha').",
                   "Pegada de carbono: indicar o âmbito (berço-portão), a norma e a data; não usar compensações para alegar neutralidade carbónica.",
                   "Registar cada alegação aprovada com evidência e data de revisão; retirar as que perderem a evidência."],
                  [("RG-SGA-19", "tbl_pegada_produto"), ("RG-SGA-21", "tbl_quimicos, tbl_declaracoes (substâncias)"), ("RG-SGA-11", "certificados de PCR por lote"), ("RG-SGA-05", "KPI-12 (conformidade PPWR)")],
                  [("00", "2026-09-24", "Emissão (Diretiva 2024/825 aplicável a partir de 27/09/2026).")]),
    "PR-SGA-15": ("Conceção para reciclagem e conformidade de embalagens (PPWR, RecyClass)", "00", "2026-09-24", "Em vigor",
                  "Garantir que cada embalagem da Plasticom é concebida para a reciclagem, cumpre os requisitos do Reg. (UE) 2025/40 (PPWR) e da legislação de segurança dos materiais, e que a reciclabilidade e o conteúdo reciclado são avaliados, documentados e comunicados com evidência.",
                  "Todos os SKUs de frascos, potes e tampas (cosmética, alimentar, farmacêutico), novos projetos e alterações de material, cor, decoração ou componente; embalagens de expedição.",
                  ["Reg. (UE) 2025/40 (PPWR), arts. 5.º a 7.º, 10.º, 12.º e anexos II e VII", "Regs. (CE) 1935/2004, 2023/2006 e (UE) 10/2011, 2022/1616", "DL 152-D/2017 (UNILEX)",
                   "Diretiva (UE) 2024/825", "Diretrizes de design para reciclagem RecyClass; EN 15343; ISO 14021; ISO 11469; ISO 18601–18606 / EN 13427–13432"],
                  [("Responsável de R&D", "Avaliação RecyClass por SKU, documentação técnica, redesign."), ("Gerente da Qualidade", "Metais pesados, PFAS, FCM, declarações UE."),
                   ("Responsável de Compras", "Certificados EN 15343 do reciclado e declarações de fornecedores."), ("Gestor do SGA / EHS", "Matriz legal, KPI e revisão anual."),
                   ("Diretor Financeiro", "RAP das embalagens de expedição e informação por país."), ("Diretor Geral", "Aprova declarações UE e alegações.")],
                  ["Em cada novo SKU ou alteração, preencher a linha em tbl_recyclass (RG-SGA-20) com os campos da ferramenta RecyClass: corpo, cor, densidade, barreira, tampa, vedante, rótulo, adesivo, cobertura e decoração.",
                   "Calcular a classe RecyClass, a taxa de reciclabilidade e o grau PPWR indicativo; só aprovar o design com grau A–C (A–B para projetos com vida para além de 2037), salvo isenção documentada (embalagem imediata de medicamento).",
                   "Confirmar o resultado na ferramenta online RecyClass para as famílias principais e pedir certificação quando o cliente o exigir ou antes de usar o logótipo.",
                   "Evitar por design: PVC, PETG, preto de negro de carbono, decoração direta em PET, tampas de PETG em PET, rótulos de papel ou adesivos não laváveis em PET.",
                   "Calcular o conteúdo reciclado por SKU e por instalação/ano face às metas do art. 7.º; aceitar reciclado só com certificado EN 15343 válido (tbl_certificados_pcr); em contacto alimentar só reciclado de processo autorizado (Reg. 2022/1616).",
                   "Manter por família a documentação técnica e a declaração UE de conformidade (metais pesados ≤ 100 mg/kg; PFAS em contacto alimentar) — tbl_familias_ppwr.",
                   "Enviar ao cliente a ficha do SKU (Formulario_RecyClass) e a informação por país (tbl_requisitos_pais); declarar as embalagens de expedição (tbl_emb_expedicao).",
                   "Rever anualmente a matriz de requisitos (tbl_requisitos_emb) e acompanhar os atos delegados do PPWR; tratar lacunas no PAM."],
                  [("RG-SGA-20", "tbl_recyclass, tbl_regras_dfr, tbl_familias_ppwr, tbl_requisitos_emb, tbl_aplicabilidade, tbl_certificados_pcr, tbl_alegacoes, tbl_requisitos_pais, tbl_emb_expedicao"),
                   ("RG-SGA-04", "LEG-09, LEG-16 a LEG-21"), ("RG-SGA-05", "KPI-12, KPI-17 a KPI-21, OBJ-07"), ("RG-SGA-06", "PAM-26-22 a PAM-26-27")],
                  [("00", "2026-09-24", "Emissão com a primeira autoavaliação RecyClass de 113 SKUs.")]),
    "PL-SGA-01": ("Plano de transição climática 2026–2030", "00", "2026-10-15", "Em vigor",
                  "Definir como a Plasticom reduz as suas emissões de GEE em linha com a trajetória de 1,5 °C e aumenta a resiliência às alterações climáticas, com metas, alavancas, investimentos e responsáveis.",
                  "Âmbitos 1, 2 e 3 do inventário (RG-SGA-19); riscos físicos de calor, seca e incêndio.",
                  ["ESRS E1-1 (plano de transição)", "SBTi para PME", "ISO 14001:2026 4.1 (alterações climáticas)"],
                  [("Diretor Geral", "Aprova o plano e o orçamento."), ("Diretor Industrial", "Alavancas de energia e processo."), ("Responsável de Compras", "PCR e fornecedores."),
                   ("Responsável de R&D", "Lightweighting e ecodesign."), ("Gestor do SGA / EHS", "Acompanhamento anual no simulador e no inventário.")],
                  ["Metas (tbl_metas_clima): âmbitos 1+2 market-based −50% até 2030; âmbito 3 −25%; eletricidade 100% renovável até 2028; 30% de conteúdo reciclado até 2030; intensidade −35%.",
                   "Alavanca 1 — Eficiência energética: submedição (PAM-26-02), compressores VSD, fugas de ar, moldes e aquecimento (−15% de consumo específico).",
                   "Alavanca 2 — Eletricidade renovável: UPAC ≈ 1 MWp (ALT-2026-07) e garantias de origem para o restante.",
                   "Alavanca 3 — Materiais: 30% de PCR certificado, lightweighting de 5% e redução do scrap (OBJ-02).",
                   "Alavanca 4 — Gases fluorados e frota: fluido de baixo GWP no chiller e 50% de viaturas elétricas.",
                   "Alavanca 5 — Logística: consolidação de cargas e transporte a jusante com −10% de t.km.",
                   "Adaptação: circuito fechado de arrefecimento (OBJ-05), gestão de combustível na envolvente e plano de seca.",
                   "Acompanhamento anual: inventário, simulador (Calculadora_GEE) e revisão pela gestão; com as alavancas atuais o âmbito 3 fica em −5% — exige ações adicionais (PCF de fornecedores, mais PCR, design para reciclagem)."],
                  [("RG-SGA-19", "Calculadora_GEE, tbl_metas_clima, tbl_inventario_gee"), ("RG-SGA-06", "tbl_pam"), ("RG-SGA-18", "ALT-2026-07 (UPAC)")],
                  [("00", "2026-10-15", "Aprovado pelo Diretor Geral após a revisão pela gestão de 2026 (proposta de 24/09/2026).")]),
}

IT = {
    "IT-SGA-02": ("Resposta a incêndio com retenção das águas de combate", "00", "2026-02-10", "Em vigor", "Diretor Industrial",
                  ["Dar o alarme (botoneira mais próxima) e avisar a portaria (ext. 100).",
                   "Portaria: ligar 112 e acionar a equipa de primeira intervenção.",
                   "Fechar a válvula de corte da rede pluvial VC-01 (chave na caixa vermelha junto à portaria) — meta ≤ 5 min.",
                   "Confirmar que a bacia de retenção BR-01 (300 m³) está livre para receber as águas de combate.",
                   "Evacuar para o ponto de encontro; não reabrir a VC-01 sem autorização do Gestor do SGA.",
                   "Após o incidente: amostrar a água retida, encaminhar como resíduo se contaminada e registar em tbl_incidentes."],
                  "RG-SGA-12 (EMG-02, VC-01, BR-01); tbl_incidentes"),
    "IT-SER-03": ("Limpeza de ecrãs e rodos na serigrafia", "02", "2026-11-10", "Em vigor", "Gerente de Produção",
                  ["Usar luvas nitrílicas e óculos; ventilação localizada ligada (na SS-001, mesa aspirante desde 17/12/2026).",
                   "Retirar o excesso de tinta com espátula para o recipiente de tinta recuperável.",
                   "Aplicar solvente só com o dispensador de segurança com tampa do posto (máx. 50 mL por ecrã) — nunca verter do bidão (PAM-26-08).",
                   "Panos sujos no contentor metálico com tampa (15 02 02*); fechar sempre o recipiente de solvente.",
                   "Registar o solvente usado na pesagem diária (tbl_pesagem_solvente).",
                   "Em derrame: aplicar IT-SGA-01 e o kit mais próximo."],
                  "RG-SGA-13 (tbl_pesagem_solvente); RG-SGA-03 (AA-014)"),
}


FORCE = False


def _save(doc, path):
    if os.path.exists(path) and not FORCE:
        return  # documento já existe: pode ter sido editado à mão
    try:
        doc.save(path)
    except PermissionError:
        print("aviso: documento aberto no Word, não atualizado:", os.path.basename(path))


def build_proc(code, spec):
    (title, ver, date, state, obj, amb, refs, resp, steps, regs, hist) = spec
    doc = new_doc(code, title, ver, date, state)
    h(doc, "1. Objetivo"); para(doc, obj)
    h(doc, "2. Âmbito"); para(doc, amb)
    h(doc, "3. Referências"); bullets(doc, refs)
    h(doc, "4. Responsabilidades"); table(doc, ["Função", "Responsabilidade"], resp, [5, 12])
    h(doc, "5. Descrição do processo")
    for i, s in enumerate(steps, start=1):
        doc.add_paragraph(f"{i}. {s}").paragraph_format.left_indent = Cm(0.4)
    h(doc, "6. Informação documentada (evidência)")
    table(doc, ["Registo", "Tabelas (Registos_SGA_Plasticom)"], regs, [4, 13])
    history(doc, hist)
    _save(doc, os.path.join(OUT, f"{code}_{slug(title.split(' (')[0])}.docx"))


def build_it(code, spec):
    title, ver, date, state, appr, steps, regs = spec
    doc = new_doc(code, title, ver, date, state, appr)
    h(doc, "Passos")
    for i, s in enumerate(steps, start=1):
        p = doc.add_paragraph(f"{i}. {s}")
        p.runs[0].font.size = Pt(11)
    h(doc, "Registos"); para(doc, regs)
    _save(doc, os.path.join(OUT, f"{code}_{slug(title)}.docx"))


def build_manual():
    doc = new_doc("MAN-SGA-01", "Manual do Sistema de Gestão Ambiental — Âmbito e Estrutura", "00", "2026-09-24", "Em vigor")
    h(doc, "1. A organização")
    para(doc, f"{EMPRESA}: fabrico de embalagens plásticas (frascos por injeção-sopro ISBM, tampas e potes por injeção) decoradas por serigrafia e hot foil, "
              "para clientes de cosmética, alimentar e farmacêutica na UE. ≈ 150 trabalhadores em 3 turnos; processo 100% elétrico (≈ 7,8 GWh em 2026); "
              "≈ 800 t/ano de produto. Estabelecimento industrial tipo 2 (SIR), em zona industrial a ≈ 250 m de habitações e próximo do Pinhal de Leiria.")
    h(doc, "2. Âmbito do SGA (4.3)")
    para(doc, "“Conceção, produção e decoração de embalagens plásticas (frascos, tampas e potes) por injeção, injeção-sopro, serigrafia e hot foil, "
              "incluindo armazenagem, expedição e os serviços de apoio da Unidade 1 da Plasticom, Marinha Grande.”")
    table(doc, ["Elemento", "Determinação"], [
        ("Limites físicos", "Terreno de 45.000 m² da Unidade 1 (edifícios, logradouro, parque de resíduos, silos, torre de arrefecimento)."),
        ("Limites organizacionais", "Todas as funções da Unidade 1; não inclui a sede comercial nem armazéns de clientes."),
        ("Atividades, produtos e serviços", "Todos os processos da Dim_Processo (RG-SGA-00); sem exclusões."),
        ("Questões externas e internas (4.1)", "RG-SGA-01 (PESTEL com as 5 condições ambientais: poluição, recursos, clima, biodiversidade, ecossistemas; SWOT; TOWS)."),
        ("Obrigações de conformidade (4.2, 6.1.3)", "RG-SGA-01 tbl_partes_interessadas e RG-SGA-04 tbl_legal."),
        ("Controlo e influência sobre o ciclo de vida (4.3 e)", "Controlo: produção, utilidades, resíduos, conceção. Influência: fornecedores de polímero e PCR, transporte, uso pelo cliente e fim de vida (tbl_outros_fornecedores, tbl_fornecedores)."),
    ], [5, 12])
    para(doc, "O âmbito está disponível às partes interessadas (site institucional e a pedido) como informação documentada.")
    h(doc, "3. Política ambiental (5.2)")
    para(doc, "POL-SGA rev. 02 (19/06/2026), com 7 compromissos (RG-SGA-05 tbl_politica): proteger o ambiente e prevenir a poluição; cumprir as obrigações de "
              "conformidade; usar eficientemente energia, água e materiais e reduzir GEE; ciclo de vida; melhoria contínua com dados; biodiversidade e "
              "ecossistemas; envolvimento de trabalhadores, fornecedores e clientes.")
    h(doc, "4. Liderança, funções e responsabilidades (5.1, 5.3)")
    para(doc, "O Diretor Geral assume a responsabilização pela eficácia do SGA, assegura recursos e conduz a revisão pela gestão. O Gestor do SGA / EHS "
              "tem a autoridade para assegurar a conformidade do SGA com a ISO 14001:2026 e reportar o desempenho à gestão de topo. As responsabilidades "
              "por processo estão na matriz RACI (RG-SGA-08 tbl_raci), com um único aprovador por processo.")
    h(doc, "5. Mapa de processos e interação")
    para(doc, "Planear: contexto → partes interessadas → aspetos, obrigações, riscos e oportunidades → objetivos e alterações. "
              "Executar: competência, comunicação, documentação, controlo operacional, fornecedores externos, emergência. "
              "Verificar: monitorização, avaliação da conformidade, auditoria interna, revisão pela gestão. "
              "Agir: incidentes, NC e ação corretiva, melhoria contínua (Kaizen), dupla materialidade para priorizar.")
    h(doc, "6. Correspondência cláusula → documento → registo")
    table(doc, ["Cláusula", "Documento", "Registo / tabelas"], [
        ("4.1 / 4.2", "MAN-SGA-01; PR-SGA-02; PR-SGA-03", "RG-SGA-01 (tbl_pestel, tbl_swot, tbl_partes_interessadas); RG-SGA-17"),
        ("4.3 / 4.4", "MAN-SGA-01", "RG-SGA-00 (índice e modelo de dados)"),
        ("5.1 / 5.2 / 5.3", "POL-SGA; MAN-SGA-01", "RG-SGA-05 (tbl_politica); RG-SGA-08 (tbl_raci)"),
        ("6.1.2", "PR-SGA-01", "RG-SGA-03"),
        ("6.1.3 / 9.1.2", "PR-SGA-03", "RG-SGA-04; RG-SGA-13 (tbl_analises)"),
        ("6.1.4 / 6.1.5", "PR-SGA-02", "RG-SGA-02; RG-SGA-06; RG-SGA-17"),
        ("6.2", "PR-SGA-02", "RG-SGA-05"),
        ("6.3", "PR-SGA-06", "RG-SGA-18"),
        ("7.1", "PR-SGA-09", "RG-SGA-10 (tbl_manutencao_ambiental); RG-SGA-15 (recursos)"),
        ("7.2 / 7.3 / 7.4", "PR-SGA-07", "RG-SGA-08; RG-SGA-09 (tbl_comunicacao, tbl_comunicacoes_externas)"),
        ("7.5", "PR-SGA-08", "RG-SGA-09 (tbl_lista_mestra)"),
        ("8.1", "PR-SGA-04; PR-SGA-09; IT-SER-03", "RG-SGA-10; RG-SGA-11"),
        ("8.2", "PR-SGA-05; IT-SGA-01; IT-SGA-02", "RG-SGA-12; RG-SGA-07 (tbl_incidentes)"),
        ("9.1.1", "PR-SGA-10", "RG-SGA-13; RG-SGA-05; RG-SGA-16"),
        ("9.2 / 9.3", "PR-SGA-11", "RG-SGA-14; RG-SGA-15"),
        ("10.1 / 10.2", "PR-SGA-12", "RG-SGA-07; RG-SGA-06; RG-SGA-16"),
        ("ESG — pilar E", "PR-SGA-13; PR-SGA-14; PL-SGA-01", "RG-SGA-19 (GEE, metas, pegada, substâncias, indicadores); RG-SGA-17"),
        ("Embalagens — reciclabilidade e PPWR", "PR-SGA-15; PR-SGA-14", "RG-SGA-20 (RecyClass, graus PPWR, reciclado, matriz legal de produto)"),
        ("Produtos químicos — REACH, CLP, SVHC, risco químico", "PR-SGA-16", "RG-SGA-21 (inventário, FDS, cenários de exposição, registo/importação, SVHC, avaliação de risco, Seveso, matriz legal)"),
    ], [2.5, 5, 9.5])
    h(doc, "7. Transição para a ISO 14001:2026")
    bullets(doc, ["4.1: condições ambientais explícitas no PESTEL (Condicao_Ambiental_ISO2026).",
                  "4.2 c): decisão sobre que necessidades se tornam obrigações de conformidade (tbl_partes_interessadas).",
                  "4.3 e): controlo e influência sobre o ciclo de vida definidos neste manual.",
                  "6.1.2: condição de emergência separada da anormal (tbl_aspetos, tbl_incidentes).",
                  "6.1.4 / 6.1.5: determinar riscos e planear ações em passos separados (PR-SGA-02).",
                  "6.3: novo PR-SGA-06 e RG-SGA-18.",
                  "8.1: tipo e extensão do controlo de processos, produtos e serviços externos (RG-SGA-11).",
                  "9.2.2: objetivos definidos para cada auditoria (tbl_programa_auditorias).",
                  "9.3: entradas 9.3.2 e resultados 9.3.3 separados (RG-SGA-15).",
                  "7.5: 'manter' → disponível; 'reter' → disponível como evidência (PR-SGA-08)."])
    history(doc, [("00", "2026-09-24", "Emissão do manual (âmbito, estrutura e correspondência com a ISO 14001:2026).")])
    _save(doc, os.path.join(OUT, "MAN-SGA-01_Manual_do_SGA.docx"))


def build(out_dir=OUT, force=False):
    global FORCE
    FORCE = force
    os.makedirs(out_dir, exist_ok=True)
    if force:
        for f in os.listdir(out_dir):  # regenera tudo (documentos gerados por este script)
            if f.endswith(".docx") and f[:3] in ("MAN", "PR-", "IT-", "PL-"):
                try:
                    os.remove(os.path.join(out_dir, f))
                except PermissionError:
                    print("aviso: documento aberto, não atualizado:", f)
    build_manual()
    for code, spec in PROC.items():
        build_proc(code, spec)
    for code, spec in IT.items():
        build_it(code, spec)
    import build_pr16_quimicos
    build_pr16_quimicos.build()
    return sorted(os.listdir(out_dir))


if __name__ == "__main__":
    import sys
    for f in build(force="--force" in sys.argv):
        print(f)
