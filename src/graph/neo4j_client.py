"""Neo4j client for SkillVector Engine.

Provides a connection wrapper with lazy initialization, error handling,
and graceful fallback when Neo4j is unavailable.
"""

import logging
import os

from src.utils.errors import GraphError

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j connection wrapper with lazy initialization and error handling."""

    def __init__(self, uri=None, user=None, password=None):
        self._uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self._user = user or os.getenv("NEO4J_USER", "neo4j")
        self._password = password or os.getenv("NEO4J_PASSWORD", "password")
        self._driver = None

    @property
    def driver(self):
        """Lazy-load the Neo4j driver."""
        if self._driver is None:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(
                self._uri, auth=(self._user, self._password)
            )
        return self._driver

    def verify_connectivity(self, timeout: float = 5.0) -> bool:
        """Test that Neo4j is reachable. Returns True/False."""
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            logger.debug("Neo4j connectivity check failed: %s", e)
            return False

    def run(self, query: str, parameters: dict | None = None) -> list:
        """Execute a Cypher query and return materialized results.

        Raises GraphError on failure.
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return list(result)
        except Exception as e:
            raise GraphError(f"Neo4j query failed: {e}") from e

    def close(self):
        """Close the driver connection. Safe to call multiple times."""
        if self._driver is not None:
            try:
                self._driver.close()
            except Exception:
                pass
            self._driver = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
