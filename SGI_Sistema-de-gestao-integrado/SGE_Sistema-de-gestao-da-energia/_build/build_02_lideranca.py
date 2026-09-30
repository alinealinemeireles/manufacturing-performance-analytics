"""RG-SGE-02 — Liderança e compromisso, política energética, equipa de gestão de energia, funções e RACI.
ISO 50001:2018 5.1 a)–m), 5.2 a)–g), 5.3 a)–e)."""
from sgelib import *
from dimse import *

LIDERANCA = [
    ("LIDE-01", "a)", "Assegurar que o âmbito e as fronteiras do SGE são estabelecidos", "Aprovação do âmbito (RG-SGE-01 tbl_ambito) e do MAN-SGE-01", "Ata RD-E-2026-01; MAN-SGE-01 rev. 00", DG, "Conforme", "Anual"),
    ("LIDE-02", "b)", "Política, objetivos e metas energéticas compatíveis com a orientação estratégica", "Aprovação da POL-SGE-01 e dos OBJ-E-01 a 06", "RG-SGE-05 tbl_objetivos (Data_Aprovacao)", DG, "Conforme", "Anual"),
    ("LIDE-03", "c)", "Integrar os requisitos do SGE nos processos de negócio", "Energia no orçamento CAPEX, nas compras (LCC), no quadro SQDC dos turnos e no plano de manutenção", "RG-SGE-09; RG-SGE-08", DIND, "Parcial", "Trimestral"),
    ("LIDE-04", "d)", "Assegurar que os planos de ação são aprovados e implementados", "Aprovação dos PA-E-01 a 07; acompanhamento mensal", "RG-SGE-05 tbl_planos_acao", DG, "Conforme", "Mensal"),
    ("LIDE-05", "e)", "Assegurar os recursos necessários", "CAPEX de submedição (€ 38 000) e VSD aprovados (RG-26-D03); 10% do tempo da equipa", "Ata RG-2026 do SGA; RD-E-2026-01", DG, "Conforme", "Anual"),
    ("LIDE-06", "f)", "Comunicar a importância da gestão eficaz da energia", "Mensagem do DG na reunião geral de setembro; quadro de energia nas naves", "RG-SGE-07 tbl_comunicacao COME-01", DG, "Conforme", "Semestral"),
    ("LIDE-07", "g)", "Assegurar que o SGE atinge os resultados pretendidos", "Revisão pela gestão com a demonstração de melhoria (LBE_Modelo)", "RG-SGE-13", DG, "Parcial", "Anual"),
    ("LIDE-08", "h)", "Promover a melhoria contínua do desempenho energético e do SGE", "Carteira de oportunidades priorizada (16 OPE)", "RG-SGE-04 tbl_oportunidades", DIND, "Conforme", "Trimestral"),
    ("LIDE-09", "i)", "Assegurar a formação de uma equipa de gestão de energia", "Nomeação da equipa (EGE) em 01/07/2026 com 7 membros", "tbl_equipa_energia; ordem de serviço OS-2026-07", DG, "Conforme", "Anual"),
    ("LIDE-10", "j)", "Dirigir e apoiar as pessoas para contribuírem para a eficácia do SGE", "Sugestões de energia com resposta em ≤ 15 dias; reconhecimento trimestral", "RG-SGE-07 tbl_sugestoes", DIND, "Parcial", "Trimestral"),
    ("LIDE-11", "k)", "Apoiar outras funções de gestão a demonstrar liderança nas suas áreas", "Cada gerente é dono de um USE/IDE (RACI)", "tbl_raci", DIND, "Conforme", "Anual"),
    ("LIDE-12", "l)", "Assegurar que os IDE representam apropriadamente o desempenho energético", "Aprovação da LBE-01 com os testes de validade e das reservas (p-valor dos graus-dia)", "RG-SGE-05 LBE_Modelo; tbl_lbe", DG, "Parcial", "Anual"),
    ("LIDE-13", "m)", "Processos para identificar e tratar alterações que afetem o SGE e o desempenho energético", "Checklist de alterações do SGI (PR-SGA-06) com secção de energia; ALE-01", "RG-SGA-18; RG-SGE-05 tbl_alteracoes_lbe", DIND, "Parcial", "Por alteração"),
]

