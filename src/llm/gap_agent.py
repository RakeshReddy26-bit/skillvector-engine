from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json


class SkillGapAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini"
        )

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
        chain = self.prompt | self.llm
        response = chain.invoke({
            "resume": resume_text,
            "job": job_text
        })

        try:
            return json.loads(response.content)
        except Exception:
            return {
                "match_score": 50,
                "priority": "Medium",
                "missing_skills": []
            }