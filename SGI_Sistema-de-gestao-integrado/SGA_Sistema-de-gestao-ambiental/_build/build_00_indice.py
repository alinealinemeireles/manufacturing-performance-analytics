"""Índice do SGA e modelo de dados: catálogo de ficheiros e tabelas, relações (FK), dimensões partilhadas,
mapa das atividades do curso e verificação de integridade referencial entre ficheiros."""
import glob
import os
import re
import datetime as dt
import openpyxl
import pandas as pd
from sgalib import *
from dims import *
import sga_requisitos

FILES = [
    ("SGA-01_Contexto_SWOT_PESTEL.xlsx", "RG-SGA-01", "Contexto do SGA e do SGI: PESTEL, SWOT, TOWS, 5 forças e partes interessadas (fonte única; liga aos riscos R/O do RG-SGA-02)", "Base da 3.1", "4.1; 4.2"),
    ("SGA-02_Gestao_Riscos_Oportunidades.xlsx", "RG-SGA-02", "Gestão de riscos e oportunidades — registo corporativo multiárea (política e apetite, riscos, planos SGI, KRI, BowTie, auditorias AUD-SGI); contexto no RG-SGA-01 e ações ambientais no PAM", "3.1", "6.1.4; 6.1.5"),
    ("SGA-03_Aspetos_Impactes_Ambientais.xlsx", "RG-SGA-03", "Aspetos e impactes ambientais (Mod.G.07.00)", "3.2", "6.1.2"),
    ("SGA-04_Requisitos_Legais_Conformidade.xlsx", "RG-SGA-04", "Requisitos legais e avaliação da conformidade (Mod.G.06.02)", "3.3", "6.1.3; 9.1.2"),
    ("SGA-05_Objetivos_Metas_KPI.xlsx", "RG-SGA-05", "Objetivos SMART e KPI", "3.4", "6.2"),
    ("SGA-06_Plano_Acoes_Melhoria_PAM.xlsx", "RG-SGA-06", "Plano de Ações de Melhoria (Mod.G.10.00)", "3.5; 6.1 T2; 6.2 T2", "6.1.5; 10"),
    ("SGA-07_Nao_Conformidades_RNC.xlsx", "RG-SGA-07", "Não conformidades, incidentes e 5 Porquês", "6.1 T1", "10.2"),
    ("SGA-08_Competencias_Consciencializacao.xlsx", "RG-SGA-08", "Competências e consciencialização", "4.1", "7.2; 7.3"),
    ("SGA-09_Comunicacao_Controlo_Documental.xlsx", "RG-SGA-09", "Comunicação (4 Q) e controlo documental", "4.2", "7.4; 7.5"),
    ("SGA-10_Controlo_Operacional_Rondas.xlsx", "RG-SGA-10", "Checklist e registo de rondas ambientais", "4.3", "8.1"),
    ("SGA-11_Fornecedores_Ciclo_Vida.xlsx", "RG-SGA-11", "Avaliação ambiental de fornecedores", "4.4", "8.1"),
    ("SGA-12_Emergencias_Ambientais.xlsx", "RG-SGA-12", "Emergências, IT-SGA-01 e simulacros", "4.5", "8.2"),
    ("SGA-13_Monitorizacao_Medicao_Desempenho.xlsx", "RG-SGA-13", "Monitorização, calibração, base de dados mensal e desvio", "5.1; 5.2 P1", "9.1.1"),
    ("SGA-14_Auditoria_Interna.xlsx", "RG-SGA-14", "Programa e constatações de auditoria", "5.3 P1", "9.2"),
    ("SGA-15_Revisao_pela_Gestao.xlsx", "RG-SGA-15", "Revisão pela gestão: agenda e ata", "5.4", "9.3"),
    ("SGA-16_Melhoria_Kaizen_EMAS.xlsx", "RG-SGA-16", "Kaizen e indicadores EMAS", "6.2 T1; 6.3", "10.1"),
    ("SGA-18_Planeamento_Alteracoes.xlsx", "RG-SGA-18", "Planeamento de alterações (gestão de mudanças) com checklist de avaliação", "ISO 14001:2026 (complemento)", "6.3"),
    ("SGA-19_ESG_Ambiental_GEE.xlsx", "RG-SGA-19", "ESG ambiental: calculadora e inventário de GEE (âmbitos 1–3), metas 2030, pegada por produto, indicadores VSME/ESRS/GRI/SASB", "ESG (complemento)", "4.1; 6.2; 9.1.1"),
    ("SGA-20_Reciclabilidade_Embalagens.xlsx", "RG-SGA-20", "Reciclabilidade e conformidade de embalagens: avaliação RecyClass por SKU, graus PPWR, conteúdo reciclado (art. 7.º), matriz legal de produto, aplicabilidade por SKU, países, certificados PCR e alegações", "Embalagens (complemento)", "8.1; 6.1.3; 7.4"),
    ("SGA-21_Gestao_Produtos_Quimicos.xlsx", "RG-SGA-21", "Gestão de produtos químicos: papel REACH, inventário e balanço de COV, FDS (Reg. 2020/878), cenários de exposição, registo/importação, declarações SVHC de fornecedores, avaliação de risco químico (DL 24/2012, DL 301/2000), medições VLE, armazenagem, Seveso, matriz legal de químicos", "Químicos (complemento)", "6.1.3; 8.1; 9.1.2"),
    ("../Documentos_SGA_Plasticom/", "MAN/PR/IT", "Manual do SGA (MAN-SGA-01), procedimentos PR-SGA-01 a 16, plano de transição climática PL-SGA-01 e instruções IT-SGA-02, IT-SER-03 (Word)", "Todas", "4.3–10.2"),
    ("SGA-17_Dupla_Materialidade.xlsx", "RG-SGA-17", "Análise de dupla materialidade (temas, IRO, evidências, partes interessadas, painel)", "ESG (complemento)", "4.1; 4.2; 6.1"),
    ("SGA_Atividades_Lusitana_e_Teoria.docx", "DOC-SGA-01", "Word: atividades Lusitana Móveis e questões teóricas", "4.1 (5); 4.2 (reflexão); 5.2 P2; 5.3 P2; auto-estudos", "—"),
]

