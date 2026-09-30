"""RG-SGA-21 — Gestão de produtos químicos: REACH, CLP, SVHC, restrições, FDS, cenários de exposição, risco químico
(toxicidade — DL 24/2012 e DL 301/2000), armazenagem, Seveso, formação e matriz legal UE + Portugal.

Tabelas principais (1 linha = 1 registo):
  tbl_papel_reach          papel da Plasticom em cada atividade (fabricante, importador, utilizador a jusante, produtor de artigos)
  tbl_quimicos             inventário de produtos químicos (42), com perigos derivados das frases H por fórmula
  tbl_componentes          componentes perigosos (secção 3 da FDS) e cruzamento com a lista de SVHC vigiadas
  tbl_fds                  verificação de cada versão de FDS (Reg. (UE) 2020/878), idade e versão em vigor
  tbl_ce_reach             verificação dos cenários de exposição (art. 37.º, n.º 4 e 5 — prazo de 12 meses)
  tbl_registo_reach        registo/importação: materiais de fora do EEE, representante único, lacunas
  tbl_declaracoes          declarações SVHC/PFAS/metais/FCM dos fornecedores e versão da lista candidata coberta
  tbl_risco_quimico        avaliação de risco químico por tarefa (método adaptado de INRS ND 2233 / Seirich)
  tbl_medicoes_vle         medições de exposição profissional (NP EN 689, teste preliminar)
  tbl_armazenagem          locais de armazenagem: retenção, compatibilidades, inspeção
  tbl_seveso / _resumo     verificação da regra da soma (DL 150/2015)
  tbl_requisitos_quimicos  matriz legal UE + PT de produtos químicos
Fonte única (sem registos repetidos noutros ficheiros): formação → RG-SGA-08; calendário de obrigações → RG-SGA-04 tbl_obrigacoes;
ações → RG-SGA-06 (PAM); SVHC nas embalagens → RG-SGA-20 tbl_familias_ppwr; kits → RG-SGA-12; inspeções → RG-SGA-10; fornecedores → RG-SGA-11.
resumo() devolve os totais (COV, SVHC) usados pelos RG-SGA-16, 17 e 19.
  tbl_analise_critica      avaliação crítica das fontes (ficheiro REACH 2024.xlsx e internet) e melhorias
"""
import datetime as dt
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.workbook.defined_name import DefinedName
from sgalib import *
from dims import *
import envdata

D = lambda s: dt.date.fromisoformat(s) if s else None
SGA, DIND, DG, PROD, MAN, QUA, LOG, CMP, RD, RH, FIN = FUNC_NAMES[:11]
OP_SER, OP_INJ, OP_SOP, OP_HF, TEC_MAN, TEC_UTL, OP_ARM, CHEFE, AUD, REP, TEC_QA = FUNC_NAMES[11:22]
SVHC_N = 253            # entradas da lista candidata (atualização ECHA de 04/02/2026)
ECHA_CL = "https://echa.europa.eu/candidate-list-table"

# ------------------------------------------------------------------------------------------ frases H (CLP, anexo III)
# (código, advertência, tipo, grupo, classe de perigo para a saúde 1-5 (0 = sem efeito na saúde), CMR (1/2/""), maternidade (S/""))
H = [
    ("H200", "Explosivo instável.", "Físico", "Explosivo", 0, "", ""),
    ("H201", "Explosivo; perigo de explosão em massa.", "Físico", "Explosivo", 0, "", ""),
    ("H202", "Explosivo; perigo grave de projeções.", "Físico", "Explosivo", 0, "", ""),
    ("H203", "Explosivo; perigo de incêndio, sopro ou projeções.", "Físico", "Explosivo", 0, "", ""),
    ("H204", "Perigo de incêndio ou projeções.", "Físico", "Explosivo", 0, "", ""),
    ("H205", "Perigo de explosão em massa em caso de incêndio.", "Físico", "Explosivo", 0, "", ""),
    ("H220", "Gás extremamente inflamável.", "Físico", "Inflamável", 0, "", ""),
    ("H221", "Gás inflamável.", "Físico", "Inflamável", 0, "", ""),
    ("H222", "Aerossol extremamente inflamável.", "Físico", "Inflamável", 0, "", ""),
    ("H223", "Aerossol inflamável.", "Físico", "Inflamável", 0, "", ""),
    ("H224", "Líquido e vapor extremamente inflamáveis.", "Físico", "Inflamável", 0, "", ""),
    ("H225", "Líquido e vapor facilmente inflamáveis.", "Físico", "Inflamável", 0, "", ""),
    ("H226", "Líquido e vapor inflamáveis.", "Físico", "Inflamável", 0, "", ""),
    ("H228", "Sólido inflamável.", "Físico", "Inflamável", 0, "", ""),
    ("H229", "Recipiente sob pressão: risco de explosão sob a ação do calor.", "Físico", "Gás/recipiente sob pressão", 0, "", ""),
    ("H230", "Pode reagir explosivamente mesmo na ausência de ar.", "Físico", "Inflamável", 0, "", ""),
    ("H240", "Risco de explosão sob a ação do calor.", "Físico", "Autorreativo/peróxido", 0, "", ""),
    ("H241", "Risco de incêndio ou explosão sob a ação do calor.", "Físico", "Autorreativo/peróxido", 0, "", ""),
    ("H242", "Risco de incêndio sob a ação do calor.", "Físico", "Autorreativo/peróxido", 0, "", ""),
    ("H250", "Risco de inflamação espontânea em contacto com o ar.", "Físico", "Pirofórico", 0, "", ""),
    ("H251", "Suscetível de autoaquecimento; risco de inflamação.", "Físico", "Autoaquecimento", 0, "", ""),
    ("H252", "Suscetível de autoaquecimento em grandes quantidades; risco de inflamação.", "Físico", "Autoaquecimento", 0, "", ""),
    ("H260", "Em contacto com a água liberta gases inflamáveis que se podem inflamar espontaneamente.", "Físico", "Reage com a água", 0, "", ""),
    ("H261", "Em contacto com a água liberta gases inflamáveis.", "Físico", "Reage com a água", 0, "", ""),
    ("H270", "Pode provocar ou agravar incêndios; comburente.", "Físico", "Comburente", 0, "", ""),
    ("H271", "Pode provocar incêndio ou explosão; muito comburente.", "Físico", "Comburente", 0, "", ""),
    ("H272", "Pode agravar incêndios; comburente.", "Físico", "Comburente", 0, "", ""),
    ("H280", "Contém gás sob pressão; risco de explosão sob a ação do calor.", "Físico", "Gás/recipiente sob pressão", 0, "", ""),
    ("H281", "Contém gás refrigerado; pode provocar queimaduras ou lesões criogénicas.", "Físico", "Gás/recipiente sob pressão", 0, "", ""),
    ("H290", "Pode ser corrosivo para os metais.", "Físico", "Corrosivo para metais", 0, "", ""),
    ("H300", "Mortal por ingestão.", "Saúde", "Toxicidade aguda (cat. 1-3)", 5, "", ""),
    ("H301", "Tóxico por ingestão.", "Saúde", "Toxicidade aguda (cat. 1-3)", 4, "", ""),
    ("H302", "Nocivo por ingestão.", "Saúde", "Toxicidade aguda (cat. 4)", 3, "", ""),
    ("H304", "Pode ser mortal por ingestão e penetração nas vias respiratórias.", "Saúde", "Perigo de aspiração", 2, "", ""),
    ("H310", "Mortal em contacto com a pele.", "Saúde", "Toxicidade aguda (cat. 1-3)", 5, "", ""),
    ("H311", "Tóxico em contacto com a pele.", "Saúde", "Toxicidade aguda (cat. 1-3)", 4, "", ""),
    ("H312", "Nocivo em contacto com a pele.", "Saúde", "Toxicidade aguda (cat. 4)", 3, "", ""),
    ("H314", "Provoca queimaduras na pele e lesões oculares graves.", "Saúde", "Corrosão/irritação", 4, "", ""),
    ("H315", "Provoca irritação cutânea.", "Saúde", "Corrosão/irritação", 2, "", ""),
    ("H317", "Pode provocar uma reação alérgica cutânea.", "Saúde", "Sensibilizante", 3, "", ""),
    ("H318", "Provoca lesões oculares graves.", "Saúde", "Corrosão/irritação", 3, "", ""),
    ("H319", "Provoca irritação ocular grave.", "Saúde", "Corrosão/irritação", 2, "", ""),
    ("H330", "Mortal por inalação.", "Saúde", "Toxicidade aguda (cat. 1-3)", 5, "", ""),
    ("H331", "Tóxico por inalação.", "Saúde", "Toxicidade aguda (cat. 1-3)", 4, "", ""),
    ("H332", "Nocivo por inalação.", "Saúde", "Toxicidade aguda (cat. 4)", 3, "", ""),
    ("H334", "Quando inalado, pode provocar sintomas de alergia ou de asma ou dificuldades respiratórias.", "Saúde", "Sensibilizante", 5, "", ""),
    ("H335", "Pode provocar irritação das vias respiratórias.", "Saúde", "STOT (exposição única)", 3, "", ""),
    ("H336", "Pode provocar sonolência ou vertigens.", "Saúde", "STOT (exposição única)", 2, "", ""),
    ("H340", "Pode provocar anomalias genéticas.", "Saúde", "CMR", 5, "1", "S"),
    ("H341", "Suspeito de provocar anomalias genéticas.", "Saúde", "CMR", 4, "2", "S"),
    ("H350", "Pode provocar cancro.", "Saúde", "CMR", 5, "1", "S"),
    ("H350i", "Pode provocar cancro por inalação.", "Saúde", "CMR", 5, "1", "S"),
    ("H351", "Suspeito de provocar cancro.", "Saúde", "CMR", 4, "2", "S"),
    ("H360", "Pode afetar a fertilidade ou o nascituro.", "Saúde", "CMR", 5, "1", "S"),
    ("H360F", "Pode afetar a fertilidade.", "Saúde", "CMR", 5, "1", "S"),
    ("H360D", "Pode afetar o nascituro.", "Saúde", "CMR", 5, "1", "S"),
    ("H360FD", "Pode afetar a fertilidade. Pode afetar o nascituro.", "Saúde", "CMR", 5, "1", "S"),
    ("H360Fd", "Pode afetar a fertilidade. Suspeito de afetar o nascituro.", "Saúde", "CMR", 5, "1", "S"),
    ("H360Df", "Pode afetar o nascituro. Suspeito de afetar a fertilidade.", "Saúde", "CMR", 5, "1", "S"),
    ("H361", "Suspeito de afetar a fertilidade ou o nascituro.", "Saúde", "CMR", 4, "2", "S"),
    ("H361f", "Suspeito de afetar a fertilidade.", "Saúde", "CMR", 4, "2", "S"),
    ("H361d", "Suspeito de afetar o nascituro.", "Saúde", "CMR", 4, "2", "S"),
    ("H361fd", "Suspeito de afetar a fertilidade. Suspeito de afetar o nascituro.", "Saúde", "CMR", 4, "2", "S"),
    ("H362", "Pode ser nocivo para as crianças alimentadas com leite materno.", "Saúde", "Efeitos na lactação", 3, "", "S"),
    ("H370", "Afeta os órgãos.", "Saúde", "STOT (exposição única)", 5, "", ""),
    ("H371", "Pode afetar os órgãos.", "Saúde", "STOT (exposição única)", 4, "", ""),
    ("H372", "Afeta os órgãos após exposição prolongada ou repetida.", "Saúde", "STOT (exposição repetida)", 5, "", ""),
    ("H373", "Pode afetar os órgãos após exposição prolongada ou repetida.", "Saúde", "STOT (exposição repetida)", 4, "", ""),
    ("H400", "Muito tóxico para os organismos aquáticos.", "Ambiente", "Perigoso para o ambiente aquático", 0, "", ""),
    ("H410", "Muito tóxico para os organismos aquáticos com efeitos duradouros.", "Ambiente", "Perigoso para o ambiente aquático", 0, "", ""),
    ("H411", "Tóxico para os organismos aquáticos com efeitos duradouros.", "Ambiente", "Perigoso para o ambiente aquático", 0, "", ""),
    ("H412", "Nocivo para os organismos aquáticos com efeitos duradouros.", "Ambiente", "Perigoso para o ambiente aquático", 0, "", ""),
    ("H413", "Pode provocar efeitos nocivos duradouros nos organismos aquáticos.", "Ambiente", "Perigoso para o ambiente aquático", 0, "", ""),
    ("H420", "Prejudica a saúde pública e o ambiente ao destruir o ozono na alta atmosfera.", "Ambiente", "Camada de ozono", 0, "", ""),
    ("EUH014", "Reage violentamente em contacto com a água.", "Suplementar", "Reatividade", 0, "", ""),
    ("EUH029", "Em contacto com a água liberta gases tóxicos.", "Suplementar", "Reatividade", 3, "", ""),
    ("EUH031", "Em contacto com ácidos liberta gases tóxicos.", "Suplementar", "Reatividade", 3, "", ""),
    ("EUH032", "Em contacto com ácidos liberta gases muito tóxicos.", "Suplementar", "Reatividade", 4, "", ""),
    ("EUH066", "Pode provocar secura da pele ou fissuras, por exposição repetida.", "Suplementar", "Corrosão/irritação", 2, "", ""),
    ("EUH070", "Tóxico por contacto com os olhos.", "Suplementar", "Toxicidade aguda (cat. 1-3)", 4, "", ""),
    ("EUH071", "Corrosivo para as vias respiratórias.", "Suplementar", "Corrosão/irritação", 3, "", ""),
    ("EUH202", "Cianoacrilato. Perigo. Cola-se à pele e aos olhos em poucos segundos. Manter fora do alcance das crianças.", "Suplementar", "Corrosão/irritação", 2, "", ""),
    ("EUH204", "Contém isocianatos. Pode provocar uma reação alérgica.", "Suplementar", "Sensibilizante", 3, "", ""),
    ("EUH208", "Contém <nome da substância sensibilizante>. Pode provocar uma reação alérgica.", "Suplementar", "Sensibilizante", 2, "", ""),
    ("EUH380", "Pode causar desregulação endócrina no ser humano.", "Saúde", "Desregulador endócrino (CLP 2023/707)", 5, "", "S"),
    ("EUH381", "Suspeito de causar desregulação endócrina no ser humano.", "Saúde", "Desregulador endócrino (CLP 2023/707)", 4, "", "S"),
    ("EUH430", "Pode causar desregulação endócrina no ambiente.", "Ambiente", "Desregulador endócrino (CLP 2023/707)", 0, "", ""),
    ("EUH431", "Suspeito de causar desregulação endócrina no ambiente.", "Ambiente", "Desregulador endócrino (CLP 2023/707)", 0, "", ""),
    ("EUH440", "Acumula-se no ambiente e nos organismos vivos, incluindo nos seres humanos.", "Ambiente", "PBT/mPmB (CLP 2023/707)", 0, "", ""),
    ("EUH441", "Acumula-se fortemente no ambiente e nos organismos vivos, incluindo nos seres humanos.", "Ambiente", "PBT/mPmB (CLP 2023/707)", 0, "", ""),
    ("EUH450", "Pode causar uma contaminação duradoura e difusa dos recursos hídricos.", "Ambiente", "PMT/mPmM (CLP 2023/707)", 0, "", ""),
    ("EUH451", "Pode causar uma contaminação muito duradoura e difusa dos recursos hídricos.", "Ambiente", "PMT/mPmM (CLP 2023/707)", 0, "", ""),
]

# ------------------------------------------------------------------------------------------ SVHC vigiadas (subconjunto da lista candidata)
SVHC = [
    ("Ftalato de bis(2-etil-hexilo) (DEHP)", "117-81-7", "Tóxico para a reprodução; desregulador endócrino", "Plastificante de PVC", "Anexo XIV; anexo XVII entrada 51"),
    ("Ftalato de dibutilo (DBP)", "84-74-2", "Tóxico para a reprodução; desregulador endócrino", "Plastificante de PVC, tintas", "Anexo XIV; anexo XVII entrada 51"),
    ("Ftalato de benzilo e butilo (BBP)", "85-68-7", "Tóxico para a reprodução; desregulador endócrino", "Plastificante de PVC", "Anexo XIV; anexo XVII entrada 51"),
    ("Ftalato de di-isobutilo (DIBP)", "84-69-5", "Tóxico para a reprodução; desregulador endócrino", "Plastificante", "Anexo XIV; anexo XVII entrada 51"),
    ("Bisfenol A (BPA)", "80-05-7", "Tóxico para a reprodução; desregulador endócrino", "Policarbonato, resinas epóxi, vernizes", "Reg. (UE) 2024/3190 (proibição em materiais em contacto com alimentos)"),
    ("Bisfenol AF (BPAF) e sais", "1478-61-1", "Tóxico para a reprodução; desregulador endócrino", "Fluoroelastómeros", "Incluído em 02/2026"),
    ("n-Hexano", "110-54-3", "Tóxico para a reprodução / efeitos neurotóxicos (preocupação equivalente)", "Desengordurantes, colas, solventes técnicos", "Incluído em 02/2026"),
    ("Octametilciclotetrassiloxano (D4)", "556-67-2", "PBT/mPmB", "Silicones, desmoldantes", "Anexo XVII entrada 70 (Reg. (UE) 2024/1328)"),
    ("Decametilciclopentassiloxano (D5)", "541-02-6", "PBT/mPmB", "Silicones, desmoldantes", "Anexo XVII entrada 70 (Reg. (UE) 2024/1328)"),
    ("Dodecametilciclohexassiloxano (D6)", "540-97-6", "PBT/mPmB", "Silicones, desmoldantes", "Anexo XVII entrada 70 (Reg. (UE) 2024/1328)"),
    ("2-Metil-1-(4-metiltiofenil)-2-morfolinopropan-1-ona", "71868-10-5", "Tóxico para a reprodução (Repr. 1B)", "Fotoiniciador de tintas e vernizes UV", ""),
    ("2-Benzil-2-dimetilamino-4'-morfolinobutirofenona", "119313-12-1", "Tóxico para a reprodução (Repr. 1B)", "Fotoiniciador de tintas UV", ""),
    ("UV-328 (benzotriazol fenólico)", "25973-55-1", "PBT/mPmB", "Absorvedor UV em plásticos", "Também POP (Convenção de Estocolmo, 2023)"),
    ("UV-327 (benzotriazol fenólico)", "3864-99-1", "mPmB", "Absorvedor UV em plásticos", ""),
    ("UV-320 (benzotriazol fenólico)", "3846-71-7", "PBT/mPmB", "Absorvedor UV em plásticos", ""),
    ("UV-350 (benzotriazol fenólico)", "36437-37-3", "mPmB", "Absorvedor UV em plásticos", ""),
    ("Parafinas cloradas de cadeia média (MCCP)", "85535-85-9", "PBT/mPmB", "Plastificante de PVC, lubrificantes", ""),
    ("Dechlorane Plus", "13560-89-9", "mPmB", "Retardador de chama", ""),
    ("Cromato de chumbo", "7758-97-6", "Cancerígeno e tóxico para a reprodução", "Pigmentos amarelos antigos", "Anexo XIV"),
    ("Chumbo", "7439-92-1", "Tóxico para a reprodução", "Estabilizantes de PVC antigos, soldaduras", "Anexo XVII entrada 63"),
    ("N-Metil-2-pirrolidona (NMP)", "872-50-4", "Tóxico para a reprodução", "Solventes, decapantes", "Anexo XVII entrada 71"),
    ("N,N-Dimetilacetamida (DMAC)", "127-19-5", "Tóxico para a reprodução", "Solventes", "Anexo XVII entrada 71"),
    ("Ácido perfluoro-hexanossulfónico (PFHxS) e sais", "355-46-4", "mPmB", "Tratamentos repelentes, espumas", "POP (Reg. (UE) 2019/1021)"),
    ("Ácido undecafluoro-hexanoico (PFHxA) e sais", "307-24-4", "Preocupação equivalente (persistência, mobilidade)", "Tratamentos repelentes", "Anexo XVII entrada 79 (Reg. (UE) 2024/2462)"),
]

# ------------------------------------------------------------------------------------------ inventário (42 produtos)
# (ID, nome, tipo, uso, processo, fornecedor, ID_forn, país, EEE, papel, qtd_kg_ano, stock_max_kg, emb_L, local,
#  frases H, pictogramas, palavra-sinal, Seveso 1, Seveso 2, SVHC declarado, anexo XVII, diisocianatos, PFAS, FCM, aspetos, estado, data aprovação)
UJ, RU, FIL, LAC, ART = ("Utilizador a jusante", "Importador (coberto por RU)", "Utilizador a jusante (importador: filial UE)",
                         "Importador — lacuna", "Destinatário de artigo")
INK, QL, LUB, GAS, AQH = "InkTec Ibérica, Lda.", "QuimiLeiria, Lda.", "LubriCentro, S.A.", "GasLis, S.A.", "AquaHigiene Lda."
# fornecedores de químicos: mestre em RG-SGA-11 (tbl_fornecedores / tbl_outros_fornecedores)
FORN_ID = {INK: "PQ-01", QL: "PQ-02", LUB: "PQ-03", GAS: "PQ-04", "CombustLeiria, Lda.": "PQ-05", "LabQuímica, Lda.": "PQ-06",
           "FoilTech S.r.l.": "PQ-07", AQH: "TOR-01", "FrioTec": "MAN-01"}
