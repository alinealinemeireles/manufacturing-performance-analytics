import datetime as dt
import numpy as np
from sgalib import *
import sga_extra as X
from dims import *

d = lambda s: dt.date.fromisoformat(s) if s else None

FORMACOES = [
    ("FOR-01", "Manuseamento seguro de produtos químicos (REACH/CLP, leitura de FDS e rótulos)", 4, "Interna (Gestor SGA)", "Não", 24),
    ("FOR-02", "Limpeza de ecrãs com solvente: método, dispensador de segurança e controlo de COV", 2, "Interna (chefe de serigrafia)", "Não", 12),
    ("FOR-03", "Resposta a derrames e uso do kit antipoluição (incl. pós-uso: registar, repor, selar)", 2, "Interna (Gestor SGA)", "Não", 12),
    ("FOR-04", "Segregação de resíduos e códigos LER; preenchimento de e-GAR", 3, "Interna (Gestor SGA)", "Não", 24),
    ("FOR-05", "Segregação de scrap por polímero/cor e reintegração (regrind)", 1, "Interna (Eng. de Processo)", "Não", 24),
    ("FOR-06", "Operation Clean Sweep: prevenção de perdas de granulado", 1, "Interna (Gestor SGA)", "Não", 24),
    ("FOR-07", "Certificação de técnico de gases fluorados (categoria I)", 35, "Entidade certificadora externa", "Sim", 0),
    ("FOR-08", "Deteção de fugas de ar comprimido por ultrassom", 4, "Fornecedor do equipamento", "Não", 36),
    ("FOR-09", "Condução de empilhadores e movimentação de químicos", 16, "Entidade formadora certificada", "Sim", 60),
    ("FOR-10", "Auditor interno ISO 14001:2026 (inclui ISO 19011)", 21, "Entidade formadora certificada", "Não", 36),
    ("FOR-11", "Sensibilização ambiental de acolhimento (política, aspetos significativos, emergência)", 1, "Interna (RH + SGA)", "Não", 12),
    ("FOR-12", "Operação da torre de arrefecimento e tratamento de água (biocidas)", 4, "Fornecedor do tratamento de água", "Não", 24),
    ("FOR-13", "Uso seguro de diisocianatos — nível intermédio (REACH anexo XVII, entrada 74)", 8, "Formação ISOPA/ALIPA (e-learning)", "Sim", 60),
    ("FOR-14", "Trabalho com agentes cancerígenos, mutagénicos e reprotóxicos (DL 301/2000)", 2, "Interna (EHS + medicina do trabalho)", "Sim", 12),
    ("FOR-15", "ADR 1.3 — preparação de expedições de resíduos perigosos", 8, "Entidade formadora externa", "Sim", 60),
]
# formações acrescentadas em 09/2026 (gestão de químicos, PR-SGA-16): registos gerados à parte para não alterar a série aleatória dos restantes
NOVAS = {"FOR-13", "FOR-14", "FOR-15"}
OVERRIDE = {("OP-SK-001", "FOR-13"): "2023-08-10", ("OP-SK-002", "FOR-13"): "2023-08-10", ("OP-SK-003", "FOR-13"): "2023-08-10", ("OP-SK-004", "FOR-13"): "2023-08-10",
            ("OP-SK-005", "FOR-13"): None, ("OP-SK-T01", "FOR-13"): None,
            ("ARM-001", "FOR-15"): "2022-05-10", ("ARM-002", "FOR-15"): "2022-05-10",
            ("UTL-001", "FOR-12"): "2024-06-05", ("UTL-002", "FOR-12"): "2024-06-05"}

