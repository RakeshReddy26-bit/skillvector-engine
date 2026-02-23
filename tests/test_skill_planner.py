"""Tests for SkillPlanner — ordering, topological sort, and fallback."""

import pytest
from unittest.mock import MagicMock

from src.graph.skill_planner import SkillPlanner


# ── Original tests (8 tests) ────────────────────────────────────────────────

class TestSkillPlanner:
    def test_plan_returns_list(self):
        planner = SkillPlanner()
        result = planner.plan(["Docker", "Kubernetes"])
        assert isinstance(result, list)

    def test_plan_each_entry_has_required_keys(self):
        planner = SkillPlanner()
        result = planner.plan(["Docker"])
        assert len(result) == 1
        assert "skill" in result[0]
        assert "estimated_weeks" in result[0]
        assert "estimated_days" in result[0]

    def test_plan_empty_list_returns_empty(self):
        planner = SkillPlanner()
        result = planner.plan([])
        assert result == []

    def test_known_skill_has_specific_estimate(self):
        planner = SkillPlanner()
        result = planner.plan(["Docker"])
        assert result[0]["estimated_days"] == 5

    def test_unknown_skill_defaults_to_14_days(self):
        planner = SkillPlanner()
        result = planner.plan(["Obscure Framework XYZ"])
        assert result[0]["estimated_days"] == 14

    def test_plan_learning_path_alias(self):
        planner = SkillPlanner()
        r1 = planner.plan(["Docker"])
        r2 = planner.plan_learning_path(["Docker"])
        assert r1 == r2

    def test_case_insensitive_matching(self):
        planner = SkillPlanner()
        r1 = planner.plan(["docker"])
        r2 = planner.plan(["Docker"])
        r3 = planner.plan(["DOCKER"])
        assert r1[0]["estimated_days"] == r2[0]["estimated_days"] == r3[0]["estimated_days"]

    def test_preserves_original_skill_name(self):
        planner = SkillPlanner()
        result = planner.plan(["Docker"])
        assert result[0]["skill"] == "Docker"


# ── Topological sort tests (8 tests) ────────────────────────────────────────

class TestTopologicalSort:
    def test_single_skill_no_edges(self):
        result = SkillPlanner._topological_sort(["Python"], [])
        assert result == ["Python"]

    def test_two_skills_one_edge(self):
        result = SkillPlanner._topological_sort(
            ["Kubernetes", "Docker"],
            [("Docker", "Kubernetes")],
        )
        assert result == ["Docker", "Kubernetes"]

    def test_chain_of_three(self):
        result = SkillPlanner._topological_sort(
            ["Kubernetes", "Docker", "Linux"],
            [("Linux", "Docker"), ("Docker", "Kubernetes")],
        )
        assert result == ["Linux", "Docker", "Kubernetes"]

    def test_diamond_dependency(self):
        # A -> B, A -> C, B -> D, C -> D
        result = SkillPlanner._topological_sort(
            ["D", "C", "B", "A"],
            [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")],
        )
        assert result.index("A") < result.index("B")
        assert result.index("A") < result.index("C")
        assert result.index("B") < result.index("D")
        assert result.index("C") < result.index("D")

    def test_preserves_case(self):
        result = SkillPlanner._topological_sort(
            ["Docker", "Linux"],
            [("Linux", "Docker")],
        )
        assert result == ["Linux", "Docker"]
        # Original casing preserved, not lowered
        assert result[0] == "Linux"

    def test_disconnected_skills_alphabetical(self):
        result = SkillPlanner._topological_sort(
            ["Python", "Git", "SQL"],
            [],
        )
        assert result == ["Git", "Python", "SQL"]

    def test_edges_outside_skill_set_ignored(self):
        result = SkillPlanner._topological_sort(
            ["Docker"],
            [("Linux", "Docker"), ("Docker", "Kubernetes")],
        )
        # Linux and Kubernetes are not in the input set, so edges are ignored
        assert result == ["Docker"]

    def test_cycle_protection(self):
        # A -> B -> C -> A (cycle), should still return all skills
        result = SkillPlanner._topological_sort(
            ["A", "B", "C"],
            [("A", "B"), ("B", "C"), ("C", "A")],
        )
        assert set(result) == {"A", "B", "C"}
        assert len(result) == 3


# ── Prerequisite ordering tests (7 tests) ───────────────────────────────────

class TestPrerequisiteOrdering:
    """Test that the planner respects real prerequisite edges from seed_skills."""

    def setup_method(self):
        self.planner = SkillPlanner()

    def _skill_names(self, result):
        return [r["skill"] for r in result]

    def test_docker_before_kubernetes(self):
        result = self._skill_names(self.planner.plan(["Kubernetes", "Docker"]))
        assert result.index("Docker") < result.index("Kubernetes")

    def test_linux_docker_kubernetes_chain(self):
        result = self._skill_names(
            self.planner.plan(["Kubernetes", "Docker", "Linux"])
        )
        assert result.index("Linux") < result.index("Docker")
        assert result.index("Docker") < result.index("Kubernetes")

    def test_git_before_cicd(self):
        result = self._skill_names(self.planner.plan(["CI/CD", "Git"]))
        assert result.index("Git") < result.index("CI/CD")

    def test_sql_before_postgresql(self):
        result = self._skill_names(self.planner.plan(["PostgreSQL", "SQL"]))
        assert result.index("SQL") < result.index("PostgreSQL")

    def test_javascript_and_html_before_react(self):
        result = self._skill_names(
            self.planner.plan(["React", "JavaScript", "HTML/CSS"])
        )
        assert result.index("JavaScript") < result.index("React")
        assert result.index("HTML/CSS") < result.index("React")

    def test_complex_chain_to_system_design(self):
        skills = ["System Design", "Microservices", "Docker", "REST APIs", "Linux", "SQL"]
        result = self._skill_names(self.planner.plan(skills))
        # Linux -> Docker -> Microservices -> System Design
        assert result.index("Linux") < result.index("Docker")
        assert result.index("Docker") < result.index("Microservices")
        assert result.index("REST APIs") < result.index("Microservices")
        assert result.index("Microservices") < result.index("System Design")
        assert result.index("SQL") < result.index("System Design")

    def test_time_estimates_present_after_ordering(self):
        result = self.planner.plan(["Kubernetes", "Docker", "Linux"])
        for entry in result:
            assert "estimated_days" in entry
            assert "estimated_weeks" in entry
            assert entry["estimated_days"] > 0


# ── Fallback behavior tests (2 tests) ───────────────────────────────────────

class TestFallbackBehavior:
    def test_neo4j_failure_falls_back_to_in_memory(self):
        """When Neo4j client raises an error, planner uses in-memory edges."""
        mock_client = MagicMock()
        mock_client.run.side_effect = Exception("Connection refused")

        planner = SkillPlanner(neo4j_client=mock_client)
        result = planner.plan(["Kubernetes", "Docker"])
        names = [r["skill"] for r in result]
        # Should still order correctly using in-memory fallback
        assert names.index("Docker") < names.index("Kubernetes")

    def test_no_neo4j_client_uses_in_memory(self):
        """When no Neo4j client is provided, planner uses in-memory edges."""
        planner = SkillPlanner(neo4j_client=None)
        result = planner.plan(["Kubernetes", "Docker"])
        names = [r["skill"] for r in result]
        assert names.index("Docker") < names.index("Kubernetes")
