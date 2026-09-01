"""
ml_lib.py

Shared helpers for the Machine Learning section (Parte 11) of
manufacturing_performance_analytics.ipynb: a strict time-based train/test split,
regression/classification evaluation, model comparison utilities, and model
persistence. Centralized so every model in the project is validated the same honest way.

Rigor note: every model in Parte 11 is chosen by comparing several candidate algorithms with
proper hyperparameter search (GridSearchCV/RandomizedSearchCV) under a time-respecting
cross-validation scheme (sklearn's TimeSeriesSplit, or a manual walk-forward split for the
per-order models) -- never a single fixed-hyperparameter model taken on faith, and never a
random shuffle that would leak future information into training.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn.metrics import (
    accuracy_score, average_precision_score, f1_score, mean_absolute_error, mean_squared_error,
    precision_score, r2_score, recall_score, roc_auc_score,
    classification_report, confusion_matrix,
)


def split_by_date(df: pd.DataFrame, date_column: str, test_fraction: float = 0.2):
    """Sorts by date and takes the oldest (1-test_fraction) share as train,
    the newest as test -- never a random split. A random split would let a
    later failure "help" predict an earlier one, which no real forecaster
    would ever have access to at prediction time."""
    df_sorted = df.sort_values(date_column).reset_index(drop=True)
    split_index = int(len(df_sorted) * (1 - test_fraction))
    return df_sorted.iloc[:split_index].copy(), df_sorted.iloc[split_index:].copy()


def regression_metrics(y_true, y_pred) -> dict:
    y_true, y_pred = np.asarray(y_true, dtype=float), np.asarray(y_pred, dtype=float)
    nonzero = y_true != 0
    mape = float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100) if nonzero.any() else np.nan
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAPE_%": mape,
        "R2": r2_score(y_true, y_pred),
    }


def classification_metrics(y_true, y_pred, probability=None) -> dict:
    """Precision/Recall/F1 alongside Accuracy on purpose: the positive
    class (a rejected lot, a machine failure tomorrow) is rare (5-40%)
    across every classifier in this project, so accuracy alone would
    reward a model that just always predicts "no problem". PR-AUC
    (average precision) is reported alongside ROC-AUC for the same reason
    ROC-AUC alone is not enough here: ROC-AUC can look deceptively good
    under class imbalance because it credits the (large) true-negative
    rate; PR-AUC only rewards ranking the rare positive class well, which
    is what actually matters for "did we catch the rejected lot / the
    failure before it happened"."""
    metrics = {
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred, zero_division=0),
        "Recall": recall_score(y_true, y_pred, zero_division=0),
        "F1": f1_score(y_true, y_pred, zero_division=0),
    }
    if probability is not None:
        metrics["ROC_AUC"] = roc_auc_score(y_true, probability)
        metrics["PR_AUC"] = average_precision_score(y_true, probability)
    return metrics


def economic_threshold(y_true, probability, cost_false_positive: float, cost_false_negative: float) -> dict:
    """Sweeps the decision threshold and picks the one that minimizes total
    expected cost, instead of accepting the default 0.5 cutoff. 0.5 is only
    the "right" threshold when a false positive and a false negative cost
    the same -- almost never true in a quality/maintenance decision (e.g. an
    unnecessary preventive-maintenance call is far cheaper than an
    unplanned failure, so the cost-minimizing threshold is usually well
    below 0.5, trading some precision for more recall on purpose)."""
    y_true = np.asarray(y_true)
    thresholds = np.linspace(0.01, 0.99, 99)
    rows = []
    for threshold in thresholds:
        pred = (np.asarray(probability) >= threshold).astype(int)
        false_positives = int(((pred == 1) & (y_true == 0)).sum())
        false_negatives = int(((pred == 0) & (y_true == 1)).sum())
        total_cost = false_positives * cost_false_positive + false_negatives * cost_false_negative
        rows.append({"threshold": threshold, "false_positives": false_positives,
                      "false_negatives": false_negatives, "total_cost": total_cost})
    sweep = pd.DataFrame(rows)
    best = sweep.loc[sweep["total_cost"].idxmin()]
    return {"best_threshold": float(best["threshold"]), "best_cost": float(best["total_cost"]),
            "cost_at_0_5": float(sweep.loc[(sweep["threshold"] - 0.5).abs().idxmin(), "total_cost"]),
            "sweep": sweep}