# (ID, Funcao, Proc, AAS, Aspeto, Educacao, Formacoes, Experiencia, SoftSkills, Tema consc., Consequencia, Metodo_Eficacia, N_colab)
MATRIZ = [
    ("COMP-01", "Operador de Serigrafia", "SER", "AA-014", "Emissão de COV na limpeza de ecrãs com solvente (AAS, IRA 40)",
     "9.º ano de escolaridade", "FOR-01; FOR-02; FOR-03; FOR-11; FOR-13; FOR-14", "6 meses em decoração industrial com acompanhamento",
     "Rigor na dosagem; comunicação de desvios ao chefe de turno",
     "Deixar latas ou panos de solvente abertos aumenta as emissões de COV (poluição do ar), o consumo de solvente e o risco de incêndio e intoxicação; cada limpeza desnecessária gasta solvente e gera resíduo perigoso.",
     "Mais COV, mais resíduos 15 02 02* e 08 03 12*, desvio do objetivo OBJ-03.", "Aprendizagem: teste prático no posto. Comportamento: observação após 3 meses (latas fechadas, dispensador usado).", 6),
    ("COMP-02", "Operador de Injeção", "INJ", "AA-007", "Consumo de energia e geração de scrap na injeção",
     "12.º ano ou experiência comprovada em moldação", "FOR-05; FOR-06; FOR-11", "1 ano em moldação por injeção",
     "Atenção a alarmes; trabalho em equipa na passagem de turno",
     "Máquinas aquecidas em vazio e scrap misturado desperdiçam energia e polímero; granulado no chão pode chegar à rede pluvial.",
     "Mais kWh/1.000 un e mais scrap (OBJ-01, OBJ-02).", "Aprendizagem: questionário. Comportamento: auditoria às caixas de scrap segregado.", 15),
    ("COMP-03", "Operador de Sopro (ISBM)", "SOP", "AA-011", "Geração de scrap e purgas de arranque no sopro",
     "12.º ano ou experiência comprovada em moldação", "FOR-05; FOR-06; FOR-11", "1 ano em sopro/ISBM",
     "Atenção a alarmes; registo rigoroso das purgas",
     "Cada arranque mal parametrizado gera kg de purga; a mistura de cores impede a reintegração.",
     "Mais scrap e polímero virgem (OBJ-02).", "Aprendizagem: questionário. Comportamento: registo de purgas por arranque.", 18),
    ("COMP-04", "Responsável de Armazém e Logística", "ARQ", "AA-005", "Derrame de químicos no armazém; gestão de resíduos perigosos",
     "12.º ano de escolaridade", "FOR-01; FOR-03; FOR-04; FOR-09; FOR-11; FOR-15", "2 anos em logística industrial",
     "Organização; capacidade de decisão em emergência",
     "Bidões fora de bacia, contentores sem identificação LER ou e-GAR incompletas geram contaminação do solo e coimas.",
     "Contaminação do solo e da água; NC legal (RGGR).", "Comportamento: resultado das rondas RON-01/02/07/08.", 2),
    ("COMP-05", "Técnico de Manutenção", "MAN", "AA-021", "Fugas de ar comprimido, óleos usados e fugas de óleo hidráulico",
     "Curso profissional de eletromecânica (nível 4)", "FOR-01; FOR-03; FOR-08; FOR-11", "2 anos em manutenção industrial",
     "Diagnóstico; registo das intervenções",
     "Uma fuga de ar de 3 mm a 7 bar consome ≈ 3 kW nos compressores (≈ 3.000 €/ano em laboração contínua); óleo derramado é resíduo perigoso e contamina o solo.",
     "Mais energia (OBJ-01) e derrames.", "Comportamento: n.º de fugas etiquetadas e reparadas por campanha.", 6),
    ("COMP-06", "Técnico de Utilidades", "UTL", "AA-023", "Água da torre de arrefecimento, purga com biocida e chiller (gás fluorado)",
     "Curso profissional de eletromecânica ou frio (nível 4)", "FOR-01; FOR-07; FOR-12; FOR-11", "3 anos em utilidades industriais",
     "Rigor no registo de leituras",
     "Purga mal regulada desperdiça água e descarrega biocida; uma fuga de R410A de 3 kg equivale a ≈ 6 tCO2e.",
     "Consumo de água (OBJ-05); emissões de GEE; NC legal (gases fluorados).", "Aprendizagem: certificado FOR-07 válido. Comportamento: registos de leituras e controlo de fugas.", 2),
    ("COMP-07", "Operador de Armazém / Empilhador", "REC", "AA-003", "Perdas de granulado na descarga de big bags",
     "9.º ano + carta de condução de empilhador", "FOR-06; FOR-09; FOR-03; FOR-11", "6 meses em armazém",
     "Cuidado na movimentação",
     "Um big bag rasgado pode libertar milhares de grânulos que chegam às sarjetas e ao rio (microplásticos).",
     "Poluição por microplásticos; regulamento de granulados (OBJ-06).", "Comportamento: inspeção semanal das sarjetas.", 5),
    ("COMP-08", "Auditor Interno do SGA", "ADM", "", "Transversal (avaliação do SGA)",
     "Licenciatura ou 12.º ano + experiência em sistemas de gestão", "FOR-10", "Participação em 2 auditorias como observador",
     "Imparcialidade; comunicação; escrita de constatações baseadas em evidência",
     "Uma constatação sem evidência objetiva ou sem requisito não gera melhoria e perde credibilidade.",
     "Auditorias ineficazes (9.2).", "Avaliação do auditor após cada auditoria (feedback do auditado).", 3),
]

