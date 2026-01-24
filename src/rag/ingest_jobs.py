import json
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from src.rag.job_embedder import JobEmbedder

load_dotenv()

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
API_KEY = os.getenv("PINECONE_API_KEY")
REGION = os.getenv("PINECONE_ENVIRONMENT")

def main():
    pc = Pinecone(api_key=API_KEY)

    # Create index if missing
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=REGION)
        )

    index = pc.Index(INDEX_NAME)
    embedder = JobEmbedder()

    with open("src/data/sample_jobs.json") as f:
        jobs = json.load(f)

    vectors = []
    for job in jobs:
        vectors.append({
            "id": job["id"],
            "values": embedder.embed(job["description"]),
            "metadata": {
                "title": job["title"],
                "company": job["company"],
                "description": job["description"]
            }
        })

    index.upsert(vectors)
    print(f"✅ Ingested {len(vectors)} jobs into Pinecone")

if __name__ == "__main__":
    main()