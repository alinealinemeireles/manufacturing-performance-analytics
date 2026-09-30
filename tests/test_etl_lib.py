"""Unit tests for lib/etl_lib.py -- cleaning, calendar, traceability and OEE building blocks.

Each test pins one decision the notebook relies on, with a hand-computable input, so a
regression shows up here instead of as a silently different KPI three Partes later."""
import numpy as np
import pandas as pd
import pytest

from lib import etl_lib as etl

# ---------------------------------------------------------------------------
# 1. Cleaning
# ---------------------------------------------------------------------------

def test_disguised_blanks_become_real_missing_values():
    df = pd.DataFrame({"Tech": ["-", " N/A ", "//", "João", None], "Qty": [1, 2, 3, 4, 5]})
    out = etl.clean_disguised_blanks(df)
    assert out["Tech"].isna().tolist() == [True, True, True, False, True]
    assert out["Qty"].tolist() == [1, 2, 3, 4, 5]  # numeric columns untouched


def test_whitespace_and_category_case_are_normalized():
    df = pd.DataFrame({"Process": ["  injection   molding ", "INJECTION MOLDING", "Injection Molding"]})
    out = etl.standardize_categories(etl.strip_extra_spaces(df), ["Process"])
    assert out["Process"].nunique() == 1
    assert out["Process"].iloc[0] == "Injection Molding"


def test_negative_quantities_are_sign_corrected_not_dropped():
    df = pd.DataFrame({"RejectedQty": [-12, 5, 0]})
    out = etl.fix_negative_quantities(df, ["RejectedQty"])
    assert out["RejectedQty"].tolist() == [12, 5, 0]
    assert len(out) == len(df)


def test_duplicate_rows_are_removed_and_counted():
    df = pd.DataFrame({"WorkOrder": ["WO-1", "WO-1", "WO-2"], "Qty": [10, 10, 7]})
    out, n_removed = etl.drop_duplicate_rows(df)
    assert n_removed == 1
    assert out["WorkOrder"].tolist() == ["WO-1", "WO-2"]


# ---------------------------------------------------------------------------
# 2. Calendar / shift
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("time_of_day, shift", [
    ("06:00:00", 1), ("13:59:59", 1), ("14:00:00", 2), ("21:59:59", 2), ("22:00:00", 3), ("05:59:59", 3),
])
def test_shift_boundaries(time_of_day, shift):
    assert etl.compute_shift_number(pd.Series([time_of_day])).iloc[0] == shift


def test_iso_week_is_used_at_year_boundary():
    # 2026-01-01 is a Thursday of ISO week 1; 2025-12-29 (Monday) is ALSO ISO week 1 of 2026.
    out = etl.add_calendar_columns(pd.DataFrame({"Date": ["2025-12-29", "2026-01-01"]}), "Date")
    assert out["ISOWeek"].tolist() == [1, 1]
    assert out["ISOWeekday"].tolist() == [1, 4]


def test_order_running_past_midnight_ends_the_next_day():
    end = etl.compute_end_datetime(pd.Series(["2026-03-10"]), pd.Series(["22:00:00"]), pd.Series(["02:30:00"]))
    assert end.iloc[0] == pd.Timestamp("2026-03-11 02:30:00")


# ---------------------------------------------------------------------------
# 3. LotId traceability
# ---------------------------------------------------------------------------

def test_lotid_prefix_layout():
    prefix = etl.build_lotid_prefix(pd.Series(["2026-01-01"]), pd.Series([2]), pd.Series(["Injection Molding"]),
                                    pd.Series(["IM-002"]), pd.Series(["WO-6005"]))
    # YY=26, ISO week=01, weekday=4 (Thu), shift=2, process=2, machine=02, order=06005
    assert prefix.iloc[0] == "26" + "01" + "4" + "2" + "2" + "02" + "06005"
    assert len(prefix.iloc[0]) == 14


@pytest.mark.parametrize("date, expected_yyww", [
    ("2025-12-29", "2601"),  # Monday of ISO week 1 of 2026 -- was "2501" (one year off)
    ("2025-12-31", "2601"),
    ("2026-12-30", "2653"),  # ISO week 53 of 2026
    ("2027-01-01", "2653"),  # still ISO 2026-W53
    ("2025-07-01", "2527"),
])
def test_lotid_year_is_the_iso_year_of_the_iso_week(date, expected_yyww):
    prefix = etl.build_lotid_prefix(pd.Series([date]), pd.Series([1]), pd.Series(["Blow Molding"]),
                                    pd.Series(["ISBM-001"]), pd.Series(["WO-1000"]))
    assert prefix.iloc[0][:4] == expected_yyww


