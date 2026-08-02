"""Security primitive unit tests."""

from __future__ import annotations

import pytest

from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self) -> None:
        hashed = hash_password("CorrectHorse123")
        assert hashed != "CorrectHorse123"
        assert verify_password("CorrectHorse123", hashed)
        assert not verify_password("WrongPassword", hashed)

    def test_unique_salts(self) -> None:
        assert hash_password("SamePass123") != hash_password("SamePass123")

    def test_verify_invalid_hash(self) -> None:
        assert not verify_password("x", "not-a-valid-hash")

    def test_long_password_handling(self) -> None:
        hashed = hash_password("x" * 100)
        assert verify_password("x" * 100, hashed)


class TestJWT:
    def test_access_token_roundtrip(self) -> None:
        token = create_access_token(42, roles=["user"])
        payload = decode_token(token, expected_type="access")
        assert payload["sub"] == "42"
        assert payload["type"] == "access"
        assert "roles" in payload

    def test_refresh_token_roundtrip(self) -> None:
        token = create_refresh_token(7)
        payload = decode_token(token, expected_type="refresh")
        assert payload["sub"] == "7"

    def test_type_mismatch_rejected(self) -> None:
        token = create_access_token(1)
        with pytest.raises(UnauthorizedError):
            decode_token(token, expected_type="refresh")

    def test_tampered_token_rejected(self) -> None:
        token = create_access_token(1)
        with pytest.raises(UnauthorizedError):
            decode_token(token[:-3] + "abc")
