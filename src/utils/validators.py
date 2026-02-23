"""Input validation and sanitization for SkillVector Engine."""

import re

MIN_INPUT_LENGTH = 50
MAX_RESUME_LENGTH = 50_000
MAX_JOB_DESC_LENGTH = 20_000


def validate_resume(text: str) -> tuple[bool, str]:
    """Validate resume text input.

    Returns:
        Tuple of (is_valid, error_message). error_message is empty if valid.
    """
    if not text or not text.strip():
        return False, "Resume text is required."
    stripped = text.strip()
    if len(stripped) < MIN_INPUT_LENGTH:
        return False, f"Resume must be at least {MIN_INPUT_LENGTH} characters."
    if len(text) > MAX_RESUME_LENGTH:
        return False, f"Resume exceeds maximum length of {MAX_RESUME_LENGTH:,} characters."
    return True, ""


def validate_job_description(text: str) -> tuple[bool, str]:
    """Validate job description text input.

    Returns:
        Tuple of (is_valid, error_message). error_message is empty if valid.
    """
    if not text or not text.strip():
        return False, "Job description is required."
    stripped = text.strip()
    if len(stripped) < MIN_INPUT_LENGTH:
        return False, f"Job description must be at least {MIN_INPUT_LENGTH} characters."
    if len(text) > MAX_JOB_DESC_LENGTH:
        return False, f"Job description exceeds maximum length of {MAX_JOB_DESC_LENGTH:,} characters."
    return True, ""


def sanitize_text(text: str) -> str:
    """Remove potentially harmful content from user input.

    Strips null bytes, normalizes excessive whitespace, and removes
    control characters that could interfere with processing.
    """
    # Remove null bytes
    text = text.replace("\x00", "")
    # Collapse runs of 4+ newlines to 3
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    # Remove other control characters (keep newlines, tabs)
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()
