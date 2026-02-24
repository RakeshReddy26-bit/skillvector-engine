"""Pydantic request/response schemas for the SkillVector API."""

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    resume: str = Field(..., min_length=50, max_length=50000, description="Resume text")
    target_job: str = Field(
        ..., min_length=50, max_length=20000, description="Target job description"
    )


class AnalyzeResponse(BaseModel):
    match_score: float
    learning_priority: str
    missing_skills: list[str]
    learning_path: list[dict]
    evidence: list[dict]
    interview_prep: list[dict]
    rubrics: list[dict]
    related_jobs: list[dict]
    request_id: str
    latency_ms: int


class HealthResponse(BaseModel):
    status: str
    version: str
    model: str
    anthropic: str
    neo4j: str
    pinecone: str
    checks_ms: int


class ErrorResponse(BaseModel):
    error: str


# ── Auth schemas (v3) ────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=128)


class UserInfo(BaseModel):
    id: str
    email: str
    plan_tier: str
    analyses_used: int
    analyses_limit: int  # 3 for free, -1 for unlimited


class AuthResponse(BaseModel):
    token: str
    user: UserInfo


class UsageResponse(BaseModel):
    analyses_used: int
    analyses_limit: int
    plan_tier: str
    resets_on: str
