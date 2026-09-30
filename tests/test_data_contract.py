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
    "BR-SHIP-AFTER-BATCH-DECISION",
    "fact_raw_material_inspection:RMI-RESULT",
    "fact_bottle_attribute_inspection:ATTR-N",
    "fact_ink_attribute_inspection:ATTR-N",
    "BR-AQL-ARROW",
    "BR-AQL-LEVEL",
    "BR-NO-OVERLAP-MOLDING",
    "BR-NO-OVERLAP-DECORATION",
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


def _bronze_batch_dispositions() -> pd.DataFrame:
    """Disposition per released/rejected BATCH (ProductBatch; PrintLot for decoration) -- the unit
    QC decides on. A batch spans several work orders; its disposition row names only one of them."""
    parts = []
    for name, key in [("fact_bottle_disposition_lot_cq_raw", "ProductBatch"),
                      ("fact_cap_disposition_lot_cq_raw", "ProductBatch"),
                      ("fact_ink_disposition_lot_cq_raw", "PrintLot")]:
        d = _bronze(name)
        parts.append(pd.DataFrame({"Batch": d[key], "FinalLotDecision": d["FinalLotDecision"].str.title(),
                                   "LotDecisionDateTime": d["LotDecisionDateTime"]}))
    return pd.concat(parts, ignore_index=True)


def _bronze_sales_batch() -> pd.Series:
    production = _bronze("fact_production_raw").drop_duplicates("WorkOrder").set_index("WorkOrder")
    return _bronze("fact_sales_raw")["WorkOrder"].map(production["ProductBatch"])


def test_no_rejected_lot_is_shipped():
    """ISO 9001 8.6/8.7 -- regression test for the expansion generator bug that shipped segregated
    lots (scripts/fix_expansion_sales_release.py at work-order level, then
    scripts/fix_audit_2026_09_30.py at batch level: 31 more rows shipped from Rejected batches
    through a sibling work order of the one named on the disposition)."""
    dispositions = _bronze_batch_dispositions()
    rejected = set(dispositions.loc[dispositions["FinalLotDecision"] == "Rejected", "Batch"])
    shipped_rejected = _bronze_sales_batch().isin(rejected)
    assert not shipped_rejected.any(), f"{shipped_rejected.sum()} sales rows from rejected batches"


def test_no_lot_ships_before_its_release_decision():
    """Expansion: no row ships before its batch decision. Versão 00 (frozen) ships 173 rows 1-6 days
    before the decision of their batch -- pinned, so a new early shipment is a regression."""
    dispositions = _bronze_batch_dispositions()
    decision_day = (pd.to_datetime(dispositions["LotDecisionDateTime"], format="mixed", errors="coerce")
                    .groupby(dispositions["Batch"]).max().dt.normalize())
    sales = _bronze("fact_sales_raw")
    decided = _bronze_sales_batch().map(decision_day)
    early = decided.notna() & (pd.to_datetime(sales["Date"]) < decided)
    is_expansion = sales["MachineId"].isin({"IM-007", "IM-008", "ISBM-009", "ISBM-010"})
    assert not (early & is_expansion).any(), f"{(early & is_expansion).sum()} expansion rows shipped early"
    assert (early & ~is_expansion).sum() == 173


def test_attribute_lot_decision_follows_the_acceptance_number():
    """ISO 2859-1: reject when defects >= Re (= Ac + 1). The expansion generator used `> Re`, so a
    sample with exactly Re defects was approved (47 inspections)."""
    for name in ("fact_bottle_attribute_inspection_cq_raw", "fact_cap_attribute_inspection_cq_raw",
                 "fact_ink_attribute_inspection_cq_raw"):
        a = _bronze(name)
        expected = (a["DefectsFound"] >= a["RejectionNumber"]).map({True: "Rejected", False: "Approved"})
        wrong = expected != a["LotDecision"].str.title()
        assert not wrong.any(), f"{name}: {wrong.sum()} decisions contradict Ac/Re"


def test_attribute_plans_follow_iso_2859_1_table_ii_a():
    """Decision D3: Ac/Re are the standard's for the code letter sampled (they were one letter too
    lenient) and every sample size is a code letter's (Storyline F used n x 1.5 = 300/472)."""
    import sys
    sys.path.insert(0, str(ROOT / "lib"))
    import aql

    for name in ("fact_bottle_attribute_inspection_cq_raw", "fact_cap_attribute_inspection_cq_raw",
                 "fact_ink_attribute_inspection_cq_raw"):
        a = _bronze(name)
        plans = [aql.single_normal_plan(letter, q) for letter, q in zip(a["CodeLetter"], a["AQL"])]
        assert a["AcceptanceNumber"].tolist() == [ac for _, ac, _, _ in plans], name
        assert (a["SampleSize"] == a["CodeLetter"].map(aql.SAMPLE_SIZE)).all(), name


def test_food_contact_caps_run_on_their_own_line():
    """Decision D2: IM-008 had 188% of its calendar hours booked (a third mold stacked on it)."""
    production = _bronze("fact_production_raw").drop_duplicates("WorkOrder")
    assert set(production.loc[production["ToolId"] == "M-INJ-014", "MachineId"]) == {"IM-009"}
    start = pd.to_datetime(production["Date"]) + pd.to_timedelta(production["StartTime"])
    booked = production.assign(start=start).query("MachineId in ['IM-008', 'IM-009']").groupby("MachineId")["start"]
    assert (booked.max() - booked.min()).dt.days.min() > 150  # both lines exist over the expansion window


def test_material_is_consumed_not_created():
    c = _bronze("fact_material_consumption_raw")
    grew = c["EndWeightKg"] > c["StartWeightKg"]
    assert not grew.any(), f"{grew.sum()} consumption records end heavier than they started"


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
