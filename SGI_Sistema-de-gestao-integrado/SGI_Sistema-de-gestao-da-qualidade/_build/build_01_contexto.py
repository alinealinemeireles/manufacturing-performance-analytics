"""RG-SGQ-01 — Contexto da organização (PESTEL, SWOT, TOWS, 5 forças), partes interessadas e âmbito do SGQ
(ISO 9001:2026 4.1, 4.2, 4.3).

Estrutura NORMALIZADA com o RG-SGA-01 (SGA-01_Contexto_SWOT_PESTEL.xlsx), que é o padrão do SGI: as folhas PESTEL,
SWOT, Matriz_TOWS, Cinco_Forcas, Vista_SWOT e Partes_Interessadas têm as MESMAS tabelas (tbl_pestel, tbl_swot, tbl_tows,
tbl_cinco_forcas, tbl_partes_interessadas) com as MESMAS colunas pela MESMA ordem. Assim o contexto do SGQ e do SGA
junta-se num único modelo para a gestão de topo (pd.concat / Power BI Append) pela coluna Ambito (SGA / SGI / SGQ).
Só mudam as colunas próprias de cada norma, na mesma posição (Efeito_no_SGA ↔ Efeito_no_SGQ, Implicacao_SGA ↔
Implicacao_SGQ, Selecionado_Atv_3_1 ↔ Prioritario, Torna_se_Obrigacao ↔ Tratado_pelo_SGQ) — ver RG-SGQ-00
Matriz_Harmonizacao_SGI. As colunas extra do SGQ ficam sempre no FIM da tabela.

Aqui registam-se os fatores com a LENTE DA QUALIDADE (efeito na capacidade de entregar produto conforme e de aumentar a
satisfação do cliente); ID_Contexto_SGI liga ao fator de origem no RG-SGA-01 quando existe.
"""
import datetime as dt
from sgqlib import *
from dimsq import *

D = DATA_REF

# ------------------------------------------------------------------ PESTEL (lente da qualidade)
# (ID, dimensão, fator externo, descrição, condição ambiental ISO 2026, direção do efeito, efeito no SGQ, classificação, tendência, horizonte,
#  probabilidade 1-3, impacto 1-3, fonte de monitorização, resposta estratégica, ID SWOT, ID RO (RG-SGQ-04), parte interessada, tema, ESG, dono,
#  IDs risco SGI (RG-SGA-02), ID contexto SGI (RG-SGA-01))
PESTEL = [
    ("PESQ-01", "Económico", "Entrada nos mercados alimentar e farmacêutico",
     "4 clientes novos (CUST-015 a CUST-018) e 17 SKU lançados em jul/2026 (dataset desde 06/07/2026).", "Não aplicável", "Não aplicável",
     "Exige requisitos legais de produto (Reg. 10/2011, 21 CFR 211.132), validação de processos e rastreabilidade mais rigorosos.",
     "Oportunidade", "Crescente", "Curto (<1 ano)", 3, 3, "Revisão de requisitos (RG-SGQ-10) e projetos D&D (RG-SGQ-11) — trimestral",
     "Stage-gate de D&D com validação de processo e safe launch por SKU.", "SWTQ-O01", "O12", "Clientes alimentar e farmacêutico",
     "Cliente / mercado", "S + G", RD_, "R12; O12", "SWT-F04"),
    ("PESQ-02", "Legal", "Materiais em contacto com alimentos e embalagem farmacêutica",
     "Reg. (CE) 1935/2004, Reg. (UE) 10/2011, BPF (Reg. 2023/2006) e 21 CFR 211.132: migração EN 1186-3 por lote e anel de inviolabilidade.",
     "Não aplicável", "Não aplicável",
     "Um lote não conforme em alimentar/farma tem consequências legais e de saúde; aumenta o custo de avaliação (ensaios de migração).",
     "Risco", "Crescente", "Curto (<1 ano)", 3, 3, "Vigilância legal e normativa (RG-SGQ-08 Documentos_Externos) — mensal",
     "Plano de controlo com ensaio de migração por lote e validação do processo (8.5.1 f).", "SWTQ-T02", "R16", "Autoridades (ASAE, INFARMED, DGAV)",
     "Legal / conformidade", "S + G", GQ, "R16; R33", "PES-18"),
    ("PESQ-03", "Económico", "Clientes exigem Cpk ≥ 1,33, zero defeito e rastreabilidade",
     "Raio-X analítico: 190 grupos máquina × molde × característica com Cpk < 1,33; CPMU 4,5 reclamações por milhão.", "Não aplicável", "Não aplicável",
     "0% dos grupos com Cpk ≥ 1,33: risco de reclamações e de perda de clientes.",
     "Risco", "Crescente", "Curto (<1 ano)", 3, 3, "KPI Cpk e PPM de cliente (RG-SGQ-05) — mensal",
     "Estudos de capacidade por Pareto e controlo estatístico nas características críticas (OBJ-Q-04).", "SWTQ-T01", "R17", "Clientes de cosmética (marcas UE)",
     "Processo / capacidade", "S + G", GQ, "R16; R17", "SWT-T04; PES-18"),
    ("PESQ-04", "Económico", "Pressão de preço e sazonalidade da procura (pico set–nov)",
     "Margem ≈ € 0,13/un; produção jul–set/2026 +30% face ao 1.º semestre.", "Não aplicável", "Não aplicável",
     "O pico aumenta turnos, operadores temporários e risco de defeito; pressão para aceitar concessões.",
     "Risco e Oportunidade", "Estável", "Curto (<1 ano)", 2, 2, "Plano de capacidade e KPI de concessões (RG-SGQ-05) — mensal",
     "Planeamento de capacidade antes do pico e concessões só com aprovação do cliente.", None, "O14", "Acionistas / Direção",
     "Cliente / mercado", "S + G", GPROD, "O14; R23", "PES-20; SWT-O05"),
    ("PESQ-05", "Económico", "Qualidade variável de resinas de fornecedores spot e de PCR/rPET",
     "Inspeção de receção: 1.896 lotes, 73 rejeitados e 117 aceites com derrogação; SUP-005 com 74,5% de lotes aceites.",
     "Recursos naturais", "Ambiente → Organização",
     "Lotes de matéria-prima fora de especificação passam à produção e geram defeito e scrap.",
     "Risco", "Crescente", "Médio (1-3 anos)", 3, 2, "Scorecard de fornecedores (RG-SGQ-12) — mensal",
     "Scorecard A–D, SCAR com 8D e qualificação de fontes alternativas (OBJ-Q-07).", "SWTQ-T03", "R13", "Fornecedores de resinas e masterbatch",
     "Cadeia de valor / fornecedores", "S + G", CMP_, "R13; R14; R36", "SWT-W02; SWT-T02; PES-03"),
    ("PESQ-06", "Ambiental", "Ondas de calor na nave de produção",
     "Temperatura ambiente > 30 °C; julho/2026: alarme de temperatura dos moldes (INC-2026-08 do SGA).", "Clima", "Ambiente → Organização",
     "Aumenta a variação de peso/espessura no sopro de PET (condicionamento de preformas) e o tempo de ciclo; risco para a conformidade.",
     "Risco", "Crescente", "Médio (1-3 anos)", 3, 2, "Temperatura da nave e do chiller (RG-SGQ-02 Ambiente_Operacao) — diária no verão",
     "Janela de processo de verão validada e reforço do arrefecimento dos moldes.", "SWTQ-T04", "R34", "Clientes de cosmética (marcas UE)",
     "Clima / GEE", "E + G", GMAN, "R34", "PES-08; SWT-T01"),
    ("PESQ-07", "Ambiental", "Disrupções da cadeia de abastecimento por eventos climáticos extremos",
     "Portos, transporte e fábricas de polímero (EUA, Singapura); paragens 'Raw Material Shortage' no dataset de paragens.", "Clima", "Ambiente → Organização",
     "A falta de matéria-prima interrompe ordens de produção e entregas (OTIF).",
     "Risco", "Crescente", "Médio (1-3 anos)", 2, 3, "Stock de segurança e fornecedores alternativos aprovados (RG-SGQ-12) — mensal",
     "Stock de segurança, segunda fonte aprovada e aviso ao cliente (8.2.1 e).", "SWTQ-T04", "R15", "Clientes (todos)",
     "Cadeia de valor / fornecedores", "E + G", CMP_, "R15; R34", "PES-19; SWT-T01"),
    ("PESQ-08", "Social", "Clientes pedem pegada de carbono e conteúdo reciclado do produto",
     "Questionários ESG de CUST-001, CUST-011 e CUST-013 (requisitos relacionados com o clima — 4.2 Nota).", "Clima", "Organização → Ambiente",
     "O requisito do cliente passa a requisito de produto a rever em 8.2 (declarações PCR e PCF).",
     "Oportunidade", "Crescente", "Curto (<1 ano)", 2, 3, "Requisitos específicos de cliente (RG-SGQ-10) — semestral",
     "Tratar as declarações PCR/PCF como requisito de produto quando especificadas.", "SWTQ-O02", "O5", "Clientes de cosmética (marcas UE)",
     "Produto / embalagem", "E + S + G", DCOM, "O5; R33", "PES-04; SWT-O01"),
    ("PESQ-09", "Tecnológico", "Visão artificial, sensores e analytics para prevenir defeitos",
     "10 de 22 máquinas com deteção automática de defeitos.", "Não aplicável", "Não aplicável",
     "Permite passar da inspeção por amostragem AQL ao controlo em linha nas características críticas.",
     "Oportunidade", "Crescente", "Curto (<1 ano)", 2, 3, "Roadmap Quality 4.0 (RG-SGQ-19) — semestral",
     "Business case de visão artificial nas características críticas.", "SWTQ-O03", "O13", "Acionistas / Direção",
     "Governação e dados", "G", TI_, "O3; O13", "PES-06; SWT-O04"),
    ("PESQ-10", "Legal", "PPWR (Reg. UE 2025/40) aplicável desde 12/08/2026",
     "Só 9 de 22 famílias com dossier PPWR (NC-SGA-26-02).", "Recursos naturais", "Organização → Ambiente",
     "A documentação técnica e a declaração UE de conformidade passam a fazer parte das saídas do design e da libertação.",
     "Risco", "Crescente", "Curto (<1 ano)", 3, 2, "Matriz legal de produto (RG-SGA-20) e saídas de D&D (RG-SGQ-11) — mensal",
     "Dossier técnico por família como saída obrigatória do D&D.", "SWTQ-T02", "R33", "Clientes (todos)",
     "Legal / conformidade", "E + G", RD_, "R33", "PES-12"),
    ("PESQ-11", "Legal", "Transição para a ISO 9001:2026 (regras IAF, até set/2029)",
     "Novos requisitos: alterações climáticas (4.1/4.2), cultura da qualidade e ética (5.1.1 i, 7.3 e), oportunidades (6.1.3), contingência (8.2.1 e).",
     "Não aplicável", "Não aplicável",
     "Condiciona o programa de auditoria e o plano de transição (MOC-Q-26-01).",
     "Risco e Oportunidade", "Estável", "Médio (1-3 anos)", 2, 2, "Plano de transição e programa de auditoria (RG-SGQ-16) — trimestral",
     "Plano de transição e auditoria interna às cláusulas novas antes da auditoria de certificação.", None, "O12", "Organismo de certificação",
     "Legal / conformidade", "G", GQ, "O12", "PES-18"),
]

