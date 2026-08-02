"""SHAP explainability wrapper.

Computes feature contributions for a single prediction using the loaded
model. Falls back to a deterministic gradient approximation when the `shap`
package or TreeExplainer is unavailable (e.g. for the baseline model).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np

from app.ml.model_loader import get_model

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("app.ml.explainer")


def explain_prediction(features_vector: np.ndarray, raw: dict, feature_names: list[str]) -> dict:
    """Return a serialisable explanation payload for a prediction."""
    loaded = get_model()
    base_value = _base_value(raw)

    if not loaded.is_baseline:
        try:
            return _shap_explanation(loaded, features_vector, feature_names, base_value)
        except Exception as exc:  # pragma: no cover - shap may be missing
            logger.warning("shap explanation failed, using fallback: %s", exc)

    contributions = (
        _gradient_fallback(loaded.pipeline, features_vector, feature_names, raw)
        if not loaded.is_baseline
        else _baseline_contributions(raw, feature_names, features_vector)
    )
    return {
        "base_value": round(float(base_value), 2),
        "predicted_value": round(float(_predicted_value(loaded, features_vector, raw)), 2),
        "features": [
            {"feature": name, "value": float(v), "contribution": round(float(c), 2)} for name, v, c in contributions
        ],
        "waterfall": [
            {"feature": name, "value": float(v), "contribution": round(float(c), 2)}
            for name, v, c in sorted(contributions, key=lambda x: -abs(x[2]))
        ],
    }


def _shap_explanation(loaded, vector: np.ndarray, names: list[str], base_value: float) -> dict:
    import shap

    explainer = shap.TreeExplainer(loaded.pipeline)
    shap_values = explainer.shap_values(vector.reshape(1, -1))
    contributions = shap_values[0] if isinstance(shap_values, list) else shap_values
    contributions = np.asarray(contributions).ravel()

    features = [
        {"feature": name, "value": float(vector[idx]), "contribution": float(contributions[idx])}
        for idx, name in enumerate(names)
    ]
    return {
        "base_value": round(
            float(explainer.expected_value)
            if not isinstance(explainer.expected_value, (list, np.ndarray))
            else float(np.asarray(explainer.expected_value).ravel()[0]),
            2,
        ),
        "predicted_value": round(
            float(
                np.sum(contributions)
                + (
                    explainer.expected_value
                    if not isinstance(explainer.expected_value, (list, np.ndarray))
                    else np.asarray(explainer.expected_value).ravel()[0]
                )
            ),
            2,
        ),
        "features": features,
        "waterfall": sorted(features, key=lambda x: -abs(x["contribution"])),
    }


def _gradient_fallback(pipeline, vector: np.ndarray, names: list[str], raw: dict) -> list[tuple]:
    """Perturbation-based contribution estimate for non-tree models."""
    base_pred = float(pipeline.predict(vector.reshape(1, -1))[0])
    result: list[tuple] = []
    for idx, name in enumerate(names):
        perturbed = vector.copy()
        perturbed[idx] = 0.0
        pred = float(pipeline.predict(perturbed.reshape(1, -1))[0])
        result.append((name, float(vector[idx]), base_pred - pred))
    return result


def _baseline_contributions(raw: dict, names: list[str], vector: np.ndarray) -> list[tuple]:
    """Explain the baseline model using its own internal multipliers."""
    from career_ml.features import (
        COMPANY_SIZE_ORDINAL,
        INDUSTRY_MULTIPLIER,
        LOCATION_MULTIPLIER,
        TITLE_BASE_SALARY,
    )

    title = raw.get("title", "software_engineer")
    base = TITLE_BASE_SALARY.get(title, 110_000.0)
    contributions: list[tuple] = []

    location = raw.get("location", "remote")
    loc_mul = LOCATION_MULTIPLIER.get(location, 1.0)
    contributions.append(("location=" + location, 0.0, (loc_mul - 1.0) * base))

    industry = raw.get("industry", "technology")
    ind_mul = INDUSTRY_MULTIPLIER.get(industry, 1.0)
    contributions.append(("industry=" + industry, 0.0, (ind_mul - 1.0) * base))

    size = raw.get("company_size", "mid")
    idx = COMPANY_SIZE_ORDINAL.get(size, 2)
    contributions.append(("company_size", float(idx), (0.05 * idx) * base))

    years = float(raw.get("years_experience", 0.0))
    exp_effect = (1.0 + 0.045 * years + 0.0012 * years * years - 1.0) * base
    contributions.append(("years_experience", years, exp_effect))

    return contributions


def _base_value(raw: dict) -> float:
    try:
        from career_ml.features import TITLE_BASE_SALARY

        return float(TITLE_BASE_SALARY.get(raw.get("title", "software_engineer"), 110_000.0))
    except ImportError:  # pragma: no cover
        return 110_000.0


def _predicted_value(loaded, vector: np.ndarray, raw: dict) -> float:
    if not loaded.is_baseline:
        return float(loaded.pipeline.predict(vector.reshape(1, -1))[0])
    from career_ml.baseline import BaselineSalaryModel

    return float(BaselineSalaryModel().predict(**raw).salary)
