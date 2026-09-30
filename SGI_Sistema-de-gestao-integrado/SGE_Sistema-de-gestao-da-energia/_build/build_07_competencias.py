"""RG-SGE-07 — Competência, consciencialização, comunicação e sugestões de melhoria do SGE.
ISO 50001:2018 7.1, 7.2 a)–d), 7.3 a)–d), 7.4 a)–e) (+ processo de comentários e sugestões)."""
import numpy as np
from sgelib import *
from dimse import *

COMPETENCIAS = [
    # (ID, função, processo, USE, descrição do USE, educação, formação obrigatória (IDs), formação, experiência, soft skills, tema de consciencialização, consequência do desvio, avaliação da eficácia, n.º colaboradores)
    ("COMPE-01", GE, "UTL", "Todos", "Todos os USE e o SGE", "Licenciatura em engenharia (eletrotécnica/mecânica/energia)", "FOR-E-03; FOR-E-05; FOR-E-06",
     "ISO 50001/50006, M&V (IPMVP/ISO 50015), auditor interno", "3 anos em energia industrial", "Análise de dados; comunicação com a gestão", "Política, objetivos, IDE", "IDE mal definidos; melhoria não demonstrada", "Auditoria interna e revisão pela gestão", 1),
    ("COMPE-02", TUTL, "UTL", "USE-03; USE-04", "Ar comprimido e frio", "Curso profissional de eletromecânica (nível 4)", "FOR-E-02; FOR-E-07",
     "Ar comprimido (ISO 11011), fugas por ultrassom, setpoints do chiller", "2 anos em utilidades", "Rigor no registo", "Fugas e setpoints", "Fugas não reparadas; setpoint baixo", "Nível 3 (comportamento no posto): rondas conformes", 2),
    ("COMPE-03", F["FE-16"], "INJ", "USE-02", "Injeção", "12.º ano ou experiência comprovada em moldação", "FOR-E-01",
     "Standby, arranque eficiente, temperaturas por molde", "6 meses no posto", "Atenção ao detalhe", "Standby nas pausas", "Máquina aquecida em vazio (até 78% da potência)", "Nível 3: ronda de standby", 18),
    ("COMPE-04", F["FE-17"], "SOP", "USE-01", "Sopro", "12.º ano ou experiência comprovada", "FOR-E-01",
     "Standby, pressão de sopro mínima, fornos de pré-forma", "6 meses no posto", "Atenção ao detalhe", "Standby e ar de sopro", "Consumo de ar e de aquecimento desnecessário", "Nível 3: ronda de standby", 24),
    ("COMPE-05", CTURNO, "PCP", "USE-01; USE-02", "Sopro e injeção", "12.º ano + formação de chefia", "FOR-E-01",
     "Checklist de pausa; leitura do quadro de energia", "2 anos", "Liderança de equipa", "Metas de energia do turno", "Standby não aplicado no turno", "Checklist assinado (100%)", 6),
    ("COMPE-06", F["FE-20"], "MAN", "USE-01; USE-02; USE-03; USE-04", "Manutenção dos USE", "Curso profissional de eletromecânica", "FOR-E-02",
     "Manutenção hidráulica, fugas, isolamento de canhões, motores IE3/IE4", "1 ano", "Rigor", "Impacto da manutenção na energia", "Perdas por fugas e desgaste", "Nível 2: teste", 7),
    ("COMPE-07", CMP_, "CMP", "Todos", "Compras de equipamentos e energia", "Licenciatura em gestão/engenharia", "FOR-E-04",
     "Critérios energéticos, LCC (EN 17463), informação aos fornecedores (8.3)", "2 anos", "Negociação", "Desempenho energético nas compras", "Comprar equipamento ineficiente", "Auditoria às compras de 2026", 2),
    ("COMPE-08", AUD, "QUA", "—", "Auditoria ao SGE", "Licenciatura", "FOR-E-06", "ISO 19011, ISO 50001, ISO 50003 (competência em desempenho energético)", "2 auditorias acompanhadas", "Imparcialidade",
     "—", "Auditoria sem avaliar a melhoria do desempenho", "Avaliação do auditor (RG-SGE-12)", 3),
    ("COMPE-09", EPROC, "PCP", "USE-01; USE-02", "Engenharia de processo", "Licenciatura em engenharia", "FOR-E-03",
     "IDE por máquina, DOE com energia como resposta, projeto (8.2)", "2 anos", "Análise de dados", "Energia nos parâmetros de processo", "Parâmetros que desperdiçam energia", "Projetos com energia avaliada", 2),
]

