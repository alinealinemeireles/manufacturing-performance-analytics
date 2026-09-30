"""Registos complementares do SGA para cumprir a ISO 14001:2026 numa fábrica real (revisão de 24/09/2026).

Cada função acrescenta uma tabela a um registo existente (chamada antes de b.save no respetivo build_NN):
  extra_01  tbl_partes_interessadas     4.2  necessidades, expectativas e quais se tornam obrigações de conformidade
  extra_07  tbl_incidentes              8.2 / 10.2  registo de incidentes e quase-incidentes ambientais
  extra_08  tbl_raci                    5.3  funções, responsabilidades e autoridades (matriz RACI)
  extra_09  tbl_comunicacoes_externas   7.4  registo de comunicações externas recebidas e enviadas
  extra_10  tbl_manutencao_ambiental    7.1 / 8.1  manutenção de equipamentos com relevância ambiental (inclui F-gas)
  8.1       colunas de tipo/extensão do controlo em tbl_fornecedores e tbl_outros_fornecedores (+ 5 prestadores novos)
  9.1       colunas de faturação (preço, custo, emissões) em tbl_meses; extra_13 tbl_analises (resultados laboratoriais vs. limites)
Dados simulados para a fábrica fictícia Plasticom, coerentes com os restantes registos (IDs, datas e ocorrências).
"""
import datetime as dt
from sgalib import *
from dims import *

d = lambda s: dt.date.fromisoformat(s) if s else None
F = {n: n for n in FUNC_NAMES}
SGA, DIND, DG, PROD, MAN, QUA, LOG, CMP, RD, RH, FIN = FUNC_NAMES[:11]
def _ensure(b):
    """Listas partilhadas usadas pelas tabelas complementares (só cria se o registo ainda não as tiver)."""
    if "Funcao" not in b.lists:
        b.add_list("Funcao", FUNC_NAMES)
    if "Processo" not in b.lists:
        b.add_list("Processo", PROC_CODES)


COND = ["Poluição", "Recursos naturais", "Clima", "Biodiversidade", "Saúde dos ecossistemas", "Não aplicável"]


# ============================================================== 4.2 partes interessadas
def extra_01(b):
    _ensure(b)
    b.add_list("PI_Tipo", ["Interna", "Externa"])
    b.add_list("PI_Cond", COND)
    b.add_list("PI_SimNao", ["Sim", "Não"])
    b.add_list("PI_Nivel", ["Alta", "Média", "Baixa"])
    b.add_list("PI_Obrig", ["Legal", "Voluntária (compromisso assumido)", "—"])
    rows = [
        ("PI-01", "Colaboradores", "Interna", "Trabalhadores próprios (≈ 150, 3 turnos)", "Ambiente de trabalho sem exposição a solventes; formação; participação na melhoria.", "Poluição", "Sim", "Sim", "Legal", "LEG-06", "Formação, DDS e comité SST/ambiente; caixa de sugestões Kaizen", "Mensal", "Média", "Alta", "RO-10", RH),
        ("PI-02", "Representantes dos trabalhadores (SST/Ambiente)", "Interna", "Representantes eleitos", "Ser consultados sobre alterações com impacto ambiental e de SST.", "Não aplicável", "Sim", "Sim", "Voluntária (compromisso assumido)", "", "Consulta formal nas alterações (RG-SGA-18)", "Por ocorrência", "Média", "Média", "", RH),
        ("PI-03", "Acionistas / Direção", "Interna", "Gestão de topo", "Continuidade, conformidade legal, custos de energia controlados, reputação.", "Clima", "Sim", "Não", "—", "", "Revisão pela gestão; painel mensal de KPI", "Trimestral", "Alta", "Alta", "RO-02", DG),
        ("PI-04", "Clientes de cosmética (marcas UE)", "Externa", "Clientes B2B", "Embalagens recicláveis com PCR, declaração PPWR, pegada de carbono, respostas EcoVadis/CDP.", "Recursos naturais", "Sim", "Sim", "Voluntária (compromisso assumido)", "LEG-09", "Questionários ESG; reunião semestral de conta", "Semestral", "Alta", "Alta", "RO-03", RD),
        ("PI-05", "Clientes alimentar e farmacêutico", "Externa", "Clientes B2B (novas linhas 2026)", "Conformidade de materiais em contacto, rastreabilidade, ausência de PFAS e substâncias restritas.", "Poluição", "Sim", "Sim", "Legal", "LEG-06; LEG-09", "Auditorias de cliente; especificações", "Anual", "Alta", "Alta", "RO-06", QUA),
        ("PI-06", "Fornecedores de polímero e PCR", "Externa", "Cadeia de abastecimento", "Previsibilidade das encomendas; critérios ambientais claros; prazos de pagamento.", "Recursos naturais", "Sim", "Não", "—", "", "Avaliação anual (RG-SGA-11); reunião mensal", "Mensal", "Média", "Média", "RO-05", CMP),
        ("PI-07", "Operadores de gestão de resíduos", "Externa", "Prestadores licenciados", "Resíduos segregados, classificados (LER) e com e-GAR corretas.", "Poluição", "Sim", "Sim", "Legal", "LEG-01; LEG-13", "e-GAR; certificados de destino", "Por recolha", "Média", "Média", "", LOG),
        ("PI-08", "APA / CCDR Centro", "Externa", "Autoridades ambientais", "Cumprimento de resíduos, emissões, licenças e comunicação de dados (MIRR, PRTR).", "Poluição", "Sim", "Sim", "Legal", "LEG-01; LEG-04; LEG-12; LEG-13", "Relatórios legais; SILiAmb", "Anual", "Alta", "Média", "RO-06", SGA),
        ("PI-09", "Câmara Municipal da Marinha Grande", "Externa", "Autoridade local", "Cumprimento do RGR (ruído) e do regulamento municipal de drenagem.", "Poluição", "Sim", "Sim", "Legal", "LEG-03; LEG-05", "Autorização de descarga; relatórios acústicos", "Por ocorrência", "Média", "Média", "RO-12", SGA),
        ("PI-10", "Entidade gestora de água e saneamento", "Externa", "Serviço público", "Descarga dentro dos VLE; uso eficiente de água em seca.", "Recursos naturais", "Sim", "Sim", "Legal", "LEG-03", "Autocontrolo semestral; comunicação de descargas anómalas", "Semestral", "Média", "Média", "RO-04", MAN),
        ("PI-11", "Comunidade / vizinhança (≈ 250 m)", "Externa", "Recetores sensíveis", "Sem ruído noturno, odores ou tráfego excessivo; resposta rápida a reclamações.", "Saúde dos ecossistemas", "Sim", "Sim", "Voluntária (compromisso assumido)", "LEG-05", "Canal de reclamações; reunião anual", "Anual", "Média", "Alta", "RO-12", SGA),
        ("PI-12", "Seguradora / banco", "Externa", "Financiadores", "Controlo do risco de incêndio e de danos ambientais; financiamento verde.", "Clima", "Sim", "Sim", "Voluntária (compromisso assumido)", "LEG-11", "Visita de risco anual; renovação da apólice", "Anual", "Média", "Baixa", "RO-08", FIN),
        ("PI-13", "Associação setorial (plásticos)", "Externa", "Setor", "Adesão ao programa Operation Clean Sweep (zero perdas de granulado).", "Saúde dos ecossistemas", "Sim", "Sim", "Voluntária (compromisso assumido)", "LEG-10", "Relatório anual OCS", "Anual", "Baixa", "Média", "RO-07", SGA),
        ("PI-14", "ONG ambientais", "Externa", "Sociedade civil", "Transparência sobre microplásticos e biodiversidade do Pinhal de Leiria.", "Biodiversidade", "Sim", "Não", "—", "", "Monitorização de media e redes", "Trimestral", "Baixa", "Média", "RO-07", SGA),
        ("PI-15", "Bombeiros / Proteção Civil", "Externa", "Emergência", "Medidas de autoproteção, plantas de emergência e retenção das águas de combate.", "Biodiversidade", "Sim", "Sim", "Legal", "LEG-11", "Simulacro anual conjunto", "Anual", "Média", "Baixa", "RO-08", DIND),
    ]
    cols = [
        col("ID_PI", 7, desc="Identificador da parte interessada.", key="PK"),
        col("Parte_Interessada", 30, desc="Parte interessada."),
        col("Tipo", 9, dv="PI_Tipo", desc="Interna ou externa."),
        col("Categoria", 24, desc="Categoria."),
        col("Necessidades_Expectativas", 50, desc="Necessidades e expectativas relevantes para o SGA (4.2 b)."),
        col("Condicao_Ambiental", 18, dv="PI_Cond", desc="Condição ambiental a que a expectativa se liga (ISO 14001:2026, 4.2 Nota 1)."),
        col("Relevante", 8, dv="PI_SimNao", desc="Se a parte é relevante para o SGA (4.2 a)."),
        col("Torna_se_Obrigacao", 9, dv="PI_SimNao", desc="Se a necessidade/expectativa é tratada como obrigação de conformidade (4.2 c)."),
        col("Tipo_Obrigacao", 22, dv="PI_Obrig", desc="Legal ou voluntária (compromisso que a organização decidiu cumprir)."),
        col("IDs_Legal", 18, desc="Requisitos legais associados (';').", key="FK → tbl_legal", req=False),
        col("Como_Monitorizar", 34, desc="Como a expectativa é acompanhada."),
        col("Frequencia", 12, desc="Frequência de acompanhamento."),
        col("Influencia", 9, dv="PI_Nivel", desc="Influência sobre a organização."),
        col("Interesse", 9, dv="PI_Nivel", desc="Interesse / grau de afetação."),
        col("Estrategia", 20, f='=IF(@ID_PI@="","",IF(AND(@Influencia@="Alta",@Interesse@="Alta"),"Gerir de perto",IF(@Influencia@="Alta","Manter satisfeita",IF(@Interesse@="Alta","Manter informada","Monitorizar"))))',
            desc="Matriz influência × interesse."),
        col("ID_RO", 8, desc="Risco/oportunidade associado.", key="FK → RG-SGA-02", req=False),
        col("Dono", 26, dv="Funcao", desc="Responsável pela relação."),
        col("Data_Revisao", 11, "date", desc="Última revisão."),
        col("IDs_Risco_SGI", 18, desc="Riscos/oportunidades do registo corporativo RG-SGA-02 (R-nn / O-nn).", key="FK → RG-SGA-02 tbRiscos/tbOportunidades", req=False),
        col("Percepcao_Risco", 44, desc="O que a parte teme ou valoriza (perceção do risco — vindo do RG-SGA-02).", req=False),
    ]
    rows = rows + [
        ("PI-16", "ACT — Autoridade para as Condições do Trabalho", "Externa", "Autoridade de SST", "Cumprimento da legislação de SST: avaliação de riscos (incl. agentes químicos e CMR), máquinas, LOTO e formação.",
         "Não aplicável", "Sim", "Sim", "Legal", "LEG-22", "Relatórios de SST; resposta a inspeções", "Por ocorrência", "Alta", "Média", "", RH),
    ]
    SGI_PI = {"PI-01": ("R9; R23; R28; R29", "Sentem pressão por meta e produtividade; o quase-acidente raramente é relatado."),
              "PI-03": ("R24; R25; O3; O4", "Esperam retorno dos investimentos em eficiência e menor custo da não-qualidade."),
              "PI-04": ("R16; R17; R18; R21; R33", "Um lote fora de especificação é visto como falha evitável (risco imposto ao cliente)."),
              "PI-05": ("R16; R17; R18; R21; R33", "Um lote fora de especificação é visto como falha evitável (risco imposto ao cliente)."),
              "PI-06": ("R13; R14; O7; O8", "O fornecedor spot vê a relação como transacional."),
              "PI-07": ("R31; O10", "Valorizam a segregação correta na origem."),
              "PI-08": ("R30; R31; R32", "A não conformidade ambiental é vista como dano à coletividade, sem margem de tolerância."),
              "PI-11": ("R30; R34", "O risco imposto por decisões da empresa gera mais indignação do que um risco voluntário."),
              "PI-12": ("R28; R30; R25", "Sensíveis a sinistros e a risco ambiental."),
              "PI-16": ("R28; R29", "Esperam avaliação de riscos registada e medidas de proteção coletiva antes do EPI.")}
    names = [c["name"] for c in cols if not c["f"]]
    data = [dict(zip(names, list(r) + [d("2026-09-24")] + list(SGI_PI.get(r[0], (None, None))))) for r in rows]
    b.table("Partes_Interessadas", "tbl_partes_interessadas", cols, data,
            "Partes interessadas, necessidades e expectativas (incl. condições ambientais) e decisão sobre obrigações de conformidade (4.2).",
            title="PARTES INTERESSADAS — NECESSIDADES, EXPECTATIVAS E OBRIGAÇÕES DE CONFORMIDADE (4.2)",
            subtitle="ISO 14001:2026 4.2 c): quais necessidades se tornam obrigações de conformidade · Obrigações legais ligam ao RG-SGA-04",
            cf=[("Torna_se_Obrigacao", {"Sim": "blue"}), ("Estrategia", {"perto": "red", "satisfeita": "orange", "informada": "yellow"})],
            row_height=45, extra_rows=10)


