"""
RAG Job Retrieval Engine.
Loads job data -> scores with Claude -> returns matched jobs.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)


def retrieve_matching_jobs(
    resume_text: str,
    target_role: str,
    top_k: int = 10,
) -> list[dict]:
    """
    Load job postings from static data for Claude scoring.
    Returns raw job list with metadata.
    """
    try:
        from src.jobs.job_data import JOBS

        jobs = []
        for job in JOBS[:top_k]:
            jobs.append({
                "id": job["id"],
                "title": job["title"],
                "company": job["company"],
                "location": job.get("location", ""),
                "salary": job.get("salary", ""),
                "apply_url": job.get("apply_url", ""),
                "posted_days_ago": job.get("posted_days_ago", 0),
                "required_skills": job.get("required_skills", []),
                "skills": job.get("required_skills", []),
                "seniority": job.get("seniority", ""),
                "category": job.get("category", ""),
                "description_preview": job["description"][:300],
                "text": job["description"],
                "pinecone_score": 0.5,
            })

        logger.info("Loaded %d jobs for role: %s", len(jobs), target_role)
        return jobs

    except Exception as e:
        logger.error("Job retrieval failed: %s", e)
        return []


def score_jobs_with_claude(
    resume_text: str,
    target_role: str,
    jobs: list[dict],
    missing_skills: list,
) -> list[dict]:
    """
    Use Claude to score each job against the resume.
    Returns jobs with match_score (0-100), match_label, why_match, why_gap.
    Falls back to default scores if Claude fails.
    """
    if not jobs:
        return []

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("No ANTHROPIC_API_KEY — using fallback scores")
        return _fallback_scores(jobs)

    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    llm_model = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")

    # Build context for Claude
    missing_text = "\n".join(
        f"- {s.get('skill', s) if isinstance(s, dict) else s}"
        for s in (missing_skills or [])[:5]
    )

    jobs_text = "\n\n".join(
        f"JOB_{i + 1} (id: {job['id']}):\n"
        f"Title: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}\n"
        f"Required Skills: {', '.join(job.get('required_skills', []))}\n"
        f"Description: {job.get('description_preview', job.get('text', ''))[:200]}"
        for i, job in enumerate(jobs[:8])
    )

    prompt = f"""You are a precise talent matching engine. Analyze this candidate against job postings.

CANDIDATE RESUME SUMMARY:
{resume_text[:1500]}

CANDIDATE TARGET ROLE: {target_role}

CANDIDATE'S IDENTIFIED SKILL GAPS:
{missing_text}

JOB POSTINGS TO EVALUATE:
{jobs_text}

For each job, return a JSON array with EXACTLY this structure:
[
  {{
    "id": "job_001",
    "match_score": 74,
    "match_label": "Strong Match",
    "why_match": "One sentence: what makes this candidate strong for this role",
    "why_gap": "One sentence: the single most important thing they're missing",
    "best_skill_to_close_gap": "The one skill that would most improve this match"
  }}
]

Scoring rules:
- 85-100: Exceptional match (candidate meets 90%+ of requirements)
- 70-84: Strong match (meets core requirements, minor gaps)
- 50-69: Moderate match (meets 60% of requirements, clear gaps)
- 30-49: Stretch role (significant gaps but direction is right)
- Below 30: Not a good match right now

Be accurate. Do not inflate scores. A 74% means 74%.
Return ONLY the JSON array. No markdown. No explanation."""

    try:
        response = client.messages.create(
            model=llm_model,
            max_tokens=2000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        scores = json.loads(raw)

        # Merge Claude scores with job metadata
        score_map = {s["id"]: s for s in scores}
        scored_jobs = []

        for job in jobs[:8]:
            job_id = job["id"]
            if job_id in score_map:
                merged = {**job, **score_map[job_id]}
                scored_jobs.append(merged)

        # Sort by Claude match score (most accurate)
        scored_jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return scored_jobs[:5]

    except Exception as e:
        logger.error("Claude job scoring failed: %s", e)
        return _fallback_scores(jobs)


def _fallback_scores(jobs: list[dict]) -> list[dict]:
    """Use default scores as fallback when Claude is unavailable."""
    for job in jobs:
        job["match_score"] = 50
        job["match_label"] = "Estimated"
        job["why_match"] = "Skills alignment detected"
        job["why_gap"] = "Detailed analysis unavailable"
        job["best_skill_to_close_gap"] = ""
    return jobs[:5]
