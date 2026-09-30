"""RG-SGA-19 — ESG Ambiental: calculadora e inventário de GEE, metas climáticas, pegada de produto, substâncias e indicadores.

Tabelas (uma linha = um registo):
  tbl_fatores_emissao    fatores de emissão com fonte e qualidade (editáveis; recalculam tudo)
  tbl_inventario_gee     inventário mensal por âmbito/categoria/fonte (GHG Protocol; âmbito 2 location e market-based)
  tbl_metas_clima        metas 2030 vs ano-base 2025/26, com a projeção do simulador
  tbl_pegada_produto     pegada de carbono berço-portão por produto (frascos e tampas do dataset)
  (substâncias: fonte única no RG-SGA-21 — só o indicador ESG-E15 é trazido de build_21_quimicos.resumo())
  tbl_indicadores_esg    catálogo de indicadores ambientais com mapeamento VSME / ESRS / GRI / SASB / CDP-EcoVadis
  tbl_matriz_esg         requisitos do pilar E → evidência → estado
Folha Calculadora_GEE: seletor de período, resultados por âmbito e categoria, intensidades, gráfico e simulador de descarbonização 2030.
Fatores e pressupostos são simulados/indicativos para a fábrica fictícia Plasticom: confirmar com as fontes oficiais do ano de reporte.
"""
import datetime as dt
import os
import numpy as np
import pandas as pd
from openpyxl.chart import BarChart, Reference
from sgalib import *
from dims import *
import envdata
import build_20_reciclabilidade as R20
from build_11_fornecedores import SCORES

SGA, DIND, DG, PROD, MAN, QUA, LOG, CMP, RD, RH, FIN = FUNC_NAMES[:11]
P12 = ("2026-01-01", "2026-12-01")   # ano de reporte = ano civil de 2026 (ano-base das metas: 2025/26)
D = lambda s: dt.date.fromisoformat(s)

# ------------------------------------------------------------------------------------------ fatores de emissão
# (ID, categoria, descrição, valor, unidade, fonte, ano, qualidade)
FE = [
    ("FE-01", "Eletricidade", "Eletricidade da rede — Portugal (location-based)", 0.110, "kgCO2e/kWh", "Parâmetro FE_ELET do RG-SGA-13 (confirmar valor anual APA/ERSE)", 2025, "Média"),
    ("FE-02", "Eletricidade", "Mix residual — Portugal (market-based, eletricidade sem garantias de origem)", 0.250, "kgCO2e/kWh", "AIB European Residual Mix — confirmar valor do ano de reporte", 2025, "Baixa"),
    ("FE-03", "Eletricidade", "Eletricidade com garantias de origem renovável (market-based)", 0.0, "kgCO2e/kWh", "GHG Protocol Scope 2 Guidance (critérios de qualidade)", 2015, "Alta"),
    ("FE-04", "Combustíveis", "Gasóleo rodoviário e de gerador (combustão)", 2.66, "kgCO2e/L", "Fatores nacionais / DEFRA — confirmar", 2025, "Média"),
    ("FE-05", "Gases fluorados", "R410A — potencial de aquecimento global (GWP100)", 2088, "kgCO2e/kg", "Reg. (UE) 2024/573, Anexo I (IPCC AR4)", 2024, "Alta"),
    ("FE-06", "Materiais", "Polipropileno virgem (PP) — berço-portão", 1.60, "kgCO2e/kg", "Eco-perfis PlasticsEurope (ordem de grandeza) — confirmar", 2023, "Média"),
    ("FE-07", "Materiais", "Polietileno virgem (HDPE, MDPE, LDPE) — berço-portão", 1.80, "kgCO2e/kg", "Eco-perfis PlasticsEurope (ordem de grandeza) — confirmar", 2023, "Média"),
    ("FE-08", "Materiais", "PET / PETG virgem — berço-portão", 2.20, "kgCO2e/kg", "Eco-perfis PlasticsEurope (ordem de grandeza) — confirmar", 2023, "Média"),
    ("FE-09", "Materiais", "PVC virgem — berço-portão", 2.00, "kgCO2e/kg", "Eco-perfis PlasticsEurope (ordem de grandeza) — confirmar", 2023, "Média"),
    ("FE-10", "Materiais", "Polímero reciclado (PCR, rPET) — reciclagem mecânica", 0.50, "kgCO2e/kg", "Estimativa de literatura — pedir PCF ao fornecedor", 2023, "Baixa"),
    ("FE-11", "Materiais", "Polímero virgem — média ponderada do mix da Plasticom", 1.90, "kgCO2e/kg", "Média ponderada de FE-06 a FE-09 pelo consumo", 2025, "Média"),
    ("FE-12", "Materiais", "Tintas de serigrafia", 3.00, "kgCO2e/kg", "Estimativa genérica — pedir PCF ao fornecedor", 2023, "Baixa"),
    ("FE-13", "Materiais", "Solvente de limpeza", 1.80, "kgCO2e/kg", "Estimativa genérica", 2023, "Baixa"),
    ("FE-14", "Materiais", "Foil de hot stamping", 3.50, "kgCO2e/kg", "Estimativa genérica", 2023, "Baixa"),
    ("FE-15", "Materiais", "Masterbatch", 3.00, "kgCO2e/kg", "Estimativa genérica — pedir PCF ao SUP-008", 2023, "Baixa"),
    ("FE-16", "Energia a montante", "Produção de combustíveis e perdas de transporte e distribuição da eletricidade (WTT + T&D)", 0.020, "kgCO2e/kWh", "Estimativa (GHG Protocol categoria 3) — confirmar", 2025, "Baixa"),
    ("FE-17", "Transporte", "Transporte a montante do polímero (média ponderada dos fornecedores do RG-SGA-11)", None, "kgCO2e/kg", "Calculado a partir de volume × distância × modo (tbl_fornecedores)", 2026, "Média"),
    ("FE-18", "Transporte", "Transporte rodoviário de mercadorias (camião articulado 40 t)", 0.108, "kgCO2e/t.km", "JRC (camião articulado 40 t, cálculo próprio) — confirmar com DEFRA/GLEC", 2023, "Média"),
    ("FE-19", "Transporte", "Transporte marítimo de mercadorias", 0.030, "kgCO2e/t.km", "IPCC — relatório especial (limite inferior) — confirmar com GLEC Framework", 2005, "Média"),
    ("FE-20", "Resíduos", "Resíduos encaminhados para reciclagem/valorização (R3, R4, R13)", 0.021, "kgCO2e/kg", "DEFRA (open-loop / transporte e triagem) — confirmar", 2025, "Média"),
    ("FE-21", "Resíduos", "Resíduos depositados em aterro (D1)", 0.45, "kgCO2e/kg", "DEFRA (resíduos comerciais mistos) — confirmar", 2025, "Média"),
    ("FE-22", "Resíduos", "Resíduos perigosos para tratamento/incineração (D15 → D10)", 0.90, "kgCO2e/kg", "Estimativa — confirmar com o operador", 2025, "Baixa"),
    ("FE-23", "Deslocações", "Automóvel ligeiro médio (por km)", 0.170, "kgCO2e/km", "DEFRA (average car, unknown fuel) — confirmar", 2025, "Média"),
    ("FE-24", "Fim de vida", "Fim de vida da embalagem plástica (mix UE: reciclagem, incineração, aterro)", 1.00, "kgCO2e/kg", "Estimativa com mix UE — confirmar por mercado", 2023, "Baixa"),
]
MAT_FE = {"PP": "FE-06", "PP-PG": "FE-06", "PP-FG": "FE-06", "HDPE": "FE-07", "MDPE": "FE-07", "LDPE": "FE-07", "HDPE-FG": "FE-07",
          "PET": "FE-08", "PETG": "FE-08", "PET-PG": "FE-08", "PVC": "FE-09", "HDPE-PCR": "FE-10", "PP-PCR": "FE-10", "rPET": "FE-10"}

# pressupostos de atividade simulados (não existiam nos dados do projeto)
DIESEL_VIATURAS_L = 260      # 2 viaturas de serviço + 1 carrinha (L/mês)
DIESEL_GERADOR_L = 18        # testes mensais do gerador de emergência GE-01 (L/mês)
KM_VIAGENS = 2400            # viagens de negócio em automóvel (km/mês)
COMMUTE = (150, 0.62, 18)    # trabalhadores, fração que vai de automóvel, km ida e volta por dia
KM_JUSANTE = 450             # distância média ponderada a clientes (km, rodoviário)


def transporte_montante_kg():
    """kgCO2e por kg de polímero comprado, ponderado por volume (mesmos fatores de modo do RG-SGA-11)."""
    num = den = 0.0
    for _sid, (_sc, dist, modo, vol, _crit) in SCORES.items():
        f = 0.016 if "Marítimo +" in modo else (0.04 if "Marítimo curto" in modo else 0.075)
        num += vol * dist * f
        den += vol * 1000
    return round(num / den, 4)


