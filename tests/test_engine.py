import pytest
from unittest.mock import patch, MagicMock
import numpy as np

from src.engine.skill_gap_engine import SkillGapEngine
from src.utils.errors import ValidationError


class TestSkillGapEngine:
    @patch("src.engine.skill_gap_engine.SkillGapAgent")
    def test_analyze_returns_required_keys(self, mock_agent_cls):
        mock_agent = MagicMock()
        mock_agent.run.return_value = {
            "match_score": 65,
            "priority": "Medium",
            "missing_skills": ["Docker"]
        }
        mock_agent_cls.return_value = mock_agent

        engine = SkillGapEngine()
        result = engine.analyze("Python developer", "Need Docker experience")

        assert "match_score" in result
        assert "priority" in result
        assert "missing_skills" in result

    @patch("src.engine.skill_gap_engine.SkillGapAgent")
    def test_analyze_empty_resume_raises_validation_error(self, mock_agent_cls):
        engine = SkillGapEngine()
        with pytest.raises(ValidationError, match="Resume"):
            engine.analyze("", "Some job")

    @patch("src.engine.skill_gap_engine.SkillGapAgent")
    def test_analyze_empty_job_raises_validation_error(self, mock_agent_cls):
        engine = SkillGapEngine()
        with pytest.raises(ValidationError, match="Job"):
            engine.analyze("Some resume", "")

    @patch("src.engine.skill_gap_engine.SkillGapAgent")
    def test_llm_failure_returns_defaults(self, mock_agent_cls):
        from src.utils.errors import LLMError
        mock_agent = MagicMock()
        mock_agent.run.side_effect = LLMError("API down")
        mock_agent_cls.return_value = mock_agent

        engine = SkillGapEngine()
        # Patch embedding service to also fail so we get full fallback
        with patch.object(engine, '_compute_embedding_score', return_value=None):
            result = engine.analyze("Resume text", "Job text")

        assert result["match_score"] == 50
        assert result["missing_skills"] == []

    @patch("src.engine.skill_gap_engine.SkillGapAgent")
    def test_embedding_failure_falls_back_to_llm_score(self, mock_agent_cls):
        mock_agent = MagicMock()
        mock_agent.run.return_value = {
            "match_score": 72,
            "priority": "Medium",
            "missing_skills": ["AWS"]
        }
        mock_agent_cls.return_value = mock_agent

        engine = SkillGapEngine()
        with patch.object(engine, '_compute_embedding_score', return_value=None):
            result = engine.analyze("Resume text", "Job text")

        # Should fall back to LLM's match score
        assert result["match_score"] == 72

    @patch("src.engine.skill_gap_engine.SkillGapAgent")
    def test_embedding_score_used_when_available(self, mock_agent_cls):
        mock_agent = MagicMock()
        mock_agent.run.return_value = {
            "match_score": 72,
            "priority": "Medium",
            "missing_skills": ["AWS"]
        }
        mock_agent_cls.return_value = mock_agent

        engine = SkillGapEngine()
        with patch.object(engine, '_compute_embedding_score', return_value=85.5):
            result = engine.analyze("Resume text", "Job text")

        # Embedding score takes priority over LLM score
        assert result["match_score"] == 85.5
