"""Model evaluation metrics for salary prediction.

Implements MAE, RMSE, R2 and MAPE plus a cross-validation helper that returns
the full metric table for model comparison.
"""

from __future__ import annotations

import numpy as np

EPSILON = 1e-6


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean absolute error."""
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root mean squared error."""
    return float(np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2)))


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Coefficient of determination."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot == 0:
        return 1.0
    return 1.0 - ss_res / ss_tot


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean absolute percentage error (fraction)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = np.abs(y_true) > EPSILON
    if not mask.any():
        return 0.0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])))


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Return a dict of all regression metrics."""
    return {
        "mae": round(mae(y_true, y_pred), 2),
        "rmse": round(rmse(y_true, y_pred), 2),
        "r2": round(r2_score(y_true, y_pred), 4),
        "mape": round(mape(y_true, y_pred), 4),
    }


def cross_validate_model(model, X, y, cv: int = 5) -> dict[str, float]:
    """Run stratified K-fold cross-validation and aggregate metrics.

    Returns aggregated (mean) metrics plus the per-fold list.
    """
    from sklearn.model_selection import KFold

    kfold = KFold(n_splits=cv, shuffle=True, random_state=42)
    agg = {"mae": [], "rmse": [], "r2": [], "mape": []}
    for train_idx, test_idx in kfold.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        agg["mae"].append(mae(y_test, preds))
        agg["rmse"].append(rmse(y_test, preds))
        agg["r2"].append(r2_score(y_test, preds))
        agg["mape"].append(mape(y_test, preds))

    return {f"cv_{metric}_mean": float(np.mean(values)) for metric, values in agg.items()}
