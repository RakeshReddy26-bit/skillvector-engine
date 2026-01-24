# src/rag/rag_engine.py

from typing import Dict
from langchain_openai import ChatOpenAI
from src.rag.retrieve_jobs import JobRetriever
from src.llm.rag_prompt import RAG_PROMPT


class RAGEngine:
    """
    Retrieval-Augmented Reasoning Engine.
    Forces the LLM to reason ONLY over retrieved job data.
    """

    def __init__(self, top_k: int = 3):
        self.retriever = JobRetriever(top_k=top_k)
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

    def analyze(self, resume_text: str, role_query: str) -> Dict:
        if not resume_text.strip():
            raise ValueError("Resume cannot be empty.")
        if not role_query.strip():
            raise ValueError("Role query cannot be empty.")

        retrieved = self.retriever.retrieve(role_query)

        job_context = "\n\n".join(
            f"- {r['job_title']} @ {r['company']}:\n{r['chunk']}"
            for r in retrieved if r["chunk"]
        )

        chain = RAG_PROMPT | self.llm

        response = chain.invoke({
            "resume": resume_text,
            "job_context": job_context
        })

        return response.content