"""
RAG Job Retrieval Engine.
Embeds resume -> queries Pinecone -> scores with Claude -> returns matched jobs.
"""

import json
import logging
import os

from anthropic import Anthropic
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Singleton model (loaded once, reused)
_model = None


def _get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def retrieve_matching_jobs(
    resume_text: str,
    target_role: str,
    top_k: int = 10,
) -> list[dict]:
    """
    Embed resume + target role, query Pinecone for semantically similar jobs.
    Returns raw matches with metadata.
    """
    try:
        model = _get_embedding_model()

        # Embed resume + target role together for better matching
        query_text = f"Candidate targeting: {target_role}\n\nResume:\n{resume_text[:2000]}"
        query_embedding = model.encode(query_text).tolist()

        index_name = os.getenv("PINECONE_INDEX_NAME", "skillvector-jobs")
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(index_name)

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
        )

        jobs = []
        for match in results.matches:
            job = dict(match.metadata) if match.metadata else {}
            job["pinecone_score"] = round(match.score, 3)
            job["id"] = match.id
            # Ensure required_skills is a list (Pinecone may return it differently)
            if "required_skills" not in job:
                job["required_skills"] = job.get("skills", [])
            jobs.append(job)

        logger.info("Retrieved %d jobs from Pinecone for role: %s", len(jobs), target_role)
        return jobs

    except Exception as e:
        logger.error("Pinecone retrieval failed: %s", e)
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
    Falls back to Pinecone cosine scores if Claude fails.
    """
    if not jobs:
        return []

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("No ANTHROPIC_API_KEY — using Pinecone scores as fallback")
        return _fallback_scores(jobs)

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

        # Merge Claude scores with Pinecone metadata
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
    """Use Pinecone cosine similarity as fallback when Claude is unavailable."""
    for job in jobs:
        job["match_score"] = round(job.get("pinecone_score", 0.5) * 100)
        job["match_label"] = "Estimated"
        job["why_match"] = "Semantic similarity match"
        job["why_gap"] = "Detailed analysis unavailable"
        job["best_skill_to_close_gap"] = ""
    jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return jobs[:5]
