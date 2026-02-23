import logging

from src.utils.errors import RetrievalError

logger = logging.getLogger(__name__)


class RAGEngine:
    """Retrieves job market context from a vector DB for richer analysis."""

    def __init__(self, retriever) -> None:
        self.retriever = retriever

    def analyze(self, job_text: str) -> str:
        """Return contextual job market insights for a job description."""
        logger.info("Retrieving job market context via RAG")
        try:
            documents = self.retriever.retrieve(job_text)
        except Exception as e:
            raise RetrievalError(f"RAG retrieval failed: {e}") from e

        if not documents:
            logger.info("No external job market context found")
            return "No external job market context found."

        context = "\n\n".join(f"- {doc['chunk']}" for doc in documents)
        logger.info("Retrieved %d relevant job context documents", len(documents))
        return context
