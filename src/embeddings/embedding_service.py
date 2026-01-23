from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Responsible for converting text into vector embeddings.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str):
        if not text or not text.strip():
            raise ValueError("Text for embedding cannot be empty.")

        return self.model.encode(
            text,
            normalize_embeddings=True
        )