COLABS = [("OP-SK-001", "COMP-01"), ("OP-SK-002", "COMP-01"), ("OP-SK-003", "COMP-01"), ("OP-SK-004", "COMP-01"), ("OP-SK-005", "COMP-01"), ("OP-SK-T01", "COMP-01"),
          ("OP-INJ-001", "COMP-02"), ("OP-INJ-002", "COMP-02"), ("OP-INJ-003", "COMP-02"), ("OP-INJ-004", "COMP-02"), ("OP-INJ-005", "COMP-02"), ("AUX-INJ-001", "COMP-02"),
          ("OP-SOP-001", "COMP-03"), ("OP-SOP-002", "COMP-03"), ("OP-SOP-003", "COMP-03"), ("OP-SOP-004", "COMP-03"), ("OP-SOP-005", "COMP-03"), ("OP-SOP-006", "COMP-03"),
          ("ARM-001", "COMP-04"), ("ARM-002", "COMP-04"),
          ("Sandra Reis", "COMP-05"), ("Hugo Marques", "COMP-05"), ("Rui Fonseca", "COMP-05"), ("Vitor Sousa", "COMP-05"), ("Marta Nogueira", "COMP-05"), ("José Pinto", "COMP-05"),
          ("UTL-001", "COMP-06"), ("UTL-002", "COMP-06"),
          ("EMP-001", "COMP-07"), ("EMP-002", "COMP-07"), ("EMP-003", "COMP-07"),
          ("AUD-001", "COMP-08"), ("AUD-002", "COMP-08"), ("AUD-003", "COMP-08")]


