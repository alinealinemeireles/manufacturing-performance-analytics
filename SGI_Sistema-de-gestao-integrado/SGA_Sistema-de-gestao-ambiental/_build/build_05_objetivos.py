import datetime as dt
import pandas as pd
from sgalib import *
from dims import *
from envdata import ambiente
import build_20_reciclabilidade as R20

DO = dt.date(2026, 6, 15)   # aprovação dos objetivos
d = dt.date.fromisoformat


def series():
    prod, mm, fact, res = ambiente()
    for t in (prod, fact, res, mm):
        t["Mes"] = pd.to_datetime(t["Mes"])
    u = prod[prod.Processo.isin(["INJ", "SOP"])].groupby("Mes").Unid.sum() / 1000
    ser = prod[prod.Processo == "SER"].set_index("Mes").Unid / 1000
    v = lambda var: fact[fact.Variavel == var].groupby("Mes").Valor.sum()
    k = pd.DataFrame({"KPI-01": v("ENE_TOTAL") / u, "KPI-02": v("AGUA_TOTAL") / u, "KPI-03": v("SCRAP_KG") / u,
                      "KPI-06": v("SOLVENTE_KG") / ser})
    return k


POLITICA = [
    ("POL-01", "Proteger o ambiente e prevenir a poluição, incluindo a perda de granulado de plástico e os derrames de produtos químicos."),
    ("POL-02", "Cumprir (meet) as obrigações de conformidade legais e os requisitos ambientais assumidos com clientes."),
    ("POL-03", "Usar de forma eficiente a energia, a água e os materiais e reduzir as emissões de gases com efeito de estufa."),
    ("POL-04", "Aplicar a perspetiva de ciclo de vida: embalagens concebidas para a reciclagem, com conteúdo reciclado e menos material."),
    ("POL-05", "Melhorar continuamente o SGA e o desempenho ambiental, com decisões baseadas em dados."),
    ("POL-06", "Proteger a biodiversidade e a saúde dos ecossistemas envolventes (Pinhal de Leiria, rio Lis, costa)."),
    ("POL-07", "Envolver trabalhadores, fornecedores e clientes na melhoria ambiental."),
]