POLITICA = [
    ("POL-E-01", "a) b) e)", "Melhorar continuamente o desempenho energético e o SGE, com objetivos e metas energéticas revistos todos os anos."),
    ("POL-E-02", "c)", "Assegurar a informação e os recursos necessários para atingir os objetivos e as metas energéticas, incluindo a medição dos usos significativos."),
    ("POL-E-03", "d)", "Cumprir os requisitos legais aplicáveis e outros requisitos subscritos relacionados com a eficiência, o uso e o consumo de energia (incluindo o SGCIE)."),
    ("POL-E-04", "f)", "Apoiar a aquisição de produtos e serviços energeticamente eficientes com impacto no desempenho energético, avaliados pelo custo do ciclo de vida."),
    ("POL-E-05", "g)", "Apoiar atividades de projeto que considerem a melhoria do desempenho energético em instalações, equipamentos, sistemas e processos novos ou modificados."),
    ("POL-E-06", "(contexto)", "Contribuir para a descarbonização aumentando a eletricidade renovável e envolvendo trabalhadores, fornecedores e clientes."),
]

EQUIPA = [
    ("EGE-01", GE, "Líder da equipa; representante do SGE junto da gestão de topo; dono do IDE-01/05", 0.5, "Curso ISO 50001 (lead implementer); M&V (IPMVP)", "5.3 a) b) d) e)"),
    ("EGE-02", GMAN, "Manutenção dos USE, compressores e chiller; dono do IDE-02", 0.10, "Eletromecânica; ISO 11011", "5.3 c) e)"),
    ("EGE-03", GPROD, "Controlo operacional da injeção e do sopro; donos dos IDE-03/04", 0.10, "Processo de moldação; standby", "5.3 c)"),
    ("EGE-04", TUTL, "Ar comprimido e frio; rondas; donos dos IDE-06/08", 0.30, "ISO 11011; sistemas de frio", "5.3 c) e)"),
    ("EGE-05", DFIN, "Compra de energia, tarifas, financiamento; dono do IDE-10", 0.05, "Mercado elétrico; LCC", "5.3 c)"),
    ("EGE-06", TI_, "Dados, analisadores e BI (IDE mensais automáticos)", 0.10, "Integração de dados; EN 17267", "5.3 e)"),
    ("EGE-07", GSGA, "Ligação ao SGA (aspetos, GEE, requisitos legais) e à auditoria integrada", 0.05, "ISO 14001; GHG Protocol", "5.3 b)"),
]

# RACI: processo do SGE × funções (R executa, A aprova — 1 por linha, C consultado, I informado)
FUNC_RACI = ["Diretor_Geral", "Diretor_Industrial", "Gestor_Energia", "Gerente_Manutencao", "Gerente_Producao", "Tecnico_Utilidades", "Gestor_SGA",
             "Diretor_Financeiro", "Resp_Compras", "Resp_RD", "Resp_RH", "Gerente_Dados_TI", "Chefes_Turno", "Operadores"]