# ============================================================== incidentes
def extra_07(b):
    _ensure(b)
    b.add_list("INC_Tipo", ["Derrame", "Fuga de óleo", "Fuga de gás fluorado", "Perda de granulado", "Descarga anómala", "Emissão / odor",
                            "Reclamação externa", "Quase-incidente", "Condição anormal"])
    b.add_list("INC_Meio", ["Pavimento (contido)", "Solo", "Rede pluvial", "Coletor municipal", "Ar", "Ruído", "Recurso (água/energia)", "Nenhum"])
    b.add_list("INC_Cond", ["Anormal", "Emergência"])
    b.add_list("INC_Turno", ["1", "2", "3"])
    b.add_list("INC_SimNao", ["Sim", "Não"])
    b.add_list("INC_Estado", ["Aberto", "Em análise", "Fechado"])
    # (ID, data, tipo, processo, local, descrição, substância, qtd, unid, meio, contido, sev, condição, comunicado, EMG, aspeto, resposta, NC, custo, reportado, turno, estado)
    rows = [
        ("INC-2025-01", "2025-03-18", "Quase-incidente", "ARQ", "Armazém de químicos", "Bidão de solvente de 25 L tombado por empilhador; tampa fechada, sem derrame.", "Solvente de limpeza", 0, "L", "Nenhum", "Sim", 1, "Anormal", "Não", "EMG-01", "AA-005", "Bidão recolocado em bacia; corredor sinalizado.", "", 0, "Operador de Armazém / Empilhador", "1", "Fechado"),
        ("INC-2025-02", "2025-04-22", "Derrame", "SER", "Serigrafia SS-001", "Derrame de tinta durante a mudança de cor.", "Tinta de serigrafia", 2, "L", "Pavimento (contido)", "Sim", 2, "Anormal", "Não", "EMG-01", "AA-017", "Absorvente do KIT-04; resíduo 15 02 02*.", "", 60, "Operador de Serigrafia", "2", "Fechado"),
        ("INC-2025-03", "2025-05-30", "Perda de granulado", "REC", "Zona de descarga de big bags", "Big bag rasgado; parte do granulado arrastado pela chuva para a sarjeta.", "Granulado PP", 5, "kg", "Rede pluvial", "Não", 2, "Anormal", "Não", "EMG-06", "AA-003", "Varrimento e aspiração da sarjeta.", "", 120, "Chefe de Turno", "1", "Fechado"),
        ("INC-2025-04", "2025-06-26", "Reclamação externa", "SER", "Envolvente (vizinho a norte)", "Reclamação de odor a solvente durante a onda de calor.", "COV", None, "", "Ar", "Sim", 2, "Anormal", "Não", "", "AA-014", "Recipientes fechados; exaustão verificada; resposta ao reclamante (COM-EXT-2025-03).", "", 0, "Comunidade / vizinhança", "", "Fechado"),
        ("INC-2025-05", "2025-07-15", "Fuga de óleo", "INJ", "IM-003", "Fuga de óleo hidráulico no tabuleiro da máquina.", "Óleo hidráulico", 5, "L", "Pavimento (contido)", "Sim", 1, "Anormal", "Não", "EMG-03", "AA-009", "Tabuleiro esvaziado; óleo 13 01 10*.", "", 40, "Operador de Injeção", "3", "Fechado"),
        ("INC-2025-06", "2025-08-12", "Descarga anómala", "UTL", "Torre de arrefecimento TR-01", "Bomba doseadora avariada: sobredosagem de biocida na purga para o coletor.", "Biocida (isotiazolinona)", 40, "L", "Coletor municipal", "Não", 3, "Emergência", "Sim", "EMG-05", "AA-024", "Purga fechada; entidade gestora notificada (COM-EXT-2025-05); bomba substituída (OT-2025-14).", "", 850, "Técnico de Utilidades", "2", "Fechado"),
        ("INC-2025-07", "2025-11-18", "Fuga de gás fluorado", "UTL", "Chiller CH-01", "Fuga de R410A detetada no controlo de fugas.", "R410A", 3.2, "kg", "Ar", "Não", 3, "Emergência", "Não", "EMG-04", "AA-025", "Reparação da brasagem e recarga por técnico certificado (OT-2025-19).", "NC-SGA-25-03", 1450, "Técnico de Manutenção", "1", "Fechado"),
        ("INC-2025-08", "2025-12-09", "Quase-incidente", "PRS", "Parque de resíduos", "Contentor de tinta residual (08 03 12*) sem tampa sob chuva, detetado em ronda.", "Tinta residual", 0, "L", "Nenhum", "Sim", 1, "Anormal", "Não", "EMG-01", "AA-027", "Tampa colocada; reforço na ronda RON-08.", "", 0, "Auditor Interno do SGA", "1", "Fechado"),
        ("INC-2026-01", "2026-01-20", "Derrame", "MAN", "Oficina de manutenção", "Derrame durante a mudança de óleo de um redutor.", "Óleo mineral", 3, "L", "Pavimento (contido)", "Sim", 1, "Anormal", "Não", "EMG-03", "AA-026", "Absorvente do KIT-02.", "", 30, "Técnico de Manutenção", "1", "Fechado"),
        ("INC-2026-02", "2026-02-11", "Fuga de óleo", "SOP", "ISBM-005", "Fuga de ≈ 15 L de óleo hidráulico para o pavimento (mangueira envelhecida).", "Óleo hidráulico", 15, "L", "Pavimento (contido)", "Sim", 2, "Emergência", "Não", "EMG-03", "AA-013", "Contenção com absorventes; mangueira substituída (OT-2026-04).", "NC-SGA-26-00", 900, "Operador de Sopro (ISBM)", "2", "Fechado"),
        ("INC-2026-03", "2026-03-05", "Perda de granulado", "REC", "Zona dos silos", "Perda na trasfega pneumática; sarjeta sem filtro recebeu granulado.", "Granulado HDPE", 8, "kg", "Rede pluvial", "Não", 2, "Anormal", "Não", "EMG-06", "AA-003", "Aspiração; pedido de filtros de sarjeta (PAM-26-11).", "", 150, "Chefe de Turno", "1", "Fechado"),
        ("INC-2026-04", "2026-04-17", "Quase-incidente", "REC", "Armazém de MP", "Garfo do empilhador perfurou um big bag no interior; recolhido sem perdas para o exterior.", "Granulado PET", 1, "kg", "Pavimento (contido)", "Sim", 1, "Anormal", "Não", "EMG-06", "AA-003", "Recolha; formação de manobra.", "", 20, "Operador de Armazém / Empilhador", "2", "Fechado"),
        ("INC-2026-05", "2026-05-28", "Derrame", "SER", "Serigrafia SS-002", "Derrame de solvente na limpeza de ecrãs.", "Solvente de limpeza", 1, "L", "Pavimento (contido)", "Sim", 1, "Anormal", "Não", "EMG-01", "AA-014", "Absorvente; recipiente de segurança com fecho automático pedido.", "", 15, "Operador de Serigrafia", "3", "Fechado"),
        ("INC-2026-06", "2026-06-23", "Reclamação externa", "UTL", "Envolvente (habitações a sul)", "Reclamação de ruído noturno após a instalação dos compressores novos.", "Ruído", None, "", "Ruído", "Não", 2, "Anormal", "Não", "", "AA-022", "Resposta ao reclamante (COM-EXT-2026-08); medição indicativa interna.", "NC-SGA-26-01", 0, "Comunidade / vizinhança", "", "Fechado"),
        ("INC-2026-07", "2026-07-08", "Reclamação externa", "UTL", "Envolvente (habitações a sul)", "Segunda reclamação de ruído noturno (mesmo recetor).", "Ruído", None, "", "Ruído", "Não", 2, "Anormal", "Não", "", "AA-022", "Avaliação acústica acreditada contratada (PAM-26-03); conforme em 28/10/2026.", "NC-SGA-26-01", 0, "Comunidade / vizinhança", "", "Fechado"),
        ("INC-2026-08", "2026-07-21", "Condição anormal", "UTL", "Torre de arrefecimento TR-01", "Onda de calor: reposição de água +35% e alarme de temperatura dos moldes.", "Água de rede", 95, "m³", "Recurso (água/energia)", "Sim", 1, "Anormal", "Não", "", "AA-023", "Redução de carga no pico; revisão do OBJ-05.", "", 0, "Técnico de Utilidades", "2", "Fechado"),
        ("INC-2026-09", "2026-08-04", "Perda de granulado", "REC", "Zona de descarga de big bags", "Big bag rasgado; 1 sarjeta sem filtro — granulado na rede pluvial.", "Granulado PP", 12, "kg", "Rede pluvial", "Não", 3, "Emergência", "Não", "EMG-06", "AA-003", "Aspiração da caixa pluvial; prioridade ao PAM-26-11.", "", 380, "Chefe de Turno", "1", "Fechado"),
        ("INC-2026-10", "2026-08-19", "Condição anormal", "UTL", "Rede de ar comprimido", "Fuga em mangueira de ar comprimido (≈ 4 kW de perdas) sinalizada na ronda.", "Ar comprimido", None, "", "Recurso (água/energia)", "Sim", 1, "Anormal", "Não", "", "AA-021", "Mangueira substituída (OT-2026-17).", "", 45, "Técnico de Utilidades", "2", "Fechado"),
        ("INC-2026-11", "2026-09-12", "Derrame", "INJ", "Zona entre injeção e serigrafia", "Derrame de tinta com o KIT-03 incompleto (absorventes em falta).", "Tinta de serigrafia", 4, "L", "Pavimento (contido)", "Sim", 2, "Emergência", "Não", "EMG-01", "AA-005", "Absorvente de outro kit; KIT-03 reposto em 16/09.", "NC-SGA-26-03", 90, "Chefe de Turno", "2", "Fechado"),
        ("INC-2026-12", "2026-11-06", "Fuga de óleo", "INJ", "Injetora IM-004", "Rutura de mangueira hidráulica: ≈ 8 L de óleo no pavimento sem tabuleiro de retenção sob a unidade hidráulica.", "Óleo hidráulico", 8, "L", "Pavimento (contido)", "Sim", 2, "Anormal", "Não", "EMG-03", "AA-009", "Contenção com o KIT-02; mangueira substituída (OT-2026-24).", "NC-SGA-26-10", 260, "Operador de Injeção", "1", "Fechado"),
        ("INC-2026-13", "2026-12-17", "Quase-incidente", "ARQ", "Armazém de químicos", "Empilhador tocou num IBC de óleo durante a arrumação; sem rutura.", "Óleo hidráulico", None, "", "Nenhum", "Sim", 1, "Anormal", "Não", "EMG-01", "AA-005", "Marcação de corredor e batente de proteção instalados.", "", 120, "Operador de Armazém / Empilhador", "2", "Fechado"),
    ]
    cols = [
        col("ID_Incidente", 11, desc="Identificador do incidente (INC-AAAA-nn).", key="PK"),
        col("Data", 11, "date", desc="Data da ocorrência."),
        col("Ano_Mes", 8, "int", f='=IF(@Data@="","",YEAR(@Data@)*100+MONTH(@Data@))', desc="Automático aaaamm (para séries temporais; numérico para funcionar em Excel de qualquer idioma)."),
        col("Tipo", 18, dv="INC_Tipo", desc="Tipo de incidente."),
        col("Processo", 8, dv="Processo", desc="Processo.", key="FK → dim processo"),
        col("Local", 24, desc="Local."),
        col("Descricao", 44, desc="O que aconteceu."),
        col("Substancia", 18, desc="Substância / fluxo envolvido.", req=False),
        col("Quantidade", 9, "num", desc="Quantidade libertada.", req=False),
        col("Unidade", 7, desc="Unidade.", req=False),
        col("Meio_Afetado", 18, dv="INC_Meio", desc="Meio afetado."),
        col("Contido_no_Local", 8, dv="INC_SimNao", desc="Se foi contido sem atingir o meio exterior."),
        col("Severidade_1a5", 8, "int", desc="1 mínima … 5 muito grave."),
        col("Condicao", 11, dv="INC_Cond", desc="Condição anormal ou de emergência (ISO 14001:2026 6.1.2)."),
        col("Comunicado_Autoridade", 9, dv="INC_SimNao", desc="Se foi comunicado a autoridade/entidade gestora."),
        col("ID_Cenario_EMG", 9, desc="Cenário de emergência (RG-SGA-12).", key="FK → tbl_cenarios", req=False),
        col("ID_Aspeto", 8, desc="Aspeto ambiental.", key="FK → tbl_aspetos", req=False),
        col("Resposta_Imediata", 40, desc="Resposta e contenção."),
        col("ID_NC", 12, desc="NC aberta (quando aplicável).", key="FK → tbl_nc", req=False),
        col("Custo_EUR", 9, "eur", desc="Custo direto (limpeza, reparação, resíduos)."),
        col("Reportado_Por", 22, desc="Quem reportou."),
        col("Turno", 6, dv="INC_Turno", desc="Turno (vazio se externo).", req=False),
        col("Estado", 10, dv="INC_Estado", desc="Estado."),
        col("Classe_Gravidade", 12, f='=IF(@Severidade_1a5@="","",IF(@Severidade_1a5@>=4,"Grave",IF(@Severidade_1a5@=3,"Moderado","Leve")))', desc="Automático."),
    ]
    names = [c["name"] for c in cols if not c["f"]]
    data = []
    for r in rows:
        x = dict(zip(names, r))
        x["Data"] = d(x["Data"])
        data.append(x)
    b.table("Registo_Incidentes", "tbl_incidentes", cols, data,
            "Registo de incidentes, quase-incidentes, condições anormais e reclamações ambientais (1 linha por ocorrência).",
            title="REGISTO DE INCIDENTES E QUASE-INCIDENTES AMBIENTAIS",
            subtitle="Todos os incidentes são registados; os que exigem ação corretiva abrem NC (ID_NC) · Condição anormal ≠ emergência (ISO 14001:2026 6.1.2)",
            cf=[("Classe_Gravidade", {"Grave": "red", "Moderado": "orange", "Leve": "green"}), ("Contido_no_Local", {"Não": "orange"}),
                ("Condicao", {"Emergência": "red"})], row_height=40, extra_rows=40)


