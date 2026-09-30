"""
data_quality.py

Executes the data contract (`contracts/data_contract.yaml`) against the silver layer and
the engineering dimensions, and turns the result into two things:

1. A **Data Quality Scorecard** by table and by DAMA dimension (completeness, uniqueness,
   validity, consistency, referential integrity, timeliness) -- every rule reports how
   many rows it checked and how many failed, never just "ok".
2. A **Data Quality Gate**: `enforce_gate` raises `DataQualityGateError` when any rule
   with `severity: block` fails, so the notebook stops BEFORE the warehouse load (Parte 3)
   instead of computing OEE/Cpk/CAPA KPIs on data that broke its contract. Rules with
   `severity: warn` are reported but let the pipeline through (known, documented defects
   of the frozen Versão 00 data).

The contract is the single source of truth for WHAT is checked; this module only knows
HOW to check each kind of rule. Cross-table business rules are the one exception that
needs code -- they are registered in `BUSINESS_RULES` under the `check` name the
contract uses, so a rule cannot exist here without also being declared there.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
import yaml

DEFAULT_CONTRACT = Path(__file__).resolve().parent.parent / "contracts" / "data_contract.yaml"
# Identifier-like columns read as text: LotId is a 16-digit code (not a number to add up),
# and reading it as int64 would silently turn a missing value into a float like 2.5e15.
TEXT_COLUMNS = {"LotId": "string", "LotIdStart": "string", "WorkOrder": "string",
                "MatchedWorkOrder": "string", "SalesOrderId": "string"}


class DataQualityGateError(RuntimeError):
    """Raised when at least one `severity: block` rule of the data contract fails."""


@dataclass
class RuleResult:
    table: str
    rule_id: str
    dimension: str
    severity: str
    description: str
    n_checked: int
    n_failed: int

    @property
    def passed(self) -> bool:
        return self.n_failed == 0


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_contract(path: str | Path = DEFAULT_CONTRACT) -> dict:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_table(path: str | Path) -> pd.DataFrame:
    header = pd.read_csv(path, nrows=0, encoding="utf-8-sig").columns
    dtypes = {column: kind for column, kind in TEXT_COLUMNS.items() if column in header}
    return pd.read_csv(path, dtype=dtypes, low_memory=False, encoding="utf-8-sig")


def load_tables(contract: dict, root: str | Path, only: list[str] | None = None) -> dict[str, pd.DataFrame]:
    """Reads every table the contract declares, from `root/<layer path>/<file>`."""
    root = Path(root)
    tables = {}
    for name, spec in contract["tables"].items():
        if only is None or name in only:
            tables[name] = read_table(root / contract["layers"][spec["layer"]] / spec["file"])
    return tables


# ---------------------------------------------------------------------------
# Per-table rules
# ---------------------------------------------------------------------------

def _eval_rule(df: pd.DataFrame, expression: str) -> pd.Series:
    result = df.eval(expression, engine="python")
    return pd.Series(result, index=df.index).fillna(False).astype(bool)


def _table_rules(name: str, spec: dict, df: pd.DataFrame, contract: dict,
                 tables: dict[str, pd.DataFrame]) -> list[RuleResult]:
    results: list[RuleResult] = []
    n = len(df)

    def add(rule_id, dimension, severity, description, n_checked, n_failed):
        results.append(RuleResult(name, rule_id, dimension, severity, description, int(n_checked), int(n_failed)))

    missing_columns = [c for c in spec.get("required", []) if c not in df.columns]
    add(f"{name}:SCHEMA", "validity", "block", f"Colunas obrigatórias presentes {spec.get('required', [])}",
        len(spec.get("required", [])), len(missing_columns))
    if missing_columns:
        return results  # every other rule would error on a missing column -- report the schema break only

    for column in spec.get("required", []):
        add(f"{name}:REQ:{column}", "completeness", "block", f"{column} preenchido", n, df[column].isna().sum())

    for key in [spec["primary_key"]] if "primary_key" in spec else []:
        add(f"{name}:PK", "uniqueness", "block", f"Chave primária única {key}", n, df.duplicated(key).sum())
    for key in spec.get("unique", []):
        subset = df.dropna(subset=key)
        add(f"{name}:UQ:{'+'.join(key)}", "uniqueness", "block", f"Valores únicos {key}", len(subset),
            subset.duplicated(key).sum())

    for column, allowed in spec.get("allowed_values", {}).items():
        values = df[column].dropna()
        add(f"{name}:DOM:{column}", "validity", "block", f"{column} dentro do domínio {allowed}", len(values),
            (~values.isin(allowed)).sum())

    for column, bounds in spec.get("ranges", {}).items():
        values = pd.to_numeric(df[column], errors="coerce").dropna()
        out_of_range = pd.Series(False, index=values.index)
        if "min" in bounds:
            out_of_range |= values < bounds["min"]
        if "max" in bounds:
            out_of_range |= values > bounds["max"]
        limits = {k: v for k, v in bounds.items() if k in ("min", "max")}
        add(f"{name}:RANGE:{column}", "validity", bounds.get("severity", "block"),
            bounds.get("description", f"{column} em {limits}"), len(values), out_of_range.sum())

    window = contract.get("dataset_window")
    if window:
        start = pd.Timestamp(window["start"])
        end = pd.Timestamp(window["end"]) + pd.Timedelta(days=window.get("closing_events_tolerance_days", 0))
        for column in spec.get("date_columns", []):
            dates = pd.to_datetime(df[column], errors="coerce", format="mixed")
            add(f"{name}:DATE:{column}", "timeliness", "block",
                f"{column} válido e dentro da janela {start.date()}..{end.date()}", n,
                (dates.isna() | (dates < start) | (dates > end)).sum())

    for rule in spec.get("row_rules", []):
        ok = _eval_rule(df, rule["rule"])
        add(f"{name}:{rule['id']}", rule.get("dimension", "validity"), rule.get("severity", "block"),
            rule.get("description", rule["rule"]), n, (~ok).sum())

    for fk in spec.get("foreign_keys", []):
        parent = tables.get(fk["references"])
        if parent is None:
            continue
        child_keys = df[fk["columns"]].dropna()
        parent_keys = set(map(tuple, parent[fk["ref_columns"]].astype(str).to_numpy()))
        orphans = sum(tuple(row) not in parent_keys for row in child_keys.astype(str).to_numpy())
        add(f"{name}:FK:{'+'.join(fk['columns'])}->{fk['references']}", "referential_integrity",
            fk.get("severity", "block"), fk.get("description", f"{fk['columns']} existe em {fk['references']}"),
            len(child_keys), orphans)
    return results


# ---------------------------------------------------------------------------
# Cross-table business rules (declared in the contract's `business_rules`)
# ---------------------------------------------------------------------------

def _dispositions(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    parts = [tables[name][["WorkOrder", "FinalLotDecision", "LotDecisionDateTime"]]
             for name in ("fact_bottle_disposition_lot", "fact_cap_disposition_lot", "fact_ink_disposition_lot")
             if name in tables]
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=["WorkOrder", "FinalLotDecision", "LotDecisionDateTime"])


def every_production_order_is_planned(tables, contract):
    production, plan = tables["fact_production"], tables["fact_production_plan"]
    return len(production), (~production["WorkOrder"].isin(plan["WorkOrder"])).sum()


def rejected_lot_not_shipped(tables, contract):
    dispositions = _dispositions(tables)
    rejected = set(dispositions.loc[dispositions["FinalLotDecision"] == "Rejected", "WorkOrder"])
    sales = tables["fact_sales"]
    return len(sales), sales["WorkOrder"].isin(rejected).sum()


def shipped_after_lot_decision(tables, contract):
    dispositions = _dispositions(tables)
    decision_day = (pd.to_datetime(dispositions["LotDecisionDateTime"], format="mixed", errors="coerce")
                    .groupby(dispositions["WorkOrder"]).max().dt.normalize())
    sales = tables["fact_sales"]
    decided = sales["WorkOrder"].map(decision_day)
    has_decision = decided.notna()
    shipped = pd.to_datetime(sales["Date"])
    return int(has_decision.sum()), int((shipped[has_decision] < decided[has_decision]).sum())


def _sales_vs_production_lotid(tables) -> pd.DataFrame:
    production_lot = tables["fact_production"].set_index("WorkOrder")["LotId"].astype(str)
    sales = tables["fact_sales"]
    return pd.DataFrame({"sales": sales["LotId"].astype(str).to_numpy(),
                         "production": sales["WorkOrder"].map(production_lot).to_numpy()}).dropna()


def sales_lotid_prefix_matches_production(tables, contract):
    pair = _sales_vs_production_lotid(tables)
    return len(pair), (pair["sales"].str[:14] != pair["production"].str[:14]).sum()


def sales_lotid_suffix_matches_production(tables, contract):
    pair = _sales_vs_production_lotid(tables)
    return len(pair), (pair["sales"].str[14:] != pair["production"].str[14:]).sum()


def dates_within_window(tables, contract):
    """Aggregate of every per-table DATE rule, so the gate has one timeliness line to show."""
    checked = failed = 0
    for name, spec in contract["tables"].items():
        if name not in tables:
            continue
        for result in _table_rules(name, {**spec, "row_rules": [], "foreign_keys": []}, tables[name], contract, tables):
            if ":DATE:" in result.rule_id:
                checked += result.n_checked
                failed += result.n_failed
    return checked, failed


BUSINESS_RULES = {
    "every_production_order_is_planned": every_production_order_is_planned,
    "rejected_lot_not_shipped": rejected_lot_not_shipped,
    "shipped_after_lot_decision": shipped_after_lot_decision,
    "sales_lotid_prefix_matches_production": sales_lotid_prefix_matches_production,
    "sales_lotid_suffix_matches_production": sales_lotid_suffix_matches_production,
    "dates_within_window": dates_within_window,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate(contract: dict, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Runs every rule of the contract against the tables given; returns one row per rule."""
    results: list[RuleResult] = []
    for name, spec in contract["tables"].items():
        if name in tables:
            results.extend(_table_rules(name, spec, tables[name], contract, tables))
    for rule in contract.get("business_rules", []):
        check = BUSINESS_RULES[rule["check"]]
        try:
            n_checked, n_failed = check(tables, contract)
        except KeyError:  # a table this rule needs was not loaded -- skip, don't guess
            continue
        results.append(RuleResult("business_rules", rule["id"], rule.get("dimension", "consistency"),
                                  rule.get("severity", "block"), rule["description"], int(n_checked), int(n_failed)))
    frame = pd.DataFrame([asdict(r) for r in results])
    frame["pass_rate"] = 1 - frame["n_failed"] / frame["n_checked"].where(frame["n_checked"] > 0)
    frame["status"] = frame.apply(
        lambda r: "PASS" if r["n_failed"] == 0 else ("FAIL" if r["severity"] == "block" else "WARN"), axis=1)
    return frame


def scorecard(results: pd.DataFrame) -> pd.DataFrame:
    """Pass rate by DAMA dimension: share of checked rows that passed, summed over rules."""
    grouped = results.groupby("dimension").agg(rules=("rule_id", "count"), rows_checked=("n_checked", "sum"),
                                               rows_failed=("n_failed", "sum"),
                                               rules_failed_block=("status", lambda s: (s == "FAIL").sum()),
                                               rules_warn=("status", lambda s: (s == "WARN").sum()))
    grouped["pass_rate_pct"] = 100 * (1 - grouped["rows_failed"] / grouped["rows_checked"].where(grouped["rows_checked"] > 0))
    return grouped.round({"pass_rate_pct": 3})


def enforce_gate(results: pd.DataFrame) -> None:
    """Stops the pipeline if any blocking rule failed."""
    blocking = results[results["status"] == "FAIL"]
    if not blocking.empty:
        lines = "\n".join(f"  - {r.rule_id}: {r.n_failed:,} de {r.n_checked:,} linhas -- {r.description}"
                          for r in blocking.itertuples())
        raise DataQualityGateError(f"PIPELINE BLOQUEADO: {len(blocking)} regra(s) block do data contract falharam:\n{lines}")