FORMACOES = [
    ("FOR-E-01", "Boas práticas de energia no posto: standby, arranques, ar comprimido", 0.5, "Interna (Gestor de Energia)", "No posto", 24),
    ("FOR-E-02", "Ar comprimido: eficiência (ISO 11011), fugas por ultrassom, pressão", 4, "Externa (fornecedor de compressores)", "Presencial", 36),
    ("FOR-E-03", "ISO 50001 e ISO 50006 para a equipa de gestão de energia (IDE, LBE, normalização)", 16, "Externa (organismo de formação)", "Presencial", 24),
    ("FOR-E-04", "Compras com critérios energéticos e custo do ciclo de vida (EN 17463)", 4, "Interna", "Presencial", 36),
    ("FOR-E-05", "Medição e verificação de poupanças (IPMVP / ISO 50015)", 16, "Externa (EVO — CMVP)", "Online", 36),
    ("FOR-E-06", "Auditor interno do SGE (ISO 19011 + ISO 50001 + ISO 50003)", 24, "Externa (organismo de certificação)", "Presencial", 36),
    ("FOR-E-07", "Operação eficiente do chiller e da torre (setpoints, free-cooling)", 2, "Externa (fornecedor do chiller)", "No posto", 36),
]

SESSOES = [
    ("CONE-01", "2026-07-06", "Lançamento do SGE: política energética e objetivos", "a) b)", "Chefias e equipa de gestão de energia", 21, 22, "Lista de presenças; apresentação"),
    ("CONE-02", "2026-07-20", "Standby nas pausas e impacto das máquinas paradas (turno 1)", "b) c) d)", "Operadores de injeção e sopro — turno 1", 15, 16, "Lista de presenças"),
    ("CONE-03", "2026-07-21", "Standby nas pausas (turno 2)", "b) c) d)", "Operadores — turno 2", 14, 15, "Lista de presenças"),
    ("CONE-04", "2026-07-22", "Standby nas pausas (turno 3)", "b) c) d)", "Operadores — turno 3", 11, 14, "Lista de presenças; 3 ausentes em férias"),
    ("CONE-05", "2026-09-08", "Ar comprimido não é gratuito: fugas e usos indevidos (limpeza com ar)", "c) d)", "Todos os operadores e manutenção", 58, 68, "Lista de presenças; quiz"),
    ("CONE-06", "2026-09-22", "Resultados de energia e sugestões premiadas (reunião geral)", "a) b)", "Todos os trabalhadores", 131, 150, "Ata da reunião geral"),
    ("CONE-07", "2026-10-01", "Arranque do standby obrigatório (PA-E-03) e do checklist de pausa", "b) c) d)", "Chefes de turno e operadores (3 turnos)", 44, 46, "Lista de presenças; checklist"),
    ("CONE-08", "2026-12-18", "Resultados do 4.º trimestre: melhoria demonstrada após as ações", "a) b)", "Todos os trabalhadores (reunião de Natal)", 138, 152, "Ata; quadro de energia"),
]

