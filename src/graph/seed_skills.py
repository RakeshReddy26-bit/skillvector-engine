from src.graph.neo4j_client import Neo4jClient


SKILLS = [
    {"name": "Python"},
    {"name": "Docker"},
    {"name": "Kubernetes"},
]

PREREQUISITES = [
    ("Python", "Docker"),
    ("Docker", "Kubernetes"),
]


def seed_skills():
    client = Neo4jClient()

    # Create skills (idempotent)
    for skill in SKILLS:
        client.run(
            """
            MERGE (s:Skill {name: $name})
            """,
            {"name": skill["name"]},
        )

    # Create prerequisite relationships (idempotent)
    for prereq, skill in PREREQUISITES:
        client.run(
            """
            MATCH (a:Skill {name: $prereq})
            MATCH (b:Skill {name: $skill})
            MERGE (a)-[:PREREQUISITE_OF]->(b)
            """,
            {"prereq": prereq, "skill": skill},
        )

    client.close()
    print(" Skills and prerequisites seeded successfully.")


if __name__ == "__main__":
    seed_skills()