"""Defines the app's page order and renders the top bar / Previous-Next controls.

app.py registers these same pages with st.navigation(..., position="hidden")
so Streamlit's own nav UI never appears -- with 7 pages, its built-in "top"
position collapses most of them into an "N more" dropdown rather than
showing them all, which isn't the always-visible top bar we want here. This
module is the single source of truth for page order and renders both the
top bar (render_top_nav) and the bottom Previous/Next buttons
(render_prev_next) using plain st.button + st.switch_page, giving full
control over the layout.
"""
from dataclasses import dataclass
from typing import List

import streamlit as st


@dataclass
class PageInfo:
    key: str
    path: str
    title: str
    icon: str


PAGES: List[PageInfo] = [
    PageInfo("home", "pages/0_🏠_Home.py", "Home", "🏠"),
    PageInfo("upload", "pages/1_📤_Upload_Resume.py", "Upload Resume", "📤"),
    PageInfo("personal", "pages/2_👤_Personal_Details.py", "Personal Details", "👤"),
    PageInfo("education", "pages/3_🎓_Education.py", "Education", "🎓"),
    PageInfo("experience", "pages/4_💼_Experience.py", "Experience", "💼"),
    PageInfo("projects", "pages/5_🚀_Projects.py", "Projects", "🚀"),
    PageInfo("skills", "pages/6_🛠️_Skills.py", "Skills", "🛠️"),
    PageInfo("review", "pages/7_📄_Review.py", "Review", "📄"),
    PageInfo("ats", "pages/8_🎯_ATS_Match.py", "ATS Match", "🎯"),
    PageInfo("download", "pages/9_⬇️_Download.py", "Download", "⬇️"),
]


def _index_of(key: str) -> int:
    for i, page in enumerate(PAGES):
        if page.key == key:
            return i
    raise ValueError(f"Unknown page key: {key}")


def render_top_nav(current_key: str) -> None:
    """Render every page as a button in a horizontal bar across the top of the page."""
    cols = st.columns(len(PAGES))
    for col, page in zip(cols, PAGES):
        with col:
            is_current = page.key == current_key
            if st.button(
                f"{page.icon} {page.title}",
                key=f"topnav_{current_key}_{page.key}",
                type="primary" if is_current else "secondary",
                width="stretch",
                disabled=is_current,
            ):
                st.switch_page(page.path)
    st.divider()


def render_prev_next(current_key: str) -> None:
    """Render Previous (left) / Next (right) buttons at the bottom of a page."""
    idx = _index_of(current_key)
    st.divider()
    col_prev, col_spacer, col_next = st.columns([2, 3, 2])
    with col_prev:
        if idx > 0:
            prev_page = PAGES[idx - 1]
            if st.button(f"← {prev_page.title}", key=f"navprev_{current_key}", width="stretch"):
                st.switch_page(prev_page.path)
    with col_next:
        if idx < len(PAGES) - 1:
            next_page = PAGES[idx + 1]
            if st.button(f"{next_page.title} →", key=f"navnext_{current_key}", width="stretch", type="primary"):
                st.switch_page(next_page.path)
