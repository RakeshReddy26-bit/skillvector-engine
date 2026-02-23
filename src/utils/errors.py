"""Custom exceptions for the SkillVector Engine."""


class SkillVectorError(Exception):
    """Base exception for all SkillVector errors."""
    pass


class ValidationError(SkillVectorError):
    """Raised when input validation fails (empty resume, bad format, etc.)."""
    pass


class EmbeddingError(SkillVectorError):
    """Raised when text embedding fails."""
    pass


class LLMError(SkillVectorError):
    """Raised when LLM API call fails."""
    pass


class RetrievalError(SkillVectorError):
    """Raised when vector DB retrieval fails (Pinecone)."""
    pass


class GraphError(SkillVectorError):
    """Raised when knowledge graph operations fail (Neo4j)."""
    pass


class ConfigurationError(SkillVectorError):
    """Raised when required configuration is missing."""
    pass
