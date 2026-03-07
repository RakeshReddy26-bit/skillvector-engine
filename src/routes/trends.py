"""
Trend analytics endpoints for SkillVector Engine.

Public endpoint: GET /trends/report — anonymized market skill data.
Protected endpoints require Atlas API key or valid JWT.
"""

import logging
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from src.analytics.skill_trends import SkillTrendsAggregator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/trends", tags=["trends"])


def verify_trends_access(x_atlas_key: str = Header(None), authorization: str = Header(None)):
    """Allow access via Atlas API key OR valid B2B API key.

    For Phase 1, we reuse the AUTOMATION_API_KEY. In Phase 2,
    we'll add a separate B2B_API_KEY for paid trend access.
    """
    expected = os.getenv("AUTOMATION_API_KEY", "")
    b2b_key = os.getenv("B2B_TRENDS_API_KEY", "")

    # Atlas agents
    if expected and x_atlas_key == expected:
        return "atlas"

    # B2B API key via Authorization header
    if b2b_key and authorization:
        token = authorization.replace("Bearer ", "").strip()
        if token == b2b_key:
            return "b2b"

    raise HTTPException(status_code=403, detail="Valid API key required")


# ── PUBLIC (rate-limited, anonymized) ───────────────────

@router.get("/report")
async def get_trends_report(
    period: str = Query("weekly", pattern="^(weekly|monthly)$"),
    auth: str = Depends(verify_trends_access),
):
    """Get anonymized market skill trend report.

    Returns top skill gaps, rising/declining trends, role demand,
    and average market scores. All data is anonymized — no PII.
    """
    aggregator = SkillTrendsAggregator()
    report = aggregator.get_report(period)
    report["access_type"] = auth
    return report


@router.get("/skill/{skill_name}")
async def get_skill_trend(
    skill_name: str,
    weeks: int = Query(12, ge=1, le=52),
    auth: str = Depends(verify_trends_access),
):
    """Get trend data for a specific skill over time.

    Returns weekly frequency and average match score data points.
    """
    aggregator = SkillTrendsAggregator()
    trend = aggregator.get_skill_trend(skill_name, weeks)
    if trend["total_appearances"] == 0:
        raise HTTPException(status_code=404, detail=f"No data for skill: {skill_name}")
    return trend


@router.get("/skills")
async def list_tracked_skills(auth: str = Depends(verify_trends_access)):
    """List all skills currently being tracked with trend data."""
    aggregator = SkillTrendsAggregator()
    skills = aggregator.get_all_tracked_skills()
    return {"skills": skills, "count": len(skills)}


# ── ATLAS-ONLY (snapshot generation) ───────────────────

@router.post("/snapshot")
async def generate_snapshot(
    x_atlas_key: str = Header(None),
):
    """Generate weekly trend snapshot (called by Scout agent).

    Aggregates raw events into skill_trend_snapshots for fast reads.
    """
    expected = os.getenv("AUTOMATION_API_KEY", "")
    if not expected or x_atlas_key != expected:
        raise HTTPException(status_code=403, detail="Atlas key required")

    aggregator = SkillTrendsAggregator()
    count = aggregator.generate_weekly_snapshot()
    return {
        "status": "success",
        "snapshots_created": count,
        "message": f"Generated {count} weekly skill trend snapshots",
    }
