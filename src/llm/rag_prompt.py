# src/llm/rag_prompt.py

from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a strict career analysis engine.

Rules:
- You MUST use only the provided job context.
- Do NOT use outside knowledge.
- If a skill is not mentioned in the context, do NOT invent it.
- Output must be valid JSON only.
"""
    ),
    (
        "human",
        """
USER RESUME:
{resume}

JOB CONTEXT (from live job market):
{job_context}

Return JSON exactly in this format:
{{
  "missing_skills": ["skill1", "skill2"],
  "learning_priority": "High|Medium|Low"
}}
"""
    )
])