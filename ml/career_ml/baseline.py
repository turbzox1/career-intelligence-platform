"""Cold-start baseline salary model.

Used when no trained artifact is available yet (fresh deployment) so the API
remains fully functional. It mirrors the same signal structure used by the
trained models, making predictions explainable and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass

from career_ml.features import (
    COMPANY_SIZE_ORDINAL,
    COMPANY_SIZES,
    DEGREE_LEVELS,
    INDUSTRY_MULTIPLIER,
    LOCATION_MULTIPLIER,
    SKILL_SALARY_DELTA,
    TITLE_BASE_SALARY,
)


@dataclass
class BaselineResult:
    salary: float
    lower_bound: float
    upper_bound: float
    confidence: float


class BaselineSalaryModel:
    """Interpretable heuristic salary estimator."""

    name = "baseline"
    version = "1.0.0"

    def predict(
        self,
        *,
        years_experience: float,
        degree: str,
        location: str,
        industry: str,
        company_size: str,
        title: str,
        skills: list[str] | None = None,
    ) -> BaselineResult:
        skills = skills or []
        base = TITLE_BASE_SALARY.get(title, 110_000.0)
        exp_growth = 1.0 + 0.045 * years_experience + 0.0012 * years_experience**2
        degree_factor = 1.0 + 0.03 * DEGREE_LEVELS.index(degree) if degree in DEGREE_LEVELS else 1.0
        company_idx = COMPANY_SIZE_ORDINAL.get(company_size, COMPANY_SIZES.index("mid"))
        company_factor = 0.90 + 0.05 * company_idx
        location_factor = LOCATION_MULTIPLIER.get(location, 1.0)
        industry_factor = INDUSTRY_MULTIPLIER.get(industry, 1.0)
        skill_bonus = min(sum(SKILL_SALARY_DELTA.get(s, 0.0) for s in skills), 60_000.0)

        salary = base * exp_growth * degree_factor * company_factor * location_factor * industry_factor + skill_bonus
        salary = max(salary, 35_000.0)
        # Baseline is intentionally more conservative about uncertainty.
        width = 0.12
        return BaselineResult(
            salary=round(salary, 2),
            lower_bound=round(salary * (1 - width), 2),
            upper_bound=round(salary * (1 + width), 2),
            confidence=0.90,
        )
