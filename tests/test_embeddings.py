import pytest
from unittest.mock import patch, MagicMock
import numpy as np

from src.embeddings.embedding_service import EmbeddingService
from src.utils.errors import ValidationError, EmbeddingError


class TestEmbeddingService:
    @patch("sentence_transformers.SentenceTransformer")
    def test_embed_returns_numpy_array(self, mock_st):
        mock_model = MagicMock()
        mock_model.encode.return_value = np.zeros(384)
        mock_st.return_value = mock_model

        service = EmbeddingService()
        result = service.embed("Python developer")

        assert isinstance(result, np.ndarray)
        assert len(result) == 384

    @patch("sentence_transformers.SentenceTransformer")
    def test_embed_calls_model_with_normalization(self, mock_st):
        mock_model = MagicMock()
        mock_model.encode.return_value = np.zeros(384)
        mock_st.return_value = mock_model

        service = EmbeddingService()
        service.embed("test text")

        mock_model.encode.assert_called_once_with("test text", normalize_embeddings=True)

    @patch("sentence_transformers.SentenceTransformer")
    def test_embed_empty_text_raises_validation_error(self, mock_st):
        mock_st.return_value = MagicMock()
        service = EmbeddingService()

        with pytest.raises(ValidationError, match="empty"):
            service.embed("")

    @patch("sentence_transformers.SentenceTransformer")
    def test_embed_whitespace_text_raises_validation_error(self, mock_st):
        mock_st.return_value = MagicMock()
        service = EmbeddingService()

        with pytest.raises(ValidationError, match="empty"):
            service.embed("   ")

    @patch("sentence_transformers.SentenceTransformer")
    def test_model_failure_raises_embedding_error(self, mock_st):
        mock_model = MagicMock()
        mock_model.encode.side_effect = RuntimeError("model crashed")
        mock_st.return_value = mock_model

        service = EmbeddingService()
        with pytest.raises(EmbeddingError):
            service.embed("valid text")

    def test_init_failure_raises_embedding_error(self):
        with patch("sentence_transformers.SentenceTransformer",
                   side_effect=RuntimeError("cannot load model")):
            with pytest.raises(EmbeddingError):
                EmbeddingService(model_name="nonexistent-model")