# ------------------------------------------------------------------ SWOT (lente da qualidade)
# (ID, quadrante, descrição, evidência, implicação no SGQ, processo, tema, ID PESTEL, converte em, ID RO (RG-SGQ-04), prioritário, estratégia,
#  indicador, IDs risco SGI (RG-SGA-02), ID contexto SGI (RG-SGA-01))
SWOT = [
    ("SWTQ-F01", "Força", "Cultura de dados: 18 meses de OEE, SPC, AQL e rastreabilidade lote → ordem num data warehouse (bronze/silver/gold) com Power BI.",
     "Data warehouse medalhão e dashboards de produção e qualidade.", "Permite análise e avaliação baseada em evidência (9.1.3) e auditorias priorizadas pelo risco.",
     "TI", "Governação e dados", "PESQ-09", "Oportunidade", "O3", "Sim", "Controlo de dados e software (RG-SGQ-08) e painel de KPI (RG-SGQ-05).",
     "N.º de KPI da qualidade com dados automáticos", "O3; R26", "SWT-F01; SWT-F05"),
    ("SWTQ-F02", "Força", "Sistema de medição adequado no peso das tampas (%GRR 3,5% da variação total; ndc 40).",
     "Estudo GRR-CAP-WEIGHT-001 (ago/2026).", "Decisões de conformidade confiáveis no peso; base para alargar o MSA a espessura, binário e inspeção visual.",
     "MET", "Medição / metrologia", None, "Oportunidade", None, "Não", "Alargar o MSA às restantes características críticas (plano MSA — RG-SGQ-09).",
     "% de características críticas com MSA aceite", "R17", "SWT-F06"),
    ("SWTQ-F03", "Força", "Estratégia 2026–2028 aprovada: crescer em alimentar/farma e certificar o SGI (ISO 9001:2026 + ISO 14001:2026).",
     "Plano estratégico 2026–2028 aprovado pela Direção.", "Integra os requisitos do SGQ nos processos de negócio (5.1.1 b) e define prioridades de investimento.",
     "GES", "Governação e dados", "PESQ-01", "Oportunidade", "O12", "Não", "Revisão pela gestão semestral (RG-SGQ-17) com objetivos ligados à estratégia.",
     "% de objetivos da qualidade no prazo", "O12", None),
    ("SWTQ-F04", "Força", "Causas-raiz conhecidas com evidência causal forte (IM-002 com MSA e DOE; SS-001 e M-SOP-007 respondem à intervenção).",
     "Estudos DOE/MSA; PFMEA (RG-SGQ-04).", "Ações de alta confiança reduzem rejeição, refação e reclamações.",
     "INJ", "Processo / capacidade", None, "Oportunidade", "O1", "Não", "Replicar a janela validada da IM-002 e a manutenção por condição (O1, O2).",
     "Short shot IM-002 (DPMO)", "O1; O2", "SWT-F06"),
    ("SWTQ-W01", "Fraqueza", "Desempenho da qualidade abaixo da meta: rejeição ≈ 2,4% (meta 2,0%), FPY 88,7% e 31% das CAPA não eficazes.",
     "Charter do projeto: FPY 0,887; CAPA vencidas 49%.", "Custo da não qualidade e reclamações; sistema de ação corretiva pouco eficaz.",
     "QUA", "Custo da qualidade", None, "Risco", "R20", "Sim", "KPI mensais (RG-SGQ-05) e eficácia das CAPA (RG-SGQ-18).",
     "Taxa de rejeição; % de CAPA eficazes", "R20; R24", "SWT-W03"),
    ("SWTQ-W02", "Fraqueza", "Cultura de produtividade: pressão por meta e prémio de defeito no turno 2 (fadiga, passagem de turno).",
     "Taxa de rejeição do turno 2 acima dos turnos 1 e 3 (raio-X analítico).", "Aumenta a rejeição em todos os processos e reduz o relato de problemas (cultura da qualidade, 5.1.1 i).",
     "PCP", "Cultura da qualidade", None, "Risco", "R9", "Não", "Avaliação da cultura da qualidade (RG-SGQ-03) e KPI por turno.",
     "Rejeição do turno 2 vs. média da fábrica", "R9", "PES-16"),
    ("SWTQ-W03", "Fraqueza", "Conhecimento crítico concentrado em poucas pessoas (afinação de moldes, DOE da IM-002, Gage R&R).",
     "3 técnicos com > 10 anos concentram as afinações de molde.", "A saída de uma pessoa-chave põe em risco a afinação e a validação de processos.",
     "RH", "Conhecimento", None, "Risco", None, "Não", "Registo de conhecimento organizacional e polivalência (RG-SGQ-07).",
     "N.º de conhecimentos críticos com ≥ 2 detentores", "O1", None),
    ("SWTQ-W04", "Fraqueza", "Frota com máquinas antigas (5 máquinas de 2011–2013) e 4 máquinas novas em 2026 por qualificar.",
     "Perfil de máquinas: ano de instalação e deteção automática.", "Máquinas antigas sem deteção automática e com mais paragens; máquinas novas exigem qualificação IQ/OQ/PQ.",
     "MAN", "Infraestrutura / equipamentos", None, "Risco", "R3", "Não", "Plano de manutenção e qualificação de equipamento (RG-SGQ-02).",
     "MTBF das máquinas de 2011–2013", "R3; R7", "SWT-W07"),
    ("SWTQ-W05", "Fraqueza", "Operadores temporários no pico e indisponibilidade de operadores (maior causa de paragem não planeada).",
     "6 operadores temporários; paragens por falta de operador.", "Pessoas sem competência validada nas características críticas; risco de erro humano (8.5.1 g).",
     "RH", "Pessoas / competências", None, "Risco", "R23", "Não", "Matriz de competências e validação no posto (RG-SGQ-07).",
     "% de operadores validados nas características críticas", "R23; R10", "SWT-W07"),
    ("SWTQ-O01", "Oportunidade", "Entrada em alimentar e farmacêutico: 4 clientes e 17 SKU novos em 2026.",
     "Dataset desde 06/07/2026; CUST-015 a CUST-018.", "Crescimento com requisitos mais exigentes: exige D&D, validação e rastreabilidade robustos.",
     "RD", "Cliente / mercado", "PESQ-01", "Oportunidade", "O12", "Sim", "Safe launch e stage-gate por SKU (RG-SGQ-11).",
     "FPY de lançamento", "R12; O12", "SWT-F04"),
    ("SWTQ-O02", "Oportunidade", "Clientes valorizam declarações verificáveis de conteúdo reciclado e pegada de carbono do produto.",
     "Questionários ESG de CUST-001, CUST-011 e CUST-013.", "Diferenciação comercial se as declarações forem controladas como requisito de produto (8.2.2).",
     "COM", "Produto / embalagem", "PESQ-08", "Oportunidade", "O5", "Não", "Requisitos específicos de cliente com evidência de fornecedor (RG-SGQ-10; RG-SGA-19).",
     "% de pedidos PCR/PCF respondidos com evidência", "O5; R33", "PES-04; SWT-O01"),
    ("SWTQ-O03", "Oportunidade", "Visão artificial, sensores e analytics para prevenir defeitos em vez de os inspecionar.",
     "Business case de visão (RG-SGA-02 O13); 10 de 22 máquinas com deteção automática.", "Menos escapes ao cliente e menor custo de avaliação.",
     "TI", "Governação e dados", "PESQ-09", "Oportunidade", "O13", "Não", "Business case de visão e painel de KRI (O13, O3).",
     "Custo de avaliação (€/mês)", "O3; O13", "SWT-O04"),
    ("SWTQ-T01", "Ameaça", "Clientes exigem Cpk ≥ 1,33, zero defeito e rastreabilidade, com risco de reclamação e devolução.",
     "190 grupos com Cpk < 1,33; CPMU 4,5.", "Reclamações, devoluções e perda de clientes se a capacidade não for demonstrada.",
     "QUA", "Processo / capacidade", "PESQ-03", "Risco", "R17", "Sim", "Estudos de capacidade por Pareto e SPC nas características críticas (OBJ-Q-04).",
     "% de subgrupos com Cpk ≥ 1,00", "R16; R17", "SWT-T04"),
    ("SWTQ-T02", "Ameaça", "Requisitos legais de produto mais exigentes: materiais em contacto com alimentos, embalagem farmacêutica e PPWR.",
     "Reg. 1935/2004 e 10/2011; 21 CFR 211.132; Reg. (UE) 2025/40.", "Um lote não conforme tem consequências legais; novas saídas obrigatórias do D&D e da libertação.",
     "LAB", "Legal / conformidade", "PESQ-02", "Risco", "R33", "Não", "Vigilância legal de produto e dossier técnico por família.",
     "% de famílias com dossier PPWR", "R16; R33", "PES-12; PES-18"),
    ("SWTQ-T03", "Ameaça", "Qualidade variável de resinas spot e de PCR/rPET.",
     "SUP-005 com 74,5% de lotes aceites; 117 lotes aceites com derrogação.", "Defeitos e scrap por matéria-prima; derrogações sem análise de risco.",
     "CMP", "Cadeia de valor / fornecedores", "PESQ-05", "Risco", "R13", "Não", "Scorecard A–D e SCAR com 8D (RG-SGQ-12).",
     "% de lotes de MP aceites sem derrogação", "R13; R14; R36", "SWT-W02; SWT-T02"),
    ("SWTQ-T04", "Ameaça", "Ondas de calor e eventos climáticos extremos afetam a janela de processo e o abastecimento de resina.",
     "Alarme de temperatura dos moldes em jul/2026; paragens por falta de matéria-prima.", "Defeitos de sopro no verão e atrasos de entrega (OTIF).",
     "SOP", "Clima / GEE", "PESQ-06", "Risco", "R34", "Não", "Janela de processo de verão validada e stock de segurança de resina.",
     "Rejeição do sopro em jun–set; OTIF", "R15; R34", "SWT-T01"),
]

