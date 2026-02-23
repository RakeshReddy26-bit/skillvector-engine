import pytest
from unittest.mock import patch, MagicMock

from src.pipeline.full_pipeline import SkillVectorPipeline


class TestSkillVectorPipeline:
    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_run_returns_all_keys(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 60,
            "priority": "Medium",
            "missing_skills": ["Docker", "Kubernetes"]
        }
        mock_engine_cls.return_value = mock_engine

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        result = pipeline.run("resume text", "job text")

        assert "match_score" in result
        assert "learning_priority" in result
        assert "missing_skills" in result
        assert "learning_path" in result
        assert "evidence" in result
        assert "interview_prep" in result
        assert "rubrics" in result
        assert "related_jobs" in result

    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_high_priority_when_score_below_50(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 30,
            "priority": "High",
            "missing_skills": ["A", "B", "C"]
        }
        mock_engine_cls.return_value = mock_engine

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        result = pipeline.run("resume", "job")

        assert result["learning_priority"] == "High"

    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_medium_priority_when_score_50_to_74(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 65,
            "priority": "Medium",
            "missing_skills": ["Docker"]
        }
        mock_engine_cls.return_value = mock_engine

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        result = pipeline.run("resume", "job")

        assert result["learning_priority"] == "Medium"

    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_low_priority_when_score_75_or_above(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 85,
            "priority": "Low",
            "missing_skills": []
        }
        mock_engine_cls.return_value = mock_engine

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        result = pipeline.run("resume", "job")

        assert result["learning_priority"] == "Low"

    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_learning_path_generated_for_missing_skills(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 55,
            "priority": "Medium",
            "missing_skills": ["Docker", "Kubernetes"]
        }
        mock_engine_cls.return_value = mock_engine

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        result = pipeline.run("resume", "job")

        assert len(result["learning_path"]) == 2
        skills_in_path = [s["skill"] for s in result["learning_path"]]
        assert "Docker" in skills_in_path
        assert "Kubernetes" in skills_in_path

    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_evidence_generated_for_learning_path(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 55,
            "priority": "Medium",
            "missing_skills": ["Docker"]
        }
        mock_engine_cls.return_value = mock_engine

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        result = pipeline.run("resume", "job")

        assert len(result["evidence"]) >= 1
        assert result["evidence"][0]["skill"] == "Docker"

    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_graceful_degradation_on_planner_failure(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 55,
            "priority": "Medium",
            "missing_skills": ["Docker"]
        }
        mock_engine_cls.return_value = mock_engine

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        pipeline.skill_planner = MagicMock()
        pipeline.skill_planner.plan.side_effect = RuntimeError("planner broken")

        result = pipeline.run("resume", "job")

        # Should still return a result with fallback learning path
        assert len(result["learning_path"]) == 1
        assert result["learning_path"][0]["skill"] == "Docker"

    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_related_jobs_empty_when_pinecone_unavailable(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 70,
            "priority": "Medium",
            "missing_skills": ["Docker"],
        }
        mock_engine_cls.return_value = mock_engine

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        pipeline._job_retriever = None
        result = pipeline.run("resume", "job")

        assert result["related_jobs"] == []

    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_related_jobs_populated_when_retriever_available(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 70,
            "priority": "Medium",
            "missing_skills": ["Docker"],
        }
        mock_engine_cls.return_value = mock_engine

        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            {
                "score": 0.92,
                "job_title": "Backend Engineer",
                "company": "Acme",
                "skills": ["Python"],
                "chunk": "...",
            }
        ]

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        pipeline._job_retriever = mock_retriever
        result = pipeline.run("resume", "job")

        assert len(result["related_jobs"]) == 1
        assert result["related_jobs"][0]["job_title"] == "Backend Engineer"

    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_result_contains_request_id_and_latency(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 70,
            "priority": "Medium",
            "missing_skills": [],
        }
        mock_engine_cls.return_value = mock_engine

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        result = pipeline.run("resume", "job")

        assert "request_id" in result
        assert isinstance(result["request_id"], str)
        assert len(result["request_id"]) == 12
        assert "latency_ms" in result
        assert isinstance(result["latency_ms"], int)
        assert result["latency_ms"] >= 0

    @patch("src.pipeline.full_pipeline.SkillGapEngine")
    def test_related_jobs_empty_on_retriever_failure(self, mock_engine_cls):
        mock_engine = MagicMock()
        mock_engine.analyze.return_value = {
            "match_score": 70,
            "priority": "Medium",
            "missing_skills": [],
        }
        mock_engine_cls.return_value = mock_engine

        mock_retriever = MagicMock()
        mock_retriever.retrieve.side_effect = RuntimeError("Pinecone timeout")

        pipeline = SkillVectorPipeline()
        pipeline.skill_engine = mock_engine
        pipeline._job_retriever = mock_retriever
        result = pipeline.run("resume", "job")

        assert result["related_jobs"] == []