RACI = [
    ("PE-01", "Contexto, âmbito e fronteiras", "4.1–4.3", "A", "C", "R", "I", "I", "I", "C", "C", "", "", "", "", "", ""),
    ("PE-02", "Política energética e objetivos", "5.2; 6.2", "A", "C", "R", "C", "C", "C", "C", "C", "", "", "", "", "I", "I"),
    ("PE-03", "Revisão energética e USE", "6.3", "I", "A", "R", "C", "C", "R", "C", "", "", "", "", "C", "", ""),
    ("PE-04", "IDE e LBE", "6.4; 6.5", "I", "A", "R", "C", "C", "C", "", "C", "", "", "", "R", "", ""),
    ("PE-05", "Plano de recolha de dados e medição", "6.6; 9.1", "", "A", "R", "R", "", "R", "", "", "", "", "", "R", "", ""),
    ("PE-06", "Competência e consciencialização", "7.2; 7.3", "I", "A", "C", "C", "C", "C", "", "", "", "", "R", "", "R", "I"),
    ("PE-07", "Controlo operacional dos USE", "8.1", "", "A", "C", "R", "R", "R", "", "", "", "", "", "", "R", "R"),
    ("PE-08", "Projeto e aquisições", "8.2; 8.3", "I", "A", "C", "C", "", "", "", "C", "R", "R", "", "", "", ""),
    ("PE-09", "Compra de energia", "8.3 b)", "A", "C", "C", "", "", "", "", "R", "R", "", "", "", "", ""),
    ("PE-10", "Conformidade legal e SGCIE", "9.1.2", "I", "A", "R", "", "", "", "C", "C", "", "", "", "", "", ""),
    ("PE-11", "Desvios significativos e M&V", "9.1.1", "I", "A", "R", "R", "C", "R", "", "", "", "", "", "C", "", ""),
    ("PE-12", "Auditoria interna do SGE", "9.2", "I", "A", "C", "", "", "", "R", "", "", "", "", "", "", ""),
    ("PE-13", "Revisão pela gestão", "9.3", "A", "R", "R", "C", "C", "", "C", "C", "", "", "", "", "", ""),
    ("PE-14", "NC, ação corretiva e melhoria", "10", "I", "A", "R", "R", "R", "R", "C", "", "", "", "", "", "C", ""),
]


