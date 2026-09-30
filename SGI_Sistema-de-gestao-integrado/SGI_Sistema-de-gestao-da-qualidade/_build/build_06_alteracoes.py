"""RG-SGQ-06 — Planeamento e controlo de alterações (gestão de mudanças, MOC).
ISO 9001:2026 6.3 a)–g) (f e g novos), 5.3 f), 8.1 (alterações planeadas e não previstas), 8.2.4, 8.3.6, 8.5.6.
Boas práticas: ISO 10007:2017 (gestão da configuração: identificação, controlo de alterações, registo do estado, auditoria da configuração)."""
from sgqlib import *
from dimsq import *

TIPOS = ["SGQ", "Processo", "Produto", "Equipamento", "Ferramenta / molde", "Fornecedor", "Requisito do cliente", "Organizacional", "Documentação"]
# (ID, data pedido, tipo, planeada?, descrição, a) propósito e consequências, b) integridade do SGQ, c) recursos e informação, d) responsabilidades,
#  e) comunicação, f) monitorização e eficácia, g) revisão dos resultados, cláusulas, requer cliente, data aprov. cliente, validação, riscos, documentos,
#  autorizado por, data autorização, data implementação, estado, data revisão eficácia, resultado, ligação SGA)
MOC = [
    ("MOC-Q-26-01", "2026-09-15", "SGQ", "Planeada", "Transição do SGQ da ISO 9001:2015 para a ISO 9001:2026",
     "Manter a certificação; incorporar cultura da qualidade, 6.1.2/6.1.3, 6.3 f–g e alterações climáticas. Consequência se falhar: perda do certificado após o fim da transição.",
     "Afeta todos os processos: registos RG-SGQ-01 a 19 reestruturados; política e objetivos revistos", "Norma adquirida; 120 h do Gerente da Qualidade; formação de auditores ISO 19011:2026",
     "Gerente da Qualidade (projeto); donos de processo (implementação)", "Reunião de direção 15/09; sessão a todos os turnos CON-26-03", "Índice de prontidão da matriz ISO 9001:2026 (RG-SGQ-00) ≥ 90%",
     "Revisão pela gestão de mar/2027 e auditoria de transição", "4 a 10", "Não", None, "Nenhuma", "R20", "Todos os PR-SGQ; POL-SGQ-01", DG, "2026-09-15", None, "Em implementação", "2027-03-31", "Por avaliar", "RG-SGA-18 ALT-SGA-01"),
    ("MOC-Q-26-02", "2026-01-12", "Equipamento", "Planeada", "Instalação das sopradoras ISBM-009 e ISBM-010 (linhas alimentar e farmacêutica)",
     "Capacidade para os SKU FA/FP; consequência: novo equipamento sem capacidade demonstrada pode gerar lotes NC", "Novos planos de controlo e instruções; máquinas no âmbito da metrologia e da manutenção",
     "Investimento € 1,9 M; técnico do fabricante 3 semanas", "Diretor Industrial; Engenheiro(a) de Processo (qualificação)", "Plano de arranque divulgado a produção, qualidade e manutenção",
     "OEE ≥ 70% e FPY ≥ 90% após 8 semanas", "Revisão aos 90 dias de produção", "7.1.3; 8.5.1 f); 8.5.6", "Sim", "2026-06-20", "IQ/OQ/PQ", "R12", "PC-SOP-01 rev. 04; IT-SOP-03", DIND, "2026-02-02", "2026-06-29", "Implementada", "2026-09-30", "Parcial", "RG-SGA-18"),
    ("MOC-Q-26-03", "2026-01-12", "Equipamento", "Planeada", "Instalação das injetoras IM-007 e IM-008 (potes PT e tampas TE/TP/TA)",
     "Capacidade para potes e tampas farma/alimentar; risco de defeitos no arranque", "Novos moldes M-INJ-010 a 014 na metrologia e manutenção", "Investimento € 1,1 M",
     "Diretor Industrial; Engenheiro(a) de Processo", "Plano de arranque", "FPY ≥ 90% após 8 semanas; anel de inviolabilidade ≤ 1 000 ppm", "Revisão aos 90 dias",
     "7.1.3; 8.5.1 f); 8.5.6", "Sim", "2026-06-20", "IQ/OQ/PQ", "R12", "PC-INJ-01 rev. 05; IT-INJ-04", DIND, "2026-02-02", "2026-06-29", "Implementada", "2026-09-30", "Não eficaz", ""),
    ("MOC-Q-26-04", "2026-03-02", "Produto", "Planeada", "Lançamento de 17 SKU (FA-030/031, FP-032/033, PT-010/011, TE-012, TP-013, TA-014)",
     "Entrada nos mercados alimentar e farmacêutico; consequência: requisitos legais novos (migração, inviolabilidade)", "Novos requisitos legais na matriz; planos de controlo com ensaio de migração e anel",
     "Projetos DD-26-01 a DD-26-06 (RG-SGQ-11)", "Responsável de R&D", "Kick-off com clientes CUST-015 a CUST-018", "FPY dos SKU novos ≥ 90% à 6.ª semana (safe launch)", "Revisão de fim de lançamento (set/2026)",
     "8.3; 8.5.6", "Sim", "2026-06-25", "Validação de design + safe launch", "R12; R33", "Especificações ESP-FA/FP/PT/TE/TP/TA", DG, "2026-03-16", "2026-07-06", "Implementada", "2026-09-25", "Parcial", "RG-SGA-20"),
    ("MOC-Q-26-05", "2025-12-10", "Processo", "Planeada", "Nova janela de parâmetros da IM-002 validada por DOE 2³ (temperatura do cilindro × velocidade de injeção)",
     "Reduzir short shot/peso (1,35% → 0,38%); consequência: janela nova pode afetar outras características", "PFMEA e plano de controlo da injeção revistos", "DOE de 27 corridas; MSA %GRR 3,5%",
     "Engenheiro(a) de Processo", "Formação dos operadores da IM-002 (FOR-Q-07)", "Taxa de defeito IM-002 ≤ 0,38% durante 3 meses", "Revisão mensal no DMAIC; fecho do projeto PRJ-Q-01",
     "8.5.6; 8.5.1", "Não", None, "Corrida de validação 3 lotes", "R4; O1", "IT-INJ-02 rev. 03; PC-INJ-01", DIND, "2026-01-08", "2026-01-15", "Fechada", "2026-05-15", "Eficaz", ""),
    ("MOC-Q-26-06", "2026-02-16", "Fornecedor", "Planeada", "Aprovação dos fornecedores SUP-009 (FarmaResin, PP-PG/PET-PG) e SUP-010 (NutriPolímeros, HDPE-FG/PP-FG)",
     "Resinas de grau farmacêutico e alimentar; consequência: fornecedores sem histórico", "Novos materiais no plano de controlo de receção", "Auditoria de qualificação; ensaios de 3 lotes",
     "Responsável de Compras; Gerente da Qualidade", "Informação aos fornecedores (8.4.3)", "Lotes aceites ≥ 95% nos primeiros 6 meses", "Reavaliação semestral (RG-SGQ-12)",
     "8.4", "Sim", "2026-04-10", "Qualificação de 3 lotes", "R13; R36", "PC-MP-01 rev. 06", CMP_, "2026-04-15", "2026-05-02", "Implementada", "2026-11-30", "Por avaliar", "RG-SGA-11"),
    ("MOC-Q-26-07", "2026-02-02", "Ferramenta / molde", "Planeada", "Reforma do molde M-SOP-007 (ISBM-001) — desgaste com flash e fuga",
     "Eliminar a fonte de flash/fuga (PFMEA RPN 280 → 120)", "Molde fora de serviço 10 dias; produção transferida para M-SOP-008", "Fornecedor de moldes externo (8.4)",
     "Gerente de Manutenção", "Aviso ao planeamento e aos clientes com encomendas", "Leakage M-SOP-007 < 300 ppm em 3 meses", "Revisão aos 90 dias", "8.5.6; 8.4", "Não", None, "FAI (primeira peça) + capacidade",
     "R2; O2", "Ficha do molde M-SOP-007", GMAN, "2026-02-05", "2026-03-02", "Fechada", "2026-06-05", "Eficaz", ""),
    ("MOC-Q-26-08", "2026-09-18", "Produto", "Não prevista", "TP-013 (tampa de pote de encaixe): característica 'binário' substituída por 'força de remoção'",
     "Erro de especificação herdado (tampa sem rosca com ensaio de binário); consequência: decisões de conformidade inválidas", "Plano de controlo, especificação e ensaio de laboratório alterados",
     "Torquímetro com adaptador de força; método de ensaio novo", "Responsável de R&D; Gerente da Qualidade", "Informação ao cliente dos potes (CUST-015)",
     "Zero decisões de lote com característica inaplicável", "Auditoria da configuração (ISO 10007) aos 17 SKU novos", "8.3.6; 8.2.4; 8.5.6", "Sim", "2026-09-22", "Reensaio de 5 lotes",
     "R12", "ESP-TP-013 rev. 01; PC-INJ-01 rev. 06", GQ, "2026-09-22", "2026-09-23", "Implementada", "2026-12-15", "Por avaliar", ""),
    ("MOC-Q-26-09", "2026-09-18", "Documentação", "Não prevista", "Especificação única por SKU nos 17 produtos novos (medições herdadas de lotes doadores com nominais diferentes)",
     "Um produto tem uma só ficha técnica; consequência: Cpk e decisões calculados contra nominais errados", "Dados de inspeção reexpressos contra a especificação correta (z-score preservado)",
     "Script de correção validado; comparação linha a linha dos dados antigos", "Gerente de Dados / TI; Gerente da Qualidade", "Nota interna à qualidade e à produção",
     "Zero SKU com mais de um nominal por característica", "Verificação na auditoria de dados", "7.5.3; 8.3.5; 8.5.2", "Não", None, "Verificação de dados", "R26", "ESP dos 17 SKU", GQ,
     "2026-09-23", "2026-09-23", "Fechada", "2026-09-28", "Eficaz", ""),
    ("MOC-Q-26-10", "2026-07-20", "Processo", "Planeada", "Leitura obrigatória de código de barras na carga (expedição) — poka-yoke contra produto trocado",
     "Eliminar reclamações de 'produto errado expedido' (29 no período)", "Instrução de expedição e ERP alterados", "Leitores (€ 6 000); integração ERP", "Responsável de Armazém e Logística",
     "Formação dos operadores de armazém", "Zero reclamações de produto trocado em 3 meses", "Revisão aos 90 dias", "8.5.1 g); 8.5.6", "Não", None, "Teste de 2 semanas",
     "R21", "IT-EXP-02 rev. 02", DIND, "2026-08-03", None, "Em implementação", "2026-12-31", "Por avaliar", ""),
    ("MOC-Q-26-11", "2026-02-09", "Equipamento", "Não prevista", "Substituição dos compressores de ar (feita sem pedido de alteração — regularização retroativa)",
     "Continuidade do ar comprimido; consequência não avaliada: ruído (SGA) e qualidade do ar de sopro (humidade/óleo)", "Falha do processo de mudanças detetada nas auditorias SGA e SGQ",
     "Análise do ar de sopro (classe ISO 8573-1)", "Gerente de Manutenção", "—", "Análise do ar de sopro conforme classe 1.4.1", "Revisão na auditoria de seguimento",
     "6.3; 8.1; 8.5.6", "Não", None, "Análise do ar comprimido", "R22; R39", "PR-SGQ-03 (novo campo: alterações de utilidades)", DIND, "2026-09-17", "2026-02-20", "Implementada", "2026-10-31", "Por avaliar", "RG-SGA-07 NC-SGA-26-06"),
    ("MOC-Q-26-12", "2026-09-01", "Equipamento", "Planeada", "Visão artificial na HF-001 (decoração) — inspeção a 100%",
     "Reduzir escapes de defeitos de decoração (O13)", "Novo critério de libertação na decoração", "€ 85 000 aprovados (RPG-2026-01 D05)", "Gerente de Dados / TI; Gerente da Qualidade",
     "Apresentação à equipa da decoração", "Reclamações de decoração −50%", "Revisão aos 6 meses", "8.5.1; 7.1.5", "Não", None, "Validação do sistema de visão (MSA por atributos)",
     "O13", "PC-DEC-01", DG, "2026-09-25", None, "Aprovada", "2027-06-30", "Por avaliar", ""),
    ("MOC-Q-26-13", "2026-08-24", "Fornecedor", "Planeada", "Qualificação de 2.º fornecedor de HDPE-PCR (redução da dependência do SUP-004)",
     "Reduzir a variação de qualidade do PCR (R14)", "Novo material no plano de receção", "Ensaios de 3 lotes; auditoria", "Responsável de Compras", "Informação ao fornecedor atual",
     "Lotes aceites ≥ 95%", "Reavaliação semestral", "8.4", "Sim", None, "Qualificação de 3 lotes", "R14", "PC-MP-01", None, None, None, "Em análise", None, "Por avaliar", "RG-SGA-11"),
    ("MOC-Q-26-14", "2026-06-22", "Organizacional", "Planeada", "Reforço de um inspetor no turno 2 em jul–nov (pico sazonal)",
     "Reduzir a fila de lotes e a pressão para libertar sem ensaio", "Nova escala de inspeção", "1 inspetor temporário qualificado", "Responsável de Recursos Humanos; Gerente da Qualidade",
     "Escala divulgada", "Tempo médio entre produção e decisão de lote ≤ 24 h", "Revisão em dez/2026", "7.1.2; 5.3", "Não", None, "Qualificação do inspetor (RG-SGQ-07)", "R9; R16",
     "Escala de inspeção", GQ, "2026-06-26", "2026-07-01", "Implementada", "2026-12-15", "Por avaliar", ""),
    ("MOC-Q-26-15", "2026-09-10", "Requisito do cliente", "Não prevista", "CUST-017 (farma) passa a exigir o resultado do ensaio do anel de inviolabilidade no certificado de cada lote",
     "Cumprir o acordo de qualidade farmacêutico", "Certificado de lote e ERP alterados", "Campo novo no certificado", "Gerente da Qualidade", "Confirmação ao cliente (8.2.4)",
     "100% dos certificados CUST-017 com o resultado", "Revisão trimestral com o cliente", "8.2.4; 8.6", "Sim", "2026-09-12", "Nenhuma", "R16", "Modelo de certificado CQ-02 rev. 03", GQ,
     "2026-09-12", "2026-09-14", "Implementada", "2026-12-14", "Por avaliar", ""),
    # 4.º trimestre de 2026
    ("MOC-Q-26-16", "2026-10-22", "Processo", "Não prevista", "Registo obrigatório no MES de todos os ajustes de parâmetros das ISBM-009/010 (GW-26-11, CON-Q-26-18)",
     "Estabilizar o peso (Cpk ≥ 1,33) e rastrear ajustes", "Campo novo no MES; ficha de parâmetros rev. 02", "Configuração do MES (TI)", "Engenheiro de Processo", "Formação FOR-Q-15",
     "Cpk do peso por turno ≥ 1,33", "Revisão mensal do SPC", "8.5.1; 8.5.6", "Não", None, "Nenhuma", "R3", "Ficha de parâmetros ISBM-009/010 rev. 02", GPROD,
     "2026-10-27", "2026-11-09", "Implementada", "2027-02-28", "Por avaliar", "RG-SGA-18 ALT-2026-10"),
    ("MOC-Q-26-17", "2026-11-26", "Documentação", "Planeada", "Transição do certificado para a ISO 9001:2026: revisão do manual e de 6 procedimentos",
     "Preparar a auditoria de transição (AUD-Q-27-01, mar/2027)", "Manual e PR-SGQ revistos", "8 h de formação (FOR-Q-16)", "Gerente da Qualidade", "Divulgação na intranet",
     "0 NC maiores na auditoria de transição", "Revisão pela gestão 2027", "4.4; 7.5", "Não", None, "Nenhuma", "R1", "MAN-SGQ-01; PR-SGQ-01..06", GQ,
     "2026-12-02", None, "Aprovada", "2027-03-31", "Por avaliar", ""),
]

