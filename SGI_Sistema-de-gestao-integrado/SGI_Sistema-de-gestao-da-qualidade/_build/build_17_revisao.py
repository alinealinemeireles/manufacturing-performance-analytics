"""RG-SGQ-17 — Revisão pela gestão (ISO 9001:2026 9.3.1, 9.3.2 a)–h), 9.3.3; 5.1.1 l) prestar contas).
Reunião RPG-2026-01 de 25/09/2026. Os números das entradas de desempenho são calculados a partir do dataset (mesma base do RG-SGQ-05)."""
import datetime as dt
from sgqlib import *
from dimsq import *
import qdata as Q
import build_05_objetivos as B5

RPG_DATA = dt.date(2026, 9, 25)


def numeros():
    df = B5.base_mensal()
    u12 = df.tail(12)
    p6, u6 = df.iloc[-12:-6], df.tail(6)
    f = lambda d, a, b_: d[a].sum() / d[b_].sum()
    n = dict(rej12=f(u12, "Rejeitado", "Produzido"), rej_p6=f(p6, "Rejeitado", "Produzido"), rej_u6=f(u6, "Rejeitado", "Produzido"),
             fpy_p6=f(p6, "Lotes_1a", "Lotes_Decididos"), fpy_u6=f(u6, "Lotes_1a", "Lotes_Decididos"),
             cpmu_p6=p6.Reclamacoes.sum() / p6.Expedido.sum() * 1e6, cpmu_u6=u6.Reclamacoes.sum() / u6.Expedido.sum() * 1e6,
             rec12=int(u12.Reclamacoes.sum()), serv12=int(u12.Reclamacoes_Servico.sum()), crit12=int(u12.Reclamacoes_Criticas.sum()),
             oee12=u12.OEE_Soma.sum() / u12.Ordens.sum(), mp_p6=f(p6, "Lotes_MP_Aceites", "Lotes_MP"), mp_u6=f(u6, "Lotes_MP_Aceites", "Lotes_MP"),
             capa_prazo=f(u12, "CAPA_Fechadas_No_Prazo", "CAPA_Com_Prazo"), capa_efic=u12.CAPA_Eficazes.sum() / (u12.CAPA_Eficazes.sum() + u12.CAPA_Nao_Eficazes.sum()),
             conc=f(u12, "Lotes_Concessao", "Lotes_Decididos"), cpk=f(u12, "Subgrupos_Cpk_1", "Subgrupos_SPC"), nc12=len(Q.nonconformance().query("Date >= '2025-09-01'")))
    return n


def tend(a, b_, maior_melhor):
    if abs(b_ - a) / max(abs(a), 1e-9) < 0.03:
        return "Estável"
    return "Melhoria" if (b_ > a) == maior_melhor else "Pior"


