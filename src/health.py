"""Health check module for SkillVector Engine.

Reports system status: LLM config, Neo4j connectivity, Pinecone connectivity,
and application version.
"""

import logging
import os
import time

logger = logging.getLogger(__name__)

VERSION = "0.2.0"


def check_health() -> dict:
    """Run all health checks and return a status report.

    Returns:
        Dict with keys: status, version, model, neo4j, pinecone, checks_ms
    """
    start = time.monotonic()

    model = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
    anthropic_ok = bool(os.getenv("ANTHROPIC_API_KEY"))

    neo4j_status = _check_neo4j()
    pinecone_status = _check_pinecone()

    elapsed_ms = round((time.monotonic() - start) * 1000)

    overall = "healthy" if anthropic_ok else "degraded"

    return {
        "status": overall,
        "version": VERSION,
        "model": model,
        "anthropic": "ok" if anthropic_ok else "missing_key",
        "neo4j": neo4j_status,
        "pinecone": pinecone_status,
        "checks_ms": elapsed_ms,
    }


def _check_neo4j() -> str:
    """Check Neo4j connectivity. Returns 'ok', 'unavailable', or 'not_configured'."""
    uri = os.getenv("NEO4J_URI", "")
    password = os.getenv("NEO4J_PASSWORD", "")
    if not uri or not password:
        return "not_configured"
    try:
        from src.graph.neo4j_client import Neo4jClient
        client = Neo4jClient()
        if client.verify_connectivity():
            client.close()
            return "ok"
        client.close()
        return "unavailable"
    except Exception as e:
        logger.debug("Neo4j health check failed: %s", e)
        return "unavailable"


def _check_pinecone() -> str:
    """Check Pinecone connectivity. Returns 'ok', 'unavailable', or 'not_configured'."""
    api_key = os.getenv("PINECONE_API_KEY", "")
    if not api_key:
        return "not_configured"
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=api_key)
        index_name = os.getenv("PINECONE_INDEX_NAME", "skillvector-jobs")
        names = pc.list_indexes().names()
        return "ok" if index_name in names else "unavailable"
    except Exception as e:
        logger.debug("Pinecone health check failed: %s", e)
        return "unavailable"
