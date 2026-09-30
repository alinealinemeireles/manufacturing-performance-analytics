"""SPC and process-capability formulas (lib/etl_lib.py section 5, lib/stats_lib.py), checked
against values computed by hand from the textbook definitions (Montgomery, AIAG SPC manual)."""
import numpy as np
import pandas as pd
import pytest

from lib import etl_lib as etl
from lib import stats_lib as sq


def _subgroups(xbars, ranges, lsl=9.0, usl=11.0):
    return pd.DataFrame({"Group": "G", "XBar": xbars, "RangeR": ranges, "LSL": lsl, "USL": usl, "Nominal": 10.0})


def test_xbar_r_control_limits_use_the_n5_constants():
    df = etl.compute_control_limits(_subgroups([10.0, 10.2, 9.8, 10.0], [0.5, 0.5, 0.5, 0.5]), ["Group"], subgroup_size=5)
    # CL = 10.0, R-bar = 0.5, A2(n=5) = 0.577, D3 = 0, D4 = 2.114
    assert df["XBarCL"].iloc[0] == pytest.approx(10.0)
    assert df["XBarUCL"].iloc[0] == pytest.approx(10.0 + 0.577 * 0.5)
    assert df["XBarLCL"].iloc[0] == pytest.approx(10.0 - 0.577 * 0.5)
    assert df["RangeRUCL"].iloc[0] == pytest.approx(2.114 * 0.5)
    assert df["RangeRLCL"].iloc[0] == pytest.approx(0.0)
    assert not df["OutOfControlXBar"].any()


def test_cp_cpk_from_within_subgroup_sigma():
    df = etl.compute_process_capability(_subgroups([10.2, 10.2], [0.4652, 0.4652]), ["Group"], subgroup_size=5)
    sigma_within = 0.4652 / 2.326                          # R-bar / d2(n=5) = 0.2
    assert df["Cp"].iloc[0] == pytest.approx(2.0 / (6 * sigma_within))                     # 1.667
    assert df["Cpk"].iloc[0] == pytest.approx((11.0 - 10.2) / (3 * sigma_within))          # 1.333
    assert df["Cpk"].iloc[0] < df["Cp"].iloc[0]  # off-centre process: Cpk < Cp


def test_pp_ppk_use_individual_measurements_not_subgroup_means():
    measurements = pd.DataFrame({"M1": [9.6, 10.4], "M2": [10.4, 9.6], "M3": [10.0, 10.0]})
    df = pd.concat([_subgroups([10.0, 10.0], [0.8, 0.8]), measurements], axis=1)
    out = etl.compute_process_capability(df, ["Group"], subgroup_size=3, measurement_columns=["M1", "M2", "M3"])
    overall_sigma = pd.Series([9.6, 10.4, 10.0, 10.4, 9.6, 10.0]).std()
    assert out["Pp"].iloc[0] == pytest.approx(2.0 / (6 * overall_sigma))
    # XBar has zero spread here, so a Pp computed from subgroup means would be infinite -- the bug
    # the `measurement_columns` path exists to avoid.
    assert np.isfinite(out["Pp"].iloc[0])


def test_attribute_indicators():
    df = etl.compute_attribute_indicators(pd.DataFrame({"DefectsFound": [2], "SampleSize": [200]}))
    assert df["DefectRateP"].iloc[0] == pytest.approx(0.01)
    assert df["DPMO"].iloc[0] == pytest.approx(10_000)


def _run_rules(values, cl=0.0, sigma=1.0):
    df = pd.DataFrame({"X": values, "CL": cl, "UCL": cl + 3 * sigma, "LCL": cl - 3 * sigma})
    return sq.apply_western_electric_rules(df, "X", "CL", "UCL", "LCL")


def test_western_electric_rule_1_point_beyond_3_sigma():
    out = _run_rules([0, 0.5, 3.5, 0])
    assert out["Rule1_Beyond3Sigma"].tolist() == [False, False, True, False]


def test_western_electric_rule_2_two_of_three_beyond_2_sigma_same_side():
    out = _run_rules([0, 2.5, -1.0, 2.5])
    assert bool(out["Rule2_2of3Beyond2Sigma"].iloc[3]) is True
    # opposite sides do not count together
    assert not _run_rules([0, 2.5, -2.5, 0])["Rule2_2of3Beyond2Sigma"].any()


def test_western_electric_rule_3_four_of_five_beyond_1_sigma():
    out = _run_rules([1.5, 1.5, 0, 1.5, 1.5])
    assert bool(out["Rule3_4of5Beyond1Sigma"].iloc[4]) is True


def test_western_electric_rule_4_eight_on_one_side():
    out = _run_rules([0.1] * 8)
    assert out["Rule4_8ConsecutiveSameSide"].tolist() == [False] * 7 + [True]
    assert not _run_rules([0.1, -0.1] * 4)["Rule4_8ConsecutiveSameSide"].any()


def test_in_control_random_data_rarely_triggers_rule_1():
    rng = np.random.default_rng(0)
    out = _run_rules(rng.normal(0, 1, 5000))
    assert out["Rule1_Beyond3Sigma"].mean() < 0.006  # theoretical 0.27%


def test_two_sample_proportion_test_detects_a_real_difference():
    result = sq.two_sample_proportion_test(60, 1000, 30, 1000)
    assert result["significant_at_0_05"] is True
    assert result["rate1"] == pytest.approx(0.06)


def test_capability_over_time_sees_a_recent_drop_the_period_value_hides():
    # 60 centred subgroups, then 25 drifting towards the USL: the whole-period Cpk still looks
    # fine, the last-25 window does not.
    xbar = [10.0] * 60 + [10.7] * 25
    df = pd.DataFrame({"G": "g", "XBar": xbar, "RangeR": 0.2326, "LSL": 9.0, "USL": 11.0,
                       "InspectionDateTime": pd.date_range("2026-01-01", periods=85, freq="h")})
    summary = etl.summarize_capability_over_time(df, ["G"], subgroup_size=5, window=25).iloc[0]
    sigma = 0.2326 / 2.326
    assert summary["LatestCpk"] == pytest.approx((11.0 - 10.7) / (3 * sigma))     # 1.0
    assert summary["PeriodCpk"] > summary["LatestCpk"]
    assert 0 < summary["PctWindowsBelowTarget"] < 1                              # a trend, not a 0/1 flag
    assert summary["SubgroupCount"] == 85


def test_capability_over_time_flags_short_history_instead_of_guessing():
    df = pd.DataFrame({"G": "g", "XBar": [10.0] * 10, "RangeR": 0.2326, "LSL": 9.0, "USL": 11.0,
                       "InspectionDateTime": pd.date_range("2026-01-01", periods=10, freq="h")})
    summary = etl.summarize_capability_over_time(df, ["G"], subgroup_size=5, window=25).iloc[0]
    assert pd.isna(summary["PctWindowsBelowTarget"])
