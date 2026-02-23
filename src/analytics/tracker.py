"""Analytics tracker for SkillVector Engine.

Provides higher-level analytics on top of the EventRepository,
computing metrics, trends, and insights.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from src.db.models import EventRepository, AnalysisRepository, FeedbackRepository, UserRepository

logger = logging.getLogger(__name__)


class AnalyticsTracker:
    """Computes analytics and metrics from stored events and analyses."""

    def __init__(self) -> None:
        self.events = EventRepository()
        self.analyses = AnalysisRepository()
        self.feedback = FeedbackRepository()
        self.users = UserRepository()

    def get_overview(self) -> dict:
        """Get high-level platform metrics."""
        total_analyses = self.events.count_events("analysis")
        anonymous_analyses = self.events.count_events("analysis_anonymous")
        total_registrations = self.events.count_events("register")
        total_logins = self.events.count_events("login")

        return {
            "total_analyses": total_analyses + anonymous_analyses,
            "authenticated_analyses": total_analyses,
            "anonymous_analyses": anonymous_analyses,
            "total_registrations": total_registrations,
            "total_logins": total_logins,
        }

    def get_daily_activity(self, days: int = 30) -> list[dict]:
        """Get daily event counts for charting."""
        return self.events.get_daily_stats(days)

    def get_feedback_summary(self) -> dict:
        """Get summary of user feedback."""
        from src.db.database import get_connection

        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT COUNT(*) as total, "
                "SUM(CASE WHEN is_positive = 1 THEN 1 ELSE 0 END) as positive, "
                "SUM(CASE WHEN is_positive = 0 THEN 1 ELSE 0 END) as negative "
                "FROM feedback"
            ).fetchone()

            total = row["total"]
            positive = row["positive"] or 0
            negative = row["negative"] or 0

            return {
                "total": total,
                "positive": positive,
                "negative": negative,
                "satisfaction_rate": round(positive / total * 100, 1) if total > 0 else 0,
            }
        finally:
            conn.close()

    def get_score_distribution(self) -> dict:
        """Get distribution of match scores across all analyses."""
        from src.db.database import get_connection

        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT match_score FROM analyses"
            ).fetchall()

            if not rows:
                return {"low": 0, "medium": 0, "high": 0, "average": 0}

            scores = [row["match_score"] for row in rows]
            low = sum(1 for s in scores if s < 50)
            medium = sum(1 for s in scores if 50 <= s < 75)
            high = sum(1 for s in scores if s >= 75)

            return {
                "low": low,
                "medium": medium,
                "high": high,
                "average": round(sum(scores) / len(scores), 1),
                "total": len(scores),
            }
        finally:
            conn.close()

    def get_top_missing_skills(self, limit: int = 10) -> list[dict]:
        """Get the most commonly missing skills across all analyses."""
        import json
        from src.db.database import get_connection

        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT missing_skills FROM analyses"
            ).fetchall()

            skill_counts: dict[str, int] = {}
            for row in rows:
                skills = json.loads(row["missing_skills"])
                for skill in skills:
                    skill_lower = skill.lower().strip()
                    skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1

            sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
            return [
                {"skill": skill, "count": count}
                for skill, count in sorted_skills[:limit]
            ]
        finally:
            conn.close()

    def get_recent_feedback(self, limit: int = 20) -> list[dict]:
        """Get recent feedback entries with comments."""
        from src.db.database import get_connection

        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT f.id, f.is_positive, f.comment, f.created_at, "
                "a.match_score "
                "FROM feedback f "
                "LEFT JOIN analyses a ON f.analysis_id = a.id "
                "ORDER BY f.created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
