"""Salary prediction API and runtime tests."""

from __future__ import annotations

import pytest

from app.ml.embeddings import cosine_similarity
from tests.conftest import auth_headers, signup_and_login

PAYLOAD = {
    "years_experience": 5,
    "degree_level": "master",
    "location": "san_francisco",
    "industry": "technology",
    "company_size": "large",
    "title": "ml_engineer",
    "skills": ["Python", "PyTorch", "AWS", "Kubernetes"],
}


class TestPredictionApi:
    def test_predict_salary(self, client) -> None:
        creds = signup_and_login(client)
        resp = client.post("/api/v1/predictions/salary", json=PAYLOAD, headers=auth_headers(creds["access_token"]))
        assert resp.status_code == 201
        body = resp.json()
        assert body["predicted_salary"] > 0
        assert body["lower_bound"] <= body["predicted_salary"] <= body["upper_bound"]
        assert 0 < body["confidence"] <= 1
        assert body["explanation"]["features"]
        assert body["model_name"]

    def test_predict_requires_auth(self, client) -> None:
        resp = client.post("/api/v1/predictions/salary", json=PAYLOAD)
        assert resp.status_code == 401

    def test_predict_invalid_feature(self, client) -> None:
        creds = signup_and_login(client)
        bad = {**PAYLOAD, "years_experience": -3}
        resp = client.post("/api/v1/predictions/salary", json=bad, headers=auth_headers(creds["access_token"]))
        assert resp.status_code == 422

    def test_predict_with_resume(self, client) -> None:
        creds = signup_and_login(client)
        upload = client.post(
            "/api/v1/resumes/upload",
            headers=auth_headers(creds["access_token"]),
            files={
                "file": (
                    "r.txt",
                    b"Skills: Python, AWS, Docker, Kubernetes\n",
                    "text/plain",
                )
            },
        )
        resume_id = upload.json()["resume"]["id"]
        payload = {**PAYLOAD, "resume_id": resume_id, "skills": []}
        resp = client.post(
            "/api/v1/predictions/salary",
            json=payload,
            headers=auth_headers(creds["access_token"]),
        )
        assert resp.status_code == 201

    def test_predict_with_unknown_resume(self, client) -> None:
        creds = signup_and_login(client)
        resp = client.post(
            "/api/v1/predictions/salary",
            json={**PAYLOAD, "resume_id": 9999},
            headers=auth_headers(creds["access_token"]),
        )
        assert resp.status_code == 404


class TestPredictionHistory:
    def test_list_and_get(self, client) -> None:
        creds = signup_and_login(client)
        headers = auth_headers(creds["access_token"])
        created = client.post("/api/v1/predictions/salary", json=PAYLOAD, headers=headers)
        prediction_id = created.json()["prediction_id"]

        listing = client.get("/api/v1/predictions", headers=headers)
        assert listing.status_code == 200
        assert listing.json()["total"] >= 1

        detail = client.get(f"/api/v1/predictions/{prediction_id}", headers=headers)
        assert detail.status_code == 200
        assert detail.json()["prediction_id"] == prediction_id

    def test_get_other_users_prediction_forbidden(self, client) -> None:
        creds_a = signup_and_login(client, email="a@test.io")
        created = client.post("/api/v1/predictions/salary", json=PAYLOAD, headers=auth_headers(creds_a["access_token"]))
        pid = created.json()["prediction_id"]
        creds_b = signup_and_login(client, email="b@test.io")
        resp = client.get(f"/api/v1/predictions/{pid}", headers=auth_headers(creds_b["access_token"]))
        assert resp.status_code == 404


class TestEmbeddings:
    def test_cosine_similarity_identical(self) -> None:
        import numpy as np

        vec = np.array([1.0, 0.0, 1.0])
        assert cosine_similarity(vec, vec) == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal(self) -> None:
        import numpy as np

        a = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        assert cosine_similarity(a, b) == pytest.approx(0.0, abs=1e-6)

    def test_cosine_similarity_zero_vector(self) -> None:
        import numpy as np

        a = np.array([0.0, 0.0])
        b = np.array([1.0, 1.0])
        assert cosine_similarity(a, b) == pytest.approx(0.0)
