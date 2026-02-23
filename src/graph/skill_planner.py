"""Skill learning path planner with prerequisite-aware ordering.

Uses topological sort (Kahn's algorithm) to order skills so that
prerequisites are learned before dependents. Tries Neo4j first,
falls back to the in-memory DAG from seed_skills.py.
"""

import logging
from collections import deque
from typing import Dict, List, Optional

from src.graph.seed_skills import get_prerequisite_edges, get_skill_estimates

logger = logging.getLogger(__name__)


class SkillPlanner:
    """Orders missing skills into a learning path with time estimates."""

    def __init__(self, neo4j_client=None):
        self._neo4j_client = neo4j_client
        self._skill_estimates = get_skill_estimates()

    # ── Public API (unchanged) ───────────────────────────────────────────────

    def plan(self, missing_skills: List[str]) -> List[Dict]:
        """Convert missing skills list into an ordered learning path."""
        return self.plan_learning_path(missing_skills)

    def plan_learning_path(self, missing_skills: List[str]) -> List[Dict]:
        """Generate an ordered learning path from missing skills.

        Skills are topologically sorted so prerequisites come first.
        """
        if not missing_skills:
            logger.info("No missing skills to plan")
            return []

        logger.info("Planning learning path for %d skills", len(missing_skills))

        # 1. Get prerequisite edges (Neo4j-first, in-memory fallback)
        edges = self._get_prerequisite_edges()

        # 2. Topological sort — prerequisites before dependents
        ordered_skills = self._topological_sort(missing_skills, edges)

        # 3. Attach time estimates
        learning_path = []
        for skill in ordered_skills:
            skill_lower = skill.lower().strip()
            estimated_days = self._skill_estimates.get(skill_lower, 14)
            estimated_weeks = max(1, round(estimated_days / 7))

            learning_path.append({
                "skill": skill,
                "estimated_weeks": estimated_weeks,
                "estimated_days": estimated_days,
            })

        logger.info(
            "Learning path: %d steps, total %d days",
            len(learning_path),
            sum(s["estimated_days"] for s in learning_path),
        )
        return learning_path

    # ── Prerequisite edge retrieval ──────────────────────────────────────────

    def _get_prerequisite_edges(self) -> List[tuple]:
        """Get prerequisite edges. Tries Neo4j first, falls back to in-memory."""
        if self._neo4j_client is not None:
            try:
                edges = self._fetch_edges_from_neo4j()
                if edges:
                    logger.debug("Loaded %d edges from Neo4j", len(edges))
                    return edges
            except Exception as e:
                logger.warning("Neo4j edge fetch failed, using in-memory fallback: %s", e)

        return get_prerequisite_edges()

    def _fetch_edges_from_neo4j(self) -> List[tuple]:
        """Fetch prerequisite edges from Neo4j."""
        records = self._neo4j_client.run(
            "MATCH (a:Skill)-[:PREREQUISITE_OF]->(b:Skill) "
            "RETURN a.name AS prereq, b.name AS dependent"
        )
        return [(r["prereq"], r["dependent"]) for r in records]

    # ── Topological sort (Kahn's BFS) ────────────────────────────────────────

    @staticmethod
    def _topological_sort(
        skills: List[str],
        edges: List[tuple],
    ) -> List[str]:
        """Order skills so prerequisites come before dependents.

        Uses Kahn's BFS algorithm. Skills at the same tier are sorted
        alphabetically for determinism. Skills not connected by any edge
        appear in alphabetical order.

        Args:
            skills: List of skill names (original casing preserved).
            edges: List of (prerequisite, dependent) tuples.

        Returns:
            Topologically sorted list of skill names.
        """
        if not skills:
            return []

        # Build case-insensitive lookup: lowercase → original name
        case_map: Dict[str, str] = {}
        for s in skills:
            case_map[s.lower().strip()] = s

        skill_set = set(case_map.keys())

        # Filter edges to only those between skills in the input set
        relevant_edges = [
            (pre.lower().strip(), dep.lower().strip())
            for pre, dep in edges
            if pre.lower().strip() in skill_set
            and dep.lower().strip() in skill_set
        ]

        # Build adjacency list and in-degree map
        adjacency: Dict[str, list] = {s: [] for s in skill_set}
        in_degree: Dict[str, int] = {s: 0 for s in skill_set}

        for pre, dep in relevant_edges:
            adjacency[pre].append(dep)
            in_degree[dep] += 1

        # BFS from zero-in-degree nodes (sorted alphabetically for determinism)
        queue = deque(sorted(s for s in skill_set if in_degree[s] == 0))
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # Sort neighbors for deterministic order
            for neighbor in sorted(adjacency[node]):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
            # Re-sort queue to maintain alphabetical order among ready nodes
            queue = deque(sorted(queue))

        # Cycle protection: append any remaining nodes not yet visited
        remaining = sorted(s for s in skill_set if s not in set(result))
        if remaining:
            logger.warning("Cycle detected in skill graph; appending %d remaining skills", len(remaining))
            result.extend(remaining)

        # Restore original casing
        return [case_map[s] for s in result]
