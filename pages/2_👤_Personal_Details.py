"""Page 1: Personal details form (name, contact info, professional summary)."""
import streamlit as st

from utils import ai_assistant as ai
from utils.navigation import render_prev_next, render_top_nav
from utils.session_manager import (
    form_key,
    get_job_description,
    get_resume_data,
    init_session_state,
    refresh_field,
)
from utils.validators import is_valid_email, is_valid_phone, is_valid_url, normalize_url

init_session_state()
render_top_nav("personal")
resume = get_resume_data()
info = resume.personal_info

st.title("👤 Personal Details")
st.caption("This information appears in your resume header.")

with st.form("personal_details_form"):
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name *", value=info.full_name)
        email = st.text_input("Email *", value=info.email, placeholder="jordan.rivera@example.com")
        phone = st.text_input(
            "Phone * (include country code)", value=info.phone, placeholder="+1 555-123-4567"
        )
    with col2:
        location = st.text_input("Location (City, State)", value=info.location)
        linkedin_url = st.text_input(
            "LinkedIn URL", value=info.linkedin_url, placeholder="linkedin.com/in/jordan-rivera"
        )
        portfolio_url = st.text_input(
            "Portfolio / GitHub URL", value=info.portfolio_url, placeholder="github.com/jordan-rivera"
        )

    professional_summary = st.text_area(
        "Professional Summary (optional -- use the AI assistant below to draft it)",
        value=info.professional_summary,
        height=120,
        key=form_key("personal_summary"),
        help="A 2-3 sentence summary of your background.",
    )

    submitted = st.form_submit_button("Save Personal Details", type="primary")

if submitted:
    errors = []

    if not full_name.strip():
        errors.append("Full Name is required.")

    if not email.strip():
        errors.append("Email is required.")
    elif not is_valid_email(email.strip()):
        errors.append("Email is not a valid address (e.g. name@example.com).")

    if not phone.strip():
        errors.append("Phone is required.")
    elif not is_valid_phone(phone.strip()):
        errors.append("Phone must include a country code, e.g. +1 555-123-4567.")

    linkedin_normalized = normalize_url(linkedin_url)
    if linkedin_url.strip() and not is_valid_url(linkedin_normalized):
        errors.append("LinkedIn URL is not valid.")

    portfolio_normalized = normalize_url(portfolio_url)
    if portfolio_url.strip() and not is_valid_url(portfolio_normalized):
        errors.append("Portfolio/GitHub URL is not valid.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        info.full_name = full_name.strip()
        info.email = email.strip()
        info.phone = phone.strip()
        info.location = location.strip()
        info.linkedin_url = linkedin_normalized
        info.portfolio_url = portfolio_normalized
        info.professional_summary = professional_summary.strip()
        st.success("Personal details saved.")

# # --- AI: professional summary --------------------------------------------------
# st.divider()
# st.subheader("✨ AI: Professional Summary")
# st.caption("Drafts a summary from the experience, projects, and skills you've entered -- nothing invented.")

# if not ai.is_configured():
#     ai.render_unavailable_notice()
# else:
#     jd = get_job_description()
#     if jd.strip():
#         st.caption("ℹ️ Tailoring emphasis to the job description from the ATS Match page.")
#     if st.button("Generate summary with AI", key="gen_summary"):
#         with st.spinner("Writing your summary..."):
#             try:
#                 st.session_state["ai_summary_proposal"] = ai.generate_summary(resume, jd)
#             except ai.AIError as exc:
#                 st.session_state.pop("ai_summary_proposal", None)
#                 st.error(str(exc))

#     proposal = st.session_state.get("ai_summary_proposal")
#     if proposal:
#         st.text_area("Proposed summary", value=proposal, height=120, disabled=True, key="ai_summary_preview")
#         col_use, col_discard = st.columns(2)
#         if col_use.button("✅ Use this summary", key="use_summary", type="primary", width="stretch"):
#             info.professional_summary = proposal
#             refresh_field("personal_summary")
#             st.session_state.pop("ai_summary_proposal", None)
#             st.rerun()
#         if col_discard.button("✕ Discard", key="discard_summary", width="stretch"):
#             st.session_state.pop("ai_summary_proposal", None)
#             st.rerun()

render_prev_next("personal")
