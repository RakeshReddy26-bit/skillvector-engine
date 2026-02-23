"""Tests for seed_skills DAG integrity."""

from collections import deque

import pytest
from src.graph.seed_skills import PREREQUISITES, SKILLS, get_prerequisite_edges, get_skill_estimates, get_skill_names


class TestSeedSkillsDAG:
    """Validate the skill prerequisite DAG is well-formed."""

    def test_all_prerequisite_targets_exist_in_skills(self):
        """Every skill referenced in PREREQUISITES must exist in SKILLS."""
        skill_names = {s["name"] for s in SKILLS}
        for prereq, dependent in PREREQUISITES:
            assert prereq in skill_names, f"Prerequisite '{prereq}' not in SKILLS"
            assert dependent in skill_names, f"Dependent '{dependent}' not in SKILLS"

    def test_no_duplicate_skill_names(self):
        """Skill names must be unique."""
        names = [s["name"] for s in SKILLS]
        assert len(names) == len(set(names)), f"Duplicate skills: {[n for n in names if names.count(n) > 1]}"

    def test_dag_is_acyclic(self):
        """The prerequisite graph must be a DAG (no cycles)."""
        skill_names = {s["name"] for s in SKILLS}
        adjacency = {s: [] for s in skill_names}
        in_degree = {s: 0 for s in skill_names}

        for prereq, dependent in PREREQUISITES:
            adjacency[prereq].append(dependent)
            in_degree[dependent] += 1

        # Kahn's algorithm — if we can visit all nodes, it's a DAG
        queue = deque(s for s in skill_names if in_degree[s] == 0)
        visited = 0
        while queue:
            node = queue.popleft()
            visited += 1
            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        assert visited == len(skill_names), (
            f"Cycle detected: visited {visited}/{len(skill_names)} nodes"
        )

    def test_minimum_30_skills(self):
        """Catalog should have at least 30 skills."""
        assert len(SKILLS) >= 30

    def test_minimum_25_edges(self):
        """Prerequisite graph should have at least 25 edges."""
        assert len(PREREQUISITES) >= 25

    def test_get_skill_estimates_returns_dict(self):
        """get_skill_estimates returns lowercase skill -> days mapping."""
        estimates = get_skill_estimates()
        assert isinstance(estimates, dict)
        assert "python" in estimates
        assert estimates["python"] == 7

    def test_get_prerequisite_edges_returns_list(self):
        """get_prerequisite_edges returns list of tuples."""
        edges = get_prerequisite_edges()
        assert isinstance(edges, list)
        assert len(edges) == len(PREREQUISITES)
        assert all(isinstance(e, tuple) and len(e) == 2 for e in edges)

    def test_get_skill_names_returns_all(self):
        """get_skill_names returns all skill names."""
        names = get_skill_names()
        assert len(names) == len(SKILLS)
        assert "Python" in names
