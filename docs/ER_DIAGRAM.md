# Database Schema

SQLAlchemy 2.0 ORM models in `backend/app/models/`. Migrations via Alembic
(`backend/alembic/versions/0001_initial.py`). Target runtime is PostgreSQL;
tests run against SQLite with `create_all`.

## ER Diagram

```mermaid
erDiagram
    USERS ||--o{ SESSIONS : has
    USERS ||--o{ RESUMES : owns
    USERS ||--o{ PREDICTIONS : owns
    USERS ||--o{ RECOMMENDATIONS : owns
    USERS ||--o{ JOB_APPLICATIONS : submits
    RESUMES ||--o{ RESUME_SKILLS : contains
    SKILLS ||--o{ RESUME_SKILLS : appears_as
    RESUMES ||--o{ PREDICTIONS : seeds
    RECOMMENDATIONS ||--o| LEARNING_RESOURCES : points_to
    RECOMMENDATIONS ||--o{ RECOMMENDATION_SKILLS : targets
    SKILLS ||--o{ RECOMMENDATION_SKILLS : appears_as
    JOBS ||--o{ JOB_APPLICATIONS : receives
    JOBS ||--o{ JOB_SKILLS : requires
    SKILLS ||--o{ JOB_SKILLS : appears_as

    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string role
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    SESSIONS {
        int id PK
        int user_id FK
        string refresh_token_hash UK
        string device_fingerprint
        string user_agent
        string ip_address
        datetime expires_at
        datetime revoked_at
        datetime created_at
    }

    RESUMES {
        int id PK
        int user_id FK
        string filename
        string file_type
        int file_size_bytes
        string storage_path
        string parse_status
        text error_message
        json parsed_data
        datetime created_at
    }

    SKILLS {
        int id PK
        string name UK
        string category
        float weight
        datetime created_at
    }

    RESUME_SKILLS {
        int id PK
        int resume_id FK
        int skill_id FK
        string source
        float confidence
    }

    PREDICTIONS {
        int id PK
        int user_id FK
        int resume_id FK, nullable
        float predicted_salary
        float lower_bound
        float upper_bound
        float confidence
        string model_name
        string model_version
        json input_features
        json explanation
        datetime created_at
    }

    LEARNING_RESOURCES {
        int id PK
        string skill_name
        string title
        string provider
        string url UK
        string resource_type
        string difficulty
        float estimated_hours
        float rating
    }

    RECOMMENDATIONS {
        int id PK
        int user_id FK
        int resource_id FK
        string skill_name
        string reason
        float score
        string status
        int priority
        datetime created_at
    }

    JOBS {
        int id PK
        string external_key UK
        string title
        string company
        string location
        text description
        float salary_min
        float salary_max
        string currency
        string source_url
        json embedding
        datetime created_at
    }

    JOB_SKILLS {
        int id PK
        int job_id FK
        int skill_id FK
    }

    JOB_APPLICATIONS {
        int id PK
        int user_id FK
        int job_id FK
        string status
        datetime applied_at
        text notes
    }
```

## Notes

- **Sessions** — one row per device session; the refresh token is stored as a
  SHA-256 hash to support revocation without storing plaintext. Unique on the
  hash, not on `(user_id, device_fingerprint)`.
- **Predictions** — the full `input_features` snapshot and `explanation`
  (SHAP waterfall) are persisted as JSON so history views can re-render
  results even if the model artifact changes.
- **Skills master** — populated by `app.db.seed` from `app/data/skills_master.py`;
  `weight` is used by the gap/priority scoring.
- **Jobs.embedding** — lazily computed and stored as a JSON float list;
  `jobs.compute_embeddings` Celery task backfills it.
