"""Page 4: Projects form. Supports multiple entries.

Each entry's fields live inside an st.form so nothing is written back to the
ResumeData model until the user clicks "Save Entry" -- typing no longer
triggers a script rerun on every keystroke, which also keeps the expander
open while editing (see the `key=` on st.expander below).
"""
import streamlit as st

from utils import ai_assistant as ai
from utils.navigation import render_prev_next, render_top_nav
from utils.session_manager import (
    add_project,
    form_key,
    get_job_description,
    get_resume_data,
    init_session_state,
    refresh_field,
    remove_project,
)
from utils.validators import is_valid_url, normalize_url

init_session_state()
render_top_nav("projects")
resume = get_resume_data()

st.title("🚀 Projects")
st.caption("Add personal, academic, or professional projects worth highlighting.")

if st.button("➕ Add Project"):
    add_project()
    st.rerun()

if not resume.projects:
    st.info("No projects yet. Click **Add Project** to start.")

ai_ready = ai.is_configured()
if resume.projects and not ai_ready:
    ai.render_unavailable_notice()

for entry in resume.projects:
    with st.expander(f"🚀 {entry.name or 'New Project'}", expanded=not entry.name, key=f"proj_exp_{entry.id}"):
        with st.form(f"proj_form_{entry.id}"):
            name = st.text_input("Project Name *", value=entry.name, key=f"proj_name_{entry.id}")
            url = st.text_input(
                "URL (repo/demo, optional)",
                value=entry.url,
                key=f"proj_url_{entry.id}",
                placeholder="github.com/username/repo",
            )
            description = st.text_area(
                "Short Description", value=entry.description, key=form_key(f"proj_desc_{entry.id}"), height=80
            )

            tech_text = st.text_input(
                "Technologies Used (comma-separated)",
                value=", ".join(entry.technologies),
                key=f"proj_tech_{entry.id}",
            )

            bullets_text = st.text_area(
                "Key Contributions / Outcomes (one bullet per line)",
                value="\n".join(entry.bullet_points),
                key=form_key(f"proj_bullets_{entry.id}"),
                height=100,
            )

            submitted = st.form_submit_button("💾 Save Entry", type="primary")

        if submitted:
            url_normalized = normalize_url(url)
            if not name.strip():
                st.error("Project Name is required.")
            elif url.strip() and not is_valid_url(url_normalized):
                st.error("Project URL is not valid.")
            else:
                entry.name = name.strip()
                entry.url = url_normalized
                entry.description = description.strip()
                entry.technologies = [t.strip() for t in tech_text.split(",") if t.strip()]
                entry.bullet_points = [line.strip() for line in bullets_text.split("\n") if line.strip()]
                st.success("Project saved.")

        # --- AI: enhance this project's saved description + bullets ------------
        if ai_ready and (entry.description or entry.bullet_points):
            st.caption("✨ AI polishes your **saved** description and bullets (save any edits first).")
            if st.button("✨ Enhance with AI", key=f"ai_proj_btn_{entry.id}"):
                with st.spinner("Enhancing project..."):
                    try:
                        new_desc, new_bullets = ai.enhance_project(
                            entry.name, entry.description, entry.technologies,
                            entry.bullet_points, get_job_description(),
                        )
                        st.session_state[f"ai_proj_{entry.id}"] = {"description": new_desc, "bullets": new_bullets}
                    except ai.AIError as exc:
                        st.session_state.pop(f"ai_proj_{entry.id}", None)
                        st.error(str(exc))

            proposal = st.session_state.get(f"ai_proj_{entry.id}")
            if proposal:
                st.markdown("**Proposed description:**")
                st.markdown(f"> {proposal['description']}")
                if proposal["bullets"]:
                    st.markdown("**Proposed bullet points:**")
                    for bullet in proposal["bullets"]:
                        st.markdown(f"- {bullet}")
                col_use, col_discard = st.columns(2)
                if col_use.button("✅ Use these", key=f"use_proj_{entry.id}", type="primary", width="stretch"):
                    entry.description = proposal["description"]
                    entry.bullet_points = proposal["bullets"]
                    refresh_field(f"proj_desc_{entry.id}")
                    refresh_field(f"proj_bullets_{entry.id}")
                    st.session_state.pop(f"ai_proj_{entry.id}", None)
                    st.rerun()
                if col_discard.button("✕ Discard", key=f"discard_proj_{entry.id}", width="stretch"):
                    st.session_state.pop(f"ai_proj_{entry.id}", None)
                    st.rerun()

        if st.button("🗑️ Remove This Project", key=f"proj_remove_{entry.id}"):
            remove_project(entry.id)
            st.rerun()

render_prev_next("projects")