MAPA = [
    ("3.1", "Tratar riscos e oportunidades", "SGA-02", "Riscos e Oportunidades: grupo METODOLOGIA SGA (filtrar 'Selecionado Atividade 3.1' = Sim)"),
    ("3.2", "Aspetos e impactes ambientais", "SGA-03", "Resumo_Atividade_3_2; Mod.G.07.00_Matriz"),
    ("3.3", "Requisitos legais e conformidade", "SGA-04", "Mod.G.06.02_Vista (print screen); Requisitos_Legais"),
    ("3.4", "Objetivos SMART e KPI", "SGA-05", "Resumo_Atividade_3_4; Objetivos_SMART"),
    ("3.5", "Plano de ações de melhoria", "SGA-06", "Mod.G.10.00_Vista (ações 01/26 e 02/26)"),
    ("4.1", "Matriz de competências", "SGA-08 + Word", "Resumo_Atividade_4_1; frase Competência vs Consciencialização no Word"),
    ("4.2", "Comunicação e documentação", "SGA-09 + Word", "Resumo_Atividade_4_2; reflexão obsoleto vs em vigor no Word"),
    ("4.3", "Checklist de ronda ambiental", "SGA-10 + Word", "Pontos_Controlo; Checklist_Ronda_Impressao; auto-estudo ar comprimido no Word"),
    ("4.4", "Fornecedores e ciclo de vida", "SGA-11 + Word", "Resumo_Atividade_4_4; auto-estudo logística reversa no Word"),
    ("4.5", "Emergência e instrução de trabalho", "SGA-12 + Word", "IT-SGA-01_Derrames (print screen); auto-estudo válvula de corte no Word"),
    ("5.1", "Plano de monitorização e medição", "SGA-13", "Plano_Monitorizacao; Equipamentos_Calibracao"),
    ("5.2 P1", "Análise de desvio (+15%)", "SGA-13", "Analise_Desvio_5_2; Hipoteses_Desvio; Pesagem_Solvente"),
    ("5.2 P2", "KPI da energia solar (Lusitana)", "Word", "Secção 5.2 Parte 2"),
    ("5.3 P1", "Auditoria interna à Plasticom", "SGA-14", "Checklist_Constatacoes; Relatorio_Resumo"),
    ("5.3 P2", "Cláusulas das constatações (Lusitana)", "Word", "Secção 5.3 Parte 2"),
    ("5.4", "Revisão pela gestão", "SGA-15", "Convocatoria_Impressao (Parte I); Ata_Impressao (Parte II)"),
    ("6.1", "NC do kit antipoluição", "SGA-07 + SGA-06", "RNC_Formulario (5 Porquês); PAM-26-04 (C1) e PAM-26-05 (C2)"),
    ("6.2", "Kaizen", "SGA-16 + SGA-06", "Resumo_Atividade_6_2; PAM-26-06"),
    ("6.3", "EMAS", "SGA-16 + Word", "EMAS_Indicadores; EMAS_Transparencia; diferenças ISO 14001 vs EMAS no Word"),
    ("QUI", "Gestão de produtos químicos — REACH/CLP e toxicidade (complemento)", "SGA-21", "Painel; Papel_REACH; Inventario; FDS_Verificacao; Avaliacao_Risco; Requisitos_Legais"),
    ("EMB", "Reciclabilidade de embalagens (complemento)", "SGA-20", "Painel; Avaliacao_RecyClass; Formulario_RecyClass; Requisitos_Embalagem; Aplicabilidade_Produto"),
    ("ESG", "Dupla materialidade (complemento)", "SGA-17", "Painel (filtros, matriz, gráfico, tabela dinâmica); Temas; IRO; Evidencias; Consultas"),
]

