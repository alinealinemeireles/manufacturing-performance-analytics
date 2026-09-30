import datetime as dt
from sgalib import *
from dims import *

d = lambda s: dt.date.fromisoformat(s) if s else None

PROG = [
    ("AUD-2026-01", "Controlos operacionais de maior significância ambiental",
     "Verificar a conformidade e a eficácia dos controlos operacionais e de emergência nos processos com aspetos significativos; verificar a eficácia das ações da auditoria 2025; preparar a transição para a ISO 14001:2026.",
     "Armazém de químicos; parque de resíduos; manutenção/engenharia (alterações); serigrafia; utilidades; emergência",
     "ISO 14001:2026 (6.1.2, 6.3, 7.2, 7.3, 8.1, 8.2, 9.1.1); PR-SGA-04; IT-SGA-01; RGGR; REACH/CLP; RGR",
     "2026-09-16", "2026-09-17", "AUD-001 (auditor líder, Qualidade) + AUD-002", "Auditores sem responsabilidade direta nas áreas auditadas", "Realizada", 10),
    ("AUD-2026-02", "Produto, compras e conformidade legal", "Avaliar a conformidade PPWR, a avaliação ambiental de fornecedores e a vigilância legal.",
     "R&D; compras; SGA (requisitos legais)", "ISO 14001:2026 (6.1.3, 8.1 fornecedores externos, 9.1.2); Reg. (UE) 2025/40", "2026-11-18", "2026-11-19",
     "AUD-003 + auditor externo convidado", "Auditor externo para R&D", "Realizada", 4),
    ("AUD-2027-01", "Liderança, contexto, objetivos e desempenho", "Verificar a integração do clima e da biodiversidade no contexto (4.1), os objetivos e a avaliação do desempenho e da eficácia (9.1.1).",
     "Gestão de topo; SGA; produção", "ISO 14001:2026 (4, 5, 6.2, 9.1, 9.3)", "2027-03-10", "2027-03-11", "AUD-001 + AUD-003", "Auditor líder não reporta ao SGA", "Planeada", 0),
]

