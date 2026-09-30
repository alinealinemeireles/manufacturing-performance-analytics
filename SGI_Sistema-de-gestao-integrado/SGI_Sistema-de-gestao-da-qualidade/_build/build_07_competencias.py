"""RG-SGQ-07 — Competências, formação, consciencialização e conhecimento organizacional.
ISO 9001:2026 7.1.2, 7.1.6, 7.2 a)–c) (evidência da competência), 7.3 a)–e) (2026: e) cultura da qualidade e comportamento ético).
Boas práticas: ISO 10015:2019 (gestão de competências: determinar necessidades → planear → implementar → avaliar resultados),
avaliação da eficácia em 4 níveis (reação, aprendizagem, comportamento, resultados)."""
import datetime as dt
import numpy as np
from sgqlib import *
from dimsq import *

COMP = [
    ("CQ-01", "Inspeção visual em cabine D65 (defeitos por atributos)", "LAB"), ("CQ-02", "Amostragem de aceitação ISO 2859-1:2026 e ISO 3951", "LAB"),
    ("CQ-03", "Medição dimensional e de peso (paquímetro, calibres, balança)", "LAB"), ("CQ-04", "SPC: cartas X̄-R e reação a pontos fora de controlo", "LAB"),
    ("CQ-05", "Ensaios de estanquidade e de anel de inviolabilidade", "LAB"), ("CQ-06", "Ensaio de migração (contacto alimentar) EN 1186", "LAB"),
    ("CQ-07", "Metrologia: verificação, calibração e MSA (Gage R&R)", "MET"), ("CQ-08", "Operação e autocontrolo de injeção (setup, arranque, parâmetros)", "INJ"),
    ("CQ-09", "Operação e autocontrolo de sopro ISBM (preformas, perfil de aquecimento)", "SOP"), ("CQ-10", "Serigrafia: registo, cor, cura e aderência", "SER"),
    ("CQ-11", "Hot foil: temperatura, pressão, transferência", "HFS"), ("CQ-12", "Afinação e manutenção de moldes", "MAN"),
    ("CQ-13", "Boas práticas de fabrico e higiene (alimentar / farmacêutico)", "EXP"), ("CQ-14", "Integridade de dados (ALCOA+) nos registos de qualidade", "QUA"),
    ("CQ-15", "Resolução de problemas: 5 Porquês, Ishikawa, 8D", "QUA"), ("CQ-16", "Auditoria interna ISO 19011:2026", "QUA"),
]
# requisitos por função: função → {competência: nível requerido 0–4}
REQ = {
    INSP: {"CQ-01": 3, "CQ-02": 3, "CQ-03": 3, "CQ-04": 2, "CQ-05": 2, "CQ-13": 2, "CQ-14": 3, "CQ-15": 2},
    "Técnico(a) de Laboratório": {"CQ-03": 3, "CQ-05": 3, "CQ-06": 3, "CQ-07": 3, "CQ-13": 2, "CQ-14": 3, "CQ-15": 2},
    "Técnico(a) de Manutenção": {"CQ-12": 3, "CQ-15": 2, "CQ-13": 1},
    "Operador(a) de Injeção": {"CQ-08": 3, "CQ-01": 2, "CQ-03": 2, "CQ-13": 2, "CQ-14": 2},
    "Operador(a) de Sopro (ISBM)": {"CQ-09": 3, "CQ-01": 2, "CQ-03": 2, "CQ-13": 2, "CQ-14": 2},
    "Operador(a) de Serigrafia": {"CQ-10": 3, "CQ-01": 2, "CQ-14": 2},
    "Operador(a) de Hot Foil": {"CQ-11": 3, "CQ-01": 2, "CQ-14": 2},
}
EXTRA_AUD = {"P-001": 3, "P-003": 3, "P-005": 2}   # auditores internos qualificados (CQ-16)

