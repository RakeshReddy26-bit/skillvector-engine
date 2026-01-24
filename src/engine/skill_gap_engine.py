from src.embeddings.embedding_service import EmbeddingService
from src.utils.similarity import cosine_similarity_score
from src.llm.gap_agent import SkillGapAgent


class SkillGapEngine:
    """
    Core engine responsible for analyzing the gap between
    a user's resume and a target job description.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.gap_agent = SkillGapAgent()

    def analyze(self, user_resume_text: str, target_job_description: str) -> dict:
        if not user_resume_text or not user_resume_text.strip():
            raise ValueError("Resume text cannot be empty.")

        if not target_job_description or not target_job_description.strip():
            raise ValueError("Job description cannot be empty.")

        # Embeddings
        resume_vector = self.embedding_service.embed(user_resume_text)
        job_vector = self.embedding_service.embed(target_job_description)

        # Match score
        match_score = cosine_similarity_score(resume_vector, job_vector)

        # LLM reasoning
        missing_skills = self.gap_agent.find_missing_skills(
            resume=user_resume_text,
            job=target_job_description
        )

        # Priority logic
        if match_score < 50:
            priority = "High"
        elif match_score < 75:
            priority = "Medium"
        else:
            priority = "Low"

        return {
            "match_score": match_score,
            "missing_skills": missing_skills,
            "learning_priority": priority
        }