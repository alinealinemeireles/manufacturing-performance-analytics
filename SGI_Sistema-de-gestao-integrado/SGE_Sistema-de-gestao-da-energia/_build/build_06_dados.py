"""RG-SGE-06 — Plano de recolha de dados energéticos, árvore de contadores, plano de monitorização e medição, equipamentos de medição
(exatidão e repetibilidade) e reconciliação mensal.
ISO 50001:2018 6.6 a)–e), 9.1.1 a)–d) · EN 17267:2019 · ISO 50006:2023 §5.6 · ISO 50015:2014."""
import numpy as np
from sgelib import *
from dimse import *
import edata

CONTADORES = [
    # (ID, descrição, nível, pai, usos, tipo, classe, estado, data de instalação, fração do consumo coberta, equipamento)
    ("M00", "Contador geral de MT do operador de rede (fatura)", 0, "—", "Todos (eletricidade)", "Fixo — faturação", "0,5S (IEC 62053-22)", "Instalado", "2019-03-01", 1.000, "EQP-01"),
    ("M01", "Analisador QGBT-SOP (naves de sopro)", 1, "M00", "SOP", "Fixo — submedição", "0,5S", "Instalado", "2026-12-15", None, "EQP-03"),
    ("M02", "Analisador QGBT-INJ (nave de injeção)", 1, "M00", "INJ", "Fixo — submedição", "0,5S", "Instalado", "2026-12-15", None, "EQP-03"),
    ("M03", "Analisador QGBT-DEC (serigrafia + hot foil)", 1, "M00", "SER; HFS", "Fixo — submedição", "0,5S", "Instalado", "2026-12-15", None, "EQP-03"),
    ("M04", "Analisador Q-AR (compressores e secadores)", 1, "M00", "UTL-AR", "Fixo — submedição", "0,5S", "Instalado", "2026-12-15", None, "EQP-03"),
    ("M05", "Analisador Q-FRIO (chiller, torre, bombas)", 1, "M00", "UTL-FRIO", "Fixo — submedição", "0,5S", "Instalado", "2026-12-15", None, "EQP-03"),
    ("M06", "Analisador Q-SERV (iluminação, AVAC, escritórios)", 1, "M00", "GER", "Fixo — submedição", "0,5S", "Instalado", "2026-12-15", None, "EQP-03"),
    ("M07", "Caudalímetro de ar comprimido na saída dos compressores", 2, "M04", "UTL-AR (Nm³)", "Fixo — variável", "±2% da leitura", "Instalado", "2025-10-15", None, "EQP-04"),
    ("M08", "Analisador portátil PA-01 (campanhas por máquina)", 2, "M01; M02; M03; M04", "Máquinas individuais", "Portátil — campanha", "1 (IEC 61557-12)", "Instalado", "2026-05-20", None, "EQE-01"),
    ("M09", "Cartão de frota (litros por abastecimento)", 0, "—", "FRO", "Fatura", "Bomba certificada", "Instalado", "2020-01-01", None, "—"),
    ("M10", "Contador da UPAC (produção fotovoltaica)", 0, "—", "Autoconsumo", "Fixo — produção", "0,5S", "Planeado", "2027-06-30", None, "—"),
]