CHECK = [
    ("a", "Propósito e consequências potenciais avaliados (6.3 a)"), ("b", "Impacto na integridade do SGQ avaliado (6.3 b; 5.3 f)"),
    ("c", "Recursos e informação disponíveis (6.3 c)"), ("d", "Responsabilidades e autoridades atribuídas (6.3 d)"), ("e", "Comunicação planeada (6.3 e)"),
    ("f", "Monitorização e avaliação da eficácia definidas (6.3 f — novo 2026)"), ("g", "Forma de rever os resultados definida (6.3 g — novo 2026)"),
    ("h", "PFMEA e plano de controlo revistos"), ("i", "Formação das pessoas afetadas"), ("j", "Validação / primeira peça / MSA quando aplicável"),
    ("k", "Stock e produto em curso com a configuração antiga tratados"), ("l", "Aspetos ambientais e requisitos legais avaliados pelo SGA (SGI)"),
    ("m", "Aprovação do cliente quando exigida (8.5.6 / acordo de qualidade)"),
]


def check_answers(m):
    st, tipo = m[21], m[2]
    done = st in ("Implementada", "Fechada")
    ans = {}
    for k, _ in CHECK:
        if k in "abcdefg":
            ans[k] = "Sim" if st != "Em análise" or k in "abc" else "Não"
        elif k == "h":
            ans[k] = "Sim" if tipo in ("Processo", "Produto", "Equipamento", "Ferramenta / molde") and (done or st == "Em implementação") else "N.A."
        elif k == "i":
            ans[k] = "Sim" if done or st == "Em implementação" else "Não"
        elif k == "j":
            ans[k] = "Sim" if m[15] != "Nenhuma" and done else ("N.A." if m[15] == "Nenhuma" else "Não")
        elif k == "k":
            ans[k] = "Sim" if tipo in ("Produto", "Processo", "Fornecedor") and done else "N.A."
        elif k == "l":
            ans[k] = "Sim" if m[24] else ("Não" if m[0] == "MOC-Q-26-11" else "N.A.")
        elif k == "m":
            ans[k] = ("Sim" if m[14] else "Não") if m[13] == "Sim" else "N.A."
    if m[0] == "MOC-Q-26-11":
        ans.update(a="Não", b="Não", e="Não")
    if m[0] == "MOC-Q-26-03":
        ans["j"] = "Sim"
    return ans