COMUNICACAO = [
    ("COME-01", "Interna", "Política energética", "Política energética POL-SGE-01 e o seu significado", "Todos os trabalhadores", "Na receção e na revisão anual", "Afixação, intranet, reunião geral", "7.3 a); 5.2", GE),
    ("COME-02", "Interna", "Desempenho energético mensal", "IDE-01 (esperado vs real), CUSUM, SEC e desvios", "Gestão de topo e chefias", "Reunião mensal de desempenho (2.ª terça)", "Quadro Power BI", "Informar decisões (9.1)", GE),
    ("COME-03", "Interna", "Energia no turno", "Consumo do turno, standby e fugas assinaladas", "Operadores e chefes de turno", "Início de turno (SQDC)", "Quadro SQDC", "Consciencialização 7.3 c)", CTURNO),
    ("COME-04", "Interna", "Sugestões de melhoria", "Canal para comentários e sugestões sobre o SGE e o desempenho energético", "Qualquer pessoa que trabalhe para a Plasticom", "Contínuo", "Caixa de sugestões, app, e-mail energia@", "7.4 (processo obrigatório)", GE),
    ("COME-05", "Externa", "SGCIE", "Relatórios de execução e progresso (REP) do PREn", "DGEG / ADENE", "Bienal (próximo out/2026)", "Plataforma SGCIE", "Obrigação legal", GE),
    ("COME-06", "Externa", "Clientes", "Dados de energia e carbono por produto; política energética a pedido", "Clientes", "A pedido / anual", "Questionários, portal do cliente", "4.2 (requisitos de clientes)", F["FE-01"]),
    ("COME-07", "Externa", "Fornecedores", "O desempenho energético é critério de avaliação na aquisição (8.3)", "Fornecedores de equipamentos e serviços com impacto nos USE", "Em cada consulta", "Caderno de encargos", "8.3", CMP_),
    ("COME-08", "Externa", "Relato de sustentabilidade", "Consumo de energia, mix e intensidade (ESRS E1-5 / VSME B3)", "Clientes, bancos, público", "Anual", "Relatório de sustentabilidade (RG-SGA-19)", "Coerência com o SGE (7.4)", GSGA),
]

SUGESTOES = [
    ("SUGE-01", "2026-09-18", "Chefe de turno 3 (injeção)", "INJ", "Standby das máquinas na pausa de 80 min do turno 3 (KZ-01 do SGA)", "Aprovada", "OPE-03; PA-E-03", 0, 145),
    ("SUGE-02", "2026-08-20", "Técnico de manutenção", "UTL-AR", "Fechar os ramais de ar das áreas paradas ao fim de semana (KZ-04 do SGA)", "Aprovada", "OPE-04", 5, 29),
    ("SUGE-03", "2026-07-28", "Operador OP-SOP-002", "SOP", "Baixar a pressão de sopro de pré-forma nos frascos de 150 mL (há margem no teste de queda)", "Implementada", "CO-02 (ficha de parâmetros)", 12, 20),
    ("SUGE-04", "2026-08-04", "Operador OP-INJ-004", "INJ", "Desligar a extração e a iluminação da ilha IM-006 quando a máquina está parada por falta de molde", "Aprovada", "OPE-03", 3, 6),
    ("SUGE-05", "2026-08-11", "Técnico de Utilidades", "UTL-FRIO", "Limpar os permutadores da torre antes do verão (ΔT caiu 1,5 °C)", "Implementada", "RG-SGE-08 CO-15", 2, 15),
    ("SUGE-06", "2026-08-25", "Engenheiro de processo", "SOP", "Recuperar o ar de 40 bar do sopro para a rede de 7 bar nas ISBM hidráulicas", "Aprovada", "OPE-07 (em estudo)", 14, 98),
    ("SUGE-07", "2026-09-02", "Operador de armazém", "GER", "Sensores de presença na zona de expedição (luzes ligadas 24 h)", "Aprovada", "OPE-11", 9, 10),
    ("SUGE-08", "2026-09-09", "Operador OP-HF-001", "HFS", "Temporizador para desligar as placas aquecidas do hot foil 20 min antes do fim do turno de sexta", "Implementada", "CO-16", 8, 3),
    ("SUGE-09", "2026-09-15", "Chefe de turno 1", "UTL-AR", "Proibir a limpeza de roupa/bancadas com ar comprimido (usar aspirador)", "Implementada", "CONE-05", 1, 12),
    ("SUGE-10", "2026-09-24", "Planeador de produção", "Todos", "Agendar a moagem de scrap para as horas de vazio", "Implementada", "OE-04", 13, 0),
    ("SUGE-11", "2026-10-14", "Operador OP-INJ-002", "INJ", "Sinal luminoso na injetora quando está em standby há > 2 h (lembrete para desligar)", "Aprovada", "CO-05", 10, 8),
    ("SUGE-12", "2026-11-20", "Técnico de Utilidades", "UTL-FRIO", "Alarme no BI quando o setpoint do chiller for alterado (ANI-02)", "Implementada", "CO-13", 6, 5),
    ("SUGE-13", "2026-12-22", "Chefe de turno 2", "SOP", "Arranque escalonado das ISBM após a paragem de Natal para não exceder a potência", "Em análise", "RE-03", None, 0),
]