# ============================================================== 5.3 RACI
def extra_08(b):
    _ensure(b)
    b.add_list("RACI", ["R", "A", "C", "I", "R/A", "—"])
    roles = [("Diretor_Geral", DG), ("Diretor_Industrial", DIND), ("Gestor_SGA", SGA), ("Gerente_Producao", PROD), ("Gerente_Manutencao", MAN),
             ("Gerente_Qualidade", QUA), ("Resp_Armazem_Logistica", LOG), ("Resp_Compras", CMP), ("Resp_RD", RD), ("Resp_RH", RH),
             ("Diretor_Financeiro", FIN), ("Chefes_Turno", "Chefe de Turno"), ("Operadores", "Operadores")]
    P = [  # processo, cláusula, DG, DIND, SGA, PROD, MAN, QUA, LOG, CMP, RD, RH, FIN, CT, OP
        ("Contexto e partes interessadas", "4.1; 4.2", "A", "C", "R", "C", "C", "C", "I", "C", "C", "I", "C", "I", "I"),
        ("Âmbito e política ambiental", "4.3; 5.2", "R/A", "C", "R", "I", "I", "I", "I", "I", "I", "I", "I", "I", "I"),
        ("Liderança, recursos e revisão pela gestão", "5.1; 7.1; 9.3", "R/A", "R", "R", "C", "C", "C", "I", "I", "I", "C", "C", "I", "—"),
        ("Aspetos e impactes ambientais", "6.1.2", "I", "A", "R", "C", "C", "C", "C", "C", "C", "—", "—", "C", "I"),
        ("Obrigações de conformidade e avaliação", "6.1.3; 9.1.2", "I", "A", "R", "C", "C", "C", "C", "C", "C", "C", "I", "I", "—"),
        ("Riscos e oportunidades e planeamento de ações", "6.1.4; 6.1.5", "A", "R", "R", "C", "C", "C", "C", "C", "C", "C", "C", "I", "—"),
        ("Objetivos ambientais e programas", "6.2", "A", "R", "R", "R", "R", "C", "C", "C", "C", "I", "C", "I", "I"),
        ("Planeamento de alterações", "6.3", "A", "R", "C", "C", "R", "C", "I", "C", "R", "C", "C", "I", "I"),
        ("Competência e consciencialização", "7.2; 7.3", "I", "A", "C", "C", "C", "C", "C", "C", "C", "R", "—", "R", "I"),
        ("Comunicação interna e externa", "7.4", "A", "C", "R", "C", "C", "C", "C", "C", "C", "C", "I", "R", "I"),
        ("Informação documentada", "7.5", "I", "A", "R", "C", "C", "C", "C", "C", "C", "C", "—", "I", "I"),
        ("Controlo operacional da produção (injeção, sopro, decoração)", "8.1", "I", "A", "C", "R", "C", "C", "—", "—", "C", "—", "—", "R", "R"),
        ("Químicos, resíduos e perdas de granulado", "8.1", "I", "A", "C", "R", "C", "—", "R", "C", "—", "—", "—", "R", "R"),
        ("Utilidades, energia, água e F-gas", "8.1; 7.1", "I", "A", "C", "C", "R", "—", "—", "C", "—", "—", "C", "I", "I"),
        ("Processos, produtos e serviços externos", "8.1", "I", "A", "C", "C", "C", "C", "C", "R", "C", "—", "C", "—", "—"),
        ("Conceção de embalagens (ciclo de vida, PPWR)", "8.1; 6.1.2", "I", "A", "C", "C", "—", "C", "—", "C", "R", "—", "C", "—", "—"),
        ("Preparação e resposta a emergências", "8.2", "I", "A", "R", "C", "R", "—", "C", "—", "—", "C", "—", "R", "R"),
        ("Monitorização, medição e calibração", "9.1.1", "I", "A", "R", "C", "R", "C", "C", "—", "—", "—", "C", "I", "—"),
        ("Auditoria interna", "9.2", "I", "C", "A", "C", "C", "C", "C", "C", "C", "C", "I", "I", "—"),
        ("Não conformidades, incidentes e ação corretiva", "10.2", "I", "A", "R", "R", "R", "C", "R", "C", "C", "C", "I", "R", "R"),
        ("Melhoria contínua e Kaizen", "10.1", "A", "R", "R", "R", "C", "C", "C", "C", "C", "C", "C", "R", "R"),
        ("Dupla materialidade e reporte ESG", "4.1; 6.1.4", "A", "C", "R", "I", "I", "C", "I", "C", "C", "C", "R", "—", "—"),
        ("Avaliação de reciclabilidade (RecyClass) e graus PPWR", "8.1; 6.1.3", "I", "A", "C", "C", "—", "C", "—", "C", "R", "—", "—", "—", "—"),
        ("Documentação técnica e declaração UE de conformidade (PPWR, FCM)", "6.1.3; 7.5", "A", "C", "C", "I", "—", "R", "—", "C", "R", "—", "—", "—", "—"),
        ("Conteúdo reciclado e certificados de PCR", "8.1", "I", "A", "C", "C", "—", "C", "—", "R", "C", "—", "C", "—", "—"),
        ("RAP de embalagens e informação aos clientes por país", "6.1.3", "I", "C", "R", "—", "—", "—", "R", "—", "C", "—", "A", "—", "—"),
        ("Alegações ambientais de produto", "7.4", "A", "C", "R", "—", "—", "C", "—", "—", "R", "—", "C", "—", "—"),
    ]
    cols = [col("ID_Processo", 7, desc="Identificador.", key="PK"), col("Processo_SGA", 40, desc="Processo do SGA."), col("Clausula", 12, desc="Cláusulas ISO 14001:2026.")]
    for c, lab in roles:
        cols.append(col(c, 9, dv="RACI", desc=f"{lab}: R executa · A aprova e presta contas · C consultado · I informado."))
    rng = ",".join(f"@{c}@" for c, _ in roles)
    cols.append(col("N_Aprovadores", 9, "int", f=f'=IF(@ID_Processo@="","",COUNTIF(INDEX({{{rng}}},0),"A")+COUNTIF(INDEX({{{rng}}},0),"R/A"))' if False else
                    f'=IF(@ID_Processo@="","",' + "+".join(f'(@{c}@="A")+(@{c}@="R/A")' for c, _ in roles) + ")",
                    desc="N.º de funções com A (deve ser 1)."))
    cols.append(col("Controlo_RACI", 14, f='=IF(@ID_Processo@="","",IF(@N_Aprovadores@=1,"OK",IF(@N_Aprovadores@=0,"FALTA aprovador","Mais de um A")))', desc="Verificação: exatamente um A."))
    data = []
    for k, p in enumerate(P, start=1):
        x = {"ID_Processo": f"PS-{k:02d}", "Processo_SGA": p[0], "Clausula": p[1]}
        for (c, _), v in zip(roles, p[2:]):
            x[c] = v
        data.append(x)
    b.table("Matriz_RACI", "tbl_raci", cols, data,
            "Funções, responsabilidades e autoridades do SGA por processo (5.3), no formato RACI.",
            title="FUNÇÕES, RESPONSABILIDADES E AUTORIDADES — MATRIZ RACI (5.3)",
            subtitle="R executa · A aprova e presta contas (um por processo) · C consultado · I informado · A gestão de topo mantém a responsabilidade final (5.1)",
            cf=[("Controlo_RACI", {"OK": "green", "FALTA": "red", "Mais": "orange"})], row_height=30, extra_rows=5, freeze_col=2)