def inventario():
    prod, mm, fact, res = envdata.ambiente()
    rng = np.random.default_rng(1919)
    piv = fact.pivot_table(index="Mes", columns="Variavel", values="Valor", aggfunc="sum")
    dias = mm.set_index("Mes")["Dias_Uteis"]
    rows = []
    S1, S2, S3 = "1", "2", "3"

    def add(m, amb, cat, fid, fonte, met, val, un, fe, q, reg, obs=None):
        rows.append(dict(Mes=m, Ambito=amb, Categoria=cat, ID_Fonte=fid, Fonte=fonte, Metodo_Ambito2=met, Dado_Atividade=round(float(val), 2),
                         Unidade=un, ID_FE=fe, Qualidade_Dado=q, Registo_Fonte=reg, Observacao=obs))

    for m in piv.index:
        r = piv.loc[m]
        kwh = r["ENE_TOTAL"]
        poly, pcr = r["POLIMERO_KG"], r["PCR_KG"]
        net_scrap = r["SCRAP_KG"] - r["REGRIND_KG"]
        produto = poly - net_scrap
        rr = res[res.Mes == m]
        rec = rr[rr.Operacao_Destino.str.startswith("R")].Quantidade_kg.sum()
        ate = rr[rr.Operacao_Destino == "D1"].Quantidade_kg.sum()
        per = rr[rr.Operacao_Destino == "D15"].Quantidade_kg.sum()
        add(m, S1, "Combustão móvel (viaturas)", "S1-01", "Gasóleo das viaturas de serviço", "Ambos", DIESEL_VIATURAS_L * rng.uniform(0.85, 1.15), "L", "FE-04", "Medido", "Faturas do cartão de frota", "Consumo simulado")
        add(m, S1, "Combustão estacionária (gerador)", "S1-02", "Gasóleo do gerador de emergência GE-01", "Ambos", DIESEL_GERADOR_L * rng.uniform(0.8, 1.2), "L", "FE-04", "Estimado", "Registo de testes do gerador", "Consumo simulado")
        add(m, S1, "Emissões fugitivas (gases fluorados)", "S1-03", "Fugas de R410A do chiller CH-01", "Ambos", r.get("FGAS_KG", 0) or 0, "kg", "FE-05", "Medido", "RG-SGA-10 tbl_manutencao_ambiental (recargas)")
        add(m, S2, "Eletricidade adquirida", "S2-LB", "Eletricidade da rede (location-based)", "Location-based", kwh, "kWh", "FE-01", "Medido", "RG-SGA-13 tbl_meses (fatura)")
        add(m, S2, "Eletricidade adquirida", "S2-MB-GO", "Eletricidade com garantias de origem renováveis (55%)", "Market-based", kwh * envdata.P["REN_SHARE"], "kWh", "FE-03", "Medido", "Rótulo de energia do comercializador")
        add(m, S2, "Eletricidade adquirida", "S2-MB-RES", "Eletricidade sem garantias de origem (mix residual)", "Market-based", kwh * (1 - envdata.P["REN_SHARE"]), "kWh", "FE-02", "Medido", "Rótulo de energia do comercializador")
        add(m, S3, "C1 Bens e serviços adquiridos", "S3-C1-VIR", "Polímero virgem", "Ambos", poly - pcr, "kg", "FE-11", "Calculado", "RG-SGA-13 tbl_dados_ambientais (POLIMERO_KG − PCR_KG)")
        add(m, S3, "C1 Bens e serviços adquiridos", "S3-C1-PCR", "Polímero reciclado (PCR, rPET)", "Ambos", pcr, "kg", "FE-10", "Calculado", "RG-SGA-13 tbl_dados_ambientais (PCR_KG)")
        add(m, S3, "C1 Bens e serviços adquiridos", "S3-C1-TIN", "Tintas de serigrafia", "Ambos", r["TINTA_KG"], "kg", "FE-12", "Calculado", "RG-SGA-13 tbl_dados_ambientais (TINTA_KG)")
        add(m, S3, "C1 Bens e serviços adquiridos", "S3-C1-SOL", "Solvente de limpeza", "Ambos", r["SOLVENTE_KG"], "kg", "FE-13", "Medido", "RG-SGA-13 tbl_pesagem_solvente")
        add(m, S3, "C1 Bens e serviços adquiridos", "S3-C1-FOI", "Foil de hot stamping", "Ambos", r["FOIL_KG"], "kg", "FE-14", "Calculado", "RG-SGA-13 tbl_dados_ambientais (FOIL_KG)")
        add(m, S3, "C3 Atividades relacionadas com combustíveis e energia", "S3-C3", "WTT e perdas T&D da eletricidade", "Ambos", kwh, "kWh", "FE-16", "Estimado", "RG-SGA-13 tbl_meses")
        add(m, S3, "C4 Transporte e distribuição a montante", "S3-C4", "Transporte do polímero desde os fornecedores", "Ambos", poly, "kg", "FE-17", "Estimado", "RG-SGA-11 tbl_fornecedores (distância e modo)")
        add(m, S3, "C5 Resíduos gerados nas operações", "S3-C5-REC", "Resíduos para reciclagem/valorização", "Ambos", rec, "kg", "FE-20", "Medido", "RG-SGA-13 tbl_residuos (R3, R4, R13)")
        add(m, S3, "C5 Resíduos gerados nas operações", "S3-C5-ATE", "Resíduos para aterro", "Ambos", ate, "kg", "FE-21", "Medido", "RG-SGA-13 tbl_residuos (D1)")
        add(m, S3, "C5 Resíduos gerados nas operações", "S3-C5-PER", "Resíduos perigosos para tratamento", "Ambos", per, "kg", "FE-22", "Medido", "RG-SGA-13 tbl_residuos (D15)")
        add(m, S3, "C6 Viagens de negócio", "S3-C6", "Viagens de negócio em automóvel", "Ambos", KM_VIAGENS * rng.uniform(0.7, 1.3), "km", "FE-23", "Estimado", "Registo de despesas de deslocação", "Simulado")
        add(m, S3, "C7 Deslocações casa-trabalho", "S3-C7", "Deslocações dos trabalhadores em automóvel", "Ambos", COMMUTE[0] * COMMUTE[1] * COMMUTE[2] * float(dias[m]), "km", "FE-23", "Estimado", "Inquérito de mobilidade (pressupostos)", "150 × 62% automóvel × 18 km × dias úteis")
        add(m, S3, "C9 Transporte e distribuição a jusante", "S3-C9", "Transporte do produto a clientes", "Ambos", produto / 1000 * KM_JUSANTE, "t.km", "FE-18", "Estimado", "RG-SGA-11 TRP-01 (distância média ponderada 450 km)")
        add(m, S3, "C12 Fim de vida dos produtos vendidos", "S3-C12", "Embalagens vendidas no fim de vida", "Ambos", produto, "kg", "FE-24", "Estimado", "Massa de produto = polímero − scrap não reintegrado")
    return rows, prod, mm, fact, res


def totais_gee(periodo=P12):
    """tCO2e por âmbito no período (mesmos dados e fatores do tbl_inventario_gee) — fonte única para o EMAS (RG-SGA-16) e a DMA (RG-SGA-17)."""
    rows = inventario()[0]
    fe = {f[0]: f[3] for f in FE}
    fe["FE-17"] = transporte_montante_kg()
    a, b_ = pd.Timestamp(periodo[0]), pd.Timestamp(periodo[1])
    t = {"S1": 0.0, "S2LB": 0.0, "S2MB": 0.0, "S3": 0.0}
    for r in rows:
        if not (a <= pd.Timestamp(r["Mes"]) <= b_) or fe.get(r["ID_FE"]) is None:
            continue
        v = r["Dado_Atividade"] * fe[r["ID_FE"]] / 1000
        if v != v:  # mês sem dado (NaN)
            continue
        if r["Ambito"] == "1":
            t["S1"] += v
        elif r["Ambito"] == "2":
            t["S2LB" if r["Metodo_Ambito2"] == "Location-based" else "S2MB"] += v
        else:
            t["S3"] += v
    return {k: round(v, 1) for k, v in t.items()}


