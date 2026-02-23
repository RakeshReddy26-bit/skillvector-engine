"""Dashboard page — User's analysis overview with metrics and quick actions."""

import streamlit as st
from app.components.ui_helpers import (
    render_header,
    render_metric_card,
    render_score_gauge,
    render_score_ring,
    render_skill_chips,
    render_empty_state,
)


def render_dashboard():
    """Render the main dashboard page."""
    user_email = st.session_state.get("user_email", "Guest")
    greeting = f"Welcome back, {user_email}" if "user_id" in st.session_state else "Welcome, Guest"

    render_header("Dashboard", greeting)

    result = st.session_state.get("result")

    if not result:
        render_empty_state("No analysis results yet", "")
        st.markdown("""
        <div style="text-align: center; margin-top: 16px;">
            <p style="color: #8B949E; font-size: 14px;">
                Navigate to <strong>Analyze</strong> to run your first skill gap analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    score = result.get("match_score", 0)
    priority = result.get("learning_priority", "N/A")
    missing = result.get("missing_skills", [])
    learning_path = result.get("learning_path", [])
    related_jobs = result.get("related_jobs", [])

    # ── Quick Stats Row ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        score_color = "green" if score >= 75 else ("orange" if score >= 50 else "red")
        render_metric_card("Match Score", f"{score}%", icon="", color=score_color)

    with c2:
        total_days = sum(s.get("estimated_days", 0) for s in learning_path)
        render_metric_card("Total Learning Days", str(total_days), icon="", color="blue")

    with c3:
        render_metric_card("Skills to Learn", str(len(missing)), icon="", color="purple")

    with c4:
        priority_color = {"High": "red", "Medium": "orange", "Low": "green"}.get(priority, "blue")
        render_metric_card("Priority", priority, icon="", color=priority_color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Score Gauge ──────────────────────────────────────────────────────
    gauge_col, info_col = st.columns([2, 3])

    with gauge_col:
        st.markdown("""
        <div class="content-card">
            <h3>Overall Match Score</h3>
        """, unsafe_allow_html=True)
        render_score_ring(score, size=180)
        st.markdown("</div>", unsafe_allow_html=True)

    with info_col:
        # Missing Skills
        st.markdown("""
        <div class="content-card">
            <h3>Missing Skills</h3>
        """, unsafe_allow_html=True)

        if missing:
            render_skill_chips(missing)
        else:
            st.markdown('<p style="color: #00C48C;">No skill gaps detected!</p>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Learning path summary
        if learning_path:
            st.markdown("""
            <div class="content-card">
                <h3>Learning Path Preview</h3>
            """, unsafe_allow_html=True)

            total_weeks = sum(s.get("estimated_weeks", 0) for s in learning_path)
            st.markdown(f"""
            <p style="color: #8B949E; font-size: 14px;">
                {len(learning_path)} skills to learn &middot; ~{total_weeks} weeks total
            </p>
            """, unsafe_allow_html=True)

            # Show first 5 skills
            preview = learning_path[:5]
            for i, step in enumerate(preview, 1):
                skill = step.get("skill", "Unknown")
                days = step.get("estimated_days", 14)
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 6px 0; border-bottom: 1px solid #2D333B;">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: #4F8BF9;
                                display: flex; align-items: center; justify-content: center;
                                font-size: 11px; font-weight: 600; color: white; margin-right: 12px;">
                        {i}
                    </div>
                    <div style="flex: 1; color: #FAFAFA; font-size: 14px;">{skill}</div>
                    <div style="color: #8B949E; font-size: 12px;">{days}d</div>
                </div>
                """, unsafe_allow_html=True)

            if len(learning_path) > 5:
                st.markdown(f"""
                <p style="color: #8B949E; font-size: 12px; margin-top: 8px; text-align: center;">
                    + {len(learning_path) - 5} more skills
                </p>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # ── Related Jobs Preview ──────────────────────────────────────────────
    if related_jobs:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="content-card">
            <h3>Related Jobs</h3>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <p style="color: #8B949E; font-size: 14px;">
            {len(related_jobs)} similar roles found in the job market
        </p>
        """, unsafe_allow_html=True)

        preview_jobs = related_jobs[:3]
        for job in preview_jobs:
            score_pct = round(job.get("score", 0) * 100)
            score_color = (
                "#00C48C" if score_pct >= 75
                else "#FFB800" if score_pct >= 50
                else "#FF4D4D"
            )
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 8px 0;
                        border-bottom: 1px solid #2D333B;">
                <div style="flex: 1;">
                    <div style="color: #FAFAFA; font-size: 14px; font-weight: 500;">
                        {job.get("job_title", "Unknown")}
                    </div>
                    <div style="color: #8B949E; font-size: 12px;">
                        {job.get("company", "Unknown")}
                    </div>
                </div>
                <div style="color: {score_color}; font-weight: 700; font-size: 16px;">
                    {score_pct}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        if len(related_jobs) > 3:
            st.markdown(f"""
            <p style="color: #8B949E; font-size: 12px; margin-top: 8px; text-align: center;">
                + {len(related_jobs) - 3} more roles
            </p>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
