"""Export a ResumeData object to an ATS-friendly PDF document (reportlab).

Same philosophy as the .docx export: a single column, standard fonts
(Helvetica), plain section headings with a thin rule, and real bullet lists.
No multi-column layouts, tables, or graphics, so applicant-tracking systems
can extract the text cleanly.
"""
from __future__ import annotations

from io import BytesIO
from typing import List
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

from models.resume_data import ResumeData


def _date_range(start: str, end: str, is_current: bool) -> str:
    end_text = "Present" if is_current else end
    if start and end_text:
        return f"{start} – {end_text}"
    return start or end_text or ""


def _styles():
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle("Name", parent=base["Title"], fontSize=20, spaceAfter=2, alignment=TA_CENTER),
        "contact": ParagraphStyle("Contact", parent=base["Normal"], fontSize=8.5, alignment=TA_CENTER, spaceAfter=6),
        "heading": ParagraphStyle("SectionHeading", parent=base["Normal"], fontName="Helvetica-Bold",
                                   fontSize=11.5, spaceBefore=10, spaceAfter=2, textColor="#222222"),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontSize=10, leading=13, spaceAfter=2),
        "entry": ParagraphStyle("Entry", parent=base["Normal"], fontSize=10, leading=13, spaceBefore=4),
        "bullet": ParagraphStyle("Bullet", parent=base["Normal"], fontSize=10, leading=13),
    }


def build_pdf(resume: ResumeData) -> bytes:
    """Render the resume to PDF bytes suitable for st.download_button."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        topMargin=0.55 * inch, bottomMargin=0.55 * inch,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        title="Resume",
    )
    s = _styles()
    story: List = []

    def heading(text: str) -> None:
        story.append(Paragraph(escape(text.upper()), s["heading"]))
        story.append(HRFlowable(width="100%", thickness=0.6, color="#888888", spaceBefore=1, spaceAfter=4))

    def bullets(items: List[str]) -> None:
        rows = [ListItem(Paragraph(escape(b), s["bullet"]), leftIndent=12) for b in items if b]
        if rows:
            story.append(ListFlowable(rows, bulletType="bullet", start="•", leftIndent=10, spaceAfter=2))

    pi = resume.personal_info

    # --- Header ---------------------------------------------------------------
    story.append(Paragraph(escape(pi.full_name or "Your Name"), s["name"]))
    contact = " | ".join(
        bit for bit in [pi.email, pi.phone, pi.location, pi.linkedin_url, pi.portfolio_url] if bit
    )
    if contact:
        story.append(Paragraph(escape(contact), s["contact"]))

    # --- Professional summary -------------------------------------------------
    if pi.professional_summary:
        heading("Professional Summary")
        story.append(Paragraph(escape(pi.professional_summary), s["body"]))

    # --- Experience -----------------------------------------------------------
    if resume.experience:
        heading("Experience")
        for exp in resume.experience:
            title = ", ".join(x for x in [exp.job_title, exp.company] if x)
            meta = " | ".join(x for x in [exp.location, _date_range(exp.start_date, exp.end_date, exp.is_current)] if x)
            header = f"<b>{escape(title)}</b>" + (f"  —  {escape(meta)}" if meta else "")
            story.append(Paragraph(header, s["entry"]))
            bullets(exp.bullet_points)

    # --- Education ------------------------------------------------------------
    if resume.education:
        heading("Education")
        for edu in resume.education:
            degree = ", ".join(x for x in [edu.degree, edu.field_of_study] if x)
            title = " — ".join(x for x in [degree, edu.institution] if x)
            extras = [_date_range(edu.start_date, edu.end_date, edu.is_current)]
            if edu.gpa:
                extras.append(f"GPA: {edu.gpa}")
            meta = " | ".join(x for x in extras if x)
            header = f"<b>{escape(title)}</b>" + (f"  —  {escape(meta)}" if meta else "")
            story.append(Paragraph(header, s["entry"]))
            bullets(edu.achievements)

    # --- Projects -------------------------------------------------------------
    if resume.projects:
        heading("Projects")
        for proj in resume.projects:
            header = f"<b>{escape(proj.name or 'Project')}</b>"
            if proj.technologies:
                header += f"  —  {escape(', '.join(proj.technologies))}"
            story.append(Paragraph(header, s["entry"]))
            if proj.description:
                story.append(Paragraph(escape(proj.description), s["body"]))
            bullets(proj.bullet_points)
            if proj.url:
                story.append(Paragraph(escape(proj.url), s["body"]))

    # --- Skills ---------------------------------------------------------------
    if any(cat.skills for cat in resume.skills):
        heading("Skills")
        for cat in resume.skills:
            if cat.skills:
                story.append(Paragraph(f"<b>{escape(cat.category_name)}:</b> {escape(', '.join(cat.skills))}", s["body"]))

    # --- Extra sections -------------------------------------------------------
    for extra in resume.extra_sections:
        if extra.heading or extra.content:
            heading(extra.heading or "Additional Information")
            if extra.content:
                story.append(Paragraph(escape(extra.content).replace("\n", "<br/>"), s["body"]))

    doc.build(story)
    return buffer.getvalue()
