"""Skill Trends Aggregator for SkillVector Engine.

Queries persisted skill_trend_events to compute anonymized
market intelligence: top gaps, rising/declining skills, role demand.

Data source: skill_trend_events table (populated by daily_stats.record_analysis).
Snapshot storage: skill_trend_snapshots table (weekly aggregates for fast reads).
"""

import json
import logging
import uuid
from collections import Counter
from datetime import date, datetime, timedelta

from src.db.database import get_connection

logger = logging.getLogger(__name__)


class SkillTrendsAggregator:
    """Aggregates anonymized skill gap data into market trend reports."""

    # ── Core queries ────────────────────────────────────────

    def get_report(self, period: str = "weekly") -> dict:
        """Generate a full trend report for the given period.

        Args:
            period: "weekly" (last 7 days) or "monthly" (last 30 days).

        Returns a dict with top_gaps, rising/declining skills, role demand, etc.
        """
        days = 7 if period == "weekly" else 30
        conn = get_connection()
        try:
            # Total analyses in period
            total_row = conn.execute(
                "SELECT COUNT(DISTINCT id) as cnt FROM skill_trend_events "
                "WHERE created_at >= datetime('now', ? || ' days')",
                (f"-{days}",),
            ).fetchone()
            total = total_row["cnt"] if total_row else 0

            # Top skill gaps by frequency
            top_gaps = self._top_gaps(conn, days)

            # Average match score across all events
            avg_row = conn.execute(
                "SELECT AVG(match_score) as avg_score FROM skill_trend_events "
                "WHERE created_at >= datetime('now', ? || ' days')",
                (f"-{days}",),
            ).fetchone()
            avg_score = round(avg_row["avg_score"], 1) if avg_row and avg_row["avg_score"] else 0.0

            # Role demand
            role_rows = conn.execute(
                "SELECT target_role, COUNT(*) as cnt FROM skill_trend_events "
                "WHERE created_at >= datetime('now', ? || ' days') "
                "GROUP BY target_role ORDER BY cnt DESC LIMIT 10",
                (f"-{days}",),
            ).fetchall()
            roles = [{"role": r["target_role"], "count": r["cnt"]} for r in role_rows]

            # Rising and declining skills (compare current period vs previous)
            rising, declining = self._compute_trends(conn, days)

            return {
                "period": period,
                "days": days,
                "total_analyses": total,
                "avg_market_score": avg_score,
                "top_gaps": top_gaps,
                "rising_skills": rising,
                "declining_gaps": declining,
                "role_demand": roles,
                "generated_at": datetime.utcnow().isoformat(),
            }
        finally:
            conn.close()

    def get_skill_trend(self, skill_name: str, weeks: int = 12) -> dict:
        """Get trend data for a specific skill over time.

        Returns weekly frequency + avg_score data points.
        """
        conn = get_connection()
        try:
            rows = conn.execute(
                """SELECT
                    strftime('%%Y-%%W', created_at) as week,
                    COUNT(*) as frequency,
                    AVG(match_score) as avg_score
                FROM skill_trend_events
                WHERE skill_name = ?
                  AND created_at >= datetime('now', ? || ' days')
                GROUP BY week
                ORDER BY week ASC""",
                (skill_name, f"-{weeks * 7}"),
            ).fetchall()

            data_points = [
                {
                    "week": r["week"],
                    "frequency": r["frequency"],
                    "avg_score": round(r["avg_score"], 1),
                }
                for r in rows
            ]

            # Overall stats for this skill
            total_row = conn.execute(
                "SELECT COUNT(*) as cnt, AVG(match_score) as avg_score "
                "FROM skill_trend_events WHERE skill_name = ?",
                (skill_name,),
            ).fetchone()

            return {
                "skill": skill_name,
                "total_appearances": total_row["cnt"] if total_row else 0,
                "overall_avg_score": round(total_row["avg_score"], 1) if total_row and total_row["avg_score"] else 0.0,
                "weekly_data": data_points,
                "generated_at": datetime.utcnow().isoformat(),
            }
        finally:
            conn.close()

    def get_all_tracked_skills(self) -> list[str]:
        """Return all skill names that have been tracked."""
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT DISTINCT skill_name FROM skill_trend_events ORDER BY skill_name"
            ).fetchall()
            return [r["skill_name"] for r in rows]
        finally:
            conn.close()

    # ── Snapshot generation (called by Scout agent or cron) ──

    def generate_weekly_snapshot(self) -> int:
        """Aggregate last 7 days into skill_trend_snapshots.

        Returns the number of skill snapshots created.
        """
        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()

        conn = get_connection()
        try:
            rows = conn.execute(
                """SELECT
                    skill_name,
                    COUNT(*) as frequency,
                    AVG(match_score) as avg_score,
                    target_role
                FROM skill_trend_events
                WHERE created_at >= datetime('now', '-7 days')
                GROUP BY skill_name"""
            ).fetchall()

            count = 0
            for row in rows:
                skill = row["skill_name"]
                freq = row["frequency"]
                avg_score = round(row["avg_score"], 1)

                # Get top roles for this skill
                role_rows = conn.execute(
                    "SELECT target_role, COUNT(*) as cnt FROM skill_trend_events "
                    "WHERE skill_name = ? AND created_at >= datetime('now', '-7 days') "
                    "GROUP BY target_role ORDER BY cnt DESC LIMIT 3",
                    (skill,),
                ).fetchall()
                top_roles = [r["target_role"] for r in role_rows]

                # Compute trend vs previous week
                prev_row = conn.execute(
                    "SELECT gap_frequency FROM skill_trend_snapshots "
                    "WHERE skill_name = ? AND week_start < ? "
                    "ORDER BY week_start DESC LIMIT 1",
                    (skill, week_start),
                ).fetchone()

                if prev_row:
                    prev_freq = prev_row["gap_frequency"]
                    if freq > prev_freq * 1.1:
                        direction = "rising"
                    elif freq < prev_freq * 0.9:
                        direction = "falling"
                    else:
                        direction = "stable"
                else:
                    direction = "new"

                snapshot_id = str(uuid.uuid4())
                conn.execute(
                    """INSERT OR REPLACE INTO skill_trend_snapshots
                    (id, week_start, skill_name, gap_frequency, avg_match_score, top_roles, trend_direction)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (snapshot_id, week_start, skill, freq, avg_score, json.dumps(top_roles), direction),
                )
                count += 1

            conn.commit()
            logger.info("Generated %d weekly skill trend snapshots for week %s", count, week_start)
            return count
        finally:
            conn.close()

    # ── Internal helpers ────────────────────────────────────

    def _top_gaps(self, conn, days: int) -> list[dict]:
        """Get top skill gaps ranked by frequency."""
        rows = conn.execute(
            "SELECT skill_name, COUNT(*) as frequency, AVG(match_score) as avg_score "
            "FROM skill_trend_events "
            "WHERE created_at >= datetime('now', ? || ' days') "
            "GROUP BY skill_name ORDER BY frequency DESC LIMIT 15",
            (f"-{days}",),
        ).fetchall()

        return [
            {
                "skill": r["skill_name"],
                "frequency": r["frequency"],
                "avg_score": round(r["avg_score"], 1),
            }
            for r in rows
        ]

    def _compute_trends(self, conn, days: int) -> tuple[list[dict], list[dict]]:
        """Compare current period vs previous period to find rising/declining skills."""
        # Current period counts
        current_rows = conn.execute(
            "SELECT skill_name, COUNT(*) as cnt FROM skill_trend_events "
            "WHERE created_at >= datetime('now', ? || ' days') "
            "GROUP BY skill_name",
            (f"-{days}",),
        ).fetchall()
        current = {r["skill_name"]: r["cnt"] for r in current_rows}

        # Previous period counts (same window, shifted back)
        prev_rows = conn.execute(
            "SELECT skill_name, COUNT(*) as cnt FROM skill_trend_events "
            "WHERE created_at >= datetime('now', ? || ' days') "
            "AND created_at < datetime('now', ? || ' days') "
            "GROUP BY skill_name",
            (f"-{days * 2}", f"-{days}"),
        ).fetchall()
        previous = {r["skill_name"]: r["cnt"] for r in prev_rows}

        rising = []
        declining = []

        for skill, count in current.items():
            prev_count = previous.get(skill, 0)
            if prev_count == 0:
                if count >= 2:
                    rising.append({"skill": skill, "current": count, "previous": 0, "change": "+new"})
            else:
                pct = round((count - prev_count) / prev_count * 100)
                if pct > 10:
                    rising.append({"skill": skill, "current": count, "previous": prev_count, "change": f"+{pct}%"})
                elif pct < -10:
                    declining.append({"skill": skill, "current": count, "previous": prev_count, "change": f"{pct}%"})

        rising.sort(key=lambda x: x["current"], reverse=True)
        declining.sort(key=lambda x: x["current"], reverse=True)

        return rising[:10], declining[:10]
