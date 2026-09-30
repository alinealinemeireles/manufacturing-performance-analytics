"""lib/data_quality.py on a tiny hand-made contract: every kind of rule must catch a planted
violation, and the gate must block on `block` rules but not on `warn` rules."""
import pandas as pd
import pytest

from lib import data_quality as dq

CONTRACT = {
    "dataset_window": {"start": "2026-01-01", "end": "2026-12-31", "closing_events_tolerance_days": 0},
    "layers": {"silver": "."},
    "tables": {
        "dim_machine_profile": {"layer": "silver", "file": "-", "primary_key": ["MachineId"], "required": ["MachineId"]},
        "fact_production": {
            "layer": "silver", "file": "-", "primary_key": ["WorkOrder"], "required": ["WorkOrder", "ProducedQty"],
            "date_columns": ["Date"], "allowed_values": {"Process": ["Blow Molding"]},
            "ranges": {"ProducedQty": {"min": 1}, "OEE": {"min": 0, "max": 1, "severity": "warn"}},
            "row_rules": [{"id": "REJ", "rule": "RejectedQty <= ProducedQty", "severity": "block"}],
            "foreign_keys": [{"columns": ["MachineId"], "references": "dim_machine_profile", "ref_columns": ["MachineId"]}],
        },
    },
    "business_rules": [],
}


def _clean_tables():
    return {
        "dim_machine_profile": pd.DataFrame({"MachineId": ["M1", "M2"]}),
        "fact_production": pd.DataFrame({
            "WorkOrder": ["WO-1", "WO-2"], "Date": ["2026-03-01", "2026-03-02"], "MachineId": ["M1", "M2"],
            "Process": ["Blow Molding", "Blow Molding"], "ProducedQty": [100, 200], "RejectedQty": [1, 2],
            "OEE": [0.8, 0.7]}),
    }


def _status(results, suffix):
    return results.loc[results["rule_id"].str.endswith(suffix), "status"].iloc[0]


def test_clean_data_passes_every_rule_and_the_gate():
    results = dq.validate(CONTRACT, _clean_tables())
    assert (results["status"] == "PASS").all()
    dq.enforce_gate(results)  # does not raise


@pytest.mark.parametrize("column, values, rule_suffix", [
    ("WorkOrder", ["WO-1", "WO-1"], "fact_production:PK"),
    ("ProducedQty", [100, None], ":REQ:ProducedQty"),
    ("Process", ["Blow Molding", "blow molding"], ":DOM:Process"),
    ("ProducedQty", [100, 0], ":RANGE:ProducedQty"),
    ("RejectedQty", [1, 500], "fact_production:REJ"),
    ("MachineId", ["M1", "M9"], "->dim_machine_profile"),
    ("Date", ["2026-03-01", "2027-06-01"], ":DATE:Date"),
])
def test_each_rule_type_catches_its_violation_and_blocks(column, values, rule_suffix):
    tables = _clean_tables()
    tables["fact_production"][column] = values
    results = dq.validate(CONTRACT, tables)
    assert _status(results, rule_suffix) == "FAIL"
    with pytest.raises(dq.DataQualityGateError):
        dq.enforce_gate(results)


def test_warn_rules_are_reported_but_do_not_block():
    tables = _clean_tables()
    tables["fact_production"]["OEE"] = [0.8, 1.2]
    results = dq.validate(CONTRACT, tables)
    assert _status(results, ":RANGE:OEE") == "WARN"
    dq.enforce_gate(results)


def test_missing_required_column_is_a_schema_failure():
    tables = _clean_tables()
    tables["fact_production"] = tables["fact_production"].drop(columns="ProducedQty")
    results = dq.validate(CONTRACT, tables)
    assert _status(results, "fact_production:SCHEMA") == "FAIL"


def _release_tables():
    # Batch B1 = WO-1 + WO-2 (disposition names only WO-2, the batch's last order); B2 = WO-3.
    return {
        "fact_production": pd.DataFrame({"WorkOrder": ["WO-1", "WO-2", "WO-3"], "ProductBatch": ["B1", "B1", "B2"]}),
        "fact_sales": pd.DataFrame({"WorkOrder": ["WO-1", "WO-3"], "Date": ["2026-03-05", "2026-03-06"]}),
        "fact_bottle_disposition_lot": pd.DataFrame({"ProductBatch": ["B1", "B2"], "WorkOrder": ["WO-2", "WO-3"],
                                                     "FinalLotDecision": ["Approved", "Rejected"],
                                                     "LotDecisionDateTime": ["2026-03-02 10:00", "2026-03-02 11:00"]}),
    }


def test_rejected_lot_shipped_business_rule():
    tables = _release_tables()
    assert dq.rejected_lot_not_shipped(tables, {}) == (2, 1)
    assert dq.shipped_after_batch_decision(tables, {}) == (2, 0)
    tables["fact_sales"]["Date"] = ["2026-03-01", "2026-03-06"]  # WO-1 shipped the day before B1's decision
    assert dq.shipped_after_batch_decision(tables, {}) == (2, 1)
    # ... which the work-order-level rule cannot see: WO-1 is not named on any disposition.
    assert dq.shipped_after_lot_decision(tables, {}) == (1, 0)


def test_release_rules_work_at_batch_level_not_work_order_level():
    """WO-1 is not named on any disposition, but its batch B2 is Rejected: it must not ship."""
    tables = _release_tables()
    tables["fact_production"]["ProductBatch"] = ["B2", "B1", "B2"]
    assert dq.rejected_lot_not_shipped(tables, {}) == (2, 2)


def test_a_broken_business_rule_is_not_silently_skipped():
    contract = {**CONTRACT, "business_rules": [{"id": "BR-X", "check": "rejected_lot_not_shipped",
                                                "description": "-"}]}
    tables = {**_clean_tables(), **_release_tables()}
    tables["fact_production"] = tables["fact_production"].drop(columns="ProductBatch")  # a real bug, not a missing table
    with pytest.raises(KeyError):
        dq.validate(contract, tables)
    del tables["fact_sales"]  # a genuinely missing table IS skipped
    assert "BR-X" not in set(dq.validate(contract, tables)["rule_id"])


def test_every_business_rule_in_the_real_contract_is_implemented():
    contract = dq.load_contract()
    assert {rule["check"] for rule in contract["business_rules"]} <= set(dq.BUSINESS_RULES)
