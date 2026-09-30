"""RG-SGQ-11 — Design e desenvolvimento de produtos (ISO 9001:2026 8.3.1–8.3.6).
Os 6 projetos que lançaram os 17 SKU alimentares, farmacêuticos e de potes em jul/2026 (dataset). O FPY de lançamento por família
é calculado a partir das decisões de lote do dataset (jul–dez/2026)."""
import datetime as dt
from sgqlib import *
from dimsq import *
import qdata as Q

PROJ = [
    # ID, título, SKUs, família (prefixo), clientes, molde/máquina, a) natureza e complexidade, d) responsável, f) interfaces, g) participação do cliente, h) requisitos p/ provisão, i) nível de controlo esperado, início, fim planeado, fim real, estado
    ("DD-26-01", "Frascos alimentares 500/1 000 ml (HDPE-FG, PP-FG)", "FA-030-HDPE-FG-1000; FA-030-PP-FG-1000; FA-031-HDPE-FG-500; FA-031-PP-FG-500", "FA-03", "CUST-015; CUST-016",
     "M-SOP-030/031 · ISBM-009", "Média: novo material de grau alimentar e requisitos de migração", RD_, "R&D ↔ ferramentaria ↔ laboratório ↔ cliente", "Aprovação de desenho e de amostras T1; ensaio no enchimento",
     "Plano de controlo com migração por lote; BPF (IT-SOP-03)", "Alto (alimentar)", "2026-01-12", "2026-06-30", "2026-07-06", "Fechado"),
    ("DD-26-02", "Frascos farmacêuticos 100/250 ml (PP-PG, PET-PG)", "FP-032-PP-PG-100; FP-032-PET-PG-100; FP-033-PP-PG-250; FP-033-PET-PG-250", "FP-03", "CUST-017; CUST-018",
     "M-SOP-032/033 · ISBM-010", "Alta: grau farmacêutico, rastreabilidade e notificação de alterações", RD_, "R&D ↔ qualidade ↔ cliente (auditoria)", "Acordo de qualidade; aprovação de cada etapa",
     "Rastreabilidade ao lote de resina; certificado por lote", "Muito alto (farma)", "2026-01-12", "2026-06-30", "2026-07-07", "Fechado"),
    ("DD-26-03", "Potes injetados 50/100 ml (PP, PP-PG)", "PT-010-PP-050; PT-010-PP-PG-050; PT-011-PP-100; PT-011-PP-PG-100", "PT-01", "CUST-015; CUST-017",
     "M-INJ-010/011 · IM-007", "Média: novo formato (pote) na injeção", RD_, "R&D ↔ injeção ↔ laboratório", "Aprovação de amostras", "Plano de controlo de potes (PC-INJ-01 rev. 05)", "Alto",
     "2026-02-02", "2026-06-30", "2026-07-06", "Fechado"),
    ("DD-26-04", "Tampa farmacêutica com anel de inviolabilidade 24/410 (PP-PG)", "TE-012-PP-PG-24410", "TE-012", "CUST-017; CUST-018",
     "M-INJ-012 · IM-008", "Alta: função de segurança (evidência de violação)", RD_, "R&D ↔ ferramentaria externa ↔ laboratório", "Validação do anel pelo cliente",
     "Ensaio do anel por lote (LAB-M-12); característica crítica S = 10", "Muito alto (farma)", "2026-01-19", "2026-06-30", "2026-07-06", "Fechado"),
    ("DD-26-05", "Tampa de pote de encaixe 70 mm (PP, PP-PG)", "TP-013-PP-070; TP-013-PP-PG-070", "TP-013", "CUST-015; CUST-017",
     "M-INJ-013 · IM-008", "Baixa: geometria simples de encaixe", RD_, "R&D ↔ injeção", "Aprovação de amostras", "Ensaio de força de remoção (não binário)", "Médio",
     "2026-02-16", "2026-06-30", "2026-07-07", "Fechado"),
    ("DD-26-06", "Tampa de rosca alimentar 28/410 (HDPE-FG, PP-FG)", "TA-014-HDPE-FG-28410; TA-014-PP-FG-28410", "TA-014", "CUST-015; CUST-016",
     "M-INJ-014 · IM-008", "Média: material de grau alimentar; vedação", RD_, "R&D ↔ injeção ↔ laboratório", "Aprovação de amostras; ensaio de vedação no cliente",
     "Plano de controlo de vedação e rosca", "Alto (alimentar)", "2026-02-16", "2026-06-30", "2026-07-06", "Fechado"),
]