# ------------------------------------------------------------------ TOWS
# (ID, cruzamento, IDs origem, estratégia, ID objetivo (RG-SGQ-05), prazo, dono, KPI, IDs risco SGI)
TOWS = [
    ("TOWSQ-01", "SO (Força+Oportunidade)", "SWTQ-F01; SWTQ-O03; PESQ-09",
     "Usar o data warehouse e a visão artificial para passar da inspeção por amostragem ao controlo em linha das características críticas.",
     "OBJ-Q-02", "2027-06-30", TI_, "Lotes aprovados à primeira (≥ 92%)", "O3; O13"),
    ("TOWSQ-02", "SO (Força+Oportunidade)", "SWTQ-F03; SWTQ-O01",
     "Crescer em alimentar/farma com safe launch e validação de processos antes da produção em série.",
     None, "2027-03-31", RD_, "FPY de lançamento ≥ meta de safe launch", "R12; O12"),
    ("TOWSQ-03", "ST (Força+Ameaça)", "SWTQ-F02; SWTQ-T02",
     "Alargar o MSA às características críticas de alimentar/farma (migração, binário, anel) para decisões de libertação fiáveis.",
     "OBJ-Q-04", "2027-06-30", GQ, "% de características críticas com MSA aceite", "R16; R17"),
    ("TOWSQ-04", "WO (Fraqueza+Oportunidade)", "SWTQ-W02; SWTQ-O01",
     "Programa de cultura da qualidade (gemba walks, relato sem culpa) ligado ao crescimento em alimentar/farma.",
     None, "2027-06-30", DG, "Rejeição do turno 2 vs. média da fábrica", "R9"),
    ("TOWSQ-05", "WT (Fraqueza+Ameaça)", "SWTQ-W01; SWTQ-T01",
     "Tratar primeiro as causas-raiz de maior evidência (IM-002, ISBM-003, SS-001, M-SOP-007) e os estudos de capacidade por Pareto.",
     "OBJ-Q-04", "2027-03-31", GQ, "% de subgrupos com Cpk ≥ 1,00 (≥ 70%)", "R4; R1; R7; R2; R17"),
    ("TOWSQ-06", "WT (Fraqueza+Ameaça)", "SWTQ-W05; SWTQ-T03; PESQ-04",
     "Antes do pico set–nov: validar a competência dos temporários nas características críticas e bloquear MP sem aceitação.",
     "OBJ-Q-07", "2026-10-31", GPROD, "Lotes de MP aceites sem derrogação (≥ 95%)", "R23; R13"),
]

# ------------------------------------------------------------------ 5 forças (lente da qualidade)
CINCO_FORCAS = [
    ("CFQ-01", "Poder negocial dos clientes", "Clientes exigem Cpk ≥ 1,33, zero defeito, aprovação prévia de alterações (farma) e plano de contingência; 18 clientes, CPMU 4,5.",
     "Crescente", "Reclamações, auditorias de cliente e perda de encomendas se a capacidade não for demonstrada.", "Risco", "R16; R17",
     "Inquérito de satisfação ISO 10004 e reclamações (RG-SGQ-15)"),
    ("CFQ-02", "Poder negocial dos fornecedores", "Resinas concentradas em poucos petroquímicos; SUP-005 spot com 74,5% de lotes aceites; PCR com oferta limitada.",
     "Estável", "Pouca alavanca para exigir certificados e 8D; risco de derrogações.", "Risco", "R13; R14; R36", "Scorecard semestral e SCAR (RG-SGQ-12)"),
    ("CFQ-03", "Ameaça de novos entrantes", "Barreira baixa em frascos simples; alta em alimentar/farma (validação, BPF, rastreabilidade).",
     "Estável", "A qualidade demonstrada (certificação, validação de processos) é barreira de entrada.", "Oportunidade", "O12", "Relatório trimestral de mercado"),
    ("CFQ-04", "Ameaça de produtos substitutos", "Vidro, alumínio e recargas; clientes pedem monomaterial e PCR.",
     "Crescente", "Novos materiais exigem requalificação do processo e novos critérios de aceitação.", "Risco", "R14", "Revisão de requisitos (RG-SGQ-10)"),
    ("CFQ-05", "Rivalidade entre concorrentes", "Concorrência por preço (≈ € 0,13/un); diferenciação por qualidade e serviço (OTIF).",
     "Crescente", "Reduzir o custo da não qualidade preserva a margem.", "Oportunidade", "O11; O4", "Custo da qualidade mensal (RG-SGQ-19)"),
]

