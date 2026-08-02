"""MLflow tracking helpers for experiment logging and artifact registration."""

from __future__ import annotations

import logging
import os

import mlflow

logger = logging.getLogger("career_ml.tracking")

DEFAULT_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
DEFAULT_EXPERIMENT = os.getenv("MLFLOW_EXPERIMENT_NAME", "salary-prediction")


def configure_experiment(experiment_name: str | None = None) -> None:
    """Set the active MLflow experiment, creating it if necessary."""
    name = experiment_name or DEFAULT_EXPERIMENT
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", DEFAULT_TRACKING_URI))
    mlflow.set_experiment(name)
    logger.info("mlflow_experiment_configured", extra={"experiment": name})


def register_model(run_id: str, model_name: str) -> str:
    """Register a trained model in the MLflow model registry.

    Returns the model version string.
    """
    try:
        client = mlflow.tracking.MlflowClient()
        version = client.create_model_version(model_name, f"runs:/{run_id}/model")
        client.transition_model_version_stage(model_name, version.version, "Production", archive_existing_versions=True)
        return version.version
    except Exception as exc:  # pragma: no cover - registry may be unavailable
        logger.warning("model_registration_failed", extra={"error": str(exc)})
        return "local"


def log_metrics(metrics: dict[str, float]) -> None:
    """Log a flat metrics dict to the current MLflow run."""
    for key, value in metrics.items():
        mlflow.log_metric(key, value)
