import datetime as dt
from sgalib import *
import sga_extra as X
from dims import *

D = dt.date(2026, 3, 16)  # data da análise de contexto (Atividade 2.1)



# ------------------------------------------------------------------ contexto do SGI (vindo do RG-SGA-02 em 24/09/2026 — fonte única aqui)
# IDs R/O = IDs do registo corporativo RG-SGA-02 (tbRiscos / tbOportunidades)
SGI_PESTEL_IDS = {"PES-01": "R33; O5", "PES-02": "R25", "PES-03": "R14", "PES-04": "O5", "PES-06": "O3; O13", "PES-08": "R34", "PES-09": "R34", "PES-14": "R31"}
SGI_PESTEL_NOVOS = [
    ("PES-16", "Social", "Cultura de produtividade e passagem de turno", "Pressão por meta, passagem de turno e relato de quase-acidentes ainda fraco no chão de fábrica.",
     "Não aplicável", "Não aplicável", "Fadiga e handover elevam a rejeição do turno 2 (mais scrap) e escondem quase-acidentes.", "Risco", "Estável", "Curto (<1 ano)", 2, 2,
     "Rejeição por turno; registo de quase-acidentes", "Estudo de handover e registo de quase-acidentes sem culpa.", "", "", "Colaboradores", "Governação e dados", "S + G", "R9; R28"),
    ("PES-17", "Legal", "Recursos hídricos, químicos (REACH/CLP) e SST", "Títulos de utilização de recursos hídricos, condições de descarga, REACH/CLP e legislação de SST sobre agentes químicos.",
     "Poluição", "Organização → Ambiente", "Cria obrigações de autorização, controlo e reporte (RG-SGA-04 LEG-03, LEG-06, LEG-22).", "Risco", "Crescente", "Curto (<1 ano)", 3, 3,
     "Matriz legal (RG-SGA-04); RG-SGA-21", "Calendário de conformidade, verificação documental e gestão de químicos (PR-SGA-16).", "SWT-T03", "RO-10", "APA / CCDR Centro", "Legal / conformidade", "E + G", "R29; R30; R32"),
    ("PES-18", "Legal", "Requisitos de clientes (Cpk, rastreabilidade) e normas ISO 9001/14001/45001", "Clientes exigem capacidade de processo demonstrada, rastreabilidade ponta a ponta e sistemas de gestão certificados.",
     "Não aplicável", "Não aplicável", "Pressão por dados fiáveis e rastreabilidade, que também servem o SGA.", "Risco", "Crescente", "Médio (1-3 anos)", 3, 2,
     "Contratos; requisitos de clientes; auditorias", "Estratificar Cpk por máquina × molde e fechar a rastreabilidade.", "SWT-T04", "", "Clientes de cosmética (marcas UE)", "Governação e dados", "S + G", "R17; R18"),
    ("PES-19", "Económico", "Operação ibérica com clientes na UE (43% da receita fora de Portugal)", "Cadeia de abastecimento na Península Ibérica e clientes em vários países da UE com requisitos diferentes.",
     "Não aplicável", "Não aplicável", "Variação regulatória por país (ex.: RAP de embalagens) e pressão dos requisitos dos clientes.", "Risco", "Estável", "Médio (1-3 anos)", 2, 2,
     "Contratos; RG-SGA-20 tbl_requisitos_pais", "Critérios mínimos comuns e análise por país e cliente.", "", "", "Clientes de cosmética (marcas UE)", "Produto / embalagem", "E + G", "R33; O5"),
    ("PES-20", "Económico", "Sazonalidade da procura (pico set–nov) e concorrência por preço", "Procura de cosmética e higiene pessoal com pico previsível em setembro–novembro e margem pressionada (≈ € 0,13/un).",
     "Não aplicável", "Não aplicável", "O pico de velocidade (+15%) aumenta defeitos e scrap; permite planeamento antecipado.", "Risco e Oportunidade", "Estável", "Curto (<1 ano)", 2, 2,
     "Vendas; histórico de duas temporadas", "Planeamento de capacidade e stock de segurança antes do pico.", "SWT-O05", "", "Acionistas / Direção", "Materiais e circularidade", "S + G", "O14; R15"),
]
SGI_SWOT_IDS = {"SWT-F01": "O3", "SWT-W01": "O6; R28; R34", "SWT-W02": "R13; R6", "SWT-W03": "R20", "SWT-W04": "R30", "SWT-O01": "O5; R33", "SWT-O03": "O6",
                "SWT-T01": "R34", "SWT-T02": "R14; R25", "SWT-T03": "R31; R32; R29"}