def build(out):
    import build_21_quimicos
    global Q21
    Q21 = build_21_quimicos.resumo()
    rows, prod, mm, fact, res = inventario()
    A = envdata.anual(fact, res, prod)
    b = Book("RG-SGA-19", "ESG Ambiental — Calculadora de GEE, Metas Climáticas e Indicadores", version="00", date=dt.date(2026, 9, 24),
             activities="Complemento ESG (pilar Ambiental) do SGA — não é atividade do curso.",
             clauses="4.1 (clima); 6.1.4; 6.2; 9.1.1 (desempenho ambiental); 7.4 (comunicação externa)",
             purpose=("Medir e comunicar o desempenho ambiental da Plasticom como os clientes, financiadores e referenciais ESG pedem: inventário de "
                      "gases com efeito de estufa (GHG Protocol / ISO 14064-1; âmbitos 1, 2 location e market-based e 3), metas de descarbonização "
                      "com simulador, pegada de carbono por produto (substâncias: RG-SGA-21) e o catálogo de indicadores E mapeado para a VSME, "
                      "ESRS E1–E5, GRI, SASB (RT-CP) e CDP/EcoVadis. Todas as tabelas estão em formato de base de dados (uma linha por registo) para "
                      "Power BI, pandas e modelos de previsão."),
             links=[("RG-SGA-13", "Dados de atividade (tbl_dados_ambientais, tbl_meses, tbl_residuos)."), ("RG-SGA-11", "Transporte a montante (tbl_fornecedores)."),
                    ("RG-SGA-10", "Recargas de gases fluorados (tbl_manutencao_ambiental)."), ("RG-SGA-17", "Temas materiais E1–E5 da dupla materialidade."),
                    ("PR-SGA-13 / PL-SGA-01", "Metodologia de cálculo e plano de transição climática (Documentos_SGA_Plasticom).")])
    b.add_list("Ambito", ["1", "2", "3"])
    b.add_list("Metodo", ["Ambos", "Location-based", "Market-based"])
    b.add_list("Qualidade", ["Alta", "Média", "Baixa"])
    b.add_list("QualidadeDado", ["Medido", "Calculado", "Estimado"])
    b.add_list("Periodo", ["Ano de reporte 2026 (jan–dez)", "Ano-base 2025/26 (set/2025–ago/2026)", "Ano civil 2025 (mar–dez)", "Todo o histórico (22 meses)"])
    b.add_list("EstadoESG", ["Disponível", "Estimado", "Parcial", "Lacuna"])
    b.add_list("Funcao", FUNC_NAMES)

    # ---------------- fatores
    fe_rows = []
    for f in FE:
        v = f[3] if f[3] is not None else transporte_montante_kg()
        fe_rows.append(dict(ID_FE=f[0], Categoria=f[1], Descricao=f[2], Valor=v, Unidade=f[4], Fonte=f[5], Ano_Fonte=f[6], Qualidade=f[7]))
    fcols = [col("ID_FE", 7, desc="Fator.", key="PK"), col("Categoria", 16, desc="Categoria."), col("Descricao", 52, desc="Descrição."),
             col("Valor", 10, "num3", desc="Valor do fator (editável: altera todo o inventário)."), col("Unidade", 13, desc="Unidade."),
             col("Fonte", 52, desc="Fonte e estado de confirmação."), col("Ano_Fonte", 8, "int", desc="Ano da fonte."), col("Qualidade", 9, dv="Qualidade", desc="Qualidade do fator.")]
    b.table("Fatores_Emissao", "tbl_fatores_emissao", fcols, fe_rows, "Fatores de emissão com fonte, ano e qualidade (editar aqui recalcula o inventário, a calculadora e a pegada).",
            title="FATORES DE EMISSÃO", subtitle="Valores indicativos para a fábrica simulada — confirmar com as fontes oficiais do ano de reporte (APA, AIB, DEFRA, eco-perfis)",
            cf=[("Qualidade", {"Baixa": "orange", "Alta": "green"})], row_height=30, extra_rows=15)
    FEV = lambda fid: f'INDEX(tbl_fatores_emissao[Valor],MATCH("{fid}",tbl_fatores_emissao[ID_FE],0))'

    # ---------------- inventário
    icols = [
        col("ID_Registo", 16, f='=IF(@Mes@="","",(YEAR(@Mes@)*100+MONTH(@Mes@))&"-"&@ID_Fonte@)', desc="Chave (mês + fonte)."),
        col("Mes", 11, "date", desc="Mês."),
        col("Ano", 6, "int", f='=IF(@Mes@="","",YEAR(@Mes@))', desc="Ano civil."),
        col("Periodo_Reporte", 12, f='=IF(@Mes@="","",IF(AND(@Mes@>=DATE(2025,9,1),@Mes@<=DATE(2026,8,1)),"2025/26","Fora"))', desc="Ano de reporte (set–ago) — ano-base 2025/26."),
        col("Ambito", 7, dv="Ambito", desc="Âmbito 1, 2 ou 3 (GHG Protocol)."),
        col("Categoria", 34, desc="Categoria do GHG Protocol."),
        col("ID_Fonte", 11, desc="Fonte de emissão."),
        col("Fonte", 38, desc="Descrição da fonte."),
        col("Metodo_Ambito2", 13, dv="Metodo", desc="Location-based / Market-based (âmbito 2) ou Ambos."),
        col("Dado_Atividade", 12, "num", desc="Dado de atividade."),
        col("Unidade", 7, desc="Unidade do dado de atividade."),
        col("ID_FE", 7, desc="Fator de emissão.", key="FK → tbl_fatores_emissao"),
        col("Fator", 9, "num3", f='=IF(@ID_FE@="","",IFERROR(INDEX(tbl_fatores_emissao[Valor],MATCH(@ID_FE@,tbl_fatores_emissao[ID_FE],0)),""))', desc="Valor do fator (automático)."),
        col("tCO2e", 10, "num3", f='=IF(OR(@Dado_Atividade@="",@Fator@=""),"",ROUND(@Dado_Atividade@*@Fator@/1000,3))', desc="Emissões = dado × fator ÷ 1000."),
        col("Qualidade_Dado", 10, dv="QualidadeDado", desc="Medido, calculado ou estimado."),
        col("Registo_Fonte", 36, desc="Origem do dado de atividade."),
        col("Observacao", 28, desc="Pressupostos.", req=False),
    ]
    for r in rows:
        r["Mes"] = r["Mes"] if isinstance(r["Mes"], dt.date) else pd.Timestamp(r["Mes"]).date()
    b.table("Inventario_GEE", "tbl_inventario_gee", icols, rows,
            "Inventário mensal de GEE por âmbito, categoria e fonte (formato longo; 1 linha = 1 fonte × mês).",
            title="INVENTÁRIO DE GASES COM EFEITO DE ESTUFA — MENSAL (GHG Protocol / ISO 14064-1)",
            subtitle="tCO2e = dado de atividade × fator ÷ 1000 · Âmbito 2 com duas linhas de método: somar location OU market, nunca os dois · Linhas vazias no fim para novos meses",
            cf=[("Qualidade_Dado", {"Estimado": "yellow", "Medido": "green"}), ("Ambito", {"1": "red", "2": "orange", "3": "blue"})],
            row_height=18, extra_rows=200, freeze_col=2)

    # ---------------- calculadora
    ws = b.sheet("Calculadora_GEE", "Calculadora interativa: período, resultados por âmbito e categoria, intensidades, gráfico e simulador de descarbonização 2030.",
                 tab_color="7030A0")
    build_calculadora(b, ws, FEV, A)

    # ---------------- metas
    mcols = [col("ID_Meta", 8, desc="Meta.", key="PK"), col("Indicador", 40, desc="Indicador."), col("Unidade", 12, desc="Unidade."),
             col("Ano_Base", 8, desc="Ano-base."), col("Valor_Base", 12, "num1", desc="Valor no ano-base (da calculadora)."),
             col("Ano_Meta", 8, "int", desc="Ano da meta."), col("Tipo_Meta", 14, desc="Redução % ou valor-alvo."),
             col("Alvo", 9, "pct", desc="Redução (negativa) ou valor-alvo (fração)."),
             col("Valor_Meta", 12, "num1", f='=IF(@Valor_Base@="","",IF(@Tipo_Meta@="Redução %",@Valor_Base@*(1+@Alvo@),@Alvo@))', desc="Valor a atingir."),
             col("Projecao_Cenario", 12, "num1", desc="Valor projetado pelo simulador (Calculadora_GEE)."),
             col("Estado", 16, f='=IF(@Projecao_Cenario@="","",IF(IF(@Tipo_Meta@="Redução %",@Projecao_Cenario@<=@Valor_Meta@,@Projecao_Cenario@>=@Valor_Meta@),"Atinge no cenário","Não atinge"))', desc="Se o cenário atinge a meta."),
             col("Referencia", 30, desc="Referência / racional.")]
    metas = [
        ("MET-01", "Emissões dos âmbitos 1 + 2 (market-based)", "tCO2e", "2025/26", "=calc_S12_base", 2030, "Redução %", -0.50, "=calc_S12_2030", "Trajetória 1,5 °C (≈ 4,2%/ano) — SBTi para PME"),
        ("MET-02", "Emissões do âmbito 3", "tCO2e", "2025/26", "=calc_S3_base", 2030, "Redução %", -0.25, "=calc_S3_2030", "Compromisso SBTi para PME (medir e reduzir o âmbito 3)"),
        ("MET-03", "Eletricidade renovável (GO + autoconsumo)", "fração", "2025/26", "=calc_REN_base", 2028, "Valor-alvo", 1.00, "=calc_REN_2030", "Clientes e RE100 (eletricidade 100% renovável)"),
        ("MET-04", "Conteúdo reciclado no polímero", "fração", "2025/26", "=calc_PCR_base", 2030, "Valor-alvo", 0.30, "=calc_PCR_2030", "Metas de conteúdo reciclado do PPWR para 2030"),
        ("MET-05", "Intensidade carbónica total (market-based)", "kgCO2e/t produto", "2025/26", "=calc_INT_base", 2030, "Redução %", -0.35, "=calc_INT_2030", "Descarbonização por unidade produzida"),
    ]
    mrows = [dict(ID_Meta=m[0], Indicador=m[1], Unidade=m[2], Ano_Base=m[3], Valor_Base=m[4], Ano_Meta=m[5], Tipo_Meta=m[6], Alvo=m[7],
                  Projecao_Cenario=m[8], Referencia=m[9]) for m in metas]
    b.table("Metas_Clima", "tbl_metas_clima", mcols, mrows, "Metas climáticas e de circularidade 2030 face ao ano-base 2025/26, com a projeção do simulador.",
            title="METAS CLIMÁTICAS 2030 — BASE, ALVO E PROJEÇÃO DO CENÁRIO", subtitle="A projeção muda com as alavancas da Calculadora_GEE · Metas propostas para aprovação na revisão pela gestão",
            cf=[("Estado", {"Não atinge": "red", "Atinge": "green"})], row_height=30)

    # ---------------- pegada de produto
    build_pegada(b, A)
    # ---------------- indicadores e matriz
    build_indicadores(b, A)
    build_matriz(b)
    return b.save(out)


