"""SkillVector API — FastAPI application.

Thin HTTP layer wrapping the existing src/ pipeline.
Endpoints: GET /health, POST /analyze, POST /upload-resume, GET / (frontend).
Auth: JWT-based optional auth with usage limits (v3).
"""

import io
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from api.auth import router as auth_router
from api.dashboard import router as dashboard_router
from api.middleware import check_usage_limit, get_optional_user
from api.models import AnalyzeRequest, AnalyzeResponse, ErrorResponse, HealthResponse
from api.stripe_routes import router as stripe_router
from src.routes.automation import router as automation_router
from src.routes.reports import router as reports_router
from src.db.database import init_db
from src.health import check_health
from src.pipeline.full_pipeline import SkillVectorPipeline
from src.utils.errors import SkillVectorError
from src.utils.rate_limiter import RateLimiter
from src.utils.validators import sanitize_text, validate_job_description, validate_resume

load_dotenv()

logger = logging.getLogger(__name__)

# Optional parser dependencies used by file upload extraction.
try:
    import pdfplumber
except Exception:  # pragma: no cover - environment dependent import
    pdfplumber = None

try:
    import docx2txt
except Exception:  # pragma: no cover - environment dependent import
    docx2txt = None

# Module-level state populated during lifespan
pipeline: Optional[SkillVectorPipeline] = None
rate_limiter: Optional[RateLimiter] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline, rate_limiter
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    logger.info("Starting SkillVector API v3...")
    init_db()
    pipeline = SkillVectorPipeline()
    rate_limiter = RateLimiter(
        max_requests=int(os.getenv("RATE_LIMIT_PER_HOUR", "10")),
        window_seconds=3600,
    )
    logger.info("SkillVector API ready")
    yield
    logger.info("Shutting down SkillVector API")


