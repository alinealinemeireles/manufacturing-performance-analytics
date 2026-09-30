import datetime as dt
from sgalib import *
from dims import *
import build_20_reciclabilidade as R20

DAV = dt.date(2026, 9, 10)   # ciclo de avaliação da conformidade 2026
# Fecho do ano (31/12/2026): reavaliações do 4.º trimestre — (evidência, tipo, data da evidência, estado, data da avaliação)
FECHO_LEG = {
    "LEG-03": ("Boletim de análise n.º 26/2410 (laboratório acreditado, 10/12/2026): pH 7,6; CQO 132 mg/L O2; SST 31 mg/L — todos abaixo do VLE municipal (2.º semestre).",
               "Relatório de ensaio", "2026-12-10", "C", "2026-12-14"),
    "LEG-05": ("Relatório AC-2026-112 (28/10/2026, laboratório acreditado): critério de incomodidade noturno cumprido nos 3 recetores após barreira acústica e redução de rotação noturna dos compressores (PAM-26-03).",
               "Relatório de ensaio", "2026-10-28", "C", "2026-11-05"),
    "LEG-07": ("Relatórios de controlo de fugas de 05/2026 e 18/11/2026 (sem fugas), assinados por técnico certificado.", "Relatório / registo", "2026-11-18", "C", "2026-11-20"),
    "LEG-09": ("Em 22/12/2026: documentação técnica e declaração UE de conformidade concluídas para 17 de 22 famílias (77%); as 5 restantes (PP-PG e PET-PG farmacêuticas; PETG e PVC em substituição — PAM-26-22) em 2027.",
               "Registo / dossier", "2026-12-22", "NC", "2026-12-22"),
    "LEG-10": ("Autoavaliação Operation Clean Sweep de 15/12/2026: 11 de 14 pontos críticos com contenção (79%); filtros em todas as sarjetas.", "Registo / autoavaliação", "2026-12-15", "Futuro", "2026-12-15"),
    "LEG-11": ("Simulacros de 26/11/2026 (derrame no armazém de químicos) e 11/12/2026 (incêndio com retenção das águas): evacuação em 5 min; VC-01 fechada em 4 min.",
               "Registo / relatório", "2026-12-11", "C", "2026-12-11"),
    "LEG-13": ("Conferência de novembro/2026: 31 e-GAR emitidas, 31 com receção confirmada (100%).", "Plataforma / comprovativo", "2026-12-03", "C", "2026-12-03"),
    "LEG-15": ("Boletim L26-1207 (07/12/2026): Legionella spp. < 100 UFC/L (limiar de ação 1.000); limpeza e desinfeção semestral a 20/10/2026.", "Relatório de ensaio", "2026-12-07", "C", "2026-12-08"),
    "LEG-18": ("Alegações proibidas retiradas do site e do catálogo a 29/09/2026 (PAM-26-27); formação da equipa comercial a 15/10/2026.", "Registo / relatório", "2026-10-15", "Futuro", "2026-10-15"),
    "LEG-19": ("Declarações de utilização recebidas a 04/12/2026 (PAM-26-26): CUST-015/016 não usam os frascos para bebidas — requisito não aplicável aos SKUs atuais.",
               "Análise documental", "2026-12-04", "C", "2026-12-04"),
    "LEG-21": ("Controlo de 18/12/2026 (PAM-26-25): certificados EN 15343 válidos para 100% dos lotes de PCR em uso; CERT-03 substituído.", "Registo / dossier", "2026-12-18", "C", "2026-12-18"),
}
d = dt.date.fromisoformat