# ------------------------------------------------------------------ partes interessadas (um requisito pertinente por linha)
# (ID, parte, tipo, categoria, necessidade/expectativa (requisito pertinente), condição ambiental, relevante, tratado pelo SGQ, tipo de obrigação, IDs legal,
#  como monitorizar, frequência, influência, interesse, ID RO (RG-SGQ-04), dono, IDs risco SGI, perceção do risco,
#  fonte do requisito, justificação do tratamento, registo de evidência, ID PI SGI (RG-SGA-01))
PARTES = [
    ("PIQ-01", "Clientes de cosmética (marcas UE)", "Externa", "Clientes B2B",
     "Produto conforme à especificação e ao artwork aprovado; entrega OTIF; resposta a reclamações em ≤ 10 dias úteis.", "Não aplicável", "Sim", "Sim",
     "Contratual (cliente)", None, "Reclamações, OTIF e inquérito de satisfação (RG-SGQ-15)", "Por encomenda", "Alta", "Alta", "R16", DCOM, "R16; R17; R18",
     "Um lote fora de especificação é visto como falha evitável (risco imposto ao cliente).",
     "Contrato / especificação / acordo de qualidade", "Requisito do cliente — núcleo do SGQ (8.2, 8.6, 9.1.2).", "RG-SGQ-10; RG-SGQ-15", "PI-04"),
    ("PIQ-02", "Clientes de cosmética (marcas UE)", "Externa", "Clientes B2B",
     "Declaração de conteúdo reciclado e pegada de carbono do produto.", "Clima", "Sim", "Sim",
     "Contratual (cliente)", "LEG-18", "Questionários ESG e pedidos de cotação", "Semestral", "Alta", "Média", "O5", DCOM, "O5; R33",
     "Uma declaração sem evidência é vista como greenwashing.",
     "Questionários ESG / pedidos de cotação", "Tratado como requisito de produto quando consta da especificação (8.2.2).", "RG-SGQ-10; RG-SGA-19", "PI-04"),
    ("PIQ-03", "Clientes alimentares (CUST-015, CUST-016)", "Externa", "Clientes B2B (novas linhas 2026)",
     "Conformidade com Reg. (CE) 1935/2004, Reg. (UE) 10/2011 e BPF (Reg. 2023/2006); declaração de conformidade por lote.", "Não aplicável", "Sim", "Sim",
     "Legal", "LEG-17", "Ensaio de migração por lote e auditorias de cliente", "Por lote", "Alta", "Alta", "R16", GQ, "R16; R33",
     "Um lote não conforme em contacto com alimentos é risco para a saúde, sem tolerância.",
     "Legislação + especificação", "Requisito legal aplicável ao produto (8.2.2 a1).", "RG-SGQ-10; RG-SGQ-13 (ensaio de migração)", "PI-05"),
    ("PIQ-04", "Clientes farmacêuticos (CUST-017, CUST-018)", "Externa", "Clientes B2B (novas linhas 2026)",
     "Rastreabilidade ao lote de resina, anel de inviolabilidade (21 CFR 211.132), notificação prévia de alterações e auditoria ao fornecedor.", "Não aplicável", "Sim", "Sim",
     "Contratual (cliente)", "LEG-20", "Acordo de qualidade e auditorias de cliente", "Por alteração", "Alta", "Alta", "R16", GQ, "R16; R17; R18",
     "Uma alteração não comunicada é vista como quebra de confiança no fornecedor.",
     "Acordo de qualidade farmacêutico", "Requisito contratual; alterações sujeitas a aprovação do cliente (8.5.6).", "RG-SGQ-06; RG-SGQ-13", "PI-05"),
    ("PIQ-05", "Clientes (todos)", "Externa", "Clientes B2B",
     "Informação sobre ações de contingência em caso de disrupção no fornecimento.", "Clima", "Sim", "Sim",
     "Contratual (cliente)", None, "Comunicação com o cliente (RG-SGQ-08 Comunicacao_Cliente)", "Por ocorrência", "Alta", "Média", "R15", DCOM, "R15; R34",
     "Esperam aviso antecipado, não surpresas na entrega.",
     "Acordo de qualidade / contrato", "Novo em 2026 (8.2.1 e).", "RG-SGQ-08 Comunicacao_Cliente", "PI-04"),
    ("PIQ-06", "Acionistas / Direção", "Interna", "Gestão de topo",
     "Redução do custo da não qualidade e cumprimento dos objetivos; certificação ISO 9001:2026.", "Não aplicável", "Sim", "Sim",
     "Voluntária (compromisso assumido)", None, "Revisão pela gestão; painel mensal de KPI", "Trimestral", "Alta", "Alta", "O12", DG, "R24; O3; O4",
     "Esperam retorno dos investimentos e menor custo da não qualidade.",
     "Plano estratégico", "Objetivos da qualidade (6.2) e revisão pela gestão (9.3).", "RG-SGQ-05; RG-SGQ-17; RG-SGQ-19", "PI-03"),
    ("PIQ-07", "Colaboradores", "Interna", "Trabalhadores próprios (3 turnos)",
     "Instruções claras, formação e condições para fazer bem à primeira; não serem culpabilizados por falhas do sistema.", "Não aplicável", "Sim", "Sim",
     "Voluntária (compromisso assumido)", None, "Inquérito de cultura da qualidade; gemba walks", "Semestral", "Média", "Alta", "R9", RH_, "R9; R23",
     "Sentem pressão por meta; o relato de problemas é visto como risco pessoal.",
     "Inquérito interno / comissão de trabalhadores", "Competência, consciencialização e ambiente dos processos (7.1.4, 7.2, 7.3).", "RG-SGQ-07; RG-SGQ-03", "PI-01"),
    ("PIQ-08", "Fornecedores de resinas e masterbatch", "Externa", "Cadeia de abastecimento",
     "Especificações e critérios de aceitação claros; feedback do desempenho; previsões de encomenda.", "Não aplicável", "Sim", "Sim",
     "Contratual (cliente)", None, "Scorecard e reunião de fornecedor (RG-SGQ-12)", "Trimestral", "Média", "Média", "R13", CMP_, "R13; R14",
     "O fornecedor spot vê a relação como transacional.",
     "Reuniões de fornecedor", "Informação para fornecedores externos (8.4.3).", "RG-SGQ-12", "PI-06"),
    ("PIQ-09", "Organismo de certificação", "Externa", "Avaliação da conformidade",
     "Conformidade com a ISO 9001:2026 e regras de transição IAF (transição até set/2029).", "Não aplicável", "Sim", "Sim",
     "Voluntária (compromisso assumido)", None, "Auditorias externas e plano de transição", "Anual", "Alta", "Baixa", "O12", GQ, "O12",
     "Espera evidência de que o sistema funciona, não documentos isolados.",
     "Regras IAF / contrato de certificação", "Condiciona o programa de auditoria e o plano de transição.", "RG-SGQ-16; RG-SGQ-06 (MOC-Q-26-01)", None),
    ("PIQ-10", "Autoridades (ASAE, INFARMED, DGAV)", "Externa", "Autoridades de produto",
     "Cumprimento dos requisitos legais de materiais em contacto com alimentos e de embalagem de medicamentos.", "Não aplicável", "Sim", "Sim",
     "Legal", "LEG-17; LEG-20", "Vigilância legal (RG-SGQ-08 Documentos_Externos)", "Mensal", "Alta", "Média", "R16", GQ, "R16; R33",
     "A não conformidade de produto é vista como dano à saúde pública, sem margem de tolerância.",
     "Legislação", "Requisito legal (8.2.2 a1, 8.5.5 a).", "RG-SGQ-08 Documentos_Externos", "PI-08"),
    ("PIQ-11", "Laboratórios externos (calibração e ensaios)", "Externa", "Prestadores de serviço",
     "Pedidos de calibração com gama, pontos e incerteza definidos; equipamentos entregues limpos.", "Não aplicável", "Sim", "Sim",
     "Contratual (cliente)", None, "Avaliação de processos externos (RG-SGQ-12)", "Anual", "Baixa", "Média", None, GQ, None,
     None,
     "Contrato de prestação", "Processo externo controlado (8.4) e rastreabilidade metrológica (7.1.5.2).", "RG-SGQ-09; RG-SGQ-12", None),
    ("PIQ-12", "Transportadores", "Externa", "Prestadores de serviço",
     "Guias e etiquetas corretas; paletes estáveis; janelas de carga cumpridas.", "Não aplicável", "Sim", "Sim",
     "Contratual (cliente)", None, "OTIF e reclamações de serviço", "Mensal", "Baixa", "Média", None, LOG, None,
     None,
     "Contrato de transporte", "Preservação e atividades de entrega (8.5.4, 8.5.5).", "RG-SGQ-13", None),
    ("PIQ-13", "Consumidor final", "Externa", "Utilizador do produto",
     "Embalagem segura (sem fugas, inviolabilidade evidente) e informação legível.", "Não aplicável", "Sim", "Sim",
     "Voluntária (compromisso assumido)", None, "Reclamações com origem no consumidor (via cliente)", "Anual", "Baixa", "Alta", "R16", RD_, "R16",
     "Uma fuga ou tampa violada é vista como risco para a saúde.",
     "Requisito não definido pelo cliente mas necessário ao uso (8.2.3 b)", "Tratado através das características críticas do plano de controlo.", "RG-SGQ-13", None),
    ("PIQ-14", "Comunidade / vizinhança", "Externa", "Recetores sensíveis",
     "Ausência de ruído e odores.", "Não aplicável", "Não", "Não",
     "—", None, "Tratado pelo SGA (canal de reclamações)", "—", "Baixa", "Média", None, "Gestor do SGA / EHS (Responsável Ambiental)", "R30; R34",
     None,
     "Reclamações", "Tratado pelo SGA (RG-SGA-01/07); não afeta a conformidade do produto.", None, "PI-11"),
]

