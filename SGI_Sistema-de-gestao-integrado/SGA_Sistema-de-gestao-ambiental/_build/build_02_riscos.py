import datetime as dt
from sgalib import *
from dims import *

D0 = dt.date(2026, 4, 14)   # workshop de riscos e oportunidades

DECISOES = ["R - Assumir o Risco", "R - Monitorizar o Risco", "R - Mitigar o Risco", "R - Eliminar a fonte do Risco",
            "R - Transferir o Risco", "O - Aceitar a Oportunidade", "O - Monitorizar a Oportunidade",
            "O - Reter oportunidade para avaliação futura", "O - Estudar a viabilidade e custo-benefício",
            "O - Desenvolver ações para perseguir a Oportunidade", "O - Integrar no Planeamento Estratégico"]

# (ID, Origem, ID_Origem, Sel, Tipo, Descricao, Causa, Consequencia, Proveniente, Area, Processo, Tema, Parte, Controlos,
#  Prob, Sev, Decisao, Acao, TipoAcao, ID_PAM, Resp, Prazo, Estado, ProbRes, SevRes, KRI, IDCorp, Forcado, Notas)
# IDCorp = linha equivalente no registo corporativo gestao-riscos-oportunidades-v3.6-Plasticom (após a consolidação de 24/09/2026)
RO = [
    ("RO-01", "SWOT_Força", "SWT-F01", "Sim", "Oportunidade",
     "Usar a cultura e a infraestrutura de dados industriais (OEE, SPC, rastreabilidade, Power BI) para criar um painel ambiental por máquina, turno e lote.",
     "18 meses de dados de produção já estruturados; equipa com competências de análise de dados.",
     "Decisões ambientais baseadas em dados; identificação rápida de desvios; resposta a questionários ESG de clientes.",
     "Novo", "Gestão Ambiental", "GER", "Governação e dados", "Acionistas / Gerência; clientes",
     "Dashboards de produção e qualidade existentes; nenhum indicador ambiental integrado.",
     "Frequente", "Muito Bom", "O - Desenvolver ações para perseguir a Oportunidade",
     "Integrar no Power BI industrial os consumos de energia, água, resíduos (por código LER) e solventes, com modelo de dados comum (máquina, turno, lote, mês) e relatório mensal automático.",
     "M", "PAM-26-09", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-12-31", "Em curso", "Frequente", "Muito Bom",
     "% KPIs ambientais com carregamento automático (meta ≥ 80%)", "O3", "Não",
     "Oportunidade SIGNIFICATIVA (nível 9). Depende da submedição do RO-02 para dados por processo."),
    ("RO-02", "SWOT_Fraqueza", "SWT-W01", "Sim", "Risco",
     "Incapacidade de demonstrar o desempenho ambiental e a eficácia das ações de eficiência por falta de submedição de energia e água por processo.",
     "Só existem os contadores gerais da fatura (eletricidade e água); consumos por processo são estimados.",
     "Metas de energia/água não verificáveis; não conformidade com 9.1.1 (avaliar desempenho e eficácia); poupanças não capturadas; resposta fraca a clientes.",
     "Novo", "Equipamentos e Infraestruturas", "UTL", "Energia", "Acionistas / Gerência; clientes; auditor de certificação",
     "Leitura mensal das faturas; estimativas por horas de marcha.",
     "Frequente", "Sério", "R - Mitigar o Risco",
     "Instalar 6 analisadores de energia (Injeção, Sopro, Decoração, Compressores, Arrefecimento, Geral) e 3 contadores de água com telemetria; rotina mensal de validação dos dados.",
     "M", "PAM-26-02", "Gerente de Manutenção", "2026-12-31", "Em curso", "Remota", "Sério",
     "% do consumo total de eletricidade com submedição (meta ≥ 90%)", "R35", "Não",
     "Risco SIGNIFICATIVO (nível -6). Transferido para o PAM na Atividade 3.5 (ação 02/26)."),
    ("RO-03", "SWOT_Oportunidade", "SWT-O01", "Sim", "Oportunidade",
     "Captar clientes europeus que procuram embalagens recicláveis com conteúdo reciclado, impulsionados pelo PPWR (Reg. (UE) 2025/40).",
     "Aplicação do PPWR desde 12/08/2026 e metas de conteúdo reciclado para 2030; pedidos de clientes em 2026.",
     "Aumento de vendas de gamas PCR e de famílias redesenhadas para reciclagem; diferenciação comercial.",
     "Novo", "Gestão Comercial", "RD", "Produto / embalagem", "Clientes europeus",
     "Experiência com HDPE-PCR e rPET; sem avaliação formal de reciclabilidade por família.",
     "Provável", "Muito Bom", "O - Estudar a viabilidade e custo-benefício",
     "Estudo de mercado e de custo do PCR certificado por família de produto antes de decidir o investimento.",
     "—", "", "Responsável de R&D", "2027-03-31", "Planeada", "Provável", "Muito Bom",
     "N.º de pedidos de cotação com requisito de PCR/reciclabilidade", "O5", "Não",
     "Nível 6 = TOLERÁVEL (não significativo): não exige ação obrigatória; decisão de estudo."),
    ("RO-04", "SWOT_Ameaça", "SWT-T01", "Sim", "Risco",
     "Ondas de calor e escassez hídrica aumentam o consumo de água e energia do arrefecimento e podem causar restrições de água ou paragens.",
     "Alterações climáticas; torre de arrefecimento aberta com perdas por evaporação e purga.",
     "Aumento do consumo específico de água e energia no verão; defeitos por arrefecimento insuficiente; risco de paragem em restrição de água.",
     "Novo", "Gestão Estratégica", "UTL", "Clima / GEE", "Vizinhança / comunidade local; entidade gestora da água",
     "Chiller e torre de arrefecimento com manutenção preventiva; sem reserva de água.",
     "Provável", "Sério", "R - Monitorizar o Risco",
     "Monitorizar m³/1.000 un normalizado pela temperatura (KPI-02) e avaliar circuito fechado no objetivo OBJ-05.",
     "—", "", "Diretor Industrial", "2027-06-30", "Planeada", "Provável", "Menor",
     "m³ de água por 1.000 un vs temperatura média mensal", "R34", "Não",
     "Nível -4 = TOLERÁVEL: monitorizar. Reavaliar após o verão de 2026."),
    ("RO-05", "SWOT_Fraqueza", "SWT-W02", "Não", "Risco",
     "Lotes de resina fora de especificação e declarações de conteúdo reciclado não verificadas de fornecedores spot (SUP-005) e de PCR.",
     "Compras spot sem avaliação ambiental; volatilidade do mercado de PCR.",
     "Mais scrap e energia desperdiçada; alegações ambientais incorretas a clientes (Diretiva (UE) 2024/825).",
     "Sim", "Compras e Fornecedores", "CMP", "Cadeia de valor / fornecedores", "Clientes europeus; fornecedores",
     "Inspeção de receção de qualidade; sem critérios ambientais.",
     "Frequente", "Sério", "R - Mitigar o Risco",
     "Aplicar a avaliação ambiental de fornecedores (RG-SGA-11) aos fornecedores críticos de resina e exigir certificação de conteúdo reciclado.",
     "M", "PAM-26-16", "Responsável de Compras", "2026-12-31", "Em curso", "Provável", "Menor",
     "% compras de resina a fornecedores avaliados (meta ≥ 90%)", "R36", "Não", ""),
    ("RO-06", "PESTEL", "PES-12", "Não", "Risco",
     "Incumprimento das obrigações do PPWR (documentação técnica, declaração UE de conformidade, substâncias preocupantes) desde 12/08/2026.",
     "Requisitos novos; dossier técnico existente só para 40% das famílias.",
     "Impossibilidade de colocar embalagens no mercado UE, coimas e perda de clientes.",
     "Sim", "Gestão Comercial", "RD", "Legal / conformidade", "Clientes europeus; autoridades",
     "Fichas técnicas de produto e declarações de contacto alimentar (linha alimentar).",
     "Frequente", "Crítico", "R - Mitigar o Risco",
     "Concluir documentação técnica e declaração UE de conformidade para 100% das famílias (OBJ-04).",
     "C2", "PAM-26-10", "Responsável de R&D", "2026-12-31", "Em curso", "Remota", "Crítico",
     "% famílias com declaração UE de conformidade PPWR", "R33", "Não", "Ver LEG-09 (NC) no RG-SGA-04."),
    ("RO-07", "PESTEL", "PES-11", "Não", "Risco",
     "Perdas de granulado de plástico na descarga de silos e big bags chegam à rede pluvial e ao meio aquático.",
     "Descarga de big bags ao ar livre; sarjetas sem filtros; limpeza a seco não sistemática.",
     "Poluição por microplásticos; não conformidade com o regulamento europeu de granulados; dano reputacional.",
     "Novo", "Gestão Ambiental", "REC", "Perdas de granulado (microplásticos)", "Vizinhança / comunidade local; ONG; autoridades",
     "Varrimento diário da zona de silos.",
     "Provável", "Crítico", "R - Mitigar o Risco",
     "Programa Operation Clean Sweep: filtros nas sarjetas, bacias de descarga, kits de recolha e inspeção semanal do perímetro.",
     "M", "PAM-26-11", "Gestor do SGA / EHS (Responsável Ambiental)", "2027-03-31", "Em curso", "Remota", "Sério",
     "kg de granulado recolhido nos pontos de contenção / mês", "R37", "Não", ""),
    ("RO-08", "PESTEL", "PES-10", "Não", "Risco",
     "Incêndio no armazém de matérias-primas com libertação de fumos e águas de combate contaminadas para a rede pluvial e a floresta envolvente.",
     "Grande carga de incêndio (granulado e embalagem); proximidade ao Pinhal de Leiria.",
     "Contaminação do solo e da água; dano a ecossistemas florestais; paragem prolongada.",
     "Sim", "Equipamentos e Infraestruturas", "REC", "Emergência", "Vizinhança / comunidade local; bombeiros; seguradora",
     "Medidas de autoproteção (SCIE), deteção automática, válvula de corte na rede pluvial, simulacro anual.",
     "Remota", "Crítico", "R - Transferir o Risco",
     "Manter seguro multirriscos e rever o plano de retenção de águas de combate no simulacro de 2026.",
     "—", "", "Diretor Industrial", "2026-11-30", "Planeada", "Remota", "Sério",
     "Tempo de fecho da válvula de corte em simulacro (meta ≤ 5 min)", "R38", "Não", "Ver EMG-02 no RG-SGA-12."),
    ("RO-09", "SWOT_Oportunidade", "SWT-O02", "Não", "Oportunidade",
     "Autoconsumo fotovoltaico na cobertura e eletricidade com garantia de origem renovável.",
     "≈ 9.000 m² de cobertura disponível; processo 100% elétrico.",
     "Redução das emissões do âmbito 2 e do custo de energia.",
     "Novo", "Gestão Estratégica", "UTL", "Energia", "Acionistas / Gerência; clientes",
     "Contrato de eletricidade com 55% de origem renovável (rótulo do comercializador).",
     "Provável", "Muito Bom", "O - Estudar a viabilidade e custo-benefício",
     "Estudo de viabilidade de UPAC (≈ 1 MWp) com candidatura a financiamento.",
     "—", "", "Diretor Financeiro", "2027-03-31", "Planeada", "Provável", "Muito Bom",
     "% energia renovável", "O15", "Não", ""),
    ("RO-10", "SWOT_Fraqueza", "SWT-W04", "Não", "Risco",
     "Derrame de tintas, solventes ou óleos não contido por kits vazios ou falta de bacias de retenção.",
     "Kits de derrame sem registo de utilização nem stock mínimo; bidões fora de bacia.",
     "Contaminação do solo e da água; resíduos perigosos; NC legal.",
     "Sim", "Gestão Ambiental", "ARQ", "Produtos químicos", "Autoridades; trabalhadores",
     "Kits de derrame distribuídos; FDS disponíveis.",
     "Provável", "Crítico", "R - Mitigar o Risco",
     "Rever IT-SGA-01, stock mínimo de kits, selo numerado e verificação semanal do conteúdo (ver NC-SGA-26-03).",
     "C2", "PAM-26-05", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-10-31", "Em curso", "Remota", "Sério",
     "% kits completos e selados nas rondas", "R30", "Não", ""),
    ("RO-11", "SWOT_Força", "SWT-F03", "Não", "Oportunidade",
     "Aumentar a reintegração interna de scrap limpo (regrind) segregado por polímero e cor.",
     "Moinhos junto às máquinas; scrap misturado reduz a taxa de reintegração.",
     "Menos polímero virgem e menos resíduos plásticos enviados para fora.",
     "Sim", "Produção", "MOA", "Materiais e circularidade", "Acionistas / Gerência",
     "Reintegração pontual decidida pelo chefe de turno.",
     "Frequente", "Bom", "O - Integrar no Planeamento Estratégico",
     "Integrar no objetivo OBJ-02 (scrap) com segregação na fonte por cor/polímero.",
     "—", "", "Gerente de Produção", "2027-06-30", "Planeada", "Frequente", "Bom",
     "% scrap reintegrado", "O10", "Não", ""),
    ("RO-12", "Obrigação de conformidade", "LEG-05", "Não", "Risco",
     "Reclamação da vizinhança por ruído dos novos compressores instalados em 2026 sem avaliação acústica atualizada.",
     "Alteração de equipamento sem avaliação de ruído no recetor (falha de gestão da mudança 6.3).",
     "Incumprimento do RGR; reclamação e coima.",
     "Novo", "Equipamentos e Infraestruturas", "UTL", "Ruído", "Vizinhança / comunidade local",
     "Compressores em sala fechada; última avaliação acústica em 2023.",
     "Provável", "Sério", "R - Mitigar o Risco",
     "Avaliação acústica por laboratório acreditado (C1) e gatilho de avaliação de ruído no controlo de mudanças (C2).",
     "C1", "PAM-26-03", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-10-31", "Em curso", "Remota", "Menor",
     "N.º reclamações de ruído", "R39", "Não", ""),
]


