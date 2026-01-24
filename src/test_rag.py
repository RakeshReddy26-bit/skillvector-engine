# src/test_rag.py

from src.rag.rag_engine import RAGEngine

if __name__ == "__main__":
    resume = """
I am a backend developer with strong Python experience.
I have worked with Flask and PostgreSQL.
"""

    rag = RAGEngine(top_k=3)

    result = rag.analyze(
        resume_text=resume,
        role_query="Backend Engineer Python"
    )

    print(result)