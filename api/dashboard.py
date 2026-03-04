from dotenv import load_dotenv
load_dotenv()
import os
import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from api.auth import get_current_user
from src.db.models import AnalysisRepository, UserRepository

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)


@router.get("/history")
async def get_analysis_history(request: Request):
    """Get all past analyses for the logged in user."""
    try:
        user = get_current_user(request)
        if not user:
            return JSONResponse(status_code=401, content={"error": "Login required"})

        repo = AnalysisRepository()
        analyses = repo.get_user_analyses(user["id"], limit=20)

        return JSONResponse(content={
            "analyses": analyses,
            "total": len(analyses),
            "user": {
                "email": user["email"],
                "plan_tier": user.get("plan_tier", "free"),
                "analyses_used": user.get("analyses_used", 0),
                "analyses_limit": user.get("analyses_limit", 3)
            }
        })
    except Exception as e:
        logger.error(f"Dashboard history error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/stats")
async def get_user_stats(request: Request):
    """Get stats for the logged in user."""
    try:
        user = get_current_user(request)
        if not user:
            return JSONResponse(status_code=401, content={"error": "Login required"})

        repo = AnalysisRepository()
        analyses = repo.get_user_analyses(user["id"], limit=100)

        if not analyses:
            return JSONResponse(content={
                "total_analyses": 0,
                "avg_match_score": 0,
                "best_match_score": 0,
                "most_common_gap": None,
                "improvement": 0
            })

        scores = [a.get("match_score", 0) for a in analyses if a.get("match_score")]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0
        best_score = round(max(scores), 1) if scores else 0

        # Calculate improvement (latest vs first)
        improvement = 0
        if len(scores) >= 2:
            improvement = round(scores[0] - scores[-1], 1)

        # Most common skill gap
        all_gaps = []
        for a in analyses:
            gaps = a.get("missing_skills", [])
            for g in gaps:
                if isinstance(g, dict):
                    all_gaps.append(g.get("skill", ""))
                else:
                    all_gaps.append(str(g))

        most_common_gap = None
        if all_gaps:
            from collections import Counter
            most_common_gap = Counter(all_gaps).most_common(1)[0][0]

        return JSONResponse(content={
            "total_analyses": len(analyses),
            "avg_match_score": avg_score,
            "best_match_score": best_score,
            "most_common_gap": most_common_gap,
            "improvement": improvement
        })
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.delete("/history/{analysis_id}")
async def delete_analysis(analysis_id: str, request: Request):
    """Delete a specific analysis."""
    try:
        user = get_current_user(request)
        if not user:
            return JSONResponse(status_code=401, content={"error": "Login required"})

        repo = AnalysisRepository()
        repo.delete_analysis(user["id"], analysis_id)
        return JSONResponse(content={"status": "deleted"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
