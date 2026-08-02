# Career Intelligence — ML Pipeline

Salary-prediction feature engineering, dataset generation and model training.

```bash
python -m pip install -e ".[dev]"
python career_ml/generate_data.py --n 10000 --output data/processed/salary_dataset.csv
python -m pipeline.train --data data/processed/salary_dataset.csv --output-dir models/trained --cv 3
```

See `docs/ML_PIPELINE.md` in the repository root for details.
