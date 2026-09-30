"""RG-SGE-03 — Riscos e oportunidades do SGE (6.1.1, 6.1.2).
Fonte única dos riscos do SGI: RG-SGA-02 (tbRiscos / tbOportunidades). Os riscos que já lá existem são referenciados pelo ID (R22, O6...);
os novos riscos de energia (RE-xx / OE-xx) ficam aqui marcados 'Propor inclusão no RG-SGA-02'."""
from sgelib import *
from dimse import *

# (ID, origem SGI, descrição, causa, efeito no SGE, P, I, opção, ação, integração no processo (6.1.2 b1), método de eficácia (6.1.2 b2), KPI, dono, prazo, resultado, plano)
RISCOS = [
    ("R35", "RG-SGA-02 R35", "Incapacidade de demonstrar o desempenho e a eficácia das ações por falta de submedição por processo",
     "Só existe o contador geral; consumos por uso por rateio", "IDE por USE e melhoria não demonstráveis; certificação em risco", 4, 4, "Mitigar",
     "6 analisadores + integração no BI; LBE por USE em 2027", "Plano de recolha de dados (RG-SGE-06)", "KPI-E-01 ≥ 90% e reconciliação ±2% com a fatura", "KPI-E-01", TI_, "2026-12-15", "Parcialmente eficaz", "PA-E-01"),
    ("RE-01", "Novo — propor inclusão no RG-SGA-02", "Não demonstrar melhoria do desempenho energético na auditoria de certificação (ISO 50003:2021)",
     "No ano (mar–dez/2026) a melhoria está dentro da incerteza; só no 4.º trimestre (após as ações) é demonstrada", "Não certificação / constatação maior", 4, 4, "Mitigar",
     "Priorizar ações de retorno rápido (OPE-01, 03, 15) e M&V por ação (opção B) para demonstrar melhoria nos USE", "Planos de ação (RG-SGE-05) e M&V (RG-SGE-11)",
     "Conclusão da LBE_Modelo = 'Melhoria DEMONSTRADA' ou poupanças verificadas por ação > incerteza", "IDE-01", GE, "2027-06-30", "Parcialmente eficaz", "PA-E-02; PA-E-03"),
    ("RE-02", "Novo — propor inclusão no RG-SGA-02", "Não cumprir as metas do PREn (SGCIE: −6% do consumo específico e da intensidade energética até 2030)",
     "Crescimento da produção com máquinas antigas; efeito dos novos produtos no consumo específico", "Incumprimento legal (LEG-08); perda de benefícios", 3, 4, "Mitigar",
     "Acompanhar a trajetória anual no RG-SGE-10 e antecipar OPE-06/OPE-14", "Planeamento de investimentos e REP bienal", "CEE do ano ≤ trajetória linear do PREn", "IDE-02", GE, "2026-10-31", "Por avaliar", "PA-E-04"),
    ("RE-03", "Novo — propor inclusão no RG-SGA-02", "Ultrapassar a potência contratada (1 400 kW) nos meses quentes com as linhas novas",
     "Potência tomada de 1 429 kW em ago/2026 (102% da contratada — risco materializado); calor; arranques simultâneos", "Penalizações e custos de potência; risco de disparo", 4, 3, "Mitigar",
     "Pedido de aumento para 1 550 kW (efetivo 01/2027); alarme a 90% nos analisadores (desde 12/2026); escalonar arranques; deslastre (OPE-16)", "Controlo operacional (RG-SGE-08) e compra de energia (RG-SGE-09)",
     "Nenhum mês com potência tomada > 95% da contratada", "—", DFIN, "2027-05-31", "Não eficaz", "—"),
    ("RE-04", "Novo — propor inclusão no RG-SGA-02", "Alterações de máquinas, moldes ou linhas sem avaliação energética (8.2) invalidam a LBE e aumentam o consumo",
     "Checklist de alterações do SGI sem campos de energia até 09/2026", "LBE desajustada (ALE-01); oportunidades de projeto perdidas", 4, 3, "Mitigar",
     "Secção de energia obrigatória na checklist do PR-SGA-06 e critérios de projeto do PR-SGE-07", "Planeamento de alterações (RG-SGA-18)", "100% das alterações de 2027 com avaliação energética", "—", DIND, "2026-12-31", "Por avaliar", "—"),
    ("RE-05", "Novo — propor inclusão no RG-SGA-02", "Dependência do Gestor de Energia (conhecimento concentrado numa pessoa)",
     "Equipa nova (07/2026); métodos só no Excel do gestor", "Paragem do SGE em caso de saída", 2, 3, "Mitigar",
     "Procedimentos PR-SGE-01 a 12 e substituto formado (Técnico de Utilidades)", "Competência (RG-SGE-07)", "Substituto com competência avaliada 'Autónomo'", "—", RH_, "2027-03-31", "Por avaliar", "—"),
    ("RE-06", "Novo — propor inclusão no RG-SGA-02", "Dados de energia com erros (leituras, rateio, fatores) levam a decisões erradas",
     "Rateio por fatores fixos (AR_FRAC); campanha curta", "IDE enganadores (ex.: IDE-07 constante)", 3, 3, "Mitigar",
     "Classificar a qualidade de cada dado (EN 17267) e reconciliar mensalmente com a fatura", "Plano de recolha de dados (RG-SGE-06)", "0 IDE com qualidade 'Estimado' nos USE em 2027", "KPI-E-01", GE, "2027-03-31", "Por avaliar", "PA-E-01"),
    ("RE-07", "Novo — propor inclusão no RG-SGA-02", "Aumento da procura de ar (fugas, linhas novas) anula a poupança dos compressores VSD",
     "Fugas 25% (jun) → 14% (dez/2026); novas máquinas", "Poupança medida na central não aparece na fatura", 2, 3, "Mitigar",
     "Programa de fugas (PA-E-02) e medição mensal de Nm³ (EQP-04)", "Controlo operacional do ar (RG-SGE-08)", "Nm³ por mil unidades estável ou a descer", "IDE-08", TUTL, "2027-06-30", "Eficaz", "PA-E-02"),
    ("R25", "RG-SGA-02 R25", "Volatilidade do preço da energia e dos polímeros comprime a margem", "Mercado ibérico; geopolítica", "Custo das ações de eficiência muda o retorno", 3, 4, "Mitigar",
     "Contratos a prazo; eficiência; UPAC", "Compra de energia (RG-SGE-09)", "Preço médio €/kWh vs orçamento", "—", DFIN, "2027-12-31", "Por avaliar", "PA-E-07"),
    ("R22", "RG-SGA-02 R22", "Falta de ar comprimido interrompe máquinas", "Avaria de compressor", "Arranques e purgas extra (energia e scrap)", 2, 4, "Mitigar",
     "Compressor em reserva e chaveamento (PCN-UTIL-01)", "Manutenção", "0 paragens por falta de ar", "—", GMAN, "Contínuo", "Eficaz", "—"),
    ("R34", "RG-SGA-02 R34", "Alterações climáticas e calor reduzem a resiliência (arrefecimento)", "Ondas de calor", "Mais consumo do frio; potência", 3, 3, "Mitigar",
     "Free-cooling e setpoint mais alto; normalização por graus-dia", "Revisão energética e IDE", "IDE-06 normalizado", "IDE-06", TUTL, "2027-12-31", "Por avaliar", "PA-E-06"),
    ("R39", "RG-SGA-02 R39", "Reclamação por ruído dos compressores novos instalados sem avaliação atualizada", "Alteração sem avaliação (6.3 SGA)", "Lição para o 8.2: avaliar energia e ruído no projeto", 3, 2, "Mitigar",
     "Tratado pelo SGA (NC-SGA-26-01); no SGE: critérios de projeto (PR-SGE-07)", "Projeto (RG-SGE-09)", "Checklist de projeto aplicada", "—", DIND, "2026-12-31", "Por avaliar", "—"),
]
OPORT = [
    ("O6", "RG-SGA-02 O6", "Eficiência energética com submedição e deteção de fugas de ar comprimido", "Beneficiar de dados reais para priorizar", 4, 4, "Explorar", "PA-E-01; PA-E-02", "Poupança verificada (MWh)", "IDE-08", GE, "Por avaliar"),
    ("O15", "RG-SGA-02 O15", "Autoconsumo fotovoltaico e eletricidade com garantia de origem", "Descarbonizar e reduzir o custo", 4, 4, "Explorar", "PA-E-07", "Quota renovável (IDE-10)", "IDE-10", DFIN, "Por avaliar"),
    ("OE-01", "Novo — propor inclusão no RG-SGA-02", "Financiamento (Portugal 2030 / Fundo Ambiental) para submedição, servo-bombas e UPAC", "Reduzir o retorno", 3, 3, "Explorar", "RG-26-D03", "Montante aprovado (€)", "—", DFIN, "Por avaliar"),
    ("OE-02", "Novo — propor inclusão no RG-SGA-02", "Certificação ISO 50001 dispensa a auditoria energética periódica da Diretiva (UE) 2023/1791 (art. 11.º)", "Evitar custos de auditoria e ganhar reputação", 3, 3, "Explorar",
     "Certificação 2027", "Certificado emitido", "—", DG, "Por avaliar"),
    ("OE-03", "Novo — propor inclusão no RG-SGA-02", "Dados de energia por máquina/SKU como vantagem comercial (PCF para clientes)", "Diferenciação em cosmética e alimentar", 3, 3, "Explorar", "PA-E-01",
     "N.º de clientes com PCF entregue", "—", GE, "Por avaliar"),
    ("OE-04", "Novo — propor inclusão no RG-SGA-02", "Deslocar cargas flexíveis (moagem, carga de empilhadores) para vazio/super vazio", "Reduzir o custo sem mudar o consumo", 3, 2, "Explorar", "—",
     "Quota de kWh em ponta (RG-SGE-09)", "—", GPROD, "Por avaliar"),
]


