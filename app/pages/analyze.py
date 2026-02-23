"""Analyze page — Resume + Job Description input, pipeline execution, full results display."""

import json
import logging
import os

import streamlit as st

from app.components.ui_helpers import (
    render_header,
    render_metric_card,
    render_score_gauge,
    render_score_ring,
    render_skill_chips,
    render_timeline,
    render_badge,
    render_table,
)
from src.pipeline.full_pipeline import SkillVectorPipeline
from src.utils.errors import SkillVectorError, ValidationError, EmbeddingError, LLMError, RetrievalError
from src.utils.validators import validate_resume, validate_job_description, sanitize_text
from src.db.models import AnalysisRepository, FeedbackRepository, EventRepository

logger = logging.getLogger(__name__)


# ── Sample data ──────────────────────────────────────────────────────────────

SAMPLE_RESUME = """Backend Engineer with 3 years of experience in Python and Django.
Built REST APIs, worked with PostgreSQL and Redis.
Deployed applications using Docker on AWS EC2.
Familiar with Git, Agile, and test-driven development."""

SAMPLE_JOB = """Senior Backend Engineer
Requirements:
- 5+ years of Python experience
- Kubernetes and container orchestration
- CI/CD pipeline design and management
- Microservices architecture
- Cloud-native development (AWS/GCP)
- System design and scalability
- Strong communication skills"""

DEMO_RESUME = """ML Engineer | 4 years experience

SKILLS: Python, NumPy, Pandas, Scikit-learn, PyTorch, SQL, Git, Docker, REST APIs, FastAPI

EXPERIENCE:
- Built recommendation engine serving 2M daily predictions using PyTorch and FastAPI
- Designed ETL pipelines processing 500GB/day with Airflow and Spark
- Deployed ML models to AWS SageMaker with CI/CD via GitHub Actions
- Implemented A/B testing framework for model evaluation across 3 product lines
- Optimized inference latency from 200ms to 45ms using model quantization and ONNX
- Managed PostgreSQL and Redis data stores for feature serving

EDUCATION: M.S. Computer Science, focus on Machine Learning"""

DEMO_JOB = """Senior ML Engineer — AI Platform Team

We are building the next-generation ML infrastructure. You will:
- Design and deploy production ML systems at scale (Kubernetes, Terraform)
- Build real-time feature pipelines with Kafka and Spark
- Own model lifecycle: training, evaluation, deployment, monitoring
- Architect microservices for model serving with low-latency requirements
- Implement MLOps best practices: experiment tracking, model registry, A/B testing

Requirements:
- 5+ years Python, strong ML/DL fundamentals (PyTorch or TensorFlow)
- Kubernetes and container orchestration in production
- CI/CD pipeline design (GitHub Actions, Jenkins, or similar)
- Cloud infrastructure (AWS or GCP), Terraform for IaC
- System design for distributed ML systems
- Kafka or similar streaming platform experience
- Strong SQL and data engineering skills"""


# ── Helpers ──────────────────────────────────────────────────────────────────

@st.cache_resource
def get_pipeline():
    return SkillVectorPipeline()


def extract_pdf_text(uploaded_file) -> str:
    """Extract text from an uploaded PDF file."""
    try:
        import pdfplumber
        with pdfplumber.open(uploaded_file) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages).strip()
    except Exception as e:
        logger.warning("PDF extraction failed: %s", e)
        return ""


def load_sample_jobs() -> list[dict]:
    """Load sample jobs for the dropdown."""
    try:
        jobs_path = os.path.join(os.path.dirname(__file__), "..", "..", "src", "data", "sample_jobs.json")
        with open(jobs_path) as f:
            return json.load(f)
    except Exception:
        return []


def is_logged_in() -> bool:
    return "user_id" in st.session_state and st.session_state["user_id"] is not None


def _render_error_card(title: str, detail: str, suggestion: str) -> None:
    """Render a styled error card instead of a plain st.error."""
    st.markdown(f"""
    <div class="content-card" style="border:1px solid #FF4D4D; padding:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
            <span style="font-size:24px; color:#FF4D4D;">&#9888;</span>
            <h3 style="margin:0; color:#FF4D4D;">{title}</h3>
        </div>
        <p style="color:#FAFAFA; font-size:14px; margin:0 0 8px 0;">{detail}</p>
        <p style="color:#8B949E; font-size:13px; margin:0;">{suggestion}</p>
    </div>
    """, unsafe_allow_html=True)


# ── Main render ──────────────────────────────────────────────────────────────

