"""Tests for usage limit checking (free vs pro vs anonymous)."""

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
            c._mock_pipeline = mock_pipeline
            c._mock_limiter = mock_limiter
            yield c


VALID_RESUME = "A" * 100
VALID_JOB = "B" * 100

PIPELINE_RESULT = {
    "match_score": 70.0,
    "learning_priority": "Medium",
    "missing_skills": ["Docker"],
    "learning_path": [{"skill": "Docker", "estimated_weeks": 2, "estimated_days": 14}],
    "evidence": [{"skill": "Docker", "project": "P", "description": "D", "deliverables": [], "estimated_weeks": 2}],
    "interview_prep": [],
    "rubrics": [],
    "related_jobs": [],
    "request_id": "req-1",
    "latency_ms": 500,
}


# ── Anonymous user (no token) — uses rate limiter ────────────────────────────


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
def test_anonymous_allowed_when_rate_limit_ok(client):
    """Anonymous users go through rate limiter, not usage limits."""
    client._mock_pipeline.run.return_value = PIPELINE_RESULT

    resp = client.post("/analyze", json={"resume": VALID_RESUME, "target_job": VALID_JOB})
    assert resp.status_code == 200
    # Rate limiter was checked
    client._mock_limiter.check.assert_called()


# ── Free user under limit ────────────────────────────────────────────────────


@patch("api.main.check_usage_limit")
@patch("api.main.get_optional_user")
@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
def test_free_user_under_limit(mock_get_user, mock_check, client):
    """Free user with < 3 analyses should be allowed."""
    mock_get_user.return_value = {"id": "u1", "email": "a@b.com", "plan_tier": "free"}
    mock_check.return_value = (True, "")
    client._mock_pipeline.run.return_value = PIPELINE_RESULT

    resp = client.post("/analyze", json={"resume": VALID_RESUME, "target_job": VALID_JOB})
    assert resp.status_code == 200


# ── Free user at limit ───────────────────────────────────────────────────────


@patch("api.main.check_usage_limit")
@patch("api.main.get_optional_user")
@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
def test_free_user_at_limit(mock_get_user, mock_check, client):
    """Free user who has used 3 analyses should get 403."""
    mock_get_user.return_value = {"id": "u1", "email": "a@b.com", "plan_tier": "free"}
    mock_check.return_value = (False, "Free tier limit reached (3 analyses per month).")

    resp = client.post("/analyze", json={"resume": VALID_RESUME, "target_job": VALID_JOB})
    assert resp.status_code == 403
    assert "limit" in resp.json()["error"].lower()


# ── Pro user — always allowed ────────────────────────────────────────────────


@patch("api.main.check_usage_limit")
@patch("api.main.get_optional_user")
@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
def test_pro_user_always_allowed(mock_get_user, mock_check, client):
    """Pro user should always be allowed regardless of usage count."""
    mock_get_user.return_value = {"id": "u2", "email": "pro@b.com", "plan_tier": "pro"}
    mock_check.return_value = (True, "")
    client._mock_pipeline.run.return_value = PIPELINE_RESULT

    resp = client.post("/analyze", json={"resume": VALID_RESUME, "target_job": VALID_JOB})
    assert resp.status_code == 200


# ── Unit test: check_usage_limit function ────────────────────────────────────


@patch("api.middleware.UserRepository")
def test_check_usage_limit_free_under(MockRepo):
    """check_usage_limit returns allowed when under limit."""
    mock_repo = MockRepo.return_value
    mock_repo.count_monthly_analyses.return_value = 2

    from api.middleware import check_usage_limit

    allowed, msg = check_usage_limit({"id": "u1", "plan_tier": "free"})
    assert allowed is True
    assert msg == ""


@patch("api.middleware.UserRepository")
def test_check_usage_limit_free_at_limit(MockRepo):
    """check_usage_limit returns blocked when at limit."""
    mock_repo = MockRepo.return_value
    mock_repo.count_monthly_analyses.return_value = 3

    from api.middleware import check_usage_limit

    allowed, msg = check_usage_limit({"id": "u1", "plan_tier": "free"})
    assert allowed is False
    assert "Upgrade" in msg


def test_check_usage_limit_pro():
    """check_usage_limit always allows pro users."""
    from api.middleware import check_usage_limit

    allowed, msg = check_usage_limit({"id": "u1", "plan_tier": "pro"})
    assert allowed is True


def test_check_usage_limit_anonymous():
    """check_usage_limit allows anonymous (None) users."""
    from api.middleware import check_usage_limit

    allowed, msg = check_usage_limit(None)
    assert allowed is True
