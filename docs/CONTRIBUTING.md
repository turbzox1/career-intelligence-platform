# Contributing

Thanks for helping build the Career Intelligence Platform.

## Getting started

```bash
python -m venv .venv
.\.venv\Scripts\python -m pip install -e "backend[dev,ml]" -e "ml"

cd frontend && npm install && cd ..
```

## Workflow

1. Branch from `main`: `git checkout -b feat/my-change`.
2. Make small, focused commits.
3. Keep the lint and coverage gates green:

```bash
# Backend
.\.venv\Scripts\python -m ruff check backend ml scripts --output-format concise
.\.venv\Scripts\python -m ruff format backend ml scripts
.\.venv\Scripts\python -m pytest backend\tests -q --cov=app \
    --cov-report=term --cov-fail-under=80 --cov-config=backend\pyproject.toml

# Frontend
cd frontend && npm run typecheck && npm run build
```

4. Open a PR against `main` using the [pull request template](.github/PULL_REQUEST_TEMPLATE.md).

## Conventions

- **Layering** — keep HTTP handlers thin; logic goes in `services/`, queries
  in `repositories/`. No business logic in routes.
- **Feature contract** — if you change feature names/levels, update
  `ml/career_ml/features.py` **and** the request schema validator.
- **Schemas** — API changes need a Pydantic schema + a test. Update
  `docs/API.md`.
- **Migrations** — schema changes get a new Alembic revision:
  `alembic revision --autogenerate -m "..."` (verify the output manually).
- **Type hints** — new code is fully typed; run `mypy backend` if you touch it.
- **No comments required** — prefer expressive code over comments.

## Testing

- Backend tests live in `backend/tests/` (pytest + coverage gate ≥ 80%).
- `scripts/smoke_test.py` exercises the API end-to-end (auth → resume → salary
  → skills → jobs → analytics) against a SQLite database.
- Frontend: `npm run typecheck` enforces strict TS; build must succeed.

## Releasing

Maintainers tag `vX.Y.Z`; the deploy workflow builds and publishes images to
GHCR. Update `docs/CHANGELOG.md` for user-visible changes.
