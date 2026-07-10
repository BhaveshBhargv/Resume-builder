"""Page 8: ATS Match -- paste/upload a job description and see how well the
resume matches it (Phase 3).

Everything here is analysis-only: it reports the match score and which of the
job's keywords are present vs missing in the resume. It never edits the
resume or suggests claiming a skill the user doesn't have -- "missing"
keywords are shown purely as information, framed as "add these *if* you
genuinely have the experience".
"""
import streamlit as st

from utils.ats_analyzer import analyze
from utils.navigation import render_prev_next, render_top_nav
from utils.resume_parser import extract_text
from utils.session_manager import get_job_description, get_resume_data, init_session_state, set_job_description

init_session_state()
render_top_nav("ats")

st.title("🎯 ATS Match")
st.caption(
    "Paste (or upload) a job description to see how well your resume matches it. "
    "The score reflects how many of the job's keywords already appear in your resume."
)

resume = get_resume_data()
resume_text = resume.searchable_text()

if not resume_text.strip():
    st.info("Your resume is empty. Fill in some sections first (or upload a resume), then come back here.")
    render_prev_next("ats")
    st.stop()

# --- Job description input (paste or upload) -----------------------------------
# The uploader sits outside the form: uploading a file triggers a rerun that
# pre-fills the text area below with the file's text.
uploaded = st.file_uploader("Upload a job description (optional)", type=["pdf", "docx", "txt"])
if uploaded is not None:
    try:
        set_job_description(extract_text(uploaded.getvalue(), uploaded.name))
    except Exception as exc:  # noqa: BLE001 -- surface any parse error to the user
        st.error(f"Couldn't read that file: {exc}")

# The text area + Analyze button live in a form so nothing is submitted until
# the user clicks Analyze (typing the JD doesn't rerun the page each keystroke).
with st.form("jd_form"):
    jd_text = st.text_area(
        "Job description",
        value=get_job_description(),
        height=240,
        placeholder="Paste the full job description here...",
    )
    analyze_clicked = st.form_submit_button("🔍 Analyze Match", type="primary")

if analyze_clicked:
    set_job_description(jd_text)
    if not jd_text.strip():
        st.warning("Please paste or upload a job description first.")
        st.stop()

    result = analyze(resume_text, jd_text)

    # --- Score summary ---------------------------------------------------------
    st.divider()
    col_score, col_sim = st.columns(2)
    with col_score:
        st.metric("ATS Match Score", f"{result.score}%")
        st.progress(result.score / 100)
        st.caption(f"{len(result.matched)} of {result.total_keywords} job keywords found in your resume.")
    with col_sim:
        st.metric("Overall Text Similarity", f"{result.similarity}%")
        st.progress(result.similarity / 100)
        st.caption("TF-IDF cosine similarity between the full texts of your resume and the job description.")

    if result.score >= 75:
        st.success("Strong match. Your resume already covers most of this job's keywords.")
    elif result.score >= 50:
        st.info("Moderate match. Worth strengthening the missing keywords below where you genuinely qualify.")
    else:
        st.warning("Low keyword match. See the missing keywords below.")

    # --- Matched keywords ------------------------------------------------------
    st.divider()
    st.subheader(f"✅ Matched keywords ({len(result.matched)})")
    if result.matched:
        st.markdown(" ".join(f":green-background[{kw}]" for kw in result.matched))
    else:
        st.caption("None of the job's keywords were found in your resume.")

    # --- Missing keywords ------------------------------------------------------
    st.subheader(f"❌ Missing keywords ({len(result.missing)})")
    if result.missing:
        st.markdown(" ".join(f":red-background[{kw}]" for kw in result.missing))
        st.caption(
            "These appear in the job description but not in your resume. Add them **only if you "
            "genuinely have that experience** -- the app never fabricates skills for you."
        )
    else:
        st.caption("Nothing missing -- every keyword from the job description is already in your resume.")

render_prev_next("ats")
