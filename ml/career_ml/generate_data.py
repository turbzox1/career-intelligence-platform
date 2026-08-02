"""Synthetic salary dataset generator.

Generates a realistic, deterministic salary dataset with the same signal
structure the platform expects in production. The generator models salary as
a function of experience, degree, location, industry, company size, title and
skill coverage, then adds heteroscedastic noise.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from career_ml.features import (
    COMPANY_SIZES,
    DEGREE_LEVELS,
    INDUSTRIES,
    INDUSTRY_MULTIPLIER,
    LOCATION_MULTIPLIER,
    LOCATIONS,
    SKILL_SALARY_DELTA,
    TITLE_BASE_SALARY,
    TITLES,
)

ALL_SKILLS = list(SKILL_SALARY_DELTA.keys())

# Skills more likely to appear for each title.
TITLE_AFFINITY: dict[str, list[str]] = {
    "software_engineer": [
        "Python",
        "Java",
        "TypeScript",
        "React",
        "Node.js",
        "PostgreSQL",
        "Redis",
        "Docker",
        "FastAPI",
        "Next.js",
    ],
    "data_scientist": [
        "Python",
        "Machine Learning",
        "TensorFlow",
        "PyTorch",
        "NLP",
        "SQL",
        "Pandas",
        "NumPy",
        "scikit-learn",
        "SHAP",
    ],
    "ml_engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "PyTorch",
        "TensorFlow",
        "MLflow",
        "Docker",
        "Kubernetes",
        "LLM",
        "RAG",
    ],
    "devops_engineer": [
        "AWS",
        "Docker",
        "Kubernetes",
        "Terraform",
        "CI/CD",
        "Linux",
        "Prometheus",
        "Grafana",
        "Ansible",
        "Helm",
    ],
    "product_manager": [
        "Product Management",
        "Analytics",
        "Agile",
        "Jira",
        "SQL",
        "Figma",
        "A/B Testing",
        "Stakeholder Management",
    ],
    "data_engineer": ["Python", "SQL", "Spark", "Kafka", "Airflow", "Snowflake", "dbt", "ETL", "PostgreSQL", "AWS"],
    "backend_engineer": [
        "Python",
        "Java",
        "Go",
        "PostgreSQL",
        "Redis",
        "Docker",
        "Kafka",
        "REST APIs",
        "Celery",
        "MongoDB",
    ],
    "frontend_engineer": [
        "JavaScript",
        "TypeScript",
        "React",
        "Next.js",
        "Vue.js",
        "Tailwind CSS",
        "GraphQL",
        "Redux",
        "Jest",
    ],
    "fullstack_engineer": [
        "JavaScript",
        "TypeScript",
        "React",
        "Node.js",
        "PostgreSQL",
        "Docker",
        "Next.js",
        "GraphQL",
        "FastAPI",
    ],
    "site_reliability_engineer": [
        "AWS",
        "Kubernetes",
        "Docker",
        "Prometheus",
        "Grafana",
        "Linux",
        "Terraform",
        "Go",
        "CI/CD",
    ],
}

DEGREE_DECAY = {level: i for i, level in enumerate(DEGREE_LEVELS)}
COMPANY_DECAY = {size: i for i, size in enumerate(COMPANY_SIZES)}


def _skill_sample(rng: np.random.Generator, title: str, years: float) -> list[str]:
    """Sample a realistic skill set for a given title and seniority."""
    affinity = TITLE_AFFINITY.get(title, ["Python"])
    rng.shuffle(affinity)
    base_count = int(min(3 + years / 2, len(affinity) + 2))
    chosen = affinity[:base_count]
    extras = [s for s in ALL_SKILLS if s not in chosen]
    rng.shuffle(extras)
    chosen.extend(extras[: max(0, base_count - len(chosen))])
    return list(dict.fromkeys(chosen))


def generate_dataset(n_samples: int = 12_000, *, seed: int = 42) -> pd.DataFrame:
    """Generate a deterministic synthetic salary dataset."""
    rng = np.random.default_rng(seed)
    rows: list[dict] = []

    titles = rng.choice(TITLES, size=n_samples, p=None)
    for i in range(n_samples):
        title = str(titles[i])
        years = float(np.round(rng.gamma(shape=2.2, scale=2.6), 1))
        years = min(years, 35.0)
        degree = str(rng.choice(DEGREE_LEVELS, p=[0.08, 0.15, 0.40, 0.30, 0.07]))
        location = str(rng.choice(LOCATIONS))
        industry = str(rng.choice(INDUSTRIES))
        company_size = str(rng.choice(COMPANY_SIZES, p=[0.10, 0.25, 0.30, 0.25, 0.10]))
        skills = _skill_sample(rng, title, years)

        base = TITLE_BASE_SALARY[title]
        exp_growth = 1.0 + 0.045 * years + 0.0012 * years**2
        degree_factor = 1.0 + 0.03 * DEGREE_DECAY[degree]
        company_factor = 0.90 + 0.05 * COMPANY_DECAY[company_size]
        location_factor = LOCATION_MULTIPLIER[location]
        industry_factor = INDUSTRY_MULTIPLIER[industry]
        skill_bonus = sum(SKILL_SALARY_DELTA.get(s, 0) for s in skills)

        salary = base * exp_growth * degree_factor * company_factor * location_factor * industry_factor + skill_bonus
        # Heteroscedastic noise: senior roles have larger variance.
        noise_std = salary * (0.06 + 0.004 * years)
        salary = float(salary + rng.normal(0, noise_std))
        salary = max(salary, 35_000.0)

        rows.append(
            {
                "title": title,
                "years_experience": years,
                "degree_level": degree,
                "location": location,
                "industry": industry,
                "company_size": company_size,
                "skills": skills,
                "skill_count": len(skills),
                "salary": salary,
            }
        )

    return pd.DataFrame(rows)


def save_dataset(df: pd.DataFrame, path: str) -> None:
    """Persist the dataset to CSV for later ingestion."""
    from pathlib import Path

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)


def load_dataset(path: str) -> pd.DataFrame:
    """Load a dataset from CSV, restoring the skill list column."""
    df = pd.read_csv(path)
    df["skills"] = df["skills"].apply(lambda v: str(v).split("|") if isinstance(v, str) else [])
    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate the synthetic salary dataset")
    parser.add_argument("--n", type=int, default=12_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="data/processed/salary_dataset.csv")
    args = parser.parse_args()

    data = generate_dataset(args.n, seed=args.seed)
    save_dataset(data, args.output)
    print(f"Generated {len(data)} rows -> {args.output}")