# IDs relacionados no registo corporativo (coluna 'Riscos / oport. relacionados (IDs)' da linha equivalente)
REL_CORP = {"RO-01": "R19;R26", "RO-02": "O6;R25", "RO-03": "R33;R14", "RO-04": "R32;O6", "RO-05": "R13;R14;O7",
            "RO-06": "O5;R14", "RO-10": "R29;R31", "RO-11": "R31"}
CORP_FILE = "gestao-riscos-oportunidades-v3.6-Plasticom.xlsx"

# critérios da metodologia do curso (lidos pelas fórmulas através de nomes definidos)
CRIT_P = [("Remota", 1, "Pouco provável de ocorrer no horizonte de 1 ano; sem histórico na Plasticom."),
          ("Provável", 2, "Pode ocorrer no horizonte de 1 ano; já ocorreu no setor ou pontualmente na Plasticom."),
          ("Frequente", 3, "Ocorre ou é esperado ocorrer várias vezes por ano / condição permanente.")]
CRIT_SR = [("Menor", -1, "Efeito reduzido e reversível, contido no local; sem implicação legal."),
           ("Sério", -2, "Efeito relevante num objetivo ou indicador; potencial reclamação ou desvio legal menor."),
           ("Crítico", -3, "Dano ambiental relevante, incumprimento legal, perda de clientes ou paragem.")]