def render_analyze():
    """Render the analysis page."""
    render_header("Skill Gap Analysis", "Discover your skill gaps and get a personalized learning path")

    # ── Input form ───────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="content-card">
            <h3>Your Resume</h3>
        """, unsafe_allow_html=True)

        resume_method = st.radio("Input method:", ["Paste text", "Upload PDF"], horizontal=True, key="resume_method")

        if resume_method == "Paste text":
            resume_text = st.text_area(
                "Paste your resume here",
                value=st.session_state.get("resume_input", ""),
                height=220,
                key="resume_area",
                label_visibility="collapsed",
                placeholder="Paste your resume content here...",
            )
        else:
            uploaded_file = st.file_uploader("Upload resume", type=["pdf", "txt"], key="resume_upload")
            if uploaded_file:
                if uploaded_file.type == "application/pdf":
                    resume_text = extract_pdf_text(uploaded_file)
                else:
                    resume_text = uploaded_file.read().decode("utf-8", errors="ignore")
                if resume_text:
                    st.text_area("Preview", resume_text[:500], height=100, disabled=True)
                else:
                    st.warning("Could not extract text.")
            else:
                resume_text = ""

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="content-card">
            <h3>Target Job Description</h3>
        """, unsafe_allow_html=True)

        # Sample job dropdown
        sample_jobs = load_sample_jobs()
        if sample_jobs:
            job_options = ["-- Select a sample job --"] + [
                f"{j['title']} ({j['level']}) - {j['company']}" for j in sample_jobs
            ]
            selected_job = st.selectbox("Or choose a sample job:", job_options, key="job_select", label_visibility="collapsed")

            if selected_job != "-- Select a sample job --":
                idx = job_options.index(selected_job) - 1
                st.session_state["job_input"] = sample_jobs[idx]["description"]

        job_text = st.text_area(
            "Paste job description",
            value=st.session_state.get("job_input", ""),
            height=220,
            key="job_area",
            label_visibility="collapsed",
            placeholder="Paste the job description here...",
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Action buttons ───────────────────────────────────────────────────
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 2, 1, 1])
    with btn_col1:
        if st.button("Load Sample Data", use_container_width=True):
            st.session_state["resume_input"] = SAMPLE_RESUME
            st.session_state["job_input"] = SAMPLE_JOB
            st.rerun()
    with btn_col2:
        analyze_clicked = st.button("Analyze Skill Gap", type="primary", use_container_width=True)
    with btn_col3:
        demo_clicked = st.button("Try Demo", use_container_width=True)
    with btn_col4:
        if st.button("Clear Results", use_container_width=True):
            for key in ["result", "resume_input", "job_input", "last_analysis_id", "show_feedback_form"]:
                st.session_state.pop(key, None)
            st.rerun()

    # Demo mode: load realistic data and auto-trigger analysis
    if demo_clicked:
        st.session_state["resume_input"] = DEMO_RESUME
        st.session_state["job_input"] = DEMO_JOB
        resume_text = DEMO_RESUME
        job_text = DEMO_JOB
        analyze_clicked = True

    # ── Run analysis ─────────────────────────────────────────────────────
    if analyze_clicked:
        resume_clean = sanitize_text(resume_text) if resume_text else ""
        job_clean = sanitize_text(job_text) if job_text else ""

        resume_valid, resume_err = validate_resume(resume_clean)
        job_valid, job_err = validate_job_description(job_clean)

        if not resume_valid:
            st.error(resume_err)
        elif not job_valid:
            st.error(job_err)
        else:
            allowed, rate_err = st.session_state["rate_limiter"].check(st.session_state["session_id"])
            if not allowed:
                st.warning(rate_err)
            else:
                # Loading skeleton
                progress_placeholder = st.empty()
                progress_placeholder.markdown("""
                <div class="content-card" style="text-align:center; padding:40px;">
                    <div class="loading-ring"></div>
                    <h3 style="margin-top:16px;">Analyzing your skill gap...</h3>
                    <p style="color:#8B949E; font-size:13px;">
                        Running AI analysis, building learning path, generating evidence
                    </p>
                </div>
                """, unsafe_allow_html=True)

                try:
                    pipeline = get_pipeline()
                    result = pipeline.run(resume_clean, job_clean)
                    progress_placeholder.empty()
                    st.session_state["result"] = result

                    latency = result.get("latency_ms", 0)
                    req_id = result.get("request_id", "")
                    logger.info("Analysis displayed | request_id=%s | latency=%dms", req_id, latency)

                    if is_logged_in():
                        analysis_id = AnalysisRepository().save_analysis(
                            user_id=st.session_state["user_id"],
                            resume_text=resume_clean,
                            job_text=job_clean,
                            result=result,
                        )
                        st.session_state["last_analysis_id"] = analysis_id
                        EventRepository().track(
                            "analysis",
                            user_id=st.session_state["user_id"],
                            metadata={"match_score": result["match_score"]},
                        )
                    else:
                        EventRepository().track(
                            "analysis_anonymous",
                            metadata={"match_score": result["match_score"]},
                        )
                except ValidationError as e:
                    progress_placeholder.empty()
                    _render_error_card("Input Error", str(e), "Check your resume and job description inputs.")
                except LLMError:
                    progress_placeholder.empty()
                    _render_error_card(
                        "AI Service Unavailable",
                        "The Anthropic API is temporarily unreachable.",
                        "Check your ANTHROPIC_API_KEY and try again in a moment.",
                    )
                except EmbeddingError:
                    progress_placeholder.empty()
                    _render_error_card(
                        "Text Processing Failed",
                        "Could not generate embeddings for your input.",
                        "Try shortening your resume or check the text encoding.",
                    )
                except RetrievalError:
                    progress_placeholder.empty()
                    st.warning("Job market data unavailable. Showing basic analysis.")
                    try:
                        from src.engine.skill_gap_engine import SkillGapEngine
                        gap = SkillGapEngine().analyze(resume_clean, job_clean)
                        st.session_state["result"] = {
                            "match_score": gap["match_score"],
                            "learning_priority": "Medium",
                            "missing_skills": gap["missing_skills"],
                            "learning_path": [],
                            "evidence": [],
                            "interview_prep": [],
                            "rubrics": [],
                        }
                    except Exception:
                        _render_error_card(
                            "Analysis Failed",
                            "Could not complete the analysis.",
                            "Please try again.",
                        )
                except SkillVectorError as e:
                    progress_placeholder.empty()
                    _render_error_card("Analysis Error", str(e), "Please try again.")
                except Exception:
                    progress_placeholder.empty()
                    logger.exception("Unexpected error during analysis")
                    _render_error_card(
                        "Unexpected Error",
                        "Something went wrong during analysis.",
                        "Please try again. If this persists, contact support.",
                    )

    # ── Display results ──────────────────────────────────────────────────
    if "result" not in st.session_state:
        return

    result = st.session_state["result"]
    score = result.get("match_score", 0)
    priority = result.get("learning_priority", "N/A")
    missing = result.get("missing_skills", [])
    learning_path = result.get("learning_path", [])
    evidence = result.get("evidence", [])
    interview_prep = result.get("interview_prep", [])
    rubrics = result.get("rubrics", [])
    related_jobs = result.get("related_jobs", [])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Score Overview ───────────────────────────────────────────────────
    score_col, gauge_col, priority_col = st.columns([1, 2, 1])

    with score_col:
        score_color = "green" if score >= 75 else ("orange" if score >= 50 else "red")
        render_metric_card("Match Score", f"{score}%", icon="", color=score_color)
        st.markdown("<br>", unsafe_allow_html=True)
        render_metric_card("Missing Skills", str(len(missing)), icon="", color="purple")

    with gauge_col:
        render_score_ring(score, size=200)

    with priority_col:
        priority_color = {"High": "red", "Medium": "orange", "Low": "green"}.get(priority, "blue")
        render_metric_card("Learning Priority", priority, icon="", color=priority_color)
        st.markdown("<br>", unsafe_allow_html=True)
        total_days = sum(s.get("estimated_days", 0) for s in learning_path)
        render_metric_card("Total Days", str(total_days), icon="", color="blue")

    # Request metadata
    req_id = result.get("request_id", "")
    latency = result.get("latency_ms", 0)
    if req_id:
        st.markdown(f"""
        <div style="text-align:right; font-size:11px; color:#8B949E; padding:4px 0;">
            request_id: <code>{req_id}</code> &middot; latency: {latency}ms
        </div>
        """, unsafe_allow_html=True)

    # ── Missing Skills Chips ─────────────────────────────────────────────
    if missing:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="content-card">
            <h3>Missing Skills</h3>
        """, unsafe_allow_html=True)
        render_skill_chips(missing)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Learning Path Timeline ───────────────────────────────────────────
    if learning_path:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="content-card">
            <h3>Learning Path (Prerequisite Order)</h3>
        """, unsafe_allow_html=True)
        render_timeline(learning_path)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Portfolio Projects ───────────────────────────────────────────────
    if evidence:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header"><h1>Portfolio Projects</h1><p>Build these to demonstrate your skills</p></div>', unsafe_allow_html=True)

        proj_cols = st.columns(2)
        for i, item in enumerate(evidence):
            with proj_cols[i % 2]:
                deliverables_html = ""
                for d in item.get("deliverables", []):
                    deliverables_html += f"<li><code>{d}</code></li>"

                weeks = item.get("estimated_weeks", "?")
                st.markdown(f"""
                <div class="project-card">
                    <h4>{item.get('skill', '')}: {item.get('project', '')}</h4>
                    <p>{item.get('description', '')}</p>
                    <div class="deliverables">
                        <div style="font-size: 12px; color: #8B949E; margin-bottom: 6px;">DELIVERABLES</div>
                        <ul style="margin: 0; padding-left: 16px;">{deliverables_html}</ul>
                    </div>
                    <div style="margin-top: 12px; font-size: 12px; color: #8B949E;">
                        ~{weeks} week(s)
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Interview Prep ───────────────────────────────────────────────────
    if interview_prep:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header"><h1>Interview Preparation</h1><p>Practice questions by skill</p></div>', unsafe_allow_html=True)

        for prep in interview_prep:
            difficulty = prep.get("difficulty", "Intermediate")
            badge_html = render_badge(difficulty, difficulty.lower())

            with st.expander(f"{prep['skill']} ({difficulty})"):
                st.markdown(f"Difficulty: {badge_html}", unsafe_allow_html=True)

                st.markdown("**Questions:**")
                for j, q in enumerate(prep.get("questions", []), 1):
                    st.markdown(f"{j}. {q}")

                tips = prep.get("tips", [])
                if tips:
                    st.markdown("**Preparation Tips:**")
                    for tip in tips:
                        st.markdown(f"- {tip}")

    # ── Rubrics ──────────────────────────────────────────────────────────
    if rubrics:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header"><h1>Evaluation Rubrics</h1><p>Self-assess your portfolio projects</p></div>', unsafe_allow_html=True)

        rubric_tabs = st.tabs([r["skill"] for r in rubrics])
        for tab, rubric in zip(rubric_tabs, rubrics):
            with tab:
                headers = ["Criterion", "Weight", "Excellent", "Good", "Needs Work"]
                rows = []
                for c in rubric.get("criteria", []):
                    rows.append([
                        c["name"],
                        f"{c['weight']}%",
                        c["levels"].get("Excellent", ""),
                        c["levels"].get("Good", ""),
                        c["levels"].get("Needs Work", ""),
                    ])
                render_table(headers, rows)

    # ── Related Jobs ──────────────────────────────────────────────────────
    if related_jobs:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="section-header"><h1>Related Jobs</h1>'
            '<p>Similar roles from the job market</p></div>',
            unsafe_allow_html=True,
        )

        job_cols = st.columns(2)
        for i, job in enumerate(related_jobs):
            with job_cols[i % 2]:
                score_pct = round(job.get("score", 0) * 100)
                score_color = (
                    "#00C48C" if score_pct >= 75
                    else "#FFB800" if score_pct >= 50
                    else "#FF4D4D"
                )
                skills_list = job.get("skills", [])
                if isinstance(skills_list, str):
                    skills_list = [s.strip() for s in skills_list.split(",")]
                skills_html = " ".join(
                    f'<span class="skill-chip default" style="font-size:11px;'
                    f'padding:2px 8px;">{s}</span>'
                    for s in skills_list[:6]
                )

                st.markdown(f"""
                <div class="job-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4>{job.get("job_title", "Unknown Role")}</h4>
                        <span style="color:{score_color}; font-weight:700; font-size:18px;">
                            {score_pct}%
                        </span>
                    </div>
                    <p style="color:#8B949E; font-size:13px; margin:4px 0 12px 0;">
                        {job.get("company", "Unknown Company")}
                    </p>
                    <div class="skill-chips" style="margin:0;">
                        {skills_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Feedback ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="content-card">
        <h3>Was this analysis helpful?</h3>
    """, unsafe_allow_html=True)

    fb1, fb2, _ = st.columns([1, 1, 3])
    with fb1:
        if st.button("Yes, helpful", key="fb_yes", use_container_width=True):
            analysis_id = st.session_state.get("last_analysis_id", "anonymous")
            FeedbackRepository().save_feedback(
                analysis_id=analysis_id,
                is_positive=True,
                user_id=st.session_state.get("user_id"),
            )
            st.success("Thanks for your feedback!")
    with fb2:
        if st.button("Needs improvement", key="fb_no", use_container_width=True):
            st.session_state["show_feedback_form"] = True

    if st.session_state.get("show_feedback_form"):
        feedback_text = st.text_input("What could be better?", key="fb_text")
        if st.button("Submit feedback", key="fb_submit"):
            analysis_id = st.session_state.get("last_analysis_id", "anonymous")
            FeedbackRepository().save_feedback(
                analysis_id=analysis_id,
                is_positive=False,
                user_id=st.session_state.get("user_id"),
                comment=feedback_text,
            )
            st.session_state["show_feedback_form"] = False
            st.success("Thanks for your feedback!")

    st.markdown("</div>", unsafe_allow_html=True)
