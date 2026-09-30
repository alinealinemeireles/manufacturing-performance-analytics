"""lib/ml_lib.py: temporal validation discipline, baselines and the decision threshold."""
import warnings

import numpy as np
import pandas as pd
import pytest
from sklearn.exceptions import ConvergenceWarning

from lib import ml_lib as ml


def test_split_by_date_never_trains_on_the_future():
    rng = np.random.default_rng(1)
    df = pd.DataFrame({"Date": pd.date_range("2026-01-01", periods=100).to_numpy()[rng.permutation(100)],
                       "y": np.arange(100)})
    train, test = ml.split_by_date(df, "Date", test_fraction=0.2)
    assert len(train) == 80 and len(test) == 20
    assert train["Date"].max() < test["Date"].min()


def test_group_rate_baseline_uses_training_history_only():
    train_groups = pd.Series(["A", "A", "B", "B"])
    y_train = [1, 0, 0, 0]
    test_groups = pd.Series(["A", "B", "C"])
    prediction = ml.group_rate_baseline(train_groups, y_train, test_groups)
    # A: 0.5, B: 0.0, unseen C: overall train mean 0.25
    assert prediction.tolist() == [0.5, 0.0, 0.25]


@pytest.mark.parametrize("model_value, baseline_value, higher, beats", [
    (0.80, 0.70, True, True),    # +14% AUC
    (0.71, 0.70, True, False),   # +1.4% -- not material
    (90.0, 100.0, False, True),  # MAE 10% lower
    (99.0, 100.0, False, False),
])
def test_baseline_verdict_requires_a_material_gain(model_value, baseline_value, higher, beats):
    verdict = ml.baseline_verdict(model_value, baseline_value, "metric", higher_is_better=higher)
    assert verdict["beats_baseline"] is beats


def test_economic_threshold_moves_down_when_false_negatives_are_expensive():
    rng = np.random.default_rng(2)
    y = rng.integers(0, 2, 2000)
    probability = np.clip(y * 0.3 + rng.uniform(0, 0.7, 2000), 0, 1)
    symmetric = ml.economic_threshold(y, probability, cost_false_positive=1, cost_false_negative=1)
    asymmetric = ml.economic_threshold(y, probability, cost_false_positive=1, cost_false_negative=20)
    assert asymmetric["best_threshold"] < symmetric["best_threshold"]
    assert asymmetric["best_cost"] <= asymmetric["cost_at_0_5"]


def test_classification_metrics_report_pr_auc_next_to_roc_auc():
    metrics = ml.classification_metrics([0, 0, 1, 1], [0, 1, 1, 1], probability=[0.1, 0.6, 0.7, 0.9])
    assert metrics["ROC_AUC"] == pytest.approx(1.0)
    assert {"Precision", "Recall", "F1", "PR_AUC"} <= set(metrics)


def test_linear_candidate_is_scaled_and_converges():
    """The logistic candidate used to run on raw features mixing 0/1 dummies with quantities in
    the thousands, and lbfgs hit its iteration limit (ConvergenceWarning in the full-run log)."""
    rng = np.random.default_rng(3)
    n = 600
    X = pd.DataFrame({"LotSize": rng.integers(1_000, 60_000, n).astype(float),
                      "SampleSize": rng.integers(50, 500, n).astype(float),
                      "Machine_A": rng.integers(0, 2, n).astype(float)})
    y = pd.Series((X["Machine_A"] + rng.uniform(0, 1, n) > 1.2).astype(int))
    X_train, X_test, y_train, y_test = X.iloc[:480], X.iloc[480:], y.iloc[:480], y.iloc[480:]
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        comparison, model, name = ml.tune_classification_models(X_train, y_train, X_test, y_test, n_splits=2)
    assert "LogisticRegression" in comparison.index
    assert comparison.loc[name, "Metric_Basis"] == "Teste (reportado)"


def test_linear_coefficients_unwrap_the_scaler_pipeline():
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    X = pd.DataFrame({"a": np.arange(20.0), "b": np.arange(20.0) ** 2})
    model = Pipeline([("scale", StandardScaler()), ("model", Ridge())]).fit(X, X["a"] * 2)
    coefficients = ml.linear_coefficients(model, X.columns)
    assert list(coefficients.index) == ["a", "b"]
    assert ml.linear_coefficients(object(), X.columns) is None