def build(out):
    b = Book("RG-SGE-07", "Competência, Consciencialização, Comunicação e Sugestões do SGE",
             activities="Determinar as competências das pessoas que afetam o desempenho energético e o SGE; formar e avaliar a eficácia; consciencializar; comunicar interna e externamente; "
                        "processo pelo qual qualquer pessoa pode fazer comentários ou sugestões de melhoria.",
             clauses="7.1 recursos; 7.2 a)–d) competência (reter evidência); 7.3 a)–d) consciencialização; 7.4 a)–e) comunicação (o quê, quando, com quem, como, quem comunica; informação "
                     "consistente e fiável) + processo de comentários e sugestões (considerar reter as sugestões).",
             purpose="Requisitos de competência por função ligados aos USE, catálogo de formação de energia, registo de formação com eficácia, sessões de consciencialização (7.3 a–d), "
                     "matriz de comunicação (7.4 a–e) e registo de sugestões com resposta e poupança estimada.",
             links=[("RG-SGE-04 tbl_use", "Pessoas que influenciam os USE (6.3 c 3) → competências aqui."), ("RG-SGA-08 / RG-SGQ-07", "Competências do SGA/SGQ (mesma estrutura)."),
                    ("RG-SGA-16", "Sugestões KZ-01 e KZ-04 (origem das SUGE-01/02).")],
             guidance=[("ISO 50004:2020 §7.2–7.4", "Exemplos de competências por função e de temas de consciencialização."),
                       ("ISO 10015 (gestão da competência) / modelo de Kirkpatrick", "Avaliação da eficácia da formação em 4 níveis (reação, aprendizagem, comportamento, resultados)."),
                       ("ISO 50003:2021 (anexo sobre competência)", "Competências de desempenho energético exigidas aos auditores (usado no COMPE-08)."),
                       ("Kent/BPF", "A formação dos operadores é das medidas mais rápidas e rentáveis.")],
             legal=[("Código do Trabalho, arts. 130.º–134.º (formação contínua)", "As horas de formação de energia contam para as 40 h anuais obrigatórias.")])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("EstadoSug", ["Recebida", "Em análise", "Aprovada", "Implementada", "Rejeitada"])
    b.add_list("Resultado", ["Aprovado", "Reprovado"])
    b.add_list("Nivel", ["N1 Reação", "N2 Aprendizagem", "N3 Comportamento", "N4 Resultados"])

    rng = np.random.default_rng(7202)
    # registo de formação (simulado): operadores do dataset e funções
    ops_inj = ["OP-INJ-001", "OP-INJ-002", "OP-INJ-003", "OP-INJ-004", "OP-INJ-005", "AUX-INJ-001"]
    ops_sop = ["OP-SOP-001", "OP-SOP-002", "OP-SOP-003", "OP-SOP-004", "OP-SOP-005", "OP-SOP-006"]
    regs = []
    k = 1
    for pid in ops_inj + ops_sop:
        nota = int(rng.integers(62, 98))
        regs.append(("REGE-%03d" % k, pid, "COMPE-03" if pid in ops_inj else "COMPE-04", "FOR-E-01", dt.date(2026, 7, 20) + dt.timedelta(days=int(rng.integers(0, 3))), 0.5,
                     "Aprovado" if nota >= 70 else "Reprovado", nota, "N3 Comportamento", 36))
        k += 1
    for pid, comp, form, d_, h in (("P-006", "COMPE-06", "FOR-E-02", "2026-08-12", 4), ("P-007", "COMPE-06", "FOR-E-02", "2026-08-12", 4), ("P-013", "COMPE-06", "FOR-E-02", "2026-08-12", 4),
                                   (TUTL, "COMPE-02", "FOR-E-02", "2026-08-12", 4), (TUTL, "COMPE-02", "FOR-E-07", "2026-08-26", 2), (GE, "COMPE-01", "FOR-E-03", "2026-07-14", 16),
                                   (GE, "COMPE-01", "FOR-E-05", "2026-09-10", 16), (GE, "COMPE-01", "FOR-E-06", "2026-06-03", 24), (EPROC, "COMPE-09", "FOR-E-03", "2026-07-14", 16),
                                   (CMP_, "COMPE-07", "FOR-E-04", "2026-09-16", 4), ("Auditor(a) Interno(a) do SGQ", "COMPE-08", "FOR-E-06", "2026-06-03", 24)):
        nota = int(rng.integers(72, 96))
        regs.append(("REGE-%03d" % k, pid, comp, form, dt.date.fromisoformat(d_), h, "Aprovado", nota, "N2 Aprendizagem", 36))
        k += 1
    # 4.º trimestre de 2026: chefes de turno no arranque do standby obrigatório (CONE-07) e reciclagem dos reprovados em FOR-E-01
    for t, d_ in (("turno 1", "2026-10-01"), ("turno 2", "2026-10-01"), ("turno 3", "2026-10-02")):
        regs.append(("REGE-%03d" % k, CTURNO, "COMPE-05", "FOR-E-01", dt.date.fromisoformat(d_), 0.5, "Aprovado", int(rng.integers(78, 96)), "N3 Comportamento", 36))
        k += 1
    for r_ in [x for x in regs if x[3] == "FOR-E-01" and x[6] == "Reprovado"]:
        regs.append(("REGE-%03d" % k, r_[1], r_[2], "FOR-E-01", dt.date(2026, 10, 15), 0.5, "Aprovado", int(rng.integers(74, 90)), "N3 Comportamento", 36))
        k += 1
    regs.append(("REGE-%03d" % k, TUTL, "COMPE-02", "FOR-E-02", dt.date(2026, 11, 25), 4, "Aprovado", int(rng.integers(80, 95)), "N3 Comportamento", 36))   # reciclagem após os VSD
    k += 1

    ccols = [col("ID_Competencia", 9, key="PK", desc="Requisito de competência."), col("Funcao", 26, dv="Funcao", desc="Função."), col("Processo", 7, desc="Processo."),
             col("ID_USE", 12, desc="USE que a função influencia (posição de ID_Aspeto_AAS no SGA).", key="FK → RG-SGE-04 tbl_use"),
             col("USE_Descricao", 22, desc="USE (posição de Aspeto_Significativo no SGA)."), col("Educacao_Habilitacoes", 28, desc="Educação (7.2 b)."),
             col("Formacao_Obrigatoria", 16, desc="Formações obrigatórias.", key="FK → tbl_formacoes"), col("Formacao_Descricao", 36, desc="Conteúdo."), col("Experiencia", 16, desc="Experiência."),
             col("Soft_Skills", 18, desc="Competências comportamentais."), col("Tema_Consciencializacao", 22, desc="Tema de consciencialização (7.3)."),
             col("Consequencia_Desvio", 30, desc="Implicação de não cumprir (7.3 d)."), col("Avaliacao_Eficacia", 26, desc="Como se avalia a eficácia (7.2 c)."),
             col("N_Colaboradores", 8, "int", desc="Pessoas na função."),
             col("Registos_Aprovados", 8, "int", f='=IF(@ID_Competencia@="","",COUNTIFS(tbl_registo_formacao[ID_Competencia],@ID_Competencia@,tbl_registo_formacao[Resultado],"Aprovado"))', desc="Formações aprovadas registadas."),
             col("Cobertura", 8, "pct", f='=IF(@ID_Competencia@="","",MIN(1,@Registos_Aprovados@/(@N_Colaboradores@*(LEN(@Formacao_Obrigatoria@)-LEN(SUBSTITUTE(@Formacao_Obrigatoria@,";",""))+1))))', desc="Aprovações ÷ (pessoas × formações obrigatórias)."),
             col("Estado", 10, f='=IF(@ID_Competencia@="","",IF(@Cobertura@>=0.9,"Coberto",IF(@Cobertura@>=0.3,"Parcial","Lacuna")))', desc="Coberto ≥ 90%.")]
    b.table("Competencias", "tbl_competencias", ccols, rows_from(input_names(ccols), COMPETENCIAS),
            "Requisitos de competência das funções que afetam o desempenho energético (7.2) — mesma estrutura do RG-SGA-08.", title="COMPETÊNCIAS DO SGE (7.2)",
            cf=[("Estado", {"Coberto": "green", "Parcial": "orange", "Lacuna": "red"})], row_height=45, freeze_col=2)
    fcols = [col("ID_Formacao", 9, key="PK", desc="Ação de formação."), col("Titulo", 60, desc="Título."), col("Duracao_h", 8, "num1", desc="Duração (h)."),
             col("Formador", 28, desc="Formador."), col("Modalidade", 12, desc="Modalidade."), col("Reciclagem_Meses", 9, "int", desc="Periodicidade de reciclagem.")]
    b.table("Formacoes", "tbl_formacoes", fcols, rows_from(input_names(fcols), FORMACOES), "Catálogo de formação de energia.", title="CATÁLOGO DE FORMAÇÃO DE ENERGIA", row_height=18)
    rcols = [col("ID_Registo", 9, key="PK", desc="Registo."), col("Colaborador", 24, desc="Pessoa (ID do dataset/RG-SGQ-07) ou função."),
             col("ID_Competencia", 9, desc="Competência.", key="FK → tbl_competencias"), col("ID_Formacao", 9, desc="Formação.", key="FK → tbl_formacoes"),
             col("Data_Realizacao", 11, "date", desc="Data."), col("Duracao_h", 7, "num1", desc="Horas."), col("Resultado", 10, dv="Resultado", desc="Aprovado / reprovado."),
             col("Nota_Teste", 7, "int", desc="Nota (0–100)."), col("Nivel_Avaliado", 14, dv="Nivel", desc="Nível de Kirkpatrick avaliado."),
             col("Reciclagem_Meses", 8, "int", desc="Reciclagem."), col("Validade", 11, "date", f='=IF(@ID_Registo@="","",EDATE(@Data_Realizacao@,@Reciclagem_Meses@))', desc="Válida até."),
             col("Valida", 7, f='=IF(@ID_Registo@="","",IF(AND(@Resultado@="Aprovado",@Validade@>=DataRef),"Sim","Não"))', desc="Válida à data de referência?")]
    b.table("Registo_Formacao", "tbl_registo_formacao", rcols, rows_from(input_names(rcols), regs),
            "Evidência de competência (7.2 d — reter).", title="REGISTO DE FORMAÇÃO DE ENERGIA (7.2 d)", subtitle="Registos simulados (operadores com IDs do dataset)",
            cf=[("Resultado", {"Reprovado": "red"}), ("Valida", {"Não": "red"})], row_height=16)
    scols = [col("ID_Sessao", 8, key="PK", desc="Sessão."), col("Data", 11, "date", desc="Data."), col("Tema", 50, desc="Tema."), col("Alineas_7_3", 8, desc="Alíneas 7.3 a–d."),
             col("Publico", 34, desc="Público."), col("Presentes", 8, "int", desc="Presentes."), col("Convocados", 8, "int", desc="Convocados."),
             col("Cobertura", 8, "pct", f='=IF(@ID_Sessao@="","",@Presentes@/@Convocados@)', desc="Presentes ÷ convocados."), col("Evidencia", 30, desc="Evidência.")]
    b.table("Consciencializacao", "tbl_consciencializacao", scols, rows_from(input_names(scols), SESSOES, dates=("Data",)),
            "Consciencialização (7.3 a–d) — mesma estrutura do RG-SGQ-07.", title="CONSCIENCIALIZAÇÃO (7.3)", row_height=20)
    mcols = [col("ID_Comunicacao", 9, key="PK", desc="Comunicação."), col("Tipo", 8, desc="Interna / externa."), col("Cenario", 22, desc="Assunto."),
             col("O_Que_Mensagem", 44, desc="Sobre o que comunicar (7.4 a)."), col("A_Quem_Publico", 30, desc="Com quem (7.4 c)."), col("Quando_Momento", 24, desc="Quando (7.4 b)."),
             col("Como_Canal", 26, desc="Como (7.4 d)."), col("Porque_Objetivo", 22, desc="Porquê."), col("Responsavel", 22, dv="Funcao", desc="Quem comunica (7.4 e).")]
    b.table("Comunicacao", "tbl_comunicacao", mcols, rows_from(input_names(mcols), COMUNICACAO),
            "Matriz de comunicação do SGE (7.4 a–e) — mesmas colunas do RG-SGA-09.", title="MATRIZ DE COMUNICAÇÃO DO SGE (7.4)",
            subtitle="Informação comunicada consistente com a gerada no SGE e fiável (7.4): os números saem dos registos RG-SGE-05/09/10", row_height=30, freeze_col=2)
    gcols = [col("ID_Sugestao", 8, key="PK", desc="Sugestão."), col("Data", 11, "date", desc="Data de receção."), col("Proponente", 26, desc="Quem sugeriu."), col("Processo", 8, desc="Uso / processo."),
             col("Sugestao", 56, desc="Comentário ou sugestão (7.4)."), col("Estado", 11, dv="EstadoSug", desc="Estado."), col("Ligacao", 18, desc="Oportunidade / plano / controlo."),
             col("Dias_Resposta", 8, "int", desc="Dias até à resposta ao proponente.", req=False), col("Poupanca_Estimada_MWh", 9, "num0", desc="[Só SGE] Poupança anual estimada (MWh)."),
             col("Resposta_no_Prazo", 9, f='=IF(@ID_Sugestao@="","",IF(@Dias_Resposta@="",IF(DataRef-@Data@>15,"Atrasada","Em prazo"),IF(@Dias_Resposta@<=15,"Sim","Não")))', desc="[Só SGE] Resposta em ≤ 15 dias?")]
    b.table("Sugestoes", "tbl_sugestoes", gcols, rows_from(["ID_Sugestao", "Data", "Proponente", "Processo", "Sugestao", "Estado", "Ligacao", "Dias_Resposta", "Poupanca_Estimada_MWh"], SUGESTOES, dates=("Data",)),
            "Processo de comentários e sugestões de melhoria do SGE e do desempenho energético (7.4) — mesma estrutura do RG-SGQ-19.", title="SUGESTÕES DE MELHORIA (7.4)",
            cf=[("Resposta_no_Prazo", {"Atrasada": "red", "Não": "orange", "Sim": "green"}), ("Estado", {"Implementada": "green", "Aprovada": "blue"})], row_height=30, freeze_col=2)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