SGI_SWOT_NOVOS = [
    ("SWT-F05", "Força", "Processos identificados e rastreáveis: 4 processos, 18 máquinas, LotId e ProductBatch consistentes.", "Dataset do projeto (lotes e ordens).",
     "Facilita ligar aspetos, riscos e KPI por processo.", "GER", "Governação e dados", "", "Oportunidade", "", "Não", "Matriz aspeto → KPI → ação e rastreabilidade ponta a ponta (O12).", "% de aspetos com KPI", "O12"),
    ("SWT-F06", "Força", "Causas-raiz conhecidas com evidência causal forte (IM-002 com MSA e DOE; SS-001 e M-SOP-007 respondem à intervenção).", "Estudos DOE/MSA; registo de riscos R1–R8.",
     "Ações de alta confiança reduzem refugo, refação e o desperdício de polímero e energia.", "INJ", "Materiais e circularidade", "", "Oportunidade", "", "Não", "Replicar a janela validada e a manutenção por condição (O1, O2).", "Short shot IM-002 (DPMO); lotes refeitos", "O1; O2"),
    ("SWT-F07", "Força", "Base de fornecedores diversificada: 7 de 8 fornecedores de resina com contrato anual ou plurianual.", "RG-SGA-11 tbl_fornecedores.",
     "Reduz a dependência do fornecedor spot e facilita exigir dados ambientais.", "CMP", "Cadeia de valor / fornecedores", "", "Oportunidade", "", "Não", "Consolidar contratos e scorecard (O8).", "% de lotes não aceites por fornecedor", "O8"),
    ("SWT-W05", "Fraqueza", "Dependência de dados de fornecedores: conteúdo reciclado, composição, carbono incorporado e reciclabilidade.", "Declarações incompletas (RG-SGA-21 tbl_declaracoes; RG-SGA-20).",
     "Risco de alegações ambientais incompletas e de lacunas PPWR/REACH.", "CMP", "Cadeia de valor / fornecedores", "PES-15", "Risco", "RO-05", "Não", "Questionário ESG e evidência documental (O7).", "% de fornecedores críticos avaliados", "O7; R33"),
    ("SWT-W06", "Fraqueza", "Parâmetros críticos não registados e capacidade de processo marginal (0% dos 190 grupos com Cpk ≥ 1,33).", "Estudo de capacidade 2026.",
     "Impede indicadores antecedentes; mais rejeição = mais polímero e energia desperdiçados.", "GER", "Governação e dados", "", "Risco", "", "Não", "Instrumentar parâmetros e priorizar Cpk por Pareto.", "% de ordens com parâmetros registados", "R19; R17"),
    ("SWT-W07", "Fraqueza", "Disponibilidade abaixo da meta (87,4%): paragens por operador, ar comprimido, matéria-prima e ativos específicos.", "OEE do dataset.",
     "Limita a capacidade sem nova máquina; paragens por ar comprimido ligam-se às fugas (energia).", "GER", "Energia", "", "Risco", "", "Não", "Programa integrado de paragens (O4).", "Disponibilidade da fábrica (%)", "R3; R22; R23; R15; O4"),
    ("SWT-O04", "Oportunidade", "Visão artificial, dados e rastreabilidade para prevenir perdas em vez de inspecionar.", "Business case de visão (RG-SGA-02 O13).",
     "Menos refugo e custo de avaliação.", "SER", "Governação e dados", "PES-06", "Oportunidade", "RO-01", "Não", "Business case de visão e painel de KRI (O13, O3).", "Custo de avaliação (€)", "O13; O3"),
    ("SWT-O05", "Oportunidade", "Sazonalidade previsível da procura (pico set–nov).", "Histórico de vendas de duas temporadas.",
     "Planear capacidade e materiais evita picos de scrap.", "GER", "Materiais e circularidade", "PES-20", "Oportunidade", "", "Não", "Planeamento de capacidade e materiais (O14).", "OTIF e rejeição em set–nov", "O14"),
    ("SWT-T04", "Ameaça", "Clientes exigem Cpk, rastreabilidade e zero defeito, com risco de reclamação e devolução (CPMU 4,76).", "Reclamações de clientes.",
     "Devoluções geram transporte e resíduos adicionais.", "GER", "Produto / embalagem", "PES-18", "Risco", "", "Não", "Indicadores antecedentes, Cpk por Pareto e rastreabilidade.", "CPMU e % de reclamações rastreáveis", "R16; R17; R18"),
]
SGI_TOWS_IDS = {"TOWS-01": "O3; O6", "TOWS-02": "R24; O10", "TOWS-04": "R30; R29"}
SGI_TOWS_NOVOS = [
    ("TOWS-06", "WO (Fraqueza+Oportunidade)", "SWT-W05; SWT-O01", "Programa de dados de fornecedores (qualidade e ambientais) para aumentar a rastreabilidade de materiais.", "", "2027-09-30", "Responsável de Compras", "% de fornecedores críticos avaliados (≥ 90%)", "O7; R33"),
    ("TOWS-07", "SO (Força+Oportunidade)", "SWT-F04; SWT-O01; PES-12", "Programa Design for Recycling para o portfólio: antecipar requisitos europeus e reduzir impactes de fim de vida.", "OBJ-07", "2028-06-30", "Responsável de R&D", "% das famílias prioritárias avaliadas (100%)", "O5; R33"),
    ("TOWS-08", "WT (Fraqueza+Ameaça)", "SWT-W06; SWT-T04", "Tratar primeiro as causas-raiz de maior evidência (IM-002, ISBM-003, SS-001, M-SOP-007, SUP-005): menos refação, scrap e reclamações.", "", "2027-03-31", "Gerente da Qualidade", "CPMU e taxa de rejeição", "R4; R1; R7; R2; R13"),
]
CINCO_FORCAS = [
    ("CF-01", "Poder negocial dos clientes", "Clientes de cosmética e higiene pessoal aumentam a exigência de Cpk, rastreabilidade, zero defeito, PPWR e dados ESG; carteira diversificada.", "Crescente",
     "Devoluções e auditorias; a diversificação reduz a dependência de um cliente.", "Risco", "R16; R17; R18", "Inquérito de satisfação e reunião semestral (RG-SGA-02 Monitoramento: Clientes)"),
    ("CF-02", "Poder negocial dos fornecedores", "Resinas commodity concentradas em poucos petroquímicos; 1 fornecedor spot com mau desempenho; PCR/rPET com pouca oferta.", "Estável",
     "Risco de custo, disponibilidade e qualidade; pouco poder de troca no reciclado.", "Risco", "R13; R14; R25", "Reunião mensal e scorecard (RG-SGA-11; RG-SGA-02 Monitoramento: Fornecedores)"),
    ("CF-03", "Ameaça de novos entrantes", "Barreira baixa em frascos simples e alta em decoração (serigrafia, hot foil), qualidade e rastreabilidade.", "Estável",
     "Pressão de preço nos produtos padrão; a decoração protege o portfólio.", "Risco", "", "Relatório trimestral de mercado"),
    ("CF-04", "Ameaça de produtos substitutos", "Vidro, alumínio, recargas e embalagens monomaterial/recicladas substituem parte dos frascos.", "Crescente",
     "Pressão por design circular e oportunidade de conteúdo reciclado.", "Oportunidade", "O5", "Relatório trimestral de mercado"),
    ("CF-05", "Rivalidade entre concorrentes", "Concorrentes disputam preço; margem pressionada (preço unitário médio ≈ € 0,13).", "Crescente",
     "Reduzir perdas e refação para preservar margem (menos desperdício = menos impacte).", "Oportunidade", "O11; O4", "Relatório trimestral de mercado"),
]


