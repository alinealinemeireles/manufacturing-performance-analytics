"""RG-SGQ-02 — Mapa de processos (tartaruga), interações, infraestrutura e ambiente para a operação dos processos.
ISO 9001:2026 4.4.1 a)–i), 4.4.2, 7.1.3, 7.1.4. Máquinas, moldes e paragens vêm do dataset do projeto."""
import pandas as pd
from sgqlib import *
from dimsq import *
import qdata as Q

# tartaruga: código → (objetivo, entradas, fornecedores do processo, saídas, clientes do processo, atividades, recursos, competências,
#                      métodos/documentos, KPIs (IDs RG-SGQ-05), riscos/oportunidades (RG-SGA-02), cláusulas)
TARTARUGA = {
    "GES": ("Definir a orientação estratégica, a política e os objetivos e rever o SGQ", "Contexto, partes interessadas, desempenho do SGQ, resultados de auditorias", "QUA; COM; todos",
            "Política, objetivos, decisões e recursos", "Todos os processos", "Planeamento estratégico; revisão pela gestão; afetação de recursos",
            "Sala de reuniões; painel Power BI", "Liderança; pensamento baseado em risco", "POL-SGQ-01; PR-SGQ-01", "KPI-Q-16; KPI-Q-14", "R24; R25; O3", "4; 5; 6.2; 9.3"),
    "QUA": ("Manter e melhorar o SGQ e a sua eficácia", "Requisitos ISO 9001:2026, NC, reclamações, KPI", "Todos", "Programa de auditoria, CAPA, relatórios de desempenho",
            "GES; todos", "Auditorias; gestão de NC e CAPA; análise de dados; melhoria", "Software de CAPA; data warehouse", "ISO 19011:2026; 8D; estatística",
            "PR-SGQ-05; PR-SGQ-06; PR-SGQ-07", "KPI-Q-10; KPI-Q-11; KPI-Q-19", "R20; O11", "6.1; 9.1.3; 9.2; 10"),
    "COM": ("Converter necessidades do cliente em encomendas exequíveis e manter a satisfação", "Pedidos de cotação, encomendas, reclamações, feedback", "Clientes; RD; PCP",
            "Propostas, encomendas revistas, acordos de qualidade, respostas a reclamações", "Clientes; PCP; RD", "Revisão de requisitos; gestão de encomendas; inquérito de satisfação; tratamento de reclamações",
            "ERP; CRM", "Conhecimento técnico de embalagem; negociação", "PR-SGQ-08; PR-SGQ-09", "KPI-Q-04; KPI-Q-06; KPI-Q-14; KPI-Q-15; KPI-Q-20", "R21; O5", "5.1.2; 8.2; 8.5.3; 8.5.5; 9.1.2"),
    "RD": ("Projetar produtos e moldes que cumpram requisitos funcionais, legais e de fabrico", "Briefing do cliente, requisitos legais, lições de projetos anteriores", "COM; clientes; fornecedores de moldes",
           "Desenhos, especificações, planos de controlo iniciais, dossiers de conformidade", "PCP; LAB; CMP; clientes", "Planeamento; revisões; verificação; validação; controlo de alterações de design",
           "CAD/CAE; protótipos; laboratório", "Engenharia de embalagem; DFMEA", "PR-SGQ-10", "KPI-Q-02", "R12; R33; O5", "8.3"),
    "PCP": ("Planear e sequenciar a produção para cumprir prazos com qualidade", "Encomendas, capacidade, stock de MP", "COM; CMP; MAN", "Plano de produção, ordens de fabrico",
            "INJ; SOP; SER; HFS; EXP", "Planeamento de capacidade; sequenciamento; gestão de trocas de molde", "ERP; MES", "Planeamento; TOC", "PR-SGQ-11", "KPI-Q-07; KPI-Q-20", "R15; O9; O14", "8.1; 8.5.1"),
    "CMP": ("Adquirir materiais e serviços conformes a fornecedores avaliados", "Necessidades de MP, especificações", "PCP; RD; LAB", "Encomendas a fornecedores, avaliações, SCAR",
            "REC; fornecedores", "Seleção; avaliação; reavaliação; comunicação de requisitos", "ERP", "Gestão de fornecedores", "PR-SGQ-12", "KPI-Q-08; KPI-Q-09", "R13; R14; R36; O8", "8.4"),
    "REC": ("Receber, inspecionar e armazenar MP preservando a conformidade", "Lotes de MP, certificados de análise", "Fornecedores; CMP", "Lotes aceites/rejeitados, MP identificada",
            "INJ; SOP; SER; HFS", "Inspeção de receção; quarentena; armazenagem FIFO", "Laboratório de receção; armazém", "Amostragem; ensaios de MP", "PC-MP-01; IT-REC-01", "KPI-Q-08", "R13; R15", "8.4.2; 8.5.2; 8.5.4"),
    "INJ": ("Injetar tampas e potes conformes", "MP, molde, ordem de fabrico, parâmetros validados", "REC; PCP; MAN", "Tampas/potes e registos de controlo",
            "SER; HFS; EXP; LAB", "Setup; arranque; controlo em processo; autocontrolo", "IM-001 a IM-008; 16 moldes", "Operação de injeção; autocontrolo", "PC-INJ-01; IT-INJ-01..04", "KPI-Q-01; KPI-Q-07", "R4; R5; R10; O1", "8.5.1; 8.5.2"),
    "SOP": ("Soprar frascos conformes", "Preformas/MP, molde, parâmetros", "REC; PCP; MAN", "Frascos e registos de controlo", "SER; HFS; EXP; LAB",
            "Setup; condicionamento de preformas; controlo em processo", "ISBM-001 a ISBM-010; 34 moldes", "Operação ISBM; autocontrolo", "PC-SOP-01; IT-SOP-01..03", "KPI-Q-01; KPI-Q-07", "R1; R2; R3; R11", "8.5.1; 8.5.2"),
    "SER": ("Decorar por serigrafia com registo, cor e aderência conformes", "Frascos, artwork aprovado, tintas", "SOP; COM; CMP", "Frascos decorados e registos", "EXP; LAB",
            "Preparação de ecrãs; impressão; cura; controlo de aderência", "SS-001, SS-002; 48 ferramentas", "Serigrafia; colorimetria", "PC-DEC-01; IT-SER-01..03", "KPI-Q-01", "R6; R7", "8.5.1; 8.5.3"),
    "HFS": ("Decorar por hot foil com transferência e aderência conformes", "Frascos, foil, artwork", "SOP; CMP", "Frascos decorados", "EXP; LAB", "Setup; estampagem; controlo visual",
            "HF-001, HF-002", "Hot foil", "PC-DEC-01; IT-HFS-01", "KPI-Q-01", "R8", "8.5.1"),
    "LAB": ("Verificar e libertar produto conforme; controlar saídas não conformes", "Amostras, planos de controlo, especificações", "INJ; SOP; SER; HFS; REC",
            "Decisões de lote, certificados, RNC", "EXP; clientes; QUA", "Inspeção por atributos (ISO 2859-1) e variáveis (ISO 3951); ensaios; libertação; segregação",
            "Laboratório; 60 equipamentos de medição", "Inspeção; estatística; metrologia", "PR-SGQ-13; PR-SGQ-14; PC-*", "KPI-Q-02; KPI-Q-12; KPI-Q-13", "R16; R17; R18", "8.6; 8.7; 9.1.1"),
    "EXP": ("Embalar, armazenar e expedir preservando o produto e sem trocas", "Produto libertado, ordens de expedição", "LAB; PCP", "Paletes etiquetadas e guias", "Clientes; transportadores",
            "Paletização; etiquetagem; verificação de carga; expedição", "Armazém; leitores de código de barras", "Logística; rastreabilidade", "IT-EXP-01..02", "KPI-Q-05; KPI-Q-20", "R21", "8.5.2; 8.5.4; 8.5.5"),
    "MAN": ("Manter máquinas e moldes disponíveis e capazes", "Planos de manutenção, avarias, contadores de ciclos", "Produção; fornecedores de peças", "Equipamento disponível, ordens de trabalho",
            "INJ; SOP; SER; HFS", "Manutenção preventiva, corretiva e de moldes", "Oficina; ferramentaria; CMMS", "Mecânica; eletricidade; hidráulica", "PR-SGQ-15", "KPI-Q-07", "R2; R3; R7; O2", "7.1.3"),
    "MET": ("Assegurar resultados de medição válidos e fiáveis", "Inventário de equipamentos, requisitos de medição", "LAB; laboratórios externos", "Equipamento confirmado, certificados, estudos MSA",
            "LAB; produção", "Calibração; verificação; MSA; avaliação de fora de tolerância", "Padrões de referência", "Metrologia; ISO 10012:2026", "PR-SGQ-16", "KPI-Q-17", "R17", "7.1.5"),
    "RH": ("Assegurar pessoas competentes e conscientes", "Necessidades de competência, admissões", "Todos", "Pessoas qualificadas, registos de formação", "Todos",
           "Recrutamento; integração; formação; avaliação da eficácia", "Plataforma de formação", "Gestão de competências (ISO 10015)", "PR-SGQ-17", "KPI-Q-18", "R23; R9", "7.1.2; 7.2; 7.3"),
    "TI": ("Disponibilizar sistemas e dados íntegros", "Necessidades de informação", "Todos", "ERP, MES, data warehouse, cópias de segurança", "Todos",
           "Gestão de sistemas; cópias de segurança; controlo de acessos; validação de software e folhas de cálculo", "Servidores; cloud", "TI; engenharia de dados", "PR-SGQ-18", "—", "R19; R26; R27; O3", "7.1.3; 7.1.6; 7.5.3"),
    "DOC": ("Controlar a informação documentada do SGQ", "Documentos novos e alterados, documentos externos", "Todos", "Documentos aprovados e distribuídos, registos protegidos", "Todos",
            "Elaboração; aprovação; distribuição; arquivo; eliminação", "Repositório controlado", "Controlo documental", "PR-SGQ-02", "—", "", "7.5"),
}

