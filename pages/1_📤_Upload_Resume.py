"""Page 1: Upload an existing resume to pre-fill the forms, or skip to manual entry.

Parsing (utils/resume_parser.py) is best-effort, rule-based extraction, not
AI -- it only ever transcribes what the uploaded file actually says, never
invents anything. The parsed values are loaded into the resume data
immediately (so they show up on every page, including Review) rather than
held in a separate pending state, since the user explicitly asked for the
upload to fill everything in. What it doesn't do is guarantee accuracy:
parsing can misread a line, so each page's own "Save" button still exists to
correct anything before you'd export or send the resume anywhere. Anything
the parser can't confidently map to a known section is kept verbatim below
and on the Review page, tagged with its original heading from the resume, so
nothing from the uploaded file is silently lost.
"""
import streamlit as st

from utils.navigation import render_prev_next, render_top_nav
from utils.resume_parser import parse_resume
from utils.session_manager import get_resume_data, init_session_state, set_resume_data

init_session_state()
render_top_nav("upload")

st.title("📤 Upload an Existing Resume")
st.caption(
    "Upload a resume and we'll pre-fill Personal Details, Education, Experience, "
    "Projects, and Skills for you. Parsing is best-effort -- please check each "
    "page afterward and correct anything that wasn't read correctly."
)

resume = get_resume_data()
has_existing_data = any(resume.completion_status().values()) or bool(resume.extra_sections)

uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    if has_existing_data:
        st.warning(
            "You already have resume data entered in this session. Parsing this "
            "file will replace it -- Personal Details, Education, Experience, "
            "Projects, and Skills will all be overwritten."
        )
    if st.button("🔍 Parse This Resume", type="primary"):
        try:
            parsed = parse_resume(uploaded_file.getvalue(), uploaded_file.name)
        except Exception as exc:
            st.error(f"Couldn't read that file: {exc}")
        else:
            set_resume_data(parsed)
            st.success("Resume parsed. Review the summary below, then use the page buttons above to check each section.")
            st.rerun()

resume = get_resume_data()
if has_existing_data:
    st.divider()
    st.subheader("Currently Loaded")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Education", len(resume.education))
    col2.metric("Experience", len(resume.experience))
    col3.metric("Projects", len(resume.projects))
    col4.metric("Skill categories", len(resume.skills))

    if resume.extra_sections:
        st.subheader("Additional Information Found")
        st.caption(
            "These sections from the uploaded file didn't match a known category, "
            "so nothing was auto-filled from them. Copy anything relevant into the "
            "right page yourself -- it's shown here so nothing gets lost."
        )
        for extra in resume.extra_sections:
            with st.expander(f"📌 {extra.heading}"):
                st.text(extra.content)

st.divider()
st.markdown("**Prefer to start from scratch?**")
if st.button("✍️ Enter Details Manually"):
    st.switch_page("pages/2_👤_Personal_Details.py")

render_prev_next("upload")
