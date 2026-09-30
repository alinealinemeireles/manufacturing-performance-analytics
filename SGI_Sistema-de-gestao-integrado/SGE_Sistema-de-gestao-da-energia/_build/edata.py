"""Dados de energia do SGE da Plasticom.

Fonte única dos consumos mensais de eletricidade (total da fatura e rateio por uso): RG-SGA-13 tbl_dados_ambientais,
gerado por envdata.ambiente() do SGA — o SGE lê exatamente os mesmos valores (mar/2025 – dez/2026), incluindo o efeito
das ações de energia de out–dez/2026 (EF_STANDBY / EF_AR no envdata).
Gasóleo (frota e gerador): mesmos valores do inventário de GEE (RG-SGA-19, build_19_esg_ambiental.inventario()).
Produção, horas de marcha e paragens por máquina: dataset do projeto (datasets/silver/fact_production_processed.csv).

Simulação didática acrescentada pelo SGE (não existia no projeto) — marcada como tal nos registos:
- campanha de medição com analisador portátil por máquina (jun–jul/2026): kW em produção e em espera aquecida;
  calibrada para que a média por processo reproduza os parâmetros KW_* do RG-SGA-13 (a campanha confirma o rateio);
- rateio da eletricidade de cada processo pelas máquinas (kW medido × horas), energia das 4 máquinas novas de 07/2026;
- medição antes/depois dos compressores (jan/2026 antigos vs jun/2026 VSD) com o caudalímetro EQP-04;
- faturas por período tarifário (ponta, cheia, vazio, super vazio), potência tomada e energia reativa.
"""
import os
import calendar
import numpy as np
import pandas as pd
import envdata
from dimse import MAQUINAS, MAQ_NOVAS_2026, PROC_DATASET, MESES, N_LBE

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SILVER = os.path.join(ROOT, "datasets", "silver")
KW = {"INJ": envdata.P["KW_INJ"], "SOP": envdata.P["KW_SOP"], "SER": envdata.P["KW_SER"], "HFS": envdata.P["KW_HFS"]}
MAQ = {m[0]: m for m in MAQUINAS}
T_BASE_CDD = 15.0   # temperatura base dos graus-dia de arrefecimento (a mesma usada no FRIO_TEMP do RG-SGA-13)

_cache = {}


def _amb():
    """envdata.ambiente() do SGA (mar/2025–dez/2026) — fonte única RG-SGA-13, já com o efeito das ações de energia de 2026."""
    if "amb" not in _cache:
        _cache["amb"] = envdata.ambiente()
    return _cache["amb"]


def efeito_acoes():
    """kWh poupados por mês pelas ações de 2026 (valor do modelo do RG-SGA-13 — serve só para validar o M&V do RG-SGE-11)."""
    _amb()
    return {m.to_timestamp().date(): d for m, d in envdata.EFEITO_ACOES.items() if d["Standby"] or d["Ar"]}


def producao_maquinas():
    """Produção, horas de marcha e paragens por máquina e mês (jul/2025 – ago/2026)."""
    if "pm" in _cache:
        return _cache["pm"]
    p = pd.read_csv(os.path.join(SILVER, "fact_production_processed.csv"), low_memory=False,
                    usecols=["Date", "Process", "MachineId", "ProducedQty", "RunTimeHours", "UnplannedDowntimeHours", "SetupTimeHours", "PlannedTimeHours"])
    p["Mes"] = pd.to_datetime(p["Date"].astype(str).str[:7] + "-01").dt.date
    p = p[(p["Mes"] >= MESES[0]) & (p["Mes"] <= MESES[-1])]
    g = p.groupby(["Mes", "MachineId"]).agg(Unid=("ProducedQty", "sum"), Horas_Marcha=("RunTimeHours", "sum"),
                                            Horas_Paragem=("UnplannedDowntimeHours", "sum"), Horas_Setup=("SetupTimeHours", "sum"),
                                            Horas_Planeadas=("PlannedTimeHours", "sum")).reset_index()
    g["Processo"] = g["MachineId"].map(lambda m: MAQ[m][1])
    _cache["pm"] = g
    return g