PLANO_RECOLHA = [
    # (ID, dado, categoria 6.6, característica-chave 9.1.1, fonte / medidor, método, freq. recolha, freq. análise, retenção, responsável, qualidade, registo)
    ("DAD-01", "Eletricidade total (kWh, kW, kvarh) e potência tomada", "b) consumo da organização", "4) consumo real vs esperado", "M00 (fatura) + leitura interna mensal",
     "Leitura do contador no último dia útil; download da fatura", "Mensal (diária a partir de 12/2026)", "Mensal", "10 anos", GE, "Medido", "RG-SGA-13; RG-SGE-09 tbl_faturas"),
    ("DAD-02", "Unidades produzidas por máquina (INJ, SOP)", "a) variáveis relevantes dos USE", "2) IDE", "MES (dataset de produção)", "Contagem automática por ordem", "Por ordem", "Mensal", "10 anos", GPROD, "Medido", "RG-SGE-05 tbl_base_energia"),
    ("DAD-03", "Eletricidade por USE (SOP, INJ, decoração)", "b) consumo dos USE", "3) operação dos USE", "Rateio RG-SGA-13 até 15/12/2026; depois M01–M03", "Rateio horas × kW → analisadores (15 min)", "Mensal → 15 min", "Mensal / semanal", "10 anos", GE, "Estimado (até 12/2026)", "RG-SGE-04 tbl_consumo_uso"),
    ("DAD-04", "Eletricidade do arrefecimento e temperatura da água gelada", "b) consumo dos USE; c) características operacionais", "3) operação dos USE", "Rateio → M05 (desde 15/12/2026); sonda do chiller",
     "Leitura do controlador do chiller", "Diária", "Mensal", "5 anos", TUTL, "Estimado (até 12/2026)", "RG-SGE-08 tbl_rondas_energia"),
    ("DAD-05", "Ar comprimido: kWh, Nm³, pressão, fugas (teste de vazio)", "b) c) consumo e características operacionais do USE", "2) IDE-08; 3) operação", "M04 + M07 + teste de vazio",
     "Registo contínuo; teste de vazio ao domingo", "Contínua / mensal", "Mensal", "5 anos", TUTL, "Medido (Nm³); estimado (kWh até 12/2026)", "RG-SGE-11 tbl_ar_mv"),
    ("DAD-06", "Temperatura exterior (graus-dia base 15 °C)", "a) variáveis relevantes", "2) IDE (normalização)", "IPMA — estação de Leiria", "Download mensal", "Mensal", "Mensal", "10 anos", GE, "Medido (externo)", "RG-SGE-05 tbl_base_energia"),
    ("DAD-07", "Gasóleo da frota e do gerador (L)", "b) consumo da organização", "4) consumo", "Cartão de frota; registo de testes do GE-01", "Faturas; registo manual", "Mensal", "Anual", "10 anos", DFIN, "Medido / estimado", "RG-SGA-19"),
    ("DAD-08", "Garantias de origem e produção da UPAC", "b) consumo da organização", "2) IDE-10", "Rótulo do comercializador; M10", "Documento anual; contador", "Anual → 15 min (2027)", "Anual", "10 anos", DFIN, "Medido", "RG-SGE-09"),
    ("DAD-09", "Fatores estáticos (n.º de máquinas, turnos, mix)", "d) fatores estáticos", "2) IDE (validade da LBE)", "Planeamento; RG-SGA-18", "Revisão trimestral", "Trimestral", "Trimestral", "10 anos", GE, "Registo", "RG-SGE-05 tbl_fatores_estaticos"),
    ("DAD-10", "Dados dos planos de ação (kW antes/depois, horas, custos)", "e) dados especificados nos planos de ação", "1) eficácia dos planos", "PA-01; analisadores; faturas de compra", "Plano de M&V de cada ação", "Por ação", "Por ação", "Vida da medida + 5 anos", GE, "Medido", "RG-SGE-11 tbl_mv_planos"),
    ("DAD-11", "Horas de marcha e paragens por máquina", "c) características operacionais dos USE", "3) operação dos USE", "MES (dataset)", "Automático", "Por ordem", "Mensal", "10 anos", GPROD, "Medido", "RG-SGE-04 tbl_energia_maquina"),
]

