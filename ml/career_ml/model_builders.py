"""Model factory for the candidate regressors used in model comparison."""

from __future__ import annotations

import logging

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression

logger = logging.getLogger("career_ml.models")

MODEL_NAMES = [
    "linear_regression",
    "random_forest",
    "gradient_boosting",
    "xgboost",
    "lightgbm",
    "catboost",
]


def build_model(name: str, *, tuned: bool = False):
    """Instantiate a candidate regressor by name.

    ``tuned=True`` applies the hyper-parameters discovered during tuning.
    """
    if name == "linear_regression":
        return LinearRegression()
    if name == "random_forest":
        params = {"n_estimators": 500, "max_depth": 18, "min_samples_leaf": 4, "n_jobs": -1}
        if not tuned:
            params = {"n_estimators": 300, "n_jobs": -1}
        return RandomForestRegressor(**params, random_state=42)
    if name == "gradient_boosting":
        params = {"n_estimators": 400, "learning_rate": 0.06, "max_depth": 5, "subsample": 0.9}
        if not tuned:
            params = {"n_estimators": 300, "max_depth": 4, "learning_rate": 0.08}
        return GradientBoostingRegressor(**params, random_state=42)

    if name in {"xgboost", "lightgbm", "catboost"}:
        if name == "xgboost":
            from xgboost import XGBRegressor

            params = {"n_estimators": 400, "max_depth": 7, "learning_rate": 0.05, "subsample": 0.9}
            if not tuned:
                params = {"n_estimators": 300, "max_depth": 6, "learning_rate": 0.08}
            return XGBRegressor(**params, random_state=42, n_jobs=-1, verbosity=0)
        if name == "lightgbm":
            from lightgbm import LGBMRegressor

            params = {
                "n_estimators": 400,
                "num_leaves": 63,
                "learning_rate": 0.05,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
            }
            if not tuned:
                params = {"n_estimators": 300, "num_leaves": 40, "learning_rate": 0.08}
            return LGBMRegressor(**params, random_state=42, n_jobs=-1, verbose=-1)
        if name == "catboost":
            from catboost import CatBoostRegressor

            params = {"iterations": 400, "depth": 8, "learning_rate": 0.05, "verbose": False}
            if not tuned:
                params = {"iterations": 300, "depth": 6, "learning_rate": 0.08, "verbose": False}
            return CatBoostRegressor(**params, random_seed=42, thread_count=-1)

    raise ValueError(f"Unknown model: {name}")


def build_all_models():
    """Return a list of (name, model) for every candidate model."""
    return [(name, build_model(name)) for name in MODEL_NAMES]