INTERACOES = [
    ("GES", "QUA", "Política, objetivos, recursos"), ("QUA", "GES", "Desempenho do SGQ, auditorias, CAPA"), ("COM", "RD", "Briefing e requisitos do cliente"),
    ("COM", "PCP", "Encomendas revistas"), ("RD", "PCP", "Especificações e plano de controlo inicial"), ("RD", "CMP", "Especificação de MP e moldes"),
    ("PCP", "CMP", "Necessidades de MP"), ("CMP", "REC", "Encomendas a fornecedores"), ("REC", "INJ", "MP aceite"), ("REC", "SOP", "MP aceite"),
    ("PCP", "INJ", "Ordens de fabrico"), ("PCP", "SOP", "Ordens de fabrico"), ("PCP", "SER", "Ordens de fabrico"), ("PCP", "HFS", "Ordens de fabrico"),
    ("SOP", "SER", "Frascos para decorar"), ("SOP", "HFS", "Frascos para decorar"), ("INJ", "LAB", "Amostras e registos"), ("SOP", "LAB", "Amostras e registos"),
    ("SER", "LAB", "Amostras"), ("HFS", "LAB", "Amostras"), ("LAB", "EXP", "Lotes libertados"), ("EXP", "COM", "Entregas / guias"), ("COM", "QUA", "Reclamações"),
    ("LAB", "QUA", "RNC e dados de inspeção"), ("REC", "CMP", "Resultados de receção / SCAR"), ("MAN", "INJ", "Equipamento disponível"), ("MAN", "SOP", "Equipamento disponível"),
    ("MAN", "SER", "Equipamento disponível"), ("MAN", "HFS", "Equipamento disponível"), ("MET", "LAB", "Equipamento calibrado e MSA"), ("RH", "INJ", "Operadores qualificados"),
    ("RH", "SOP", "Operadores qualificados"), ("RH", "LAB", "Inspetores qualificados"), ("TI", "QUA", "Dados e painéis"), ("DOC", "INJ", "Instruções e planos de controlo"),
    ("DOC", "LAB", "Planos de controlo e normas"), ("QUA", "COM", "Respostas 8D ao cliente"), ("CMP", "QUA", "Desempenho de fornecedores"),
]

