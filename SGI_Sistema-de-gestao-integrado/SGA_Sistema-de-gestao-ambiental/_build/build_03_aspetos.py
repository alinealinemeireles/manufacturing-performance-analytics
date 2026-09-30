import datetime as dt
from sgalib import *
from dims import *
from envdata import ambiente, anual

DA = dt.date(2026, 5, 20)   # avaliação anual de aspetos (antes da Revisão pela Gestão)

IMPACTES = [
    ("IMP-01", "Esgotamento de Recursos Naturais / Recursos", "Adverso"),
    ("IMP-02", "Contaminação do Solo e/ou Recursos Hídricos", "Adverso"),
    ("IMP-03", "Poluição do Ar", "Adverso"),
    ("IMP-04", "Mudanças Climáticas", "Adverso"),
    ("IMP-05", "Incomodidade da Vizinhança", "Adverso"),
    ("IMP-06", "Perturbação da Fauna / Flora / Paisagem", "Adverso"),
    ("IMP-07", "Redução da vida útil de aterros e passivos ambientais", "Adverso"),
    ("IMP-08", "Degradação da saúde dos ecossistemas aquáticos (microplásticos)", "Adverso"),
    ("IMP-09", "Promoção da Eficiência Hídrica e Circularidade (valorização interna de resíduos/águas)", "Benéfico"),
    ("IMP-10", "Otimização do Consumo de Matérias-Primas (poupança ou geração de novos recursos)", "Benéfico"),
    ("IMP-11", "Extensão do ciclo de vida de materiais (conversão de resíduos em subprodutos)", "Benéfico"),
    ("IMP-12", "Minimização da Pressão Ecológica (materiais recicláveis ou de origem sustentável)", "Benéfico"),
]
IMP_SHORT = {i[0]: i[1].split(" (")[0] for i in IMPACTES}


