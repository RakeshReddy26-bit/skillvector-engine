"""Admin page — Platform analytics dashboard with Plotly charts.

Gated by ADMIN_EMAIL environment variable.
"""

import os
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go

from app.components.ui_helpers import (
    render_header,
    render_metric_card,
    render_table,
    render_empty_state,
    COLORS,
    CATEGORY_COLORS,
)
from src.analytics.tracker import AnalyticsTracker
from src.graph.seed_skills import SKILLS
from src.health import check_health


def _is_admin() -> bool:
    if "user_id" not in st.session_state or st.session_state.get("user_id") is None:
        return False
    admin_email = os.getenv("ADMIN_EMAIL", "")
    user_email = st.session_state.get("user_email", "")
    return admin_email and user_email.lower() == admin_email.lower()


def _skill_category_map() -> dict:
    """Build skill_name_lower -> category map."""
    return {s["name"].lower(): s["category"] for s in SKILLS}


def _build_daily_activity_chart(daily: list[dict]) -> go.Figure:
    """Build a Plotly bar chart for daily activity."""
    if not daily:
        return None

    dates = [d.get("day", d.get("date", "")) for d in daily]
    counts = [d.get("count", 0) for d in daily]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dates, y=counts,
        marker=dict(
            color=COLORS["primary"],
            cornerradius=4,
        ),
        hovertemplate="Date: %{x}<br>Events: %{y}<extra></extra>",
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=40, r=20, t=10, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, color=COLORS["muted"], tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor=COLORS["border"], color=COLORS["muted"], tickfont=dict(size=11)),
        bargap=0.3,
    )
    return fig


def _build_score_distribution_chart(scores: dict) -> go.Figure:
    """Build a Plotly donut chart for score distribution."""
    labels = ["Strong (75%+)", "Moderate (50-74%)", "Gap (<50%)"]
    values = [scores.get("high", 0), scores.get("medium", 0), scores.get("low", 0)]
    colors = [COLORS["success"], COLORS["warning"], COLORS["error"]]

    if sum(values) == 0:
        return None

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=COLORS["dark_bg"], width=2)),
        textfont=dict(size=12, color=COLORS["text"]),
        hovertemplate="%{label}<br>Count: %{value}<br>%{percent}<extra></extra>",
    )])

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            font=dict(color=COLORS["muted"], size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        annotations=[dict(
            text=f"{scores.get('average', 0)}%",
            x=0.5, y=0.5, font_size=22,
            font_color=COLORS["text"],
            showarrow=False,
        )],
    )
    return fig


def _build_top_skills_chart(top_skills: list[dict]) -> go.Figure:
    """Build a Plotly horizontal bar chart for top missing skills."""
    if not top_skills:
        return None

    cat_map = _skill_category_map()
    skills = [s["skill"] for s in reversed(top_skills)]
    counts = [s["count"] for s in reversed(top_skills)]
    colors = [CATEGORY_COLORS.get(cat_map.get(s.lower(), "default"), "#8B949E") for s in skills]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=counts, y=skills,
        orientation="h",
        marker=dict(color=colors, cornerradius=4),
        hovertemplate="%{y}<br>Count: %{x}<extra></extra>",
    ))

    fig.update_layout(
        height=max(250, len(top_skills) * 35),
        margin=dict(l=120, r=20, t=10, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor=COLORS["border"], color=COLORS["muted"], tickfont=dict(size=11)),
        yaxis=dict(showgrid=False, color=COLORS["text"], tickfont=dict(size=12)),
    )
    return fig


def _build_category_radar(top_skills: list[dict]) -> go.Figure:
    """Build a radar chart showing missing skill frequency by category."""
    if not top_skills:
        return None

    cat_map = _skill_category_map()
    category_counts = {}
    for s in top_skills:
        cat = cat_map.get(s["skill"].lower(), "other")
        category_counts[cat] = category_counts.get(cat, 0) + s["count"]

    if not category_counts:
        return None

    categories = sorted(category_counts.keys())
    values = [category_counts[c] for c in categories]
    # Close the radar
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=[c.capitalize() for c in categories_closed],
        fill="toself",
        fillcolor="rgba(79, 139, 249, 0.15)",
        line=dict(color=COLORS["primary"], width=2),
        marker=dict(size=6, color=COLORS["primary"]),
    ))

    fig.update_layout(
        height=350,
        margin=dict(l=60, r=60, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                showticklabels=True,
                tickfont=dict(size=10, color=COLORS["muted"]),
                gridcolor=COLORS["border"],
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=COLORS["text"]),
                gridcolor=COLORS["border"],
            ),
        ),
    )
    return fig