# relações FK: (tabela origem, coluna, tabela destino, coluna destino, separador)
REL = [
    ("tbl_swot", "ID_RO", "tbRiscos|tbOportunidades", "ID RO (SGA)|ID RO (SGA)"), ("tbl_pestel", "ID_RO", "tbRiscos|tbOportunidades", "ID RO (SGA)|ID RO (SGA)"), ("tbl_pestel", "ID_SWOT", "tbl_swot", "ID_SWOT"),
    ("tbRiscos", "ID de origem (contexto SGA)", "tbl_swot|tbl_pestel|tbl_legal", "ID_SWOT|ID_PESTEL|ID_Legal"), ("tbRiscos", "Cód. PAM (RG-SGA-06)", "tbl_pam", "ID_Acao"),
    ("tbOportunidades", "ID de origem (contexto SGA)", "tbl_swot|tbl_pestel|tbl_legal", "ID_SWOT|ID_PESTEL|ID_Legal"), ("tbOportunidades", "Cód. PAM (RG-SGA-06)", "tbl_pam", "ID_Acao"),
    ("tbl_aspetos", "ID_Legal", "tbl_legal", "ID_Legal"), ("tbl_aspetos", "ID_RO", "tbRiscos|tbOportunidades", "ID RO (SGA)|ID RO (SGA)"), ("tbl_aspetos", "ID_Objetivo", "tbl_objetivos", "ID_OBJ"),
    ("tbl_aspetos", "ID_PAM", "tbl_pam", "ID_Acao"), ("tbl_aspetos", "ID_Monitorizacao", "tbl_plano_monitorizacao", "ID_MED"),
    ("tbl_legal", "ID_PAM", "tbl_pam", "ID_Acao"), ("tbl_legal", "IDs_Aspetos", "tbl_aspetos", "ID_Aspeto"),
    ("tbl_objetivos", "Origem_IDs", "tbl_aspetos|tbRiscos|tbOportunidades|tbl_legal|tbl_pestel", "ID_Aspeto|ID RO (SGA)|ID RO (SGA)|ID_Legal|ID_PESTEL"), ("tbl_objetivos", "Acoes_PAM", "tbl_pam", "ID_Acao"),
    ("tbl_kpi", "ID_MED", "tbl_plano_monitorizacao", "ID_MED"),
    ("tbl_pam", "ID_RO_Afetado", "tbRiscos|tbOportunidades", "ID RO (SGA)|ID RO (SGA)"),
    ("tbl_nc", "ID_PAM_C1", "tbl_pam", "ID_Acao"), ("tbl_nc", "ID_PAM_C2", "tbl_pam", "ID_Acao"),
    ("tbl_competencias", "ID_Aspeto_AAS", "tbl_aspetos", "ID_Aspeto"),
    ("tbl_pontos", "ID_Aspeto", "tbl_aspetos", "ID_Aspeto"), ("tbl_execucao_rondas", "ID_NC", "tbl_nc", "ID_NC"),
    ("tbl_cenarios", "IDs_Aspetos", "tbl_aspetos", "ID_Aspeto"), ("tbl_simulacros", "ID_PAM", "tbl_pam", "ID_Acao"),
    ("tbl_plano_monitorizacao", "IDs_Aspetos", "tbl_aspetos", "ID_Aspeto"), ("tbl_hipoteses", "ID_PAM", "tbl_pam", "ID_Acao"),
    ("tbl_constatacoes", "ID_NC", "tbl_nc", "ID_NC"), ("tbl_constatacoes", "ID_PAM", "tbl_pam", "ID_Acao"),
    ("tbl_decisoes", "IDs_PAM", "tbl_pam", "ID_Acao"), ("tbl_kaizen", "ID_PAM", "tbl_pam", "ID_Acao"),
    ("tbl_dma_iro", "ID_Tema", "tbl_dma_temas", "ID_Tema"), ("tbl_dma_iro", "IDs_Contexto", "tbl_swot|tbl_pestel", "ID_SWOT|ID_PESTEL"),
    ("tbl_dma_iro", "ID_RO", "tbRiscos|tbOportunidades", "ID RO (SGA)|ID RO (SGA)"), ("tbl_dma_iro", "IDs_Aspetos", "tbl_aspetos", "ID_Aspeto"),
    ("tbl_dma_iro", "ID_Legal", "tbl_legal", "ID_Legal"), ("tbl_dma_iro", "ID_OBJ", "tbl_objetivos", "ID_OBJ"),
    ("tbl_dma_iro", "ID_KPI", "tbl_kpi", "ID_KPI"), ("tbl_dma_iro", "ID_PAM", "tbl_pam", "ID_Acao"),
    ("tbl_dma_evidencias", "ID_IRO", "tbl_dma_iro", "ID_IRO"), ("tbl_dma_consultas", "ID_Tema", "tbl_dma_temas", "ID_Tema"),
    ("tbl_partes_interessadas", "IDs_Legal", "tbl_legal", "ID_Legal"), ("tbl_partes_interessadas", "ID_RO", "tbRiscos|tbOportunidades", "ID RO (SGA)|ID RO (SGA)"),
    ("tbl_incidentes", "ID_NC", "tbl_nc", "ID_NC"), ("tbl_incidentes", "ID_Aspeto", "tbl_aspetos", "ID_Aspeto"), ("tbl_incidentes", "ID_Cenario_EMG", "tbl_cenarios", "ID_Cenario"),
    ("tbl_comunicacoes_externas", "ID_Incidente", "tbl_incidentes", "ID_Incidente"), ("tbl_comunicacoes_externas", "ID_NC", "tbl_nc", "ID_NC"),
    ("tbl_comunicacoes_externas", "ID_PAM", "tbl_pam", "ID_Acao"), ("tbl_manutencao_ambiental", "ID_Legal", "tbl_legal", "ID_Legal"),
    ("tbl_manutencao_ambiental", "ID_Incidente", "tbl_incidentes", "ID_Incidente"), ("tbl_fornecedores", "IDs_Aspetos", "tbl_aspetos", "ID_Aspeto"),
    ("tbl_outros_fornecedores", "IDs_Aspetos", "tbl_aspetos", "ID_Aspeto"), ("tbl_analises", "ID_Legal", "tbl_legal", "ID_Legal"),
    ("tbl_alteracoes", "IDs_Aspetos", "tbl_aspetos", "ID_Aspeto"), ("tbl_alteracoes", "ID_Legal", "tbl_legal", "ID_Legal"),
    ("tbl_alteracoes", "ID_RO", "tbRiscos|tbOportunidades", "ID RO (SGA)|ID RO (SGA)"),
    ("tbl_inventario_gee", "ID_FE", "tbl_fatores_emissao", "ID_FE"), ("tbl_pegada_produto", "ID_FE_Material", "tbl_fatores_emissao", "ID_FE"),
    ("tbl_legal", "IDs_Req_Embalagem", "tbl_requisitos_emb", "ID_Req"), ("tbl_requisitos_emb", "ID_Legal", "tbl_legal", "ID_Legal"),
    ("tbl_requisitos_emb", "ID_PAM", "tbl_pam", "ID_Acao"), ("tbl_aplicabilidade", "ID_Req", "tbl_requisitos_emb", "ID_Req"),
    ("tbl_recyclass", "Familia_PPWR", "tbl_familias_ppwr", "ID_Familia"), ("tbl_tampas", "Familia_PPWR", "tbl_familias_ppwr", "ID_Familia"),
    ("tbl_familias_ppwr", "ID_PAM", "tbl_pam", "ID_Acao"), ("tbl_alegacoes", "ID_PAM", "tbl_pam", "ID_Acao"), ("tbl_maturidade_emb", "ID_PAM", "tbl_pam", "ID_Acao"),
    ("tbl_certificados_pcr", "ID_Fornecedor", "tbl_fornecedores", "ID_Fornecedor"), ("tbl_materiais", "ID_Fornecedor", "tbl_fornecedores", "ID_Fornecedor"),
    ("tbl_quimicos", "ID_Fornecedor", "tbl_fornecedores|tbl_outros_fornecedores", "ID_Fornecedor|ID"), ("tbl_quimicos", "IDs_Aspetos", "tbl_aspetos", "ID_Aspeto"),
    ("tbl_registo_reach", "ID_Fornecedor", "tbl_fornecedores", "ID_Fornecedor"), ("tbl_declaracoes", "ID_Fornecedor", "tbl_fornecedores|tbl_outros_fornecedores", "ID_Fornecedor|ID"),
    ("tbl_requisitos_quimicos", "ID_Legal", "tbl_legal", "ID_Legal"), ("tbl_requisitos_quimicos", "IDs_PAM", "tbl_pam", "ID_Acao"),
    ("tbl_armazenagem", "ID_Meio", "tbl_meios", "ID_Meio"), ("tbl_armazenagem", "ID_Ponto_Ronda", "tbl_pontos", "ID_Ponto"),
    ("tbl_obrigacoes", "ID_Legal", "tbl_legal", "ID_Legal"), ("tbl_registo_formacao", "ID_Formacao", "tbl_formacoes", "ID_Formacao"),
    ("tbl_pestel", "IDs_Risco_SGI", "tbRiscos|tbOportunidades", "ID|ID"), ("tbl_swot", "IDs_Risco_SGI", "tbRiscos|tbOportunidades", "ID|ID"),
    ("tbl_tows", "IDs_Risco_SGI", "tbRiscos|tbOportunidades", "ID|ID"), ("tbl_cinco_forcas", "IDs_Risco_SGI", "tbRiscos|tbOportunidades", "ID|ID"),
    ("tbl_partes_interessadas", "IDs_Risco_SGI", "tbRiscos|tbOportunidades", "ID|ID"),
    ("tbl_componentes", "ID_Quimico", "tbl_quimicos", "ID_Quimico"), ("tbl_fds", "ID_Quimico", "tbl_quimicos", "ID_Quimico"),
    ("tbl_ce_reach", "ID_Quimico", "tbl_quimicos", "ID_Quimico"), ("tbl_risco_quimico", "ID_Quimico", "tbl_quimicos", "ID_Quimico"),
    ("tbl_risco_quimico", "ID_Medicao", "tbl_medicoes_vle", "ID_Medicao"),
]