PLANO_MM = [
    # (ID, o que medir, unidade, tipo, como medir, equipamentos, quando medir, quem mede, KPI, critério/meta, quando analisar, característica 9.1.1, desvio significativo, ação)
    ("MEDE-01", "Desempenho energético da instalação (IDE-01)", "% vs LBE-01", "Calcular", "Modelo da LBE-01 com unidades e graus-dia", "M00; MES; IPMA", "Mensal", GE, "IDE-01",
     "Melhoria ≥ 2% (2026) e ≥ 5% (2027)", "Mensal (reunião da EGE)", "2) IDE; 4) real vs esperado", "|real − esperado| > t × erro-padrão (≈ 35 000 kWh/mês)", "Investigar em ≤ 30 dias (RG-SGE-11 tbl_desvios)"),
    ("MEDE-02", "Consumo específico da instalação (IDE-02)", "kWh/1.000 un", "Calcular", "kWh ÷ unidades", "M00; MES", "Mensal", GMAN, "IDE-02", "≤ 101 até 12/2027", "Mensal", "2) IDE", "> LBE + 5% em 2 meses seguidos", "Analisar causas no quadro SQDC"),
    ("MEDE-03", "Operação do sopro (kW por máquina, standby)", "kW; h", "Medir", "Campanha PA-01 → M01", "EQE-01; EQP-03", "Semestral (campanha) → contínua", GPROD, "IDE-03", "Espera ≤ 30% da potência de marcha nas elétricas", "Mensal", "3) operação dos USE", "Máquina > média do processo + 15%", "Verificar parâmetros e manutenção"),
    ("MEDE-04", "Operação da injeção (kW por máquina, standby)", "kW; h", "Medir", "Campanha PA-01 → M02", "EQE-01; EQP-03", "Semestral → contínua", GPROD, "IDE-04", "Standby aplicado em 100% das pausas > 30 min", "Mensal", "3) operação dos USE", "Standby não aplicado em ronda", "Corrigir no turno; formação"),
    ("MEDE-05", "Ar comprimido: potência específica e fugas", "kWh/Nm³; %", "Medir", "M04 + M07; teste de vazio ao domingo; ultrassom", "EQP-04; EQP-05; EQE-01", "Mensal", TUTL, "IDE-08", "≤ 0,105 kWh/Nm³; fugas ≤ 10%", "Mensal", "2) IDE; 3) operação", "Fugas > 15% ou pressão > 7,2 bar", "Campanha de fugas em ≤ 5 dias"),
    ("MEDE-06", "Frio: rácio e setpoint", "fração; °C", "Medir", "Rateio → M05; controlador do chiller", "EQP-03", "Diária (setpoint) / mensal", TUTL, "IDE-06", "≤ 0,095; setpoint ≥ 10 °C", "Mensal", "3) operação dos USE", "Setpoint < 9 °C sem justificação", "Repor e registar"),
    ("MEDE-07", "Eficácia dos planos de ação", "MWh poupados", "Calcular", "Plano de M&V por ação (IPMVP)", "Conforme o plano", "Por ação", GE, "KPI-E-03", "Poupança verificada ≥ 80% da prevista", "Trimestral", "1) eficácia dos planos de ação", "Poupança verificada < 50% da prevista", "Rever a ação (10.1)"),
    ("MEDE-08", "Potência tomada vs contratada", "kW", "Medir", "Fatura / analisador geral", "EQP-01", "Mensal (15 min a partir de 12/2026)", DFIN, "—", "≤ 90% da contratada", "Mensal", "3) operação", "> 95% da contratada", "Deslastre; rever o contrato"),
    ("MEDE-09", "Conformidade legal (SGCIE)", "Estado", "Avaliar", "Checklist legal", "—", "Semestral", GE, "—", "100% conforme", "Semestral", "— (9.1.2)", "Obrigação vencida", "Tratar como NC (RG-SGE-14)"),
]

