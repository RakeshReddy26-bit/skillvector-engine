"""Tests for InterviewGenerator."""

import pytest
from src.evidence.interview_generator import InterviewGenerator


class TestInterviewGenerator:
    def setup_method(self):
        self.gen = InterviewGenerator(use_llm=False)

    def test_generate_returns_list(self):
        result = self.gen.generate(["Python", "Docker"])
        assert isinstance(result, list)
        assert len(result) == 2

    def test_generate_empty_skills_returns_empty(self):
        assert self.gen.generate([]) == []

    def test_entry_has_required_keys(self):
        result = self.gen.generate(["Python"])
        entry = result[0]
        assert "skill" in entry
        assert "questions" in entry
        assert "difficulty" in entry
        assert "tips" in entry

    def test_known_skill_returns_curated_questions(self):
        result = self.gen.generate(["Python"], questions_per_skill=3)
        entry = result[0]
        assert len(entry["questions"]) == 3
        assert entry["skill"] == "Python"

    def test_unknown_skill_returns_generic_questions(self):
        result = self.gen.generate(["SomeObscureTech"])
        entry = result[0]
        assert len(entry["questions"]) > 0
        assert "SomeObscureTech" in entry["questions"][0]

    def test_difficulty_levels(self):
        result = self.gen.generate(["system design", "docker", "python"])
        difficulties = {r["skill"]: r["difficulty"] for r in result}
        assert difficulties["system design"] == "Advanced"
        assert difficulties["docker"] == "Intermediate"
        assert difficulties["python"] == "Foundational"

    def test_questions_per_skill_limit(self):
        result = self.gen.generate(["Python"], questions_per_skill=2)
        assert len(result[0]["questions"]) == 2

    def test_tips_returned(self):
        result = self.gen.generate(["Docker"])
        assert len(result[0]["tips"]) > 0
