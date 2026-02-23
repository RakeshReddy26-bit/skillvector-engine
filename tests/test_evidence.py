import pytest

from src.evidence.evidence_engine import EvidenceEngine


class TestEvidenceEngine:
    def test_generate_returns_list(self):
        engine = EvidenceEngine()
        result = engine.generate([{"skill": "Docker", "estimated_weeks": 1}])
        assert isinstance(result, list)

    def test_generate_empty_path_returns_empty(self):
        engine = EvidenceEngine()
        assert engine.generate([]) == []

    def test_known_skill_uses_template(self):
        engine = EvidenceEngine()
        result = engine.generate([{"skill": "Docker", "estimated_weeks": 1}])
        assert len(result) == 1
        assert result[0]["project"] == "Dockerize a FastAPI Application"
        assert "Dockerfile" in result[0]["deliverables"]

    def test_unknown_skill_gets_generic_project(self):
        engine = EvidenceEngine()
        result = engine.generate([{"skill": "Elixir", "estimated_weeks": 2}])
        assert len(result) == 1
        assert "Elixir" in result[0]["project"]
        assert result[0]["deliverables"] == ["README.md"]

    def test_each_entry_has_required_keys(self):
        engine = EvidenceEngine()
        result = engine.generate([{"skill": "Docker", "estimated_weeks": 1}])
        entry = result[0]
        assert "skill" in entry
        assert "project" in entry
        assert "description" in entry
        assert "deliverables" in entry
        assert "estimated_weeks" in entry

    def test_multiple_skills(self):
        engine = EvidenceEngine()
        path = [
            {"skill": "Docker", "estimated_weeks": 1},
            {"skill": "Kubernetes", "estimated_weeks": 1},
            {"skill": "Go", "estimated_weeks": 2},
        ]
        result = engine.generate(path)
        assert len(result) == 3

    def test_weeks_from_input_preserved(self):
        engine = EvidenceEngine()
        result = engine.generate([{"skill": "Docker", "estimated_weeks": 5}])
        assert result[0]["estimated_weeks"] == 5