AMBIENTE = [
    ("AMB-01", "Físico", "Temperatura da nave de sopro", "SOP", "18–28 °C (preformas PET: condicionamento a 20 ± 3 °C)", "Termo-higrómetro TH-01, registo contínuo", "Diária (verão: por turno)",
     "Acima de 30 °C a variação de espessura aumenta; atuar no chiller e ajustar perfil de aquecimento", "PESQ-06", GMAN),
    ("AMB-02", "Físico", "Humidade relativa no armazém de resinas higroscópicas (PET, PETG)", "REC", "HR ≤ 60%; secagem antes do uso (humidade ≤ 50 ppm no PET)", "Termo-higrómetro TH-02; Karl Fischer por lote", "Por lote",
     "Resina húmida causa bolhas e perda de transparência; secar e reensaiar", "PESQ-05", LOG),
    ("AMB-03", "Físico", "Iluminação nos postos de inspeção visual", "LAB", "Cabine D65; ≥ 1.000 lux no posto de inspeção", "Luxímetro; verificação da cabine D65", "Semestral",
     "Iluminação insuficiente reduz a deteção de pontos negros e manchas", "SWTQ-F02", GQ),
    ("AMB-04", "Físico", "Higiene da zona de embalagem das linhas alimentar e farmacêutica", "EXP", "Zona segregada, sacos fechados, sem madeira nem vidro; limpeza diária registada", "Checklist de higiene HIG-01", "Diária",
     "Contaminação por material estranho (reclamação crítica)", "PESQ-02", GPROD),
    ("AMB-05", "Físico", "Ruído e circulação de ar na serigrafia (solventes)", "SER", "Exaustão ligada; VLE de exposição cumprido (RG-SGA-21)", "Medição de exposição (SGA)", "Anual",
     "Desconforto e erro humano; articulação com o SGA/SST", "", "Gestor do SGA / EHS (Responsável Ambiental)"),
    ("AMB-06", "Psicológico", "Fadiga e pressão por meta no turno 2 (passagem de turno)", "PCP", "Pausas cumpridas; passagem de turno estruturada (checklist)", "Taxa de rejeição por turno; inquérito de clima", "Mensal",
     "Prémio de defeito no turno 2 (R9)", "SWTQ-W02", GPROD),
    ("AMB-07", "Social", "Não culpabilização no relato de defeitos e quase-falhas", "QUA", "Relato livre; NC tratadas como falha do sistema (cultura justa)", "Inquérito de cultura da qualidade (RG-SGQ-03)", "Semestral",
     "Sem relato não há contenção precoce", "SWTQ-W02", GQ),
    ("AMB-08", "Social", "Integração de operadores temporários no pico", "RH", "Acolhimento, tutor designado e validação no posto antes de trabalhar sozinho", "Matriz de competências (RG-SGQ-07)", "Por admissão",
     "Operadores sem validação nas características críticas", "SWTQ-W05", RH_),
]