def build(out):
    b = Book("RG-SGQ-06", "Planeamento e Controlo de Alterações (Gestão de Mudanças)",
             activities="Planear, autorizar, implementar e rever as alterações ao SGQ, aos processos, produtos, equipamentos, fornecedores e requisitos do cliente.",
             clauses="6.3 a)–g) Planeamento de alterações (2026: f) monitorizar e avaliar a eficácia; g) rever os resultados); 5.3 f); 8.1 (alterações planeadas e não previstas); 8.2.4; 8.3.6; 8.5.6 (evidência: resultados da revisão, quem autorizou, ações)",
             purpose="Registo único dos pedidos de alteração (MOC) da Plasticom com a análise 6.3 a)–g), a autorização (8.5.6), a aprovação do cliente quando exigida, a validação e a revisão da eficácia; inclui a checklist de avaliação por alteração e o controlo de qualidade do registo.",
             links=[("RG-SGA-18 Planeamento de alterações (SGA)", "Ligacao_SGA: a mesma alteração é avaliada nos aspetos ambientais (SGI)."),
                    ("RG-SGA-02 / RG-SGQ-04", "Riscos afetados pela alteração."), ("RG-SGQ-11", "Alterações de design (8.3.6) dos projetos DD-26-nn.")],
             guidance=[("ISO 10007:2017 — Gestão da configuração", "Identificação da configuração (documentos afetados), controlo de alterações (pedido → avaliação → autorização → implementação → verificação), registo do estado e auditoria da configuração (MOC-Q-26-08/09)."),
                       ("ISO/TC 176 APG — Changes (planning of changes)", "O auditor procura alterações recentes (máquinas novas, produtos novos, fornecedores) e verifica se foram planeadas; o caso MOC-Q-26-11 mostra uma alteração não controlada."),
                       ("Nota sobre a ISO 10012", "A ISO 10012:2026 trata de sistemas de gestão da medição (aplicada no RG-SGQ-09), não de gestão de mudanças.")])
    b.add_list("TipoAlt", TIPOS)
    b.add_list("Natureza", ["Planeada", "Não prevista"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("SimNaoNA", ["Sim", "Não", "N.A."])
    b.add_list("EstadoAlt", ["Em análise", "Aprovada", "Em implementação", "Implementada", "Fechada", "Rejeitada"])
    b.add_list("Resultado", ["Eficaz", "Parcial", "Não eficaz", "Por avaliar"])
    b.add_list("Funcao", FUNC_NAMES)

    # mesmos nomes de coluna do RG-SGA-18 tbl_alteracoes (Origem, Tipo, Aprovador, Data_Aprovacao, Data_Verificacao, Verificacao_Pos_Implementacao,
    # Completude_Checklist, Alerta); as alíneas 6.3 a)–g) e os campos de cliente/validação são só do SGQ
    cols = [
        col("ID_Alteracao", 11, key="PK", desc="Pedido de alteração.", dom="MOC-Q-AA-nn"), col("Data_Pedido", 11, "date", desc="Data do pedido."),
        col("Origem", 9, f='=IF(@ID_Alteracao@="","",IF(OR(@Tipo@="Requisito do cliente",@Tipo@="Fornecedor"),"Externa","Interna"))',
            desc="Interna ou externa (calculada pelo tipo; mesmo domínio do RG-SGA-18)."),
        col("Tipo", 13, dv="TipoAlt", desc="Tipo de alteração."),
        col("Descricao", 42, desc="Descrição da alteração."),
        col("Natureza", 10, dv="Natureza", desc="[Só SGQ] Planeada ou não prevista (8.1: rever consequências das não previstas)."),
        col("a_Proposito_Consequencias", 40, desc="6.3 a)."), col("b_Integridade_SGQ", 32, desc="6.3 b)."),
        col("c_Recursos_Informacao", 26, desc="6.3 c)."), col("d_Responsabilidades", 24, desc="6.3 d)."), col("e_Comunicacao", 24, desc="6.3 e)."),
        col("f_Monitorizacao_Eficacia", 28, desc="6.3 f) — como se monitoriza e avalia a eficácia (novo 2026)."), col("g_Revisao_Resultados", 22, desc="6.3 g) — como se reveem os resultados (novo 2026)."),
        col("Completude_Checklist", 9, "pct", f='=IF(@ID_Alteracao@="","",IFERROR(COUNTIFS(tbl_checklist_alt[ID_Alteracao],@ID_Alteracao@,tbl_checklist_alt[Resposta],"Sim")/COUNTIFS(tbl_checklist_alt[ID_Alteracao],@ID_Alteracao@,tbl_checklist_alt[Resposta],"<>N.A."),""))',
            desc="% de itens aplicáveis da checklist respondidos 'Sim'."),
        col("Clausulas", 13, desc="Cláusulas ISO 9001:2026 envolvidas."), col("Requer_Aprovacao_Cliente", 10, dv="SimNao", desc="Acordo de qualidade exige aprovação prévia do cliente?"),
        col("Data_Aprovacao_Cliente", 11, "date", desc="Data da aprovação escrita do cliente.", req=False), col("Validacao_Requerida", 18, desc="IQ/OQ/PQ, primeira peça, MSA, safe launch..."),
        col("IDs_Risco_SGI", 10, desc="Riscos/oportunidades (RG-SGA-02 R-nn / O-nn).", key="FK → RG-SGA-02", req=False), col("Documentos_Afetados", 24, desc="Configuração afetada (ISO 10007)."),
        col("Aprovador", 22, dv="Funcao", desc="Quem autorizou (8.5.6).", req=False), col("Data_Aprovacao", 11, "date", desc="Data da autorização.", req=False),
        col("Data_Implementacao", 11, "date", desc="Data de implementação.", req=False),
        col("Verificacao_Pos_Implementacao", 12, dv="Resultado", desc="Resultado da revisão da eficácia (6.3 f–g)."),
        col("Data_Verificacao", 11, "date", desc="Quando se revê a eficácia.", req=False),
        col("Estado", 13, dv="EstadoAlt", desc="Estado."),
        col("Dias_Pedido_Aprovacao", 8, "int", f='=IF(OR(@Data_Aprovacao@="",@Data_Pedido@=""),"",@Data_Aprovacao@-@Data_Pedido@)', desc="Tempo de decisão (dias)."),
        col("Alerta", 24, f=('=IF(@ID_Alteracao@="","",IF(AND(OR(@Estado@="Implementada",@Estado@="Fechada"),@Aprovador@=""),"FALTA autorização (8.5.6)",'
                             'IF(AND(@Requer_Aprovacao_Cliente@="Sim",@Data_Aprovacao_Cliente@="",@Estado@<>"Em análise"),"FALTA aprovação do cliente",'
                             'IF(AND(@Data_Aprovacao@<>"",@Data_Implementacao@<>"",@Data_Implementacao@<@Data_Aprovacao@),"Implementada ANTES de autorizada",'
                             'IF(AND(@Data_Verificacao@<>"",@Data_Verificacao@<DataRef,@Verificacao_Pos_Implementacao@="Por avaliar"),"FALTA rever resultados (6.3 g)","OK")))))'),
            desc="Regras: autorização antes da implementação, aprovação do cliente e revisão dos resultados."),
        col("Ligacao_SGA", 18, desc="[Só SGQ] Registo equivalente no SGA (SGI).", req=False),
    ]
    MOC_N = ["ID_Alteracao", "Data_Pedido", "Tipo", "Natureza", "Descricao", "a_Proposito_Consequencias", "b_Integridade_SGQ", "c_Recursos_Informacao",
             "d_Responsabilidades", "e_Comunicacao", "f_Monitorizacao_Eficacia", "g_Revisao_Resultados", "Clausulas", "Requer_Aprovacao_Cliente",
             "Data_Aprovacao_Cliente", "Validacao_Requerida", "IDs_Risco_SGI", "Documentos_Afetados", "Aprovador", "Data_Aprovacao", "Data_Implementacao",
             "Estado", "Data_Verificacao", "Verificacao_Pos_Implementacao", "Ligacao_SGA"]
    rows = rows_from(MOC_N, MOC, dates=("Data_Pedido", "Data_Aprovacao_Cliente", "Data_Aprovacao", "Data_Implementacao", "Data_Verificacao"))
    # fecho do ano (31/12/2026): revisão dos resultados (6.3 g) e avanço das alterações do 4.º trimestre
    FECHO_MOC = {"MOC-Q-26-06": dict(Verificacao_Pos_Implementacao="Eficaz"), "MOC-Q-26-08": dict(Verificacao_Pos_Implementacao="Eficaz"),
                 "MOC-Q-26-10": dict(Estado="Implementada", Data_Implementacao=dt.date(2026, 12, 10)),
                 "MOC-Q-26-11": dict(Verificacao_Pos_Implementacao="Eficaz"),
                 "MOC-Q-26-13": dict(Estado="Em implementação", Data_Aprovacao_Cliente=dt.date(2026, 10, 9), Aprovador=CMP_, Data_Aprovacao=dt.date(2026, 10, 12), Data_Verificacao=dt.date(2027, 3, 31)),
                 "MOC-Q-26-14": dict(Verificacao_Pos_Implementacao="Eficaz"), "MOC-Q-26-15": dict(Verificacao_Pos_Implementacao="Eficaz")}
    for r_ in rows:
        r_.update(FECHO_MOC.get(r_["ID_Alteracao"], {}))
    for r in rows:
        r["Ligacao_SGA"] = r["Ligacao_SGA"] or None
    b.table("Registo_Alteracoes", "tbl_alteracoes", cols, rows, "Pedidos de alteração (MOC) com a análise 6.3 a)–g), autorização e revisão da eficácia.",
            title="REGISTO DE ALTERAÇÕES DO SGQ E DA OPERAÇÃO (6.3 · 8.5.6)",
            subtitle="Uma linha por pedido de alteração · Checklist e controlo calculados · ISO 10007: identificar → avaliar → autorizar → implementar → verificar a configuração",
            cf=[("Estado", {"Em análise": "gray", "Aprovada": "blue", "Em implementação": "yellow", "Implementada": "green", "Fechada": "green"}),
                ("Verificacao_Pos_Implementacao", {"Não eficaz": "red", "Parcial": "orange", "Eficaz": "green"}), ("Natureza", {"Não prevista": "orange"}),
                ("Alerta", {"FALTA": "red", "ANTES": "red", "OK": "green"}), ("Completude_Checklist", "AND(@<>\"\",@<1)", "yellow")],
            row_height=75, freeze_col=1, extra_rows=5)

    crow = []
    for m in MOC:
        ans = check_answers(m)
        for k, txt in CHECK:
            crow.append(dict(ID_Alteracao=m[0], Item=k, Pergunta=txt, Resposta=ans[k]))
    ccols = [col("ID_Alteracao", 11, desc="Pedido de alteração.", key="FK → tbl_alteracoes"), col("Item", 5, desc="Item da checklist."),
             col("Chave", 14, f='=@ID_Alteracao@&"|"&@Item@', desc="Chave técnica."), col("Pergunta", 60, desc="Pergunta da checklist."),
             col("Resposta", 8, dv="SimNaoNA", desc="Sim / Não / N.A."), col("Evidencia", 30, desc="Evidência (opcional).", req=False)]
    b.table("Checklist_Alteracoes", "tbl_checklist_alt", ccols, crow, "Checklist de avaliação de cada alteração (formato longo: uma linha por item).",
            cf=[("Resposta", {"Não": "red", "Sim": "green"})], row_height=16)

    ws = b.sheet("Resumo_Alteracoes", "Resumo calculado por tipo e estado; alterações não previstas e controlos em falta.")
    title(ws, "RESUMO DAS ALTERAÇÕES — calculado", "Entrada para a revisão pela gestão (9.3.3: necessidades de alteração do SGQ)")
    header_row(ws, 4, ["Tipo", "Total", "Não previstas", "Em curso", "Implementadas/fechadas", "Com falhas de controlo"], widths=[24, 8, 12, 10, 20, 20])
    T = lambda c_: f"tbl_alteracoes[{c_}]"
    for k, t in enumerate(TIPOS):
        r = 5 + k
        cell(ws, r, 1, t)
        cell(ws, r, 2, f'=COUNTIF({T("Tipo")},A{r})', fmt="0")
        cell(ws, r, 3, f'=COUNTIFS({T("Tipo")},A{r},{T("Natureza")},"Não prevista")', fmt="0")
        cell(ws, r, 4, f'=COUNTIFS({T("Tipo")},A{r},{T("Estado")},"Em implementação")+COUNTIFS({T("Tipo")},A{r},{T("Estado")},"Aprovada")+COUNTIFS({T("Tipo")},A{r},{T("Estado")},"Em análise")', fmt="0")
        cell(ws, r, 5, f'=COUNTIFS({T("Tipo")},A{r},{T("Estado")},"Implementada")+COUNTIFS({T("Tipo")},A{r},{T("Estado")},"Fechada")', fmt="0")
        cell(ws, r, 6, f'=COUNTIFS({T("Tipo")},A{r},{T("Alerta")},"<>OK",{T("ID_Alteracao")},"<>")', fmt="0")
    r = 5 + len(TIPOS)
    cell(ws, r, 1, "Total", bold=True)
    for c_ in range(2, 7):
        L = get_column_letter(c_)
        cell(ws, r, c_, f"=SUM({L}5:{L}{r - 1})", fmt="0", bold=True)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
