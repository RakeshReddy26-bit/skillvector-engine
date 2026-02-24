"""Tests for auth endpoints: register, login, me, usage."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    """Create a TestClient with mocked pipeline and rate limiter."""
    with (
        patch("api.main.SkillVectorPipeline") as MockPipeline,
        patch("api.main.RateLimiter") as MockLimiter,
    ):
        mock_pipeline = MagicMock()
        MockPipeline.return_value = mock_pipeline
        mock_limiter = MagicMock()
        mock_limiter.check.return_value = (True, "ok")
        MockLimiter.return_value = mock_limiter

        from api.main import app
        import api.main as api_mod

        api_mod.pipeline = mock_pipeline
        api_mod.rate_limiter = mock_limiter

        with TestClient(app) as c:
            yield c


# ── Register ───────────────────────────────────────────────────────────────


@patch("api.auth.UserRepository")
@patch("api.auth.AuthService")
def test_register_success(MockAuth, MockRepo, client):
    MockAuth.validate_email.return_value = (True, "")
    MockAuth.validate_password.return_value = (True, "")
    mock_auth = MockAuth.return_value
    mock_auth.hash_password.return_value = "salt:hash"

    mock_repo = MockRepo.return_value
    mock_repo.user_exists.return_value = False
    mock_repo.create_user.return_value = "user-123"

    resp = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["plan_tier"] == "free"
    assert data["user"]["analyses_used"] == 0
    assert data["user"]["analyses_limit"] == 3


@patch("api.auth.UserRepository")
@patch("api.auth.AuthService")
def test_register_duplicate_email(MockAuth, MockRepo, client):
    MockAuth.validate_email.return_value = (True, "")
    MockAuth.validate_password.return_value = (True, "")
    mock_repo = MockRepo.return_value
    mock_repo.user_exists.return_value = True

    resp = client.post(
        "/auth/register",
        json={"email": "taken@example.com", "password": "password123"},
    )
    assert resp.status_code == 409
    assert "already registered" in resp.json()["error"]


@patch("api.auth.AuthService")
def test_register_invalid_email(MockAuth, client):
    MockAuth.validate_email.return_value = (False, "Please enter a valid email address.")
    MockAuth.validate_password.return_value = (True, "")

    resp = client.post(
        "/auth/register",
        json={"email": "notanemail", "password": "password123"},
    )
    assert resp.status_code == 422
    assert "email" in resp.json()["error"].lower()


def test_register_short_password(client):
    """Password < 8 chars should fail Pydantic validation."""
    resp = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "short"},
    )
    assert resp.status_code == 422


# ── Login ──────────────────────────────────────────────────────────────────


@patch("api.auth.UserRepository")
@patch("api.auth.AuthService")
def test_login_success(MockAuth, MockRepo, client):
    mock_repo = MockRepo.return_value
    mock_repo.get_user_by_email.return_value = {
        "id": "user-123",
        "email": "test@example.com",
        "password_hash": "salt:hash",
        "plan_tier": "free",
    }
    mock_repo.count_monthly_analyses.return_value = 1

    mock_auth = MockAuth.return_value
    mock_auth.verify_password.return_value = True

    resp = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["analyses_used"] == 1


@patch("api.auth.UserRepository")
@patch("api.auth.AuthService")
def test_login_wrong_password(MockAuth, MockRepo, client):
    mock_repo = MockRepo.return_value
    mock_repo.get_user_by_email.return_value = {
        "id": "user-123",
        "email": "test@example.com",
        "password_hash": "salt:hash",
        "plan_tier": "free",
    }
    mock_auth = MockAuth.return_value
    mock_auth.verify_password.return_value = False

    resp = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrongpass123"},
    )
    assert resp.status_code == 401
    assert "Invalid" in resp.json()["error"]


@patch("api.auth.UserRepository")
def test_login_nonexistent_email(MockRepo, client):
    mock_repo = MockRepo.return_value
    mock_repo.get_user_by_email.return_value = None

    resp = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    assert resp.status_code == 401
    assert "Invalid" in resp.json()["error"]


# ── GET /auth/me ───────────────────────────────────────────────────────────


@patch("api.auth.UserRepository")
def test_me_with_valid_token(MockRepo, client):
    mock_repo = MockRepo.return_value
    mock_repo.get_user_by_email.return_value = {
        "id": "user-123",
        "email": "test@example.com",
        "password_hash": "salt:hash",
        "plan_tier": "free",
    }
    mock_repo.count_monthly_analyses.return_value = 2

    from api.auth import create_token

    token = create_token("user-123", "test@example.com")

    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["analyses_used"] == 2


def test_me_without_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_with_invalid_token(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401
