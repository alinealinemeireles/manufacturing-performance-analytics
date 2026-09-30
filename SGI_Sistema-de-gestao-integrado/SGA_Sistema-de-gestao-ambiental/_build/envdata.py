"""Gera a base de dados ambiental mensal da Plasticom (mar/2025 – dez/2026, 22 meses; ano de reporte = 2026).

Fonte operacional: datasets/silver/fact_production_processed.csv (produção, rejeições, horas de marcha)
e fact_downtime_processed.csv (mudanças de molde). Meses mar–jun/2025 são anteriores ao dataset de
produção e são reconstruídos a partir das faturas (estimativa, marcados como tal).
Os fatores (kW médios, m³/MWh, g/peça...) estão em PARAMS e são publicados no ficheiro RG-SGA-13.
"""
import os
import numpy as np
import pandas as pd

# Raiz do projeto: _build -> SGA_Sistema-de-gestao-ambiental -> SGI_Sistema-de-gestao-integrado -> raiz.
# (Eram dois níveis quando a pasta do SGA ficava na raiz; depois de movida para dentro do SGI o caminho
# apontava para SGI_Sistema-de-gestao-integrado/datasets, que não existe, e o SGA deixou de regenerar.)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SILVER = os.path.join(ROOT, "datasets", "silver")
MESES = pd.period_range("2025-03", "2026-12", freq="M")   # fecho do ano de 2026 (portefólio apresentado em 2027)

PARAMS = [
    # código, valor, unidade, descrição
    ("KW_INJ", 45.0, "kW", "Potência média absorvida por máquina de injeção em marcha"),
    ("KW_SOP", 55.0, "kW", "Potência média absorvida por máquina ISBM em marcha"),
    ("KW_SER", 18.0, "kW", "Potência média por máquina de serigrafia (inclui cura UV/IR)"),
    ("KW_HFS", 9.0, "kW", "Potência média por máquina de hot foil"),
    ("AR_FRAC", 0.19, "fração", "Energia dos compressores de ar em proporção da energia dos processos"),
    ("FRIO_FRAC", 0.10, "fração", "Energia do chiller/torre em proporção da energia de injeção + sopro, a 15 °C"),
    ("FRIO_TEMP", 0.05, "1/°C", "Aumento relativo da energia de arrefecimento por °C acima de 15 °C"),
    ("BASE_KWH", 42000, "kWh/mês", "Consumo base (iluminação, escritórios, armazéns, AVAC a 18 °C)"),
    ("AGUA_TORRE", 1.45, "m³/MWh", "Água de reposição da torre por MWh de injeção + sopro, a 15 °C"),
    ("AGUA_TEMP", 0.045, "1/°C", "Aumento relativo da reposição da torre por °C acima de 15 °C"),
    ("AGUA_SAN", 150, "m³/mês", "Água sanitária e de limpeza (≈ 150 trabalhadores)"),
    ("G_FRASCO", 22.0, "g/un", "Massa média de um frasco soprado"),
    ("G_TAMPA", 6.0, "g/un", "Massa média de uma tampa injetada"),
    ("KG_SETUP_SOP", 3.0, "kg/troca", "Purga e peças de arranque por mudança de molde no sopro"),
    ("KG_SETUP_INJ", 1.5, "kg/troca", "Purga e peças de arranque por mudança de molde na injeção"),
    ("REGRIND", 0.48, "fração", "Fração do scrap limpo de injeção/sopro reintegrada por moagem"),
    ("PCR_SHARE", 0.12, "fração", "Fração de polímero reciclado (PCR/rPET) no consumo total"),
    ("TINTA_G", 0.24, "kg/1.000 un", "Consumo de tinta por 1.000 peças serigrafadas"),
    ("SOLV_G", 0.16, "kg/1.000 un", "Solvente de limpeza de ecrãs por 1.000 peças serigrafadas (referência)"),
    ("FOIL_G", 1.9, "kg/1.000 un", "Consumo de foil por 1.000 peças decoradas por hot foil"),
    ("FOIL_RES", 0.72, "kg/1.000 un", "Resíduo de foil (filme de suporte) por 1.000 peças"),
    ("FE_ELET", 0.110, "kgCO2e/kWh", "Fator de emissão da eletricidade da rede (location-based, Portugal). CÓPIA do FE-01 do RG-SGA-19 (mestre dos fatores) — alterar lá e regenerar"),
    ("REN_SHARE", 0.55, "fração", "Quota renovável do mix do comercializador (rótulo de energia)"),
    ("GWP_R410A", 2088, "kgCO2e/kg", "GWP do R410A (chiller CH-01). CÓPIA do FE-05 do RG-SGA-19 (mestre dos fatores)"),
]
P = {k: v for k, v, _, _ in PARAMS}