INV = [
    ("QUI-001", "Tinta serigráfica base solvente (PP/PE)", "Mistura", "Decoração de frascos e tampas de PP/HDPE", "SER", INK, "—", "Alemanha", "Sim", UJ, 780, 120, 5, "ARM-01",
     "H226; H332; H315; H318; H411", "GHS02; GHS05; GHS07; GHS09", "Perigo", "P5c", "E2", "Não", "—", "Não", "Não", "Não", "AA-015; AA-016; AA-005", "Aprovado", "2019-04-10"),
    ("QUI-002", "Tinta serigráfica UV (PET) — ensaio SS-002", "Mistura", "Decoração de frascos PET (ALT-2025-01)", "SER", INK, "—", "Alemanha", "Sim", UJ, 300, 50, 5, "ARM-01",
     "H360FD; H317; H302; H411", "GHS07; GHS08; GHS09", "Perigo", "E2", "—", "Sim", "Entrada 30 (só venda ao público — N.A.)", "Não", "Não", "Não", "AA-015", "Aprovado condicionado", "2025-06-10"),
    ("QUI-003", "Endurecedor poli-isocianato alifático (tinta 2K)", "Mistura", "Catalisador da tinta 2K das tampas (resistência química)", "SER", INK, "—", "Alemanha", "Sim", UJ, 70, 10, 1, "ARM-01",
     "H226; H317; H332; H335; H412; EUH204", "GHS02; GHS07", "Atenção", "P5c", "—", "Não", "Entrada 74 (diisocianatos ≥ 0,1%)", "Sim", "Não", "Não", "AA-015", "Aprovado condicionado", "2023-08-01"),
    ("QUI-004", "Diluente serigráfico (ciclo-hexanona / acetato de metoxipropilo)", "Mistura", "Ajuste de viscosidade das tintas", "SER", INK, "—", "Alemanha", "Sim", UJ, 350, 60, 5, "ARM-01",
     "H226; H332; H319; H336", "GHS02; GHS07", "Atenção", "P5c", "—", "Não", "—", "Não", "Não", "Não", "AA-015; AA-006", "Aprovado", "2019-04-10"),
    ("QUI-005", "Retardador (acetato de 2-butoxietilo)", "Substância", "Retardador de secagem das tintas", "SER", INK, "—", "Alemanha", "Sim", UJ, 40, 10, 1, "ARM-01",
     "H312; H332", "GHS07", "Atenção", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-015", "Aprovado", "2019-04-10"),
    ("QUI-006", "Solvente de limpeza de ecrãs (ésteres e cetonas)", "Mistura", "Limpeza de ecrãs e rodos", "SER", QL, "—", "Portugal", "Sim", UJ, 740, 150, 25, "ARM-01",
     "H225; H319; H336; EUH066", "GHS02; GHS07", "Perigo", "P5c", "—", "Não", "—", "Não", "Não", "Não", "AA-014; AA-006", "Aprovado", "2020-02-12"),
    ("QUI-007", "Emulsão fotossensível diazo", "Mistura", "Preparação de ecrãs (gravação)", "SER", INK, "—", "Alemanha", "Sim", UJ, 30, 10, 1, "ARM-01",
     "H317; H319", "GHS07", "Atenção", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-016", "Aprovado", "2019-04-10"),
    ("QUI-008", "Removedor de emulsão (periodato de sódio < 10%)", "Mistura", "Recuperação de ecrãs", "SER", INK, "—", "Alemanha", "Sim", UJ, 60, 20, 5, "ARM-03",
     "H315; H319", "GHS07", "Atenção", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-016", "Aprovado", "2019-04-10"),
    ("QUI-009", "Removedor de imagem fantasma (hidróxido de sódio 5–10%)", "Mistura", "Recuperação de ecrãs", "SER", INK, "—", "Alemanha", "Sim", UJ, 25, 10, 1, "ARM-03",
     "H290; H314", "GHS05", "Perigo", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-016", "Aprovado", "2019-04-10"),
    ("QUI-010", "Propano (flamejamento de PP/PE antes da serigrafia)", "Gás", "Tratamento superficial por chama", "SER", GAS, "—", "Portugal", "Sim", UJ, 1400, 180, None, "ARM-06",
     "H220; H280", "GHS02; GHS04", "Perigo", "Parte 2 — GPL", "—", "Não", "—", "Não", "Não", "Não", "AA-015", "Aprovado", "2018-01-15"),
    ("QUI-011", "Foil de hot stamping (poliéster metalizado com verniz)", "Artigo", "Decoração por hot foil", "HFS", "FoilTech S.r.l.", "—", "Itália", "Sim", ART, 12040, 2000, None, "ARM-12",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Por confirmar", "Sim", "AA-018; AA-019", "Aprovado condicionado", "2020-05-05"),
    ("QUI-012", "PP homopolímero e copolímero (granulado)", "Polímero", "Injeção de tampas e potes", "INJ", "Meridian Petrochemicals GmbH", "SUP-002", "Alemanha", "Sim", UJ, 180000, 30000, None, "ARM-10",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Sim", "AA-001; AA-003", "Aprovado", "2018-01-15"),
    ("QUI-013", "HDPE / LDPE / MDPE (granulado)", "Polímero", "Sopro de frascos e injeção", "SOP", "PolyGlobal Resins Corp", "SUP-001", "EUA", "Não", RU, 120000, 20000, None, "ARM-10",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Sim", "AA-001; AA-003", "Aprovado", "2018-01-15"),
    ("QUI-014", "PET e PETG (granulado)", "Polímero", "ISBM de frascos", "SOP", "NorthStar Polymer Solutions", "SUP-003", "EUA", "Não", FIL, 140000, 25000, None, "ARM-10",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Sim", "AA-001; AA-003", "Aprovado", "2018-01-15"),
    ("QUI-015", "HDPE-PCR e rPET (reciclado pós-consumo)", "Polímero", "Conteúdo reciclado (cosmética)", "SOP", "TransAtlantic Polymers plc", "SUP-004", "Reino Unido", "Não", LAC, 60000, 10000, None, "ARM-10",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-001; AA-003", "Aprovado condicionado", "2021-03-01"),
    ("QUI-016", "PP e PVC (compra spot)", "Polímero", "PVC: 4 SKUs legados (frascos)", "SOP", "Orient Polymer Industries", "SUP-005", "Singapura", "Não", LAC, 18000, 6000, None, "ARM-10",
     "", "—", "—", "—", "—", "Por confirmar", "Entradas 51 (ftalatos) e 63 (chumbo) — por confirmar", "Não", "Não", "Não", "AA-001", "Suspenso", "2022-06-20"),
    ("QUI-017", "HDPE e PET (granulado)", "Polímero", "Sopro e ISBM", "SOP", "Zenith Chemicals Group", "SUP-006", "Países Baixos", "Sim", UJ, 150000, 25000, None, "ARM-10",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Sim", "AA-001; AA-003", "Aprovado", "2018-01-15"),
    ("QUI-018", "PP, HDPE e LDPE (granulado)", "Polímero", "Injeção e sopro", "INJ", "Tarraco Petroquimica S.A.", "SUP-007", "Espanha", "Sim", UJ, 110000, 20000, None, "ARM-10",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Sim", "AA-001; AA-003", "Aprovado", "2018-01-15"),
    ("QUI-019", "PP-PG e PET-PG (grau farmacêutico)", "Polímero", "Linha farmacêutica", "INJ", "FarmaResin Especialidades Ltda", "SUP-009", "Brasil", "Não", RU, 25000, 5000, None, "ARM-10",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Sim", "AA-001", "Aprovado", "2026-04-15"),
    ("QUI-020", "HDPE-FG e PP-FG (grau alimentar)", "Polímero", "Linha alimentar", "INJ", "NutriPolímeros Ibéria S.A.", "SUP-010", "Espanha", "Sim", UJ, 45000, 8000, None, "ARM-10",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Sim", "AA-001", "Aprovado", "2026-04-15"),
    ("QUI-021", "Masterbatch de cor (pigmentos em PE/PP)", "Mistura", "Coloração", "INJ", "Lusomastic Polimeros S.A.", "SUP-008", "Portugal", "Sim", UJ, 16000, 3000, None, "ARM-10",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Sim", "AA-001", "Aprovado", "2018-01-15"),
    ("QUI-022", "Masterbatch aditivo deslizante / antiestático", "Mistura", "Aditivação de tampas", "INJ", "Lusomastic Polimeros S.A.", "SUP-008", "Portugal", "Sim", UJ, 800, 200, None, "ARM-10",
     "", "—", "—", "—", "—", "Por confirmar", "—", "Não", "Por confirmar", "Sim", "AA-001", "Aprovado condicionado", "2019-09-01"),
    ("QUI-023", "Masterbatch absorvedor UV (benzotriazol UV-329)", "Mistura", "Proteção UV de frascos PET", "SOP", "Lusomastic Polimeros S.A.", "SUP-008", "Portugal", "Sim", UJ, 400, 100, None, "ARM-10",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-001", "Aprovado", "2026-04-20"),
    ("QUI-024", "Spray desmoldante de silicone", "Mistura (aerossol)", "Desmoldagem em arranques de molde", "INJ", LUB, "—", "Portugal", "Sim", UJ, 90, 12, 0.5, "ARM-05",
     "H222; H229; H315; H336; H411", "GHS02; GHS07; GHS09", "Perigo", "P3a", "—", "Por confirmar", "Entrada 70 (D4/D5/D6) — confirmar", "Não", "Não", "Não", "AA-007; AA-012", "Aprovado condicionado", "2018-03-01"),
    ("QUI-025", "Spray antioxidante para moldes", "Mistura (aerossol)", "Proteção de moldes em armazém", "MAN", LUB, "—", "Portugal", "Sim", UJ, 60, 10, 0.5, "ARM-05",
     "H222; H229; H336; H412; EUH066", "GHS02; GHS07", "Perigo", "P3a", "—", "Não", "—", "Não", "Não", "Não", "AA-026", "Aprovado", "2018-03-01"),
    ("QUI-026", "Limpa-moldes desengordurante em aerossol (contém n-hexano)", "Mistura (aerossol)", "Limpeza de cavidades de molde", "MAN", LUB, "—", "Portugal", "Sim", UJ, 120, 15, 0.5, "ARM-05",
     "H222; H229; H315; H336; H361f; H373; H411", "GHS02; GHS07; GHS08; GHS09", "Perigo", "P3a", "—", "Sim", "—", "Não", "Não", "Não", "AA-026", "Aprovado condicionado", "2017-05-02"),
    ("QUI-027", "Óleo hidráulico mineral ISO VG 46", "Mistura", "Circuitos hidráulicos das máquinas", "MAN", LUB, "—", "Portugal", "Sim", UJ, 1800, 1000, 200, "ARM-02",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-009; AA-013", "Aprovado", "2018-01-15"),
    ("QUI-028", "Óleo de compressor sintético", "Mistura", "Compressores CMP-01/02", "UTL", LUB, "—", "Portugal", "Sim", UJ, 200, 200, 20, "ARM-02",
     "", "—", "—", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-021", "Aprovado", "2026-02-02"),
    ("QUI-029", "Fluido de arrefecimento (monoetilenoglicol 30–50%)", "Mistura", "Circuito de água gelada / termorreguladores", "UTL", LUB, "—", "Portugal", "Sim", UJ, 400, 400, 200, "ARM-02",
     "H302; H373", "GHS07; GHS08", "Atenção", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-023", "Aprovado", "2018-01-15"),
    ("QUI-030", "Trava-roscas anaeróbico (metacrilatos)", "Mistura", "Manutenção mecânica", "MAN", LUB, "—", "Portugal", "Sim", UJ, 3, 1, 0.05, "ARM-05",
     "H317; H319; H335; H412", "GHS07", "Atenção", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-026", "Aprovado", "2018-01-15"),
    ("QUI-031", "Adesivo cianoacrilato", "Mistura", "Manutenção e reparações", "MAN", LUB, "—", "Portugal", "Sim", UJ, 2, 0.5, 0.02, "ARM-05",
     "H315; H319; H335; EUH202", "GHS07", "Atenção", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-026", "Aprovado", "2018-01-15"),
    ("QUI-032", "Gasóleo (gerador e viaturas)", "Substância", "Combustível", "GER", "CombustLeiria, Lda.", "—", "Portugal", "Sim", UJ, 2600, 2500, 3000, "ARM-07",
     "H226; H304; H315; H332; H351; H373; H411", "GHS02; GHS07; GHS08; GHS09", "Perigo", "Parte 2 — Produtos petrolíferos", "—", "Não", "—", "Não", "Não", "Não", "AA-029", "Aprovado", "2018-01-15"),
    ("QUI-033", "Acetileno dissolvido (soldadura)", "Gás", "Oficina de manutenção", "MAN", GAS, "—", "Portugal", "Sim", UJ, 40, 16, None, "ARM-06",
     "H220; H230; H280", "GHS02; GHS04", "Perigo", "Parte 2 — Acetileno", "—", "Não", "—", "Não", "Não", "Não", "AA-026", "Aprovado", "2018-01-15"),
    ("QUI-034", "Oxigénio comprimido (soldadura)", "Gás", "Oficina de manutenção", "MAN", GAS, "—", "Portugal", "Sim", UJ, 60, 20, None, "ARM-06",
     "H270; H280", "GHS03; GHS04", "Perigo", "Parte 2 — Oxigénio", "—", "Não", "—", "Não", "Não", "Não", "AA-026", "Aprovado", "2018-01-15"),
    ("QUI-035", "Eletrólito de baterias (ácido sulfúrico 35–38%)", "Mistura", "Manutenção das baterias dos empilhadores", "MAN", LUB, "—", "Portugal", "Sim", UJ, 60, 50, 25, "ARM-09",
     "H290; H314", "GHS05", "Perigo", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-026", "Aprovado", "2018-01-15"),
    ("QUI-036", "Biocida da torre (isotiazolinonas CMIT/MIT) — TP11", "Mistura", "Tratamento da água da torre TR-01", "UTL", AQH, "—", "Portugal", "Sim", UJ, 600, 1000, 1000, "ARM-04",
     "H314; H317; H410; EUH071", "GHS05; GHS07; GHS09", "Perigo", "E1", "—", "Não", "—", "Não", "Não", "Não", "AA-023; AA-024", "Aprovado", "2018-01-15"),
    ("QUI-037", "Anti-incrustante / inibidor de corrosão (fosfonatos, pH ácido)", "Mistura", "Tratamento da água da torre TR-01", "UTL", AQH, "—", "Portugal", "Sim", UJ, 900, 200, 25, "ARM-04",
     "H319", "GHS07", "Atenção", "—", "—", "Não", "—", "Não", "Não", "Não", "AA-023", "Aprovado", "2018-01-15"),
    ("QUI-038", "Hipoclorito de sódio 12–14% (choque de Legionella)", "Mistura", "Desinfeção de choque da torre", "UTL", AQH, "—", "Portugal", "Sim", UJ, 500, 250, 25, "ARM-04",
     "H290; H314; H400; EUH031", "GHS05; GHS09", "Perigo", "E1", "—", "Não", "—", "Não", "Não", "Não", "AA-023", "Aprovado", "2021-07-01"),
    ("QUI-039", "R410A (fluido do chiller CH-01)", "Gás", "Refrigeração (em equipamento)", "UTL", "FrioTec", "—", "Portugal", "Sim", UJ, 3.2, 30, None, "ARM-11",
     "H280", "GHS04", "Atenção", "—", "—", "Não", "—", "Não", "Sim (HFC-125 — definição OCDE)", "Não", "AA-025", "Aprovado condicionado", "2015-06-01"),
    ("QUI-040", "Etanol 96% (laboratório)", "Substância", "Ensaios e limpeza de laboratório", "LAB", "LabQuímica, Lda.", "—", "Portugal", "Sim", UJ, 50, 20, 5, "ARM-08",
     "H225; H319", "GHS02; GHS07", "Perigo", "P5c", "—", "Não", "—", "Não", "Não", "Não", "AA-029", "Aprovado", "2026-05-02"),
    ("QUI-041", "Ácido acético glacial (simulante de migração 3%)", "Substância", "Ensaios de migração (linha alimentar)", "LAB", "LabQuímica, Lda.", "—", "Portugal", "Sim", UJ, 10, 5, 2.5, "ARM-08",
     "H226; H314", "GHS02; GHS05", "Perigo", "P5c", "—", "Não", "—", "Não", "Não", "Não", "AA-029", "Aprovado", "2026-05-02"),
    ("QUI-042", "Isopropanol (limpeza técnica e laboratório)", "Substância", "Limpeza de peças e superfícies", "SER", QL, "—", "Portugal", "Sim", UJ, 200, 50, 25, "ARM-01",
     "H225; H319; H336", "GHS02; GHS07", "Perigo", "P5c", "—", "Não", "—", "Não", "Não", "Não", "AA-014", "Aprovado", "2020-02-12"),
]

# teor de COV (fração m/m, da FDS secção 9 — 'teor de COV'); combustíveis ficam fora (0)
TEOR_COV = {"QUI-001": 0.40, "QUI-002": 0.0, "QUI-003": 0.30, "QUI-004": 1.0, "QUI-005": 1.0, "QUI-006": 1.0, "QUI-024": 0.60, "QUI-025": 0.70,
            "QUI-026": 0.90, "QUI-040": 1.0, "QUI-041": 1.0, "QUI-042": 1.0}


def _anual():
    prod, mm, fact, res = envdata.ambiente()
    return envdata.anual(fact, res, prod)


_A = _anual()
# tintas e solvente de limpeza: mesma fonte que RG-SGA-13 (tbl_dados_ambientais) e RG-SGA-19 — 72% das tintas são base solvente, 28% UV
QTD_ENV = {"QUI-001": round(_A["tinta_kg"] * 0.72), "QUI-002": round(_A["tinta_kg"] * 0.28), "QUI-006": round(_A["solvente_kg"])}


def resumo():
    """Totais do inventário usados por outros registos (fonte única: este ficheiro)."""
    cov = 0.0
    for r in INV:
        q = QTD_ENV.get(r[0], r[10])
        cov += q * TEOR_COV.get(r[0], 0)
    svhc = sum(1 for r in INV if r[19] == "Sim")
    pfas = sum(1 for r in INV if str(r[22]).startswith("Sim"))
    pc = sum(1 for r in INV if r[19] == "Por confirmar" or r[22] == "Por confirmar")
    return dict(cov_t=round(cov / 1000, 2), solvente_kg=QTD_ENV["QUI-006"], n_svhc=svhc, n_pfas=pfas, n_por_confirmar=pc,
                n_preocupantes=svhc + pfas, n_produtos=len(INV))


# ------------------------------------------------------------------------------------------ componentes perigosos (secção 3)
# (ID_Quimico, componente, CAS, CE, conc. mín %, conc. máx %, registo REACH, VLE de referência)
COMP = [
    ("QUI-001", "Ciclo-hexanona", "108-94-1", "203-631-1", 10, 25, "Indicado na FDS (secção 3)", "VLE-MP 10 ppm; VLE-CD 20 ppm (Dir. 2000/39/CE)"),
    ("QUI-001", "Acetato de 1-metoxi-2-propilo (PGMEA)", "108-65-6", "203-603-9", 10, 20, "Indicado na FDS (secção 3)", "VLE-MP 50 ppm; VLE-CD 100 ppm (Dir. 2000/39/CE)"),
    ("QUI-001", "Pigmentos orgânicos (mistura)", "—", "—", 5, 15, "Indicado na FDS (secção 3)", ""),
    ("QUI-002", "2-Metil-1-(4-metiltiofenil)-2-morfolinopropan-1-ona (fotoiniciador)", "71868-10-5", "400-600-6", 1, 3, "Indicado na FDS (secção 3)", ""),
    ("QUI-002", "Diacrilato de tripropilenoglicol (TPGDA)", "42978-66-5", "256-032-2", 10, 25, "Indicado na FDS (secção 3)", ""),
    ("QUI-002", "Acrilato de isobornilo", "5888-33-5", "227-561-6", 5, 10, "Indicado na FDS (secção 3)", ""),
    ("QUI-003", "Oligómeros de HDI (isocianurato)", "28182-81-2", "500-060-2", 60, 80, "Polímero — isento", ""),
    ("QUI-003", "Di-isocianato de hexametileno (HDI, monómero)", "822-06-0", "212-485-8", 0.1, 0.5, "Indicado na FDS (secção 3)", "Confirmar VLE na NP 1796 (diisocianatos)"),
    ("QUI-003", "Acetato de n-butilo", "123-86-4", "204-658-1", 15, 30, "Indicado na FDS (secção 3)", "VLE-MP 50 ppm; VLE-CD 150 ppm (Dir. (UE) 2019/1831)"),
    ("QUI-004", "Ciclo-hexanona", "108-94-1", "203-631-1", 40, 60, "Indicado na FDS (secção 3)", "VLE-MP 10 ppm; VLE-CD 20 ppm (Dir. 2000/39/CE)"),
    ("QUI-004", "Acetato de 1-metoxi-2-propilo (PGMEA)", "108-65-6", "203-603-9", 40, 60, "Indicado na FDS (secção 3)", "VLE-MP 50 ppm; VLE-CD 100 ppm (Dir. 2000/39/CE)"),
    ("QUI-005", "Acetato de 2-butoxietilo", "112-07-2", "203-933-3", 99, 100, "Indicado na FDS (secção 3)", "VLE-MP 20 ppm; VLE-CD 50 ppm (Dir. 2000/39/CE)"),
    ("QUI-006", "Acetato de etilo", "141-78-6", "205-500-4", 30, 50, "Indicado na FDS (secção 3)", "VLE-MP 200 ppm; VLE-CD 400 ppm (Dir. (UE) 2017/164)"),
    ("QUI-006", "Butanona (MEK)", "78-93-3", "201-159-0", 20, 30, "Indicado na FDS (secção 3)", "VLE-MP 200 ppm; VLE-CD 300 ppm (Dir. 2000/39/CE)"),
    ("QUI-006", "Acetato de 1-metoxi-2-propilo (PGMEA)", "108-65-6", "203-603-9", 20, 30, "Indicado na FDS (secção 3)", "VLE-MP 50 ppm; VLE-CD 100 ppm (Dir. 2000/39/CE)"),
    ("QUI-009", "Hidróxido de sódio", "1310-73-2", "215-185-5", 5, 10, "Indicado na FDS (secção 3)", "Confirmar VLE na NP 1796"),
    ("QUI-010", "Propano", "74-98-6", "200-827-9", 95, 100, "Indicado na FDS (secção 3)", ""),
    ("QUI-022", "Aditivo antiestático (amina etoxilada) — identidade a confirmar", "—", "—", 5, 20, "Não indicado — pedir", ""),
    ("QUI-023", "UV-329 (2-(2H-benzotriazol-2-il)-4-(1,1,3,3-tetrametilbutil)fenol)", "3147-75-9", "221-573-5", 10, 20, "Indicado na FDS (secção 3)", ""),
    ("QUI-024", "Hidrocarbonetos C6-C7 (propulsor/solvente)", "—", "927-510-4", 30, 50, "Indicado na FDS (secção 3)", ""),
    ("QUI-024", "Polidimetilsiloxano", "63148-62-9", "—", 1, 5, "Polímero — isento", ""),
    ("QUI-024", "Decametilciclopentassiloxano (D5) — impureza declarada < 0,1%", "541-02-6", "208-764-9", 0, 0.09, "Indicado na FDS (secção 3)", ""),
    ("QUI-026", "n-Hexano", "110-54-3", "203-777-6", 5, 10, "Indicado na FDS (secção 3)", "VLE-MP 20 ppm (Dir. 2006/15/CE)"),
    ("QUI-026", "Acetona", "67-64-1", "200-662-2", 30, 50, "Indicado na FDS (secção 3)", "VLE-MP 500 ppm (Dir. 2000/39/CE)"),
    ("QUI-026", "Propano/butano (propulsor)", "68476-85-7", "270-704-2", 30, 40, "Indicado na FDS (secção 3)", ""),
    ("QUI-029", "Etano-1,2-diol (monoetilenoglicol)", "107-21-1", "203-473-3", 30, 50, "Indicado na FDS (secção 3)", "VLE-MP 20 ppm; VLE-CD 40 ppm; pele (Dir. 2000/39/CE)"),
    ("QUI-032", "Combustíveis para motores diesel", "68334-30-5", "269-822-7", 93, 100, "Indicado na FDS (secção 3)", ""),
    ("QUI-035", "Ácido sulfúrico", "7664-93-9", "231-639-5", 35, 38, "Indicado na FDS (secção 3)", "VLE-MP 0,05 mg/m³ (névoas, fração torácica; Dir. 2009/161/UE)"),
    ("QUI-036", "Mistura CMIT/MIT (3:1)", "55965-84-9", "611-341-5", 1, 1.5, "Substância ativa aprovada (Reg. 528/2012)", ""),
    ("QUI-038", "Hipoclorito de sódio", "7681-52-9", "231-668-3", 12, 14, "Indicado na FDS (secção 3)", ""),
    ("QUI-040", "Etanol", "64-17-5", "200-578-6", 96, 100, "Indicado na FDS (secção 3)", "Confirmar VLE na NP 1796"),
    ("QUI-041", "Ácido acético", "64-19-7", "200-580-7", 99, 100, "Indicado na FDS (secção 3)", "VLE-MP 10 ppm; VLE-CD 20 ppm (Dir. (UE) 2017/164)"),
    ("QUI-042", "Propan-2-ol", "67-63-0", "200-661-7", 99, 100, "Indicado na FDS (secção 3)", "Confirmar VLE na NP 1796"),
]

# ------------------------------------------------------------------------------------------ verificação das FDS
FDS_CHK = ["C01_Lingua_PT", "C02_Formato_2020_878", "C03_Identificacao_Coerente", "C04_Contacto_Emergencia", "C05_Sec2_Igual_Rotulo",
           "C06_Sec3_Composicao", "C07_Sec8_VLE_EPI", "C08_Sec11_Toxicologia", "C09_Sec12_Ecologia", "C10_Uso_Identificado",
           "C11_CE_Anexo", "C12_Sec15_Regulamentacao"]
FDS_Q = ["Em português (REACH art. 31.º, n.º 5)?",
         "16 secções e subsecções obrigatórias do anexo II na redação do Reg. (UE) 2020/878 (em vigor desde 01/01/2023)?",
         "Nome comercial, fornecedor e UFI (se aplicável) coincidem com o rótulo e com a encomenda?",
         "Secção 1.4 com telefone de emergência (em Portugal: CIAV 800 250 250)?",
         "Classificação, pictogramas, palavra-sinal e frases H/P da secção 2 iguais ao rótulo recebido?",
         "Secção 3 com identificadores (CAS/CE), intervalos de concentração, n.º de registo e SVHC ≥ 0,1%?",
         "Secção 8 com VLE/DNEL e EPI específicos (material das luvas, tipo de filtro)?",
         "Secção 11 completa, incl. 11.2 (desregulação endócrina) do Reg. 2020/878?",
         "Secção 12 completa, incl. 12.5 (PBT/mPmB) e 12.6 (desregulação endócrina)?",
         "A utilização da Plasticom está nas utilizações identificadas (1.2) ou não desaconselhada?",
         "Se substância registada ≥ 10 t e perigosa: tem cenários de exposição em anexo (FDS alargada)? (N.A. se não aplicável)",
         "Secção 15 indica restrições (anexo XVII), autorização (anexo XIV), SVHC e legislação nacional?"]
# (ID_FDS, ID_Quimico, data receção, data FDS, versão, 12 respostas S/N/NA, disponível no posto, pedido fornecedor, verificado por)
FDS = [
    ("FDS-001", "QUI-001", "2026-05-14", "2026-05-12", "7.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-002", "QUI-002", "2026-05-14", "2026-05-12", "4.1", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-003", "QUI-003", "2025-09-10", "2025-08-28", "5.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-004a", "QUI-004", "2021-06-01", "2021-03-15", "3.0", "S N S S S S S N N S NA S", "Sim", "2026-09-03", TEC_QA),
    ("FDS-005", "QUI-005", "2021-06-01", "2021-02-20", "2.2", "S N S S S S S N N S NA S", "Sim", "2026-09-03", TEC_QA),
    ("FDS-006a", "QUI-006", "2022-11-10", "2022-10-04", "4.0", "S N S S S S S N N S S S", "Não", "", TEC_QA),
    ("FDS-006b", "QUI-006", "2026-03-02", "2026-02-20", "5.0", "S S S S S S S S S S S S", "Sim", "", TEC_QA),
    ("FDS-007", "QUI-007", "2025-04-02", "2025-03-11", "3.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-008", "QUI-008", "2024-07-15", "2024-06-30", "2.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-009", "QUI-009", "2024-07-15", "2024-06-30", "2.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-010", "QUI-010", "2025-01-20", "2024-11-05", "9.0", "S S S S S S S S S S S S", "Sim", "", TEC_QA),
    ("FDS-012", "QUI-012", "2025-07-10", "2025-05-02", "3.0", "S S S S S S S S S S NA S", "Não", "", TEC_QA),
    ("FDS-013", "QUI-013", "2026-02-20", "2026-01-10", "6.0", "N S S S S S S S S S NA S", "Não", "2026-02-25", TEC_QA),
    ("FDS-014", "QUI-014", "2026-03-05", "2025-12-01", "4.0", "S S S S S S S S S S NA S", "Não", "", TEC_QA),
    ("FDS-015", "QUI-015", "2025-01-15", "2024-12-12", "2.0", "S S S S S S S S S S NA N", "Não", "2026-07-20", TEC_QA),
    ("FDS-017", "QUI-017", "2026-02-28", "2026-01-15", "5.0", "S S S S S S S S S S NA S", "Não", "", TEC_QA),
    ("FDS-018", "QUI-018", "2025-09-01", "2025-06-30", "3.0", "S S S S S S S S S S NA S", "Não", "", TEC_QA),
    ("FDS-019", "QUI-019", "2026-03-20", "2026-02-10", "2.0", "S S S S S S S S S S NA S", "Não", "", TEC_QA),
    ("FDS-020", "QUI-020", "2026-07-01", "2026-06-15", "3.0", "S S S S S S S S S S NA S", "Não", "", TEC_QA),
    ("FDS-021", "QUI-021", "2026-01-20", "2025-12-18", "8.0", "S S S S S S S S S S NA S", "Não", "", TEC_QA),
    ("FDS-022", "QUI-022", "2019-09-01", "2019-06-12", "1.0", "S N S S S N S N N S NA N", "Não", "2026-09-10", TEC_QA),
    ("FDS-023", "QUI-023", "2026-04-12", "2026-03-30", "1.0", "S S S S S S S S S S NA S", "Não", "", TEC_QA),
    ("FDS-024", "QUI-024", "2024-02-10", "2023-11-20", "6.0", "S S S S S N S S S S NA S", "Sim", "2026-09-10", TEC_QA),
    ("FDS-025", "QUI-025", "2024-02-10", "2023-11-20", "4.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-026", "QUI-026", "2026-03-18", "2026-03-01", "7.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-027", "QUI-027", "2025-10-01", "2025-09-12", "5.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-028", "QUI-028", "2026-02-02", "2025-11-30", "2.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-029", "QUI-029", "2025-03-03", "2025-01-20", "4.0", "S S S S S S S S S S S S", "Sim", "", TEC_QA),
    ("FDS-030", "QUI-030", "2024-05-06", "2024-03-01", "5.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-031", "QUI-031", "2024-05-06", "2024-02-15", "3.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-032", "QUI-032", "2025-07-01", "2025-05-20", "12.0", "S S S S S S S S S S S S", "Sim", "", TEC_QA),
    ("FDS-033", "QUI-033", "2025-01-20", "2024-10-10", "6.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-034", "QUI-034", "2025-01-20", "2024-10-10", "6.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-035", "QUI-035", "2025-02-11", "2024-12-01", "5.0", "S S S S S S S S S S S S", "Sim", "", TEC_QA),
    ("FDS-036", "QUI-036", "2026-06-09", "2026-05-15", "6.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-037", "QUI-037", "2026-06-09", "2026-05-15", "3.0", "S S S S S S S S S S NA S", "Sim", "", TEC_QA),
    ("FDS-038", "QUI-038", "2026-06-09", "2026-04-02", "8.0", "S S S S S S S S S S S S", "Sim", "", TEC_QA),
    ("FDS-039", "QUI-039", "2025-11-18", "2025-09-01", "5.0", "S S S S S S S S S S NA S", "Não", "", TEC_QA),
    ("FDS-040", "QUI-040", "2026-05-02", "2026-01-12", "10.0", "S S S S S S S S S S S S", "Sim", "", TEC_QA),
    ("FDS-041", "QUI-041", "2026-05-02", "2025-11-03", "7.0", "S S S S S S S S S S S S", "Sim", "", TEC_QA),
    ("FDS-042", "QUI-042", "2025-12-09", "2025-10-20", "9.0", "S S S S S S S S S S S S", "Sim", "", TEC_QA),
]

# ------------------------------------------------------------------------------------------ cenários de exposição
# (ID, ID_Quimico, ID_FDS, substância do CE, título, descritores do fornecedor, uso real, PROC real, condições do CE (MGR/CO),
#  condições reais, método, resultado, ação, data implementação, responsável)
CE = [
    ("CE-01", "QUI-006", "FDS-006b", "Acetato de 1-metoxi-2-propilo (PGMEA)", "Utilização industrial em agentes de limpeza", "SU3; PROC 10; ERC 4",
     "Limpeza manual de ecrãs com pano na SS-001, ≈ 2 h por turno", "PROC 10",
     "Sem ventilação local (LEV) limitar a < 1 h/dia; acima de 1 h/dia: LEV com eficácia ≥ 80%; luvas de butilo (EN ISO 374).",
     "2 h/turno sem LEV na SS-001 (a SS-002 tem mesa aspirante); luvas de nitrilo.", "Comparação direta", "Não coberto",
     "Implementar condições do CE", None, PROD),
    ("CE-02", "QUI-004", "FDS-004a", "Ciclo-hexanona", "Utilização industrial em revestimentos e tintas", "SU3; PROC 5, 8b, 10; ERC 4",
     "Mistura no tinteiro e ajuste de viscosidade na SS-001 e SS-002", "PROC 5; PROC 8b",
     "LEV no ponto de mistura ou duração < 15 min/dia; luvas de butilo; óculos.", "Adição com doseador (< 10 min/turno); SS-002 com captação; luvas de nitrilo.",
     "Escalonamento (scaling)", "Parcialmente coberto", "Implementar condições do CE", None, PROD),
    ("CE-03", "QUI-042", "FDS-042", "Propan-2-ol", "Utilização industrial como agente de limpeza", "SU3; PROC 10, 13; ERC 4",
     "Limpeza de peças e superfícies com pano", "PROC 10", "Ventilação geral (3–5 renovações/h); duração ≤ 4 h; luvas.",
     "Ventilação geral mecânica; < 1 h/dia; luvas de nitrilo.", "Comparação direta", "Coberto", "Nenhuma", None, PROD),
    ("CE-04", "QUI-040", "FDS-040", "Etanol", "Utilização em laboratório", "SU22; PROC 15; ERC 8a", "Ensaios de migração e limpeza no laboratório", "PROC 15",
     "Utilização em pequena escala em laboratório; ventilação geral.", "Hotte e ventilação geral; < 0,5 L/dia.", "Comparação direta", "Coberto", "Nenhuma", None, QUA),
    ("CE-05", "QUI-041", "FDS-041", "Ácido acético", "Utilização em laboratório", "SU22; PROC 15, 9", "Preparação do simulante 3% na hotte", "PROC 15",
     "Hotte; luvas e óculos; ≤ 1 L por operação.", "Hotte; luvas de nitrilo; óculos; ≈ 0,1 L por operação.", "Comparação direta", "Coberto", "Nenhuma", None, QUA),
    ("CE-06", "QUI-032", "FDS-032", "Combustíveis para motores diesel", "Utilização como combustível — industrial", "SU3; PROC 1, 8b, 16; ERC 7",
     "Abastecimento do gerador e viaturas a partir do depósito", "PROC 8b; PROC 16", "Transferência em sistemas dedicados; luvas; evitar contacto cutâneo repetido.",
     "Bomba com pistola e corte automático; luvas.", "Comparação direta", "Coberto", "Nenhuma", None, MAN),
    ("CE-07", "QUI-029", "FDS-029", "Etano-1,2-diol", "Utilização industrial em fluidos funcionais", "SU3; PROC 1, 2, 8a; ERC 7",
     "Enchimento e reposição do circuito de água gelada", "PROC 8a", "Luvas; ventilação geral; evitar formação de névoas.", "Luvas de nitrilo; operação ocasional.",
     "Comparação direta", "Coberto", "Nenhuma", None, MAN),
    ("CE-08", "QUI-035", "FDS-035", "Ácido sulfúrico", "Manutenção de baterias", "SU3; PROC 9, 8b; ERC 7",
     "Reposição de eletrólito nas baterias dos empilhadores", "PROC 9", "Luvas resistentes a ácidos; viseira facial completa; ventilação da sala de carga.",
     "Luvas de PVC e óculos (sem viseira); sala ventilada.", "Comparação direta", "Parcialmente coberto", "Implementar condições do CE", None, MAN),
    ("CE-09", "QUI-026", "FDS-026", "n-Hexano", "Utilização profissional em produtos de limpeza em aerossol", "SU22; PROC 11; ERC 8a",
     "Pulverização das cavidades do molde na máquina, ≈ 30 min por mudança", "PROC 7",
     "PROC 11 (profissional) com ventilação; uso industrial (PROC 7) não coberto pelo CE do fornecedor.", "Pulverização em máquina sem LEV, ventilação geral.",
     "Pedido ao fornecedor", "Não coberto", "Substituir produto/fornecedor", None, MAN),
    ("CE-10", "QUI-010", "FDS-010", "Propano", "Utilização industrial como combustível", "SU3; PROC 1, 2; ERC 7", "Flamejamento em linha (queimadores fixos)", "PROC 2",
     "Sistema fechado; verificação de fugas; ventilação.", "Sistema fechado com corte de chama; verificação anual.", "Comparação direta", "Coberto", "Nenhuma", None, MAN),
]

# ------------------------------------------------------------------------------------------ registo / importação
# (ID, ID_Forn, fornecedor, país, EEE, material, qtd_t, importador legal, RU, data carta RU, Plasticom na lista do RU,
#  substâncias a registar (monómeros/aditivos ≥ 1 t), observação)
IMP = [
    ("IMP-01", "SUP-001", "PolyGlobal Resins Corp", "EUA", "Não", "HDPE / LDPE / MDPE", 120, "Plasticom", "PolyGlobal EU OR B.V. (Países Baixos)", "2026-01-15", "Sim",
     "Etileno (74-85-1); 1-hexeno (592-41-6) — cobertos pelo registo do RU", "Carta do RU com a Plasticom na lista de importadores cobertos e tonelagem."),
    ("IMP-02", "SUP-003", "NorthStar Polymer Solutions", "EUA", "Não", "PET e PETG", 140, "NorthStar Polymer Europe B.V.", "", "", "",
     "Ácido tereftálico (100-21-0); etilenoglicol (107-21-1) — registados pela filial UE", "Fatura e incoterm DAP pela filial UE: a Plasticom não é o importador."),
    ("IMP-03", "SUP-004", "TransAtlantic Polymers plc", "Reino Unido", "Não", "HDPE-PCR e rPET", 60, "Plasticom", "", "", "Não",
     "Monómeros do rPET/HDPE e aditivos residuais — por confirmar", "Após o Brexit o Reino Unido é país terceiro; a isenção de substâncias recuperadas (art. 2.º, n.º 7, d) só se aplica à recuperação na UE. Pedido de RU enviado em 20/07/2026 sem resposta."),
    ("IMP-04", "SUP-005", "Orient Polymer Industries", "Singapura", "Não", "PP e PVC (spot)", 18, "Plasticom", "", "", "Não",
     "Monocloreto de vinilo (75-01-4); plastificante do PVC (≈ 1,8 t/ano ≥ 1 t) — identidade desconhecida", "Compra spot sem RU e sem declaração de composição: compras suspensas (PAM-26-28)."),
    ("IMP-05", "SUP-009", "FarmaResin Especialidades Ltda", "Brasil", "Não", "PP-PG e PET-PG", 25, "Plasticom", "FarmaResin EU OR, Lda. (Portugal)", "2025-11-03", "Sim",
     "Propileno (115-07-1); ácido tereftálico; etilenoglicol — cobertos pelo registo do RU", ""),
    ("IMP-06", "SUP-002", "Meridian Petrochemicals GmbH", "Alemanha", "Sim", "PP, PP-PCR", 180, "—", "", "", "", "—", ""),
    ("IMP-07", "SUP-006", "Zenith Chemicals Group", "Países Baixos", "Sim", "HDPE, PET", 150, "—", "", "", "", "—", ""),
    ("IMP-08", "SUP-007", "Tarraco Petroquimica S.A.", "Espanha", "Sim", "PP, HDPE, LDPE", 110, "—", "", "", "", "—", ""),
    ("IMP-09", "SUP-008", "Lusomastic Polimeros S.A.", "Portugal", "Sim", "Masterbatches", 17.2, "—", "", "", "", "—", ""),
    ("IMP-10", "SUP-010", "NutriPolímeros Ibéria S.A.", "Espanha", "Sim", "HDPE-FG, PP-FG", 45, "—", "", "", "", "—", ""),
]

# ------------------------------------------------------------------------------------------ declarações de fornecedores
# (ID, ID_Forn, fornecedor, material, data, n.º entradas da lista coberta, SVHC ≥ 0,1%, metais PPWR ≤ 100 mg/kg, PFAS, BPA, ftalatos, DoC FCM)
DEC = [
    ("DEC-01", "SUP-001", "PolyGlobal Resins Corp", "HDPE / LDPE / MDPE", "2026-02-20", 253, "Não", "Sim", "Não", "Não", "Não", "Sim"),
    ("DEC-02", "SUP-002", "Meridian Petrochemicals GmbH", "PP, PP-PCR", "2025-07-10", 250, "Não", "Sim", "Não", "Não", "Não", "Sim"),
    ("DEC-03", "SUP-003", "NorthStar Polymer Solutions", "PET, PETG", "2026-03-05", 253, "Não", "Sim", "Não", "Não", "Não", "Sim"),
    ("DEC-04", "SUP-004", "TransAtlantic Polymers plc", "HDPE-PCR, rPET", "2025-01-15", 247, "Não", "Sim", "Não", "Não", "Não", "N.A."),
    ("DEC-05", "SUP-005", "Orient Polymer Industries", "PP, PVC", "", None, "Por confirmar", "Por confirmar", "Por confirmar", "Por confirmar", "Por confirmar", "N.A."),
    ("DEC-06", "SUP-006", "Zenith Chemicals Group", "HDPE, PET", "2026-02-28", 253, "Não", "Sim", "Não", "Não", "Não", "Sim"),
    ("DEC-07", "SUP-007", "Tarraco Petroquimica S.A.", "PP, HDPE, LDPE", "2025-09-01", 250, "Não", "Sim", "Não", "Não", "Não", "Sim"),
    ("DEC-08", "SUP-008", "Lusomastic Polimeros S.A.", "Masterbatch de cor", "2026-01-20", 251, "Não", "Sim", "Não", "Não", "Não", "Sim"),
    ("DEC-09", "SUP-008", "Lusomastic Polimeros S.A.", "Masterbatch deslizante/antiestático", "", None, "Por confirmar", "Sim", "Por confirmar", "Não", "Não", "Sim"),
    ("DEC-10", "SUP-008", "Lusomastic Polimeros S.A.", "Masterbatch absorvedor UV (UV-329)", "2026-04-12", 253, "Não", "Sim", "Não", "Não", "Não", "N.A."),
    ("DEC-11", "SUP-009", "FarmaResin Especialidades Ltda", "PP-PG, PET-PG", "2026-03-20", 253, "Não", "Sim", "Não", "Não", "Não", "N.A."),
    ("DEC-12", "SUP-010", "NutriPolímeros Ibéria S.A.", "HDPE-FG, PP-FG", "2026-07-01", 253, "Não", "Sim", "Não", "Não", "Não", "Sim"),
    ("DEC-13", "PQ-07", "FoilTech S.r.l.", "Foil de hot stamping", "2025-11-18", 251, "Não", "Sim", "Por confirmar", "Não", "Não", "N.A."),
    ("DEC-14", "PQ-01", "InkTec Ibérica, Lda.", "Tintas serigráficas (solvente, UV, 2K)", "2026-05-12", 253, "Sim (tinta UV: 71868-10-5 na mistura)", "Sim", "Não", "Não", "Não", "N.A."),
]

# ------------------------------------------------------------------------------------------ métodos de avaliação de risco
VOLAT = [("Baixa — sólido não pulverulento, granulado ou líquido com PE > 150 °C", 1), ("Média — líquido com PE 50–150 °C ou pó grosso", 10),
         ("Alta — líquido com PE < 50 °C, aerossol, gás ou pó fino", 100)]
PROCED = [("Fechado permanente", 0.001), ("Fechado com aberturas regulares", 0.05), ("Aberto (sem dispersão particular)", 0.5), ("Dispersivo (pulverização, limpeza de grandes superfícies)", 1)]
PROT = [("Confinamento ou captação envolvente (hotte, cabine)", 0.001), ("Captação localizada (mesa aspirante, fenda, braço)", 0.1),
        ("Ventilação geral mecânica verificada", 0.7), ("Sem ventilação mecânica / ventilação natural", 1), ("Trabalho no exterior", 0.7)]
SUPERF = [("Sem contacto possível", 0), ("Uma mão", 1), ("Duas mãos", 2), ("Mãos e antebraços", 3), ("Membros superiores e tronco / rosto", 10)]
FREQ = [("Ocasional (< 30 min/dia)", 1), ("Intermitente (30 min–2 h/dia)", 2), ("Frequente (2–6 h/dia)", 5), ("Permanente (> 6 h/dia)", 10)]
V, P, PR, S, F = ({k: k for k, _ in x} for x in (VOLAT, PROCED, PROT, SUPERF, FREQ))
vB, vM, vA = [k for k, _ in VOLAT]
pF, pFA, pA, pD = [k for k, _ in PROCED]
cE, cL, cV, cN, cX = [k for k, _ in PROT]
s0, s1, s2, s3, s4 = [k for k, _ in SUPERF]
f1, f2, f3, f4 = [k for k, _ in FREQ]

# (ID, ID_Quimico, agente (se não inventariado), posto/tarefa, processo, função, n.º trab., classe manual, volatilidade, procedimento, proteção,
#  superfície, frequência, EPI, medidas existentes, ID medição, medidas adicionais, risco residual, responsável, prazo, data, avaliador)
RISCO = [
    ("ARQ-01", "QUI-001", "", "SS-001/SS-002 — enchimento do tinteiro e impressão", "SER", OP_SER, 8, None, vM, pA, cL, s2, f3,
     "Luvas de nitrilo EN ISO 374; óculos", "Mesa aspirante na SS-002; tampas nos recipientes", "MVLE-2025-02; MVLE-2025-03", "Captação localizada na SS-001 (PAM-26-31)", "Médio", PROD, "2027-03-02", "2024-03-15", SGA),
    ("ARQ-02", "QUI-002", "", "SS-002 — impressão e limpeza com tinta UV (ensaio)", "SER", OP_SER, 3, None, vB, pA, cL, s2, f2,
     "Luvas de nitrilo 0,4 mm; óculos; bata", "Mesa aspirante; acesso limitado a 3 operadores", "", "Substituir por tinta UV sem fotoiniciadores Repr. 1B (PAM-26-29); lista de trabalhadores expostos (DL 301/2000)", "Alto", RD, "2026-12-31", "2026-06-12", SGA),
    ("ARQ-03", "QUI-003", "", "Mistura da tinta 2K (endurecedor com diisocianatos)", "SER", OP_SER, 8, None, vM, pA, cL, s2, f1,
     "Luvas de butilo; óculos; semimáscara A2 na mistura", "Formação diisocianatos (entrada 74); mistura na mesa aspirante", "MVLE-2026-01", "Formar os 2 operadores novos (PAM-26-32)", "Médio", RH, "2026-10-31", "2026-02-10", SGA),
    ("ARQ-04", "QUI-004", "", "Ajuste de viscosidade com diluente", "SER", OP_SER, 8, None, vM, pA, cV, s1, f1,
     "Luvas de nitrilo; óculos", "Doseador; recipientes fechados", "MVLE-2025-02", "Luvas de butilo conforme CE-02", "Baixo", PROD, "2026-12-31", "2024-03-15", SGA),
    ("ARQ-05", "QUI-006", "", "SS-001 — limpeza manual de ecrãs com pano (2 h/turno)", "SER", OP_SER, 4, None, vA, pD, cV, s3, f3,
     "Luvas de nitrilo; óculos", "Recipientes de segurança com tampa; panos em contentor fechado", "MVLE-2025-01", "Mesa aspirante na SS-001 e luvas de butilo (CE-01, PAM-26-31)", "Alto", PROD, "2027-03-02", "2024-03-15", SGA),
    ("ARQ-06", "QUI-006", "", "SS-002 — limpeza de ecrãs em mesa aspirante", "SER", OP_SER, 4, None, vA, pA, cL, s2, f2,
     "Luvas de butilo; óculos", "Mesa aspirante com verificação anual", "MVLE-2025-04", "", "Baixo", PROD, "", "2024-03-15", SGA),
    ("ARQ-07", "QUI-009", "", "Recuperação de ecrãs com removedor alcalino", "SER", OP_SER, 2, None, vB, pA, cV, s2, f1,
     "Luvas de neopreno; viseira; avental", "Lava-olhos junto à cabine de lavagem", "", "", "Baixo", PROD, "", "2024-03-15", SGA),
    ("ARQ-08", "QUI-024", "", "Pulverização de desmoldante no molde", "INJ", OP_INJ, 12, None, vA, pD, cV, s1, f1,
     "Luvas de nitrilo", "Uso só no arranque; lata de 0,5 L", "", "Confirmar D4/D5/D6 (PAM-26-34)", "Médio", MAN, "2026-11-30", "2025-01-20", SGA),
    ("ARQ-09", "QUI-026", "", "Limpeza de cavidades de molde com aerossol (n-hexano)", "MAN", TEC_MAN, 6, None, vA, pD, cV, s2, f2,
     "Luvas de nitrilo; óculos", "Nenhuma específica", "MVLE-2026-03", "Substituir por limpa-moldes sem n-hexano (PAM-26-30)", "Alto", MAN, "2026-12-15", "2026-09-15", SGA),
    ("ARQ-10", "QUI-032", "", "Abastecimento de gasóleo (gerador e viaturas)", "GER", OP_ARM, 4, None, vB, pA, cX, s1, f1,
     "Luvas de nitrilo", "Bomba com corte automático; bacia do depósito", "", "", "Baixo", LOG, "", "2025-01-20", SGA),
    ("ARQ-11", "QUI-035", "", "Reposição de eletrólito nas baterias", "MAN", TEC_MAN, 3, None, vB, pA, cV, s1, f1,
     "Luvas de PVC; óculos", "Sala de carga ventilada; lava-olhos", "", "Viseira facial completa (CE-08)", "Médio", MAN, "2026-10-31", "2025-01-20", SGA),
    ("ARQ-12", "QUI-036", "", "Ligação do IBC de biocida ao doseador", "UTL", TEC_UTL, 3, None, vB, pFA, cX, s1, f1,
     "Luvas de nitrilo; viseira; avental", "Doseamento automático; bacia de retenção", "", "", "Baixo", MAN, "", "2025-06-10", SGA),
    ("ARQ-13", "QUI-038", "", "Desinfeção de choque com hipoclorito (verter manualmente)", "UTL", TEC_UTL, 3, None, vM, pA, cX, s2, f1,
     "Luvas de nitrilo; óculos", "Operação trimestral no exterior", "", "Bomba doseadora para o choque; separar do anti-incrustante (PAM-26-33)", "Alto", MAN, "2026-10-31", "2025-06-10", SGA),
    ("ARQ-14", "QUI-041", "", "Preparação do simulante de migração (ácido acético)", "LAB", TEC_QA, 2, None, vM, pA, cE, s1, f1,
     "Luvas de nitrilo; óculos", "Hotte verificada anualmente", "", "", "Baixo", QUA, "", "2026-05-10", SGA),
    ("ARQ-15", "QUI-029", "", "Enchimento do circuito com glicol", "UTL", TEC_UTL, 3, None, vB, pA, cV, s1, f1,
     "Luvas de nitrilo", "Bomba de trasfega", "", "", "Baixo", MAN, "", "2025-06-10", SGA),
    ("ARQ-16", "QUI-013", "", "Carga de tremonhas e transferência pneumática de granulado", "REC", OP_ARM, 6, None, vB, pFA, cV, s1, f3,
     "Luvas", "Transporte pneumático fechado; aspiração nos pontos de descarga", "", "Programa OCS (perdas de granulado)", "Baixo", PROD, "", "2025-01-20", SGA),
    ("ARQ-17", "", "Fumos de moldação do PET (acetaldeído gerado no processo)", "Purga e arranque das ISBM", "SOP", OP_SOP, 10, 4, vA, pFA, cV, s0, f2,
     "—", "Ventilação geral; purga para contentor", "MVLE-2026-02", "Medir acetaldeído na purga (agente gerado pelo processo — DL 24/2012)", "Médio", PROD, "2026-11-30", "2026-09-15", SGA),
    ("ARQ-18", "QUI-007", "", "Aplicação da emulsão fotossensível nos ecrãs", "SER", OP_SER, 2, None, vB, pA, cV, s2, f1,
     "Luvas de nitrilo; óculos", "Sala de gravação com luz inativa e ventilação", "", "", "Baixo", PROD, "", "2025-03-12", SGA),
    ("ARQ-19", "QUI-025", "", "Pulverização de antioxidante em moldes armazenados", "MAN", TEC_MAN, 6, None, vA, pD, cV, s1, f1,
     "Luvas de nitrilo", "Pulverização junto à porta do armazém de moldes", "", "Pulverizar em zona ventilada dedicada", "Médio", MAN, "2026-12-31", "2025-01-20", SGA),
    ("ARQ-20", "QUI-042", "", "Limpeza de peças com isopropanol", "SER", OP_SER, 8, None, vA, pA, cV, s2, f1,
     "Luvas de nitrilo", "Recipientes de segurança com tampa", "", "", "Baixo", PROD, "", "2025-03-12", SGA),
    ("ARQ-21", "QUI-040", "", "Ensaios de migração e limpeza no laboratório (etanol)", "LAB", TEC_QA, 2, None, vA, pA, cE, s1, f1,
     "Luvas de nitrilo; óculos", "Hotte verificada anualmente", "", "", "Baixo", QUA, "", "2026-05-10", SGA),
]

MEDICOES = [
    # (ID, data, posto, agente, CAS, método, laboratório, n.º amostras, resultado máx (ppm), VLE-MP (ppm), observação)
    ("MVLE-2025-01", "2025-11-20", "SS-001 (limpeza de ecrãs)", "Acetato de 1-metoxi-2-propilo", "108-65-6", "Amostragem pessoal 8 h (NP EN 689)", "Laboratório acreditado (IPAC)", 3, 9.5, 50, ""),
    ("MVLE-2025-02", "2025-11-20", "SS-001 (impressão)", "Ciclo-hexanona", "108-94-1", "Amostragem pessoal 8 h (NP EN 689)", "Laboratório acreditado (IPAC)", 3, 2.8, 10, ""),
    ("MVLE-2025-03", "2025-11-20", "SS-002 (impressão com mesa aspirante)", "Ciclo-hexanona", "108-94-1", "Amostragem pessoal 8 h (NP EN 689)", "Laboratório acreditado (IPAC)", 3, 0.6, 10, ""),
    ("MVLE-2025-04", "2025-11-20", "SS-002 (limpeza em mesa aspirante)", "Acetato de etilo", "141-78-6", "Amostragem pessoal 8 h (NP EN 689)", "Laboratório acreditado (IPAC)", 3, 12, 200, ""),
    ("MVLE-2026-01", "2026-03-18", "Mistura da tinta 2K", "HDI monómero", "822-06-0", "Amostragem pessoal na tarefa (derivatização)", "Laboratório acreditado (IPAC)", 3, 0.0004, 0.005, "VLE a confirmar na NP 1796 em vigor."),
    ("MVLE-2026-02", "2026-11-15", "Purga das ISBM", "Acetaldeído", "75-07-0", "Amostragem pessoal 8 h (NP EN 689)", "Laboratório acreditado (IPAC)", None, None, None, "Planeada (ARQ-17). Confirmar VLE aplicável."),
    ("MVLE-2026-03", "2026-10-20", "Oficina — limpeza de moldes", "n-Hexano", "110-54-3", "Amostragem pessoal na tarefa (NP EN 689)", "Laboratório acreditado (IPAC)", None, None, 20, "Planeada (ARQ-09)."),
]

ARMAZ = [
    # (ID, local, tipo, capacidade de retenção (L), ventilação, kit (RG-SGA-12 tbl_meios), incompatibilidades verificadas, ponto de ronda (RG-SGA-10), observação)
    ("ARM-01", "Armazém de químicos — zona de inflamáveis (estrados com bacia, EN 14470-1 para < 50 L)", "Interior", 400, "Mecânica", "KIT-01", "Sim", "RON-02", "Local de risco C (RT-SCIE); zona ATEX a confirmar no DPCE."),
    ("ARM-02", "Armazém de químicos — óleos e fluidos (bacias de 2 bidões)", "Interior", 440, "Natural", "KIT-01", "Sim", "RON-02", "NC de auditoria CONST-01: bidões no chão; 2 bacias novas em compra (PAM-26-19)."),
    ("ARM-03", "Serigrafia — armário do posto (quantidade do turno)", "Interior", 60, "Mecânica", "KIT-04", "Sim", "RON-01", ""),
    ("ARM-04", "Torre de arrefecimento — bacia do IBC e bidões de tratamento", "Exterior coberto", 1100, "Natural", "KIT-05", "Não", "RON-11", "Hipoclorito na mesma bacia que o anti-incrustante ácido (liberta cloro — EUH031)."),
    ("ARM-05", "Oficina — armário de aerossóis, colas e sprays", "Interior", 30, "Natural", "KIT-02", "Sim", "RON-11", ""),
    ("ARM-06", "Parque de gases (exterior, garrafas acorrentadas)", "Exterior", None, "Natural", "—", "Sim", "RON-11", "Oxigénio separado dos gases inflamáveis por muro corta-fogo."),
    ("ARM-07", "Depósito de gasóleo 3.000 L (parede dupla com detetor de fuga)", "Exterior", 3000, "Natural", "KIT-05", "Sim", "RON-11", "Parede dupla = retenção de 100%."),
    ("ARM-08", "Laboratório — armários de ácidos e de inflamáveis", "Interior", 20, "Mecânica", "KIT-01", "Sim", "RON-11", ""),
    ("ARM-09", "Sala de carga de baterias", "Interior", 50, "Mecânica", "KIT-02", "Sim", "RON-11", "Ventilação para hidrogénio; zona ATEX a confirmar."),
    ("ARM-10", "Silos e armazém de granulado", "Interior/exterior", None, "N.A.", "TMP-01", "Sim", "RON-09", "Contenção de granulado (OCS) — não é retenção de líquidos."),
    ("ARM-11", "Em equipamento (circuitos fechados: chiller, termorreguladores)", "Equipamento", None, "N.A.", "—", "N.A.", "—", "Controlo de fugas F-gás (LEG-07)."),
    ("ARM-12", "Armazém de matérias-primas secas (foil, embalagens)", "Interior", None, "Natural", "—", "N.A.", "—", ""),
]

SEVESO = [
    # (categoria, designação, limiar inferior t, limiar superior t, grupo para a regra da soma)
    ("H1", "Toxicidade aguda cat. 1 (todas as vias)", 5, 20, "Saúde"),
    ("H2", "Toxicidade aguda cat. 2 / cat. 3 inalação", 50, 200, "Saúde"),
    ("H3", "STOT exposição única cat. 1", 50, 200, "Saúde"),
    ("P2", "Gases inflamáveis cat. 1 ou 2", 10, 50, "Físico"),
    ("P3a", "Aerossóis inflamáveis cat. 1 ou 2 (massa líquida)", 150, 500, "Físico"),
    ("P3b", "Aerossóis inflamáveis sem gás/líquido inflamável cat. 1", 5000, 50000, "Físico"),
    ("P4", "Gases comburentes cat. 1", 50, 200, "Físico"),
    ("P5a", "Líquidos inflamáveis cat. 1 ou mantidos acima do ponto de ebulição", 10, 50, "Físico"),
    ("P5b", "Líquidos inflamáveis cat. 2/3 em condições de risco de acidente grave", 50, 200, "Físico"),
    ("P5c", "Líquidos inflamáveis cat. 2 ou 3 (restantes)", 5000, 50000, "Físico"),
    ("P8", "Líquidos e sólidos comburentes cat. 1, 2 ou 3", 50, 200, "Físico"),
    ("E1", "Perigoso para o ambiente aquático — aguda 1 ou crónica 1", 100, 200, "Ambiente"),
    ("E2", "Perigoso para o ambiente aquático — crónica 2", 200, 500, "Ambiente"),
    ("O1", "Substâncias com EUH014", 100, 500, "Físico"),
    ("O2", "Substâncias que em contacto com a água libertam gases inflamáveis cat. 1", 100, 500, "Físico"),
    ("O3", "Substâncias com EUH029", 50, 200, "Saúde"),
    ("Parte 2 — GPL", "Gases liquefeitos extremamente inflamáveis, incl. GPL", 50, 200, "Físico"),
    ("Parte 2 — Acetileno", "Acetileno", 5, 50, "Físico"),
    ("Parte 2 — Oxigénio", "Oxigénio", 200, 2000, "Físico"),
    ("Parte 2 — Produtos petrolíferos", "Produtos petrolíferos e combustíveis alternativos (gasóleo)", 2500, 25000, "Físico; Ambiente"),
]
SEVESO_CATS = [s[0] for s in SEVESO] + ["—"]

# ------------------------------------------------------------------------------------------ matriz legal de químicos (UE + PT)
EURLEX_REACH = "https://eur-lex.europa.eu/eli/reg/2006/1907/oj"
EURLEX_CLP = "https://eur-lex.europa.eu/eli/reg/2008/1272/oj"
REQ = [
    # (ID, âmbito, tema, diploma, artigos, papel, obrigação, aplicável, justificação, evidência, frequência, estado, ID_Legal, ação, responsável, fonte)
    ("RQ-01", "UE", "REACH — registo", "Reg. (CE) 1907/2006 (REACH)", "Arts. 5.º, 6.º (incl. n.º 3 — monómeros de polímeros), 7.º, n.º 1",
     "Importador", "Registar substâncias fabricadas/importadas ≥ 1 t/ano ('sem dados, não há mercado'); em polímeros importados, registar monómeros e aditivos não registados a montante.",
     "Condicional", "A Plasticom importa polímeros de fora do EEE (SUP-001/003/004/005/009).", "tbl_registo_reach", "Anual e em cada novo fornecedor", "Parcial", "LEG-06", "PAM-26-28", CMP, EURLEX_REACH),
    ("RQ-02", "UE", "REACH — registo", "Reg. (CE) 1907/2006 (REACH)", "Art. 8.º (representante único)", "Importador",
     "Quando o fornecedor extra-UE nomeia um representante único (RU), o importador passa a utilizador a jusante — exige carta do RU com a Plasticom na lista de importadores cobertos.",
     "Sim", "RU confirmado para SUP-001 e SUP-009; em falta para SUP-004 e SUP-005.", "tbl_registo_reach", "Anual", "Parcial", "LEG-06", "PAM-26-28", CMP, EURLEX_REACH),
    ("RQ-03", "UE", "REACH — FDS", "Reg. (CE) 1907/2006 + Reg. (UE) 2020/878 (anexo II)", "Art. 31.º", "Utilizador a jusante",
     "Receber FDS em português, no formato do anexo II (Reg. 2020/878), para substâncias e misturas perigosas; exigir FDS atualizadas quando há nova informação.",
     "Sim", "42 produtos, 36 perigosos ou com FDS voluntária.", "tbl_fds", "Por receção + revisão anual", "Parcial", "LEG-06", "PAM-26-34", TEC_QA, "https://eur-lex.europa.eu/eli/reg/2020/878/oj"),
    ("RQ-04", "UE", "REACH — informação", "Reg. (CE) 1907/2006 (REACH)", "Art. 32.º", "Utilizador a jusante",
     "Para produtos sem FDS obrigatória, obter informação sobre registo, autorização, restrições e medidas de gestão de risco.", "Sim",
     "Polímeros e masterbatches não classificados.", "tbl_fds (FDS voluntárias); tbl_declaracoes", "Anual", "Conforme", "LEG-06", "", CMP, EURLEX_REACH),
    ("RQ-05", "UE", "REACH — cenários de exposição", "Reg. (CE) 1907/2006 (REACH)", "Arts. 37.º, n.os 4–6, e 39.º", "Utilizador a jusante",
     "Verificar se o uso está coberto pelo cenário de exposição (CE) da FDS alargada e aplicar as condições em 12 meses; senão, pedir inclusão do uso, elaborar RSQ-UJ ou substituir.",
     "Sim", "10 CE verificados; 2 não cobertos e 2 parcialmente cobertos, destes 2 com o prazo de 12 meses ultrapassado (CE-02, CE-08).", "tbl_ce_reach", "Por receção de FDS alargada", "Não conforme", "LEG-06", "PAM-26-31; PAM-26-33; PAM-26-30", PROD,
     "https://echa.europa.eu/regulations/reach/downstream-users"),
    ("RQ-06", "UE", "REACH — cenários de exposição", "Reg. (CE) 1907/2006 (REACH)", "Art. 38.º", "Utilizador a jusante",
     "Comunicar à ECHA, em 6 meses, os usos não cobertos para os quais se elabora RSQ-UJ (> 1 t/ano).", "Condicional",
     "Não foi elaborado nenhum RSQ-UJ (opções escolhidas: implementar condições ou substituir).", "tbl_ce_reach", "Por ocorrência", "Não aplicável", "LEG-06", "", SGA,
     "https://echa.europa.eu/regulations/reach/downstream-users/more-on-downstream-user-responsibilities/downstream-user-reports"),
    ("RQ-07", "UE", "REACH — comunicação na cadeia", "Reg. (CE) 1907/2006 (REACH)", "Art. 34.º", "Utilizador a jusante",
     "Comunicar ao fornecedor nova informação sobre perigos ou medidas de gestão de risco inadequadas.", "Sim",
     "Pedidos de correção de FDS e de inclusão de uso (CE-09).", "tbl_fds (Pedido_Fornecedor); tbl_ce_reach", "Por ocorrência", "Conforme", "LEG-06", "", TEC_QA, EURLEX_REACH),
    ("RQ-08", "UE", "REACH — trabalhadores", "Reg. (CE) 1907/2006 (REACH)", "Art. 35.º", "Utilizador a jusante",
     "Dar aos trabalhadores e representantes acesso à informação das FDS dos produtos que usam.", "Sim",
     "FDS no posto e ficha-resumo; 12 FDS de polímeros só em formato eletrónico.", "tbl_fds (Disponivel_Posto)", "Contínuo", "Conforme", "LEG-06", "", LOG, EURLEX_REACH),
    ("RQ-09", "UE", "REACH — conservação", "Reg. (CE) 1907/2006 (REACH)", "Art. 36.º", "Utilizador a jusante",
     "Conservar toda a informação REACH durante pelo menos 10 anos após a última utilização/fornecimento.", "Sim",
     "Este registo tem retenção de 10 anos; versões substituídas das FDS mantêm-se (Em_Vigor = Não).", "Todo o RG-SGA-21", "Contínuo", "Conforme", "LEG-06", "", SGA, EURLEX_REACH),
    ("RQ-13", "UE", "REACH — autorização", "Reg. (CE) 1907/2006 (REACH)", "Art. 56.º; anexo XIV", "Utilizador a jusante",
     "Não usar substâncias do anexo XIV após a data de expiração sem autorização (própria ou do fornecedor, com notificação à ECHA — art. 66.º).", "Sim",
     "Nenhum componente do anexo XIV nas FDS; PVC (SUP-005) por confirmar.", "tbl_componentes; tbl_svhc_vigiadas", "Anual", "Conforme", "LEG-06", "", SGA, EURLEX_REACH),
    ("RQ-14", "UE", "REACH — restrições", "Reg. (CE) 1907/2006, anexo XVII (entradas 23, 46, 50, 51, 63, 70, 79)", "Art. 67.º", "Produtor de artigos / utilizador",
     "Cumprir as restrições aplicáveis: cádmio em plásticos (23), ftalatos em materiais plastificados (51, Reg. 2018/2005), chumbo em PVC (63), D4/D5/D6 (70, Reg. 2024/1328), PFHxA (79, Reg. 2024/2462).",
     "Sim", "Relevante para PVC legado, silicones de desmoldante e aditivos.", "tbl_quimicos (Anexo_XVII); tbl_declaracoes", "Anual", "Parcial", "LEG-06", "PAM-26-28; PAM-26-34", RD, "https://echa.europa.eu/substances-restricted-under-reach"),
    ("RQ-15", "UE", "REACH — restrições", "Reg. (CE) 1907/2006, anexo XVII, entrada 74 (Reg. (UE) 2020/1149)", "Diisocianatos", "Utilizador industrial",
     "Formação em uso seguro de diisocianatos antes do uso (≥ 0,1%), renovada a cada 5 anos, com registo.", "Sim",
     "Endurecedor da tinta 2K (QUI-003) com HDI monómero 0,1–0,5%.", "RG-SGA-08 FOR-13", "5 anos", "Não conforme", "LEG-06", "PAM-26-32", RH, "https://eur-lex.europa.eu/eli/reg/2020/1149/oj"),
    ("RQ-16", "UE", "REACH — microplásticos", "Reg. (CE) 1907/2006, anexo XVII, entrada 78 (Reg. (UE) 2023/2055)", "N.os 11 e 12 da entrada 78", "Utilizador industrial de granulado",
     "Comunicar anualmente à ECHA (até 31/05) as estimativas de libertação de micropartículas de polímeros sintéticos (granulado) do ano anterior.", "Sim",
     "≈ 865 t/ano de granulado e masterbatch.", "RG-SGA-04 tbl_obrigacoes", "Anual (31/05)", "Conforme", "LEG-10", "", SGA,
     "https://echa.europa.eu/support/dossier-submission-tools/reach-it/microplastics-reporting"),
    ("RQ-17", "UE", "CLP — rotulagem", "Reg. (CE) 1272/2008 (CLP)", "Arts. 17.º, 31.º e 35.º", "Utilizador a jusante",
     "Manter recipientes rotulados; recipientes de trasfega internos identificados com nome e perigos (sinalização de segurança).", "Sim",
     "Amostra de 15 recipientes conforme (LEG-06, 02/09/2026).", "RG-SGA-10 (rondas)", "Mensal", "Conforme", "LEG-06", "", LOG, EURLEX_CLP),
    ("RQ-18", "UE", "CLP — novas classes de perigo", "Reg. Delegado (UE) 2023/707", "Anexo I (desreguladores endócrinos, PBT/mPmB, PMT/mPmM — EUH380 a EUH451)", "Utilizador a jusante",
     "Aceitar e integrar as novas classes nas FDS: substâncias já no mercado até 01/11/2026; misturas já no mercado até 01/05/2028.", "Sim",
     "Afeta a classificação de perigo (tbl_frases_h já inclui os códigos EUH380–EUH451).", "tbl_fds (C08, C09); tbl_frases_h", "Semestral", "Em acompanhamento", "LEG-06", "", SGA, "https://eur-lex.europa.eu/eli/reg_del/2023/707/oj"),
    ("RQ-19", "UE", "CLP — revisão", "Reg. (UE) 2024/2865 e Reg. (UE) 2025/2439 ('stop-the-clock')", "Formatação de rótulos, vendas à distância, publicidade", "Utilizador a jusante",
     "Regras de formatação de rótulos adiadas para 01/01/2028; a Plasticom não coloca químicos no mercado — só verifica os rótulos recebidos.", "Não",
     "Obrigação do fornecedor.", "—", "—", "Não aplicável", "LEG-06", "", SGA, "https://www.consilium.europa.eu/en/press/press-releases/2025/11/17/council-signs-off-postponing-rules-on-classification-labelling-and-packaging-of-chemicals-to-2028/"),
    ("RQ-20", "UE", "CLP — centros antivenenos", "Reg. (CE) 1272/2008, art. 45.º e anexo VIII (UFI)", "Notificação harmonizada", "Formulador",
     "Notificação de misturas perigosas colocadas no mercado; a Plasticom não coloca misturas no mercado (as misturas no posto são para uso próprio).", "Não",
     "Verificar apenas o UFI no rótulo/FDS dos fornecedores (C03).", "tbl_fds C03", "—", "Não aplicável", "LEG-06", "", SGA, EURLEX_CLP),
    ("RQ-21", "UE", "Poluentes orgânicos persistentes", "Reg. (UE) 2019/1021 (POP)", "Arts. 3.º e 4.º; anexo I", "Utilizador / produtor de artigos",
     "Não fabricar, colocar no mercado ou usar POP (ex.: PFOA, PFHxS, UV-328, decaBDE) acima dos limites.", "Sim",
     "Declarações dos fornecedores excluem POP; absorvedor UV é UV-329 (não UV-328).", "tbl_declaracoes; tbl_componentes", "Anual", "Conforme", "LEG-06", "", CMP, "https://eur-lex.europa.eu/eli/reg/2019/1021/oj"),
    ("RQ-22", "UE/PT", "Biocidas", "Reg. (UE) 528/2012 e DL 140/2017", "Art. 17.º, n.º 5", "Utilizador profissional",
     "Usar apenas produtos biocidas autorizados e conforme o rótulo e as condições de autorização.", "Sim", "Biocida TP11 da torre (QUI-036).", "RG-SGA-04 tbl_obrigacoes", "Anual", "Conforme", "LEG-15", "", MAN,
     "https://eur-lex.europa.eu/eli/reg/2012/528/oj"),
    ("RQ-28", "UE/PT", "Acidentes graves", "Diretiva 2012/18/UE (Seveso III) e DL 150/2015", "Arts. 2.º e 3.º; anexo I", "Operador",
     "Verificar se as quantidades presentes atingem os limiares (incl. regra da soma).", "Sim (verificação)", "Σ q/Q muito inferior a 1 em todos os grupos.",
     "Seveso (tbl_seveso, tbl_seveso_resumo)", "Anual e em cada alteração", "Não aplicável", "LEG-02", "", SGA, "https://diariodarepublica.pt/dr/detalhe/decreto-lei/150-2015-70041373"),
    ("RQ-29", "PT", "REACH — execução nacional", "DL 293/2009", "Autoridades competentes (DGAE, APA, DGS); helpdesk DGAE; regime contraordenacional", "Todos",
     "Cumprir o REACH sob fiscalização da ASAE, IGAMAOT e ACT; usar o helpdesk da DGAE para dúvidas.", "Sim", "Enquadramento sancionatório.", "Todo o RG-SGA-21", "—", "Conforme", "LEG-06", "", SGA,
     "https://diariodarepublica.pt/dr/detalhe/decreto-lei/293-2009-491732"),
    ("RQ-30", "PT", "CLP — execução nacional", "DL 220/2012", "Autoridades e contraordenações CLP", "Todos", "Cumprir o CLP sob o regime nacional.", "Sim", "Enquadramento sancionatório.", "tbl_fds; rondas", "—", "Conforme", "LEG-06", "", SGA,
     "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2012-155903178"),
    ("RQ-31", "PT", "SST — agentes químicos", "DL 24/2012 (e alterações posteriores, incl. DL 102/2024)", "Avaliação de riscos, VLE, medições, informação, formação, vigilância da saúde",
     "Empregador", "Avaliar os riscos dos agentes químicos (incl. os gerados no processo), eliminar/reduzir, cumprir VLE, medir quando necessário e informar/formar os trabalhadores.",
     "Sim", "21 tarefas avaliadas (5 de prioridade 1); 5 produtos perigosos ainda sem avaliação.", "tbl_risco_quimico; tbl_medicoes_vle", "3 anos e em cada alteração", "Parcial", "", "PAM-26-29; PAM-26-30; PAM-26-31; PAM-26-35", SGA,
     "https://diariodarepublica.pt/dr/detalhe/decreto-lei/24-2012-543402"),
    ("RQ-32", "PT", "SST — cancerígenos, mutagénicos e reprotóxicos", "DL 301/2000 (redação do DL 102/2024, transpõe a Dir. (UE) 2022/431)", "Substituição, sistema fechado, lista de expostos",
     "Empregador", "Substituir agentes CMR/reprotóxicos cat. 1A/1B quando tecnicamente possível; reduzir a exposição; manter a lista de trabalhadores expostos (40 anos; 5 anos para reprotóxicos).",
     "Sim", "Tinta UV QUI-002 (H360FD).", "tbl_risco_quimico ARQ-02; RG-SGA-04 tbl_obrigacoes", "Contínuo", "Não conforme", "", "PAM-26-29", SGA,
     "https://diariodarepublica.pt/dr/detalhe/decreto-lei/102-2024-898867718"),
    ("RQ-33", "PT", "SST — regime geral", "Lei 102/2009 (regime jurídico da promoção da SST) e Código do Trabalho (Lei 7/2009), art. 62.º",
     "Avaliação de riscos; proteção de trabalhadoras grávidas, puérperas e lactantes e de menores", "Empregador",
     "Identificar tarefas com agentes que exigem proteção da maternidade e de menores (CMR, H362) e adaptar as condições de trabalho.", "Sim",
     "Coluna Protecao_Maternidade do inventário (3 produtos).", "tbl_quimicos (Protecao_Maternidade)", "Por ocorrência", "Parcial", "", "PAM-26-29", RH, "https://diariodarepublica.pt/dr/legislacao-consolidada/lei/2009-34480075"),
    ("RQ-34", "PT", "SST — atmosferas explosivas", "DL 236/2003 (ATEX)", "Documento de proteção contra explosões", "Empregador",
     "Classificar zonas e elaborar o documento de proteção contra explosões (armazém de inflamáveis, serigrafia, sala de baterias).", "Sim", "Inflamáveis e hidrogénio de carga de baterias.",
     "tbl_armazenagem (observações)", "Em cada alteração", "Por avaliar", "LEG-11", "", MAN, "https://diariodarepublica.pt/dr/detalhe/decreto-lei/236-2003-574001"),
    ("RQ-35", "PT", "SST — sinalização", "Portaria 1456-A/95", "Sinalização de recipientes e tubagens", "Empregador", "Identificar recipientes e tubagens de produtos perigosos.", "Sim", "",
     "RG-SGA-10 (rondas)", "Mensal", "Conforme", "", "", LOG, "https://diariodarepublica.pt/"),
    ("RQ-40", "UE/PT", "Normas técnicas", "NP EN 689:2018 e NP 1796:2014", "Estratégia de medição e valores-limite de exposição", "Empregador",
     "Medir a exposição com estratégia NP EN 689 (teste preliminar ou estatístico); usar os VLE legais e, na falta, os da NP 1796.", "Sim", "", "tbl_medicoes_vle", "Anual", "Parcial", "", "PAM-26-35", SGA, "https://www.ipq.pt/"),
    ("RQ-41", "UE", "Ozono", "Reg. (UE) 2024/590", "Substâncias que empobrecem a camada de ozono", "Operador", "Não usar SEO; verificar equipamentos antigos.", "Não",
     "Sem SEO nos equipamentos (R410A não é SEO).", "tbl_quimicos (H420)", "—", "Não aplicável", "LEG-07", "", MAN, "https://eur-lex.europa.eu/eli/reg/2024/590/oj"),
    ("RQ-42", "UE", "Exportação de químicos", "Reg. (UE) 649/2012 (PIC)", "Notificação de exportação", "Exportador", "A Plasticom não exporta produtos químicos.", "Não", "", "—", "—", "Não aplicável", "", "", SGA,
     "https://eur-lex.europa.eu/eli/reg/2012/649/oj"),
    ("RQ-43", "UE", "Detergentes", "Reg. (CE) 648/2004", "Rotulagem e biodegradabilidade", "Fabricante/distribuidor", "A Plasticom não coloca detergentes no mercado; limpeza por prestador externo (SGA-11 LIM-01).", "Não", "",
     "RG-SGA-11", "—", "Não aplicável", "", "", SGA, "https://eur-lex.europa.eu/eli/reg/2004/648/oj"),
]

PAPEL = [
    # (ID, atividade, papel, justificação, obrigações principais, evidência)
    ("PAP-01", "Uso de tintas, solventes, óleos, gases, biocidas e reagentes comprados na UE", "Utilizador a jusante (utilizador final industrial)",
     "Usa substâncias e misturas na atividade industrial sem as colocar no mercado.", "Arts. 31.º–39.º REACH: receber e verificar FDS, verificar CE e aplicar condições (12 meses), comunicar ao fornecedor, acesso dos trabalhadores, conservar 10 anos.",
     "tbl_quimicos; tbl_fds; tbl_ce_reach"),
    ("PAP-02", "Mistura de tinta com diluente/endurecedor no posto", "Utilizador a jusante (não é formulador)",
     "A mistura é feita para uso próprio e não é colocada no mercado.", "Sem FDS/rotulagem própria nem notificação a centros antivenenos; identificar os recipientes de trasfega; avaliar o risco da mistura.",
     "tbl_risco_quimico ARQ-01/03/04"),
    ("PAP-03", "Compra de polímeros a fornecedores de fora do EEE", "Importador (salvo se houver RU ou importador UE)",
     "Quem introduz fisicamente a substância/mistura no território aduaneiro da UE é o importador.", "Registo dos monómeros ≥ 2% e ≥ 1 t/ano e dos aditivos ≥ 1 t/ano não registados a montante (art. 6.º, n.º 3); ou confirmação de RU (art. 8.º).",
     "tbl_registo_reach"),
    ("PAP-04", "Fabrico de frascos, tampas e potes", "Produtor de artigos",
     "As embalagens têm forma/desenho que determinam a função mais do que a composição química.", "Art. 7.º, n.º 2 (notificação SVHC > 0,1% e > 1 t/ano); art. 33.º (comunicação a clientes); SCIP; restrições do anexo XVII aplicáveis a artigos.",
     "RG-SGA-20 tbl_familias_ppwr; tbl_declaracoes"),
    ("PAP-05", "Uso industrial de granulado de polímeros", "Utilizador a jusante industrial de micropartículas de polímeros sintéticos",
     "Granulado usado como matéria-prima na produção de plásticos em instalação industrial (derrogação da entrada 78).", "Relatório anual à ECHA das libertações estimadas (até 31/05); prevenção de perdas (Reg. 2025/2365).",
     "RG-SGA-04 tbl_obrigacoes; LEG-10"),
    ("PAP-06", "Fabrico de substâncias", "Não aplicável", "A Plasticom não sintetiza substâncias (a moldação transforma polímeros em artigos).", "—", "—"),
    ("PAP-07", "Venda/distribuição de químicos", "Não aplicável", "A Plasticom não vende produtos químicos; o scrap vendido é resíduo/material recuperado gerido pelo reciclador.", "—", "—"),
    ("PAP-08", "Uso de produto biocida na torre de arrefecimento", "Utilizador profissional de biocida (Reg. 528/2012)",
     "Usa um produto biocida autorizado (TP11).", "Usar conforme o rótulo e a autorização; FDS; formação dos técnicos.", "tbl_quimicos QUI-036; RG-SGA-04 tbl_obrigacoes"),
    ("PAP-09", "Laboratório (ensaios de migração)", "Utilizador a jusante (laboratório)", "Pequenas quantidades de reagentes em laboratório.", "FDS, CE de laboratório (PROC 15), hotte.", "tbl_ce_reach CE-04/05"),
]

CRITICA = [
    # (ID, fonte, constatação, avaliação, melhoria implementada, onde)
    ("AC-01", "REACH 2024.xlsx (referência)", "Folhas 'GERAL' e 'FDS 2024' com 74 e 121 colunas numa só linha por produto (verificação, composição, perigos, EPI, CE e conclusão juntos).",
     "Difícil de manter, filtrar e auditar; uma FDS nova apaga o histórico da anterior.", "Modelo relacional: inventário, componentes, versões de FDS (com histórico) e CE em tabelas separadas ligadas pelo ID_Quimico.", "Inventario; Componentes; FDS_Verificacao; Cenarios_Exposicao"),
    ("AC-02", "REACH 2024.xlsx (referência)", "Erros de fórmula: #N/A (FDS 2024), #REF! (BASE DADOS, linha 4) e #VALUE! (pictogramas); XLOOKUP matricial.",
     "Um registo com erros não é evidência fiável e parte-se em versões antigas do Excel.", "Fórmulas INDEX/MATCH/SUMPRODUCT compatíveis, protegidas com IF/IFERROR; recálculo com 0 erros.", "Todo o ficheiro"),
    ("AC-03", "REACH 2024.xlsx (referência)", "Nota da secção 9 remete para o Reg. (UE) 2015/830.", "Revogado: desde 01/01/2023 só vale o anexo II na redação do Reg. (UE) 2020/878 (novas subsecções 9, 11.2 e 12.6, nanoformas, UFI).",
     "Checklist de 12 pontos alinhada com o Reg. 2020/878 (C02, C08, C09).", "FDS_Verificacao"),
    ("AC-04", "REACH 2024.xlsx (referência)", "Verificação SIM/NÃO sem conclusão nem ação; sem data da próxima revisão.", "Não prova que as falhas foram tratadas.",
     "Resultado automático, pedido ao fornecedor com data, idade da FDS e estado (OK / Pedir correção / Pedir confirmação / Substituída).", "FDS_Verificacao"),
    ("AC-05", "REACH 2024.xlsx (referência)", "Análise dos cenários de exposição apenas descritiva.", "Falta o prazo legal de 12 meses (art. 39.º) e a decisão entre as opções do art. 37.º, n.º 4.",
     "Método, resultado, ação escolhida, prazo legal e prazo de relatório à ECHA calculados.", "Cenarios_Exposicao"),
    ("AC-06", "REACH 2024.xlsx (referência)", "Não determina o papel REACH da empresa.", "A obrigação de registo depende do papel: importar de fora do EEE torna a empresa importadora.",
     "Folha Papel_REACH e registo por fornecedor com RU/importador legal e lacunas.", "Papel_REACH; Registo_Importacao"),
    ("AC-07", "REACH 2024.xlsx (referência)", "SVHC registada como texto, sem indicar a versão da lista candidata usada.", "Uma declaração 'sem SVHC' só é válida para a versão da lista que cobre.",
     "Declarações com n.º de entradas coberto e alerta automático quando a lista (parâmetro P-01 = 253) é mais recente.", "Declaracoes_SVHC; Parametros"),
    ("AC-08", "REACH 2024.xlsx (referência)", "Cópia estática da tabela de classificação harmonizada (ATP 18, 4.378 linhas).", "Desatualiza a cada ATP e aumenta o ficheiro; a fonte oficial é o inventário C&L da ECHA.",
     "Verificação por CAS dos componentes e ligação à base de dados da ECHA; lista vigiada de SVHC relevantes para plásticos.", "Componentes; Ref_SVHC_Vigiadas"),
    ("AC-09", "REACH 2024.xlsx (referência)", "Não avalia o risco para os trabalhadores (toxicidade) nem trata artigos, Seveso, armazenagem, formação ou restrições.",
     "O REACH é só uma parte da gestão de químicos; o DL 24/2012 e o DL 301/2000 exigem avaliação de riscos registada.", "Folhas Avaliacao_Risco, Medicoes_VLE, Seveso, Armazenagem e Requisitos_Legais; formação, calendário, ações e SVHC em embalagens nos registos donos (RG-SGA-08, 04, 06, 20).", "Várias"),
    ("AC-10", "REACH 2024.xlsx (referência)", "Base de dados em lista de materiais de cosmética (INCI) e em espanhol/português.", "Não se aplica a uma fábrica de embalagens plásticas.",
     "Triagem SVHC por família PPWR no RG-SGA-20 (tbl_familias_ppwr) e texto só em português.", "RG-SGA-20"),
    ("AC-11", "Internet (sites de consultoria)", "Afirmação frequente: 'a FDS é válida 3 anos e tem de ser renovada'.", "Não existe prazo de validade no REACH: o art. 31.º, n.º 9 exige atualização sem demora quando há nova informação.",
     "Os 36 meses ficam como critério INTERNO para pedir confirmação ao fornecedor (parâmetro P-02), identificado como tal.", "Parametros; FDS_Verificacao"),
    ("AC-12", "Internet (guias genéricos)", "'Os utilizadores a jusante não têm de registar nada.'", "Só é verdade se todos os fornecedores estiverem no EEE ou houver RU/importador UE.", "Verificação fornecedor a fornecedor (Registo_Importacao).", "Registo_Importacao"),
    ("AC-13", "Internet (checklists 2024–2025)", "Indicam 01/07/2026 para as novas regras de formatação de rótulos CLP e dão a revisão do REACH ('REACH 2.0') como iminente.",
     "Datas adiadas para 01/01/2028 (Reg. (UE) 2025/2439); em 27/04/2026 a Comissão anunciou que não vai abrir o texto do REACH, preferindo alterar anexos.", "Matriz legal com as datas corrigidas e acompanhamento semestral (calendário do RG-SGA-04).", "Requisitos_Legais"),
    ("AC-14", "Internet (guias e listas)", "Números desatualizados da lista candidata (ex.: 235 ou 240 substâncias).", "Em 04/02/2026 a lista passou a 253 entradas (inclui n-hexano e BPAF).",
     "Valor parametrizado (P-01) e verificação semestral (calendário do RG-SGA-04).", "Parametros; RG-SGA-04"),
    ("AC-15", "Métodos de avaliação (INRS ND 2233 / Seirich, COSHH Essentials)", "Métodos por pontuação dão uma prioridade, não uma medição.", "Não substituem medições onde existe VLE; os fatores numéricos variam entre versões.",
     "Método adaptado e documentado (Metodologia) usado só para priorizar; medições NP EN 689 nas tarefas P1/P2 com VLE.", "Avaliacao_Risco; Medicoes_VLE; Metodologia"),
    ("AC-16", "Prática comum (Seveso)", "Instalações pequenas declaram 'Seveso não aplicável' sem cálculo.", "Sem a regra da soma não há evidência.", "Cálculo automático a partir do stock máximo do inventário.", "Seveso"),
    ("AC-17", "RG-SGA-19 (SGA Plasticom)", "SUB-05 (óleo hidráulico ISO VG 46) com H304.", "H304 só se aplica a hidrocarbonetos com viscosidade cinemática ≤ 20,5 mm²/s a 40 °C; o VG 46 tem ≈ 46 mm²/s.", "Corrigido no RG-SGA-19.", "RG-SGA-19"),
    ("AC-18", "RG-SGA-04 (SGA Plasticom)", "LEG-10 sem o número do regulamento de perdas de granulado.", "Publicado como Reg. (UE) 2025/2365; abaixo de 1.500 t/ano há declaração de conformidade em vez de certificação.",
     "LEG-10 atualizado e obrigações no calendário do RG-SGA-04.", "RG-SGA-04 tbl_legal e tbl_obrigacoes"),
    ("AC-20", "Revisão de redundâncias (24/09/2026)", "A 1.ª versão deste registo repetia formação, calendário, ações, SVHC em embalagens, kits, inspeções e requisitos já existentes noutros registos.",
     "Registos repetidos obrigam a escrever duas vezes e divergem (ex.: formação por função aqui vs por colaborador no RG-SGA-08).",
     "Fonte única: cada assunto no registo dono (ver SGA-00 Matriz_Fonte_Unica); aqui ficam só IDs de ligação.", "Armazenagem; Requisitos_Legais; Inventario"),
    ("AC-21", "RG-SGA-16/17/19 (COV)", "COV estimados como 'solvente de limpeza + 40% das tintas' (1,17 t/ano).",
     "Ignorava diluente, retardador, isopropanol, endurecedor e aerossóis; a tinta UV não tem 40% de COV.",
     "Balanço de COV a partir do inventário (Qtd × Teor_COV); RG-SGA-16, 17 e 19 usam este valor (resumo()).", "Inventario (Teor_COV, COV_kg_ano)"),
    ("AC-19", "ECHA e EUR-Lex (fontes oficiais)", "Relatório anual de microplásticos (entrada 78) com 1.º prazo a 31/05/2026 para utilizadores industriais de granulado.",
     "Obrigação nova pouco divulgada e aplicável à Plasticom.", "Registada em Papel_REACH (PAP-05), matriz legal (RQ-16) e no calendário do RG-SGA-04.", "Papel_REACH; Requisitos_Legais"),
]

PARAMS = [
    ("P-01", "Entradas da lista candidata de SVHC em vigor", SVHC_N, "n.º", f"ECHA, atualização de 04/02/2026 — {ECHA_CL} (confirmar em cada atualização semestral)"),
    ("P-02", "Idade máxima da FDS antes de pedir confirmação ao fornecedor", 36, "meses", "Critério INTERNO (o REACH não fixa prazo de validade — art. 31.º, n.º 9)"),
    ("P-03", "Prazo para aplicar as condições do cenário de exposição", 12, "meses", "REACH art. 39.º, n.º 1"),
    ("P-04", "Prazo para comunicar à ECHA um uso com RSQ-UJ", 6, "meses", "REACH art. 39.º, n.º 2 / art. 38.º"),
    ("P-05", "Limiar de SVHC em artigos e em misturas (secção 3 da FDS)", 0.001, "fração m/m", "REACH arts. 7.º, 31.º e 33.º (0,1%)"),
    ("P-06", "Prazo de revisão da avaliação de risco químico", 36, "meses", "Critério interno; revisão obrigatória em cada alteração (DL 24/2012)"),
    ("P-07", "Fator de retenção sobre o volume total armazenado", 0.5, "fração", "Critério interno: retenção ≥ máx(100% do maior recipiente; 50% do total) — boa prática; confirmar na licença"),
]
P_ROW = {p[0]: 5 + i for i, p in enumerate(PARAMS)}


def lookup(tbl, key_col, ret_col, key):
    return f'INDEX({tbl}[{ret_col}],MATCH({key},{tbl}[{key_col}],0))'


def build(out):
    b = Book("RG-SGA-21", "Gestão de Produtos Químicos (REACH, CLP, SVHC e Risco Químico)", version="00", date=dt.date(2026, 9, 24),
             retention="10 anos após a última utilização do produto (REACH art. 36.º); lista de expostos a CMR: 40 anos (reprotóxicos: 5 anos)",
             activities="Complemento — gestão integrada de produtos químicos (não é atividade do curso).",
             clauses="6.1.2; 6.1.3; 7.2; 7.5; 8.1 (incl. fornecedores externos); 8.2; 9.1.1; 9.1.2",
             purpose=("Registo único e evidência do controlo de produtos químicos da Plasticom: papel REACH, inventário, FDS, cenários de exposição, "
                      "registo/importação, SVHC em artigos e SCIP, restrições, avaliação de riscos para a saúde (toxicidade) e medições, armazenagem, Seveso, "
                      "formação, obrigações periódicas e matriz legal UE + Portugal. Procedimento: PR-SGA-16."),
             links=[("PR-SGA-16", "Procedimento de gestão de produtos químicos (Documentos_SGA_Plasticom)."),
                    ("RG-SGA-04", "LEG-06 (REACH/CLP), LEG-07, LEG-09, LEG-10, LEG-17 → coluna ID_Legal."),
                    ("RG-SGA-06", "Todas as ações de químicos: PAM-26-28 a PAM-26-35 (e PAM-26-11/19/22)."),
                    ("RG-SGA-08", "Formação: FOR-01, FOR-03, FOR-12 a FOR-15 (registo por colaborador)."),
                    ("RG-SGA-04", "Calendário de obrigações (tbl_obrigacoes OBR-11, OBR-19 a OBR-30) e LEG-22 (SST — agentes químicos)."),
                    ("RG-SGA-20", "SVHC nas embalagens por família PPWR (tbl_familias_ppwr) e requisitos de produto."),
                    ("RG-SGA-10 / RG-SGA-12", "Inspeção dos locais (RON-02, RON-11) e kits de derrame (KIT-01 a KIT-05)."),
                    ("RG-SGA-03", "Aspetos AA-005, AA-006, AA-014 a AA-016, AA-023 → IDs_Aspetos."),
                    ("RG-SGA-11", "ID_Fornecedor (SUP-001 a SUP-010; fornecedores de químicos PQ-01 a PQ-07, TOR-01, MAN-01)."),
                    ("RG-SGA-16 / 17 / 19", "Recebem de resumo() os totais de COV e de substâncias preocupantes (ESRS E2)."),
                    ("Fontes", "ECHA (echa.europa.eu), EUR-Lex, Diário da República, DGAE (helpdesk REACH/CLP), ACT, INRS ED 6485 (Seirich).")])

    # ---------------------------------------------------------------- listas
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("SimNaoPC", ["Sim", "Não", "Por confirmar"])
    b.add_list("SimNaoNA", ["Sim", "Não", "N.A."])
    b.add_list("TipoProduto", ["Substância", "Mistura", "Mistura (aerossol)", "Gás", "Polímero", "Artigo"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("PapelREACH", [UJ, RU, FIL, LAC, ART, "Importador (registo próprio)", "Formulador", "Distribuidor"])
    b.add_list("EstadoAprov", ["Em avaliação", "Aprovado", "Aprovado condicionado", "Suspenso", "Proibido", "Descontinuado"])
    b.add_list("Seveso", SEVESO_CATS)
    b.add_list("Local", [a[0] for a in ARMAZ])
    b.add_list("Volatilidade", [k for k, _ in VOLAT])
    b.add_list("Procedimento", [k for k, _ in PROCED])
    b.add_list("ProtColetiva", [k for k, _ in PROT])
    b.add_list("Superficie", [k for k, _ in SUPERF])
    b.add_list("Frequencia", [k for k, _ in FREQ])
    b.add_list("RiscoResidual", ["Baixo", "Médio", "Alto"])
    b.add_list("MetodoCE", ["Comparação direta", "Escalonamento (scaling)", "Ferramenta de estimativa (ECETOC TRA)", "Pedido ao fornecedor"])
    b.add_list("ResultadoCE", ["Coberto", "Parcialmente coberto", "Não coberto"])
    b.add_list("AcaoCE", ["Nenhuma", "Implementar condições do CE", "Pedir inclusão do uso ao fornecedor (art. 37.º, n.º 2)", "Elaborar RSQ-UJ (art. 37.º, n.º 4)",
                          "Substituir produto/fornecedor", "Deixar de usar"])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("Aplicavel", ["Sim", "Não", "Condicional", "Sim (verificação)"])
    b.add_list("EstadoConf", ["Conforme", "Parcial", "Não conforme", "Em implementação", "Em acompanhamento", "Por avaliar", "Não aplicável"])
    b.add_list("TipoAcaoQ", ["Corretiva", "Preventiva", "Melhoria"])
    b.add_list("Hierarquia", ["Eliminação", "Substituição", "Engenharia", "Administrativa", "EPI"])
    b.add_list("EstadoAcao", ["Aberta", "Em curso", "Concluída", "Cancelada"])
    b.add_list("Triagem", ["Concluída", "Por confirmar"])

    # ---------------------------------------------------------------- parâmetros
    b.table("Parametros", "tbl_param_quimicos",
            [col("ID_Param", 8, key="PK"), col("Parametro", 58, desc="Parâmetro."), col("Valor", 12, "num3", desc="Valor (editar aqui)."),
             col("Unidade", 12, desc="Unidade."), col("Fonte", 80, desc="Fonte / justificação.")],
            [dict(ID_Param=p[0], Parametro=p[1], Valor=p[2], Unidade=p[3], Fonte=p[4]) for p in PARAMS],
            "Parâmetros usados nas fórmulas (lista candidata, prazos, critérios internos). Editar o Valor quando a regra muda.",
            title="PARÂMETROS DO REGISTO DE QUÍMICOS", subtitle="Editar só a coluna Valor · P-01 muda a cada atualização da lista candidata (janeiro e junho)", row_height=30)
    for pid, name in [("P-01", "p_SVHC_N"), ("P-02", "p_Meses_FDS"), ("P-03", "p_Meses_CE"), ("P-04", "p_Meses_RSQ"), ("P-05", "p_Limiar_SVHC"),
                      ("P-06", "p_Meses_ARQ"), ("P-07", "p_Fator_Retencao")]:
        b.wb.defined_names[name] = DefinedName(name, attr_text=f"Parametros!$C${P_ROW[pid]}")

    # ---------------------------------------------------------------- papel REACH
    b.table("Papel_REACH", "tbl_papel_reach",
            [col("ID_Papel", 8, key="PK"), col("Atividade", 40), col("Papel_REACH_CLP", 32, desc="Papel da Plasticom (definições do art. 3.º REACH)."),
             col("Justificacao", 48), col("Obrigacoes_Principais", 70), col("Evidencia", 30)],
            [dict(zip(["ID_Papel", "Atividade", "Papel_REACH_CLP", "Justificacao", "Obrigacoes_Principais", "Evidencia"], p)) for p in PAPEL],
            "Determinação do papel REACH/CLP da Plasticom em cada atividade — é o ponto de partida: as obrigações dependem do papel.",
            title="PAPEL DA PLASTICOM NO REACH E NO CLP", subtitle="Rever quando muda a origem de uma compra (fora do EEE), se passar a vender químicos ou a formular misturas para terceiros",
            cf=[("Papel_REACH_CLP", {"Importador": "orange", "Não aplicável": "gray"})], row_height=60)

    # ---------------------------------------------------------------- frases H (referência)
    b.table("Ref_Frases_H", "tbl_frases_h",
            [col("Codigo", 9, key="PK", desc="Código H/EUH (anexo III do CLP)."), col("Advertencia", 62), col("Tipo", 11, desc="Físico, Saúde, Ambiente ou Suplementar."),
             col("Grupo", 30, desc="Grupo de perigo usado nos alertas."),
             col("Classe_Perigo_Saude", 9, "int", desc="Classe de perigo para a saúde 1–5 do método de avaliação (0 = sem efeito na saúde). Adaptado de INRS ND 2233."),
             col("CMR_Categoria", 8, desc="1 = cat. 1A/1B (DL 301/2000); 2 = suspeito."), col("Protecao_Maternidade", 10, desc="S = exige avaliação específica para grávidas/lactantes.")],
            [dict(Codigo=h[0], Advertencia=h[1], Tipo=h[2], Grupo=h[3], Classe_Perigo_Saude=h[4], CMR_Categoria=h[5] or None, Protecao_Maternidade=h[6] or None) for h in H],
            "Frases H e EUH do CLP com o grupo de perigo e a classe usada na avaliação de risco (inclui as novas classes EUH380–EUH451 do Reg. 2023/707).",
            title="REFERÊNCIA — ADVERTÊNCIAS DE PERIGO (CLP, ANEXO III)", subtitle="Texto oficial PT do CLP · Classes 1–5 adaptadas do INRS ND 2233 · Verificar no EUR-Lex após cada ATP",
            cf=[("Grupo", {"CMR": "red", "Sensibilizante": "orange", "cat. 1-3": "red", "aquático": "blue"})], row_height=18)

    # ---------------------------------------------------------------- SVHC vigiadas
    b.table("Ref_SVHC_Vigiadas", "tbl_svhc_vigiadas",
            [col("Substancia", 50), col("CAS", 13, key="PK"), col("Motivo_SVHC", 40), col("Uso_Tipico_Plasticos", 34), col("Outras_Regras", 44, req=False)],
            [dict(zip(["Substancia", "CAS", "Motivo_SVHC", "Uso_Tipico_Plasticos", "Outras_Regras"], s)) for s in SVHC],
            "Subconjunto da lista candidata com SVHC típicas do setor dos plásticos, usado para cruzar automaticamente os componentes (NÃO substitui a lista completa).",
            title="SVHC VIGIADAS (SUBCONJUNTO DA LISTA CANDIDATA DA ECHA)",
            subtitle=f"Lista completa ({SVHC_N} entradas em 04/02/2026): {ECHA_CL} · Acrescentar aqui as novas entradas relevantes em cada atualização", row_height=30)

    # ---------------------------------------------------------------- inventário
    names_inv = ["ID_Quimico", "Nome_Comercial", "Tipo_Produto", "Uso_Plasticom", "Processo", "Fornecedor", "ID_Fornecedor", "Pais_Origem", "Origem_EEE",
                 "Papel_REACH", "Qtd_Ano_kg", "Stock_Max_kg", "Volume_Embalagem_L", "Local_Armazenagem", "Frases_H", "Pictogramas", "Palavra_Sinal",
                 "Categoria_Seveso", "Categoria_Seveso_2", "SVHC_Declarado", "Anexo_XVII", "Diisocianatos_0_1", "PFAS", "Contacto_Alimentar", "IDs_Aspetos",
                 "Estado_Aprovacao", "Data_Aprovacao"]
    HN = "@H_norm@"
    hit = f'ISNUMBER(SEARCH(";"&tbl_frases_h[Codigo]&";",{HN}))'
    inv_cols = [
        col("ID_Quimico", 9, key="PK", desc="QUI-nnn."), col("Nome_Comercial", 36), col("Tipo_Produto", 12, dv="TipoProduto", desc="Substância, mistura, gás, polímero ou artigo (o artigo não tem FDS)."),
        col("Uso_Plasticom", 30), col("Processo", 8, dv="Processo", key="FK → Dim_Processo"), col("Fornecedor", 24, desc="Nome (informativo; o mestre é o RG-SGA-11)."), col("ID_Fornecedor", 9, key="FK → RG-SGA-11 (SUP-, PQ-, TOR-, MAN-)"),
        col("Pais_Origem", 11), col("Origem_EEE", 7, dv="SimNao", desc="Fornecedor estabelecido no EEE? 'Não' → ver Registo_Importacao."),
        col("Papel_REACH", 22, dv="PapelREACH"), col("Qtd_Ano_kg", 10, "num0", desc="Consumo anual (kg)."), col("Stock_Max_kg", 10, "num0", desc="Quantidade máxima presente (kg) — usada no Seveso."),
        col("Volume_Embalagem_L", 9, "num", desc="Volume da maior embalagem (L) — usado na retenção.", req=False),
        col("Local_Armazenagem", 9, dv="Local", key="FK → tbl_armazenagem"),
        col("Frases_H", 30, desc="Códigos H/EUH da secção 2 da FDS separados por ';' (vazio = não classificado)."), col("Pictogramas", 18, req=False), col("Palavra_Sinal", 9, req=False),
        col("Categoria_Seveso", 14, dv="Seveso", desc="Categoria do anexo I do DL 150/2015 ('—' se nenhuma)."), col("Categoria_Seveso_2", 10, dv="Seveso", req=False),
        col("SVHC_Declarado", 10, dv="SimNaoPC", desc="SVHC ≥ 0,1% declarada na FDS (secção 3/15) ou pelo fornecedor."), col("Anexo_XVII", 22, desc="Entrada de restrição relevante ('—' se nenhuma)."),
        col("Diisocianatos_0_1", 9, dv="SimNao", desc="Diisocianatos ≥ 0,1% (entrada 74 → formação obrigatória)."), col("PFAS", 12, desc="Contém PFAS?"),
        col("Contacto_Alimentar", 9, dv="SimNao", desc="Usado na linha alimentar (FCM)?"), col("IDs_Aspetos", 16, key="FK → tbl_aspetos", req=False),
        col("Estado_Aprovacao", 14, dv="EstadoAprov"), col("Data_Aprovacao", 11, "date", req=False),
        col("Teor_COV", 8, "pct", desc="Fração de compostos orgânicos voláteis (FDS secção 9). Base do balanço de solventes/COV (LEG-04)."),
        col("COV_kg_ano", 9, "num0", f='=IF(@ID_Quimico@="","",N(@Qtd_Ano_kg@)*N(@Teor_COV@))', desc="COV emitidos (kg/ano) = quantidade × teor (sem tratamento de efluentes gasosos)."),
        col("H_norm", 12, f='=IF(@ID_Quimico@="","",";"&SUBSTITUTE(SUBSTITUTE(@Frases_H@," ",""),",",";")&";")', desc="Frases H normalizadas para pesquisa (auxiliar)."),
        col("Perigoso", 8, f=f'=IF(@ID_Quimico@="","",IF(SUMPRODUCT(--{hit})>0,"Sim","Não"))', desc="Tem pelo menos uma frase H/EUH."),
        col("Classe_Perigo_Saude", 8, "int", f=f'=IF(@ID_Quimico@="","",MAX(1,IFERROR(_xlfn.AGGREGATE(14,6,tbl_frases_h[Classe_Perigo_Saude]/{hit},1),1)))',
            desc="Classe 1–5 = a mais alta das frases H/EUH (método de avaliação)."),
        col("CMR", 11, f=(f'=IF(@ID_Quimico@="","",IF(SUMPRODUCT({hit}*(tbl_frases_h[CMR_Categoria]="1"))>0,"Cat. 1A/1B",'
                          f'IF(SUMPRODUCT({hit}*(tbl_frases_h[CMR_Categoria]="2"))>0,"Cat. 2","Não")))'), desc="Cancerígeno, mutagénico ou reprotóxico."),
        col("Sensibilizante", 9, f=f'=IF(@ID_Quimico@="","",IF(SUMPRODUCT({hit}*(tbl_frases_h[Grupo]="Sensibilizante"))>0,"Sim","Não"))'),
        col("Toxico_Agudo", 8, f=f'=IF(@ID_Quimico@="","",IF(SUMPRODUCT({hit}*(tbl_frases_h[Grupo]="Toxicidade aguda (cat. 1-3)"))>0,"Sim","Não"))', desc="Toxicidade aguda cat. 1–3."),
        col("STOT", 8, f=f'=IF(@ID_Quimico@="","",IF(SUMPRODUCT({hit}*ISNUMBER(SEARCH("STOT",tbl_frases_h[Grupo])))>0,"Sim","Não"))', desc="Toxicidade para órgãos-alvo."),
        col("Perigoso_Ambiente", 9, f=f'=IF(@ID_Quimico@="","",IF(SUMPRODUCT({hit}*(tbl_frases_h[Tipo]="Ambiente"))>0,"Sim","Não"))'),
        col("Inflamavel", 8, f=f'=IF(@ID_Quimico@="","",IF(SUMPRODUCT({hit}*(tbl_frases_h[Grupo]="Inflamável"))>0,"Sim","Não"))'),
        col("Protecao_Maternidade", 10, f=f'=IF(@ID_Quimico@="","",IF(SUMPRODUCT({hit}*(tbl_frases_h[Protecao_Maternidade]="S"))>0,"Sim","Não"))',
            desc="Exige avaliação para grávidas/lactantes (Lei 102/2009; CT art. 62.º)."),
        col("SVHC_Componentes", 9, f='=IF(@ID_Quimico@="","",IF(COUNTIFS(tbl_componentes[ID_Quimico],@ID_Quimico@,tbl_componentes[SVHC_Acima_Limiar],"Sim")>0,"Sim","Não"))',
            desc="Algum componente da secção 3 é SVHC vigiada ≥ 0,1%."),
        col("Data_FDS_Vigor", 11, "date", f=f'=IF(@ID_Quimico@="","",IFERROR({lookup("tbl_fds", "Chave_Vigor", "Data_FDS", "@ID_Quimico@")},""))', desc="Data da FDS em vigor."),
        col("Estado_FDS", 20, f=(f'=IF(@ID_Quimico@="","",IFERROR({lookup("tbl_fds", "Chave_Vigor", "Estado_FDS", "@ID_Quimico@")},'
                                 f'IF(@Tipo_Produto@="Artigo","N.A. (artigo)",IF(@Perigoso@="Sim","Sem FDS","Sem FDS (não obrigatória)"))))'), desc="Estado da FDS em vigor."),
        col("Avaliacao_Risco", 10, f='=IF(@ID_Quimico@="","",IF(COUNTIF(tbl_risco_quimico[ID_Quimico],@ID_Quimico@)>0,"Feita",IF(@Perigoso@="Não","N.A.",IF(@Classe_Perigo_Saude@=1,"N.A. (só perigo físico — ATEX/SCIE)","Em falta"))))',
            desc="Existe avaliação de risco (DL 24/2012) para o produto?"),
        col("Alerta", 30, f=('=IF(@ID_Quimico@="","",IF(OR(@Estado_Aprovacao@="Suspenso",@Estado_Aprovacao@="Proibido"),"Uso bloqueado — "&@Estado_Aprovacao@,'
                             'IF(@CMR@="Cat. 1A/1B","CMR 1A/1B — substituir (DL 301/2000)",IF(OR(@SVHC_Declarado@="Sim",@SVHC_Componentes@="Sim"),"SVHC — plano de substituição",'
                             'IF(OR(@SVHC_Declarado@="Por confirmar",@PFAS@="Por confirmar"),"Pedir declaração (SVHC/PFAS)",'
                             'IF(ISNUMBER(SEARCH("Pedir",@Estado_FDS@)),"FDS — "&@Estado_FDS@,IF(@Estado_FDS@="Sem FDS","FDS em falta",'
                             'IF(@Avaliacao_Risco@="Em falta","Avaliação de risco em falta",IF(@Origem_EEE@="Não","Importação — ver registo","OK")))))))))'),
            desc="Alerta de gestão por ordem de prioridade."),
    ]
    inv_rows = []
    for r in INV:
        x = dict(zip(names_inv, r))
        x["Data_Aprovacao"] = D(x["Data_Aprovacao"])
        x["ID_Fornecedor"] = x["ID_Fornecedor"] if x["ID_Fornecedor"] != "—" else FORN_ID[x["Fornecedor"]]
        x["Frases_H"] = x["Frases_H"] or None
        x["Teor_COV"] = TEOR_COV.get(x["ID_Quimico"], 0)
        if x["ID_Quimico"] in QTD_ENV:
            x["Qtd_Ano_kg"] = QTD_ENV[x["ID_Quimico"]]
        inv_rows.append(x)
    b.table("Inventario", "tbl_quimicos", inv_cols, inv_rows,
            "Inventário de produtos químicos (1 linha por produto comercial): identificação, fornecedor, papel REACH, quantidades, classificação CLP e perigos calculados.",
            title="INVENTÁRIO DE PRODUTOS QUÍMICOS — REACH / CLP / TOXICIDADE",
            subtitle="Brancas = entrada (secção 2 e 3 da FDS) · Cinzentas = calculadas a partir das frases H e das outras folhas · Um produto novo só entra com Estado 'Em avaliação' até concluir o PR-SGA-16",
            cf=[("Alerta", {"bloqueado": "red", "CMR": "red", "SVHC": "red", "Pedir": "orange", "falta": "orange", "Importação": "yellow", "OK": "green"}),
                ("CMR", {"1A/1B": "red", "Cat. 2": "orange"}), ("Estado_Aprovacao", {"Suspenso": "red", "condicionado": "yellow", "Aprovado": "green"}),
                ("Sensibilizante", {"Sim": "orange"}), ("Perigoso_Ambiente", {"Sim": "blue"}), ("Protecao_Maternidade", {"Sim": "purple"})],
            row_height=36, extra_rows=30, freeze_col=2, tab_color="C0392B")

    # ---------------------------------------------------------------- componentes
    cp_cols = [col("ID_Componente", 9, key="PK"), col("ID_Quimico", 9, key="FK → tbl_quimicos"), col("Componente", 42), col("CAS", 12), col("CE", 11, req=False),
               col("Conc_Min_pct", 8, "num", desc="% m/m mínima (secção 3)."), col("Conc_Max_pct", 8, "num", desc="% m/m máxima (secção 3)."),
               col("Registo_REACH", 24, desc="N.º de registo indicado na FDS, isenção ou pedido."), col("VLE_Referencia", 40, req=False, desc="VLE UE/PT aplicável (DL 24/2012; NP 1796)."),
               col("SVHC_Vigiada", 8, f='=IF(@ID_Componente@="","",IF(COUNTIF(tbl_svhc_vigiadas[CAS],@CAS@)>0,"Sim","Não"))', desc="O CAS está na lista de SVHC vigiadas."),
               col("SVHC_Acima_Limiar", 8, f='=IF(@ID_Componente@="","",IF(AND(@SVHC_Vigiada@="Sim",@Conc_Max_pct@/100>=p_Limiar_SVHC),"Sim","Não"))', desc="SVHC ≥ 0,1% na mistura."),
               col("Consulta_ECHA", 16, f='=IF(@CAS@="","",IF(@CAS@="—","",HYPERLINK("https://chem.echa.europa.eu/","ECHA CHEM — pesquisar "&@CAS@)))',
                   desc="Ligação à pesquisa da ECHA (classificação harmonizada, registo, C&L).")]
    cp_rows = [dict(ID_Componente=f"CMP-{i:03d}", ID_Quimico=c[0], Componente=c[1], CAS=c[2], CE=c[3], Conc_Min_pct=c[4], Conc_Max_pct=c[5], Registo_REACH=c[6], VLE_Referencia=c[7] or None)
               for i, c in enumerate(COMP, start=1)]
    b.table("Componentes", "tbl_componentes", cp_cols, cp_rows,
            "Componentes perigosos da secção 3 das FDS, com VLE e cruzamento automático com as SVHC vigiadas.",
            title="COMPONENTES PERIGOSOS (SECÇÃO 3 DA FDS)", subtitle="Uma linha por componente · SVHC calculada por CAS · Ligação à ECHA para confirmar a classificação harmonizada (anexo VI do CLP)",
            cf=[("SVHC_Acima_Limiar", {"Sim": "red"}), ("SVHC_Vigiada", {"Sim": "orange"})], row_height=30, extra_rows=40)

    # ---------------------------------------------------------------- FDS
    chk_cols = [col(c, 9, dv="SimNaoNA", desc=q) for c, q in zip(FDS_CHK, FDS_Q)]
    nao = "+".join(f'(@{c}@="Não")' for c in FDS_CHK)
    fds_cols = [col("ID_FDS", 10, key="PK"), col("ID_Quimico", 9, key="FK → tbl_quimicos"),
                col("Produto", 30, f=f'=IF(@ID_Quimico@="","",IFERROR({lookup("tbl_quimicos", "ID_Quimico", "Nome_Comercial", "@ID_Quimico@")},"ID inválido"))'),
                col("Data_Rececao", 11, "date"), col("Data_FDS", 11, "date", desc="Data de revisão da FDS."), col("Versao", 7)] + chk_cols + [
                col("Disponivel_Posto", 9, dv="SimNao", desc="FDS (ou ficha-resumo) acessível no posto de trabalho (art. 35.º)."),
                col("Pedido_Fornecedor", 11, "date", req=False, desc="Data do pedido de correção/atualização ao fornecedor."),
                col("Verificado_Por", 22, dv="Funcao"),
                col("N_Nao", 6, "int", f=f'=IF(@ID_FDS@="","",{nao})', desc="Pontos não conformes."),
                col("Resultado", 16, f='=IF(@ID_FDS@="","",IF(@N_Nao@=0,"Conforme","Pedir correção"))'),
                col("Idade_Meses", 7, "int", f='=IF(OR(@ID_FDS@="",@Data_FDS@=""),"",DATEDIF(@Data_FDS@,DataRef,"m"))', desc="Idade da FDS na data de referência."),
                col("Em_Vigor", 7, f='=IF(@ID_FDS@="","",IF(@Data_FDS@=_xlfn.MAXIFS(#Data_FDS#,#ID_Quimico#,@ID_Quimico@),"Sim","Não"))', desc="Versão mais recente do produto."),
                col("Chave_Vigor", 9, f='=IF(@Em_Vigor@="Sim",@ID_Quimico@,"")', desc="Auxiliar para o inventário."),
                col("Estado_FDS", 22, f=('=IF(@ID_FDS@="","",IF(@Em_Vigor@="Não","Substituída (conservar 10 anos)",IF(@N_Nao@>0,"Pedir correção ao fornecedor",'
                                         'IF(@Idade_Meses@>p_Meses_FDS,"Pedir confirmação (> "&p_Meses_FDS&" meses)","OK"))))'))]
    fds_rows = []
    for f in FDS:
        i, q, dr, dfds, v, chk, disp, ped, ver = f
        x = dict(ID_FDS=i, ID_Quimico=q, Data_Rececao=D(dr), Data_FDS=D(dfds), Versao=v, Disponivel_Posto=disp, Pedido_Fornecedor=D(ped), Verificado_Por=ver)
        x.update(dict(zip(FDS_CHK, [{"S": "Sim", "N": "Não", "NA": "N.A."}[t] for t in chk.split()])))
        fds_rows.append(x)
    b.table("FDS_Verificacao", "tbl_fds", fds_cols, fds_rows,
            "Verificação de cada versão de FDS recebida (checklist Reg. (UE) 2020/878), com histórico, idade e estado da versão em vigor.",
            title="VERIFICAÇÃO DAS FICHAS DE DADOS DE SEGURANÇA (REACH art. 31.º; anexo II — Reg. (UE) 2020/878)",
            subtitle="Uma linha por VERSÃO recebida (não apagar as antigas — art. 36.º) · 'Não' em qualquer ponto → pedir correção ao fornecedor (art. 34.º) · 36 meses = critério interno",
            cf=[("Estado_FDS", {"OK": "green", "Pedir": "orange", "Substituída": "gray"}), ("Resultado", {"Conforme": "green", "Pedir": "orange"})] + [(c, {"Não": "red"}) for c in FDS_CHK],
            row_height=30, extra_rows=40, freeze_col=3)

    # ---------------------------------------------------------------- cenários de exposição
    ce_names = ["ID_CE", "ID_Quimico", "ID_FDS", "Substancia_CE", "Titulo_CE", "Descritores_Fornecedor", "Uso_Real", "PROC_Real", "Condicoes_CE", "Condicoes_Reais",
                "Metodo_Verificacao", "Resultado", "Acao", "Data_Implementacao", "Responsavel"]
    ce_cols = [col("ID_CE", 7, key="PK"), col("ID_Quimico", 9, key="FK → tbl_quimicos"), col("ID_FDS", 9, key="FK → tbl_fds"), col("Substancia_CE", 26),
               col("Titulo_CE", 30), col("Descritores_Fornecedor", 18, desc="SU / PROC / ERC / PC do CE."), col("Uso_Real", 34, desc="Como a Plasticom usa (tarefa, duração, quantidade)."),
               col("PROC_Real", 10, desc="Categoria de processo real (ECHA R.12)."), col("Condicoes_CE", 40, desc="Condições operacionais e medidas de gestão de risco do CE."),
               col("Condicoes_Reais", 36), col("Metodo_Verificacao", 18, dv="MetodoCE"), col("Resultado", 13, dv="ResultadoCE"), col("Acao", 26, dv="AcaoCE", desc="Opções do art. 37.º, n.º 4."),
               col("Data_Implementacao", 11, "date", req=False), col("Responsavel", 22, dv="Funcao"),
               col("Data_Rececao_FDS", 11, "date", f=f'=IF(@ID_CE@="","",IFERROR({lookup("tbl_fds", "ID_FDS", "Data_Rececao", "@ID_FDS@")},""))'),
               col("Prazo_Legal", 11, "date", f='=IF(OR(@ID_CE@="",@Data_Rececao_FDS@=""),"",IF(@Resultado@="Coberto","",EDATE(@Data_Rececao_FDS@,p_Meses_CE)))', desc="12 meses após a receção (art. 39.º)."),
               col("Prazo_Relatorio_ECHA", 11, "date", f='=IF(@Acao@="Elaborar RSQ-UJ (art. 37.º, n.º 4)",EDATE(@Data_Rececao_FDS@,p_Meses_RSQ),"")', desc="6 meses se houver RSQ-UJ."),
               col("Estado", 22, f=('=IF(@ID_CE@="","",IF(@Resultado@="Coberto","Conforme",IF(@Data_Implementacao@<>"","Implementado",'
                                    'IF(@Prazo_Legal@<DataRef,"Prazo legal ultrapassado","Em curso — "&TEXT(@Prazo_Legal@-DataRef,"0")&" dias"))))'))]
    ce_rows = [dict(zip(ce_names, c)) for c in CE]
    b.table("Cenarios_Exposicao", "tbl_ce_reach", ce_cols, ce_rows,
            "Verificação dos cenários de exposição das FDS alargadas face ao uso real (REACH art. 37.º, n.º 4–6, e 39.º).",
            title="CENÁRIOS DE EXPOSIÇÃO — VERIFICAÇÃO PELO UTILIZADOR A JUSANTE",
            subtitle="Passos ECHA: 1) descrever o uso real (PROC) 2) comparar com o CE 3) se não coberto: escalonar, pedir ao fornecedor, RSQ-UJ ou substituir · Prazo: 12 meses após a receção da FDS",
            cf=[("Resultado", {"Não coberto": "red", "Parcialmente": "orange", "Coberto": "green"}), ("Estado", {"ultrapassado": "red", "Em curso": "orange", "Conforme": "green", "Implementado": "green"})],
            row_height=60, extra_rows=20, freeze_col=2)

    # ---------------------------------------------------------------- registo / importação
    imp_names = ["ID_Imp", "ID_Fornecedor", "Fornecedor", "Pais", "Origem_EEE", "Material", "Qtd_t_Ano", "Importador_Legal", "Representante_Unico", "Data_Carta_RU",
                 "Plasticom_Lista_RU", "Substancias_a_Registar", "Observacao"]
    imp_cols = [col("ID_Imp", 7, key="PK"), col("ID_Fornecedor", 9, key="FK → tbl_fornecedores"), col("Fornecedor", 26), col("Pais", 11), col("Origem_EEE", 7, dv="SimNao"),
                col("Material", 20), col("Qtd_t_Ano", 8, "num1"), col("Importador_Legal", 24, desc="Quem introduz a mercadoria na UE (ver fatura/incoterm/declaração aduaneira)."),
                col("Representante_Unico", 26, req=False), col("Data_Carta_RU", 11, "date", req=False), col("Plasticom_Lista_RU", 8, dv="SimNao", req=False, desc="A carta do RU cita a Plasticom como importador coberto?"),
                col("Substancias_a_Registar", 40, desc="Monómeros (≥ 2% e ≥ 1 t/ano) e aditivos (≥ 1 t/ano)."), col("Observacao", 44, req=False),
                col("Conclusao", 34, f=('=IF(@ID_Imp@="","",IF(@Origem_EEE@="Sim","N.A. — fornecedor no EEE (registo a montante)",'
                                        'IF(@Importador_Legal@<>"Plasticom","Utilizador a jusante (importador: "&@Importador_Legal@&")",'
                                        'IF(AND(@Data_Carta_RU@<>"",@Plasticom_Lista_RU@="Sim"),"Coberto por RU — Plasticom = utilizador a jusante",'
                                        'IF(@Qtd_t_Ano@<1,"Abaixo de 1 t/ano — sem registo","LACUNA — Plasticom é importador: RU ou registo próprio")))))'))]
    imp_rows = []
    for r in IMP:
        x = dict(zip(imp_names, r))
        x["Data_Carta_RU"] = D(x["Data_Carta_RU"])
        for k in ("Representante_Unico", "Plasticom_Lista_RU", "Observacao"):
            x[k] = x[k] or None
        imp_rows.append(x)
    b.table("Registo_Importacao", "tbl_registo_reach", imp_cols, imp_rows,
            "Verificação, fornecedor a fornecedor, se a Plasticom é importadora e se as substâncias estão registadas (RU, filial UE ou registo próprio).",
            title="REGISTO REACH — IMPORTAÇÃO DE FORA DO EEE E REPRESENTANTE ÚNICO",
            subtitle="Polímeros estão isentos de registo, mas os monómeros e aditivos não (art. 6.º, n.º 3) · Sem RU nem importador UE, a Plasticom tem de registar (ver PR-SGA-16, §6.6)",
            cf=[("Conclusao", {"LACUNA": "red", "Coberto": "green", "N.A.": "gray", "Utilizador": "green"})], row_height=45, extra_rows=15)

    # ---------------------------------------------------------------- declarações
    dec_names = ["ID_Decl", "ID_Fornecedor", "Fornecedor", "Material", "Data_Declaracao", "Lista_Coberta_N", "SVHC_0_1", "Metais_PPWR_Conforme", "PFAS", "BPA", "Ftalatos", "DoC_FCM"]
    dec_cols = [col("ID_Decl", 8, key="PK"), col("ID_Fornecedor", 9, key="FK → RG-SGA-11"), col("Fornecedor", 26), col("Material", 28),
                col("Data_Declaracao", 11, "date", req=False), col("Lista_Coberta_N", 9, "int", req=False, desc="N.º de entradas da lista candidata coberto pela declaração."),
                col("SVHC_0_1", 18, desc="SVHC > 0,1% m/m?"), col("Metais_PPWR_Conforme", 10, desc="Pb+Cd+Hg+Cr(VI) ≤ 100 mg/kg?"), col("PFAS", 12), col("BPA", 10), col("Ftalatos", 10),
                col("DoC_FCM", 8, desc="Declaração de conformidade para contacto alimentar (Reg. 10/2011)."),
                col("Idade_Meses", 7, "int", f='=IF(OR(@ID_Decl@="",@Data_Declaracao@=""),"",DATEDIF(@Data_Declaracao@,DataRef,"m"))'),
                col("Estado", 24, f=('=IF(@ID_Decl@="","",IF(@Data_Declaracao@="","Em falta — pedir",IF(N(@Lista_Coberta_N@)<p_SVHC_N,"Desatualizada — pedir nova",'
                                     'IF(OR(@SVHC_0_1@="Por confirmar",@PFAS@="Por confirmar"),"Incompleta",IF(@Idade_Meses@>12,"Renovar (> 12 meses)","Atualizada")))))'))]
    dec_rows = []
    for r in DEC:
        x = dict(zip(dec_names, r))
        x["Data_Declaracao"] = D(x["Data_Declaracao"])
        dec_rows.append(x)
    b.table("Declaracoes_SVHC", "tbl_declaracoes", dec_cols, dec_rows,
            "Declarações dos fornecedores (SVHC, metais pesados PPWR, PFAS, BPA, ftalatos, contacto alimentar) com a versão da lista candidata coberta.",
            title="DECLARAÇÕES DE FORNECEDORES — SVHC, PFAS, METAIS, BPA, FTALATOS E FCM",
            subtitle="Uma declaração 'sem SVHC' só vale para a lista que cobre: se Lista_Coberta_N < P-01 → pedir nova · Renovar pelo menos anualmente",
            cf=[("Estado", {"falta": "red", "Desatualizada": "orange", "Incompleta": "orange", "Renovar": "yellow", "Atualizada": "green"}), ("SVHC_0_1", {"Sim": "red", "Por confirmar": "orange"})],
            row_height=30, extra_rows=20)

    # ---------------------------------------------------------------- métodos (tabelas de pontuação)
    b.table("Metodologia", "tbl_m_volat", [col("Volatilidade", 60, key="PK"), col("Score", 8, "num3")],
            [dict(Volatilidade=k, Score=v) for k, v in VOLAT],
            "Método de avaliação de risco químico (adaptado de INRS ND 2233 e Seirich/ED 6485): pontuações de volatilidade, procedimento, proteção coletiva, superfície e frequência.",
            title="METODOLOGIA DE AVALIAÇÃO DO RISCO QUÍMICO (ADAPTADA DE INRS ND 2233 / SEIRICH)",
            subtitle="Inalação = 10^(Classe−1) × Volatilidade × Procedimento × Proteção coletiva · Cutâneo = 10^(Classe−1) × Superfície × Frequência · > 1000 → P1; 100–1000 → P2; < 100 → P3")
    ws_m = b.wb["Metodologia"]
    b.sheets_info.pop()
    b.sheets_info.append(("Metodologia", "Método de avaliação do risco químico (tabelas tbl_m_*), explicação e limites de uso."))

    def small_table(ws, r0, c0, name, hdr, rows, fmt=None):
        from openpyxl.utils import get_column_letter as L
        from openpyxl.worksheet.table import Table, TableStyleInfo
        for j, hh in enumerate(hdr):
            c = ws.cell(row=r0, column=c0 + j, value=hh)
            c.font, c.fill, c.alignment, c.border = F_HEAD, FILL_HEAD, CENTER, BORDER
        for i, row in enumerate(rows, start=1):
            for j, v in enumerate(row):
                c = ws.cell(row=r0 + i, column=c0 + j, value=v)
                c.font, c.border, c.alignment = F_BASE, BORDER, WRAP_TOP
        t = Table(displayName=name, ref=f"{L(c0)}{r0}:{L(c0 + len(hdr) - 1)}{r0 + len(rows)}")
        t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
        ws.add_table(t)

    small_table(ws_m, 4, 4, "tbl_m_proced", ["Procedimento", "Score"], PROCED)
    small_table(ws_m, 4, 7, "tbl_m_prot", ["Protecao", "Score"], PROT)
    small_table(ws_m, 12, 1, "tbl_m_superf", ["Superficie", "Score"], SUPERF)
    small_table(ws_m, 12, 4, "tbl_m_freq", ["Frequencia", "Score"], FREQ)
    small_table(ws_m, 12, 7, "tbl_m_classes", ["Classe", "Score_Perigo", "Exemplos de frases H"],
                [(1, 1, "Sem frases H de saúde"), (2, 10, "H304, H315, H319, H336, EUH066"), (3, 100, "H302, H312, H332, H317, H318, H335, H362, EUH204"),
                 (4, 1000, "H301, H311, H331, H314, H341, H351, H361, H371, H373"), (5, 10000, "H300, H310, H330, H334, H340, H350, H360, H370, H372")])
    for cl, w in zip("ABCDEFGHI", [52, 9, 3, 52, 9, 3, 52, 12, 50]):
        ws_m.column_dimensions[cl].width = w
    notas = ["COMO LER: o método dá uma PRIORIDADE (P1 muito alta, P2 alta, P3 moderada) do risco potencial por tarefa, antes dos EPI. Não é uma medição.",
             "Classe de perigo: a mais alta das frases H/EUH do produto (tbl_frases_h); agentes gerados no processo (fumos) usam a classe manual.",
             "Procedimento: categorias do guia técnico europeu usadas no Seirich — dispersivo, aberto, fechado com aberturas regulares, fechado.",
             "Proteção coletiva: considera-se a mais eficaz existente (ventilação geral ou captação); sem manutenção anual comprovada usar a linha seguinte (menos eficaz).",
             "Cutâneo: superfície exposta sem contar com luvas ou vestuário; 'Sem contacto possível' anula o risco cutâneo.",
             "Regras que se sobrepõem à pontuação: CMR 1A/1B → DL 301/2000 (substituir, lista de expostos); sensibilizantes → vigilância da saúde; VLE existente e P1/P2 → medir (NP EN 689).",
             "Fonte dos fatores: INRS ND 2233 (2005) e INRS ED 6485 (Seirich); os valores numéricos são uma adaptação documentada — rever se a Plasticom adotar o Seirich."]
    for i, t in enumerate(notas):
        c = ws_m.cell(row=20 + i, column=1, value=t)
        c.font, c.alignment = (F_BOLD if i == 0 else F_BASE), Alignment(wrap_text=False, vertical="top")

    # ---------------------------------------------------------------- avaliação de risco
    rk_names = ["ID_Avaliacao", "ID_Quimico", "Agente_Gerado", "Posto_Tarefa", "Processo", "Funcao_Exposta", "N_Trabalhadores", "Classe_Manual", "Volatilidade",
                "Procedimento", "Protecao_Coletiva", "Superficie_Cutanea", "Frequencia", "EPI", "Medidas_Existentes", "ID_Medicao", "Medidas_Adicionais",
                "Risco_Residual", "Responsavel", "Prazo", "Data_Avaliacao", "Avaliador"]
    INV_L = lambda c: f'IFERROR({lookup("tbl_quimicos", "ID_Quimico", c, "@ID_Quimico@")},"")'
    rk_cols = [col("ID_Avaliacao", 8, key="PK"), col("ID_Quimico", 9, key="FK → tbl_quimicos", req=False), col("Agente_Gerado", 24, req=False, desc="Agente gerado pelo processo (fumos, poeiras) — sem ID."),
               col("Posto_Tarefa", 32), col("Processo", 7, dv="Processo"), col("Funcao_Exposta", 20, dv="Funcao"), col("N_Trabalhadores", 7, "int"),
               col("Classe_Manual", 7, "int", req=False, desc="Classe 1–5 só para agentes gerados (sem ID)."),
               col("Volatilidade", 22, dv="Volatilidade"), col("Procedimento", 20, dv="Procedimento"), col("Protecao_Coletiva", 22, dv="ProtColetiva"),
               col("Superficie_Cutanea", 14, dv="Superficie"), col("Frequencia", 16, dv="Frequencia"), col("EPI", 24), col("Medidas_Existentes", 28),
               col("ID_Medicao", 14, key="FK → tbl_medicoes_vle", req=False), col("Medidas_Adicionais", 32, req=False), col("Risco_Residual", 8, dv="RiscoResidual", desc="Após medidas existentes e EPI."),
               col("Responsavel", 20, dv="Funcao"), col("Prazo", 11, "date", req=False), col("Data_Avaliacao", 11, "date"), col("Avaliador", 20, dv="Funcao"),
               col("Produto", 26, f=f'=IF(@ID_Avaliacao@="","",IF(@ID_Quimico@="",@Agente_Gerado@,{INV_L("Nome_Comercial")}))'),
               col("Classe_Perigo", 7, "int", f=f'=IF(@ID_Avaliacao@="","",IF(@ID_Quimico@="",@Classe_Manual@,{INV_L("Classe_Perigo_Saude")}))'),
               col("CMR", 10, f=f'=IF(OR(@ID_Avaliacao@="",@ID_Quimico@=""),"",{INV_L("CMR")})'),
               col("Sensibilizante", 8, f=f'=IF(OR(@ID_Avaliacao@="",@ID_Quimico@=""),"",{INV_L("Sensibilizante")})'),
               col("Protecao_Maternidade", 9, f=f'=IF(OR(@ID_Avaliacao@="",@ID_Quimico@=""),"",{INV_L("Protecao_Maternidade")})'),
               col("Score_Inalacao", 10, "num1", f=('=IF(@ID_Avaliacao@="","",10^(@Classe_Perigo@-1)*INDEX(tbl_m_volat[Score],MATCH(@Volatilidade@,tbl_m_volat[Volatilidade],0))'
                                                    '*INDEX(tbl_m_proced[Score],MATCH(@Procedimento@,tbl_m_proced[Procedimento],0))*INDEX(tbl_m_prot[Score],MATCH(@Protecao_Coletiva@,tbl_m_prot[Protecao],0)))')),
               col("Score_Cutaneo", 10, "num0", f=('=IF(@ID_Avaliacao@="","",10^(@Classe_Perigo@-1)*INDEX(tbl_m_superf[Score],MATCH(@Superficie_Cutanea@,tbl_m_superf[Superficie],0))'
                                                   '*INDEX(tbl_m_freq[Score],MATCH(@Frequencia@,tbl_m_freq[Frequencia],0)))')),
               col("Prioridade", 12, f='=IF(@ID_Avaliacao@="","",IF(MAX(@Score_Inalacao@,@Score_Cutaneo@)>1000,"P1 — muito alta",IF(MAX(@Score_Inalacao@,@Score_Cutaneo@)>=100,"P2 — alta","P3 — moderada")))'),
               col("Regime_Especifico", 34, f=('=IF(@ID_Avaliacao@="","",IF(@CMR@="Cat. 1A/1B","DL 301/2000: substituir; sistema fechado; lista de expostos; vigilância da saúde",'
                                               'IF(@Sensibilizante@="Sim","Sensibilizante: vigilância da saúde; luvas do material indicado na FDS",'
                                               'IF(@Classe_Perigo@>=4,"Tóxico/corrosivo/CMR 2: acesso restrito; EPI obrigatório; formação","Medidas gerais do DL 24/2012"))))')),
               col("Medir_Exposicao", 12, f='=IF(@ID_Avaliacao@="","",IF(@ID_Medicao@<>"","Sim — "&@ID_Medicao@,IF(AND(LEFT(@Prioridade@,2)<>"P3",@Score_Inalacao@>=100),"Avaliar medição","Não necessário")))'),
               col("Proxima_Revisao", 11, "date", f='=IF(OR(@ID_Avaliacao@="",@Data_Avaliacao@=""),"",EDATE(@Data_Avaliacao@,p_Meses_ARQ))'),
               col("Estado", 14, f='=IF(@ID_Avaliacao@="","",IF(@Proxima_Revisao@<DataRef,"Revisão em atraso",IF(AND(@Prazo@<>"",@Prazo@<DataRef),"Medidas em atraso","Em dia")))')]
    rk_rows = []
    # fecho do ano (31/12/2026): medidas adicionais implementadas no 4.º trimestre → passam a medidas existentes e a tarefa é reavaliada
    FECHO_ARQ = {"ARQ-01": ("Mesa aspirante na SS-002 e na SS-001 (17/12/2026); tampas nos recipientes", "2026-12-17"),
                 "ARQ-03": ("Formação diisocianatos (entrada 74) de todos os operadores, incl. os 2 novos (27/10/2026); mistura na mesa aspirante", "2026-10-27"),
                 "ARQ-08": ("Uso só no arranque; lata de 0,5 L; declaração do fornecedor: D4/D5/D6 < 0,1% (27/11/2026)", "2026-11-27"),
                 "ARQ-09": ("Limpa-moldes sem n-hexano (base de ésteres) desde 10/12/2026 — reavaliar a classe de perigo com a nova FDS", "2026-12-10"),
                 "ARQ-11": ("Sala de carga ventilada; lava-olhos; viseira facial completa (30/10/2026)", "2026-10-30"),
                 "ARQ-13": ("Operação trimestral no exterior; bacias separadas do anti-incrustante (30/10/2026); bomba doseadora para o choque (15/11/2026)", "2026-11-15")}
    RISCO_F = []
    for r in RISCO:
        if r[0] in FECHO_ARQ:
            med, dat = FECHO_ARQ[r[0]]
            r = r[:14] + (med, r[15], "", r[17], r[18], "", dat) + r[21:]
        RISCO_F.append(r)
    for r in RISCO_F:
        x = dict(zip(rk_names, r))
        x["Prazo"], x["Data_Avaliacao"] = D(x["Prazo"]), D(x["Data_Avaliacao"])
        for k in ("ID_Quimico", "Agente_Gerado", "ID_Medicao", "Medidas_Adicionais"):
            x[k] = x[k] or None
        rk_rows.append(x)
    b.table("Avaliacao_Risco", "tbl_risco_quimico", rk_cols, rk_rows,
            "Avaliação de risco químico por tarefa para a saúde dos trabalhadores (toxicidade — DL 24/2012 e DL 301/2000), inalação e cutâneo, com prioridade e medidas.",
            title="AVALIAÇÃO DE RISCO QUÍMICO POR TAREFA — TOXICIDADE (DL 24/2012; DL 301/2000)",
            subtitle="Uma linha por tarefa × produto (ou agente gerado) · Pontuação na folha Metodologia · P1 → medidas imediatas · Rever em 36 meses e em cada alteração",
            cf=[("Prioridade", {"P1": "red", "P2": "orange", "P3": "green"}), ("CMR", {"1A/1B": "red", "Cat. 2": "orange"}), ("Risco_Residual", {"Alto": "red", "Médio": "yellow", "Baixo": "green"}),
                ("Estado", {"atraso": "red", "Em dia": "green"})], row_height=48, extra_rows=30, freeze_col=4, tab_color="C0392B")

    # ---------------------------------------------------------------- medições
    md_names = ["ID_Medicao", "Data", "Posto", "Agente", "CAS", "Metodo", "Laboratorio", "N_Amostras", "Resultado_Max_ppm", "VLE_MP_ppm", "Observacao"]
    md_cols = [col("ID_Medicao", 12, key="PK"), col("Data", 11, "date"), col("Posto", 28), col("Agente", 24), col("CAS", 10), col("Metodo", 26), col("Laboratorio", 20),
               col("N_Amostras", 7, "int", req=False), col("Resultado_Max_ppm", 9, "num3", req=False), col("VLE_MP_ppm", 8, "num3", req=False), col("Observacao", 30, req=False),
               col("Indice_Exposicao", 8, "pct", f='=IF(OR(@Resultado_Max_ppm@="",N(@VLE_MP_ppm@)=0),"",@Resultado_Max_ppm@/@VLE_MP_ppm@)', desc="Resultado máximo ÷ VLE."),
               col("Limite_Teste_Preliminar", 8, "pct", f='=IF(@N_Amostras@="","",IF(@N_Amostras@=3,0.1,IF(@N_Amostras@=4,0.15,IF(@N_Amostras@>=5,0.2,""))))', desc="NP EN 689, anexo F."),
               col("Conclusao", 24, f=('=IF(@ID_Medicao@="","",IF(@Resultado_Max_ppm@="",IF(@Data@>DataRef,"Planeada","Resultado em falta"),'
                                       'IF(@Indice_Exposicao@>1,"Não conforme — ação imediata",IF(AND(@Limite_Teste_Preliminar@<>"",@Indice_Exposicao@<@Limite_Teste_Preliminar@),'
                                       '"Conforme (teste preliminar)","Inconclusivo — medição periódica"))))')),
               col("Proxima_Medicao", 11, "date", f=('=IF(@ID_Medicao@="","",IF(@Resultado_Max_ppm@="","",IF(ISNUMBER(SEARCH("Não conforme",@Conclusao@)),EDATE(@Data@,3),'
                                                     'IF(ISNUMBER(SEARCH("Inconclusivo",@Conclusao@)),EDATE(@Data@,12),EDATE(@Data@,36)))))'))]
    md_rows = []
    for m in MEDICOES:
        x = dict(zip(md_names, m))
        x["Data"] = D(x["Data"])
        x["Observacao"] = x["Observacao"] or None
        md_rows.append(x)
    b.table("Medicoes_VLE", "tbl_medicoes_vle", md_cols, md_rows,
            "Medições de exposição profissional a agentes químicos e conclusão pelo teste preliminar da NP EN 689.",
            title="MEDIÇÕES DE EXPOSIÇÃO PROFISSIONAL (NP EN 689:2018)",
            subtitle="Teste preliminar: 3 amostras < 10% do VLE, 4 < 15%, 5 < 20% → conforme · Senão: medição periódica · VLE: DL 24/2012 (diretivas IOELV) ou NP 1796",
            cf=[("Conclusao", {"Não conforme": "red", "Inconclusivo": "orange", "Conforme": "green", "Planeada": "blue"})], row_height=30, extra_rows=20)

    # ---------------------------------------------------------------- armazenagem
    ar_names = ["ID_Local", "Local", "Tipo", "Capacidade_Retencao_L", "Ventilacao", "ID_Meio", "Incompatibilidades_Verificadas", "ID_Ponto_Ronda", "Observacao"]
    ar_cols = [col("ID_Local", 8, key="PK"), col("Local", 44), col("Tipo", 12), col("Capacidade_Retencao_L", 10, "num0", req=False), col("Ventilacao", 10), col("ID_Meio", 9, key="FK → RG-SGA-12 tbl_meios", desc="Kit de derrame mais próximo (verificação e reposição registadas no RG-SGA-12)."),
               col("Incompatibilidades_Verificadas", 11, desc="Segregação verificada com a Matriz_Compatibilidade e a secção 10 das FDS."),
               col("ID_Ponto_Ronda", 9, key="FK → RG-SGA-10 tbl_pontos", desc="Ponto da ronda ambiental onde o local é inspecionado (a inspeção regista-se no RG-SGA-10)."),
               col("Observacao", 40, req=False),
               col("N_Produtos", 7, "int", f='=IF(@ID_Local@="","",COUNTIF(tbl_quimicos[Local_Armazenagem],@ID_Local@))'),
               col("Stock_Max_kg", 9, "num0", f='=IF(@ID_Local@="","",SUMIFS(tbl_quimicos[Stock_Max_kg],tbl_quimicos[Local_Armazenagem],@ID_Local@))', desc="≈ litros (densidade ≈ 1)."),
               col("Maior_Recipiente_L", 9, "num0", f='=IF(@ID_Local@="","",_xlfn.MAXIFS(tbl_quimicos[Volume_Embalagem_L],tbl_quimicos[Local_Armazenagem],@ID_Local@))'),
               col("Retencao_Necessaria_L", 10, "num0", f='=IF(OR(@ID_Local@="",@Capacidade_Retencao_L@=""),"",MAX(@Maior_Recipiente_L@,p_Fator_Retencao*@Stock_Max_kg@))',
                   desc="máx(100% do maior recipiente; P-07 × total)."),
               col("Estado", 22, f=('=IF(@ID_Local@="","",IF(@Incompatibilidades_Verificadas@="Não","Incompatibilidade — separar",IF(@Capacidade_Retencao_L@="","N.A. (sem líquidos a reter)",'
                                    'IF(@Capacidade_Retencao_L@<@Retencao_Necessaria_L@,"Retenção insuficiente",IF(OR(@ID_Ponto_Ronda@="",@ID_Ponto_Ronda@="—"),"Sem ponto de ronda","Conforme")))))'))]
    ar_rows = []
    for a in ARMAZ:
        x = dict(zip(ar_names, a))
        x["Observacao"] = x["Observacao"] or None
        ar_rows.append(x)
    b.table("Armazenagem", "tbl_armazenagem", ar_cols, ar_rows,
            "Locais de armazenagem de químicos: retenção necessária vs existente, compatibilidades, ventilação e inspeção.",
            title="ARMAZENAGEM DE PRODUTOS QUÍMICOS — RETENÇÃO E COMPATIBILIDADES",
            subtitle="Retenção ≥ máx(100% do maior recipiente; 50% do total) — critério interno P-07 · Stock a partir do inventário · Kits no RG-SGA-12 · Inspeções nas rondas do RG-SGA-10 (RON-02, RON-11)",
            cf=[("Estado", {"Incompatibilidade": "red", "insuficiente": "red", "Sem ponto": "orange", "Conforme": "green", "N.A.": "gray"})], row_height=36, extra_rows=10)

    # ---------------------------------------------------------------- matriz de compatibilidade (apresentação)
    ws = b.sheet("Matriz_Compatibilidade", "Matriz simplificada de armazenagem conjunta por classe de perigo (confirmar sempre as secções 7 e 10 das FDS).")
    ws["A1"] = "MATRIZ DE COMPATIBILIDADE DE ARMAZENAGEM (simplificada)"
    ws["A1"].font = F_TITLE
    ws["A2"] = "✓ pode armazenar junto · ! separar (bacias distintas / distância ou armário próprio) · ✗ incompatível — local separado · Confirmar sempre as secções 7 e 10 da FDS"
    ws["A2"].font = F_SUB
    cls = ["Inflamáveis (GHS02)", "Comburentes (GHS03)", "Gases sob pressão (GHS04)", "Corrosivos ácidos (GHS05)", "Corrosivos bases / hipoclorito (GHS05)",
           "Tóxicos agudos (GHS06)", "Perigo para a saúde (GHS07/08)", "Perigosos p/ ambiente (GHS09)"]
    M = [["✓", "✗", "!", "!", "!", "!", "✓", "✓"],
         ["✗", "✓", "!", "!", "!", "!", "!", "!"],
         ["!", "!", "✓", "!", "!", "!", "!", "!"],
         ["!", "!", "!", "✓", "✗", "!", "✓", "✓"],
         ["!", "!", "!", "✗", "✓", "!", "✓", "✓"],
         ["!", "!", "!", "!", "!", "✓", "✓", "✓"],
         ["✓", "!", "!", "✓", "✓", "✓", "✓", "✓"],
         ["✓", "!", "!", "✓", "✓", "✓", "✓", "✓"]]
    ws.column_dimensions["A"].width = 34
    for j, c in enumerate(cls):
        cell = ws.cell(row=4, column=2 + j, value=c)
        cell.font, cell.fill, cell.alignment, cell.border = F_HEAD, FILL_HEAD, CENTER, BORDER
        ws.column_dimensions[chr(66 + j)].width = 15
        rc = ws.cell(row=5 + j, column=1, value=c)
        rc.font, rc.fill, rc.border = F_BOLD, FILL_BAND, BORDER
    colors = {"✓": CF_COLORS["green"], "!": CF_COLORS["yellow"], "✗": CF_COLORS["red"]}
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            c = ws.cell(row=5 + i, column=2 + j, value=v)
            bg, fg = colors[v]
            c.fill, c.font, c.alignment, c.border = PatternFill("solid", fgColor=bg), Font(name=FONT, size=12, bold=True, color=fg), Alignment(horizontal="center", vertical="center"), BORDER
    ws.row_dimensions[4].height = 45
    for i, t in enumerate(["Casos da Plasticom:",
                           "• Hipoclorito (EUH031) + anti-incrustante ácido na mesma bacia da torre → liberta cloro: separar (ARM-04, PAM-26-33).",
                           "• Oxigénio separado de acetileno e propano por muro corta-fogo (ARM-06).",
                           "• Aerossóis (H222/H229) em armário próprio, longe de fontes de calor (ARM-05).",
                           "• Inflamáveis > 50 L fora de armário: local de risco C do RT-SCIE (ARM-01)."]):
        ws.cell(row=15 + i, column=1, value=t).font = F_BOLD if i == 0 else F_BASE

    # ---------------------------------------------------------------- Seveso
    sv_cols = [col("Categoria", 26, key="PK"), col("Designacao", 50), col("Limiar_Inferior_t", 10, "num0"), col("Limiar_Superior_t", 10, "num0"), col("Grupo_Soma", 14),
               col("Qtd_Presente_t", 10, "num3", f='=IF(@Categoria@="","",(SUMIFS(tbl_quimicos[Stock_Max_kg],tbl_quimicos[Categoria_Seveso],@Categoria@)+SUMIFS(tbl_quimicos[Stock_Max_kg],tbl_quimicos[Categoria_Seveso_2],@Categoria@))/1000)'),
               col("Racio_Inferior", 10, "num3", f='=IF(@Categoria@="","",@Qtd_Presente_t@/@Limiar_Inferior_t@)'),
               col("Racio_Superior", 10, "num3", f='=IF(@Categoria@="","",@Qtd_Presente_t@/@Limiar_Superior_t@)')]
    b.table("Seveso", "tbl_seveso", sv_cols, [dict(Categoria=s[0], Designacao=s[1], Limiar_Inferior_t=s[2], Limiar_Superior_t=s[3], Grupo_Soma=s[4]) for s in SEVESO],
            "Verificação Seveso (DL 150/2015): quantidade máxima por categoria, rácio face aos limiares e regra da soma por grupo.",
            title="VERIFICAÇÃO SEVESO (DIRETIVA 2012/18/UE; DL 150/2015) — REGRA DA SOMA",
            subtitle="Quantidades = Stock_Max_kg do inventário por categoria · Substâncias designadas (parte 2) prevalecem sobre as categorias · Resumo em tbl_seveso_resumo (à direita)",
            cf=[("Racio_Inferior", "@>=1", "red"), ("Racio_Inferior", "@>=0.1", "yellow")], row_height=18)
    ws_s = b.wb["Seveso"]
    small_table(ws_s, 4, 10, "tbl_seveso_resumo", ["Grupo", "Soma_Racio_Inferior", "Soma_Racio_Superior", "Conclusao"],
                [(g, f'=SUMPRODUCT(ISNUMBER(SEARCH("{g}",tbl_seveso[Grupo_Soma]))*tbl_seveso[Racio_Inferior])',
                  f'=SUMPRODUCT(ISNUMBER(SEARCH("{g}",tbl_seveso[Grupo_Soma]))*tbl_seveso[Racio_Superior])',
                  f'=IF(SUMPRODUCT(ISNUMBER(SEARCH("{g}",tbl_seveso[Grupo_Soma]))*tbl_seveso[Racio_Superior])>=1,"Nível superior",IF(SUMPRODUCT(ISNUMBER(SEARCH("{g}",tbl_seveso[Grupo_Soma]))*tbl_seveso[Racio_Inferior])>=1,"Nível inferior","Não abrangido (Σ < 1)"))')
                 for g in ("Saúde", "Físico", "Ambiente")])
    for r in range(5, 8):
        for cc in (11, 12):
            ws_s.cell(row=r, column=cc).number_format = "0.0000"
            ws_s.cell(row=r, column=cc).fill = FILL_CALC
        ws_s.cell(row=r, column=13).fill = FILL_CALC
    for cl, w in zip("JKLM", [12, 12, 12, 24]):
        ws_s.column_dimensions[cl].width = w

    # ---------------------------------------------------------------- matriz legal
    rq_names = ["ID_Req", "Ambito", "Tema", "Diploma", "Artigos", "Papel_Plasticom", "Obrigacao", "Aplicavel", "Justificacao", "Evidencia", "Frequencia", "Estado", "ID_Legal",
                "IDs_PAM", "Responsavel", "Fonte"]
    rq_cols = [col("ID_Req", 7, key="PK"), col("Ambito", 7), col("Tema", 22), col("Diploma", 34), col("Artigos", 30), col("Papel_Plasticom", 16), col("Obrigacao", 60),
               col("Aplicavel", 10, dv="Aplicavel"), col("Justificacao", 34, req=False), col("Evidencia", 26), col("Frequencia", 14), col("Estado", 13, dv="EstadoConf"),
               col("ID_Legal", 8, key="FK → tbl_legal", req=False), col("IDs_PAM", 16, key="FK → RG-SGA-06 tbl_pam", req=False), col("Responsavel", 20, dv="Funcao"), col("Fonte", 30)]
    rq_rows = []
    for r in REQ:
        x = dict(zip(rq_names, r))
        for k in ("Justificacao", "ID_Legal", "IDs_PAM"):
            x[k] = x[k] or None
        rq_rows.append(x)
    b.table("Requisitos_Legais", "tbl_requisitos_quimicos", rq_cols, rq_rows,
            "Matriz legal de produtos químicos — União Europeia e Portugal — com aplicabilidade, evidência, estado e ligação ao RG-SGA-04.",
            title="MATRIZ LEGAL — PRODUTOS QUÍMICOS (UE + PORTUGAL)",
            subtitle="Detalhe dos requisitos de químicos (REACH/CLP do utilizador, SST, Seveso) · SVHC em embalagens, PPWR e contacto alimentar → RG-SGA-20 · F-gás, granulado, SCIE, ADR, resíduos e COV → RG-SGA-04 · Ações no PAM",
            cf=[("Estado", {"Não conforme": "red", "Parcial": "orange", "Por avaliar": "yellow", "implementação": "yellow", "acompanhamento": "blue", "Conforme": "green", "Não aplicável": "gray"})],
            row_height=60, extra_rows=15, freeze_col=3)

    # ---------------------------------------------------------------- análise crítica
    b.table("Analise_Critica", "tbl_analise_critica",
            [col("ID_AC", 7, key="PK"), col("Fonte", 26), col("Constatacao", 50), col("Avaliacao", 50), col("Melhoria_Implementada", 50), col("Onde", 26)],
            [dict(zip(["ID_AC", "Fonte", "Constatacao", "Avaliacao", "Melhoria_Implementada", "Onde"], c)) for c in CRITICA],
            "Avaliação crítica das fontes consultadas (ficheiro de referência REACH 2024.xlsx, guias da internet, registos do SGA) e melhorias feitas neste registo.",
            title="ANÁLISE CRÍTICA DAS FONTES E MELHORIAS", subtitle="Referência: REGISTOS/REACH (REACH 2024.xlsx, GUIA REACH.pdf — ECHA 2015, Purple Book GHS rev. 10) + ECHA, EUR-Lex, DGAE, ACT, INRS",
            row_height=60)

    # ---------------------------------------------------------------- painel
    ws = b.sheet("Painel", "Indicadores de controlo de produtos químicos (calculados a partir das tabelas).", tab_color="1F4E5F")
    ws["A1"] = "PAINEL — GESTÃO DE PRODUTOS QUÍMICOS"
    ws["A1"].font = F_TITLE
    ws["A2"] = "Valores calculados em tempo real a partir das tabelas deste ficheiro · Data de referência: Listas!DataReferencia"
    ws["A2"].font = F_SUB
    kpis = [
        ("Produtos no inventário (ativos)", '=COUNTIFS(tbl_quimicos[ID_Quimico],"QUI-*",tbl_quimicos[Estado_Aprovacao],"<>Descontinuado")', None, "—", "Inventario"),
        ("Produtos classificados como perigosos", '=COUNTIF(tbl_quimicos[Perigoso],"Sim")', None, "—", "Inventario"),
        ("Produtos CMR cat. 1A/1B em uso", '=COUNTIF(tbl_quimicos[CMR],"Cat. 1A/1B")', 0, "≤", "Inventario"),
        ("Produtos com SVHC (declarada ou em componente)", '=SUMPRODUCT((tbl_quimicos[ID_Quimico]<>"")*((tbl_quimicos[SVHC_Declarado]="Sim")+(tbl_quimicos[SVHC_Componentes]="Sim")>0))', 0, "≤", "Inventario"),
        ("Produtos com SVHC/PFAS por confirmar", '=SUMPRODUCT((tbl_quimicos[ID_Quimico]<>"")*((tbl_quimicos[SVHC_Declarado]="Por confirmar")+(tbl_quimicos[PFAS]="Por confirmar")>0))', 0, "≤", "Inventario"),
        ("Sensibilizantes em uso", '=COUNTIF(tbl_quimicos[Sensibilizante],"Sim")', None, "—", "Inventario"),
        ("FDS em vigor conformes (OK)", '=IFERROR(COUNTIF(tbl_fds[Estado_FDS],"OK")/COUNTIF(tbl_fds[Em_Vigor],"Sim"),0)', 0.95, "≥", "FDS_Verificacao"),
        ("FDS a pedir ao fornecedor (correção ou confirmação)", '=COUNTIF(tbl_fds[Estado_FDS],"Pedir*")', 0, "≤", "FDS_Verificacao"),
        ("Cenários de exposição não conformes (não/parcialmente cobertos por implementar)", '=COUNTIFS(tbl_ce_reach[Estado],"<>Conforme",tbl_ce_reach[Estado],"<>Implementado",tbl_ce_reach[ID_CE],"CE-*")', 0, "≤", "Cenarios_Exposicao"),
        ("Lacunas de registo / importação", '=COUNTIF(tbl_registo_reach[Conclusao],"LACUNA*")', 0, "≤", "Registo_Importacao"),
        ("Declarações de fornecedores não atualizadas", '=COUNTIFS(tbl_declaracoes[Estado],"<>Atualizada",tbl_declaracoes[ID_Decl],"DEC-*")', 0, "≤", "Declaracoes_SVHC"),
        ("Tarefas com prioridade P1", '=COUNTIF(tbl_risco_quimico[Prioridade],"P1*")', 0, "≤", "Avaliacao_Risco"),
        ("Produtos perigosos sem avaliação de risco", '=COUNTIF(tbl_quimicos[Avaliacao_Risco],"Em falta")', 0, "≤", "Inventario"),
        ("Medições não conformes ou inconclusivas", '=COUNTIF(tbl_medicoes_vle[Conclusao],"Não conforme*")+COUNTIF(tbl_medicoes_vle[Conclusao],"Inconclusivo*")', 0, "≤", "Medicoes_VLE"),
        ("Locais de armazenagem não conformes", '=COUNTIF(tbl_armazenagem[Estado],"Incompat*")+COUNTIF(tbl_armazenagem[Estado],"Retenção*")+COUNTIF(tbl_armazenagem[Estado],"Sem ponto*")', 0, "≤", "Armazenagem"),
        ("Seveso — grupo físico", '=INDEX(tbl_seveso_resumo[Conclusao],2)', None, "texto", "Seveso"),
        ("Requisitos legais não conformes ou parciais", '=COUNTIF(tbl_requisitos_quimicos[Estado],"Não conforme")+COUNTIF(tbl_requisitos_quimicos[Estado],"Parcial")', 0, "≤", "Requisitos_Legais"),
        ("Emissões de COV estimadas (balanço do inventário, t/ano)", '=SUM(tbl_quimicos[COV_kg_ano])/1000', 5, "≤", "Inventario"),
    ]
    header_row(ws, 4, ["Indicador", "Valor", "Meta", "Sentido", "Estado", "Folha"], [62, 14, 10, 9, 14, 22])
    for i, (nm, f, meta, sent, sh) in enumerate(kpis):
        r = 5 + i
        vals = [nm, f, meta, sent, None, sh]
        for j, v in enumerate(vals):
            c = ws.cell(row=r, column=1 + j, value=v)
            c.font, c.border, c.alignment = F_BASE, BORDER, WRAP_TOP
        ws.cell(row=r, column=2).fill = FILL_CALC
        ws.cell(row=r, column=2).number_format = "0%" if "conformes (OK)" in nm else ("0.00" if "COV" in nm else "0")
        if "conformes (OK)" in nm:
            ws.cell(row=r, column=3).number_format = "0%"
        ws.cell(row=r, column=5).value = (f'=IF(D{r}="≤",IF(B{r}<=C{r},"OK","Atenção"),IF(D{r}="≥",IF(B{r}>=C{r},"OK","Atenção"),'
                                          f'IF(D{r}="texto",IF(ISNUMBER(SEARCH("Não abrangido",B{r})),"OK","Atenção"),"—")))')
        ws.cell(row=r, column=5).fill = FILL_CALC
    rng = f"E5:E{4 + len(kpis)}"
    for txt, colr in (("Atenção", "red"), ("OK", "green")):
        bg, fg = CF_COLORS[colr]
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("{txt}",E5))'], fill=PatternFill("solid", fgColor=bg), font=Font(name=FONT, color=fg, bold=True)))
    r = 7 + len(kpis)
    ws.cell(row=r, column=1, value="PROVA DE CONTROLO REACH — o que um inspetor (ASAE / IGAMAOT / ACT) pede e onde está").font = F_BOLD
    prova = [("Papel REACH da empresa e fornecedores extra-UE", "Papel_REACH; Registo_Importacao"), ("Lista de produtos químicos com quantidades e perigos", "Inventario"),
             ("FDS em português, atualizadas, acessíveis aos trabalhadores", "FDS_Verificacao"), ("Verificação dos cenários de exposição e medidas aplicadas", "Cenarios_Exposicao"),
             ("SVHC: declarações e comunicação a clientes (art. 33.º) / SCIP", "Declaracoes_SVHC; RG-SGA-20 tbl_familias_ppwr"), ("Restrições (anexo XVII) e autorização (anexo XIV)", "Requisitos_Legais; Componentes"),
             ("Avaliação de riscos químicos e medições (DL 24/2012; DL 301/2000)", "Avaliacao_Risco; Medicoes_VLE"), ("Formação (diisocianatos, CMR, derrames)", "RG-SGA-08 (FOR-01, FOR-03, FOR-13, FOR-14, FOR-15)"),
             ("Armazenagem, compatibilidades e Seveso", "Armazenagem; Matriz_Compatibilidade; Seveso"), ("Relatório de microplásticos (granulado) e outras obrigações periódicas", "RG-SGA-04 tbl_obrigacoes"),
             ("Ações e seguimento", "RG-SGA-06 (PAM-26-28 a PAM-26-35)")]
    for i, (a, bb) in enumerate(prova):
        ws.cell(row=r + 1 + i, column=1, value="• " + a).font = F_BASE
        ws.cell(row=r + 1 + i, column=2, value=bb).font = F_BASE
    ws.freeze_panes = "A5"

    # ordem das folhas: Painel logo a seguir ao LEIA-ME
    order = ["Painel", "Papel_REACH", "Inventario", "Componentes", "FDS_Verificacao", "Cenarios_Exposicao", "Registo_Importacao", "Declaracoes_SVHC",
             "Avaliacao_Risco", "Medicoes_VLE", "Metodologia", "Armazenagem", "Matriz_Compatibilidade", "Seveso", "Requisitos_Legais",
             "Analise_Critica", "Parametros", "Ref_Frases_H", "Ref_SVHC_Vigiadas"]
    b.wb._sheets = [b.wb[n] for n in order] + [s for s in b.wb.worksheets if s.title not in order]
    info = dict(b.sheets_info)
    b.sheets_info = [(n, info[n]) for n in order if n in info] + [(n, d) for n, d in b.sheets_info if n not in order]
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
