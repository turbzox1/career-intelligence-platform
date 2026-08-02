# Roadmap

## Released

- **v1.0.0**
  - FastAPI backend with full auth (JWT refresh rotation, RBAC, sessions).
  - Salary prediction API with SHAP explainability and confidence intervals.
  - Resume parsing (PDF/DOCX/TXT) + rule-based skill extraction.
  - Skill-gap analysis and curated learning-catalog roadmaps.
  - Semantic job matching with embedding fallbacks.
  - Personal analytics dashboard.
  - Training pipeline (6 model families, CV, MLflow) and committed artifact.
  - Next.js 15 frontend with dashboard, predictor, resumes, skills, jobs,
    analytics pages.
  - Docker Compose stack (Postgres, Redis, Celery, MLflow, Prometheus,
    Grafana), GitHub Actions CI/CD, full documentation.

## Upcoming

### High priority
- **Real labour-market data** — replace/augment synthetic data with an
  O*NET / BLS-derived dataset; retrain with `--tune`.
- **True NLP embeddings** — install `sentence-transformers` and `spacy`
  models in production images to replace the hashing fallback.
- **Async resume parsing** — move CPU-bound parsing into Celery tasks with
  polling/webhook status.
- **Multi-user analytics** — admin-only aggregate analytics across users.

### Medium priority
- **Email verification & password reset** flows.
- **Rate-limit-aware caching** (Redis) for repeated salary requests.
- **Docker Compose health-gated rollout** and zero-downtime deployments.
- **Grafana alerting rules** (error budget, latency SLOs) with Slack/webhook.
- **Model A/B serving** — serve two model versions behind a flag and compare.

### Low priority / nice-to-have
- **OAuth (Google/LinkedIn) sign-in.**
- **Resume versioning** with diff view.
- **Job application tracking** UI + reminders.
- **PDF export** of learning roadmaps.
- **i18n** (multi-language UI).
