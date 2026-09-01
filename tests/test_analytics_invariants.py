import pandas as pd

from lib.etl_lib import SIX_BIG_LOSSES_CATEGORIES, compute_oee_components, compute_six_big_losses


def test_oee_components_are_bounded_and_performance_raw_remains_visible():
    production = pd.DataFrame({
        "WorkOrder": ["WO-1", "WO-2"],
        "MachineId": ["M1", "M1"],
        "ToolId": ["T1", "T1"],
        "ProducedQty": [1000, 1050],
        "RejectedQty": [20, 10],
        "LeadTimeProdHours": [1.0, 1.0],
        "_start_dt": pd.to_datetime(["2026-01-01 08:00", "2026-01-01 10:00"]),
    })
    plan = pd.DataFrame({"WorkOrder": ["WO-1", "WO-2"], "PlannedHours": [1.0, 1.0]})
    downtime = pd.DataFrame(columns=["WorkOrder", "PlannedStoppage", "StoppageReason", "DowntimeDurationMin"])
    capacity = {("M1", "T1"): 1000.0}

    out = compute_oee_components(production, plan, downtime, capacity)

    assert (out["Performance"] <= 1).all()
    assert (out["OEE"] <= 1).all()
    assert out.loc[out["WorkOrder"] == "WO-2", "PerformanceVsNominal"].iloc[0] > 1


def test_quality_loss_is_not_double_counted_with_speed_loss():
    """Exercises the real gold/report code path (lib.etl_lib.compute_six_big_losses),
    not a formula recomputed inside the test -- so this fails if someone reintroduces
    `RunTimeHours * (1 - Quality)` (double-counted with speed loss) into that function
    or back into the notebook instead of calling it."""
    production = pd.DataFrame({
        "RunTimeHours": [10.0],
        "Performance": [0.8],
        "Quality": [0.9],
    })
    downtime = pd.DataFrame({
        "DowntimeDurationMin": pd.Series([], dtype=float),
        "UnplannedFailure": pd.Series([], dtype=bool),
        "IsChangeoverSetup": pd.Series([], dtype=bool),
        "PlannedStoppage": pd.Series([], dtype=object),
    })

    losses = compute_six_big_losses(production, downtime, group_columns=[])

    assert sorted(losses["LossCategory"]) == sorted(SIX_BIG_LOSSES_CATEGORIES)
    hours_by_category = losses.set_index("LossCategory")["Hours"]
    speed_loss = hours_by_category["Perda de velocidade"]
    quality_loss = hours_by_category["Perda de qualidade (sucata)"]
    good_equivalent = production["RunTimeHours"].sum() - speed_loss - quality_loss

    assert abs(speed_loss - 2.0) < 1e-12
    assert abs(quality_loss - 0.8) < 1e-12
    assert abs(good_equivalent - 7.2) < 1e-12

    # The double-counted bug (RunTimeHours * (1 - Quality), ignoring Performance)
    # would give 10.0 * (1 - 0.9) = 1.0 here -- must NOT be what the function returns.
    double_counted_bug_value = 10.0 * (1 - 0.9)
    assert abs(quality_loss - double_counted_bug_value) > 1e-9
