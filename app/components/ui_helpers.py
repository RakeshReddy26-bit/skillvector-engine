"""Reusable UI components for SkillVector Engine dashboard.

All functions render styled HTML via st.markdown(unsafe_allow_html=True)
or return Plotly figures for st.plotly_chart().
"""

import os
import streamlit as st
import plotly.graph_objects as go

# ── Color palette ────────────────────────────────────────────────────────────

COLORS = {
    "primary": "#4F8BF9",
    "secondary": "#6C63FF",
    "success": "#00C48C",
    "warning": "#FFB800",
    "error": "#FF4D4D",
    "dark_bg": "#0E1117",
    "card_bg": "#1E2329",
    "border": "#2D333B",
    "muted": "#8B949E",
    "text": "#FAFAFA",
}

CATEGORY_COLORS = {
    "language": "#4F8BF9",
    "data": "#00C48C",
    "devops": "#6C63FF",
    "cloud": "#8B5CF6",
    "architecture": "#FFB800",
    "frontend": "#EC4899",
    "framework": "#0EA5E9",
    "runtime": "#0EA5E9",
    "tool": "#9CA3AF",
    "operations": "#F59E0B",
}


# ── CSS Injection ────────────────────────────────────────────────────────────

def inject_custom_css():
    """Load and inject the custom theme CSS."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "styles", "theme.css")
    try:
        with open(css_path) as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


# ── Metric Cards ─────────────────────────────────────────────────────────────

def render_metric_card(title: str, value, icon: str = "", color: str = "blue", delta: str = ""):
    """Render a styled metric card with icon, value, and optional delta."""
    delta_html = ""
    if delta:
        delta_class = "positive" if delta.startswith("+") or delta.startswith("^") else "negative"
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'

    st.markdown(f"""
    <div class="metric-card {color}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# ── Score Gauge ──────────────────────────────────────────────────────────────