# ============================================================== 7.4 comunicações externas
def extra_09(b):
    _ensure(b)
    b.add_list("CE_Sentido", ["Recebida", "Enviada"])
    b.add_list("CE_Tipo", ["Reclamação", "Pedido de informação", "Questionário ESG", "Notificação", "Relatório legal", "Resposta", "Informação voluntária"])
    b.add_list("CE_Estado", ["Aberta", "Respondida", "Fechada"])
    rows = [
        ("COM-EXT-2025-01", "2025-03-28", "Enviada", "APA / CCDR Centro", "SILiAmb", "Submissão do MIRR 2024", "Relatório legal", "Resíduos", "", "2025-03-31", "2025-03-28", SGA, "", "", "Fechada"),
        ("COM-EXT-2025-02", "2025-05-12", "Recebida", "Clientes de cosmética (marcas UE)", "E-mail", "Questionário EcoVadis (marca A)", "Questionário ESG", "Clima; circularidade", "", "2025-06-15", "2025-06-10", SGA, "", "", "Fechada"),
        ("COM-EXT-2025-03", "2025-06-26", "Recebida", "Comunidade / vizinhança", "Telefone", "Reclamação de odor a solvente", "Reclamação", "Ar", "INC-2025-04", "2025-07-03", "2025-06-30", SGA, "", "", "Fechada"),
        ("COM-EXT-2025-04", "2025-06-30", "Enviada", "Comunidade / vizinhança", "Carta", "Resposta ao reclamante com medidas tomadas", "Resposta", "Ar", "INC-2025-04", "", "2025-06-30", SGA, "", "", "Fechada"),
        ("COM-EXT-2025-05", "2025-08-12", "Enviada", "Entidade gestora de água e saneamento", "E-mail + telefone", "Notificação de descarga anómala de biocida", "Notificação", "Água", "INC-2025-06", "2025-08-12", "2025-08-12", MAN, "", "", "Fechada"),
        ("COM-EXT-2025-06", "2025-08-20", "Recebida", "Entidade gestora de água e saneamento", "Ofício", "Pedido de boletim analítico extraordinário", "Pedido de informação", "Água", "INC-2025-06", "2025-09-05", "2025-09-02", MAN, "", "", "Fechada"),
        ("COM-EXT-2025-07", "2025-09-15", "Recebida", "Clientes de cosmética (marcas UE)", "Portal CDP", "Questionário CDP Supply Chain (marca B)", "Questionário ESG", "Clima", "", "2025-10-31", "2025-10-28", SGA, "", "", "Fechada"),
        ("COM-EXT-2025-08", "2025-11-20", "Enviada", "APA / CCDR Centro", "Plataforma F-gas", "Comunicação de fuga e reparação do CH-01", "Relatório legal", "Clima", "INC-2025-07", "2025-12-31", "2025-11-28", MAN, "NC-SGA-25-03", "", "Fechada"),
        ("COM-EXT-2026-01", "2026-02-04", "Enviada", "Câmara Municipal da Marinha Grande", "SIR / ePortugal", "Comunicação da substituição dos compressores (LEG-02)", "Notificação", "Licenciamento", "", "", "2026-02-04", DIND, "", "", "Fechada"),
        ("COM-EXT-2026-02", "2026-03-18", "Enviada", "APA / CCDR Centro", "SILiAmb", "Submissão do MIRR 2025", "Relatório legal", "Resíduos", "", "2026-03-31", "2026-03-18", SGA, "", "", "Fechada"),
        ("COM-EXT-2026-03", "2026-03-25", "Enviada", "APA / CCDR Centro", "E-mail", "Resultados da monitorização da chaminé FP1", "Relatório legal", "Ar", "", "2026-04-30", "2026-03-25", SGA, "", "", "Fechada"),
        ("COM-EXT-2026-04", "2026-04-09", "Recebida", "Clientes alimentar e farmacêutico", "E-mail", "Pedido de declaração de ausência de PFAS e de conformidade para contacto alimentar", "Pedido de informação", "Substâncias", "", "2026-04-30", "2026-04-27", QUA, "", "", "Fechada"),
        ("COM-EXT-2026-05", "2026-05-06", "Recebida", "Clientes de cosmética (marcas UE)", "E-mail", "Pedido de declarações PPWR para 7 famílias", "Pedido de informação", "Embalagens", "", "2026-07-31", "2026-12-22", RD, "", "PAM-26-10", "Fechada"),
        ("COM-EXT-2026-06", "2026-05-20", "Recebida", "Clientes de cosmética (marcas UE)", "E-mail", "Questionário EcoVadis (marca C)", "Questionário ESG", "Clima; circularidade", "", "2026-06-20", "2026-06-18", SGA, "", "", "Fechada"),
        ("COM-EXT-2026-07", "2026-06-05", "Recebida", "Seguradora / banco", "Visita", "Visita de risco da seguradora: plano de retenção das águas de combate", "Pedido de informação", "Emergência", "", "2026-07-05", "2026-07-02", DIND, "", "", "Fechada"),
        ("COM-EXT-2026-08", "2026-06-23", "Recebida", "Comunidade / vizinhança", "Formulário do site", "Reclamação de ruído noturno (compressores)", "Reclamação", "Ruído", "INC-2026-06", "2026-06-30", "2026-06-29", SGA, "NC-SGA-26-01", "PAM-26-03", "Respondida"),
        ("COM-EXT-2026-09", "2026-07-08", "Recebida", "Comunidade / vizinhança", "Telefone", "Segunda reclamação de ruído noturno", "Reclamação", "Ruído", "INC-2026-07", "2026-07-15", "2026-07-17", SGA, "NC-SGA-26-01", "PAM-26-03", "Respondida"),
        ("COM-EXT-2026-10", "2026-07-17", "Enviada", "Comunidade / vizinhança", "Carta + reunião", "Resposta: avaliação acústica acreditada contratada e prazo das medidas", "Resposta", "Ruído", "INC-2026-07", "", "2026-07-17", SGA, "", "PAM-26-03", "Fechada"),
        ("COM-EXT-2026-11", "2026-08-12", "Enviada", "Clientes de cosmética (marcas UE)", "Newsletter", "Informação sobre a aplicação do PPWR e o plano da Plasticom", "Informação voluntária", "Embalagens", "", "", "2026-08-12", RD, "", "PAM-26-10", "Fechada"),
        ("COM-EXT-2026-12", "2026-09-02", "Recebida", "Associação setorial (plásticos)", "E-mail", "Pedido do relatório anual Operation Clean Sweep", "Pedido de informação", "Granulado", "", "2026-10-15", "2026-10-12", SGA, "", "PAM-26-11", "Fechada"),
        ("COM-EXT-2026-13", "2026-09-10", "Recebida", "APA / CCDR Centro", "Ofício", "Campanha de fiscalização de e-GAR/MIRR: pedido de listagem de guias de 2026", "Pedido de informação", "Resíduos", "", "2026-10-10", "2026-10-08", LOG, "", "", "Fechada"),
        ("COM-EXT-2026-14", "2026-11-05", "Enviada", "Comunidade / vizinhança", "Carta", "Informação: avaliação acústica conforme e medidas implementadas nos compressores", "Resposta", "Ruído", "INC-2026-07", "", "2026-11-05", SGA, "NC-SGA-26-01", "PAM-26-03", "Fechada"),
        ("COM-EXT-2026-15", "2026-11-12", "Recebida", "Clientes de cosmética (marcas UE)", "Portal CDP", "Questionário CDP Supply Chain 2026 (marca B)", "Questionário ESG", "Clima", "", "2026-12-15", "2026-12-10", SGA, "", "", "Fechada"),
        ("COM-EXT-2026-16", "2026-12-14", "Recebida", "APA / CCDR Centro", "Ofício", "Resultado da fiscalização de e-GAR/MIRR: sem desconformidades", "Notificação", "Resíduos", "", "", "", LOG, "", "", "Fechada"),
    ]
    cols = [
        col("ID_Com_Ext", 14, desc="Identificador (COM-EXT-AAAA-nn).", key="PK"),
        col("Data", 11, "date", desc="Data de receção ou envio."),
        col("Sentido", 9, dv="CE_Sentido", desc="Recebida ou enviada."),
        col("Parte_Interessada", 28, desc="Parte interessada (tbl_partes_interessadas do RG-SGA-01)."),
        col("Canal", 14, desc="Canal."),
        col("Assunto", 44, desc="Assunto."),
        col("Tipo", 16, dv="CE_Tipo", desc="Tipo de comunicação."),
        col("Tema", 16, desc="Tema ambiental."),
        col("ID_Incidente", 11, desc="Incidente associado.", key="FK → tbl_incidentes", req=False),
        col("Prazo_Resposta", 11, "date", desc="Prazo de resposta (vazio se não aplicável).", req=False),
        col("Data_Resposta_Envio", 11, "date", desc="Data da resposta ou do envio.", req=False),
        col("Responsavel", 26, dv="Funcao", desc="Responsável."),
        col("ID_NC", 12, desc="NC associada.", key="FK → tbl_nc", req=False),
        col("ID_PAM", 10, desc="Ação do PAM.", key="FK → tbl_pam", req=False),
        col("Estado", 10, dv="CE_Estado", desc="Estado."),
        col("Dias_Resposta", 8, "int", f='=IF(OR(@Data_Resposta_Envio@="",@Sentido@="Enviada"),"",@Data_Resposta_Envio@-@Data@)', desc="Dias até à resposta (comunicações recebidas)."),
        col("No_Prazo", 8, f='=IF(@Prazo_Resposta@="","",IF(@Data_Resposta_Envio@="",IF(DataRef>@Prazo_Resposta@,"Atrasada","Em curso"),IF(@Data_Resposta_Envio@<=@Prazo_Resposta@,"Sim","Não")))', desc="Cumprimento do prazo."),
    ]
    names = [c["name"] for c in cols if not c["f"]]
    data = []
    for r in rows:
        x = dict(zip(names, r))
        for k in ("Data", "Prazo_Resposta", "Data_Resposta_Envio"):
            x[k] = d(x[k])
        data.append(x)
    b.table("Comunicacoes_Externas", "tbl_comunicacoes_externas", cols, data,
            "Registo de comunicações externas recebidas e enviadas (reclamações, pedidos, relatórios legais, questionários ESG) — 7.4.3.",
            title="REGISTO DE COMUNICAÇÕES EXTERNAS (7.4.3)",
            subtitle="Complementa a Matriz_Comunicacao (plano): aqui fica cada comunicação real, com prazo e resposta · Reclamações ligam a incidentes e NC",
            cf=[("No_Prazo", {"Não": "red", "Atrasada": "red", "Sim": "green"}), ("Tipo", {"Reclamação": "orange"})], row_height=30, extra_rows=40)


