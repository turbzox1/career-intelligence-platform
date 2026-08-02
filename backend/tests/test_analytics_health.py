"""Analytics, health and error-handling API tests."""

from __future__ import annotations

from tests.conftest import auth_headers, signup_and_login

PAYLOAD = {
    "years_experience": 3,
    "degree_level": "bachelor",
    "location": "new_york",
    "industry": "finance",
    "company_size": "mid",
    "title": "data_scientist",
    "skills": ["Python", "SQL"],
}


class TestAnalytics:
    def test_dashboard_empty(self, client) -> None:
        creds = signup_and_login(client)
        resp = client.get("/api/v1/analytics/dashboard", headers=auth_headers(creds["access_token"]))
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_predictions"] == 0
        assert isinstance(body["top_skills"], list)

    def test_dashboard_with_predictions(self, client) -> None:
        creds = signup_and_login(client)
        headers = auth_headers(creds["access_token"])
        client.post("/api/v1/predictions/salary", json=PAYLOAD, headers=headers)
        client.post("/api/v1/predictions/salary", json=PAYLOAD, headers=headers)
        resp = client.get("/api/v1/analytics/dashboard", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_predictions"] == 2
        assert body["average_salary"] > 0
        assert len(body["salary_trend"]) >= 1
        assert len(body["salary_by_location"]) >= 1


class TestHealth:
    def test_liveness(self, client) -> None:
        resp = client.get("/api/v1/health/live")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_readiness_without_redis(self, client) -> None:
        resp = client.get("/api/v1/health/ready")
        # Without Redis running, the service is not ready but still returns 503.
        assert resp.status_code in (200, 503)


class TestErrors:
    def test_unknown_route_404(self, client) -> None:
        resp = client.get("/api/v1/does-not-exist")
        assert resp.status_code == 404

    def test_validation_error_shape(self, client) -> None:
        resp = client.post(
            "/api/v1/predictions/salary",
            json={"years_experience": -1},
            headers=auth_headers(signup_and_login(client)["access_token"]),
        )
        assert resp.status_code == 422
        assert "error" in resp.json()
        assert "details" in resp.json()["error"]

    def test_root_metadata(self, client) -> None:
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["name"]
        assert resp.json()["docs"] == "/docs"
