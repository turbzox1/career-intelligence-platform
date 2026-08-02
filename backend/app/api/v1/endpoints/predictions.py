"""Salary prediction endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbDep
from app.schemas.common import Page
from app.schemas.prediction import (
    PredictionHistoryItem,
    SalaryPredictionRequest,
    SalaryPredictionResponse,
)
from app.services.salary_predictor import SalaryPredictionService

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("/salary", response_model=SalaryPredictionResponse, status_code=status.HTTP_201_CREATED)
def predict_salary(
    payload: SalaryPredictionRequest,
    user: CurrentUser,
    db: DbDep,
) -> SalaryPredictionResponse:
    """Predict expected annual salary with confidence interval and explanation."""
    return SalaryPredictionService(db).predict(user, payload)


@router.get("", response_model=Page[PredictionHistoryItem])
def list_predictions(
    user: CurrentUser,
    db: DbDep,
    page: int = 1,
    page_size: int = 20,
) -> Page[PredictionHistoryItem]:
    """List the current user's prediction history."""
    items, total = SalaryPredictionService(db).list_for_user(user, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size
    return Page[PredictionHistoryItem](
        items=[PredictionHistoryItem.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{prediction_id}", response_model=SalaryPredictionResponse)
def get_prediction(prediction_id: int, user: CurrentUser, db: DbDep) -> SalaryPredictionResponse:
    """Retrieve a single prediction with its explanation."""
    prediction = SalaryPredictionService(db).get_for_user(user, prediction_id)
    return SalaryPredictionResponse(
        prediction_id=prediction.id,
        predicted_salary=prediction.predicted_salary,
        lower_bound=prediction.lower_bound,
        upper_bound=prediction.upper_bound,
        confidence=prediction.confidence,
        model_name=prediction.model_name,
        model_version=prediction.model_version,
        explanation=prediction.explanation,
        input_features=prediction.input_features,
        created_at=prediction.created_at,
    )
