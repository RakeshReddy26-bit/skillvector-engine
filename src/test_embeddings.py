from src.embeddings.embedding_service import EmbeddingService

service = EmbeddingService()

vector = service.embed("I am a Python developer")

print(type(vector))
print(len(vector))
