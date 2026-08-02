# Career Intelligence Platform

AI-powered career intelligence: machine-learning salary prediction with SHAP
explanations, resume parsing and skill extraction, skill-gap analysis,
personalized learning roadmaps, and semantic job matching — wrapped in a
production-grade FastAPI + Next.js application.

![Backend CI](https://img.shields.io/badge/build-backend%20CI-2ea44f) 
![Frontend CI](https://img.shields.io/badge/build-frontend%20CI-2ea44f)
![coverage](https://img.shields.io/badge/coverage-87%25-2ea44f)

---

## Features

| Feature | Description |
| --- | --- |
| **Salary prediction** | CatBoost model (R² ≈ 0.94) trained on a 10k-row synthetic labour-market dataset with confidence intervals and model-version transparency. |
| **Explainability** | SHAP-based per-feature contributions rendered as a waterfall chart — see *why* the model returned a number. |
| **Resume parsing** | Upload PDF, DOCX or TXT; extract name, contact details, experience, education, certifications and skills. |
| **Skill extraction** | Rule-based normalization against a master catalog of 200+ canonical skills with category and weight. |
| **Skill-gap analysis** | Compare your profile against a job description; get a match percentage and prioritized missing skills. |
| **Learning roadmaps** | Curated course catalog with estimated hours; auto-built prioritized roadmaps with weekly estimates. |
| **Job matching** | Sentence-embedding similarity between your profile and job postings, with matched/missing skill breakdown. |
| **Analytics** | Salary trends by date, location, industry and experience plus most-common/most-missing skills. |
| **Auth & security** | JWT access + refresh token rotation, device-aware sessions, bcrypt hashing, RBAC, rate limiting. |

## Tech Stack

- **Backend** — FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Redis, Celery, Pydantic v2
- **ML** — scikit-learn, CatBoost, LightGBM, XGBoost, SHAP, MLflow
- **Frontend** — Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui, Recharts
- **Ops** — Docker Compose, Prometheus, Grafana, GitHub Actions

## Repository Layout

```
.
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/           # Routers, dependencies, rate limiting
│   │   ├── core/          # Config, security, logging, exceptions
│   │   ├── db/            # Session, seed scripts
│   │   ├── data/          # Master skills catalog, learning catalog
│   │   ├── ml/            # Model loading, inference, SHAP explainer
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── repositories/  # Data-access layer
│   │   ├── schemas/       # Pydantic request/response models
│   │   ├── services/      # Business logic
│   │   └── worker/        # Celery app + tasks
│   ├── alembic/           # Database migrations
│   └── tests/             # 101 tests, ~87% coverage
├── ml/                    # Training pipeline
│   ├── career_ml/         # Feature engineering, metrics, model builders
│   ├── pipeline/          # Training entrypoint + MLflow tracking
│   ├── data/processed/    # salary_dataset.csv (10k rows)
│   └── models/trained/    # model.joblib + metadata
├── frontend/              # Next.js application
│   └── src/app/           # App Router pages (landing, auth, dashboard)
├── infra/                 # Dockerfiles, docker-compose, Prometheus, Grafana
├── scripts/               # Smoke test, seeding
└── .github/workflows/     # CI/CD pipelines
```

## Quick Start (Docker)

```bash
cd infra
cp .env.example .env            # set SECRET_KEY etc.
docker compose up --build
```

| Service | URL |
| --- | --- |
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| OpenAPI docs | http://localhost:8000/docs |
| MLflow | http://localhost:5000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 (admin/admin) |

Run migrations on first boot:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
```

## Quick Start (Local Development)

Prerequisites: Python 3.12–3.14, Node 22.

```bash
# Backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -e "backend[dev,ml]" -e "ml"
Copy-Item backend\.env.example .env   # adjust as needed

# Start services (Postgres + Redis) — or point config at SQLite for a quick test
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000   # from backend/

# Frontend
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Verification

```bash
# Tests + coverage gate (80%)
.\.venv\Scripts\python -m pytest backend\tests -q --cov=app --cov-report=term --cov-config=backend\pyproject.toml

# Lint
.\.venv\Scripts\python -m ruff check backend ml scripts --output-format concise

# End-to-end smoke test
.\.venv\Scripts\python scripts\smoke_test.py
```

## Documentation

- [Architecture](docs/architecture.md)
- [API reference](docs/API.md)
- [Database schema / ER diagram](docs/ER_DIAGRAM.md)
- [Deployment guide](docs/DEPLOYMENT.md)
- [ML pipeline](docs/ML_PIPELINE.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Roadmap](docs/ROADMAP.md)
- [Changelog](docs/CHANGELOG.md)

## License

[MIT](LICENSE)