# Temperatura média mensal (°C) — aproximação às normais de Leiria/Marinha Grande + anomalia do ano
T_NORM = {1: 10.2, 2: 11.0, 3: 12.8, 4: 14.3, 5: 16.6, 6: 19.6, 7: 21.4, 8: 21.8, 9: 20.4, 10: 17.4, 11: 13.6, 12: 11.2}
T_ANOM = {"2025-03": 0.4, "2025-04": 0.9, "2025-05": 0.2, "2025-06": 1.6, "2025-07": 0.8, "2025-08": 1.3, "2025-09": 0.5,
          "2025-10": 0.7, "2025-11": -0.3, "2025-12": 0.2, "2026-01": -0.6, "2026-02": 0.9, "2026-03": 0.3, "2026-04": 0.6,
          "2026-05": 1.0, "2026-06": 1.7, "2026-07": 1.9, "2026-08": 2.2,
          "2026-09": 1.2, "2026-10": 0.8, "2026-11": 0.2, "2026-12": -0.1}
DIAS_UTEIS = {"2025-03": 21, "2025-04": 20, "2025-05": 21, "2025-06": 19, "2025-07": 23, "2025-08": 20, "2025-09": 22,
              "2025-10": 22, "2025-11": 19, "2025-12": 20, "2026-01": 21, "2026-02": 20, "2026-03": 22, "2026-04": 20,
              "2026-05": 20, "2026-06": 20, "2026-07": 23, "2026-08": 21,
              "2026-09": 22, "2026-10": 21, "2026-11": 21, "2026-12": 20}   # feriados: 5/10, 1/12, 8/12, 25/12

PROC_MAP = {"Injection Molding": "INJ", "Blow Molding": "SOP", "Screen Printing": "SER", "Hot Foil Stamping": "HFS"}
# desvio simulado para a Atividade 5.2: solvente de limpeza na serigrafia ≈ +15% em jun–ago/2026 com produção estável
SOLV_DESVIO = {"2026-06": 1.10, "2026-07": 1.13, "2026-08": 1.14, "2026-09": 1.10, "2026-10": 1.04}   # desvio corrigido a partir de nov/2026 (ação do PAM)
# efeito das ações de energia do SGE no fecho de 2026 (fração poupada): standby nas pausas (PA-E-03, desde 05/10) nos processos INJ/SOP;
# programa de fugas (PA-E-02, desde 10/2026) e pressão de 6,8 bar (desde 16/11) no ar comprimido. Registado no RG-SGE-11 (M&V).
EF_STANDBY = {"2026-10": 0.03 * 0.55, "2026-11": 0.03 * 0.85, "2026-12": 0.03 * 0.95}
EF_AR = {"2026-10": 0.04, "2026-11": 0.10 + 0.02, "2026-12": 0.15 + 0.04}
EFEITO_ACOES = {}   # preenchido por ambiente(): {Period: {"Standby": kWh, "Ar": kWh}}


def producao():
    p = pd.read_csv(os.path.join(SILVER, "fact_production_processed.csv"), low_memory=False,
                    usecols=["Date", "Process", "ProducedQty", "RejectedQty", "RunTimeHours"])
    p["Mes"] = pd.PeriodIndex(p["Date"].astype(str).str[:7], freq="M")
    p["Processo"] = p["Process"].map(PROC_MAP)
    g = p.groupby(["Mes", "Processo"]).agg(Unid=("ProducedQty", "sum"), Rej=("RejectedQty", "sum"), Horas=("RunTimeHours", "sum")).reset_index()
    d = pd.read_csv(os.path.join(SILVER, "fact_downtime_processed.csv"), low_memory=False,
                    usecols=["Date", "Process", "StoppageReason"])
    d = d[d["StoppageReason"].astype(str).str.startswith("Mold Change / Setup - Internal: New Mold Mounting")]
    d["Mes"] = pd.PeriodIndex(d["Date"].astype(str).str[:7], freq="M")
    d["Processo"] = d["Process"].map(PROC_MAP)
    s = d.groupby(["Mes", "Processo"]).size().rename("Setups").reset_index()
    g = g.merge(s, on=["Mes", "Processo"], how="left").fillna({"Setups": 0})
    g["Fonte"] = "Dataset de produção (silver)"
    # meses anteriores ao dataset: média jul–dez/2025 com variação estimada
    base = g[(g["Mes"] >= pd.Period("2025-07", "M")) & (g["Mes"] <= pd.Period("2025-12", "M"))].groupby("Processo")[["Unid", "Rej", "Horas", "Setups"]].mean()
    rng = np.random.default_rng(14001)
    extra = []
    for m in MESES[MESES < pd.Period("2025-07", "M")]:
        f = DIAS_UTEIS[str(m)] / 21.5
        for proc, row in base.iterrows():
            k = f * rng.normal(1.0, 0.03)
            extra.append(dict(Mes=m, Processo=proc, Unid=round(row.Unid * k), Rej=round(row.Rej * k * rng.normal(1, 0.04)),
                              Horas=round(row.Horas * k, 1), Setups=round(row.Setups * k), Fonte="Reconstruído (pré-dataset, faturas e registos de turno)"))
    g = pd.concat([pd.DataFrame(extra), g], ignore_index=True)
    g = g[g["Mes"].isin(MESES)].sort_values(["Mes", "Processo"]).reset_index(drop=True)
    return g