def build(out):
    b = Book("RG-SGE-02", "Liderança, Política Energética, Equipa de Gestão de Energia e Responsabilidades",
             activities="Evidenciar a liderança da gestão de topo (5.1 a–m), estabelecer e comunicar a política energética (5.2), nomear a equipa de gestão de energia e atribuir responsabilidades (5.3).",
             clauses="5.1 a)–m); 5.2 a)–g) (disponível como informação documentada, comunicada, disponível às partes interessadas, revista periodicamente); 5.3 a)–e) (equipa de gestão de energia).",
             purpose="Compromissos da liderança com evidência e estado; política energética POL-SGE-01 com a correspondência a 5.2 a–g; equipa de gestão de energia com tempo alocado; "
                     "matriz RACI dos processos do SGE validada por fórmula (um único 'A' por processo).",
             links=[("RG-SGE-05", "Objetivos energéticos ligados aos compromissos POL-E-xx."), ("RG-SGA-08 / RG-SGQ-03", "RACI do SGA e do SGQ (mesma estrutura de colunas)."),
                    ("RG-SGE-13", "Revisão pela gestão (evidência de 5.1 g, l).")],
             guidance=[("ISO 50004:2020 §5", "Papel da equipa de gestão de energia e da gestão de topo; exemplos de política."),
                       ("M-5 Liderança (curso Bureau Veritas)", "Interpretação das alíneas 5.1 a)–m) — as novas face à ISO 50001:2011 são i) equipa, l) IDE e m) alterações."),
                       ("ISO 50005:2021", "Níveis de maturidade para a implementação faseada (usados na autoavaliação do RG-SGE-00).")],
             legal=[("DL 71/2008 (SGCIE)", "A política inclui o compromisso de cumprir o SGCIE (POL-E-03).")])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Estado", ESTADO)
    b.add_list("RACI", ["R", "A", "C", "I"])

    lcols = [col("ID", 8, key="PK", desc="Compromisso."), col("Alinea", 6, desc="Alínea de 5.1."), col("Compromisso", 44, desc="Requisito 5.1."),
             col("Como_Demonstra", 44, desc="Como a gestão de topo demonstra."), col("Evidencia", 30, desc="Evidência."), col("Responsavel", 22, dv="Funcao", desc="Responsável."),
             col("Estado", 9, dv="Estado", desc="Conforme / parcial / lacuna."), col("Frequencia", 11, desc="Frequência.")]
    b.table("Lideranca", "tbl_lideranca", lcols, rows_from(input_names(lcols), LIDERANCA), "Evidências de liderança e compromisso (5.1 a–m) — mesma estrutura do RG-SGQ-03.",
            title="LIDERANÇA E COMPROMISSO DA GESTÃO DE TOPO (5.1 a–m)", cf=[("Estado", {"Conforme": "green", "Parcial": "orange", "Lacuna": "red"})], row_height=36, freeze_col=2)

    ws = b.sheet("Politica_Energetica", "Política energética POL-SGE-01 (5.2) para afixação e publicação.", tab_color="1F4E5F")
    title(ws, "POLÍTICA ENERGÉTICA DA PLASTICOM — POL-SGE-01 rev. 00 (29/09/2026)", f"{EMPRESA} · Aprovada pelo Diretor Geral na revisão pela gestão RD-E-2026-01")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 120
    cell(ws, 4, 1, "", border=False)
    cell(ws, 4, 2, "A Plasticom fabrica embalagens plásticas num processo 100% elétrico. A energia é o nosso primeiro custo ambiental e uma das principais alavancas de "
                   "competitividade e de descarbonização. Por isso, a gestão de topo compromete-se a:", border=False)
    for i, (pid, alin, txt) in enumerate(POLITICA):
        cell(ws, 5 + i, 1, pid, bold=True)
        cell(ws, 5 + i, 2, txt)
    cell(ws, 12, 2, "Esta política é o enquadramento dos objetivos e metas energéticas (RG-SGE-05), é comunicada a todas as pessoas que trabalham para a Plasticom, está disponível "
                    "às partes interessadas (site e a pedido) e é revista anualmente na revisão pela gestão.", border=False)
    for r in range(4, 13):
        ws.row_dimensions[r].height = 32
    pcols = [col("ID_Politica", 9, key="PK", desc="Compromisso da política."), col("Alineas_5_2", 10, desc="Alíneas de 5.2 a que responde."), col("Compromisso", 90, desc="Texto do compromisso."),
             col("N_Objetivos", 9, "int", desc="N.º de objetivos energéticos que lhe dão corpo (RG-SGE-05, à data de referência).")]
    NOBJ = {"POL-E-01": 3, "POL-E-02": 1, "POL-E-03": 1, "POL-E-04": 1}
    b.table("Compromissos", "tbl_politica", pcols, [dict(ID_Politica=p[0], Alineas_5_2=p[1], Compromisso=p[2], N_Objetivos=NOBJ.get(p[0], 0)) for p in POLITICA],
            "Compromissos da política energética (5.2 a–g) — mesmo nome de tabela do RG-SGA-05 (tbl_politica).", row_height=30)
    vcols = [col("Requisito_5_2", 12, key="PK"), col("Texto_Norma", 60), col("Onde_Na_Politica", 20), col("Cumpre", 8, dv="Estado")]
    V52 = [("5.2 a)", "Apropriada ao propósito da organização", "Introdução", "Conforme"), ("5.2 b)", "Enquadramento para objetivos e metas energéticas", "POL-E-01", "Conforme"),
           ("5.2 c)", "Compromisso com a disponibilidade de informação e recursos", "POL-E-02", "Conforme"), ("5.2 d)", "Compromisso de cumprir requisitos legais e outros", "POL-E-03", "Conforme"),
           ("5.2 e)", "Compromisso com a melhoria contínua do desempenho energético e do SGE", "POL-E-01", "Conforme"), ("5.2 f)", "Apoiar a aquisição de produtos e serviços eficientes", "POL-E-04", "Conforme"),
           ("5.2 g)", "Apoiar atividades de projeto que considerem a melhoria do desempenho energético", "POL-E-05", "Conforme"),
           ("5.2 (final)", "Disponível, comunicada, disponível às partes interessadas, revista periodicamente", "Parágrafo final; COME-01", "Parcial")]
    b.table("Verificacao_5_2", "tbl_verif_politica", vcols, [dict(zip(["Requisito_5_2", "Texto_Norma", "Onde_Na_Politica", "Cumpre"], v)) for v in V52],
            "Verificação da política contra 5.2 a–g.", cf=[("Cumpre", {"Conforme": "green", "Parcial": "orange"})], row_height=20)

    ecols = [col("ID_Membro", 8, key="PK", desc="Membro da equipa."), col("Funcao", 34, dv="Funcao", desc="Função."), col("Papel_na_Equipa", 50, desc="Papel e IDE de que é dono."),
             col("Pct_Tempo", 8, "pct", desc="Tempo alocado ao SGE."), col("Competencias", 30, desc="Competências-chave (RG-SGE-07)."), col("Responsabilidades_5_3", 14, desc="Alíneas de 5.3."),
             col("FTE", 7, "num", f='=IF(@ID_Membro@="","",@Pct_Tempo@)', desc="Equivalente a tempo inteiro.")]
    b.table("Equipa_Gestao_Energia", "tbl_equipa_energia", ecols, rows_from(input_names(ecols), EQUIPA),
            "Equipa de gestão de energia (5.1 i, 5.3 a–e) nomeada pela OS-2026-07.", title="EQUIPA DE GESTÃO DE ENERGIA (5.3)",
            subtitle="Reúne mensalmente (2.ª quinta-feira) · Reporta à gestão de topo trimestralmente e na revisão pela gestão (5.3 d)", row_height=30)
    ws = b.wb["Equipa_Gestao_Energia"]
    te = b.tables["tbl_equipa_energia"]
    L_ = te["colmap"]["FTE"]
    cell(ws, te["last"] + 1, 1, "Total FTE", bold=True)
    cell(ws, te["last"] + 1, list(te["colmap"]).index("FTE") + 1, f"=SUM({L_}{te['first']}:{L_}{te['last']})", fmt="0.00", bold=True)

    rcols = [col("ID_Processo", 8, key="PK", desc="Processo do SGE."), col("Processo_SGE", 34, desc="Processo (posição equivalente a Processo_SGA)."), col("Clausula", 10, desc="Cláusula.")]
    rcols += [col(f, 9, dv="RACI", desc=f"RACI da função {f.replace('_', ' ')}.", req=False) for f in FUNC_RACI]
    rcols += [col("N_Aprovadores", 8, "int", f="=0", desc="N.º de 'A'."),
              col("Controlo_RACI", 12, f='=IF(@ID_Processo@="","",IF(@N_Aprovadores@=1,"OK","Rever: 1 aprovador"))', desc="Exatamente um aprovador por processo.")]
    rrows = [dict(zip(["ID_Processo", "Processo_SGE", "Clausula"] + FUNC_RACI, [v if v != "" else None for v in r])) for r in RACI]
    ws = b.table("RACI", "tbl_raci", rcols, rrows, "Matriz RACI dos processos do SGE (5.3) — mesma estrutura do RG-SGA-08 / RG-SGQ-03.",
                 title="MATRIZ RACI DO SGE (5.3)", subtitle="R executa · A aprova (um por processo) · C consultado · I informado",
                 cf=[("Controlo_RACI", {"Rever": "red", "OK": "green"})], row_height=18, freeze_col=3)
    tr = b.tables["tbl_raci"]
    Ln = tr["colmap"]["N_Aprovadores"]
    lastf = get_column_letter(3 + len(FUNC_RACI))
    for k in range(len(RACI)):
        r = tr["first"] + k
        ws[f"{Ln}{r}"] = f'=IF(A{r}="","",COUNTIF(D{r}:{lastf}{r},"A"))'
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
