"""RG-SGE-12 — Auditoria interna do SGE: auditores, programa, checklist por requisito e constatações.
ISO 50001:2018 9.2.1 a)–c), 9.2.2 a)–f) · ISO 19011 (diretrizes) · ISO 50003:2021 (competência em desempenho energético)."""
from sgelib import *
from dimse import *

AUDITORES = [
    ("AUDE-01", "Auditor(a) Interno(a) do SGQ (P-003 Carlos Mendes)", "Auditor interno SGQ/SGA; FOR-E-06 (24 h, 06/2026)", "ISO 50001, ISO 19011, noções de IDE/LBE", "Todos exceto LAB/QUA", 16, "Bom", "Qualidade (auditoria da própria área)", "Sim", "2026-06-03", "Sim"),
    ("AUDE-02", "Gestor do SGA / EHS", "Auditor ISO 14001; FOR-E-06", "Ligação SGA–SGE, requisitos legais", "Todos exceto GES", 12, "Bom", "SGA", "Sim", "2026-06-03", "Sim"),
    ("AUDE-03", "Consultor(a) externo(a) de energia (auditor SGCIE credenciado)", "Auditor energético credenciado DGEG; ISO 50001 lead auditor", "Revisão energética, M&V, ISO 50003 (desempenho energético)", "Todos", 24, "Muito bom", "—", "Sim", "2025-11-20", "Sim"),
]
PROGRAMA = [
    ("AUD-E-2026-01", "Todo o SGE (4 a 10) — auditoria de diagnóstico antes da certificação", "Verificar a conformidade com a ISO 50001:2018 + Amd 1:2024 e se o SGE melhora o desempenho energético (9.2.1 a–c)",
     "ISO 50001:2018 + Amd 1:2024; PR-SGE-01 a 12; DL 71/2008", "Entrevistas, amostragem de registos, visita aos USE, reexecução dos cálculos da LBE", "AUDE-03 (líder); AUDE-01", "2026-11-16", "2026-11-18", "Realizada", "Sim"),
    ("AUD-E-2027-01", "Todo o SGE — auditoria de pré-certificação", "Confirmar o fecho das NC de 2026 e a melhoria demonstrada", "Idem", "Idem; foco em 8.2, 8.3, 9.1.1", "AUDE-03; AUDE-02", "2027-05-10", None, "Planeada", "—"),
    ("AUD-E-2027-02", "Auditoria de certificação (fase 1 e 2) — organismo externo", "Certificação ISO 50001 (ISO 50003:2021)", "ISO 50001", "Organismo de certificação", "Externa", "2027-09-20", None, "Planeada", "—"),
]
CHECK = [
    ("4.1–4.3", "Contexto, partes interessadas, âmbito e fronteiras (incl. alterações climáticas)", "RG-SGE-01 completo; âmbito mantido", "Conforme"),
    ("5.1", "Liderança: equipa de gestão de energia, IDE representativos, alterações", "EGE nomeada em 07/2026; LIDE-03/07/10/12/13 parciais", "Conforme"),
    ("5.2", "Política energética com a–g, comunicada e disponível", "POL-SGE-01 afixada; 3 operadores não a conheciam", "Oportunidade de melhoria"),
    ("6.1", "Riscos e oportunidades do SGE e avaliação da eficácia", "RG-SGE-03; RE-xx ainda não incluídos no RG-SGA-02", "Oportunidade de melhoria"),
    ("6.2", "Objetivos, metas energéticas e planos com método de verificação", "6 objetivos SMART; 8 metas; 7 planos com IPMVP", "Conforme"),
    ("6.3", "Revisão energética: métodos e critérios mantidos, resultados retidos", "Critérios de USE claros; consumos por uso estimados", "Conforme"),
    ("6.4 / 6.5", "IDE e LBE: metodologia, normalização, validade estatística", "LBE-01 'válida com reserva' (p-valor dos graus-dia 0,27)", "Observação"),
    ("6.6", "Plano de recolha de dados; exatidão e repetibilidade", "Plano completo; submedição por instalar à data da auditoria", "Oportunidade de melhoria"),
    ("7.2 / 7.3", "Competência e consciencialização das pessoas que afetam os USE", "Registos de formação; 83% dos operadores formados", "Conforme"),
    ("7.4", "Comunicação e processo de sugestões", "2 sugestões de setembro sem resposta em 15 dias", "Oportunidade de melhoria"),
    ("7.5", "Informação documentada", "Controlo pelo PR-SGA-08; lista mestra do SGE incompleta", "Conforme"),
    ("8.1", "Critérios operacionais dos USE e controlo das alterações não intencionais", "ANI-02 (setpoint do chiller) tratado; CO-09/13 ainda não conformes", "Conforme"),
    ("8.2", "Projeto com avaliação do desempenho energético", "Linhas novas (PRJ-E-01) sem avaliação energética documentada", "Não conformidade menor"),
    ("8.3", "Aquisições: critérios, informação aos fornecedores, compra de energia", "Contrato de manutenção do chiller sem critérios energéticos (AQE-26-04)", "Não conformidade menor"),
    ("9.1.1", "IDE vs LBE; desvios significativos investigados", "DSV-26-01 a 03 investigados em ≤ 30 dias", "Conforme"),
    ("9.1.2", "Avaliação da conformidade legal (SGCIE)", "REP 2026 entregue a 28/10/2026", "Conforme"),
    ("9.3", "Revisão pela gestão", "Por realizar (agendada para 18/12/2026)", "Não aplicável"),
    ("10.1 / 10.2", "NC, ação corretiva e melhoria contínua demonstrada", "Melhoria ainda não demonstrada à data (novembro) — dados de out/2026 promissores", "Observação"),
]
CONST = [
    ("CONE-A-26-01", "8.2", "Não conformidade menor", "Manutenção / engenharia", "O projeto das linhas novas (PRJ-E-01) não tem evidência de avaliação do desempenho energético ao longo da vida nem de critérios de controlo operacional.",
     "Atas de projeto e propostas sem análise energética nem LCC", "NCE-26-01", "2027-02-28", "Em curso"),
    ("CONE-A-26-02", "8.3", "Não conformidade menor", "Compras", "O contrato de manutenção do chiller (serviço com impacto no USE-04) não informa o fornecedor de que o desempenho energético é critério nem tem especificação.",
     "Contrato AQE-26-04 de 15/06/2026", "NCE-26-02", "2026-12-31", "Fechada"),
    ("CONE-A-26-03", "6.4 / 6.5", "Observação", "Gestão de energia", "LBE-01 aprovada com um p-valor de 0,27 nos graus-dia: justificar ou rever com dados medidos.", "LBE_Modelo", "—", "2027-07-31", "Em curso"),
    ("CONE-A-26-04", "7.4", "Oportunidade de melhoria", "Gestão de energia", "Definir prazo de resposta às sugestões e cumpri-lo (2 sugestões de setembro sem resposta).", "tbl_sugestoes", "—", "2026-12-31", "Fechada"),
    ("CONE-A-26-05", "6.6", "Oportunidade de melhoria", "Dados / TI", "Acelerar a submedição: os IDE por USE são estimados.", "tbl_contadores", "—", "2026-12-15", "Fechada"),
    ("CONE-A-26-06", "5.2", "Oportunidade de melhoria", "Produção", "Reforçar a comunicação da política aos operadores do turno 3.", "Entrevistas no posto", "—", "2026-12-18", "Fechada"),
    ("CONE-A-26-07", "6.1", "Oportunidade de melhoria", "Gestão de topo", "Incluir os riscos RE-01 a RE-07 no registo corporativo RG-SGA-02 (fonte única).", "RG-SGE-03", "—", "2027-03-31", "Em curso"),
    ("CONE-A-26-08", "10.2", "Observação", "Gestão de energia", "A melhoria do desempenho energético ainda não estava demonstrada; manter o foco em ações de retorno rápido e na M&V.", "LBE_Modelo (dados até out/2026)", "—", "2026-12-31", "Fechada"),
]


