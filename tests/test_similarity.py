import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from src.utils.similarity import cosine_similarity_score


class TestCosineSimilarity:
    def test_identical_vectors_score_100(self):
        vec = np.array([1.0, 0.0, 0.0])
        score = cosine_similarity_score(vec, vec)
        assert score == 100.0

    def test_orthogonal_vectors_score_0(self):
        vec_a = np.array([1.0, 0.0])
        vec_b = np.array([0.0, 1.0])
        score = cosine_similarity_score(vec_a, vec_b)
        assert score == 0.0

    def test_similar_vectors_positive_score(self):
        vec_a = np.array([1.0, 0.5, 0.0])
        vec_b = np.array([0.9, 0.6, 0.1])
        score = cosine_similarity_score(vec_a, vec_b)
        assert 0 < score <= 100

    def test_returns_float(self):
        vec_a = np.array([1.0, 0.0])
        vec_b = np.array([0.5, 0.5])
        score = cosine_similarity_score(vec_a, vec_b)
        assert isinstance(score, float)

    def test_score_rounded_to_2_decimals(self):
        vec_a = np.array([1.0, 0.3333333])
        vec_b = np.array([0.5, 0.7777777])
        score = cosine_similarity_score(vec_a, vec_b)
        assert score == round(score, 2)