def machines():
    prof = Q.rd("dim_machine_profile.csv", Q.DIM)
    mach = Q.rd("dim_machine.csv")
    mold = Q.rd("dim_mold.csv")
    d = Q.periodo(Q.rd("fact_downtime_processed.csv"), "Date")
    unpl = d[d["UnplannedFailure"]].groupby("MachineId").agg(Horas_Paragem_Nao_Planeada=("EffectiveDowntimeMin", lambda s: round(s.sum() / 60, 1)),
                                                             N_Avarias=("DowntimeDurationMin", "size"))
    prev = d[d["IsPreventiveMaintenance"]].groupby("MachineId").size().rename("N_Preventivas")
    p = Q.production()
    run = p.groupby("MachineId").agg(Horas_Marcha=("RunTimeHours", lambda s: round(s.sum(), 1)), OEE_Medio=("OEE", "mean"),
                                     Produzido=("ProducedQty", "sum"), Rejeitado=("RejectedQty", "sum"))
    m = mach.merge(prof, on="MachineId").merge(mold.groupby("MachineId").MoldId.count().rename("N_Moldes"), on="MachineId", how="left")
    m = m.merge(unpl, on="MachineId", how="left").merge(prev, on="MachineId", how="left").merge(run, on="MachineId", how="left")
    rows = []
    for _, r in m.sort_values("MachineId").iterrows():
        rows.append(dict(ID_Maquina=r.MachineId, Processo=Q.T_PROC[r.Process], Ano_Instalacao=int(r.InstallationYear),
                         Detecao_Automatica="Sim" if r.HasAutomatedDefectDetection else "Não", N_Moldes=int(r.N_Moldes or 0),
                         Horas_Marcha=float(r.Horas_Marcha), N_Avarias=int(r.N_Avarias), Horas_Paragem_Nao_Planeada=float(r.Horas_Paragem_Nao_Planeada),
                         N_Preventivas=int(r.N_Preventivas), OEE_Medio=round(float(r.OEE_Medio), 4), Produzido=int(r.Produzido), Rejeitado=int(r.Rejeitado),
                         Qualificacao="IQ/OQ/PQ concluída (2026)" if r.InstallationYear >= 2026 else "Histórica (antes do SGQ 2026)"))
    return rows


