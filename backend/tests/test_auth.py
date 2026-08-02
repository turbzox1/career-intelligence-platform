"""Authentication API tests."""

from __future__ import annotations

from tests.conftest import auth_headers, signup_and_login


class TestSignup:
    def test_signup_success(self, client) -> None:
        resp = client.post(
            "/api/v1/auth/signup",
            json={"email": "new@test.io", "full_name": "New User", "password": "StrongPass1"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["user"]["email"] == "new@test.io"
        assert "access_token" in body["tokens"]
        assert "refresh_token" in body["tokens"]

    def test_duplicate_email_conflict(self, client) -> None:
        signup_and_login(client, email="dup@test.io")
        resp = client.post(
            "/api/v1/auth/signup",
            json={"email": "dup@test.io", "full_name": "X", "password": "StrongPass1"},
        )
        assert resp.status_code == 409

    def test_weak_password_rejected(self, client) -> None:
        resp = client.post(
            "/api/v1/auth/signup",
            json={"email": "weak@test.io", "full_name": "X", "password": "short"},
        )
        assert resp.status_code == 422

    def test_invalid_email_rejected(self, client) -> None:
        resp = client.post(
            "/api/v1/auth/signup",
            json={"email": "not-an-email", "full_name": "X", "password": "StrongPass1"},
        )
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client) -> None:
        signup_and_login(client, email="login@test.io")
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "login@test.io", "password": "SecurePass123"},
        )
        assert resp.status_code == 200
        assert resp.json()["tokens"]["access_token"]

    def test_login_wrong_password(self, client) -> None:
        signup_and_login(client, email="wrong@test.io")
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@test.io", "password": "WrongPass1"},
        )
        assert resp.status_code == 401

    def test_login_unknown_user(self, client) -> None:
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@test.io", "password": "Whatever1"},
        )
        assert resp.status_code == 401


class TestRefreshLogout:
    def test_refresh_rotates_token(self, client) -> None:
        creds = signup_and_login(client)
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": creds["refresh_token"]})
        assert resp.status_code == 200
        assert resp.json()["tokens"]["access_token"] != creds["access_token"]

    def test_logout_revokes_refresh_token(self, client) -> None:
        creds = signup_and_login(client)
        client.post("/api/v1/auth/logout", json={"refresh_token": creds["refresh_token"]})
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": creds["refresh_token"]})
        assert resp.status_code == 401

    def test_logout_all(self, client) -> None:
        creds = signup_and_login(client)
        resp = client.post("/api/v1/auth/logout-all", headers=auth_headers(creds["access_token"]))
        assert resp.status_code == 200
        resp2 = client.post("/api/v1/auth/refresh", json={"refresh_token": creds["refresh_token"]})
        assert resp2.status_code == 401


class TestAuthGuard:
    def test_missing_token_rejected(self, client) -> None:
        resp = client.get("/api/v1/users/me")
        assert resp.status_code == 401

    def test_garbage_token_rejected(self, client) -> None:
        resp = client.get("/api/v1/users/me", headers=auth_headers("garbage.token.here"))
        assert resp.status_code == 401

    def test_me_endpoint(self, client) -> None:
        creds = signup_and_login(client)
        resp = client.get("/api/v1/users/me", headers=auth_headers(creds["access_token"]))
        assert resp.status_code == 200
        assert resp.json()["email"] == "user@test.io"