# constatações da AUD-2026-02 (18–19/11/2026), acrescentadas no fecho do ano
CONST_Q4 = [
    ("CONST-11", "R&D — conformidade PPWR", "RD", "6.1.3; 9.1.2", "Como é demonstrada a conformidade PPWR das famílias colocadas no mercado desde 12/08/2026?",
     "Documentação técnica e declaração UE por família.", "13 de 22 famílias com declaração em 18/11/2026; plano com datas para as restantes; 5 famílias dependem da substituição de PETG/PVC.",
     "OM", "—", "Reg. (UE) 2025/40 e ISO 14001:2026 §6.1.3", "A NC legal NC-SGA-26-02 já está aberta e o plano é credível; oportunidade de priorizar pelas vendas.", "", "PAM-26-10", "AUD-003"),
    ("CONST-12", "Compras", "CMP", "8.1", "A avaliação ambiental dos fornecedores está aplicada e o controlo é proporcional ao risco?",
     "Critérios, avaliação e extensão do controlo por fornecedor.", "Avaliação aplicada a 10 fornecedores críticos (PAM-26-16); controlo coerente com a relevância.",
     "Conforme", "—", "ISO 14001:2026 §8.1 (processos externos)", "—", "", "", "AUD-003"),
    ("CONST-13", "Compras", "CMP", "6.1.3", "As declarações de substâncias (SVHC/PFAS) dos fornecedores estão válidas?",
     "Declaração anual de todos os fornecedores de matérias com contacto.", "2 declarações (DEC-05, DEC-09) em falta há mais de 60 dias apesar dos pedidos formais (PAM-26-34).",
     "OM", "—", "REACH art. 33.º; ISO 14001:2026 §6.1.3", "Pedido feito; escalar ao fornecedor ou suspender o material.", "", "PAM-26-34", "AUD-003"),
    ("CONST-14", "Compras", "CMP", "8.1; 9.1.1", "O conteúdo reciclado declarado aos clientes tem prova (EN 15343) para cada lote?",
     "Certificado válido na data de receção de cada lote de PCR/rPET.", "Lotes de rPET recebidos de jul a out/2026 com o certificado CERT-03 expirado (30/06/2026) contados como reciclado no KPI e nas fichas técnicas.",
     "NC", "Menor", "ISO 14001:2026 §8.1 e ISO 14021 §7.8 (alegação de conteúdo reciclado)", "Alegação sem prova para os lotes em causa.", "NC-SGA-26-11", "PAM-26-25", "Auditor externo"),
]
# (ID, Processo_Auditado, Area, Clausula, Pergunta, Evidencia_esperada, Evidencia_obtida, Classificacao, Gravidade, Requisito_violado, Justificacao, ID_NC, ID_PAM, Auditor)
CONST = [
    ("CONST-01", "Armazém de químicos", "ARQ", "8.1", "Como é garantida a contenção em caso de derrame dos bidões de óleo e de solvente?",
     "Todos os recipientes > 20 L sobre bacia; ronda RON-02 conforme.",
     "3 bidões de 200 L de óleo hidráulico novo pousados diretamente no chão, sem bacia de retenção (as 2 bacias existentes estavam ocupadas). Fotografia AUD-01-F03.",
     "NC", "Menor", "ISO 14001:2026 §8.1 (controlo operacional) e PR-SGA-04; risco de incumprimento do regime de prevenção da poluição do solo",
     "O critério operacional (bacia obrigatória) está definido mas não é cumprido; há potencial de contaminação do solo. Menor porque não houve derrame e a falha é pontual.", "NC-SGA-26-04", "PAM-26-19", "AUD-001"),
    ("CONST-02", "Armazém de químicos", "ARQ", "6.1.3; 7.5", "As FDS de todos os químicos em uso estão disponíveis e atualizadas no ponto de uso?",
     "FDS de todos os produtos, com revisão ≤ 3 anos.",
     "40 de 42 FDS atualizadas; 2 FDS de solventes com revisão de 2021 — atualização já pedida ao fornecedor em 03/09/2026.",
     "OM", "—", "ISO 14001:2026 §7.5 (informação documentada) e REACH (art. 31)",
     "A organização detetou e está a tratar a lacuna; oportunidade de automatizar um alerta de revisão das FDS no inventário.", "", "", "AUD-002"),
    ("CONST-03", "Parque de resíduos", "PRS", "8.1", "Os resíduos perigosos estão identificados, fechados e armazenados de forma a evitar contaminação?",
     "Contentores com código LER, fechados, em bacia e sob cobertura.",
     "Contentor de absorventes contaminados (LER 15 02 02*) sem etiqueta e sem tampa, exposto à chuva. Fotografia AUD-01-F07.",
     "NC", "Menor", "ISO 14001:2026 §8.1; Decreto-Lei n.º 102-D/2020 (RGGR) — armazenagem adequada dos resíduos",
     "Requisito legal e operacional não cumprido; risco de escorrência para a rede pluvial.", "NC-SGA-26-05", "PAM-26-15", "AUD-001"),
    ("CONST-04", "Parque de resíduos", "PRS", "9.1.1", "Como é assegurada a fiabilidade das quantidades de resíduos reportadas no MIRR?",
     "Pesagem interna coerente com o peso no destino (e-GAR).",
     "Em 2 de 10 e-GAR amostradas a pesagem interna difere 6% do peso confirmado no destino.",
     "OM", "—", "ISO 14001:2026 §9.1.1 (dados fiáveis)",
     "Não há requisito violado (o MIRR usa o peso do destino), mas a reconciliação mensal melhoraria a fiabilidade dos indicadores.", "", "", "AUD-002"),
    ("CONST-05", "Manutenção / engenharia", "MAN", "6.3", "Como são avaliados os impactes ambientais e os requisitos legais antes de alterar equipamentos ou processos?",
     "Pedido de alteração com análise ambiental/legal aprovada pelo SGA.",
     "Os compressores CMP-01/02 foram substituídos em 02/2026 (pedido INV-2026-004) sem avaliação do ruído, dos aspetos ou dos requisitos legais; não existe procedimento de gestão de alterações.",
     "NC", "Menor", "ISO 14001:2026 §6.3 Planeamento de alterações (novo requisito)",
     "Requisito novo da edição 2026 não implementado; originou a NC legal de ruído (NC-SGA-26-01).", "NC-SGA-26-06", "PAM-26-17", "AUD-001"),
    ("CONST-06", "Manutenção / engenharia", "PRS", "9.1.1", "Os equipamentos usados para medir dados ambientais estão calibrados ou verificados?",
     "Plano de calibração com todos os equipamentos e etiquetas válidas.",
     "Balança de plataforma do parque de resíduos com última verificação em 03/2024 (periodicidade anual) e ausente do plano de calibração.",
     "NC", "Menor", "ISO 14001:2026 §9.1.1 (equipamento de monitorização calibrado ou verificado)",
     "Equipamento de medição de um indicador reportado à APA sem verificação válida.", "NC-SGA-26-07", "PAM-26-20", "AUD-002"),
    ("CONST-07", "Serigrafia", "SER", "7.2; 7.3", "Os operadores conhecem o aspeto significativo do seu posto e aplicam os controlos?",
     "Operadores formados na IT de limpeza; recipientes fechados.",
     "O operador do turno 2 (temporário, OP-SK-T01) não tem formação na instrução de limpeza e não sabia que o solvente emite COV; 2 latas de solvente abertas no posto.",
     "NC", "Menor", "ISO 14001:2026 §7.2 (competência) e §7.3 (consciencialização)",
     "Pessoa que realiza trabalho com impacte significativo sem a competência e a consciencialização exigidas.", "NC-SGA-26-08", "PAM-26-08", "AUD-001"),
    ("CONST-08", "Serigrafia", "SER", "10.1", "Como se minimiza a geração de resíduos perigosos (panos e absorventes com solvente)?",
     "Medidas de prevenção na fonte.",
     "Usam-se panos descartáveis; o resíduo 15 02 02* é ≈ 0,5 t/ano.",
     "OM", "—", "ISO 14001:2026 §10.1 (melhoria contínua) e hierarquia de resíduos do RGGR",
     "Oportunidade: panos reutilizáveis lavados por empresa licenciada reduziriam o resíduo perigoso e o custo.", "", "", "AUD-002"),
    ("CONST-09", "Utilidades", "UTL", "9.1.1; 6.2", "Como é controlado o consumo de energia do ar comprimido?",
     "Indicador de energia do ar comprimido e fugas etiquetadas.",
     "Não há indicador (kWh/Nm³); 3 fugas audíveis sem etiqueta; campanha de fugas (PAM-26-01) em curso com 25% de evolução.",
     "OM", "—", "ISO 14001:2026 §9.1.1 (o que monitorizar) e §6.2 (objetivo OBJ-01)",
     "A ação já está planeada; recomenda-se incluir o KPI kWh/Nm³ no painel mensal para medir a eficácia.", "", "PAM-26-01", "AUD-001"),
    ("CONST-10", "Emergência", "GER", "8.2", "As ações de resposta a emergências ambientais são testadas periodicamente?",
     "Simulacros dos cenários ambientais com tempos medidos.",
     "Nunca foi feito simulacro de derrame; no único simulacro (incêndio, 14/11/2025) a válvula de corte pluvial foi fechada em 9 min (meta ≤ 5 min).",
     "NC", "Menor", "ISO 14001:2026 §8.2 (testar periodicamente as ações de resposta planeadas)",
     "Cenário de emergência de maior criticidade (EMG-01) nunca testado.", "NC-SGA-26-09", "PAM-26-21", "AUD-002"),
]


