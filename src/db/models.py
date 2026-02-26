"""Data access layer for SkillVector Engine."""

import json
import logging
import uuid
from typing import Optional

from src.db.database import get_connection

logger = logging.getLogger(__name__)


class UserRepository:
    """Data access for user accounts."""

    def create_user(self, email: str, password_hash: str, auth_provider: str = "email") -> str:
        """Create a new user. Returns user ID."""
        user_id = str(uuid.uuid4())
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO users (id, email, password_hash, auth_provider) VALUES (?, ?, ?, ?)",
                (user_id, email.lower().strip(), password_hash, auth_provider),
            )
            conn.commit()
            logger.info("Created user %s via %s", email, auth_provider)
            return user_id
        except Exception as e:
            logger.error("Failed to create user %s: %s", email, e)
            raise
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Find a user by email. Returns dict or None."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT id, email, password_hash, plan_tier, stripe_customer_id, "
                "stripe_subscription_id, created_at FROM users WHERE email = ?",
                (email.lower().strip(),),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def user_exists(self, email: str) -> bool:
        """Check if a user email is already registered."""
        return self.get_user_by_email(email) is not None

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Find a user by ID."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT id, email, password_hash, plan_tier, stripe_customer_id, "
                "stripe_subscription_id, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def update_plan(
        self,
        user_id: str,
        plan_tier: str,
        stripe_customer_id: str = None,
        stripe_subscription_id: str = None,
    ) -> None:
        """Update user plan tier and Stripe IDs."""
        conn = get_connection()
        try:
            conn.execute(
                """UPDATE users SET plan_tier = ?,
                   stripe_customer_id = COALESCE(?, stripe_customer_id),
                   stripe_subscription_id = COALESCE(?, stripe_subscription_id)
                   WHERE id = ?""",
                (plan_tier, stripe_customer_id, stripe_subscription_id, user_id),
            )
            conn.commit()
            logger.info("Updated plan for user %s to %s", user_id, plan_tier)
        finally:
            conn.close()

    def get_user_by_stripe_customer(self, stripe_customer_id: str) -> Optional[dict]:
        """Find a user by Stripe customer ID."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT id, email, password_hash, plan_tier, stripe_customer_id, "
                "stripe_subscription_id, created_at FROM users WHERE stripe_customer_id = ?",
                (stripe_customer_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def count_monthly_analyses(self, user_id: str) -> int:
        """Count analyses this calendar month for a user."""
        conn = get_connection()
        try:
            row = conn.execute(
                """SELECT COUNT(*) as cnt FROM analyses
                   WHERE user_id = ?
                   AND created_at >= date('now', 'start of month')""",
                (user_id,),
            ).fetchone()
            return row["cnt"] if row else 0
        finally:
            conn.close()


class AnalysisRepository:
    """Data access for skill gap analyses."""

    def save_analysis(
        self,
        user_id: str,
        resume_text: str,
        job_text: str,
        result: dict,
    ) -> str:
        """Save an analysis result. Returns analysis ID."""
        analysis_id = str(uuid.uuid4())
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO analyses
                   (id, user_id, resume_text, job_text, match_score,
                    learning_priority, missing_skills, result_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    analysis_id,
                    user_id,
                    resume_text[:1000],  # Store truncated for space
                    job_text[:1000],
                    result.get("match_score", 0),
                    result.get("learning_priority", "Medium"),
                    json.dumps(result.get("missing_skills", [])),
                    json.dumps(result),
                ),
            )
            conn.commit()
            logger.info("Saved analysis %s for user %s", analysis_id, user_id)
            return analysis_id
        finally:
            conn.close()

    def get_user_analyses(self, user_id: str, limit: int = 20) -> list[dict]:
        """Get recent analyses for a user."""
        conn = get_connection()
        try:
            rows = conn.execute(
                """SELECT id, match_score, learning_priority, missing_skills,
                          result_json, created_at
                   FROM analyses WHERE user_id = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (user_id, limit),
            ).fetchall()
            results = []
            for row in rows:
                entry = dict(row)
                entry["missing_skills"] = json.loads(entry["missing_skills"])
                entry["result"] = json.loads(entry["result_json"])
                del entry["result_json"]
                results.append(entry)
            return results
        finally:
            conn.close()

    def get_analysis_by_id(self, analysis_id: str) -> Optional[dict]:
        """Get a single analysis by ID."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
            ).fetchone()
            if not row:
                return None
            entry = dict(row)
            entry["missing_skills"] = json.loads(entry["missing_skills"])
            entry["result"] = json.loads(entry["result_json"])
            return entry
        finally:
            conn.close()

    def count_user_analyses(self, user_id: str) -> int:
        """Count total analyses for a user."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM analyses WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            return row["cnt"]
        finally:
            conn.close()


class FeedbackRepository:
    """Data access for user feedback."""

    def save_feedback(
        self,
        analysis_id: str,
        is_positive: bool,
        user_id: str = None,
        comment: str = None,
    ) -> str:
        """Save feedback for an analysis."""
        feedback_id = str(uuid.uuid4())
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO feedback (id, analysis_id, user_id, is_positive, comment)
                   VALUES (?, ?, ?, ?, ?)""",
                (feedback_id, analysis_id, user_id, int(is_positive), comment),
            )
            conn.commit()
            return feedback_id
        finally:
            conn.close()


class EventRepository:
    """Data access for analytics events."""

    def track(self, event_type: str, user_id: str = None, metadata: dict = None) -> None:
        """Record an analytics event."""
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO events (event_type, user_id, metadata) VALUES (?, ?, ?)",
                (event_type, user_id, json.dumps(metadata) if metadata else None),
            )
            conn.commit()
        finally:
            conn.close()

    def get_daily_stats(self, days: int = 30) -> list[dict]:
        """Get daily event counts for the last N days."""
        conn = get_connection()
        try:
            rows = conn.execute(
                """SELECT date(created_at) as day, event_type, COUNT(*) as count
                   FROM events
                   WHERE created_at >= datetime('now', ? || ' days')
                   GROUP BY day, event_type
                   ORDER BY day DESC""",
                (f"-{days}",),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def count_events(self, event_type: str = None) -> int:
        """Count total events, optionally filtered by type."""
        conn = get_connection()
        try:
            if event_type:
                row = conn.execute(
                    "SELECT COUNT(*) as cnt FROM events WHERE event_type = ?",
                    (event_type,),
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) as cnt FROM events").fetchone()
            return row["cnt"]
        finally:
            conn.close()
