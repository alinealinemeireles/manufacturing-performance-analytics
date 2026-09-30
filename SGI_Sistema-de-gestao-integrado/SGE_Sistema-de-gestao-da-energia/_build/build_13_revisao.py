"""RG-SGE-13 — Revisão pela gestão do SGE (RD-E-2026-01, 18/12/2026, integrada no SGI).
ISO 50001:2018 9.3.1, 9.3.2 a)–e), 9.3.3 (entradas de desempenho energético), 9.3.4 a)–g) (resultados — reter)."""
from sgelib import *
from dimse import *

AGENDA = [
    (1, "9.3.2 a)", "Estado das ações de revisões anteriores (1.ª revisão do SGE; decisões do SGA RG-26-D03/D04 sobre energia)", "RG-SGA-15; tbl_acoes_anteriores", GE, 10),
    (2, "9.3.2 b)", "Alterações em questões externas e internas, riscos e oportunidades: DL 130/2026 (autoconsumo), transposição da Diretiva 2023/1791, linhas novas, calor de agosto, preço", "RG-SGE-01; RG-SGE-03", GE, 15),
    (3, "9.3.2 c) 1)", "Não conformidades e ações corretivas (NCE-26-01 a 04)", "RG-SGE-14", GE, 10),
    (4, "9.3.2 c) 2) / 9.3.3", "Resultados de monitorização e medição: IDE vs LBE; melhoria de 5,4% demonstrada em out–dez/2026; +1,9% (não significativa) em mar–dez/2026", "RG-SGE-05 LBE_Modelo; RG-SGE-11", GE, 25),
    (5, "9.3.2 c) 3)", "Resultados da auditoria AUD-E-2026-01 (2 NC menores, 2 observações, 4 oportunidades)", "RG-SGE-12", AUD, 10),
    (6, "9.3.2 c) 4)", "Avaliação da conformidade legal: REP 2026 entregue; trajetória do PREn na meta por margem estreita", "RG-SGE-10", GE, 10),
    (7, "9.3.3", "Grau de cumprimento dos objetivos e metas energéticas; estado dos planos de ação", "RG-SGE-05 tbl_objetivos, tbl_planos_acao", DIND, 15),
    (8, "9.3.2 d)", "Oportunidades de melhoria (16 OPE, 1,2 GWh/ano) incluindo competência", "RG-SGE-04; RG-SGE-07", GE, 15),
    (9, "9.3.2 e)", "Política energética (adequação)", "RG-SGE-02", DG, 5),
]
DECISOES = [
    ("RD-E-26-D01", "9.3.4 a) Oportunidades de melhoria do desempenho energético", "Aprovar PA-E-04 (servo-bombas IM-002/004 + isolamento de canhões, € 63 200) com base no LCC (RG-SGE-09) para o 1.º semestre de 2027.", DIND, "2027-06-30", 63200, "PA-E-04", "Aprovada"),
    ("RD-E-26-D02", "9.3.4 b) Política energética", "Manter a POL-SGE-01; reforçar a comunicação no turno 3 (CONE-A-26-06).", DG, "2027-01-31", 0, "COME-01", "Aprovada"),
    ("RD-E-26-D03", "9.3.4 c) IDE ou LBE", "Manter a LBE-01 'válida com reserva' até haver 12 meses medidos; criar a LBE-01b (com as máquinas novas) em 07/2027 e as LBE por USE em 01/2028.", GE, "2027-07-31", 0, "ALE-01; ALE-03", "Aprovada"),
    ("RD-E-26-D04", "9.3.4 d) Objetivos, metas e planos", "Manter OBJ-E-01 (+5% até 12/2027) e antecipar o free-cooling (PA-E-06) para 06/2027; meta de 2026 (+2%) atingida no 4.º trimestre.", DIND, "2027-06-30", 42000, "PA-E-06", "Aprovada"),
    ("RD-E-26-D05", "9.3.4 e) Integração nos processos de negócio", "Incluir a secção de energia (critérios de projeto e LCC) na checklist de alterações do SGI (PR-SGA-06) e no processo de investimentos.", DIND, "2027-02-28", 0, "NCE-26-01", "Aprovada"),
    ("RD-E-26-D06", "9.3.4 f) Recursos", "Aumentar a potência contratada para 1 550 kW (efetivo 01/2027) e orçamentar o estudo da UPAC (PRJ-E-02) e a candidatura Portugal 2030.", DFIN, "2027-03-31", 850000, "RE-03; PA-E-07", "Aprovada"),
    ("RD-E-26-D07", "9.3.4 g) Competência, consciencialização e comunicação", "Formar o substituto do Gestor de Energia (Técnico de Utilidades) em M&V e IDE (FOR-E-03/05) — risco RE-05.", RH_, "2027-04-30", 3500, "RE-05", "Aprovada"),
    ("RD-E-26-D08", "Conclusão sobre a eficácia (9.3.1)", "O SGE é adequado e suficiente; a eficácia é parcial: melhoria demonstrada só após as ações de out–dez/2026. Decidido avançar para a certificação em 09/2027.", DG, "2027-09-30", 0, "AUD-E-2027-02", "Aprovada"),
]
ANTERIORES = [
    ("RG-26-D03", "SGA: aprovar o CAPEX de submedição (6 analisadores + 3 contadores de água) e o VSD do compressor", GMAN, "2026-12-15", "Concluída", "Analisadores em serviço desde 15/12/2026 (M01–M06)"),
    ("RG-26-D04", "SGA: estudo de viabilidade da UPAC ≈ 1 MWp e diagnóstico EMAS", DFIN, "2027-03-31", "Em curso", "Estudo da UPAC entregue a 30/11/2026; EMAS em 2027"),
]