def build(out):
    n = numeros()
    pc = lambda x: f"{x * 100:.1f}%".replace(".", ",")
    dec = lambda x: f"{x:.1f}".replace(".", ",")
    ENTRADAS = [
        ("9.3.2 a)", "Estado das ações de revisões anteriores", "RPG-2025-02: 8 decisões — 5 concluídas, 2 em curso, 1 atrasada (reforço do laboratório de receção).", "—", "RG-SGQ-17 tbl_acoes_anteriores", GQ),
        ("9.3.2 b)", "Alterações nas questões externas e internas", "Entrada em alimentar/farma (17 SKU), PPWR aplicável desde 12/08/2026, ondas de calor (jul/2026), ISO 9001:2026 publicada; alterações climáticas determinadas como pertinentes.", "—", "RG-SGQ-01 tbl_pestel; tbl_swot; tbl_clima", GQ),
        ("9.3.2 c)", "Alterações nas necessidades das partes interessadas", "Clientes farma pedem resultado do anel no certificado (MOC-Q-26-15); clientes cosméticos pedem pegada de carbono; organismo de certificação: transição até 2029.", "—", "RG-SGQ-01 tbl_partes_interessadas", DCOM),
        ("9.3.2 d1)", "NC e ações corretivas (tendências)", f"{n['nc12']} NC em 12 meses; CAPA no prazo {pc(n['capa_prazo'])}; eficácia das CAPA {pc(n['capa_efic'])}; 272 NC maiores sem CAPA (CON-Q-26-07).",
         "Pior" if n["capa_efic"] < 0.6 else "Estável", "RG-SGQ-14; RG-SGQ-18", GQ),
        ("9.3.2 d2)", "Resultados de monitorização e medição", f"Rejeição interna: {pc(n['rej_p6'])} → {pc(n['rej_u6'])} (meta 2,0%); FPY de lote {pc(n['fpy_p6'])} → {pc(n['fpy_u6'])}; OEE 12 m {pc(n['oee12'])}; subgrupos com Cpk ≥ 1,00: {pc(n['cpk'])}.",
         tend(n["rej_p6"], n["rej_u6"], False), "RG-SGQ-05 Painel_KPI", GPROD),
        ("9.3.2 d3)", "Resultados das auditorias", "4 auditorias realizadas (100% do programa até à data); 12 constatações: 2 NC maiores (concessões sem aprovação do cliente; ação corretiva não sistemática), 6 NC menores.", "Pior", "RG-SGQ-16", GQ),
        ("9.3.2 d4)", "Satisfação do cliente e feedback", f"CSI 72,6% → 78,5% (meta 80%); NPS 0 → 38; {n['rec12']} reclamações em 12 m ({n['serv12']} de serviço/logística, {n['crit12']} críticas); CPMU {dec(n['cpmu_p6'])} → {dec(n['cpmu_u6'])}.",
         tend(n["cpmu_p6"], n["cpmu_u6"], False), "RG-SGQ-15", DCOM),
        ("9.3.2 d5)", "Grau de cumprimento dos objetivos", "1 de 8 objetivos atingido (OTIF); 6 em curso; 1 semestral. Rejeição e CPMU a melhorar; FPY, CAPA e Cpk abaixo da meta.", "Estável", "RG-SGQ-05 tbl_objetivos", GQ),
        ("9.3.2 d6)", "Desempenho dos processos e conformidade dos produtos", f"Lotes libertados por concessão {pc(n['conc'])} (meta 1%); lançamento de TE-012 e TA-014 com FPY < 90%; ISBM-005 com MTBF 8,4 h.", "Estável", "RG-SGQ-13; RG-SGQ-11; RG-SGQ-02", GPROD),
        ("9.3.2 d7)", "Desempenho dos fornecedores externos", f"Lotes de MP aceites {pc(n['mp_p6'])} → {pc(n['mp_u6'])} (meta 95%); SUP-005 classe D (suspender); SUP-004 e SUP-006 classe C.",
         tend(n["mp_p6"], n["mp_u6"], True), "RG-SGQ-12", CMP_),
        ("9.3.2 e)", "Oportunidades de melhoria", "Visão artificial HF-001 (O13); replicar DOE da IM-002 (O1); SMED (O9); rastreabilidade de resina no MES (O12).", "—", "RG-SGQ-04 tbl_oport_q; RG-SGQ-19", GQ),
        ("9.3.2 f)", "Adequação dos recursos", "Inspetores insuficientes no pico (fila de lotes); 1 só responsável pelo pipeline de dados (R26); leak testers só em 3 postos.", "—", "RG-SGQ-07; RG-SGQ-09", DIND),
        ("9.3.2 g)", "Eficácia das ações para tratar riscos", "27 riscos da qualidade: 3 eficazes, 4 parciais, 3 não eficazes (R3, R13, R20), 17 por avaliar.", "—", "RG-SGQ-04 Resumo_Riscos", GQ),
        ("9.3.2 h)", "Eficácia das ações para tratar oportunidades", "11 oportunidades: 1 parcial (O8 scorecard), 10 por avaliar — a maioria iniciada em 2026.", "—", "RG-SGQ-04 tbl_oport_q", GQ),
        ("5.1.1 i)", "Cultura da qualidade e comportamento ético (complemento)", "Maturidade 'Definida' em todas as dimensões ISO 10010; mais fracas: comunicação aberta (2,6) e aprendizagem (2,7); 4 relatos de integridade (3 confirmados).", "—", "RG-SGQ-03", DG),
    ]
    DECISOES = [
        ("RPG-2026-01-D01", "Melhoria", "Tornar obrigatória a abertura de CAPA para todas as NC maiores e críticas; comité semanal de CAPA com a Direção Industrial", DIND, "2026-10-31", 0, "CAPA-Q-26-12", "Em curso"),   # 17% das NC maiores de out–nov ainda sem CAPA (CON-Q-26-16)
        ("RPG-2026-01-D02", "Alteração ao SGQ", "Concessões só com aprovação escrita do cliente registada no ERP antes da expedição (bloqueio)", GQ, "2026-10-31", 3000, "CAPA-Q-26-08", "Concluída"),
        ("RPG-2026-01-D03", "Recursos", "Contratar 1 inspetor efetivo e 1 temporário para o pico set–nov", RH_, "2026-10-15", 38000, "MOC-Q-26-14", "Concluída"),
        ("RPG-2026-01-D04", "Recursos", "Leak testers em linha nas ISBM-003 e ISBM-005 (estanquidade 100%)", DIND, "2027-01-31", 60000, "OBJ-Q-02", "Aprovada"),
        ("RPG-2026-01-D05", "Recursos", "Visão artificial na HF-001", DG, "2027-06-30", 85000, "MOC-Q-26-12", "Aprovada"),
        ("RPG-2026-01-D06", "Melhoria", "Suspender novas encomendas ao SUP-005 e qualificar alternativa para PP/PVC", CMP_, "2026-12-31", 0, "RG-SGQ-12", "Concluída"),
        ("RPG-2026-01-D07", "Alteração ao SGQ", "Registar o lote de resina no consumo de material (MES) — rastreabilidade completa", TI_, "2027-03-31", 15000, "O12; CON-Q-26-08", "Aprovada"),
        ("RPG-2026-01-D08", "Alteração ao SGQ", "Concluir a transição para a ISO 9001:2026 e auditoria de transição em mar/2027", GQ, "2027-03-31", 9000, "MOC-Q-26-01", "Em curso"),
        ("RPG-2026-01-D09", "Melhoria", "Plano de melhoria dos prazos de entrega (maior lacuna de satisfação): planeamento de capacidade e stock de segurança", LOG, "2026-12-31", 5000, "OBJ-Q-08", "Concluída"),
        ("RPG-2026-01-D10", "Melhoria", "Programa de cultura da qualidade: formação de chefias (FOR-Q-12) e reconhecimento de relatos", RH_, "2027-03-31", 12000, "RG-SGQ-03", "Aprovada"),
        ("RPG-2026-01-D11", "Recursos", "Formar 2.º responsável pelo pipeline de dados da qualidade", TI_, "2027-01-31", 4000, "KNW-09; R26", "Aprovada"),
    ]
    ANTERIORES = [
        ("RPG-2025-02-D01", "Implementar scorecard de fornecedores", CMP_, "2026-03-31", "Concluída", "RG-SGQ-12 em uso desde mar/2026"),
        ("RPG-2025-02-D02", "Projeto DMAIC na IM-002", GPROD, "2026-05-31", "Concluída", "Taxa de defeito 1,35% → 0,38% (PRJ-Q-01)"),
        ("RPG-2025-02-D03", "Reforma do molde M-SOP-007", GMAN, "2026-03-31", "Concluída", "MOC-Q-26-07 eficaz"),
        ("RPG-2025-02-D04", "Estudo MSA do peso das tampas", GQ, "2026-08-31", "Concluída", "GRR 3,5% da TV — aceitável"),
        ("RPG-2025-02-D05", "Qualificar fornecedores de resina alimentar e farmacêutica", CMP_, "2026-04-30", "Concluída", "SUP-009 (condicional) e SUP-010 aprovados"),
        ("RPG-2025-02-D06", "Inquérito de satisfação semestral", DCOM, "2026-06-30", "Em curso", "2.ª onda feita; falta plano por atributo"),
        ("RPG-2025-02-D07", "Checklist de passagem de turno", GPROD, "2026-06-30", "Em curso", "Em implementação digital (EH-09)"),
        ("RPG-2025-02-D08", "Reforço do laboratório de receção (2.º técnico)", RH_, "2026-03-31", "Concluída", "Técnico admitido a 16/11/2026 (após reprogramação)"),
    ]
    b = Book("RG-SGQ-17", "Revisão pela Gestão",
             activities="Rever o SGQ a intervalos planeados para assegurar a sua adequação, suficiência, eficácia e alinhamento com a orientação estratégica; registar as entradas a)–h) e as decisões.",
             clauses="9.3.1 (inclui alinhamento com a orientação estratégica); 9.3.2 a)–h) (2026: g) eficácia das ações para riscos e h) para oportunidades, separadas); 9.3.3 decisões sobre melhoria, alterações ao SGQ e recursos (informação documentada como evidência); 5.1.1 l)",
             purpose="Registo da revisão pela gestão RPG-2026-01 (25/09/2026): entradas com dados do dataset e dos registos do SGQ, tendências, decisões com responsável, prazo e recursos, estado das ações anteriores e ata para assinatura, incluindo a conclusão da gestão de topo sobre a eficácia do SGQ.",
             links=[("RG-SGQ-01 a 16, 18, 19", "Fonte de cada entrada (coluna Fonte)."), ("RG-SGA-15", "Revisão pela gestão do SGA — a reunião RPG-2026-01 foi conjunta (SGI) com a do SGA de 23/09/2026.")],
             guidance=[("ISO/TC 176 APG — Management review", "A revisão tem de ter as entradas exigidas e produzir decisões; o auditor procura evidência de que a gestão de topo participa e decide."),
                       ("Academy — cap. 88 e UC00556 OA 3.6 (Análise de dados e revisão pela gestão)", "Entradas com tendência e análise, não apenas listas; decisões com recursos."),
                       ("iso9001help.co.uk — Management review", "Agenda estruturada pelas entradas 9.3.2 e registo das saídas 9.3.3.")])
    b.add_list("Tendencia", ["Melhoria", "Estável", "Pior", "—"])
    b.add_list("TipoDecisao", ["Melhoria", "Alteração ao SGQ", "Recursos"])
    b.add_list("EstadoDec", ["Aprovada", "Em curso", "Concluída", "Atrasada", "Cancelada"])
    b.add_list("Funcao", FUNC_NAMES)

    # nomes de coluna comuns ao RG-SGA-15 (tbl_agenda: Entrada_9_3_2, Topico, Fonte_Dados, Apresentador; tbl_decisoes: Tipo_Saida_9_3_3, Decisao_Tomada)
    ecols = [col("Entrada_9_3_2", 9, key="PK", desc="Entrada 9.3.2 (alínea)."), col("Topico", 34, desc="Tópico."), col("Resumo_Dados", 80, desc="Informação apresentada (dados do dataset e dos registos)."),
             col("Tendencia", 9, dv="Tendencia", desc="Tendência (9.3.2 d: 'incluindo as tendências')."), col("Fonte_Dados", 28, desc="Registo de origem."), col("Apresentador", 24, dv="Funcao", desc="Quem apresentou.")]
    b.table("Entradas_9_3_2", "tbl_entradas_rpg", ecols, rows_from(input_names(ecols), ENTRADAS), "Entradas da revisão pela gestão RPG-2026-01 (9.3.2 a–h).",
            title="REVISÃO PELA GESTÃO RPG-2026-01 — ENTRADAS (9.3.2)", subtitle="25/09/2026 · Números calculados a partir do dataset (mesma base do RG-SGQ-05)",
            cf=[("Tendencia", {"Pior": "red", "Melhoria": "green", "Estável": "yellow"})], row_height=48)
    dcols = [col("ID_Decisao", 16, key="PK", desc="Decisão."), col("Tipo_Saida_9_3_3", 14, dv="TipoDecisao", desc="9.3.3: melhoria / alterações ao SGQ / recursos."), col("Decisao_Tomada", 70, desc="Decisão."),
             col("Responsavel", 24, dv="Funcao", desc="Responsável."), col("Prazo", 11, "date", desc="Prazo."), col("Recursos_EUR", 10, "eur", desc="Recursos aprovados."),
             col("Ligacao", 18, desc="Objetivo, MOC, CAPA ou risco.", req=False), col("Estado", 10, dv="EstadoDec", desc="Estado."),
             col("Alerta", 10, f='=IF(@ID_Decisao@="","",IF(AND(@Estado@<>"Concluída",@Prazo@<DataRef),"Atrasada","OK"))', desc="Alerta de prazo.")]
    b.table("Decisoes_9_3_3", "tbl_decisoes", dcols, rows_from(input_names(dcols), DECISOES, dates=("Prazo",)), "Decisões da revisão pela gestão (9.3.3).",
            title="DECISÕES DA REVISÃO PELA GESTÃO (9.3.3)", cf=[("Tipo_Saida_9_3_3", {"Recursos": "blue", "Alteração": "purple", "Melhoria": "green"}), ("Alerta", {"Atrasada": "red"})], row_height=30, extra_rows=5)
    acols = [col("ID_Decisao", 16, key="PK", desc="Decisão anterior."), col("Decisao", 50, desc="Decisão."), col("Responsavel", 24, dv="Funcao", desc="Responsável."),
             col("Prazo", 11, "date", desc="Prazo."), col("Estado", 10, dv="EstadoDec", desc="Estado."), col("Evidencia", 44, desc="Evidência / comentário.")]
    b.table("Acoes_Anteriores", "tbl_acoes_anteriores", acols, rows_from(input_names(acols), ANTERIORES, dates=("Prazo",)), "Estado das ações das revisões anteriores (9.3.2 a).",
            cf=[("Estado", {"Atrasada": "red", "Em curso": "yellow", "Concluída": "green"})], row_height=30)

    ws = b.sheet("Ata_RPG_2026_01", "Ata da revisão pela gestão em formato de impressão, com conclusão sobre a eficácia do SGQ (9.3.1; 5.1.1 l).", tab_color="7030A0")
    doc_header(ws, "RG-SGQ-17", "ATA DA REVISÃO PELA GESTÃO", "RPG-2026-01", 6)
    ws.column_dimensions["A"].width = 30
    for L in "BCDEF":
        ws.column_dimensions[L].width = 22
    blocos = [("Data / local", "25/09/2026, 09:30–13:00 — sala de reuniões da Unidade 1 (reunião conjunta SGQ + SGA)"),
              ("Participantes", "Diretor Geral (preside); Diretor Industrial; Gerente da Qualidade; Gerente de Produção; Gerente de Manutenção; Diretor Comercial; Responsável de Compras; Responsável de R&D; Responsável de RH; Gerente de Dados/TI; Gestor do SGA/EHS"),
              ("Entradas analisadas", "=COUNTA(tbl_entradas_rpg[Entrada_9_3_2])&\" entradas (9.3.2 a–h e cultura) — ver folha Entradas_9_3_2\""),
              ("Decisões tomadas", "=COUNTA(tbl_decisoes[ID_Decisao])&\" decisões — \"&COUNTIF(tbl_decisoes[Tipo_Saida_9_3_3],\"Recursos\")&\" de recursos (\"&FIXED(SUMIFS(tbl_decisoes[Recursos_EUR],tbl_decisoes[Tipo_Saida_9_3_3],\"Recursos\"),0)&\" €), \"&COUNTIF(tbl_decisoes[Tipo_Saida_9_3_3],\"Alteração ao SGQ\")&\" de alteração ao SGQ, \"&COUNTIF(tbl_decisoes[Tipo_Saida_9_3_3],\"Melhoria\")&\" de melhoria\""),
              ("Adequação (suitability)", "O SGQ é adequado ao propósito e ao novo contexto (alimentar/farma), mas os requisitos de concessão e de ação corretiva precisam de ser reforçados."),
              ("Suficiência (adequacy)", "Suficiente em documentação e processos; insuficiente em recursos de inspeção no pico e na rastreabilidade do lote de resina."),
              ("Eficácia (effectiveness)", "Parcialmente eficaz: rejeição e reclamações a melhorar; FPY, eficácia das CAPA e capacidade de processo abaixo das metas; 2 NC maiores de auditoria."),
              ("Alinhamento com a orientação estratégica (novo 2026)", "Alinhado com a estratégia 2026–2028 (crescimento em alimentar/farma); prioridade à conformidade legal e à prevenção de escapes."),
              ("Necessidades de alteração do SGQ", "Transição ISO 9001:2026 (MOC-Q-26-01); regra de concessões; rastreabilidade de resina; abertura obrigatória de CAPA."),
              ("Conclusão e responsabilização (5.1.1 l)", "A gestão de topo assume a responsabilidade pela eficácia do SGQ e pela execução das decisões RPG-2026-01-D01 a D11. Próxima revisão: março/2027 (após a auditoria de transição)."),
              ("Assinatura", "Diretor Geral: ______________________        Gerente da Qualidade: ______________________")]
    for k, (a, t) in enumerate(blocos):
        form_block(ws, 5 + k, a, t, vw=5, height=48 if len(str(t)) > 120 else 32)
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