REQ_FUNCAO = [
    ("RF-01", GQ, "Licenciatura em engenharia ou ciências", "ISO 9001:2026; ISO 19011:2026 (auditor coordenador); estatística (CQE/Black Belt)", "5 anos em qualidade industrial", "Auditor coordenador qualificado"),
    ("RF-02", INSP, "12.º ano (técnico)", "CQ-01 a CQ-05; integridade de dados", "1 ano em inspeção (ou 6 meses com tutor)", "Validação no posto + teste de acuidade visual e de cor (Ishihara) anual"),
    ("RF-03", "Técnico(a) de Laboratório", "Licenciatura em química ou materiais", "Ensaios de migração, estanquidade, anel; metrologia", "2 anos em laboratório", "Participação em ensaio interlaboratorial"),
    ("RF-04", "Técnico(a) de Metrologia", "Curso técnico de metrologia", "ISO 10012:2026; MSA (AIAG); incerteza de medição", "2 anos", "—"),
    ("RF-05", "Operador(a) de Injeção", "9.º ano", "CQ-08; autocontrolo; BPF", "Validação no posto (40 h com tutor)", "Validação por chefe de turno + inspetor"),
    ("RF-06", "Operador(a) de Sopro (ISBM)", "9.º ano", "CQ-09; autocontrolo; BPF", "Validação no posto (40 h com tutor)", "Validação por chefe de turno + inspetor"),
    ("RF-07", "Operador(a) de Serigrafia", "9.º ano", "CQ-10; colorimetria básica", "Validação no posto (60 h com tutor)", "—"),
    ("RF-08", "Operador(a) de Hot Foil", "9.º ano", "CQ-11", "Validação no posto (30 h com tutor)", "—"),
    ("RF-09", "Técnico(a) de Manutenção", "Curso profissional de eletromecânica", "CQ-12; hidráulica; segurança de máquinas", "2 anos", "Habilitação elétrica quando aplicável"),
    ("RF-10", "Auditor(a) Interno(a) do SGQ", "12.º ano + formação ISO 9001", "ISO 19011:2026 (16 h); ISO 9001:2026 (16 h)", "2 auditorias como observador", "Independência da área auditada"),
    ("RF-11", "Engenheiro(a) de Processo", "Licenciatura em engenharia", "DOE, SPC, PFMEA, validação de processos", "3 anos", "—"),
    ("RF-12", CTURNO, "12.º ano", "Liderança de equipas; SPC básico; 8D", "3 anos na produção", "—"),
]

FORM = [
    ("FOR-Q-01", "ISO 9001:2026 — novidades e impacto nos processos", "Donos de processo e chefias", "CQ-15", "2026-10-06", 8, "Interna", "Realizada"),
    ("FOR-Q-02", "Auditor interno ISO 19011:2026 (atualização)", "Auditores internos", "CQ-16", "2026-09-22", 16, "Externa", "Realizada"),
    ("FOR-Q-03", "Amostragem ISO 2859-1:2026 — inspeção normal, reforçada e reduzida", "Inspetores", "CQ-02", "2026-03-10", 8, "Interna", "Realizada"),
    ("FOR-Q-04", "Ensaio do anel de inviolabilidade (TE-012) e de estanquidade", "Inspetores e laboratório", "CQ-05", "2026-06-24", 6, "Interna", "Realizada"),
    ("FOR-Q-05", "Boas práticas de fabrico e higiene — linhas alimentar e farmacêutica", "Operadores ISBM-009/010, IM-007/008, armazém", "CQ-13", "2026-06-25", 4, "Interna", "Realizada"),
    ("FOR-Q-06", "Integridade de dados ALCOA+ nos registos de qualidade", "Operadores e inspetores", "CQ-14", "2026-05-20", 2, "Interna", "Realizada"),
    ("FOR-Q-07", "Nova janela de parâmetros da IM-002 (DOE)", "Operadores de injeção", "CQ-08", "2026-01-14", 4, "Interna", "Realizada"),
    ("FOR-Q-08", "Retreino em autocontrolo de peso (injeção)", "OP-INJ-003", "CQ-08", "2026-02-18", 8, "Interna (tutor)", "Realizada"),
    ("FOR-Q-09", "Serigrafia: ensaio de aderência no arranque e cura UV", "Operadores de serigrafia", "CQ-10", "2026-08-05", 4, "Interna", "Realizada"),
    ("FOR-Q-10", "8D e 5 Porquês para donos de CAPA", "Donos de CAPA", "CQ-15", "2026-04-15", 8, "Interna", "Realizada"),
    ("FOR-Q-11", "Gage R&R por ANOVA e MSA por atributos (kappa)", "Laboratório e metrologia", "CQ-07", "2026-07-08", 8, "Externa", "Realizada"),
    ("FOR-Q-12", "Liderança de equipas e passagem de turno", "Chefes de turno", "CQ-15", "2026-10-13", 12, "Externa", "Realizada"),
    ("FOR-Q-13", "Acolhimento de temporários: qualidade, higiene e parar para corrigir", "Operadores temporários", "CQ-13", "2026-06-15", 4, "Interna", "Realizada"),
    ("FOR-Q-14", "Inspeção visual D65 e catálogo de defeitos", "Inspetores e operadores", "CQ-01", "2026-11-04", 3, "Interna", "Realizada"),
    ("FOR-Q-15", "Parâmetros e SPC do peso nas ISBM-009/010 (estabilização, CON-Q-26-18)", "Operadores de sopro", "CQ-08", "2026-12-02", 4, "Interna", "Realizada"),
    ("FOR-Q-16", "ISO 9001:2026 — preparação da auditoria de transição (mar/2027)", "Donos de processo", "CQ-15", "2027-01-20", 8, "Interna", "Planeada"),
]