# (ID, Codigo_Tema, Tema, Diploma, Tipo, Data_Pub, Ambito, Entidade, Resumo, Aplicab, Justif, Processos, Aspetos,
#  Disposicoes, Evidencia, Tipo_Evid, Data_Evid, Estado, Periodicidade, ID_PAM, Responsavel, Fonte)
LEG = [
    ("LEG-01", "RES", "Resíduos industriais", "Decreto-Lei n.º 102-D/2020, de 10 de dezembro (RGGR)", "Decreto-Lei", "2020-12-10", "Nacional", "APA / IGAMAOT",
     "Separar na origem, armazenar em condições adequadas, classificar pela Lista Europeia de Resíduos (LER), encaminhar para operadores licenciados e submeter o MIRR anual no SILiAmb até 31 de março.",
     "Sim", "Produtor de resíduos não urbanos com mais de 10 trabalhadores e resíduos perigosos.", "PRS; SER; MAN; INJ; SOP", "AA-004; AA-008; AA-011; AA-016; AA-026; AA-029",
     "Parque de resíduos com contentores identificados por código LER; balança de plataforma verificada; contratos com 7 operadores licenciados.",
     "Submissão do MIRR 2025 no SILiAmb em 18/03/2026 (comprovativo n.º MIRR-2025-PLA-0417). Amostra de 20 e-GAR de jan–ago/2026: 100% com operador licenciado e código LER coerente com a pesagem interna.",
     "Plataforma / comprovativo", "2026-03-18", "C", 12, "", "Gestor do SGA / EHS (Responsável Ambiental)", "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2020-150908020"),
    ("LEG-02", "LIC", "Licenciamento industrial", "Decreto-Lei n.º 169/2012, de 1 de agosto (SIR), republicado pelo DL 73/2015", "Decreto-Lei", "2012-08-01", "Nacional", "IAPMEI / CCDR Centro",
     "Explorar o estabelecimento industrial com título válido e comunicar alterações que modifiquem a tipologia ou as condições de exploração.",
     "Sim", "Estabelecimento industrial do tipo 2 (transformação de matérias plásticas).", "GER", "",
     "Título Digital de Exploração arquivado; controlo de mudanças avalia alterações de layout e equipamento.",
     "Título Digital de Exploração n.º TDE-2019-0588 válido; comunicação da instalação dos novos compressores submetida em 04/02/2026 (sem alteração de tipologia).",
     "Licença / título", "2026-02-04", "C", 12, "", "Diretor Industrial", "Portal ePortugal / SIR"),
    ("LEG-03", "AGU", "Água e águas residuais", "Lei n.º 58/2005 (Lei da Água); Regulamento Municipal de Drenagem de Águas Residuais (Marinha Grande)", "Lei / Regulamento", "2005-12-29", "Nacional / Municipal", "Entidade gestora municipal / APA",
     "Descarregar águas residuais industriais no coletor apenas com autorização e dentro dos valores-limite do regulamento municipal; realizar autocontrolo analítico semestral.",
     "Sim", "Descarga da purga da torre de arrefecimento e águas domésticas no coletor municipal.", "UTL; GER", "AA-023; AA-024; AA-035",
     "Autorização de descarga n.º AD-112/2021; ponto de amostragem na caixa de visita final; dosagem automática de biocida.",
     "Boletim de análise n.º 26/1187 (laboratório acreditado, 12/06/2026): pH 7,8; CQO 145 mg/L O2 (VLE 1.000); SST 38 mg/L (VLE 1.000) — todos os parâmetros abaixo do VLE municipal.",
     "Relatório de ensaio", "2026-06-12", "C", 6, "", "Gerente de Manutenção", "Regulamento municipal / Diário da República"),
    ("LEG-04", "COV", "Ar — COV (solventes)", "Decreto-Lei n.º 127/2013, de 30 de agosto — Capítulo V e Anexo VII (instalações que utilizam solventes orgânicos)", "Decreto-Lei", "2013-08-30", "Nacional", "APA / CCDR Centro",
     "Instalações acima do limiar de consumo de solventes (ex.: 5 t/ano para revestimento de plástico; 15 t/ano para impressão) têm VLE, plano de gestão de solventes e registo. Abaixo do limiar: demonstrar anualmente o consumo.",
     "Não", "Consumo anual de solventes ≈ 1,2 t (limpeza + fração solvente das tintas) < 5 t/ano. Manter o cálculo anual para confirmar a não aplicabilidade.", "SER", "AA-014; AA-006",
     "Balanço anual de solventes a partir do inventário (compras − stock).",
     "Balanço de solventes set/2025–ago/2026: 0,75 t de solvente de limpeza + ≈ 0,43 t na fração solvente das tintas = ≈ 1,2 t/ano (24% do limiar). Registo BAL-SOLV-2026 arquivado.",
     "Registo / cálculo", "2026-09-05", "C", 12, "", "Gestor do SGA / EHS (Responsável Ambiental)", "Diário da República — DL 127/2013"),
    ("LEG-05", "RUI", "Ruído ambiente", "Decreto-Lei n.º 9/2007, de 17 de janeiro (Regulamento Geral do Ruído)", "Decreto-Lei", "2007-01-17", "Nacional", "Câmara Municipal / IGAMAOT",
     "Cumprir o critério de exposição máxima e o critério de incomodidade junto dos recetores sensíveis; avaliar após alterações que possam aumentar o ruído.",
     "Sim", "Habitações a ≈ 250 m; laboração em 3 turnos (período noturno).", "UTL", "AA-022",
     "Compressores em sala fechada; última avaliação acústica em 2023, antes da substituição dos compressores (fev/2026).",
     "Não existe avaliação acústica posterior à instalação dos compressores CMP-01/02 (fev/2026). Relatório AC-2023-041 (09/2023) já não representa as condições atuais de funcionamento noturno.",
     "Relatório de ensaio", "2023-09-14", "NC", 36, "PAM-26-03", "Gestor do SGA / EHS (Responsável Ambiental)", "https://diariodarepublica.pt/dr/detalhe/decreto-lei/9-2007-522807"),
    ("LEG-06", "QUI", "Produtos químicos", "Regulamento (CE) n.º 1907/2006 (REACH) e Regulamento (CE) n.º 1272/2008 (CLP)", "Regulamento UE", "2006-12-18", "UE", "IGAMAOT / ACT",
     "Dispor de fichas de dados de segurança (FDS) atualizadas no ponto de uso, recipientes rotulados, e cumprir as condições de utilização segura e de armazenagem.",
     "Sim", "Utilizador a jusante de tintas, solventes, óleos e biocidas.", "ARQ; SER; UTL; MAN", "AA-005; AA-006; AA-015; AA-017",
     "Registo integrado RG-SGA-21 (inventário de 42 produtos, FDS, cenários de exposição, importação, SVHC, risco químico) e procedimento PR-SGA-16; dossier de FDS no armazém e junto às máquinas; armário de inflamáveis.",
     "Avaliação completa de 24/09/2026 (RG-SGA-21): rotulagem CLP 100% conforme (15 recipientes); FDS em vigor 85% conformes (6 a pedir ao fornecedor, 2 de 2021 pedidas em 03/09/2026); 2 cenários de exposição com o prazo de 12 meses do art. 39.º ultrapassado (CE-02, CE-08); 2 fornecedores extra-UE sem representante único (Plasticom = importador sem registo — SUP-004, SUP-005); tinta UV com fotoiniciador Repr. 1B/SVHC; 2 operadores sem formação em diisocianatos (entrada 74).",
     "Inspeção / registo", "2026-09-24", "NC", 12, "PAM-26-28", "Responsável de Armazém e Logística", "https://eur-lex.europa.eu/eli/reg/2006/1907/oj"),
    ("LEG-07", "FGA", "Gases fluorados", "Regulamento (UE) 2024/573 (gases fluorados) e Decreto-Lei n.º 145/2017", "Regulamento UE", "2024-02-07", "UE / Nacional", "APA / IGAMAOT",
     "Controlo de fugas periódico conforme a carga em tCO2e, por técnico certificado; registos do equipamento; reparação e reposição documentadas; comunicação anual quando aplicável.",
     "Sim", "Chiller CH-01 com 30 kg de R410A (≈ 62,6 tCO2e → controlo de fugas semestral).", "UTL", "AA-025",
     "Contrato de manutenção com empresa certificada; registo do equipamento CH-01.",
     "Relatórios de controlo de fugas de 11/2025 (fuga de 3,2 kg detetada e reparada) e de 05/2026 (sem fugas), assinados por técnico certificado; registo do equipamento atualizado.",
     "Registo / relatório", "2026-05-20", "C", 6, "", "Gerente de Manutenção", "https://eur-lex.europa.eu/eli/reg/2024/573/oj"),
    ("LEG-08", "ENE", "Energia", "Decreto-Lei n.º 71/2008, de 15 de abril (SGCIE — consumidores intensivos de energia)", "Decreto-Lei", "2008-04-15", "Nacional", "DGEG / ADENE",
     "Instalações com consumo ≥ 500 tep/ano: registo, auditoria energética periódica e Plano de Racionalização do Consumo de Energia (PREn) com metas de intensidade energética e relatórios de execução.",
     "Sim", "Consumo ≈ 7,8 GWh em 2026 ≈ 1.680 tep/ano (fator 0,215 tep/MWh).", "INJ; SOP; UTL; GER", "AA-007; AA-010; AA-021; AA-030",
     "Registo SGCIE; auditoria energética de 2022; ARCE com metas até 2029.",
     "Relatório de execução e progresso do ARCE (2024–2025) submetido na plataforma SGCIE em 28/04/2026; auditoria energética de 2022 válida até 2030.",
     "Plataforma / comprovativo", "2026-04-28", "C", 24, "", "Gerente de Manutenção", "Diário da República — DL 71/2008"),
    ("LEG-09", "EMB", "Embalagens (produto)", "Regulamento (UE) 2025/40 (PPWR) — aplicável desde 12/08/2026", "Regulamento UE", "2025-01-22", "UE", "APA / ASAE",
     "Fabricante de embalagens: avaliação da conformidade, documentação técnica e declaração UE de conformidade; limites de chumbo, cádmio, mercúrio e crómio VI; restrições a substâncias preocupantes; preparação para metas de reciclabilidade e conteúdo reciclado.",
     "Sim", "A Plasticom fabrica embalagens colocadas no mercado da UE (cosmética, alimentar, farmacêutica).", "RD; LAB", "AA-037; AA-038; AA-043",
     "Fichas técnicas de produto; declarações de contacto alimentar (linha alimentar); análise de metais pesados por família.",
     "Em 10/09/2026: documentação técnica e declaração UE de conformidade concluídas para 9 de 22 famílias (41%). Relatório de metais pesados RM-2026-07 (< 100 mg/kg) só cobre as famílias HDPE.",
     "Registo / dossier", "2026-09-10", "NC", 6, "PAM-26-10", "Responsável de R&D", "https://eur-lex.europa.eu/eli/reg/2025/40/oj"),
    ("LEG-10", "GRA", "Perdas de granulado", "Regulamento (UE) 2025/2365 (prevenção de perdas de granulados de plástico) e REACH anexo XVII, entrada 78 (Reg. (UE) 2023/2055 — relatório anual de microplásticos)", "Regulamento UE", "", "UE", "APA",
     "Evitar perdas de granulado com a hierarquia de medidas e notificar cada instalação à autoridade até 17/12/2027; instalações < 1.500 t/ano: declaração de conformidade (certificação por terceiros só ≥ 1.500 t/ano); relatório anual à ECHA das libertações estimadas até 31/05 (entrada 78).",
     "Futuro", "A Plasticom manipula ≈ 865 t/ano de granulado (< 1.500 t): notificação e declaração de conformidade até 17/12/2027; o relatório de microplásticos já é exigível (submetido em 28/05/2026).", "REC; INJ; SOP; MOA", "AA-003",
     "Varrimento diário; programa OCS em implementação (PAM-26-11).",
     "Autoavaliação Operation Clean Sweep de 30/06/2026: 6 de 14 pontos críticos com contenção (43%). Plano de ação aprovado.",
     "Registo / autoavaliação", "2026-06-30", "Futuro", 6, "PAM-26-11", "Gestor do SGA / EHS (Responsável Ambiental)", "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202502365"),
    ("LEG-11", "SCI", "Emergência / segurança contra incêndio", "Decreto-Lei n.º 220/2008, de 12 de novembro (RJ-SCIE) e Portaria n.º 1532/2008", "Decreto-Lei", "2008-11-12", "Nacional", "ANEPC",
     "Implementar medidas de autoproteção, manter meios de 1.ª intervenção, formação e simulacros com a periodicidade da categoria de risco.",
     "Sim", "Utilização-tipo XII (industrial), 2.ª categoria de risco.", "GER; REC; ARQ", "AA-034; AA-005",
     "Medidas de autoproteção aprovadas; extintores e RIA com manutenção anual; válvula de corte na rede pluvial.",
     "Relatório do simulacro de 14/11/2025 (incêndio no armazém de MP): evacuação em 6 min; válvula de corte pluvial fechada em 9 min (meta ≤ 5 min → ação de melhoria). Manutenção de extintores de 03/2026.",
     "Relatório / registo", "2025-11-14", "C", 12, "", "Diretor Industrial", "Diário da República — DL 220/2008"),
    ("LEG-12", "EAR", "Ar — fontes pontuais", "Decreto-Lei n.º 39/2018, de 11 de junho (prevenção e controlo das emissões para o ar)", "Decreto-Lei", "2018-06-11", "Nacional", "CCDR Centro",
     "Fontes pontuais: chaminé com tomas de amostragem normalizadas, altura adequada e monitorização pontual conforme o caudal mássico; comunicação dos resultados.",
     "Sim", "Chaminé da estufa de cura da serigrafia (FP1).", "SER", "AA-014",
     "Chaminé FP1 com tomas de amostragem normalizadas; exaustão localizada nas máquinas de serigrafia.",
     "Relatório de ensaio n.º 2026/03-EF (laboratório acreditado, 18/03/2026): COVT 22 mg C/Nm³, caudal mássico 0,04 kg C/h — abaixo do limiar mássico; próxima monitorização em 2029.",
     "Relatório de ensaio", "2026-03-18", "C", 36, "", "Gestor do SGA / EHS (Responsável Ambiental)", "Diário da República — DL 39/2018"),
    ("LEG-13", "RES", "Transporte de resíduos", "Portaria n.º 145/2017, de 26 de abril (guias eletrónicas e-GAR)", "Portaria", "2017-04-26", "Nacional", "APA / GNR-SEPNA",
     "Emitir e-GAR antes de cada transporte de resíduos e confirmar a receção pelo destinatário no SILiAmb.",
     "Sim", "Todos os envios de resíduos da Plasticom.", "PRS", "AA-016; AA-026; AA-029",
     "Emissão de e-GAR pelo Responsável de Armazém; conferência mensal no SILiAmb.",
     "Conferência de agosto/2026: 34 e-GAR emitidas, 34 com receção confirmada pelo destinatário (100%).",
     "Plataforma / comprovativo", "2026-09-03", "C", 12, "", "Responsável de Armazém e Logística", "Diário da República — Portaria 145/2017"),
    ("LEG-14", "RAM", "Responsabilidade ambiental", "Decreto-Lei n.º 147/2008, de 29 de julho (regime de responsabilidade por danos ambientais)", "Decreto-Lei", "2008-07-29", "Nacional", "APA",
     "Operadores de atividades do Anexo III: garantia financeira obrigatória e prevenção/reparação de danos ambientais.",
     "Não", "Atividade não incluída no Anexo III (sem licença ambiental IED nem gestão de resíduos). A responsabilidade subjetiva geral mantém-se.", "GER", "",
     "Seguro de responsabilidade ambiental voluntário.",
     "Análise de aplicabilidade revista em 10/09/2026: a atividade (CAE 22220) não consta do Anexo III. Apólice voluntária RC-Ambiental n.º 55-0931 válida até 12/2026.",
     "Análise documental", "2026-09-10", "C", 12, "", "Diretor Financeiro", "Diário da República — DL 147/2008"),
    ("LEG-15", "LEG", "Legionella (torres de arrefecimento)", "Lei n.º 52/2018, de 20 de agosto (regime de prevenção e controlo da doença dos legionários)", "Lei", "2018-08-20", "Nacional", "DGS / Autoridade de saúde / IGAMAOT",
     "Plano de prevenção e controlo da Legionella para a torre; registo do equipamento; limpeza e desinfeção periódicas; monitorização de Legionella com laboratório acreditado e ação acima do limiar.",
     "Sim", "Torre de arrefecimento TR-01 (sistema de arrefecimento com aerossolização).", "UTL", "AA-023; AA-024",
     "Plano de prevenção e controlo (AquaHigiene Lda.); limpeza e desinfeção semestral; Legionella trimestral (tbl_analises do RG-SGA-13).",
     "Boletim L26-0908 (08/09/2026): Legionella spp. 100 UFC/L (limiar de ação 1.000). Excedência de 08/2025 (1.200 UFC/L) tratada com desinfeção de choque e reanálise conforme.",
     "Relatório de ensaio", "2026-09-08", "C", 3, "", "Gerente de Manutenção", "Diário da República — Lei 52/2018"),
    ("LEG-16", "RAP", "Embalagens — RAP (responsabilidade alargada do produtor)", "Decreto-Lei n.º 152-D/2017, de 11 de dezembro (UNILEX), alterado pelo DL 102-D/2020 — embalagens e resíduos de embalagens", "Decreto-Lei", "2017-12-11", "Nacional", "APA / IGAMAOT",
     "Quem coloca embalagens no mercado nacional (embalador) transfere a responsabilidade pela gestão dos resíduos para um sistema integrado (entidade gestora) ou individual, declara as quantidades e paga a prestação financeira.",
     "Sim", "A Plasticom é embaladora das embalagens de expedição (caixas, filme, paletes) enviadas a clientes em Portugal; os clientes são embaladores das embalagens que enchem (a Plasticom fornece-lhes massa e material por SKU).", "EXP; ADM", "",
     "Adesão ao sistema integrado de embalagens não urbanas (contrato NU-2021-0342); massas de expedição por mês, país e material em tbl_emb_expedicao (RG-SGA-20).",
     "Declaração anual de 2025 submetida à entidade gestora em 26/02/2026 e prestação financeira paga; massas de 2026 calculadas a partir das vendas (RG-SGA-20).",
     "Plataforma / comprovativo", "2026-02-26", "C", 12, "", "Diretor Financeiro", "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2017-114337039"),
    ("LEG-17", "FCM", "Contacto alimentar (FCM)", "Regulamentos (CE) 1935/2004 e 2023/2006 e (UE) 10/2011 e 2022/1616 — materiais plásticos em contacto com alimentos", "Regulamento UE", "2004-10-27", "UE", "ASAE / DGAV",
     "Materiais inertes nas condições de uso; boas práticas de fabrico; só substâncias da lista da União; limites de migração; declaração de conformidade (anexo IV); reciclado só de processos autorizados.",
     "Sim", "Linha alimentar (frascos FA-030/031 e tampas TA-014) em HDPE-FG e PP-FG, sem plástico reciclado.", "RD; LAB; INJ; SOP", "",
     "Declarações de conformidade (anexo IV do Reg. 10/2011), ensaios de migração, BPF no sistema de qualidade, declaração PFAS do fornecedor SUP-010.",
     "Ensaios de migração global e específica de 03/2026 (laboratório acreditado) conformes; declaração de conformidade emitida para 4 frascos e 2 tampas; declaração PFAS SUP-010 (07/2026). Falta auditoria interna específica de BPF (Reg. 2023/2006).",
     "Relatório de ensaio", "2026-03-20", "C", 12, "", "Gerente da Qualidade", "https://eur-lex.europa.eu/eli/reg/2011/10/oj"),
    ("LEG-18", "ALE", "Alegações ambientais", "Diretiva (UE) 2024/825 (capacitação dos consumidores para a transição ecológica) — aplicável a partir de 27/09/2026; confirmar a transposição nacional", "Diretiva UE", "2024-03-06", "UE / Nacional", "DGC / ASAE",
     "Proíbe alegações ambientais genéricas sem desempenho reconhecido, alegações de neutralidade baseadas em compensações e alegações sobre o produto inteiro quando só se aplicam a uma parte.",
     "Futuro", "A Plasticom comunica alegações (site, catálogo, fichas técnicas) que chegam ao consumidor através dos clientes.", "ADM; RD", "",
     "PR-SGA-14; registo de alegações tbl_alegacoes (RG-SGA-20) com evidência e estado.",
     "Revisão de 22/09/2026: 10 alegações — 4 a retirar, proibidas ou suspensas ('eco-friendly', '100% recicláveis', 'neutra em carbono' e '50% rPET' com certificado expirado); retirada até 27/09/2026 (PAM-26-27).",
     "Registo / relatório", "2026-09-22", "Futuro", 6, "PAM-26-27", "Diretor Geral (Gestão de Topo)", "https://eur-lex.europa.eu/eli/dir/2024/825/oj"),
    ("LEG-19", "SUP", "Plásticos de utilização única", "Diretiva (UE) 2019/904 (SUP) e Decreto-Lei n.º 78/2021, de 24 de setembro", "Decreto-Lei", "2021-09-24", "UE / Nacional", "APA / ASAE",
     "Recipientes para bebidas até 3 L com tampas de plástico têm de ter tampas presas; recipientes para alimentos de consumo imediato com medidas de redução e RAP.",
     "Condicional", "Só se os frascos alimentares FA-030/031 forem usados para bebidas — as tampas TA-014 teriam de ser presas (tethered).", "RD", "",
     "Pedido de declaração de utilização aos clientes CUST-015 e CUST-016.",
     "Pedido enviado em 18/09/2026; resposta pendente. Sem SKUs de garrafas de bebidas no portfólio atual.",
     "Análise documental", "2026-09-18", "Em avaliação", 6, "PAM-26-26", "Responsável de R&D", "https://eur-lex.europa.eu/eli/dir/2019/904/oj"),
    ("LEG-20", "CLI", "Outros requisitos (clientes / voluntários)", "Requisitos de clientes: acordos de qualidade farmacêuticos (Diretiva 2001/83/CE, EudraLex vol. 4, guideline EMA de materiais plásticos) e cosméticos (Reg. (CE) 1223/2009)", "Requisito de cliente", "", "Contratual", "Clientes (auditorias de fornecedor)",
     "Fornecer especificações e composição, notificar alterações de material/processo, permitir auditorias, cumprir a Farmacopeia Europeia (PP-PG, PET-PG) e as especificações de embalagem primária.",
     "Sim", "Fornecedor de acondicionamento primário a CUST-017/018 (farmacêutico) e a clientes de cosmética e higiene.", "RD; LAB; CMP", "",
     "Acordos de qualidade; controlo de alterações notificado ao cliente (RG-SGA-18); especificações aprovadas.",
     "Auditoria de CUST-017 (14/05/2026) sem NC maiores; falta a carta de acesso ao DMF do PET-PG (fornecedor SUP-009).",
     "Relatório / registo", "2026-05-14", "C", 12, "", "Gerente da Qualidade", "Contratos e acordos de qualidade"),
    ("LEG-21", "VOL", "Outros requisitos (clientes / voluntários)", "Compromissos voluntários de produto: diretrizes RecyClass (DfR), EN 15343, ISO 14021, ISO 14067, ISO 11469 (política POL-04)", "Norma voluntária", "", "Contratual", "Organismos de certificação / clientes",
     "Avaliar a reciclabilidade de todos os SKUs, comprovar o conteúdo reciclado com certificados EN 15343 e só fazer alegações comprovadas.",
     "Sim", "Compromisso da política ambiental (POL-04) e pedidos de 7 de 9 grandes clientes.", "RD; CMP; ADM", "",
     "Autoavaliação RecyClass por SKU (RG-SGA-20 tbl_recyclass); certificados dos fornecedores de PCR (tbl_certificados_pcr).",
     "__EV21__",
     "Registo / autoavaliação", "2026-09-22", "NC", 12, "PAM-26-25", "Responsável de R&D", "https://recyclass.eu"),
    ("LEG-22", "QUI", "Produtos químicos", "Decreto-Lei n.º 24/2012 (agentes químicos) e Decreto-Lei n.º 301/2000 na redação do DL 102/2024 (cancerígenos, mutagénicos e reprotóxicos) — SST integrada na gestão de químicos", "Decreto-Lei", "2012-02-06", "Nacional", "ACT",
     "Avaliar e registar o risco de todos os agentes químicos (incl. gerados no processo); cumprir VLE e medir quando necessário; substituir CMR/reprotóxicos 1A/1B; lista de trabalhadores expostos; vigilância da saúde; informação e formação.",
     "Sim", "Empregador com agentes químicos perigosos (tintas, solventes, aerossóis, biocidas) e uma tinta UV reprotóxica (Repr. 1B).", "SER; MAN; UTL; LAB; SOP", "AA-014; AA-015",
     "Avaliação de risco químico por tarefa e medições NP EN 689 no RG-SGA-21 (tbl_risco_quimico, tbl_medicoes_vle); procedimento PR-SGA-16.",
     "Avaliação de 24/09/2026 (RG-SGA-21): 21 tarefas avaliadas, 5 de prioridade P1; 5 produtos perigosos sem avaliação; lista de trabalhadores expostos a reprotóxicos inexistente (tinta UV QUI-002); medições de 11/2025 conformes na SS-002 e inconclusivas na SS-001.",
     "Registo / avaliação", "2026-09-24", "NC", 12, "PAM-26-29", "Gestor do SGA / EHS (Responsável Ambiental)", "https://diariodarepublica.pt/dr/detalhe/decreto-lei/102-2024-898867718"),
]


