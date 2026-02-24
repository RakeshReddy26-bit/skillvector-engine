"""Authentication endpoints for SkillVector API."""

import logging
import os
from datetime import date, datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from api.models import AuthResponse, LoginRequest, RegisterRequest, UserInfo, UsageResponse
from src.auth.auth_service import AuthService
from src.db.models import UserRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 72

FREE_TIER_LIMIT = 3


def create_token(user_id: str, email: str) -> str:
    """Create a JWT token for authenticated sessions."""
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Decode and verify a JWT token. Returns payload or None."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def get_current_user(request: Request) -> dict | None:
    """Extract user from Authorization header. Returns None if not authenticated."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    payload = decode_token(token)
    if not payload:
        return None
    user_repo = UserRepository()
    return user_repo.get_user_by_email(payload.get("email", ""))


def _get_monthly_usage(user_id: str) -> int:
    """Count analyses this calendar month for a user."""
    user_repo = UserRepository()
    return user_repo.count_monthly_analyses(user_id)


def _next_reset_date() -> str:
    """Return the first day of next month as ISO date string."""
    today = date.today()
    if today.month == 12:
        return date(today.year + 1, 1, 1).isoformat()
    return date(today.year, today.month + 1, 1).isoformat()


@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest):
    """Register a new user with email and password."""
    auth_service = AuthService()
    user_repo = UserRepository()

    # 1. Validate email format
    valid, err = AuthService.validate_email(req.email)
    if not valid:
        return JSONResponse(status_code=422, content={"error": err})

    # 2. Validate password strength
    valid, err = AuthService.validate_password(req.password)
    if not valid:
        return JSONResponse(status_code=422, content={"error": err})

    # 3. Check if email already taken
    if user_repo.user_exists(req.email):
        return JSONResponse(status_code=409, content={"error": "Email already registered."})

    # 4. Create user
    password_hash = auth_service.hash_password(req.password)
    user_id = user_repo.create_user(req.email, password_hash)

    # 5. Generate JWT
    token = create_token(user_id, req.email.lower().strip())

    return AuthResponse(
        token=token,
        user=UserInfo(
            id=user_id,
            email=req.email.lower().strip(),
            plan_tier="free",
            analyses_used=0,
            analyses_limit=FREE_TIER_LIMIT,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest):
    """Log in with email and password."""
    auth_service = AuthService()
    user_repo = UserRepository()

    # 1. Find user
    user = user_repo.get_user_by_email(req.email)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid email or password."})

    # 2. Verify password
    if not auth_service.verify_password(req.password, user["password_hash"]):
        return JSONResponse(status_code=401, content={"error": "Invalid email or password."})

    # 3. Get usage info
    analyses_used = _get_monthly_usage(user["id"])
    plan_tier = user.get("plan_tier", "free")

    # 4. Generate JWT
    token = create_token(user["id"], user["email"])

    return AuthResponse(
        token=token,
        user=UserInfo(
            id=user["id"],
            email=user["email"],
            plan_tier=plan_tier,
            analyses_used=analyses_used,
            analyses_limit=-1 if plan_tier == "pro" else FREE_TIER_LIMIT,
        ),
    )


@router.get("/me", response_model=UserInfo)
def get_me(request: Request):
    """Get current user info from JWT token."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated."})

    analyses_used = _get_monthly_usage(user["id"])
    plan_tier = user.get("plan_tier", "free")

    return UserInfo(
        id=user["id"],
        email=user["email"],
        plan_tier=plan_tier,
        analyses_used=analyses_used,
        analyses_limit=-1 if plan_tier == "pro" else FREE_TIER_LIMIT,
    )


@router.get("/usage", response_model=UsageResponse)
def get_usage(request: Request):
    """Get usage stats for the current user."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated."})

    analyses_used = _get_monthly_usage(user["id"])
    plan_tier = user.get("plan_tier", "free")

    return UsageResponse(
        analyses_used=analyses_used,
        analyses_limit=-1 if plan_tier == "pro" else FREE_TIER_LIMIT,
        plan_tier=plan_tier,
        resets_on=_next_reset_date(),
    )