def build_calculadora(b, ws, FEV, A):
    ws["A1"] = "CALCULADORA DE GASES COM EFEITO DE ESTUFA — PLASTICOM"
    ws["A1"].font = F_TITLE
    ws["A2"] = ("Resultados do inventário (tbl_inventario_gee) por período · Células amarelas editáveis · Âmbito 2 reportado nos dois métodos "
                "(GHG Protocol) · Metas e total usam o market-based · Simulador à direita projeta 2030")
    ws["A2"].font = F_SUB
    for L, w in zip("ABCDEFGHIJKL", (12, 44, 14, 11, 14, 3, 46, 14, 16, 3, 14, 14)):
        ws.column_dimensions[L].width = w
    YEL = PatternFill("solid", fgColor="FFF2B3")

    def band(r, c1, c2, text):
        ws.cell(row=r, column=c1, value=text).font = F_BOLD
        for c in range(c1, c2 + 1):
            ws.cell(row=r, column=c).fill = FILL_BAND

    def cell(r, c, v, fmt=None, bold=False, fill=None):
        x = ws.cell(row=r, column=c, value=v)
        x.font = F_BOLD if bold else F_BASE
        x.border = BORDER
        x.alignment = WRAP_TOP
        if fmt:
            x.number_format = fmt
        if fill:
            x.fill = fill
        return x

    band(4, 1, 5, "1. PERÍODO")
    cell(5, 1, "Período", bold=True)
    sel = cell(5, 2, "Ano de reporte 2026 (jan–dez)", bold=True, fill=YEL)
    dv = DataValidation(type="list", formula1="=lst_Periodo", allow_blank=False)
    ws.add_data_validation(dv)
    dv.add("B5")
    I = lambda c: f"tbl_inventario_gee[{c}]"

    def S(crit, per=True):
        base = f'SUMIFS({I("tCO2e")}{crit}'
        if not per:
            return base + f',{I("Periodo_Reporte")},"2025/26")'
        return (f'IF($B$5="Ano-base 2025/26 (set/2025–ago/2026)",{base},{I("Periodo_Reporte")},"2025/26"),'
                f'IF($B$5="Ano civil 2025 (mar–dez)",{base},{I("Ano")},2025),IF($B$5="Ano de reporte 2026 (jan–dez)",{base},{I("Ano")},2026),{base}))))')

    band(7, 1, 5, "2. RESULTADOS (tCO2e)")
    for j, h in enumerate(["Âmbito", "Categoria / método", "Período selecionado", "% do total (MB)", "Ano-base 2025/26"]):
        c = ws.cell(row=8, column=1 + j, value=h)
        c.font, c.fill, c.alignment, c.border = F_HEAD, FILL_HEAD, CENTER, BORDER
    lines = [("1", "Combustão móvel (viaturas)", None), ("1", "Combustão estacionária (gerador)", None), ("1", "Emissões fugitivas (gases fluorados)", None),
             ("2", "Eletricidade adquirida", "Location-based"), ("2", "Eletricidade adquirida", "Market-based"),
             ("3", "C1 Bens e serviços adquiridos", None), ("3", "C3 Atividades relacionadas com combustíveis e energia", None),
             ("3", "C4 Transporte e distribuição a montante", None), ("3", "C5 Resíduos gerados nas operações", None), ("3", "C6 Viagens de negócio", None),
             ("3", "C7 Deslocações casa-trabalho", None), ("3", "C9 Transporte e distribuição a jusante", None), ("3", "C12 Fim de vida dos produtos vendidos", None)]
    r = 9
    pos = {}
    for amb, cat, met in lines:
        crit = f',{I("Ambito")},"{amb}",{I("Categoria")},"{cat}"' + (f',{I("Metodo_Ambito2")},"{met}"' if met else "")
        cell(r, 1, amb)
        cell(r, 2, cat + (f" — {met}" if met else ""))
        cell(r, 3, "=" + S(crit), "#,##0.0")
        cell(r, 5, "=" + S(crit, per=False), "#,##0.0")
        pos[(amb, cat, met)] = r
        r += 1
    rS1, rLB, rMB = r, r + 1, r + 2
    tot = [("Total âmbito 1", f"=SUM(C9:C11)", "=SUM(E9:E11)"), ("Total âmbito 2 — location-based", "=C12", "=E12"),
           ("Total âmbito 2 — market-based", "=C13", "=E13"), ("Total âmbito 3", f"=SUM(C14:C{r - 1})", f"=SUM(E14:E{r - 1})"),
           ("TOTAL âmbitos 1+2+3 — location-based", f"=C{r}+C{r + 1}+C{r + 3}", f"=E{r}+E{r + 1}+E{r + 3}"),
           ("TOTAL âmbitos 1+2+3 — market-based", f"=C{r}+C{r + 2}+C{r + 3}", f"=E{r}+E{r + 2}+E{r + 3}")]
    for k, (lab, fc, fe_) in enumerate(tot):
        cell(r + k, 2, lab, bold=True)
        cell(r + k, 3, fc, "#,##0.0", bold=True)
        cell(r + k, 5, fe_, "#,##0.0", bold=True)
    rT_LB, rT_MB = r + 4, r + 5
    for rr in list(range(9, r - 1 + 1)) + [r, r + 1, r + 2, r + 3]:
        if rr == 12:
            continue
        cell(rr, 4, f'=IFERROR(C{rr}/$C${rT_MB},"")', "0.0%")
    cell(12, 4, "—")
    rS12 = r + 6
    cell(rS12, 2, "Âmbitos 1 + 2 (market-based)", bold=True)
    cell(rS12, 3, f"=C{r}+C{r + 2}", "#,##0.0", bold=True)
    cell(rS12, 5, f"=E{r}+E{r + 2}", "#,##0.0", bold=True)
    for nm, ref in (("calc_S12_base", f"$E${rS12}"), ("calc_S3_base", f"$E${r + 3}"), ("calc_TOT_MB_base", f"$E${rT_MB}")):
        b.wb.defined_names[nm] = DefinedName(nm, attr_text=f"'Calculadora_GEE'!{ref}")

    # intensidades (ano-base)
    ri = rS12 + 2
    band(ri, 1, 5, "3. INTENSIDADES (ano-base 2025/26)")
    A_prod = f'SUMIFS({I("Dado_Atividade")},{I("ID_Fonte")},"S3-C12",{I("Periodo_Reporte")},"2025/26")/1000'
    ints = [("Produção (t de embalagem)", "=" + A_prod, "#,##0.0"),
            ("Unidades produzidas (injeção + sopro)", A["unid_primarias"], "#,##0"),
            ("Faturação (€)", 3680000, "#,##0 €"),
            ("Intensidade market-based (kgCO2e/t produto)", f"=IFERROR(E{rT_MB}*1000/C{ri + 1},\"\")", "#,##0"),
            ("Intensidade market-based (tCO2e/M€ de faturação)", f"=IFERROR(E{rT_MB}/(C{ri + 3}/1000000),\"\")", "#,##0.0"),
            ("Intensidade âmbitos 1+2 MB (kgCO2e/1.000 unidades)", f"=IFERROR(E{rS12}*1000/(C{ri + 2}/1000),\"\")", "#,##0.00"),
            ("Peso do âmbito 3 no total (MB)", f"=IFERROR(E{r + 3}/E{rT_MB},\"\")", "0%")]
    for k, (lab, f, fmt) in enumerate(ints, start=1):
        cell(ri + k, 2, lab)
        cell(ri + k, 3, f, fmt, fill=YEL if lab.startswith("Faturação") else None)
    b.wb.defined_names["calc_INT_base"] = DefinedName("calc_INT_base", attr_text=f"'Calculadora_GEE'!$C${ri + 4}")
    b.wb.defined_names["calc_PROD_t"] = DefinedName("calc_PROD_t", attr_text=f"'Calculadora_GEE'!$C${ri + 1}")

    # gráfico por categoria (período selecionado)
    ch = BarChart()
    ch.type = "bar"
    ch.style = 10
    ch.title = "Emissões por categoria — período selecionado (tCO2e; âmbito 2 market-based)"
    data = Reference(ws, min_col=3, min_row=8, max_row=r - 1)
    cats = Reference(ws, min_col=2, min_row=9, max_row=r - 1)
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(cats)
    ch.legend = None
    ch.height, ch.width = 9, 17
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ws.add_chart(ch, f"A{ri + 10}")

    # ---------------- simulador
    band(4, 7, 12, "4. SIMULADOR DE DESCARBONIZAÇÃO — CENÁRIO 2030 (altere as células amarelas)")
    levers = [("Crescimento da produção até 2030", 0.10, "0%"), ("Redução do consumo específico de energia (OBJ-01 e seguintes)", 0.15, "0%"),
              ("Produção fotovoltaica em autoconsumo (MWh/ano)", 1400, "#,##0"), ("Eletricidade da rede com garantias de origem", 1.00, "0%"),
              ("Conteúdo reciclado no polímero", 0.30, "0%"), ("Redução de massa por embalagem (lightweighting)", 0.05, "0%"),
              ("GWP do fluido do chiller após substituição (kgCO2e/kg)", 675, "#,##0"), ("Fuga anual esperada de fluido (kg)", 1.5, "0.0"),
              ("Viaturas elétricas", 0.50, "0%"), ("Redução de t.km no transporte a jusante", 0.10, "0%")]
    for k, (lab, v, fmt) in enumerate(levers):
        cell(5 + k, 7, lab)
        cell(5 + k, 8, v, fmt, bold=True, fill=YEL)
    g, eff, pv, go, pcr, lw, gwp, leak, ev, tkm = [f"$H${5 + k}" for k in range(10)]
    SA = lambda fid: f'SUMIFS({I("Dado_Atividade")},{I("ID_Fonte")},"{fid}",{I("Periodo_Reporte")},"2025/26")'
    ST = lambda fid: f'SUMIFS({I("tCO2e")},{I("ID_Fonte")},"{fid}",{I("Periodo_Reporte")},"2025/26")'
    rb = 16
    band(rb, 7, 12, "Valores de base (ano 2025/26, lidos do inventário)")
    base = [("Eletricidade (kWh)", "=" + SA("S2-LB"), "#,##0"), ("Polímero total (kg)", f'={SA("S3-C1-VIR")}+{SA("S3-C1-PCR")}', "#,##0"),
            ("Gasóleo das viaturas (L)", "=" + SA("S1-01"), "#,##0"), ("Gasóleo do gerador (L)", "=" + SA("S1-02"), "#,##0"),
            ("Outros bens C1 — tintas, solvente, foil (tCO2e)", f'={ST("S3-C1-TIN")}+{ST("S3-C1-SOL")}+{ST("S3-C1-FOI")}', "#,##0.0"),
            ("C5 resíduos (tCO2e)", f'={ST("S3-C5-REC")}+{ST("S3-C5-ATE")}+{ST("S3-C5-PER")}', "#,##0.0"),
            ("C6 + C7 deslocações (tCO2e)", f'={ST("S3-C6")}+{ST("S3-C7")}', "#,##0.0"),
            ("C9 transporte a jusante (tCO2e)", "=" + ST("S3-C9"), "#,##0.0"), ("C12 fim de vida (tCO2e)", "=" + ST("S3-C12"), "#,##0.0"),
            ("PCR no ano-base (fração)", f'=IFERROR({SA("S3-C1-PCR")}/H{rb + 2},0)', "0%")]
    for k, (lab, f, fmt) in enumerate(base, start=1):
        cell(rb + k, 7, lab)
        cell(rb + k, 8, f, fmt)
    kwh, poly, dveh, dgen, oc1, c5, c67, c9, c12, pcr0 = [f"$H${rb + k}" for k in range(1, 11)]
    b.wb.defined_names["calc_PCR_base"] = DefinedName("calc_PCR_base", attr_text=f"'Calculadora_GEE'!{pcr0}")
    rp = rb + 12
    band(rp, 7, 12, "Projeção 2030 (tCO2e)")
    for j, h in enumerate(["Indicador", "Ano-base 2025/26", "2030 (cenário)", "", "Variação"]):
        if h:
            c = ws.cell(row=rp + 1, column=7 + j, value=h)
            c.font, c.fill, c.alignment, c.border = F_HEAD, FILL_HEAD, CENTER, BORDER
    kwh30 = f"({kwh}*(1+{g})*(1-{eff}))"
    grid = f"MAX({kwh30}-{pv}*1000,0)"
    poly30 = f"({poly}*(1+{g})*(1-{lw}))"
    rows_p = [
        ("Âmbito 1", f"=E{r}", f"=({dveh}*(1-{ev})+{dgen})*{FEV('FE-04')}/1000+{leak}*{gwp}/1000"),
        ("Âmbito 2 — location-based", f"=E{r + 1}", f"={grid}*{FEV('FE-01')}/1000"),
        ("Âmbito 2 — market-based", f"=E{r + 2}", f"={grid}*(1-{go})*{FEV('FE-02')}/1000"),
        ("Âmbito 3", f"=E{r + 3}", (f"={poly30}*((1-{pcr})*{FEV('FE-11')}+{pcr}*{FEV('FE-10')})/1000+{oc1}*(1+{g})+{grid}*{FEV('FE-16')}/1000"
                                    f"+{poly30}*{FEV('FE-17')}/1000+{c5}*(1+{g})+{c67}+{c9}*(1+{g})*(1-{lw})*(1-{tkm})+{c12}*(1+{g})*(1-{lw})")),
    ]
    for k, (lab, fb, fp) in enumerate(rows_p, start=2):
        cell(rp + k, 7, lab)
        cell(rp + k, 8, fb, "#,##0.0")
        cell(rp + k, 9, fp, "#,##0.0")
        cell(rp + k, 11, f'=IFERROR(I{rp + k}/H{rp + k}-1,"")', "0%")
    rr = rp + 6
    cell(rr, 7, "Âmbitos 1 + 2 (market-based)", bold=True)
    cell(rr, 8, f"=H{rp + 2}+H{rp + 4}", "#,##0.0", bold=True)
    cell(rr, 9, f"=I{rp + 2}+I{rp + 4}", "#,##0.0", bold=True)
    cell(rr, 11, f'=IFERROR(I{rr}/H{rr}-1,"")', "0%", bold=True)
    cell(rr + 1, 7, "TOTAL market-based", bold=True)
    cell(rr + 1, 8, f"=H{rr}+H{rp + 5}", "#,##0.0", bold=True)
    cell(rr + 1, 9, f"=I{rr}+I{rp + 5}", "#,##0.0", bold=True)
    cell(rr + 1, 11, f'=IFERROR(I{rr + 1}/H{rr + 1}-1,"")', "0%", bold=True)
    cell(rr + 2, 7, "Eletricidade renovável (fração)")
    cell(rr + 2, 8, envdata.P["REN_SHARE"], "0%")
    cell(rr + 2, 9, f"=IFERROR(({pv}*1000+{grid}*{go})/{kwh30},0)", "0%")
    cell(rr + 3, 7, "Conteúdo reciclado no polímero (fração)")
    cell(rr + 3, 8, f"={pcr0}", "0%")
    cell(rr + 3, 9, f"={pcr}", "0%")
    cell(rr + 4, 7, "Intensidade total MB (kgCO2e/t produto)")
    cell(rr + 4, 8, "=calc_INT_base", "#,##0")
    cell(rr + 4, 9, f"=IFERROR(I{rr + 1}*1000/(calc_PROD_t*(1+{g})*(1-{lw})),\"\")", "#,##0")
    for k in range(2, 5):
        cell(rr + k, 11, f'=IFERROR(I{rr + k}/H{rr + k}-1,"")', "0%")
    for nm, ref in (("calc_S12_2030", f"$I${rr}"), ("calc_S3_2030", f"$I${rp + 5}"), ("calc_REN_base", f"$H${rr + 2}"),
                    ("calc_REN_2030", f"$I${rr + 2}"), ("calc_PCR_2030", f"$I${rr + 3}"), ("calc_INT_2030", f"$I${rr + 4}")):
        b.wb.defined_names[nm] = DefinedName(nm, attr_text=f"'Calculadora_GEE'!{ref}")
    ws.cell(row=rr + 6, column=7, value=("Leitura: a projeção aplica as alavancas às quantidades do ano-base. Fatores na folha Fatores_Emissao. "
                                         "As metas e o seu estado estão em Metas_Clima (tbl_metas_clima).")).font = F_SUB
    ch2 = BarChart()
    ch2.style = 10
    ch2.title = "Ano-base vs 2030 (tCO2e)"
    ch2.add_data(Reference(ws, min_col=8, max_col=9, min_row=rp + 1, max_row=rp + 5), titles_from_data=True)
    ch2.set_categories(Reference(ws, min_col=7, min_row=rp + 2, max_row=rp + 5))
    ch2.height, ch2.width = 8, 15
    ch2.x_axis.delete = False
    ch2.y_axis.delete = False
    ws.add_chart(ch2, f"G{rr + 8}")
    ws.freeze_panes = "A4"


