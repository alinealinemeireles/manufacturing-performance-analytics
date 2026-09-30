import datetime as dt
from sgalib import *
from dims import *

REU = dt.date(2026, 9, 23)

PART = [
    ("Diretor Geral (Gestão de Topo)", "Preside e decide", "Presente"), ("Diretor Industrial", "Participante", "Presente"),
    ("Diretor Financeiro", "Participante (recursos)", "Presente"), ("Gestor do SGA / EHS (Responsável Ambiental)", "Apresenta e secretaria a ata", "Presente"),
    ("Gerente de Produção", "Participante", "Presente"), ("Gerente de Manutenção", "Participante", "Presente"),
    ("Gerente da Qualidade", "Participante (auditorias)", "Presente"), ("Responsável de Compras", "Participante", "Presente"),
    ("Responsável de R&D", "Participante (PPWR)", "Presente"), ("Responsável de Armazém e Logística", "Convidado (pontos 6 e 7)", "Presente"),
    ("Responsável de Recursos Humanos", "Participante (competências)", "Ausente justificado"),
    ("Representante dos Trabalhadores (SST/Ambiente)", "Participante (consulta e participação)", "Presente"),
]

AG = [
    (1, "9.3.2 a)", "Abertura; estado das ações da revisão pela gestão de 2025 (4 decisões: 3 concluídas, 1 em curso).", "Atas RG-2025; RG-SGA-06", "Diretor Geral", 10),
    (2, "9.3.2 b)", "Alterações nas questões externas e internas relevantes, incluindo as condições ambientais: verão de 2026 mais quente (+2 °C), risco de seca, risco de incêndio florestal, preço da energia e mercado de PCR.", "RG-SGA-01 (PESTEL/SWOT)", "Gestor do SGA / EHS (Responsável Ambiental)", 15),
    (3, "9.3.2 b)", "Necessidades e expectativas das partes interessadas e obrigações de conformidade: PPWR aplicável desde 12/08/2026, regulamento europeu de granulados, reclamação de ruído da vizinhança, pedidos ESG de clientes.", "RG-SGA-04; registo de reclamações", "Gestor do SGA / EHS (Responsável Ambiental)", 15),
    (4, "9.3.2 b)", "Aspetos ambientais significativos (COV da serigrafia, ruído dos compressores, embalagens sem declaração PPWR) e riscos e oportunidades significativos (6 riscos, 1 oportunidade).", "RG-SGA-03; RG-SGA-02", "Gestor do SGA / EHS (Responsável Ambiental)", 15),
    (5, "9.3.2 c)", "Grau de cumprimento dos objetivos ambientais OBJ-01 a OBJ-06 (energia, scrap, solvente, PPWR, água, granulado).", "RG-SGA-05", "Diretor Industrial", 15),
    (6, "9.3.2 d)", "Desempenho ambiental: tendências de 18 meses dos KPI; desvio de +15% no solvente; não conformidades e ações corretivas (9 NC em 2026); avaliação da conformidade legal (82%, 2 NC); auditoria interna AUD-2026-01 (6 NC, 4 OM).", "RG-SGA-13; RG-SGA-07; RG-SGA-04; RG-SGA-14", "Gestor do SGA / EHS (Responsável Ambiental)", 35),
    (7, "9.3.2 e)", "Adequação dos recursos: submedição, recursos para o PPWR, formação de temporários, equipamento de recuperação de solvente.", "RG-SGA-06; RG-SGA-08", "Diretor Financeiro", 15),
    (8, "9.3.2 f)", "Comunicações relevantes das partes interessadas, incluindo reclamações (ruído) e sugestões dos trabalhadores (caixa Kaizen).", "RG-SGA-09; RG-SGA-16", "Representante dos Trabalhadores (SST/Ambiente)", 10),
    (9, "9.3.2 g)", "Oportunidades de melhoria contínua: Kaizen do turno 3, fotovoltaico, preparação do registo EMAS.", "RG-SGA-16; RG-SGA-02", "Gestor do SGA / EHS (Responsável Ambiental)", 15),
    (10, "9.3.3", "Conclusões sobre a adequação, suficiência e eficácia do SGA; decisões, recursos e alterações ao SGA; encerramento.", "—", "Diretor Geral", 20),
]