CONSC = [
    ("CON-26-01", "2026-02-11", "Política da qualidade e objetivos 2026", "a) política; d) objetivos", "Todos os turnos", 142, 150, "Quiz de 5 perguntas (média 82%)"),
    ("CON-26-02", "2026-05-13", "O custo de uma reclamação: do defeito ao cliente (casos reais CC-20000, CC-20181)", "b) contribuição; c) implicações de não cumprir", "Produção e expedição", 118, 130, "Discussão por turno; registo de presenças"),
    ("CON-26-03", "2026-09-16", "Cultura da qualidade e comportamento ético: 'nunca libertar produto duvidoso'", "e) cultura da qualidade e ética (novo 2026)", "Todos os turnos", 131, 152, "Quiz (média 76%); canal de relatos divulgado"),
    ("CON-26-04", "2026-06-26", "Linhas alimentar e farmacêutica: porque a higiene e a rastreabilidade importam", "b) contribuição; c) implicações", "Novas linhas", 34, 36, "Perguntas no posto"),
    ("CON-26-06", "2026-11-18", "Resultados de 2026 e objetivos 2027: reclamações, CAPA e lições das linhas novas", "a) política; d) objetivos; b) benefícios da melhoria", "Todos os turnos", 139, 154, "Quiz (média 81%)"),
    ("CON-26-05", "2026-08-19", "Resultados do 1.º semestre e benefícios da melhoria (DMAIC IM-002)", "b) benefícios da melhoria do desempenho; d) objetivos", "Injeção", 22, 24, "Quadro de KPI da área"),
]

CONHEC = [
    ("KNW-01", "Janela de processo da IM-002 (DOE 2³: temperatura × velocidade)", "Métodos e processos", "IT-INJ-02 rev. 03; relatório DOE", "Engenheiro(a) de Processo; Rui Fonseca", 2, "Replicar às outras injetoras (O1)", "Lição: interação temperatura×velocidade explica o short shot"),
    ("KNW-02", "Afinação de moldes de sopro (perfil de aquecimento por cavidade)", "Experiência das pessoas", "Só na experiência dos técnicos", "Vitor Sousa; Rui Fonseca", 2, "Gravar vídeo-instruções e fichas de afinação por molde", "Risco de perda: 2 detentores com > 13 anos de casa"),
    ("KNW-03", "Estudo Gage R&R do peso das tampas (%GRR 3,5% da variação total)", "Informação documentada", "RG-SGQ-09 tbl_grr", "Ana Silva; Beatriz Costa; Carlos Mendes", 3, "Estender a espessura e binário", "O sistema de medição do peso é adequado"),
    ("KNW-04", "Reforma do molde M-SOP-007 (flash e fuga)", "Métodos e processos", "Relatório de reforma; PFMEA", "Sandra Reis", 1, "Registar na ficha do molde; manutenção por ciclos", "Desgaste acumulado previsível pelos ciclos"),
    ("KNW-05", "Especificação única por SKU (erro de clonagem de especificações)", "Sistemas digitais", "MOC-Q-26-09; script de correção", "Gerente de Dados / TI", 1, "Regra no ERP: um nominal por característica e SKU", "Validação de dados mestre antes de lançar produtos"),
    ("KNW-06", "Ensaio do anel de inviolabilidade (21 CFR 211.132)", "Formação e aprendizagem", "Método de ensaio LAB-M-12", "Elena Santos; Ana Silva", 2, "Formar os 4 inspetores", "Ferramenta TE-012 com pontes a rever"),
    ("KNW-07", "Tratamento de reclamações com 8D", "Informação documentada", "PR-SGQ-09; RG-SGQ-18 tbl_8d", "Gerente da Qualidade; donos de CAPA", 4, "Biblioteca de 8D fechados", "31% das CAPA não eficazes: causa raiz superficial"),
    ("KNW-08", "Requisitos de clientes farmacêuticos (acordos de qualidade)", "Informação documentada", "RG-SGQ-10 tbl_requisitos_cliente", "Gerente da Qualidade; Key Account", 2, "Resumo de requisitos por cliente no ERP", "Notificação prévia de alterações é obrigatória"),
    ("KNW-09", "Pipeline de dados da qualidade (bronze → silver → gold)", "Sistemas digitais", "Repositório do projeto; notebook", "Gerente de Dados / TI", 1, "Documentar e formar um 2.º responsável", "Pessoa única: risco R26"),
]