EQUIP = [
    # (ID, equipamento, IDs_MED, tipo de controlo, última calibração, periodicidade (meses), entidade, evidência, classe, incerteza, repetibilidade, dono do registo)
    ("EQP-01", "Contador geral de eletricidade (operador de rede)", "MEDE-01; MEDE-02; MEDE-08", "Verificação metrológica pelo operador de rede", "2024-05-10", 60, "Operador de rede", "Selo e verificação periódica",
     "0,5S", "±0,5%", "Comparação mensal leitura interna × fatura (tbl_reconciliacao)", "RG-SGA-13"),
    ("EQP-03", "Analisadores de energia (6 un.) — M01 a M06", "MEDE-03 a MEDE-06", "Verificação inicial na instalação + comparação com EQE-01", "2026-12-15", 24, "Instalador certificado", "Relatório de comissionamento RC-2026-12 (Σ M01–M06 = M00 −0,6%)",
     "0,5S", "±0,5%", "Σ M01–M06 vs M00 (±2%)", "RG-SGA-13"),
    ("EQP-04", "Medidor de caudal de ar comprimido", "MEDE-05", "Calibração", "2025-10-15", 24, "Laboratório acreditado", "Certificado CAL-2025-331", "±2% da leitura", "±2%", "Teste de vazio repetido (2 domingos)", "RG-SGA-13"),
    ("EQP-05", "Detetor ultrassónico de fugas", "MEDE-05", "Verificação funcional", "2026-07-01", 12, "Fornecedor", "Relatório de verificação", "—", "Qualitativo", "Fuga-padrão de referência", "RG-SGA-13"),
    ("EQE-01", "Analisador portátil PA-01 com pinças flexíveis (3 × 3 000 A)", "MEDE-03; MEDE-04; MEDE-05; MEDE-07", "Calibração", "2026-05-20", 12, "Laboratório acreditado (IPAC)", "Certificado CAL-2026-118",
     "1 (IEC 61557-12)", "±1% + erro das pinças ±1%", "Medição repetida em 2 máquinas iguais (IM-005/006)", "RG-SGE-06"),
    ("EQE-02", "Sonda de temperatura da água gelada (chiller)", "MEDE-06", "Verificação com termómetro de referência", "2026-03-12", 12, "Interna (termómetro calibrado)", "Registo VT-2026-03", "±0,5 °C", "±0,5 °C", "Duas leituras com 1 h", "RG-SGE-06"),
]


