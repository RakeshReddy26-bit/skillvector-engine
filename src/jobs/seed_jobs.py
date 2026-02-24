"""
Seed Pinecone with realistic ML/tech job postings.
Run once: python -m src.jobs.seed_jobs
"""

import os

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

load_dotenv()

# 10 realistic job postings — covers ML, Data, Backend, AI roles
JOBS = [
    {
        "id": "job_001",
        "title": "Senior ML Engineer",
        "company": "Stripe",
        "location": "San Francisco, CA",
        "salary": "$220k-$280k",
        "apply_url": "https://stripe.com/jobs",
        "posted_days_ago": 2,
        "description": (
            "We are looking for a Senior ML Engineer to join Stripe's ML Platform team. "
            "You will build and maintain production ML systems that power fraud detection, "
            "risk scoring, and financial intelligence at scale. "
            "Requirements: 5+ years ML engineering experience, production MLOps experience "
            "(Kubeflow, MLflow, or similar), Python, PyTorch or TensorFlow, experience with "
            "distributed training (Ray, Spark), LLMOps experience preferred, strong system "
            "design skills, feature store experience (Feast, Tecton)."
        ),
        "required_skills": [
            "Python", "MLOps", "Kubeflow", "PyTorch", "Distributed Systems",
            "Feature Stores", "LLMOps",
        ],
        "seniority": "Senior",
        "category": "ML Engineering",
    },
    {
        "id": "job_002",
        "title": "ML Platform Engineer",
        "company": "Anthropic",
        "location": "San Francisco, CA",
        "salary": "$200k-$260k",
        "apply_url": "https://anthropic.com/careers",
        "posted_days_ago": 1,
        "description": (
            "Anthropic is looking for an ML Platform Engineer to build the infrastructure "
            "that enables our research teams to train, evaluate, and deploy large language models. "
            "Requirements: Experience building ML training infrastructure, deep knowledge of "
            "LLM evaluation frameworks (RAGAS, deepeval, custom evals), Python, distributed "
            "systems, experience with Ray or similar distributed compute, understanding of "
            "RLHF training pipelines, feature engineering at scale."
        ),
        "required_skills": [
            "Python", "LLMOps", "Evals", "Ray", "RLHF", "Distributed Systems",
        ],
        "seniority": "Senior",
        "category": "ML Platform",
    },
    {
        "id": "job_003",
        "title": "AI/ML Engineer",
        "company": "Notion",
        "location": "Remote",
        "salary": "$180k-$230k",
        "apply_url": "https://notion.so/careers",
        "posted_days_ago": 3,
        "description": (
            "Join Notion's AI team to build intelligent features that help millions of users "
            "work smarter. You'll work on RAG pipelines, semantic search, and LLM integration. "
            "Requirements: Experience with LLM APIs (OpenAI, Anthropic, etc.), RAG pipeline "
            "experience, FastAPI or similar Python web frameworks, vector database experience "
            "(Pinecone, Weaviate), understanding of embedding models."
        ),
        "required_skills": [
            "Python", "FastAPI", "LLMs", "RAG", "Pinecone", "Embeddings",
        ],
        "seniority": "Mid-Senior",
        "category": "AI Engineering",
    },
    {
        "id": "job_004",
        "title": "Data Scientist - Growth",
        "company": "Airbnb",
        "location": "San Francisco, CA (Hybrid)",
        "salary": "$170k-$220k",
        "apply_url": "https://airbnb.com/careers",
        "posted_days_ago": 5,
        "description": (
            "Airbnb's Growth team is looking for a Data Scientist to drive experiments "
            "and build predictive models that improve host and guest experiences. "
            "Requirements: Statistical modeling and A/B testing expertise, Python (pandas, "
            "sklearn, statsmodels), SQL at expert level, causal inference experience preferred, "
            "experience with recommendation systems, strong communication skills."
        ),
        "required_skills": [
            "Python", "SQL", "Statistics", "A/B Testing", "sklearn", "Causal Inference",
        ],
        "seniority": "Senior",
        "category": "Data Science",
    },
    {
        "id": "job_005",
        "title": "Senior Backend Engineer - ML Systems",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "salary": "$250k-$350k",
        "apply_url": "https://openai.com/careers",
        "posted_days_ago": 1,
        "description": (
            "Build the systems that serve OpenAI's models to millions of users. "
            "You'll work on inference optimization, API reliability, and scaling challenges. "
            "Requirements: Python and Go or Rust, distributed systems expert, experience "
            "with high-throughput API design, understanding of ML inference pipelines, "
            "Kubernetes and cloud infrastructure, observability and monitoring."
        ),
        "required_skills": [
            "Python", "Distributed Systems", "API Design", "Kubernetes",
            "Inference Optimization",
        ],
        "seniority": "Senior",
        "category": "Backend Engineering",
    },
    {
        "id": "job_006",
        "title": "ML Engineer - Recommendations",
        "company": "Spotify",
        "location": "New York, NY",
        "salary": "$185k-$240k",
        "apply_url": "https://spotify.com/careers",
        "posted_days_ago": 4,
        "description": (
            "Build the recommendation systems that create personalized music experiences "
            "for 600 million users. You'll work on collaborative filtering, content-based "
            "models, and real-time personalization. Requirements: Experience building "
            "recommendation systems, Python, PyTorch or TensorFlow, familiarity with "
            "feature stores, real-time inference experience, Spark or Flink for data processing."
        ),
        "required_skills": [
            "Python", "PyTorch", "Recommendation Systems", "Feature Stores", "Spark",
        ],
        "seniority": "Mid-Senior",
        "category": "ML Engineering",
    },
    {
        "id": "job_007",
        "title": "Applied Scientist",
        "company": "Amazon",
        "location": "Seattle, WA",
        "salary": "$175k-$250k",
        "apply_url": "https://amazon.jobs",
        "posted_days_ago": 2,
        "description": (
            "Amazon's Applied Science team works on production ML models that power "
            "search, recommendations, and supply chain optimization. Requirements: "
            "PhD or MS in ML, Statistics, or related field, deep ML modeling expertise, "
            "Python, Spark, SageMaker, publication record preferred, NLP or CV specialization a plus."
        ),
        "required_skills": [
            "Python", "Deep Learning", "SageMaker", "Spark", "Research", "NLP",
        ],
        "seniority": "Senior",
        "category": "Applied Science",
    },
    {
        "id": "job_008",
        "title": "LLM Engineer",
        "company": "Cohere",
        "location": "Remote",
        "salary": "$160k-$220k",
        "apply_url": "https://cohere.com/careers",
        "posted_days_ago": 3,
        "description": (
            "Work directly on LLM fine-tuning, RLHF pipelines, and evaluation frameworks. "
            "You'll help improve Cohere's enterprise language models. Requirements: "
            "Experience with LLM fine-tuning, RLHF or RLAIF implementation experience, "
            "Python, PyTorch, evaluation framework design, understanding of alignment techniques."
        ),
        "required_skills": [
            "Python", "PyTorch", "LLM Fine-tuning", "RLHF", "Evals", "Alignment",
        ],
        "seniority": "Mid-Senior",
        "category": "LLM Engineering",
    },
    {
        "id": "job_009",
        "title": "Data Engineer - ML Platform",
        "company": "DoorDash",
        "location": "San Francisco, CA",
        "salary": "$165k-$210k",
        "apply_url": "https://doordash.com/careers",
        "posted_days_ago": 6,
        "description": (
            "Build the data infrastructure that powers DoorDash's ML models. "
            "You'll work on feature pipelines, data quality, and real-time data systems. "
            "Requirements: Python and SQL expert, Spark, Kafka, or Flink experience, "
            "feature store experience (Feast preferred), dbt or similar transformation tools, "
            "data quality frameworks, Airflow or Prefect for orchestration."
        ),
        "required_skills": [
            "Python", "SQL", "Spark", "Kafka", "Feature Stores", "Airflow", "dbt",
        ],
        "seniority": "Senior",
        "category": "Data Engineering",
    },
    {
        "id": "job_010",
        "title": "Research Engineer - Foundation Models",
        "company": "Google DeepMind",
        "location": "London, UK / Remote",
        "salary": "$180k-$260k",
        "apply_url": "https://deepmind.com/careers",
        "posted_days_ago": 1,
        "description": (
            "Work alongside world-class researchers to implement and scale "
            "foundation model experiments. Bridge research and production. "
            "Requirements: PyTorch or JAX expertise, distributed training at scale, "
            "Python systems programming, research implementation experience, "
            "TPU or GPU cluster experience."
        ),
        "required_skills": [
            "Python", "PyTorch", "JAX", "Distributed Training", "Research Engineering",
        ],
        "seniority": "Senior",
        "category": "Research Engineering",
    },
]


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
