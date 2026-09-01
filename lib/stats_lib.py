"""
stats_lib.py

Python replacements for the statistical routines the project's earlier, separate
R notebook (`qcc`, `SixSigma`) used to provide -- written so the single consolidated
notebook needs only one kernel. Nothing here is a re-derivation of new statistics:
X-bar/R control limits and Cp/Cpk/Cpm already exist in `etl_lib.py` (reused, not
duplicated); this module adds the pieces that were R-only before: a reusable X-bar/R
plot, the Western Electric run rules, and small helpers for a Pareto chart and a
two-sample proportion test presented the way this project's narrative expects.

Sections:
1. X-bar/R control chart plotting
2. Western Electric run rules (zone tests beyond simple 3-sigma)
3. Pareto chart
4. Two-sample proportion test (wraps statsmodels, adds the plain-language framing)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest

# ---------------------------------------------------------------------------
# 1. X-BAR/R CONTROL CHART PLOTTING
# ---------------------------------------------------------------------------

def plot_xbar_chart(ax, df: pd.DataFrame, value_col: str, cl_col: str, ucl_col: str, lcl_col: str,
                     title: str, flag_col: str | None = None) -> None:
    """Plots one X-bar (or any subgroup-average) control chart on a given Matplotlib
    axis -- center line, 3-sigma limits, and (optionally) points flagged by an
    out-of-control test highlighted in red. Equivalent to what `qcc::qcc(type="xbar")`
    drew in the retired R notebook, built directly on control limits this project's
    own Python cleaning pipeline already computes (`etl_lib.compute_control_limits`)."""
    x = range(len(df))
    ax.plot(x, df[value_col], color="#444444", lw=1, marker=".", markersize=3, label=value_col)
    ax.axhline(df[cl_col].iloc[0], color="green", ls="-", lw=1, label="Linha central")
    ax.axhline(df[ucl_col].iloc[0], color="firebrick", ls="--", lw=1, label="LSC/LIC (3σ)")
    ax.axhline(df[lcl_col].iloc[0], color="firebrick", ls="--", lw=1)
    if flag_col is not None:
        flagged = df[df[flag_col]]
        ax.scatter(flagged.index if not isinstance(df.index, pd.RangeIndex) else [x[i] for i in flagged.index],
                    flagged[value_col], color="firebrick", s=45, zorder=5, marker="x", label="Fora de controle")
    ax.set_title(title)


# ---------------------------------------------------------------------------
# 2. WESTERN ELECTRIC RUN RULES
# ---------------------------------------------------------------------------

def apply_western_electric_rules(df: pd.DataFrame, value_col: str, cl_col: str,
                                  ucl_col: str, lcl_col: str) -> pd.DataFrame:
    """The four classic Western Electric zone tests, applied on top of the simple
    3-sigma limits already present in `df`:
    - Rule 1: 1 point beyond 3-sigma (equivalent to the simple test).
    - Rule 2: 2 of 3 consecutive points beyond 2-sigma, same side.
    - Rule 3: 4 of 5 consecutive points beyond 1-sigma, same side.
    - Rule 4: 8 consecutive points on one side of the center line.
    Zone boundaries are derived from the existing 3-sigma limits (sigma = (UCL-CL)/3),
    not re-estimated -- this keeps the run rules consistent with whatever control
    limits the rest of the notebook already trusts."""
    df = df.copy().reset_index(drop=True)
    n = len(df)
    sigma = (df[ucl_col] - df[cl_col]) / 3.0
    zone1_upper, zone1_lower = df[cl_col] + sigma, df[cl_col] - sigma
    zone2_upper, zone2_lower = df[cl_col] + 2 * sigma, df[cl_col] - 2 * sigma

    beyond_1s_upper = (df[value_col] > zone1_upper).to_numpy()
    beyond_1s_lower = (df[value_col] < zone1_lower).to_numpy()
    beyond_2s_upper = (df[value_col] > zone2_upper).to_numpy()
    beyond_2s_lower = (df[value_col] < zone2_lower).to_numpy()
    beyond_3s = ((df[value_col] > df[ucl_col]) | (df[value_col] < df[lcl_col])).to_numpy()
    side = np.where(df[value_col] >= df[cl_col], 1, -1)

    rule1, rule2, rule3, rule4 = beyond_3s.copy(), np.zeros(n, bool), np.zeros(n, bool), np.zeros(n, bool)
    for i in range(n):
        # Rules 2/3 only require that the points counted toward the "k of n beyond
        # sigma" test share a side -- NOT that every point in the window does (the
        # window's other points may sit anywhere, even beyond the threshold on the
        # opposite side). Checking side[w] == side[i] for the whole window was the
        # audited bug: it under-counted real signals (e.g. IM-001 Rule 2: 134 -> 298).
        if i >= 2:
            w = slice(i - 2, i + 1)
            if beyond_2s_upper[w].sum() >= 2 or beyond_2s_lower[w].sum() >= 2:
                rule2[i] = True
        if i >= 4:
            w = slice(i - 4, i + 1)
            if beyond_1s_upper[w].sum() >= 4 or beyond_1s_lower[w].sum() >= 4:
                rule3[i] = True
        if i >= 7:
            w = slice(i - 7, i + 1)
            if np.all(side[w] == side[i]):
                rule4[i] = True

    df["Rule1_Beyond3Sigma"] = rule1
    df["Rule2_2of3Beyond2Sigma"] = rule2
    df["Rule3_4of5Beyond1Sigma"] = rule3
    df["Rule4_8ConsecutiveSameSide"] = rule4
    df["AnyRuleFlag"] = rule1 | rule2 | rule3 | rule4
    df["AnyRunRuleOnly"] = (rule2 | rule3 | rule4) & ~rule1
    return df


# ---------------------------------------------------------------------------
# 3. PARETO CHART
# ---------------------------------------------------------------------------

def pareto_chart(series: pd.Series, title: str, ax, ylabel: str = "Ocorrências") -> pd.Series:
    """Classic Pareto: bars sorted descending, cumulative-% line on a second axis,
    an 80% reference line. Returns the sorted series (with its cumulative %) so the
    caller can print/inspect the same numbers shown on the chart."""
    series = series.sort_values(ascending=False)
    cum_pct = series.cumsum() / series.sum() * 100
    ax.bar(range(len(series)), series.values, color="#2980b9")
    ax2 = ax.twinx()
    ax2.plot(range(len(series)), cum_pct.values, color="black", marker="o", markersize=4)
    ax2.axhline(80, color="firebrick", linestyle="--", linewidth=1)
    ax2.set_ylim(0, 105)
    ax.set_xticks(range(len(series)))
    ax.set_xticklabels(series.index, rotation=60, ha="right", fontsize=8)
    ax.set_ylabel(ylabel)
    ax2.set_ylabel("% acumulado")
    ax.set_title(title)
    return pd.DataFrame({"Valor": series, "PctAcumulado": cum_pct})


# ---------------------------------------------------------------------------
# 4. TWO-SAMPLE PROPORTION TEST
# ---------------------------------------------------------------------------

def two_sample_proportion_test(count1: int, nobs1: int, count2: int, nobs2: int) -> dict:
    """Wraps statsmodels' proportions_ztest (the Python equivalent of R's
    prop.test for two independent samples) and returns a small, print-ready dict --
    the rigorous version of "eyeballing a bar chart" this project already commits to
    everywhere else."""
    z_stat, p_value = proportions_ztest([count1, count2], [nobs1, nobs2])
    return {
        "rate1": count1 / nobs1, "rate2": count2 / nobs2,
        "z_stat": float(z_stat), "p_value": float(p_value),
        "significant_at_0_05": bool(p_value < 0.05),
    }