def build(out):
    prod, mm, fact, res = ambiente()
    A = anual(fact, res, prod)
    kg = lambda v: round(v / 1000, 1)   # kg -> t

    # (ID, Proc, Area, Atividade, Fase, Categoria, Descricao, Tipo, Condicao, Temporalidade, Imp principal, Imp secundários,
    #  F, M, G, L, Qtd, Unidade, Fonte, Medidas, Controlo existente, Justificação, LEG, RO, OBJ, PAM, MED, Sel)
    AS = [
        ("AA-001", "CMP", "Compras e fornecedores", "Aquisição de polímeros (PP, HDPE, PET)", "Aquisição", "Consumo de recursos",
         "Consumo de polímeros virgens de origem fóssil", "Indireto", "Normal", "Presente", "IMP-01", "IMP-04",
         5, 5, 2, 1, kg(A["polimero_kg"] - A["pcr_kg"]), "t/ano", "Inventário de matérias-primas (12 meses)",
         "Critérios de compra com conteúdo reciclado certificado; lightweighting.", "Especificação técnica de compra.",
         "F5 contínuo; M5 maior fluxo de matéria da fábrica; G2 material inerte mas não renovável.", "", "RO-05", "OBJ-02", "PAM-26-16", "MED-05", "Não"),
        ("AA-002", "CMP", "Compras e fornecedores", "Transporte de matérias-primas pelos fornecedores", "Aquisição", "Emissões atmosféricas",
         "Emissões de gases de escape (CO2, NOx, partículas) no transporte rodoviário e marítimo de resinas", "Indireto", "Normal", "Presente", "IMP-04", "IMP-03",
         4, 4, 3, 1, None, "", "Guias de remessa; origem dos fornecedores", "Preferir fornecedores ibéricos e cargas completas.", "—",
         "F4 entregas diárias; M4 ≈ 810 t/ano transportadas; G3 poluente convencional.", "", "", "", "", "", "Não"),
        ("AA-003", "REC", "Receção e silos", "Descarga de big bags e transferência pneumática para silos", "Produção", "Perdas de granulado",
         "Perda de granulado de plástico para o pavimento e a rede de águas pluviais", "Direto", "Normal", "Presente", "IMP-08", "IMP-02; IMP-06",
         4, 3, 4, 1, kg(A["granulado_kg"]) * 1000, "kg/ano recolhidos", "Pesagem do granulado recolhido",
         "Operation Clean Sweep: filtros nas sarjetas, tabuleiros de descarga, aspiração, inspeção semanal.", "Varrimento diário.",
         "F4 diário; M3 perdas de kg/mês; G4 microplásticos persistentes e nocivos para a fauna aquática.", "LEG-10", "RO-07", "OBJ-06", "PAM-26-11", "MED-09", "Não"),
        ("AA-004", "REC", "Receção e silos", "Desembalagem de matérias-primas", "Produção", "Resíduos",
         "Geração de resíduos de embalagem de matérias-primas (big bags, sacos, paletes, cartão)", "Direto", "Normal", "Presente", "IMP-07", "IMP-01",
         4, 3, 2, 1, None, "", "Pesagens por código LER", "Segregação por fluxo; big bags retornáveis com fornecedor.", "Contentores identificados no parque de resíduos.",
         "F4 diário; M3; G2 resíduos não perigosos recicláveis.", "LEG-01", "", "", "", "MED-04", "Não"),
        ("AA-005", "ARQ", "Armazém de químicos", "Armazenagem de tintas, solventes e óleos", "Produção", "Contaminação do solo",
         "Derrame acidental de tintas, solventes ou óleos (rutura de embalagem, queda na movimentação)", "Direto", "Emergência", "Futuro", "IMP-02", "IMP-03",
         1, 3, 5, 1, None, "", "Inventário do armazém (≈ 1,5 m³ de líquidos perigosos)",
         "Bacias de retenção, kits de derrame completos e selados, IT-SGA-01, simulacro semestral.", "Kits de derrame; FDS; parte dos bidões em bacia.",
         "F1 emergência improvável; M3 até 200 L; G5 solventes com H336/H225 e tintas com H411.", "LEG-06", "RO-10", "", "PAM-26-05", "MED-10", "Sim"),
        ("AA-006", "ARQ", "Armazém de químicos", "Manuseamento e trasfega de solventes", "Produção", "Emissões atmosféricas",
         "Evaporação de COV de recipientes abertos ou mal fechados", "Direto", "Anormal", "Presente", "IMP-03", "IMP-04",
         3, 2, 5, 1, None, "", "Ronda ambiental", "Recipientes fechados, dispensadores de segurança, regra 'tampa fechada'.", "Instrução verbal.",
         "F3 semanal; M2 pequenas quantidades; G5 COV sem tratamento.", "LEG-06", "", "OBJ-03", "PAM-26-08", "MED-06", "Não"),
        ("AA-007", "INJ", "Injeção de tampas", "Moldação por injeção (IM-001 a IM-009)", "Produção", "Consumo de recursos",
         "Consumo de energia elétrica (aquecimento do canhão, hidráulica, extração)", "Direto", "Normal", "Presente", "IMP-01", "IMP-04",
         5, 5, 3, 1, kg(A["ene_INJ"]), "MWh/ano", "Rateio da fatura por horas de marcha (sem submedição)",
         "Standby nas pausas (Kaizen KZ-01), manutenção de resistências e isolamento do canhão, submedição.", "Manutenção preventiva.",
         "F5 contínuo; M5 um dos maiores consumos; G3 emissões indiretas convencionais.", "LEG-08", "RO-02", "OBJ-01", "PAM-26-06", "MED-01", "Não"),
        ("AA-008", "INJ", "Injeção de tampas", "Moldação por injeção (IM-001 a IM-009)", "Produção", "Resíduos",
         "Geração de scrap plástico (peças rejeitadas, jitos e purgas de arranque)", "Direto", "Normal", "Presente", "IMP-01", "IMP-07",
         5, 3, 3, 1, None, "", "Pesagem de scrap", "Controlo de processo (DOE IM-002), segregação por cor e reintegração.", "Moinhos junto às máquinas.",
         "F5 contínuo; M3; G3 resíduo não perigoso em grande quantidade.", "LEG-01", "RO-11", "OBJ-02", "", "MED-03", "Não"),
        ("AA-009", "INJ", "Injeção de tampas", "Mudança de óleo hidráulico e fugas em mangueiras", "Produção", "Contaminação do solo",
         "Fuga de óleo hidráulico durante manutenção ou por rotura de mangueira", "Direto", "Anormal", "Presente", "IMP-02", "",
         2, 2, 4, 1, None, "", "Registos de manutenção", "Tabuleiros de retenção sob a hidráulica; inspeção de mangueiras.", "Absorventes na oficina.",
         "F2 trimestral; M2 litros; G4 óleo usado (resíduo perigoso standard).", "LEG-01", "RO-10", "", "", "", "Não"),
        ("AA-010", "SOP", "Sopro de frascos (ISBM)", "Moldação por injeção-sopro (ISBM-001 a 010)", "Produção", "Consumo de recursos",
         "Consumo de energia elétrica (aquecimento de pré-formas, sopro, hidráulica)", "Direto", "Normal", "Presente", "IMP-01", "IMP-04",
         5, 5, 3, 1, kg(A["ene_SOP"]), "MWh/ano", "Rateio da fatura por horas de marcha (sem submedição)",
         "Submedição, ajuste de temperaturas de condicionamento, standby nas pausas.", "Manutenção preventiva.",
         "F5 contínuo; M5 maior consumo de energia; G3.", "LEG-08", "RO-02", "OBJ-01", "PAM-26-02", "MED-01", "Não"),
        ("AA-011", "SOP", "Sopro de frascos (ISBM)", "Moldação por injeção-sopro (ISBM-001 a 010)", "Produção", "Resíduos",
         "Geração de scrap plástico (frascos rejeitados e purgas)", "Direto", "Normal", "Presente", "IMP-01", "IMP-07",
         5, 4, 3, 1, kg(A["scrap_kg"]), "t/ano (todos os processos)", "Pesagem de scrap",
         "Controlo da espessura de parede (ISBM-003), manutenção de moldes, reintegração.", "Cartas de controlo.",
         "F5; M4 maior fluxo de scrap; G3.", "LEG-01", "RO-11", "OBJ-02", "", "MED-03", "Não"),
        ("AA-012", "SOP", "Sopro de frascos (ISBM)", "Arranque e paragem de máquinas / mudança de molde", "Produção", "Resíduos",
         "Purgas e peças de arranque após mudança de molde ou paragem", "Direto", "Anormal", "Presente", "IMP-01", "IMP-07",
         4, 3, 3, 1, None, "", "Registos de setup", "SMED e receitas de arranque validadas.", "Setup padrão.",
         "F4 diário; M3; G3.", "", "", "OBJ-02", "", "MED-03", "Não"),
        ("AA-013", "SOP", "Sopro de frascos (ISBM)", "Hidráulica envelhecida da ISBM-005", "Produção", "Contaminação do solo",
         "Fugas de óleo hidráulico na ISBM-005 (paragens não planeadas 2,3× a média)", "Direto", "Anormal", "Presente", "IMP-02", "",
         4, 2, 4, 1, None, "", "fact_downtime (ISBM-005)", "Plano de manutenção por horas de operação; tabuleiro de retenção.", "Absorventes.",
         "F4 semanal; M2; G4 óleo.", "LEG-01", "RO-10", "", "", "", "Não"),
        ("AA-014", "SER", "Serigrafia", "Limpeza de ecrãs e rodos com solvente", "Produção", "Emissões atmosféricas",
         "Emissão difusa de COV na limpeza de ecrãs e rodos com solvente", "Direto", "Normal", "Presente", "IMP-03", "IMP-04",
         5, 3, 5, 1, round(A["solvente_kg"]), "kg solvente/ano", "Inventário de solvente (compras - stock)",
         "Dispensadores de segurança, panos pré-dosados, limpeza por necessidade, avaliação de solvente de menor volatilidade.", "Exaustão localizada; FDS no posto.",
         "F5 em cada mudança de cor/turno; M3; G5 COV sem tratamento (PR.G.01.01).", "LEG-04", "", "OBJ-03", "PAM-26-08", "MED-06", "Sim"),
        ("AA-015", "SER", "Serigrafia", "Impressão serigráfica (SS-001, SS-002)", "Produção", "Consumo de recursos",
         "Consumo de tintas de serigrafia", "Direto", "Normal", "Presente", "IMP-01", "IMP-03",
         5, 3, 4, 1, round(A["tinta_kg"]), "kg/ano", "Inventário", "Dosagem controlada; recuperação de tinta do ecrã.", "—",
         "F5; M3; G4 tintas classificadas.", "LEG-06", "", "OBJ-03", "", "MED-06", "Não"),
        ("AA-016", "SER", "Serigrafia", "Limpeza e troca de tintas", "Produção", "Resíduos",
         "Resíduos perigosos: tinta residual (08 03 12*), panos/absorventes (15 02 02*) e embalagens contaminadas (15 01 10*)", "Direto", "Normal", "Presente", "IMP-02", "IMP-07",
         4, 3, 4, 1, round(A["res_perig"]), "kg/ano (todos os perigosos)", "Pesagens e e-GAR",
         "Recipientes fechados e identificados; encaminhamento por operador licenciado; e-GAR.", "Contentores na área.",
         "F4; M3; G4 resíduos perigosos standard.", "LEG-01", "RO-10", "", "", "MED-04", "Não"),
        ("AA-017", "SER", "Serigrafia", "Mudança de tinta na linha", "Produção", "Contaminação do solo",
         "Derrame de tinta ou solvente na linha de serigrafia", "Direto", "Emergência", "Futuro", "IMP-02", "IMP-03",
         1, 2, 5, 1, None, "", "Registo de incidentes", "Kit de derrame junto à linha; IT-SGA-01.", "Kit de derrame.",
         "F1; M2 poucos litros; G5.", "LEG-06", "RO-10", "", "PAM-26-05", "", "Não"),
        ("AA-018", "HFS", "Hot foil stamping", "Decoração por hot foil (HF-001, HF-002)", "Produção", "Resíduos",
         "Resíduo de foil (filme de suporte com restos de metalização)", "Direto", "Normal", "Presente", "IMP-07", "IMP-01",
         5, 3, 2, 1, None, "", "Pesagens", "Otimizar passo do foil; valorizar filme como plástico.", "—",
         "F5; M3; G2 não perigoso.", "LEG-01", "", "", "", "MED-04", "Não"),
        ("AA-019", "HFS", "Hot foil stamping", "Decoração por hot foil (HF-001, HF-002)", "Produção", "Consumo de recursos",
         "Consumo de energia elétrica (placas aquecidas)", "Direto", "Normal", "Presente", "IMP-01", "IMP-04",
         5, 2, 3, 1, kg(A["ene_HFS"]), "MWh/ano", "Rateio da fatura", "Desligar placas nas paragens.", "—",
         "F5; M2; G3.", "", "", "OBJ-01", "", "MED-01", "Não"),
        ("AA-020", "MOA", "Moagem de scrap", "Moagem e reintegração de rebarbas", "Produção", "Consumo de recursos",
         "Reintegração de scrap limpo (regrind) em substituição de polímero novo", "Direto", "Normal", "Presente", "IMP-10", "IMP-09",
         5, 4, -1, 1, kg(A["regrind_kg"]), "t/ano", "Pesagem nos moinhos", "Segregar por polímero/cor para aumentar a taxa.", "Moinhos junto às máquinas.",
         "Aspeto benéfico: G -1 circularidade interna (evita compra de matéria-prima).", "", "RO-11", "OBJ-02", "", "MED-03", "Não"),
        ("AA-021", "UTL", "Utilidades", "Produção de ar comprimido (CMP-01/02)", "Produção", "Consumo de recursos",
         "Consumo de energia dos compressores, agravado por fugas na rede de ar comprimido", "Direto", "Normal", "Presente", "IMP-01", "IMP-04",
         5, 4, 3, 1, kg(A["ene_UTL-AR"]), "MWh/ano", "Rateio da fatura", "Caça a fugas por ultrassom; reduzir pressão de 7,5 para 6,8 bar.", "Manutenção dos compressores.",
         "F5; M4; G3.", "LEG-08", "RO-02", "OBJ-01", "PAM-26-01", "MED-02", "Não"),
        ("AA-022", "UTL", "Utilidades", "Operação dos compressores novos (2026)", "Produção", "Ruído e vibrações",
         "Emissão de ruído para o exterior pelos compressores e torre de arrefecimento", "Direto", "Normal", "Presente", "IMP-05", "",
         5, 3, 2, 2, None, "", "Última avaliação acústica: 2023 (antes da troca de compressores)",
         "Avaliação acústica por laboratório acreditado; atenuadores se necessário.", "Compressores em sala fechada.",
         "L2: falta a medição obrigatória após alteração (RGR) → AAS pela regra de ouro.", "LEG-05", "RO-12", "", "PAM-26-03", "MED-07", "Não"),
        ("AA-023", "UTL", "Utilidades", "Torre de arrefecimento TR-01", "Produção", "Consumo de recursos",
         "Consumo de água de rede para reposição da torre de arrefecimento (evaporação e purga)", "Direto", "Normal", "Presente", "IMP-01", "",
         5, 4, 3, 1, round(A["agua_torre"]), "m³/ano", "Balanço da fatura de água", "Circuito fechado / torre adiabática; controlo da purga por condutividade.", "Tratamento de água da torre.",
         "F5; M4 principal consumo de água; G3.", "LEG-03", "RO-04", "OBJ-05", "PAM-26-14", "MED-08", "Não"),
        ("AA-024", "UTL", "Utilidades", "Purga da torre de arrefecimento", "Produção", "Efluentes",
         "Descarga da purga da torre (com biocida e anti-incrustante) no coletor municipal", "Direto", "Normal", "Presente", "IMP-02", "",
         4, 3, 4, 1, None, "", "Análises semestrais do efluente", "Dosagem automática; análises; limites do regulamento municipal.", "Autorização de descarga.",
         "F4; M3; G4 biocida (H400).", "LEG-03", "", "", "", "MED-11", "Não"),
        ("AA-025", "UTL", "Utilidades", "Chiller CH-01 (R410A)", "Produção", "Fugas",
         "Fuga de gás fluorado R410A do chiller", "Direto", "Emergência", "Passado", "IMP-04", "",
         1, 1, 5, 1, 3.2, "kg R410A (fuga nov/2025)", "Relatório do técnico certificado", "Controlo de fugas conforme carga em tCO2e; técnico certificado.", "Registo do equipamento.",
         "F1; M1; G5 (GWP 2088). Ocorrência passada em nov/2025.", "LEG-07", "", "", "", "", "Não"),
        ("AA-026", "MAN", "Manutenção", "Manutenção mecânica e elétrica", "Produção", "Resíduos",
         "Geração de óleos usados (13 02 05*), lâmpadas (20 01 21*) e sucata metálica", "Direto", "Especial" if False else "Anormal", "Presente", "IMP-02", "IMP-07",
         2, 3, 4, 1, None, "", "Pesagens e e-GAR", "Recolha por operadores licenciados; armazenagem em bacia.", "Bidão de óleo usado em bacia.",
         "F2 trimestral; M3; G4.", "LEG-01", "", "", "", "MED-04", "Não"),
        ("AA-027", "PRS", "Parque de resíduos", "Armazenagem temporária de resíduos", "Fim de Vida", "Contaminação do solo",
         "Escorrência de resíduos perigosos armazenados para a rede pluvial em dia de chuva", "Direto", "Anormal", "Presente", "IMP-02", "",
         2, 2, 4, 1, None, "", "Ronda ambiental", "Cobertura e bacia no ponto de resíduos perigosos.", "Contentores fechados.",
         "F2; M2; G4.", "LEG-01", "RO-10", "", "", "MED-10", "Não"),
        ("AA-028", "PRS", "Parque de resíduos", "Encaminhamento de resíduos", "Fim de Vida", "Resíduos",
         "Envio de scrap sujo e embalagens para reciclagem por operador licenciado (R3)", "Indireto", "Normal", "Presente", "IMP-11", "IMP-12",
         4, 3, -1, 1, None, "", "e-GAR", "Aumentar a segregação para subir a taxa de valorização.", "Contratos com operadores.",
         "Aspeto benéfico: G -1 (resíduo convertido em matéria-prima secundária).", "LEG-01", "", "", "", "MED-04", "Não"),
        ("AA-029", "GER", "Geral", "Funcionamento geral da instalação", "Produção", "Resíduos",
         "Resíduos indiferenciados (20 03 01) enviados para aterro", "Direto", "Normal", "Presente", "IMP-07", "",
         5, 3, 2, 1, None, "", "Pesagens / e-GAR", "Reduzir contaminação dos fluxos recicláveis.", "Ecopontos.",
         "F5; M3; G2.", "LEG-01", "", "", "", "MED-04", "Não"),
        ("AA-030", "GER", "Geral", "Iluminação, AVAC, escritórios", "Produção", "Consumo de recursos",
         "Consumo de energia elétrica geral (iluminação, AVAC, armazéns)", "Direto", "Normal", "Presente", "IMP-01", "IMP-04",
         5, 3, 3, 1, kg(A["ene_GER"]), "MWh/ano", "Rateio da fatura", "LED com sensores; horários de AVAC.", "—",
         "F5; M3; G3.", "", "", "OBJ-01", "", "MED-01", "Não"),
        ("AA-031", "GER", "Geral", "Contrato de eletricidade", "Produção", "Consumo de recursos",
         "Consumo de eletricidade com garantia de origem renovável (55% do mix)", "Direto", "Normal", "Presente", "IMP-12", "IMP-04",
         5, 5, -1, 1, round(A["ene_total_kwh"] / 1000 * 0.55), "MWh renováveis/ano", "Rótulo de energia do comercializador",
         "Aumentar a quota renovável no próximo contrato.", "Contrato 2026.", "Aspeto benéfico: G -1.", "", "RO-09", "", "", "MED-01", "Não"),
        ("AA-032", "GER", "Geral", "Autoconsumo fotovoltaico previsto (UPAC ≈ 1 MWp)", "Produção", "Consumo de recursos",
         "Produção de energia renovável para autoconsumo", "Direto", "Normal", "Futuro", "IMP-12", "IMP-04",
         5, 4, -2, 1, 1400, "MWh/ano (estimativa)", "Estudo preliminar", "Estudo de viabilidade e candidatura.", "—",
         "Aspeto benéfico futuro: G -2 regenerativo/descarbonização.", "", "RO-09", "", "", "", "Não"),
        ("AA-033", "GER", "Geral", "Ocupação do terreno industrial", "Produção", "Ocupação do solo",
         "Impermeabilização do solo (≈ 32.000 m² construídos e pavimentados) e escoamento pluvial", "Direto", "Normal", "Passado", "IMP-06", "IMP-02",
         5, 3, 2, 1, 32000, "m² área impermeabilizada", "Planta da instalação", "Áreas verdes com espécies nativas; pavimento permeável em ampliações.", "—",
         "Aspeto de biodiversidade (ISO 14001:2026): herdado da construção.", "", "", "", "", "", "Não"),
        ("AA-034", "GER", "Geral", "Incêndio na instalação", "Produção", "Emissões atmosféricas",
         "Fumos de combustão de plástico e águas de combate contaminadas (incêndio)", "Direto", "Emergência", "Futuro", "IMP-03", "IMP-02; IMP-06",
         1, 5, 5, 1, None, "", "Plano de emergência", "Deteção, válvula de corte pluvial, simulacro anual, faixa de gestão de combustível.", "Medidas de autoproteção (SCIE).",
         "F1; M5 grande carga de incêndio; G5.", "LEG-11", "RO-08", "", "", "", "Não"),
        ("AA-035", "GER", "Geral", "Uso de instalações sanitárias", "Produção", "Efluentes",
         "Águas residuais domésticas descarregadas no coletor municipal", "Direto", "Normal", "Presente", "IMP-02", "",
         5, 2, 2, 1, round(A["agua_san"]), "m³/ano", "Estimativa (água sanitária)", "—", "Ligação ao coletor.",
         "F5; M2; G2.", "LEG-03", "", "", "", "", "Não"),
        ("AA-036", "ADM", "Administrativos", "Trabalho de escritório", "Produção", "Consumo de recursos",
         "Consumo de papel e toners", "Direto", "Normal", "Presente", "IMP-01", "IMP-07",
         4, 1, 1, 1, None, "", "Compras", "Documentação digital.", "—", "F4; M1; G1.", "", "", "", "", "", "Não"),
        ("AA-037", "RD", "R&D", "Conceção de novas embalagens", "Design e Conceção", "Consumo de recursos",
         "Escolha de material, peso e combinação de componentes das embalagens (define impactes a montante e no fim de vida)", "Direto", "Normal", "Presente", "IMP-01", "IMP-07",
         4, 5, 3, 1, None, "", "Dossier de desenvolvimento", "Checklist Design for Recycling; monomaterial; redução de peso.", "—",
         "F4 cada projeto; M5 afeta todo o volume; G3.", "LEG-09", "RO-03", "OBJ-04", "PAM-26-10", "", "Não"),
        ("AA-038", "RD", "R&D", "Colocação de embalagens no mercado UE", "Design e Conceção", "Consumo de recursos",
         "Embalagens colocadas no mercado sem documentação técnica nem declaração UE de conformidade PPWR", "Direto", "Normal", "Presente", "IMP-07", "IMP-01",
         5, 5, 3, 2, None, "", "Avaliação de conformidade LEG-09", "Dossier técnico por família (OBJ-04).", "Fichas técnicas.",
         "L2: incumprimento do Reg. (UE) 2025/40 desde 12/08/2026 → AAS pela regra de ouro.", "LEG-09", "RO-06", "OBJ-04", "PAM-26-10", "MED-12", "Não"),
        ("AA-039", "EXP", "Expedição", "Embalagem de produto acabado", "Distribuição", "Consumo de recursos",
         "Consumo de cartão, filme estirável e paletes", "Direto", "Normal", "Presente", "IMP-01", "IMP-07",
         5, 4, 2, 1, None, "", "Compras", "Caixas e paletes retornáveis com clientes ibéricos.", "—", "F5; M4; G2.", "", "", "", "", "", "Não"),
        ("AA-040", "EXP", "Expedição", "Transporte de produto a clientes", "Distribuição", "Emissões atmosféricas",
         "Emissões do transporte rodoviário de produto acabado (Península Ibérica e UE)", "Indireto", "Normal", "Presente", "IMP-04", "IMP-03; IMP-05",
         5, 4, 3, 1, None, "", "Guias de transporte", "Consolidação de cargas; critérios ambientais para transportadores.", "—",
         "F5; M4; G3.", "", "", "", "", "", "Não"),
        ("AA-041", "EXP", "Expedição", "Embalagens de transporte retornáveis (piloto)", "Distribuição", "Resíduos",
         "Reutilização de caixas e paletes com clientes ibéricos", "Direto", "Normal", "Futuro", "IMP-11", "IMP-10",
         3, 3, -1, 1, None, "", "Piloto previsto 2027", "Alargar a 3 clientes.", "—", "Aspeto benéfico: G -1.", "", "", "", "", "", "Não"),
        ("AA-042", "GER", "Uso pelo cliente", "Enchimento e uso da embalagem pelo cliente e consumidor", "Uso (Consumidor Final)", "Resíduos",
         "Restos de produto cosmético/alimentar na embalagem usada", "Indireto", "Normal", "Presente", "IMP-02", "IMP-07",
         5, 2, 2, 1, None, "", "—", "Design que facilita o esvaziamento total.", "—", "F5; M2; G2.", "", "", "", "", "", "Não"),
        ("AA-043", "GER", "Fim de vida", "Embalagem pós-consumo", "Fim de Vida", "Resíduos",
         "Embalagens pós-consumo não recicladas (aterro, incineração ou abandono)", "Indireto", "Normal", "Presente", "IMP-07", "IMP-08; IMP-06",
         5, 5, 3, 1, None, "", "Taxas de reciclagem de embalagens plásticas (UE)", "Design for Recycling; informação ao cliente sobre reciclagem.", "—",
         "F5; M5 todo o volume vendido; G3.", "LEG-09", "RO-03", "OBJ-04", "", "", "Não"),
    ]
    b = Book("RG-SGA-03", "Matriz de Identificação e Avaliação de Aspetos e Impactes Ambientais (Mod.G.07.00)",
             activities="Atividade 3.2 — Identificação e Avaliação de Aspetos e Impactes Ambientais (aspetos selecionados: AA-005 e AA-014).",
             clauses="6.1.2 Aspetos ambientais (perspetiva de ciclo de vida; situações de emergência distinguidas das anormais — ISO 14001:2026); 6.1.5; 8.1; 8.2",
             purpose="Identificar, para todas as atividades da Plasticom e em todas as fases do ciclo de vida, os aspetos ambientais (causa) e os impactes (efeito), e avaliar a significância pelo IRA = (F + M) × G × L segundo o PR.G.01.01. Ponto de partida: folha 03_Aspectos_Impactes do Plasticom_SGA_ISO14001_2026_ESG_com_Dupla_Materialidade.xlsx, revista e alargada.",
             links=[("RG-SGA-04 Requisitos legais", "ID_Legal liga o aspeto à obrigação de conformidade."),
                    ("RG-SGA-05 Objetivos", "ID_Objetivo liga aspetos significativos a objetivos."),
                    ("RG-SGA-06 PAM", "ID_PAM liga a ação de controlo/melhoria."),
                    ("RG-SGA-13 Monitorização", "ID_Monitorizacao liga ao plano de medição (MED-xx). Quantidade_Anual vem dos dados de monitorização ano civil de 2026.")])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Fase", FASES_CV)
    b.add_list("Categoria", ["Emissões atmosféricas", "Efluentes", "Resíduos", "Contaminação do solo", "Consumo de recursos",
                             "Ruído e vibrações", "Fugas", "Perdas de granulado", "Ocupação do solo"])
    b.add_list("TipoAspeto", ["Direto", "Indireto"])
    b.add_list("Condicao", ["Normal", "Anormal", "Emergência"])
    b.add_list("Temporalidade", ["Presente", "Passado", "Futuro"])
    b.add_list("Impacte", [i[0] for i in IMPACTES])
    b.add_list("F15", [1, 2, 3, 4, 5])
    b.add_list("M15", [1, 2, 3, 4, 5])
    b.add_list("G", [-2, -1, 1, 2, 3, 4, 5])
    b.add_list("L", [1, 2])
    b.add_list("SimNao", ["Sim", "Não"])

    cols = [
        col("ID_Aspeto", 9, desc="Identificador do aspeto.", key="PK", dom="AA-nnn"),
        col("Processo", 8, dv="Processo", desc="Código do processo.", key="FK → dim processo"),
        col("Area_Atividade", 18, desc="Área / atividade (coluna 'Área / Atividade' do Mod.G.07.00)."),
        col("Atividade", 30, desc="Atividade ou tarefa que origina o aspeto."),
        col("Fase_Ciclo_Vida", 15, dv="Fase", desc="Fase do ciclo de vida (Aquisição, Design e Conceção, Produção, Distribuição, Uso, Fim de Vida)."),
        col("Categoria_Aspeto", 17, dv="Categoria", desc="Categoria do aspeto (PR.G.01.01 §5.2)."),
        col("Descricao_Aspeto", 46, desc="O que é emitido, consumido, descarregado ou derramado (causa)."),
        col("Tipo_Aspeto", 9, dv="TipoAspeto", desc="Direto (controlo da Plasticom) ou Indireto (apenas influência)."),
        col("Condicao_Operacao", 11, dv="Condicao", desc="Normal (rotina), Anormal (arranque, paragem, manutenção, picos — 'Especial' no PR.G.01.01) ou Emergência."),
        col("Temporalidade", 11, dv="Temporalidade", desc="Presente, Passado (passivo) ou Futuro (planeado/potencial)."),
        col("ID_Impacte_Principal", 11, dv="Impacte", desc="Impacte principal (lista do Mod.G.07.00 + microplásticos).", key="FK → tbl_impactes"),
        col("Impacte_Principal", 30, f=f'=IFERROR(INDEX(tbl_impactes[Impacte],MATCH(@ID_Impacte_Principal@,tbl_impactes[ID_Impacte],0)),"")', desc="Nome do impacte principal."),
        col("IDs_Impactes_Secundarios", 15, desc="Outros impactes (IDs separados por ';'). Também na tabela longa tbl_aspeto_impacte.", req=False),
        col("F", 5, "int", dv="F15", desc="Frequência 1 (rara) a 5 (contínua)."),
        col("M", 5, "int", dv="M15", desc="Magnitude 1 (vestigial) a 5 (massiva)."),
        col("G", 5, "int", dv="G", desc="Gravidade 1 (inerte) a 5 (tóxica/crítica); -1/-2 para aspetos benéficos."),
        col("L", 5, "int", dv="L", desc="Cumprimento legal: 1 conforme; 2 não conforme / falta medição ou licença."),
        col("Tipo_Efeito", 12, f='=IF(@G@="","",IF(@G@<0,"(-) Benéfico","(+) Adverso"))', desc="Convenção do enunciado da Atividade 3.2: (+) adverso, (-) benéfico (derivado do sinal de G)."),
        col("IRA", 6, "int", f='=IF(COUNT(@F@,@M@,@G@,@L@)<4,"",(@F@+@M@)*@G@*@L@)', desc="Índice de Risco Ambiental = (F + M) × G × L."),
        col("Classificacao", 30, f=('=IF(@IRA@="","",IF(OR(@L@=2,@IRA@>=40),"ASPETO AMBIENTAL SIGNIFICATIVO (AAS)",IF(@IRA@>=20,"Moderado",'
                                    'IF(@IRA@>=0,"Não Significativo",IF(@IRA@>=-14,"Oportunidade Tática","ASPETO AMBIENTAL SIGNIFICATIVO (AAS) BENÉFICO")))))'),
            desc="Regra do Mod.G.07.00 / PR.G.01.01 (inclui regra de ouro L=2 → AAS)."),
        col("Motivo_Classificacao", 16, f='=IF(@IRA@="","",IF(@L@=2,"Regra de ouro (L=2)",IF(@IRA@>=40,"IRA ≥ 40",IF(@IRA@>=20,"IRA 20-39",IF(@IRA@>=0,"IRA 0-19",IF(@IRA@>=-14,"IRA -1 a -14","IRA ≤ -15"))))))', desc="Porque recebeu a classificação."),
        col("Ranking_IRA", 8, "int", f='=IF(@IRA@="","",RANK(@IRA@,#IRA#,0))', desc="Posição do aspeto por IRA (1 = maior)."),
        col("Acao_Plano_Melhoria", 10, f='=IF(@Classificacao@="","",IF(OR(@Classificacao@="ASPETO AMBIENTAL SIGNIFICATIVO (AAS)",@Classificacao@="Moderado"),"SIM","NÃO"))', desc="SIM se AAS ou Moderado (enunciado)."),
        col("Medidas_Controlo_Acao", 44, desc="Controlo operacional ou ação a implementar."),
        col("Controlo_Existente", 26, desc="Controlo operacional já existente."),
        col("Quantidade_Anual", 11, "num0", desc="Evidência de magnitude: quantidade anual (ano civil de 2026) quando medida.", req=False),
        col("Unidade_Quantidade", 16, desc="Unidade da quantidade anual.", req=False),
        col("Fonte_Dado", 26, desc="Origem da informação usada na avaliação."),
        col("Justificacao_Criterios", 40, desc="Justificação dos valores de F, M, G e L (rastreabilidade para auditoria)."),
        col("ID_Legal", 8, desc="Obrigação de conformidade relacionada.", key="FK → RG-SGA-04", req=False),
        col("ID_RO", 8, desc="Risco/oportunidade relacionado.", key="FK → RG-SGA-02", req=False),
        col("ID_Objetivo", 8, desc="Objetivo ambiental relacionado.", key="FK → RG-SGA-05", req=False),
        col("ID_PAM", 10, desc="Ação no Plano de Ações de Melhoria.", key="FK → RG-SGA-06", req=False),
        col("ID_Monitorizacao", 9, desc="Parâmetro do plano de monitorização.", key="FK → RG-SGA-13", req=False),
        col("Verificacao_Gestao", 20, f=('=IF(@Acao_Plano_Melhoria@="SIM",IF(@Medidas_Controlo_Acao@="","FALTA medida de controlo",'
                                         'IF(AND(LEFT(@Classificacao@,6)="ASPETO",@L@=2,@ID_PAM@=""),"FALTA ação corretiva (L=2)",'
                                         'IF(AND(LEFT(@Classificacao@,6)="ASPETO",@ID_Monitorizacao@=""),"Sugestão: definir monitorização","OK"))),"OK")'),
            desc="Controlo automático: aspetos que exigem gestão têm medida, ação e monitorização."),
        col("Selecionado_Atv_3_2", 10, dv="SimNao", desc="Aspeto escolhido para a Atividade 3.2."),
        col("Data_Avaliacao", 11, "date", desc="Data da avaliação."),
        col("Proxima_Revisao", 11, "date", f='=IF(@Data_Avaliacao@="","",EDATE(@Data_Avaliacao@,12))', desc="Revisão anual (ou antes: mudança, acidente, nova legislação)."),
        col("Avaliador", 22, desc="Quem avaliou."),
    ]
    rows = []
    for a in AS:
        (i, pr, ar, at, fa, ca, de, tp, co, te, ip, isec, F, M, G, L, q, u, fo, me, ce, ju, lg, ro, ob, pa, md, se) = a
        rows.append(dict(ID_Aspeto=i, Processo=pr, Area_Atividade=ar, Atividade=at, Fase_Ciclo_Vida=fa, Categoria_Aspeto=ca,
                         Descricao_Aspeto=de, Tipo_Aspeto=tp, Condicao_Operacao=co, Temporalidade=te, ID_Impacte_Principal=ip,
                         IDs_Impactes_Secundarios=isec or None, F=F, M=M, G=G, L=L, Medidas_Controlo_Acao=me, Controlo_Existente=ce,
                         Quantidade_Anual=q, Unidade_Quantidade=u or None, Fonte_Dado=fo, Justificacao_Criterios=ju,
                         ID_Legal=lg or None, ID_RO=ro or None, ID_Objetivo=ob or None, ID_PAM=pa or None, ID_Monitorizacao=md or None,
                         Selecionado_Atv_3_2=se, Data_Avaliacao=DA, Avaliador="Gestor do SGA + responsável do setor"))
    # tabela de impactes primeiro (referenciada por fórmulas)
    icols = [col("ID_Impacte", 10, desc="Identificador do impacte.", key="PK"),
             col("Impacte", 70, desc="Categoria de impacte ambiental (Mod.G.07.00; IMP-08 acrescentado para microplásticos/ecossistemas — ISO 14001:2026)."),
             col("Natureza", 12, desc="Adverso ou Benéfico."),
             col("N_Aspetos", 10, "int", f='=COUNTIF(tbl_aspeto_impacte[ID_Impacte],@ID_Impacte@)', desc="N.º de aspetos associados."),
             col("N_AAS", 8, "int", f='=COUNTIFS(tbl_aspeto_impacte[ID_Impacte],@ID_Impacte@,tbl_aspeto_impacte[Classificacao],"ASPETO*")', desc="N.º de aspetos significativos associados.")]
    b.table("Impactes", "tbl_impactes", icols, [dict(ID_Impacte=i, Impacte=n, Natureza=t) for i, n, t in IMPACTES],
            "Catálogo de impactes ambientais (dimensão).")
    b.table("Aspetos_Impactes", "tbl_aspetos", cols, rows,
            "Registo de aspetos e impactes (1 linha por aspeto) com avaliação IRA e gestão.",
            title="MATRIZ DE AVALIAÇÃO DE ASPETOS E IMPACTES AMBIENTAIS — PLASTICOM (registo de dados)",
            subtitle="IRA = (F + M) × G × L · AAS se IRA ≥ 40 ou L = 2 · Moderado 20-39 · Não significativo 0-19 · Oportunidade tática -1 a -14 · AAS benéfico ≤ -15 · Filtrar Selecionado_Atv_3_2 = Sim",
            cf=[("Classificacao", {"BENÉFICO": "blue", "ASPETO": "red", "Moderado": "orange", "Não Signif": "green", "Tática": "purple"}),
                ("Verificacao_Gestao", {"FALTA": "red", "Sugestão": "yellow", "OK": "green"}),
                ("Condicao_Operacao", {"Emergência": "red", "Anormal": "yellow"}),
                ("Selecionado_Atv_3_2", {"Sim": "purple"})],
            row_height=70, freeze_col=2)
    # tabela longa aspeto-impacte
    ai = []
    for a in AS:
        ai.append(dict(ID_Aspeto=a[0], ID_Impacte=a[10], Principal="Sim"))
        for s in (a[11] or "").split(";"):
            if s.strip():
                ai.append(dict(ID_Aspeto=a[0], ID_Impacte=s.strip(), Principal="Não"))
    aicols = [col("ID_Aspeto", 10, desc="Aspeto.", key="FK → tbl_aspetos"),
              col("ID_Impacte", 10, dv="Impacte", desc="Impacte.", key="FK → tbl_impactes"),
              col("Principal", 9, dv="SimNao", desc="Sim = impacte principal."),
              col("Impacte", 50, f='=IFERROR(INDEX(tbl_impactes[Impacte],MATCH(@ID_Impacte@,tbl_impactes[ID_Impacte],0)),"")', desc="Nome do impacte."),
              col("Classificacao", 32, f='=IFERROR(INDEX(tbl_aspetos[Classificacao],MATCH(@ID_Aspeto@,tbl_aspetos[ID_Aspeto],0)),"")', desc="Classificação do aspeto (para análise por impacte)."),
              col("IRA", 6, "int", f='=IFERROR(INDEX(tbl_aspetos[IRA],MATCH(@ID_Aspeto@,tbl_aspetos[ID_Aspeto],0)),"")', desc="IRA do aspeto.")]
    b.table("Aspeto_Impacte", "tbl_aspeto_impacte", aicols, ai, "Relação N:N aspeto × impacte (formato longo, para análise e para os 'X' da matriz Mod.G.07.00).")

    # ------------- vista Mod.G.07.00 (formato do curso, calculada)
    ws = b.sheet("Mod.G.07.00_Matriz", "Matriz no formato do modelo do curso (Mod.G.07.00), com 'X' calculados a partir das tabelas. Para impressão; editar em Aspetos_Impactes.", tab_color="C00000")
    ncol = 2 + 6 + 1 + 3 + len(IMPACTES) + 8
    doc_header(ws, "RG-SGA-03", "MATRIZ DE AVALIAÇÃO DE ASPETOS E IMPACTES AMBIENTAIS", "Mod. G.07.00", ncol)
    groups = [("Área / Atividade", 1, 2), ("Ciclo de Vida", 3, 8), ("Aspeto", 9, 9), ("Natureza do aspeto", 10, 12),
              ("Potenciais Impactes Ambientais", 13, 12 + len(IMPACTES)), ("Avaliação", 13 + len(IMPACTES), 19 + len(IMPACTES)),
              ("Gestão", 20 + len(IMPACTES), 21 + len(IMPACTES))]
    for lab, c1, c2 in groups:
        c = ws.cell(row=5, column=c1, value=lab)
        c.font, c.fill, c.alignment = F_HEAD, FILL_HEAD, CENTER
        if c2 > c1:
            ws.merge_cells(start_row=5, start_column=c1, end_row=5, end_column=c2)
    heads = (["Área / Atividade", "ID"] + FASES_CV + ["Descrição do Aspeto Ambiental", "Tipo de Aspeto", "Condição de Operação", "Temporalidade"]
             + [n for _, n, _ in IMPACTES] + ["Tipo (+/-)", "F", "M", "G", "L", "IRA", "Classificação", "Ação em Plano de Melhoria", "Medidas de Controlo / Ação"])
    widths = ([20, 8] + [5] * 6 + [38, 9, 11, 10] + [5] * len(IMPACTES) + [9, 4, 4, 4, 4, 6, 24, 10, 40])
    header_row(ws, 6, heads, widths)
    for c in range(3, 9):
        ws.cell(row=6, column=c).alignment = Alignment(text_rotation=90, horizontal="center", vertical="bottom", wrap_text=True)
    for c in range(13, 13 + len(IMPACTES)):
        ws.cell(row=6, column=c).alignment = Alignment(text_rotation=90, horizontal="center", vertical="bottom", wrap_text=True)
    ws.row_dimensions[6].height = 190
    T = lambda f: b.ref("tbl_aspetos", f)
    for k in range(len(AS)):
        r = 7 + k
        idx = k + 1
        vals = [f'=INDEX({T("Area_Atividade")},{idx})&" — "&INDEX({T("Atividade")},{idx})', f'=INDEX({T("ID_Aspeto")},{idx})']
        vals += [f'=IF(INDEX({T("Fase_Ciclo_Vida")},{idx})="{fa}","X","")' for fa in FASES_CV]
        vals += [f'=INDEX({T("Descricao_Aspeto")},{idx})', f'=INDEX({T("Tipo_Aspeto")},{idx})',
                 f'=INDEX({T("Condicao_Operacao")},{idx})', f'=INDEX({T("Temporalidade")},{idx})']
        vals += [f'=IF(COUNTIFS(tbl_aspeto_impacte[ID_Aspeto],$B{r},tbl_aspeto_impacte[ID_Impacte],"{iid}")>0,"X","")' for iid, _, _ in IMPACTES]
        vals += [f'=LEFT(INDEX({T("Tipo_Efeito")},{idx}),3)'] + [f'=INDEX({T(x)},{idx})' for x in ("F", "M", "G", "L", "IRA", "Classificacao", "Acao_Plano_Melhoria", "Medidas_Controlo_Acao")]
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=j + 1, value=v)
            c.font, c.border = Font(name=FONT, size=9), BORDER
            c.alignment = CENTER if (2 <= j <= 7 or 12 <= j <= 12 + len(IMPACTES) + 6) else WRAP_TOP
        ws.row_dimensions[r].height = 48
    cls_col = get_column_letter(13 + len(IMPACTES) + 6)
    rng = f"{cls_col}7:{cls_col}{6 + len(AS)}"
    for txt, color in {"BENÉFICO": "blue", "ASPETO": "red", "Moderado": "orange", "Não Signif": "green", "Tática": "purple"}.items():
        bg, fg = CF_COLORS[color]
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("{txt}",{cls_col}7))'], fill=PatternFill("solid", fgColor=bg), font=Font(name=FONT, size=9, color=fg, bold=True)))
    ws.freeze_panes = "C7"
    r = 8 + len(AS)
    ws.cell(row=r, column=1, value="O Responsável pela Avaliação: Gestor(a) do SGA / EHS").font = F_BOLD
    ws.cell(row=r + 1, column=1, value=f"Data: {DA:%d/%m/%Y} · Aprovado por: Diretor Geral (lista de AAS aprovada — PR.G.01.01 §4)").font = F_BASE
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows = "5:6"

    # ------------- resumo da Atividade 3.2
    ws = b.sheet("Resumo_Atividade_3_2", "Ficha dos 2 aspetos selecionados para a Atividade 3.2 (campos do enunciado, calculados).", tab_color="7030A0")
    ws["A1"] = "ATIVIDADE 3.2 — IDENTIFICAÇÃO E AVALIAÇÃO DE ASPETOS E IMPACTES (2 aspetos selecionados)"
    ws["A1"].font = F_TITLE
    ws["A2"] = "Valores calculados a partir de tbl_aspetos. Método: PR.G.01.01 — IRA = (F + M) × G × L."
    ws["A2"].font = F_SUB
    ws.column_dimensions["A"].width = 38
    ws.column_dimensions["B"].width = 62
    ws.column_dimensions["C"].width = 62
    campos = [("DADOS", None), ("Ciclo de Vida", "Fase_Ciclo_Vida"), ("Atividade", "Atividade"), ("Área / processo", "Area_Atividade"),
              ("Descrição do Aspeto Ambiental", "Descricao_Aspeto"), ("a) Tipo de Aspeto", "Tipo_Aspeto"),
              ("b) Condição de Operação", "Condicao_Operacao"), ("c) Temporalidade", "Temporalidade"),
              ("Impacte Ambiental (principal)", "Impacte_Principal"), ("AVALIAÇÃO", None), ("Tipo (+/-)", "Tipo_Efeito"),
              ("F — Frequência (1-5)", "F"), ("M — Magnitude (1-5)", "M"), ("G — Gravidade (1-5)", "G"), ("L — Cumprimento Legal (1/2)", "L"),
              ("IRA = (F + M) × G × L", "IRA"), ("Classificação", "Classificacao"), ("Justificação dos critérios", "Justificacao_Criterios"),
              ("GESTÃO", None), ("Ação em Plano de Melhoria (SIM|NÃO)", "Acao_Plano_Melhoria"), ("Medidas de Controlo / Ação", "Medidas_Controlo_Acao"),
              ("Ação no PAM", "ID_PAM"), ("Requisito legal", "ID_Legal")]
    header_row(ws, 4, ["Campo", "Aspeto 1", "Aspeto 2"])
    ids = T("ID_Aspeto")
    ws.cell(row=5, column=1, value="ID do aspeto").font = F_BOLD
    for j, aid in enumerate(["AA-014", "AA-005"]):
        ws.cell(row=5, column=2 + j, value=aid).font = F_BOLD
    for k, (lab, fld) in enumerate(campos):
        r = 6 + k
        a = ws.cell(row=r, column=1, value=lab)
        a.border = BORDER
        if fld is None:
            a.font, a.fill = F_HEAD, FILL_HEAD_CALC
            for j in range(2):
                ws.cell(row=r, column=2 + j).fill = FILL_HEAD_CALC
            continue
        a.font = F_BOLD
        for j in range(2):
            c = ws.cell(row=r, column=2 + j, value=f'=INDEX({T(fld)},MATCH({get_column_letter(2 + j)}$5,{ids},0))&""')
            c.font, c.alignment, c.border = F_BASE, WRAP_TOP, BORDER
        if fld in ("Descricao_Aspeto", "Medidas_Controlo_Acao", "Justificacao_Criterios"):
            ws.row_dimensions[r].height = 45
    r = 7 + len(campos)
    ws.cell(row=r, column=1, value="Nota metodológica").font = F_BOLD
    ws.cell(row=r, column=2, value=("Convenção do sinal conforme o enunciado da Atividade 3.2: (+) adverso e (-) benéfico, coerente com o sinal do IRA "
                                    "(o 'Exemplo Calçado' do Mod.G.07.00 usa a convenção inversa). 'Anormal' corresponde a 'Especial' no PR.G.01.01 "
                                    "(arranque, paragem, manutenção, picos). A ISO 14001:2026 exige distinguir as situações de emergência das anormais."))
    ws.cell(row=r, column=2).alignment = WRAP_TOP
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    ws.row_dimensions[r].height = 60

    # ------------- estatísticas
    ws = b.sheet("Analise", "Distribuição dos aspetos por classificação, processo, condição e fase (calculado).")
    ws["A1"] = "ANÁLISE DA MATRIZ DE ASPETOS (calculada)"
    ws["A1"].font = F_TITLE
    cl = T("Classificacao")
    classes = ["ASPETO AMBIENTAL SIGNIFICATIVO (AAS)", "Moderado", "Não Significativo", "Oportunidade Tática", "ASPETO AMBIENTAL SIGNIFICATIVO (AAS) BENÉFICO"]
    header_row(ws, 3, ["Processo"] + ["AAS", "Moderado", "Não signif.", "Op. tática", "AAS benéfico", "Total", "IRA máx."], widths=[44, 9, 10, 10, 10, 11, 8, 9])
    for k, pcode in enumerate(PROC_CODES):
        r = 4 + k
        ws.cell(row=r, column=1, value=f"{pcode} — {PROC_NAME[pcode]}").font = F_BASE
        for j, c in enumerate(classes):
            ws.cell(row=r, column=2 + j, value=f'=COUNTIFS({T("Processo")},"{pcode}",{cl},"{c}")')
        ws.cell(row=r, column=7, value=f'=COUNTIF({T("Processo")},"{pcode}")').font = F_BOLD
        ws.cell(row=r, column=8, value=f'=IF(G{r}=0,"",_xlfn.MAXIFS({T("IRA")},{T("Processo")},"{pcode}"))')
    rt = 4 + len(PROC_CODES)
    ws.cell(row=rt, column=1, value="TOTAL").font = F_BOLD
    for j in range(2, 8):
        L = get_column_letter(j)
        ws.cell(row=rt, column=j, value=f"=SUM({L}4:{L}{rt - 1})").font = F_BOLD
    r = rt + 2
    header_row(ws, r, ["Condição de operação", "N.º aspetos", "N.º AAS"])
    for k, c in enumerate(["Normal", "Anormal", "Emergência"]):
        ws.cell(row=r + 1 + k, column=1, value=c)
        ws.cell(row=r + 1 + k, column=2, value=f'=COUNTIF({T("Condicao_Operacao")},"{c}")')
        ws.cell(row=r + 1 + k, column=3, value=f'=COUNTIFS({T("Condicao_Operacao")},"{c}",{cl},"ASPETO*")')
    r += 5
    header_row(ws, r, ["Fase do ciclo de vida", "N.º aspetos", "N.º AAS"])
    for k, c in enumerate(FASES_CV):
        ws.cell(row=r + 1 + k, column=1, value=c)
        ws.cell(row=r + 1 + k, column=2, value=f'=COUNTIF({T("Fase_Ciclo_Vida")},"{c}")')
        ws.cell(row=r + 1 + k, column=3, value=f'=COUNTIFS({T("Fase_Ciclo_Vida")},"{c}",{cl},"ASPETO*")')

    # ------------- critérios
    ws = b.sheet("Criterios", "Critérios F, M, G, L e tabela de significância (PR.G.01.01).")
    ws["A1"] = "CRITÉRIOS DE AVALIAÇÃO DA SIGNIFICÂNCIA — PR.G.01.01"
    ws["A1"].font = F_TITLE
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 26
    ws.column_dimensions["C"].width = 90
    crit = [
        ("F — Frequência", [(1, "Rara", "Anual ou menos (emergência improvável, manutenção anual)"), (2, "Esporádica", "Trimestral"), (3, "Intermitente", "Semanal"),
                            (4, "Frequente", "Diária, mas não a tempo inteiro"), (5, "Contínua", "Durante toda a laboração")]),
        ("M — Magnitude", [(1, "Vestigial", "Gramas / mililitros"), (2, "Baixa", "Pequenos consumos de escritório ou manutenção"), (3, "Média", "Consumos industriais auxiliares"),
                           (4, "Alta", "Fluxos principais do processo"), (5, "Massiva", "Maiores fluxos da fábrica (polímero, eletricidade)")]),
        ("G — Gravidade", [(-2, "Regenerativo / Descarbonização", "Gera recursos limpos (ex.: fotovoltaico para autoconsumo)"), (-1, "Circularidade interna", "Evita matéria-prima ou combustível por reutilização (ex.: regrind)"),
                           (1, "Inerte", "Sem impacto nocivo conhecido"), (2, "Leve", "Temporário, reversível, não perigoso"), (3, "Moderada", "Poluente convencional ou resíduo não perigoso em grande quantidade"),
                           (4, "Nociva", "Substância nociva/irritante; resíduos perigosos standard"), (5, "Tóxica / Crítica", "Frases H350/H340/H360/H334/H370; COV sem tratamento")]),
        ("L — Legal", [(1, "Conforme", "Cumpre integralmente e existem evidências"), (2, "Não conforme", "Incumprimento, falta de medição obrigatória ou de licença → AAS automático")]),
        ("Significância", [("≥ 40", "AAS", "Objetivo de redução, controlo operacional diário, avaliar BAT"), ("20 a 39", "Moderado", "Manter monitorização e controlo; ação em plano"),
                           ("0 a 19", "Não Significativo", "Gestão corrente"), ("-1 a -14", "Oportunidade Tática", "Manter a prática e registar poupanças"),
                           ("≤ -15", "AAS Benéfico", "Aspeto diferenciador; destacar no relatório/Declaração Ambiental")]),
    ]
    r = 3
    for t, lines in crit:
        ws.cell(row=r, column=1, value=t).font = F_BOLD
        r += 1
        for ln in lines:
            for j, v in enumerate(ln):
                c = ws.cell(row=r, column=1 + j, value=v)
                c.font, c.alignment, c.border = F_BASE, WRAP_TOP, BORDER
            r += 1
        r += 1
    ws.cell(row=r, column=1, value="Revisão").font = F_BOLD
    ws.cell(row=r, column=3, value="Anual (antes da Revisão pela Gestão); após mudança de processo/produto (6.3), acidente ou emergência, e alteração legal.").alignment = WRAP_TOP
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