# Matriz de fonte única: cada assunto é registado num só ficheiro (dono); os outros só guardam IDs de ligação ou mostram valores gerados.
FONTE_UNICA = [
    # (assunto, registo dono, tabela(s) dona(s), quem só referencia (por ID / valor gerado), regra)
    ("Contexto externo e interno do SGA e do SGI (PESTEL, SWOT, TOWS, 5 forças)", "RG-SGA-01", "tbl_pestel; tbl_swot; tbl_tows; tbl_cinco_forcas", "RG-SGA-17 (IDs_Contexto); RG-SGA-02 (IDs R/O ligados pela coluna IDs_Risco_SGI)", "Contexto do RG-SGA-02 consolidado aqui em 24/09/2026 (backup em _backup/)"),
    ("Partes interessadas e obrigações que delas resultam", "RG-SGA-01", "tbl_partes_interessadas", "RG-SGA-17 tbl_dma_consultas (contributos); RG-SGA-02 (lista de validação Critérios!T71)", "As consultas da DMA são registos de participação; a lista do RG-SGA-02 é só validação"),
    ("Riscos e oportunidades (e política/apetite ao risco)", "RG-SGA-02", "tbRiscos; tbOportunidades; Politica_Apetite", "RG-SGA-01/03/17/18 (ID_RO, IDs_Risco_SGI)", "Registo corporativo mantido à mão (editar no Excel)"),
    ("Aspetos e impactes ambientais", "RG-SGA-03", "tbl_aspetos", "RG-SGA-04/08/10/11/12/13/17/18/21 (IDs_Aspetos)", ""),
    ("Requisitos legais (nível diploma) e avaliação da conformidade", "RG-SGA-04", "tbl_legal; tbl_hist_conformidade", "RG-SGA-20 tbl_requisitos_emb; RG-SGA-21 tbl_requisitos_quimicos (detalhe por artigo, ligado por ID_Legal)", "O estado da conformidade do diploma decide-se só no RG-SGA-04"),
    ("Calendário de obrigações legais recorrentes", "RG-SGA-04", "tbl_obrigacoes", "RG-SGA-21 (antes Calendario)", "Um só calendário (inclui químicos: OBR-11, OBR-19 a OBR-30)"),
    ("Requisitos de produto (embalagens: PPWR, FCM, REACH art. 33.º, SCIP)", "RG-SGA-20", "tbl_requisitos_emb; tbl_familias_ppwr", "RG-SGA-21 (declarações de fornecedores)", "SVHC nas embalagens decidido por família PPWR"),
    ("Requisitos de químicos usados na fábrica (REACH utilizador, CLP, SST, Seveso)", "RG-SGA-21", "tbl_requisitos_quimicos", "RG-SGA-04 LEG-06, LEG-22", ""),
    ("Objetivos e catálogo de KPI", "RG-SGA-05", "tbl_objetivos; tbl_kpi", "RG-SGA-13 (ID_KPI); RG-SGA-17 (ID_KPI)", ""),
    ("Plano de ações (corretivas, preventivas e de melhoria)", "RG-SGA-06", "tbl_pam", "RG-SGA-02 (Cód. PAM); RG-SGA-03/04/07/12/13/15/16/17/20/21 (ID_PAM)", "Uma ação ambiental só existe no PAM; o RG-SGA-02 guarda o Cód. PAM (planos PAC ambientais removidos)"),
    ("Não conformidades e incidentes", "RG-SGA-07", "tbl_nc; tbl_incidentes", "RG-SGA-09/10/14 (ID_NC, ID_Incidente)", ""),
    ("Competências e formação (por colaborador)", "RG-SGA-08", "tbl_formacoes; tbl_registo_formacao", "RG-SGA-21 (FOR-13 a FOR-15)", "Inclui formação legal de químicos (diisocianatos, CMR, ADR)"),
    ("Documentos controlados", "RG-SGA-09", "tbl_lista_mestra", "SGA-00 tbl_ficheiros (catálogo técnico)", ""),
    ("Inspeções de rondas (incl. locais de químicos)", "RG-SGA-10", "tbl_pontos; tbl_execucao_rondas", "RG-SGA-21 tbl_armazenagem (ID_Ponto_Ronda)", ""),
    ("Fornecedores (todos, incl. químicos)", "RG-SGA-11", "tbl_fornecedores; tbl_outros_fornecedores", "RG-SGA-19/20/21 (ID_Fornecedor)", "Nomes noutros registos são informativos"),
    ("Meios de emergência (kits, válvula, bacia)", "RG-SGA-12", "tbl_meios", "RG-SGA-21 tbl_armazenagem (ID_Meio)", ""),
    ("Dados ambientais mensais (energia, água, resíduos, solvente) e KPI mensais", "RG-SGA-13", "tbl_dados_ambientais; tbl_residuos; Indicadores_Mensais", "RG-SGA-16/17/19 (valores anuais gerados)", ""),
    ("Fatores de emissão e inventário de GEE", "RG-SGA-19", "tbl_fatores_emissao; tbl_inventario_gee", "RG-SGA-13 (cópias FE_ELET/GWP_R410A, marcadas); RG-SGA-16 EMAS-06; RG-SGA-17 EVI (valores gerados)", "EMAS-06 = âmbitos 1 + 2 LB do inventário"),
    ("Inventário de produtos químicos, FDS, SVHC e risco químico", "RG-SGA-21", "tbl_quimicos; tbl_fds; tbl_declaracoes; tbl_risco_quimico", "RG-SGA-19 ESG-E15; RG-SGA-20 (SVHC por família)", "Antes duplicado em RG-SGA-19 tbl_substancias (removida)"),
    ("Balanço de COV (solventes)", "RG-SGA-21", "tbl_quimicos (Teor_COV, COV_kg_ano)", "RG-SGA-16 EMAS-06b; RG-SGA-19 ESG-E12; RG-SGA-17 EVI (valores gerados)", "Antes: 'solvente + 40% das tintas' em 3 registos"),
    ("Auditorias internas do SGA", "RG-SGA-14", "tbl_programa_auditorias; tbl_constatacoes", "RG-SGA-06 (ID_PAM)", "As auditorias do SGI no RG-SGA-02 usam AUD-SGI-aaaa-nn (sem colisão de IDs)"),
    ("Alterações (gestão de mudanças)", "RG-SGA-18", "tbl_alteracoes", "RG-SGA-21 (aprovação de novos químicos abre alteração)", ""),
]


