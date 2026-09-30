"""Matriz de requisitos ISO 14001:2026 → documento → registo/tabela → estado (verificação de 24/09/2026, atualizada a 31/12/2026).

Usada pelo build_00_indice para a folha Matriz_ISO14001_2026 (tbl_matriz_iso) e o resumo por cláusula.
Estado: Conforme (evidência completa) · Parcial (processo existe, com lacuna de evidência ou de eficácia) · Lacuna (sem evidência).
Fontes da verificação: Change Summary ISO 14001:2026, "O que mudou na ISO 14001:2026", lista mestra de documentos 2026, checklists de auditoria
(pasta ISO_14001_2026-Sistema-de-Gestão-Ambiental-Interpretação).
"""
from sgalib import *

# (ID, cláusula, requisito, novo/alterado 2026, informação documentada, documento, registo e tabelas, estado, observação/lacuna, ação)
REQ = [
    ("REQ-01", "4.1", "Determinar questões externas e internas relevantes", "Não", "—", "MAN-SGA-01", "RG-SGA-01 tbl_pestel, tbl_swot, tbl_tows", "Conforme", "15 fatores PESTEL e 14 SWOT com prioridade e revisão.", ""),
    ("REQ-02", "4.1", "Incluir condições ambientais (poluição, recursos, clima, biodiversidade, ecossistemas) afetadas pela organização ou que a afetam", "Sim", "—", "MAN-SGA-01", "RG-SGA-01 tbl_pestel (Condicao_Ambiental_ISO2026, Direcao_Efeito)", "Conforme", "As 5 condições estão representadas nos dois sentidos.", ""),
    ("REQ-03", "4.1", "Determinar se as alterações climáticas são uma questão relevante", "Sim", "—", "MAN-SGA-01", "RG-SGA-01 PES-01/08/09; RG-SGA-02 RO-04; RG-SGA-17 DM-01 a DM-03", "Conforme", "Mitigação (GEE) e adaptação (calor, seca, incêndio) avaliadas.", ""),
    ("REQ-04", "4.2", "Partes interessadas relevantes e as suas necessidades e expectativas", "Sim", "—", "PR-SGA-03", "RG-SGA-01 tbl_partes_interessadas; RG-SGA-17 tbl_dma_consultas", "Conforme", "15 partes; condição ambiental associada a cada expectativa.", ""),
    ("REQ-05", "4.2 c)", "Decidir quais necessidades e expectativas se tornam obrigações de conformidade", "Sim", "—", "PR-SGA-03", "RG-SGA-01 tbl_partes_interessadas (Torna_se_Obrigacao, Tipo_Obrigacao)", "Conforme", "Legais e voluntárias distinguidas.", ""),
    ("REQ-06", "4.3", "Âmbito com limites, aplicabilidade e controlo/influência sobre o ciclo de vida, disponível como informação documentada", "Sim", "Disponível", "MAN-SGA-01 §2", "RG-SGA-00", "Conforme", "Âmbito e alínea e) definidos no manual.", ""),
    ("REQ-07", "4.4", "Estabelecer o SGA e os processos necessários e as suas interações", "Não", "—", "MAN-SGA-01 §5–6", "RG-SGA-00 (índice e modelo de dados)", "Conforme", "", ""),
    ("REQ-08", "5.1", "Liderança e compromisso da gestão de topo (responsabilização, recursos, apoio a todas as funções relevantes)", "Sim", "—", "MAN-SGA-01 §4", "RG-SGA-15 tbl_decisoes; RG-SGA-08 tbl_raci", "Conforme", "Decisões com recursos na revisão pela gestão.", ""),
    ("REQ-09", "5.2", "Política ambiental adequada, com compromissos, disponível e comunicada", "Sim", "Disponível", "POL-SGA rev. 02", "RG-SGA-05 tbl_politica; RG-SGA-09 tbl_lista_mestra", "Conforme", "7 compromissos incluindo biodiversidade e ciclo de vida.", ""),
    ("REQ-10", "5.3", "Funções, responsabilidades e autoridades atribuídas e comunicadas", "Não", "—", "MAN-SGA-01 §4", "RG-SGA-08 tbl_raci", "Conforme", "22 processos com um único aprovador (A).", ""),
    ("REQ-11", "6.1.1", "Processos para 6.1.2 a 6.1.5 disponíveis como informação documentada", "Sim", "Disponível", "PR-SGA-01; PR-SGA-02; PR-SGA-03", "—", "Conforme", "", ""),
    ("REQ-12", "6.1.2", "Aspetos ambientais e impactes com perspetiva de ciclo de vida (controlados e influenciados)", "Sim", "Disponível", "PR-SGA-01", "RG-SGA-03 tbl_aspetos (Fase_Ciclo_Vida)", "Conforme", "43 aspetos nas 6 fases do ciclo de vida.", ""),
    ("REQ-13", "6.1.2", "Situações de emergência potenciais determinadas, separadas das condições anormais", "Sim", "Disponível", "PR-SGA-01; PR-SGA-05", "RG-SGA-03 tbl_aspetos (Condicao_Operacao); RG-SGA-12 tbl_cenarios; RG-SGA-07 tbl_incidentes (Condicao)", "Conforme", "33 normais, 6 anormais, 4 de emergência.", ""),
    ("REQ-14", "6.1.2", "Critérios de significância e aspetos significativos documentados", "Não", "Disponível", "PR-SGA-01", "RG-SGA-03 (IRA, Classificacao)", "Conforme", "", ""),
    ("REQ-15", "6.1.3", "Obrigações de conformidade determinadas e acessíveis", "Não", "Disponível", "PR-SGA-03", "RG-SGA-04 tbl_legal", "Conforme", "15 diplomas; LEG-15 (Legionella) acrescentado nesta revisão.", ""),
    ("REQ-16", "6.1.4", "Determinar riscos e oportunidades (aspetos, obrigações, contexto)", "Sim", "Disponível", "PR-SGA-02", "RG-SGA-02 tbRiscos, tbOportunidades; RG-SGA-17 tbl_dma_iro", "Conforme", "", ""),
    ("REQ-17", "6.1.5", "Planear ações e integrá-las nos processos; avaliar a eficácia", "Sim", "—", "PR-SGA-02", "RG-SGA-06 tbl_pam; RG-SGA-02 tbPlanos", "Conforme", "", ""),
    ("REQ-18", "6.2", "Objetivos ambientais mensuráveis e planeamento para os atingir", "Não", "Disponível", "PR-SGA-02", "RG-SGA-05 tbl_objetivos, tbl_kpi, tbl_acomp_objetivos", "Conforme", "6 objetivos SMART com KPI e ações.", ""),
    ("REQ-19", "6.3", "Planeamento de alterações que afetam o SGA", "Sim", "—", "PR-SGA-06", "RG-SGA-18 tbl_alteracoes", "Conforme", "PR-SGA-06 e formulário com checklist ambiental em uso desde 25/11/2026; ALT-2026-01 verificada (05/11/2026); ALT-2026-09/10 já passaram pela checklist.", "PAM-26-17"),
    ("REQ-20", "7.1", "Recursos, incluindo infraestrutura e manutenção com relevância ambiental", "Não", "—", "PR-SGA-09", "RG-SGA-10 tbl_manutencao_ambiental; RG-SGA-06 tbl_pam (custos)", "Conforme", "", ""),
    ("REQ-21", "7.2", "Competência de quem afeta o desempenho ambiental", "Não", "Disponível como evidência", "PR-SGA-07", "RG-SGA-08 tbl_competencias, tbl_registo_formacao", "Conforme", "", ""),
    ("REQ-22", "7.3", "Consciencialização (política, aspetos, contributo, consequências)", "Não", "—", "PR-SGA-07", "RG-SGA-08; RG-SGA-16 tbl_kaizen", "Conforme", "", ""),
    ("REQ-23", "7.4", "Comunicação interna e externa planeada, rastreável; permitir contribuir para a melhoria", "Sim", "Disponível como evidência", "PR-SGA-07", "RG-SGA-09 tbl_comunicacao, tbl_comunicacoes_externas", "Conforme", "Registo de comunicações externas acrescentado; 1 resposta fora de prazo.", ""),
    ("REQ-24", "7.5", "Informação documentada criada, atualizada e controlada ('disponível' / 'disponível como evidência')", "Sim", "Disponível", "PR-SGA-08", "RG-SGA-09 tbl_lista_mestra, tbl_verif_documental", "Conforme", "Manual e procedimentos passam a existir como documentos (Documentos_SGA_Plasticom).", ""),
    ("REQ-25", "8.1", "Controlo operacional dos processos associados aos aspetos significativos", "Não", "Disponível", "PR-SGA-09; PR-SGA-04; IT-SER-03", "RG-SGA-10 tbl_pontos, tbl_execucao_rondas", "Conforme", "", ""),
    ("REQ-26", "8.1", "Processos, produtos e serviços providos externamente controlados ou influenciados, com tipo e extensão definidos", "Sim", "Disponível", "PR-SGA-09", "RG-SGA-11 tbl_fornecedores, tbl_outros_fornecedores (Tipo_Controlo, Extensao_Controlo)", "Conforme", "MOL-01 ainda sem verificação.", ""),
    ("REQ-27", "8.1", "Perspetiva de ciclo de vida: requisitos na conceção e nas compras; informação sobre uso e fim de vida", "Sim", "—", "PR-SGA-09", "RG-SGA-03 AA-037/038/043; RG-SGA-11; RG-SGA-06 PAM-26-10; RG-SGA-20 (RecyClass, requisitos por SKU)", "Parcial", "Documentação PPWR em 17 de 22 famílias (77%) em 22/12/2026; PETG/PVC em substituição (PAM-26-22).", "PAM-26-10"),
    ("REQ-28", "8.2", "Preparação e resposta a emergências, testada e alinhada com 6.1.2", "Sim", "Disponível", "PR-SGA-05; IT-SGA-01; IT-SGA-02", "RG-SGA-12 tbl_cenarios, tbl_simulacros; RG-SGA-07 tbl_incidentes", "Conforme", "IT-SGA-01 rev. 01 (29/10/2026); simulacros de derrame (26/11) e de incêndio (11/12/2026) eficazes.", "PAM-26-21"),
    ("REQ-29", "9.1.1", "Monitorização e medição com métodos, critérios e frequência definidos", "Não", "Disponível como evidência", "PR-SGA-10", "RG-SGA-13 tbl_plano_monitorizacao, tbl_dados_ambientais, tbl_meses, tbl_analises", "Conforme", "Analisadores de energia e contadores de água em serviço desde 15/12/2026 (PAM-26-02); até lá rateio documentado.", "PAM-26-02"),
    ("REQ-30", "9.1.1", "Equipamentos de medição calibrados ou verificados", "Não", "Disponível como evidência", "PR-SGA-10", "RG-SGA-13 tbl_equipamentos", "Conforme", "Balança do parque verificada a 23/10/2026; balanças de piso a 18/11/2026; condutivímetro a 09/12/2026.", "PAM-26-20"),
    ("REQ-31", "9.1.1", "Avaliar o desempenho ambiental e a eficácia do SGA", "Sim", "Disponível como evidência", "PR-SGA-10; PR-SGA-11", "RG-SGA-05 tbl_acomp_objetivos; RG-SGA-15; RG-SGA-16 tbl_emas", "Conforme", "", ""),
    ("REQ-32", "9.1.2", "Avaliar o cumprimento das obrigações de conformidade", "Não", "Disponível como evidência", "PR-SGA-03", "RG-SGA-04 tbl_legal, tbl_hist_conformidade, tbl_obrigacoes; RG-SGA-13 tbl_analises", "Conforme", "Processo conforme; 2 incumprimentos legais em tratamento (ruído, PPWR).", "PAM-26-03; PAM-26-10"),
    ("REQ-33", "9.2.1", "Auditorias internas a intervalos planeados", "Não", "Disponível como evidência", "PR-SGA-11", "RG-SGA-14 tbl_programa_auditorias, tbl_constatacoes", "Conforme", "", ""),
    ("REQ-34", "9.2.2", "Programa de auditoria com objetivos, critérios e âmbito para cada auditoria", "Sim", "Disponível como evidência", "PR-SGA-11", "RG-SGA-14 tbl_programa_auditorias (Objetivo, Criterios, Ambito)", "Parcial", "Programa cobre 2026–27; falta o plano trienal que garanta todas as cláusulas e processos.", ""),
    ("REQ-35", "9.3.1/9.3.2", "Revisão pela gestão com as entradas definidas", "Sim", "Disponível como evidência", "PR-SGA-11", "RG-SGA-15 tbl_agenda (Entrada_9_3_2)", "Conforme", "Entradas a) a g) cobertas.", ""),
    ("REQ-36", "9.3.3", "Resultados da revisão (decisões, recursos, alterações, oportunidades)", "Sim", "Disponível como evidência", "PR-SGA-11", "RG-SGA-15 tbl_decisoes, tbl_conclusoes", "Conforme", "", ""),
    ("REQ-37", "10.1", "Melhoria contínua da adequação, suficiência e eficácia do SGA", "Sim", "—", "PR-SGA-12", "RG-SGA-16 tbl_kaizen; RG-SGA-06; RG-SGA-17", "Conforme", "10.3 integrada na 10.1/10.2 na edição 2026.", ""),
    ("REQ-38", "10.2", "Reagir a NC e incidentes, analisar causas, ação corretiva e verificação da eficácia", "Sim", "Disponível como evidência", "PR-SGA-12", "RG-SGA-07 tbl_nc, tbl_5porques, tbl_incidentes", "Conforme", "Registo de incidentes e quase-incidentes acrescentado.", ""),
]