# ============================================================== 7.1 / 8.1 manutenção ambiental (inclui F-gas)
def extra_10(b):
    _ensure(b)
    b.add_list("MA_Tipo", ["Controlo de fugas F-gas", "Preventiva", "Corretiva", "Limpeza e desinfeção", "Inspeção", "Instalação"])
    b.add_list("MA_Exec", ["Interno", "Empresa externa"])
    b.add_list("MA_Res", ["Conforme", "Não conforme", "Corrigido"])
    b.add_list("MA_SimNao", ["Sim", "Não"])
    EQ = {"CH-01": "Chiller CH-01 (30 kg R410A)", "TR-01": "Torre de arrefecimento TR-01", "CMP-01": "Compressor CMP-01", "CMP-02": "Compressor CMP-02",
          "DB-01": "Bomba doseadora de biocida DB-01", "EX-FP1": "Exaustão / chaminé FP1 da serigrafia", "ISBM-005": "ISBM-005 (hidráulica)",
          "BR-01": "Bacia de retenção de águas de combate", "VC-01": "Válvula de corte da rede pluvial", "REDE-AR": "Rede de ar comprimido",
          "IM-004": "Injetora IM-004 (hidráulica)", "QGBT": "Quadros elétricos (QGBT e quadros dos USE)"}
    FG = "FrioTec — técnico certificado F-gas (cat. I)"
    rows = [
        ("OT-2025-03", "2025-05-20", "CH-01", "Controlo de fugas F-gas", "Controlo semestral de fugas (≥ 50 tCO2e).", "Empresa externa", FG, "Conforme", "Não", 0, 2, 180, "LEG-07", ""),
        ("OT-2025-04", "2025-06-10", "TR-01", "Limpeza e desinfeção", "Limpeza e desinfeção semestral; análise de Legionella.", "Empresa externa", "AquaHigiene Lda.", "Conforme", "Não", 0, 6, 950, "LEG-15", ""),
        ("OT-2025-05", "2025-06-18", "CMP-01", "Preventiva", "Manutenção 4.000 h do compressor antigo.", "Empresa externa", "Atlas Service PT", "Conforme", "Não", 0, 4, 1200, "", ""),
        ("OT-2025-07", "2025-07-02", "EX-FP1", "Preventiva", "Substituição de filtros da exaustão da serigrafia.", "Interno", "", "Conforme", "Não", 0, 3, 320, "LEG-12", ""),
        ("OT-2025-09", "2025-07-22", "REDE-AR", "Inspeção", "Deteção de fugas por ultrassons (12 fugas etiquetadas).", "Interno", "", "Não conforme", "Sim", 0, 6, 0, "LEG-08", ""),
        ("OT-2025-11", "2025-07-30", "REDE-AR", "Corretiva", "Reparação de 10 das 12 fugas de ar comprimido.", "Interno", "", "Corrigido", "Não", 0, 8, 260, "LEG-08", ""),
        ("OT-2025-14", "2025-08-12", "DB-01", "Corretiva", "Substituição da bomba doseadora avariada (sobredosagem).", "Interno", "", "Corrigido", "Não", 0, 3, 640, "LEG-03", "INC-2025-06"),
        ("OT-2025-15", "2025-09-08", "BR-01", "Inspeção", "Inspeção da bacia de retenção (estanquidade e limpeza).", "Interno", "", "Conforme", "Não", 0, 2, 0, "LEG-11", ""),
        ("OT-2025-16", "2025-09-08", "VC-01", "Inspeção", "Teste de manobra da válvula de corte pluvial.", "Interno", "", "Conforme", "Não", 0, 1, 0, "LEG-11", ""),
        ("OT-2025-17", "2025-10-14", "EX-FP1", "Preventiva", "Substituição de filtros da exaustão da serigrafia.", "Interno", "", "Conforme", "Não", 0, 3, 320, "LEG-12", ""),
        ("OT-2025-19", "2025-11-18", "CH-01", "Controlo de fugas F-gas", "Controlo semestral: fuga detetada; reparação da brasagem e recarga.", "Empresa externa", FG, "Corrigido", "Sim", 3.2, 6, 1450, "LEG-07", "INC-2025-07"),
        ("OT-2025-20", "2025-12-16", "CH-01", "Controlo de fugas F-gas", "Verificação pós-reparação (≤ 1 mês após a reparação).", "Empresa externa", FG, "Conforme", "Não", 0, 1, 120, "LEG-07", "INC-2025-07"),
        ("OT-2025-21", "2025-12-10", "TR-01", "Limpeza e desinfeção", "Limpeza e desinfeção semestral; análise de Legionella.", "Empresa externa", "AquaHigiene Lda.", "Conforme", "Não", 0, 6, 950, "LEG-15", ""),
        ("OT-2026-01", "2026-01-26", "EX-FP1", "Preventiva", "Substituição de filtros da exaustão da serigrafia.", "Interno", "", "Conforme", "Não", 0, 3, 320, "LEG-12", ""),
        ("OT-2026-02", "2026-02-02", "CMP-01", "Instalação", "Substituição dos compressores CMP-01/02 por unidades de velocidade variável (ALT-2026-01).", "Empresa externa", "Atlas Service PT", "Conforme", "Não", 0, 24, 78000, "LEG-02; LEG-05", ""),
        ("OT-2026-04", "2026-02-12", "ISBM-005", "Corretiva", "Substituição da mangueira hidráulica e plano de substituição por horas.", "Interno", "", "Corrigido", "Não", 0, 5, 700, "", "INC-2026-02"),
        ("OT-2026-06", "2026-03-15", "ISBM-005", "Preventiva", "Substituição preventiva de mangueiras hidráulicas (> 20.000 h).", "Interno", "", "Conforme", "Não", 0, 10, 1900, "", ""),
        ("OT-2026-08", "2026-04-20", "EX-FP1", "Preventiva", "Substituição de filtros da exaustão da serigrafia.", "Interno", "", "Conforme", "Não", 0, 3, 320, "LEG-12", ""),
        ("OT-2026-10", "2026-05-20", "CH-01", "Controlo de fugas F-gas", "Controlo semestral de fugas.", "Empresa externa", FG, "Conforme", "Não", 0, 2, 180, "LEG-07", ""),
        ("OT-2026-11", "2026-06-09", "TR-01", "Limpeza e desinfeção", "Limpeza e desinfeção semestral; análise de Legionella.", "Empresa externa", "AquaHigiene Lda.", "Conforme", "Não", 0, 6, 980, "LEG-15", ""),
        ("OT-2026-13", "2026-06-24", "CMP-02", "Preventiva", "Manutenção 2.000 h dos compressores novos.", "Empresa externa", "Atlas Service PT", "Conforme", "Não", 0, 4, 900, "", ""),
        ("OT-2026-15", "2026-07-13", "REDE-AR", "Inspeção", "Deteção de fugas por ultrassons (9 fugas etiquetadas).", "Interno", "", "Não conforme", "Sim", 0, 6, 0, "LEG-08", ""),
        ("OT-2026-17", "2026-08-19", "REDE-AR", "Corretiva", "Substituição de mangueira com fuga e reparação de 5 fugas.", "Interno", "", "Corrigido", "Não", 0, 5, 210, "LEG-08", "INC-2026-10"),
        ("OT-2026-18", "2026-08-24", "EX-FP1", "Preventiva", "Substituição de filtros da exaustão da serigrafia.", "Interno", "", "Conforme", "Não", 0, 3, 330, "LEG-12", ""),
        ("OT-2026-19", "2026-09-07", "BR-01", "Inspeção", "Inspeção da bacia de retenção (seca e limpa).", "Interno", "", "Conforme", "Não", 0, 2, 0, "LEG-11", ""),
        ("OT-2026-20", "2026-09-07", "VC-01", "Inspeção", "Teste de manobra da válvula de corte (3 min).", "Interno", "", "Conforme", "Não", 0, 1, 0, "LEG-11", ""),
        ("OT-2026-21", "2026-10-20", "TR-01", "Limpeza e desinfeção", "Limpeza e desinfeção semestral; análise de Legionella.", "Empresa externa", "AquaHigiene Lda.", "Conforme", "Não", 0, 6, 990, "LEG-15", ""),
        ("OT-2026-22", "2026-10-26", "EX-FP1", "Preventiva", "Substituição de filtros da exaustão da serigrafia.", "Interno", "", "Conforme", "Não", 0, 3, 330, "LEG-12", ""),
        ("OT-2026-23", "2026-11-18", "CH-01", "Controlo de fugas F-gas", "Controlo semestral de fugas (sem fugas).", "Empresa externa", FG, "Conforme", "Não", 0, 2, 185, "LEG-07", ""),
        ("OT-2026-24", "2026-11-06", "IM-004", "Corretiva", "Substituição da mangueira hidráulica rompida; tabuleiro de retenção sob a unidade hidráulica.", "Interno", "", "Corrigido", "Não", 0, 4, 640, "", "INC-2026-12"),
        ("OT-2026-25", "2026-12-09", "REDE-AR", "Inspeção", "Deteção de fugas por ultrassons (3 fugas etiquetadas e reparadas).", "Interno", "", "Corrigido", "Sim", 0, 5, 90, "LEG-08", ""),
        ("OT-2026-26", "2026-12-11", "VC-01", "Inspeção", "Teste de manobra da válvula de corte no simulacro (4 min).", "Interno", "", "Conforme", "Não", 0, 1, 0, "LEG-11", ""),
        ("OT-2026-27", "2026-12-15", "QGBT", "Instalação", "Instalação de 6 analisadores de energia e 3 contadores de água com telemetria (PAM-26-02).", "Empresa externa", "Instalador certificado", "Conforme", "Não", 0, 40, 24000, "LEG-08", ""),
    ]
    PER = {"Controlo de fugas F-gas": 6, "Limpeza e desinfeção": 6, "Preventiva": 3, "Inspeção": 12}
    cols = [
        col("ID_OT", 10, desc="Ordem de trabalho.", key="PK"),
        col("Data", 11, "date", desc="Data da intervenção."),
        col("ID_Equipamento", 10, desc="Equipamento."),
        col("Equipamento", 30, f=None, desc="Descrição do equipamento."),
        col("Tipo_Intervencao", 20, dv="MA_Tipo", desc="Tipo de intervenção."),
        col("Descricao", 44, desc="Trabalho realizado."),
        col("Executante", 13, dv="MA_Exec", desc="Interno ou empresa externa."),
        col("Empresa_Tecnico", 30, desc="Empresa e certificação (F-gas: técnico certificado obrigatório).", req=False),
        col("Resultado", 12, dv="MA_Res", desc="Resultado."),
        col("Fuga_Detetada", 8, dv="MA_SimNao", desc="Se foi detetada fuga (gás, ar, óleo)."),
        col("Fluido_Recarregado_kg", 9, "num", desc="Gás fluorado recarregado (kg)."),
        col("Horas", 7, "num", desc="Horas de trabalho."),
        col("Custo_EUR", 10, "eur", desc="Custo."),
        col("ID_Legal", 12, desc="Requisito legal associado.", key="FK → tbl_legal", req=False),
        col("ID_Incidente", 11, desc="Incidente associado.", key="FK → tbl_incidentes (RG-SGA-07)", req=False),
        col("tCO2e_Fuga", 9, "num", f='=IF(@Fluido_Recarregado_kg@="","",ROUND(@Fluido_Recarregado_kg@*2088/1000,2))', desc="Emissão equivalente da recarga (R410A, GWP 2.088)."),
        col("Proxima_Intervencao", 11, "date", f=('=IF(@Data@="","",IF(@Tipo_Intervencao@="Controlo de fugas F-gas",EDATE(@Data@,6),IF(@Tipo_Intervencao@="Limpeza e desinfeção",EDATE(@Data@,6),'
                                                  'IF(@Tipo_Intervencao@="Preventiva",EDATE(@Data@,3),IF(@Tipo_Intervencao@="Inspeção",EDATE(@Data@,12),"")))))'),
            desc="Próxima intervenção periódica (F-gas e desinfeção 6 meses; preventiva 3; inspeção 12)."),
    ]
    names = [c["name"] for c in cols if not c["f"]]
    data = []
    for r in rows:
        x = dict(zip([n for n in names if n != "Equipamento"], r))
        x["Equipamento"] = EQ[x["ID_Equipamento"]]
        x["Data"] = d(x["Data"])
        data.append(x)
    b.table("Manutencao_Ambiental", "tbl_manutencao_ambiental", cols, data,
            "Manutenção de equipamentos com relevância ambiental: controlo de fugas F-gas, torre (Legionella), compressores, exaustão, meios de emergência (7.1, 8.1).",
            title="MANUTENÇÃO DE EQUIPAMENTOS COM RELEVÂNCIA AMBIENTAL (7.1 · 8.1 · F-gas)",
            subtitle="Controlo de fugas do CH-01 semestral (Reg. (UE) 2024/573) · Torre TR-01: limpeza/desinfeção semestral e Legionella trimestral (Lei 52/2018)",
            cf=[("Resultado", {"Não conforme": "red", "Corrigido": "orange", "Conforme": "green"}), ("Fuga_Detetada", {"Sim": "orange"})],
            row_height=30, extra_rows=40)


