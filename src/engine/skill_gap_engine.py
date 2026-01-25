from src.llm.gap_agent import SkillGapAgent


class SkillGapEngine:
    def __init__(self):
        self.gap_agent = SkillGapAgent()

    def analyze(self, resume_text: str, job_text: str) -> dict:
        """
        Analyze resume vs job and return gap analysis
        """

        result = self.gap_agent.run(
            resume_text=resume_text,
            job_text=job_text
        )

        # Normalize output so pipeline NEVER breaks
        return {
            "match_score": result.get("match_score", 50),
            "priority": result.get("priority", "Medium"),
            "missing_skills": result.get("missing_skills", [])
        }