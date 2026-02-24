import logging
import numpy as np

from src.utils.errors import EmbeddingError, ValidationError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Converts text into vector embeddings using sentence transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        logger.info("Loading embedding model: %s", model_name)
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name)
        except Exception as e:
            raise EmbeddingError(f"Failed to load embedding model '{model_name}': {e}") from e

    def embed(self, text: str) -> np.ndarray:
        """Convert text to a normalized embedding vector."""
        if not text or not text.strip():
            raise ValidationError("Text for embedding cannot be empty.")

        try:
            return self.model.encode(text, normalize_embeddings=True)
        except Exception as e:
            raise EmbeddingError(f"Embedding failed: {e}") from e
