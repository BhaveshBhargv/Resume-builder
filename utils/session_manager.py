"""Session-state bridge between Streamlit pages and the ResumeData model.

Every page calls init_session_state() first, then reads/mutates the
ResumeData object via get_resume_data() and the add_/remove_ helpers
below. Centralizing this here means UI pages never touch
st.session_state keys directly -- form code stays focused on rendering,
and the storage mechanism (currently in-memory session state) can be
swapped later without touching every page.
"""
import streamlit as st

from models.resume_data import (
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
    ResumeData,
    SkillCategory,
)

_RESUME_KEY = "resume_data"
_JD_KEY = "job_description"


def init_session_state() -> None:
    """Ensure a ResumeData object exists in session state. Call at the top of every page."""
    if _RESUME_KEY not in st.session_state:
        st.session_state[_RESUME_KEY] = ResumeData()


def get_resume_data() -> ResumeData:
    """Return the current session's ResumeData, creating it if needed."""
    init_session_state()
    return st.session_state[_RESUME_KEY]


def set_resume_data(new_resume: ResumeData) -> None:
    """Wholesale-replace the session's resume data.

    Used after parsing an uploaded resume. Every entry in new_resume has
    freshly generated ids (see models.resume_data._new_id), so form widgets
    on other pages -- keyed by entry id -- always see brand-new keys here
    rather than colliding with any previous session state.
    """
    st.session_state[_RESUME_KEY] = new_resume


def get_job_description() -> str:
    """Return the job-description text pasted on the ATS Match page (Phase 3)."""
    return st.session_state.get(_JD_KEY, "")


def set_job_description(text: str) -> None:
    st.session_state[_JD_KEY] = text


def add_education() -> EducationEntry:
    entry = EducationEntry()
    get_resume_data().education.append(entry)
    return entry


def remove_education(entry_id: str) -> None:
    resume = get_resume_data()
    resume.education = [e for e in resume.education if e.id != entry_id]


def add_experience() -> ExperienceEntry:
    entry = ExperienceEntry()
    get_resume_data().experience.append(entry)
    return entry


def remove_experience(entry_id: str) -> None:
    resume = get_resume_data()
    resume.experience = [e for e in resume.experience if e.id != entry_id]


def add_project() -> ProjectEntry:
    entry = ProjectEntry()
    get_resume_data().projects.append(entry)
    return entry


def remove_project(entry_id: str) -> None:
    resume = get_resume_data()
    resume.projects = [p for p in resume.projects if p.id != entry_id]


def add_skill_category() -> SkillCategory:
    entry = SkillCategory()
    get_resume_data().skills.append(entry)
    return entry


def remove_skill_category(entry_id: str) -> None:
    resume = get_resume_data()
    resume.skills = [s for s in resume.skills if s.id != entry_id]
