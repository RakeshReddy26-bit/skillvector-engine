"""
SkillVector — Beautiful Single Page PDF Report
Uses reportlab canvas for precise pixel-perfect layout
"""

import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm

W, H = A4  # 595 x 842 points

# Colors
C_BG       = colors.HexColor("#080b10")
C_SURFACE  = colors.HexColor("#0d1117")
C_SURFACE2 = colors.HexColor("#141b24")
C_ACCENT   = colors.HexColor("#00e5a0")
C_PURPLE   = colors.HexColor("#7c6fff")
C_DANGER   = colors.HexColor("#ef4444")
C_WARN     = colors.HexColor("#f59e0b")
C_TEXT     = colors.HexColor("#e8edf5")
C_MUTED    = colors.HexColor("#5a6478")
C_BORDER   = colors.HexColor("#1e2a3a")
C_WHITE    = colors.white


def priority_color(p):
    p = (p or "").upper()
    if p == "HIGH":   return C_DANGER
    if p == "MEDIUM": return C_WARN
    return C_PURPLE


def score_color(s):
    if s >= 70: return C_ACCENT
    if s >= 40: return C_WARN
    return C_DANGER


def draw_rounded_rect(c, x, y, w, h, r=6, fill=None, stroke=None, stroke_width=0.5):
    p = c.beginPath()
    p.moveTo(x + r, y)
    p.lineTo(x + w - r, y)
    p.arcTo(x + w - r, y, x + w, y + r, -90, 90)
    p.lineTo(x + w, y + h - r)
    p.arcTo(x + w - r, y + h - r, x + w, y + h, 0, 90)
    p.lineTo(x + r, y + h)
    p.arcTo(x, y + h - r, x + r, y + h, 90, 90)
    p.lineTo(x, y + r)
    p.arcTo(x, y, x + r, y + r, 180, 90)
    p.close()
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(stroke_width)
    if fill and stroke:
        c.drawPath(p, fill=1, stroke=1)
    elif fill:
        c.drawPath(p, fill=1, stroke=0)
    elif stroke:
        c.drawPath(p, fill=0, stroke=1)


def draw_score_ring(c, cx, cy, score, col):
    import math
    radius = 32
    thickness = 7

    # Background ring
    c.setStrokeColor(C_BORDER)
    c.setLineWidth(thickness)
    c.circle(cx, cy, radius, fill=0, stroke=1)

    # Score arc
    angle = 360 * (score / 100)
    start = 90

    c.setStrokeColor(col)
    c.setLineWidth(thickness)
    c.setLineCap(1)

    steps = max(int(angle / 2), 1)
    for i in range(steps):
        a1 = math.radians(start - i * (angle / steps))
        a2 = math.radians(start - (i + 1) * (angle / steps))
        x1 = cx + radius * math.cos(a1)
        y1 = cy + radius * math.sin(a1)
        x2 = cx + radius * math.cos(a2)
        y2 = cy + radius * math.sin(a2)
        c.line(x1, y1, x2, y2)

    # Glow dot at start
    c.setFillColor(col)
    gx = cx + radius * math.cos(math.radians(start))
    gy = cy + radius * math.sin(math.radians(start))
    c.circle(gx, gy, thickness / 2, fill=1, stroke=0)

    # Score text inside
    c.setFillColor(col)
    score_font = "Helvetica-Bold"
    score_size = 28
    c.setFont(score_font, score_size)
    score_txt = f"{score}%"
    face = pdfmetrics.getFont(score_font).face
    ascent = (face.ascent / 1000.0) * score_size
    descent = (face.descent / 1000.0) * score_size
    score_y = cy - ((ascent + descent) / 2.0)
    c.drawCentredString(cx, score_y, score_txt)

    c.setFillColor(C_MUTED)
    c.setFont("Helvetica", 7)
    score_bottom = score_y + descent
    c.drawCentredString(cx, score_bottom - 10, "MATCH")


def truncate(text, max_chars):
    return text if len(text) <= max_chars else text[:max_chars - 1] + "..."