def build_pegada(b, A):
    root = envdata.ROOT
    bt = pd.read_csv(os.path.join(root, "datasets", "silver", "dim_bottle.csv"))
    cp = pd.read_csv(os.path.join(root, "datasets", "silver", "dim_cap.csv"))
    over = (A["ene_UTL-AR"] + A["ene_UTL-FRIO"] + A["ene_GER"]) / (A["ene_INJ"] + A["ene_SOP"] + A["ene_SER"] + A["ene_HFS"])
    prod, _mm, fact, res = envdata.ambiente()
    p12 = prod[(prod.Mes >= D(P12[0])) & (prod.Mes <= D(P12[1]))].groupby("Processo")[["Unid", "Rej"]].sum()
    kwh_sop = A["ene_SOP"] / p12.loc["SOP", "Unid"] * 1000 * (1 + over)
    kwh_inj = A["ene_INJ"] / p12.loc["INJ", "Unid"] * 1000 * (1 + over)
    rej_sop = p12.loc["SOP", "Rej"] / p12.loc["SOP", "Unid"]
    rej_inj = p12.loc["INJ", "Rej"] / p12.loc["INJ", "Unid"]
    rows = []
    for x in bt.itertuples():
        m = round(envdata.P["G_FRASCO"] * (x.VolumeMl / 300) ** (2 / 3), 1)
        rows.append(dict(ProductId=x.ProductId, Tipo="Frasco (ISBM)", Material=x.BaseMaterial, ID_FE_Material=MAT_FE[x.BaseMaterial],
                         Conteudo_Reciclado="Sim" if x.BaseMaterial in ("HDPE-PCR", "PP-PCR", "rPET") else "Não", Volume_ml=x.VolumeMl,
                         Massa_g=m, Origem_Massa="Estimada (22 g a 300 ml, escala ^2/3)", Masterbatch_Frac=x.StandardDosagePctMass,
                         Taxa_Rejeicao=round(rej_sop, 4), kWh_por_1000=round(kwh_sop, 1)))
    for x in cp.itertuples():
        m = round((x.MinWeightG + x.MaxWeightG) / 2, 1)
        rows.append(dict(ProductId=x.CapId, Tipo="Tampa (injeção)", Material=x.Material, ID_FE_Material=MAT_FE[x.Material],
                         Conteudo_Reciclado="Sim" if "PCR" in x.Material else "Não", Volume_ml=None, Massa_g=m,
                         Origem_Massa="Especificação (média mín./máx.)", Masterbatch_Frac=0.02, Taxa_Rejeicao=round(rej_inj, 4), kWh_por_1000=round(kwh_inj, 1)))
    cols = [col("ProductId", 22, desc="Produto (dataset).", key="PK"), col("Tipo", 14, desc="Frasco ou tampa."), col("Material", 9, desc="Material base."),
            col("ID_FE_Material", 8, desc="Fator do material.", key="FK → tbl_fatores_emissao"), col("Conteudo_Reciclado", 9, desc="Sim se PCR/rPET."),
            col("Volume_ml", 8, "num0", desc="Volume (frascos).", req=False), col("Massa_g", 8, "num1", desc="Massa por unidade (g)."),
            col("Origem_Massa", 26, desc="Origem da massa."), col("Masterbatch_Frac", 9, "pct", desc="Dosagem de masterbatch (fração da massa)."),
            col("Taxa_Rejeicao", 8, "pct1", desc="Rejeição do processo no ano de reporte (material extra consumido)."),
            col("kWh_por_1000", 9, "num1", desc="Eletricidade por 1.000 unidades (processo + utilidades rateadas)."),
            col("kgCO2e_Material_1000", 11, "num1", f='=IFERROR(@Massa_g@*(1+@Taxa_Rejeicao@)*(1-@Masterbatch_Frac@)*INDEX(tbl_fatores_emissao[Valor],MATCH(@ID_FE_Material@,tbl_fatores_emissao[ID_FE],0)),"")',
                desc="Polímero por 1.000 un (kg = g/un) × fator."),
            col("kgCO2e_Masterbatch_1000", 11, "num1", f='=IFERROR(@Massa_g@*(1+@Taxa_Rejeicao@)*@Masterbatch_Frac@*INDEX(tbl_fatores_emissao[Valor],MATCH("FE-15",tbl_fatores_emissao[ID_FE],0)),"")', desc="Masterbatch."),
            col("kgCO2e_Energia_LB_1000", 11, "num1", f='=IFERROR(@kWh_por_1000@*INDEX(tbl_fatores_emissao[Valor],MATCH("FE-01",tbl_fatores_emissao[ID_FE],0)),"")', desc="Eletricidade (location-based)."),
            col("kgCO2e_Total_1000", 11, "num1", f='=IFERROR(@kgCO2e_Material_1000@+@kgCO2e_Masterbatch_1000@+@kgCO2e_Energia_LB_1000@,"")', desc="Pegada berço-portão por 1.000 un (sem decoração nem transporte)."),
            col("gCO2e_por_Unidade", 9, "num1", f='=IFERROR(@kgCO2e_Total_1000@,"")', desc="g CO2e por unidade (= kg por 1.000)."),
            col("Peso_Material_Pct", 9, "pct", f='=IFERROR((@kgCO2e_Material_1000@+@kgCO2e_Masterbatch_1000@)/@kgCO2e_Total_1000@,"")', desc="Peso dos materiais na pegada.")]
    b.table("Pegada_Produto", "tbl_pegada_produto", cols, rows,
            "Pegada de carbono berço-portão por produto (frascos e tampas do dataset), para resposta a clientes e ecodesign.",
            title="PEGADA DE CARBONO POR PRODUTO — BERÇO-PORTÃO (estimativa ISO 14067 simplificada)",
            subtitle="Sem decoração, embalagem de transporte nem fim de vida · Massa dos frascos estimada · Fatores em Fatores_Emissao · Não é uma PCF verificada",
            cf=[("Conteudo_Reciclado", {"Sim": "green"})], row_height=18, freeze_col=1)


