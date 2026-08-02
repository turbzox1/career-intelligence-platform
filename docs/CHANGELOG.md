# Changelog

All notable changes to the Career Intelligence Platform.

## [1.0.0] - 2026-08-03

### Added
- FastAPI backend: versioned REST API, auth (JWT refresh rotation, RBAC,
  device-aware sessions), structured logging, rate limiting, Prometheus
  metrics.
- Salary prediction endpoint with confidence intervals and SHAP-based
  explanation (gradient/rule-based fallbacks).
- Resume upload/parsing (PDF/DOCX/TXT) with rule-based skill extraction
  against a 200+ canonical skill catalog.
- Skill-gap analysis and personalized learning roadmaps from a curated
  course catalog.
- Semantic job matching with embedding + hashing fallbacks; job ingestion
  (admin) and seeded demo jobs.
- Personal analytics dashboard (trends by date/location/industry/experience,
  top skills, most-missing skills).
- ML pipeline: deterministic 10k-row dataset generation, 6-model CV
  comparison, MLflow tracking, committed CatBoost artifact (R² ≈ 0.94).
- Next.js 15 frontend (React 19, TypeScript, Tailwind, shadcn/ui, Recharts):
  landing, auth, dashboard, predictor with SHAP waterfall, resumes, skill gap
  & roadmap, job matching, analytics.
- Infra: Docker Compose (Postgres, Redis, Celery worker, MLflow, Prometheus,
  Grafana), Dockerfiles, monitoring dashboards.
- CI/CD: GitHub Actions for backend lint+tests, frontend typecheck+build, and
  GHCR image publishing.
- Docs: architecture, API reference, ER diagram, deployment, ML pipeline,
  contributing, roadmap, changelog.
- Tests: 101 backend tests at ~87% coverage; end-to-end smoke test.

### Fixed
- bcrypt integration (replaced passlib) for password hashing.
- JWT `jti` claim to prevent token-hash uniqueness collisions.
- Session revocation model (unique on refresh-token hash only).
- Timezone-naive session expiry handling for SQLite test runs.
- Repository ordering resolution (generic repository typing).
- Mutable default arguments in feature-spec dataclass.

### Security
- Secrets never committed; `SECRET_KEY` externalised via env.
- Admin-gated job ingestion; role-based access control.
