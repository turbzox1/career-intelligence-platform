"""Salary prediction runtime wrapper.

Wraps the trained pipeline (or baseline) and produces predictions together
with confidence intervals and SHAP-style explanations.
"""

from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.core.exceptions import ModelNotReadyError
from app.ml.model_loader import get_model

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("app.ml.salary_model")

Z_90 = 1.645


@dataclass
class PredictionOutput:
    salary: float
    lower_bound: float
    upper_bound: float
    confidence: float
    model_name: str
    model_version: str


class SalaryPredictor:
    """Predicts annual salary from structured features."""

    def predict(self, *, features_vector: np.ndarray, raw: dict) -> PredictionOutput:
        loaded = get_model()
        if loaded.is_baseline:
            return self._predict_baseline(raw)

        try:
            prediction = float(loaded.pipeline.predict(features_vector.reshape(1, -1))[0])
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("model inference failed", exc_info=exc)
            raise ModelNotReadyError("Model inference failed, please try again later") from exc

        residual_std = float(loaded.metadata.get("residual_std", prediction * 0.10))
        interval = Z_90 * max(residual_std, prediction * 0.05)
        return PredictionOutput(
            salary=round(prediction, 2),
            lower_bound=round(max(prediction - interval, 0), 2),
            upper_bound=round(prediction + interval, 2),
            confidence=self._confidence(prediction, residual_std),
            model_name=loaded.model_name,
            model_version=loaded.model_version,
        )

    @staticmethod
    def _predict_baseline(raw: dict) -> PredictionOutput:
        try:
            from career_ml.baseline import BaselineSalaryModel
        except ImportError as exc:  # pragma: no cover
            raise ModelNotReadyError("Salary model is not yet available") from exc

        result = BaselineSalaryModel().predict(**raw)
        return PredictionOutput(
            salary=result.salary,
            lower_bound=result.lower_bound,
            upper_bound=result.upper_bound,
            confidence=result.confidence,
            model_name="baseline",
            model_version="1.0.0",
        )

    @staticmethod
    def _confidence(prediction: float, residual_std: float) -> float:
        """Confidence based on relative residual magnitude (higher = worse)."""
        if prediction <= 0:
            return 0.0
        cv = residual_std / prediction
        # Map cv in [0.02, 0.25] to confidence in [0.99, 0.70].
        return round(float(np.clip(1.0 - (cv - 0.02) * 1.3, 0.70, 0.99)), 2)