def build_indicadores(b, A):
    TV = lambda amb, extra="": f'=SUMIFS(tbl_inventario_gee[tCO2e],tbl_inventario_gee[Ambito],"{amb}",tbl_inventario_gee[Ano],2026{extra})'
    ene = A["ene_total_kwh"] / 1000
    water_evap = A["agua_torre"] * 0.8
    res_t, per_t, val_t = A["res_total"] / 1000, A["res_perig"] / 1000, A["res_valoriz"] / 1000
    poly_t, pcr_t = A["polimero_kg"] / 1000, A["pcr_kg"] / 1000
    # (ID, tema, indicador, valor, unidade, VSME, ESRS, GRI, SASB, CDP/EcoVadis, fonte, estado)
    ind = [
        ("ESG-E01", "Energia", "Consumo total de energia", round(ene, 1), "MWh", "B3", "E1-5", "302-1", "RT-CP-130a.1", "CDP C8 / EcoVadis ENV", "RG-SGA-13 tbl_meses", "Disponível"),
        ("ESG-E02", "Energia", "Eletricidade renovável (garantias de origem)", round(ene * envdata.P["REN_SHARE"], 1), "MWh", "B3", "E1-5", "302-1", "RT-CP-130a.1", "CDP C8", "Rótulo de energia", "Disponível"),
        ("ESG-E03", "Energia", "Quota de energia renovável", envdata.P["REN_SHARE"], "fração", "B3", "E1-5", "302-1", "RT-CP-130a.1", "CDP C8", "Rótulo de energia", "Disponível"),
        ("ESG-E04", "Energia", "Intensidade energética", round(ene / (A["unid_primarias"] / 1000) * 1000, 1), "kWh/1.000 un", "—", "E1-5", "302-3", "—", "EcoVadis ENV", "RG-SGA-05 KPI-01", "Disponível"),
        ("ESG-E05", "Clima", "Emissões de GEE — âmbito 1", TV("1"), "tCO2e", "B3", "E1-6", "305-1", "RT-CP-110a.1", "CDP C6", "tbl_inventario_gee", "Disponível"),
        ("ESG-E06", "Clima", "Emissões de GEE — âmbito 2 location-based", TV("2", ',tbl_inventario_gee[Metodo_Ambito2],"Location-based"'), "tCO2e", "B3", "E1-6", "305-2", "—", "CDP C6", "tbl_inventario_gee", "Disponível"),
        ("ESG-E07", "Clima", "Emissões de GEE — âmbito 2 market-based", TV("2", ',tbl_inventario_gee[Metodo_Ambito2],"Market-based"'), "tCO2e", "B3", "E1-6", "305-2", "—", "CDP C6", "tbl_inventario_gee", "Estimado"),
        ("ESG-E08", "Clima", "Emissões de GEE — âmbito 3 (8 categorias)", TV("3"), "tCO2e", "C (abrangente)", "E1-6", "305-3", "—", "CDP C6.5", "tbl_inventario_gee", "Estimado"),
        ("ESG-E09", "Clima", "Intensidade de GEE por faturação (market-based)", "=calc_TOT_MB_base/3.68", "tCO2e/M€", "B3", "E1-6", "305-4", "—", "CDP C6.10", "Calculadora_GEE", "Estimado"),
        ("ESG-E10", "Clima", "Metas de redução de GEE", "=COUNTA(tbl_metas_clima[ID_Meta])", "n.º de metas", "C (abrangente)", "E1-4", "305-5", "—", "CDP C4", "tbl_metas_clima", "Parcial"),
        ("ESG-E11", "Clima", "Plano de transição climática", "PL-SGA-01", "documento", "C (abrangente)", "E1-1", "—", "—", "CDP C3", "Documentos_SGA_Plasticom", "Parcial"),
        ("ESG-E12", "Poluição", "Emissões de COV (balanço do inventário de químicos: quantidade × teor de COV)", Q21["cov_t"], "t", "B4", "E2-4", "305-7", "RT-CP-120a.1", "EcoVadis ENV", "RG-SGA-16 EMAS-06b (mesmo método)", "Estimado"),
        ("ESG-E13", "Poluição", "Perdas de granulado recolhidas (microplásticos)", round(A["granulado_kg"], 1), "kg", "B4", "E2-4", "306", "—", "—", "RG-SGA-13 GRANULADO_KG", "Parcial"),
        ("ESG-E14", "Poluição", "Resultados de ensaios não conformes com o limite", '=COUNTIF(tbl_analises_ref,"Não conforme")', "n.º", "B4", "E2-4", "303-4", "—", "—", "RG-SGA-13 tbl_analises", "Disponível"),
        ("ESG-E15", "Poluição", "Substâncias preocupantes (SVHC/PFAS) em uso", Q21["n_preocupantes"], "n.º", "—", "E2-5", "—", "—", "EcoVadis ENV", "RG-SGA-21 tbl_quimicos (resumo)", "Parcial"),
        ("ESG-E16", "Água", "Captação total de água (rede pública)", round(A["agua_total"], 0), "m³", "B6", "E3-4", "303-3", "RT-CP-140a.1", "CDP W1", "RG-SGA-13 tbl_meses", "Disponível"),
        ("ESG-E17", "Água", "Consumo de água (evaporação na torre)", round(water_evap, 0), "m³", "B6", "E3-4", "303-5", "RT-CP-140a.1", "CDP W1", "tbl_meses (80% da água da torre)", "Estimado"),
        ("ESG-E18", "Água", "Captação em zona de stress hídrico", "Por avaliar (WRI Aqueduct, região Centro)", "texto", "B6", "E3-4", "303-3", "RT-CP-140a.1", "CDP W1", "—", "Lacuna"),
        ("ESG-E19", "Biodiversidade", "Área total do terreno", 45000, "m²", "B5", "E4-5", "304-1", "—", "—", "RG-SGA-16 EMAS-05", "Disponível"),
        ("ESG-E20", "Biodiversidade", "Área impermeabilizada", 32000, "m²", "B5", "E4-5", "—", "—", "—", "RG-SGA-16 EMAS-05b", "Disponível"),
        ("ESG-E21", "Biodiversidade", "Área orientada para a natureza no local", 3500, "m²", "B5", "E4-5", "—", "—", "—", "RG-SGA-16 EMAS-05c", "Disponível"),
        ("ESG-E22", "Biodiversidade", "Proximidade de áreas sensíveis para a biodiversidade", "Sim — Pinhal de Leiria (confirmar Rede Natura 2000 / ICNF)", "texto", "B5", "E4-5", "304-1", "—", "—", "RG-SGA-01 PES-10", "Parcial"),
        ("ESG-E23", "Recursos", "Materiais consumidos — polímero", round(poly_t, 1), "t", "B7", "E5-4", "301-1", "RT-CP-410a.1", "EcoVadis ENV", "RG-SGA-13 POLIMERO_KG", "Disponível"),
        ("ESG-E24", "Recursos", "Conteúdo reciclado no polímero", round(pcr_t / poly_t, 3), "fração", "B7", "E5-4", "301-2", "RT-CP-410a.1", "EcoVadis ENV", "RG-SGA-13 PCR_KG", "Disponível"),
        ("ESG-E25", "Recursos", "Resíduos produzidos (total)", round(res_t, 1), "t", "B7", "E5-5", "306-3", "—", "EcoVadis ENV", "RG-SGA-13 tbl_residuos", "Disponível"),
        ("ESG-E26", "Recursos", "Resíduos perigosos", round(per_t, 2), "t", "B7", "E5-5", "306-3", "RT-CP-150a.1", "—", "RG-SGA-13 tbl_residuos", "Disponível"),
        ("ESG-E27", "Recursos", "Resíduos desviados de eliminação (operações R)", round(val_t, 1), "t", "B7", "E5-5", "306-4", "—", "—", "RG-SGA-13 tbl_residuos", "Disponível"),
        ("ESG-E28", "Recursos", "Taxa de valorização de resíduos", round(val_t / res_t, 3), "fração", "B7", "E5-5", "306-4", "—", "EcoVadis ENV", "RG-SGA-05 KPI-05", "Disponível"),
        ("ESG-E29", "Recursos", "Produtos recicláveis por massa (grau PPWR indicativo A–C, não isentos)", round(R20.resumo()["pct_ac_massa"], 3), "fração", "B7", "E5-5", "301-3", "RT-CP-410a.2", "EcoVadis ENV", "RG-SGA-20 tbl_recyclass; RG-SGA-05 KPI-20", "Estimado"),
        ("ESG-E30", "Produto", "Pegada de carbono média por unidade (berço-portão)", "=AVERAGE(tbl_pegada_produto[gCO2e_por_Unidade])", "gCO2e/un", "—", "E1 (voluntário)", "—", "—", "CDP (clientes)", "tbl_pegada_produto", "Estimado"),
        ("ESG-E31", "Gestão", "Incidentes ambientais no ano de reporte", '=COUNTIFS(tbl_incidentes_ref,">="&DATE(2025,9,1))', "n.º", "—", "E2", "—", "—", "EcoVadis ENV", "RG-SGA-07 tbl_incidentes", "Disponível"),
        ("ESG-E32", "Gestão", "Coimas e sanções ambientais", 0, "€", "—", "G1 / E2", "2-27", "—", "EcoVadis ENV", "RG-SGA-04", "Disponível"),
        ("ESG-E33", "Gestão", "Sistema de gestão ambiental", "ISO 14001:2026 em implementação (prontidão no RG-SGA-00)", "texto", "B2", "E1–E5 MDR-P", "—", "—", "EcoVadis ENV", "RG-SGA-00 Resumo_Prontidao", "Disponível"),
        ("ESG-E34", "Cadeia de valor", "Fornecedores de resina avaliados ambientalmente", 1.0, "fração", "—", "G1-2", "308-1", "—", "EcoVadis SUP", "RG-SGA-11 tbl_fornecedores", "Disponível"),
    ]
    cols = [col("ID_Indicador", 8, desc="Identificador.", key="PK"), col("Tema", 13, desc="Tema ambiental."), col("Indicador", 40, desc="Indicador."),
            col("Valor", 14, "num", desc="Valor do ano de reporte 2026 (fórmula quando calculado neste ficheiro; valor fixo quando vem de outro registo)."),
            col("Unidade", 11, desc="Unidade."), col("VSME", 10, desc="Norma voluntária para PME (EFRAG): B = módulo básico; C = abrangente."),
            col("ESRS", 10, desc="Requisito ESRS equivalente."), col("GRI", 8, desc="GRI Standard."), col("SASB_RT_CP", 12, desc="SASB Containers & Packaging."),
            col("CDP_EcoVadis", 16, desc="Pergunta CDP / tema EcoVadis."), col("Registo_Fonte", 28, desc="Origem do valor."),
            col("Estado", 10, dv="EstadoESG", desc="Disponível · Estimado · Parcial · Lacuna.")]
    names = [c["name"] for c in cols]
    data = [dict(zip(names, i)) for i in ind]
    b.table("Indicadores_ESG_E", "tbl_indicadores_esg", cols, data,
            "Catálogo de indicadores ambientais do ano de reporte 2026 mapeados para VSME, ESRS, GRI, SASB e CDP/EcoVadis.",
            title="INDICADORES ESG — PILAR AMBIENTAL (ano de reporte 2026)",
            subtitle="Pronto para relatório VSME, questionários CDP/EcoVadis e Power BI · Estimado/Parcial/Lacuna indicam o que falta melhorar",
            cf=[("Estado", {"Lacuna": "red", "Parcial": "orange", "Estimado": "yellow", "Disponível": "green"})], row_height=30, extra_rows=20)
    # referências externas usadas nos COUNTIF (valores copiados dos outros registos — sem ligações entre ficheiros)
    ws = b.sheet("Refs_Outros_Registos", "Cópia de colunas de outros registos usadas nos indicadores (evita ligações externas entre ficheiros).")
    import openpyxl
    folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Registos_SGA_Plasticom"))
    conf, inc = [], []
    try:
        w13 = openpyxl.load_workbook(os.path.join(folder, "SGA-13_Monitorizacao_Medicao_Desempenho.xlsx"), data_only=True)["Analises_Laboratoriais"]
        hdr = [c.value for c in w13[4]]
        k = hdr.index("Conformidade")
        conf = [r[k] for r in w13.iter_rows(min_row=5, values_only=True) if r[0]]
        w7 = openpyxl.load_workbook(os.path.join(folder, "SGA-07_Nao_Conformidades_RNC.xlsx"), data_only=True)["Registo_Incidentes"]
        hdr = [c.value for c in w7[4]]
        k = hdr.index("Data")
        inc = [r[k] for r in w7.iter_rows(min_row=5, values_only=True) if r[0]]
    except Exception:
        pass
    ws["A1"], ws["B1"] = "Conformidade (tbl_analises, RG-SGA-13)", "Data (tbl_incidentes, RG-SGA-07)"
    ws["A1"].font = ws["B1"].font = F_BOLD
    for k, v in enumerate(conf, start=2):
        ws.cell(row=k, column=1, value=v)
    for k, v in enumerate(inc, start=2):
        c = ws.cell(row=k, column=2, value=v)
        c.number_format = "yyyy-mm-dd"
    ws.column_dimensions["A"].width = ws.column_dimensions["B"].width = 34
    b.wb.defined_names["tbl_analises_ref"] = DefinedName("tbl_analises_ref", attr_text=f"'Refs_Outros_Registos'!$A$2:$A${max(2, len(conf) + 1)}")
    b.wb.defined_names["tbl_incidentes_ref"] = DefinedName("tbl_incidentes_ref", attr_text=f"'Refs_Outros_Registos'!$B$2:$B${max(2, len(inc) + 1)}")