def load_tables(folder):
    """Lê todas as tabelas Excel (ListObjects) de todos os ficheiros com valores calculados."""
    out, cat = {}, []
    for f in sorted(glob.glob(os.path.join(folder, "SGA-[0-9][0-9]_*.xlsx"))):
        if os.path.basename(f).startswith("SGA-00"):
            continue
        wb = openpyxl.load_workbook(f, data_only=True)
        for ws in wb.worksheets:
            for name, t in ws.tables.items():
                ref = t.ref if hasattr(t, "ref") else t
                rows = list(ws[ref])
                hdr = [c.value for c in rows[0]]
                data = [[c.value for c in r] for r in rows[1:]]
                df = pd.DataFrame(data, columns=hdr)
                out[name] = df
                hr = rows[0][0].row
                cat.append(dict(Ficheiro=os.path.basename(f), Folha=ws.title, Tabela=name, Linha_Cabecalho=hr, N_Linhas=len(df), N_Colunas=len(hdr),
                                Chave_Primaria=hdr[0], Leitura_pandas=f'pd.read_excel("{os.path.basename(f)}", sheet_name="{ws.title}", header={hr - 1})'))
    return out, cat


def split_ids(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return []
    return [x.strip() for x in re.split(r"[;,]", str(v)) if x.strip() and x.strip() not in ("—", "-")]


def integridade(T):
    res = []
    for src, colname, dst, dcol in REL:
        if src not in T:
            continue
        valid = set()
        for tt, cc in zip(dst.split("|"), dcol.split("|")):
            if tt in T:
                valid |= set(T[tt][cc].dropna().astype(str))
        refs = [i for v in T[src][colname] for i in split_ids(v)]
        refs = [r for r in refs if re.match(r"^(RO|SWT|PES|LEG|AA|OBJ|PAM|MED|NC|KPI|DM|IRO|INC|EMG|FE|EU-ENV|FCM|COS|PHAR|ISO|PT|FAM|SUP|QUI|MVLE|PQ|TOR|MAN|KIT|TMP|RON|FOR)-", r) or re.match(r"^[RO]\d+$", r)]
        missing = sorted({r for r in refs if r not in valid})
        res.append(dict(Tabela_Origem=src, Coluna=colname, Tabela_Destino=dst.replace("|", " / "), N_Referencias=len(refs),
                        N_Invalidas=len(missing), IDs_Invalidos="; ".join(missing) or None, Resultado="OK" if not missing else "Rever"))
    return res


def build(out, folder):
    T, cat = load_tables(folder)
    b = Book("RG-SGA-00", "Índice do SGA e Modelo de Dados",
             activities="Índice de todas as atividades (Módulos 3 a 6) e dos ficheiros onde estão.",
             clauses="7.5 Informação documentada (lista de registos); 9.1.1 (dados para análise)",
             purpose="Ponto de entrada do sistema de registos do SGA da Plasticom: onde está cada atividade, que tabelas existem, como se ligam (chaves), dimensões partilhadas e verificação automática da integridade referencial entre ficheiros — base para Power BI, análises estatísticas, previsão e machine learning.")
    fcols = [col("Ficheiro", 46, desc="Nome do ficheiro."), col("Codigo", 11, desc="Código do registo.", key="PK"), col("Conteudo", 50, desc="Conteúdo."),
             col("Atividades", 22, desc="Atividades do curso."), col("Clausulas", 14, desc="Cláusulas ISO 14001:2026.")]
    b.table("Ficheiros", "tbl_ficheiros", fcols, [dict(zip([c["name"] for c in fcols], f)) for f in FILES], "Lista de ficheiros do sistema de registos do SGA.",
            title="ÍNDICE DO SISTEMA DE REGISTOS DO SGA — PLASTICOM (ISO 14001:2026)", subtitle="Pasta Registos_SGA_Plasticom · 20 registos Excel + Documentos_SGA_Plasticom (manual, 15 procedimentos, plano climático, 2 instruções) + 1 documento Word · Data de referência 31/12/2026 (fecho do ano)", row_height=30)
    mcols = [col("Atividade", 9, desc="Atividade do curso.", key="PK"), col("Titulo", 36, desc="Título."), col("Ficheiro", 20, desc="Ficheiro(s)."), col("Onde_Ver", 70, desc="Folha(s) a abrir.")]
    b.table("Mapa_Atividades", "tbl_mapa_atividades", mcols, [dict(zip([c["name"] for c in mcols], m)) for m in MAPA], "Onde encontrar a resposta a cada atividade.", row_height=30)
    ccols = [col("Ficheiro", 40, desc="Ficheiro."), col("Folha", 26, desc="Folha."), col("Tabela", 26, desc="Nome da tabela Excel.", key="PK"),
             col("Linha_Cabecalho", 9, "int", desc="Linha do cabeçalho."), col("N_Linhas", 8, "int", desc="N.º de registos."), col("N_Colunas", 8, "int", desc="N.º de colunas."),
             col("Chave_Primaria", 18, desc="Primeira coluna (chave)."), col("Leitura_pandas", 80, desc="Código para ler a tabela em Python.")]
    b.table("Catalogo_Tabelas", "tbl_catalogo", ccols, cat, "Catálogo de todas as tabelas de dados (gerado automaticamente a partir dos ficheiros).")
    rcols = [col("Tabela_Origem", 22, desc="Tabela com a chave estrangeira."), col("Coluna", 18, desc="Coluna FK (pode ter vários IDs separados por ';')."),
             col("Tabela_Destino", 40, desc="Tabela referenciada."), col("N_Referencias", 10, "int", desc="N.º de referências verificadas."),
             col("N_Invalidas", 9, "int", desc="Referências sem correspondência."), col("IDs_Invalidos", 40, desc="IDs em falta.", req=False),
             col("Resultado", 9, desc="OK / Rever.")]
    b.table("Integridade_Referencial", "tbl_integridade", rcols, integridade(T),
            "Verificação das relações entre ficheiros (instantâneo gerado na construção, 31/12/2026).", cf=[("Resultado", {"Rever": "red", "OK": "green"})])
    b.table("Dim_Processo", "tbl_dim_processo", [col("Codigo", 9, desc="Código.", key="PK"), col("Processo", 56, desc="Processo."), col("Tipo", 12, desc="Tipo."),
                                                  col("Maquinas_Dataset", 26, desc="Máquinas do dataset."), col("Fase_Ciclo_Vida", 18, desc="Fase principal.")],
            [dict(Codigo=a, Processo=p, Tipo=t, Maquinas_Dataset=m, Fase_Ciclo_Vida=f) for a, p, t, m, f in PROCESSOS], "Dimensão processo (usada em todos os registos).")
    b.table("Dim_Funcao", "tbl_dim_funcao", [col("ID_Funcao", 9, desc="ID.", key="PK"), col("Funcao", 46, desc="Função."), col("Area", 8, desc="Área.")],
            [dict(ID_Funcao=a, Funcao=f, Area=r) for a, f, r in FUNCOES], "Dimensão função/responsável.")
    b.table("Dim_Clausula_ISO14001_2026", "tbl_dim_clausula", [col("Clausula", 9, desc="Cláusula.", key="PK"), col("Titulo", 100, desc="Título (ISO 14001:2026).")],
            [dict(Clausula=a, Titulo=t) for a, t in CLAUSULAS], "Dimensão cláusulas da ISO 14001:2026 (estrutura harmonizada).")
    b.table("Matriz_Fonte_Unica", "tbl_fonte_unica",
            [col("Assunto", 44, key="PK"), col("Registo_Dono", 11, desc="Único ficheiro onde o assunto é registado."), col("Tabelas_Donas", 36),
             col("So_Referenciado_Em", 50, desc="Onde aparece só por ID ou valor gerado (não se escreve lá)."), col("Regra_Nota", 46, req=False)],
            [dict(zip(["Assunto", "Registo_Dono", "Tabelas_Donas", "So_Referenciado_Em", "Regra_Nota"], f)) for f in FONTE_UNICA],
            "Matriz de fonte única: em que ficheiro se regista cada assunto (evita registos repetidos em ficheiros diferentes).",
            title="MATRIZ DE FONTE ÚNICA — ONDE SE REGISTA CADA ASSUNTO",
            subtitle="Regra: escrever só no registo dono; nos outros, apenas o ID de ligação · Revisão de redundâncias de 24/09/2026", row_height=36)
    sga_requisitos.matriz(b)
    ws = b.sheet("Modelo_Dados", "Descrição do modelo de dados (estrela) e convenções de IDs.")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 110
    ws["A1"] = "MODELO DE DADOS DO SGA"
    ws["A1"].font = F_TITLE
    lines = [
        ("Estrutura", "Modelo em estrela: tabelas de factos (dados ambientais mensais, resíduos, rondas, formação, pesagens, avaliações de fornecedores, histórico de conformidade) ligadas a dimensões partilhadas (mês, processo, função, cláusula, aspeto, KPI) e a registos de gestão (riscos, objetivos, PAM, NC, auditorias, decisões) por IDs estáveis."),
        ("Convenção de IDs", "SWT/PES (contexto) · RO (riscos/oportunidades) · AA (aspetos) · IMP (impactes) · LEG/OBR (legal) · OBJ/KPI/POL (objetivos) · PAM-AA-nn (ações) · NC-SGA-AA-nn (não conformidades) · COMP/FOR/RF (competências) · COM/DOC (comunicação/documentos) · RON/RND (rondas) · SUP/CRIT (fornecedores) · EMG/KIT/SIM (emergências) · MED/EQP (monitorização) · AUD/CONST (auditoria) · RG-AA-Dnn (decisões) · KZ/EMAS (melhoria)."),
        ("Ligação à fábrica", "Máquinas (IM-/ISBM-/SS-/HF-), operadores (OP-*), fornecedores (SUP-*), produtos e clientes usam os mesmos IDs do dataset em datasets/ — permite cruzar dados ambientais com produção, qualidade, OEE e manutenção."),
        ("Casos de ML sugeridos", "1) Previsão mensal de kWh e m³ com produção, horas de marcha e temperatura (regressão / séries temporais). 2) Deteção de anomalias em KPI (ex.: desvio do solvente). 3) Classificação da probabilidade de não conformidade numa ronda (tbl_execucao_rondas.NC_Flag) por ponto, turno e mês. 4) Tempo até fecho de NC/ações (análise de sobrevivência). 5) Pontuação de risco de fornecedores."),
        ("Leitura em lote", "for f in glob('Registos_SGA_Plasticom/SGA-*.xlsx'): usar openpyxl ws.tables para obter o intervalo de cada tabela, ou a coluna Leitura_pandas do Catalogo_Tabelas."),
        ("Atualização", "Os ficheiros são gerados por scripts em _build/ (python build_NN_*.py) e recalculados no Excel (recalc.py). Os registos podem ser editados diretamente no Excel; as colunas calculadas atualizam-se sozinhas."),
    ]
    for k, (a, t) in enumerate(lines):
        form_block(ws, 3 + k, a, t, vw=1, height=60)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1], sys.argv[2]))