# Âmbito: (elemento, conteúdo)
AMBITO = [
    ("Declaração de âmbito", "Conceção, desenvolvimento e fabrico de embalagens plásticas rígidas — frascos soprados (ISBM) em PET, PETG, rPET, PP, PE e PVC, potes e tampas injetadas "
                             "(incluindo tampas com anel de inviolabilidade e tampas de encaixe) — e decoração por serigrafia e hot foil stamping, para os setores da cosmética, "
                             "higiene pessoal, alimentar e farmacêutico."),
    ("Tipos de produtos cobertos (4.3)", "Frascos (famílias FR, FA alimentar, FP farmacêutico), potes (PT), tampas (TR rosca, TF flip top, TE farma inviolável, TP pote, TA alimentar) e peças decoradas."),
    ("Serviços cobertos", "Apoio técnico ao cliente no desenvolvimento de embalagem, gestão de artwork e decoração personalizada."),
    ("Localização", "Plasticom — Unidade 1, Zona Industrial da Marinha Grande, Portugal (instalação única; sem locais remotos)."),
    ("Processos incluídos", "Todos os processos do mapa de processos (RG-SGQ-02 tbl_processos): 3 de gestão, 10 de realização e 5 de suporte."),
    ("Processos subcontratados controlados pelo SGQ (8.4.1 c)", "Calibração de equipamentos (laboratório acreditado), ensaios de migração de confirmação (laboratório externo acreditado), "
                                                              "reparação e reforma de moldes, transporte para o cliente."),
    ("Questões externas e internas consideradas (4.3 a)", "11 fatores PESTEL (tbl_pestel), 16 itens SWOT (tbl_swot), 5 forças competitivas (tbl_cinco_forcas) e a determinação sobre alterações climáticas (tbl_clima)."),
    ("Requisitos das partes interessadas considerados (4.3 b)", "14 requisitos pertinentes de 13 partes interessadas; 13 tratados pelo SGQ (tbl_partes_interessadas, coluna Tratado_pelo_SGQ)."),
    ("Requisitos não aplicáveis (4.3)", "Nenhum. Todos os requisitos da ISO 9001:2026 são aplicáveis: a Plasticom projeta os seus produtos (8.3 aplicável), "
                                        "usa moldes e artwork de clientes (8.5.3 aplicável) e mede com rastreabilidade metrológica (7.1.5.2 aplicável)."),
    ("Integração", "O SGQ integra-se com o SGA (ISO 14001:2026) num sistema de gestão integrado (SGI): registo de riscos único (RG-SGA-02) e contexto com a MESMA estrutura "
                   "no RG-SGA-01 e no RG-SGQ-01 (tbl_pestel, tbl_swot, tbl_tows, tbl_cinco_forcas, tbl_partes_interessadas), consolidável pela coluna Ambito."),
    ("Aprovação", "Diretor Geral, 28/09/2026 — revisto na revisão pela gestão (RG-SGQ-17)."),
]

# Aplicabilidade por cláusula com justificação (4.3)
APLIC = [(c, t, "Aplicável", j) for c, t, j in [
    ("7.1.5.2", "Rastreabilidade da medição", "Balanças, paquímetros, torquímetros e calibres decidem a conformidade de características críticas: calibração rastreável obrigatória."),
    ("8.3", "Design e desenvolvimento", "A Plasticom projeta moldes, frascos e tampas (famílias FA, FP, PT, TE, TP, TA em 2026)."),
    ("8.5.1 f)", "Validação de processos especiais", "Migração em contacto alimentar, cura de tinta e anel de inviolabilidade não são verificáveis a 100% após produção."),
    ("8.5.3", "Propriedade do cliente", "Moldes M-SOP-030 a 033 pagos por clientes; artwork e ficheiros de cor fornecidos pelos clientes."),
    ("8.5.5", "Atividades pós-entrega", "Tratamento de reclamações, devoluções e apoio técnico no enchimento do cliente."),
]]

CLIMA = [
    ("CLI-01", "A mudança climática é uma questão pertinente para o SGQ? (4.1)", "Sim", "Afeta a capacidade de entregar produto conforme (temperatura de processo) e a continuidade do fornecimento.", "PESQ-06; PESQ-07"),
    ("CLI-02", "Efeito físico no processo", "Sim", "Ondas de calor alteram a janela de processo do sopro de PET (condicionamento de preformas) e o arrefecimento dos moldes.", "PESQ-06; SWTQ-T04"),
    ("CLI-03", "Efeito na cadeia de abastecimento", "Sim", "Eventos extremos nos portos e fábricas de polímero (EUA, Singapura) causam atrasos de resina.", "PESQ-07"),
    ("CLI-04", "Requisitos de partes interessadas relacionados com o clima (4.2 Nota)", "Sim", "Clientes pedem pegada de carbono e conteúdo reciclado; tratados como requisito de produto quando especificados.", "PESQ-08; PIQ-02; PIQ-05"),
    ("CLI-05", "Riscos e oportunidades resultantes (6.1)", "Sim", "Tratados no registo corporativo RG-SGA-02 (R34, O5) e na vista da qualidade RG-SGQ-04.", "R34; O5"),
    ("CLI-06", "Revisão da determinação", "Sim", "Revista anualmente na revisão pela gestão e sempre que houver evento climático com impacto em produto ou entrega.", "RG-SGQ-17"),
]


