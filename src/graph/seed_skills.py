"""Skill graph data and Neo4j seeding for SkillVector Engine.

This module is the SINGLE SOURCE OF TRUTH for the skill prerequisite DAG.
Both the Neo4j seeder and the in-memory fallback in SkillPlanner import from here.
"""

import logging

logger = logging.getLogger(__name__)


# ── Complete skill catalog (32 skills) ────────────────────────────────────────

SKILLS = [
    # Languages
    {"name": "Python", "category": "language", "estimated_days": 7},
    {"name": "JavaScript", "category": "language", "estimated_days": 7},
    {"name": "Java", "category": "language", "estimated_days": 10},
    {"name": "Go", "category": "language", "estimated_days": 10},
    # Data foundations
    {"name": "SQL", "category": "data", "estimated_days": 5},
    {"name": "PostgreSQL", "category": "data", "estimated_days": 5},
    {"name": "MongoDB", "category": "data", "estimated_days": 5},
    {"name": "Redis", "category": "data", "estimated_days": 4},
    # Tools
    {"name": "Git", "category": "tool", "estimated_days": 3},
    # Operations
    {"name": "Linux", "category": "operations", "estimated_days": 5},
    {"name": "Nginx", "category": "operations", "estimated_days": 3},
    # Frontend
    {"name": "HTML/CSS", "category": "frontend", "estimated_days": 5},
    {"name": "TypeScript", "category": "language", "estimated_days": 7},
    {"name": "React", "category": "frontend", "estimated_days": 10},
    # Runtimes / Frameworks
    {"name": "Node.js", "category": "runtime", "estimated_days": 7},
    {"name": "Django", "category": "framework", "estimated_days": 7},
    {"name": "FastAPI", "category": "framework", "estimated_days": 5},
    {"name": "Spring Boot", "category": "framework", "estimated_days": 10},
    # Architecture
    {"name": "REST APIs", "category": "architecture", "estimated_days": 4},
    {"name": "GraphQL", "category": "architecture", "estimated_days": 5},
    {"name": "Microservices", "category": "architecture", "estimated_days": 10},
    {"name": "System Design", "category": "architecture", "estimated_days": 14},
    # DevOps
    {"name": "Docker", "category": "devops", "estimated_days": 5},
    {"name": "Kubernetes", "category": "devops", "estimated_days": 7},
    {"name": "CI/CD", "category": "devops", "estimated_days": 5},
    {"name": "Terraform", "category": "devops", "estimated_days": 7},
    # Cloud
    {"name": "AWS", "category": "cloud", "estimated_days": 10},
    {"name": "GCP", "category": "cloud", "estimated_days": 10},
    {"name": "Azure", "category": "cloud", "estimated_days": 10},
    # Data engineering
    {"name": "Kafka", "category": "data", "estimated_days": 7},
    {"name": "Spark", "category": "data", "estimated_days": 10},
    {"name": "Airflow", "category": "data", "estimated_days": 7},
]


# ── Prerequisite edges (30 edges) ────────────────────────────────────────────
# Format: (prerequisite, dependent) — "prerequisite must be learned before dependent"
# Edge direction matches Neo4j: (prerequisite)-[:PREREQUISITE_OF]->(dependent)

PREREQUISITES = [
    # Language → Framework chains
    ("JavaScript", "TypeScript"),
    ("JavaScript", "React"),
    ("JavaScript", "Node.js"),
    ("HTML/CSS", "React"),
    ("Python", "Django"),
    ("Python", "FastAPI"),
    ("Java", "Spring Boot"),
    # SQL → Database chains
    ("SQL", "PostgreSQL"),
    ("SQL", "MongoDB"),
    ("SQL", "Redis"),
    # API layer
    ("REST APIs", "FastAPI"),
    ("REST APIs", "GraphQL"),
    ("REST APIs", "Microservices"),
    # Linux → Infrastructure
    ("Linux", "Docker"),
    ("Linux", "AWS"),
    ("Linux", "GCP"),
    ("Linux", "Azure"),
    ("Linux", "Nginx"),
    # DevOps chains
    ("Docker", "Kubernetes"),
    ("Docker", "CI/CD"),
    ("Docker", "Microservices"),
    ("Git", "CI/CD"),
    ("AWS", "Terraform"),
    # Data engineering
    ("Python", "Spark"),
    ("SQL", "Spark"),
    ("Python", "Airflow"),
    ("SQL", "Airflow"),
    ("Python", "Kafka"),
    # Advanced patterns
    ("Microservices", "System Design"),
    ("SQL", "System Design"),
]


# ── Export functions for in-memory fallback ───────────────────────────────────

def get_skill_estimates() -> dict[str, int]:
    """Return {skill_name_lower: estimated_days} dict."""
    return {s["name"].lower(): s["estimated_days"] for s in SKILLS}


def get_prerequisite_edges() -> list[tuple[str, str]]:
    """Return prerequisite edges as (prerequisite, dependent) tuples."""
    return list(PREREQUISITES)


def get_skill_names() -> list[str]:
    """Return all skill names."""
    return [s["name"] for s in SKILLS]


# ── Neo4j seeding ─────────────────────────────────────────────────────────────

def seed_skills():
    """Seed the Neo4j database with all skills and prerequisite edges."""
    from src.graph.neo4j_client import Neo4jClient

    client = Neo4jClient()

    # Create skills (idempotent via MERGE)
    for skill in SKILLS:
        client.run(
            """
            MERGE (s:Skill {name: $name})
            SET s.category = $category, s.estimated_days = $days
            """,
            {
                "name": skill["name"],
                "category": skill["category"],
                "days": skill["estimated_days"],
            },
        )

    # Create prerequisite relationships (idempotent via MERGE)
    for prereq, dependent in PREREQUISITES:
        client.run(
            """
            MATCH (a:Skill {name: $prereq})
            MATCH (b:Skill {name: $dependent})
            MERGE (a)-[:PREREQUISITE_OF]->(b)
            """,
            {"prereq": prereq, "dependent": dependent},
        )

    client.close()
    logger.info("Seeded %d skills and %d prerequisite edges", len(SKILLS), len(PREREQUISITES))


if __name__ == "__main__":
    seed_skills()
    print(f"Seeded {len(SKILLS)} skills and {len(PREREQUISITES)} prerequisite edges.")
