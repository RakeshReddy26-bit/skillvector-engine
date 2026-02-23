import os
import logging
from typing import List, Dict

from dotenv import load_dotenv
from pinecone import Pinecone

from src.embeddings.embedding_service import EmbeddingService
from src.utils.errors import RetrievalError, ConfigurationError

load_dotenv()

logger = logging.getLogger(__name__)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "skillvector-jobs")


class JobRetriever:
    """Retrieves semantically similar jobs from Pinecone."""

    def __init__(self, top_k: int = 5) -> None:
        if not PINECONE_API_KEY:
            raise ConfigurationError("PINECONE_API_KEY is not set.")

        self.top_k = top_k
        self.embedding_service = EmbeddingService()

        try:
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            self.index = self.pc.Index(INDEX_NAME)
        except Exception as e:
            raise RetrievalError(f"Failed to connect to Pinecone: {e}") from e

    def retrieve(self, query: str) -> List[Dict]:
        """Query Pinecone for semantically similar jobs."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        try:
            query_vector = self.embedding_service.embed(query).tolist()
            response = self.index.query(
                vector=query_vector,
                top_k=self.top_k,
                include_metadata=True
            )
        except Exception as e:
            raise RetrievalError(f"Pinecone query failed: {e}") from e

        results = []
        for match in response.matches:
            metadata = match.metadata or {}
            results.append({
                "score": round(match.score, 4),
                "job_title": metadata.get("title", "Unknown"),
                "company": metadata.get("company", "Unknown"),
                "skills": metadata.get("skills", []),
                "chunk": metadata.get("text", "")
            })

        logger.info("Retrieved %d jobs from Pinecone (top_k=%d)", len(results), self.top_k)
        return results
