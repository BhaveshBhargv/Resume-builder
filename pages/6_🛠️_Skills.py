"""Page 5: Skills form. Skills are grouped into categories (e.g. 'Languages', 'Tools').

Each category's fields live inside an st.form so nothing is written back to
the ResumeData model until the user clicks "Save Category" -- typing no
longer triggers a script rerun on every keystroke, which also keeps the
expander open while editing (see the `key=` on st.expander below).
"""
import streamlit as st

from utils.navigation import render_prev_next, render_top_nav
from utils.session_manager import add_skill_category, get_resume_data, init_session_state, remove_skill_category

init_session_state()
render_top_nav("skills")
resume = get_resume_data()

st.title("🛠️ Skills")
st.caption(
    "Group your skills into categories. Only list skills you actually have -- "
    "these will be matched against job descriptions in Phase 2."
)

if st.button("➕ Add Skill Category"):
    add_skill_category()
    st.rerun()

if not resume.skills:
    st.info("No skill categories yet. Click **Add Skill Category** to start (e.g. 'Programming Languages').")

for entry in resume.skills:
    with st.expander(
        f"🛠️ {entry.category_name or 'New Category'} ({len(entry.skills)} skills)",
        expanded=not entry.category_name,
        key=f"skill_exp_{entry.id}",
    ):
        with st.form(f"skill_form_{entry.id}"):
            category_name = st.text_input(
                "Category Name *",
                value=entry.category_name,
                key=f"skill_cat_{entry.id}",
                placeholder="e.g. Programming Languages, Tools & Frameworks, Soft Skills",
            )
            skills_text = st.text_input(
                "Skills (comma-separated) *",
                value=", ".join(entry.skills),
                key=f"skill_list_{entry.id}",
                placeholder="e.g. Python, SQL, Git",
            )

            submitted = st.form_submit_button("💾 Save Category", type="primary")

        if submitted:
            if not category_name or not skills_text:
                st.error("Category Name and at least one skill are required.")
            else:
                entry.category_name = category_name.strip()
                entry.skills = [s.strip() for s in skills_text.split(",") if s.strip()]
                st.success("Category saved.")

        if st.button("🗑️ Remove This Category", key=f"skill_remove_{entry.id}"):
            remove_skill_category(entry.id)
            st.rerun()

render_prev_next("skills")
