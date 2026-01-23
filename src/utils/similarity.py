import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def cosine_similarity_score(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """
    Computes cosine similarity between two vectors
    and returns a percentage score (0–100).
    """
    score = cosine_similarity([vector_a], [vector_b])[0][0]
    return round(score * 100, 2)