# ============================================================== 8.1 processos externos → colunas nas tabelas de fornecedores (RG-SGA-11)
# Tipo e extensão do controlo/influência (ISO 14001:2026 8.1) acrescentados como colunas a tbl_fornecedores e tbl_outros_fornecedores.
FORN_CTRL = {  # ID_Fornecedor: (IDs_Aspetos, Tipo_Controlo, Extensao_Controlo)
    "SUP-001": ("AA-001; AA-002", "Influência", "Critérios ambientais no contrato e avaliação anual; sem controlo da produção do polímero."),
    "SUP-002": ("AA-001; AA-002", "Influência", "Contrato com critérios; PP-PCR aceite só com certificado de conteúdo reciclado."),
    "SUP-003": ("AA-001; AA-002", "Influência", "Critérios ambientais no contrato e avaliação anual."),
    "SUP-004": ("AA-001; AA-002", "Controlo", "PCR/rPET aceite só com certificado por lote e inspeção de receção; auditoria ao reciclador."),
    "SUP-005": ("AA-001; AA-002", "Controlo", "Compra spot bloqueada sem avaliação ambiental; inspeção reforçada de cada lote."),
    "SUP-006": ("AA-001; AA-002", "Influência", "Critérios ambientais no contrato e avaliação anual."),
    "SUP-007": ("AA-001; AA-002", "Influência", "Critérios ambientais no contrato e avaliação anual."),
    "SUP-008": ("AA-015", "Controlo", "Aprovação prévia de FDS e restrição de substâncias (SVHC, PFAS)."),
    "SUP-009": ("AA-001", "Controlo", "Declaração de conformidade para contacto farmacêutico por lote."),
    "SUP-010": ("AA-001", "Controlo", "Declaração de conformidade para contacto alimentar por lote."),
}
# colunas 8.1 de tbl_outros_fornecedores: ID → (IDs_Aspetos, Relevância, Tipo_Controlo, Extensão, Mecanismos, Frequência, Última verificação, Resultado, Responsável)
OUTROS_CTRL = {
    "TRP-01": ("AA-040", "Média", "Influência", "Frota Euro VI; consolidação de cargas; reporte anual de t.km e tCO2e.", "Contrato; relatório anual", "Anual", "2026-03-31", "Com reservas", LOG),
    "OGR-01": ("AA-028; AA-029", "Alta", "Controlo", "Operador licenciado para os LER entregues; operação R3; e-GAR confirmada.", "Verificação de licença; e-GAR; certificado de reciclagem", "Por recolha", "2026-09-19", "Conforme", LOG),
    "OGR-06": ("AA-016; AA-026", "Alta", "Controlo", "Licença para 08 03 12*, 15 01 10*, 15 02 02*; destino de valorização.", "Verificação de licença; e-GAR; destino final", "Por recolha", "2026-09-19", "Conforme", LOG),
    "LIM-01": ("AA-029", "Baixa", "Controlo", "Produtos com rótulo ecológico; segregação de resíduos; formação.", "Lista de produtos e FDS; registo de formação", "Anual", "2026-02-20", "Conforme", LOG),
}
OUTROS_NOVOS = [  # 6 colunas originais + 9 colunas 8.1
    # fornecedores de produtos químicos (IDs usados no RG-SGA-21 — inventário, FDS e declarações)
    ("PQ-01", "InkTec Ibérica, Lda. (tintas, diluentes, endurecedores, emulsões)", "Fornecedor de produtos químicos", "FDS em PT no formato do Reg. 2020/878; sem CMR 1A/1B nem SVHC; declaração SVHC anual com a versão da lista.",
     "FDS; declaração SVHC; ficha técnica", "Aquisição: substâncias perigosas usadas na serigrafia",
     "AA-015; AA-016", "Alta", "Controlo", "Aprovação prévia de cada produto (PR-SGA-16); verificação de cada FDS.", "RG-SGA-21 tbl_fds e tbl_declaracoes", "Por receção", "2026-05-14", "Com reservas", "Responsável de Compras"),
    ("PQ-02", "QuimiLeiria, Lda. (solventes de limpeza e isopropanol)", "Fornecedor de produtos químicos", "FDS em PT (Reg. 2020/878) com cenários de exposição; embalagens com fecho de segurança.",
     "FDS alargada; declaração SVHC", "Aquisição: solventes (COV)", "AA-006; AA-014", "Alta", "Controlo", "Aprovação prévia; verificação da FDS e dos cenários de exposição.", "RG-SGA-21 tbl_fds e tbl_ce_reach", "Por receção", "2026-03-02", "Conforme", "Responsável de Compras"),
    ("PQ-03", "LubriCentro, S.A. (óleos, aerossóis técnicos, colas)", "Fornecedor de produtos químicos", "FDS em PT; aerossóis sem SVHC (n-hexano, D4/D5/D6); óleos com recolha de embalagens.",
     "FDS; declaração SVHC", "Aquisição: manutenção", "AA-009; AA-026", "Média", "Controlo", "Aprovação prévia; verificação da FDS.", "RG-SGA-21 tbl_fds", "Por receção", "2026-03-18", "Com reservas", "Responsável de Compras"),
    ("PQ-04", "GasLis, S.A. (propano, acetileno, oxigénio)", "Fornecedor de produtos químicos", "Garrafas com inspeção periódica válida; FDS em PT; recolha das garrafas vazias.",
     "FDS; certificado de inspeção das garrafas", "Aquisição: gases", "AA-015; AA-026", "Média", "Controlo", "Verificação na receção.", "RG-SGA-21 tbl_fds", "Por receção", "2026-12-02", "Conforme", "Responsável de Compras"),
    ("PQ-05", "CombustLeiria, Lda. (gasóleo)", "Fornecedor de produtos químicos", "Descarga com operador presente e bacia; FDS em PT.",
     "FDS; guia de entrega", "Aquisição: combustível", "AA-029", "Média", "Controlo", "Supervisão da descarga.", "RG-SGA-21 tbl_fds", "Por receção", "2026-11-05", "Conforme", "Responsável de Armazém e Logística"),
    ("PQ-06", "LabQuímica, Lda. (reagentes de laboratório)", "Fornecedor de produtos químicos", "FDS em PT; pequenas embalagens.",
     "FDS", "Aquisição: laboratório", "AA-029", "Baixa", "Controlo", "Verificação da FDS.", "RG-SGA-21 tbl_fds", "Por receção", "2026-05-02", "Conforme", "Gerente da Qualidade"),
    ("PQ-07", "FoilTech S.r.l. (foil de hot stamping)", "Fornecedor de produtos químicos", "Declaração SVHC e PFAS do foil (artigo); declaração para contacto alimentar quando aplicável.",
     "Declaração SVHC/PFAS", "Aquisição: decoração (artigo)", "AA-018; AA-019", "Média", "Influência", "Pedido de declaração anual.", "RG-SGA-21 tbl_declaracoes", "Anual", "2026-11-20", "Conforme", "Responsável de Compras"),
    ("MAN-01", "FrioTec — manutenção do chiller e gases fluorados", "Prestador de serviços", "Técnico com certificado F-gas; controlo de fugas semestral; registo no livro do equipamento.",
     "Certificado do técnico; relatório de intervenção", "Produção: emissões de gases fluorados",
     "AA-025", "Alta", "Controlo", "Contrato com técnico certificado; controlo de fugas semestral do CH-01.", "Contrato; verificação do certificado; relatório", "Semestral", "2026-05-20", "Conforme", MAN),
    ("TOR-01", "AquaHigiene — limpeza e desinfeção da torre", "Prestador de serviços", "Plano de prevenção da Legionella; produtos biocidas autorizados.",
     "Plano; relatório de limpeza; boletins de Legionella", "Produção: água e efluente da torre",
     "AA-023; AA-024", "Alta", "Controlo", "Limpeza e desinfeção semestral; Legionella trimestral (Lei 52/2018).", "Contrato; plano; boletins", "Trimestral", "2026-09-08", "Conforme", MAN),
    ("LAB-01", "Laboratório acreditado (efluente, emissões, ruído, Legionella)", "Prestador de serviços", "Acreditação ISO/IEC 17025 para os ensaios; métodos normalizados.",
     "Anexo técnico de acreditação IPAC; relatórios de ensaio", "Monitorização (9.1)",
     "AA-024; AA-014; AA-022", "Alta", "Controlo", "Só ensaios acreditados contam para a conformidade legal.", "Verificação da acreditação", "Por ensaio", "2026-06-12", "Conforme", SGA),
    ("ENE-01", "Comercializador de eletricidade", "Prestador de serviços", "Garantias de origem renováveis; informação do mix energético.",
     "Rótulo de energia; garantias de origem", "Produção: energia",
     "AA-031", "Média", "Influência", "Contrato com 55% de origem renovável; negociação de quota maior.", "Contrato; rótulo anual", "Anual", "2026-01-15", "Conforme", FIN),
    ("MOL-01", "Moldes Marinha — manutenção de moldes (subcontratada)", "Prestador de serviços", "Gestão dos resíduos e óleos da oficina; devolução de moldes limpos.",
     "Declaração de gestão de resíduos", "Produção (processo externo)",
     "AA-012", "Média", "Influência", "Requisitos ambientais na encomenda; sem acesso à oficina do subcontratado.", "Requisitos na encomenda", "Anual", None, "Por verificar", PROD),
]


