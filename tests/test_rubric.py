"""Tests for RubricEngine."""

import pytest
from src.evidence.rubric import RubricEngine


class TestRubricEngine:
    def setup_method(self):
        self.engine = RubricEngine()

    def test_generate_returns_list(self):
        result = self.engine.generate(["Python", "Docker"])
        assert isinstance(result, list)
        assert len(result) == 2

    def test_generate_empty_skills_returns_empty(self):
        assert self.engine.generate([]) == []

    def test_entry_has_required_keys(self):
        result = self.engine.generate(["Python"])
        rubric = result[0]
        assert "skill" in rubric
        assert "criteria" in rubric
        assert "scoring" in rubric
        assert "total_points" in rubric
        assert rubric["total_points"] == 100

    def test_known_skill_has_specific_criteria(self):
        result = self.engine.generate(["Python"])
        criteria_names = [c["name"] for c in result[0]["criteria"]]
        assert "Code Quality" in criteria_names
        assert "Testing" in criteria_names

    def test_unknown_skill_has_generic_criteria(self):
        result = self.engine.generate(["SomeObscureTech"])
        criteria_names = [c["name"] for c in result[0]["criteria"]]
        assert "Technical Implementation" in criteria_names
        assert "Code Quality" in criteria_names

    def test_criteria_weights_sum_to_100(self):
        result = self.engine.generate(["Python"])
        total = sum(c["weight"] for c in result[0]["criteria"])
        assert total == 100

    def test_each_criterion_has_levels(self):
        result = self.engine.generate(["Docker"])
        for criterion in result[0]["criteria"]:
            assert "Excellent" in criterion["levels"]
            assert "Good" in criterion["levels"]
            assert "Needs Work" in criterion["levels"]

    def test_scoring_guide_structure(self):
        result = self.engine.generate(["Python"])
        scoring = result[0]["scoring"]
        assert "Excellent" in scoring
        assert "Good" in scoring
        assert "Needs Work" in scoring
        assert "range" in scoring["Excellent"]

    def test_evaluate_checklist_known_skill(self):
        checklist = self.engine.evaluate_checklist("Python")
        assert isinstance(checklist, list)
        assert len(checklist) > 0
        assert "item" in checklist[0]
        assert "category" in checklist[0]

    def test_evaluate_checklist_unknown_skill(self):
        checklist = self.engine.evaluate_checklist("SomeObscureTech")
        assert isinstance(checklist, list)
        assert len(checklist) > 0