def build_matriz(b):
    # (ID, referencial, tema, requisito, evidência, estado, lacuna/ação)
    M = [
        ("ESGM-01", "VSME B2 / ESRS MDR-P", "Transversal", "Políticas ambientais (clima, poluição, água, biodiversidade, recursos)", "POL-SGA rev. 02 (RG-SGA-05 tbl_politica)", "Conforme", ""),
        ("ESGM-02", "ESRS 1 / IRO-1", "Transversal", "Avaliação de materialidade (dupla) dos temas E1–E5", "RG-SGA-17", "Conforme", ""),
        ("ESGM-03", "ESRS E1-1", "Clima", "Plano de transição para a mitigação das alterações climáticas", "PL-SGA-01; tbl_metas_clima; simulador", "Parcial", "Aprovar o plano e as metas na revisão pela gestão; orçamento plurianual"),
        ("ESGM-04", "ESRS E1 IRO-1 / TCFD", "Clima", "Riscos climáticos físicos e de transição (cenários)", "RG-SGA-02 R34, R25; RG-SGA-17 DM-01 a DM-03", "Parcial", "Análise de cenários físicos (RCP 4.5/8.5) para calor e seca"),
        ("ESGM-05", "ESRS E1-4 / SBTi", "Clima", "Metas de redução de GEE com ano-base", "tbl_metas_clima", "Parcial", "Metas propostas; submeter compromisso SBTi para PME"),
        ("ESGM-06", "ESRS E1-5 / GRI 302", "Clima", "Consumo e mix de energia", "tbl_indicadores_esg ESG-E01 a E04", "Conforme", ""),
        ("ESGM-07", "ESRS E1-6 / GRI 305 / ISO 14064-1", "Clima", "Inventário de GEE âmbitos 1, 2 (dois métodos) e 3", "tbl_inventario_gee; PR-SGA-13", "Conforme", "Âmbito 3 estimado: substituir por PCF de fornecedores"),
        ("ESGM-08", "ISO 14064-3", "Clima", "Verificação independente do inventário", "—", "Lacuna", "Verificação limitada por terceira parte antes de publicar"),
        ("ESGM-09", "CDP / clientes", "Produto", "Pegada de carbono por produto", "tbl_pegada_produto", "Parcial", "Estimativa; PCF ISO 14067 verificada para as 5 famílias principais"),
        ("ESGM-10", "ESRS E2-4 / VSME B4", "Poluição", "Emissões para o ar, água e solo", "RG-SGA-13 tbl_analises; ESG-E12, E13", "Conforme", ""),
        ("ESGM-11", "ESRS E2-5", "Poluição", "Substâncias que suscitam preocupação (SVHC) e PFAS", "RG-SGA-21 tbl_quimicos e tbl_declaracoes", "Parcial", "Obter as declarações 'Por confirmar' (PAM-26-34) e substituir SVHC (PAM-26-29, PAM-26-30)"),
        ("ESGM-12", "Reg. (UE) 2025/2365 / OCS", "Poluição", "Prevenção de perdas de granulado de plástico", "RG-SGA-03 AA-003; OBJ-06; RG-SGA-18 ALT-2026-06", "Parcial", "Medir perdas totais (não só as recolhidas)"),
        ("ESGM-13", "ESRS E3-4 / VSME B6", "Água", "Captação, consumo e descarga de água", "tbl_meses (água); ESG-E16, E17", "Parcial", "Avaliar stress hídrico (WRI Aqueduct) e medir a purga"),
        ("ESGM-14", "ESRS E4-5 / VSME B5", "Biodiversidade", "Uso do solo e proximidade a áreas sensíveis", "ESG-E19 a E22; POL-06", "Parcial", "Confirmar com o ICNF a relação com a Rede Natura 2000"),
        ("ESGM-15", "ESRS E5-4 / VSME B7", "Recursos", "Fluxos de entrada de materiais e conteúdo reciclado", "ESG-E23, E24; tbl_dados_ambientais", "Conforme", ""),
        ("ESGM-16", "ESRS E5-5 / VSME B7", "Recursos", "Resíduos por tipo, perigosidade e destino", "RG-SGA-13 tbl_residuos; ESG-E25 a E28", "Conforme", ""),
        ("ESGM-17", "ESRS E5-5 / PPWR", "Recursos", "Reciclabilidade dos produtos", "RG-SGA-20 tbl_recyclass; RG-SGA-05 KPI-18/KPI-20", "Parcial", "Autoavaliação RecyClass feita (113 SKUs); falta certificação e os atos delegados de DfR do PPWR"),
        ("ESGM-18", "Diretiva (UE) 2024/825", "Produto", "Alegações ambientais fundamentadas", "PR-SGA-14; RG-SGA-20 tbl_alegacoes", "Parcial", "Retirar 4 alegações até 27/09/2026 (PAM-26-27)"),
        ("ESGM-19", "GRI 308 / EcoVadis SUP", "Cadeia de valor", "Avaliação ambiental de fornecedores", "RG-SGA-11", "Conforme", ""),
        ("ESGM-20", "EU Taxonomy", "Finanças sustentáveis", "Elegibilidade/alinhamento de atividades (ex.: UPAC, eficiência)", "—", "Lacuna", "Não obrigatório para a Plasticom; útil para financiamento verde"),
        ("ESGM-21", "VSME / CSRD", "Reporte", "Relatório de sustentabilidade (módulo básico VSME)", "tbl_indicadores_esg", "Parcial", "Compilar o relatório VSME anual a partir deste registo"),
    ]
    cols = [col("ID", 8, desc="Identificador.", key="PK"), col("Referencial", 24, desc="Referencial ou regulamento."), col("Tema", 14, desc="Tema."),
            col("Requisito", 46, desc="Requisito."), col("Evidencia", 40, desc="Onde está a evidência."),
            col("Estado", 9, dv="EstadoReqE", desc="Conforme · Parcial · Lacuna."), col("Lacuna_Acao", 44, desc="Lacuna e próxima ação.", req=False),
            col("Pontos", 7, "num", f='=IF(@Estado@="","",IF(@Estado@="Conforme",1,IF(@Estado@="Parcial",0.5,0)))', desc="Para o índice de prontidão ESG-E.")]
    b.add_list("EstadoReqE", ["Conforme", "Parcial", "Lacuna"])
    names = [c["name"] for c in cols if not c["f"]]
    b.table("Matriz_ESG_E", "tbl_matriz_esg", cols, [dict(zip(names, m)) for m in M],
            "Requisitos do pilar Ambiental do ESG (VSME, ESRS E1–E5, GRI, SASB, CDP/EcoVadis, regulamentos UE) → evidência → estado.",
            title="MATRIZ DE REQUISITOS ESG — PILAR AMBIENTAL", subtitle="Índice de prontidão ESG-E = média de Pontos (Conforme 1 · Parcial 0,5 · Lacuna 0)",
            cf=[("Estado", {"Conforme": "green", "Parcial": "orange", "Lacuna": "red"})], row_height=36)


if __name__ == "__main__":
    import sys
    print(build(sys.argv[1]))
