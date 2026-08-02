"""Resume API and parser tests."""

from __future__ import annotations

from tests.conftest import auth_headers, signup_and_login

RESUME_TEXT = (
    "Jane Doe\njane.doe@example.com\n+1 555-123-4567\n"
    "Senior Software Engineer with 8 years of experience.\n"
    "Work Experience: 2018-present: Backend Engineer at Acme Corp.\n"
    "Skills: Python, Django, AWS, PostgreSQL, Docker, Kubernetes, Machine Learning\n"
    "Education: BSc Computer Science, University, 2016\n"
    "Projects: Built a recommendation engine\n"
    "Certifications: AWS Solutions Architect\n"
    "Languages: English, Spanish\n"
)


def _upload(client, creds, content=RESUME_TEXT, filename="resume.txt"):
    return client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers(creds["access_token"]),
        files={"file": (filename, content.encode(), "text/plain")},
    )


class TestResumeUpload:
    def test_upload_txt(self, client) -> None:
        creds = signup_and_login(client)
        resp = _upload(client, creds)
        assert resp.status_code == 201
        body = resp.json()
        assert body["resume"]["parse_status"] == "parsed"
        assert "Python" in body["skills"]

    def test_upload_rejects_unsupported_extension(self, client) -> None:
        creds = signup_and_login(client)
        resp = _upload(client, creds, content="", filename="resume.exe")
        assert resp.status_code == 422

    def test_upload_empty_text(self, client) -> None:
        creds = signup_and_login(client)
        resp = _upload(client, creds, content="   \n  \n", filename="resume.txt")
        assert resp.status_code == 422

    def test_upload_requires_auth(self, client) -> None:
        resp = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("r.txt", b"hello", "text/plain")},
        )
        assert resp.status_code == 401


class TestResumeListAndGet:
    def test_list_resumes(self, client) -> None:
        creds = signup_and_login(client)
        _upload(client, creds)
        resp = client.get("/api/v1/resumes", headers=auth_headers(creds["access_token"]))
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_get_resume_parsed_fields(self, client) -> None:
        creds = signup_and_login(client)
        up = _upload(client, creds)
        resume_id = up.json()["resume"]["id"]
        resp = client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers(creds["access_token"]))
        assert resp.status_code == 200
        parsed = resp.json()["parsed_data"]
        assert parsed["email"] == "jane.doe@example.com"
        assert parsed["years_of_experience"] >= 8

    def test_delete_resume(self, client) -> None:
        creds = signup_and_login(client)
        up = _upload(client, creds)
        resume_id = up.json()["resume"]["id"]
        resp = client.delete(f"/api/v1/resumes/{resume_id}", headers=auth_headers(creds["access_token"]))
        assert resp.status_code == 200
        get = client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers(creds["access_token"]))
        assert get.status_code == 404

    def test_cannot_access_other_users_resume(self, client) -> None:
        creds_a = signup_and_login(client, email="a@test.io")
        up = _upload(client, creds_a)
        creds_b = signup_and_login(client, email="b@test.io")
        resp = client.get(
            f"/api/v1/resumes/{up.json()['resume']['id']}",
            headers=auth_headers(creds_b["access_token"]),
        )
        assert resp.status_code == 404
