"""Salary prediction service orchestrating ML inference and persistence."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.ml.explainer import explain_prediction
from app.ml.salary_model import SalaryPredictor
from app.models.prediction import Prediction, PredictionHistory
from app.models.user import User
from app.repositories.prediction_repo import PredictionRepository
from app.repositories.resume_repo import ResumeRepository
from app.schemas.prediction import SalaryPredictionRequest, SalaryPredictionResponse

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger("app.services.salary_predictor")


class SalaryPredictionService:
    """High-level salary prediction workflow."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.predictions = PredictionRepository(db)
        self.resumes = ResumeRepository(db)
        self._predictor = SalaryPredictor()

    def predict(self, user: User, payload: SalaryPredictionRequest) -> SalaryPredictionResponse:
        from career_ml.features import build_feature_vector, feature_names

        raw = {
            "years_experience": payload.years_experience,
            "degree": payload.degree_level,
            "location": payload.location,
            "industry": payload.industry,
            "company_size": payload.company_size,
            "title": payload.title,
            "skills": payload.skills,
        }
        vector = build_feature_vector(**raw)
        result = self._predictor.predict(features_vector=vector, raw=raw)

        resume_id = None
        if payload.resume_id is not None:
            resume = self.resumes.get_for_user(payload.resume_id, user.id)
            if resume is None:
                raise NotFoundError("Resume not found")
            resume_id = resume.id
            if not payload.skills:
                payload.skills = [rs.skill.name for rs in resume.skills]

        explanation = explain_prediction(vector, raw, feature_names())

        prediction = self.predictions.create(
            user_id=user.id,
            resume_id=resume_id,
            input_features={**raw, "resume_id": resume_id},
            predicted_salary=result.salary,
            lower_bound=result.lower_bound,
            upper_bound=result.upper_bound,
            confidence=result.confidence,
            model_name=result.model_name,
            model_version=result.model_version,
            explanation=explanation,
        )
        history = PredictionHistory(
            prediction_id=prediction.id,
            user_id=user.id,
            predicted_salary=result.salary,
            years_experience=payload.years_experience,
            location=payload.location,
            industry=payload.industry,
            title=payload.title,
            skill_count=len(payload.skills),
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(prediction)

        logger.info(
            "prediction_created",
            extra={
                "user_id": user.id,
                "salary": result.salary,
                "model": result.model_name,
            },
        )
        return SalaryPredictionResponse(
            prediction_id=prediction.id,
            predicted_salary=result.salary,
            lower_bound=result.lower_bound,
            upper_bound=result.upper_bound,
            confidence=result.confidence,
            model_name=result.model_name,
            model_version=result.model_version,
            explanation=explanation,
            input_features=dict(prediction.input_features),
            created_at=prediction.created_at,
        )

    def list_for_user(self, user: User, *, page: int, page_size: int) -> tuple[list[Prediction], int]:
        return self.predictions.list_for_user(user.id, page=page, page_size=page_size)

    def get_for_user(self, user: User, prediction_id: int) -> Prediction:
        prediction = self.predictions.get_for_user(prediction_id, user.id)
        if prediction is None:
            raise NotFoundError("Prediction not found")
        return prediction
