"""Database seeding: master skills, demo jobs and a demo admin user."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.data.skills_master import SKILL_CATALOG
from app.models.job import Job
from app.models.resume import Skill
from app.models.user import ROLE_ADMIN, User

logger = logging.getLogger("app.db.seed")

DEMO_JOBS = [
    {
        "external_key": "demo-senior-ml-engineer",
        "title": "Senior Machine Learning Engineer",
        "company": "Acme AI",
        "location": "San Francisco",
        "description": (
            "We are hiring a Senior Machine Learning Engineer to build production ML "
            "systems. Required: strong Python, Machine Learning, Deep Learning, PyTorch "
            "or TensorFlow, Docker, Kubernetes, and AWS. Experience with NLP, LLMs and "
            "MLflow is a plus. Nice to have: RAG, MLOps, CI/CD, Spark."
        ),
        "skills": [
            "Python",
            "Machine Learning",
            "Deep Learning",
            "PyTorch",
            "TensorFlow",
            "Docker",
            "Kubernetes",
            "AWS",
            "NLP",
            "MLflow",
            "CI/CD",
            "Spark",
            "LLM",
        ],
        "salary_min": 160000.0,
        "salary_max": 210000.0,
        "source_url": "",
    },
    {
        "external_key": "demo-data-scientist",
        "title": "Data Scientist",
        "company": "Globex Analytics",
        "location": "New York",
        "description": (
            "Data Scientist role focused on predictive modeling and experimentation. "
            "Skills: Python, SQL, scikit-learn, Pandas, NumPy, Machine Learning, "
            "Statistical Analysis, A/B Testing, Tableau. Knowledge of XGBoost, LightGBM "
            "and feature engineering is expected."
        ),
        "skills": [
            "Python",
            "SQL",
            "scikit-learn",
            "Pandas",
            "NumPy",
            "Machine Learning",
            "Statistical Analysis",
            "A/B Testing",
            "Tableau",
            "XGBoost",
            "LightGBM",
            "Feature Engineering",
        ],
        "salary_min": 130000.0,
        "salary_max": 170000.0,
        "source_url": "",
    },
    {
        "external_key": "demo-backend-engineer",
        "title": "Backend Engineer",
        "company": "Initech Systems",
        "location": "Remote",
        "description": (
            "Backend Engineer to design scalable REST APIs. Required: Python or Go, "
            "PostgreSQL, Redis, Docker, REST APIs, Kafka. Experience with FastAPI, "
            "Celery, and AWS is valued."
        ),
        "skills": ["Python", "Go", "PostgreSQL", "Redis", "Docker", "REST APIs", "Kafka", "FastAPI", "Celery", "AWS"],
        "salary_min": 120000.0,
        "salary_max": 155000.0,
        "source_url": "",
    },
    {
        "external_key": "demo-data-engineer",
        "title": "Data Engineer",
        "company": "Umbrella Data",
        "location": "Seattle",
        "description": (
            "Data Engineer for streaming and batch pipelines. Skills: Python, SQL, Spark, "
            "Kafka, Airflow, dbt, Snowflake, AWS, ETL. Knowledge of ClickHouse and "
            "PostgreSQL is a bonus."
        ),
        "skills": [
            "Python",
            "SQL",
            "Spark",
            "Kafka",
            "Airflow",
            "dbt",
            "Snowflake",
            "AWS",
            "ETL",
            "PostgreSQL",
            "ClickHouse",
        ],
        "salary_min": 125000.0,
        "salary_max": 165000.0,
        "source_url": "",
    },
    {
        "external_key": "demo-devops-engineer",
        "title": "DevOps Engineer",
        "company": "Cyberdyne Cloud",
        "location": "Austin",
        "description": (
            "DevOps engineer owning CI/CD and infrastructure. Required: Linux, Docker, "
            "Kubernetes, Terraform, CI/CD, AWS, Prometheus, Grafana. Experience with "
            "Ansible, Helm, and GitHub Actions preferred."
        ),
        "skills": [
            "Linux",
            "Docker",
            "Kubernetes",
            "Terraform",
            "CI/CD",
            "AWS",
            "Prometheus",
            "Grafana",
            "Ansible",
            "Helm",
            "GitHub Actions",
        ],
        "salary_min": 115000.0,
        "salary_max": 150000.0,
        "source_url": "",
    },
    {
        "external_key": "demo-frontend-engineer",
        "title": "Frontend Engineer",
        "company": "Stark Industries",
        "location": "London",
        "description": (
            "Frontend engineer for a design system. Skills: JavaScript, TypeScript, React, "
            "Next.js, Tailwind CSS, GraphQL, Redux, Jest. Experience with accessibility "
            "and shadcn/ui is appreciated."
        ),
        "skills": ["JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS", "GraphQL", "Redux", "Jest"],
        "salary_min": 90000.0,
        "salary_max": 130000.0,
        "source_url": "",
    },
]


def seed_skills(db: Session) -> int:
    """Insert the master skill catalog if absent. Returns inserted count."""
    existing = {row.name for row in db.scalars(select(Skill.name)).all()}
    inserted = 0
    for name, (category, weight, aliases) in SKILL_CATALOG.items():
        if name not in existing:
            db.add(Skill(name=name, category=category, aliases=aliases, weight=weight))
            inserted += 1
    db.commit()
    if inserted:
        logger.info("skills_seeded", extra={"count": inserted})
    return inserted


def seed_jobs(db: Session) -> int:
    """Insert demo jobs if absent. Returns inserted count."""
    existing = {row.external_key for row in db.scalars(select(Job.external_key)).all()}
    inserted = 0
    for job_data in DEMO_JOBS:
        if job_data["external_key"] not in existing:
            db.add(Job(**job_data))
            inserted += 1
    db.commit()
    if inserted:
        logger.info("jobs_seeded", extra={"count": inserted})
    return inserted


def seed_admin(db: Session, *, email: str = "admin@careerintel.io", password: str = "Admin123!") -> User:
    """Create a demo admin user if absent."""
    from app.repositories.user_repo import UserRepository

    repo = UserRepository(db)
    user = repo.get_by_email(email)
    if user is None:
        user = repo.create(
            email=email,
            full_name="Platform Admin",
            hashed_password=hash_password(password),
            role=ROLE_ADMIN,
            is_active=True,
        )
        db.commit()
        db.refresh(user)
        logger.info("admin_seeded", extra={"email": email})
    return user


def seed_all(db: Session) -> dict[str, int]:
    """Run all seeders and return counts."""
    return {
        "skills": seed_skills(db),
        "jobs": seed_jobs(db),
    }