def build(out):
    b = Book("RG-SGA-14", "Programa e Registo de Auditoria Interna do SGA",
             activities="Atividade 5.3 Parte 1 — da checklist ao relatório: âmbito, questões de auditoria, evidência simulada, classificação NC/OM e justificação por cláusula/requisito legal. A Parte 2 (Lusitana Móveis) está no documento Word.",
             clauses="9.2.1; 9.2.2 Programa de auditoria interna (ISO 14001:2026: definir objetivos, critérios e âmbito de cada auditoria); ISO 19011:2018",
             purpose="Planear o programa de auditorias por importância ambiental, registar cada questão com a evidência objetiva, classificar a constatação (NC ou OM) com o requisito e ligar às NC e ações. As constatações ficam em formato de tabela para análise por cláusula, processo e classificação.",
             links=[("RG-SGA-07 NC", "ID_NC liga cada NC de auditoria ao registo de não conformidades."), ("RG-SGA-06 PAM", "ID_PAM liga a ação corretiva.")])
    b.add_list("EstadoAud", ["Planeada", "Realizada", "Adiada", "Cancelada"])
    b.add_list("Classificacao", ["NC", "OM", "Conforme"])
    b.add_list("Gravidade", ["Maior", "Menor", "—"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Clausula", CLAUSE_CODES)

    pcols = [col("ID_Auditoria", 12, desc="Auditoria.", key="PK"), col("Tema", 32, desc="Tema."), col("Objetivo", 56, desc="Objetivo da auditoria (exigido pela ISO 14001:2026)."),
             col("Ambito", 40, desc="Processos/áreas."), col("Criterios", 44, desc="Critérios de auditoria."),
             col("Data_Inicio", 11, "date", desc="Início."), col("Data_Fim", 11, "date", desc="Fim."), col("Equipa_Auditora", 30, desc="Auditores."),
             col("Independencia", 30, desc="Como se garante a imparcialidade."), col("Estado", 10, dv="EstadoAud", desc="Estado."),
             col("N_Questoes", 9, "int", desc="N.º de questões."),
             col("N_NC", 7, "int", f='=COUNTIFS(tbl_constatacoes[ID_Auditoria],@ID_Auditoria@,tbl_constatacoes[Classificacao],"NC")', desc="N.º de NC."),
             col("N_OM", 7, "int", f='=COUNTIFS(tbl_constatacoes[ID_Auditoria],@ID_Auditoria@,tbl_constatacoes[Classificacao],"OM")', desc="N.º de OM.")]
    prow = []
    for p in PROG:
        dd = dict(zip([c["name"] for c in pcols if not c["f"]], p))
        dd["Data_Inicio"], dd["Data_Fim"] = d(dd["Data_Inicio"]), d(dd["Data_Fim"])
        prow.append(dd)
    b.table("Programa_Auditorias", "tbl_programa_auditorias", pcols, prow, "Programa de auditorias internas 2026-2027 (objetivos, âmbito, critérios).", row_height=80)

    ccols = [col("ID_Constatacao", 10, desc="Constatação.", key="PK"), col("ID_Auditoria", 12, desc="Auditoria.", key="FK → tbl_programa_auditorias"),
             col("Processo_Auditado", 20, desc="Âmbito (processo)."), col("Area", 7, dv="Processo", desc="Código do processo."),
             col("Clausula", 9, desc="Cláusula(s) ISO 14001:2026."), col("Questao_Auditoria", 46, desc="Pergunta feita."),
             col("Evidencia_Esperada", 34, desc="O que deveria existir."), col("Evidencia_Objetiva", 56, desc="O que se encontrou (evidência simulada)."),
             col("Classificacao", 9, dv="Classificacao", desc="NC (requisito não cumprido) ou OM (oportunidade de melhoria)."),
             col("Gravidade", 8, dv="Gravidade", desc="Maior / Menor (NC)."), col("Requisito_Violado_ou_Melhoravel", 46, desc="Cláusula da norma ou requisito legal."),
             col("Justificacao", 50, desc="Porque é NC ou OM."), col("ID_NC", 12, desc="NC registada.", key="FK → RG-SGA-07", req=False),
             col("ID_PAM", 10, desc="Ação.", key="FK → RG-SGA-06", req=False), col("Auditor", 9, desc="Auditor."),
             col("Controlo_Qualidade", 18, f='=IF(AND(@Classificacao@="NC",OR(@ID_NC@="",@Requisito_Violado_ou_Melhoravel@="")),"FALTA NC/requisito",IF(@Evidencia_Objetiva@="","FALTA evidência","OK"))', desc="Regras: NC exige requisito e registo de NC; toda a constatação exige evidência.")]
    crow = []
    for c in CONST + CONST_Q4:
        dd = dict(zip([x["name"] for x in ccols if not x["f"] and x["name"] != "ID_Auditoria"], c))
        dd["ID_Auditoria"] = "AUD-2026-02" if c in CONST_Q4 else "AUD-2026-01"
        dd["ID_NC"] = dd["ID_NC"] or None
        dd["ID_PAM"] = dd["ID_PAM"] or None
        crow.append(dd)
    b.table("Checklist_Constatacoes", "tbl_constatacoes", ccols, crow, "Checklist de auditoria com evidência e classificação (1 linha por questão).",
            title="AUDITORIAS INTERNAS 2026 — CHECKLIST E CONSTATAÇÕES", subtitle="Questão → evidência objetiva → classificação (NC/OM) → requisito → justificação · AUD-2026-01 (16–17/09/2026) e AUD-2026-02 (18–19/11/2026)",
            cf=[("Classificacao", {"NC": "red", "OM": "blue", "Conforme": "green"}), ("Controlo_Qualidade", {"FALTA": "red", "OK": "green"})],
            row_height=100, freeze_col=1)

    ws = b.sheet("Relatorio_Resumo", "Síntese do relatório de auditoria: constatações por cláusula e processo (calculado).", tab_color="7030A0")
    ws["A1"] = "RELATÓRIO DE AUDITORIA INTERNA AUD-2026-01 — SÍNTESE"
    ws["A1"].font = F_TITLE
    ws["A2"] = "Objetivo, âmbito e critérios na folha Programa_Auditorias. Conclusão: o SGA está implementado; os controlos de químicos, resíduos e emergência precisam de reforço e o novo requisito 6.3 (alterações) não está implementado."
    ws["A2"].font = F_SUB
    C = lambda f: b.ref("tbl_constatacoes", f)
    header_row(ws, 4, ["Processo auditado", "Questões", "NC", "OM"], widths=[30, 10, 8, 8])
    procs = []
    for c in CONST:
        if c[1] not in procs:
            procs.append(c[1])
    for k, p in enumerate(procs):
        r = 5 + k
        ws.cell(row=r, column=1, value=p)
        ws.cell(row=r, column=2, value=f'=COUNTIF({C("Processo_Auditado")},A{r})')
        ws.cell(row=r, column=3, value=f'=COUNTIFS({C("Processo_Auditado")},A{r},{C("Classificacao")},"NC")')
        ws.cell(row=r, column=4, value=f'=COUNTIFS({C("Processo_Auditado")},A{r},{C("Classificacao")},"OM")')
    r = 6 + len(procs)
    ws.cell(row=r, column=1, value="TOTAL").font = F_BOLD
    for j, L in enumerate("BCD"):
        ws.cell(row=r, column=2 + j, value=f"=SUM({L}5:{L}{r - 1})").font = F_BOLD
    r += 2
    header_row(ws, r, ["Cláusula", "NC", "OM"])
    for k, cl in enumerate(["6.1.3", "6.3", "7.2", "7.5", "8.1", "8.2", "9.1.1", "10.1"]):
        rr = r + 1 + k
        ws.cell(row=rr, column=1, value=cl)
        ws.cell(row=rr, column=2, value=f'=COUNTIFS({C("Clausula")},"*{cl}*",{C("Classificacao")},"NC")')
        ws.cell(row=rr, column=3, value=f'=COUNTIFS({C("Clausula")},"*{cl}*",{C("Classificacao")},"OM")')
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