NAT = {k: "Obrigação legal" for k in [f"LEG-{i:02d}" for i in range(1, 19)]}
NAT.update({"LEG-19": "Necessita verificação", "LEG-20": "Requisito contratual", "LEG-21": "Norma voluntária", "LEG-22": "Obrigação legal (SST — gestão integrada de químicos)"})
PAPEL = {"LEG-01": "Produtor de resíduos", "LEG-02": "Estabelecimento industrial (tipo 2)", "LEG-03": "Utilizador do coletor municipal",
         "LEG-04": "Operador abaixo do limiar de solventes", "LEG-05": "Operador (fonte de ruído)", "LEG-06": "Utilizador a jusante de misturas; fornecedor de artigos",
         "LEG-07": "Operador de equipamento com gases fluorados", "LEG-08": "Consumidor intensivo de energia", "LEG-09": "Fabricante de embalagens e fornecedor a fabricantes de produtos embalados",
         "LEG-10": "Operador que manipula granulado", "LEG-11": "Utilização-tipo XII (industrial)", "LEG-12": "Operador de fonte pontual", "LEG-13": "Produtor/expedidor de resíduos",
         "LEG-14": "Operador fora do anexo III", "LEG-15": "Proprietário de torre de arrefecimento", "LEG-16": "Embalador (embalagens de expedição)",
         "LEG-17": "Fabricante de materiais em contacto com alimentos", "LEG-18": "Autor de comunicações comerciais", "LEG-19": "Fabricante de tampas (condicional)",
         "LEG-20": "Fornecedor de acondicionamento primário", "LEG-21": "Organização (compromisso voluntário)", "LEG-22": "Empregador (agentes químicos e CMR)"}
