import pytest
from unittest.mock import MagicMock

from src.rag.rag_engine import RAGEngine
from src.utils.errors import RetrievalError


class TestRAGEngine:
    def test_analyze_returns_context_string(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            {"chunk": "Kubernetes experience is valued."},
            {"chunk": "Docker skills are essential."},
        ]

        engine = RAGEngine(retriever=mock_retriever)
        result = engine.analyze("Backend Engineer role")

        assert "Kubernetes" in result
        assert "Docker" in result

    def test_analyze_empty_results(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []

        engine = RAGEngine(retriever=mock_retriever)
        result = engine.analyze("Some query")

        assert "No external job market context found" in result

    def test_analyze_retriever_failure_raises_retrieval_error(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.side_effect = RuntimeError("connection failed")

        engine = RAGEngine(retriever=mock_retriever)
        with pytest.raises(RetrievalError):
            engine.analyze("Some query")
