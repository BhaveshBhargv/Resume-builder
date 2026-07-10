"""Page 7: Review all entered data before moving on to later phases
(ATS matching in Phase 3, AI rewriting and export in Phase 4)."""
import pandas as pd
import streamlit as st

from utils.navigation import render_prev_next, render_top_nav
from utils.session_manager import get_resume_data, init_session_state

init_session_state()
render_top_nav("review")
resume = get_resume_data()

st.title("📄 Review Your Resume Data")

status = resume.completion_status()
missing = [section for section, done in status.items() if not done]
if missing:
    st.warning(f"Incomplete sections: {', '.join(missing)}")
else:
    st.success("All sections have data. Ready for Phase 3 (job description matching).")

st.divider()

st.subheader("👤 Personal Details")
info = resume.personal_info
if info.full_name:
    st.write(f"**{info.full_name}**  \n{info.email} | {info.phone} | {info.location}")
    if info.linkedin_url:
        st.write(info.linkedin_url)
    if info.professional_summary:
        st.write(info.professional_summary)
else:
    st.caption("No data yet.")

st.divider()
st.subheader("🎓 Education")
if resume.education:
    df = pd.DataFrame(
        [
            {
                "Institution": e.institution,
                "Degree": e.degree,
                "Field": e.field_of_study,
                "Start": e.start_date,
                "End": e.end_date,
                "GPA": e.gpa,
            }
            for e in resume.education
        ]
    )
    st.dataframe(df, width="stretch", hide_index=True)
else:
    st.caption("No entries yet.")

st.divider()
st.subheader("💼 Experience")
if resume.experience:
    for e in resume.experience:
        st.markdown(f"**{e.job_title}** — {e.company} ({e.start_date} – {e.end_date})")
        for bullet in e.bullet_points:
            st.markdown(f"- {bullet}")
else:
    st.caption("No entries yet.")

st.divider()
st.subheader("🚀 Projects")
if resume.projects:
    for p in resume.projects:
        tech = ", ".join(p.technologies)
        st.markdown(f"**{p.name}**" + (f" — {tech}" if tech else ""))
        if p.url:
            st.caption(p.url)
        if p.description:
            st.caption(p.description)
        for bullet in p.bullet_points:
            st.markdown(f"- {bullet}")
else:
    st.caption("No entries yet.")

st.divider()
st.subheader("🛠️ Skills")
if resume.skills:
    for s in resume.skills:
        st.markdown(f"**{s.category_name}:** {', '.join(s.skills)}")
else:
    st.caption("No entries yet.")

if resume.extra_sections:
    st.divider()
    st.subheader("📌 Additional Information (from uploaded resume)")
    st.caption("Found in the uploaded file but not auto-filled into a section above.")
    for extra in resume.extra_sections:
        with st.expander(extra.heading):
            st.text(extra.content)

render_prev_next("review")
