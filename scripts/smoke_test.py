"""Quick end-to-end smoke test of the API against SQLite.

Run: .venv/Scripts/python.exe scripts/smoke_test.py
"""

import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

os.environ["DATABASE_URL"] = "sqlite:///./smoke_test.db"
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "smoke-test-secret"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app import models  # noqa: F401  (registers all tables on Base.metadata)

# Create tables + seed before importing app (import triggers lifespan? no, TestClient triggers).
from app.db.base import Base
from app.db.session import engine
from fastapi.testclient import TestClient

Base.metadata.create_all(bind=engine)

from app.db.seed import seed_all
from app.db.session import SessionLocal

with SessionLocal() as db:
    seed_all(db)

from app.main import app

client = TestClient(app)

results = []


def check(name, condition, extra=""):
    results.append((name, bool(condition), extra))
    print(("PASS" if condition else "FAIL"), name, extra)


# 1. Health
r = client.get("/api/v1/health/live")
check("health.live", r.status_code == 200, r.json())

# 2. Signup
signup = client.post(
    "/api/v1/auth/signup",
    json={
        "email": "user@test.io",
        "full_name": "Test User",
        "password": "SecurePass123",
    },
)
check("auth.signup", signup.status_code == 201, signup.status_code)
body = signup.json()
access = body["tokens"]["access_token"]
refresh = body["tokens"]["refresh_token"]
check("auth.signup.tokens", bool(access and refresh))

# 3. Me
headers = {"Authorization": f"Bearer {access}"}
me = client.get("/api/v1/users/me", headers=headers)
check("users.me", me.status_code == 200 and me.json()["email"] == "user@test.io", me.status_code)

# 4. Predict salary
payload = {
    "years_experience": 5,
    "degree_level": "master",
    "location": "san_francisco",
    "industry": "technology",
    "company_size": "large",
    "title": "ml_engineer",
    "skills": ["Python", "PyTorch", "AWS", "Kubernetes"],
}
pred = client.post("/api/v1/predictions/salary", json=payload, headers=headers)
check("predict.salary", pred.status_code == 201, pred.status_code)
pdata = pred.json()
check("predict.salary.value", pdata["predicted_salary"] > 0, pdata["predicted_salary"])
check("predict.salary.explanation", "explanation" in pdata and pdata["explanation"]["features"], "")

# 5. Upload resume (docx? use txt)
resume_text = (
    "Jane Doe\njane.doe@example.com\n+1 555-123-4567\n"
    "Software Engineer with 6 years of experience in Python, Django, AWS, PostgreSQL.\n"
    "Skills: Python, Django, AWS, PostgreSQL, Docker, Kubernetes, Machine Learning\n"
    "Education: BSc Computer Science, 2016\n"
)
r = client.post(
    "/api/v1/resumes/upload",
    headers=headers,
    files={"file": ("jane_resume.txt", resume_text.encode(), "text/plain")},
)
check("resume.upload", r.status_code == 201, r.status_code)
resume_id = r.json()["resume"]["id"]
check("resume.upload.skills", len(r.json()["skills"]) >= 3, r.json()["skills"])

# 6. Skill gap analysis
gap = client.post(
    "/api/v1/skills/gap",
    json={
        "resume_skills": ["Python", "AWS", "Docker"],
        "job_description": "We need a Machine Learning Engineer with Python, TensorFlow, Kubernetes, AWS, PyTorch and Docker experience.",
    },
)
check("skills.gap", gap.status_code == 200, gap.status_code)
gdata = gap.json()
check("skills.gap.missing", len(gdata["missing_skills"]) > 0, gdata["missing_skills"])

# 7. Learning roadmap
roadmap = client.post(
    "/api/v1/skills/recommendations/roadmap",
    json={
        "missing_skills": ["Kubernetes", "PyTorch"],
        "daily_hours": 2,
    },
)
check("skills.roadmap", roadmap.status_code == 200 and len(roadmap.json()["steps"]) == 2, roadmap.status_code)

# 8. Job matching
match = client.post(
    "/api/v1/jobs/match",
    json={"query": "Machine Learning Engineer with Python, PyTorch, AWS, Docker, Kubernetes skills"},
)
check("jobs.match", match.status_code == 200 and len(match.json()["results"]) > 0, match.status_code)

# 9. Jobs list
jobs = client.get("/api/v1/jobs", headers=headers)
check("jobs.list", jobs.status_code == 200 and jobs.json()["total"] >= 5, jobs.json().get("total"))

# 10. Analytics dashboard
dash = client.get("/api/v1/analytics/dashboard", headers=headers)
check("analytics.dashboard", dash.status_code == 200, dash.status_code)
check("analytics.dashboard.total", dash.json()["total_predictions"] >= 1, dash.json().get("total_predictions"))

# 11. Refresh token
refr = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
check("auth.refresh", refr.status_code == 200 and refr.json()["tokens"]["access_token"], refr.status_code)

# 12. Unauthorized access
noauth = client.get("/api/v1/users/me")
check("auth.requires_token", noauth.status_code == 401, noauth.status_code)

# 13. Validation error
bad = client.post("/api/v1/predictions/salary", json={"years_experience": -5}, headers=headers)
check("validation.error", bad.status_code == 422, bad.status_code)

# 14. Skill catalog
cat = client.get("/api/v1/skills/catalog?query=python", headers=headers)
check("skills.catalog", cat.status_code == 200 and len(cat.json()) > 0, cat.status_code)

failed = [name for name, ok, _ in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
if failed:
    print("FAILED:", failed)
    sys.exit(1)
print("SMOKE TEST OK")
