"""
Automation endpoints for Atlas agent network.
Called only by Atlas — protected by API key header.
DO NOT expose these in the public API docs.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/automation", tags=["automation"])

def verify_atlas(x_atlas_key: str = Header(None)):
    expected = os.getenv("AUTOMATION_API_KEY", "")
    if not expected or x_atlas_key != expected:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return True


# ── MODELS ──────────────────────────────────────────────

class JobIngestRequest(BaseModel):
    jobs: list[dict]
    source: str        # "nexus_agent", "remotive", "arbeitnow"
    ingested_by: str   # agent name for audit log

class TrendUpdateRequest(BaseModel):
    trending_skills: list[str]
    market_data: Optional[dict] = {}
    source: str        # "scout_agent"


# ── ENDPOINTS ───────────────────────────────────────────

@router.post("/ingest-jobs")
async def ingest_jobs(
    request: JobIngestRequest,
    auth=Depends(verify_atlas)
):
    """
    Nexus agent sends validated job listings here.
    Sentinel must approve them before Nexus calls this.
    Jobs are embedded and stored in Pinecone.
    """
    try:
        from src.jobs.rag_retriever import embed_and_upsert_jobs
        count = await embed_and_upsert_jobs(request.jobs)
        logger.info(f"[ATLAS] {request.ingested_by} ingested {count} jobs from {request.source}")
        return {
            "status": "success",
            "jobs_indexed": count,
            "source": request.source,
            "message": f"{count} new jobs added to SkillVector"
        }
    except Exception as e:
        logger.error(f"[ATLAS] Job ingestion failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/trend-update")
async def update_trends(
    request: TrendUpdateRequest,
    auth=Depends(verify_atlas)
):
    """
    Scout agent sends trending skills after NewsAPI research.
    Updates skill frequency weights used in gap scoring.
    """
    try:
        from src.analytics.daily_stats import update_trending_skills
        await update_trending_skills(request.trending_skills)
        logger.info(f"[ATLAS] Scout updated {len(request.trending_skills)} skill trends")
        return {
            "status": "success",
            "skills_updated": len(request.trending_skills),
            "trending": request.trending_skills[:5]
        }
    except Exception as e:
        logger.error(f"[ATLAS] Trend update failed: {e}")
        raise HTTPException(500, str(e))


@router.get("/daily-insight")
async def get_daily_insight(auth=Depends(verify_atlas)):
    """
    Scribe agent calls this at 8AM to get today's data.
    Returns real stats + Claude-generated post hook.
    Scribe uses this to write LinkedIn + Twitter posts.
    """
    from src.analytics.daily_stats import get_todays_stats
    from anthropic import Anthropic

    stats = await get_todays_stats()
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    hook_prompt = f"""You are the voice of SkillVector — an AI career intelligence platform.

Real data from today:
- Resumes analyzed: {stats['total_analyses']}
- Most common skill gap: {stats['top_skill_gap']}
- Average match score: {stats['avg_match_score']}%  
- Trending roles: {', '.join(stats['trending_roles'][:3])}
- Top 5 skill gaps: {stats['skill_gap_distribution']}

Write TWO things:

1. LINKEDIN_HOOK: First 2 sentences of a LinkedIn post.
   - Lead with the surprising data
   - Sound like a founder, not a marketer
   - Never use: excited, thrilled, leverage, journey, game-changer
   - Make ML engineers stop scrolling

2. TWEET: One tweet under 260 chars.
   - Lead with the most shocking number
   - End with the app URL placeholder: [URL]

Return ONLY this JSON:
{{"linkedin_hook": "...", "tweet": "..."}}"""

    llm_model = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
    try:
        response = client.messages.create(
            model=llm_model,
            max_tokens=300,
            temperature=0.7,
            messages=[{"role": "user", "content": hook_prompt}]
        )
        import json
        raw = response.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
        hooks = json.loads(raw)
    except Exception:
        hooks = {
            "linkedin_hook": f"We analyzed {stats['total_analyses']} resumes today. The most common missing skill? {stats['top_skill_gap']}.",
            "tweet": f"{stats['total_analyses']} resumes analyzed. #{stats['top_skill_gap']} is the #1 skill gap. [URL]"
        }

    return {
        "status": "success",
        "linkedin_hook": hooks["linkedin_hook"],
        "tweet": hooks["tweet"],
        "stats": stats,
        "app_url": os.getenv("SKILLEVECTOR_URL", "https://skill-vector.com")
    }


@router.get("/health-atlas")
async def atlas_health(auth=Depends(verify_atlas)):
    """Atlas calls this first to confirm SkillVector is alive."""
    return {
        "status": "ok",
        "message": "SkillVector ready for Atlas pipeline",
        "endpoints": ["/automation/ingest-jobs", "/automation/trend-update", "/automation/daily-insight"]
    }
