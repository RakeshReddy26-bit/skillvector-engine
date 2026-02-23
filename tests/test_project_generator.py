"""Tests for ProjectGenerator."""

import pytest
from src.evidence.project_generator import ProjectGenerator


class TestProjectGenerator:
    def setup_method(self):
        self.gen = ProjectGenerator()

    def test_generate_returns_list(self):
        result = self.gen.generate(["Python", "Docker"])
        assert isinstance(result, list)
        assert len(result) > 0

    def test_generate_empty_skills_returns_empty(self):
        assert self.gen.generate([]) == []

    def test_entry_has_required_keys(self):
        result = self.gen.generate(["Docker"])
        entry = result[0]
        assert "skill" in entry
        assert "project" in entry
        assert "description" in entry
        assert "deliverables" in entry
        assert "difficulty" in entry
        assert "estimated_weeks" in entry

    def test_known_skill_uses_catalog(self):
        result = self.gen.generate(["Docker"], max_projects_per_skill=1)
        assert result[0]["project"] == "Multi-Service Docker Compose Stack"

    def test_unknown_skill_gets_generic(self):
        result = self.gen.generate(["SomeObscureTech"])
        assert len(result) == 1
        assert "SomeObscureTech" in result[0]["project"]

    def test_max_projects_per_skill(self):
        result = self.gen.generate(["Docker"], max_projects_per_skill=2)
        docker_projects = [r for r in result if r["skill"] == "Docker"]
        assert len(docker_projects) == 2

    def test_leverage_existing_skills(self):
        result = self.gen.generate(
            ["Docker"],
            existing_skills=["Networking"],
            max_projects_per_skill=1,
        )
        entry = result[0]
        assert "leverage_existing" in entry

    def test_roadmap_returns_phases(self):
        roadmap = self.gen.get_roadmap(["Docker", "System Design"])
        assert "phases" in roadmap
        assert "total_weeks" in roadmap
        assert roadmap["total_weeks"] > 0

    def test_roadmap_empty_skills(self):
        roadmap = self.gen.get_roadmap([])
        assert roadmap == {"phases": [], "total_weeks": 0}
