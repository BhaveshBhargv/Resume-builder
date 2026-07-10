"""Page 3: Work experience form. Supports multiple entries with bullet points.

Each entry's fields live inside an st.form so nothing is written back to the
ResumeData model until the user clicks "Save Entry" -- typing no longer
triggers a script rerun on every keystroke, which also keeps the expander
open while editing (see the `key=` on st.expander below).
"""
import streamlit as st

from utils.date_picker import is_start_after_end, month_year_input
from utils.navigation import render_prev_next, render_top_nav
from utils.session_manager import add_experience, get_resume_data, init_session_state, remove_experience

init_session_state()
render_top_nav("experience")
resume = get_resume_data()

st.title("💼 Work Experience")
st.caption(
    "Add one entry per role, most recent first. Write bullet points describing what you "
    "actually did -- these can be refined later, but never invented."
)

if st.button("➕ Add Experience Entry"):
    add_experience()
    st.rerun()

if not resume.experience:
    st.info("No experience entries yet. Click **Add Experience Entry** to start.")

for entry in resume.experience:
    with st.expander(
        f"💼 {entry.job_title or 'New Role'} at {entry.company or 'Company'}",
        expanded=not entry.company,
        key=f"exp_exp_{entry.id}",
    ):
        with st.form(f"exp_form_{entry.id}"):
            col1, col2 = st.columns(2)
            with col1:
                job_title = st.text_input("Job Title *", value=entry.job_title, key=f"exp_title_{entry.id}")
                company = st.text_input("Company *", value=entry.company, key=f"exp_company_{entry.id}")
            with col2:
                location = st.text_input("Location", value=entry.location, key=f"exp_loc_{entry.id}")
                is_current = st.checkbox(
                    "I currently work here", value=entry.is_current, key=f"exp_current_{entry.id}"
                )

            st.markdown("**Start Date**")
            start_date = month_year_input(entry.start_date, key_prefix=f"exp_start_{entry.id}")
            st.markdown("**End Date** (ignored if 'I currently work here' is checked)")
            end_date = month_year_input(entry.end_date, key_prefix=f"exp_end_{entry.id}")

            bullets_text = st.text_area(
                "Responsibilities & Achievements (one bullet per line) *",
                value="\n".join(entry.bullet_points),
                key=f"exp_bullets_{entry.id}",
                height=140,
                help="Describe what you actually did. Use action verbs and, where possible, quantify results.",
            )

            submitted = st.form_submit_button("💾 Save Entry", type="primary")

        if submitted:
            errors = []
            if not job_title or not company:
                errors.append("Job Title and Company are required.")
            if not is_current and is_start_after_end(start_date, end_date):
                errors.append("Start Date cannot be after End Date.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                entry.job_title = job_title.strip()
                entry.company = company.strip()
                entry.location = location.strip()
                entry.is_current = is_current
                entry.start_date = start_date
                entry.end_date = "Present" if is_current else end_date
                entry.bullet_points = [line.strip() for line in bullets_text.split("\n") if line.strip()]
                st.success("Entry saved.")

        if st.button("🗑️ Remove This Entry", key=f"exp_remove_{entry.id}"):
            remove_experience(entry.id)
            st.rerun()

render_prev_next("experience")