def economic_threshold_val_test(model, X_train, y_train, X_test, y_test, cost_false_positive: float,
                                 cost_false_negative: float, val_fraction: float = 0.2) -> dict:
    """Same idea as `economic_threshold`, but picks the threshold WITHOUT
    touching X_test: the sweep runs on a validation slice carved from the
    newest part of X_train (`_chrono_inner_split` -- the same device used
    for algorithm selection in `tune_classification_models`), using
    probabilities from the already-fitted `model`. X_test is then scored
    exactly once, at that already-chosen threshold -- not re-swept -- so
    the reported test cost is a genuine out-of-sample number, not one the
    test set helped pick."""
    _, X_val, _, y_val = _chrono_inner_split(X_train, y_train, val_fraction)
    val_proba = model.predict_proba(X_val)[:, 1]
    val_result = economic_threshold(y_val, val_proba, cost_false_positive, cost_false_negative)
    chosen_threshold = val_result["best_threshold"]

    test_proba = model.predict_proba(X_test)[:, 1]
    y_test_arr = np.asarray(y_test)
    pred_at_chosen = (test_proba >= chosen_threshold).astype(int)
    fp = int(((pred_at_chosen == 1) & (y_test_arr == 0)).sum())
    fn = int(((pred_at_chosen == 0) & (y_test_arr == 1)).sum())
    cost_at_chosen_on_test = fp * cost_false_positive + fn * cost_false_negative
    pred_at_0_5 = (test_proba >= 0.5).astype(int)
    fp_05 = int(((pred_at_0_5 == 1) & (y_test_arr == 0)).sum())
    fn_05 = int(((pred_at_0_5 == 0) & (y_test_arr == 1)).sum())
    cost_at_0_5_on_test = fp_05 * cost_false_positive + fn_05 * cost_false_negative
    return {"best_threshold": chosen_threshold, "best_threshold_chosen_on": "validação (não no teste)",
            "best_cost": cost_at_chosen_on_test, "cost_at_0_5": cost_at_0_5_on_test,
            "false_positives": fp, "false_negatives": fn, "n_test": len(y_test_arr),
            "n_flagged": int((pred_at_chosen == 1).sum()), "validation_sweep": val_result["sweep"]}


def show_classification_report(y_true, y_pred, class_names=("Negative", "Positive")) -> None:
    print(classification_report(y_true, y_pred, target_names=list(class_names)))
    cm = confusion_matrix(y_true, y_pred)
    print(pd.DataFrame(cm, index=[f"Actual {c}" for c in class_names],
                        columns=[f"Predicted {c}" for c in class_names]))


def compare_models(candidates: dict, X_train, y_train, X_test, y_test, metric_fn, higher_is_better: bool = True) -> pd.DataFrame:
    """Fits every already-configured estimator in `candidates` (name ->
    fitted-or-unfitted sklearn-compatible estimator with .fit/.predict),
    scores each on the held-out test set with metric_fn, and returns a
    sorted comparison table. Kept generic so it can be reused for both
    regression and classification comparisons."""
    rows = []
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        row = {"model": name}
        row.update(metric_fn(y_test, y_pred))
        rows.append(row)
    comparison = pd.DataFrame(rows).set_index("model")
    sort_col = comparison.columns[-1]
    return comparison.sort_values(sort_col, ascending=not higher_is_better)


def _chrono_inner_split(X, y, val_fraction: float):
    """Carves a validation slice off the NEWEST part of an already
    chronologically-ordered X/y (as produced by `split_by_date`'s train
    half) -- strictly older than whatever X_test the caller holds, so this
    never touches test data, just borrows a bit more of train for a
    genuine held-out comparison between candidate algorithms."""
    split = int(len(X) * (1 - val_fraction))
    return X.iloc[:split], X.iloc[split:], y.iloc[:split], y.iloc[split:]