REQS = {"LEG-01": "EU-ENV-006; PT-002", "LEG-06": "EU-ENV-008; EU-ENV-009",
        "LEG-09": "EU-ENV-001; EU-ENV-002; EU-ENV-003; EU-ENV-004; EU-ENV-005; EU-ENV-010; EU-ENV-011; EU-ENV-013; EU-ENV-014; EU-ENV-015; PHAR-006; PT-004",
        "LEG-16": "PT-001; PT-003; EU-ENV-016", "LEG-17": "FCM-001; FCM-002; FCM-003; FCM-004; FCM-005; EU-ENV-012", "LEG-18": "EU-ENV-018; COS-005",
        "LEG-19": "EU-ENV-007; PT-006", "LEG-20": "COS-001; COS-002; COS-003; COS-004; PHAR-001; PHAR-003; PHAR-004; PHAR-005",
        "LEG-21": "ISO-001; ISO-002; ISO-003; ISO-004; ISO-007; ISO-008; ISO-009; ISO-010; ISO-011; ISO-012; ISO-013; ISO-014"}


def _ev():
    r = R20.resumo()
    ev21 = (f"Autoavaliação de 22/09/2026 (RG-SGA-20): {r['n_ac']} de {r['n_nao_isentos']} SKUs não isentos com grau PPWR indicativo A–C ({r['pct_ac_skus']:.0%}); "
            f"{r['n_F']} SKUs classe F (PVC, PETG, preto de carbono). Certificado de rPET (CERT-03) expirado em 30/06/2026.")
    ev09 = f" Autoavaliação RecyClass de 22/09/2026 (RG-SGA-20): {r['n_ac']} de {r['n_nao_isentos']} SKUs não isentos com grau indicativo A–C."
    return ev21, ev09


