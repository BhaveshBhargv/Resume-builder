"""AI Resume Builder -- application entry point.

This file only wires up navigation: it registers every page from
utils.navigation.PAGES with Streamlit's st.navigation(), using
position="hidden" so Streamlit's own nav UI never renders (with this many
pages, its built-in "top" position collapses most into an "N more" dropdown,
which isn't the always-visible top bar we want). Each page instead calls
utils.navigation.render_top_nav() itself to draw a full horizontal bar of
page buttons, and render_prev_next() for Previous/Next controls at the
bottom. This file still needs st.navigation()/.run() underneath since that's
what makes st.switch_page() and URL routing work.
"""
import streamlit as st

from utils.navigation import PAGES

st.set_page_config(page_title="AI Resume Builder", page_icon="📄", layout="wide")

nav_pages = [
    st.Page(page.path, title=page.title, icon=page.icon, url_path=page.key, default=(page.key == "home"))
    for page in PAGES
]
nav = st.navigation(nav_pages, position="hidden")
nav.run()
