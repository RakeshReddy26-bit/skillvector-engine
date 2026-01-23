from src.embeddings.embedding_service import EmbeddingService
from src.utils.similarity import cosine_similarity_score

embedder = EmbeddingService()

resume_vec = embedder.embed("I am a Python backend developer")
job_vec = embedder.embed("Looking for a backend engineer with Python experience")

score = cosine_similarity_score(resume_vec, job_vec)

print("Match Score:", score)