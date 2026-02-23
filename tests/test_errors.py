import pytest

from src.utils.errors import (
    SkillVectorError,
    ValidationError,
    EmbeddingError,
    LLMError,
    RetrievalError,
    GraphError,
    ConfigurationError,
)


class TestErrorHierarchy:
    def test_all_errors_inherit_from_base(self):
        for error_cls in [ValidationError, EmbeddingError, LLMError,
                          RetrievalError, GraphError, ConfigurationError]:
            assert issubclass(error_cls, SkillVectorError)

    def test_base_inherits_from_exception(self):
        assert issubclass(SkillVectorError, Exception)

    def test_errors_can_be_raised_and_caught(self):
        with pytest.raises(SkillVectorError):
            raise ValidationError("test")

    def test_error_message_preserved(self):
        msg = "Missing API key"
        err = ConfigurationError(msg)
        assert str(err) == msg
