# src/rag/retrieve_jobs.py

import os
from typing import List, Dict
from dotenv import load_dotenv
from pinecone import Pinecone
from src.embeddings.embedding_service import EmbeddingService

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "skillvector-jobs")


class JobRetriever:
    """
    Reads from Pinecone.
    Given a semantic query, returns the most relevant job chunks.
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.embedding_service = EmbeddingService()

        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(INDEX_NAME)

    def retrieve(self, query: str) -> List[Dict]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        # Convert ndarray → list for Pinecone
        query_vector = self.embedding_service.embed(query).tolist()

        response = self.index.query(
            vector=query_vector,
            top_k=self.top_k,
            include_metadata=True
        )

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

        return results