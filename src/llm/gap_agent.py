import json
import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from src.utils.errors import LLMError

logger = logging.getLogger(__name__)


class SkillGapAgent:
    """Uses an LLM to compare a resume against a job description and identify missing skills."""

    def __init__(self) -> None:
        self.llm = ChatAnthropic(temperature=0, model="claude-sonnet-4-20250514")
        self.prompt = ChatPromptTemplate.from_template(
            """
You are a senior technical recruiter.

Compare the RESUME and JOB DESCRIPTION.

Return JSON ONLY in this exact format:

{{
  "match_score": number,
  "priority": "Low" | "Medium" | "High",
  "missing_skills": [list of strings]
}}

RESUME:
{resume}

JOB DESCRIPTION:
{job}
"""
        )

    def run(self, resume_text: str, job_text: str) -> dict:
        """Analyze resume vs job and return match score, priority, and missing skills."""
        logger.info("Running LLM skill gap analysis")
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({"resume": resume_text, "job": job_text})
        except Exception as e:
            raise LLMError(f"LLM API call failed: {e}") from e

        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            result = json.loads(content)
            logger.info("LLM returned match_score=%s, %d missing skills",
                        result.get("match_score"), len(result.get("missing_skills", [])))
            return result
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Failed to parse LLM response, returning defaults: %s", e)
            return {
                "match_score": 50,
                "priority": "Medium",
                "missing_skills": []
            }