def build(out):
    k = series()
    rz = R20.resumo()
    base12 = k.loc["2025-09":"2026-08"].mean()
    base_solv = k.loc["2025-09":"2026-05", "KPI-06"].mean()
    b = Book("RG-SGA-05", "Objetivos Ambientais, Metas e Indicadores (KPI)",
             activities="Atividade 3.4 — Planeamento de Objetivos Ambientais e Definição de KPIs (objetivos SMART OBJ-01 a OBJ-06; ficha da atividade com OBJ-01, OBJ-03 e OBJ-04).",
             clauses="6.2.1 Objetivos ambientais; 6.2.2 Planeamento de ações para atingir os objetivos; 9.1.1 (indicadores); 5.2 (ligação à política)",
             purpose="Transformar aspetos significativos, riscos e requisitos legais em objetivos SMART, com indicador (a 'régua'), baseline medida, meta numérica, prazo, recursos e responsável; acompanhar a trajetória até à meta. O catálogo de KPI segue a tipologia da ISO 14031 (indicadores de desempenho operacional, de gestão e de condição ambiental).",
             links=[("RG-SGA-02 / RG-SGA-03 / RG-SGA-04", "Origem_IDs aponta para riscos (RO), aspetos (AA) e requisitos legais (LEG)."),
                    ("RG-SGA-06 PAM", "Acoes_PAM lista as ações do programa para atingir cada objetivo."),
                    ("RG-SGA-13 Monitorização", "Baselines calculadas com os dados mensais do RG-SGA-13 (set/2025–ago/2026).")])
    b.add_list("Politica", [p[0] for p in POLITICA])
    b.add_list("OrigemTipo", ["Aspeto significativo (AAS)", "Aspeto moderado", "Risco legal", "Risco", "Oportunidade", "Parte interessada"])
    b.add_list("Polaridade", ["Menor é melhor", "Maior é melhor", "Zero é o alvo"])
    b.add_list("TipoISO14031", ["ODI — desempenho operacional", "MPI — desempenho de gestão", "ECI — condição ambiental"])
    b.add_list("Frequencia", ["Mensal", "Trimestral", "Semestral", "Anual", "Por ocorrência"])
    b.add_list("MetaTipo", ["Redução relativa", "Aumento relativo", "Valor absoluto"])
    b.add_list("Estado", ["Planeado", "Em curso", "Atingido", "Não atingido", "Cancelado"])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("SimNao", ["Sim", "Não"])

    # política
    pcols = [col("ID_Politica", 10, desc="Compromisso da política ambiental.", key="PK"),
             col("Compromisso", 100, desc="Texto do compromisso (Política Ambiental Plasticom, rev. 2026)."),
             col("N_Objetivos", 11, "int", f='=COUNTIF(tbl_objetivos[ID_Politica],@ID_Politica@)', desc="N.º de objetivos que concretizam o compromisso.")]
    b.table("Politica", "tbl_politica", pcols, [dict(ID_Politica=a, Compromisso=t) for a, t in POLITICA],
            "Compromissos da Política Ambiental (5.2) que dão origem aos objetivos.")

    # catálogo de KPI
    K = [
        ("KPI-01", "Intensidade energética", "Eletricidade total (kWh) ÷ unidades produzidas em injeção + sopro (milhares)", "kWh/1.000 un", "Menor é melhor", "ODI — desempenho operacional", "Mensal", "Fatura + dataset de produção", "Gerente de Manutenção", base12["KPI-01"], "OBJ-01", "MED-01"),
        ("KPI-02", "Intensidade hídrica", "Água de rede (m³) ÷ unidades produzidas (milhares)", "m³/1.000 un", "Menor é melhor", "ODI — desempenho operacional", "Mensal", "Fatura da água + produção", "Gerente de Manutenção", base12["KPI-02"], "OBJ-05", "MED-08"),
        ("KPI-03", "Intensidade de scrap", "Scrap gerado (kg) ÷ unidades produzidas (milhares)", "kg/1.000 un", "Menor é melhor", "ODI — desempenho operacional", "Mensal", "Pesagens + produção", "Gerente de Produção", base12["KPI-03"], "OBJ-02", "MED-03"),
        ("KPI-04", "Taxa de reintegração de scrap", "Scrap reintegrado (kg) ÷ scrap gerado (kg)", "%", "Maior é melhor", "ODI — desempenho operacional", "Mensal", "Pesagens nos moinhos", "Gerente de Produção", None, "OBJ-02", "MED-03"),
        ("KPI-05", "Taxa de valorização de resíduos", "Resíduos com operação R (kg) ÷ resíduos totais (kg)", "%", "Maior é melhor", "ODI — desempenho operacional", "Mensal", "e-GAR / pesagens", "Gestor do SGA / EHS (Responsável Ambiental)", None, "", "MED-04"),
        ("KPI-06", "Solvente de limpeza na serigrafia", "Solvente consumido (kg) ÷ peças serigrafadas (milhares)", "kg/1.000 peças", "Menor é melhor", "ODI — desempenho operacional", "Mensal", "Inventário de solvente + produção SER", "Gestor do SGA / EHS (Responsável Ambiental)", base_solv, "OBJ-03", "MED-06"),
        ("KPI-07", "Resíduos perigosos", "Soma dos resíduos com código LER * (kg)", "kg/mês", "Menor é melhor", "ODI — desempenho operacional", "Mensal", "Pesagens / e-GAR", "Gestor do SGA / EHS (Responsável Ambiental)", None, "", "MED-04"),
        ("KPI-08", "Emissões GEE do âmbito 2", "kWh × fator de emissão da rede", "tCO2e", "Menor é melhor", "ODI — desempenho operacional", "Mensal", "RG-SGA-13 Indicadores_Mensais (kWh) × FE-01 do RG-SGA-19; total anual oficial no RG-SGA-19 tbl_inventario_gee", "Gestor do SGA / EHS (Responsável Ambiental)", None, "OBJ-01", "MED-01"),
        ("KPI-09", "Quota de energia renovável", "kWh renováveis ÷ kWh totais", "%", "Maior é melhor", "ODI — desempenho operacional", "Anual", "Rótulo de energia", "Diretor Financeiro", 0.55, "", "MED-01"),
        ("KPI-10", "Conformidade das rondas ambientais", "Pontos conformes ÷ pontos verificados", "%", "Maior é melhor", "MPI — desempenho de gestão", "Mensal", "RG-SGA-10", "Gestor do SGA / EHS (Responsável Ambiental)", None, "", "MED-10"),
        ("KPI-11", "Incidentes ambientais", "N.º de derrames, fugas e perdas de contenção registados", "n.º/mês", "Zero é o alvo", "MPI — desempenho de gestão", "Mensal", "Registo de incidentes", "Gestor do SGA / EHS (Responsável Ambiental)", None, "", "MED-10"),
        ("KPI-12", "Famílias com conformidade PPWR", "Famílias com documentação técnica e declaração UE ÷ total de famílias", "%", "Maior é melhor", "MPI — desempenho de gestão", "Mensal", "Dossier de produto", "Responsável de R&D", 9 / 22, "OBJ-04", "MED-12"),
        ("KPI-13", "Pontos críticos de granulado com contenção", "Pontos com contenção ÷ pontos críticos (14)", "%", "Maior é melhor", "MPI — desempenho de gestão", "Mensal", "Autoavaliação OCS", "Gestor do SGA / EHS (Responsável Ambiental)", 6 / 14, "OBJ-06", "MED-09"),
        ("KPI-14", "Taxa de conformidade legal", "Requisitos conformes ÷ requisitos aplicáveis", "%", "Maior é melhor", "MPI — desempenho de gestão", "Anual", "RG-SGA-04", "Gestor do SGA / EHS (Responsável Ambiental)", None, "", ""),
        ("KPI-15", "Ações do PAM no prazo", "Ações concluídas no prazo ÷ ações com prazo vencido", "%", "Maior é melhor", "MPI — desempenho de gestão", "Mensal", "RG-SGA-06", "Gestor do SGA / EHS (Responsável Ambiental)", None, "", ""),
        ("KPI-17", "SKUs com avaliação de reciclabilidade", "SKUs de frascos e potes com autoavaliação RecyClass ÷ SKUs ativos", "%", "Maior é melhor", "MPI — desempenho de gestão", "Anual", "RG-SGA-20 tbl_recyclass", "Responsável de R&D", rz["n_avaliados"] / rz["n_skus"], "", ""),
        ("KPI-18", "SKUs com grau PPWR indicativo A–C", "SKUs não isentos com grau A, B ou C ÷ SKUs não isentos", "%", "Maior é melhor", "ODI — desempenho operacional", "Anual", "RG-SGA-20 tbl_recyclass", "Responsável de R&D", rz["pct_ac_skus"], "OBJ-07", ""),
        ("KPI-19", "Conteúdo reciclado no polímero", "Polímero reciclado pós-consumo (kg) ÷ polímero consumido (kg)", "%", "Maior é melhor", "ODI — desempenho operacional", "Mensal", "RG-SGA-13 PCR_KG / POLIMERO_KG; RG-SGA-20", "Responsável de Compras", rz["pcr_massa"], "", ""),
        ("KPI-20", "Massa vendida com grau PPWR A–C", "Massa de corpos vendida com grau A–C ÷ massa vendida (não isentos)", "%", "Maior é melhor", "ODI — desempenho operacional", "Anual", "RG-SGA-20 tbl_recyclass", "Responsável de R&D", rz["pct_ac_massa"], "OBJ-07", ""),
        ("KPI-21", "Certificados de reciclado válidos", "Materiais com PCR com certificado EN 15343 válido ÷ materiais com PCR", "%", "Maior é melhor", "MPI — desempenho de gestão", "Mensal", "RG-SGA-20 tbl_certificados_pcr", "Responsável de Compras", rz["cert_validos"] / rz["cert_necessarios"], "", ""),
        ("KPI-16", "Temperatura média exterior", "Média mensal (°C) — variável explicativa de energia e água", "°C", "Menor é melhor", "ECI — condição ambiental", "Mensal", "IPMA (estação mais próxima)", "Gestor do SGA / EHS (Responsável Ambiental)", None, "", ""),
    ]
    kcols = [col("ID_KPI", 8, desc="Identificador do indicador.", key="PK"), col("Nome", 30, desc="Nome do indicador."),
             col("Formula_Calculo", 50, desc="Numerador ÷ denominador (definição operacional)."), col("Unidade", 14, desc="Unidade."),
             col("Polaridade", 14, dv="Polaridade", desc="Sentido desejado."), col("Tipo_ISO14031", 26, dv="TipoISO14031", desc="Tipologia ISO 14031."),
             col("Frequencia", 11, dv="Frequencia", desc="Frequência de cálculo."), col("Fonte_Dados", 30, desc="Origem dos dados."),
             col("Responsavel", 28, dv="Funcao", desc="Responsável pelo indicador."),
             col("Baseline", 11, "num3", desc="Linha de base (média set/2025–ago/2026 salvo indicação).", req=False),
             col("ID_OBJ", 8, desc="Objetivo que o indicador mede.", key="FK → tbl_objetivos", req=False),
             col("ID_MED", 8, desc="Parâmetro do plano de monitorização.", key="FK → RG-SGA-13", req=False)]
    kn = [c["name"] for c in kcols]
    krows = [dict(zip(kn, [x if x != "" else None for x in r])) for r in K]
    for r in krows:
        if isinstance(r["Baseline"], float):
            r["Baseline"] = round(r["Baseline"], 4)
    b.table("Catalogo_KPI", "tbl_kpi", kcols, krows, "Catálogo de indicadores ambientais (definição operacional de cada 'régua').", row_height=34)

    # objetivos
    O = [
        ("OBJ-01", "POL-03", "Aspeto moderado", "AA-007; AA-010; AA-021; RO-02; LEG-08",
         "Consumo elevado de energia elétrica (≈ 7,8 GWh em 2026, 1.º custo ambiental) nos processos de injeção, sopro e ar comprimido.",
         "Reduzir o consumo específico de eletricidade (kWh por 1.000 unidades produzidas) em 8% até 31/12/2027, face à média set/2025–ago/2026.",
         "KPI-01", "Redução relativa", -0.08, "2027-12-31",
         "Gerente de Manutenção (líder), técnico de utilidades (0,2 ETI), equipa Kaizen de turno.",
         "Detetor ultrassónico de fugas, 6 analisadores de energia, variador de velocidade no compressor CMP-02.",
         42000, "Gerente de Manutenção", "PAM-26-01; PAM-26-02; PAM-26-06", "Em curso"),
        ("OBJ-02", "POL-04", "Aspeto moderado", "AA-008; AA-011; AA-020; RO-11",
         "Scrap plástico ≈ 31 t/ano; taxa de reintegração interna de apenas ≈ 37%.",
         "Reduzir o scrap gerado (kg por 1.000 unidades) em 12% até 30/06/2027, mantendo a taxa de rejeição ≤ 2,0%.",
         "KPI-03", "Redução relativa", -0.12, "2027-06-30",
         "Gerente de Produção, Eng.ª de Processo (DOE), chefes de turno.",
         "Caixas coloridas para segregar scrap por cor/polímero, receitas de arranque validadas.",
         8500, "Gerente de Produção", "PAM-26-12", "Em curso"),
        ("OBJ-03", "POL-01", "Aspeto significativo (AAS)", "AA-014; AA-006; LEG-04; LEG-12",
         "Emissão difusa de COV na limpeza de ecrãs da serigrafia (AAS, IRA 40) e subida recente do consumo de solvente.",
         "Reduzir o consumo de solvente de limpeza na serigrafia (kg por 1.000 peças serigrafadas) em 20% até 30/06/2027, face à média set/2025–mai/2026.",
         "KPI-06", "Redução relativa", -0.20, "2027-06-30",
         "Gestor do SGA/EHS, chefe da serigrafia, operadores SS-001/SS-002 (formação de 2 h).",
         "Dispensadores de segurança com tampa, panos pré-dosados, unidade de recuperação de solvente (destilador).",
         18500, "Gestor do SGA / EHS (Responsável Ambiental)", "PAM-26-07; PAM-26-08; PAM-26-13", "Em curso"),
        ("OBJ-04", "POL-02", "Risco legal", "LEG-09; RO-06; AA-038",
         "PPWR (Reg. (UE) 2025/40) aplicável desde 12/08/2026: só 9 de 22 famílias têm documentação técnica e declaração UE de conformidade (NC legal).",
         "Garantir que 100% das famílias de embalagem têm documentação técnica e declaração UE de conformidade PPWR até 31/12/2026.",
         "KPI-12", "Valor absoluto", 1.0, "2026-12-31",
         "Responsável de R&D, técnico de qualidade/ambiente (0,5 ETI), consultor externo PPWR.",
         "Ensaios de metais pesados por família em laboratório acreditado; modelo de dossier técnico.",
         26000, "Responsável de R&D", "PAM-26-10", "Em curso"),
        ("OBJ-05", "POL-03", "Risco", "AA-023; RO-04; PES-08; PES-09",
         "Consumo de água da torre de arrefecimento (≈ 80% da água) sensível às ondas de calor e à escassez hídrica.",
         "Reduzir o consumo específico de água (m³ por 1.000 unidades) em 10% até 31/12/2027, face à média set/2025–ago/2026.",
         "KPI-02", "Redução relativa", -0.10, "2027-12-31",
         "Diretor Industrial, técnico de utilidades, empresa de tratamento de água.",
         "Controlo automático da purga por condutividade; estudo de torre adiabática em circuito fechado.",
         65000, "Diretor Industrial", "PAM-26-14", "Planeado"),
        ("OBJ-06", "POL-06", "Risco legal", "AA-003; RO-07; LEG-10",
         "Perdas de granulado para a rede pluvial (microplásticos) e regulamento europeu de granulados a aplicar.",
         "Garantir contenção em 100% dos 14 pontos críticos de manuseamento de granulado até 31/03/2027, com zero granulado visível nas sarjetas nas inspeções semanais.",
         "KPI-13", "Valor absoluto", 1.0, "2027-03-31",
         "Gestor do SGA/EHS, operadores de armazém, manutenção.",
         "Filtros de sarjeta, tabuleiros de descarga de big bags, aspirador industrial, kits de recolha.",
         14000, "Gestor do SGA / EHS (Responsável Ambiental)", "PAM-26-11", "Em curso"),
        ("OBJ-07", "POL-04", "Risco legal", "LEG-09; LEG-21; RO-06",
         "PPWR art. 6.º: a partir de 2030 só embalagens com grau A–C. A autoavaliação RecyClass (RG-SGA-20) mostra SKUs em classe F (PVC, PETG, preto de carbono) e abaixo de C (decoração direta em PET).",
         "Garantir que 100% dos SKUs de embalagem não isentos têm grau PPWR indicativo A–C até 31/12/2028, eliminando PVC, PETG e preto de carbono e substituindo a decoração direta em PET.",
         "KPI-18", "Valor absoluto", 1.0, "2028-12-31",
         "Responsável de R&D (líder), área comercial, Responsável de Compras, técnico de qualidade.",
         "Moldes de PET/PP para substituir PVC e PETG, masterbatch preto detetável por NIR, rótulos PE/PP, certificação RecyClass das famílias principais.",
         85000, "Responsável de R&D", "PAM-26-22; PAM-26-23; PAM-26-24", "Em curso"),
    ]
    ocols = [
        col("ID_OBJ", 8, desc="Identificador do objetivo.", key="PK"),
        col("ID_Politica", 9, dv="Politica", desc="Compromisso da política de origem.", key="FK → tbl_politica"),
        col("Origem_Tipo", 18, dv="OrigemTipo", desc="Tipo de origem (AAS, risco legal...)."),
        col("Origem_IDs", 20, desc="IDs de aspetos, riscos e requisitos legais de origem.", key="FK → RG-SGA-02/03/04"),
        col("Origem_Descricao", 40, desc="Origem do objetivo (enunciado: 'Qual o item da Política, Aspeto ou Lei que lhe deu origem?')."),
        col("Declaracao_Objetivo", 50, desc="Verbo de ação + substantivo + meta + prazo."),
        col("ID_KPI", 8, desc="Indicador (régua).", key="FK → tbl_kpi"),
        col("Indicador_KPI", 26, f='=IFERROR(INDEX(tbl_kpi[Nome],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0))&" ("&INDEX(tbl_kpi[Unidade],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0))&")","")', desc="Nome e unidade do KPI."),
        col("Baseline", 10, "num3", f='=IFERROR(INDEX(tbl_kpi[Baseline],MATCH(@ID_KPI@,tbl_kpi[ID_KPI],0)),"")', desc="Linha de base (do catálogo de KPI)."),
        col("Meta_Tipo", 14, dv="MetaTipo", desc="Tipo de meta."),
        col("Meta_Valor", 9, "pct", desc="Variação relativa (ex.: -8%) ou valor absoluto (ex.: 100%)."),
        col("Meta_Numerica", 11, "num3", f='=IF(@Meta_Tipo@="Valor absoluto",@Meta_Valor@,IF(@Baseline@="","",@Baseline@*(1+@Meta_Valor@)))', desc="Valor numérico do KPI a atingir."),
        col("Prazo", 11, "date", desc="Data limite."),
        col("Recursos_Humanos", 32, desc="Pessoas envolvidas."),
        col("Recursos_Materiais", 32, desc="Equipamentos e materiais."),
        col("Recursos_Financeiros_EUR", 11, "eur", desc="Orçamento aprovado (CAPEX + OPEX)."),
        col("Responsavel", 26, dv="Funcao", desc="Responsável pelo objetivo."),
        col("Acoes_PAM", 22, desc="Ações do programa no PAM.", key="FK → RG-SGA-06"),
        col("Estado", 10, dv="Estado", desc="Estado do objetivo."),
        col("Valor_Atual", 10, "num3", desc="Último valor do KPI (média out–dez/2026; água: ano civil de 2026 por causa da sazonalidade; PPWR/granulado: situação em 31/12/2026).", req=False),
        col("Progresso", 9, "pct", f='=IF(OR(@Valor_Atual@="",@Meta_Numerica@="",@Baseline@=""),"",IF(@Meta_Numerica@=@Baseline@,"",MAX(-1,MIN(1,(@Valor_Atual@-@Baseline@)/(@Meta_Numerica@-@Baseline@)))))', desc="Percentagem do caminho baseline → meta já percorrido (negativo = afastou-se)."),
        col("Dias_ate_Prazo", 9, "int", f='=@Prazo@-DataRef', desc="Dias até ao prazo."),
        col("S_Especifico", 8, f='=IF(AND(LEN(@Declaracao_Objetivo@)>40,@ID_KPI@<>""),"✔","✘")', desc="S: declaração clara e ligada a um indicador."),
        col("M_Mensuravel", 8, f='=IF(ISNUMBER(@Meta_Valor@),"✔","✘")', desc="M: meta numérica."),
        col("A_Atingivel", 8, f='=IF(AND(@Recursos_Financeiros_EUR@>0,@Responsavel@<>"",@Acoes_PAM@<>""),"✔","✘")', desc="A: recursos, responsável e ações planeadas."),
        col("R_Relevante", 8, f='=IF(AND(@Origem_IDs@<>"",@ID_Politica@<>""),"✔","✘")', desc="R: nasce de aspeto/risco/lei e da política."),
        col("T_Temporal", 8, f='=IF(ISNUMBER(@Prazo@),"✔","✘")', desc="T: data limite."),
        col("Validacao_SMART", 12, f='=IF((@S_Especifico@="✔")+(@M_Mensuravel@="✔")+(@A_Atingivel@="✔")+(@R_Relevante@="✔")+(@T_Temporal@="✔")=5,"SMART","Rever")', desc="SMART se os 5 critérios estiverem cumpridos."),
        col("Data_Aprovacao", 11, "date", desc="Data de aprovação pela gestão."),
    ]
    val_atual = {"OBJ-01": k.loc["2026-10":"2026-12", "KPI-01"].mean(), "OBJ-02": k.loc["2026-10":"2026-12", "KPI-03"].mean(),
                 "OBJ-03": k.loc["2026-10":"2026-12", "KPI-06"].mean(), "OBJ-04": 17 / 22, "OBJ-05": k.loc["2026-10":"2026-12", "KPI-02"].mean(),
                 "OBJ-06": 11 / 14, "OBJ-07": rz["pct_ac_skus"]}
    val_atual["OBJ-05"] = k.loc["2026-01":"2026-12", "KPI-02"].mean()  # água: ano civil de 2026 (sazonalidade)
    orows = []
    for o in O:
        (i, pol, ot, oi, od, dec, kpi, mt, mv, pz, rh, rm, rf, resp, pam, est) = o
        orows.append(dict(ID_OBJ=i, ID_Politica=pol, Origem_Tipo=ot, Origem_IDs=oi, Origem_Descricao=od, Declaracao_Objetivo=dec,
                          ID_KPI=kpi, Meta_Tipo=mt, Meta_Valor=mv, Prazo=d(pz), Recursos_Humanos=rh, Recursos_Materiais=rm,
                          Recursos_Financeiros_EUR=rf, Responsavel=resp, Acoes_PAM=pam, Estado=est,
                          Valor_Atual=round(val_atual[i], 4), Data_Aprovacao=DO))
    b.table("Objetivos_SMART", "tbl_objetivos", ocols, orows,
            "Registo de objetivos ambientais SMART (1 linha por objetivo) com validação automática SMART e progresso.",
            title="OBJETIVOS AMBIENTAIS SMART — PLASTICOM 2026-2027",
            subtitle="Objetivo = resultado pretendido · Indicador = régua com que se mede · Validação SMART calculada · Valor_Atual: média out–dez/2026 (fecho do ano)",
            cf=[("Validacao_SMART", {"SMART": "green", "Rever": "red"}),
                ("Progresso", "AND(ISNUMBER(@),@<0)", "red"), ("Progresso", "AND(ISNUMBER(@),@>=0.5)", "green"),
                ("Origem_Tipo", {"AAS": "red", "legal": "purple"})],
            row_height=95, freeze_col=1)

    # acompanhamento mensal (trajetória)
    acc = []
    for oid, kid, pz, mv in (("OBJ-01", "KPI-01", "2027-12-31", -0.08), ("OBJ-02", "KPI-03", "2027-06-30", -0.12),
                             ("OBJ-03", "KPI-06", "2027-06-30", -0.20), ("OBJ-05", "KPI-02", "2027-12-31", -0.10)):
        base = base_solv if kid == "KPI-06" else base12[kid]
        for m, val in k[kid].items():
            acc.append(dict(ID_OBJ=oid, ID_KPI=kid, Mes=m.date(), Valor_Real=round(val, 4), Baseline=round(base, 4),
                            Meta_Final=round(base * (1 + mv), 4)))
    acols = [col("ID_OBJ", 8, desc="Objetivo.", key="FK → tbl_objetivos"), col("ID_KPI", 8, desc="Indicador.", key="FK → tbl_kpi"),
             col("Mes", 11, "date", desc="Mês."), col("Valor_Real", 10, "num3", desc="Valor mensal do KPI (dados RG-SGA-13)."),
             col("Baseline", 10, "num3", desc="Linha de base."), col("Meta_Final", 10, "num3", desc="Meta no prazo."),
             col("Desvio_vs_Baseline", 11, "pct1", f='=IF(@Baseline@=0,"",@Valor_Real@/@Baseline@-1)', desc="Variação face à baseline."),
             col("Media_Movel_3M", 11, "num3", f='=IF(COUNTIFS(#ID_OBJ#,@ID_OBJ@,#Mes#,"<="&@Mes@)<3,"",AVERAGEIFS(#Valor_Real#,#ID_OBJ#,@ID_OBJ@,#Mes#,"<="&@Mes@,#Mes#,">"&EDATE(@Mes@,-3)))', desc="Média móvel de 3 meses."),
             col("Sinal", 14, f='=IF(@Desvio_vs_Baseline@="","",IF(@Desvio_vs_Baseline@>=0.1,"▲ Alerta (≥+10%)",IF(@Desvio_vs_Baseline@<=0,"▼ Favorável","≈ Estável")))', desc="Leitura rápida do desvio.")]
    b.table("Acompanhamento_Mensal", "tbl_acomp_objetivos", acols, acc,
            "Série mensal dos KPI dos objetivos (formato longo) com desvio, média móvel e sinal — base para gráficos e previsão.",
            cf=[("Sinal", {"Alerta": "red", "Favorável": "green", "Estável": "yellow"})])

    # ficha da atividade 3.4
    ws = b.sheet("Resumo_Atividade_3_4", "Ficha da Atividade 3.4 com os campos do enunciado para OBJ-01, OBJ-03 e OBJ-04 (calculada).", tab_color="7030A0")
    ws["A1"] = "ATIVIDADE 3.4 — OBJETIVOS AMBIENTAIS SMART E KPIs"
    ws["A1"].font = F_TITLE
    ws["A2"] = "OBJ-01 nasce de aspetos moderados de energia + risco RO-02; OBJ-03 de um AAS (COV); OBJ-04 de um risco legal (PPWR). Calculado a partir de tbl_objetivos."
    ws["A2"].font = F_SUB
    ws.column_dimensions["A"].width = 30
    for L in "BCD":
        ws.column_dimensions[L].width = 52
    T = lambda f: b.ref("tbl_objetivos", f)
    header_row(ws, 4, ["Campo", "Objetivo 1", "Objetivo 2", "Objetivo 3"])
    ws.cell(row=5, column=1, value="ID").font = F_BOLD
    for j, oid in enumerate(["OBJ-01", "OBJ-03", "OBJ-04"]):
        ws.cell(row=5, column=2 + j, value=oid).font = F_BOLD
    campos = [("Origem do Objetivo", "Origem_Descricao"), ("IDs de origem", "Origem_IDs"), ("Declaração do Objetivo", "Declaracao_Objetivo"),
              ("Indicador (KPI)", "Indicador_KPI"), ("Baseline", "Baseline"), ("Meta (Target)", "Meta_Numerica"), ("Meta (variação)", "Meta_Valor"),
              ("Prazo", "Prazo"), ("Recursos — humanos", "Recursos_Humanos"), ("Recursos — materiais", "Recursos_Materiais"),
              ("Recursos — financeiros (€)", "Recursos_Financeiros_EUR"), ("Responsável", "Responsavel"), ("Ações no PAM", "Acoes_PAM"),
              ("Validação SMART", "Validacao_SMART")]
    for k2, (lab, fld) in enumerate(campos):
        r = 6 + k2
        a = ws.cell(row=r, column=1, value=lab)
        a.font, a.border, a.fill = F_BOLD, BORDER, FILL_BAND
        for j in range(3):
            c = ws.cell(row=r, column=2 + j, value=f'=INDEX({T(fld)},MATCH({get_column_letter(2 + j)}$5,{T("ID_OBJ")},0))')
            c.font, c.alignment, c.border = F_BASE, WRAP_TOP, BORDER
            c.number_format = {"Prazo": "dd/mm/yyyy", "Meta_Valor": "+0%;-0%;0%", "Recursos_Financeiros_EUR": "#,##0 €", "Baseline": "0.000", "Meta_Numerica": "0.000"}.get(fld, "General")
        if fld in ("Origem_Descricao", "Declaracao_Objetivo", "Recursos_Humanos", "Recursos_Materiais"):
            ws.row_dimensions[r].height = 60
    r = 7 + len(campos)
    notes = [("S (Específico)", "Uma variável, um âmbito e um indicador definidos (ex.: kWh por 1.000 unidades de injeção + sopro)."),
             ("M (Mensurável)", "Meta numérica face a uma baseline medida (não 'a medir')."),
             ("A (Atingível)", "Orçamento aprovado, responsável e ações planeadas no PAM."),
             ("R (Relevante)", "Nasce de um AAS, de um risco ou de uma obrigação legal e de um compromisso da política."),
             ("T (Temporal)", "Data limite explícita."),
             ("Objetivo vs indicador", "O objetivo é o resultado pretendido (ex.: -8% de energia específica); o indicador é a régua (kWh/1.000 un) com que se mede o progresso.")]
    for lab, txt in notes:
        ws.cell(row=r, column=1, value=lab).font = F_BOLD
        c = ws.cell(row=r, column=2, value=txt)
        c.alignment = WRAP_TOP
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
        r += 1
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
