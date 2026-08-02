# Deployment

## Option 1 — Docker Compose (single host, recommended for demo/VPS)

```bash
cd infra
cp .env.example .env
# 1. Set SECRET_KEY to a long random value:  openssl rand -hex 32
# 2. Adjust POSTGRES_* credentials.

docker compose up -d --build
```

**First boot only — schema + seed data:**

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
```

The seed script creates an admin account (email/password printed to the logs)
and six demo job postings so job matching has content.

**Apply migrations after every upgrade:**

```bash
docker compose exec backend alembic upgrade head
```

**Backups** — the Postgres volume can be dumped:

```bash
docker compose exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql
```

### Reverse proxy (Caddy example)

```nginx
api.example.com {
    reverse_proxy backend:8000
}
app.example.com {
    reverse_proxy frontend:3000
}
```

Set `BACKEND_CORS_ORIGINS=["https://app.example.com"]` in `infra/.env` and
`NEXT_PUBLIC_API_BASE_URL=https://api.example.com/api/v1`.

## Option 2 — CI/CD (GitHub Container Registry)

Push a tag (`vX.Y.Z`) or run the deploy workflow manually. It builds and
pushes `ghcr.io/<owner>/<repo>/backend` and `frontend` images. On your server:

```bash
docker pull ghcr.io/<owner>/<repo>/backend:latest
docker pull ghcr.io/<owner>/<repo>/frontend:latest
docker compose up -d
```

## Environment variables (backend)

| Variable | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | dev value | JWT signing secret — **change in production**. |
| `ENVIRONMENT` | `development` | `development` / `staging` / `production` / `test`. |
| `DATABASE_URL` | derived | Full SQLAlchemy URI overrides host/port/user parts. |
| `POSTGRES_HOST` / `_PORT` / `_USER` / `_PASSWORD` / `_DB` | local | Postgres connection parts. |
| `REDIS_URL` | derived | Redis URI for rate limits, sessions and Celery. |
| `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` | derived | Redis DB 1 / 2. |
| `STORAGE_BACKEND` | `local` | `local` or `s3`. |
| `S3_BUCKET` / `S3_REGION` / `S3_ACCESS_KEY` / `S3_SECRET_KEY` | — | Required when S3. |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | Model registry/tracking server. |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:3000"]` | JSON array of allowed origins. |
| `RATE_LIMIT_DEFAULT` / `RATE_LIMIT_AUTH` | `100/minute` / `10/minute` | SlowAPI limits. |

## Production hardening checklist

- [ ] Rotate `SECRET_KEY` and set it via a secret manager (not plaintext env).
- [ ] Use Postgres 16 with a dedicated user and strong password.
- [ ] Enable TLS at the reverse proxy; HSTS headers.
- [ ] Point MLflow at Postgres-backed store and external object storage.
- [ ] Restrict CORS origins to your real frontend domain.
- [ ] Enable S3 storage backend for resume files (or mount persistent volume).
- [ ] Run the Celery worker with multiple concurrency and a Redis sentinel/cluster.
- [ ] Back up Postgres nightly; verify restores.
- [ ] Rotate the demo admin credentials after seeding.