def test_material_lot_sequence_treats_consecutive_blank_lots_as_one_lot():
    consumption = pd.DataFrame({"WorkOrder": ["WO-1"] * 3, "MaterialLot": [np.nan, np.nan, np.nan],
                                "RecordSeq": [1, 2, 3]})
    assert etl.compute_material_lot_sequence(consumption).tolist() == [1, 1, 1]


def test_material_lot_sequence_increments_only_on_real_lot_change():
    consumption = pd.DataFrame({
        "WorkOrder": ["WO-1", "WO-1", "WO-1", "WO-1", "WO-2"],
        "MaterialLot": ["A", "A", "B", "B", "C"],
        "RecordSeq": [1, 2, 3, 4, 1],
    }).sample(frac=1, random_state=0)  # shuffled on purpose: order must come from RecordSeq
    seq = etl.compute_material_lot_sequence(consumption)
    expected = {(1, "A"): 1, (2, "A"): 1, (3, "B"): 2, (4, "B"): 2}
    for idx, row in consumption.iterrows():
        if row["WorkOrder"] == "WO-1":
            assert seq.loc[idx] == expected[(row["RecordSeq"], row["MaterialLot"])]
        else:
            assert seq.loc[idx] == 1


# ---------------------------------------------------------------------------
# 4. Downtime and OEE
# ---------------------------------------------------------------------------

def _downtime(rows):
    return pd.DataFrame(rows, columns=["Date", "MachineId", "StoppageStartTime", "DowntimeDurationMin"])


def test_effective_downtime_counts_overlapping_events_once():
    # M1: 08:00-09:00, 08:30-09:30 (overlaps 30 min), 08:40-08:50 (fully inside) -> union = 90 min.
    # M2: a separate machine, never merged with M1.
    downtime = _downtime([
        ("2026-05-04", "M1", "08:00:00", 60.0),
        ("2026-05-04", "M1", "08:30:00", 60.0),
        ("2026-05-04", "M1", "08:40:00", 10.0),
        ("2026-05-04", "M2", "08:30:00", 60.0),
    ])
    effective = etl.compute_effective_downtime(downtime)
    assert effective.tolist() == [60.0, 30.0, 0.0, 60.0]
    assert effective[downtime["MachineId"] == "M1"].sum() == 90.0
    assert (effective <= downtime["DowntimeDurationMin"]).all()


def _oee_inputs(downtime_rows=(), planned_hours=(1.0, 1.0)):
    production = pd.DataFrame({
        "WorkOrder": ["WO-1", "WO-2"], "MachineId": ["M1", "M1"], "ToolId": ["T1", "T1"],
        "ProducedQty": [900, 1000], "RejectedQty": [90, 0], "LeadTimeProdHours": [1.0, 1.0],
        "_start_dt": pd.to_datetime(["2026-01-01 08:00", "2026-01-01 10:00"]),
    })
    plan = pd.DataFrame({"WorkOrder": ["WO-1", "WO-2"], "PlannedHours": list(planned_hours)})
    downtime = pd.DataFrame(list(downtime_rows),
                            columns=["WorkOrder", "PlannedStoppage", "StoppageReason", "DowntimeDurationMin",
                                     "EffectiveDowntimeMin"])
    return production, plan, downtime, {("M1", "T1"): 1000.0}


def test_oee_identity_and_bounds():
    production, plan, downtime, capacity = _oee_inputs(
        [("WO-1", "No", "Machine Failure", 6.0, 6.0)])
    out = etl.compute_oee_components(production, plan, downtime, capacity).set_index("WorkOrder")
    for column in ["Availability", "Performance", "Quality", "OEE"]:
        assert out[column].between(0, 1).all()
    assert np.allclose(out["OEE"], out["Availability"] * out["Performance"] * out["Quality"])
    assert out.loc["WO-1", "Availability"] == pytest.approx(0.9)          # 54 of 60 min running
    assert out.loc["WO-1", "Performance"] == pytest.approx(1.0)           # 900 pcs in 0.9 h = 1000/h
    assert out.loc["WO-1", "Quality"] == pytest.approx(0.9)               # 810 good of 900