def build(out):
    b = Book("RG-SGE-03", "Riscos e Oportunidades do SGE",
             activities="Determinar os riscos e oportunidades que é preciso tratar para que o SGE atinja os resultados pretendidos (incluindo a melhoria do desempenho energético), prevenir efeitos "
                        "indesejáveis e melhorar continuamente; planear as ações, a sua integração nos processos e a avaliação da eficácia.",
             clauses="6.1.1 (considerar 4.1, 4.2 e rever as atividades que afetam o desempenho energético); 6.1.2 a) ações; b) 1) integrar nos processos do SGE e do desempenho energético; 2) avaliar a eficácia.",
             purpose="Vista do registo corporativo de riscos (RG-SGA-02) com a lente da energia + 7 riscos e 4 oportunidades novos do SGE, avaliados por P × I (1–5), com tratamento, integração, "
                     "método e resultado da avaliação da eficácia.",
             links=[("RG-SGA-02", "Fonte única dos riscos do SGI: os RE-/OE- devem ser incluídos lá na próxima revisão (propostos)."),
                    ("RG-SGE-01", "Questões de contexto (CTX-E-xx) e partes interessadas que originam os riscos."), ("RG-SGE-05", "Planos de ação (PA-E-xx).")],
             guidance=[("ISO 31000:2018", "Processo de gestão do risco (identificar, analisar, avaliar, tratar, monitorizar)."),
                       ("ISO 50004:2020 §6.1", "Exemplos de riscos e oportunidades de energia (preço, fornecimento, dados, alterações)."),
                       ("M-6 Planejamento (curso Bureau Veritas)", "Figura A.2 da ISO 50001: planeamento energético → riscos, revisão energética, IDE, LBE, objetivos.")],
             legal=[("DL 71/2008 (SGCIE)", "Risco RE-02 (metas do PREn)."), ("Diretiva (UE) 2023/1791, art. 11.º", "Oportunidade OE-02.")])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Opcao", ["Mitigar", "Evitar", "Transferir", "Aceitar", "Explorar", "Partilhar", "Realçar"])
    b.add_list("Escala", [1, 2, 3, 4, 5])
    b.add_list("Eficacia", ["Eficaz", "Parcialmente eficaz", "Não eficaz", "Por avaliar"])

    rcols = [col("ID_Risco", 8, key="PK", desc="Risco (R = RG-SGA-02; RE = novo do SGE)."), col("Origem_SGI", 20, desc="Onde está no registo corporativo."),
             col("Descricao", 44, desc="Risco."), col("Causa", 32, desc="Causa."), col("Efeito_no_SGE", 32, desc="Efeito nos resultados do SGE / desempenho energético."),
             col("Probabilidade", 7, "int", dv="Escala", desc="1–5."), col("Impacto", 7, "int", dv="Escala", desc="1–5."),
             col("Score", 6, "int", f='=IF(@ID_Risco@="","",@Probabilidade@*@Impacto@)', desc="P × I."),
             col("Nivel", 9, f='=IF(@ID_Risco@="","",IF(@Score@>=15,"Crítico",IF(@Score@>=10,"Alto",IF(@Score@>=5,"Médio","Baixo"))))', desc="Crítico ≥ 15 · Alto ≥ 10 · Médio ≥ 5."),
             col("Opcao_Tratamento", 10, dv="Opcao", desc="Opção de tratamento (ISO 31000)."), col("Acao", 40, desc="Ação (6.1.2 a)."),
             col("Integracao_Processo", 28, desc="Integração nos processos do SGE (6.1.2 b 1)."), col("Metodo_Eficacia", 36, desc="Como se avalia a eficácia (6.1.2 b 2)."),
             col("KPI", 8, desc="Indicador.", key="FK → RG-SGE-05 tbl_kpi", req=False), col("Dono", 22, dv="Funcao", desc="Dono."), col("Prazo", 11, desc="Prazo."),
             col("Resultado_Eficacia", 12, dv="Eficacia", desc="Resultado da avaliação."), col("ID_Plano", 12, desc="Plano de ação.", req=False)]
    b.table("Riscos_SGE", "tbl_riscos_e", rcols, rows_from(input_names(rcols), RISCOS), "Riscos do SGE (6.1) — vista do RG-SGA-02 + novos.",
            title="RISCOS DO SGE (6.1)", subtitle="R = já no registo corporativo RG-SGA-02 (fonte única) · RE = novo, proposto para inclusão no RG-SGA-02",
            cf=[("Nivel", {"Crítico": "red", "Alto": "orange", "Médio": "yellow", "Baixo": "green"}), ("Resultado_Eficacia", {"Não eficaz": "red", "Eficaz": "green", "Por avaliar": "gray"})],
            row_height=48, freeze_col=2)
    ocols = [col("ID_Oport", 8, key="PK", desc="Oportunidade (O = RG-SGA-02; OE = nova)."), col("Origem_SGI", 20, desc="Registo corporativo."), col("Descricao", 44, desc="Oportunidade."),
             col("Beneficio", 30, desc="Benefício esperado."), col("Probabilidade", 7, "int", dv="Escala", desc="1–5."), col("Beneficio_1a5", 7, "int", dv="Escala", desc="1–5."),
             col("Score", 6, "int", f='=IF(@ID_Oport@="","",@Probabilidade@*@Beneficio_1a5@)', desc="P × B."),
             col("Nivel", 9, f='=IF(@ID_Oport@="","",IF(@Score@>=12,"Alta",IF(@Score@>=6,"Média","Baixa")))', desc="Relevância."),
             col("Decisao", 9, dv="Opcao", desc="Decisão."), col("Acao_Plano", 20, desc="Ação / plano."), col("Metodo_Eficacia", 30, desc="Como se avalia."),
             col("KPI", 8, desc="Indicador.", req=False), col("Dono", 22, dv="Funcao", desc="Dono."), col("Resultado_Eficacia", 12, dv="Eficacia", desc="Resultado.")]
    b.table("Oportunidades_SGE", "tbl_oport_e", ocols, rows_from(input_names(ocols), OPORT), "Oportunidades do SGE (6.1) — distintas das oportunidades técnicas da revisão energética (RG-SGE-04).",
            title="OPORTUNIDADES DO SGE (6.1)", subtitle="Oportunidades do sistema; as oportunidades de melhoria do desempenho energético (OPE-xx, 6.3 d) estão no RG-SGE-04",
            cf=[("Nivel", {"Alta": "green", "Média": "yellow", "Baixa": "gray"})], row_height=40, freeze_col=2)

    ws = b.sheet("Matriz_Risco", "Mapa de calor P × I calculado a partir de tbl_riscos_e.", tab_color="C00000")
    title(ws, "MAPA DE CALOR DOS RISCOS DO SGE — calculado", "N.º de riscos por probabilidade (linhas) × impacto (colunas)")
    header_row(ws, 3, ["P \\ I", "1", "2", "3", "4", "5"], widths=[10, 8, 8, 8, 8, 8])
    for i, p_ in enumerate(range(5, 0, -1)):
        r = 4 + i
        cell(ws, r, 1, p_, bold=True)
        for j, imp in enumerate(range(1, 6)):
            c_ = cell(ws, r, 2 + j, f"=COUNTIFS(tbl_riscos_e[Probabilidade],{p_},tbl_riscos_e[Impacto],{imp})", fmt="0")
            sc = p_ * imp
            colr = "red" if sc >= 15 else "orange" if sc >= 10 else "yellow" if sc >= 5 else "green"
            c_.fill = PatternFill("solid", fgColor=CF_COLORS[colr][0])
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
