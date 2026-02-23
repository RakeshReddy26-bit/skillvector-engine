"""Learning Path page — Visual roadmap with prerequisite graph and phase breakdown."""

import streamlit as st
import plotly.graph_objects as go

from app.components.ui_helpers import (
    render_header,
    render_metric_card,
    render_timeline,
    render_table,
    render_empty_state,
    render_badge,
    CATEGORY_COLORS,
    COLORS,
)
from src.graph.seed_skills import PREREQUISITES, SKILLS, get_skill_estimates


def _get_category(skill_name: str) -> str:
    """Look up category for a skill."""
    for s in SKILLS:
        if s["name"].lower() == skill_name.lower():
            return s["category"]
    return "default"


def _build_prerequisite_graph(missing_skills: list[str]) -> go.Figure:
    """Build a Plotly network graph showing prerequisite relationships."""
    skill_set = {s.lower() for s in missing_skills}
    case_map = {s.lower(): s for s in missing_skills}

    # Filter edges to skills in the set
    edges = [
        (pre, dep) for pre, dep in PREREQUISITES
        if pre.lower() in skill_set and dep.lower() in skill_set
    ]

    if not edges and len(missing_skills) <= 1:
        return None

    # Assign positions using topological layers
    in_degree = {s.lower(): 0 for s in missing_skills}
    adjacency = {s.lower(): [] for s in missing_skills}
    for pre, dep in edges:
        adjacency[pre.lower()].append(dep.lower())
        in_degree[dep.lower()] += 1

    # BFS to determine layers
    layers = {}
    queue = sorted([s for s in in_degree if in_degree[s] == 0])
    for s in queue:
        layers[s] = 0

    visited = set(queue)
    while queue:
        current = queue.pop(0)
        for neighbor in sorted(adjacency.get(current, [])):
            layers[neighbor] = max(layers.get(neighbor, 0), layers[current] + 1)
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    # Handle any unvisited nodes
    for s in in_degree:
        if s not in layers:
            layers[s] = 0

    # Position nodes
    layer_groups = {}
    for s, layer in layers.items():
        layer_groups.setdefault(layer, []).append(s)

    node_x, node_y = {}, {}
    for layer, nodes in layer_groups.items():
        for i, node in enumerate(sorted(nodes)):
            node_x[node] = layer * 2
            node_y[node] = i - (len(nodes) - 1) / 2

    # Edge traces
    edge_x, edge_y = [], []
    for pre, dep in edges:
        pl, dl = pre.lower(), dep.lower()
        if pl in node_x and dl in node_x:
            edge_x += [node_x[pl], node_x[dl], None]
            edge_y += [node_y[pl], node_y[dl], None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1.5, color="#4F8BF9"),
        hoverinfo="none",
    )

    # Node traces
    nx, ny, labels, colors, hover_texts = [], [], [], [], []
    for s in missing_skills:
        sl = s.lower()
        if sl in node_x:
            nx.append(node_x[sl])
            ny.append(node_y[sl])
            labels.append(case_map.get(sl, s))
            cat = _get_category(s)
            colors.append(CATEGORY_COLORS.get(cat, "#8B949E"))
            est = get_skill_estimates().get(sl, 14)
            hover_texts.append(f"{s}<br>Category: {cat}<br>Est. {est} days")

    node_trace = go.Scatter(
        x=nx, y=ny,
        mode="markers+text",
        text=labels,
        textposition="top center",
        textfont=dict(size=12, color=COLORS["text"]),
        hovertext=hover_texts,
        hoverinfo="text",
        marker=dict(
            size=20,
            color=colors,
            line=dict(width=2, color=COLORS["dark_bg"]),
        ),
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        height=max(350, len(missing_skills) * 50),
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    # Add arrows
    for pre, dep in edges:
        pl, dl = pre.lower(), dep.lower()
        if pl in node_x and dl in node_x:
            fig.add_annotation(
                x=node_x[dl], y=node_y[dl],
                ax=node_x[pl], ay=node_y[pl],
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True,
                arrowhead=2, arrowsize=1.5, arrowwidth=1.5,
                arrowcolor="#4F8BF9",
                opacity=0.6,
            )

    return fig


def render_learning_path():
    """Render the learning path page."""
    render_header("Learning Roadmap", "Your prerequisite-ordered skill development plan")

    result = st.session_state.get("result")

    if not result or not result.get("learning_path"):
        render_empty_state("No learning path available", "")
        st.markdown("""
        <div style="text-align: center;">
            <p style="color: #8B949E; font-size: 14px;">
                Run an analysis first to generate your learning roadmap.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    learning_path = result["learning_path"]
    missing_skills = result.get("missing_skills", [])
    total_days = sum(s.get("estimated_days", 0) for s in learning_path)
    total_weeks = sum(s.get("estimated_weeks", 0) for s in learning_path)

    # ── Summary Stats ────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Skills to Learn", str(len(learning_path)), icon="", color="purple")
    with c2:
        render_metric_card("Total Days", str(total_days), icon="", color="blue")
    with c3:
        render_metric_card("Total Weeks", str(total_weeks), icon="", color="green")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Prerequisite Graph ───────────────────────────────────────────────
    st.markdown("""
    <div class="content-card">
        <h3>Skill Prerequisite Graph</h3>
    """, unsafe_allow_html=True)

    fig = _build_prerequisite_graph(missing_skills)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown('<p style="color: #8B949E;">Single skill — no prerequisite dependencies to display.</p>', unsafe_allow_html=True)

    # Category legend
    categories_used = set()
    for s in missing_skills:
        categories_used.add(_get_category(s))

    legend_html = '<div style="display: flex; flex-wrap: wrap; gap: 16px; margin-top: 12px;">'
    for cat in sorted(categories_used):
        color = CATEGORY_COLORS.get(cat, "#8B949E")
        legend_html += f"""
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background: {color};"></div>
            <span style="font-size: 12px; color: #8B949E; text-transform: capitalize;">{cat}</span>
        </div>
        """
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Learning Timeline ────────────────────────────────────────────────
    st.markdown("""
    <div class="content-card">
        <h3>Step-by-Step Learning Path</h3>
    """, unsafe_allow_html=True)
    render_timeline(learning_path)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detailed Table ───────────────────────────────────────────────────
    st.markdown("""
    <div class="content-card">
        <h3>Detailed Breakdown</h3>
    """, unsafe_allow_html=True)

    headers = ["#", "Skill", "Category", "Days", "Weeks"]
    rows = []
    for i, step in enumerate(learning_path, 1):
        skill = step.get("skill", "Unknown")
        cat = _get_category(skill)
        days = step.get("estimated_days", 14)
        weeks = step.get("estimated_weeks", 2)
        rows.append([str(i), skill, cat.capitalize(), str(days), str(weeks)])

    rows.append(["", "<strong>Total</strong>", "", f"<strong>{total_days}</strong>", f"<strong>{total_weeks}</strong>"])

    render_table(headers, rows)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    export_text = "SkillVector Learning Path\n" + "=" * 40 + "\n\n"
    for i, step in enumerate(learning_path, 1):
        export_text += f"{i}. {step['skill']} — {step.get('estimated_days', 14)} days\n"
    export_text += f"\nTotal: {total_days} days ({total_weeks} weeks)\n"

    st.download_button(
        "Download Learning Path",
        data=export_text,
        file_name="skillvector_learning_path.txt",
        mime="text/plain",
        use_container_width=True,
    )