def test_oee_time_base_is_the_real_window_not_the_plan():
    """Decision D1 (audit 2026-09-30): an order planned for 1 h that really took 2 h must not
    show Availability 100% and full speed -- the overrun is lost time."""
    production, plan, downtime, capacity = _oee_inputs()
    production["LeadTimeProdHours"] = [2.0, 1.0]          # WO-1 ran twice as long as planned
    out = etl.compute_oee_components(production, plan, downtime, capacity).set_index("WorkOrder")
    assert out.loc["WO-1", "PlannedTimeHours"] == pytest.approx(2.0)
    assert out.loc["WO-1", "PlannedHours"] == pytest.approx(1.0)       # the plan is still there
    assert out.loc["WO-1", "Performance"] == pytest.approx(900 / 2 / 1000)  # 450 pcs/h vs 1000


def test_setup_is_an_availability_loss_and_breaks_are_not_planned_production_time():
    production, plan, downtime, capacity = _oee_inputs([
        ("WO-1", "Yes", "Mold Change / Setup", 12.0, 12.0),
        ("WO-1", "Yes", "Scheduled Cleaning", 6.0, 6.0),
    ])
    out = etl.compute_oee_components(production, plan, downtime, capacity).set_index("WorkOrder")
    assert out.loc["WO-1", "PlannedTimeHours"] == pytest.approx(54 / 60)   # 60 min - 6 min cleaning
    assert out.loc["WO-1", "SetupTimeHours"] == pytest.approx(12 / 60)
    assert out.loc["WO-1", "RunTimeHours"] == pytest.approx(42 / 60)       # setup is lost time
    assert out.loc["WO-1", "Availability"] == pytest.approx(42 / 54)


def test_availability_uses_effective_not_summed_downtime():
    # Two overlapping unplanned events: 30 min of events, but only 20 min of machine time lost.
    production, plan, downtime, capacity = _oee_inputs([
        ("WO-1", "No", "Machine Failure", 20.0, 20.0),
        ("WO-1", "No", "Quality Adjustment", 10.0, 0.0),
    ])
    out = etl.compute_oee_components(production, plan, downtime, capacity).set_index("WorkOrder")
    assert out.loc["WO-1", "UnplannedDowntimeHours"] == pytest.approx(20 / 60)


def test_order_without_plan_keeps_a_finite_availability():
    """Regression: RunTime used the lead-time fallback but Availability divided by the
    unfilled PlannedTimeHours, so an unplanned order got Availability = OEE = NaN."""
    production, plan, downtime, capacity = _oee_inputs()
    plan = plan[plan["WorkOrder"] == "WO-2"]
    out = etl.compute_oee_components(production, plan, downtime, capacity).set_index("WorkOrder")
    assert out.loc["WO-1", "Availability"] == pytest.approx(1.0)
    assert out["OEE"].notna().all()


def test_downtime_reaching_planned_time_is_flagged_not_silently_floored():
    production, plan, downtime, capacity = _oee_inputs([("WO-1", "No", "Machine Failure", 60.0, 60.0)])
    out = etl.compute_oee_components(production, plan, downtime, capacity).set_index("WorkOrder")
    assert bool(out.loc["WO-1", "DowntimeExceedsPlan"]) is True
    assert pd.isna(out.loc["WO-1", "PerformanceVsNominal"])  # 900 pcs / 0.01 h would be a fake 90x
    assert out.loc["WO-1", "Performance"] <= 1
    assert bool(out.loc["WO-2", "DowntimeExceedsPlan"]) is False


def test_only_equipment_failures_count_as_breakdowns():
    """Supply/staffing stops cost availability but are not equipment failures -- they must
    not feed MTBF/MTTR/Weibull, the "Quebras" loss, or the predictive-maintenance target."""
    downtime = pd.DataFrame({
        "StoppageReason": ["Electrical/Control Failure", "Mechanical Failure (Breakage/Jam)", "Mold Change / Setup",
                           "Operator Unavailable", "Raw Material Shortage", "Utilities Shortage (Compressed Air)",
                           "Mechanical Failure (Breakage/Jam)"],
        "PlannedStoppage": ["No", "No", "No", "No", "No", "No", "Yes"],
    })
    assert etl.classify_stoppage(downtime).tolist() == [True, True, False, False, False, False, False]