def matriz():
    rng = np.random.default_rng(10015)
    rows = []
    for pid, nome, func, proc, adm, vinc in PESSOAS:
        req = dict(REQ.get(func, {}))
        if pid in EXTRA_AUD:
            req["CQ-16"] = 2
        anos = (DATA_REF - dt.date.fromisoformat(adm)).days / 365
        for c, lvl in req.items():
            if vinc == "Temporário" and anos < 0.5:
                act = max(0, lvl - int(rng.integers(1, 3)))
            elif anos >= 5:
                act = min(4, lvl + int(rng.integers(0, 2)))
            else:
                act = max(0, lvl - (1 if rng.random() < 0.12 else 0))
            if pid == "OP-INJ-003" and c == "CQ-08":
                act = 2
            if pid == "OP-SOP-004" and c == "CQ-14":
                act = 1
            if pid in EXTRA_AUD and c == "CQ-16":
                act = EXTRA_AUD[pid]
            if c == "CQ-05" and pid in ("P-002", "P-004"):
                act = 1
            val = None if act < lvl else (DATA_REF - dt.timedelta(days=int(rng.integers(20, 400))))
            rows.append(dict(ID_Pessoa=pid, Nome=nome, Funcao=func, Processo=proc, ID_Competencia=c, Nivel_Requerido=lvl, Nivel_Atual=act,
                             Data_Validacao=val, Validado_Por=(CTURNO if proc in ("INJ", "SOP", "SER", "HFS") else GQ) if val else None))
    return rows


def registos_formacao():
    tgt = {"FOR-Q-03": ["P-001", "P-002", "P-003", "P-004"], "FOR-Q-04": ["P-001", "P-002", "P-003", "P-004", "P-005"],
           "FOR-Q-05": ["OP-SOP-005", "OP-SOP-006", "OP-INJ-005", "OP-INJ-001", "OP-SOP-001"], "FOR-Q-06": ["OP-SOP-001", "OP-SOP-002", "OP-SOP-003", "OP-SOP-004", "P-001", "P-004"],
           "FOR-Q-07": ["OP-INJ-001", "OP-INJ-002", "OP-INJ-003", "OP-INJ-004"], "FOR-Q-08": ["OP-INJ-003"], "FOR-Q-09": ["OP-SK-001", "OP-SK-002"],
           "FOR-Q-10": ["P-005", "P-003", "P-001", "P-006", "P-008", "P-010"], "FOR-Q-11": ["P-005", "P-001", "P-002"], "FOR-Q-13": ["OP-SOP-005", "OP-SOP-006", "OP-INJ-005"],
           "FOR-Q-02": ["P-001", "P-003", "P-005"],
           # 4.º trimestre de 2026
           "FOR-Q-01": ["P-001", "P-003", "P-005", "P-006", "P-008", "P-010"], "FOR-Q-12": ["P-006", "P-008", "P-010"],
           "FOR-Q-14": ["P-001", "P-002", "P-004", "OP-INJ-001", "OP-SOP-001"], "FOR-Q-15": ["OP-SOP-005", "OP-SOP-006", "OP-SOP-001", "OP-SOP-002"]}
    rng = np.random.default_rng(42)
    nomes = {p[0]: p[1] for p in PESSOAS}
    out, k = [], 0
    for f, pes in tgt.items():
        fd = [x for x in FORM if x[0] == f][0]
        for p in pes:
            k += 1
            teste = int(rng.integers(68, 100))
            comp = "Sim" if teste >= 70 else "Não"
            if p == "OP-INJ-003" and f == "FOR-Q-07":
                teste, comp = 62, "Não"
            if f == "FOR-Q-10" and p in ("P-006", "P-010"):
                comp = "Não"
            out.append(dict(ID_Registo=f"RF-{k:03d}", ID_Formacao=f, Colaborador=p, Nome=nomes[p], Data_Realizacao=dt.date.fromisoformat(fd[4]), Duracao_h=fd[5],
                            N1_Reacao=int(rng.integers(3, 6)), N2_Aprendizagem_Pct=teste / 100, N3_Comportamento_Posto=comp if dt.date.fromisoformat(fd[4]) < dt.date(2026, 12, 1) else None,
                            N4_Resultado=("KPI da área melhorou" if comp == "Sim" and f in ("FOR-Q-07", "FOR-Q-08") else None)))
    return out