ENTRADAS = {
    "a": ("Requisitos funcionais e de desempenho", {"DD-26-01": "Volume 500/1 000 ml; estanquidade; queda 1,2 m cheio; compatível com enchimento a quente até 60 °C",
                                                    "DD-26-02": "Volume 100/250 ml; estanquidade; barreira; compatível com esterilização por irradiação (PET-PG)",
                                                    "DD-26-03": "Volume 50/100 ml; empilhamento; fecho com TP-013", "DD-26-04": "Anel separa na 1.ª abertura com força 15–35 N; não separa no transporte",
                                                    "DD-26-05": "Força de remoção 20–40 N; vedação ao pó", "DD-26-06": "Binário de abertura 8–16 N·cm; vedação; retenção de binário"}),
    "b": ("Informação de designs anteriores semelhantes", {"DD-26-01": "Família FR-007 (HDPE); lições de espessura da ISBM-003", "DD-26-02": "FR-011/012-PET-400 (curva de aprendizagem, R12)",
                                                          "DD-26-03": "Nenhum pote anterior — risco maior", "DD-26-04": "Tampas TR 24/410 (rosca) — sem anel anterior",
                                                          "DD-26-05": "Nenhuma tampa de encaixe anterior", "DD-26-06": "TR-001 28/410 (back-off e binário em reclamações)"}),
    "c": ("Requisitos legais e regulamentares", {"DD-26-01": "Reg. 1935/2004; Reg. 10/2011; BPF 2023/2006; PPWR", "DD-26-02": "Ph. Eur. 3.2.2; acordo de qualidade; PPWR",
                                                "DD-26-03": "Reg. 10/2011 (versão alimentar); PPWR", "DD-26-04": "21 CFR 211.132 (referência do cliente); Ph. Eur.",
                                                "DD-26-05": "Reg. 10/2011; PPWR", "DD-26-06": "Reg. 1935/2004; Reg. 10/2011; PPWR"}),
    "d": ("Normas e códigos de prática assumidos", {"DD-26-01": "EN 1186-3:2022; ASTM D2463-23", "DD-26-02": "ISO 15378 (referência); ASTM D2463-23",
                                                   "DD-26-03": "ASTM D642", "DD-26-04": "Método interno LAB-M-12", "DD-26-05": "Método interno de força de remoção", "DD-26-06": "ASTM D2063 (binário)"}),
    "e": ("Consequências potenciais de falha", {"DD-26-01": "Contaminação de alimentos; recolha", "DD-26-02": "Medicamento comprometido; recolha e perda do cliente",
                                               "DD-26-03": "Fuga do conteúdo", "DD-26-04": "Violação não evidente: risco para o doente (S = 10)", "DD-26-05": "Abertura acidental", "DD-26-06": "Fuga; contaminação"}),
}

ETAPAS = [
    ("G0", "Revisão de conceito e entradas", "Revisão (8.3.4 b)", 0),
    ("G1", "Revisão de design (desenho 3D, simulação, DFMEA)", "Revisão (8.3.4 b)", 30),
    ("G2", "Verificação: amostras T1 — dimensional, peso, ensaios de laboratório", "Verificação (8.3.4 c)", 85),
    ("G3", "Validação: ensaio no enchimento do cliente e ensaios de uso", "Validação (8.3.4 d)", 130),
    ("G4", "Libertação para série e safe launch (6 semanas)", "Revisão final / libertação", 170),
    ("G5", "Fecho do projeto: auditoria da configuração pós-lançamento e lições aprendidas", "Revisão final / libertação", 290),
]
RESULT = {("DD-26-04", "G2"): ("Aprovado com ações", "Força de rotura das pontes acima de 35 N em 2 cavidades; retificar pontes", "DC-26-02"),
          ("DD-26-02", "G2"): ("Aprovado com ações", "FP-032: queda falhou em 1/20 frascos — aumentar espessura na base", "DC-26-03"),
          ("DD-26-05", "G2"): ("Aprovado com ações", "Plano de controlo herdou 'binário' e 'rosca' de tampa de rosca — rever características", "DC-26-01"),
          ("DD-26-05", "G5"): ("Aprovado com ações", "Validação da estanquidade com o cliente sem registo (CON-Q-26-13 → CAPA-Q-26-14); registada em 10/12/2026", "DC-26-01"),
          ("DD-26-06", "G3"): ("Aprovado com ações", "Vedação marginal com o vedante do cliente; ajustar tolerância do lábio", "DC-26-04")}