def outros_lists(b):
    _ensure(b)
    b.add_list("PE_Ctrl", ["Controlo", "Influência"])
    b.add_list("PE_Rel", ["Alta", "Média", "Baixa"])
    b.add_list("PE_Res", ["Conforme", "Com reservas", "Não conforme", "Por verificar"])


def forn_cols():
    """Colunas 8.1 acrescentadas a tbl_fornecedores."""
    return [col("IDs_Aspetos", 14, desc="Aspetos ambientais associados.", key="FK → tbl_aspetos (RG-SGA-03)"),
            col("Tipo_Controlo", 10, dv="PE_Ctrl", desc="Controlo ou influência (ISO 14001:2026 8.1)."),
            col("Extensao_Controlo", 44, desc="Extensão do controlo ou da influência definida pelo SGA.")]


def outros_cols():
    """Colunas 8.1 acrescentadas a tbl_outros_fornecedores."""
    return [
        col("IDs_Aspetos", 14, desc="Aspetos ambientais associados.", key="FK → tbl_aspetos (RG-SGA-03)"),
        col("Relevancia_SGA", 9, dv="PE_Rel", desc="Relevância para os resultados pretendidos do SGA."),
        col("Tipo_Controlo", 10, dv="PE_Ctrl", desc="Controlo ou influência (ISO 14001:2026 8.1)."),
        col("Extensao_Controlo", 44, desc="Extensão do controlo ou da influência definida pelo SGA."),
        col("Mecanismos", 30, desc="Como o controlo é exercido."),
        col("Frequencia_Verificacao", 12, desc="Frequência de verificação."),
        col("Ultima_Verificacao", 11, "date", desc="Última verificação.", req=False),
        col("Resultado", 12, dv="PE_Res", desc="Resultado da última verificação."),
        col("Responsavel", 26, dv="Funcao", desc="Responsável."),
        col("Alerta", 18, f='=IF(@ID@="","",IF(@Resultado@="Não conforme","Ação necessária",IF(@Ultima_Verificacao@="","Sem verificação",IF(DataRef-@Ultima_Verificacao@>400,"Verificação vencida","OK"))))', desc="Automático."),
    ]


def outros_rows(outros, base_names):
    extra = ["IDs_Aspetos", "Relevancia_SGA", "Tipo_Controlo", "Extensao_Controlo", "Mecanismos", "Frequencia_Verificacao", "Ultima_Verificacao", "Resultado", "Responsavel"]
    rows = []
    for o in outros:
        x = dict(zip(base_names, o))
        x.update(dict(zip(extra, OUTROS_CTRL[o[0]])))
        rows.append(x)
    for o in OUTROS_NOVOS:
        x = dict(zip(base_names, o[:6]))
        x.update(dict(zip(extra, o[6:])))
        rows.append(x)
    for x in rows:
        x["Ultima_Verificacao"] = d(x["Ultima_Verificacao"])
    return rows


