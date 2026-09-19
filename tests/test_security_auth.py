"""Automated unit & integration test suite for Authentication, Security, and JWT tokens."""

import pytest
from backend.app.utils.security import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hashing():
    """Verify bcrypt password hashing and verification."""
    password = "SecurePassword#2026"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_access_token_creation_and_decoding():
    """Verify JWT access token creation and decoding."""
    payload = {"sub": "officer@sih26191.gov.in", "role": "disaster_officer"}
    token = create_access_token(payload)

    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "officer@sih26191.gov.in"
    assert decoded["role"] == "disaster_officer"


def test_auth_token_api_endpoint(client):
    """Verify OAuth2 token login endpoint POST /api/v1/auth/token."""
    payload = {
        "username": "admin@sih26191.gov.in",
        "password": "AdminDisaster#2026",
    }
    res = client.post("/api/v1/auth/token", data=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
