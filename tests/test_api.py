"""Tests for the FastAPI /health and /analyze endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture()
def client():
    """Create a TestClient with mocked pipeline and rate limiter."""
    with patch("api.main.SkillVectorPipeline") as MockPipeline, \
         patch("api.main.RateLimiter") as MockLimiter:
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


VALID_RESUME = "A" * 100  # meets 50 char minimum
VALID_JOB = "B" * 100     # meets 50 char minimum


# ── Health ──────────────────────────────────────────────────────────────────


@patch("api.main.check_health")
def test_health_returns_200(mock_health, client):
    mock_health.return_value = {
        "status": "healthy",
        "version": "0.2.0",
        "model": "claude-sonnet-4-20250514",
        "anthropic": "ok",
        "neo4j": "ok",
        "pinecone": "ok",
        "checks_ms": 42,
    }
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.2.0"


# ── Analyze — success ──────────────────────────────────────────────────────


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
def test_analyze_returns_result(client):
    client._mock_pipeline.run.return_value = {
        "match_score": 72.5,
        "learning_priority": "Medium",
        "missing_skills": ["Docker", "Kubernetes"],
        "learning_path": [{"skill": "Docker", "estimated_weeks": 2, "estimated_days": 14}],
        "evidence": [{"skill": "Docker", "project": "Dockerize App", "description": "Build it", "deliverables": ["Dockerfile"], "estimated_weeks": 2}],
        "interview_prep": [{"skill": "Docker", "questions": ["What is Docker?"], "difficulty": "Foundational", "tips": ["Practice"]}],
        "rubrics": [{"skill": "Docker", "criteria": [], "scoring": {}, "total_points": 100}],
        "related_jobs": [{"score": 0.85, "job_title": "DevOps Engineer", "company": "Acme", "skills": ["Docker"], "chunk": ""}],
        "request_id": "abc123",
        "latency_ms": 1500,
    }
    resp = client.post("/analyze", json={"resume": VALID_RESUME, "target_job": VALID_JOB})
    assert resp.status_code == 200
    data = resp.json()
    assert data["match_score"] == 72.5
    assert data["learning_priority"] == "Medium"
    assert len(data["missing_skills"]) == 2
    assert data["request_id"] == "abc123"


# ── Analyze — validation errors ────────────────────────────────────────────


def test_analyze_rejects_empty_resume(client):
    resp = client.post("/analyze", json={"resume": "", "target_job": VALID_JOB})
    assert resp.status_code == 422


def test_analyze_rejects_short_resume(client):
    resp = client.post("/analyze", json={"resume": "too short", "target_job": VALID_JOB})
    assert resp.status_code == 422


def test_analyze_rejects_short_job(client):
    resp = client.post("/analyze", json={"resume": VALID_RESUME, "target_job": "short"})
    assert resp.status_code == 422


def test_analyze_rejects_missing_fields(client):
    resp = client.post("/analyze", json={})
    assert resp.status_code == 422


# ── CORS ────────────────────────────────────────────────────────────────────


def test_cors_allows_github_pages(client):
    resp = client.options(
        "/analyze",
        headers={
            "Origin": "https://rakeshreddy26-bit.github.io",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "https://rakeshreddy26-bit.github.io"


def test_cors_blocks_unknown_origin(client):
    resp = client.options(
        "/analyze",
        headers={
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.headers.get("access-control-allow-origin") != "https://evil.com"


# ── Rate limiting ──────────────────────────────────────────────────────────


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
def test_analyze_rate_limiting(client):
    client._mock_limiter.check.return_value = (False, "Rate limit exceeded. Try again in 30 minutes.")
    resp = client.post("/analyze", json={"resume": VALID_RESUME, "target_job": VALID_JOB})
    assert resp.status_code == 429
    data = resp.json()
    assert "Rate limit" in data["error"]
