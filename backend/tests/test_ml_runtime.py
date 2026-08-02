"""Runtime ML tests: baseline fallback and prediction bounds."""

from __future__ import annotations

from career_ml.baseline import BaselineSalaryModel
from career_ml.features import build_feature_vector

from app.ml.salary_model import SalaryPredictor

BASE_RAW = dict(
    years_experience=4.0,
    degree="bachelor",
    location="remote",
    industry="technology",
    company_size="mid",
    title="software_engineer",
    skills=["Python", "AWS"],
)


class TestBaselineModel:
    def test_predict_sane_range(self) -> None:
        model = BaselineSalaryModel()
        result = model.predict(**BASE_RAW)
        assert 40_000 <= result.salary <= 300_000
        assert result.lower_bound <= result.salary <= result.upper_bound
        assert 0 < result.confidence <= 1

    def test_experience_increases_salary(self) -> None:
        model = BaselineSalaryModel()
        junior = model.predict(**{**BASE_RAW, "years_experience": 1}).salary
        senior = model.predict(**{**BASE_RAW, "years_experience": 12}).salary
        assert senior > junior


class TestSalaryPredictor:
    def test_predictor_returns_bounds(self) -> None:
        vector = build_feature_vector(**BASE_RAW)
        result = SalaryPredictor().predict(features_vector=vector, raw=BASE_RAW)
        assert result.lower_bound <= result.salary <= result.upper_bound
        assert result.model_name in {
            "baseline",
            "catboost",
            "xgboost",
            "lightgbm",
            "gradient_boosting",
            "random_forest",
            "linear_regression",
        }
