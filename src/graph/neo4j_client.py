from neo4j import GraphDatabase
import os


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(
                os.getenv("NEO4J_USER", "neo4j"),
                os.getenv("NEO4J_PASSWORD", "password"),
            ),
        )

    def run(self, query: str, parameters: dict | None = None):
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            # 🔑 Materialize INSIDE the client
            return list(result)