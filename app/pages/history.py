"""History page — Past analyses with score trend chart and expandable details."""

import streamlit as st
import plotly.graph_objects as go

from app.components.ui_helpers import (
    render_header,
    render_metric_card,
    render_skill_chips,
    render_badge,
    render_empty_state,
    COLORS,
)
from src.db.models import AnalysisRepository


def _build_score_trend(analyses: list[dict]) -> go.Figure:
    """Build a Plotly line chart showing score trend over time."""
    dates = [a["created_at"] for a in reversed(analyses)]
    scores = [a["match_score"] for a in reversed(analyses)]

    fig = go.Figure()

    # Background zones
    fig.add_hrect(y0=0, y1=50, fillcolor="rgba(255, 77, 77, 0.05)", line_width=0)
    fig.add_hrect(y0=50, y1=75, fillcolor="rgba(255, 184, 0, 0.05)", line_width=0)
    fig.add_hrect(y0=75, y1=100, fillcolor="rgba(0, 196, 140, 0.05)", line_width=0)

    # Score line
    fig.add_trace(go.Scatter(
        x=dates, y=scores,
        mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=8, color=COLORS["primary"], line=dict(width=2, color=COLORS["dark_bg"])),
        hovertemplate="Score: %{y}%<br>Date: %{x}<extra></extra>",
    ))

    # Zone labels
    fig.add_annotation(x=0, y=25, text="Significant Gap", showarrow=False,
                       xref="paper", font=dict(size=10, color="#FF4D4D"), opacity=0.5)
    fig.add_annotation(x=0, y=62, text="Moderate", showarrow=False,
                       xref="paper", font=dict(size=10, color="#FFB800"), opacity=0.5)
    fig.add_annotation(x=0, y=87, text="Strong Match", showarrow=False,
                       xref="paper", font=dict(size=10, color="#00C48C"), opacity=0.5)

    fig.update_layout(
        height=300,
        margin=dict(l=40, r=20, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False,
            color=COLORS["muted"],
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            range=[0, 100],
            showgrid=True,
            gridcolor=COLORS["border"],
            color=COLORS["muted"],
            ticksuffix="%",
            tickfont=dict(size=11),
        ),
        showlegend=False,
    )
    return fig


def render_history():
    """Render the history page."""
    render_header("Analysis History", "Track your skill gap progress over time")

    if "user_id" not in st.session_state or st.session_state.get("user_id") is None:
        render_empty_state("Login Required", "")
        st.markdown("""
        <div style="text-align: center;">
            <p style="color: #8B949E; font-size: 14px;">
                Please log in to view your analysis history.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    analyses = AnalysisRepository().get_user_analyses(st.session_state["user_id"])

    if not analyses:
        render_empty_state("No analyses yet", "")
        st.markdown("""
        <div style="text-align: center;">
            <p style="color: #8B949E; font-size: 14px;">
                Run your first analysis to start tracking your progress.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Summary Stats ────────────────────────────────────────────────────
    scores = [a["match_score"] for a in analyses]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    # Most common missing skill
    skill_counts = {}
    for a in analyses:
        for s in a.get("missing_skills", []):
            skill_counts[s] = skill_counts.get(s, 0) + 1
    top_skill = max(skill_counts, key=skill_counts.get) if skill_counts else "N/A"

    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Total Analyses", str(len(analyses)), icon="", color="blue")
    with c2:
        render_metric_card("Average Score", f"{avg_score}%", icon="", color="green")
    with c3:
        render_metric_card("Top Gap Skill", top_skill, icon="", color="orange")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Score Trend Chart ────────────────────────────────────────────────
    if len(analyses) >= 2:
        st.markdown("""
        <div class="content-card">
            <h3>Score Trend</h3>
        """, unsafe_allow_html=True)
        fig = _build_score_trend(analyses)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Analysis Cards ───────────────────────────────────────────────────
    st.markdown(f"""
    <div class="section-header">
        <h1>All Analyses</h1>
        <p>{len(analyses)} analyses recorded</p>
    </div>
    """, unsafe_allow_html=True)

    for analysis in analyses:
        score = analysis["match_score"]
        priority = analysis.get("learning_priority", analysis.get("result", {}).get("learning_priority", "N/A"))
        skills = analysis.get("missing_skills", [])
        created = analysis["created_at"]
        result = analysis.get("result", {})

        score_color = "green" if score >= 75 else ("orange" if score >= 50 else "red")
        priority_badge = render_badge(priority, priority.lower() if priority != "N/A" else "")

        with st.expander(f"{score}% match | {len(skills)} skills | {created}"):
            m1, m2, m3 = st.columns(3)
            with m1:
                render_metric_card("Score", f"{score}%", color=score_color)
            with m2:
                st.markdown(f"**Priority:** {priority_badge}", unsafe_allow_html=True)
            with m3:
                st.markdown(f"**Missing Skills:** {len(skills)}")

            if skills:
                st.markdown("**Skills to learn:**")
                render_skill_chips(skills)

            lp = result.get("learning_path", [])
            if lp:
                st.markdown("**Learning Path:**")
                for i, step in enumerate(lp, 1):
                    st.markdown(f"{i}. {step['skill']} ({step.get('estimated_days', '?')} days)")

            ev = result.get("evidence", [])
            if ev:
                st.markdown("**Portfolio Projects:**")
                for item in ev:
                    st.markdown(f"- {item['skill']}: {item['project']}")
