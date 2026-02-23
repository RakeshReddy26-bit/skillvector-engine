import pytest
import numpy as np


SAMPLE_RESUME = """
Backend Engineer with 3 years of experience in Python, FastAPI, and Django.
Built REST APIs, worked with PostgreSQL and Redis.
Deployed applications using Docker.
"""

SAMPLE_JOB = """
Senior Backend Engineer with experience in Python, Kubernetes,
cloud-native architecture, CI/CD pipelines, and microservices.
"""


@pytest.fixture
def sample_resume():
    return SAMPLE_RESUME.strip()


@pytest.fixture
def sample_job():
    return SAMPLE_JOB.strip()


@pytest.fixture
def sample_missing_skills():
    return ["Kubernetes", "CI/CD", "Docker", "Python"]


@pytest.fixture
def sample_learning_path():
    return [
        {"skill": "Docker", "estimated_weeks": 1, "estimated_days": 5},
        {"skill": "Kubernetes", "estimated_weeks": 1, "estimated_days": 7},
    ]


@pytest.fixture
def mock_llm_result():
    """Mock LLM response for skill gap analysis."""
    return {
        "match_score": 62,
        "priority": "Medium",
        "missing_skills": ["Kubernetes", "CI/CD", "Microservices"]
    }


@pytest.fixture
def mock_embedding_vector():
    """A fake normalized embedding vector."""
    vec = np.random.randn(384)
    return vec / np.linalg.norm(vec)
