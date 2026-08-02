"""End-to-end model training pipeline.

Runs dataset ingestion, feature engineering, candidate comparison via
cross-validation, optional hyper-parameter tuning, final training, artifact
persistence and MLflow tracking.

Usage (from the repo root):
    python -m pipeline.train --data ml/data/processed/salary_dataset.csv \
        --output ml/models/trained --tune
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

# Allow `python -m pipeline.train` and bare `python ml/pipeline/train.py`.
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from career_ml.features import FEATURE_SPEC, build_feature_vector, feature_names
from career_ml.metrics import (
    cross_validate_model,
    regression_metrics,
)
from career_ml.model_builders import build_all_models, build_model
from pipeline.tracking import (
    configure_experiment,
    log_metrics,
    register_model,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("pipeline.train")


def build_matrix(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Build the feature matrix and target vector from a dataset."""
    rows = []
    for _, row in df.iterrows():
        rows.append(
            build_feature_vector(
                years_experience=float(row["years_experience"]),
                degree=str(row["degree_level"]),
                location=str(row["location"]),
                industry=str(row["industry"]),
                company_size=str(row["company_size"]),
                title=str(row["title"]),
                skills=list(row.get("skills") or []),
            )
        )
    X = np.vstack(rows)
    y = df["salary"].to_numpy(dtype=float)
    return X, y