def build(out):
    b = Book("RG-SGE-13", "Revisão pela Gestão do SGE",
             activities="A gestão de topo revê o SGE a intervalos planeados quanto à adequação, suficiência, eficácia e alinhamento com a orientação estratégica, e decide sobre melhoria e recursos.",
             clauses="9.3.1; 9.3.2 a)–e); 9.3.3 (objetivos e metas atingidos; desempenho energético e melhoria com base na monitorização, incluindo os IDE; estado dos planos de ação); "
                     "9.3.4 a)–g) (reter como evidência); 5.1 g) e l).",
             purpose="1.ª revisão pela gestão do SGE (RD-E-2026-01, 18/12/2026, integrada na revisão do SGI): agenda com a entrada da norma de cada ponto, ações anteriores, "
                     "8 decisões classificadas por 9.3.4 a)–g) e ata.",
             links=[("RG-SGE-05", "IDE, LBE e objetivos (9.3.3)."), ("RG-SGE-12", "Resultados da auditoria."), ("RG-SGA-15 / RG-SGQ-17", "Revisões do SGA e do SGQ (mesmas tabelas).")],
             guidance=[("ISO 50004:2020 §9.3", "Conteúdo típico das entradas e saídas da revisão pela gestão do SGE."),
                       ("M-9 Avaliação de desempenho (curso Bureau Veritas)", "Entradas específicas de desempenho energético (9.3.3).")],
             legal=[("DL 71/2008 (SGCIE)", "Estado do PREn e do REP apresentado (ponto 6).")])
    b.add_list("Funcao", FUNC_NAMES)
    acols = [col("ID_Reuniao", 12, desc="Reunião.", key="PK (com Ponto)"), col("Ponto", 6, "int", desc="Ponto."), col("Entrada_9_3_2", 14, desc="Entrada da norma (9.3.2 / 9.3.3)."),
             col("Topico", 70, desc="Tópico."), col("Fonte_Dados", 30, desc="Registo."), col("Apresentador", 24, dv="Funcao", desc="Quem apresenta."), col("Duracao_min", 8, "int", desc="Minutos."),
             col("N_Decisoes", 8, "int", f='=IF(@ID_Reuniao@="","",COUNTIF(tbl_decisoes[Ponto_Agenda],@Ponto@))', desc="Decisões associadas.")]
    PONTO = {"RD-E-26-D01": 8, "RD-E-26-D02": 9, "RD-E-26-D03": 4, "RD-E-26-D04": 7, "RD-E-26-D05": 5, "RD-E-26-D06": 2, "RD-E-26-D07": 8, "RD-E-26-D08": 4}
    b.table("Agenda", "tbl_agenda", acols, [dict(ID_Reuniao="RD-E-2026-01", Ponto=a[0], Entrada_9_3_2=a[1], Topico=a[2], Fonte_Dados=a[3], Apresentador=a[4], Duracao_min=a[5]) for a in AGENDA],
            "Agenda com as entradas 9.3.2 e 9.3.3 — mesma estrutura do RG-SGA-15.", title="REVISÃO PELA GESTÃO RD-E-2026-01 — 18/12/2026 — AGENDA", row_height=36)
    dcols = [col("ID_Decisao", 12, key="PK", desc="Decisão."), col("Ponto_Agenda", 7, "int", desc="Ponto da agenda.", key="FK → tbl_agenda"),
             col("Tipo_Saida_9_3_4", 30, desc="Resultado da norma (9.3.4 a–g) — posição de Tipo_Saida_9_3_3 no SGA."), col("Decisao_Tomada", 60, desc="Decisão."),
             col("Responsavel", 22, dv="Funcao", desc="Responsável."), col("Prazo", 11, "date", desc="Prazo."), col("Recursos_EUR", 11, "eur", desc="Recursos."),
             col("Ligacao", 16, desc="Ligação."), col("Estado", 9, desc="Estado."), col("Dias_ate_Prazo", 8, "int", f='=IF(@ID_Decisao@="","",@Prazo@-DataRef)', desc="Dias até ao prazo.")]
    drows = rows_from(["ID_Decisao", "Tipo_Saida_9_3_4", "Decisao_Tomada", "Responsavel", "Prazo", "Recursos_EUR", "Ligacao", "Estado"], DECISOES, dates=("Prazo",))
    for d in drows:
        d["Ponto_Agenda"] = PONTO[d["ID_Decisao"]]
    b.table("Decisoes", "tbl_decisoes", dcols, drows, "Decisões da revisão (9.3.4 a–g — reter).", title="DECISÕES (9.3.4)", row_height=45)
    ncols = [col("ID_Decisao", 10, key="PK", desc="Decisão anterior."), col("Decisao", 60, desc="Decisão."), col("Responsavel", 22, dv="Funcao", desc="Responsável."), col("Prazo", 11, "date", desc="Prazo."),
             col("Estado", 10, desc="Estado."), col("Evidencia", 40, desc="Evidência.")]
    b.table("Acoes_Anteriores", "tbl_acoes_anteriores", ncols, rows_from(input_names(ncols), ANTERIORES, dates=("Prazo",)), "Estado das ações de revisões anteriores (9.3.2 a).", row_height=30)
    ws = b.sheet("Ata", "Ata da revisão pela gestão (resumo para assinatura).", tab_color="1F4E5F")
    title(ws, "ATA DA REVISÃO PELA GESTÃO DO SGE — RD-E-2026-01", f"{EMPRESA} · 18/12/2026, 14h00–16h00 · Integrada na revisão do SGI")
    notes(ws, 4, [
        ("Presentes", "Diretor Geral (preside); Diretor Industrial; Gestor(a) de Energia; Gerente de Manutenção; Gerente de Produção; Técnico de Utilidades; Diretor Financeiro; Gestor do SGA; Auditor(a) interno(a)."),
        ("Desempenho energético", "Melhoria normalizada de 5,4% em out–dez/2026 (92 MWh), estatisticamente significativa (incerteza 61 MWh) e coerente com as poupanças verificadas por ação (71 MWh; diferença de 21 MWh dentro da incerteza). No período mar–dez/2026: +1,9% (100 MWh), dentro da incerteza (106 MWh) — não demonstrada."),
        ("Objetivos", "OBJ-E-06 atingido (submedição); OBJ-E-02 com potência específica de 0,106 kWh/Nm³ (meta 0,105) e fugas de 14%; restantes em curso."),
        ("Conformidade", "REP 2026 do SGCIE entregue; trajetória do PREn cumprida por margem de 0,3%; ultrapassagem da potência contratada em agosto tratada (NCE-26-04)."),
        ("Conclusão (9.3.1)", "O SGE é adequado, suficiente e alinhado com a estratégia de descarbonização; eficácia parcial. Decidido avançar para a certificação ISO 50001 em 09/2027."),
        ("Assinaturas", "Diretor Geral ______________________    Gestor(a) de Energia ______________________"),
    ])
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