SAIDAS = [
    ("DD-26-01", "ESP-FA-030/031; desenho D-FA-030 rev. B", "PC-SOP-01 rev. 04 (migração por lote, estanquidade)", "AQL crítico 0,1 (fuga); migração ≤ 10 mg/dm²", "Declaração de conformidade FCM por lote; dossier PPWR", "Concluídas"),
    ("DD-26-02", "ESP-FP-032/033; desenho D-FP-032 rev. C", "PC-SOP-01 rev. 04", "AQL crítico 0,1; rastreabilidade ao lote de resina", "Certificado CQ-02 por lote; notificação de alterações", "Concluídas"),
    ("DD-26-03", "ESP-PT-010/011", "PC-INJ-01 rev. 05", "Carga de empilhamento ≥ 25 kgf", "Declaração FCM (versão PP)", "Concluídas"),
    ("DD-26-04", "ESP-TE-012 rev. B (pontes retificadas)", "PC-INJ-01 rev. 05 (anel por lote)", "Força de rotura das pontes 15–35 N; 0 falhas em 32 amostras", "Certificado com resultado do anel (MOC-Q-26-15)", "Concluídas"),
    ("DD-26-05", "ESP-TP-013 rev. 01 (força de remoção)", "PC-INJ-01 rev. 06", "Força de remoção 20–40 N", "Declaração FCM", "Concluídas"),
    ("DD-26-06", "ESP-TA-014 rev. A", "PC-INJ-01 rev. 05", "Binário 8–16 N·cm; vedação 100% no ensaio de fuga", "Declaração FCM; dossier PPWR", "Concluídas"),
]

ALT_DD = [
    ("DC-26-01", "DD-26-05", "2026-06-10", "Características de inspeção de TP-013 revistas: 'binário' → 'força de remoção'; 'rosca' não aplicável a tampa de encaixe",
     "Revisão G2: tampa sem rosca não pode ser ensaiada a binário nem a rosca", "Parcial: binário corrigido em 22/09 (MOC-Q-26-08); a característica 'rosca' continuou no plano de inspeção por atributos e rejeitou 7 lotes (auditoria da configuração de 28/09)",
     GQ, "2026-09-22", "Retirar 'rosca' do plano de atributos de TP-013; reavaliar os 7 lotes rejeitados; auditoria da configuração aos 17 SKU", "Implementada"),
    ("DC-26-02", "DD-26-04", "2026-05-06", "Retificação das pontes do anel de inviolabilidade (2 cavidades)", "Verificação G2: força de rotura > 35 N", "Reensaio 32 amostras conforme",
     RD_, "2026-05-08", "Ensaio 100% do anel nas primeiras 6 semanas; PFMEA S = 10", "Implementada"),
    ("DC-26-03", "DD-26-02", "2026-05-12", "FP-032: +0,15 mm de espessura na base", "Verificação G2: falha no ensaio de queda", "Queda 20/20 conforme após alteração", RD_, "2026-05-14",
     "Notificação ao cliente farmacêutico antes da validação (acordo de qualidade)", "Implementada"),
    ("DC-26-04", "DD-26-06", "2026-06-18", "Tolerância do lábio de vedação TA-014 ajustada ao vedante do cliente", "Validação G3 no cliente", "Vedação 100% conforme no ensaio de fuga",
     RD_, "2026-06-20", "Ensaio de vedação por lote no safe launch", "Implementada"),
    ("DC-26-05", "DD-26-01..06", "2026-09-18", "Especificação única por SKU (nominais herdados de lotes doadores)", "Auditoria de dados pós-lançamento", "Dados reexpressos contra a especificação correta",
     GQ, "2026-09-23", "Regra no ERP: um nominal por característica e SKU (MOC-Q-26-09)", "Implementada"),
]