def tune_regression_models(X_train, y_train, X_test, y_test, n_splits: int = 4, random_state: int = 42,
                            val_fraction: float = 0.2):
    """Model selection for a regression target: three genuinely different
    algorithm families (a regularized linear model, a bagged tree ensemble,
    a boosted tree ensemble), each hyperparameter-tuned via GridSearchCV
    under `TimeSeriesSplit` (folds respect chronological order -- a random
    K-fold would let a later week leak into an earlier fold's training set).

    Choosing the WINNING algorithm by scoring all three candidates on
    X_test would make X_test part of model selection, not a genuine
    held-out set -- so the three candidates are compared on an inner
    validation slice carved from the newest part of X_train instead
    (`_chrono_inner_split`, still strictly older than X_test). Only the
    winning algorithm's tuned hyperparameters get refit on the FULL X_train
    and scored against X_test -- exactly once, only for the model that is
    actually reported/deployed.

    Returns (comparison_df, best_fitted_model, best_model_name). In
    `comparison_df`, every row except the winner's shows validation-set
    metrics (used for selection, not comparable 1:1 to a test-set number);
    the winner's row is overwritten with its real test-set metrics -- see
    the `Metric_Basis` column."""
    from sklearn.base import clone
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
    from xgboost import XGBRegressor

    X_inner_train, X_val, y_inner_train, y_val = _chrono_inner_split(X_train, y_train, val_fraction)
    cv = TimeSeriesSplit(n_splits=max(2, min(n_splits, len(X_inner_train) // 8)))
    grids = {
        "Ridge": (Ridge(random_state=random_state), {"alpha": [0.1, 1.0, 10.0, 50.0]}),
        "RandomForest": (RandomForestRegressor(random_state=random_state),
                          {"n_estimators": [200, 400], "max_depth": [4, 6, None], "min_samples_leaf": [1, 3]}),
        "XGBoost": (XGBRegressor(random_state=random_state, objective="reg:squarederror", verbosity=0),
                    {"n_estimators": [100, 200], "max_depth": [3, 5], "learning_rate": [0.05, 0.1]}),
    }
    rows, best_params_by_name = [], {}
    for name, (estimator, grid) in grids.items():
        search = GridSearchCV(estimator, grid, cv=cv, scoring="neg_mean_absolute_error", n_jobs=-1)
        search.fit(X_inner_train, y_inner_train)
        metrics = regression_metrics(y_val, search.best_estimator_.predict(X_val))
        metrics["best_params"] = str(search.best_params_)
        metrics["Metric_Basis"] = "Validação (seleção)"
        rows.append({"model": name, **metrics})
        best_params_by_name[name] = search.best_params_
    comparison = pd.DataFrame(rows).set_index("model").sort_values("MAE")
    best_name = comparison.index[0]

    final_model = clone(grids[best_name][0]).set_params(**best_params_by_name[best_name])
    final_model.fit(X_train, y_train)
    test_metrics = regression_metrics(y_test, final_model.predict(X_test))
    test_metrics["best_params"] = str(best_params_by_name[best_name])
    test_metrics["Metric_Basis"] = "Teste (reportado)"
    comparison.loc[best_name] = pd.Series(test_metrics)
    return comparison, final_model, best_name


def tune_classification_models(X_train, y_train, X_test, y_test, n_splits: int = 4, random_state: int = 42,
                                 val_fraction: float = 0.2):
    """Classification counterpart to `tune_regression_models`: Logistic
    Regression, Random Forest, and XGBoost, tuned via `GridSearchCV` under
    `TimeSeriesSplit`, scored on ROC-AUC (robust to the class imbalance
    every classifier in this project faces -- the positive class is
    always the rarer "something went wrong" outcome).

    Same fix as `tune_regression_models`: the three candidates are compared
    on an inner validation slice carved from the newest part of X_train
    (`_chrono_inner_split`), never on X_test -- only the winning algorithm
    gets refit on the full X_train and scored against X_test, once. If the
    validation slice happens to contain only one class (possible with a
    rare positive class and a small slice), ROC-AUC can't be computed
    there, so selection falls back to the GridSearchCV cross-validated
    score (`search.best_score_`, itself never touching X_test either).

    Returns (comparison_df, best_fitted_model, best_model_name)."""
    from sklearn.base import clone
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
    from xgboost import XGBClassifier

    X_inner_train, X_val, y_inner_train, y_val = _chrono_inner_split(X_train, y_train, val_fraction)
    val_has_both_classes = y_val.nunique() >= 2
    cv = TimeSeriesSplit(n_splits=max(2, min(n_splits, len(X_inner_train) // 50)))
    grids = {
        "LogisticRegression": (LogisticRegression(max_iter=2000, random_state=random_state),
                                {"C": [0.1, 1.0, 10.0]}),
        "RandomForest": (RandomForestClassifier(random_state=random_state, class_weight="balanced"),
                          {"n_estimators": [200, 400], "max_depth": [4, 6, None]}),
        "XGBoost": (XGBClassifier(random_state=random_state, eval_metric="logloss", verbosity=0),
                    {"n_estimators": [100, 200], "max_depth": [3, 5], "learning_rate": [0.05, 0.1]}),
    }
    rows, best_params_by_name = [], {}
    for name, (estimator, grid) in grids.items():
        search = GridSearchCV(estimator, grid, cv=cv, scoring="roc_auc", n_jobs=-1)
        search.fit(X_inner_train, y_inner_train)
        if val_has_both_classes:
            proba = search.best_estimator_.predict_proba(X_val)[:, 1]
            metrics = classification_metrics(y_val, search.best_estimator_.predict(X_val), probability=proba)
        else:
            metrics = {"ROC_AUC": search.best_score_}
        metrics["best_params"] = str(search.best_params_)
        metrics["Metric_Basis"] = "Validação (seleção)" if val_has_both_classes else "CV interna (seleção, sem classe rara suficiente na validação)"
        rows.append({"model": name, **metrics})
        best_params_by_name[name] = search.best_params_
    comparison = pd.DataFrame(rows).set_index("model").sort_values("ROC_AUC", ascending=False)
    best_name = comparison.index[0]

    final_model = clone(grids[best_name][0]).set_params(**best_params_by_name[best_name])
    final_model.fit(X_train, y_train)
    proba_test = final_model.predict_proba(X_test)[:, 1]
    test_metrics = classification_metrics(y_test, final_model.predict(X_test), probability=proba_test)
    test_metrics["best_params"] = str(best_params_by_name[best_name])
    test_metrics["Metric_Basis"] = "Teste (reportado)"
    comparison.loc[best_name] = pd.Series(test_metrics)
    return comparison, final_model, best_name


def save_model(model, path: str, **metadata) -> None:
    """Wraps joblib.dump so feature names, training window, and test
    metrics travel with the pickle instead of living only in a notebook
    cell that's easy to lose track of."""
    dump({"model": model, "metadata": metadata}, path)
    print(f"Saved model to {path} with metadata keys: {list(metadata.keys())}")


def load_model(path: str) -> dict:
    return load(path)