def build(out):
    ev21, ev09 = _ev()
    b = Book("RG-SGA-04", "Tabela de Identificação de Requisitos Legais e Avaliação da Conformidade (Mod.G.06.02)",
             activities="Atividade 3.3 — Identificação de Requisitos Legais e Avaliação da Conformidade (tabela completa; vista para print screen no formato Mod.G.06.02).",
             clauses="6.1.3 Obrigações de conformidade; 9.1.2 Avaliação da conformidade; 5.2 (compromisso de cumprir as obrigações de conformidade — ISO 14001:2026: 'meet')",
             purpose="Identificar a legislação e outros requisitos aplicáveis por tema ambiental, interpretar as obrigações, registar as disposições internas e avaliar a conformidade com evidência objetiva (documento, número, data, valor medido vs limite). Inclui calendário de obrigações recorrentes e histórico de avaliações para análise de tendência.",
             links=[("RG-SGA-03 Aspetos", "IDs_Aspetos liga cada diploma aos aspetos ambientais que regula."),
                    ("RG-SGA-06 PAM", "NC legal → ação no PAM (ID_PAM)."),
                    ("RG-SGA-07 NC", "NC legais são também registadas no registo de não conformidades.")])
    b.add_list("Tema", ["Resíduos industriais", "Transporte de resíduos", "Licenciamento industrial", "Água e águas residuais", "Ar — COV (solventes)",
                        "Ar — fontes pontuais", "Ruído ambiente", "Produtos químicos", "Gases fluorados", "Energia", "Embalagens (produto)",
                        "Perdas de granulado", "Emergência / segurança contra incêndio", "Responsabilidade ambiental", "Outros requisitos (clientes / voluntários)", "Legionella (torres de arrefecimento)",
                        "Embalagens — RAP (responsabilidade alargada do produtor)", "Contacto alimentar (FCM)", "Alegações ambientais", "Plásticos de utilização única"])
    b.add_list("TipoDiploma", ["Decreto-Lei", "Lei", "Lei / Regulamento", "Portaria", "Regulamento UE", "Diretiva UE", "Regulamento municipal", "Licença / autorização", "Requisito de cliente", "Norma voluntária"])
    b.add_list("Ambito", ["UE", "Nacional", "UE / Nacional", "Municipal", "Nacional / Municipal", "Contratual"])
    b.add_list("Aplicabilidade", ["Sim", "Não", "Futuro", "Condicional"])
    b.add_list("Natureza", ["Obrigação legal", "Norma técnica de suporte", "Requisito contratual", "Norma voluntária", "Necessita verificação"])
    b.add_list("TipoEvidencia", ["Relatório de ensaio", "Plataforma / comprovativo", "Licença / título", "Registo / relatório", "Registo / cálculo",
                                 "Registo / dossier", "Registo / autoavaliação", "Inspeção / registo", "Relatório / registo", "Análise documental"])
    b.add_list("Estado", ["C", "NC", "Futuro", "Em avaliação"])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Frequencia", ["Por ocorrência", "Mensal", "Trimestral", "Semestral", "Anual", "Bienal", "Trienal", "Quinquenal", "Octenal"])

    cols = [
        col("ID_Legal", 8, desc="Identificador do requisito.", key="PK", dom="LEG-nn"),
        col("Codigo_Tema", 8, desc="Código do tema (Mod.G.06.02 'Código / Tema')."),
        col("Tema", 22, dv="Tema", desc="Tema ambiental."),
        col("Diploma_Documento", 42, desc="N.º do diploma, ano e data."),
        col("Tipo_Diploma", 14, dv="TipoDiploma", desc="Tipo de documento legal."),
        col("Data_Publicacao", 11, "date", desc="Data de publicação.", req=False),
        col("Ambito", 12, dv="Ambito", desc="Âmbito geográfico."),
        col("Entidade_Fiscalizadora", 18, desc="Entidade competente/fiscalizadora."),
        col("Resumo_Obrigacoes", 55, desc="O que a lei obriga a fazer."),
        col("Aplicabilidade", 10, dv="Aplicabilidade", desc="Sim / Não / Futuro (aplicável a partir de data futura)."),
        col("Justificacao_Aplicabilidade", 38, desc="Porque é (ou não é) aplicável — limiares, características da instalação."),
        col("Processos", 14, desc="Processos afetados (códigos)."),
        col("IDs_Aspetos", 18, desc="Aspetos ambientais regulados.", key="FK → RG-SGA-03", req=False),
        col("Disposicoes_Internas", 44, desc="O que está instalado/implementado para cumprir."),
        col("Avaliacao_Conformidade_Evidencia", 60, desc="Frase técnica com a evidência objetiva (documento, número, data, valor vs limite)."),
        col("Tipo_Evidencia", 16, dv="TipoEvidencia", desc="Tipo de evidência."),
        col("Data_Evidencia", 11, "date", desc="Data da evidência."),
        col("Estado", 7, dv="Estado", desc="C conforme; NC não conforme; Futuro (ainda não exigível)."),
        col("Data_Avaliacao", 11, "date", desc="Data da avaliação da conformidade."),
        col("Periodicidade_Meses", 9, "int", desc="Periodicidade da avaliação (meses)."),
        col("Proxima_Avaliacao", 11, "date", f='=IF(@Data_Avaliacao@="","",EDATE(@Data_Avaliacao@,@Periodicidade_Meses@))', desc="Data da próxima avaliação."),
        col("Idade_Evidencia_Dias", 10, "int", f='=IF(@Data_Evidencia@="","",DataRef-@Data_Evidencia@)', desc="Dias desde a evidência até à data de referência (2026-12-31)."),
        col("Alerta", 22, f=('=IF(AND(@Estado@="NC",@ID_PAM@=""),"NC sem ação no PAM",IF(@Proxima_Avaliacao@<DataRef,"Avaliação vencida",'
                             'IF(@Proxima_Avaliacao@-DataRef<=60,"Avaliar nos próximos 60 dias",IF(@Estado@="NC","NC com ação em curso","OK"))))'),
            desc="Alerta automático de gestão."),
        col("ID_PAM", 10, desc="Ação no PAM quando NC.", key="FK → RG-SGA-06", req=False),
        col("Responsavel", 26, dv="Funcao", desc="Responsável pelo cumprimento."),
        col("Fonte_Oficial", 30, desc="Fonte oficial (Diário da República, EUR-Lex)."),
        col("Natureza_Obrigacao", 18, dv="Natureza", desc="Obrigação legal / norma técnica de suporte / requisito contratual / norma voluntária / necessita verificação."),
        col("Papel_Plasticom", 30, desc="Papel jurídico da Plasticom face ao requisito."),
        col("IDs_Req_Embalagem", 34, desc="Requisitos detalhados na matriz de embalagens (RG-SGA-20 tbl_requisitos_emb).", key="FK → RG-SGA-20", req=False),
    ]
    rows = []
    for t in LEG:
        (i, ct, te, dp, tp, dpub, am, en, rs, ap, ju, pr, asp, di, ev, tev, dev, es, per, pam, resp, fo) = t
        ev = ev21 if ev == "__EV21__" else (ev + ev09 if i == "LEG-09" else ev)
        dav_i = DAV
        if i in FECHO_LEG:
            ev, tev, dev, es, dav_s = FECHO_LEG[i]
            dav_i = d(dav_s)
        rows.append(dict(ID_Legal=i, Codigo_Tema=ct, Tema=te, Diploma_Documento=dp, Tipo_Diploma=tp, Data_Publicacao=d(dpub) if dpub else None,
                         Ambito=am, Entidade_Fiscalizadora=en, Resumo_Obrigacoes=rs, Aplicabilidade=ap, Justificacao_Aplicabilidade=ju,
                         Processos=pr, IDs_Aspetos=asp or None, Disposicoes_Internas=di, Avaliacao_Conformidade_Evidencia=ev,
                         Tipo_Evidencia=tev, Data_Evidencia=d(dev), Estado=es, Data_Avaliacao=dav_i, Periodicidade_Meses=per,
                         ID_PAM=pam or None, Responsavel=resp, Fonte_Oficial=fo, Natureza_Obrigacao=NAT[i], Papel_Plasticom=PAPEL[i], IDs_Req_Embalagem=REQS.get(i)))
    b.table("Requisitos_Legais", "tbl_legal", cols, rows,
            "Registo de requisitos legais e avaliação da conformidade (1 linha por diploma).",
            title="TABELA DE IDENTIFICAÇÃO DE REQUISITOS LEGAIS E AVALIAÇÃO DA CONFORMIDADE — PLASTICOM",
            subtitle="Evidência objetiva obrigatória (nunca apenas 'Cumpre') · Data de referência para alertas: 2026-12-31 (nome DataRef) · Dados de evidência simulados",
            cf=[("Estado", {"NC": "red", "Futuro": "blue", "Em avaliação": "orange", "C": "green"}),
                ("Alerta", {"NC sem": "red", "vencida": "red", "60 dias": "yellow", "em curso": "orange", "OK": "green"}),
                ("Aplicabilidade", {"Não": "gray", "Futuro": "blue"})],
            row_height=110, freeze_col=2)

    # calendário de obrigações recorrentes
    OB = [
        ("OBR-01", "LEG-01", "Submeter o MIRR do ano anterior no SILiAmb", "Anual", "2027-03-31", "2026-03-18", "Comprovativo MIRR-2025-PLA-0417", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-02", "LEG-13", "Emitir e-GAR antes de cada transporte e confirmar receção", "Por ocorrência", "2026-09-30", "2026-09-19", "e-GAR de setembro (conferência mensal)", "Responsável de Armazém e Logística"),
        ("OBR-03", "LEG-03", "Autocontrolo analítico semestral do efluente", "Semestral", "2026-12-12", "2026-06-12", "Boletim 26/1187", "Gerente de Manutenção"),
        ("OBR-04", "LEG-07", "Controlo de fugas do chiller CH-01 (≥ 50 tCO2e)", "Semestral", "2026-11-20", "2026-05-20", "Relatório de controlo de fugas 05/2026", "Gerente de Manutenção"),
        ("OBR-05", "LEG-08", "Relatório de execução e progresso do ARCE (SGCIE)", "Bienal", "2028-04-30", "2026-04-28", "Submissão SGCIE 28/04/2026", "Gerente de Manutenção"),
        ("OBR-06", "LEG-08", "Auditoria energética SGCIE", "Octenal", "2030-06-30", "2022-06-15", "Relatório de auditoria energética 2022", "Gerente de Manutenção"),
        ("OBR-07", "LEG-12", "Monitorização pontual da chaminé FP1", "Trienal", "2029-03-18", "2026-03-18", "Relatório 2026/03-EF", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-08", "LEG-05", "Avaliação acústica após alteração dos compressores", "Por ocorrência", "2026-04-30", "2023-09-14", "Relatório AC-2023-041 (desatualizado)", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-09", "LEG-11", "Simulacro de emergência (medidas de autoproteção)", "Anual", "2026-11-14", "2025-11-14", "Relatório de simulacro 14/11/2025", "Diretor Industrial"),
        ("OBR-10", "LEG-15", "Análise trimestral de Legionella na torre TR-01", "Trimestral", "2026-12-08", "2026-09-08", "Boletim L26-0908", "Gerente de Manutenção"),
        ("OBR-14", "LEG-11", "Manutenção anual de extintores e RIA", "Anual", "2027-03-15", "2026-03-15", "Relatório da empresa de manutenção", "Diretor Industrial"),
        ("OBR-11", "LEG-06", "Revisão do inventário de químicos e das FDS (e pedido de confirmação das FDS com mais de 36 meses)", "Anual", "2027-09-02", "2026-09-02", "RG-SGA-21 Inventario e FDS_Verificacao", "Responsável de Armazém e Logística"),
        ("OBR-12", "LEG-09", "Declaração UE de conformidade PPWR por família de embalagem", "Por ocorrência", "2026-08-12", "", "Em curso: 9/22 famílias concluídas (PAM-26-10)", "Responsável de R&D"),
        ("OBR-13", "LEG-04", "Balanço anual de solventes (confirmar não aplicabilidade)", "Anual", "2027-09-05", "2026-09-05", "BAL-SOLV-2026", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-15", "LEG-16", "Declaração anual das embalagens de expedição à entidade gestora (SIGRE)", "Anual", "2027-02-28", "2026-02-26", "Declaração 2025 (26/02/2026)", "Diretor Financeiro"),
        ("OBR-16", "LEG-21", "Reavaliação anual da reciclabilidade por SKU (RecyClass / graus PPWR)", "Anual", "2027-09-22", "2026-09-22", "RG-SGA-20 tbl_recyclass", "Responsável de R&D"),
        ("OBR-17", "LEG-17", "Rever declarações de conformidade FCM (alteração de material ou legislação)", "Anual", "2027-03-20", "2026-03-20", "DoC anexo IV + ensaios de migração 03/2026", "Gerente da Qualidade"),
        ("OBR-18", "LEG-18", "Retirar alegações proibidas antes da aplicação da Diretiva 2024/825", "Por ocorrência", "2026-09-27", "", "tbl_alegacoes (RG-SGA-20)", "Diretor Geral (Gestão de Topo)"),
        # produtos químicos (antes em RG-SGA-21 Calendario — calendário único aqui)
        ("OBR-19", "LEG-06", "Verificar a atualização da lista candidata SVHC (ECHA: janeiro e junho), atualizar o parâmetro P-01 e rever SVHC nas embalagens (art. 33.º / SCIP)", "Semestral", "2026-08-10", "2026-02-10", "RG-SGA-21 Parametros P-01; RG-SGA-20 tbl_familias_ppwr", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-20", "LEG-10", "Relatório anual à ECHA das libertações estimadas de granulado (REACH anexo XVII, entrada 78)", "Anual", "2027-05-31", "2026-05-28", "Submissão REACH-IT (dados de 2025)", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-21", "LEG-06", "Renovar as declarações SVHC/PFAS/metais/BPA/FCM dos fornecedores", "Anual", "2027-03-05", "2026-03-05", "RG-SGA-21 tbl_declaracoes", "Responsável de Compras"),
        ("OBR-22", "LEG-22", "Rever a avaliação de riscos químicos (e sempre que houver alteração)", "Trienal", "2027-03-15", "2024-03-15", "RG-SGA-21 tbl_risco_quimico", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-23", "LEG-22", "Medição da exposição a COV na serigrafia (NP EN 689)", "Anual", "2026-11-20", "2025-11-20", "RG-SGA-21 tbl_medicoes_vle", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-24", "LEG-02", "Verificação Seveso — regra da soma com o stock máximo do inventário (DL 150/2015)", "Anual", "2027-09-02", "2026-09-02", "RG-SGA-21 Seveso", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-25", "LEG-06", "Renovar a formação em diisocianatos (5 anos — anexo XVII, entrada 74)", "Quinquenal", "2028-08-10", "2023-08-10", "RG-SGA-08 FOR-13", "Responsável de Recursos Humanos"),
        ("OBR-26", "LEG-10", "Notificar as instalações e emitir a declaração de conformidade (< 1.500 t/ano) — Reg. (UE) 2025/2365", "Por ocorrência", "2027-12-17", "", "PAM-26-11", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-27", "LEG-22", "Vigilância da saúde dos trabalhadores expostos a sensibilizantes e CMR", "Anual", "2027-01-20", "2026-01-20", "Fichas de aptidão (medicina do trabalho)", "Responsável de Recursos Humanos"),
        ("OBR-28", "LEG-22", "Criar e rever a lista de trabalhadores expostos a CMR/reprotóxicos (DL 301/2000)", "Anual", "2026-10-31", "", "PAM-26-29", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-29", "LEG-06", "Acompanhar prazos CLP (Reg. 2023/707 — novas classes; Reg. 2025/2439 — rótulos) e alterações aos anexos do REACH", "Semestral", "2026-10-15", "2026-04-15", "RG-SGA-21 tbl_requisitos_quimicos", "Gestor do SGA / EHS (Responsável Ambiental)"),
        ("OBR-30", "LEG-15", "Confirmar a validade da autorização do biocida da torre (Reg. (UE) 528/2012)", "Anual", "2027-06-09", "2026-06-09", "RG-SGA-21 FDS-036; rótulo com n.º de autorização", "Gerente de Manutenção"),
    ]
    ocols = [
        col("ID_Obrigacao", 9, desc="Identificador da obrigação recorrente.", key="PK"),
        col("ID_Legal", 8, desc="Requisito de origem.", key="FK → tbl_legal"),
        col("Obrigacao", 48, desc="O que tem de ser feito."),
        col("Frequencia", 12, dv="Frequencia", desc="Periodicidade."),
        col("Prazo_Proximo", 11, "date", desc="Próximo prazo legal."),
        col("Ultimo_Cumprimento", 11, "date", desc="Data do último cumprimento."),
        col("Evidencia", 34, desc="Referência da evidência."),
        col("Responsavel", 26, dv="Funcao", desc="Responsável."),
        col("Dias_ate_Prazo", 9, "int", f='=@Prazo_Proximo@-DataRef', desc="Dias até ao prazo (negativo = vencido)."),
        col("Estado", 14, f='=IF(@Dias_ate_Prazo@<0,IF(@Ultimo_Cumprimento@>=@Prazo_Proximo@,"Cumprida em atraso","VENCIDA"),IF(@Dias_ate_Prazo@<=30,"A vencer (≤30 d)","Em dia"))', desc="Estado calculado face à data de referência."),
    ]
    # fecho do ano: obrigações cumpridas no 4.º trimestre — (próximo prazo, último cumprimento, evidência)
    FECHO_OB = {"OBR-02": ("2027-01-31", "2026-12-18", "e-GAR de dezembro (conferência mensal)"), "OBR-03": ("2027-06-12", "2026-12-10", "Boletim 26/2410"),
                "OBR-04": ("2027-05-20", "2026-11-18", "Relatório de controlo de fugas 11/2026 (sem fugas)"),
                "OBR-08": ("2029-10-28", "2026-10-28", "Relatório AC-2026-112 (conforme)"), "OBR-09": ("2027-11-26", "2026-11-26", "Relatórios de simulacro 26/11 e 11/12/2026"),
                "OBR-10": ("2027-03-08", "2026-12-07", "Boletim L26-1207"), "OBR-12": ("2026-08-12", "", "Em curso: 17/22 famílias concluídas (PAM-26-10 concluída; 5 famílias em 2027)"),
                "OBR-18": ("2026-09-27", "2026-09-29", "Alegações retiradas a 29/09/2026 (PAM-26-27)"), "OBR-19": ("2027-02-10", "2026-07-30", "Lista candidata de junho/2026 verificada; P-01 atualizado"),
                "OBR-23": ("2027-11-20", "2026-11-19", "Relatório de medição NP EN 689 (19/11/2026)"), "OBR-28": ("2027-11-12", "2026-11-12", "Lista de expostos a CMR criada (12/11/2026)"),
                "OBR-29": ("2027-04-15", "2026-10-14", "Revisão CLP/REACH de 14/10/2026")}
    OB = [(o[0], o[1], o[2], o[3]) + (FECHO_OB[o[0]] if o[0] in FECHO_OB else (o[4], o[5], o[6])) + (o[7],) for o in OB]
    orows = [dict(zip([c["name"] for c in ocols], (o[0], o[1], o[2], o[3], d(o[4]), d(o[5]) if o[5] else None, o[6], o[7]))) for o in OB]
    b.table("Calendario_Obrigacoes", "tbl_obrigacoes", ocols, orows, "Calendário de obrigações legais recorrentes com estado calculado (compliance calendar).",
            cf=[("Estado", {"VENCIDA": "red", "atraso": "orange", "A vencer": "yellow", "Em dia": "green"})], row_height=32)

    # histórico de avaliações (2 ciclos) — para tendência
    H = []
    prev = {"LEG-01": "C", "LEG-02": "C", "LEG-03": "C", "LEG-04": "C", "LEG-05": "C", "LEG-06": "NC", "LEG-07": "C", "LEG-08": "C",
            "LEG-09": "Futuro", "LEG-10": "Futuro", "LEG-11": "C", "LEG-12": "NC", "LEG-13": "C", "LEG-14": "C", "LEG-15": "NC", "LEG-16": "C", "LEG-17": "C", "LEG-18": "Futuro", "LEG-19": "Em avaliação", "LEG-20": "C", "LEG-21": "Futuro", "LEG-22": "Em avaliação"}
    for t in LEG:
        H.append(dict(ID_Legal=t[0], Ciclo="2025", Data_Avaliacao=dt.date(2025, 9, 12), Estado=prev[t[0]]))
        H.append(dict(ID_Legal=t[0], Ciclo="2026", Data_Avaliacao=DAV, Estado=t[17]))
    hcols = [col("ID_Legal", 8, desc="Requisito.", key="FK → tbl_legal"), col("Ciclo", 7, desc="Ano do ciclo de avaliação."),
             col("Data_Avaliacao", 11, "date", desc="Data."), col("Estado", 7, dv="Estado", desc="Resultado da avaliação.")]
    b.table("Historico_Avaliacoes", "tbl_hist_conformidade", hcols, H, "Histórico das avaliações de conformidade por ciclo (formato longo para análise de tendência).",
            cf=[("Estado", {"NC": "red", "Futuro": "blue", "C": "green"})])

    # vista Mod.G.06.02 (formato do enunciado)
    ws = b.sheet("Mod.G.06.02_Vista", "Tabela no formato do enunciado (7 colunas) para print screen no fórum, calculada a partir de tbl_legal.", tab_color="C00000")
    doc_header(ws, "RG-SGA-04", "TABELA DE IDENTIFICAÇÃO DE REQUISITOS LEGAIS E AVALIAÇÃO DA CONFORMIDADE", "Mod. G.06.02", 7)
    heads = ["Código / Tema", "Diploma / Documento", "Resumo / Obrigações", "Aplicabilidade", "Disposições Internas", "Avaliação da Conformidade (EVIDÊNCIA)", "Estado (C/NC)"]
    header_row(ws, 5, heads, widths=[20, 34, 46, 14, 40, 56, 10])
    T = lambda f: b.ref("tbl_legal", f)
    for k in range(len(LEG)):
        r = 6 + k
        i = k + 1
        vals = [f'=INDEX({T("Tema")},{i})', f'=INDEX({T("Diploma_Documento")},{i})', f'=INDEX({T("Resumo_Obrigacoes")},{i})',
                f'=INDEX({T("Aplicabilidade")},{i})&IF(INDEX({T("Aplicabilidade")},{i})="Sim",""," — "&INDEX({T("Justificacao_Aplicabilidade")},{i}))',
                f'=INDEX({T("Disposicoes_Internas")},{i})', f'=INDEX({T("Avaliacao_Conformidade_Evidencia")},{i})', f'=INDEX({T("Estado")},{i})']
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=j + 1, value=v)
            c.font, c.border = Font(name=FONT, size=9), BORDER
            c.alignment = CENTER if j in (3, 6) else WRAP_TOP
        ws.row_dimensions[r].height = 105
    for txt, color in {"NC": "red", "Futuro": "blue", "Em avaliação": "orange", "C": "green"}.items():
        bg, fg = CF_COLORS[color]
        ws.conditional_formatting.add(f"G6:G{5 + len(LEG)}", FormulaRule(formula=[f'G6="{txt}"'], fill=PatternFill("solid", fgColor=bg), font=Font(name=FONT, color=fg, bold=True)))
    r = 7 + len(LEG)
    ws.cell(row=r, column=1, value="Síntese").font = F_BOLD
    st = T("Estado")
    ws.cell(row=r, column=2, value=f'="Conformes: "&COUNTIF({st},"C")&" · Não conformes: "&COUNTIF({st},"NC")&" · Futuros: "&COUNTIF({st},"Futuro")&" · Taxa de conformidade (aplicáveis): "&TEXT(COUNTIFS({st},"C",{T("Aplicabilidade")},"Sim")/COUNTIF({T("Aplicabilidade")},"Sim"),"0%")')
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
    ws.freeze_panes = "B6"
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows = "5:5"

    path = b.save(out)
    return path


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