def meses():
    rows = []
    for m in MESES:
        k = str(m)
        rows.append(dict(Mes=m.to_timestamp().date(), Ano=m.year, Mes_Num=m.month, Trimestre=f"{m.year}-T{(m.month - 1) // 3 + 1}",
                         Temp_Media_C=round(T_NORM[m.month] + T_ANOM[k], 1), Dias_Uteis=DIAS_UTEIS[k],
                         Periodo_Dataset="Pré-dataset" if m < pd.Period("2025-07", "M") else "Dataset de produção"))
    return pd.DataFrame(rows)


def ambiente():
    """Devolve (producao, meses, fact_long, residuos)."""
    rng = np.random.default_rng(2026)
    prod = producao()
    mm = meses().set_index(pd.PeriodIndex([pd.Period(str(x)[:7], "M") for x in meses()["Mes"]]))
    rows, res = [], []

    def add(m, proc, var, desc, val, unit, fonte, qual):
        rows.append(dict(Mes=m.to_timestamp().date(), Processo=proc, Variavel=var, Descricao=desc, Valor=round(float(val), 2),
                         Unidade=unit, Fonte=fonte, Qualidade_Dado=qual))

    for m in MESES:
        T = mm.loc[m, "Temp_Media_C"]
        pm = prod[prod["Mes"] == m].set_index("Processo")
        nz = lambda s=0.02: rng.normal(1, s)
        kwh = {}
        for proc, kw in (("INJ", P["KW_INJ"]), ("SOP", P["KW_SOP"]), ("SER", P["KW_SER"]), ("HFS", P["KW_HFS"])):
            kwh[proc] = pm.loc[proc, "Horas"] * kw * nz()
        kwh["UTL-AR"] = P["AR_FRAC"] * sum(kwh.values()) * nz()
        kwh["UTL-FRIO"] = (kwh["INJ"] + kwh["SOP"]) * P["FRIO_FRAC"] * (1 + P["FRIO_TEMP"] * (T - 15)) * nz()
        kwh["GER"] = (P["BASE_KWH"] + 900 * abs(T - 18)) * nz(0.03)
        sb, ar = EF_STANDBY.get(str(m), 0.0), EF_AR.get(str(m), 0.0)
        EFEITO_ACOES[m] = dict(Standby=(kwh["INJ"] + kwh["SOP"]) * sb, Ar=kwh["UTL-AR"] * ar)
        kwh["INJ"] *= 1 - sb
        kwh["SOP"] *= 1 - sb
        kwh["UTL-AR"] *= 1 - ar
        total = sum(kwh.values())
        add(m, "GER", "ENE_TOTAL", "Eletricidade total (fatura)", total, "kWh", "Fatura do comercializador", "Medido")
        for proc, v in kwh.items():
            add(m, proc, "ENE_PROC", "Eletricidade por processo/uso (rateio por horas de marcha)", v, "kWh", "Rateio por horas de marcha", "Estimado")
        torre = (kwh["INJ"] + kwh["SOP"]) / 1000 * P["AGUA_TORRE"] * (1 + P["AGUA_TEMP"] * (T - 15)) * nz(0.03)
        san = P["AGUA_SAN"] * mm.loc[m, "Dias_Uteis"] / 21 * nz(0.05)
        add(m, "GER", "AGUA_TOTAL", "Água de rede total (fatura)", torre + san, "m³", "Fatura da entidade gestora", "Medido")
        add(m, "UTL-FRIO", "AGUA_USO", "Água de reposição da torre de arrefecimento (estimativa)", torre, "m³", "Balanço (fatura - sanitária)", "Estimado")
        add(m, "GER", "AGUA_USO", "Água sanitária e limpezas (estimativa)", san, "m³", "Estimativa por n.º de trabalhadores", "Estimado")
        # produção e scrap
        scrap = {}
        scrap["SOP"] = (pm.loc["SOP", "Rej"] * P["G_FRASCO"] + pm.loc["SOP", "Setups"] * P["KG_SETUP_SOP"] * 1000) / 1000 * nz(0.04)
        scrap["INJ"] = (pm.loc["INJ", "Rej"] * P["G_TAMPA"] + pm.loc["INJ", "Setups"] * P["KG_SETUP_INJ"] * 1000) / 1000 * nz(0.04)
        scrap["SER"] = pm.loc["SER", "Rej"] * P["G_FRASCO"] / 1000 * nz(0.04)
        scrap["HFS"] = pm.loc["HFS", "Rej"] * P["G_FRASCO"] / 1000 * nz(0.04)
        for proc, v in scrap.items():
            add(m, proc, "SCRAP_KG", "Scrap plástico gerado (rejeitados + purgas de arranque)", v, "kg", "Pesagem na balança da área", "Medido")
        regrind = (scrap["SOP"] + scrap["INJ"]) * P["REGRIND"] * nz(0.05)
        add(m, "MOA", "REGRIND_KG", "Scrap limpo moído e reintegrado no processo", regrind, "kg", "Pesagem nos moinhos", "Medido")
        good_mass = (pm.loc["SOP", "Unid"] * P["G_FRASCO"] + pm.loc["INJ", "Unid"] * P["G_TAMPA"]) / 1000
        polimero = good_mass + scrap["SOP"] + scrap["INJ"] - regrind
        add(m, "REC", "POLIMERO_KG", "Polímero consumido (virgem + reciclado)", polimero * nz(0.01), "kg", "Inventário de matérias-primas", "Medido")
        add(m, "REC", "PCR_KG", "Polímero reciclado (PCR/rPET) consumido", polimero * P["PCR_SHARE"] * nz(0.06), "kg", "Inventário de matérias-primas", "Medido")
        ser_u, hfs_u = pm.loc["SER", "Unid"], pm.loc["HFS", "Unid"]
        add(m, "SER", "TINTA_KG", "Tinta de serigrafia consumida", ser_u / 1000 * P["TINTA_G"] * nz(0.04), "kg", "Inventário (compras - stock)", "Medido")
        solv = ser_u / 1000 * P["SOLV_G"] * SOLV_DESVIO.get(str(m), 1.0) * nz(0.025)
        add(m, "SER", "SOLVENTE_KG", "Solvente de limpeza de ecrãs consumido", solv, "kg", "Inventário (compras - stock)", "Medido")
        add(m, "HFS", "FOIL_KG", "Foil consumido", hfs_u / 1000 * P["FOIL_G"] * nz(0.03), "kg", "Inventário", "Medido")
        pel = (9 if m < pd.Period("2026-06", "M") else 16 if m < pd.Period("2026-10", "M") else 11) * nz(0.25)
        add(m, "REC", "GRANULADO_KG", "Granulado recolhido nos pontos de contenção / varrimento", pel, "kg", "Pesagem", "Medido")
        # resíduos por código LER
        sold = scrap["SOP"] + scrap["INJ"] - regrind + scrap["SER"] + scrap["HFS"]
        wl = [
            ("07 02 13", "Resíduos de plásticos (scrap não reintegrado)", "Não", sold, "R3", "OGR-01 Recicladora de plásticos"),
            ("15 01 01", "Embalagens de papel e cartão", "Não", 3400 * nz(0.08), "R3", "OGR-02 Gestor de papel/cartão"),
            ("15 01 02", "Embalagens de plástico (filme, big bags, sacos)", "Não", 1750 * nz(0.08), "R3", "OGR-01 Recicladora de plásticos"),
            ("15 01 03", "Embalagens de madeira (paletes)", "Não", 1150 * nz(0.12), "R3", "OGR-03 Recuperador de paletes"),
            ("07 02 13", "Resíduo de foil (filme de suporte)", "Não", hfs_u / 1000 * P["FOIL_RES"] * nz(0.05), "R13", "OGR-01 Recicladora de plásticos"),
            ("20 03 01", "Misturas de resíduos urbanos (indiferenciados)", "Não", 2150 * nz(0.07), "D1", "OGR-04 Sistema municipal"),
            ("17 04 05", "Ferro e aço (sucata)", "Não", 280 * nz(0.35), "R4", "OGR-05 Sucateiro licenciado"),
            ("08 03 12*", "Resíduos de tintas de impressão com substâncias perigosas", "Sim", ser_u / 1000 * 0.07 * nz(0.1), "R13", "OGR-06 Operador de resíduos perigosos"),
            ("15 01 10*", "Embalagens contaminadas por substâncias perigosas", "Sim", 38 * nz(0.12), "R13", "OGR-06 Operador de resíduos perigosos"),
            ("15 02 02*", "Absorventes e panos contaminados", "Sim", solv * 0.55 * nz(0.1) + 12, "D15", "OGR-06 Operador de resíduos perigosos"),
            ("13 02 05*", "Óleos minerais de motores e lubrificação usados", "Sim", (190 if m.month in (3, 6, 9, 12) else 12) * nz(0.1), "R13", "OGR-07 Regenerador de óleos"),
            ("20 01 21*", "Lâmpadas fluorescentes", "Sim", (6 if m.month in (4, 10) else 0) * nz(0.1), "R13", "OGR-06 Operador de resíduos perigosos"),
        ]
        for ler, desc, perig, kg, op, ogr in wl:
            res.append(dict(Mes=m.to_timestamp().date(), Codigo_LER=ler, Descricao=desc, Perigoso=perig, Quantidade_kg=round(max(kg, 0), 1),
                            Operacao_Destino=op, Operador=ogr))
    # incidente: fuga de R410A no chiller em nov/2025
    add(pd.Period("2025-11", "M"), "UTL-FRIO", "FGAS_KG", "Fuga de gás fluorado R410A (reposição após fuga)", 3.2, "kg", "Relatório do técnico certificado", "Medido")
    fact = pd.DataFrame(rows)
    prod_out = prod.copy()
    prod_out["Mes"] = prod_out["Mes"].dt.to_timestamp().dt.date
    return prod_out, meses(), fact, pd.DataFrame(res)