DEC = [
    ("RG-26-D01", 6, "Oportunidades de melhoria contínua",
     "O consumo específico de solvente de limpeza na serigrafia subiu 15% em jun–ago/2026 com a produção estável; o aspeto (COV) é significativo (IRA 40) e o solvente usado é enviado como resíduo perigoso. As causas confirmadas são recipientes abertos, a SS-001 após o overhaul e um operador temporário sem formação.",
     "Aprovar a compra de uma unidade de recuperação de solvente (destilador de 60 L) e de 4 dispensadores de segurança, e tornar obrigatória a formação FOR-02 antes de qualquer temporário trabalhar na serigrafia.",
     14100, "Gestor do SGA (0,1 ETI); chefe de serigrafia; fornecedor do destilador", "Gestor do SGA / EHS (Responsável Ambiental)", "2027-03-31", "PAM-26-13; PAM-26-08"),
    ("RG-26-D02", 3, "Implicações para a direção estratégica",
     "O PPWR aplica-se desde 12/08/2026 e só 9 de 22 famílias (41%) têm documentação técnica e declaração UE de conformidade (NC legal); os clientes alimentares e farmacêuticos já pedem as declarações.",
     "Contratar consultoria especializada em PPWR, afetar um técnico de qualidade/ambiente a 50% durante 6 meses e priorizar as famílias por volume de vendas; o incumprimento passa a ser risco estratégico acompanhado mensalmente pela gestão.",
     26000, "Responsável de R&D; técnico Q/A (0,5 ETI, 6 meses); consultor externo", "Responsável de R&D", "2026-12-31", "PAM-26-10"),
    ("RG-26-D03", 7, "Recursos",
     "Sem submedição não é possível demonstrar o desempenho de energia e água (RO-02, nível -6) nem medir o efeito das ações; o ar comprimido tem ≈ 25% de fugas.",
     "Aprovar o CAPEX de submedição (6 analisadores + 3 contadores) e do variador de velocidade do compressor, e submeter candidatura ao Portugal 2030 para cofinanciamento.",
     38000, "Gerente de Manutenção; técnico de utilidades; instalador", "Gerente de Manutenção", "2026-12-31", "PAM-26-01; PAM-26-02"),
    ("RG-26-D04", 9, "Oportunidades de melhoria contínua",
     "Oportunidade RO-09: fotovoltaico em ≈ 9.000 m² de cobertura; clientes pedem dados de carbono; o registo EMAS daria acesso a clientes públicos e a menos inspeções.",
     "Encomendar o estudo de viabilidade de uma UPAC de ≈ 1 MWp e preparar o diagnóstico para o registo EMAS em 2027 (declaração ambiental com os 6 indicadores principais).",
     4000, "Diretor Financeiro; Gestor do SGA", "Diretor Financeiro", "2027-03-31", "PAM-26-18"),
    ("RG-26-D05", 6, "Necessidade de alterações ao SGA",
     "A auditoria AUD-2026-01 detetou que a substituição dos compressores não passou por avaliação ambiental (requisito novo 6.3 da ISO 14001:2026), o que originou a NC legal de ruído.",
     "Aprovar o procedimento PR-SGA-06 'Planeamento de alterações' com checklist ambiental/legal obrigatória antes de qualquer investimento em equipamento, processo, layout ou material.",
     0, "Gestor do SGA; Diretor Industrial", "Gestor do SGA / EHS (Responsável Ambiental)", "2026-11-30", "PAM-26-17"),
]