def generate_pdf_report(analysis_result: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    score        = round(analysis_result.get("match_score", 0))
    target_role  = analysis_result.get("target_role", "")
    missing      = analysis_result.get("missing_skills", [])
    learning     = analysis_result.get("learning_path", [])
    evidence     = analysis_result.get("evidence", [])
    jobs         = analysis_result.get("related_jobs", [])
    req_id       = analysis_result.get("request_id", "-")
    latency      = analysis_result.get("latency_ms", 0)
    generated    = datetime.now().strftime("%d %b %Y  %H:%M")
    generated_card = datetime.now().strftime("%B %d, %Y")
    sc           = score_color(score)

    margin = 22

    # FULL BACKGROUND
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # HEADER BAR
    header_h = 54
    c.setFillColor(C_SURFACE)
    c.rect(0, H - header_h, W, header_h, fill=1, stroke=0)
    c.setFillColor(C_ACCENT)
    c.rect(0, H - header_h, 3, header_h, fill=1, stroke=0)
    c.setFillColor(C_ACCENT)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin + 10, H - 32, "SkillVector")
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(margin + 10, H - 44, "AI CAREER INTELLIGENCE REPORT")
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawRightString(W - margin, H - 28, generated)
    c.drawRightString(W - margin, H - 40, f"ID: {req_id}")
    draw_rounded_rect(c, W - margin - 75, H - 48, 60, 14,
                      r=4, fill=colors.HexColor("#0a2a1f"))
    c.setFillColor(C_ACCENT)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(W - margin - 45, H - 39, "v3.0  PRODUCTION")

    y = H - header_h - 16

    # SCORE + ROLE CARD
    card_h = 88
    draw_rounded_rect(c, margin, y - card_h, W - 2 * margin, card_h,
                      r=8, fill=C_SURFACE, stroke=C_BORDER)
    ring_cx = margin + 58
    ring_cy = y - card_h / 2 - 2
    draw_score_ring(c, ring_cx, ring_cy, score, sc)
    c.setStrokeColor(C_BORDER)
    c.setLineWidth(0.7)
    c.line(margin + 102, y - 10, margin + 102, y - card_h + 10)
    label = "Strong Match" if score >= 70 else ("Moderate Match" if score >= 40 else "Needs Development")
    c.setFillColor(sc)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 112, y - 22, label.upper())
    c.setFillColor(C_TEXT)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin + 112, y - 38, truncate(target_role, 38))
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(margin + 112, y - 52,
                 "Resume analyzed against job requirements")
    c.drawString(margin + 112, y - 62,
                 f"Analyzed on {generated_card}   .   {len(missing)} skill gaps   .   {latency/1000:.1f}s")
    chip_x = margin + 112
    chip_y = y - 78
    for skill_item in missing[:5]:
        sname = skill_item.get("skill", str(skill_item)) if isinstance(skill_item, dict) else str(skill_item)
        sname = truncate(sname, 14)
        pri   = skill_item.get("priority", "LOW") if isinstance(skill_item, dict) else "LOW"
        col   = priority_color(pri)
        sw    = c.stringWidth(sname, "Helvetica", 7) + 12
        draw_rounded_rect(c, chip_x, chip_y - 2, sw, 13, r=3,
                          fill=colors.HexColor("#0d1117"), stroke=col, stroke_width=0.7)
        c.setFillColor(col)
        c.setFont("Helvetica", 7)
        c.drawString(chip_x + 6, chip_y + 4, sname)
        chip_x += sw + 6

    y -= card_h + 12

    # TWO COLUMN LAYOUT
    col_w   = (W - 2 * margin - 10) / 2
    left_x  = margin
    right_x = margin + col_w + 10

    # LEFT COL: SKILL GAPS
    c.setFillColor(C_ACCENT)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left_x, y, "01  SKILL GAPS")
    c.setStrokeColor(C_ACCENT)
    c.setLineWidth(0.5)
    c.line(left_x + 72, y + 4, left_x + col_w, y + 4)

    skill_card_h = 44
    skill_row_gap = 6
    sy = y - 14
    for skill_item in missing[:5]:
        sname = skill_item.get("skill", str(skill_item)) if isinstance(skill_item, dict) else str(skill_item)
        pri   = skill_item.get("priority", "MEDIUM") if isinstance(skill_item, dict) else "MEDIUM"
        why   = skill_item.get("why", "") if isinstance(skill_item, dict) else ""
        col   = priority_color(pri)
        card_top = sy
        card_y = card_top - skill_card_h
        draw_rounded_rect(c, left_x, card_y, col_w, skill_card_h, r=5,
                          fill=C_SURFACE, stroke=C_BORDER)
        c.setFillColor(col)
        c.rect(left_x, card_y, 3, skill_card_h, fill=1, stroke=0)
        c.setFillColor(col)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(left_x + 8, card_top - 14, truncate(sname, 35))
        c.setFillColor(C_MUTED)
        c.setFont("Helvetica", 6.5)
        c.drawString(left_x + 8, card_top - 26, truncate(why, 65))
        bw = c.stringWidth(pri, "Helvetica-Bold", 6) + 16
        badge_h = 11
        badge_y = card_y + (skill_card_h - badge_h) / 2
        badge_x = left_x + col_w - bw - 8
        draw_rounded_rect(c, badge_x, badge_y, bw, badge_h,
                          r=3, fill=col)
        c.setFillColor(C_BG)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(badge_x + bw / 2, badge_y + 2.5, pri)
        sy -= skill_card_h + skill_row_gap

    # RIGHT COL: LEARNING PATH
    c.setFillColor(C_ACCENT)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(right_x, y, "02  LEARNING PATH")
    c.setStrokeColor(C_ACCENT)
    c.setLineWidth(0.5)
    c.line(right_x + 100, y + 4, right_x + col_w, y + 4)

    learning_card_h = 44
    learning_row_gap = 6
    ly = y - 14
    for i, step in enumerate(learning[:5]):
        sname = step.get("skill", str(step)) if isinstance(step, dict) else str(step)
        desc  = step.get("description", "") if isinstance(step, dict) else ""
        card_top = ly
        card_y = card_top - learning_card_h
        draw_rounded_rect(c, right_x, card_y, col_w, learning_card_h, r=5,
                          fill=C_SURFACE, stroke=C_BORDER)
        cx2 = right_x + 14
        cy2 = card_y + learning_card_h / 2
        c.setFillColor(C_ACCENT)
        c.circle(cx2, cy2, 8, fill=1, stroke=0)
        c.setFillColor(C_BG)
        c.setFont("Helvetica-Bold", 7)
        nw = c.stringWidth(str(i + 1), "Helvetica-Bold", 7)
        c.drawString(cx2 - nw / 2, cy2 - 3, str(i + 1))
        if i < len(learning[:5]) - 1:
            c.setStrokeColor(C_BORDER)
            c.setLineWidth(0.8)
            next_card_top = ly - (learning_card_h + learning_row_gap)
            c.line(right_x + 14, card_y, right_x + 14, next_card_top)
        c.setFillColor(C_TEXT)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(right_x + 28, card_top - 14, truncate(sname, 32))
        c.setFillColor(C_MUTED)
        c.setFont("Helvetica", 6.5)
        c.drawString(right_x + 28, card_top - 26, truncate(desc, 45))
        ly -= learning_card_h + learning_row_gap

    y = min(sy, ly) - 14

    # EVIDENCE PROJECTS
    c.setFillColor(C_PURPLE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left_x, y, "03  EVIDENCE BUILDER")
    c.setStrokeColor(C_PURPLE)
    c.setLineWidth(0.5)
    c.line(left_x + 116, y + 4, W - margin, y + 4)

    ey    = y - 14
    ecols = 2
    ew    = (W - 2 * margin - 10) / ecols
    for i, ev in enumerate(evidence[:4]):
        ex     = left_x + (i % ecols) * (ew + 10)
        ecy    = ey if i < ecols else ey - 62
        ptitle = ev.get("project_title", str(ev)) if isinstance(ev, dict) else str(ev)
        skill  = ev.get("skill_covered", "") if isinstance(ev, dict) else ""
        pdesc  = ev.get("description", "") if isinstance(ev, dict) else ""
        deliv  = ev.get("deliverables", []) if isinstance(ev, dict) else []
        draw_rounded_rect(c, ex, ecy - 54, ew, 58, r=5,
                          fill=C_SURFACE, stroke=C_BORDER)
        c.setFillColor(C_BORDER)
        c.rect(ex, ecy - 54, ew, 2, fill=1, stroke=0)
        tw2 = c.stringWidth(skill, "Helvetica-Bold", 6) + 8
        draw_rounded_rect(c, ex + 8, ecy - 12, tw2, 11,
                          r=3, fill=colors.HexColor("#1a1040"), stroke=C_PURPLE, stroke_width=0.5)
        c.setFillColor(C_PURPLE)
        c.setFont("Helvetica-Bold", 6)
        c.drawString(ex + 12, ecy - 5, skill)
        c.setFillColor(C_TEXT)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(ex + 8, ecy - 24, truncate(ptitle, 38))
        c.setFillColor(C_MUTED)
        c.setFont("Helvetica", 6.5)
        c.drawString(ex + 8, ecy - 35, truncate(pdesc, 40))
        dtext = "  .  ".join([truncate(d, 16) for d in deliv[:2]])
        c.setFillColor(C_MUTED)
        c.setFont("Helvetica", 6)
        c.drawString(ex + 8, ecy - 46, truncate(dtext, 50))

    y -= 140

    # MATCHING JOBS
    if jobs:
        c.setFillColor(C_ACCENT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(left_x, y, "04  MATCHING JOBS")
        c.setStrokeColor(C_ACCENT)
        c.setLineWidth(0.5)
        c.line(left_x + 100, y + 4, W - margin, y + 4)

        jy    = y - 14
        jcols = 2
        jw    = (W - 2 * margin - 8) / jcols
        for i, job in enumerate(jobs[:4]):
            jx   = left_x + (i % jcols) * (jw + 8)
            jcy  = jy if i < jcols else jy - 36
            ms   = job.get("match_score", 0) if isinstance(job, dict) else 0
            jt   = job.get("title", "") if isinstance(job, dict) else str(job)
            url  = job.get("apply_url", "") if isinstance(job, dict) else ""
            jcol = score_color(ms)
            draw_rounded_rect(c, jx, jcy - 28, jw, 30, r=5,
                              fill=C_SURFACE, stroke=C_BORDER)
            msw = c.stringWidth(f"{ms}%", "Helvetica-Bold", 12) + 4
            c.setFillColor(jcol)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(jx + 8, jcy - 12, f"{ms}%")
            c.setStrokeColor(C_BORDER)
            c.setLineWidth(0.5)
            c.line(jx + msw + 10, jcy - 4, jx + msw + 10, jcy - 24)
            c.setFillColor(C_TEXT)
            c.setFont("Helvetica-Bold", 7.5)
            c.drawString(jx + msw + 16, jcy - 10, truncate(jt, 22))
            c.setFillColor(C_MUTED)
            c.setFont("Helvetica", 6.5)
            c.drawString(jx + msw + 16, jcy - 22,
                         truncate(url.replace("https://", "").replace("www.", ""), 28))

    # FOOTER
    fy = 18
    c.setFillColor(C_SURFACE)
    c.rect(0, 0, W, fy + 10, fill=1, stroke=0)
    c.setFillColor(C_ACCENT)
    c.rect(0, fy + 10, W, 0.5, fill=1, stroke=0)
    c.setFillColor(C_MUTED)
    c.setFont("Helvetica", 6.5)
    c.drawString(margin, fy + 2,
                 "SkillVector  .  AI Career Intelligence  .  Powered by Claude Sonnet  .  skillevector.app")
    c.drawRightString(W - margin, fy + 2,
                      f"Generated {generated}  .  Open source on GitHub")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
