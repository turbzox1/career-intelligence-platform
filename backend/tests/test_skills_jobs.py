"""Skill, skill-gap, learning and job-matching API tests."""

from __future__ import annotations

from tests.conftest import auth_headers, signup_and_login

RESUME_SKILLS = ["Python", "AWS", "Docker"]
JOB_DESCRIPTION = (
    "We need a Machine Learning Engineer with Python, TensorFlow, Kubernetes, AWS, PyTorch and Docker experience."
)


class TestSkillGap:
    def test_gap_analysis(self, client) -> None:
        resp = client.post(
            "/api/v1/skills/gap",
            json={"resume_skills": RESUME_SKILLS, "job_description": JOB_DESCRIPTION},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "Python" in body["matched_skills"]
        missing_names = {item["skill"] for item in body["missing_skills"]}
        assert "Kubernetes" in missing_names
        assert 0 <= body["skill_match_percentage"] <= 100

    def test_gap_full_match(self, client) -> None:
        resp = client.post(
            "/api/v1/skills/gap",
            json={
                "resume_skills": ["Python", "Kubernetes", "AWS", "Docker"],
                "job_description": "Need Python, Kubernetes, AWS, Docker engineers",
            },
        )
        body = resp.json()
        assert body["skill_match_percentage"] == 100.0
        assert body["missing_skills"] == []

    def test_gap_short_description_rejected(self, client) -> None:
        resp = client.post("/api/v1/skills/gap", json={"resume_skills": [], "job_description": "too short"})
        assert resp.status_code == 422


class TestSkillCatalog:
    def test_catalog_search(self, client) -> None:
        resp = client.get(
            "/api/v1/skills/catalog?query=python", headers=auth_headers(signup_and_login(client)["access_token"])
        )
        assert resp.status_code == 200
        assert any(s["name"] == "Python" for s in resp.json())

    def test_catalog_all(self, client) -> None:
        creds = signup_and_login(client)
        resp = client.get("/api/v1/skills/catalog?limit=200", headers=auth_headers(creds["access_token"]))
        assert resp.status_code == 200
        assert len(resp.json()) > 100


class TestLearning:
    def test_roadmap(self, client) -> None:
        resp = client.post(
            "/api/v1/skills/recommendations/roadmap",
            json={"missing_skills": ["Kubernetes", "PyTorch"], "daily_hours": 2},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["steps"]) == 2
        assert body["total_estimated_hours"] > 0
        assert all(s["resources"] for s in body["steps"])

    def test_generate_and_list_recommendations(self, client) -> None:
        creds = signup_and_login(client)
        headers = auth_headers(creds["access_token"])
        resp = client.post(
            "/api/v1/skills/recommendations",
            json={"resume_skills": RESUME_SKILLS, "job_description": JOB_DESCRIPTION},
            headers=headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()) > 0

        listing = client.get("/api/v1/skills/recommendations", headers=headers)
        assert listing.status_code == 200
        assert len(listing.json()) > 0


class TestJobs:
    def test_list_jobs_seeded(self, client) -> None:
        resp = client.get("/api/v1/jobs")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 5

    def test_match_jobs(self, client) -> None:
        resp = client.post(
            "/api/v1/jobs/match",
            json={"query": "Machine Learning Engineer with Python, PyTorch, AWS, Docker skills"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["results"]) > 0
        assert 0 <= body["results"][0]["similarity"] <= 1

    def test_match_short_query_rejected(self, client) -> None:
        resp = client.post("/api/v1/jobs/match", json={"query": "short"})
        assert resp.status_code == 422

    def test_admin_create_job(self, client, admin_client) -> None:
        _, creds = admin_client
        resp = client.post(
            "/api/v1/jobs",
            json={
                "external_key": "test-job-1",
                "title": "Test Engineer",
                "company": "Test Co",
                "description": "A test job posting requiring Python and AWS.",
                "skills": ["Python", "AWS"],
            },
        )
        assert resp.status_code == 201

    def test_non_admin_cannot_create_job(self, client) -> None:
        creds = signup_and_login(client)
        resp = client.post(
            "/api/v1/jobs",
            json={
                "external_key": "no-admin-job",
                "title": "X",
                "company": "Y",
                "description": "Description of a job that is long enough.",
            },
            headers=auth_headers(creds["access_token"]),
        )
        assert resp.status_code in (403, 401)
