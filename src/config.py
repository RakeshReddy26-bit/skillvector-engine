"""Centralized configuration for SkillVector Engine."""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """Get a config value from env vars, falling back to Streamlit secrets."""
    value = os.getenv(key, "")
    if not value:
        try:
            import streamlit as st
            value = st.secrets.get(key, default)
        except Exception:
            value = default
    return value


class Config:
    """Application configuration loaded from environment variables."""

    # Required
    ANTHROPIC_API_KEY: str = _get_secret("ANTHROPIC_API_KEY")

    # Pinecone (optional)
    PINECONE_API_KEY: str = _get_secret("PINECONE_API_KEY")
    PINECONE_INDEX_NAME: str = _get_secret("PINECONE_INDEX_NAME", "skillvector-jobs")
    PINECONE_ENVIRONMENT: str = _get_secret("PINECONE_ENVIRONMENT", "us-east-1")

    # Neo4j (optional)
    NEO4J_URI: str = _get_secret("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = _get_secret("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = _get_secret("NEO4J_PASSWORD")

    # Model settings
    EMBEDDING_MODEL: str = _get_secret("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    LLM_MODEL: str = _get_secret("LLM_MODEL", "claude-sonnet-4-20250514")
    LLM_TEMPERATURE: float = float(_get_secret("LLM_TEMPERATURE", "0"))

    # Application settings
    LOG_LEVEL: str = _get_secret("LOG_LEVEL", "INFO")
    RATE_LIMIT_PER_HOUR: int = int(_get_secret("RATE_LIMIT_PER_HOUR", "10"))
    MAX_RESUME_LENGTH: int = int(_get_secret("MAX_RESUME_LENGTH", "50000"))
    MAX_JOB_DESC_LENGTH: int = int(_get_secret("MAX_JOB_DESC_LENGTH", "20000"))

    @classmethod
    def validate_core(cls) -> list[str]:
        """Validate that minimum required config is set. Returns list of errors."""
        errors = []
        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is not set")
        return errors

    @classmethod
    def validate_rag(cls) -> list[str]:
        """Validate RAG-specific config. Returns list of errors."""
        errors = cls.validate_core()
        if not cls.PINECONE_API_KEY:
            errors.append("PINECONE_API_KEY is not set")
        return errors

    @classmethod
    def validate_graph(cls) -> list[str]:
        """Validate graph-specific config. Returns list of errors."""
        errors = []
        if not cls.NEO4J_PASSWORD:
            errors.append("NEO4J_PASSWORD is not set")
        return errors


@lru_cache
def get_config() -> Config:
    """Get singleton config instance."""
    return Config()