# ============================================================== 9.1 dimensão mês com faturas (colunas acrescentadas a tbl_meses do RG-SGA-13)
def dim_mes(b, mm):
    """Dim_Mes com colunas de faturação: consumos lidos de tbl_dados_ambientais por fórmula; preços e tarifas como entrada."""
    import numpy as np
    rng = np.random.default_rng(1401)
    rows = []
    for r in mm.to_dict("records"):
        m = r["Mes"]
        base = 0.118 if m.year == 2025 else 0.131
        r.update(Fatura_Eletricidade=f"FE-{m:%Y%m}-{int(rng.integers(1000, 9999))}",
                 Preco_Eletricidade_EUR_kWh=round(base + 0.012 * float(np.cos((m.month - 1) / 12 * 2 * np.pi)) + float(rng.normal(0, 0.003)), 4),
                 Potencia_Contratada_kW=1350, Fatura_Agua=f"FA-{m:%Y%m}",
                 Tarifa_Agua_EUR_m3=1.62 if m.year == 2025 else 1.71, Tarifa_Saneamento_EUR_m3=1.05 if m.year == 2025 else 1.11)
        rows.append(r)
    S = 'SUMIFS(tbl_dados_ambientais[Valor],tbl_dados_ambientais[Mes],@Mes@,tbl_dados_ambientais[Variavel],"{}")'
    cols = [col("Mes", 11, "date", desc="Mês (1.º dia).", key="PK"), col("Ano", 6, "int", desc="Ano."), col("Mes_Num", 6, "int", desc="Mês (1-12)."),
            col("Trimestre", 9, desc="Trimestre."), col("Temp_Media_C", 9, "num1", desc="Temperatura média exterior (°C) — variável explicativa (KPI-16)."),
            col("Dias_Uteis", 7, "int", desc="Dias úteis."), col("Periodo_Dataset", 18, desc="Origem dos dados de produção."),
            col("Fatura_Eletricidade", 18, desc="N.º da fatura de eletricidade do mês."),
            col("Energia_kWh", 12, "num0", f="=" + S.format("ENE_TOTAL"), desc="Eletricidade faturada (ENE_TOTAL de tbl_dados_ambientais)."),
            col("Preco_Eletricidade_EUR_kWh", 10, "num3", desc="Preço médio (energia + redes + impostos, sem IVA) — simulado; validar com a fatura."),
            col("Potencia_Contratada_kW", 9, "num0", desc="Potência contratada."),
            col("Custo_Eletricidade_EUR", 12, "eur", f='=ROUND(@Energia_kWh@*@Preco_Eletricidade_EUR_kWh@,0)', desc="Custo da eletricidade."),
            col("Fatura_Agua", 11, desc="N.º da fatura de água do mês."),
            col("Agua_m3", 9, "num0", f="=" + S.format("AGUA_TOTAL"), desc="Água faturada (AGUA_TOTAL de tbl_dados_ambientais)."),
            col("Tarifa_Agua_EUR_m3", 8, "num", desc="Tarifa variável de água (€/m³)."),
            col("Tarifa_Saneamento_EUR_m3", 8, "num", desc="Tarifa variável de saneamento (€/m³)."),
            col("Custo_Agua_EUR", 10, "eur", f='=ROUND(@Agua_m3@*(@Tarifa_Agua_EUR_m3@+@Tarifa_Saneamento_EUR_m3@),0)', desc="Custo de água e saneamento."),
            col("Custo_por_MWh_EUR", 9, "eur", f='=IFERROR(ROUND(@Custo_Eletricidade_EUR@/@Energia_kWh@*1000,0),"")', desc="Custo médio por MWh (série para previsão de preço)."),
            col("Agua_Torre_m3", 9, "num0", f='=SUMIFS(tbl_dados_ambientais[Valor],tbl_dados_ambientais[Mes],@Mes@,tbl_dados_ambientais[Variavel],"AGUA_USO",tbl_dados_ambientais[Processo],"UTL-FRIO")',
                desc="Reposição da torre de arrefecimento (AGUA_USO UTL-FRIO)."),
            col("Agua_Consumida_m3", 9, "num0", f='=ROUND(@Agua_Torre_m3@*0.8,0)', desc="Consumo (evaporação na torre ≈ 80% da reposição; 20% sai como purga) — GRI 303-5 / ESRS E3-4."),
            col("Agua_Descarregada_m3", 9, "num0", f='=@Agua_m3@-@Agua_Consumida_m3@', desc="Descarga no coletor (sanitária + purga) = captação − consumo — GRI 303-4."),
            ]
    b.table("Dim_Mes", "tbl_meses", cols, rows,
            "Dimensão mês com temperatura, dias úteis e faturas de eletricidade e água (consumo, preço, custo, emissões do âmbito 2).",
            row_height=18, freeze_col=1)


# ============================================================== 9.1 análises laboratoriais (RG-SGA-13)
def extra_13(b):
    _ensure(b)
    b.add_list("AN_Matriz", ["Efluente (coletor municipal)", "Água da torre", "Águas pluviais", "Ruído ambiente", "Emissões — chaminé FP1"])
    b.add_list("AN_Limite", ["VLE legal", "Limiar legal de ação", "Valor de referência interno"])
    b.add_list("AN_SimNao", ["Sim", "Não"])
    # análises laboratoriais: (data, matriz, ponto, parâmetro, valor, unidade, lim_min, lim_max, tipo_limite, laboratório, acreditado, relatório, ID_Legal)
    LAB, INT = "Laboratório acreditado (IPAC L0xxx)", "Medição interna (sonómetro classe 2)"
    an = []
    for dia, rel, v in (("2025-06-11", "25/1033", (7.6, 162, 44, 61, 12)), ("2025-12-10", "25/2210", (7.9, 131, 35, 48, 9)),
                        ("2026-06-12", "26/1187", (7.8, 145, 38, 55, 10)), ("2026-12-10", "26/2410", (7.6, 132, 31, 45, 8))):
        for p, val, u, lo, hi in (("pH", v[0], "Escala Sørensen", 5.5, 9.5), ("CQO", v[1], "mg/L O2", None, 1000), ("SST", v[2], "mg/L", None, 1000),
                                  ("CBO5", v[3], "mg/L O2", None, 500), ("Óleos e gorduras", v[4], "mg/L", None, 100)):
            an.append((dia, "Efluente (coletor municipal)", "Caixa de visita final", p, val, u, lo, hi, "VLE legal", LAB, "Sim", rel, "LEG-03"))
    an.append(("2025-08-13", "Efluente (coletor municipal)", "Caixa de visita final", "Isotiazolinonas (biocida)", 2.8, "mg/L", None, 1.0,
               "Valor de referência interno", LAB, "Sim", "25/1520", "LEG-03"))
    for dia, val, rel in (("2025-03-12", 50, "L25-0311"), ("2025-06-10", 100, "L25-0610"), ("2025-08-14", 1200, "L25-0814"), ("2025-09-09", 50, "L25-0909"),
                          ("2025-12-10", 50, "L25-1210"), ("2026-03-11", 100, "L26-0311"), ("2026-06-09", 150, "L26-0609"), ("2026-09-08", 100, "L26-0908"), ("2026-12-07", 50, "L26-1207")):
        an.append((dia, "Água da torre", "Bacia da torre TR-01", "Legionella spp.", val, "UFC/L", None, 1000, "Limiar legal de ação", LAB, "Sim", rel, "LEG-15"))
    for dia, sst, hc, rel in (("2025-11-20", 48, 0.6, "25/2101"), ("2026-04-22", 31, 0.4, "26/0907"), ("2026-11-19", 29, 0.3, "26/2288")):
        an.append((dia, "Águas pluviais", "Caixa de saída pluvial (portão sul)", "SST", sst, "mg/L", None, 60, "Valor de referência interno", LAB, "Sim", rel, "LEG-03"))
        an.append((dia, "Águas pluviais", "Caixa de saída pluvial (portão sul)", "Hidrocarbonetos totais", hc, "mg/L", None, 10, "Valor de referência interno", LAB, "Sim", rel, "LEG-03"))
    for dia, rel, lab, ac, vals in (("2023-09-14", "AC-2023-041", LAB, "Sim", (("Ln (recetor R1)", 47), ("Incomodidade noturna ΔLA (R1)", 2))),
                                    ("2026-07-10", "MI-2026-07", INT, "Não", (("Ln (recetor R1)", 51), ("Incomodidade noturna ΔLA (R1)", 5))),
                                    ("2026-10-28", "AC-2026-112", LAB, "Sim", (("Ln (recetor R1)", 48), ("Incomodidade noturna ΔLA (R1)", 2)))):
        for p, val in vals:
            lim = 55 if p.startswith("Ln") else 3
            an.append((dia, "Ruído ambiente", "Recetor R1 (habitação a sul, 250 m)", p, val, "dB(A)", None, lim,
                       "VLE legal" if ac == "Sim" else "Valor de referência interno", lab, ac, rel, "LEG-05"))
    for dia, rel, cov, mas in (("2023-03-21", "2023/03-EF", 27, 0.05), ("2026-03-18", "2026/03-EF", 22, 0.04)):
        an.append((dia, "Emissões — chaminé FP1", "Chaminé FP1 (estufa de cura)", "COVT", cov, "mg C/Nm³", None, 200, "VLE legal", LAB, "Sim", rel, "LEG-12"))
        an.append((dia, "Emissões — chaminé FP1", "Chaminé FP1 (estufa de cura)", "Caudal mássico COVT", mas, "kg C/h", None, 2, "Limiar legal de ação", LAB, "Sim", rel, "LEG-12"))
    arow = []
    for k, a in enumerate(sorted(an, key=lambda x: x[0]), start=1):
        arow.append(dict(ID_Analise=f"AN-{k:03d}", Data=d(a[0]), Matriz=a[1], Ponto_Amostragem=a[2], Parametro=a[3], Valor=a[4], Unidade=a[5],
                         Limite_Min=a[6], Limite_Max=a[7], Tipo_Limite=a[8], Laboratorio=a[9], Acreditado=a[10], N_Relatorio=a[11], ID_Legal=a[12]))
    acols = [
        col("ID_Analise", 9, desc="Identificador do resultado.", key="PK"),
        col("Data", 11, "date", desc="Data da colheita/medição."),
        col("Matriz", 24, dv="AN_Matriz", desc="Matriz ambiental."),
        col("Ponto_Amostragem", 30, desc="Ponto de amostragem / recetor."),
        col("Parametro", 26, desc="Parâmetro."),
        col("Valor", 10, "num", desc="Resultado."),
        col("Unidade", 12, desc="Unidade."),
        col("Limite_Min", 9, "num", desc="Limite inferior (ex.: pH).", req=False),
        col("Limite_Max", 9, "num", desc="Limite superior (VLE ou referência)."),
        col("Tipo_Limite", 20, dv="AN_Limite", desc="Origem do limite (confirmar valores na licença/regulamento aplicável)."),
        col("Laboratorio", 30, desc="Laboratório ou medição interna."),
        col("Acreditado", 8, dv="AN_SimNao", desc="Ensaio acreditado (ISO/IEC 17025)."),
        col("N_Relatorio", 12, desc="N.º do relatório/boletim."),
        col("ID_Legal", 8, desc="Requisito legal.", key="FK → tbl_legal (RG-SGA-04)"),
        col("Pct_do_Limite", 9, "pct", f='=IF(OR(@Valor@="",@Limite_Max@=""),"",@Valor@/@Limite_Max@)', desc="Resultado em % do limite superior."),
        col("Conformidade", 12, f='=IF(@Valor@="","",IF(OR(AND(@Limite_Min@<>"",@Valor@<@Limite_Min@),@Valor@>@Limite_Max@),"Não conforme","Conforme"))', desc="Automático."),
    ]
    b.table("Analises_Laboratoriais", "tbl_analises", acols, arow,
            "Resultados de monitorização por ensaio (efluente, águas pluviais, torre/Legionella, ruído, emissões) comparados com os limites (9.1.1, 9.1.2).",
            title="RESULTADOS DE MONITORIZAÇÃO — ENSAIOS E MEDIÇÕES vs. LIMITES",
            subtitle="Formato longo (1 linha = 1 parâmetro) · Limites indicativos a confirmar na autorização de descarga, RGR e DL 39/2018 · Medições internas não substituem ensaios acreditados",
            cf=[("Conformidade", {"Não conforme": "red", "Conforme": "green"}), ("Acreditado", {"Não": "yellow"})], row_height=18, extra_rows=60, freeze_col=2)
