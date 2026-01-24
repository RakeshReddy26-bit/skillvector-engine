# src/test_retrieval.py

from src.rag.retrieve_jobs import JobRetriever

if __name__ == "__main__":
    retriever = JobRetriever(top_k=3)

    results = retriever.retrieve("Backend Engineer Python")

    for r in results:
        print("\n---")
        print(f"Score: {r['score']}")
        print(f"Title: {r['job_title']} @ {r['company']}")
        print(f"Skills: {r['skills']}")

        chunk = r.get("chunk") or ""
        print(f"Chunk: {chunk[:200]}...")