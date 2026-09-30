"""The data contract (contracts/data_contract.yaml) against the project's real data.

Two levels, so CI can run without a SQL Server and without the (git-ignored) silver layer:
- bronze + dim (always): referential integrity and product-release rules on the versioned
  source data itself -- a regression introduced by a generator/fix script fails here;
- silver (when datasets/silver/ exists, i.e. after the notebook ran): the full contract,
  exactly as the Data Quality Gate at the end of Parte 2 runs it.
"""
from pathlib import Path

import pandas as pd
import pytest

from lib import data_quality as dq

ROOT = Path(__file__).resolve().parent.parent
BRONZE, DIM, SILVER = ROOT / "datasets" / "bronze", ROOT / "datasets" / "dim", ROOT / "datasets" / "silver"

# Known, documented defects of the frozen Versão 00 data (see each rule's description in the
# contract). A NEW warning is a regression to investigate, not noise -- so the set is pinned.
KNOWN_WARNINGS = {
    "fact_production:RANGE:PerformanceVsNominal",
    "fact_bottle_inspection_variables:BVAR-POS",
    "fact_cap_inspection_variable:CVAR-POS",
    "fact_bottle_disposition_lot:BDISP-AQL",
    "fact_capa:CAPA-EFF",
    "BR-LOTID-SUFFIX",
}


def _bronze(name: str) -> pd.DataFrame:
    df = pd.read_csv(BRONZE / f"{name}.csv", encoding="utf-8-sig", low_memory=False)
    for column in df.select_dtypes(include=["object", "string"]).columns:
        df[column] = df[column].str.strip()
    return df


def _dim(name: str) -> pd.DataFrame:
    return pd.read_csv(DIM / f"{name}.csv", encoding="utf-8-sig", low_memory=False)


# ---------------------------------------------------------------------------
# bronze + dim -- always
# ---------------------------------------------------------------------------

def test_dimension_primary_keys_are_unique():
    for name, key in [("dim_machine_profile", ["MachineId"]), ("dim_machine_setup", ["MoldId", "MachineId"]),
                      ("dim_customer", ["CustomerId"]), ("dim_supplier", ["SupplierId"]),
                      ("dim_masterbatch", ["ProductId"]), ("dim_cap", ["CapId"])]:
        assert not _dim(name).duplicated(key).any(), name


def test_every_production_order_references_known_machine_and_tool():
    production = _bronze("fact_production_raw")
    setup = _dim("dim_machine_setup")
    assert set(production["MachineId"]) <= set(_dim("dim_machine_profile")["MachineId"])
    known_pairs = set(zip(setup["MachineId"], setup["MoldId"]))
    assert set(zip(production["MachineId"], production["ToolId"])) <= known_pairs


def test_sales_and_supplier_lots_reference_known_master_data():
    assert set(_bronze("fact_sales_raw")["CustomerId"]) <= set(_dim("dim_customer")["CustomerId"])
    assert set(_bronze("fact_raw_material_lot_disposition_raw")["SupplierId"]) <= set(_dim("dim_supplier")["SupplierId"])


def _bronze_dispositions() -> pd.DataFrame:
    parts = [_bronze(name)[["WorkOrder", "FinalLotDecision", "LotDecisionDateTime"]]
             for name in ("fact_bottle_disposition_lot_cq_raw", "fact_cap_disposition_lot_cq_raw",
                          "fact_ink_disposition_lot_cq_raw")]
    dispositions = pd.concat(parts, ignore_index=True)
    dispositions["FinalLotDecision"] = dispositions["FinalLotDecision"].str.title()
    return dispositions


def test_no_rejected_lot_is_shipped():
    """ISO 9001 8.6/8.7 -- regression test for the expansion generator bug that shipped 30
    segregated lots (fixed by scripts/fix_expansion_sales_release.py)."""
    dispositions = _bronze_dispositions()
    rejected = set(dispositions.loc[dispositions["FinalLotDecision"] == "Rejected", "WorkOrder"])
    shipped_rejected = _bronze("fact_sales_raw")["WorkOrder"].isin(rejected)
    assert not shipped_rejected.any(), f"{shipped_rejected.sum()} rejected lots shipped"


def test_no_lot_ships_before_its_release_decision():
    dispositions = _bronze_dispositions()
    decision_day = (pd.to_datetime(dispositions["LotDecisionDateTime"], format="mixed", errors="coerce")
                    .groupby(dispositions["WorkOrder"]).max().dt.normalize())
    sales = _bronze("fact_sales_raw")
    decided = sales["WorkOrder"].map(decision_day)
    early = pd.to_datetime(sales["Date"])[decided.notna()] < decided[decided.notna()]
    assert not early.any(), f"{early.sum()} lots shipped before the lot decision"


# ---------------------------------------------------------------------------
# silver -- the full contract, when the notebook has produced it
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def silver_results():
    if not (SILVER / "fact_production_processed.csv").exists():
        pytest.skip("datasets/silver/ não existe -- rode o notebook (Partes 1-2) para gerar a camada silver")
    contract = dq.load_contract()
    return dq.validate(contract, dq.load_tables(contract, ROOT))


def test_silver_passes_the_quality_gate(silver_results):
    failures = silver_results[silver_results["status"] == "FAIL"]
    assert failures.empty, failures[["rule_id", "n_failed", "description"]].to_string()


def test_silver_warnings_are_only_the_documented_ones(silver_results):
    warnings = set(silver_results.loc[silver_results["status"] == "WARN", "rule_id"])
    assert warnings <= KNOWN_WARNINGS, f"novo aviso de qualidade de dado: {warnings - KNOWN_WARNINGS}"
