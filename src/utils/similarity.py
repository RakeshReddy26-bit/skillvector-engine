import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def cosine_similarity_score(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors, returning a 0-100 score."""
    score = cosine_similarity([vector_a], [vector_b])[0][0]
    result = round(score * 100, 2)
    logger.debug("Cosine similarity score: %.2f", result)
    return result