def load_data(path: str) -> pd.DataFrame:
    """Load the raw CSV dataset."""
    df = pd.read_csv(path)
    required = {"years_experience", "degree_level", "location", "industry", "company_size", "title", "salary"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {sorted(missing)}")
    if "skills" in df.columns:
        df["skills"] = df["skills"].apply(lambda v: str(v).split("|") if isinstance(v, str) and v else [])
    else:
        df["skills"] = [[] for _ in range(len(df))]
    return df


def compare_models(X: np.ndarray, y: np.ndarray, cv: int) -> pd.DataFrame:
    """Cross-validate every candidate model and return a comparison table."""
    results = []
    for name, model in build_all_models():
        logger.info("cross_validating %s", name)
        try:
            metrics = cross_validate_model(model, X, y, cv=cv)
            # Fit once on the full data for a hold-out style sanity check.
            results.append({"model": name, **metrics})
        except Exception as exc:  # pragma: no cover - optional libs may be absent
            logger.warning("model %s failed: %s", name, exc)
            results.append({"model": name, "error": str(exc)})
    return pd.DataFrame(results)


def tune_best(name: str, X: np.ndarray, y: np.ndarray) -> object:
    """Run a small randomized search over the winning model's hyper-parameters."""
    from scipy.stats import randint, uniform
    from sklearn.model_selection import RandomizedSearchCV

    logger.info("tuning %s", name)
    param_grid: dict = {}
    if name == "random_forest":
        param_grid = {
            "n_estimators": randint(200, 600),
            "max_depth": randint(10, 30),
            "min_samples_leaf": randint(2, 8),
        }
    elif name == "gradient_boosting":
        param_grid = {
            "n_estimators": randint(200, 500),
            "learning_rate": uniform(0.02, 0.1),
            "max_depth": randint(3, 8),
            "subsample": uniform(0.7, 0.3),
        }
    elif name == "xgboost":
        param_grid = {
            "n_estimators": randint(200, 600),
            "learning_rate": uniform(0.02, 0.1),
            "max_depth": randint(4, 10),
            "subsample": uniform(0.7, 0.3),
        }
    elif name == "lightgbm":
        param_grid = {
            "n_estimators": randint(200, 600),
            "num_leaves": randint(16, 128),
            "learning_rate": uniform(0.02, 0.1),
        }
    elif name == "catboost":
        param_grid = {
            "iterations": randint(200, 600),
            "depth": randint(4, 10),
            "learning_rate": uniform(0.02, 0.1),
        }
    else:
        return build_model(name, tuned=True)

    base = build_model(name)
    search = RandomizedSearchCV(
        base,
        param_grid,
        n_iter=15,
        cv=3,
        scoring="r2",
        n_jobs=-1,
        random_state=42,
        verbose=0,
    )
    search.fit(X, y)
    logger.info("best params for %s: %s", name, search.best_params_)
    return search.best_estimator_


def save_artifact(model, meta: dict, output_dir: str) -> Path:
    """Persist the model and metadata to disk."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model_path = out / "model.joblib"
    joblib.dump(model, model_path)
    (out / "metadata.json").write_text(json.dumps(meta, indent=2, default=str))
    return model_path


def run(args: argparse.Namespace) -> None:
    df = load_data(args.data)
    X, y = build_matrix(df)
    logger.info("feature matrix shape: %s", X.shape)

    comparison = compare_models(X, y, cv=args.cv)
    comparison.to_csv(Path(args.output_dir) / "model_comparison.csv", index=False)
    logger.info("\n%s", comparison.to_string(index=False))

    valid = (
        comparison[comparison.get("error", pd.Series(dtype=str)).isna()]
        if "error" in comparison.columns
        else comparison
    )
    best_name = valid.sort_values("cv_r2_mean", ascending=False).iloc[0]["model"]
    best_cv_metrics = valid.sort_values("cv_r2_mean", ascending=False).iloc[0].to_dict()
    logger.info("best model: %s", best_name)

    final_model = tune_best(best_name, X, y) if args.tune else build_model(best_name, tuned=True)
    final_model.fit(X, y)

    # Residual-based prediction intervals (90% coverage => z ~ 1.645).
    train_preds = final_model.predict(X)
    residuals = y - train_preds
    residual_std = float(np.std(residuals))

    final_metrics = regression_metrics(y, train_preds)
    logger.info("final metrics on training data: %s", final_metrics)

    metadata = {
        "model_name": best_name,
        "model_version": args.version,
        "trained_at": pd.Timestamp.utcnow().isoformat(),
        "n_samples": len(df),
        "feature_spec_length": FEATURE_SPEC.expected_length,
        "feature_names": feature_names(),
        "categorical_levels": FEATURE_SPEC.onehot_levels,
        "metrics": final_metrics,
        "cv_metrics": {k: round(float(v), 4) for k, v in best_cv_metrics.items() if k != "model"},
        "residual_std": round(residual_std, 2),
        "baseline_mae": round(float(np.mean(np.abs(residuals))), 2),
    }

    model_path = save_artifact(final_model, metadata, args.output_dir)
    logger.info("artifact saved to %s", model_path)

    # MLflow tracking (graceful when the server is offline).
    try:
        configure_experiment(args.experiment)
        with mlflow.start_run(run_name=f"{best_name}-{args.version}"):
            mlflow.log_params({"model": best_name, "tuned": args.tune, "cv_folds": args.cv})
            log_metrics({**final_metrics, **metadata["cv_metrics"]})
            mlflow.log_artifact(str(model_path))
            mlflow.log_artifact(str(Path(args.output_dir) / "model_comparison.csv"))
            mlflow.sklearn.log_model(final_model, artifact_path="model")
            version = register_model(mlflow.active_run().info.run_id, "salary-predictor")
        logger.info("logged to mlflow, model version=%s", version)
    except Exception as exc:  # pragma: no cover
        logger.warning("mlflow logging skipped: %s", exc)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the salary prediction model")
    parser.add_argument("--data", default="ml/data/processed/salary_dataset.csv")
    parser.add_argument("--output-dir", default="ml/models/trained")
    parser.add_argument("--experiment", default=os.getenv("MLFLOW_EXPERIMENT_NAME", "salary-prediction"))
    parser.add_argument("--cv", type=int, default=5)
    parser.add_argument("--tune", action="store_true", help="run hyper-parameter tuning on the best model")
    parser.add_argument("--version", default="1.0.0")
    return parser.parse_args(argv)


if __name__ == "__main__":
    import mlflow

    run(parse_args())
