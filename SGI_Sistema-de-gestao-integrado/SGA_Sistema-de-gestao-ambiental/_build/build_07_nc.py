import datetime as dt
from sgalib import *
import sga_extra as X
from dims import *

d = lambda s: dt.date.fromisoformat(s) if s else None

ORIGENS = ["Ronda ambiental", "Auditoria interna", "Auditoria externa", "Avaliação da conformidade legal", "Monitorização e medição",
           "Incidente ambiental", "Reclamação de parte interessada", "Simulacro"]

# (ID, Data, Origem, ID_Origem, Processo, Local, Tipo, Classificacao, Requisito, Descricao, Evidencia, Impacte, Severidade,
#  C1, CausaRaiz, 6M, Metodo, PAM_C1, PAM_C2, Resp, Prazo, Estado, Fecho, Eficacia, DataEf, Recorrente, Custo, Reportado)
NC = [
    ("NC-SGA-25-01", "2025-09-24", "Auditoria interna", "AUD-2025-01", "ARQ", "Armazém de químicos", "Não conformidade", "NC Menor", "6.1.3 / REACH-CLP",
     "5 FDS em falta no ponto de uso da serigrafia.", "Dossier de FDS da SS-001 sem as FDS de 5 tintas novas.", "Exposição e resposta inadequada em derrame.", "Baixa",
     "Imprimir e colocar as 5 FDS no posto.", "Receção de novos químicos sem verificação de FDS.", "Método", "5 Porquês", "", "", "Responsável de Armazém e Logística",
     "2025-10-31", "Fechada", "2025-10-20", "Eficaz", "2026-01-15", "Não", 0, "Auditor interno"),
    ("NC-SGA-25-02", "2025-10-14", "Avaliação da conformidade legal", "LEG-13", "PRS", "Parque de resíduos", "Não conformidade", "NC Legal", "Portaria 145/2017 (e-GAR)",
     "2 e-GAR de setembro sem confirmação de receção pelo destinatário após 30 dias.", "Consulta SILiAmb de 14/10/2025.", "Rastreabilidade de resíduos incompleta.", "Média",
     "Contactar o operador e obter a confirmação no SILiAmb.", "Sem conferência mensal das e-GAR.", "Método", "5 Porquês", "", "", "Responsável de Armazém e Logística",
     "2025-11-15", "Fechada", "2025-11-05", "Eficaz", "2026-02-10", "Não", 0, "Gestor do SGA"),
    ("NC-SGA-25-03", "2025-11-18", "Incidente ambiental", "INC-2025-07", "UTL", "Chiller CH-01", "Incidente ambiental", "NC Menor", "8.1 / Reg. (UE) 2024/573",
     "Fuga de 3,2 kg de R410A no chiller CH-01 (6,7 tCO2e).", "Relatório do técnico certificado de 18/11/2025.", "Emissão de gás com efeito de estufa.", "Média",
     "Reparação da brasagem e reposição de carga por técnico certificado.", "Corrosão de uma brasagem por vibração (suporte sem amortecedor).", "Máquina", "Ishikawa",
     "", "", "Gerente de Manutenção", "2025-12-15", "Fechada", "2025-12-10", "Eficaz", "2026-05-20", "Não", 1450, "Técnico de manutenção"),
    ("NC-SGA-26-00", "2026-02-11", "Incidente ambiental", "INC-2026-02", "SOP", "ISBM-005", "Incidente ambiental", "NC Menor", "8.1",
     "Fuga de ≈ 15 L de óleo hidráulico da ISBM-005 para o pavimento (contida com absorventes).", "Registo de incidente e ordem de trabalho de 11/02/2026.", "Contaminação do solo (contida).", "Média",
     "Contenção com absorventes; limpeza; encaminhamento 15 02 02*.", "Mangueira hidráulica envelhecida sem substituição preventiva por horas de operação.", "Máquina", "5 Porquês",
     "", "", "Gerente de Manutenção", "2026-03-31", "Fechada", "2026-03-20", "Eficaz", "2026-07-01", "Não", 900, "Operador de sopro"),
    ("NC-SGA-26-01", "2026-09-10", "Avaliação da conformidade legal", "LEG-05", "UTL", "Sala de compressores", "Não conformidade", "NC Legal", "DL 9/2007 (RGR); 6.3",
     "Sem avaliação acústica após a substituição dos compressores (fev/2026).", "Último relatório acústico AC-2023-041 (09/2023).", "Incomodidade da vizinhança; coima.", "Média",
     "Contratar avaliação acústica (PAM-26-03).", "Gestão de mudanças sem checklist ambiental/legal.", "Método", "5 Porquês", "PAM-26-03", "PAM-26-17",
     "Gestor do SGA / EHS (Responsável Ambiental)", "2026-11-30", "Em tratamento", "", "Por avaliar", "2027-04-15", "Não", 1800, "Gestor do SGA"),
    ("NC-SGA-26-02", "2026-09-10", "Avaliação da conformidade legal", "LEG-09", "RD", "R&D / Dossier de produto", "Não conformidade", "NC Legal", "Reg. (UE) 2025/40 (PPWR); 6.1.3",
     "Só 9 de 22 famílias com documentação técnica e declaração UE de conformidade PPWR.", "Lista de dossiers de 10/09/2026.", "Impossibilidade de colocar no mercado; coima.", "Alta",
     "Priorizar as famílias de maior volume.", "Vigilância legal sem regulamentos europeus de produto.", "Método", "5 Porquês", "", "PAM-26-10",
     "Responsável de R&D", "2026-12-31", "Em tratamento", "", "Por avaliar", "2027-01-15", "Não", 26000, "Gestor do SGA"),
    ("NC-SGA-26-03", "2026-09-15", "Ronda ambiental", "RON-06", "INJ", "Zona entre injeção e serigrafia (kit KIT-03)", "Não conformidade", "NC Menor", "8.2; 7.2; 7.3",
     "Kit antipoluição com selo quebrado, praticamente vazio e sem qualquer registo de utilização.",
     "Ronda ambiental mensal de 15/09/2026: KIT-03 com 1 de 12 almofadas absorventes, sem barreiras nem luvas; selo partido; registo de incidentes sem entradas desde 02/2026.",
     "Derrame não contido no próximo evento; derrame anterior não investigado.", "Média",
     "Reposição imediata e selagem (PAM-26-04).", "IT-SGA-01 sem etapa pós-uso, sem stock mínimo nem responsável pela reposição; formação não cobre o ciclo pós-utilização.",
     "Método", "5 Porquês", "PAM-26-04", "PAM-26-05", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-10-31", "Em tratamento", "", "Por avaliar", "2027-01-31", "Não", 1130, "Gestor do SGA (ronda)"),
    ("NC-SGA-26-04", "2026-09-16", "Auditoria interna", "CONST-01", "ARQ", "Armazém de químicos", "Não conformidade", "NC Menor", "8.1",
     "3 bidões de 200 L de óleo hidráulico novo no chão, sem bacia de retenção.", "Observação direta na auditoria de 16/09/2026 (fotografia AUD-01-F03).", "Contaminação do solo em caso de rotura.", "Média",
     "Transferir os bidões para bacia provisória.", "Capacidade de retenção não dimensionada para o stock máximo.", "Material", "5 Porquês", "", "PAM-26-19",
     "Responsável de Armazém e Logística", "2026-10-15", "Em tratamento", "", "Por avaliar", "2026-12-31", "Não", 1200, "Auditor interno"),
    ("NC-SGA-26-05", "2026-09-16", "Auditoria interna", "CONST-03", "PRS", "Parque de resíduos", "Não conformidade", "NC Menor", "8.1; DL 102-D/2020",
     "Contentor de absorventes contaminados (15 02 02*) sem identificação LER e sem tampa.", "Observação direta (fotografia AUD-01-F07).", "Mistura de resíduos; escorrência em chuva.", "Baixa",
     "Colocar tampa e etiqueta provisória.", "Sem etiquetas padronizadas nem verificação na ronda.", "Material", "5 Porquês", "", "PAM-26-15",
     "Responsável de Armazém e Logística", "2026-10-15", "Em tratamento", "", "Por avaliar", "2026-12-31", "Não", 400, "Auditor interno"),
    ("NC-SGA-26-06", "2026-09-17", "Auditoria interna", "CONST-05", "UTL", "Manutenção / engenharia", "Não conformidade", "NC Menor", "6.3 Planeamento de alterações",
     "Substituição dos compressores (fev/2026) sem avaliação de aspetos, requisitos legais e riscos.", "Pedido de investimento INV-2026-004 sem análise ambiental.", "Novos impactes não avaliados (ruído).", "Média",
     "—", "Processo de gestão de mudanças inexistente.", "Método", "5 Porquês", "", "PAM-26-17",
     "Gestor do SGA / EHS (Responsável Ambiental)", "2026-11-30", "Aberta", "", "Por avaliar", "2027-04-15", "Não", 0, "Auditor interno"),
    ("NC-SGA-26-07", "2026-09-17", "Auditoria interna", "CONST-06", "PRS", "Parque de resíduos", "Não conformidade", "NC Menor", "9.1.1",
     "Balança de plataforma do parque de resíduos sem verificação desde 03/2024.", "Etiqueta de verificação de 03/2024; plano de calibração sem o equipamento.", "Dados de resíduos (MIRR) pouco fiáveis.", "Baixa",
     "Suspender o uso da balança até à verificação (usar a balança da expedição).", "Inventário de equipamentos de medição ambiental incompleto.", "Medição", "5 Porquês", "", "PAM-26-20",
     "Gerente da Qualidade", "2026-10-31", "Em tratamento", "", "Por avaliar", "2027-01-15", "Não", 350, "Auditor interno"),
    ("NC-SGA-26-08", "2026-09-17", "Auditoria interna", "CONST-07", "SER", "Serigrafia SS-001", "Não conformidade", "NC Menor", "7.2; 7.3",
     "Operador do turno 2 sem formação na instrução de limpeza de ecrãs; 2 latas de solvente abertas no posto.", "Entrevista e observação; matriz de competências sem registo.", "Emissões de COV e risco de incêndio.", "Média",
     "Fechar as latas; formação imediata no posto.", "Integração de operadores temporários sem formação ambiental.", "Mão de obra", "5 Porquês", "", "PAM-26-08",
     "Gestor do SGA / EHS (Responsável Ambiental)", "2026-11-15", "Em tratamento", "", "Por avaliar", "2027-02-28", "Sim", 0, "Auditor interno"),
    ("NC-SGA-26-09", "2026-09-17", "Auditoria interna", "CONST-10", "GER", "Plano de emergência", "Não conformidade", "NC Menor", "8.2",
     "Nunca foi feito simulacro de derrame; no simulacro de incêndio a válvula de corte pluvial demorou 9 min (meta ≤ 5 min).", "Relatório de simulacro de 14/11/2025; plano de simulacros 2026.", "Resposta ineficaz a emergência ambiental.", "Média",
     "—", "Plano de simulacros só cobre requisitos SCIE (incêndio).", "Método", "5 Porquês", "", "PAM-26-21",
     "Gestor do SGA / EHS (Responsável Ambiental)", "2026-12-15", "Aberta", "", "Por avaliar", "2027-01-31", "Não", 800, "Auditor interno"),
]

# Fecho do ano (31/12/2026): estado, fecho e eficácia das NC abertas em setembro
FECHO_2026 = {
    "NC-SGA-26-01": dict(Estado="Fechada", Data_Fecho="2026-11-25"),
    "NC-SGA-26-02": dict(Prazo="2027-06-30"),   # PPWR: 17/22 famílias em 22/12/2026 — prazo replaneado para as 5 restantes
    "NC-SGA-26-03": dict(Estado="Fechada", Data_Fecho="2026-10-29", Eficacia="Eficaz", Data_Verif_Eficacia="2026-12-15"),
    "NC-SGA-26-04": dict(Estado="Fechada", Data_Fecho="2026-10-20", Eficacia="Eficaz", Data_Verif_Eficacia="2026-12-05"),
    "NC-SGA-26-05": dict(Estado="Fechada", Data_Fecho="2026-10-14", Eficacia="Eficaz", Data_Verif_Eficacia="2026-12-05"),
    "NC-SGA-26-06": dict(Estado="Fechada", Data_Fecho="2026-11-25"),
    "NC-SGA-26-07": dict(Estado="Fechada", Data_Fecho="2026-10-23", Eficacia="Eficaz", Data_Verif_Eficacia="2026-12-15"),
    "NC-SGA-26-08": dict(Estado="Fechada", Data_Fecho="2026-11-10", Eficacia="Eficaz", Data_Verif_Eficacia="2026-12-10"),
    "NC-SGA-26-09": dict(Estado="Fechada", Data_Fecho="2026-12-11", Eficacia="Eficaz", Data_Verif_Eficacia="2026-12-11"),
}
NC_Q4 = [
    ("NC-SGA-26-10", "2026-11-06", "Incidente ambiental", "INC-2026-12", "INJ", "Injetora IM-004", "Não conformidade", "NC Menor", "8.1; 8.2",
     "Fuga de ≈ 8 L de óleo hidráulico da IM-004 para o pavimento, sem tabuleiro de retenção sob a unidade hidráulica.",
     "Ronda do turno 1 de 06/11/2026; fotografias; OT-2026-24.", "Contaminação do solo / rede pluvial se não contida.", "Média",
     "Contenção com o KIT-02, limpeza e resíduo 15 02 02* (OT-2026-24).",
     "Mangueiras hidráulicas das injetoras antigas fora do plano de substituição por horas (só a ISBM-005 tinha plano) e unidade hidráulica sem tabuleiro.",
     "Máquina", "5 Porquês", "", "", "Gerente de Manutenção", "2026-12-15", "Fechada", "2026-12-04", "Eficaz", "2026-12-18", "Sim", 1300, "Operador de Injeção"),
    ("NC-SGA-26-11", "2026-11-19", "Auditoria interna", "CONST-14", "CMP", "Compras / R&D", "Não conformidade", "NC Menor", "8.1; 9.1.1; ISO 14021",
     "Lotes de rPET de jul a out/2026 recebidos com o certificado EN 15343 expirado e contados como reciclado no KPI e nas fichas técnicas.",
     "AUD-2026-02: CERT-03 expirado a 30/06/2026; 6 lotes de rPET sem prova.", "Alegação de conteúdo reciclado sem prova perante clientes.", "Média",
     "Lotes reclassificados como virgem no KPI; clientes afetados informados (2).",
     "O controlo de validade dos certificados não bloqueava a receção (verificação só anual).", "Método", "5 Porquês", "", "PAM-26-25",
     "Responsável de Compras", "2026-12-31", "Fechada", "2026-12-18", "Por avaliar", "2027-03-31", "Não", 400, "Auditor externo"),
]

WHY = {
    "NC-SGA-26-03": [
        ("Porque é que o kit está vazio?", "Porque alguém o usou para conter um derrame (provavelmente óleo ou tinta na zona injeção/serigrafia, em agosto) e o conteúdo não foi reposto.", "Selo partido; absorventes em falta; manchas de óleo junto à IM-006."),
        ("Porque é que não foi reposto?", "Porque quem o usou não avisou o armazém nem o Gestor do SGA e ninguém ficou responsável por repor.", "Nenhum pedido de material nem registo de incidente em ago–set/2026."),
        ("Porque é que não avisou?", "Porque a IT-SGA-01 (derrames) termina na limpeza: não diz que é obrigatório registar o incidente, pedir reposição e voltar a selar.", "IT-SGA-01 rev. 00, passos 1 a 6."),
        ("Porque é que a instrução não prevê o pós-uso?", "Porque foi escrita apenas para a resposta imediata; não existe stock mínimo de kits nem responsável pela reposição.", "Sem artigo 'kit de derrame' no stock do armazém."),
        ("Porque é que a falha não foi detetada mais cedo?", "Porque a ronda só verificava se o kit estava no lugar (não o selo nem o conteúdo) e a formação de derrames ensinou a usar o kit, não o ciclo pós-utilização.", "Checklist RON-06 antigo: 'kit presente? S/N'; plano de formação 2025."),
    ],
    "NC-SGA-26-01": [
        ("Porque não existe avaliação acústica recente?", "Ninguém a pediu após a troca dos compressores.", "Pedido de investimento INV-2026-004."),
        ("Porque ninguém a pediu?", "A alteração foi tratada só como investimento técnico.", "Aprovação pela Direção Industrial sem parecer do SGA."),
        ("Porque não houve parecer do SGA?", "O pedido de alteração não tem checklist ambiental/legal.", "Formulário de investimento em vigor."),
        ("Porque não tem checklist?", "O processo de planeamento de alterações (6.3 da ISO 14001:2026) ainda não foi implementado.", "Lista mestra de documentos sem procedimento de mudanças."),
    ],
    "NC-SGA-26-04": [
        ("Porque estão os bidões no chão?", "As bacias existentes estavam cheias.", "2 bacias com 4 bidões; 3 bidões fora."),
        ("Porque estavam cheias?", "A compra de óleo passou a ser feita em lotes de 5 bidões por causa do desconto.", "Encomenda de 08/2026."),
        ("Porque não se ajustou a contenção?", "O processo de compras não considera a capacidade de armazenagem com retenção.", "Procedimento de compras sem critério de armazenagem."),
    ],
}


def build(out):
    b = Book("RG-SGA-07", "Relatórios de Não Conformidade, Incidentes e Ações Corretivas (RNC)",
             activities="Atividade 6.1 — Tarefa 1 (5 Porquês do kit antipoluição, NC-SGA-26-03) e registo das NC originadas nas Atividades 3.3 e 5.3.",
             clauses="10.2 Não conformidade e ação corretiva (ISO 14001:2026: reagir, controlar e corrigir, lidar com as consequências, avaliar a necessidade de eliminar a causa, rever a eficácia); 8.2; 9.1.2",
             purpose="Registar cada não conformidade e incidente ambiental com evidência objetiva, requisito violado, correção imediata, análise de causa raiz (5 Porquês em formato de tabela), ligação às ações C1/C2 no PAM, prazo, fecho e verificação da eficácia. Inclui histórico de 2025-2026 para análise de tempos de resposta, recorrência e eficácia.",
             links=[("RG-SGA-06 PAM", "ID_PAM_C1 / ID_PAM_C2 ligam as ações de correção e corretivas."),
                    ("RG-SGA-10 Rondas / RG-SGA-14 Auditoria / RG-SGA-04 Legal", "ID_Origem indica o registo que detetou a NC.")])
    b.add_list("Origem", ORIGENS)
    b.add_list("Processo", PROC_CODES)
    b.add_list("TipoRegisto", ["Não conformidade", "Incidente ambiental", "Reclamação"])
    b.add_list("Classificacao", ["NC Maior", "NC Menor", "NC Legal"])
    b.add_list("Severidade", ["Baixa", "Média", "Alta"])
    b.add_list("Cat6M", ["Método", "Máquina", "Material", "Mão de obra", "Medição", "Meio ambiente"])
    b.add_list("Metodo", ["5 Porquês", "Ishikawa", "5 Porquês + Ishikawa", "Análise de árvore de falhas"])
    b.add_list("Estado", ["Aberta", "Em tratamento", "Fechada"])
    b.add_list("Eficacia", ["Por avaliar", "Eficaz", "Não eficaz"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("Funcao", FUNC_NAMES)

    cols = [
        col("ID_NC", 12, desc="Identificador da NC/incidente.", key="PK", dom="NC-SGA-AA-nn"),
        col("Data_Detecao", 11, "date", desc="Data de deteção."),
        col("Origem", 18, dv="Origem", desc="Como foi detetada."),
        col("ID_Origem", 11, desc="ID da ronda, constatação, requisito ou incidente.", key="FK"),
        col("Processo", 8, dv="Processo", desc="Processo.", key="FK → dim processo"),
        col("Local", 20, desc="Local exato."),
        col("Tipo_Registo", 14, dv="TipoRegisto", desc="NC, incidente ou reclamação."),
        col("Classificacao", 10, dv="Classificacao", desc="NC Maior / Menor / Legal."),
        col("Requisito_Violado", 20, desc="Cláusula ISO 14001:2026 e/ou diploma legal."),
        col("Descricao", 42, desc="Descrição da NC."),
        col("Evidencia_Objetiva", 42, desc="Evidência (o que se viu, documento, data)."),
        col("Impacte_Potencial", 26, desc="Consequência ambiental/legal potencial."),
        col("Severidade", 9, dv="Severidade", desc="Severidade."),
        col("Correcao_C1", 34, desc="Correção imediata (controlar e corrigir; lidar com as consequências)."),
        col("Causa_Raiz", 40, desc="Causa raiz identificada."),
        col("Categoria_6M", 11, dv="Cat6M", desc="Categoria Ishikawa."),
        col("Metodo_Analise", 12, dv="Metodo", desc="Método de análise de causa."),
        col("N_Porques", 8, "int", f='=COUNTIF(tbl_5porques[ID_NC],@ID_NC@)', desc="N.º de níveis de 'porquê' registados na tabela 5 Porquês."),
        col("ID_PAM_C1", 10, desc="Ação de correção no PAM.", key="FK → RG-SGA-06", req=False),
        col("ID_PAM_C2", 10, desc="Ação corretiva no PAM.", key="FK → RG-SGA-06", req=False),
        col("Responsavel", 26, dv="Funcao", desc="Responsável."),
        col("Prazo", 11, "date", desc="Prazo de tratamento."),
        col("Estado", 12, dv="Estado", desc="Estado."),
        col("Data_Fecho", 11, "date", desc="Data de fecho.", req=False),
        col("Dias_Aberta", 9, "int", f='=IF(@Data_Fecho@="",DataRef-@Data_Detecao@,@Data_Fecho@-@Data_Detecao@)', desc="Dias entre deteção e fecho (ou até à data de referência)."),
        col("No_Prazo", 9, f='=IF(@Data_Fecho@="",IF(@Prazo@<DataRef,"Atrasada","Em curso"),IF(@Data_Fecho@<=@Prazo@,"Sim","Não"))', desc="Fechada dentro do prazo?"),
        col("Eficacia", 10, dv="Eficacia", desc="Resultado da verificação de eficácia."),
        col("Data_Verif_Eficacia", 11, "date", desc="Data da verificação de eficácia."),
        col("Recorrente", 9, dv="SimNao", desc="Repetição de NC anterior."),
        col("Custo_EUR", 9, "eur", desc="Custo associado (correção + ações)."),
        col("Reportado_Por", 18, desc="Quem detetou."),
        col("Controlo_Qualidade", 20, f=('=IF(AND(@Classificacao@<>"",@Causa_Raiz@=""),"FALTA causa raiz",IF(AND(@Estado@="Fechada",@Eficacia@="Por avaliar",@Data_Verif_Eficacia@<DataRef),"FALTA verificar eficácia",'
                                         'IF(AND(@Estado@<>"Fechada",@ID_PAM_C2@="",@Categoria_6M@<>""),"FALTA ação corretiva (C2)","OK")))'), desc="Regras de qualidade do registo."),
    ]
    names = [c["name"] for c in cols if not c["f"]]
    rows = []
    for t in NC + NC_Q4:
        dd = dict(zip(names, t))
        if dd["ID_NC"] in FECHO_2026:   # estado no fecho do ano (31/12/2026)
            dd.update(FECHO_2026[dd["ID_NC"]])
        for k in ("Data_Detecao", "Prazo", "Data_Fecho", "Data_Verif_Eficacia"):
            dd[k] = d(dd[k])
        for k in ("ID_PAM_C1", "ID_PAM_C2"):
            dd[k] = dd[k] or None
        rows.append(dd)
    b.table("Registo_NC", "tbl_nc", cols, rows, "Registo de não conformidades e incidentes ambientais (1 linha por NC).",
            title="REGISTO DE NÃO CONFORMIDADES E INCIDENTES AMBIENTAIS — PLASTICOM",
            subtitle="Reagir → corrigir (C1) → analisar a causa → ação corretiva (C2) → verificar a eficácia · Dias, prazo e controlo de qualidade calculados",
            cf=[("Estado", {"Aberta": "red", "Em tratamento": "yellow", "Fechada": "green"}),
                ("Classificacao", {"Legal": "purple", "Maior": "red", "Menor": "orange"}),
                ("Eficacia", {"Não eficaz": "red", "Eficaz": "green"}),
                ("Controlo_Qualidade", {"FALTA": "red", "OK": "green"}),
                ("No_Prazo", {"Atrasada": "red", "Não": "orange", "Sim": "green"})],
            row_height=80, freeze_col=1)

    wrows = []
    for nc, levels in WHY.items():
        for n, (q, a, e) in enumerate(levels, 1):
            wrows.append(dict(ID_NC=nc, Nivel=n, Pergunta_Porque=q, Resposta=a, Evidencia=e,
                              E_Causa_Raiz="Sim" if n == len(levels) else "Não"))
    wcols = [col("ID_NC", 12, desc="NC analisada.", key="FK → tbl_nc"), col("Nivel", 6, "int", desc="Nível do porquê (1 a 5)."),
             col("Chave", 16, f='=@ID_NC@&"|"&@Nivel@', desc="Chave técnica (NC|nível)."),
             col("Pergunta_Porque", 40, desc="Pergunta 'Porquê...?'."), col("Resposta", 60, desc="Resposta."),
             col("Evidencia", 40, desc="Evidência que confirma a resposta."), col("E_Causa_Raiz", 10, dv="SimNao", desc="Sim no nível que é a causa raiz.")]
    b.table("Cinco_Porques", "tbl_5porques", wcols, wrows, "Análise dos 5 Porquês em formato longo (1 linha por nível) — permite análise de texto e de padrões de causa.",
            cf=[("E_Causa_Raiz", {"Sim": "red"})], row_height=48)

    # formulário RNC para a NC-SGA-26-03 (Atividade 6.1)
    ws = b.sheet("RNC_Formulario", "Relatório de Não Conformidade (formato de impressão) da NC selecionada em B5 — por defeito NC-SGA-26-03 (Atividade 6.1).", tab_color="7030A0")
    doc_header(ws, "RG-SGA-07", "RELATÓRIO DE NÃO CONFORMIDADE (RNC)", "Mod. RNC-SGA", 6)
    for L, w in zip("ABCDEF", (26, 22, 22, 22, 22, 22)):
        ws.column_dimensions[L].width = w
    form_block(ws, 5, "N.º da NC (escolher)", "NC-SGA-26-03", vw=5, bold_value=True)
    dv = DataValidation(type="list", formula1="=" + b.ref("tbl_nc", "ID_NC"), allow_blank=False)
    ws.add_data_validation(dv)
    dv.add("B5")
    T = lambda f: b.ref("tbl_nc", f)
    m = f'MATCH($B$5,{T("ID_NC")},0)'
    fields = [("Data de deteção", "Data_Detecao"), ("Origem / referência", None), ("Local", "Local"), ("Classificação", "Classificacao"),
              ("Requisito violado", "Requisito_Violado"), ("Descrição", "Descricao"), ("Evidência objetiva", "Evidencia_Objetiva"),
              ("Impacte potencial", "Impacte_Potencial"), ("Correção imediata (C1)", "Correcao_C1")]
    r = 6
    for lab, fld in fields:
        v = (f'=INDEX({T("Origem")},{m})&" — "&INDEX({T("ID_Origem")},{m})' if fld is None else f'=INDEX({T(fld)},{m})')
        c = form_block(ws, r, lab, v, vw=5, height=34 if fld in ("Descricao", "Evidencia_Objetiva", "Correcao_C1") else None)
        if fld == "Data_Detecao":
            c.number_format = "dd/mm/yyyy"
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="INVESTIGAÇÃO — 5 PORQUÊS").font = F_BOLD
    r += 1
    header_row(ws, r, ["Nível", "Pergunta", "", "Resposta", "", "Evidência"])
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
    W = lambda f: b.ref("tbl_5porques", f)
    for n in range(1, 6):
        r += 1
        mm = f'MATCH($B$5&"|{n}",{W("Chave")},0)'
        vals = [f'=IFERROR(IF(INDEX({W("E_Causa_Raiz")},{mm})="Sim","{n} ► causa raiz","{n}"),"")',
                f'=IFERROR(INDEX({W("Pergunta_Porque")},{mm}),"")', None, f'=IFERROR(INDEX({W("Resposta")},{mm}),"")', None,
                f'=IFERROR(INDEX({W("Evidencia")},{mm}),"")']
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=j + 1, value=v)
            c.font, c.alignment, c.border = F_BASE, WRAP_TOP, BORDER
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
        ws.row_dimensions[r].height = 62
    r += 2
    for lab, fld in [("CAUSA RAIZ", "Causa_Raiz"), ("Categoria (6M)", "Categoria_6M"), ("Ação de correção (PAM)", "ID_PAM_C1"),
                     ("Ação corretiva (PAM)", "ID_PAM_C2"), ("Responsável", "Responsavel"), ("Prazo", "Prazo"), ("Estado", "Estado"),
                     ("Verificação de eficácia prevista", "Data_Verif_Eficacia")]:
        c = form_block(ws, r, lab, f'=INDEX({T(fld)},{m})&""' if fld not in ("Prazo", "Data_Verif_Eficacia") else f'=INDEX({T(fld)},{m})', vw=5,
                       height=34 if fld == "Causa_Raiz" else None, bold_value=(fld == "Causa_Raiz"))
        if fld in ("Prazo", "Data_Verif_Eficacia"):
            c.number_format = "dd/mm/yyyy"
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Elaborado: Gestor(a) do SGA/EHS").font = F_BASE
    ws.cell(row=r, column=4, value="Aprovado: Diretor Industrial").font = F_BASE
    ws.page_setup.orientation = "portrait"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToHeight = 0

    # indicadores
    ws = b.sheet("Indicadores_NC", "Indicadores calculados: NC por origem e estado, tempo médio de fecho, eficácia e recorrência.")
    ws["A1"] = "INDICADORES DE NÃO CONFORMIDADES — calculado"
    ws["A1"].font = F_TITLE
    header_row(ws, 3, ["Origem", "Total", "Abertas / em tratamento", "Fechadas", "Dias médios (fechadas)"], widths=[34, 9, 22, 10, 22])
    for k, o in enumerate(ORIGENS):
        r = 4 + k
        ws.cell(row=r, column=1, value=o)
        ws.cell(row=r, column=2, value=f'=COUNTIF({T("Origem")},"{o}")')
        ws.cell(row=r, column=3, value=f'=COUNTIFS({T("Origem")},"{o}",{T("Estado")},"<>Fechada")')
        ws.cell(row=r, column=4, value=f'=COUNTIFS({T("Origem")},"{o}",{T("Estado")},"Fechada")')
        c = ws.cell(row=r, column=5, value=f'=IFERROR(AVERAGEIFS({T("Dias_Aberta")},{T("Origem")},"{o}",{T("Estado")},"Fechada"),"")')
        c.number_format = "0"
    r = 5 + len(ORIGENS)
    for lab, f, fmt in [("Taxa de eficácia (fechadas verificadas)", f'=IFERROR(COUNTIF({T("Eficacia")},"Eficaz")/COUNTIFS({T("Eficacia")},"<>Por avaliar"),"")', "0%"),
                        ("NC recorrentes", f'=COUNTIF({T("Recorrente")},"Sim")', "0"),
                        ("Custo total das NC (€)", f'=SUM({T("Custo_EUR")})', "#,##0 €")]:
        ws.cell(row=r, column=1, value=lab).font = F_BOLD
        c = ws.cell(row=r, column=2, value=f)
        c.number_format = fmt
        r += 1
    X.extra_07(b)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