def build(out):
    b = Book("RG-SGA-08", "Matriz de Competências e Consciencialização Ambiental",
             activities="Atividade 4.1 — Definição da Matriz de Competências Ambientais (função selecionada: Operador de Serigrafia, AAS de COV). A frase 'Competência vs Consciencialização' está no documento Word.",
             clauses="7.1 Recursos; 7.2 Competência; 7.3 Consciencialização (ISO 14001:2026)",
             purpose="Definir, para cada função cujo trabalho afeta o desempenho ambiental, a competência necessária (Competência = Educação + Formação + Experiência + Soft skills), o tema crítico de consciencialização e a forma de avaliar a eficácia da formação (reação, aprendizagem, comportamento). Regista a formação individual para medir a cobertura e cruzar com o desempenho (ex.: NC, scrap, solvente por operador).",
             links=[("RG-SGA-03 Aspetos", "ID_Aspeto_AAS liga a função ao aspeto significativo que controla."),
                    ("Dataset da fábrica", "Os IDs de colaborador (OP-*, técnicos) são os do dataset (dim_operator), permitindo cruzar formação com defeitos e produtividade.")])
    b.add_list("Processo", PROC_CODES)
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("SimNao", ["Sim", "Não"])
    b.add_list("Resultado", ["Aprovado", "Reprovado", "Pendente"])
    b.add_list("Nivel", ["Reação", "Aprendizagem", "Comportamento"])

    fcols = [col("ID_Formacao", 10, desc="Identificador da ação de formação.", key="PK"), col("Formacao", 60, desc="Designação."),
             col("Duracao_h", 9, "int", desc="Duração (horas)."), col("Entidade", 28, desc="Entidade formadora."),
             col("Obrigatoria_Legal", 10, dv="SimNao", desc="Exigida por lei."), col("Reciclagem_Meses", 10, "int", desc="Periodicidade de reciclagem (0 = certificação sem reciclagem)."),
             col("N_Registos", 9, "int", f='=COUNTIF(tbl_registo_formacao[ID_Formacao],@ID_Formacao@)', desc="N.º de registos individuais.")]
    b.table("Catalogo_Formacao", "tbl_formacoes", fcols, [dict(zip([c["name"] for c in fcols], f)) for f in FORMACOES],
            "Catálogo de ações de formação ambiental.")

    mcols = [
        col("ID_Competencia", 10, desc="Identificador do perfil.", key="PK"),
        col("Funcao", 26, dv="Funcao", desc="Função operacional."),
        col("Processo", 8, dv="Processo", desc="Processo."),
        col("ID_Aspeto_AAS", 9, desc="Aspeto significativo associado.", key="FK → RG-SGA-03", req=False),
        col("Aspeto_Significativo", 34, desc="Aspeto ambiental significativo/relevante da função."),
        col("Educacao_Habilitacoes", 24, desc="Nível de educação exigido."),
        col("Formacao_Obrigatoria", 22, desc="Ações de formação obrigatórias (IDs).", key="FK → tbl_formacoes"),
        col("Formacao_Descricao", 44, f='=IFERROR(INDEX(tbl_formacoes[Formacao],MATCH(LEFT(@Formacao_Obrigatoria@,6),tbl_formacoes[ID_Formacao],0))&IF(LEN(@Formacao_Obrigatoria@)>6," (+ "&(LEN(@Formacao_Obrigatoria@)-LEN(SUBSTITUTE(@Formacao_Obrigatoria@,";","")))&" outras)",""),"")', desc="Primeira formação e n.º de outras."),
        col("Experiencia", 26, desc="Experiência mínima."),
        col("Soft_Skills", 28, desc="Competências comportamentais."),
        col("Tema_Consciencializacao", 52, desc="O que o colaborador precisa de saber sobre as consequências do seu trabalho (7.3)."),
        col("Consequencia_Desvio", 30, desc="Consequência de não cumprir."),
        col("Avaliacao_Eficacia", 36, desc="Como se avalia a eficácia (reação, aprendizagem, comportamento)."),
        col("N_Colaboradores", 10, "int", f='=COUNTIF(tbl_registo_formacao[ID_Competencia],@ID_Competencia@)/MAX(1,LEN(@Formacao_Obrigatoria@)-LEN(SUBSTITUTE(@Formacao_Obrigatoria@,";",""))+1)', desc="N.º de colaboradores no perfil (registos ÷ formações obrigatórias)."),
        col("Registos_Aprovados", 10, "int", f='=COUNTIFS(tbl_registo_formacao[ID_Competencia],@ID_Competencia@,tbl_registo_formacao[Resultado],"Aprovado",tbl_registo_formacao[Valida],"Sim")', desc="Registos de formação aprovados e válidos."),
        col("Cobertura", 9, "pct", f='=IFERROR(@Registos_Aprovados@/COUNTIF(tbl_registo_formacao[ID_Competencia],@ID_Competencia@),"")', desc="% de formações obrigatórias concluídas e válidas no perfil."),
        col("Estado", 11, f='=IF(@Cobertura@="","",IF(@Cobertura@>=1,"✓ OK",IF(@Cobertura@>=0.8,"Parcial","Pendente")))', desc="OK = 100%; Parcial ≥ 80%; Pendente < 80%."),
        col("Selecionado_Atv_4_1", 10, dv="SimNao", desc="Função escolhida na Atividade 4.1."),
    ]
    mrows = []
    for m in MATRIZ:
        (i, f, p, aa, asp, ed, fo, ex, ss, tc, cq, ae, n) = m
        mrows.append(dict(ID_Competencia=i, Funcao=f, Processo=p, ID_Aspeto_AAS=aa or None, Aspeto_Significativo=asp, Educacao_Habilitacoes=ed,
                          Formacao_Obrigatoria=fo, Experiencia=ex, Soft_Skills=ss, Tema_Consciencializacao=tc, Consequencia_Desvio=cq,
                          Avaliacao_Eficacia=ae, Selecionado_Atv_4_1="Sim" if i == "COMP-01" else "Não"))
    b.table("Matriz_Competencias", "tbl_competencias", mcols, mrows, "Matriz de competências ambientais por função (cruzando função × aspeto significativo).",
            title="MATRIZ DE COMPETÊNCIAS AMBIENTAIS — PLASTICOM",
            subtitle="Competência = Educação + Formação + Experiência + Soft skills · Consciencialização = entender o impacto das próprias ações · Cobertura calculada a partir do registo individual",
            cf=[("Estado", {"OK": "green", "Parcial": "yellow", "Pendente": "red"}), ("Selecionado_Atv_4_1", {"Sim": "purple"})],
            row_height=110, freeze_col=2)

    # registo individual de formação (dados para análise)
    rng = np.random.default_rng(71)
    reg = []
    k = 0
    for colab, comp in COLABS:
        perfil = next(m for m in MATRIZ if m[0] == comp)
        for fid in [x.strip() for x in perfil[6].split(";")]:
            if fid in NOVAS:
                continue
            k += 1
            fr = next(f for f in FORMACOES if f[0] == fid)
            base = dt.date(2025, 10, 1) + dt.timedelta(days=int(rng.integers(0, 330)))
            res = "Aprovado"
            pend = False
            if colab == "OP-SK-T01" and fid in ("FOR-02", "FOR-03"):
                pend = True                     # operador temporário do turno 2 (NC-SGA-26-08)
            if fid == "FOR-03" and not pend and rng.random() < 0.25:
                pend = True                     # formação de derrames revista após NC-SGA-26-03 (pós-uso)
            if pend:
                res, data = "Pendente", None
            else:
                data = base
            nota = None if pend else int(rng.integers(70, 100))
            reg.append(dict(ID_Registo=f"RF-{k:04d}", Colaborador=colab, ID_Competencia=comp, ID_Formacao=fid, Data_Realizacao=data,
                            Duracao_h=fr[2], Resultado=res, Nota_Teste=nota,
                            Nivel_Avaliado="Comportamento" if (not pend and rng.random() < 0.4) else ("Aprendizagem" if not pend else None),
                            Reciclagem_Meses=fr[5]))
    for r in reg:  # datas reais das formações com evidência externa
        key = (r["Colaborador"], r["ID_Formacao"])
        if key in OVERRIDE and OVERRIDE[key]:
            r["Data_Realizacao"] = d(OVERRIDE[key])
    for colab, comp in COLABS:
        perfil = next(m for m in MATRIZ if m[0] == comp)
        for fid in [x.strip() for x in perfil[6].split(";")]:
            if fid not in NOVAS:
                continue
            k += 1
            fr = next(f for f in FORMACOES if f[0] == fid)
            data = d(OVERRIDE[(colab, fid)]) if OVERRIDE.get((colab, fid)) else None
            reg.append(dict(ID_Registo=f"RF-{k:04d}", Colaborador=colab, ID_Competencia=comp, ID_Formacao=fid, Data_Realizacao=data, Duracao_h=fr[2],
                            Resultado="Aprovado" if data else "Pendente", Nota_Teste=80 if data else None, Nivel_Avaliado="Aprendizagem" if data else None,
                            Reciclagem_Meses=fr[5]))
    # fecho do ano (31/12/2026): formações pendentes realizadas no 4.º trimestre (as 2 últimas transitam para jan/2027)
    rq = np.random.default_rng(1231)
    pend = [r for r in reg if r["Resultado"] == "Pendente"]
    for r in pend[:-2]:
        r["Data_Realizacao"] = dt.date(2026, 10, 12) + dt.timedelta(days=int(rq.integers(0, 63)))
        r["Resultado"], r["Nota_Teste"], r["Nivel_Avaliado"] = "Aprovado", int(rq.integers(72, 96)), "Aprendizagem"
    rcols = [col("ID_Registo", 9, desc="Identificador do registo.", key="PK"), col("Colaborador", 13, desc="ID do colaborador (dataset dim_operator ou interno).", key="FK → dim_operator"),
             col("ID_Competencia", 10, desc="Perfil de competência.", key="FK → tbl_competencias"), col("ID_Formacao", 9, desc="Formação.", key="FK → tbl_formacoes"),
             col("Data_Realizacao", 11, "date", desc="Data em que concluiu.", req=False), col("Duracao_h", 8, "int", desc="Horas."),
             col("Resultado", 10, dv="Resultado", desc="Resultado."), col("Nota_Teste", 8, "int", desc="Nota do teste (0-100).", req=False),
             col("Nivel_Avaliado", 13, dv="Nivel", desc="Nível de avaliação da eficácia (Kirkpatrick).", req=False),
             col("Reciclagem_Meses", 9, "int", desc="Periodicidade de reciclagem."),
             col("Validade", 11, "date", f='=IF(OR(@Data_Realizacao@="",@Reciclagem_Meses@=0),"",EDATE(@Data_Realizacao@,@Reciclagem_Meses@))', desc="Data de validade."),
             col("Valida", 7, f='=IF(@Resultado@<>"Aprovado","Não",IF(@Validade@="","Sim",IF(@Validade@>=DataRef,"Sim","Não")))', desc="Válida na data de referência.")]
    b.table("Registo_Formacao", "tbl_registo_formacao", rcols, reg, "Registo individual de formação ambiental (1 linha por colaborador × formação).",
            cf=[("Resultado", {"Pendente": "red", "Reprovado": "red", "Aprovado": "green"}), ("Valida", {"Não": "red"})])

    # ficha da atividade 4.1
    ws = b.sheet("Resumo_Atividade_4_1", "Ficha da Atividade 4.1 (Operador de Serigrafia), calculada a partir da matriz.", tab_color="7030A0")
    ws["A1"] = "ATIVIDADE 4.1 — MATRIZ DE COMPETÊNCIAS AMBIENTAIS (função selecionada)"
    ws["A1"].font = F_TITLE
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 100
    T = lambda f: b.ref("tbl_competencias", f)
    m = f'MATCH("COMP-01",{T("ID_Competencia")},0)'
    r = 3
    for lab, fld in [("Função", "Funcao"), ("Aspeto Significativo", "Aspeto_Significativo"), ("Educação (habilitações)", "Educacao_Habilitacoes"),
                     ("Formação específica obrigatória (IDs)", "Formacao_Obrigatoria"), ("Experiência", "Experiencia"), ("Soft skills", "Soft_Skills"),
                     ("Consciencialização (tema crítico)", "Tema_Consciencializacao"), ("Consequência de não cumprir", "Consequencia_Desvio"),
                     ("Avaliação da eficácia da formação", "Avaliacao_Eficacia"), ("Cobertura atual da formação", "Cobertura"), ("Estado", "Estado")]:
        c = form_block(ws, r, lab, f'=INDEX({T(fld)},{m})', vw=1, height=48 if fld in ("Tema_Consciencializacao", "Avaliacao_Eficacia") else None)
        if fld == "Cobertura":
            c.number_format = "0%"
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Formações da função").font = F_BOLD
    for fid in ("FOR-01", "FOR-02", "FOR-03", "FOR-11"):
        r += 1
        ws.cell(row=r, column=1, value=fid).font = F_BASE
        ws.cell(row=r, column=2, value=f'=INDEX(tbl_formacoes[Formacao],MATCH(A{r},tbl_formacoes[ID_Formacao],0))&" — "&INDEX(tbl_formacoes[Duracao_h],MATCH(A{r},tbl_formacoes[ID_Formacao],0))&" h"').font = F_BASE
    X.extra_08(b)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