def campanha():
    """Campanha de medição com analisador portátil PA-01 (simulada): kW por máquina em produção e em espera aquecida.
    O fator de escala por processo faz com que a média ponderada pelas horas reproduza KW_INJ/KW_SOP/KW_SER/KW_HFS do RG-SGA-13."""
    if "camp" in _cache:
        return _cache["camp"]
    rng = np.random.default_rng(50001)
    pm = producao_maquinas()
    h = pm.groupby("MachineId")["Horas_Marcha"].sum()
    rows = []
    for mid, proc, ano, tec in MAQUINAS:
        idade = 2026 - ano
        if proc == "INJ":
            base = tec.split(" (")[0]  # nota entre parênteses (ex.: linha dedicada) não altera a tecnologia
            rel = {"Injetora hidráulica de bomba fixa": 1.38, "Injetora servo-hidráulica": 0.92, "Injetora totalmente elétrica": 0.70}[base]
            esp = {"Injetora hidráulica de bomba fixa": 0.72, "Injetora servo-hidráulica": 0.42, "Injetora totalmente elétrica": 0.22}[base]
        elif proc == "SOP":
            rel = {"ISBM hidráulica": 1.12 + 0.012 * idade, "ISBM híbrida (servo)": 0.98, "ISBM elétrica com recuperação de ar": 0.80}[tec]
            esp = {"ISBM hidráulica": 0.62, "ISBM híbrida (servo)": 0.45, "ISBM elétrica com recuperação de ar": 0.30}[tec]
        elif proc == "SER":
            rel, esp = 1.0, 0.35
        else:
            rel, esp = 1.0, 0.55
        rows.append(dict(ID_Maquina=mid, Processo=proc, Ano_Instalacao=ano, Tecnologia=tec, rel=rel * rng.normal(1, 0.03), Fracao_Espera=round(esp * rng.normal(1, 0.04), 3)))
    c = pd.DataFrame(rows)
    c["h"] = c["ID_Maquina"].map(h).fillna(0)
    for proc, kw in KW.items():
        s = c["Processo"] == proc
        k = kw / np.average(c.loc[s, "rel"], weights=c.loc[s, "h"])
        c.loc[s, "kW_Producao"] = (c.loc[s, "rel"] * k).round(1)
    c["kW_Espera_Aquecida"] = (c["kW_Producao"] * c["Fracao_Espera"]).round(1)
    c["kW_Desligada"] = np.where(c["Processo"].isin(["INJ", "SOP"]), 0.6, 0.2)
    base = pd.Timestamp("2026-06-08")
    c["Data_Medicao"] = [(base + pd.Timedelta(days=int(i // 3) * 2)).date() for i in range(len(c))]
    c["Duracao_h"] = 48
    c["Instrumento"] = "PA-01"
    c["Kg_h_Medido"] = 0.0
    _cache["camp"] = c.drop(columns=["rel", "h"])
    return _cache["camp"]


def energia_maquinas():
    """Rateio mensal da eletricidade de cada processo (RG-SGA-13) pelas máquinas: peso = kW produção × horas de marcha
    + kW espera × (horas de paragem + setup). A soma por processo e mês é igual ao valor do RG-SGA-13."""
    if "em" in _cache:
        return _cache["em"]
    _, _, fact, _ = _amb()
    ene = fact[fact["Variavel"] == "ENE_PROC"].set_index(["Mes", "Processo"])["Valor"]
    pm = producao_maquinas().copy()
    c = campanha().set_index("ID_Maquina")
    pm["kWh_Modelo"] = pm["MachineId"].map(c["kW_Producao"]) * pm["Horas_Marcha"] + pm["MachineId"].map(c["kW_Espera_Aquecida"]) * (pm["Horas_Paragem"] + pm["Horas_Setup"])
    pm["Soma_Proc"] = pm.groupby(["Mes", "Processo"])["kWh_Modelo"].transform("sum")
    pm["kWh_Processo_SGA"] = [ene.get((m, p), np.nan) for m, p in zip(pm["Mes"], pm["Processo"])]
    pm["kWh_Rateado"] = (pm["kWh_Processo_SGA"] * pm["kWh_Modelo"] / pm["Soma_Proc"]).round(0)
    _cache["em"] = pm
    return pm


def diesel():
    """Litros de gasóleo por mês (frota e gerador) — mesmos valores do tbl_inventario_gee do RG-SGA-19."""
    if "dsl" in _cache:
        return _cache["dsl"]
    import build_19_esg_ambiental as g19
    rows = g19.inventario()[0]
    d = pd.DataFrame(rows)
    d = d[d["ID_Fonte"].isin(["S1-01", "S1-02"])].pivot_table(index="Mes", columns="ID_Fonte", values="Dado_Atividade", aggfunc="sum")
    d.index = [pd.Timestamp(x).date().replace(day=1) for x in d.index]
    d = d.rename(columns={"S1-01": "L_Frota", "S1-02": "L_Gerador"})
    _cache["dsl"] = d
    return _cache["dsl"]


def base_mensal():
    """Uma linha por mês: eletricidade total e por uso (RG-SGA-13), produção e horas (dataset / reconstruído),
    temperatura e graus-dia, energia das máquinas novas de 07/2026 (rateio + utilidades), gasóleo."""
    prod, mm, fact, _ = _amb()
    piv = fact[fact["Variavel"] == "ENE_PROC"].pivot_table(index="Mes", columns="Processo", values="Valor", aggfunc="sum")
    tot = fact[fact["Variavel"] == "ENE_TOTAL"].set_index("Mes")["Valor"]
    pr = prod.pivot_table(index="Mes", columns="Processo", values=["Unid", "Horas"], aggfunc="sum")
    fonte = prod.groupby("Mes")["Fonte"].first()
    m = mm.set_index("Mes")
    em = energia_maquinas()
    nov = em[em["MachineId"].isin(MAQ_NOVAS_2026)]
    dsl = diesel()
    rows = []
    for i, mes in enumerate(MESES):
        T = float(m.loc[mes, "Temp_Media_C"])
        dias = calendar.monthrange(mes.year, mes.month)[1]
        nm = nov[nov["Mes"] == mes]
        # mesma regra do RG-SGA-13 (horas de marcha × KW do processo): até haver submedição, é assim que a fatura é repartida
        k_inj_n = float(nm[nm["Processo"] == "INJ"]["Horas_Marcha"].sum()) * KW["INJ"]
        k_sop_n = float(nm[nm["Processo"] == "SOP"]["Horas_Marcha"].sum()) * KW["SOP"]
        proc_tot = sum(float(piv.loc[mes, p]) for p in ("INJ", "SOP", "SER", "HFS"))
        injsop = float(piv.loc[mes, "INJ"] + piv.loc[mes, "SOP"])
        k_ut_n = float(piv.loc[mes, "UTL-AR"]) * (k_inj_n + k_sop_n) / proc_tot + float(piv.loc[mes, "UTL-FRIO"]) * (k_inj_n + k_sop_n) / injsop
        rows.append(dict(
            Mes=mes, Periodo="Referência (LBE)" if i < N_LBE else "Reporte",
            Qualidade_Producao="Dataset" if str(fonte.get(mes, "")).startswith("Dataset") else "Reconstruído (pré-dataset)",
            Fonte_Energia="RG-SGA-13 (fatura)",
            Dias_Calendario=dias, Dias_Uteis=int(m.loc[mes, "Dias_Uteis"]), Temp_Media_C=T,
            CDD_15=round(max(0.0, T - T_BASE_CDD) * dias, 1),
            kWh_Total=round(float(tot.loc[mes])),
            **{f"kWh_{p.replace('-', '_')}": round(float(piv.loc[mes, p])) for p in ("SOP", "INJ", "UTL-AR", "UTL-FRIO", "GER", "SER", "HFS")},
            Unid_INJ=int(pr.loc[mes, ("Unid", "INJ")]), Unid_SOP=int(pr.loc[mes, ("Unid", "SOP")]),
            Unid_SER=int(pr.loc[mes, ("Unid", "SER")]), Unid_HFS=int(pr.loc[mes, ("Unid", "HFS")]),
            Horas_INJ=round(float(pr.loc[mes, ("Horas", "INJ")]), 1), Horas_SOP=round(float(pr.loc[mes, ("Horas", "SOP")]), 1),
            Horas_SER=round(float(pr.loc[mes, ("Horas", "SER")]), 1), Horas_HFS=round(float(pr.loc[mes, ("Horas", "HFS")]), 1),
            Unid_Maquinas_Novas=int(nm["Unid"].sum()), kWh_Maquinas_Novas=round(k_inj_n + k_sop_n + k_ut_n),
            L_Gasoleo_Frota=round(float(dsl.loc[mes, "L_Frota"]), 1) if mes in dsl.index else None,
            L_Gasoleo_Gerador=round(float(dsl.loc[mes, "L_Gerador"]), 1) if mes in dsl.index else None,
        ))
    return pd.DataFrame(rows)


def compressores():
    """M&V dos compressores (ALT-2026-01): semana de registo antes (jan/2026, compressores antigos carga/vazio) e depois
    (jun/2026, compressores de velocidade variável), com o analisador PA-01 e o caudalímetro EQP-04 (simulado)."""
    rng = np.random.default_rng(1102)
    rows = []
    for fase, ini, spc, pres, fuga in (("Antes (CMP antigos, carga/vazio)", pd.Timestamp("2026-01-12"), 0.131, 7.6, 0.27),
                                       ("Depois (CMP VSD)", pd.Timestamp("2026-06-15"), 0.112, 7.4, 0.25),
                                       ("Depois (VSD + fugas + 6,8 bar)", pd.Timestamp("2026-12-07"), 0.106, 6.85, 0.14)):
        for d in range(7):
            dia = (ini + pd.Timedelta(days=d)).date()
            fim_semana = d >= 5
            nm3 = (24000 if not fim_semana else 10000) * (0.90 if fase.endswith("bar)") else 1.0) * rng.normal(1, 0.03)
            if fim_semana and d == 6:
                nm3 = 7600 * rng.normal(1, 0.02)
            s = spc * (1.10 if fim_semana and fase.startswith("Antes") else 1.0) * rng.normal(1, 0.015)
            rows.append(dict(Fase=fase, Data=dia, Dia_Semana=["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][d], Producao="Não" if fim_semana else "Sim",
                             Nm3_Dia=round(nm3), kWh_Dia=round(nm3 * s), Pressao_Media_bar=round(pres * rng.normal(1, 0.005), 2),
                             Fuga_Teste_Vazio=round(fuga * rng.normal(1, 0.03), 3) if d == 6 else None))
    return pd.DataFrame(rows)


# preços simulados (€/kWh energia + redes) por período horário e ano; potência (€/kW.dia)
PRECOS = {2025: dict(Ponta=0.1790, Cheia=0.1380, Vazio=0.1060, Super_Vazio=0.0960, Pot_Ponta=0.3150, Pot_Contratada=0.0310),
          2026: dict(Ponta=0.1850, Cheia=0.1420, Vazio=0.1090, Super_Vazio=0.0985, Pot_Ponta=0.3220, Pot_Contratada=0.0320)}
POT_CONTRATADA = 1400   # kW (contrato de média tensão)


def faturas():
    """Faturas mensais de eletricidade por período tarifário (simuladas; total de kWh = RG-SGA-13)."""
    rng = np.random.default_rng(8030)
    b = base_mensal()
    rows = []
    for _, r in b.iterrows():
        mes = r["Mes"]
        kwh = r["kWh_Total"]
        sh = np.array([0.160, 0.420, 0.280, 0.140]) * rng.normal(1, [0.03, 0.02, 0.02, 0.03])
        sh = sh / sh.sum()
        horas = r["Dias_Calendario"] * 24
        media_kw = kwh / horas
        pico = media_kw * (1.30 + 0.04 * rng.standard_normal())
        pot_ponta = pico * 0.93 * rng.normal(1, 0.015)
        rows.append(dict(ID_Fatura=f"FT-{mes:%Y%m}", Mes=mes, kWh_Ponta=round(kwh * sh[0]), kWh_Cheia=round(kwh * sh[1]), kWh_Vazio=round(kwh * sh[2]),
                         kWh_Super_Vazio=round(kwh * sh[3]), kW_Potencia_Horas_Ponta=round(pot_ponta), kW_Potencia_Tomada_Max=round(pico),
                         kW_Potencia_Contratada=POT_CONTRATADA, kvarh_Reativa_Faturada=round(kwh * 0.012 * rng.uniform(0.5, 1.5))))
    return pd.DataFrame(rows)


def preco_medio(ini="2026-01-01", fim="2026-12-01"):
    """€/kWh médio (energia + redes, sem potência) das faturas simuladas nos 12 meses indicados."""
    f = faturas()
    f = f[(f["Mes"] >= pd.Timestamp(ini).date()) & (f["Mes"] <= pd.Timestamp(fim).date())]
    cust = kwh = 0.0
    for _, r in f.iterrows():
        p = PRECOS[r["Mes"].year]
        for per in ("Ponta", "Cheia", "Vazio", "Super_Vazio"):
            cust += r[f"kWh_{per}"] * p[per]
            kwh += r[f"kWh_{per}"]
    return round(cust / kwh, 4)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    b = base_mensal()
    print(b.drop(columns=["Qualidade_Producao"]).to_string())
    print(campanha().to_string())
    print(compressores().groupby("Fase")[["Nm3_Dia", "kWh_Dia"]].sum())
    print(faturas().head().to_string())