def fpy_familias():
    lots = Q.lot_dispositions()
    out = {}
    for p in PROJ:
        fam = p[3]
        l = lots[lots["Produto"].str.startswith(fam)]
        out[p[0]] = (len(l), int((l["DispositionDetail"] == "Approved - First Pass").sum()), int((l["FinalLotDecision"] == "Rejected").sum()))
    return out


def build(out):
    b = Book("RG-SGQ-11", "Design e Desenvolvimento de Produtos",
             activities="Planear, controlar (revisão, verificação, validação), registar entradas e saídas e controlar alterações dos projetos de design e desenvolvimento.",
             clauses="8.3.1 (abordagem iterativa); 8.3.2 a)–j); 8.3.3 a)–e) (evidência das entradas); 8.3.4 a)–f); 8.3.5 a)–d) (evidência das saídas); 8.3.6 (alterações: revisão, autorização, ações)",
             purpose="Registo dos 6 projetos que lançaram os 17 SKU alimentares, farmacêuticos e de potes em julho/2026: planeamento (8.3.2), entradas por categoria (8.3.3), etapas stage-gate com revisão/verificação/validação (8.3.4), saídas (8.3.5), alterações de design (8.3.6) e o FPY real do lançamento medido no dataset.",
             links=[("RG-SGQ-06", "Alterações de design com impacto na produção (MOC)."), ("RG-SGQ-04 PFMEA", "Características críticas e severidades."),
                    ("RG-SGA-20", "Reciclabilidade e dossier PPWR por família (saídas de design)."), ("dataset", "Decisões de lote dos SKU novos (jul–dez/2026).")],
             guidance=[("Academy — cap. 94–97 (Classificação de características, entradas, verificação e validação)", "Verificação = saídas cumprem entradas; validação = produto cumpre o uso previsto (no enchimento do cliente)."),
                       ("ISO 10007:2017", "Auditoria da configuração após lançamento (DC-26-01, DC-26-05)."),
                       ("ISO/TC 176 APG — Design and development", "O auditor segue um projeto do briefing à libertação e verifica que os problemas das revisões originaram ações (8.3.4 e).")])
    b.add_list("EstadoProj", ["Planeado", "Em desenvolvimento", "Em safe launch", "Fechado"])
    b.add_list("TipoEtapa", ["Revisão (8.3.4 b)", "Verificação (8.3.4 c)", "Validação (8.3.4 d)", "Revisão final / libertação"])
    b.add_list("ResEtapa", ["Aprovado", "Aprovado com ações", "Reprovado", "Pendente"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("EstadoAlt", ["Em análise", "Em curso", "Implementada", "Rejeitada"])
    b.add_list("EstadoSaida", ["Concluídas", "Em revisão", "Pendentes"])
    b.add_list("Funcao", FUNC_NAMES)

    fpy = fpy_familias()
    pcols = [col("ID_Projeto", 9, key="PK", desc="Projeto."), col("Titulo", 36, desc="Título."), col("SKUs", 40, desc="Produtos (IDs do dataset)."), col("Familia", 7, desc="Prefixo da família."),
             col("Clientes", 16, desc="Clientes (8.3.2 g)."), col("Molde_Maquina", 20, desc="Molde e máquina."), col("a_Natureza_Complexidade", 30, desc="8.3.2 a)."),
             col("d_Responsavel", 20, dv="Funcao", desc="8.3.2 d)."), col("f_Interfaces", 26, desc="8.3.2 f)."), col("g_Participacao_Cliente", 28, desc="8.3.2 g)."),
             col("h_Requisitos_Provisao", 30, desc="8.3.2 h)."), col("i_Nivel_Controlo", 14, desc="8.3.2 i)."), col("Inicio", 11, "date", desc="Início."),
             col("Fim_Planeado", 11, "date", desc="Fim planeado."), col("Fim_Real", 11, "date", desc="Libertação para série.", req=False), col("Estado", 13, dv="EstadoProj", desc="Estado."),
             col("Lotes_Lancamento", 8, "int", desc="Lotes com decisão desde o lançamento (dataset jul–dez/2026)."),
             col("Lotes_1a", 8, "int", desc="Lotes aprovados à primeira (dataset)."), col("Lotes_Rejeitados", 8, "int", desc="Lotes rejeitados (dataset)."),
             col("FPY_Lancamento", 9, "pct1", f='=IFERROR(@Lotes_1a@/@Lotes_Lancamento@,"")', desc="FPY de lote desde o lançamento."),
             col("Meta_Safe_Launch", 8, "pct", desc="Meta de FPY no safe launch."),
             col("Etapas_Concluidas", 9, "int", f='=COUNTIFS(tbl_etapas[ID_Projeto],@ID_Projeto@,tbl_etapas[Resultado],"Aprovado*")', desc="Gates aprovados."),
             col("Acoes_Abertas", 8, "int", f='=COUNTIFS(tbl_alteracoes_dd[ID_Projeto],@ID_Projeto@,tbl_alteracoes_dd[Estado],"Em curso")', desc="Alterações de design em curso."),
             col("Situacao", 16, f='=IF(@ID_Projeto@="","",IF(@FPY_Lancamento@="","Sem dados",IF(@FPY_Lancamento@>=@Meta_Safe_Launch@,"Lançamento OK","Reforçar safe launch")))', desc="Situação do lançamento.")]
    prow = []
    for p in PROJ:
        d = dict(zip(input_names(pcols)[:16], p))
        for k in ("Inicio", "Fim_Planeado", "Fim_Real"):
            d[k] = dt.date.fromisoformat(d[k]) if d[k] else None
        n, a, r = fpy[p[0]]
        d.update(Lotes_Lancamento=n, Lotes_1a=a, Lotes_Rejeitados=r, Meta_Safe_Launch=0.90)
        prow.append(d)
    b.table("Projetos_DD", "tbl_projetos_dd", pcols, prow, "Planeamento dos projetos de design e desenvolvimento (8.3.2) e resultado real do lançamento (dataset).",
            title="PROJETOS DE DESIGN E DESENVOLVIMENTO 2026 (8.3.2)", subtitle="FPY de lançamento calculado com as decisões de lote reais do dataset (jul–dez/2026) · Meta de safe launch 90%",
            cf=[("Situacao", {"Reforçar": "red", "OK": "green"}), ("FPY_Lancamento", "AND(@<>\"\",@<0.9)", "orange")], row_height=48, freeze_col=2)

    ecols = [col("ID_Projeto", 9, desc="Projeto.", key="FK → tbl_projetos_dd"), col("Alinea", 6, desc="8.3.3 a)–e)."), col("Tipo_Entrada", 30, desc="Categoria."),
             col("Entrada", 60, desc="Entrada determinada."), col("Completa_Sem_Ambiguidade", 10, dv="SimNao", desc="Completa e sem ambiguidade (8.3.3)."),
             col("Conflitos_Resolvidos", 10, dv="SimNao", desc="Entradas contraditórias resolvidas.")]
    erows = []
    for p in PROJ:
        for k, (tipo, m) in ENTRADAS.items():
            erows.append(dict(ID_Projeto=p[0], Alinea=f"{k})", Tipo_Entrada=tipo, Entrada=m[p[0]], Completa_Sem_Ambiguidade="Não" if (p[0], k) == ("DD-26-05", "a") else "Sim",
                              Conflitos_Resolvidos="Sim"))
    b.table("Entradas_DD", "tbl_entradas_dd", ecols, erows, "Entradas do design por projeto e categoria (evidência de 8.3.3).",
            cf=[("Completa_Sem_Ambiguidade", {"Não": "red"})], row_height=30)

    scols = [col("ID_Etapa", 12, key="PK", desc="Etapa."), col("ID_Projeto", 9, desc="Projeto.", key="FK → tbl_projetos_dd"), col("Gate", 5, desc="Gate."), col("Descricao", 44, desc="Etapa."),
             col("Tipo", 18, dv="TipoEtapa", desc="Revisão / verificação / validação (8.3.4)."), col("Data_Planeada", 11, "date", desc="Data planeada."), col("Data_Real", 11, "date", desc="Data real."),
             col("Resultado", 13, dv="ResEtapa", desc="Resultado."), col("Problemas_Acoes", 44, desc="Problemas e ações (8.3.4 e).", req=False), col("ID_Alteracao", 9, desc="Alteração de design.", key="FK → tbl_alteracoes_dd", req=False),
             col("Atraso_Dias", 7, "int", f='=IF(OR(@Data_Real@="",@Data_Planeada@=""),"",@Data_Real@-@Data_Planeada@)', desc="Real − planeado.")]
    srows = []
    for p in PROJ:
        ini = dt.date.fromisoformat(p[12])
        for g, desc, tipo, off in ETAPAS:
            plan = ini + dt.timedelta(days=off)
            res, prob, alt = RESULT.get((p[0], g), ("Aprovado", None, None))
            real = plan + dt.timedelta(days=(3 if res != "Aprovado" else 0) + (4 if g == "G4" else 0))
            srows.append(dict(ID_Etapa=f"{p[0]}-{g}", ID_Projeto=p[0], Gate=g, Descricao=desc, Tipo=tipo, Data_Planeada=plan, Data_Real=real, Resultado=res, Problemas_Acoes=prob, ID_Alteracao=alt))
    b.table("Etapas_Controlo", "tbl_etapas", scols, srows, "Revisões, verificações e validações por projeto (evidência de 8.3.4 f).",
            title="CONTROLOS DO DESIGN — STAGE-GATE (8.3.4)", cf=[("Resultado", {"ações": "orange", "Reprovado": "red", "Aprovado": "green"}), ("Atraso_Dias", "AND(@<>\"\",@>7)", "orange")], row_height=30)

    ocols = [col("ID_Projeto", 9, key="PK / FK", desc="Projeto."), col("Especificacao_Desenho", 34, desc="8.3.5 d) características do produto."),
             col("Plano_Controlo", 30, desc="8.3.5 b) c) adequado aos processos seguintes; monitorização."), col("Criterios_Aceitacao", 36, desc="8.3.5 c) critérios de aceitação."),
             col("Informacao_Produto", 36, desc="8.3.5 d) informação para utilização segura e correta."), col("Estado", 11, dv="EstadoSaida", desc="Estado.")]
    b.table("Saidas_DD", "tbl_saidas_dd", ocols, rows_from(input_names(ocols), SAIDAS), "Saídas do design (evidência de 8.3.5).", cf=[("Estado", {"revisão": "orange", "Concluídas": "green"})], row_height=30)

    acols = [col("ID_Alteracao", 9, key="PK", desc="Alteração de design."), col("ID_Projeto", 11, desc="Projeto."), col("Data", 11, "date", desc="Data."),
             col("Alteracao", 44, desc="8.3.6 a) alteração."), col("Origem", 30, desc="Onde foi identificada."), col("Resultado_Revisao", 44, desc="8.3.6 b) resultado da revisão."),
             col("Autorizado_Por", 20, dv="Funcao", desc="8.3.6 c) autorização."), col("Data_Autorizacao", 11, "date", desc="Data da autorização."),
             col("Acoes_Impacto_Adverso", 44, desc="8.3.6 d) ações para prevenir impacto adverso."), col("Estado", 11, dv="EstadoAlt", desc="Estado.")]
    b.table("Alteracoes_Design", "tbl_alteracoes_dd", acols, rows_from(input_names(acols), ALT_DD, dates=("Data", "Data_Autorizacao")),
            "Alterações do design e desenvolvimento (evidência de 8.3.6 a–d).", title="ALTERAÇÕES DO DESIGN (8.3.6)",
            subtitle="DC-26-01: auditoria da configuração (ISO 10007) encontrou a característica 'rosca' ainda aplicada à tampa de encaixe TP-013 no dataset de inspeção por atributos",
            cf=[("Estado", {"Em curso": "orange", "Implementada": "green"})], row_height=60)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
