# Career Intelligence — Backend

FastAPI service for the Career Intelligence Platform.

## Run locally

```bash
python -m pip install -e ".[dev,ml]"
uvicorn app.main:app --reload --port 8000   # from this directory
```

- Swagger docs: http://localhost:8000/docs
- Health: `GET /api/v1/health/ready`
- Tests: `pytest tests -q --cov=app --cov-report=term --cov-config=pyproject.toml`

See the repository root `README.md` and `docs/` for full documentation.