CONCL = [
    ("Adequação", "O SGA continua adequado ao contexto da Plasticom, mas tem de integrar o PPWR, o regulamento de granulados e a gestão de alterações (6.3)."),
    ("Suficiência", "Recursos insuficientes em medição e em conformidade de produto: reforçados pelas decisões D02 e D03."),
    ("Eficácia", "Eficácia parcial: 2 de 6 objetivos no caminho previsto (energia, scrap); solvente e água com desvio; 1 de 2 ações de NC verificadas como eficazes."),
    ("Política Ambiental", "Rev. 02 (junho/2026) mantém-se adequada; não é necessária alteração."),
]


def build(out):
    b = Book("RG-SGA-15", "Revisão pela Gestão 2026 — Ordem de Trabalhos, Participantes e Ata de Decisões",
             activities="Atividade 5.4 — Parte I: Ordem de Trabalhos (inputs da cláusula 9.3). Parte II: excerto da Ata com as decisões (reunião de 23/09/2026).",
             clauses="9.3.1 Generalidades; 9.3.2 Entradas; 9.3.3 Resultados (estrutura da ISO 14001:2026)",
             purpose="Registar a convocatória, os participantes, a ordem de trabalhos ligada às entradas obrigatórias da 9.3.2 e às fontes de dados de cada ponto, as conclusões sobre adequação/suficiência/eficácia e as decisões com problema, decisão, recursos, responsável, prazo e ação no PAM.",
             links=[("RG-SGA-06 PAM", "Cada decisão gera ação(ões) no PAM."), ("Todos os registos", "A coluna Fonte_Dados indica o registo que alimenta cada ponto.")])
    b.add_list("Presenca", ["Presente", "Ausente justificado", "Ausente"])
    b.add_list("Entrada932", ["9.3.2 a)", "9.3.2 b)", "9.3.2 c)", "9.3.2 d)", "9.3.2 e)", "9.3.2 f)", "9.3.2 g)", "9.3.3"])
    b.add_list("Saida933", ["Conclusões sobre adequação, suficiência e eficácia", "Oportunidades de melhoria contínua", "Necessidade de alterações ao SGA",
                            "Recursos", "Ações quando os objetivos não foram atingidos", "Integração nos processos de negócio", "Implicações para a direção estratégica"])
    b.add_list("Funcao", FUNC_NAMES)

    pcols = [col("ID_Reuniao", 10, desc="Reunião.", key="FK"), col("Funcao", 40, dv="Funcao", desc="Cargo convocado."), col("Papel", 34, desc="Papel na reunião."),
             col("Presenca", 16, dv="Presenca", desc="Presença.")]
    b.table("Participantes", "tbl_participantes", pcols, [dict(ID_Reuniao="RG-2026", Funcao=f, Papel=p, Presenca=s) for f, p, s in PART], "Participantes convocados e presença.")

    acols = [col("ID_Reuniao", 10, desc="Reunião.", key="FK"), col("Ponto", 6, "int", desc="N.º do ponto."), col("Entrada_9_3_2", 10, dv="Entrada932", desc="Alínea da 9.3.2."),
             col("Topico", 80, desc="Tópico adaptado à Plasticom."), col("Fonte_Dados", 30, desc="Registo que suporta o ponto."),
             col("Apresentador", 34, dv="Funcao", desc="Quem apresenta."), col("Duracao_min", 9, "int", desc="Duração (min)."),
             col("Hora_Inicio", 9, f='=TIME(14,30,0)+SUMIFS(#Duracao_min#,#Ponto#,"<"&@Ponto@)/1440', desc="Hora de início do ponto (reunião às 14:30)."),
             col("N_Decisoes", 9, "int", f='=COUNTIF(tbl_decisoes[Ponto_Agenda],@Ponto@)', desc="Decisões tomadas neste ponto.")]
    arows = [dict(ID_Reuniao="RG-2026", Ponto=a, Entrada_9_3_2=e, Topico=t, Fonte_Dados=f, Apresentador=p, Duracao_min=m) for a, e, t, f, p, m in AG]
    b.table("Ordem_Trabalhos", "tbl_agenda", acols, arows, "Ordem de trabalhos: 1 linha por ponto, ligada à alínea da 9.3.2 e à fonte de dados.",
            title="ORDEM DE TRABALHOS — REVISÃO PELA GESTÃO 2026", subtitle="23/09/2026, 14:30–17:30 · Sala de Reuniões da Administração, Plasticom Unidade 1 · Convocatória enviada a 09/09/2026",
            row_height=48)
    ws = b.tables["tbl_agenda"]["ws"]
    L = b.tables["tbl_agenda"]["colmap"]["Hora_Inicio"]
    for r in range(b.tables["tbl_agenda"]["first"], b.tables["tbl_agenda"]["last"] + 1):
        ws[f"{L}{r}"].number_format = "hh:mm"

    dcols = [col("ID_Decisao", 10, desc="Decisão.", key="PK"), col("Ponto_Agenda", 7, "int", desc="Ponto da agenda."),
             col("Tipo_Saida_9_3_3", 30, dv="Saida933", desc="Tipo de resultado exigido pela 9.3.3."),
             col("Problema_Analise", 56, desc="O que motivou a decisão."), col("Decisao_Tomada", 56, desc="O que se vai comprar, alterar ou implementar."),
             col("Recursos_EUR", 11, "eur", desc="Orçamento alocado."), col("Recursos_Pessoas", 36, desc="Pessoas envolvidas."),
             col("Responsavel", 30, dv="Funcao", desc="Quem executa."), col("Prazo", 11, "date", desc="Até quando."), col("IDs_PAM", 18, desc="Ações no PAM.", key="FK → RG-SGA-06"),
             col("Dias_ate_Prazo", 9, "int", f="=@Prazo@-DataRef", desc="Dias até ao prazo.")]
    drows = [dict(ID_Decisao=a, Ponto_Agenda=p, Tipo_Saida_9_3_3=t, Problema_Analise=pr, Decisao_Tomada=dc, Recursos_EUR=e, Recursos_Pessoas=pe,
                  Responsavel=rs, Prazo=dt.date.fromisoformat(pz), IDs_PAM=pam) for a, p, t, pr, dc, e, pe, rs, pz, pam in DEC]
    b.table("Ata_Decisoes", "tbl_decisoes", dcols, drows, "Decisões da revisão pela gestão (saídas 9.3.3) com recursos, responsável e prazo.", row_height=110, freeze_col=1)

    ccols = [col("Tema", 18, desc="Conclusão exigida."), col("Conclusao", 110, desc="Conclusão da gestão.")]
    b.table("Conclusoes", "tbl_conclusoes", ccols, [dict(Tema=a, Conclusao=t) for a, t in CONCL], "Conclusões sobre adequação, suficiência e eficácia (9.3.3).", row_height=32)

    # Convocatória imprimível
    ws = b.sheet("Convocatoria_Impressao", "Parte I — Convocatória/Ordem de trabalhos em formato de impressão (fórum), calculada a partir das tabelas.", tab_color="7030A0")
    doc_header(ws, "RG-SGA-15", "CONVOCATÓRIA — REVISÃO PELA GESTÃO DO SGA 2026", "RG-SGA-15", 5)
    for L, w in zip("ABCDE", (8, 12, 70, 34, 10)):
        ws.column_dimensions[L].width = w
    r = 5
    for lab, v in [("Data e hora", "23/09/2026, 14:30–17:30"), ("Local", "Sala de Reuniões da Administração — Plasticom, Unidade 1 (Marinha Grande)"),
                   ("Convocada por", "Diretor Geral, sob proposta do Gestor do SGA/EHS"),
                   ("Participantes", "=" + "&\", \"&".join([f'INDEX({b.ref("tbl_participantes", "Funcao")},{k + 1})' for k in range(len(PART))])),
                   ("Documentos de apoio", "Registos RG-SGA-01 a RG-SGA-16 e painel ambiental (enviados a 16/09/2026)")]:
        form_block(ws, r, lab, v, lw=2, vw=3, height=48 if lab == "Participantes" else None)
        r += 1
    r += 1
    header_row(ws, r, ["Ponto", "Hora", "Tópico (entrada da 9.3.2)", "Apresentador", "Min"])
    A = lambda f: b.ref("tbl_agenda", f)
    for k in range(len(AG)):
        r += 1
        vals = [f"=INDEX({A('Ponto')},{k + 1})", f"=INDEX({A('Hora_Inicio')},{k + 1})",
                f'=INDEX({A("Topico")},{k + 1})&" ["&INDEX({A("Entrada_9_3_2")},{k + 1})&"]"', f"=INDEX({A('Apresentador')},{k + 1})", f"=INDEX({A('Duracao_min')},{k + 1})"]
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=j + 1, value=v)
            c.font, c.border = F_BASE, BORDER
            c.alignment = CENTER if j in (0, 1, 4) else WRAP_TOP
            if j == 1:
                c.number_format = "hh:mm"
        ws.row_dimensions[r].height = 58

    # Ata imprimível
    ws = b.sheet("Ata_Impressao", "Parte II — Excerto da ata com as decisões (formato para auditor externo), calculado a partir de tbl_decisoes.", tab_color="7030A0")
    doc_header(ws, "RG-SGA-15", "ATA N.º 01/2026 — REVISÃO PELA GESTÃO (EXCERTO)", "RG-SGA-15", 2)
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 110
    r = 5
    form_block(ws, r, "Reunião", "23/09/2026, 14:30–17:30, Sala de Reuniões da Administração. Presidida pelo Diretor Geral; secretariada pelo Gestor do SGA/EHS.", vw=1)
    r += 1
    form_block(ws, r, "Presenças", f'=COUNTIF({b.ref("tbl_participantes", "Presenca")},"Presente")&" de "&COUNTA({b.ref("tbl_participantes", "Funcao")})&" convocados presentes"', vw=1)
    r += 2
    D = lambda f: b.ref("tbl_decisoes", f)
    for k in range(len(DEC)):
        ws.cell(row=r, column=1, value=f'="DECISÃO "&INDEX({D("ID_Decisao")},{k + 1})&" (ponto "&INDEX({D("Ponto_Agenda")},{k + 1})&")"').font = Font(name=FONT, bold=True, size=11, color=C_HEAD)
        r += 1
        for lab, fld in [("Problema / Análise", "Problema_Analise"), ("Decisão tomada", "Decisao_Tomada"), ("Recursos alocados", None),
                         ("Responsável e prazo", "RP"), ("Ações no PAM", "IDs_PAM")]:
            if fld is None:
                v = f'=FIXED(INDEX({D("Recursos_EUR")},{k + 1}),0)&" € — "&INDEX({D("Recursos_Pessoas")},{k + 1})'
            elif fld == "RP":
                v = f'=INDEX({D("Responsavel")},{k + 1})&" — até "&TEXT(DAY(INDEX({D("Prazo")},{k + 1})),"00")&"/"&TEXT(MONTH(INDEX({D("Prazo")},{k + 1})),"00")&"/"&YEAR(INDEX({D("Prazo")},{k + 1}))'
            else:
                v = f'=INDEX({D(fld)},{k + 1})'
            form_block(ws, r, lab, v, vw=1, height=48 if fld in ("Problema_Analise", "Decisao_Tomada") else None)
            r += 1
        r += 1
    ws.cell(row=r, column=1, value="Conclusões (9.3.3)").font = Font(name=FONT, bold=True, size=11, color=C_HEAD)
    for k in range(len(CONCL)):
        r += 1
        form_block(ws, r, f'=INDEX({b.ref("tbl_conclusoes", "Tema")},{k + 1})', f'=INDEX({b.ref("tbl_conclusoes", "Conclusao")},{k + 1})', vw=1, height=32)
    r += 2
    ws.cell(row=r, column=1, value="Assinaturas: Diretor Geral ________________    Gestor do SGA/EHS ________________").font = F_BASE
    ws.page_setup.orientation = "portrait"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToHeight = 0
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
