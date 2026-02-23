"""Authentication service for SkillVector Engine."""

import hashlib
import logging
import re
import secrets

logger = logging.getLogger(__name__)


class AuthService:
    """Handles password hashing and verification."""

    def hash_password(self, password: str) -> str:
        """Hash a password with PBKDF2 + random salt."""
        salt = secrets.token_hex(16)
        hash_bytes = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
        )
        return f"{salt}:{hash_bytes.hex()}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify a password against a stored hash."""
        try:
            salt, hash_val = stored_hash.split(":")
            check = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
            )
            return check.hex() == hash_val
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Basic email validation."""
        if not email or not email.strip():
            return False, "Email is required."
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email.strip()):
            return False, "Please enter a valid email address."
        return True, ""

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Password strength validation."""
        if not password:
            return False, "Password is required."
        if len(password) < 8:
            return False, "Password must be at least 8 characters."
        return True, ""
