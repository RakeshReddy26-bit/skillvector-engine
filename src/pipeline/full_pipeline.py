import logging
import os
import time
import uuid

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
        self._job_retriever = self._try_job_retriever()

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

    @staticmethod
    def _try_job_retriever():
        """Return a JobRetriever if Pinecone is configured, else None."""
        try:
            from src.rag.retrieve_jobs import JobRetriever
            retriever = JobRetriever(top_k=5)
            logger.info("Pinecone connected — related jobs enabled")
            return retriever
        except Exception as e:
            logger.debug("Pinecone unavailable, related jobs disabled: %s", e)
        return None

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

        # 7. Related jobs (optional — requires Pinecone)
        related_jobs = []
        if self._job_retriever:
            try:
                related_jobs = self._job_retriever.retrieve(target_job)
            except Exception as e:
                logger.warning("Related jobs retrieval failed: %s", e)

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