def matriz(b):
    b.add_list("EstadoReq", ["Conforme", "Parcial", "Lacuna"])
    b.add_list("SimNaoReq", ["Sim", "Não"])
    b.add_list("InfoDoc", ["Disponível", "Disponível como evidência", "—"])
    cols = [
        col("ID_Requisito", 8, desc="Identificador.", key="PK"),
        col("Clausula", 9, desc="Cláusula da ISO 14001:2026."),
        col("Grupo", 7, f='=IF(@Clausula@="","",LEFT(@Clausula@,1))', desc="Cláusula principal (4 a 10)."),
        col("Requisito", 50, desc="Requisito (resumo)."),
        col("Novo_ou_Alterado_2026", 9, dv="SimNaoReq", desc="Sim se é novo ou foi alterado na edição 2026."),
        col("Informacao_Documentada", 16, dv="InfoDoc", desc="Exigência de informação documentada (2026: 'disponível' / 'disponível como evidência')."),
        col("Documento", 26, desc="Documento controlado (Documentos_SGA_Plasticom)."),
        col("Evidencia_Registo_Tabelas", 46, desc="Registo e tabelas com a evidência."),
        col("Estado", 9, dv="EstadoReq", desc="Conforme · Parcial · Lacuna (verificação de 24/09/2026, atualizada a 31/12/2026)."),
        col("Observacao", 44, desc="Observação ou lacuna.", req=False),
        col("Acao", 16, desc="Ação do PAM que trata a lacuna.", req=False),
        col("Pontos", 7, "num", f='=IF(@Estado@="","",IF(@Estado@="Conforme",1,IF(@Estado@="Parcial",0.5,0)))', desc="1 conforme · 0,5 parcial · 0 lacuna (para índice de prontidão)."),
    ]
    names = [c["name"] for c in cols if not c["f"]]
    rows = [dict(zip(names, r)) for r in REQ]
    b.table("Matriz_ISO14001_2026", "tbl_matriz_iso", cols, rows,
            "Mapa requisito → documento → evidência → estado para a ISO 14001:2026 (auditoria interna, transição e gap analysis).",
            title="MATRIZ DE REQUISITOS ISO 14001:2026 — DOCUMENTO, EVIDÊNCIA E ESTADO",
            subtitle="Verificação de 24/09/2026 (atualizada a 31/12/2026) face aos guias de transição da pasta de interpretação · Parcial = processo existe mas falta evidência ou eficácia",
            cf=[("Estado", {"Conforme": "green", "Parcial": "orange", "Lacuna": "red"}), ("Novo_ou_Alterado_2026", {"Sim": "blue"})],
            row_height=36, freeze_col=2)
    ws = b.sheet("Resumo_Prontidao", "Índice de prontidão para a ISO 14001:2026 por cláusula (calculado a partir de tbl_matriz_iso).")
    ws["A1"] = "PRONTIDÃO PARA A ISO 14001:2026 — RESUMO POR CLÁUSULA"
    ws["A1"].font = F_TITLE
    header_row(ws, 3, ["Cláusula", "Tema", "Requisitos", "Conforme", "Parcial", "Lacuna", "Novos 2026", "Índice de prontidão"],
               widths=[10, 30, 11, 10, 10, 10, 11, 14])
    temas = [("4", "Contexto"), ("5", "Liderança"), ("6", "Planeamento"), ("7", "Suporte"), ("8", "Operação"), ("9", "Avaliação do desempenho"), ("10", "Melhoria")]
    R = lambda c: f"tbl_matriz_iso[{c}]"
    for k, (g, t) in enumerate(temas):
        r = 4 + k
        crit = f'"{g}"' if g != "10" else '"1"'
        ws.cell(row=r, column=1, value=g)
        ws.cell(row=r, column=2, value=t)
        ws.cell(row=r, column=3, value=f'=COUNTIFS({R("Grupo")},{crit},{R("Clausula")},"{g}*")')
        for j, e in enumerate(("Conforme", "Parcial", "Lacuna")):
            ws.cell(row=r, column=4 + j, value=f'=COUNTIFS({R("Grupo")},{crit},{R("Clausula")},"{g}*",{R("Estado")},"{e}")')
        ws.cell(row=r, column=7, value=f'=COUNTIFS({R("Grupo")},{crit},{R("Clausula")},"{g}*",{R("Novo_ou_Alterado_2026")},"Sim")')
        c = ws.cell(row=r, column=8, value=f'=IFERROR(SUMIFS({R("Pontos")},{R("Grupo")},{crit},{R("Clausula")},"{g}*")/C{r},"")')
        c.number_format = "0%"
    rt = 4 + len(temas)
    ws.cell(row=rt, column=1, value="Total").font = F_BOLD
    for col_ in range(3, 8):
        L = "ABCDEFGH"[col_ - 1]
        ws.cell(row=rt, column=col_, value=f"=SUM({L}4:{L}{rt - 1})").font = F_BOLD
    c = ws.cell(row=rt, column=8, value=f'=IFERROR(SUM({R("Pontos")})/C{rt},"")')
    c.number_format, c.font = "0%", F_BOLD
    for r in range(4, rt + 1):
        for cc in range(1, 9):
            ws.cell(row=r, column=cc).border = BORDER
    ws.cell(row=rt + 2, column=1, value=("Índice de prontidão = (Conforme + 0,5 × Parcial) ÷ requisitos. Os requisitos 'Parcial' têm a ação do PAM indicada na matriz. "
                                         "Dados simulados da fábrica fictícia Plasticom.")).font = F_SUB
