from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


class SkillGapAgent:
    """
    Uses an LLM to identify missing skills between
    a resume and a job description.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2
        )

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a senior technical recruiter and curriculum architect."
            ),
            (
                "human",
                """
Compare the following resume and job description.

Resume:
{resume}

Job Description:
{job}

Identify ONLY the skills required by the job that are NOT clearly present in the resume.

Return JSON ONLY in this format:
{{
  "missing_skills": ["skill1", "skill2"]
}}
"""
            )
        ])

        self.parser = JsonOutputParser()

    def find_missing_skills(self, resume: str, job: str) -> list[str]:
        chain = self.prompt | self.llm | self.parser
        result = chain.invoke({"resume": resume, "job": job})
        return result.get("missing_skills", [])