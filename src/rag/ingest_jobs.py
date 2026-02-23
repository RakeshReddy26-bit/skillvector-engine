import json
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

from src.embeddings.embedding_service import EmbeddingService
from src.utils.errors import ConfigurationError

load_dotenv()
logger = logging.getLogger(__name__)

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "skillvector-jobs")
API_KEY = os.getenv("PINECONE_API_KEY")
REGION = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")


def main():
    if not API_KEY:
        raise ConfigurationError("PINECONE_API_KEY is not set.")

    pc = Pinecone(api_key=API_KEY)

    # Create index if missing
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=REGION),
        )

    index = pc.Index(INDEX_NAME)
    embedder = EmbeddingService()

    data_path = Path(__file__).parent.parent / "data" / "sample_jobs.json"
    with open(data_path) as f:
        jobs = json.load(f)

    vectors = []
    for job in jobs:
        vector = embedder.embed(job["description"]).tolist()
        vectors.append({
            "id": job["id"],
            "values": vector,
            "metadata": {
                "title": job["title"],
                "company": job["company"],
                "text": job["description"],
            },
        })

    index.upsert(vectors)
    logger.info("Ingested %d jobs into Pinecone index '%s'", len(vectors), INDEX_NAME)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
