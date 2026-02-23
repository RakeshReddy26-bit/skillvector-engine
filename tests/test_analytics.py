"""Tests for AnalyticsTracker."""

import json
import pytest
from src.db.database import get_connection, init_db
from src.db.models import EventRepository, AnalysisRepository, FeedbackRepository, UserRepository
from src.analytics.tracker import AnalyticsTracker


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Use a temporary database for each test."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("src.db.database.DB_PATH", db_path)
    init_db()
    yield


class TestAnalyticsTracker:
    def test_overview_empty(self):
        tracker = AnalyticsTracker()
        overview = tracker.get_overview()
        assert overview["total_analyses"] == 0
        assert overview["total_registrations"] == 0

    def test_overview_with_events(self):
        events = EventRepository()
        events.track("analysis", user_id="u1")
        events.track("analysis", user_id="u2")
        events.track("analysis_anonymous")
        events.track("register", user_id="u1")

        tracker = AnalyticsTracker()
        overview = tracker.get_overview()
        assert overview["total_analyses"] == 3
        assert overview["authenticated_analyses"] == 2
        assert overview["anonymous_analyses"] == 1
        assert overview["total_registrations"] == 1

    def test_feedback_summary_empty(self):
        tracker = AnalyticsTracker()
        summary = tracker.get_feedback_summary()
        assert summary["total"] == 0
        assert summary["satisfaction_rate"] == 0

    def test_feedback_summary_with_data(self):
        users = UserRepository()
        user_id = users.create_user("test@test.com", "hash")
        analyses = AnalysisRepository()
        aid = analyses.save_analysis(
            user_id=user_id,
            resume_text="test resume",
            job_text="test job",
            result={"match_score": 70, "learning_priority": "Medium",
                    "missing_skills": [], "learning_path": [], "evidence": []},
        )

        fb = FeedbackRepository()
        fb.save_feedback(aid, is_positive=True, user_id=user_id)
        fb.save_feedback(aid, is_positive=True, user_id=user_id)
        fb.save_feedback(aid, is_positive=False, user_id=user_id, comment="Needs work")

        tracker = AnalyticsTracker()
        summary = tracker.get_feedback_summary()
        assert summary["total"] == 3
        assert summary["positive"] == 2
        assert summary["negative"] == 1
        assert summary["satisfaction_rate"] == pytest.approx(66.7, abs=0.1)

    def test_score_distribution(self):
        users = UserRepository()
        user_id = users.create_user("dist@test.com", "hash")
        analyses = AnalysisRepository()

        # Create analyses with different scores
        for score in [30, 45, 60, 70, 80, 90]:
            analyses.save_analysis(
                user_id=user_id,
                resume_text="test",
                job_text="test",
                result={"match_score": score, "learning_priority": "Medium",
                        "missing_skills": [], "learning_path": [], "evidence": []},
            )

        tracker = AnalyticsTracker()
        dist = tracker.get_score_distribution()
        assert dist["low"] == 2    # 30, 45
        assert dist["medium"] == 2  # 60, 70
        assert dist["high"] == 2   # 80, 90
        assert dist["total"] == 6

    def test_top_missing_skills(self):
        users = UserRepository()
        user_id = users.create_user("skills@test.com", "hash")
        analyses = AnalysisRepository()

        analyses.save_analysis(
            user_id=user_id,
            resume_text="test",
            job_text="test",
            result={"match_score": 50, "learning_priority": "Medium",
                    "missing_skills": ["Docker", "Kubernetes"],
                    "learning_path": [], "evidence": []},
        )
        analyses.save_analysis(
            user_id=user_id,
            resume_text="test",
            job_text="test",
            result={"match_score": 50, "learning_priority": "Medium",
                    "missing_skills": ["Docker", "CI/CD"],
                    "learning_path": [], "evidence": []},
        )

        tracker = AnalyticsTracker()
        top = tracker.get_top_missing_skills()
        assert len(top) > 0
        assert top[0]["skill"] == "docker"
        assert top[0]["count"] == 2
