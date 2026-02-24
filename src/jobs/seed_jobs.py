"""
Seed Pinecone with realistic ML/tech job postings.
Run once: python -m src.jobs.seed_jobs
"""

import os

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from src.jobs.job_data import JOBS

load_dotenv()


def seed_pinecone():
    """Embed all jobs and upsert into Pinecone index."""
    index_name = os.getenv("PINECONE_INDEX_NAME", "skillvector-jobs")

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Connecting to Pinecone...")
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)

    vectors = []
    for job in JOBS:
        # Embed the full job description + skills for rich semantic matching
        text_to_embed = (
            f"{job['title']} at {job['company']}\n"
            f"{job['description']}\n"
            f"Required skills: {', '.join(job['required_skills'])}"
        )

        embedding = model.encode(text_to_embed).tolist()

        vectors.append({
            "id": job["id"],
            "values": embedding,
            "metadata": {
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "salary": job["salary"],
                "apply_url": job["apply_url"],
                "posted_days_ago": job["posted_days_ago"],
                "required_skills": job["required_skills"],
                "seniority": job["seniority"],
                "category": job["category"],
                "description_preview": job["description"][:300],
                # Keep backward-compatible fields
                "text": job["description"],
                "skills": job["required_skills"],
            },
        })
        print(f"  Embedded: {job['title']} @ {job['company']}")

    # Upsert in batches of 10
    batch_size = 10
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        index.upsert(vectors=batch)
        print(f"  Upserted batch {i // batch_size + 1}")

    print(f"\nSeeded {len(JOBS)} jobs into Pinecone index: {index_name}")


if __name__ == "__main__":
    seed_pinecone()