app = FastAPI(
    title="SkillVector API",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS — production + local dev
ALLOWED_ORIGINS = [
    "https://rakeshreddy26-bit.github.io",
    "https://skill-vector.com",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Mount auth and stripe routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(stripe_router)
app.include_router(automation_router)
app.include_router(reports_router)


@app.get("/health", response_model=HealthResponse)
def health():
    """Return system health status."""
    return check_health()


@app.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        403: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def analyze(request: AnalyzeRequest, req: Request):
    """Run the full SkillVector analysis pipeline."""
    # 1. Check auth and usage limits
    user = get_optional_user(req)

    if user is None:
        # Anonymous: rate limit by client IP
        client_ip = req.client.host if req.client else "unknown"
        allowed, rate_msg = rate_limiter.check(client_ip)
        if not allowed:
            return JSONResponse(status_code=429, content={"error": rate_msg})
    else:
        # Authenticated: check usage limit
        allowed, limit_msg = check_usage_limit(user)
        if not allowed:
            return JSONResponse(status_code=403, content={"error": limit_msg})

    # 2. Sanitize input
    resume = sanitize_text(request.resume)
    job = sanitize_text(request.target_job)

    # 3. Validate
    valid, err = validate_resume(resume)
    if not valid:
        return JSONResponse(status_code=422, content={"error": err})
    valid, err = validate_job_description(job)
    if not valid:
        return JSONResponse(status_code=422, content={"error": err})

    # 4. Check Anthropic key
    if not os.getenv("ANTHROPIC_API_KEY"):
        return JSONResponse(
            status_code=503,
            content={"error": "Service not configured. ANTHROPIC_API_KEY is missing."},
        )

    # 5. Run pipeline
    try:
        result = pipeline.run(resume, job)

        # Save analysis for authenticated users
        if user:
            try:
                from src.db.models import AnalysisRepository

                AnalysisRepository().save_analysis(user["id"], resume, job, result)
            except Exception:
                logger.exception("Failed to save analysis for user %s", user["id"])

        return result
    except SkillVectorError as e:
        logger.error("Pipeline error: %s", e)
        return JSONResponse(
            status_code=500, content={"error": f"Analysis failed: {e}"}
        )
    except Exception:
        logger.exception("Unexpected error in /analyze")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error. Please try again."},
        )


# ── File upload endpoint ──────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png"}


def _extract_text_from_file(filename: str, content: bytes) -> str:
    """Extract text from uploaded file based on extension."""
    ext = Path(filename).suffix.lower()
    file_size = len(content)
    logger.info(
        "Starting file extraction: filename=%s extension=%s size_bytes=%d",
        filename,
        ext,
        file_size,
    )

    if file_size == 0:
        raise ValueError("Uploaded file is empty.")

    if ext == ".txt":
        try:
            text = content.decode("utf-8", errors="replace")
        except Exception as e:
            logger.exception(
                "TXT extraction failed: filename=%s error_type=%s error=%s",
                filename,
                type(e).__name__,
                e,
            )
            raise ValueError(f"Failed to decode TXT file: {e}") from e
        if not text.strip():
            raise ValueError("TXT file contains no readable text.")
        return text

    if ext == ".pdf":
        if pdfplumber is None:
            raise ValueError("PDF extraction dependency is unavailable: pdfplumber is not installed.")
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                page_texts = []
                for idx, page in enumerate(pdf.pages, start=1):
                    try:
                        page_texts.append(page.extract_text() or "")
                    except Exception as e:
                        logger.warning(
                            "Failed to extract PDF page text: filename=%s page=%d error_type=%s error=%s",
                            filename,
                            idx,
                            type(e).__name__,
                            e,
                        )
                        page_texts.append("")
        except Exception as e:
            error_message = str(e)
            error_type = type(e).__name__
            logger.exception(
                "PDF extraction failed: filename=%s error_type=%s error=%s",
                filename,
                error_type,
                error_message,
            )
            if "password" in error_message.lower() or "encrypted" in error_message.lower():
                raise ValueError("PDF is password-protected or encrypted and cannot be read.") from e
            raise ValueError(f"Failed to parse PDF file: {error_type}: {error_message}") from e

        text = "\n".join(page_texts).strip()
        if not text:
            raise ValueError(
                "PDF was parsed but no readable text was found (it may contain only scanned images or empty pages)."
            )
        return text

    if ext == ".docx":
        if docx2txt is None:
            raise ValueError("DOCX extraction dependency is unavailable: docx2txt is not installed.")
        try:
            text = docx2txt.process(io.BytesIO(content))
        except Exception as e:
            logger.exception(
                "DOCX extraction failed: filename=%s error_type=%s error=%s",
                filename,
                type(e).__name__,
                e,
            )
            raise ValueError(f"Failed to parse DOCX file: {e}") from e
        if not text or not text.strip():
            raise ValueError("DOCX file contains no readable text.")
        return text

    if ext in {".jpg", ".jpeg", ".png"}:
        try:
            from PIL import Image
            import pytesseract

            image = Image.open(io.BytesIO(content))
            return pytesseract.image_to_string(image)
        except ImportError:
            raise ValueError(
                "Image OCR requires pytesseract and Tesseract to be installed."
            )
        except Exception as e:
            logger.exception(
                "Image OCR extraction failed: filename=%s error_type=%s error=%s",
                filename,
                type(e).__name__,
                e,
            )
            raise ValueError(f"Failed to extract text from image file: {e}") from e

    raise ValueError(f"Unsupported file type: {ext}")


@app.post(
    "/upload-resume",
    response_model=AnalyzeResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
async def upload_resume(
    req: Request,
    file: UploadFile = File(...),
    target_job: str = Form(...),
):
    """Upload a resume file (PDF/DOCX/TXT/image) and run analysis."""
    # 1. Check auth and usage limits
    user = get_optional_user(req)

    if user is None:
        client_ip = req.client.host if req.client else "unknown"
        allowed, rate_msg = rate_limiter.check(client_ip)
        if not allowed:
            return JSONResponse(status_code=429, content={"error": rate_msg})
    else:
        allowed, limit_msg = check_usage_limit(user)
        if not allowed:
            return JSONResponse(status_code=403, content={"error": limit_msg})

    # 2. Validate file
    if not file.filename:
        return JSONResponse(status_code=400, content={"error": "No file provided."})
    logger.info(
        "Received upload request: filename=%s content_type=%s",
        file.filename,
        file.content_type,
    )
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported file type: {ext}. Allowed: PDF, DOCX, TXT, JPG, PNG."},
        )

    # 3. Extract text
    try:
        content = await file.read()
        logger.info(
            "Read uploaded file bytes: filename=%s content_type=%s size_bytes=%d",
            file.filename,
            file.content_type,
            len(content),
        )
        resume = _extract_text_from_file(file.filename, content)
    except ValueError as e:
        logger.warning(
            "File extraction validation error: filename=%s error_type=%s error=%s",
            file.filename,
            type(e).__name__,
            e,
        )
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        logger.exception(
            "Unexpected file extraction error: filename=%s error_type=%s error=%s",
            file.filename,
            type(e).__name__,
            e,
        )
        return JSONResponse(
            status_code=400,
            content={"error": f"Could not read file: {type(e).__name__}: {e}"},
        )

    # 4. Sanitize + validate
    resume = sanitize_text(resume)
    job = sanitize_text(target_job)

    valid, err = validate_resume(resume)
    if not valid:
        return JSONResponse(status_code=422, content={"error": err})
    valid, err = validate_job_description(job)
    if not valid:
        return JSONResponse(status_code=422, content={"error": err})

    # 4b. Detect and translate language if needed
    from src.language.translator import process_resume_language
    lang_result = process_resume_language(resume)
    resume = lang_result["text"]
    detected_language = lang_result["language_name"]
    was_translated = lang_result["translated"]
    if was_translated:
        logger.info(f"Resume translated from {detected_language} to English")

    # 5. Check Anthropic key
    if not os.getenv("ANTHROPIC_API_KEY"):
        return JSONResponse(
            status_code=503,
            content={"error": "Service not configured. ANTHROPIC_API_KEY is missing."},
        )

    # 6. Run pipeline
    try:
        # === CACHE CHECK ===
        from src.cache.analysis_cache import get_cached_result, save_cached_result
        cached = get_cached_result(resume, job)
        if cached:
            logger.info("CACHE HIT - instant result returned")
            return JSONResponse(content=cached)
        logger.info("CACHE MISS - calling Claude pipeline")

        # === PIPELINE CALL ===
        result = pipeline.run(resume, job)

        # === CACHE SAVE ===
        if result and isinstance(result, dict) and "match_score" in result:
            save_cached_result(resume, job, result)
            logger.info(f"CACHE SAVED - {len(json.dumps(result, default=str))} bytes")
        else:
            logger.warning(f"CACHE SKIP - result missing fields: {list(result.keys()) if result else 'None'}")

        # Add language metadata to result
        result["detected_language"] = detected_language
        result["was_translated"] = was_translated

        # Save analysis for authenticated users
        if user:
            try:
                from src.db.models import AnalysisRepository

                AnalysisRepository().save_analysis(user["id"], resume, job, result)
            except Exception:
                logger.exception("Failed to save analysis for user %s", user["id"])

        return result
    except SkillVectorError as e:
        logger.error("Pipeline error: %s", e)
        return JSONResponse(status_code=500, content={"error": f"Analysis failed: {e}"})
    except Exception:
        logger.exception("Unexpected error in /upload-resume")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error. Please try again."},
        )


# ── Redirect root to Vercel frontend ─────────────────────────────────────

@app.get("/", include_in_schema=False)
def frontend():
    """Redirect to the Vercel frontend."""
    return RedirectResponse(url="https://skill-vector.com")
