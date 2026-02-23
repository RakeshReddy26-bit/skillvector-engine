"""Tests for health check module."""

from unittest.mock import patch

from src.health import check_health, VERSION


class TestCheckHealth:
    """Tests for check_health()."""

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}, clear=False)
    @patch("src.health._check_neo4j", return_value="not_configured")
    @patch("src.health._check_pinecone", return_value="not_configured")
    def test_healthy_when_anthropic_key_present(self, _neo4j, _pinecone):
        result = check_health()
        assert result["status"] == "healthy"
        assert result["anthropic"] == "ok"
        assert result["version"] == VERSION
        assert isinstance(result["checks_ms"], int)

    @patch.dict("os.environ", {}, clear=False)
    @patch("src.health._check_neo4j", return_value="not_configured")
    @patch("src.health._check_pinecone", return_value="not_configured")
    def test_degraded_when_anthropic_key_missing(self, _neo4j, _pinecone):
        import os
        key = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            result = check_health()
            assert result["status"] == "degraded"
            assert result["anthropic"] == "missing_key"
        finally:
            if key:
                os.environ["ANTHROPIC_API_KEY"] = key

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test", "LLM_MODEL": "claude-opus-4-20250514"}, clear=False)
    @patch("src.health._check_neo4j", return_value="ok")
    @patch("src.health._check_pinecone", return_value="ok")
    def test_reports_correct_model(self, _neo4j, _pinecone):
        result = check_health()
        assert result["model"] == "claude-opus-4-20250514"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}, clear=False)
    @patch("src.health._check_neo4j", return_value="ok")
    @patch("src.health._check_pinecone", return_value="unavailable")
    def test_reports_service_statuses(self, _neo4j, _pinecone):
        result = check_health()
        assert result["neo4j"] == "ok"
        assert result["pinecone"] == "unavailable"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}, clear=False)
    @patch("src.health._check_neo4j", return_value="not_configured")
    @patch("src.health._check_pinecone", return_value="not_configured")
    def test_latency_is_non_negative(self, _neo4j, _pinecone):
        result = check_health()
        assert result["checks_ms"] >= 0


class TestNeo4jHealthCheck:
    """Tests for _check_neo4j()."""

    @patch.dict("os.environ", {}, clear=False)
    def test_not_configured_when_no_env_vars(self):
        import os
        uri = os.environ.pop("NEO4J_URI", None)
        pwd = os.environ.pop("NEO4J_PASSWORD", None)
        try:
            from src.health import _check_neo4j
            assert _check_neo4j() == "not_configured"
        finally:
            if uri:
                os.environ["NEO4J_URI"] = uri
            if pwd:
                os.environ["NEO4J_PASSWORD"] = pwd


class TestPineconHealthCheck:
    """Tests for _check_pinecone()."""

    @patch.dict("os.environ", {}, clear=False)
    def test_not_configured_when_no_api_key(self):
        import os
        key = os.environ.pop("PINECONE_API_KEY", None)
        try:
            from src.health import _check_pinecone
            assert _check_pinecone() == "not_configured"
        finally:
            if key:
                os.environ["PINECONE_API_KEY"] = key