def build(out):
    b = Book("RG-SGE-06", "Recolha de Dados Energéticos, Medição e Monitorização",
             activities="Identificar, medir, monitorizar e analisar as características-chave que afetam o desempenho energético; planear a recolha de dados (o quê, como, com que frequência, "
                        "retenção); assegurar dados exatos e repetíveis; plano de monitorização e medição (9.1.1).",
             clauses="6.6 (plano de recolha de dados; a) variáveis relevantes dos USE, b) consumo dos USE e da organização, c) características operacionais dos USE, d) fatores estáticos, "
                     "e) dados dos planos de ação; plano revisto em intervalos definidos; equipamentos com dados exatos e repetíveis — reter); 9.1.1 a) 1)–4), b), c), d).",
             purpose="Árvore de contadores com cobertura medida vs estimada; plano de recolha de dados 6.6 a–e; plano de monitorização 9.1.1 (mesma estrutura do RG-SGA-13) com critério de "
                     "desvio significativo; equipamentos de medição com exatidão, repetibilidade e estado de calibração calculado; reconciliação mensal leitura interna × fatura.",
             links=[("RG-SGA-13", "Dono dos equipamentos EQP-01 a EQP-05 (cópia aqui para o SGE) e dos consumos mensais."),
                    ("RG-SGE-05", "IDE alimentados (ID_KPI)."), ("RG-SGE-11", "Desvios significativos e dados de M&V."), ("RG-SGQ-09", "Gestão metrológica do SGI (mesma lógica de confirmação).")],
             guidance=[("EN 17267:2019", "Plano de medição e monitorização: contexto, situação atual, priorização, implementação, uso e manutenção dos dados; árvore de contadores."),
                       ("ISO 50006:2023 §5.6", "Recolha de dados, qualidade e frequência coerentes com os IDE."),
                       ("ISO 50015:2014", "Exatidão, incerteza e plano de medição para M&V."),
                       ("IEC 62053-22 / IEC 61557-12", "Classes de exatidão de contadores (0,5S) e analisadores (classe 1)."),
                       ("M-9 Medição e indicadores (curso Bureau Veritas)", "Conteúdo do plano de medição: o quê, porquê, como, frequência, valores esperados, responsável, registo, desvio e ação.")],
             legal=[("Diretiva 2014/32/UE (MID — instrumentos de medição) e controlo metrológico legal do IPQ", "Contador de faturação sujeito a controlo metrológico legal; verificado pelo operador de rede (EQP-01).")])
    b.add_list("Funcao", FUNC_NAMES)
    b.add_list("EstadoCont", ["Instalado", "Em instalação", "Planeado"])

    bm = edata.base_mensal()
    last12 = bm.iloc[-12:]   # ano civil de 2026
    tot = last12["kWh_Total"].sum()
    cov = {"M00": 1.0}
    for k, c_ in (("M01", "kWh_SOP"), ("M02", "kWh_INJ"), ("M04", "kWh_UTL_AR"), ("M05", "kWh_UTL_FRIO"), ("M06", "kWh_GER")):
        cov[k] = round(last12[c_].sum() / tot, 4)
    cov["M03"] = round((last12["kWh_SER"].sum() + last12["kWh_HFS"].sum()) / tot, 4)
    rows = []
    for c_ in CONTADORES:
        d = dict(zip(["ID_Contador", "Descricao", "Nivel", "Pai", "Usos", "Tipo", "Classe_Exatidao", "Estado", "Data_Instalacao", "Fracao_Consumo", "ID_Equipamento"], c_))
        d["Data_Instalacao"] = dt.date.fromisoformat(d["Data_Instalacao"])
        d["Fracao_Consumo"] = cov.get(c_[0])
        rows.append(d)
    ccols = [col("ID_Contador", 8, key="PK", desc="Ponto de medida."), col("Descricao", 44, desc="Contador / analisador."), col("Nivel", 6, "int", desc="0 fronteira; 1 quadro/USE; 2 equipamento."),
             col("Pai", 12, desc="Contador a montante (árvore)."), col("Usos", 18, desc="Usos medidos."), col("Tipo", 20, desc="Tipo."), col("Classe_Exatidao", 14, desc="Classe de exatidão."),
             col("Estado", 12, dv="EstadoCont", desc="Estado."), col("Data_Instalacao", 11, "date", desc="Data de instalação / prevista."),
             col("Fracao_Consumo", 9, "pct1", desc="Fração da eletricidade de 2026 que o ponto mede.", req=False),
             col("ID_Equipamento", 9, desc="Equipamento (tbl_equipamentos).", key="FK → tbl_equipamentos"),
             col("Mede_Hoje", 8, f='=IF(@ID_Contador@="","",IF(AND(@Estado@="Instalado",@Data_Instalacao@<=DataRef),"Sim","Não"))', desc="Em serviço à data de referência?")]
    b.table("Arvore_Contadores", "tbl_contadores", ccols, rows, "Árvore de contadores e cobertura da medição (EN 17267).",
            title="ÁRVORE DE CONTADORES (EN 17267) — cobertura da medição", subtitle="Nível 0 = fronteira; nível 1 = quadros dos USE (em serviço desde 15/12/2026 — PA-E-01); nível 2 = equipamento / campanha",
            cf=[("Estado", {"Em instalação": "orange", "Planeado": "gray", "Instalado": "green"})], row_height=18, freeze_col=2)
    ws = b.wb["Arvore_Contadores"]
    tc = b.tables["tbl_contadores"]
    r = tc["last"] + 2
    cell(ws, r, 1, "KPI-E-01", bold=True)
    cell(ws, r, 2, "Eletricidade medida por submedição fixa em serviço (nível 1) ÷ total", border=False)
    cell(ws, r, 10, '=SUMIFS(tbl_contadores[Fracao_Consumo],tbl_contadores[Nivel],1,tbl_contadores[Mede_Hoje],"Sim")', fmt="0.0%", bold=True)
    cell(ws, r + 1, 2, "Cobertura quando os analisadores M01–M06 estiverem em serviço", border=False)
    cell(ws, r + 1, 10, "=SUMIFS(tbl_contadores[Fracao_Consumo],tbl_contadores[Nivel],1)", fmt="0.0%", bold=True)

    pcols = [col("ID_Dado", 8, key="PK", desc="Dado."), col("Dado", 40, desc="Dado a recolher."), col("Categoria_6_6", 28, desc="Alínea de 6.6 (a–e)."),
             col("Caracteristica_9_1_1", 24, desc="Característica-chave de 9.1.1 a) 1)–4)."), col("Fonte_Medidor", 32, desc="Fonte / medidor."), col("Metodo", 34, desc="Como é recolhido."),
             col("Frequencia_Recolha", 18, desc="Com que frequência se recolhe."), col("Frequencia_Analise", 14, desc="Com que frequência se analisa."), col("Retencao", 12, desc="Tempo de retenção (6.6)."),
             col("Responsavel", 22, dv="Funcao", desc="Responsável."), col("Qualidade_Dados", 18, desc="Medido / estimado (EN 17267)."), col("Registo", 30, desc="Onde fica retido.")]
    b.table("Plano_Recolha_Dados", "tbl_plano_recolha", pcols, rows_from(input_names(pcols), PLANO_RECOLHA),
            "Plano de recolha de dados energéticos (6.6 a–e) — revisto anualmente com a revisão energética.", title="PLANO DE RECOLHA DE DADOS ENERGÉTICOS (6.6)",
            subtitle="Revisto em intervalos definidos (anual) e quando mudam os USE ou os contadores · Categorias a) a e) de 6.6 todas cobertas",
            cf=[("Qualidade_Dados", {"Estimado": "orange", "Medido": "green"})], row_height=36, freeze_col=2)
    ws = b.wb["Plano_Recolha_Dados"]
    tr_ = b.tables["tbl_plano_recolha"]
    r = tr_["last"] + 2
    for i, a_ in enumerate(["a)", "b)", "c)", "d)", "e)"]):
        cell(ws, r + i, 2, f"Categoria 6.6 {a_} coberta?", border=False)
        cell(ws, r + i, 3, f'=IF(COUNTIF(tbl_plano_recolha[Categoria_6_6],"*{a_}*")>0,"Sim","Não")', bold=True)

    mcols = [col("ID_MED", 9, key="PK", desc="Linha do plano de monitorização."), col("O_Que_Medir", 36, desc="O que monitorizar (9.1.1 a)."), col("Unidade", 12, desc="Unidade."),
             col("Tipo", 8, desc="Medir / calcular / avaliar."), col("Como_Medir", 36, desc="Método (9.1.1 b)."), col("Equipamentos", 18, desc="Equipamentos.", key="FK → tbl_equipamentos"),
             col("Quando_Medir", 22, desc="Quando medir (9.1.1 c)."), col("Quem_Mede", 22, dv="Funcao", desc="Responsável."), col("ID_KPI", 9, desc="IDE.", key="FK → RG-SGE-05 tbl_kpi", req=False),
             col("Criterio_Meta", 28, desc="Valor esperado / meta."), col("Quando_Analisar", 18, desc="[Só SGE] Quando analisar e avaliar (9.1.1 d)."),
             col("Caracteristica_9_1_1", 22, desc="[Só SGE] Característica-chave (9.1.1 a 1–4)."),
             col("Desvio_Significativo", 32, desc="[Só SGE] O que é um desvio significativo (9.1.1; M-9)."), col("Acao_Desvio", 30, desc="[Só SGE] Resposta ao desvio.")]
    b.table("Plano_Monitorizacao", "tbl_plano_monitorizacao", mcols, rows_from(input_names(mcols), PLANO_MM),
            "Plano de monitorização, medição, análise e avaliação (9.1.1) — mesmas colunas iniciais do RG-SGA-13.", title="PLANO DE MONITORIZAÇÃO E MEDIÇÃO DO SGE (9.1.1)",
            subtitle="As 4 características-chave mínimas de 9.1.1 a) estão cobertas (eficácia dos planos, IDE, operação dos USE, real vs esperado)", row_height=40, freeze_col=2)

    ecols = [col("ID_Equipamento", 9, key="PK", desc="Equipamento."), col("Equipamento", 40, desc="Descrição."), col("IDs_MED", 20, desc="Linhas do plano que servem."),
             col("Tipo_Controlo", 30, desc="Calibração / verificação."), col("Ultima_Calibracao", 11, "date", desc="Última calibração/verificação.", req=False),
             col("Periodicidade_Meses", 8, "int", desc="Intervalo."), col("Entidade", 22, desc="Quem calibra."), col("Evidencia", 24, desc="Certificado / registo."),
             col("Proxima_Calibracao", 11, "date", f='=IF(OR(@ID_Equipamento@="",@Ultima_Calibracao@=""),"",EDATE(@Ultima_Calibracao@,@Periodicidade_Meses@))', desc="Próxima."),
             col("Estado", 12, f='=IF(@ID_Equipamento@="","",IF(@Ultima_Calibracao@="","Por instalar",IF(@Proxima_Calibracao@<DataRef,"Vencido",IF(@Proxima_Calibracao@-DataRef<=60,"A vencer","Válido"))))', desc="Estado."),
             col("Classe_Exatidao", 14, desc="[Só SGE] Classe / exatidão (6.6)."), col("Incerteza", 16, desc="[Só SGE] Incerteza declarada."),
             col("Verificacao_Repetibilidade", 34, desc="[Só SGE] Como se confirma a repetibilidade (6.6)."), col("Registo_Dono", 10, desc="[Só SGE] Registo dono do equipamento (fonte única).")]
    b.table("Equipamentos_Medicao", "tbl_equipamentos", ecols, rows_from(input_names(ecols), EQUIP, dates=("Ultima_Calibracao",)),
            "Equipamentos de medição de energia: exatidão, repetibilidade e confirmação (6.6 — reter).", title="EQUIPAMENTOS DE MEDIÇÃO DE ENERGIA (6.6)",
            subtitle="EQP-xx = registados no RG-SGA-13 (dono) · EQE-xx = novos do SGE", cf=[("Estado", {"Vencido": "red", "A vencer": "orange", "Válido": "green", "Por instalar": "gray"})],
            row_height=30, freeze_col=2)

    rng = np.random.default_rng(6601)
    rrows = []
    for _, r_ in bm.iterrows():
        fat = int(r_["kWh_Total"])
        leit = int(round(fat * (1 + rng.normal(0, 0.0025))))
        if r_["Mes"] == dt.date(2025, 11, 1):
            leit = int(round(fat * 1.018))   # erro de transcrição detetado e corrigido
        rrows.append(dict(Mes=r_["Mes"], kWh_Fatura=fat, kWh_Leitura_Interna=leit, Leitor=TUTL,
                          Observacao="Erro de transcrição (dígito trocado) corrigido em 03/12/2025" if r_["Mes"] == dt.date(2025, 11, 1) else None))
    rcols = [col("Mes", 11, "date", key="PK", desc="Mês."), col("kWh_Fatura", 11, "kwh", desc="kWh da fatura (RG-SGA-13)."), col("kWh_Leitura_Interna", 11, "kwh", desc="Leitura interna do contador M00 (simulada)."),
             col("Diferenca_Pct", 9, "pct1", f='=IF(@Mes@="","",(@kWh_Leitura_Interna@-@kWh_Fatura@)/@kWh_Fatura@)', desc="Diferença relativa."),
             col("Resultado", 12, f='=IF(@Mes@="","",IF(ABS(@Diferenca_Pct@)<=0.01,"OK","Investigar"))', desc="Critério: |diferença| ≤ 1%."),
             col("Leitor", 22, dv="Funcao", desc="Quem leu."), col("Observacao", 40, desc="Nota.", req=False)]
    b.table("Reconciliacao_Mensal", "tbl_reconciliacao", rcols, rrows, "Reconciliação mensal leitura interna × fatura (repetibilidade e exatidão dos dados — 6.6).",
            title="RECONCILIAÇÃO MENSAL — LEITURA INTERNA × FATURA (6.6)", subtitle="Leituras internas simuladas · Desde 15/12/2026 também Σ analisadores M01–M06 × M00 (±2%): −0,6% no comissionamento",
            cf=[("Resultado", {"Investigar": "red", "OK": "green"})], row_height=16)
    return b.save(out)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
