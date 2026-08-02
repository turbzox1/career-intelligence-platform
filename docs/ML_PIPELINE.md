# ML Pipeline

## Overview

The pipeline produces the salary-prediction artifact served by the backend.
Feature engineering is shared between training and serving via
`ml/career_ml/features.py` to guarantee train/serve parity.

```
ml/career_ml/generate_data.py  →  data/processed/salary_dataset.csv (10k rows)
ml/pipeline/train.py           →  models/trained/{model.joblib, metadata.json, model_comparison.csv}
                                     └──→ served by backend/app/ml/model_loader.py
```

## Data

`generate_data.py` synthesises a deterministic (seeded) dataset:

- 10 job titles × 10 locations × 9 industries × 5 company sizes × 5 degree levels
- Base salary from title, multiplied by location and industry factors
- Skill deltas from a curated skill→salary map, plus realistic noise
- Capped range (~$40k–$500k) to avoid extreme tails

## Features

| Group | Features |
| --- | --- |
| Numeric | `years_experience`, `skill_count`, `degree_ordinal`, `company_size_ordinal` |
| One-hot | `location` (10), `industry` (9), `title` (10) |

Vector length = 33. See `features.py` for the canonical level lists.

## Training

```bash
.\.venv\Scripts\python -m pipeline.train \
  --data data\processed\salary_dataset.csv \
  --output-dir models\trained \
  --cv 3
```

- Compares 6 model families under 3-fold CV: Linear, Random Forest,
  Gradient Boosting, XGBoost, LightGBM, CatBoost, plus an SVR baseline.
- Evaluates R², RMSE, MAE; picks the best by R².
- Optional `--tune` flag runs a small `RandomizedSearchCV` on the top models.
- Writes the winning pipeline as `model.joblib` with `metadata.json`
  (model name/version/hyper-parameters) and `model_comparison.csv`.
- Logs parameters + metrics to MLflow when `MLFLOW_TRACKING_URI` is set.

**Current production artifact:** CatBoost — R² ≈ 0.94, MAE ≈ $13.3k.

## Serving & explainability

- `backend/app/ml/model_loader.py` — thread-safe singleton; resolves the
  artifact relative to the repo root (`ml/models/trained`); falls back to the
  deterministic baseline so the API never 5xxs.
- `backend/app/ml/salary_model.py` — builds the 33-dim vector from the
  request, runs the pipeline, returns salary + bounds + confidence.
- `backend/app/ml/explainer.py` — SHAP `TreeExplainer`; if SHAP is
  unavailable, a **gradient approximation**, and finally a **rule-based
  baseline** (each feature's signed contribution from known coefficients).

## Retraining workflow

1. Update/replace the dataset or feature definitions.
2. `python -m pipeline.train ...` (optionally with `--tune`).
3. Commit the new `model.joblib` + `metadata.json` (they are force-included in
   git via `.gitignore` exceptions).
4. Bump `model_version` in metadata; the API exposes it in responses.

## Model registry (MLflow)

- Tracking server: `infra/docker-compose.yml` exposes MLflow on `:5000`.
- The pipeline registers runs under experiment `salary-prediction`; the
  registered model name is `salary-predictor`.