def build(out):
    b = Book("RG-SGA-01", "Contexto da Organização — PESTEL, SWOT, Partes Interessadas, 5 Forças e TOWS (SGA e SGI)",
             activities="Base da Atividade 3.1 (recuperação da SWOT da Atividade 2.1). Contexto 4.1/4.2.",
             clauses="4.1 (questões externas/internas e condições ambientais: clima, poluição, recursos naturais, biodiversidade, saúde dos ecossistemas); 4.2; 6.1.4",
             purpose="Registar as questões externas (PESTEL) e internas/externas (SWOT) relevantes para o SGA, incluindo a dupla perspetiva exigida pela ISO 14001:2026 (condições ambientais afetadas pela organização e que a afetam). Cada fraqueza, oportunidade e ameaça é convertida num risco ou oportunidade do registo RG-SGA-02.",
             links=[("RG-SGA-02 Riscos e Oportunidades", "Coluna ID_RO liga ao risco ambiental (RO-xx); IDs_Risco_SGI liga aos riscos/oportunidades do registo corporativo (R-nn / O-nn)."),
                    ("Fonte única do contexto", "Desde 24/09/2026 o contexto do sistema integrado (qualidade, SST e ambiente) regista-se só aqui; o RG-SGA-02 deixou de ter PESTEL/SWOT/partes interessadas/5 forças/TOWS próprios."),
                    ("RG-SGA-05 Objetivos", "A Matriz TOWS aponta os objetivos ambientais (OBJ-xx) derivados do cruzamento estratégico.")])
    b.add_list("Dimensao", ["Político", "Económico", "Social", "Tecnológico", "Ambiental", "Legal"])
    b.add_list("CondicaoAmbiental", ["Clima", "Poluição", "Recursos naturais", "Biodiversidade", "Saúde dos ecossistemas", "Não aplicável"])
    b.add_list("Direcao", ["Organização → Ambiente", "Ambiente → Organização", "Bidirecional", "Não aplicável"])
    b.add_list("Classificacao", ["Risco", "Oportunidade", "Risco e Oportunidade"])
    b.add_list("Tendencia", ["Crescente", "Estável", "Decrescente"])
    b.add_list("Horizonte", ["Curto (<1 ano)", "Médio (1-3 anos)", "Longo (>3 anos)"])
    b.add_list("Escala13", [1, 2, 3])
    b.add_list("Quadrante", ["Força", "Fraqueza", "Oportunidade", "Ameaça"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Tema", TEMAS)
    b.add_list("ESG", ESG)
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Cruzamento", ["SO (Força+Oportunidade)", "ST (Força+Ameaça)", "WO (Fraqueza+Oportunidade)", "WT (Fraqueza+Ameaça)"])

    pestel = [
        ("PES-01", "Político", "Pacto Ecológico Europeu, Clean Industrial Deal e PNEC 2030", "Metas europeias e nacionais de descarbonização e economia circular aumentam a exigência sobre emissões e eficiência da indústria.", "Clima", "Bidirecional", "Exige inventário de GEE e metas de redução no SGA.", "Risco e Oportunidade", "Crescente", "Médio (1-3 anos)", 3, 2, "Comissão Europeia; APA; associação setorial (APIP)", "Inventário GEE âmbitos 1-2 e plano de eficiência energética.", "SWT-F02", "RO-09", "Governo / reguladores", "Clima / GEE", "E + G"),
        ("PES-02", "Económico", "Volatilidade do preço da eletricidade", "Injeção e sopro são eletrointensivos (≈ 7 GWh/ano); variações de preço afetam margem e retorno de projetos de eficiência.", "Não aplicável", "Não aplicável", "Aumenta o retorno financeiro das ações de eficiência energética.", "Risco", "Estável", "Curto (<1 ano)", 3, 3, "Faturas; OMIE; Financeiro", "Submedição, caça a fugas de ar comprimido e avaliação de PPA/fotovoltaico.", "SWT-W01", "RO-02", "Acionistas / Gerência", "Energia", "E + G"),
        ("PES-03", "Económico", "Preço e disponibilidade de PCR / rPET", "Prémio de preço do reciclado face ao virgem e oferta limitada de PCR de qualidade alimentar.", "Recursos naturais", "Ambiente → Organização", "Condiciona metas de conteúdo reciclado e pode aumentar o scrap.", "Risco", "Crescente", "Médio (1-3 anos)", 3, 2, "Compras; fornecedores SUP-004/SUP-002; índices de mercado", "Qualificar múltiplas fontes e ensaios DOE de materiais antes de mudar de fornecedor.", "SWT-T02", "RO-05", "Fornecedores", "Materiais e circularidade", "E + G"),
        ("PES-04", "Social", "Clientes exigem embalagem circular e dados ambientais", "Marcas de cosmética, alimentar e farmacêutica pedem conteúdo reciclado, reciclabilidade, pegada de carbono e respostas a questionários ESG (CSRD/ESRS da cadeia de valor).", "Recursos naturais", "Organização → Ambiente", "Transforma dados ambientais em requisito comercial.", "Oportunidade", "Crescente", "Curto (<1 ano)", 3, 3, "Pedidos de clientes; auditorias de clientes; questionários", "Programa Design for Recycling e ficha ambiental por família de produto.", "SWT-O01", "RO-03", "Clientes europeus", "Produto / embalagem", "E + S + G"),
        ("PES-05", "Social", "Sensibilidade da comunidade a ruído e tráfego", "Zona industrial de Marinha Grande com habitações a ~250 m; compressores e camiões noturnos são fonte potencial de reclamações.", "Poluição", "Organização → Ambiente", "Exige avaliação acústica e canal de reclamações.", "Risco", "Estável", "Médio (1-3 anos)", 2, 2, "Registo de reclamações; Câmara Municipal", "Avaliação de ruído no recetor e janelas de expedição.", "SWT-W04", "RO-10", "Vizinhança / comunidade local", "Ruído", "E + S"),
        ("PES-06", "Tecnológico", "Monitorização digital, IoT e analytics", "Sensores de energia/caudal de baixo custo, integração no BI e IA permitem gestão ambiental em tempo quase real (reforçado pela ISO 14001:2026).", "Não aplicável", "Não aplicável", "Permite medir desempenho e eficácia do SGA (9.1.1).", "Oportunidade", "Crescente", "Curto (<1 ano)", 3, 2, "Fornecedores de automação; Data/TI", "Integrar dados ambientais no modelo de dados industrial.", "SWT-F01", "RO-01", "Acionistas / Gerência", "Governação e dados", "E + G"),
        ("PES-07", "Tecnológico", "Design for recycling, monomaterial e redução de peso", "Tecnologias de lightweighting e embalagens monomaterial PP/PE facilitam a reciclagem e reduzem polímero por unidade.", "Recursos naturais", "Organização → Ambiente", "Reduz impacte a montante e no fim de vida.", "Oportunidade", "Crescente", "Médio (1-3 anos)", 2, 3, "R&D; RecyClass; clientes", "Revisão de design das famílias prioritárias.", "SWT-O01", "RO-03", "Clientes europeus", "Produto / embalagem", "E + G"),
        ("PES-08", "Ambiental", "Ondas de calor mais frequentes", "Verões mais quentes aumentam a carga térmica dos moldes, o consumo do chiller e a evaporação da torre de arrefecimento.", "Clima", "Ambiente → Organização", "Aumenta consumo de energia e água no verão; risco para qualidade e continuidade.", "Risco", "Crescente", "Médio (1-3 anos)", 3, 2, "IPMA; dados de consumo mensais", "Normalizar indicadores pela temperatura e reforçar capacidade de arrefecimento.", "SWT-T01", "RO-04", "Acionistas / Gerência", "Clima / GEE", "E"),
        ("PES-09", "Ambiental", "Seca e escassez hídrica na região Centro", "Períodos de seca prolongada podem levar a restrições de uso de água de rede pela entidade gestora.", "Recursos naturais", "Bidirecional", "Exige eficiência hídrica e plano de contingência para água de arrefecimento.", "Risco", "Crescente", "Longo (>3 anos)", 2, 2, "APA (monitorização de seca); entidade gestora de água", "Circuito fechado de arrefecimento e reservatório de reserva.", "SWT-T01", "RO-04", "Vizinhança / comunidade local", "Água e efluentes", "E + S"),
        ("PES-10", "Ambiental", "Risco de incêndio rural na envolvente florestal", "Proximidade ao Pinhal de Leiria (Mata Nacional afetada pelo grande incêndio de 2017); um incêndio na fábrica pode atingir a floresta e vice-versa.", "Biodiversidade", "Bidirecional", "Cenário de emergência com impacte em ecossistemas e continuidade.", "Risco", "Crescente", "Médio (1-3 anos)", 2, 3, "ANEPC; ICNF; Plano de Emergência Interno", "Faixa de gestão de combustível, retenção de águas de combate e simulacros.", "SWT-T01", "RO-08", "Vizinhança / comunidade local", "Biodiversidade e ecossistemas", "E + S"),
        ("PES-11", "Ambiental", "Poluição por microplásticos (perdas de granulado)", "Granulado perdido na descarga de silos e big bags pode chegar à rede pluvial, ao rio Lis e à costa, afetando ecossistemas aquáticos.", "Saúde dos ecossistemas", "Organização → Ambiente", "Novo aspeto ambiental significativo e requisito legal emergente.", "Risco", "Crescente", "Curto (<1 ano)", 2, 3, "ONG; Operation Clean Sweep; regulamento UE sobre granulados", "Programa de contenção de granulado (OCS) e inspeção de sarjetas.", "SWT-W04", "RO-07", "Vizinhança / comunidade local", "Perdas de granulado (microplásticos)", "E + S + G"),
        ("PES-12", "Legal", "PPWR — Regulamento (UE) 2025/40 aplicável desde 12/08/2026", "Obrigações do fabricante de embalagens: documentação técnica, declaração UE de conformidade, limites de substâncias preocupantes, metas de conteúdo reciclado e reciclabilidade.", "Recursos naturais", "Organização → Ambiente", "Obrigação de conformidade nova com impacto comercial direto.", "Risco e Oportunidade", "Crescente", "Curto (<1 ano)", 3, 3, "EUR-Lex; APA; clientes", "Dossier técnico por família e plano de conformidade PPWR.", "SWT-O01", "RO-06", "Clientes europeus", "Legal / conformidade", "E + G"),
        ("PES-13", "Legal", "Regulamento da UE sobre prevenção de perdas de granulados de plástico", "Adotado em 2025: obrigações de avaliação de risco, plano de gestão, contenção e (para grandes empresas) certificação por terceiros — confirmar n.º e datas de aplicação no EUR-Lex.", "Saúde dos ecossistemas", "Organização → Ambiente", "Antecipar requisitos antes da data de aplicação.", "Risco", "Crescente", "Médio (1-3 anos)", 3, 2, "EUR-Lex; Plastics Europe", "Autoavaliação OCS e plano de contenção por ponto crítico.", "SWT-W04", "RO-07", "Governo / reguladores", "Perdas de granulado (microplásticos)", "E + G"),
        ("PES-14", "Legal", "Fiscalização de resíduos (RGGR, e-GAR, MIRR)", "Fiscalização da IGAMAOT/APA sobre classificação LER, e-GAR e reporte anual MIRR.", "Poluição", "Organização → Ambiente", "Exige rastreabilidade completa dos resíduos.", "Risco", "Estável", "Curto (<1 ano)", 2, 2, "APA/SILiAmb; IGAMAOT", "Pesagem por código LER e verificação mensal das e-GAR.", "SWT-W04", "RO-10", "Governo / reguladores", "Resíduos", "E + G"),
        ("PES-15", "Legal", "Alegações ambientais (Diretiva (UE) 2024/825)", "Proibição de alegações ambientais genéricas não comprovadas; clientes pedem prova de conteúdo reciclado e reciclabilidade.", "Não aplicável", "Não aplicável", "Exige evidência verificável para qualquer declaração ambiental de produto.", "Risco", "Crescente", "Curto (<1 ano)", 2, 2, "EUR-Lex; clientes", "Só comunicar alegações com certificação (EuCertPlast/RecyClass).", "SWT-W02", "RO-05", "Clientes europeus", "Produto / embalagem", "G"),
    ]
    pcols = [
        col("ID_PESTEL", 11, desc="Identificador único do fator PESTEL.", key="PK", dom="PES-nn"),
        col("Dimensao", 13, dv="Dimensao", desc="Dimensão PESTEL."),
        col("Fator_Externo", 34, desc="Nome curto do fator externo."),
        col("Descricao", 55, desc="Descrição do fator e do seu estado atual."),
        col("Condicao_Ambiental_ISO2026", 20, dv="CondicaoAmbiental", desc="Condição ambiental da cláusula 4.1 da ISO 14001:2026 a que o fator se refere."),
        col("Direcao_Efeito", 20, dv="Direcao", desc="Dupla perspetiva 2026: a organização afeta o ambiente, o ambiente afeta a organização, ou ambos."),
        col("Efeito_no_SGA", 40, desc="Como o fator afeta os resultados pretendidos do SGA."),
        col("Classificacao", 15, dv="Classificacao", desc="Se o fator gera risco, oportunidade ou ambos."),
        col("Tendencia", 12, dv="Tendencia", desc="Tendência observada."),
        col("Horizonte", 15, dv="Horizonte", desc="Horizonte temporal do efeito."),
        col("Probabilidade_1a3", 11, "int", dv="Escala13", desc="Probabilidade de afetar o SGA (1 baixa – 3 alta)."),
        col("Impacto_1a3", 10, "int", dv="Escala13", desc="Impacto no SGA (1 baixo – 3 alto)."),
        col("Score", 8, "int", f="=@Probabilidade_1a3@*@Impacto_1a3@", desc="Probabilidade × Impacto (1-9)."),
        col("Prioridade", 10, f='=IF(@Score@>=6,"Alta",IF(@Score@>=3,"Média","Baixa"))', desc="Alta ≥6; Média 3-5; Baixa ≤2."),
        col("Fonte_Monitorizacao", 30, desc="Fonte de informação usada para acompanhar o fator."),
        col("Resposta_Estrategica", 42, desc="Resposta estratégica prevista."),
        col("ID_SWOT", 10, desc="Item SWOT relacionado.", key="FK → tbl_swot"),
        col("ID_RO", 9, desc="Risco/oportunidade gerado no RG-SGA-02.", key="FK → RG-SGA-02"),
        col("Parte_Interessada", 24, desc="Parte interessada mais relacionada (4.2)."),
        col("Tema", 22, dv="Tema", desc="Tema ambiental."),
        col("ESG", 9, dv="ESG", desc="Pilar ESG."),
        col("Dono", 28, dv="Funcao", desc="Função responsável por monitorizar o fator."),
        col("Data_Avaliacao", 12, "date", desc="Data da análise."),
        col("Proxima_Revisao", 12, "date", f="=EDATE(@Data_Avaliacao@,12)", desc="Revisão anual (antes da Revisão pela Gestão)."),
        col("Ambito", 12, desc="SGA (ambiental) ou SGI (qualidade/SST, vindo do RG-SGA-02)."),
        col("IDs_Risco_SGI", 16, desc="Riscos/oportunidades do registo corporativo RG-SGA-02 (R-nn / O-nn).", key="FK → RG-SGA-02 tbRiscos/tbOportunidades", req=False),
    ]
    owners = {"Político": "Diretor Geral (Gestão de Topo)", "Económico": "Diretor Financeiro", "Social": "Gestor do SGA / EHS (Responsável Ambiental)",
              "Tecnológico": "Diretor Industrial", "Ambiental": "Gestor do SGA / EHS (Responsável Ambiental)", "Legal": "Gestor do SGA / EHS (Responsável Ambiental)"}
    names = [c["name"] for c in pcols if not c["f"]]
    prow = []
    for p in pestel + [x[:-1] for x in SGI_PESTEL_NOVOS]:
        d = dict(zip([n for n in names if n not in ("Dono", "Data_Avaliacao", "Ambito", "IDs_Risco_SGI")], p))
        d["Dono"] = owners[d["Dimensao"]]
        d["Data_Avaliacao"] = D
        novo = next((x for x in SGI_PESTEL_NOVOS if x[0] == d["ID_PESTEL"]), None)
        d["Ambito"] = "SGI" if novo else "SGA"
        d["IDs_Risco_SGI"] = novo[-1] if novo else SGI_PESTEL_IDS.get(d["ID_PESTEL"])
        for k in ("ID_SWOT", "ID_RO"):
            d[k] = d[k] or None
        prow.append(d)
    b.table("PESTEL", "tbl_pestel", pcols, prow, "Registo das questões externas (PESTEL) com a dupla perspetiva ambiental da ISO 14001:2026.",
            cf=[("Prioridade", {"Alta": "red", "Média": "yellow", "Baixa": "green"}),
                ("Classificacao", {"Risco e": "purple", "Oportunidade": "blue", "Risco": "orange"})], row_height=60)

    swot = [
        ("SWT-F01", "Força", "Cultura de dados industriais: OEE, SPC, AQL e rastreabilidade lote → ordem em 18 meses de dados (22 máquinas, 3 turnos) já integrados em Power BI.", "Dataset do projeto (datasets/silver); dashboards de produção e qualidade.", "Permite construir rapidamente indicadores ambientais por máquina, turno e lote.", "GER", "Governação e dados", "PES-06", "Oportunidade", "RO-01", "Sim", "Integrar consumos de energia, água e resíduos no modelo de dados industrial.", "N.º de KPIs ambientais com dados automáticos"),
        ("SWT-F02", "Força", "Processo 100% elétrico: sem caldeiras nem combustão in situ; empilhadores elétricos.", "Inventário de equipamentos; faturas (sem gás natural).", "Emissões diretas (âmbito 1) muito baixas; descarbonização depende da eletricidade.", "GER", "Clima / GEE", "PES-01", "Oportunidade", "RO-09", "Não", "Contratar eletricidade com garantia de origem renovável / fotovoltaico.", "% energia renovável"),
        ("SWT-F03", "Força", "Moinhos junto às máquinas permitem reintegrar rebarbas e jitos (regrind) no próprio processo.", "Registos de moagem; boas práticas de produção.", "Reduz consumo de polímero virgem e resíduos plásticos enviados para fora.", "MOA", "Materiais e circularidade", "", "Oportunidade", "RO-11", "Não", "Segregar scrap limpo por polímero/cor para aumentar a taxa de reintegração.", "% scrap reintegrado"),
        ("SWT-F04", "Força", "Experiência com resinas PCR (HDPE-PCR, rPET) e entrada em mercados alimentar e farmacêutico (2026).", "Portefólio FR-002-HDPE-PCR, rPET; clientes CUST-015 a CUST-018.", "Base técnica para responder às metas de conteúdo reciclado.", "RD", "Materiais e circularidade", "PES-04", "Oportunidade", "RO-03", "Não", "Oferecer gama com conteúdo reciclado certificado.", "% vendas com PCR"),
        ("SWT-W01", "Fraqueza", "Não existe submedição de energia nem de água por processo ou máquina: os consumos só são conhecidos pela fatura global mensal.", "Fatura única de eletricidade e água; ausência de contadores parciais.", "Impede baselines por processo, metas robustas e prova de eficácia das ações (9.1.1).", "UTL", "Energia", "PES-02", "Risco", "RO-02", "Sim", "Instalar analisadores de energia e contadores de água nos principais consumidores.", "% do consumo com submedição"),
        ("SWT-W02", "Fraqueza", "Dependência do fornecedor spot SUP-005 (PP/PVC) com lotes fora de especificação.", "Registos de inspeção de receção e reclamações a fornecedores.", "Mais scrap, retrabalho e alegações ambientais pouco fiáveis.", "CMP", "Cadeia de valor / fornecedores", "PES-15", "Risco", "RO-05", "Não", "Avaliação ambiental e de qualidade de fornecedores; migrar volumes para contratos.", "% compras a fornecedores avaliados"),
        ("SWT-W03", "Fraqueza", "Taxa de rejeição ≈ 2,4% acima da meta de 2,0% e 31% de CAPA não eficazes.", "fact_production / fact_capa do projeto.", "Cada peça rejeitada desperdiça polímero, energia e água.", "GER", "Materiais e circularidade", "", "Risco", "RO-11", "Não", "Ligar a redução de scrap ao objetivo ambiental OBJ-02.", "kg scrap / 1.000 un"),
        ("SWT-W04", "Fraqueza", "Gestão informal da contenção de químicos, kits de derrame e granulado (sem registo de utilização nem stock mínimo).", "Rondas ambientais; NC-SGA-26-03.", "Risco de derrame não contido, perdas de granulado e não conformidade legal.", "ARQ", "Produtos químicos", "PES-11", "Risco", "RO-07", "Não", "Formalizar rondas, stock mínimo de kits e registo de incidentes.", "% rondas conformes"),
        ("SWT-O01", "Oportunidade", "PPWR e procura de embalagens recicláveis com conteúdo reciclado por clientes europeus.", "Reg. (UE) 2025/40; pedidos de clientes 2026.", "Diferenciação comercial se a Plasticom demonstrar conformidade e desempenho.", "RD", "Produto / embalagem", "PES-12", "Oportunidade", "RO-03", "Sim", "Programa Design for Recycling com dossier técnico por família.", "% famílias avaliadas"),
        ("SWT-O02", "Oportunidade", "Autoconsumo fotovoltaico na cobertura (≈ 9.000 m² disponíveis) e contratos PPA renováveis.", "Estudo preliminar; área de cobertura.", "Reduz emissões do âmbito 2 e custo energético.", "UTL", "Energia", "PES-01", "Oportunidade", "RO-09", "Não", "Estudo de viabilidade de UPAC.", "MWh autoproduzidos"),
        ("SWT-O03", "Oportunidade", "Financiamento público para eficiência energética e economia circular (Portugal 2030, Fundo Ambiental).", "Avisos de candidatura abertos.", "Reduz o payback dos investimentos ambientais.", "ADM", "Governação e dados", "PES-01", "Oportunidade", "RO-09", "Não", "Candidatar submedição + fotovoltaico.", "€ financiados"),
        ("SWT-T01", "Ameaça", "Ondas de calor e escassez hídrica (alterações climáticas) afetam o arrefecimento de moldes, a água técnica e a continuidade.", "Dados de consumo de verão; alertas de seca.", "Mais consumo de energia e água no verão; risco de paragem e de defeitos.", "UTL", "Clima / GEE", "PES-08", "Risco", "RO-04", "Sim", "Plano de adaptação climática: arrefecimento eficiente e reserva de água.", "m³/1.000 un no verão"),
        ("SWT-T02", "Ameaça", "Volatilidade de preço e qualidade do PCR/rPET.", "Mercado; reclamações a fornecedores.", "Pode limitar metas de conteúdo reciclado e aumentar scrap.", "CMP", "Materiais e circularidade", "PES-03", "Risco", "RO-05", "Não", "Qualificar múltiplas fontes certificadas.", "N.º fornecedores PCR qualificados"),
        ("SWT-T03", "Ameaça", "Aumento da exigência regulatória (PPWR, granulados, resíduos) com risco de coimas e perda de clientes.", "Matriz legal RG-SGA-04.", "Obrigações novas exigem recursos e evidências.", "GER", "Legal / conformidade", "PES-12", "Risco", "RO-06", "Não", "Calendário legal e revisão trimestral da conformidade.", "% obrigações conformes"),
    ]
    scols = [
        col("ID_SWOT", 10, desc="Identificador único do item SWOT.", key="PK", dom="SWT-Xnn (F força, W fraqueza, O oportunidade, T ameaça)"),
        col("Quadrante", 13, dv="Quadrante", desc="Quadrante SWOT."),
        col("Natureza", 10, f='=IF(OR(@Quadrante@="Força",@Quadrante@="Fraqueza"),"Interno","Externo")', desc="Interno (Força/Fraqueza) ou Externo (Oportunidade/Ameaça)."),
        col("Descricao", 55, desc="Descrição aplicada à Plasticom."),
        col("Evidencia", 36, desc="Dado ou fonte que sustenta o item."),
        col("Implicacao_SGA", 40, desc="Implicação para o sistema de gestão ambiental."),
        col("Processo", 10, dv="Processo", desc="Processo mais afetado.", key="FK → dim processo"),
        col("Tema", 22, dv="Tema", desc="Tema ambiental."),
        col("ID_PESTEL", 10, desc="Fator PESTEL de origem (itens externos).", key="FK → tbl_pestel", req=False),
        col("Converte_em", 13, dv="Classificacao", desc="Tratamento no registo de riscos: risco ou oportunidade."),
        col("ID_RO", 8, desc="ID no registo RG-SGA-02.", key="FK → RG-SGA-02"),
        col("Selecionado_Atv_3_1", 12, dv="SimNao", desc="Item escolhido para a Atividade 3.1 (1 por quadrante)."),
        col("Estrategia", 42, desc="Estratégia/resposta."),
        col("Indicador", 26, desc="Indicador de acompanhamento."),
        col("Data_Avaliacao", 12, "date", desc="Data da análise SWOT."),
        col("Chave_Vista", 14, f='=@Quadrante@&"|"&COUNTIF(INDEX(#Quadrante#,1):@Quadrante@,@Quadrante@)', desc="Chave técnica (quadrante|ordem) usada pela Vista_SWOT."),
        col("Ambito", 9, desc="SGA ou SGI (qualidade/SST, vindo do RG-SGA-02)."),
        col("IDs_Risco_SGI", 16, desc="Riscos/oportunidades do RG-SGA-02 (R-nn / O-nn).", key="FK → RG-SGA-02 tbRiscos/tbOportunidades", req=False),
    ]
    snames = [c["name"] for c in scols if not c["f"]]
    srows = []
    ordem = {"Força": 0, "Fraqueza": 1, "Oportunidade": 2, "Ameaça": 3}
    for s in sorted(swot + [x[:-1] for x in SGI_SWOT_NOVOS], key=lambda x: (ordem[x[1]], x[0])):
        d = dict(zip([n for n in snames if n not in ("Data_Avaliacao", "Ambito", "IDs_Risco_SGI")], s))
        d["Data_Avaliacao"] = D
        novo = next((x for x in SGI_SWOT_NOVOS if x[0] == d["ID_SWOT"]), None)
        d["Ambito"] = "SGI" if novo else "SGA"
        d["IDs_Risco_SGI"] = novo[-1] if novo else SGI_SWOT_IDS.get(d["ID_SWOT"])
        for k in ("ID_PESTEL", "ID_RO"):
            d[k] = d[k] or None
        srows.append(d)
    b.table("SWOT", "tbl_swot", scols, srows, "Registo SWOT (formato longo: um item por linha). Coluna Selecionado_Atv_3_1 marca os 4 itens da Atividade 3.1.",
            cf=[("Quadrante", {"Força": "green", "Fraqueza": "orange", "Oportunidade": "blue", "Ameaça": "red"}),
                ("Selecionado_Atv_3_1", {"Sim": "purple"})], row_height=58)

    tows = [
        ("TOWS-01", "SO (Força+Oportunidade)", "SWT-F01; SWT-O01; PES-06", "Usar a infraestrutura de dados existente para criar o painel ambiental e o dossier ambiental por família de produto.", "OBJ-04", "2026-12-31", "Gestor do SGA / EHS (Responsável Ambiental)", "% KPIs ambientais com dados automáticos"),
        ("TOWS-02", "ST (Força+Ameaça)", "SWT-F03; SWT-T02", "Aumentar a reintegração de scrap limpo para reduzir a dependência de PCR/virgem e o custo de material.", "OBJ-02", "2027-06-30", "Gerente de Produção", "% scrap reintegrado"),
        ("TOWS-03", "WO (Fraqueza+Oportunidade)", "SWT-W01; SWT-O03", "Candidatar a submedição de energia e água a financiamento e usá-la como base das metas de eficiência.", "OBJ-01", "2026-12-31", "Gerente de Manutenção", "% consumo submedido"),
        ("TOWS-04", "WT (Fraqueza+Ameaça)", "SWT-W04; SWT-T03; PES-13", "Programa de contenção de químicos e granulado (bacias, kits, OCS) antes da aplicação do regulamento de granulados.", "OBJ-06", "2027-03-31", "Gestor do SGA / EHS (Responsável Ambiental)", "N.º ocorrências de perda de granulado"),
        ("TOWS-05", "WT (Fraqueza+Ameaça)", "SWT-W01; SWT-T01", "Plano de adaptação climática: medir água e energia do arrefecimento e dimensionar reserva de água.", "OBJ-05", "2027-12-31", "Diretor Industrial", "m³/1.000 un"),
    ]
    tcols = [
        col("ID_TOWS", 10, desc="Identificador da estratégia cruzada.", key="PK"),
        col("Cruzamento", 24, dv="Cruzamento", desc="Tipo de cruzamento TOWS."),
        col("IDs_Origem", 26, desc="IDs SWOT/PESTEL combinados (separados por ';')."),
        col("Estrategia", 60, desc="Estratégia resultante."),
        col("ID_Objetivo", 10, desc="Objetivo ambiental derivado.", key="FK → RG-SGA-05"),
        col("Prazo", 12, "date", desc="Prazo."),
        col("Dono", 30, dv="Funcao", desc="Responsável."),
        col("KPI", 30, desc="Indicador de sucesso."),
        col("IDs_Risco_SGI", 16, desc="Riscos/oportunidades do RG-SGA-02 (R-nn / O-nn).", key="FK → RG-SGA-02 tbRiscos/tbOportunidades", req=False),
    ]
    tn = [c["name"] for c in tcols]
    trows = [dict(zip(tn, t)) for t in tows + SGI_TOWS_NOVOS]
    for t in trows:
        t["Prazo"] = dt.date.fromisoformat(t["Prazo"])
        t["IDs_Risco_SGI"] = t.get("IDs_Risco_SGI") or SGI_TOWS_IDS.get(t["ID_TOWS"])
        t["ID_Objetivo"] = t["ID_Objetivo"] or None
    b.table("Matriz_TOWS", "tbl_tows", tcols, trows, "Cruzamento estratégico SWOT (TOWS) que liga o contexto aos objetivos ambientais e aos riscos do SGI.", row_height=48)

    # 5 forças de Porter (antes no RG-SGA-02 Contexto §5)
    fcols = [col("ID_Forca", 8, key="PK"), col("Forca_Competitiva", 28), col("Cenario_Evidencias", 60), col("Tendencia", 11, dv="Tendencia"),
             col("Impacto_Organizacao", 46), col("Classificacao", 14, dv="Classificacao"),
             col("IDs_Risco_SGI", 16, desc="Riscos/oportunidades do RG-SGA-02 (R-nn / O-nn).", key="FK → RG-SGA-02 tbRiscos/tbOportunidades", req=False),
             col("Como_Monitorizar", 44), col("Data_Avaliacao", 12, "date")]
    frows = [dict(zip([c["name"] for c in fcols], list(x) + [D])) for x in CINCO_FORCAS]
    for x in frows:
        x["IDs_Risco_SGI"] = x["IDs_Risco_SGI"] or None
    b.table("Cinco_Forcas", "tbl_cinco_forcas", fcols, frows, "Cinco forças competitivas (Porter) do sistema integrado, com ligação aos riscos/oportunidades do RG-SGA-02.",
            title="CINCO FORÇAS COMPETITIVAS (PORTER)", subtitle="Contexto externo do SGI · Vindo do RG-SGA-02 (24/09/2026) — registar só aqui",
            cf=[("Classificacao", {"Oportunidade": "blue", "Risco": "orange"})], row_height=48)

    # Vista SWOT (quadro 2x2 calculado a partir da tabela)
    ws = b.sheet("Vista_SWOT", "Quadro SWOT 2×2 para impressão, calculado por fórmulas a partir de tbl_swot (não editar aqui).")
    ws["A1"] = "ANÁLISE SWOT — PLASTICOM (vista calculada)"
    ws["A1"].font = F_TITLE
    ws["A2"] = "Itens marcados com ► foram selecionados para a Atividade 3.1. Editar a folha SWOT; esta vista atualiza sozinha."
    ws["A2"].font = F_SUB
    ws.column_dimensions["A"].width = 70
    ws.column_dimensions["B"].width = 70
    q = b.ref("tbl_swot", "Quadrante")
    ids = b.ref("tbl_swot", "ID_SWOT")
    ds = b.ref("tbl_swot", "Descricao")
    sel = b.ref("tbl_swot", "Selecionado_Atv_3_1")
    layout = [(4, 1, "Força", "FORÇAS (internas, positivas)", "green"), (4, 2, "Fraqueza", "FRAQUEZAS (internas, negativas)", "orange"),
              (13, 1, "Oportunidade", "OPORTUNIDADES (externas, positivas)", "blue"), (13, 2, "Ameaça", "AMEAÇAS (externas, negativas)", "red")]
    for r0, c0, quad, label, color in layout:
        h = ws.cell(row=r0, column=c0, value=label)
        h.font = Font(name=FONT, bold=True, size=11, color=CF_COLORS[color][1])
        h.fill = PatternFill("solid", fgColor=CF_COLORS[color][0])
        h.border = BORDER
        for k in range(1, 8):
            key = b.ref("tbl_swot", "Chave_Vista")
            idx = f'MATCH("{quad}|{k}",{key},0)'
            f = (f'=IFERROR(IF(INDEX({sel},{idx})="Sim","► ","• ")&INDEX({ids},{idx})&" — "&INDEX({ds},{idx}),"")')
            c = ws.cell(row=r0 + k, column=c0, value=f)
            c.font, c.alignment, c.border = F_BASE, WRAP_TOP, BORDER
            ws.row_dimensions[r0 + k].height = 42
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    X.extra_01(b)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