def build(out):
    b = Book("RG-SGE-12", "Auditoria Interna do SGE",
             activities="Planear e realizar auditorias internas para saber se o SGE melhora o desempenho energético, está conforme e é eficaz; qualificar auditores; registar constatações.",
             clauses="9.2.1 a) melhora o desempenho energético; b) conformidade (requisitos próprios, política, objetivos, metas, ISO 50001); c) implementado e mantido; "
                     "9.2.2 a)–f) programa, critérios e âmbito, objetividade e imparcialidade, relato, ações (10.1/10.2), evidência retida.",
             purpose="Auditores do SGE com competência em desempenho energético; programa 2026–2027; checklist por requisito da auditoria de diagnóstico AUD-E-2026-01 (16–18/11/2026) "
                     "e 8 constatações (2 NC menores) com ligação às ações.",
             links=[("RG-SGQ-16 / RG-SGA-14", "Auditorias do SGQ e do SGA (mesmas tabelas)."), ("RG-SGE-14", "NC abertas (NCE-xx)."), ("RG-SGE-13", "Resultados relatados na revisão pela gestão.")],
             guidance=[("ISO 19011 (diretrizes para auditorias de sistemas de gestão)", "Programa baseado no risco, imparcialidade, amostragem, relato."),
                       ("ISO 50003:2021", "Competências de desempenho energético do auditor e verificação da melhoria demonstrada (usadas como critério interno)."),
                       ("M-11 O processo de certificação (curso Bureau Veritas)", "Fases 1 e 2 da certificação e evidências esperadas.")],
             legal=[("DL 71/2008 (SGCIE)", "O auditor externo AUDE-03 é auditor energético credenciado pela DGEG.")])
    b.add_list("Classificacao", ["Não conformidade maior", "Não conformidade menor", "Observação", "Oportunidade de melhoria", "Conforme", "Não aplicável"])
    acols = [col("ID_Auditor", 8, key="PK", desc="Auditor."), col("Nome", 40, desc="Nome / função."), col("Qualificacao", 34, desc="Qualificação."),
             col("Conhecimento_Tecnico", 32, desc="Conhecimento de desempenho energético (ISO 50003)."), col("Pode_Auditar", 20, desc="Âmbito que pode auditar."),
             col("Horas_Auditoria", 8, "int", desc="Horas de auditoria de energia."), col("Avaliacao_Desempenho", 10, desc="Avaliação."), col("Nao_Pode_Auditar", 22, desc="Áreas excluídas (imparcialidade)."),
             col("Competencia_Remota", 8, desc="Auditoria remota?"), col("Ultima_Formacao", 11, "date", desc="Última formação."), col("Qualificado", 8, desc="Qualificado?")]
    b.table("Auditores", "tbl_auditores", acols, rows_from(input_names(acols), AUDITORES, dates=("Ultima_Formacao",)), "Auditores do SGE (mesmas colunas do RG-SGQ-16).",
            title="AUDITORES DO SGE (9.2.2 c)", row_height=30)
    pcols = [col("ID_Auditoria", 13, key="PK", desc="Auditoria."), col("Ambito", 36, desc="Âmbito (9.2.2 b)."), col("Objetivo", 40, desc="Objetivo."), col("Criterios", 28, desc="Critérios (9.2.2 b)."),
             col("Metodo", 34, desc="Método."), col("Equipa_Auditora", 18, desc="Equipa."), col("Data_Planeada", 11, "date", desc="Início."), col("Data_Real", 11, "date", desc="Fim.", req=False),
             col("Estado", 10, desc="Estado."), col("Relatorio_Emitido", 8, desc="Relatório emitido?"),
             col("N_Constatacoes", 8, "int", f='=IF(@ID_Auditoria@="","",IF(@Estado@="Realizada",COUNTA(tbl_constatacoes[ID_Constatacao]),0))', desc="Constatações."),
             col("N_NC", 6, "int", f='=IF(@ID_Auditoria@="","",IF(@Estado@="Realizada",COUNTIF(tbl_constatacoes[Classificacao],"Não conformidade*"),0))', desc="Não conformidades.")]
    b.table("Programa_Auditorias", "tbl_programa_auditorias", pcols, rows_from(input_names(pcols), PROGRAMA, dates=("Data_Planeada", "Data_Real")),
            "Programa de auditorias do SGE (9.2.2 a) — mesmo nome do SGA/SGQ.", title="PROGRAMA DE AUDITORIAS DO SGE 2026–2027 (9.2.2 a)", row_height=36)
    ccols = [col("ID_Pergunta", 8, key="PK", desc="Pergunta."), col("ID_Auditoria", 13, desc="Auditoria.", key="FK → tbl_programa_auditorias"), col("Clausula", 10, desc="Requisito."),
             col("Questao_Auditoria", 50, desc="O que foi verificado."), col("Evidencia_Objetiva", 50, desc="Evidência."), col("Resultado", 18, dv="Classificacao", desc="Resultado.")]
    crows = [dict(ID_Pergunta=f"CHKE-{i + 1:02d}", ID_Auditoria="AUD-E-2026-01", Clausula=c[0], Questao_Auditoria=c[1], Evidencia_Objetiva=c[2], Resultado=c[3]) for i, c in enumerate(CHECK)]
    b.table("Checklist", "tbl_checklist_aud", ccols, crows, "Checklist da auditoria AUD-E-2026-01 por requisito.", title="CHECKLIST — AUD-E-2026-01 (16–18/11/2026)",
            cf=[("Resultado", {"Não conformidade": "red", "Observação": "yellow", "Oportunidade": "blue", "Conforme": "green"})], row_height=30)
    kcols = [col("ID_Constatacao", 12, key="PK", desc="Constatação."), col("ID_Auditoria", 13, desc="Auditoria."), col("Clausula", 9, desc="Requisito."),
             col("Classificacao", 18, dv="Classificacao", desc="Classificação."), col("Processo_Auditado", 18, desc="Área."), col("Constatacao", 60, desc="Constatação."),
             col("Evidencia_Objetiva", 30, desc="Evidência."), col("ID_NC", 9, desc="NC aberta (RG-SGE-14).", key="FK → RG-SGE-14 tbl_nc", req=False), col("Prazo", 11, "date", desc="Prazo."),
             col("Estado", 9, desc="Estado."), col("Alerta", 9, f='=IF(@ID_Constatacao@="","",IF(AND(@Estado@<>"Fechada",@Prazo@<DataRef),"Atrasada",""))', desc="Atrasada?")]
    b.table("Constatacoes", "tbl_constatacoes", kcols,
            rows_from(["ID_Constatacao", "Clausula", "Classificacao", "Processo_Auditado", "Constatacao", "Evidencia_Objetiva", "ID_NC", "Prazo", "Estado"], CONST, dates=("Prazo",)),
            "Constatações da auditoria interna (9.2.2 d–f).", title="CONSTATAÇÕES — AUD-E-2026-01",
            cf=[("Classificacao", {"Não conformidade": "red", "Observação": "yellow", "Oportunidade": "blue"}), ("Alerta", {"Atrasada": "red"})], row_height=45)
    ws = b.wb["Constatacoes"]
    t = b.tables["tbl_constatacoes"]
    for r in range(t["first"], t["last"] + 1):
        ws[f"{t['colmap']['ID_Auditoria']}{r}"] = "AUD-E-2026-01"
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