def render_admin():
    """Render the admin analytics dashboard."""
    render_header("Admin Dashboard", f"Platform analytics | {datetime.now().strftime('%B %d, %Y')}")

    if not _is_admin():
        render_empty_state("Access Denied", "")
        st.markdown("""
        <div style="text-align: center;">
            <p style="color: #8B949E; font-size: 14px;">
                Admin access required. Contact the platform administrator.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    tracker = AnalyticsTracker()

    # ── Platform Overview ────────────────────────────────────────────────
    overview = tracker.get_overview()
    feedback_summary = tracker.get_feedback_summary()
    score_dist = tracker.get_score_distribution()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Analyses", str(overview["total_analyses"]), icon="", color="blue")
    with c2:
        render_metric_card("Registered Users", str(overview["total_registrations"]), icon="", color="green")
    with c3:
        render_metric_card("Satisfaction", f"{feedback_summary['satisfaction_rate']}%", icon="", color="purple")
    with c4:
        render_metric_card("Avg Score", f"{score_dist.get('average', 0)}%", icon="", color="orange")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── System Health ─────────────────────────────────────────────────────
    health = check_health()
    st.markdown("""
    <div class="content-card">
        <h3>System Health</h3>
    """, unsafe_allow_html=True)

    h1, h2, h3, h4, h5 = st.columns(5)

    def _status_dot(status):
        color = {"ok": "#00C48C", "healthy": "#00C48C", "degraded": "#FFB800"}.get(
            status, "#FF4D4D"
        )
        return f'<span style="color:{color};font-size:18px;">&#9679;</span> {status}'

    with h1:
        st.markdown(f"**Status**<br>{_status_dot(health['status'])}", unsafe_allow_html=True)
    with h2:
        st.markdown(f"**Model**<br><code>{health['model']}</code>", unsafe_allow_html=True)
    with h3:
        st.markdown(f"**Anthropic**<br>{_status_dot(health['anthropic'])}", unsafe_allow_html=True)
    with h4:
        st.markdown(f"**Neo4j**<br>{_status_dot(health['neo4j'])}", unsafe_allow_html=True)
    with h5:
        st.markdown(f"**Pinecone**<br>{_status_dot(health['pinecone'])}", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:8px; font-size:11px; color:#8B949E;">
        Version {health['version']} &middot; Health check took {health['checks_ms']}ms
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ───────────────────────────────────────────────────────
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("""
        <div class="content-card">
            <h3>Daily Activity (30 Days)</h3>
        """, unsafe_allow_html=True)
        daily = tracker.get_daily_activity(30)
        fig = _build_daily_activity_chart(daily)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<p style="color: #8B949E;">No activity data yet.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with chart2:
        st.markdown("""
        <div class="content-card">
            <h3>Score Distribution</h3>
        """, unsafe_allow_html=True)
        fig = _build_score_distribution_chart(score_dist)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<p style="color: #8B949E;">No score data yet.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top Missing Skills + Radar ───────────────────────────────────────
    top_skills = tracker.get_top_missing_skills()

    skill_chart_col, radar_col = st.columns(2)

    with skill_chart_col:
        st.markdown("""
        <div class="content-card">
            <h3>Top Missing Skills</h3>
        """, unsafe_allow_html=True)
        fig = _build_top_skills_chart(top_skills)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<p style="color: #8B949E;">No skill data yet.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with radar_col:
        st.markdown("""
        <div class="content-card">
            <h3>Skill Category Breakdown</h3>
        """, unsafe_allow_html=True)
        fig = _build_category_radar(top_skills)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<p style="color: #8B949E;">No category data yet.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Feedback + Overview Details ──────────────────────────────────────
    fb_col, detail_col = st.columns(2)

    with fb_col:
        st.markdown("""
        <div class="content-card">
            <h3>Recent Feedback</h3>
        """, unsafe_allow_html=True)

        recent_fb = tracker.get_recent_feedback(10)
        if recent_fb:
            headers = ["Date", "Sentiment", "Score", "Comment"]
            rows = []
            for fb in recent_fb:
                sentiment = "Positive" if fb["is_positive"] else "Negative"
                sent_color = "#00C48C" if fb["is_positive"] else "#FF4D4D"
                sentiment_html = f'<span style="color: {sent_color}; font-weight: 600;">{sentiment}</span>'
                score_str = f"{fb['match_score']}%" if fb.get("match_score") else "-"
                comment = fb.get("comment", "") or "-"
                date_str = fb.get("created_at", "")[:10]
                rows.append([date_str, sentiment_html, score_str, comment])
            render_table(headers, rows)
        else:
            st.markdown('<p style="color: #8B949E;">No feedback yet.</p>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with detail_col:
        st.markdown("""
        <div class="content-card">
            <h3>Platform Details</h3>
        """, unsafe_allow_html=True)

        details = [
            ["Total Analyses", str(overview["total_analyses"])],
            ["Authenticated", str(overview["authenticated_analyses"])],
            ["Anonymous", str(overview["anonymous_analyses"])],
            ["Total Logins", str(overview["total_logins"])],
            ["Registrations", str(overview["total_registrations"])],
            ["Feedback Count", str(feedback_summary["total"])],
            ["Positive", str(feedback_summary["positive"])],
            ["Negative", str(feedback_summary["negative"])],
        ]
        render_table(["Metric", "Value"], details)

        st.markdown("</div>", unsafe_allow_html=True)
