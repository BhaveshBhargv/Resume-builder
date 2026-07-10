"""Page 2: Education form. Supports multiple entries (degrees, certifications).

Each entry's fields live inside an st.form so nothing is written back to the
ResumeData model until the user clicks "Save Entry" -- typing no longer
triggers a script rerun on every keystroke, which also keeps the expander
open while editing (see the `key=` on st.expander below).
"""
import streamlit as st

from utils.date_picker import is_start_after_end, month_year_input
from utils.navigation import render_prev_next, render_top_nav
from utils.session_manager import add_education, get_resume_data, init_session_state, remove_education

init_session_state()
render_top_nav("education")
resume = get_resume_data()

st.title("🎓 Education")
st.caption("Add one entry per degree or certification, most recent first.")

if st.button("➕ Add Education Entry"):
    add_education()
    st.rerun()

if not resume.education:
    st.info("No education entries yet. Click **Add Education Entry** to start.")

for entry in resume.education:
    with st.expander(
        f"🎓 {entry.institution or 'New Entry'} — {entry.degree or 'Untitled'}",
        expanded=not entry.institution,
        key=f"edu_exp_{entry.id}",
    ):
        with st.form(f"edu_form_{entry.id}"):
            col1, col2 = st.columns(2)
            with col1:
                institution = st.text_input("Institution *", value=entry.institution, key=f"edu_inst_{entry.id}")
                degree = st.text_input("Degree *", value=entry.degree, key=f"edu_degree_{entry.id}")
                field_of_study = st.text_input(
                    "Field of Study", value=entry.field_of_study, key=f"edu_field_{entry.id}"
                )
            with col2:
                try:
                    gpa_default = float(entry.gpa) if entry.gpa else 0.0
                except ValueError:
                    gpa_default = 0.0
                gpa = st.number_input(
                    "GPA (optional, leave at 0 if not applicable)",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.01,
                    format="%.2f",
                    value=gpa_default,
                    key=f"edu_gpa_{entry.id}",
                )
                is_current = st.checkbox(
                    "Currently studying here", value=entry.is_current, key=f"edu_current_{entry.id}"
                )

            st.markdown("**Start Date**")
            start_date = month_year_input(entry.start_date, key_prefix=f"edu_start_{entry.id}")
            st.markdown("**End Date** (ignored if 'Currently studying here' is checked)")
            end_date = month_year_input(entry.end_date, key_prefix=f"edu_end_{entry.id}")

            achievements_text = st.text_area(
                "Achievements / Honors (one per line, optional)",
                value="\n".join(entry.achievements),
                key=f"edu_ach_{entry.id}",
                height=80,
            )

            submitted = st.form_submit_button("💾 Save Entry", type="primary")

        if submitted:
            errors = []
            if not institution or not degree:
                errors.append("Institution and Degree are required.")
            if not is_current and is_start_after_end(start_date, end_date):
                errors.append("Start Date cannot be after End Date.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                entry.institution = institution.strip()
                entry.degree = degree.strip()
                entry.field_of_study = field_of_study.strip()
                entry.gpa = f"{gpa:.2f}" if gpa > 0 else ""
                entry.is_current = is_current
                entry.start_date = start_date
                entry.end_date = "Present" if is_current else end_date
                entry.achievements = [line.strip() for line in achievements_text.split("\n") if line.strip()]
                st.success("Entry saved.")

        if st.button("🗑️ Remove This Entry", key=f"edu_remove_{entry.id}"):
            remove_education(entry.id)
            st.rerun()

render_prev_next("education")