def build(out):
    b = Book("RG-SGQ-01", "Contexto da Organização — PESTEL, SWOT, Partes Interessadas, 5 Forças e TOWS (SGQ) · Âmbito",
             activities="Determinar e rever as questões externas (PESTEL) e internas/externas (SWOT) pertinentes para o SGQ, incluindo alterações climáticas; "
                        "cruzamento estratégico (TOWS) e forças competitivas; partes interessadas e os requisitos que o SGQ trata; âmbito e aplicabilidade.",
             clauses="4.1 Compreender a organização e o seu contexto (inclui determinar se as alterações climáticas são pertinentes); 4.2 Necessidades e expectativas das partes interessadas (a, b, c); 4.3 Âmbito do SGQ (disponível como informação documentada, com justificação de não aplicabilidade)",
             purpose="Registar, com evidência, as questões de contexto que afetam a capacidade da Plasticom de fornecer produtos conformes e aumentar a satisfação do cliente, "
                     "os requisitos pertinentes das partes interessadas e a decisão sobre quais são tratados pelo SGQ, e o âmbito do SGQ. Base para os riscos e oportunidades "
                     "(RG-SGQ-04) e para a revisão pela gestão (9.3.2 b, c). Estrutura igual à do RG-SGA-01 para consolidar o contexto do SGI num único modelo para a gestão de topo.",
             links=[("RG-SGA-01 Contexto (padrão do SGI)", "Mesmas folhas, tabelas e colunas (tbl_pestel, tbl_swot, tbl_tows, tbl_cinco_forcas, tbl_partes_interessadas). "
                                                          "Consolidar: juntar as tabelas homónimas dos dois ficheiros e filtrar pela coluna Ambito (SGA / SGI / SGQ)."),
                    ("RG-SGA-01 — origem dos fatores", "ID_Contexto_SGI liga ao fator PESTEL/SWOT de origem; ID_PI_SGI liga à parte interessada do SGI."),
                    ("RG-SGQ-04 Riscos e oportunidades da qualidade", "ID_RO liga ao risco/oportunidade da qualidade (R-nn / O-nn)."),
                    ("RG-SGA-02 Riscos e oportunidades", "IDs_Risco_SGI (R-nn / O-nn) — registo corporativo único de riscos."),
                    ("RG-SGQ-05 Objetivos", "A Matriz TOWS aponta os objetivos da qualidade (OBJ-Q-nn) derivados do cruzamento estratégico."),
                    ("RG-SGQ-00 Matriz_Harmonizacao_SGI", "Correspondência coluna a coluna entre as tabelas do SGQ e do SGA.")],
             guidance=[("ISO/TC 176 APG — Context of the organization", "O auditor procura evidência de que as questões são conhecidas, monitorizadas e usadas no planeamento, não um documento PESTEL isolado: colunas Efeito_no_SGQ, Fonte_Monitorizacao, Resposta_Estrategica, ID_RO e Proxima_Revisao."),
                       ("ISO/TC 176 APG — Climate change issues (Amd 1:2024)", "A determinação sobre as alterações climáticas é registada com a justificação (tbl_clima) e os fatores climáticos marcados em Condicao_Ambiental_ISO2026 = Clima."),
                       ("iso9001help.co.uk — Navigator Pro (Planning stage)", "Contexto → partes interessadas → âmbito como entradas encadeadas do planeamento do SGQ.")])
    # listas com os MESMOS nomes e valores do RG-SGA-01 (as do SGQ só acrescentam valores)
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
    b.add_list("Tema", TEMAS_Q)
    b.add_list("ESG", ESG)
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Cruzamento", ["SO (Força+Oportunidade)", "ST (Força+Ameaça)", "WO (Fraqueza+Oportunidade)", "WT (Fraqueza+Ameaça)"])

    # ---------------------------------------------------------------- PESTEL (= RG-SGA-01 tbl_pestel)
    pcols = [
        col("ID_PESTEL", 11, desc="Identificador único do fator PESTEL do SGQ.", key="PK", dom="PESQ-nn"),
        col("Dimensao", 13, dv="Dimensao", desc="Dimensão PESTEL."),
        col("Fator_Externo", 34, desc="Nome curto do fator externo."),
        col("Descricao", 55, desc="Descrição do fator, do seu estado atual e do dado que o sustenta."),
        col("Condicao_Ambiental_ISO2026", 20, dv="CondicaoAmbiental", desc="Condição ambiental a que o fator se refere; 'Clima' marca as questões de alterações climáticas (ISO 9001:2026 4.1)."),
        col("Direcao_Efeito", 20, dv="Direcao", desc="A organização afeta o ambiente, o ambiente afeta a organização, ou ambos (só para fatores com condição ambiental)."),
        col("Efeito_no_SGQ", 40, desc="Como o fator afeta a capacidade de entregar produto conforme e aumentar a satisfação do cliente (equivale a Efeito_no_SGA)."),
        col("Classificacao", 15, dv="Classificacao", desc="Se o fator gera risco, oportunidade ou ambos (4.1 Nota 1: positivo/negativo)."),
        col("Tendencia", 12, dv="Tendencia", desc="Tendência observada."),
        col("Horizonte", 15, dv="Horizonte", desc="Horizonte temporal do efeito."),
        col("Probabilidade_1a3", 11, "int", dv="Escala13", desc="Probabilidade de afetar o SGQ (1 baixa – 3 alta)."),
        col("Impacto_1a3", 10, "int", dv="Escala13", desc="Impacto no SGQ (1 baixo – 3 alto)."),
        col("Score", 8, "int", f='=IF(@ID_PESTEL@="","",@Probabilidade_1a3@*@Impacto_1a3@)', desc="Probabilidade × Impacto (1-9)."),
        col("Prioridade", 10, f='=IF(@ID_PESTEL@="","",IF(@Score@>=6,"Alta",IF(@Score@>=3,"Média","Baixa")))', desc="Alta ≥6; Média 3-5; Baixa ≤2."),
        col("Fonte_Monitorizacao", 30, desc="Como e com que frequência o fator é acompanhado (4.1 último parágrafo)."),
        col("Resposta_Estrategica", 42, desc="Resposta estratégica prevista."),
        col("ID_SWOT", 10, desc="Item SWOT relacionado.", key="FK → tbl_swot", req=False),
        col("ID_RO", 9, desc="Risco/oportunidade da qualidade gerado (RG-SGQ-04).", key="FK → RG-SGQ-04", req=False),
        col("Parte_Interessada", 24, desc="Parte interessada mais relacionada (4.2)."),
        col("Tema", 22, dv="Tema", desc="Tema (grafia comum ao SGA quando o tema é partilhado)."),
        col("ESG", 9, dv="ESG", desc="Pilar ESG."),
        col("Dono", 28, dv="Funcao", desc="Função responsável por monitorizar o fator."),
        col("Data_Avaliacao", 12, "date", desc="Data da análise."),
        col("Proxima_Revisao", 12, "date", f='=IF(@ID_PESTEL@="","",EDATE(@Data_Avaliacao@,12))', desc="Revisão anual (antes da Revisão pela Gestão)."),
        col("Ambito", 12, desc="Sistema dono do registo: SGQ (no RG-SGA-01: SGA ou SGI)."),
        col("IDs_Risco_SGI", 16, desc="Riscos/oportunidades do registo corporativo RG-SGA-02 (R-nn / O-nn).", key="FK → RG-SGA-02 tbRiscos/tbOportunidades", req=False),
        col("ID_Contexto_SGI", 16, desc="[Só SGQ] Fator de origem no RG-SGA-01 (PES-nn / SWT-Xnn).", key="FK → RG-SGA-01", req=False),
    ]
    pn = ["ID_PESTEL", "Dimensao", "Fator_Externo", "Descricao", "Condicao_Ambiental_ISO2026", "Direcao_Efeito", "Efeito_no_SGQ", "Classificacao", "Tendencia", "Horizonte",
          "Probabilidade_1a3", "Impacto_1a3", "Fonte_Monitorizacao", "Resposta_Estrategica", "ID_SWOT", "ID_RO", "Parte_Interessada", "Tema", "ESG", "Dono",
          "IDs_Risco_SGI", "ID_Contexto_SGI"]
    prow = []
    for p in PESTEL:
        d = dict(zip(pn, p))
        d["Data_Avaliacao"] = D
        d["Ambito"] = "SGQ"
        prow.append(d)
    b.table("PESTEL", "tbl_pestel", pcols, prow, "Registo das questões externas (PESTEL) pertinentes para o SGQ, com a mesma estrutura do RG-SGA-01.",
            title="PESTEL — QUESTÕES EXTERNAS PERTINENTES PARA O SGQ (4.1)",
            subtitle="Mesma estrutura do RG-SGA-01 tbl_pestel · Ambito = SGQ · Clima marcado em Condicao_Ambiental_ISO2026 · Rever na revisão pela gestão",
            cf=[("Prioridade", {"Alta": "red", "Média": "yellow", "Baixa": "green"}),
                ("Classificacao", {"Risco e": "purple", "Oportunidade": "blue", "Risco": "orange"}),
                ("Condicao_Ambiental_ISO2026", {"Clima": "blue"})], row_height=60, extra_rows=6)

    # ---------------------------------------------------------------- SWOT (= RG-SGA-01 tbl_swot)
    scols = [
        col("ID_SWOT", 10, desc="Identificador único do item SWOT do SGQ.", key="PK", dom="SWTQ-Xnn (F força, W fraqueza, O oportunidade, T ameaça)"),
        col("Quadrante", 13, dv="Quadrante", desc="Quadrante SWOT."),
        col("Natureza", 10, f='=IF(@ID_SWOT@="","",IF(OR(@Quadrante@="Força",@Quadrante@="Fraqueza"),"Interno","Externo"))', desc="Interno (Força/Fraqueza) ou Externo (Oportunidade/Ameaça) — 4.1 Notas 2 e 3."),
        col("Descricao", 55, desc="Descrição aplicada à Plasticom."),
        col("Evidencia", 36, desc="Dado ou fonte que sustenta o item."),
        col("Implicacao_SGQ", 40, desc="Implicação para o sistema de gestão da qualidade (equivale a Implicacao_SGA)."),
        col("Processo", 10, dv="Processo", desc="Processo mais afetado.", key="FK → dim processo"),
        col("Tema", 22, dv="Tema", desc="Tema."),
        col("ID_PESTEL", 10, desc="Fator PESTEL de origem (itens externos).", key="FK → tbl_pestel", req=False),
        col("Converte_em", 13, dv="Classificacao", desc="Tratamento no registo de riscos: risco ou oportunidade."),
        col("ID_RO", 8, desc="ID no registo RG-SGQ-04 (R-nn / O-nn).", key="FK → RG-SGQ-04", req=False),
        col("Prioritario", 12, dv="SimNao", desc="Item prioritário para o planeamento 6.1 (1 por quadrante; equivale a Selecionado_Atv_3_1 do SGA)."),
        col("Estrategia", 42, desc="Estratégia/resposta."),
        col("Indicador", 26, desc="Indicador de acompanhamento."),
        col("Data_Avaliacao", 12, "date", desc="Data da análise SWOT."),
        col("Chave_Vista", 14, f='=IF(@ID_SWOT@="","",@Quadrante@&"|"&COUNTIF(INDEX(#Quadrante#,1):@Quadrante@,@Quadrante@))', desc="Chave técnica (quadrante|ordem) usada pela Vista_SWOT."),
        col("Ambito", 9, desc="Sistema dono do registo: SGQ."),
        col("IDs_Risco_SGI", 16, desc="Riscos/oportunidades do RG-SGA-02 (R-nn / O-nn).", key="FK → RG-SGA-02 tbRiscos/tbOportunidades", req=False),
        col("ID_Contexto_SGI", 16, desc="[Só SGQ] Item de origem no RG-SGA-01 (SWT-Xnn / PES-nn).", key="FK → RG-SGA-01", req=False),
    ]
    sn = ["ID_SWOT", "Quadrante", "Descricao", "Evidencia", "Implicacao_SGQ", "Processo", "Tema", "ID_PESTEL", "Converte_em", "ID_RO", "Prioritario",
          "Estrategia", "Indicador", "IDs_Risco_SGI", "ID_Contexto_SGI"]
    srows = []
    for s in SWOT:
        d = dict(zip(sn, s))
        d["Data_Avaliacao"] = D
        d["Ambito"] = "SGQ"
        srows.append(d)
    b.table("SWOT", "tbl_swot", scols, srows, "Registo SWOT do SGQ (formato longo: um item por linha), com a mesma estrutura do RG-SGA-01. Prioritario marca 1 item por quadrante.",
            title="SWOT — QUESTÕES INTERNAS E EXTERNAS PERTINENTES PARA O SGQ (4.1)",
            subtitle="Mesma estrutura do RG-SGA-01 tbl_swot · Internas: valores, cultura, conhecimento, desempenho (4.1 Nota 3)",
            cf=[("Quadrante", {"Força": "green", "Fraqueza": "orange", "Oportunidade": "blue", "Ameaça": "red"}),
                ("Prioritario", {"Sim": "purple"})], row_height=58, extra_rows=6)

    # ---------------------------------------------------------------- TOWS (= RG-SGA-01 tbl_tows)
    tcols = [
        col("ID_TOWS", 10, desc="Identificador da estratégia cruzada.", key="PK", dom="TOWSQ-nn"),
        col("Cruzamento", 24, dv="Cruzamento", desc="Tipo de cruzamento TOWS."),
        col("IDs_Origem", 26, desc="IDs SWOT/PESTEL combinados (separados por ';')."),
        col("Estrategia", 60, desc="Estratégia resultante."),
        col("ID_Objetivo", 10, desc="Objetivo da qualidade derivado.", key="FK → RG-SGQ-05", req=False),
        col("Prazo", 12, "date", desc="Prazo."),
        col("Dono", 30, dv="Funcao", desc="Responsável."),
        col("KPI", 30, desc="Indicador de sucesso."),
        col("IDs_Risco_SGI", 16, desc="Riscos/oportunidades do RG-SGA-02 (R-nn / O-nn).", key="FK → RG-SGA-02 tbRiscos/tbOportunidades", req=False),
    ]
    trows = [dict(zip([c["name"] for c in tcols], t)) for t in TOWS]
    for t in trows:
        t["Prazo"] = dt.date.fromisoformat(t["Prazo"])
    b.table("Matriz_TOWS", "tbl_tows", tcols, trows, "Cruzamento estratégico SWOT (TOWS) que liga o contexto aos objetivos da qualidade e aos riscos do SGI.",
            title="MATRIZ TOWS — ESTRATÉGIAS CRUZADAS DO SGQ", subtitle="Mesma estrutura do RG-SGA-01 tbl_tows · Liga contexto → objetivos (RG-SGQ-05) → riscos (RG-SGA-02)",
            row_height=48)

    # ---------------------------------------------------------------- 5 forças (= RG-SGA-01 tbl_cinco_forcas)
    fcols = [col("ID_Forca", 8, key="PK", desc="Identificador da força.", dom="CFQ-nn"), col("Forca_Competitiva", 28, desc="Força de Porter."),
             col("Cenario_Evidencias", 60, desc="Cenário e evidências, com a lente da qualidade."), col("Tendencia", 11, dv="Tendencia", desc="Tendência."),
             col("Impacto_Organizacao", 46, desc="Impacto na capacidade de entregar produto conforme."), col("Classificacao", 14, dv="Classificacao", desc="Risco ou oportunidade."),
             col("IDs_Risco_SGI", 16, desc="Riscos/oportunidades do RG-SGA-02 (R-nn / O-nn).", key="FK → RG-SGA-02 tbRiscos/tbOportunidades", req=False),
             col("Como_Monitorizar", 44, desc="Como a força é acompanhada."), col("Data_Avaliacao", 12, "date", desc="Data da análise.")]
    frows = [dict(zip([c["name"] for c in fcols], list(x) + [D])) for x in CINCO_FORCAS]
    b.table("Cinco_Forcas", "tbl_cinco_forcas", fcols, frows, "Cinco forças competitivas (Porter) com a lente da qualidade, ligadas aos riscos/oportunidades do RG-SGA-02.",
            title="CINCO FORÇAS COMPETITIVAS (PORTER) — LENTE DA QUALIDADE", subtitle="Mesma estrutura do RG-SGA-01 tbl_cinco_forcas",
            cf=[("Classificacao", {"Oportunidade": "blue", "Risco": "orange"})], row_height=48)

    # ---------------------------------------------------------------- Vista SWOT (quadro 2x2 calculado, igual ao RG-SGA-01)
    ws = b.sheet("Vista_SWOT", "Quadro SWOT 2×2 para impressão, calculado por fórmulas a partir de tbl_swot (não editar aqui).")
    ws["A1"] = "ANÁLISE SWOT DO SGQ — PLASTICOM (vista calculada)"
    ws["A1"].font = F_TITLE
    ws["A2"] = "Itens marcados com ► são prioritários para o planeamento (6.1). Editar a folha SWOT; esta vista atualiza sozinha."
    ws["A2"].font = F_SUB
    ws.column_dimensions["A"].width = 70
    ws.column_dimensions["B"].width = 70
    ids = b.ref("tbl_swot", "ID_SWOT")
    ds = b.ref("tbl_swot", "Descricao")
    sel = b.ref("tbl_swot", "Prioritario")
    key = b.ref("tbl_swot", "Chave_Vista")
    layout = [(4, 1, "Força", "FORÇAS (internas, positivas)", "green"), (4, 2, "Fraqueza", "FRAQUEZAS (internas, negativas)", "orange"),
              (13, 1, "Oportunidade", "OPORTUNIDADES (externas, positivas)", "blue"), (13, 2, "Ameaça", "AMEAÇAS (externas, negativas)", "red")]
    for r0, c0, quad, label, color in layout:
        h = ws.cell(row=r0, column=c0, value=label)
        h.font = Font(name=FONT, bold=True, size=11, color=CF_COLORS[color][1])
        h.fill = PatternFill("solid", fgColor=CF_COLORS[color][0])
        h.border = BORDER
        for k in range(1, 8):
            idx = f'MATCH("{quad}|{k}",{key},0)'
            f = f'=IFERROR(IF(INDEX({sel},{idx})="Sim","► ","• ")&INDEX({ids},{idx})&" — "&INDEX({ds},{idx}),"")'
            c = ws.cell(row=r0 + k, column=c0, value=f)
            c.font, c.alignment, c.border = F_BASE, WRAP_TOP, BORDER
            ws.row_dimensions[r0 + k].height = 42

    # ---------------------------------------------------------------- partes interessadas (= RG-SGA-01 tbl_partes_interessadas)
    b.add_list("PI_Tipo", ["Interna", "Externa"])
    b.add_list("PI_Nivel", ["Alta", "Média", "Baixa"])
    b.add_list("PI_Obrig", ["Legal", "Contratual (cliente)", "Voluntária (compromisso assumido)", "—"])
    icols = [
        col("ID_PI", 7, desc="Identificador do requisito da parte interessada (uma linha por requisito pertinente).", key="PK", dom="PIQ-nn"),
        col("Parte_Interessada", 30, desc="Parte interessada pertinente (4.2 a)."),
        col("Tipo", 9, dv="PI_Tipo", desc="Interna ou externa."),
        col("Categoria", 24, desc="Categoria."),
        col("Necessidades_Expectativas", 50, desc="Requisito pertinente da parte interessada para o SGQ (4.2 b)."),
        col("Condicao_Ambiental", 18, dv="CondicaoAmbiental", desc="'Clima' quando o requisito está relacionado com as alterações climáticas (ISO 9001:2026 4.2 Nota)."),
        col("Relevante", 8, dv="SimNao", desc="Se a parte é pertinente para o SGQ (4.2 a)."),
        col("Tratado_pelo_SGQ", 9, dv="SimNao", desc="Decisão 4.2 c): o requisito é tratado pelo SGQ? (equivale a Torna_se_Obrigacao do SGA)."),
        col("Tipo_Obrigacao", 22, dv="PI_Obrig", desc="Natureza do requisito: legal, contratual (cliente) ou voluntário."),
        col("IDs_Legal", 18, desc="Requisitos legais associados no RG-SGA-04 (';').", key="FK → RG-SGA-04 tbl_legal", req=False),
        col("Como_Monitorizar", 34, desc="Como o requisito é acompanhado."),
        col("Frequencia", 12, desc="Frequência de acompanhamento."),
        col("Influencia", 9, dv="PI_Nivel", desc="Influência sobre a organização."),
        col("Interesse", 9, dv="PI_Nivel", desc="Interesse / grau de afetação."),
        col("Estrategia", 20, f='=IF(@ID_PI@="","",IF(AND(@Influencia@="Alta",@Interesse@="Alta"),"Gerir de perto",IF(@Influencia@="Alta","Manter satisfeita",IF(@Interesse@="Alta","Manter informada","Monitorizar"))))',
            desc="Matriz influência × interesse."),
        col("ID_RO", 8, desc="Risco/oportunidade da qualidade associado (RG-SGQ-04).", key="FK → RG-SGQ-04", req=False),
        col("Dono", 26, dv="Funcao", desc="Responsável pela relação."),
        col("Data_Revisao", 11, "date", desc="Última revisão."),
        col("IDs_Risco_SGI", 18, desc="Riscos/oportunidades do registo corporativo RG-SGA-02 (R-nn / O-nn).", key="FK → RG-SGA-02 tbRiscos/tbOportunidades", req=False),
        col("Percepcao_Risco", 44, desc="O que a parte teme ou valoriza (perceção do risco).", req=False),
        col("Fonte_Requisito", 26, desc="[Só SGQ] De onde vem o requisito."),
        col("Justificacao_Tratamento", 40, desc="[Só SGQ] Justificação da decisão 4.2 c) e cláusula onde é tratado."),
        col("Registo_Evidencia", 24, desc="[Só SGQ] Registo onde está a evidência.", key="FK → RG-SGQ-nn", req=False),
        col("ID_PI_SGI", 9, desc="[Só SGQ] Parte interessada no RG-SGA-01.", key="FK → RG-SGA-01 tbl_partes_interessadas", req=False),
    ]
    inames = ["ID_PI", "Parte_Interessada", "Tipo", "Categoria", "Necessidades_Expectativas", "Condicao_Ambiental", "Relevante", "Tratado_pelo_SGQ", "Tipo_Obrigacao",
              "IDs_Legal", "Como_Monitorizar", "Frequencia", "Influencia", "Interesse", "ID_RO", "Dono", "IDs_Risco_SGI", "Percepcao_Risco",
              "Fonte_Requisito", "Justificacao_Tratamento", "Registo_Evidencia", "ID_PI_SGI"]
    irows = []
    for p in PARTES:
        d = dict(zip(inames, p))
        d["Data_Revisao"] = D
        irows.append(d)
    b.table("Partes_Interessadas", "tbl_partes_interessadas", icols, irows,
            "Partes interessadas pertinentes, os seus requisitos e a decisão de quais são tratados pelo SGQ (4.2 a–c), com a mesma estrutura do RG-SGA-01.",
            title="PARTES INTERESSADAS — REQUISITOS PERTINENTES E DECISÃO DE TRATAMENTO PELO SGQ (4.2)",
            subtitle="Mesma estrutura do RG-SGA-01 tbl_partes_interessadas · 4.2 c): quais requisitos se tratam no SGQ · Requisitos legais ligam ao RG-SGA-04",
            cf=[("Tratado_pelo_SGQ", {"Sim": "green", "Não": "gray"}), ("Condicao_Ambiental", {"Clima": "blue"}),
                ("Estrategia", {"perto": "red", "satisfeita": "orange", "informada": "yellow"})], row_height=48, extra_rows=6)

    # ---------------------------------------------------------------- folhas próprias do SGQ (4.1 clima, 4.3 âmbito)
    ccols = [col("ID_Clima", 8, key="PK", desc="Pergunta da determinação."), col("Pergunta", 40, desc="Pergunta."), col("Resposta", 9, dv="SimNao", desc="Sim/Não."),
             col("Justificacao", 70, desc="Justificação da determinação."), col("Ligacoes", 18, desc="IDs relacionados.", req=False)]
    b.table("Alteracoes_Climaticas", "tbl_clima", ccols, rows_from(input_names(ccols), CLIMA),
            "Determinação documentada sobre se as alterações climáticas são uma questão pertinente (4.1) e requisitos das partes interessadas relacionados (4.2 Nota).",
            title="DETERMINAÇÃO SOBRE AS ALTERAÇÕES CLIMÁTICAS (4.1 e 4.2 — ISO 9001:2026)",
            subtitle="A norma exige determinar SE é pertinente; a resposta e a justificação ficam aqui como evidência", cf=[("Resposta", {"Sim": "blue"})], row_height=40)

    acols = [col("Elemento", 34, key="PK", desc="Elemento do âmbito."), col("Conteudo", 110, desc="Conteúdo aprovado.")]
    b.table("Ambito_SGQ", "tbl_ambito", acols, [dict(Elemento=a, Conteudo=c) for a, c in AMBITO],
            "Âmbito do SGQ disponível como informação documentada (4.3).",
            title="ÂMBITO DO SISTEMA DE GESTÃO DA QUALIDADE (4.3)",
            subtitle="Tipos de produtos e serviços cobertos · Justificação de requisitos não aplicáveis · Aprovado pela Direção", row_height=46)
    xcols = [col("Clausula", 9, key="PK", desc="Cláusula com aplicabilidade a justificar."), col("Titulo", 30, desc="Título."),
             col("Decisao", 11, desc="Aplicável / Não aplicável."), col("Justificacao", 90, desc="Justificação da decisão.")]
    b.table("Aplicabilidade", "tbl_aplicabilidade", xcols, [dict(zip(input_names(xcols), a)) for a in APLIC],
            "Cláusulas cuja aplicabilidade foi analisada e a justificação (4.3).", cf=[("Decisao", {"Não": "orange", "Aplicável": "green"})], row_height=34)

    ws = b.sheet("Resumo_Contexto", "Resumo calculado: fatores por classificação e prioridade; requisitos tratados pelo SGQ.")
    title(ws, "RESUMO DO CONTEXTO DO SGQ — calculado")
    header_row(ws, 3, ["Indicador", "Valor"], widths=[52, 12])
    P = lambda c: f"tbl_pestel[{c}]"
    S = lambda c: f"tbl_swot[{c}]"
    I = lambda c: f"tbl_partes_interessadas[{c}]"
    ind = [("Fatores PESTEL registados", f'=COUNTA({P("ID_PESTEL")})'),
           ("  prioridade Alta", f'=COUNTIF({P("Prioridade")},"Alta")'),
           ("  relacionados com o clima", f'=COUNTIF({P("Condicao_Ambiental_ISO2026")},"Clima")'),
           ("  sem ligação a risco/oportunidade da qualidade (rever)", f'=COUNTIFS({P("ID_PESTEL")},"<>",{P("ID_RO")},"")'),
           ("Itens SWOT registados", f'=COUNTA({S("ID_SWOT")})'),
           ("  internos (forças e fraquezas)", f'=COUNTIF({S("Natureza")},"Interno")'),
           ("  externos (oportunidades e ameaças)", f'=COUNTIF({S("Natureza")},"Externo")'),
           ("  sem ligação a risco/oportunidade da qualidade (rever)", f'=COUNTIFS({S("ID_SWOT")},"<>",{S("ID_RO")},"")'),
           ("Estratégias TOWS", '=COUNTA(tbl_tows[ID_TOWS])'),
           ("Requisitos de partes interessadas", f'=COUNTA({I("ID_PI")})'),
           ("  tratados pelo SGQ (4.2 c)", f'=COUNTIF({I("Tratado_pelo_SGQ")},"Sim")'),
           ("  relacionados com o clima", f'=COUNTIF({I("Condicao_Ambiental")},"Clima")'),
           ("  a gerir de perto (influência e interesse altos)", f'=COUNTIF({I("Estrategia")},"Gerir de perto")'),
           ("Fatores PESTEL com revisão vencida", f'=COUNTIFS({P("Proxima_Revisao")},"<"&DataRef)')]
    for k, (a, f) in enumerate(ind):
        cell(ws, 4 + k, 1, a, bold=not a.startswith("  "))
        cell(ws, 4 + k, 2, f, fmt="0")
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
