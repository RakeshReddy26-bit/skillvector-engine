# SkillVector Engine

AI-powered career skill gap analysis platform. Paste a resume and a job description, get a match score, missing skills, learning path, interview prep, portfolio project ideas, and evaluation rubrics.

Built with Python, Streamlit, LangChain, Sentence Transformers, Pinecone, and Neo4j.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Running Tests](#running-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment (Streamlit Cloud)](#deployment-streamlit-cloud)
- [Usage Guide](#usage-guide)
- [Admin Dashboard](#admin-dashboard)
- [API Reference (Internal Modules)](#api-reference-internal-modules)
- [Tech Stack](#tech-stack)
- [Roadmap](#roadmap)

---

## Features

| Feature | Description |
|---------|-------------|
| **Skill Gap Analysis** | Cosine similarity + LLM reasoning to identify missing skills |
| **Match Score** | Deterministic 0-100% score using semantic embeddings |
| **Learning Path** | Ordered skill-building steps with time estimates |
| **Interview Prep** | 5 curated interview questions per missing skill with difficulty levels |
| **Portfolio Projects** | Personalized project ideas with deliverables and rubrics |
| **Evaluation Rubrics** | Weighted criteria (Excellent/Good/Needs Work) for self-assessment |
| **User Accounts** | Registration, login, password hashing (PBKDF2) |
| **Analysis History** | Saved results per user with full history |
| **Feedback System** | Thumbs up/down + text feedback on results |
| **Admin Dashboard** | Platform metrics, score distribution, top missing skills |
| **PDF Upload** | Upload resume as PDF or paste text |
| **Rate Limiting** | Session-based sliding window (configurable) |
| **RAG (Optional)** | Semantic job retrieval via Pinecone vector database |
| **Knowledge Graph (Optional)** | Skill prerequisites via Neo4j |
| **Graceful Degradation** | App works without Pinecone/Neo4j (falls back to local data) |

---

## Architecture

```
Resume + Job Description
        |
        v
+------------------+
| SkillGapEngine   |  Embedding similarity + LLM analysis
+------------------+
        |
        v
+------------------+
| SkillPlanner     |  Orders skills into learning path
+------------------+
        |
        v
+------------------+     +----------------------+     +---------------+
| EvidenceEngine   | --> | InterviewGenerator   | --> | RubricEngine  |
| (project ideas)  |     | (interview Qs)       |     | (eval rubrics)|
+------------------+     +----------------------+     +---------------+
        |
        v
+------------------+
| SkillVector      |  Full pipeline orchestrator
| Pipeline         |  (graceful degradation at each step)
+------------------+
        |
        v
+------------------+
| Streamlit UI     |  Web interface + auth + history + admin
+------------------+
```

**Data flow:**
1. `EmbeddingService` encodes resume + job using `all-MiniLM-L6-v2` (384-dim vectors)
2. `cosine_similarity` produces deterministic match score (0-100%)
3. `SkillGapAgent` (GPT-4o-mini via LangChain) identifies missing skills
4. `SkillPlanner` orders skills with time estimates
5. `EvidenceEngine` maps skills to portfolio projects
6. `InterviewGenerator` generates 5 interview questions per skill
7. `RubricEngine` produces weighted evaluation criteria
8. Results saved to SQLite (if logged in), displayed in Streamlit

---

## Project Structure

```
skillvector-engine/
|-- .github/workflows/ci.yml      # GitHub Actions CI pipeline
|-- .streamlit/
|   |-- config.toml                # Streamlit theme/server config
|   `-- secrets.toml.example       # Template for Streamlit Cloud secrets
|-- app/
|   `-- streamlit_app.py           # Main Streamlit application (~580 lines)
|-- src/
|   |-- config.py                  # Centralized configuration
|   |-- analytics/tracker.py       # Platform analytics engine
|   |-- auth/auth_service.py       # PBKDF2 password hashing + validation
|   |-- db/
|   |   |-- database.py            # SQLite connection + schema init
|   |   `-- models.py              # UserRepo, AnalysisRepo, FeedbackRepo, EventRepo
|   |-- embeddings/
|   |   `-- embedding_service.py   # SentenceTransformer wrapper
|   |-- engine/
|   |   `-- skill_gap_engine.py    # Core analysis: embeddings + LLM + scoring
|   |-- evidence/
|   |   |-- evidence_engine.py     # Portfolio project templates
|   |   |-- interview_generator.py # Interview Q generator (20 skills, LLM optional)
|   |   |-- project_generator.py   # Personalized project catalog
|   |   `-- rubric.py              # Evaluation rubric engine
|   |-- graph/
|   |   |-- skill_planner.py       # Learning path ordering + time estimates
|   |   |-- neo4j_client.py        # Neo4j connection
|   |   `-- seed_skills.py         # Graph seeding script
|   |-- llm/
|   |   |-- gap_agent.py           # GPT-4o-mini skill gap agent
|   |   `-- rag_prompt.py          # RAG-enhanced prompt builder
|   |-- pipeline/
|   |   `-- full_pipeline.py       # End-to-end orchestrator
|   |-- rag/
|   |   |-- retrieve_jobs.py       # Pinecone job retrieval
|   |   |-- rag_engine.py          # RAG context builder
|   |   `-- ingest_jobs.py         # Pinecone job ingestion script
|   |-- data/
|   |   `-- sample_jobs.json       # 55 job descriptions (Junior to Staff)
|   `-- utils/
|       |-- errors.py              # 7 custom exception classes
|       |-- logger.py              # Structured logging utility
|       |-- rate_limiter.py        # Session-based rate limiter
|       |-- similarity.py          # Cosine similarity scoring
|       `-- validators.py          # Input validation + sanitization
|-- tests/                         # 12 test files, 79 tests
|-- requirements.txt               # Production dependencies
|-- requirements-dev.txt           # Dev dependencies (pytest, ruff, mypy)
|-- pyproject.toml                 # Project config (build, ruff, pytest, mypy)
|-- .pre-commit-config.yaml        # Linting hooks (ruff)
|-- .env.example                   # Environment variable template
`-- .gitignore
```

**Stats:** 56 Python files | ~3,990 lines of code | 79 tests | 55 sample jobs

---

## Prerequisites

- **Python 3.11+**
- **OpenAI API key** (required for LLM analysis)
- **Pinecone API key** (optional, for RAG job retrieval)
- **Neo4j instance** (optional, for skill prerequisite graph)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/kalamakuntlarakeshreddy/skillvector-engine.git
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

---

## Configuration

Edit `.env` with your settings:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

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
LLM_MODEL=gpt-4o-mini                  # OpenAI model
LLM_TEMPERATURE=0                      # Deterministic output

# Application settings
LOG_LEVEL=INFO
RATE_LIMIT_PER_HOUR=10
MAX_RESUME_LENGTH=50000
MAX_JOB_DESC_LENGTH=20000
ADMIN_EMAIL=admin@example.com           # Email for admin dashboard access
```

**Note:** The app works without Pinecone and Neo4j. Those features degrade gracefully.

---

## Running the App

```bash
streamlit run app/streamlit_app.py
```

Opens at `http://localhost:8501`. The first load takes a few seconds while the embedding model (all-MiniLM-L6-v2) downloads and caches.

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Run a specific test file
pytest tests/test_pipeline.py -v

# Run linter
ruff check src/ tests/ app/

# Run formatter
ruff format src/ tests/ app/

# Run type checker
mypy src/ --ignore-missing-imports
```

All 79 tests should pass without any external API keys (all external calls are mocked).

---

## CI/CD Pipeline

GitHub Actions runs on every push to `main` and every PR:

| Job | What it does |
|-----|-------------|
| **lint** | `ruff check` + `ruff format --check` |
| **test** | `pytest` with coverage (needs lint to pass first) |
| **type-check** | `mypy` (needs lint to pass first) |

Configuration: `.github/workflows/ci.yml`

---

## Deployment (Streamlit Cloud)

1. Push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `app/streamlit_app.py`
5. Add secrets in the Streamlit Cloud dashboard:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY` (optional)
   - Other keys from `.streamlit/secrets.toml.example`
6. Deploy

The app auto-detects Streamlit Cloud secrets via `st.secrets` fallback in `src/config.py`.

---

## Usage Guide

### 1. Analyze Skill Gap

1. Open the app
2. Paste your resume text (or upload a PDF)
3. Paste the target job description
4. Click **Analyze Skill Gap**

Or click **Load sample data** to try with pre-filled examples.

### 2. Read Your Results

The analysis returns:

- **Match Score** (0-100%) - How well your resume matches the job
- **Learning Priority** (Low/Medium/High) - Deterministic based on score
- **Missing Skills** - Skills you need to develop
- **Learning Path** - Ordered steps with time estimates
- **Portfolio Project Ideas** - Concrete projects to build
- **Interview Preparation** - 5 questions per skill with difficulty and tips
- **Evaluation Rubrics** - Self-assessment criteria for your projects

### 3. Create an Account

Register via the sidebar to:
- Save analysis results
- View analysis history
- Provide feedback

### 4. Give Feedback

After each analysis, rate the results (thumbs up/down + optional text). This data drives platform improvements.

---

## Admin Dashboard

Accessible only to the email set in `ADMIN_EMAIL` env var. Shows:

- **Platform Overview** - Total analyses, registrations, logins
- **Feedback Summary** - Positive/negative ratio, satisfaction rate
- **Score Distribution** - How users are matching (low/medium/high)
- **Top Missing Skills** - Most commonly missing skills across all analyses
- **Daily Activity** - Event counts over last 30 days
- **Recent Feedback** - Latest user feedback with comments

---

## API Reference (Internal Modules)

### SkillVectorPipeline

```python
from src.pipeline.full_pipeline import SkillVectorPipeline

pipeline = SkillVectorPipeline()
result = pipeline.run(resume_text, job_description)

# result keys:
# - match_score: float (0-100)
# - learning_priority: str ("Low" | "Medium" | "High")
# - missing_skills: list[str]
# - learning_path: list[dict] (skill, estimated_weeks, estimated_days)
# - evidence: list[dict] (skill, project, deliverables, estimated_weeks)
# - interview_prep: list[dict] (skill, questions, difficulty, tips)
# - rubrics: list[dict] (skill, criteria, scoring, total_points)
```

### InterviewGenerator

```python
from src.evidence.interview_generator import InterviewGenerator

gen = InterviewGenerator(use_llm=False)  # or True for LLM-generated Qs
questions = gen.generate(
    missing_skills=["Docker", "Kubernetes"],
    questions_per_skill=5,
)
```

### ProjectGenerator

```python
from src.evidence.project_generator import ProjectGenerator

gen = ProjectGenerator()
projects = gen.generate(
    missing_skills=["Docker", "CI/CD"],
    existing_skills=["Python", "Git"],
    max_projects_per_skill=2,
)
roadmap = gen.get_roadmap(missing_skills=["Docker", "CI/CD"])
```

### RubricEngine

```python
from src.evidence.rubric import RubricEngine

engine = RubricEngine()
rubrics = engine.generate(missing_skills=["Python", "Docker"])
checklist = engine.evaluate_checklist("Docker")
```

### AnalyticsTracker

```python
from src.analytics.tracker import AnalyticsTracker

tracker = AnalyticsTracker()
overview = tracker.get_overview()
top_skills = tracker.get_top_missing_skills(limit=10)
scores = tracker.get_score_distribution()
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Embeddings** | Sentence Transformers (`all-MiniLM-L6-v2`, 384-dim) |
| **Similarity** | scikit-learn cosine similarity |
| **LLM** | OpenAI GPT-4o-mini via LangChain |
| **Vector DB** | Pinecone (optional) |
| **Knowledge Graph** | Neo4j (optional) |
| **Database** | SQLite with WAL journaling |
| **Auth** | PBKDF2-SHA256 (100K iterations) |
| **Web UI** | Streamlit |
| **PDF Parsing** | pdfplumber |
| **CI/CD** | GitHub Actions |
| **Linting** | ruff |
| **Testing** | pytest (79 tests) |
| **Type Checking** | mypy |

---

## Roadmap

### Completed

- [x] Core skill gap engine (embeddings + LLM)
- [x] Deterministic cosine similarity scoring
- [x] Full analysis pipeline with graceful degradation
- [x] Streamlit web UI with PDF upload
- [x] Input validation and rate limiting
- [x] Custom error hierarchy (7 exception types)
- [x] User accounts with PBKDF2 auth
- [x] SQLite persistence (analyses, feedback, events)
- [x] Analysis history page
- [x] Interview prep generator (20 skills, 5 Qs each)
- [x] Portfolio project generator with personalization
- [x] Evaluation rubric engine
- [x] 55 sample jobs (Junior to Staff)
- [x] Admin dashboard with platform metrics
- [x] GitHub Actions CI/CD (lint + test + type-check)
- [x] Streamlit Cloud deployment config
- [x] Feedback collection system
- [x] Analytics tracker

### Next Steps

- [ ] Real Neo4j skill prerequisite ordering (currently hardcoded estimates)
- [ ] Pinecone job ingestion pipeline (production seeding)
- [ ] Downloadable PDF reports from analysis results
- [ ] Email notifications for saved analyses
- [ ] PostgreSQL migration for production scaling
- [ ] FastAPI backend for API-first access
- [ ] Multi-language resume support
- [ ] Resume parsing improvements (structured section extraction)
- [ ] Caching layer for identical analyses
- [ ] A/B testing on LLM prompts

---

## License

MIT
