import logging

from src.llm.gap_agent import SkillGapAgent
from src.embeddings.embedding_service import EmbeddingService
from src.utils.similarity import cosine_similarity_score
from src.utils.errors import ValidationError, LLMError, EmbeddingError

logger = logging.getLogger(__name__)


class SkillGapEngine:
    """Orchestrates skill gap analysis using both embeddings and LLM reasoning."""

    def __init__(self) -> None:
        self.gap_agent = SkillGapAgent()
        self._embedding_service = None

    def _get_embedding_service(self) -> EmbeddingService:
        """Lazy-load the embedding model."""
        if self._embedding_service is None:
            self._embedding_service = EmbeddingService()
        return self._embedding_service

    def analyze(self, resume_text: str, job_text: str) -> dict:
        """Analyze resume vs job description and return gap analysis.

        Uses embedding cosine similarity for a deterministic match score,
        and LLM reasoning for identifying missing skills.
        """
        if not resume_text or not resume_text.strip():
            raise ValidationError("Resume text cannot be empty.")
        if not job_text or not job_text.strip():
            raise ValidationError("Job description cannot be empty.")

        # 1. Deterministic match score via embeddings
        match_score = self._compute_embedding_score(resume_text, job_text)

        # 2. LLM-based missing skill identification
        llm_result = self._run_llm_analysis(resume_text, job_text)
        missing_skills = llm_result.get("missing_skills", [])

        # If embedding score failed, fall back to LLM score
        if match_score is None:
            match_score = llm_result.get("match_score", 50)

        return {
            "match_score": match_score,
            "priority": llm_result.get("priority", "Medium"),
            "missing_skills": missing_skills,
        }

    def _compute_embedding_score(self, resume_text: str, job_text: str) -> float | None:
        """Compute cosine similarity between resume and job embeddings."""
        try:
            service = self._get_embedding_service()
            resume_vec = service.embed(resume_text)
            job_vec = service.embed(job_text)
            score = cosine_similarity_score(resume_vec, job_vec)
            logger.info("Embedding match score: %.2f", score)
            return score
        except (EmbeddingError, Exception) as e:
            logger.warning("Embedding scoring failed, will use LLM score: %s", e)
            return None

    def _run_llm_analysis(self, resume_text: str, job_text: str) -> dict:
        """Run LLM analysis with fallback on failure."""
        try:
            return self.gap_agent.run(resume_text=resume_text, job_text=job_text)
        except LLMError as e:
            logger.error("LLM analysis failed: %s", e)
            return {"match_score": 50, "priority": "Medium", "missing_skills": []}