def build(out):
    b = Book("RG-SGQ-07", "Competências, Formação, Consciencialização e Conhecimento Organizacional",
             activities="Determinar a competência necessária por função, avaliar cada pessoa, planear e registar a formação com avaliação da eficácia, evidenciar a consciencialização (7.3 a–e) e gerir o conhecimento crítico.",
             clauses="7.1.2 Pessoas; 7.1.6 Conhecimento organizacional; 7.2 a)–c) Competência (informação documentada como evidência); 7.3 a)–e) Consciencialização (2026: e) cultura da qualidade e comportamento ético)",
             purpose="Matriz de competências pessoa × competência (29 pessoas do dataset e da estrutura), com lacunas calculadas; plano e registos de formação com avaliação da eficácia em 4 níveis (ISO 10015); sessões de consciencialização com cobertura; registo do conhecimento organizacional crítico e risco de perda.",
             links=[("RG-SGQ-03", "Consciencialização sobre cultura e ética (7.3 e)."), ("RG-SGQ-16 tbl_auditores", "Competência dos auditores internos (CQ-16)."),
                    ("RG-SGA-08", "Formação ambiental (SGI) — mesma estrutura de registos."), ("RG-SGQ-04 R10, R23", "Riscos de competência.")],
             guidance=[("ISO 10015:2019 — Competence management and people development", "Ciclo: determinar necessidades (tbl_requisitos_funcao, matriz) → planear (tbl_formacoes) → implementar → avaliar os resultados (tbl_registo_formacao N1–N4)."),
                       ("ISO/TC 176 APG — Competence", "O auditor verifica a competência para o trabalho real (validação no posto), não só certificados de presença; a eficácia das ações tem de ser avaliada (7.2 c)."),
                       ("ISO/TC 176 APG — Organizational knowledge", "Conhecimento crítico identificado, retido e partilhado; risco de perda quando só uma ou duas pessoas o detêm."),
                       ("Academy — cap. 15 (Formação da qualidade)", "Avaliação de Kirkpatrick em 4 níveis.")])
    b.add_list("Funcao", FUNC_NAMES + ["Técnico(a) de Laboratório", "Técnico(a) de Manutenção"])
    b.add_list("Processo", PROC_CODES)
    b.add_list("EstadoForm", ["Planeada", "Realizada", "Adiada", "Cancelada"])
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("TipoConhec", ["Experiência das pessoas", "Formação e aprendizagem", "Métodos e processos", "Informação documentada", "Sistemas digitais"])
    b.add_list("Vinculo", ["Efetivo", "Temporário"])

    rcols = [col("ID_Req", 7, key="PK", desc="Requisito de função."), col("Funcao", 28, dv="Funcao", desc="Função."), col("Educacao", 26, desc="Educação."),
             col("Formacao", 40, desc="Formação requerida."), col("Experiencia", 24, desc="Experiência."), col("Qualificacao_Especifica", 34, desc="Qualificação/validação específica.")]
    b.table("Requisitos_Funcao", "tbl_requisitos_funcao", rcols, rows_from(input_names(rcols), REQ_FUNCAO),
            "Competência necessária por função (7.2 a): educação, formação e experiência.", title="COMPETÊNCIA NECESSÁRIA POR FUNÇÃO (7.2 a)", row_height=32)
    ccols = [col("ID_Competencia", 9, key="PK", desc="Competência técnica."), col("Competencia", 54, desc="Descrição."), col("Processo", 7, dv="Processo", desc="Processo principal.")]
    b.table("Competencias", "tbl_competencias", ccols, [dict(zip(input_names(ccols), c)) for c in COMP], "Catálogo de competências técnicas do SGQ.", row_height=16)
    pcols = [col("ID_Pessoa", 11, key="PK", desc="ID da pessoa (IDs de operador do dataset)."), col("Nome", 16, desc="Nome (operadores identificados pelo ID)."),
             col("Funcao", 26, dv="Funcao", desc="Função."), col("Processo", 7, dv="Processo", desc="Processo."), col("Data_Admissao", 11, "date", desc="Admissão."),
             col("Vinculo", 10, dv="Vinculo", desc="Efetivo / temporário."), col("Anos_Casa", 7, "num1", f='=(DataRef-@Data_Admissao@)/365', desc="Anos na empresa."),
             col("N_Lacunas", 8, "int", f='=COUNTIFS(tbl_matriz[ID_Pessoa],@ID_Pessoa@,tbl_matriz[Lacuna],">0")', desc="Competências abaixo do requerido."),
             col("Pode_Trabalhar_Sozinho", 12, f='=IF(@N_Lacunas@=0,"Sim","Com tutor")', desc="Sem lacunas = autónomo; com lacunas = tutor obrigatório (AMB-08).")]
    b.table("Pessoas", "tbl_pessoas", pcols, rows_from(input_names(pcols), PESSOAS, dates=("Data_Admissao",)), "Pessoas que fazem trabalho que afeta o desempenho do SGQ (7.2 a).",
            cf=[("Pode_Trabalhar_Sozinho", {"tutor": "orange", "Sim": "green"}), ("Vinculo", {"Temporário": "yellow"})], row_height=16)
    mcols = [col("ID_Pessoa", 11, desc="Pessoa.", key="FK → tbl_pessoas"), col("Nome", 16, desc="Nome."), col("Funcao", 24, desc="Função."), col("Processo", 7, desc="Processo."),
             col("ID_Competencia", 9, desc="Competência.", key="FK → tbl_competencias"),
             col("Competencia", 34, f='=IFERROR(INDEX(tbl_competencias[Competencia],MATCH(@ID_Competencia@,tbl_competencias[ID_Competencia],0)),"")', desc="Descrição (calculada)."),
             col("Nivel_Requerido", 8, "int", desc="0 sem conhecimento · 1 em formação · 2 executa com supervisão · 3 autónomo · 4 forma outros."),
             col("Nivel_Atual", 8, "int", desc="Nível avaliado."), col("Lacuna", 7, "int", f='=MAX(0,@Nivel_Requerido@-@Nivel_Atual@)', desc="Requerido − atual."),
             col("Estado", 12, f='=IF(@Lacuna@=0,IF(@Nivel_Atual@>=4,"Formador","Qualificado"),IF(@Nivel_Atual@>=@Nivel_Requerido@-1,"Em formação","Lacuna"))', desc="Estado."),
             col("Data_Validacao", 11, "date", desc="Data da validação no posto / avaliação.", req=False), col("Validado_Por", 22, desc="Quem validou.", req=False),
             col("Revalidar_Ate", 11, "date", f='=IF(@Data_Validacao@="","",EDATE(@Data_Validacao@,24))', desc="Revalidação a cada 24 meses.")]
    b.table("Matriz_Competencias", "tbl_matriz", mcols, matriz(), "Matriz de competências pessoa × competência (formato longo), evidência de 7.2 b).",
            title="MATRIZ DE COMPETÊNCIAS — PESSOA × COMPETÊNCIA (7.2)", subtitle="Escala 0–4 · Lacuna, estado e revalidação calculados · Níveis avaliados pelo chefe de turno / Gerente da Qualidade",
            cf=[("Estado", {"Lacuna": "red", "Em formação": "orange", "Qualificado": "green", "Formador": "blue"})], row_height=16, freeze_col=2)

    # mesmos nomes de coluna do RG-SGA-08 tbl_formacoes (Formacao, Duracao_h, N_Registos)
    fcols = [col("ID_Formacao", 10, key="PK", desc="Ação de formação."), col("Formacao", 50, desc="Designação / tema."),
             col("Duracao_h", 8, "int", desc="Duração (horas)."), col("Publico", 32, desc="[Só SGQ] Destinatários."),
             col("ID_Competencia", 9, desc="Competência desenvolvida.", key="FK → tbl_competencias"), col("Data", 11, "date", desc="Data (planeada ou realizada)."),
             col("Tipo", 14, desc="Interna / externa."), col("Estado", 10, dv="EstadoForm", desc="Estado."),
             col("N_Registos", 9, "int", f='=COUNTIF(tbl_registo_formacao[ID_Formacao],@ID_Formacao@)', desc="N.º de registos individuais (participantes)."),
             col("Eficacia_Pct", 9, "pct", f='=IFERROR(COUNTIFS(tbl_registo_formacao[ID_Formacao],@ID_Formacao@,tbl_registo_formacao[Eficaz],"Sim")/COUNTIFS(tbl_registo_formacao[ID_Formacao],@ID_Formacao@,tbl_registo_formacao[Eficaz],"<>Por avaliar"),"")',
                 desc="% de participantes com formação eficaz.")]
    FORM_N = ["ID_Formacao", "Formacao", "Publico", "ID_Competencia", "Data", "Duracao_h", "Tipo", "Estado"]
    b.table("Plano_Formacao", "tbl_formacoes", fcols, rows_from(FORM_N, FORM, dates=("Data",)), "Plano de formação 2026 (7.2 c).",
            title="PLANO DE FORMAÇÃO DA QUALIDADE 2026", cf=[("Estado", {"Realizada": "green", "Planeada": "blue", "Adiada": "orange"}), ("Eficacia_Pct", "AND(@<>\"\",@<0.8)", "red")], row_height=30)
    # mesmos nomes de coluna do RG-SGA-08 tbl_registo_formacao (Colaborador, Data_Realizacao, Duracao_h)
    gcols = [col("ID_Registo", 8, key="PK", desc="Registo de presença."), col("Colaborador", 11, desc="ID da pessoa (IDs de operador do dataset).", key="FK → tbl_pessoas"),
             col("Nome", 14, desc="[Só SGQ] Nome."), col("ID_Formacao", 10, desc="Formação.", key="FK → tbl_formacoes"),
             col("Data_Realizacao", 11, "date", desc="Data em que concluiu."), col("Duracao_h", 6, "int", desc="Horas."), col("N1_Reacao", 8, "int", desc="Nível 1 — satisfação (1–5)."),
             col("N2_Aprendizagem_Pct", 10, "pct", desc="Nível 2 — resultado do teste."), col("N3_Comportamento_Posto", 11, dv="SimNao", desc="Nível 3 — aplica no posto (observação 30 dias depois).", req=False),
             col("N4_Resultado", 22, desc="Nível 4 — efeito no KPI (quando mensurável).", req=False),
             col("Eficaz", 10, f='=IF(@N3_Comportamento_Posto@="","Por avaliar",IF(AND(@N2_Aprendizagem_Pct@>=0.7,@N3_Comportamento_Posto@="Sim"),"Sim","Não"))', desc="Eficácia: teste ≥ 70% e aplicação no posto."),
             col("Acao_Se_Nao_Eficaz", 16, f='=IF(@Eficaz@="Não","Retreino + tutor","")', desc="Ação quando não eficaz.")]
    b.table("Registo_Formacao", "tbl_registo_formacao", gcols, registos_formacao(), "Registos de formação com avaliação da eficácia em 4 níveis (evidência de 7.2 c).",
            cf=[("Eficaz", {"Não": "red", "Sim": "green", "Por avaliar": "gray"})], row_height=16)

    kcols = [col("ID_Sessao", 10, key="PK", desc="Sessão de consciencialização."), col("Data", 11, "date", desc="Data."), col("Tema", 48, desc="Tema."),
             col("Alineas_7_3", 28, desc="Alíneas de 7.3 cobertas."), col("Publico", 18, desc="Público."), col("Presentes", 8, "int", desc="Presentes."), col("Convocados", 9, "int", desc="Convocados."),
             col("Cobertura", 9, "pct", f='=IFERROR(@Presentes@/@Convocados@,"")', desc="Presentes ÷ convocados."), col("Evidencia", 32, desc="Evidência da compreensão.")]
    b.table("Consciencializacao", "tbl_consciencializacao", kcols, rows_from(input_names(kcols), CONSC, dates=("Data",)),
            "Consciencialização das pessoas (7.3 a–e), incluindo cultura da qualidade e comportamento ético (novo 2026).",
            title="CONSCIENCIALIZAÇÃO (7.3 a–e)", cf=[("Cobertura", "AND(@<>\"\",@<0.9)", "orange")], row_height=30)

    ncols = [col("ID_Conhecimento", 9, key="PK", desc="Conhecimento crítico."), col("Conhecimento", 44, desc="Conhecimento necessário à operação (7.1.6)."),
             col("Forma", 18, dv="TipoConhec", desc="Forma do conhecimento (7.1.6 Nota)."), col("Onde_Esta_Retido", 28, desc="Onde está conservado."),
             col("Detentores", 30, desc="Quem o detém."), col("N_Detentores", 8, "int", desc="N.º de pessoas que o dominam."),
             col("Risco_Perda", 9, f='=IF(@N_Detentores@<=1,"Alto",IF(@N_Detentores@=2,"Médio","Baixo"))', desc="Risco de perda do conhecimento."),
             col("Acao_Partilha", 36, desc="Como se partilha / adquire (7.1.6)."), col("Licao_Aprendida", 40, desc="Lição aprendida associada.")]
    b.table("Conhecimento_Organizacional", "tbl_conhecimento", ncols, rows_from(input_names(ncols), CONHEC),
            "Conhecimento organizacional crítico, retenção, partilha e lições aprendidas (7.1.6).", title="CONHECIMENTO ORGANIZACIONAL (7.1.6)",
            cf=[("Risco_Perda", {"Alto": "red", "Médio": "orange", "Baixo": "green"})], row_height=40)

    ws = b.sheet("Resumo_Competencias", "Indicadores calculados: cumprimento do plano (KPI-Q-18), eficácia, lacunas por processo.")
    title(ws, "RESUMO DE COMPETÊNCIAS E FORMAÇÃO — calculado")
    header_row(ws, 3, ["Indicador", "Valor"], widths=[56, 12])
    ind = [("Cumprimento do plano de formação até à data (KPI-Q-18)", '=IFERROR(COUNTIFS(tbl_formacoes[Estado],"Realizada")/COUNTIFS(tbl_formacoes[Data],"<="&DataRef),"")', "0%"),
           ("Formações com eficácia avaliada ≥ 80%", '=COUNTIF(tbl_formacoes[Eficacia_Pct],">="&0.8)', "0"),
           ("Participações não eficazes (retreino)", '=COUNTIF(tbl_registo_formacao[Eficaz],"Não")', "0"),
           ("Pares pessoa × competência avaliados", "=COUNTA(tbl_matriz[ID_Pessoa])", "0"),
           ("  qualificados ou formadores", '=COUNTIF(tbl_matriz[Estado],"Qualificado")+COUNTIF(tbl_matriz[Estado],"Formador")', "0"),
           ("  com lacuna", '=COUNTIF(tbl_matriz[Estado],"Lacuna")', "0"),
           ("% de cobertura de competências", '=IFERROR((B8)/B7,"")', "0%"),
           ("Pessoas que só podem trabalhar com tutor", '=COUNTIF(tbl_pessoas[Pode_Trabalhar_Sozinho],"Com tutor")', "0"),
           ("Conhecimentos críticos com risco de perda alto", '=COUNTIF(tbl_conhecimento[Risco_Perda],"Alto")', "0"),
           ("Cobertura média da consciencialização", "=AVERAGE(tbl_consciencializacao[Cobertura])", "0%")]
    for k, (a, f, fmt) in enumerate(ind):
        cell(ws, 4 + k, 1, a, bold=not a.startswith("  "))
        cell(ws, 4 + k, 2, f, fmt=fmt)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
