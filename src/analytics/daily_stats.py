"""
Tracks daily analysis stats for Scribe agent content creation.
In-memory store — resets daily. No database needed.
"""

import asyncio
from datetime import date
from collections import Counter

_store = {
    "date": date.today().isoformat(),
    "match_scores": [],
    "skill_gaps": [],
    "roles": [],
    "trending_skills": []
}
_lock = asyncio.Lock()


async def record_analysis(match_score: int, missing_skills: list, target_role: str):
    """Called by full_pipeline.py after every /analyze call."""
    async with _lock:
        today = date.today().isoformat()
        if _store["date"] != today:
            _store.update({
                "date": today,
                "match_scores": [],
                "skill_gaps": [],
                "roles": [],
                "trending_skills": []
            })
        _store["match_scores"].append(match_score)
        _store["roles"].append(target_role)
        for s in (missing_skills or []):
            name = s.get("skill", s) if isinstance(s, dict) else s
            _store["skill_gaps"].append(name)


async def update_trending_skills(skills: list[str]):
    """Called by /automation/trend-update when Scout sends data."""
    async with _lock:
        _store["trending_skills"] = skills


async def get_todays_stats() -> dict:
    """Called by /automation/daily-insight for Scribe agent."""
    async with _lock:
        if not _store["match_scores"]:
            return {
                "total_analyses": 0,
                "top_skill_gap": "MLOps",
                "avg_match_score": 72.0,
                "trending_roles": ["Senior ML Engineer"],
                "skill_gap_distribution": {"MLOps": 5}
            }
        skill_c = Counter(_store["skill_gaps"])
        role_c = Counter(_store["roles"])
        return {
            "total_analyses": len(_store["match_scores"]),
            "top_skill_gap": skill_c.most_common(1)[0][0],
            "avg_match_score": round(sum(_store["match_scores"]) / len(_store["match_scores"]), 1),
            "trending_roles": [r for r, _ in role_c.most_common(3)],
            "skill_gap_distribution": dict(skill_c.most_common(5))
        }
