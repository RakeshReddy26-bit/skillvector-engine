<div align="center">

# SkillVector Engine

### AI Career Intelligence Platform

**Deterministic skill gap analysis. Real evidence projects. Prerequisite-ordered learning paths. Geo-localized monetization. Built 100% by one developer.**

[![Live App](https://img.shields.io/badge/Live-skill--vector.com-00e5a0?style=for-the-badge&logo=railway)](https://skill-vector.com)
[![API](https://img.shields.io/badge/API-api.skill--vector.com-blue?style=for-the-badge&logo=fastapi)](https://api.skill-vector.com/health)
[![Tests](https://img.shields.io/badge/Tests-152_passing-success?style=for-the-badge&logo=pytest)](https://github.com/RakeshReddy26-bit/skillvector-engine)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Claude](https://img.shields.io/badge/Claude-Sonnet_4-cc785c?style=for-the-badge&logo=anthropic)](https://anthropic.com)

<br>

**11,000+ lines of code** · **152 automated tests** · **55 indexed jobs** · **32 skills in DAG** · **7-stage pipeline** · **8 languages supported**

[Live Demo](https://skill-vector.com) · [API Docs](https://api.skill-vector.com/health) · [Report Bug](https://github.com/RakeshReddy26-bit/skillvector-engine/issues)

</div>

---

## What Is SkillVector?

SkillVector is a **production SaaS platform** that analyzes your resume against any target job and delivers:

- **Match Score** — Cosine similarity + Claude reasoning (0–100%)
- **Missing Skills** — Priority-ranked gaps with frequency data
- **Learning Path** — Prerequisite-ordered steps with week/day estimates
- **Evidence Projects** — Portfolio-ready project briefs with deliverables
- **Interview Prep** — 5 targeted questions per skill with difficulty levels
- **Evaluation Rubrics** — Weighted criteria (Excellent/Good/Needs Work)
- **Related Jobs** — RAG-powered semantic matches from 55+ real job listings
- **Downloadable PDF** — Pixel-perfect dark-theme A4 scorecard report

Upload a resume (PDF, DOCX, TXT, JPG, PNG), paste a job description, and get your full analysis in under 30 seconds.

---

## Table of Contents

- [What Is SkillVector?](#what-is-skillvector)
- [Features at a Glance](#features-at-a-glance)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Frontend Components](#frontend-components)
- [Monetization Strategy](#monetization-strategy)
- [Version History](#version-history)
- [Roadmap — v4.0 and Beyond](#roadmap--v40-and-beyond)
- [Contributing](#contributing)
- [License](#license)

---

## Features at a Glance

### Core Intelligence

| Feature | Description |
|---------|-------------|
| **7-Stage Analysis Pipeline** | Embeddings → LLM gap analysis → priority ranking → learning path → evidence → interview prep → rubrics |
| **Deterministic Match Score** | Cosine similarity using `all-MiniLM-L6-v2` (384-dim vectors) — same input always = same score |
| **Claude Sonnet Reasoning** | Anthropic Claude identifies nuanced skill gaps a keyword matcher would miss |
| **Prerequisite-Ordered Learning** | Neo4j skill graph ensures you learn fundamentals before advanced topics |
| **RAG Job Matching** | Pinecone vector search finds semantically similar jobs with Claude-scored insights |
| **SQLite Analysis Cache** | SHA-256 content hashing with configurable TTL — instant repeat lookups |
| **Multi-Language Resumes** | Auto-detects 8 languages (DE, FR, ES, IT, PT, NL, PL, EN) and translates via Claude Haiku |
| **Graceful Degradation** | Works without Pinecone/Neo4j — every sub-system fails safely |

### Platform & Monetization

| Feature | Description |
|---------|-------------|
| **Google + GitHub OAuth** | One-click sign-in with secure JWT tokens (72h expiry) |
| **Freemium Model** | 3 free analyses/month, unlimited for Pro subscribers |
| **Stripe Payments** | Checkout sessions, webhooks, customer portal for self-service management |
| **Geo-Localized Pricing** | IP-based country detection → regional pricing for 11+ markets (₹199 India, $9 US, £7 UK, €9 EU) |
| **User Dashboard** | Analysis history, stats cards, delete/download actions |
| **PDF Scorecard** | ReportLab-generated dark-theme A4 report with score ring, skill gaps, learning path, projects |
| **Usage Tracking** | Monthly limits, usage badges, paywall enforcement |
| **Analytics Engine** | Platform-wide metrics: total analyses, score distributions, top skill gaps, daily activity |
| **Agent Automation** | Atlas/Nexus/Scout/Scribe agents for job ingestion, trend updates, social content |

### Developer Quality

| Feature | Description |
|---------|-------------|
| **152 Automated Tests** | All mocked — no API keys needed to run full suite |
| **Type-Safe Frontend** | TypeScript strict mode across 22 files |
| **11,000+ Lines of Code** | 55 Python + 22 TypeScript files |
| **GitHub Actions CI** | Lint (Ruff) → Test (pytest) → Type-check (mypy) on every push |
| **Custom Error Hierarchy** | 7 exception types with structured error responses |
| **Rate Limiting** | IP-based sliding window for anonymous users |

---

## Architecture

```
                    Railway (Frontend)                    Railway (Backend)
               ┌─────────────────────────┐    HTTPS    ┌────────────────────────────┐
               │  Next.js 14 (Standalone) │ ──────────> │  FastAPI + Uvicorn          │
 Users ──────> │  React 18 + TypeScript   │  REST API   │                            │
               │  Tailwind CSS            │             │  ┌──────────────────────┐   │
               │  14 Components           │             │  │ 7-Stage Pipeline     │   │
               │                          │             │  │                      │   │
               │  Cloudflare DNS + CDN    │             │  │  EmbeddingService    │   │
               └─────────────────────────┘             │  │  SkillGapAgent       │   │
                                                       │  │  SkillPlanner        │   │
                                                       │  │  EvidenceEngine      │   │
                ┌─────────────────────┐                │  │  InterviewGenerator  │   │
                │  Stripe Payments    │ <──────────────│  │  RubricEngine        │   │
                │  (checkout/webhooks)│                │  │  RAG JobMatcher      │   │
                └─────────────────────┘                │  └──────────────────────┘   │
                                                       │                            │
                ┌─────────────────────┐                │  SQLite (cache + analytics) │
                │  Google OAuth 2.0   │ <──────────────│  Pinecone (vector search)   │
                │  GitHub OAuth       │                │  Neo4j (skill graph)        │
                └─────────────────────┘                │  Claude Sonnet (LLM)        │
                                                       │  Claude Haiku (translate)   │
                                                       └────────────────────────────┘
```

### Data Flow

```
Resume (PDF/DOCX/TXT/Image) ──> Parse ──> Cache Check ──> Language Detect
                                                              │
                                    ┌─────────────────────────┘
                                    ▼
                              Translate (if needed)
                                    │
                                    ▼
                    Embed (all-MiniLM-L6-v2, 384-dim)
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Cosine Score    Claude Analysis    Pinecone RAG
              (deterministic)  (skill gaps)     (job matches)
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                    ┌──── Priority Ranking ────┐
                    │                          │
                    ▼                          ▼
             Learning Path              Evidence Projects
             (Neo4j ordering)           (portfolio briefs)
                    │                          │
                    ▼                          ▼
             Interview Prep              Rubric Engine
             (5 Qs per skill)           (weighted criteria)
                    │                          │
                    └──────────┬───────────────┘
                               ▼
                    Cache Save ──> JSON Response ──> Frontend Render
                                                         │
                                                         ▼
                                                    PDF Report (optional)
```

---

## How It Works

### 1. Upload Screen

- Drag & drop resume file (PDF, DOCX, TXT, JPG, PNG — 10MB limit)
- Or paste resume text directly
- Paste target job description (optional, improves accuracy)
- Enter target role (e.g., "Senior ML Engineer at Stripe")
- Click **ANALYZE MY RESUME** or **TRY DEMO**

### 2. Results Dashboard (5 Panels)

| Panel | What You See |
|-------|-------------|
| **01 Intelligence Score** | Animated SVG ring (green >70%, amber >40%, red <40%), latency badge, request ID |
| **02 Skill Gap Matrix** | Priority-colored cards (HIGH red, MEDIUM amber, LOW purple), frequency badges |
| **03 Learning Path** | Numbered timeline with prerequisite ordering, week/day duration badges |
| **04 Evidence Builder** | Portfolio project cards with skill tags, deliverable lists, "Copy Brief" button |
| **05 Related Jobs** | RAG matches with score, company, salary, location, "why match/gap" insights, apply links |

### 3. Additional Screens

- **Dashboard** — View all past analyses, stats (avg score, improvement trend, most common gap), delete/download
- **Profile** — Plan tier, usage bar, upgrade CTA with geo-priced amounts, analysis history
- **PDF Report** — Downloadable dark-theme A4 scorecard with everything from the analysis

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript | Production SPA with standalone output |
| **Styling** | Tailwind CSS, custom dark theme | Responsive UI with glassmorphism effects |
| **Backend** | FastAPI, Uvicorn, Pydantic v2 | REST API with async support |
| **LLM** | Claude Sonnet 4 (Anthropic) via LangChain | Skill gap analysis, job scoring |
| **Translation** | Claude Haiku (Anthropic) | Fast/cheap language detection & translation |
| **Embeddings** | Sentence Transformers (`all-MiniLM-L6-v2`) | 384-dim vectors, runs locally |
| **Vector DB** | Pinecone | Semantic job matching (55+ indexed jobs) |
| **Graph DB** | Neo4j Aura | Skill prerequisite relationships (32 skills, 25+ edges) |
| **Cache** | SQLite with WAL | SHA-256 content-hashed analysis cache |
| **Auth** | JWT (HS256, 72h), Google/GitHub OAuth | Secure user sessions |
| **Payments** | Stripe (Checkout, Webhooks, Portal) | SaaS subscriptions with geo pricing |
| **File Parsing** | pdfplumber, docx2txt, pytesseract (OCR) | Resume extraction from any format |
| **PDF Reports** | ReportLab canvas | Pixel-perfect dark-theme A4 scorecards |
| **Hosting** | Railway (frontend + backend) | Production deployment with auto-deploy |
| **DNS/CDN** | Cloudflare | HTTPS, caching, DDoS protection |
| **CI/CD** | GitHub Actions | Lint (Ruff) + Test (pytest) + Type-check (mypy) |
| **Testing** | pytest, 152 tests | Full coverage, all external calls mocked |

---

## Project Structure

```
skillvector-engine/
├── api/                                # FastAPI backend
│   ├── main.py                         # App entry: CORS, routers, /health, /analyze, /upload-resume
│   ├── auth.py                         # Google/GitHub OAuth, JWT, login/register, usage tracking
│   ├── dashboard.py                    # User dashboard: history, stats, delete
│   ├── stripe_routes.py                # Stripe checkout, webhooks, customer portal
│   ├── middleware.py                   # Request middleware (logging, timing)
│   └── models.py                       # Pydantic request/response schemas
│
├── src/                                # Core Python engine (55 files)
│   ├── config.py                       # Centralized settings from env vars
│   ├── health.py                       # Health check aggregator
│   ├── analytics/
│   │   ├── tracker.py                  # Platform analytics (scores, skills, activity)
│   │   └── daily_stats.py              # Daily metric computation
│   ├── auth/
│   │   └── auth_service.py             # PBKDF2 password hashing
│   ├── cache/
│   │   └── analysis_cache.py           # SQLite cache with SHA-256 keys, TTL, hit tracking
│   ├── db/
│   │   ├── database.py                 # SQLite connection + schema (WAL mode)
│   │   └── models.py                   # UserRepo, AnalysisRepo, FeedbackRepo, EventRepo
│   ├── embeddings/
│   │   └── embedding_service.py        # SentenceTransformer wrapper (all-MiniLM-L6-v2)
│   ├── engine/
│   │   └── skill_gap_engine.py         # Core: embeddings + LLM + cosine scoring
│   ├── evidence/
│   │   ├── evidence_engine.py          # Portfolio project template mapping
│   │   ├── interview_generator.py      # LLM + fallback curated questions (20 skills)
│   │   ├── project_generator.py        # Extensive project catalog by skill & difficulty
│   │   ├── project_templates.py        # Template data for project generation
│   │   └── rubric.py                   # Weighted evaluation criteria engine
│   ├── graph/
│   │   ├── skill_planner.py            # Learning path ordering + time estimates
│   │   ├── neo4j_client.py             # Neo4j connection manager
│   │   └── seed_skills.py              # Skill graph seeding (32 skills, 25+ edges)
│   ├── jobs/                           # Job processing utilities
│   ├── language/
│   │   └── translator.py              # Multi-language detection + Claude Haiku translation
│   ├── llm/
│   │   ├── gap_agent.py                # Claude Sonnet skill gap agent
│   │   └── rag_prompt.py               # RAG-enhanced prompt builder
│   ├── pipeline/
│   │   └── full_pipeline.py            # 7-stage orchestrator with cache integration
│   ├── rag/
│   │   ├── rag_engine.py               # RAG context builder
│   │   ├── retrieve_jobs.py            # Pinecone job retrieval + Claude scoring
│   │   └── ingest_jobs.py              # Job ingestion script
│   ├── reports/
│   │   └── pdf_generator.py            # ReportLab dark-theme A4 PDF scorecards
│   ├── routes/
│   │   └── automation.py               # Atlas agent endpoints (ingest, trends, insights)
│   ├── skills/                         # Skill data and utilities
│   ├── data/
│   │   └── sample_jobs.json            # 55 real job descriptions (Junior → Staff)
│   └── utils/
│       ├── errors.py                   # 7 custom exception classes
│       ├── logger.py                   # Structured logging
│       ├── rate_limiter.py             # IP-based sliding window rate limiter
│       ├── similarity.py               # Cosine similarity scoring
│       └── validators.py               # Input validation + sanitization
│
├── frontend/                           # Next.js 14 frontend (22 TS/TSX files)
│   ├── app/
│   │   ├── layout.tsx                  # Root layout with AuthProvider, metadata, og:tags
│   │   ├── page.tsx                    # Home page: upload + 5 result panels + modals
│   │   ├── globals.css                 # Tailwind + dark theme + glassmorphism
│   │   └── sitemap.ts                  # Dynamic XML sitemap for SEO
│   ├── components/
│   │   ├── AuthModal.tsx               # Sign In / Register tabs, Google + GitHub OAuth
│   │   ├── Dashboard.tsx               # Full-screen: stats cards, history list, actions
│   │   ├── ErrorBoundary.tsx           # Panel error isolation with retry
│   │   ├── EvidencePanel.tsx           # Project cards with deliverables + copy
│   │   ├── HealthBanner.tsx            # Sticky nav: health, model, auth, version badge
│   │   ├── LearningPath.tsx            # Numbered timeline with duration badges
│   │   ├── PaywallModal.tsx            # Upgrade prompt with geo pricing + billing toggle
│   │   ├── ProfilePanel.tsx            # Profile + plan + usage bar + history
│   │   ├── RelatedJobs.tsx             # RAG job cards with rich metadata
│   │   ├── ScoreRing.tsx               # Animated SVG ring with glow
│   │   ├── Skeleton.tsx                # Loading skeletons for all panels
│   │   ├── SkillGapGrid.tsx            # Priority-colored skill cards
│   │   ├── UploadZone.tsx              # Drag & drop + paste + role input
│   │   └── UsageBadge.tsx              # PRO badge or X/Y usage indicator
│   ├── lib/
│   │   ├── api.ts                      # API client: analyze, upload, auth, dashboard
│   │   ├── auth-context.tsx            # React context: JWT, OAuth callback, persistence
│   │   ├── demo-data.ts               # Pre-built demo result for instant preview
│   │   ├── types.ts                    # TypeScript interfaces (API + Display)
│   │   └── use-geo-price.ts            # IP → country → regional pricing hook
│   ├── railway.json                    # Railway frontend deployment config
│   ├── .env.production                 # Production API URL + Google Client ID
│   └── package.json                    # Dependencies + standalone build script
│
├── tests/                              # 20 test files, 152 tests
│   ├── conftest.py                     # Shared fixtures
│   ├── test_analytics.py              # Analytics engine tests
│   ├── test_api.py                     # FastAPI endpoint tests
│   ├── test_auth.py                    # Auth flow tests
│   ├── test_embeddings.py             # Embedding service tests
│   ├── test_engine.py                 # Skill gap engine tests
│   ├── test_errors.py                 # Custom exception tests
│   ├── test_evidence.py               # Evidence engine tests
│   ├── test_health.py                 # Health check tests
│   ├── test_interview_generator.py    # Interview question tests
│   ├── test_pipeline.py               # Full pipeline tests
│   ├── test_project_generator.py      # Project generator tests
│   ├── test_rag.py                    # RAG retrieval tests
│   ├── test_rubric.py                 # Rubric engine tests
│   ├── test_seed_skills.py            # Skill graph tests
│   ├── test_similarity.py             # Cosine similarity tests
│   ├── test_skill_planner.py          # Learning path planner tests
│   ├── test_stripe.py                 # Stripe integration tests
│   └── test_usage.py                  # Usage limit tests
│
├── railway.json                        # Railway backend deployment config
├── Procfile                            # Process definition (uvicorn)
├── requirements.txt                    # Production Python dependencies (40 packages)
├── requirements-dev.txt                # Dev dependencies (pytest, ruff, mypy)
├── pyproject.toml                      # Build/tool config
└── runtime.txt                         # Python 3.11
```

**Stats:** 55 Python files · 22 TypeScript files · 11,000+ total lines · 152 tests · 40 dependencies

---

## Getting Started

### Prerequisites

| Requirement | Purpose | Required? |
|------------|---------|-----------|
| Python 3.11+ | Backend runtime | Yes |
| Node.js 18+ | Frontend dev server | Yes |
| Anthropic API key | Claude Sonnet LLM | Yes |
| Pinecone API key | Semantic job matching | Optional |
| Neo4j instance | Skill prerequisite graph | Optional |
| Stripe keys | Payment processing | Optional |
| Google OAuth credentials | Social sign-in | Optional |

### Installation

```bash
# Clone
git clone https://github.com/RakeshReddy26-bit/skillvector-engine.git
cd skillvector-engine

# Backend setup
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing/linting

# Copy environment template and add your keys
cp .env.example .env

# Frontend setup
cd frontend
npm install
echo 'NEXT_PUBLIC_API_URL=http://127.0.0.1:8000' > .env.local
```

---

## Configuration

### Required Environment Variables

```bash
# .env (backend)
ANTHROPIC_API_KEY=sk-ant-your-key-here    # Required — powers all analysis
JWT_SECRET=your-random-256-bit-hex        # Required — for user auth tokens
```

### Optional Environment Variables

```bash
# Vector search (RAG job matching)
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=skillvector-jobs
PINECONE_ENVIRONMENT=us-east-1

# Skill graph (prerequisite ordering)
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=your-user
NEO4J_PASSWORD=your-password

# Stripe payments
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/auth/callback/google

# App settings
LLM_MODEL=claude-sonnet-4-20250514
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_TEMPERATURE=0
LOG_LEVEL=INFO
RATE_LIMIT_PER_HOUR=10
FRONTEND_URL=http://localhost:3000
API_URL=http://127.0.0.1:8000
CACHE_TTL_HOURS=24
```

The app **works without Pinecone, Neo4j, Stripe, and OAuth** — all features degrade gracefully.

---

## Running Locally

```bash
# Terminal 1: Backend
cd skillvector-engine
source .venv/bin/activate
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd skillvector-engine/frontend
npm run dev
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend | http://127.0.0.1:8000 |
| Health | http://127.0.0.1:8000/health |
| API Docs | http://127.0.0.1:8000/docs |

### Quick Test

```bash
# Health check
curl http://127.0.0.1:8000/health

# Analyze via text
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"resume": "5 years Python, ML, TensorFlow, Docker...", "target_job": "Senior ML Engineer at Stripe..."}'

# Upload resume file
curl -X POST http://127.0.0.1:8000/upload-resume \
  -F "file=@resume.pdf" \
  -F "target_job=Senior ML Engineer at Stripe"
```

---

## Running Tests

```bash
# Run all 152 tests (no API keys needed — all mocked)
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=src --cov-report=term-missing

# Specific test file
pytest tests/test_pipeline.py -v

# Linting
ruff check src/ tests/ api/

# Type checking
mypy src/ --ignore-missing-imports
```

---

## Deployment

### Production Setup (Railway — Current)

Both frontend and backend are deployed on **Railway** with auto-deploy from GitHub.

#### Backend Service

| Setting | Value |
|---------|-------|
| Root Directory | `/` (repo root) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| Custom Domain | `api.skill-vector.com` |
| Health Check | `/health` |

#### Frontend Service

| Setting | Value |
|---------|-------|
| Root Directory | `/frontend` |
| Build Command | `npm run build` (standalone output + static copy) |
| Start Command | `HOSTNAME=0.0.0.0 node .next/standalone/server.js` |
| Custom Domain | `skill-vector.com` |

#### DNS (Cloudflare)

| Record | Type | Name | Target |
|--------|------|------|--------|
| Frontend | CNAME | `@` | `c53tuyif.up.railway.app` |
| Backend | CNAME | `api` | `u81ml99u.up.railway.app` |

#### Required Environment Variables (Railway Dashboard)

**Backend service:**
```
ANTHROPIC_API_KEY, JWT_SECRET, PINECONE_API_KEY, PINECONE_INDEX_NAME,
NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GOOGLE_CLIENT_ID,
GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, STRIPE_SECRET_KEY,
STRIPE_WEBHOOK_SECRET, STRIPE_PRICE_ID, FRONTEND_URL, API_URL, LLM_MODEL
```

**Frontend service:** Uses `.env.production` committed to repo (no Railway env vars needed).

---

## API Reference

### Core Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | System health + dependency status |
| `POST` | `/analyze` | Optional | Full skill gap analysis (text input) |
| `POST` | `/upload-resume` | Optional | Upload file + analyze (PDF/DOCX/TXT/JPG/PNG) |

### Auth Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/register` | Create account (email + password) |
| `POST` | `/auth/login` | Sign in (returns JWT) |
| `GET` | `/auth/google` | Start Google OAuth flow |
| `GET` | `/auth/github` | Start GitHub OAuth flow |
| `GET` | `/auth/callback/google` | Google OAuth callback |
| `GET` | `/auth/callback/github` | GitHub OAuth callback |
| `GET` | `/auth/me` | Current user info + plan tier |
| `GET` | `/auth/usage` | Monthly usage count + reset date |
| `GET` | `/auth/history` | Last 20 analyses for user |

### Dashboard Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/dashboard/history` | Yes | Analysis history with plan info |
| `GET` | `/dashboard/stats` | Yes | Stats: avg score, improvement, top gap |
| `DELETE` | `/dashboard/history/{id}` | Yes | Delete specific analysis |

### Payment Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/stripe/create-checkout` | Create Stripe Checkout Session |
| `POST` | `/stripe/webhook` | Handle Stripe events (activate/downgrade) |
| `GET` | `/stripe/portal` | Redirect to Stripe Customer Portal |

### Automation Endpoints (API-key protected)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/automation/ingest-jobs` | Atlas agent: ingest job listings → Pinecone |
| `POST` | `/automation/trend-update` | Scout agent: update skill trend weights |
| `GET` | `/automation/daily-insight` | Scribe agent: daily stats for social posts |

### Report Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/reports/generate` | Generate downloadable PDF scorecard |

### Example Response (`POST /analyze`)

```json
{
  "match_score": 62.5,
  "learning_priority": "Medium",
  "missing_skills": ["MLOps", "Distributed Systems", "Kubernetes"],
  "learning_path": [
    {"skill": "Docker", "estimated_weeks": 2, "estimated_days": 10},
    {"skill": "Kubernetes", "estimated_weeks": 4, "estimated_days": 20},
    {"skill": "MLOps", "estimated_weeks": 6, "estimated_days": 30}
  ],
  "evidence": [
    {
      "skill": "MLOps",
      "project": "ML Pipeline Orchestrator",
      "description": "Build an end-to-end ML pipeline...",
      "deliverables": ["CI/CD pipeline config", "Model registry", "Monitoring dashboard"],
      "estimated_weeks": 3
    }
  ],
  "related_jobs": [
    {
      "score": 0.89,
      "job_title": "ML Engineer",
      "company": "Stripe",
      "match_score": 89,
      "skills": ["Python", "MLOps", "TensorFlow"],
      "why_match": "Strong Python and ML foundations",
      "why_gap": "Missing production MLOps experience",
      "salary": "$180k–$250k",
      "location": "San Francisco, CA",
      "apply_url": "https://stripe.com/jobs/..."
    }
  ],
  "interview_prep": ["..."],
  "rubrics": ["..."],
  "request_id": "abc-123-def",
  "latency_ms": 14200,
  "detected_language": "en",
  "was_translated": false
}
```

---

## Frontend Components

| Component | Purpose |
|-----------|---------|
| `UploadZone` | Drag & drop, file picker, text paste, target role input, validation |
| `ScoreRing` | Animated SVG ring, color-coded (green/amber/red), glow effect, latency |
| `SkillGapGrid` | Priority cards (HIGH/MEDIUM/LOW), color borders, frequency badges |
| `LearningPath` | Numbered timeline, prerequisite ordering, duration badges |
| `EvidencePanel` | Project cards, skill tags, deliverable lists, copy-to-clipboard |
| `RelatedJobs` | Rich job cards with match insights, salary, location, apply links |
| `Dashboard` | Stats cards, history list with score rings, download PDF, delete |
| `ProfilePanel` | Avatar, plan badge, usage bar, geo-priced upgrade CTA |
| `PaywallModal` | Monthly/yearly toggle, geo pricing, Pro feature list, Stripe redirect |
| `AuthModal` | Sign In/Register tabs, Google + GitHub OAuth, email/password |
| `UsageBadge` | Compact "PRO" or "2/3 USED" indicator in nav |
| `HealthBanner` | Sticky nav, API health status, model name, version badge |
| `ErrorBoundary` | Panel error isolation with "Try Again" recovery |
| `Skeleton` | Loading states for score ring, grid, and sections |

---

## Monetization Strategy

### Current Revenue Model

```
┌─────────────────────────────────────────────────────┐
│                  FREEMIUM MODEL                      │
├─────────────────────┬───────────────────────────────┤
│  FREE TIER          │  PRO TIER                     │
│  3 analyses/month   │  Unlimited analyses           │
│  Basic results      │  PDF scorecard downloads      │
│  No history         │  Full dashboard + history     │
│                     │  Priority API access           │
│  $0/month           │  $3–$9/month (geo-priced)     │
└─────────────────────┴───────────────────────────────┘
```

### Geo-Localized Pricing

Prices automatically adjust based on user location:

| Region | Monthly | Yearly |
|--------|---------|--------|
| India | ₹199 | ₹1,599 |
| United States | $9 | $79 |
| United Kingdom | £7 | £59 |
| EU (Germany, France, Netherlands, etc.) | €9 | €79 |
| Brazil | $5 | $39 |
| Nigeria / Pakistan / Bangladesh | $3 | $25 |
| Philippines | $4 | $35 |
| Rest of World | $9 | $79 |

### Future Revenue Opportunities

| Opportunity | Description | Est. Revenue |
|-------------|-------------|-------------|
| **B2B API Access** | Companies pay per-analysis for bulk resume screening | $0.50–$2.00/analysis |
| **Enterprise Tier** | White-label for recruitment agencies, custom branding | $99–$499/mo |
| **University Partnerships** | Career services integration for students | $5k–$20k/year |
| **Resume Writing Upsell** | AI-powered resume rewriting based on gap analysis | $19–$49 one-time |
| **Interview Coaching** | Live mock interviews based on generated questions | $29–$79/session |
| **Certification Prep** | Partner with Coursera/Udemy for affiliate revenue | 20–40% commission |
| **Job Board Integration** | "Apply Now" affiliate links to matched jobs | $1–$5 CPC |
| **Recruiter Tools** | Bulk candidate screening, team skill gap matrices | $199–$999/mo |
| **Premium Templates** | Curated project templates with step-by-step guides | $9–$19 per pack |
| **Analytics Reports** | Market skill trend reports for companies | $49–$199/mo |

### Revenue Projections

| Stage | Users | Conversion | MRR |
|-------|-------|-----------|-----|
| Launch (Month 1–3) | 500 free | 2% → 10 Pro | $50–$90 |
| Growth (Month 4–6) | 2,000 free | 3% → 60 Pro | $300–$540 |
| Scale (Month 7–12) | 10,000 free | 4% → 400 Pro | $2,000–$3,600 |
| B2B Launch (Year 2) | + 5 enterprise clients | — | +$2,500–$10,000 |

---

## Version History

### v3.2.0 — Current (March 2026)

- Railway deployment (frontend + backend on paid tier)
- SQLite analysis cache with SHA-256 hashing, TTL, hit tracking
- Multi-language resume support (8 languages, Claude Haiku translation)
- User dashboard with stats, history, delete
- Production DNS fix (.env.local override removed)
- Cloudflare DNS + Railway custom domains configured
- 152 automated tests

### v3.1.0

- Google + GitHub OAuth integration
- Stripe payment integration with geo-localized pricing
- PDF scorecard generation (ReportLab dark theme)
- Usage tracking and paywall enforcement
- Analytics engine (platform-wide metrics)
- Agent automation endpoints (Atlas/Nexus/Scout/Scribe)

### v3.0.0

- Complete Next.js 14 frontend rewrite (14 components)
- FastAPI backend with full REST API
- Auth system (JWT + OAuth)
- Dashboard and profile panels
- Production deployment

### v2.0.0

- Claude Sonnet migration (from GPT-4o-mini)
- RAG job matching via Pinecone
- Neo4j skill prerequisite graph
- Interview prep generator
- Evaluation rubric engine
- 124 automated tests

### v1.0.0

- Core skill gap analysis engine
- Cosine similarity scoring
- Basic learning path generation
- Streamlit frontend (local dev only)
- 55 sample job descriptions

---

## Roadmap — v4.0 and Beyond

### v4.0 — Intelligence Upgrade (Q2 2026)

- [ ] **Real-time job scraping** — Live job feeds from LinkedIn/Indeed/Greenhouse APIs
- [ ] **Team skill matrix** — Upload multiple resumes, see team-wide gaps
- [ ] **Resume rewriting** — AI rewrites resume sections to close identified gaps
- [ ] **Comparison mode** — Analyze same resume against multiple roles side-by-side
- [ ] **Skill progress tracking** — Re-analyze periodically, show improvement over time
- [ ] **PostgreSQL migration** — Replace SQLite for production-grade scaling

### v4.1 — Marketplace (Q3 2026)

- [ ] **Course recommendations** — Partner with Coursera/Udemy for targeted learning links
- [ ] **Project marketplace** — Community-submitted evidence projects with ratings
- [ ] **Mentor matching** — Connect users with mentors in their target skill areas
- [ ] **Chrome extension** — Analyze any job posting directly from LinkedIn/Indeed

### v5.0 — Enterprise (Q4 2026)

- [ ] **B2B API** — Pay-per-analysis for recruitment platforms
- [ ] **White-label** — Custom branding for recruitment agencies
- [ ] **Bulk screening** — Upload 100+ resumes against one job description
- [ ] **ATS integration** — Greenhouse, Lever, Workday connectors
- [ ] **Compliance reports** — Skills-based hiring audit trails
- [ ] **SSO / SAML** — Enterprise single sign-on

### v5.1 — AI Agents (2027)

- [ ] **Career coach agent** — Ongoing AI mentor that tracks progress and suggests next steps
- [ ] **Interview simulator** — Voice-based mock interviews using generated questions
- [ ] **Networking assistant** — Identifies people to connect with based on skill gaps
- [ ] **Auto-apply** — Automated job applications with tailored cover letters

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all 152 tests pass (`pytest tests/ -v`)
5. Run linting (`ruff check src/ tests/ api/`)
6. Commit with descriptive messages (`git commit -m 'feat: add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## License

MIT License — See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built by [Rakesh Reddy](https://github.com/RakeshReddy26-bit)**

SkillVector v3.2.0 · Powered by Claude Sonnet · Open Source · 11,000+ lines · 152 tests

[Live App](https://skill-vector.com) · [API](https://api.skill-vector.com/health) · [GitHub](https://github.com/RakeshReddy26-bit/skillvector-engine)

</div>
