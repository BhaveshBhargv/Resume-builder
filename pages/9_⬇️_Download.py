"""Page 9: Download the finished resume as an ATS-friendly Word or PDF file."""
import re

import streamlit as st

from utils import docx_export, pdf_export
from utils.navigation import render_prev_next, render_top_nav
from utils.session_manager import get_resume_data, init_session_state

_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

init_session_state()
render_top_nav("download")
resume = get_resume_data()

st.title("⬇️ Download Your Resume")

# Something to export? (any content at all)
has_content = bool(resume.personal_info.full_name or resume.searchable_text().strip())
if not has_content:
    st.info("Your resume is empty. Fill in some sections first, then come back to download.")
    render_prev_next("download")
    st.stop()

st.caption(
    "Exports a clean, single-column, ATS-friendly document -- standard fonts and headings, "
    "real bullet lists, no tables or graphics that trackers struggle to read."
)

safe_name = re.sub(r"[^A-Za-z0-9]+", "_", resume.personal_info.full_name).strip("_") or "resume"

col_docx, col_pdf = st.columns(2)
with col_docx:
    st.download_button(
        "⬇️ Download as Word (.docx)",
        data=docx_export.build_docx(resume),
        file_name=f"{safe_name}_resume.docx",
        mime=_DOCX_MIME,
        type="primary",
        width="stretch",
    )
with col_pdf:
    st.download_button(
        "⬇️ Download as PDF",
        data=pdf_export.build_pdf(resume),
        file_name=f"{safe_name}_resume.pdf",
        mime="application/pdf",
        width="stretch",
    )

st.caption("Tip: run the **ATS Match** step against a specific job first, then tweak and re-download.")

render_prev_next("download")