def build(out):
    b = Book("RG-SGQ-02", "Mapa de Processos, Interações, Infraestrutura e Ambiente",
             activities="Caracterizar cada processo do SGQ (entradas, saídas, sequência, interação, critérios, KPI, recursos, responsáveis, riscos) e a infraestrutura e o ambiente de que dependem.",
             clauses="4.4.1 a)–i) processos do SGQ; 4.4.2 informação documentada disponível; 7.1.3 Infraestrutura; 7.1.4 Ambiente para a operação dos processos (fatores sociais, psicológicos, físicos)",
             purpose="Mostrar a abordagem por processos da Plasticom: 18 processos com dono, KPI e riscos, a matriz de interações e o estado da infraestrutura produtiva (22 máquinas do dataset com horas de marcha, avarias e OEE) e das condições ambientais que afetam a conformidade do produto.",
             links=[("RG-SGQ-05 KPI", "KPIs de cada processo (KPI-Q-nn)."), ("RG-SGA-02", "Riscos e oportunidades (R-nn / O-nn)."),
                    ("RG-SGQ-08 Lista mestra", "Documentos citados em Metodos_Documentos (PR-SGQ-nn, PC-*, IT-*).")],
             guidance=[("ISO/TC 176 APG — Processes / process approach", "Cada processo tem dono, critérios e KPI e é auditado pela sequência entrada → atividade → saída → cliente (diagrama de tartaruga)."),
                       ("Academy — cap. 40/155 (Tartaruga, SIPOC)", "Colunas da tartaruga: com quê (recursos), com quem (competência), como (métodos), quanto (KPI), entradas e saídas."),
                       ("iso9001help.co.uk — Process definition", "Descrição de processo com objetivo, sequência e medidas de desempenho ligadas aos objetivos.")])
    b.add_list("Processo", PROC_CODES)
    b.add_list("TipoProc", ["Gestão", "Realização", "Suporte"])
    b.add_list("Funcao", FUNC_NAMES + ["Gestor do SGA / EHS (Responsável Ambiental)"])
    b.add_list("FatorAmb", ["Físico", "Psicológico", "Social"])
    b.add_list("SimNao", ["Sim", "Não"])

    cols = [
        col("Codigo", 7, desc="Código do processo.", key="PK", dv="Processo"), col("Processo", 34, desc="Nome do processo."),
        col("Tipo", 10, dv="TipoProc", desc="Gestão / realização / suporte."), col("Dono", 24, dv="Funcao", desc="Dono do processo (4.4.1 f)."),
        col("Objetivo", 36, desc="Finalidade / resultado pretendido."), col("Entradas", 34, desc="Entradas requeridas (4.4.1 b)."),
        col("Fornecedores_Processo", 16, desc="De onde vêm as entradas (processos ou partes externas)."), col("Saidas", 34, desc="Saídas esperadas (4.4.1 b)."),
        col("Clientes_Processo", 16, desc="Quem recebe as saídas."), col("Atividades", 40, desc="Atividades principais (sequência)."),
        col("Recursos", 26, desc="Com quê (4.4.1 e)."), col("Competencias", 24, desc="Com quem (7.2)."), col("Metodos_Documentos", 24, desc="Como: documentos (4.4.2).", key="FK → RG-SGQ-08"),
        col("KPIs", 22, desc="Quanto: indicadores (4.4.1 d).", key="FK → RG-SGQ-05"), col("Riscos_Oportunidades", 16, desc="4.4.1 g).", key="FK → RG-SGA-02", req=False),
        col("Clausulas", 16, desc="Cláusulas ISO 9001:2026."),
        col("N_Entradas_Matriz", 9, "int", f='=COUNTIF(tbl_interacoes[Para],@Codigo@)', desc="N.º de interações recebidas (matriz)."),
        col("N_Saidas_Matriz", 9, "int", f='=COUNTIF(tbl_interacoes[De],@Codigo@)', desc="N.º de interações enviadas (matriz)."),
        col("Completo", 10, f='=IF(OR(@Dono@="",@KPIs@="",@Metodos_Documentos@=""),"FALTA",IF(@N_Entradas_Matriz@+@N_Saidas_Matriz@=0,"Isolado","OK"))',
            desc="Controlo: dono, KPI e documento definidos e processo ligado à matriz."),
    ]
    rows = []
    for code, name, tipo, dono, _ in PROCESSOS:
        t = TARTARUGA[code]
        rows.append(dict(zip(input_names(cols), (code, name, tipo, dono) + t)))
    b.table("Mapa_Processos", "tbl_processos", cols, rows, "Caracterização dos processos do SGQ (diagrama de tartaruga), 4.4.1.",
            title="MAPA DE PROCESSOS DO SGQ — TARTARUGA (4.4.1)",
            subtitle="18 processos (3 gestão, 10 realização, 5 suporte) · Colunas cinzentas calculadas a partir da matriz de interações", tab_color="1F4E5F",
            cf=[("Tipo", {"Gestão": "purple", "Realização": "blue", "Suporte": "gray"}), ("Completo", {"FALTA": "red", "Isolado": "orange", "OK": "green"})], row_height=72, freeze_col=2)

    icols = [col("ID_Interacao", 8, f='="INT-"&TEXT(ROW()-1,"00")', desc="ID sequencial."),
             col("De", 7, dv="Processo", desc="Processo de origem.", key="FK → tbl_processos"), col("Para", 7, dv="Processo", desc="Processo de destino.", key="FK → tbl_processos"),
             col("O_que_Flui", 40, desc="Informação ou material que passa (sequência e interação 4.4.1 c).")]
    b.table("Interacoes", "tbl_interacoes", icols, [dict(De=a, Para=c, O_que_Flui=w) for a, c, w in INTERACOES],
            "Interações entre processos (uma linha por fluxo).", row_height=18)

    ws = b.sheet("Matriz_Interacao", "Matriz de-para calculada a partir de tbl_interacoes (n.º de fluxos entre processos).")
    title(ws, "MATRIZ DE INTERAÇÃO ENTRE PROCESSOS (4.4.1 c) — calculada", "Linha = processo que envia; coluna = processo que recebe; valor = n.º de fluxos em tbl_interacoes")
    ws.column_dimensions["A"].width = 8
    cell(ws, 4, 1, "De \\ Para", bold=True, fill=FILL_BAND)
    for j, p in enumerate(PROC_CODES):
        c = cell(ws, 4, 2 + j, p, bold=True, fill=FILL_BAND)
        c.alignment = CENTER
        ws.column_dimensions[get_column_letter(2 + j)].width = 5.5
    for i, p in enumerate(PROC_CODES):
        cell(ws, 5 + i, 1, p, bold=True, fill=FILL_BAND)
        for j, q in enumerate(PROC_CODES):
            c = cell(ws, 5 + i, 2 + j, f'=IF(COUNTIFS(tbl_interacoes[De],$A{5 + i},tbl_interacoes[Para],{get_column_letter(2 + j)}$4)=0,"",COUNTIFS(tbl_interacoes[De],$A{5 + i},tbl_interacoes[Para],{get_column_letter(2 + j)}$4))')
            c.alignment = CENTER
    last = get_column_letter(1 + len(PROC_CODES))
    ws.conditional_formatting.add(f"B5:{last}{4 + len(PROC_CODES)}", FormulaRule(formula=["B5<>\"\""], fill=PatternFill("solid", fgColor="CFE2F3")))

    mcols = [col("ID_Maquina", 10, desc="Máquina (ID do dataset).", key="PK"), col("Processo", 7, dv="Processo", desc="Processo.", key="FK → dim processo"),
             col("Ano_Instalacao", 9, "int", desc="Ano de instalação."), col("Idade_Anos", 7, "int", f='=YEAR(DataRef)-@Ano_Instalacao@', desc="Idade à data de referência."),
             col("Detecao_Automatica", 10, dv="SimNao", desc="Tem deteção automática de defeitos (visão/sensores)?"), col("N_Moldes", 7, "int", desc="Moldes/ferramentas associados."),
             col("Horas_Marcha", 10, "num1", desc="Horas de marcha no período (dataset)."), col("N_Avarias", 8, "int", desc="Paragens não planeadas (avarias) no período."),
             col("Horas_Paragem_Nao_Planeada", 11, "num1", desc="Horas de paragem não planeada."), col("N_Preventivas", 9, "int", desc="Intervenções preventivas registadas."),
             col("MTBF_h", 8, "num1", f='=IFERROR(@Horas_Marcha@/@N_Avarias@,"")', desc="Tempo médio entre avarias (h)."),
             col("MTTR_h", 8, "num", f='=IFERROR(@Horas_Paragem_Nao_Planeada@/@N_Avarias@,"")', desc="Tempo médio de reparação (h)."),
             col("OEE_Medio", 8, "pct1", desc="OEE médio das ordens (dataset)."), col("Produzido", 11, "num0", desc="Unidades produzidas."), col("Rejeitado", 9, "num0", desc="Unidades rejeitadas."),
             col("Taxa_Rejeicao", 8, "pct1", f='=IFERROR(@Rejeitado@/@Produzido@,"")', desc="Rejeitado ÷ produzido."),
             col("Qualificacao", 22, desc="Estado de qualificação do equipamento."),
             col("Criticidade", 10, f='=IF(@ID_Maquina@="","",IF(OR(@MTBF_h@<12,@Taxa_Rejeicao@>0.03),"Alta",IF(OR(@Idade_Anos@>=12,@Detecao_Automatica@="Não"),"Média","Baixa")))',
                 desc="Alta: MTBF < 12 h ou rejeição > 3%; Média: ≥ 12 anos ou sem deteção automática.")]
    b.table("Infraestrutura_Maquinas", "tbl_maquinas", mcols, machines(),
            "Infraestrutura produtiva (7.1.3): 22 máquinas com desempenho de manutenção e qualidade calculado a partir do dataset.",
            title="INFRAESTRUTURA — MÁQUINAS DE PRODUÇÃO (7.1.3)",
            subtitle=f"Dados do dataset {PER_INI} a {PER_FIM} · MTBF, MTTR, taxa de rejeição e criticidade calculados · Máquinas de 2026 em arranque",
            cf=[("Criticidade", {"Alta": "red", "Média": "yellow", "Baixa": "green"}), ("Detecao_Automatica", {"Não": "orange"})], row_height=18)

    acols = [col("ID_Fator", 8, key="PK", desc="Fator do ambiente."), col("Tipo_Fator", 10, dv="FatorAmb", desc="Social, psicológico ou físico (7.1.4 Nota)."),
             col("Fator", 34, desc="Fator."), col("Processo", 7, dv="Processo", desc="Processo afetado."), col("Criterio", 40, desc="Condição requerida."),
             col("Monitorizacao", 30, desc="Como é verificado."), col("Frequencia", 14, desc="Frequência."), col("Efeito_Produto", 40, desc="Efeito na conformidade se falhar."),
             col("ID_Contexto", 10, desc="Fator de contexto (RG-SGQ-01 tbl_pestel / tbl_swot).", key="FK → RG-SGQ-01", req=False), col("Responsavel", 24, dv="Funcao", desc="Responsável.")]
    arows = rows_from(input_names(acols), AMBIENTE)
    for r in arows:
        r["ID_Contexto"] = r["ID_Contexto"] or None
    b.table("Ambiente_Operacao", "tbl_ambiente", acols, arows,
            "Ambiente necessário para a operação dos processos (7.1.4): fatores físicos, psicológicos e sociais.",
            title="AMBIENTE PARA A OPERAÇÃO DOS PROCESSOS (7.1.4)",
            subtitle="ISO 9001:2026: fatores sociais, psicológicos e físicos — alguns influenciados pela cultura da qualidade e pelo comportamento ético",
            cf=[("Tipo_Fator", {"Físico": "blue", "Psicológico": "purple", "Social": "yellow"})], row_height=45)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
