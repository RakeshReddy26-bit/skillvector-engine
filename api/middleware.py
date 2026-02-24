"""Optional auth dependency and usage limit checking for SkillVector API."""

import logging

from fastapi import Request

from api.auth import FREE_TIER_LIMIT, get_current_user
from src.db.models import UserRepository

logger = logging.getLogger(__name__)


def get_optional_user(request: Request) -> dict | None:
    """Dependency: returns user dict if authenticated, None otherwise."""
    return get_current_user(request)


def check_usage_limit(user: dict | None) -> tuple[bool, str]:
    """Check if the user has remaining analyses.

    Returns (allowed, error_message).
    Anonymous users: always allowed (rate limiter handles them).
    Free users: 3/month limit.
    Pro users: unlimited.
    """
    if user is None:
        return True, ""  # Anonymous — rate limiter handles this

    plan_tier = user.get("plan_tier", "free")
    if plan_tier == "pro":
        return True, ""

    user_repo = UserRepository()
    used = user_repo.count_monthly_analyses(user["id"])
    if used >= FREE_TIER_LIMIT:
        return False, (
            f"Free tier limit reached ({FREE_TIER_LIMIT} analyses per month). "
            "Upgrade to Pro for unlimited analyses."
        )
    return True, ""