def anual(fact, res, prod, inicio="2026-01", fim="2026-12"):
    """Totais do ano civil de 2026 (12 meses fechados) (usados como magnitude nos aspetos e no EMAS)."""
    a, b = pd.Period(inicio, "M").to_timestamp().date(), pd.Period(fim, "M").to_timestamp().date()
    f = fact[(fact.Mes >= a) & (fact.Mes <= b)]
    r = res[(res.Mes >= a) & (res.Mes <= b)]
    p = prod[(prod.Mes >= a) & (prod.Mes <= b)]
    out = {}
    out["ene_total_kwh"] = f[f.Variavel == "ENE_TOTAL"].Valor.sum()
    for proc in ("INJ", "SOP", "SER", "HFS", "UTL-AR", "UTL-FRIO", "GER"):
        out[f"ene_{proc}"] = f[(f.Variavel == "ENE_PROC") & (f.Processo == proc)].Valor.sum()
    out["agua_total"] = f[f.Variavel == "AGUA_TOTAL"].Valor.sum()
    out["agua_torre"] = f[(f.Variavel == "AGUA_USO") & (f.Processo == "UTL-FRIO")].Valor.sum()
    out["agua_san"] = f[(f.Variavel == "AGUA_USO") & (f.Processo == "GER")].Valor.sum()
    for v in ("SCRAP_KG", "REGRIND_KG", "POLIMERO_KG", "PCR_KG", "TINTA_KG", "SOLVENTE_KG", "FOIL_KG", "GRANULADO_KG"):
        out[v.lower()] = f[f.Variavel == v].Valor.sum()
    out["res_total"] = r.Quantidade_kg.sum()
    out["res_perig"] = r[r.Perigoso == "Sim"].Quantidade_kg.sum()
    out["res_valoriz"] = r[r.Operacao_Destino.str.startswith("R")].Quantidade_kg.sum()
    out["unid_primarias"] = p[p.Processo.isin(["INJ", "SOP"])].Unid.sum()
    out["unid_ser"] = p[p.Processo == "SER"].Unid.sum()
    return out


if __name__ == "__main__":
    prod, mm, fact, res = ambiente()
    print(prod.head(), mm.head(), fact.shape, res.shape, sep="\n")
    a = anual(fact, res, prod)
    for k, v in a.items():
        print(f"{k:16s} {v:,.0f}")