CRIT_SO = [("Suficiente", 1, "Benefício ambiental/de negócio limitado ou local."),
           ("Bom", 2, "Benefício relevante num processo ou num indicador."),
           ("Muito Bom", 3, "Benefício relevante para vários processos, clientes ou objetivos estratégicos.")]
CRIT_SIG = [("Risco", "-6, -9", -6, "SIGNIFICATIVO — NÃO ACEITÁVEL → decisão e ação de tratamento obrigatórias", "crit_Lim_R_Sig"),
            ("Risco", "-3, -4", -3, "TOLERÁVEL — ACEITÁVEL → monitorizar / controlos existentes", "crit_Lim_R_Tol"),
            ("Risco", "-1, -2", -1, "BAIXO — ACEITÁVEL → assumir o risco", None),
            ("Oportunidade", "9", 9, "SIGNIFICATIVO — AÇÃO REQUERIDA → desenvolver ações / integrar no planeamento", "crit_Lim_O_Sig"),
            ("Oportunidade", "3, 4, 6", 3, "TOLERÁVEL — ACEITÁVEL → estudar viabilidade / reter", "crit_Lim_O_Tol"),
            ("Oportunidade", "1, 2", 1, "BAIXO — ACEITÁVEL → monitorizar", None)]


class BookRO(Book):
    """Book com a secção de critérios escrita na folha Listas (substitui a antiga folha Criterios)."""

    def _write_lists(self):
        super()._write_lists()
        ws = self.wb["Listas"]
        self.sheets_info[-1] = ("Listas", "Domínios (listas de valores) da validação de dados e, abaixo, os CRITÉRIOS P × S do curso "
                                          "(escalas e limites de significância) lidos pelas fórmulas — substitui a antiga folha Criterios.")
        r = 3 + max(len(v) for v in self.lists.values()) + 2
        ws.cell(row=r, column=1, value="CRITÉRIOS DE AVALIAÇÃO DE RISCOS E OPORTUNIDADES — Nível = P × S (lidos pelas fórmulas; "
                                       "alterar aqui altera a classificação)").font = F_BOLD
        for c in range(1, 8):
            ws.cell(row=r, column=c).fill = FILL_BAND
        ws.cell(row=r + 1, column=1, value="Fonte: METODOLOGIA DE AVALIAÇÃO DE RISCOS E OPORTUNIDADES (UC00557, OA 3.1). Equivalente 1–5 = "
                                           "|valor| + 1: conversão usada no registo corporativo (escala 5×5).").font = F_SUB
        r += 3
        for title, data, nm in (("PROBABILIDADE (P)", CRIT_P, "P"), ("SEVERIDADE (S) — RISCOS", CRIT_SR, "SR"),
                                ("SEVERIDADE (S) — OPORTUNIDADES", CRIT_SO, "SO")):
            ws.cell(row=r, column=1, value=title).font = F_BOLD
            header_row(ws, r + 1, ["Nível", "Valor", "Equivalente 1–5", "Descrição"])
            for k, (lv, val, desc) in enumerate(data):
                rr = r + 2 + k
                for c, v in enumerate((lv, val, f"=ABS(B{rr})+1", desc), start=1):
                    cell = ws.cell(row=rr, column=c, value=v)
                    cell.font, cell.border = F_BASE, BORDER
            self.wb.defined_names[f"crit_{nm}_Nivel"] = DefinedName(f"crit_{nm}_Nivel", attr_text=f"Listas!$A${r + 2}:$A${r + 4}")
            self.wb.defined_names[f"crit_{nm}_Valor"] = DefinedName(f"crit_{nm}_Valor", attr_text=f"Listas!$B${r + 2}:$B${r + 4}")
            r += 6
        ws.cell(row=r, column=1, value="SIGNIFICÂNCIA").font = F_BOLD
        header_row(ws, r + 1, ["Tipo", "Níveis (P×S)", "Limite", "Classificação — aceitabilidade / resposta"])
        for k, (tp, lv, lim, txt, nm) in enumerate(CRIT_SIG):
            rr = r + 2 + k
            for c, v in enumerate((tp, lv, lim, txt), start=1):
                cell = ws.cell(row=rr, column=c, value=v)
                cell.font, cell.border = F_BASE, BORDER
            if nm:
                self.wb.defined_names[nm] = DefinedName(nm, attr_text=f"Listas!$C${rr}")
        r += 2 + len(CRIT_SIG) + 1
        ws.cell(row=r, column=1, value="Nota do enunciado").font = F_BOLD
        ws.cell(row=r, column=2, value="Se nenhum dos 4 itens da Atividade 3.1 resultasse em SIGNIFICATIVO, forçar P ou S e marcar "
                                       "Simulacao_Forcada = Sim. Não foi necessário: RO-01 (9) e RO-02 (-6) são significativos com "
                                       "valores realistas.").font = F_BASE


