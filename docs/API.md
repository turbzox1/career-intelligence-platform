# API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive docs are available at `http://localhost:8000/docs` (Swagger) and
`http://localhost:8000/redoc`.

## Conventions

- All routes except `/health/*`, auth and skills-analysis endpoints require a
  Bearer token: `Authorization: Bearer <access_token>`.
- Errors use a standard shape:
  ```json
  { "detail": "message", "code": "optional_code", "request_id": "req-..." }
  ```
- Pagination uses `page` (1-based) and `page_size` query parameters and
  returns `{ items, total, page, page_size, pages }`.
- Rate limits apply per endpoint group; exceeding them returns `429`.

## Health

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health/live` | Liveness probe (always `{"status": "ok"}`). |
| GET | `/health/ready` | Readiness probe (checks DB + Redis; `503` when not ready). |

## Auth

| Method | Path | Description |
| --- | --- | --- |
| POST | `/auth/signup` | Register `{ full_name, email, password }` → user + tokens. |
| POST | `/auth/login` | Login `{ email, password }` → user + tokens (device fingerprint optional). |
| POST | `/auth/refresh` | Rotate tokens `{ refresh_token }`. |
| GET | `/auth/me` | Current user profile. |
| POST | `/auth/logout` | Revoke the current session's refresh token. |
| POST | `/auth/logout-all` | Revoke all sessions for the user. |

## Users

| Method | Path | Description |
| --- | --- | --- |
| GET | `/users/me` | Current user details. |
| PATCH | `/users/me` | Update `full_name` / `password`. |
| GET | `/users/me/predictions` | Paginated prediction history. |
| GET | `/users/me/resumes` | Paginated resume list. |
| GET | `/users/{user_id}` | Admin: view a user. |
| GET | `/users` | Admin: list users. |

## Resumes

| Method | Path | Description |
| --- | --- | --- |
| POST | `/resumes/upload` | Multipart upload (PDF/DOCX/TXT) → parsed structure + skills. |
| GET | `/resumes` | Paginated resume list for the current user. |
| GET | `/resumes/{resume_id}` | Full parsed resume. |
| DELETE | `/resumes/{resume_id}` | Delete a resume and its extracted skills. |

## Predictions

| Method | Path | Description |
| --- | --- | --- |
| POST | `/predictions/salary` | Run a salary prediction (see payload below). |
| GET | `/predictions` | Paginated prediction history. |
| GET | `/predictions/{prediction_id}` | A single prediction with explanation. |

**Salary prediction request**

```json
{
  "years_experience": 5,
  "degree_level": "master",
  "location": "san_francisco",
  "industry": "technology",
  "company_size": "large",
  "title": "ml_engineer",
  "skills": ["Python", "PyTorch", "AWS", "MLOps"],
  "resume_id": null
}
```

- `degree_level` ∈ `none | associate | bachelor | master | phd`
- `company_size` ∈ `startup | small | mid | large | enterprise`
- `location` ∈ `remote | san_francisco | new_york | seattle | austin | london | bengaluru | berlin | toronto | singapore`
- `industry` ∈ `technology | finance | healthcare | retail | manufacturing | consulting | education | media | energy`
- `title` ∈ `software_engineer | data_scientist | ml_engineer | devops_engineer | product_manager | data_engineer | backend_engineer | frontend_engineer | fullstack_engineer | site_reliability_engineer`

**Response**

```json
{
  "prediction_id": 42,
  "predicted_salary": 336875.0,
  "currency": "USD",
  "lower_bound": 307875.0,
  "upper_bound": 365875.0,
  "confidence": 0.9,
  "model_name": "catboost",
  "model_version": "1.0.0",
  "explanation": {
    "base_value": 129302.0,
    "predicted_value": 336875.0,
    "features": [
      { "feature": "years_experience", "value": 5.0, "contribution": 48200.0 }
    ]
  },
  "input_features": {},
  "created_at": "2026-08-03T10:00:00Z"
}
```

## Skills

| Method | Path | Description |
| --- | --- | --- |
| POST | `/skills/gap` | `{ resume_skills: [], job_description: "..." }` → match %, matched/missing skills. |
| GET | `/skills/catalog` | Master skill catalog, optional `?query=` + `?limit=`. |
| POST | `/skills/recommendations/roadmap` | `{ missing_skills: [], daily_hours: 1 }` → prioritized roadmap with resources. |
| POST | `/skills/recommendations` | Analyze gap + persist learning recommendations for the user. |
| GET | `/skills/recommendations` | List the user's persisted recommendations. |

## Jobs

| Method | Path | Description |
| --- | --- | --- |
| GET | `/jobs` | Paginated public job list; optional `title`/`company`/`location` filters. |
| POST | `/jobs/match` | `{ query: "..." }` (+ `?top_k=`) → ranked matches with similarity and skills. |
| POST | `/jobs` | Admin: ingest a job posting. |

## Analytics

| Method | Path | Description |
| --- | --- | --- |
| GET | `/analytics/dashboard` | Aggregates: total predictions, average salary, salary trends by date/location/industry/experience, top skills, most missing skills. |

## Observability

| Method | Path | Description |
| --- | --- | --- |
| GET | `/metrics` | Prometheus metrics (no auth). |
