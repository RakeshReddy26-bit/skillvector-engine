# SkillVector Engine

AI-powered career skill gap analysis platform. Upload a resume (PDF, DOCX, TXT, or image) or paste text, provide a target job description, and get a match score, missing skills, prerequisite-ordered learning path, portfolio project ideas, and semantically matched related jobs.

Built with **Python 3.11**, **Claude Sonnet (Anthropic)**, **FastAPI**, **Next.js 14**, **Pinecone**, **Neo4j**, **LangChain**, and **Sentence Transformers**.

**Live App:** [skill-vector.com](https://skill-vector.com)
**API Backend:** [api.skill-vector.com](https://api.skill-vector.com)
**GitHub:** [github.com/RakeshReddy26-bit/skillvector-engine](https://github.com/RakeshReddy26-bit/skillvector-engine)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [API Endpoints](#api-endpoints)
- [Frontend Components](#frontend-components)
- [Tech Stack](#tech-stack)
- [Roadmap](#roadmap)
- [License](#license)

---

## Features

| Feature | Description |
|---------|-------------|
| **Skill Gap Analysis** | Cosine similarity + Claude Sonnet reasoning to identify missing skills |
| **Match Score** | Deterministic 0-100% score using semantic embeddings (all-MiniLM-L6-v2) |
| **Learning Path** | Prerequisite-ordered skill-building steps with week/day estimates |
| **Evidence Projects** | Personalized portfolio project ideas with deliverables |
| **Related Jobs** | Semantic job matching via Pinecone vector database |
| **File Upload** | Upload resume as PDF, DOCX, TXT, JPG, or PNG (OCR via Tesseract) |
| **Drag & Drop** | Drag files directly into the upload zone |
| **Demo Mode** | Try the platform instantly with pre-loaded sample data |
| **Interview Prep** | 5 curated interview questions per missing skill with difficulty levels |
| **Evaluation Rubrics** | Weighted criteria (Excellent/Good/Needs Work) for self-assessment |
| **Rate Limiting** | IP-based sliding window rate limiter |
| **Graceful Degradation** | Works without Pinecone/Neo4j (falls back to local data) |
| **124 Tests** | Comprehensive test suite covering all pipeline stages |

---

## Architecture

```
                    Vercel (Free)                       Render (Free Tier)
               ┌─────────────────────┐    HTTPS    ┌──────────────────────────┐
               │  Next.js 14 App     │ ──────────> │  FastAPI + Uvicorn       │
               │  (React, Tailwind)  │  /analyze   │                          │
               │                     │  /upload    │  ┌────────────────────┐   │
               │  9 Components       │  /health    │  │ SkillVectorPipeline│   │
               │  TypeScript Strict  │             │  │                    │   │
               └─────────────────────┘             │  │  EmbeddingService  │   │
                                                   │  │  SkillGapAgent     │   │
                                                   │  │  SkillPlanner      │   │
                                                   │  │  EvidenceEngine    │   │
                                                   │  │  InterviewGen      │   │
                                                   │  │  RubricEngine      │   │
                                                   │  └────────────────────┘   │
                                                   │                          │
                                                   │  Pinecone ─ Neo4j ─ SQLite│
                                                   └──────────────────────────┘
```

**Data Flow:**

1. User uploads resume (file or text) + job description via Next.js frontend
2. Frontend sends POST to FastAPI backend (`/analyze` or `/upload-resume`)
3. `EmbeddingService` encodes resume + job using `all-MiniLM-L6-v2` (384-dim vectors)
4. `cosine_similarity` produces deterministic match score (0-100%)
5. `SkillGapAgent` (Claude Sonnet via LangChain) identifies missing skills
6. `SkillPlanner` orders skills by prerequisites with time estimates
7. `EvidenceEngine` generates portfolio project ideas with deliverables
8. `InterviewGenerator` produces 5 interview questions per skill
9. `RubricEngine` creates weighted evaluation criteria
10. Frontend transforms API response into rich display format and renders 5 dashboard panels

---

## How It Works

### Screen 1: Upload

- Upload a resume file (PDF, DOCX, TXT, JPG, PNG) via drag & drop or file picker
- Or paste resume text directly
- Paste target job description (optional but improves accuracy)
- Enter target role (e.g., "Senior ML Engineer at Stripe")
- Click **ANALYZE MY RESUME** or **TRY DEMO**

### Screen 2: Results Dashboard

Five panels render after analysis:

| Panel | Content |
|-------|---------|
| **01 Intelligence Score** | Animated SVG ring showing match %, color-coded (green >70, amber >40, red <40) |
| **02 Missing Skills** | Card grid with priority badges (HIGH/MEDIUM/LOW), color-coded top borders |
| **03 Learning Path** | Timeline with prerequisite ordering, duration badges, skill descriptions |
| **04 Evidence Builder** | Project cards with skill tags, descriptions, deliverable lists, copy button |
| **05 Related Jobs** | Semantic matches via Pinecone with match %, company, required skills chips |

---

## Project Structure

```
skillvector-engine/
├── api/                           # FastAPI backend
│   ├── __init__.py
│   ├── main.py                    # FastAPI app: /health, /analyze, /upload-resume
│   └── models.py                  # Pydantic request/response schemas
├── frontend/                      # Next.js 14 frontend
│   ├── app/
│   │   ├── layout.tsx             # Root layout with metadata
│   │   ├── page.tsx               # Home page with all panels
│   │   └── globals.css            # Tailwind + dashboard panel CSS
│   ├── components/
│   │   ├── ErrorBoundary.tsx      # React error boundary wrapper
│   │   ├── EvidencePanel.tsx      # Portfolio project cards
│   │   ├── HealthBanner.tsx       # API health status indicator
│   │   ├── LearningPath.tsx       # Timeline learning path
│   │   ├── RelatedJobs.tsx        # Semantic job matches
│   │   ├── ScoreRing.tsx          # Animated SVG score ring
│   │   ├── Skeleton.tsx           # Loading skeleton components
│   │   ├── SkillGapGrid.tsx       # Missing skills card grid
│   │   └── UploadZone.tsx         # File upload + text paste zone
│   ├── lib/
│   │   ├── api.ts                 # API client + transform layer
│   │   ├── demo-data.ts           # Demo result constant
│   │   └── types.ts               # TypeScript types (API + Display)
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── src/                           # Core Python pipeline (untouched by frontend)
│   ├── config.py                  # Centralized configuration
│   ├── health.py                  # Health check aggregator
│   ├── analytics/tracker.py       # Platform analytics engine
│   ├── auth/auth_service.py       # PBKDF2 password hashing
│   ├── db/
│   │   ├── database.py            # SQLite connection + schema
│   │   └── models.py              # UserRepo, AnalysisRepo, FeedbackRepo
│   ├── embeddings/
│   │   └── embedding_service.py   # SentenceTransformer wrapper (all-MiniLM-L6-v2)
│   ├── engine/
│   │   └── skill_gap_engine.py    # Core: embeddings + LLM + scoring
│   ├── evidence/
│   │   ├── evidence_engine.py     # Portfolio project templates
│   │   ├── interview_generator.py # Interview question generator (20 skills)
│   │   ├── project_generator.py   # Personalized project catalog
│   │   └── rubric.py              # Evaluation rubric engine
│   ├── graph/
│   │   ├── skill_planner.py       # Learning path ordering + time estimates
│   │   ├── neo4j_client.py        # Neo4j connection
│   │   └── seed_skills.py         # Graph seeding script
│   ├── llm/
│   │   ├── gap_agent.py           # Claude Sonnet skill gap agent
│   │   └── rag_prompt.py          # RAG-enhanced prompt builder
│   ├── pipeline/
│   │   └── full_pipeline.py       # End-to-end orchestrator
│   ├── rag/
│   │   ├── retrieve_jobs.py       # Pinecone job retrieval
│   │   ├── rag_engine.py          # RAG context builder
│   │   └── ingest_jobs.py         # Job ingestion script
│   ├── data/
│   │   └── sample_jobs.json       # 55 job descriptions (Junior to Staff)
│   └── utils/
│       ├── errors.py              # 7 custom exception classes
│       ├── logger.py              # Structured logging
│       ├── rate_limiter.py        # IP-based rate limiter
│       ├── similarity.py          # Cosine similarity scoring
│       └── validators.py          # Input validation + sanitization
├── app/                           # Streamlit app (local dev only, not deployed)
│   └── streamlit_app.py           # Full Streamlit dashboard with auth + history
├── tests/                         # 15 test files, 124 tests
│   ├── test_api.py                # FastAPI endpoint tests
│   ├── test_pipeline.py           # Full pipeline tests
│   ├── test_engine.py             # Skill gap engine tests
│   ├── test_embeddings.py         # Embedding service tests
│   ├── test_evidence.py           # Evidence engine tests
│   ├── test_health.py             # Health check tests
│   ├── test_interview_generator.py
│   ├── test_pipeline.py
│   ├── test_project_generator.py
│   ├── test_rag.py
│   ├── test_rubric.py
│   ├── test_seed_skills.py
│   ├── test_similarity.py
│   ├── test_skill_planner.py
│   ├── test_analytics.py
│   └── test_errors.py
├── docs/
│   └── index.html                 # GitHub Pages landing page
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Dev dependencies (pytest, ruff, mypy, httpx)
├── pyproject.toml                 # Project config (build, ruff, pytest, mypy)
├── Procfile                       # Render deployment: uvicorn api.main:app
├── render.yaml                    # Render service configuration
├── .github/workflows/ci.yml      # GitHub Actions: lint + test + type-check
├── .env.example                   # Environment variable template
└── .gitignore
```

**Stats:** ~60 Python files | ~4,500 lines Python | 9 React components | 124 tests | 55 sample jobs

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for frontend development)
- **Anthropic API key** (required for Claude Sonnet LLM analysis)
- **Pinecone API key** (optional, for semantic job retrieval)
- **Neo4j instance** (optional, for skill prerequisite graph)

---

## Installation

### Backend

```bash
# Clone the repository
git clone https://github.com/RakeshReddy26-bit/skillvector-engine.git
cd skillvector-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt

# Install dev dependencies (for testing/linting)
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo 'NEXT_PUBLIC_API_URL=http://localhost:8000' > .env.local
```

---

## Configuration

Edit `.env` with your settings:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional - RAG (Pinecone)
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=skillvector-jobs
PINECONE_ENVIRONMENT=us-east-1

# Optional - Knowledge Graph (Neo4j)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Model configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2       # Local model, no API needed
LLM_MODEL=claude-sonnet                 # Anthropic Claude Sonnet
LLM_TEMPERATURE=0                      # Deterministic output

# Application settings
LOG_LEVEL=INFO
RATE_LIMIT_PER_HOUR=10
MAX_RESUME_LENGTH=50000
MAX_JOB_DESC_LENGTH=20000
```

The app works without Pinecone and Neo4j. Those features degrade gracefully.

---

## Running Locally

### Start both servers

```bash
# Terminal 1: Backend (FastAPI)
cd skillvector-engine
source venv/bin/activate
uvicorn api.main:app --reload --port 8000

# Terminal 2: Frontend (Next.js)
cd skillvector-engine/frontend
npm run dev
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Health check: `http://localhost:8000/health`

### Quick test

```bash
# Check backend health
curl http://localhost:8000/health

# Analyze (text paste)
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"resume": "5 years Python, ML, TensorFlow...", "target_job": "Senior ML Engineer..."}'

# Upload resume file
curl -X POST http://localhost:8000/upload-resume \
  -F "file=@resume.pdf" \
  -F "target_job=Senior ML Engineer at Stripe"
```

---

## Running Tests

```bash
# Run all 124 tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Run a specific test file
pytest tests/test_pipeline.py -v
pytest tests/test_api.py -v

# Run linter
ruff check src/ tests/ api/

# Run type checker
mypy src/ --ignore-missing-imports
```

All 124 tests pass without any external API keys (all external calls are mocked).

---

## Deployment

### Backend (Render)

The backend is deployed on Render's free tier.

1. Push to GitHub
2. Connect repo on [render.com](https://render.com)
3. Service auto-detects `render.yaml`:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Health check:** `/health`
4. Add environment variables: `ANTHROPIC_API_KEY`, `PINECONE_API_KEY` (optional)

### Frontend (Vercel)

The frontend is deployed on Vercel.

```bash
cd frontend

# Deploy
npx vercel --prod --yes

# Set environment variable
npx vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://api.skill-vector.com
```

Or connect the repo on [vercel.com](https://vercel.com) and set:
- **Root directory:** `frontend`
- **Framework:** Next.js
- **Environment variable:** `NEXT_PUBLIC_API_URL` = `https://api.skill-vector.com`

### CI/CD (GitHub Actions)

Runs on every push to `main` and every PR:

| Job | What it does |
|-----|-------------|
| **lint** | `ruff check` + `ruff format --check` |
| **test** | `pytest` with coverage (needs lint to pass first) |
| **type-check** | `mypy` (needs lint to pass first) |

---

## API Endpoints

### `GET /health`

Returns backend health status with dependency checks.

```json
{
  "status": "healthy",
  "version": "0.2.0",
  "model": "claude-sonnet",
  "anthropic": "ok",
  "neo4j": "unavailable",
  "pinecone": "ok"
}
```

### `POST /analyze`

Analyze resume text against a target job.

**Request:**
```json
{
  "resume": "Full resume text here (min 50 chars)...",
  "target_job": "Target role and job description (min 50 chars)..."
}
```

**Response:**
```json
{
  "match_score": 62.5,
  "learning_priority": "Medium",
  "missing_skills": ["MLOps", "Distributed Systems"],
  "learning_path": [
    {"skill": "MLOps", "estimated_weeks": 4, "estimated_days": 20}
  ],
  "evidence": [
    {"skill": "MLOps", "project": "ML Pipeline Orchestrator", "description": "...", "deliverables": ["..."], "estimated_weeks": 3}
  ],
  "related_jobs": [
    {"score": 0.89, "job_title": "ML Engineer", "company": "Stripe", "skills": ["Python", "MLOps"], "chunk": "..."}
  ],
  "interview_prep": [...],
  "rubrics": [...],
  "request_id": "abc123",
  "latency_ms": 14200
}
```

### `POST /upload-resume`

Upload a resume file for analysis.

**Request:** `multipart/form-data` with `file` and `target_job` fields.

**Supported formats:** PDF, DOCX, TXT, JPG, JPEG, PNG (images use OCR via Tesseract).

### `GET /`

Returns API info and available endpoints.

---

## Frontend Components

| Component | Purpose |
|-----------|---------|
| `UploadZone` | File upload (drag & drop), text paste, target role input, job description textarea |
| `ScoreRing` | Animated SVG ring with color-coded match score, latency display |
| `SkillGapGrid` | 3-column card grid with priority badges (HIGH red, MEDIUM amber, LOW purple) |
| `LearningPath` | Vertical timeline with animated dots, duration badges |
| `EvidencePanel` | 2-column project cards with skill tags, deliverable lists, copy button |
| `RelatedJobs` | Job rows with match %, company, skill chips, hover animations |
| `HealthBanner` | Checks `/health` on load, shows warning if backend is down |
| `Skeleton` | Loading skeleton components for all 4 panels |
| `ErrorBoundary` | React error boundary wrapping each panel |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Uvicorn, Pydantic v2 |
| **LLM** | Claude Sonnet (Anthropic) via LangChain |
| **Embeddings** | Sentence Transformers (`all-MiniLM-L6-v2`, 384-dim) |
| **Similarity** | scikit-learn cosine similarity |
| **Vector DB** | Pinecone (optional, for semantic job matching) |
| **Knowledge Graph** | Neo4j (optional, for skill prerequisites) |
| **Database** | SQLite with WAL journaling |
| **File Parsing** | pdfplumber (PDF), docx2txt (DOCX), pytesseract (images) |
| **Hosting** | Vercel (frontend) + Render (backend) |
| **CI/CD** | GitHub Actions (lint + test + type-check) |
| **Linting** | Ruff |
| **Testing** | pytest (124 tests) |
| **Type Checking** | mypy |

---

## Roadmap

### Completed

- [x] Core skill gap engine (embeddings + LLM)
- [x] Deterministic cosine similarity scoring (0-100%)
- [x] Full analysis pipeline with graceful degradation
- [x] Claude Sonnet integration (migrated from GPT-4o-mini)
- [x] FastAPI backend with /health, /analyze, /upload-resume
- [x] Next.js 14 frontend with 9 React components
- [x] File upload support (PDF, DOCX, TXT, JPG, PNG)
- [x] Drag & drop file upload
- [x] Demo mode with pre-loaded sample data
- [x] Animated results dashboard (5 panels)
- [x] Input validation and IP-based rate limiting
- [x] Custom error hierarchy (7 exception types)
- [x] 55 sample jobs (Junior to Staff level)
- [x] 124 automated tests (all mocked, no API keys needed)
- [x] GitHub Actions CI/CD (lint + test + type-check)
- [x] Vercel + Render deployment
- [x] Interview prep generator (20 skills, 5 Qs each)
- [x] Portfolio project generator with personalization
- [x] Evaluation rubric engine
- [x] Semantic job matching via Pinecone
- [x] Health check with dependency monitoring
- [x] Loading skeletons and error boundaries

### Next Steps

- [ ] Real Neo4j skill prerequisite ordering (currently hardcoded estimates)
- [ ] Pinecone job ingestion pipeline (production seeding)
- [ ] Downloadable PDF reports from analysis results
- [ ] PostgreSQL migration for production scaling
- [ ] Multi-language resume support
- [ ] Resume section extraction (structured parsing)
- [ ] Caching layer for identical analyses
- [ ] User accounts and saved analysis history
- [ ] OAuth login (GitHub, Google)
- [ ] Comparison mode (multiple resumes against one job)

---

## License

MIT

---

Built by [Rakesh Reddy](https://github.com/RakeshReddy26-bit)