def build(out):
    b = BookRO("RG-SGA-02", "Gestão de Riscos e Oportunidades do SGA — Identificação e Avaliação",
               version="02", date=dt.date(2026, 9, 24),
               activities="Atividade 3.1 — Aplicação da Matriz de Riscos e Planeamento de Ações (4 itens da SWOT: RO-01 a RO-04; "
                          "filtrar Selecionado_Atv_3_1 = Sim em Riscos e Oportunidades, ou ver Resumo_Atividade_3_1).",
               clauses="6.1.1; 6.1.4 Riscos e oportunidades; 6.1.5 Planeamento de ações (numeração ISO 14001:2026)",
               purpose=("Avaliar a significância dos riscos e oportunidades do SGA com a metodologia do curso (Nível = P × S; P 1-3; S -1 a -3 "
                        "para riscos e 1 a 3 para oportunidades) e registar a decisão e a ação de tratamento. Revisão 02: a antiga Matriz_RO "
                        "foi dividida em Riscos (tbl_riscos) e Oportunidades (tbl_oportunidades), os critérios passaram para a folha Listas e o "
                        "mapa de calor para o Resumo_Atividade_3_1 — a mesma estrutura do registo corporativo " + CORP_FILE + ", onde "
                        "cada item tem uma linha equivalente (ID_Registo_Corporativo) com a avaliação 5×5, o risco inerente, o critério de "
                        "eficácia e o BowTie."),
               links=[("RG-SGA-01 Contexto", "ID_Origem aponta para o item SWOT/PESTEL de origem."),
                      ("RG-SGA-06 PAM", "ID_PAM aponta para a ação no Plano de Ações de Melhoria (Mod.G.10.00); o PAM usa o ID_RO."),
                      (CORP_FILE, "Registo corporativo multiárea (qualidade, SST, ambiente). ID_Registo_Corporativo = linha equivalente "
                                  "(R30, R33 a R39; O3, O5, O10, O15); IDs_Relacionados_Corporativo = outros riscos/oportunidades ligados.")])
    b.add_list("Origem", ["SWOT_Força", "SWOT_Fraqueza", "SWOT_Oportunidade", "SWOT_Ameaça", "PESTEL", "Aspeto ambiental",
                          "Obrigação de conformidade", "Parte interessada", "Incidente / NC", "Auditoria"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("Proveniente", ["Sim", "Não", "Novo", "Alterada"])
    b.add_list("AreaGestao", ["Gestão Estratégica", "Gestão Ambiental", "Produção", "Recursos Humanos", "Gestão Comercial",
                              "Equipamentos e Infraestruturas", "Compras e Fornecedores", "Qualidade"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Tema", TEMAS)
    b.add_list("DecisaoRisco", [d for d in DECISOES if d.startswith("R")])
    b.add_list("DecisaoOportunidade", [d for d in DECISOES if d.startswith("O")])
    b.add_list("TipoAcao", ["C1", "C2", "M", "—"])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("EstadoAcao", ["Planeada", "Em curso", "Concluída", "Cancelada"])

    def cols_for(kind):
        risk = kind == "R"
        sv = "SR" if risk else "SO"
        P = '=IF(@{0}@="","",IFERROR(INDEX(crit_P_Valor,MATCH(@{0}@,crit_P_Nivel,0)),""))'
        S = '=IF(@{0}@="","",IFERROR(INDEX(crit_' + sv + '_Valor,MATCH(@{0}@,crit_' + sv + '_Nivel,0)),""))'
        if risk:
            SIG = '=IF(@{0}@="","",IF(@{0}@<=crit_Lim_R_Sig,"SIGNIFICATIVO",IF(@{0}@<=crit_Lim_R_Tol,"TOLERÁVEL","BAIXO")))'
        else:
            SIG = '=IF(@{0}@="","",IF(@{0}@>=crit_Lim_O_Sig,"SIGNIFICATIVO",IF(@{0}@>=crit_Lim_O_Tol,"TOLERÁVEL","BAIXO")))'
        yes = "NÃO ACEITÁVEL" if risk else "AÇÃO REQUERIDA"
        nome = "risco" if risk else "oportunidade"
        sev_desc = "Menor -1, Sério -2, Crítico -3." if risk else "Suficiente 1, Bom 2, Muito Bom 3."
        return [
            col("ID_RO", 8, desc=f"Identificador do {nome} no SGA (RO-nn, numeração comum a riscos e oportunidades).", key="PK", dom="RO-nn"),
            col("Data_Identificacao", 12, "date", desc="Data de identificação."),
            col("Origem", 16, dv="Origem", desc="Fonte da identificação (SWOT, PESTEL, aspeto, legal...)."),
            col("ID_Origem", 10, desc="ID do item de origem (ex.: SWT-F01, PES-12, LEG-05).", key="FK → RG-SGA-01/03/04"),
            col("Selecionado_Atv_3_1", 11, dv="SimNao", desc="Um dos 4 itens SWOT escolhidos para a Atividade 3.1."),
            col("Descricao", 50, desc=f"Descrição do {nome} (evento e efeito)."),
            col("Causa", 36, desc="Causa." if risk else "Causa ou condição favorável."),
            col("Consequencia", 40, desc="Consequência para os resultados pretendidos do SGA."),
            col("Proveniente_Analise_Anterior", 12, dv="Proveniente", desc="Se transita da análise anterior (Sim/Não/Novo/Alterada)."),
            col("Area_Gestao", 20, dv="AreaGestao", desc="Área de gestão (lista do curso)."),
            col("Processo", 9, dv="Processo", desc="Processo principal.", key="FK → dim processo"),
            col("Tema", 20, dv="Tema", desc="Tema ambiental."),
            col("Parte_Interessada", 24, desc="Partes interessadas afetadas/beneficiadas."),
            col("Controlos_Existentes", 32, desc="Controlos já existentes considerados na avaliação."),
            col("Probabilidade", 12, dv="=crit_P_Nivel", desc="Remota (1), Provável (2), Frequente (3) — critérios na folha Listas."),
            col("P", 5, "int", f=P.format("Probabilidade"), desc="Valor numérico da probabilidade (1-3)."),
            col("Severidade", 12, dv=f"=crit_{sv}_Nivel", desc=sev_desc + " Critérios na folha Listas."),
            col("S", 5, "int", f=S.format("Severidade"), desc="Valor numérico da severidade."),
            col("Nivel", 7, "int", f='=IF(COUNT(@P@,@S@)=2,@P@*@S@,"")', desc="Nível = P × S."),
            col("Significancia", 15, f=SIG.format("Nivel"), desc="SIGNIFICATIVO / TOLERÁVEL / BAIXO pelos limites da folha Listas."),
            col("Aceitabilidade", 15, f=f'=IF(@Significancia@="","",IF(@Significancia@="SIGNIFICATIVO","{yes}","ACEITÁVEL"))',
                desc="Resultado da matriz do curso."),
            col("Coerencia", 18, f=('=IF(@Nivel@="","",IF(LEFT(@Decisao@,1)<>"' + ("R" if risk else "O") + '","ERRO: decisão não é de '
                                    + nome + '",IF(AND(@Significancia@="SIGNIFICATIVO",@Acao_Tratamento@=""),"FALTA ação de tratamento","OK")))'),
                desc="Controlo de qualidade dos dados."),
            col("Decisao", 30, dv="DecisaoRisco" if risk else "DecisaoOportunidade", desc="Tipo de decisão (lista do curso)."),
            col("Acao_Tratamento", 50, desc="Ação de tratamento definida."),
            col("Tipo_Acao", 8, dv="TipoAcao", desc="C1 correção; C2 ação corretiva; M melhoria; — sem ação."),
            col("ID_PAM", 11, desc="Ação no Plano de Ações de Melhoria.", key="FK → RG-SGA-06", req=False),
            col("Responsavel", 26, dv="Funcao", desc=f"Dono do {nome} / responsável pela ação."),
            col("Prazo", 11, "date", desc="Prazo da ação ou da reavaliação."),
            col("Estado_Acao", 11, dv="EstadoAcao", desc="Estado da ação em 2026-09-23."),
            col("Probabilidade_Residual", 12, dv="=crit_P_Nivel", desc="Probabilidade esperada após o tratamento."),
            col("Severidade_Residual", 12, dv=f"=crit_{sv}_Nivel", desc="Severidade esperada após o tratamento."),
            col("Nivel_Residual", 9, "int", f=('=IF(OR(@Probabilidade_Residual@="",@Severidade_Residual@=""),"",IFERROR('
                                               'INDEX(crit_P_Valor,MATCH(@Probabilidade_Residual@,crit_P_Nivel,0))*'
                                               f'INDEX(crit_{sv}_Valor,MATCH(@Severidade_Residual@,crit_{sv}_Nivel,0)),""))'),
                desc="Nível residual esperado (P × S)."),
            col("Significancia_Residual", 15, f=SIG.format("Nivel_Residual"), desc="Significância residual esperada."),
            col("KRI", 34, desc="Indicador-chave / gatilho de reavaliação."),
            col("Data_Avaliacao", 12, "date", desc="Data da última avaliação."),
            col("Proxima_Revisao", 12, "date", f='=IF(@Data_Avaliacao@="","",EDATE(@Data_Avaliacao@,IF(@Significancia@="SIGNIFICATIVO",6,12)))',
                desc="6 meses se significativo, 12 meses nos restantes."),
            col("ID_Registo_Corporativo", 11, desc=f"Linha equivalente no registo corporativo {CORP_FILE} (tbRiscos/tbOportunidades, coluna ID).",
                key="FK → registo corporativo"),
            col("IDs_Relacionados_Corporativo", 14, desc="Outros riscos/oportunidades do registo corporativo ligados a este item (separados por ';').",
                req=False),
            col("Simulacao_Forcada", 10, dv="SimNao", desc="Sim se P ou S foi forçado para simular um caso significativo (nota do enunciado)."),
            col("Notas", 40, desc="Justificação / notas.", req=False),
        ]

    rows = {"Risco": [], "Oportunidade": []}
    for t in RO:
        (i, o, io, sel, tp, de, ca, co, pv, ar, pr, te, pi, ce, pb, sv, dc, ac, ta, pam, rs, pz, es, pbr, svr, kri, idc, fc, nt) = t
        rows[tp].append(dict(ID_RO=i, Data_Identificacao=D0, Origem=o, ID_Origem=io, Selecionado_Atv_3_1=sel, Descricao=de,
                             Causa=ca, Consequencia=co, Proveniente_Analise_Anterior=pv, Area_Gestao=ar, Processo=pr, Tema=te,
                             Parte_Interessada=pi, Controlos_Existentes=ce, Probabilidade=pb, Severidade=sv, Decisao=dc,
                             Acao_Tratamento=ac, Tipo_Acao=ta, ID_PAM=pam or None, Responsavel=rs, Prazo=dt.date.fromisoformat(pz),
                             Estado_Acao=es, Probabilidade_Residual=pbr, Severidade_Residual=svr, KRI=kri, Data_Avaliacao=D0,
                             ID_Registo_Corporativo=idc or None, IDs_Relacionados_Corporativo=REL_CORP.get(i),
                             Simulacao_Forcada=fc, Notas=nt or None))
    sig_cf = {"SIGNIFICATIVO": "red", "TOLERÁVEL": "yellow", "BAIXO": "green"}
    common_cf = [("Significancia", sig_cf), ("Significancia_Residual", sig_cf),
                 ("Coerencia", {"ERRO": "red", "FALTA": "orange", "OK": "green"}), ("Selecionado_Atv_3_1", {"Sim": "purple"})]
    b.table("Riscos", "tbl_riscos", cols_for("R"), rows["Risco"],
            "Riscos do SGA (ameaças): identificação e avaliação P × S, decisão, tratamento e residual (1 linha por risco).",
            title="RISCOS DO SGA — IDENTIFICAÇÃO E AVALIAÇÃO (Nível = P × S)",
            subtitle="Significativo: nível -6 ou -9 · Cabeçalho cinzento = calculado · Critérios na folha Listas · "
                     "Filtrar Selecionado_Atv_3_1 = Sim para a Atividade 3.1",
            cf=common_cf + [("Aceitabilidade", {"NÃO ACEITÁVEL": "red", "ACEITÁVEL": "green"})], row_height=75, freeze_col=1)
    b.table("Oportunidades", "tbl_oportunidades", cols_for("O"), rows["Oportunidade"],
            "Oportunidades do SGA: identificação e avaliação P × S, decisão, ação e residual (1 linha por oportunidade).",
            title="OPORTUNIDADES DO SGA — IDENTIFICAÇÃO E AVALIAÇÃO (Nível = P × S)",
            subtitle="Significativa: nível 9 · Cabeçalho cinzento = calculado · Critérios na folha Listas · "
                     "Filtrar Selecionado_Atv_3_1 = Sim para a Atividade 3.1",
            cf=common_cf + [("Aceitabilidade", {"AÇÃO REQUERIDA": "blue", "ACEITÁVEL": "green"})], row_height=75, freeze_col=1)

    # ---------- resumo da atividade 3.1 + mapa de calor (ex-Matriz_PxS)
    ws = b.sheet("Resumo_Atividade_3_1", "Quadro da Atividade 3.1 para impressão/fórum (4 itens SWOT) e mapa de calor P × S com "
                                         "indicadores (calculado a partir de tbl_riscos e tbl_oportunidades; substitui a Matriz_PxS).",
                 tab_color="7030A0")
    ws["A1"] = "ATIVIDADE 3.1 — MATRIZ DE RISCOS E PLANEAMENTO DE AÇÕES (4 itens da SWOT)"
    ws["A1"].font = F_TITLE
    ws["A2"] = "Valores calculados a partir de tbl_riscos (folha Riscos) e tbl_oportunidades (folha Oportunidades). Metodologia: Nível = P × S."
    ws["A2"].font = F_SUB
    hdr = ["ID", "Origem SWOT", "Descrição", "Tipo", "Probabilidade", "P", "Severidade", "S", "Nível", "Significância",
           "Aceitabilidade", "Decisão", "Ação de tratamento", "PAM"]
    fields = ["ID_RO", "ID_Origem", "Descricao", None, "Probabilidade", "P", "Severidade", "S", "Nivel", "Significancia",
              "Aceitabilidade", "Decisao", "Acao_Tratamento", "ID_PAM"]
    header_row(ws, 4, hdr, widths=[8, 12, 46, 13, 12, 5, 12, 5, 7, 15, 15, 28, 50, 11])
    ids_r, ids_o = b.ref("tbl_riscos", "ID_RO"), b.ref("tbl_oportunidades", "ID_RO")
    for k, rid in enumerate(["RO-01", "RO-02", "RO-03", "RO-04"]):
        r = 5 + k
        mr, mo = f'MATCH("{rid}",{ids_r},0)', f'MATCH("{rid}",{ids_o},0)'
        for j, fld in enumerate(fields):
            if fld is None:  # Tipo: deduzido da tabela onde o ID está
                f = f'=IF(ISNUMBER({mr}),"Risco",IF(ISNUMBER({mo}),"Oportunidade",""))'
            else:
                look = (f'IFERROR(INDEX({b.ref("tbl_riscos", fld)},{mr}),'
                        f'IFERROR(INDEX({b.ref("tbl_oportunidades", fld)},{mo}),""))')
                f = f"={look}" if fld in ("P", "S", "Nivel") else f'={look}&""'
            c = ws.cell(row=r, column=j + 1, value=f)
            c.font, c.alignment, c.border = F_BASE, WRAP_TOP, BORDER
        ws.row_dimensions[r].height = 95
    for txt, colr in sig_cf.items():
        bg, fg = CF_COLORS[colr]
        ws.conditional_formatting.add("J5:J8", FormulaRule(formula=[f'ISNUMBER(SEARCH("{txt}",J5))'],
                                                           fill=PatternFill("solid", fgColor=bg), font=Font(name=FONT, color=fg, bold=True)))
    ws["A10"] = "Conclusão"
    ws["A10"].font = F_BOLD
    ws["A10"].alignment = WRAP_TOP
    ws["B10"] = ("Dos 4 itens, 2 são SIGNIFICATIVOS sem necessidade de forçar valores: a oportunidade RO-01 (P3 × S3 = 9 → ação requerida) "
                 "e o risco RO-02 (P3 × S-2 = -6 → não aceitável). Para ambos foi escolhida a decisão e definida a ação de tratamento, "
                 "transferida para o Plano de Ações de Melhoria (PAM-26-09 e PAM-26-02). RO-03 (6) e RO-04 (-4) são TOLERÁVEIS: "
                 "decisão de estudar viabilidade e de monitorizar, sem ação obrigatória.")
    ws["B10"].alignment = WRAP_TOP
    ws.merge_cells("B10:M10")
    ws.row_dimensions[10].height = 60

    ws["A13"] = "MAPA DE CALOR — NÚMERO DE RISCOS E OPORTUNIDADES POR CÉLULA DA MATRIZ"
    ws["A13"].font = F_TITLE
    for tname, tipo, svals, r0 in (("tbl_riscos", "Risco", [-1, -2, -3], 15), ("tbl_oportunidades", "Oportunidade", [1, 2, 3], 22)):
        Pr, Sr = b.ref(tname, "P"), b.ref(tname, "S")
        ws.cell(row=r0, column=1, value=f"{tipo.upper()}S — P (linhas) × S (colunas)").font = F_BOLD
        for j, t in enumerate(["P \\ S"] + [str(s) for s in svals]):
            c = ws.cell(row=r0 + 1, column=1 + j, value=t)
            c.font, c.fill, c.alignment, c.border = F_HEAD, FILL_HEAD, CENTER, BORDER
        for i, p in enumerate([3, 2, 1]):
            ws.cell(row=r0 + 2 + i, column=1, value=p).font = F_BOLD
            for j, s in enumerate(svals):
                c = ws.cell(row=r0 + 2 + i, column=2 + j, value=f"=COUNTIFS({Pr},{p},{Sr},{s})")
                lvl = p * s
                sig = (lvl <= -6) if tipo == "Risco" else (lvl >= 9)
                tol = (-4 <= lvl <= -3) if tipo == "Risco" else (3 <= lvl <= 6)
                c.fill = PatternFill("solid", fgColor=CF_COLORS["red" if sig else ("yellow" if tol else "green")][0])
                c.font, c.alignment, c.border = Font(name=FONT, bold=True, size=12), CENTER, BORDER
    ws["F15"] = "Indicadores"
    ws["F15"].font = F_BOLD
    ws.column_dimensions["F"].width = 42
    ws.column_dimensions["G"].width = 10
    sgr, sgo = b.ref("tbl_riscos", "Significancia"), b.ref("tbl_oportunidades", "Significancia")
    pr_, po_ = b.ref("tbl_riscos", "ID_PAM"), b.ref("tbl_oportunidades", "ID_PAM")
    kpis = [("Total de riscos", f'=COUNTIF({ids_r},"RO-*")'), ("Total de oportunidades", f'=COUNTIF({ids_o},"RO-*")'),
            ("N.º significativos", f'=COUNTIF({sgr},"SIGNIFICATIVO")+COUNTIF({sgo},"SIGNIFICATIVO")'),
            ("Significativos com ação no PAM",
             f'=COUNTIFS({sgr},"SIGNIFICATIVO",{pr_},"PAM*")+COUNTIFS({sgo},"SIGNIFICATIVO",{po_},"PAM*")'),
            ("% significativos com ação", "=IFERROR(G19/G18,0)")]
    for k, (lab, f) in enumerate(kpis):
        ws.cell(row=16 + k, column=6, value=lab).font = F_BASE
        c = ws.cell(row=16 + k, column=7, value=f)
        c.font = F_BOLD
        if "%" in lab:
            c.number_format = "0%"
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToHeight = 0
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