def render_score_gauge(score: float, height: int = 280):
    """Render a Plotly gauge chart for match score."""
    if score < 50:
        bar_color = COLORS["error"]
    elif score < 75:
        bar_color = COLORS["warning"]
    else:
        bar_color = COLORS["success"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 42, "color": COLORS["text"]}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": COLORS["border"],
                "tickfont": {"color": COLORS["muted"], "size": 11},
            },
            "bar": {"color": bar_color, "thickness": 0.3},
            "bgcolor": COLORS["card_bg"],
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50], "color": "rgba(255, 77, 77, 0.08)"},
                {"range": [50, 75], "color": "rgba(255, 184, 0, 0.08)"},
                {"range": [75, 100], "color": "rgba(0, 196, 140, 0.08)"},
            ],
        },
    ))

    fig.update_layout(
        height=height,
        margin=dict(l=30, r=30, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": COLORS["text"]},
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Score Ring (CSS) ────────────────────────────────────────────────────────

def render_score_ring(score: float, size: int = 160):
    """Render an animated CSS circular progress ring for match score."""
    if score >= 70:
        color = COLORS["success"]
    elif score >= 40:
        color = COLORS["warning"]
    else:
        color = COLORS["error"]

    # SVG-based circle progress — works in all browsers, no JS needed
    radius = 54
    circumference = 2 * 3.14159 * radius
    offset = circumference - (score / 100) * circumference

    st.markdown(f"""
    <div style="display:flex; flex-direction:column; align-items:center;">
        <svg width="{size}" height="{size}" viewBox="0 0 120 120" style="transform:rotate(-90deg);">
            <circle cx="60" cy="60" r="{radius}" fill="none"
                    stroke="{COLORS['border']}" stroke-width="8"/>
            <circle cx="60" cy="60" r="{radius}" fill="none"
                    stroke="{color}" stroke-width="8"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}"
                    stroke-linecap="round"
                    style="transition: stroke-dashoffset 1.2s ease-out;">
                <animate attributeName="stroke-dashoffset"
                         from="{circumference}" to="{offset}"
                         dur="1.2s" fill="freeze"/>
            </circle>
        </svg>
        <div style="margin-top:-{size // 2 + 18}px; font-size:32px; font-weight:700;
                    color:{color}; text-align:center; position:relative;">
            {round(score)}%
        </div>
        <div style="height:{size // 2 - 20}px;"></div>
    </div>
    """, unsafe_allow_html=True)


# ── Skill Chips ──────────────────────────────────────────────────────────────

def get_skill_category(skill_name: str) -> str:
    """Look up a skill's category from seed_skills data."""
    try:
        from src.graph.seed_skills import SKILLS
        for s in SKILLS:
            if s["name"].lower() == skill_name.lower():
                return s["category"]
    except ImportError:
        pass
    return "default"


def render_skill_chips(skills: list[str]):
    """Render a row of colored skill chips."""
    chips_html = ""
    for skill in skills:
        category = get_skill_category(skill)
        chips_html += f'<span class="skill-chip {category}">{skill}</span>'

    st.markdown(f'<div class="skill-chips">{chips_html}</div>', unsafe_allow_html=True)


# ── Section Header ───────────────────────────────────────────────────────────

def render_header(title: str, subtitle: str = ""):
    """Render a gradient page header."""
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div class="gradient-header">
        <h1>{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str = ""):
    """Render a section header with border."""
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div class="section-header">
        <h1>{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


# ── Content Card ─────────────────────────────────────────────────────────────

def render_card(title: str, content_html: str):
    """Render a styled card with title and HTML content."""
    st.markdown(f"""
    <div class="content-card">
        <h3>{title}</h3>
        {content_html}
    </div>
    """, unsafe_allow_html=True)


# ── Learning Path Timeline ───────────────────────────────────────────────────

def render_timeline(learning_path: list[dict]):
    """Render a vertical learning path timeline."""
    if not learning_path:
        render_empty_state("No learning path available", "---")
        return

    items_html = ""
    for i, step in enumerate(learning_path, 1):
        skill = step.get("skill", "Unknown")
        days = step.get("estimated_days", 14)
        weeks = step.get("estimated_weeks", 2)
        category = get_skill_category(skill)

        items_html += f"""
        <div class="timeline-item">
            <div class="timeline-step">Step {i}</div>
            <div class="timeline-skill">{skill}</div>
            <div class="timeline-meta">
                <span class="skill-chip {category}" style="font-size:11px;padding:2px 8px;">{category}</span>
                &nbsp;&middot;&nbsp; {days} days ({weeks}w)
            </div>
        </div>
        """

    st.markdown(f'<div class="timeline">{items_html}</div>', unsafe_allow_html=True)


# ── Priority Badge ───────────────────────────────────────────────────────────

def render_badge(text: str, variant: str = ""):
    """Render an inline badge. variant: high, medium, low, beginner, intermediate, advanced, foundational."""
    css_class = variant.lower() if variant else text.lower()
    return f'<span class="badge {css_class}">{text}</span>'


# ── Progress Bar ─────────────────────────────────────────────────────────────

def render_progress_bar(value: float, max_value: float = 100, color: str = ""):
    """Render a styled progress bar."""
    pct = min(100, (value / max_value) * 100) if max_value > 0 else 0
    color_class = color if color else ("green" if pct >= 75 else "orange" if pct >= 50 else "red")
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar {color_class}" style="width: {pct}%"></div>
    </div>
    """, unsafe_allow_html=True)


# ── Empty State ──────────────────────────────────────────────────────────────

def render_empty_state(message: str, icon: str = ""):
    """Render a centered empty state with icon and message."""
    st.markdown(f"""
    <div class="empty-state">
        <div class="icon">{icon}</div>
        <h3>{message}</h3>
        <p>Run an analysis to get started.</p>
    </div>
    """, unsafe_allow_html=True)


# ── Styled Table ─────────────────────────────────────────────────────────────

def render_table(headers: list[str], rows: list[list[str]]):
    """Render a styled HTML table."""
    thead = "".join(f"<th>{h}</th>" for h in headers)
    tbody = ""
    for row in rows:
        cells = "".join(f"<td>{cell}</td>" for cell in row)
        tbody += f"<tr>{cells}</tr>"

    st.markdown(f"""
    <table class="styled-table">
        <thead><tr>{thead}</tr></thead>
        <tbody>{tbody}</tbody>
    </table>
    """, unsafe_allow_html=True)


# ── Footer ───────────────────────────────────────────────────────────────────

def render_footer():
    """Render the app footer."""
    st.markdown("""
    <div class="app-footer">
        SkillVector Engine v1.0 &middot; Built with Streamlit + Plotly
    </div>
    """, unsafe_allow_html=True)
