"""Tests for Skill Trends Analytics — Phase 1.

Tests cover:
- SQLite persistence of skill_trend_events
- SkillTrendsAggregator.get_report (weekly/monthly)
- SkillTrendsAggregator.get_skill_trend (per-skill history)
- SkillTrendsAggregator.generate_weekly_snapshot
- daily_stats.record_analysis persistence
- /trends/* API endpoints
"""

import asyncio
import json
import pytest
from unittest.mock import patch

from src.db.database import get_connection, init_db
from src.analytics.skill_trends import SkillTrendsAggregator
from src.analytics.daily_stats import record_analysis


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Use a temporary database for each test."""
    db_path = tmp_path / "test_trends.db"
    monkeypatch.setattr("src.db.database.DB_PATH", db_path)
    monkeypatch.setattr("src.analytics.daily_stats.get_connection", get_connection)
    init_db()
    yield


def _insert_events(events: list[tuple]):
    """Helper to insert skill_trend_events directly."""
    conn = get_connection()
    try:
        for skill, score, role in events:
            conn.execute(
                "INSERT INTO skill_trend_events (skill_name, match_score, target_role) VALUES (?, ?, ?)",
                (skill, score, role),
            )
        conn.commit()
    finally:
        conn.close()


def _insert_events_with_date(events: list[tuple]):
    """Helper to insert events with specific dates for trend testing."""
    conn = get_connection()
    try:
        for skill, score, role, created_at in events:
            conn.execute(
                "INSERT INTO skill_trend_events (skill_name, match_score, target_role, created_at) "
                "VALUES (?, ?, ?, ?)",
                (skill, score, role, created_at),
            )
        conn.commit()
    finally:
        conn.close()


# ── SkillTrendsAggregator unit tests ───────────────────


class TestSkillTrendsAggregator:
    def test_empty_report(self):
        agg = SkillTrendsAggregator()
        report = agg.get_report("weekly")
        assert report["total_analyses"] == 0
        assert report["avg_market_score"] == 0.0
        assert report["top_gaps"] == []
        assert report["period"] == "weekly"

    def test_report_with_data(self):
        _insert_events([
            ("Kubernetes", 55.0, "Senior ML Engineer"),
            ("Kubernetes", 60.0, "Backend Engineer"),
            ("MLOps", 45.0, "Senior ML Engineer"),
            ("Docker", 70.0, "DevOps Engineer"),
        ])

        agg = SkillTrendsAggregator()
        report = agg.get_report("weekly")

        assert report["total_analyses"] == 4
        assert report["avg_market_score"] > 0
        assert len(report["top_gaps"]) >= 1
        # Kubernetes should be the top gap (2 occurrences)
        top_skill = report["top_gaps"][0]["skill"]
        assert top_skill == "Kubernetes"
        assert report["top_gaps"][0]["frequency"] == 2

    def test_report_monthly_period(self):
        _insert_events([
            ("Python", 80.0, "Data Scientist"),
        ])

        agg = SkillTrendsAggregator()
        report = agg.get_report("monthly")
        assert report["period"] == "monthly"
        assert report["days"] == 30
        assert report["total_analyses"] == 1

    def test_role_demand(self):
        _insert_events([
            ("Python", 80.0, "ML Engineer"),
            ("Docker", 60.0, "ML Engineer"),
            ("Kubernetes", 55.0, "ML Engineer"),
            ("SQL", 75.0, "Data Analyst"),
        ])

        agg = SkillTrendsAggregator()
        report = agg.get_report("weekly")
        roles = report["role_demand"]
        assert len(roles) >= 1
        assert roles[0]["role"] == "ML Engineer"
        assert roles[0]["count"] == 3

    def test_get_skill_trend_no_data(self):
        agg = SkillTrendsAggregator()
        trend = agg.get_skill_trend("NonexistentSkill")
        assert trend["total_appearances"] == 0
        assert trend["weekly_data"] == []

    def test_get_skill_trend_with_data(self):
        _insert_events([
            ("MLOps", 50.0, "ML Engineer"),
            ("MLOps", 55.0, "Data Scientist"),
            ("MLOps", 60.0, "ML Engineer"),
        ])

        agg = SkillTrendsAggregator()
        trend = agg.get_skill_trend("MLOps")
        assert trend["skill"] == "MLOps"
        assert trend["total_appearances"] == 3
        assert trend["overall_avg_score"] == 55.0
        assert len(trend["weekly_data"]) >= 1

    def test_get_all_tracked_skills_empty(self):
        agg = SkillTrendsAggregator()
        skills = agg.get_all_tracked_skills()
        assert skills == []

    def test_get_all_tracked_skills(self):
        _insert_events([
            ("Python", 80.0, "Backend Engineer"),
            ("Docker", 60.0, "DevOps Engineer"),
            ("MLOps", 50.0, "ML Engineer"),
        ])

        agg = SkillTrendsAggregator()
        skills = agg.get_all_tracked_skills()
        assert "Docker" in skills
        assert "MLOps" in skills
        assert "Python" in skills
        assert len(skills) == 3

    def test_generate_weekly_snapshot_empty(self):
        agg = SkillTrendsAggregator()
        count = agg.generate_weekly_snapshot()
        assert count == 0

    def test_generate_weekly_snapshot(self):
        _insert_events([
            ("Kubernetes", 55.0, "Senior ML Engineer"),
            ("Kubernetes", 60.0, "Backend Engineer"),
            ("MLOps", 45.0, "Senior ML Engineer"),
        ])

        agg = SkillTrendsAggregator()
        count = agg.generate_weekly_snapshot()
        assert count == 2  # Kubernetes + MLOps

        # Verify snapshots were stored
        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM skill_trend_snapshots").fetchall()
            assert len(rows) == 2
            skills = {r["skill_name"] for r in rows}
            assert "Kubernetes" in skills
            assert "MLOps" in skills
        finally:
            conn.close()

    def test_snapshot_trend_direction(self):
        """New skills should have 'new' direction."""
        _insert_events([
            ("NewSkill", 50.0, "Engineer"),
        ])

        agg = SkillTrendsAggregator()
        agg.generate_weekly_snapshot()

        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT trend_direction FROM skill_trend_snapshots WHERE skill_name = ?",
                ("NewSkill",),
            ).fetchone()
            assert row["trend_direction"] == "new"
        finally:
            conn.close()

    def test_rising_declining_trends(self):
        """Test trend comparison between two periods."""
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        # Old period (8-14 days ago): Kubernetes appeared 2 times
        old_date = (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
        # Current period (0-7 days ago): Kubernetes appeared 5 times
        new_date = (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")

        _insert_events_with_date([
            ("Kubernetes", 50.0, "Engineer", old_date),
            ("Kubernetes", 55.0, "Engineer", old_date),
            ("Kubernetes", 50.0, "Engineer", new_date),
            ("Kubernetes", 55.0, "Engineer", new_date),
            ("Kubernetes", 60.0, "Engineer", new_date),
            ("Kubernetes", 50.0, "Engineer", new_date),
            ("Kubernetes", 55.0, "Engineer", new_date),
        ])

        agg = SkillTrendsAggregator()
        report = agg.get_report("weekly")
        # Kubernetes: 5 current vs 2 previous = +150% → rising
        rising_skills = [s["skill"] for s in report["rising_skills"]]
        assert "Kubernetes" in rising_skills


# ── daily_stats persistence tests ──────────────────────


class TestDailyStatsPersistence:
    def test_record_analysis_persists_to_db(self):
        """record_analysis should write to skill_trend_events."""
        asyncio.get_event_loop().run_until_complete(
            record_analysis(
                match_score=65,
                missing_skills=["Docker", "Kubernetes"],
                target_role="ML Engineer",
            )
        )

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM skill_trend_events").fetchall()
            assert len(rows) == 2
            skills = {r["skill_name"] for r in rows}
            assert skills == {"Docker", "Kubernetes"}
            assert rows[0]["match_score"] == 65.0
            assert rows[0]["target_role"] == "ML Engineer"
        finally:
            conn.close()

    def test_record_analysis_handles_dict_skills(self):
        """Missing skills can be dicts with 'skill' key."""
        asyncio.get_event_loop().run_until_complete(
            record_analysis(
                match_score=55,
                missing_skills=[{"skill": "MLOps"}, {"skill": "CI/CD"}],
                target_role="DevOps",
            )
        )

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM skill_trend_events").fetchall()
            skills = {r["skill_name"] for r in rows}
            assert skills == {"MLOps", "CI/CD"}
        finally:
            conn.close()

    def test_record_analysis_empty_skills(self):
        """Empty missing_skills should not crash."""
        asyncio.get_event_loop().run_until_complete(
            record_analysis(
                match_score=90,
                missing_skills=[],
                target_role="Junior Developer",
            )
        )

        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM skill_trend_events").fetchall()
            assert len(rows) == 0
        finally:
            conn.close()


# ── API endpoint tests ─────────────────────────────────


class TestTrendsAPI:
    @pytest.fixture
    def client(self):
        """Create a test client with the FastAPI app."""
        import os
        os.environ["AUTOMATION_API_KEY"] = "test-atlas-key"

        from fastapi.testclient import TestClient
        from api.main import app
        with TestClient(app) as c:
            yield c

    def test_trends_report_unauthorized(self, client):
        resp = client.get("/trends/report")
        assert resp.status_code == 403

    def test_trends_report_with_atlas_key(self, client):
        _insert_events([
            ("Python", 80.0, "ML Engineer"),
            ("Docker", 60.0, "DevOps Engineer"),
        ])

        resp = client.get(
            "/trends/report?period=weekly",
            headers={"X-Atlas-Key": "test-atlas-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["period"] == "weekly"
        assert data["total_analyses"] >= 2
        assert data["access_type"] == "atlas"

    def test_trends_report_monthly(self, client):
        _insert_events([("Kubernetes", 55.0, "Engineer")])

        resp = client.get(
            "/trends/report?period=monthly",
            headers={"X-Atlas-Key": "test-atlas-key"},
        )
        assert resp.status_code == 200
        assert resp.json()["period"] == "monthly"

    def test_trends_report_invalid_period(self, client):
        resp = client.get(
            "/trends/report?period=yearly",
            headers={"X-Atlas-Key": "test-atlas-key"},
        )
        assert resp.status_code == 422

    def test_skill_trend_endpoint(self, client):
        _insert_events([
            ("MLOps", 50.0, "ML Engineer"),
            ("MLOps", 60.0, "Data Scientist"),
        ])

        resp = client.get(
            "/trends/skill/MLOps",
            headers={"X-Atlas-Key": "test-atlas-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["skill"] == "MLOps"
        assert data["total_appearances"] == 2

    def test_skill_trend_not_found(self, client):
        resp = client.get(
            "/trends/skill/NonexistentSkill",
            headers={"X-Atlas-Key": "test-atlas-key"},
        )
        assert resp.status_code == 404

    def test_list_tracked_skills(self, client):
        _insert_events([
            ("Python", 80.0, "Engineer"),
            ("Docker", 60.0, "DevOps"),
        ])

        resp = client.get(
            "/trends/skills",
            headers={"X-Atlas-Key": "test-atlas-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2
        assert "Python" in data["skills"]
        assert "Docker" in data["skills"]

    def test_snapshot_endpoint(self, client):
        _insert_events([
            ("Kubernetes", 55.0, "Engineer"),
            ("MLOps", 50.0, "ML Engineer"),
        ])

        resp = client.post(
            "/trends/snapshot",
            headers={"X-Atlas-Key": "test-atlas-key"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["snapshots_created"] == 2

    def test_snapshot_unauthorized(self, client):
        resp = client.post("/trends/snapshot")
        assert resp.status_code == 403

    def test_b2b_api_key_access(self, client, monkeypatch):
        monkeypatch.setenv("B2B_TRENDS_API_KEY", "b2b-test-key")
        _insert_events([("Python", 80.0, "Engineer")])

        resp = client.get(
            "/trends/report",
            headers={"Authorization": "Bearer b2b-test-key"},
        )
        assert resp.status_code == 200
        assert resp.json()["access_type"] == "b2b"
