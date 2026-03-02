import logging
import os
import time
import uuid

from neo4j import GraphDatabase

from src.engine.skill_gap_engine import SkillGapEngine
from src.graph.skill_planner import SkillPlanner
from src.evidence.evidence_engine import EvidenceEngine
from src.evidence.interview_generator import InterviewGenerator
from src.evidence.rubric import RubricEngine
from src.utils.errors import SkillVectorError

logger = logging.getLogger(__name__)


class SkillVectorPipeline:
    """End-to-end pipeline: skill gap analysis -> learning path -> evidence projects."""

    def __init__(self) -> None:
        self.skill_engine = SkillGapEngine()
        neo4j_client = self._try_neo4j_client()
        self.skill_planner = SkillPlanner(neo4j_client=neo4j_client)
        self.evidence_engine = EvidenceEngine()
        self.interview_generator = InterviewGenerator()
        self.rubric_engine = RubricEngine()

    @staticmethod
    def _try_neo4j_client():
        """Return a Neo4jClient if Neo4j is reachable, else None."""
        try:
            from src.graph.neo4j_client import Neo4jClient
            client = Neo4jClient()
            if client.verify_connectivity():
                logger.info("Neo4j connected — using graph database for skill ordering")
                return client
            client.close()
        except Exception as e:
            logger.debug("Neo4j unavailable: %s", e)
        return None

    def _try_job_retriever(
        self,
        resume_text: str,
        target_role: str,
        missing_skills: list,
    ) -> list:
        """RAG job retrieval using Pinecone + Claude scoring.

        Gracefully degrades if Pinecone is unavailable.
        """
        try:
            from src.jobs.rag_retriever import retrieve_matching_jobs, score_jobs_with_claude

            # Step 1: Get semantic matches from Pinecone
            raw_jobs = retrieve_matching_jobs(
                resume_text=resume_text,
                target_role=target_role,
                top_k=10,
            )

            if not raw_jobs:
                logger.warning("No jobs retrieved from Pinecone")
                return []

            # Step 2: Score with Claude for accuracy
            scored_jobs = score_jobs_with_claude(
                resume_text=resume_text,
                target_role=target_role,
                jobs=raw_jobs,
                missing_skills=missing_skills,
            )

            # Step 3: Normalize output to keep backward-compatible keys
            result = []
            for job in scored_jobs:
                result.append({
                    # Backward-compatible keys (existing frontend expects these)
                    "score": job.get("pinecone_score", job.get("match_score", 0) / 100),
                    "job_title": job.get("title", "Unknown"),
                    "company": job.get("company", "Unknown"),
                    "skills": job.get("required_skills", job.get("skills", [])),
                    "chunk": job.get("description_preview", job.get("text", "")),
                    # New enriched fields
                    "location": job.get("location", ""),
                    "salary": job.get("salary", ""),
                    "apply_url": job.get("apply_url", ""),
                    "posted_days_ago": job.get("posted_days_ago", 0),
                    "match_score": job.get("match_score", 0),
                    "match_label": job.get("match_label", ""),
                    "why_match": job.get("why_match", ""),
                    "why_gap": job.get("why_gap", ""),
                    "best_skill_to_close_gap": job.get("best_skill_to_close_gap", ""),
                })

            logger.info("Job retrieval complete: %d jobs scored", len(result))
            return result

        except Exception as e:
            logger.error("Job retrieval pipeline failed: %s", e)
            return []

    def get_learning_path_from_neo4j(self, missing_skills: list) -> list:
        """Build a learning path directly from Neo4j using the official driver."""
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")

        if not uri or not user or not password or not missing_skills:
            return []

        query = """
        UNWIND $skills AS skill_name
        OPTIONAL MATCH (s:Skill {name: skill_name})
        OPTIONAL MATCH (pre:Skill)-[:PREREQUISITE_OF]->(s)
        RETURN skill_name AS skill, count(pre) AS prereq_count
        ORDER BY prereq_count DESC, skill ASC
        """

        driver = GraphDatabase.driver(uri, auth=(user, password))
        try:
            with driver.session() as session:
                records = session.run(query, skills=missing_skills)
                return [
                    {"skill": record["skill"], "estimated_weeks": 2, "estimated_days": 14}
                    for record in records
                ]
        finally:
            driver.close()

    def run(self, resume: str, target_job: str) -> dict:
        """Run the full analysis pipeline.

        Returns a dict with match_score, learning_priority, missing_skills,
        learning_path, evidence, interview_prep, rubrics, related_jobs,
        request_id, and latency_ms.
        """
        request_id = uuid.uuid4().hex[:12]
        start = time.monotonic()
        model = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
        logger.info("[%s] Starting SkillVector pipeline | model=%s", request_id, model)

        # 1. Skill gap analysis
        gap_result = self.skill_engine.analyze(resume, target_job)
        match_score = gap_result["match_score"]
        missing_skills = gap_result["missing_skills"]

        # 2. Priority logic (deterministic)
        if match_score < 50:
            learning_priority = "High"
        elif match_score < 75:
            learning_priority = "Medium"
        else:
            learning_priority = "Low"

        # 3. Learning path planning (graceful degradation)
        try:
            learning_path = self.skill_planner.plan(missing_skills)
        except Exception as e:
            logger.warning("Learning path planning failed, using fallback: %s", e)
            learning_path = [{"skill": s, "estimated_weeks": 2, "estimated_days": 14} for s in missing_skills]

        # 4. Evidence generation (graceful degradation)
        try:
            evidence = self.evidence_engine.generate(learning_path)
        except Exception as e:
            logger.warning("Evidence generation failed: %s", e)
            evidence = []

        # 5. Interview prep (graceful degradation)
        try:
            interview_prep = self.interview_generator.generate(missing_skills)
        except Exception as e:
            logger.warning("Interview prep generation failed: %s", e)
            interview_prep = []

        # 6. Rubrics (graceful degradation)
        try:
            rubrics = self.rubric_engine.generate(missing_skills)
        except Exception as e:
            logger.warning("Rubric generation failed: %s", e)
            rubrics = []

        # 7. Related jobs (RAG: Pinecone retrieval + Claude scoring)
        related_jobs = self._try_job_retriever(resume, target_job, missing_skills)

        result = {
            "match_score": match_score,
            "learning_priority": learning_priority,
            "missing_skills": missing_skills,
            "learning_path": learning_path,
            "evidence": evidence,
            "interview_prep": interview_prep,
            "rubrics": rubrics,
            "related_jobs": related_jobs,
            "request_id": request_id,
        }

        latency_ms = round((time.monotonic() - start) * 1000)
        result["latency_ms"] = latency_ms
        logger.info(
            "[%s] Pipeline complete | score=%.1f | priority=%s | missing=%d | model=%s | latency=%dms",
            request_id, match_score, learning_priority, len(missing_skills), model, latency_ms,
        )
        return result
