"""Shared salary-prediction feature engineering.

Single source of truth for feature definitions used BOTH at training time
(in ``ml/pipeline``) and at inference time (in ``backend/app/ml``). Keeping
the categorical levels and skill weights here guarantees train/serve skew is
minimised.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# --- Categorical levels (must stay in sync with the API validation layer) ---
DEGREE_LEVELS = ["none", "associate", "bachelor", "master", "phd"]
COMPANY_SIZES = ["startup", "small", "mid", "large", "enterprise"]
LOCATIONS = [
    "remote",
    "san_francisco",
    "new_york",
    "seattle",
    "austin",
    "london",
    "bengaluru",
    "berlin",
    "toronto",
    "singapore",
]
INDUSTRIES = [
    "technology",
    "finance",
    "healthcare",
    "retail",
    "manufacturing",
    "consulting",
    "education",
    "media",
    "energy",
]
TITLES = [
    "software_engineer",
    "data_scientist",
    "ml_engineer",
    "devops_engineer",
    "product_manager",
    "data_engineer",
    "backend_engineer",
    "frontend_engineer",
    "fullstack_engineer",
    "site_reliability_engineer",
]

# --- Ordinal mappings ---
DEGREE_ORDINAL = {level: idx for idx, level in enumerate(DEGREE_LEVELS)}
COMPANY_SIZE_ORDINAL = {size: idx for idx, size in enumerate(COMPANY_SIZES)}

# --- Location salary multipliers (used by the synthetic data generator) ---
LOCATION_MULTIPLIER = {
    "remote": 0.95,
    "san_francisco": 1.35,
    "new_york": 1.30,
    "seattle": 1.20,
    "austin": 1.05,
    "london": 1.25,
    "bengaluru": 0.55,
    "berlin": 1.10,
    "toronto": 1.00,
    "singapore": 1.05,
}

# --- Industry multipliers ---
INDUSTRY_MULTIPLIER = {
    "technology": 1.10,
    "finance": 1.25,
    "healthcare": 1.00,
    "retail": 0.85,
    "manufacturing": 0.90,
    "consulting": 1.15,
    "education": 0.75,
    "media": 0.90,
    "energy": 1.05,
}

# --- Title base salaries (USD, annual) ---
TITLE_BASE_SALARY = {
    "software_engineer": 115_000,
    "data_scientist": 125_000,
    "ml_engineer": 140_000,
    "devops_engineer": 120_000,
    "product_manager": 130_000,
    "data_engineer": 125_000,
    "backend_engineer": 120_000,
    "frontend_engineer": 105_000,
    "fullstack_engineer": 112_000,
    "site_reliability_engineer": 135_000,
}

# --- Skill salary deltas (USD) ---
SKILL_SALARY_DELTA = {
    "Python": 8_000,
    "Java": 7_000,
    "TypeScript": 6_000,
    "React": 5_000,
    "AWS": 10_000,
    "Kubernetes": 9_000,
    "Docker": 6_000,
    "TensorFlow": 8_000,
    "PyTorch": 8_000,
    "Machine Learning": 12_000,
    "Deep Learning": 10_000,
    "NLP": 9_000,
    "Spark": 9_000,
    "Kafka": 8_000,
    "PostgreSQL": 5_000,
    "Redis": 3_000,
    "MongoDB": 3_000,
    "LLM": 12_000,
    "RAG": 8_000,
    "FastAPI": 4_000,
    "Django": 4_000,
    "Terraform": 8_000,
    "CI/CD": 5_000,
    "Golang": 8_000,
    "Rust": 8_000,
    "Snowflake": 7_000,
    "Airflow": 6_000,
    "GraphQL": 4_000,
    "Next.js": 4_000,
    "Node.js": 4_000,
}

# Order of features in the model input vector.
NUMERIC_FEATURES = [
    "years_experience",
    "skill_count",
    "degree_ordinal",
    "company_size_ordinal",
]

# One-hot categorical feature names.
ONEHOT_FEATURES = ["location", "industry", "title"]

ALL_FEATURE_GROUPS = ("numeric", "onehot")


@dataclass(frozen=True)
class FeatureSpec:
    """Describes the full set of features the model expects."""

    numeric: list[str] = field(default_factory=lambda: list(NUMERIC_FEATURES))
    onehot: list[str] = field(default_factory=lambda: list(ONEHOT_FEATURES))
    onehot_levels: dict[str, list[str]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "onehot_levels",
            {
                "location": LOCATIONS,
                "industry": INDUSTRIES,
                "title": TITLES,
            },
        )

    @property
    def expected_length(self) -> int:
        onehot_len = sum(len(levels) for levels in self.onehot_levels.values())
        return len(self.numeric) + onehot_len


FEATURE_SPEC = FeatureSpec()


def encode_ordinal(degree: str, company_size: str) -> tuple[int, int]:
    """Encode ordinal categorical features to integers."""
    return (
        DEGREE_ORDINAL.get(degree, 0),
        COMPANY_SIZE_ORDINAL.get(company_size, 2),
    )


def onehot_encode(value: str, levels: list[str]) -> list[float]:
    """One-hot encode a categorical value against known levels."""
    vector = [0.0] * len(levels)
    try:
        idx = levels.index(value)
        vector[idx] = 1.0
    except ValueError:
        pass  # unknown category -> all-zero vector
    return vector


def skill_delta(skills: list[str]) -> float:
    """Sum of known skill salary deltas (clamped to avoid extreme tails)."""
    if not skills:
        return 0.0
    return float(min(sum(SKILL_SALARY_DELTA.get(skill, 0.0) for skill in skills), 60_000))


def build_feature_vector(
    *,
    years_experience: float,
    degree: str,
    location: str,
    industry: str,
    company_size: str,
    title: str,
    skills: list[str],
) -> np.ndarray:
    """Build the numeric model input vector for a single prediction."""
    degree_ord, company_ord = encode_ordinal(degree, company_size)
    numeric = [
        float(years_experience),
        float(len(skills)),
        float(degree_ord),
        float(company_ord),
    ]
    onehot: list[float] = []
    for feature in ONEHOT_FEATURES:
        value = {
            "location": location,
            "industry": industry,
            "title": title,
        }[feature]
        onehot.extend(onehot_encode(value, FEATURE_SPEC.onehot_levels[feature]))
    return np.asarray(numeric + onehot, dtype=np.float64)


def feature_names() -> list[str]:
    """Return human-readable feature names for the vector (used in SHAP)."""
    names = list(NUMERIC_FEATURES)
    for feature in ONEHOT_FEATURES:
        names.extend(f"{feature}={level}" for level in FEATURE_SPEC.onehot_levels[feature])
    return names
