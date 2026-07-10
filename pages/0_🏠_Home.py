"""Page 0: Home / landing page -- welcome text, start choice, and progress overview."""
import streamlit as st

from utils.navigation import render_prev_next, render_top_nav
from utils.session_manager import get_resume_data, init_session_state

init_session_state()
render_top_nav("home")

st.title("📄 AI-Powered Resume Builder")
st.markdown(
    """
    Build an ATS-friendly resume tailored to a job description --
    without inventing experience or skills you don't have.
    """
)

st.divider()

st.subheader("Get Started")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**📤 Upload an existing resume**")
    st.caption("We'll read it and pre-fill every section for you to review.")
    if st.button("Upload a Resume", width="stretch"):
        st.switch_page("pages/1_📤_Upload_Resume.py")
with col2:
    st.markdown("**✍️ Enter your details manually**")
    st.caption("Start from a blank form and fill in each section yourself.")
    if st.button("Enter Details Manually", width="stretch", type="primary"):
        st.switch_page("pages/2_👤_Personal_Details.py")

st.divider()

resume = get_resume_data()
status = resume.completion_status()

st.subheader("Your Progress")
cols = st.columns(len(status))
for col, (section, done) in zip(cols, status.items()):
    with col:
        st.metric(label=section, value="Complete" if done else "Empty")

render_prev_next("home")
