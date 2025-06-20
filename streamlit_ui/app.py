import streamlit as st
from api_client import (
    generate_jd_from_api,
    save_jd_to_db,
    get_all_jds,
    get_jd_details,
    update_jd_in_db,
    delete_jd_from_db,
)
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser

# --- Page Configuration ---
st.set_page_config(
    page_title="AI HR Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
# Inject custom CSS for a more polished look
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# You can create a style.css file for more complex styles, but for a header, this is fine
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 2rem;
    color: white; /* Ensure header text is white */
}
.stTabs [data-baseweb="tab-list"] {
		gap: 24px;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
}
.stTabs [aria-selected="true"] {
    background-color: #FFFFFF;
    color: #d72638; /* Make selected tab text red */
}
</style>""", unsafe_allow_html=True)


# --- Helper function to display JD content ---
def display_jd(jd_content):
    st.subheader(jd_content.get("job_title_generated", "Job Description"))
    
    if "company_summary" in jd_content:
        st.markdown(f"**Company Summary:** {jd_content['company_summary']}")
    if "role_summary" in jd_content:
        st.markdown(f"**Role Summary:** {jd_content['role_summary']}")

    st.markdown("---")
    
    if "key_responsibilities" in jd_content:
        st.markdown("#### Key Responsibilities")
        for item in jd_content["key_responsibilities"]:
            st.markdown(f"- {item}")
    
    if "required_qualifications" in jd_content:
        st.markdown("#### Required Qualifications")
        for item in jd_content["required_qualifications"]:
            st.markdown(f"- {item}")

    if "preferred_qualifications" in jd_content and jd_content["preferred_qualifications"]:
        st.markdown("#### Preferred Qualifications")
        for item in jd_content["preferred_qualifications"]:
            st.markdown(f"- {item}")

    if "benefits" in jd_content and jd_content["benefits"]:
        st.markdown("#### Benefits")
        for item in jd_content["benefits"]:
            st.markdown(f"- {item}")


# --- Page: Create New Job Description ---
def page_create_jd():
    st.markdown('<p class="main-header">Create New Job Description</p>', unsafe_allow_html=True)

    with st.form("jd_creation_form"):
        st.header("Provide Job Details")
        job_title_input = st.text_input("Job Title", placeholder="e.g., Senior Python Developer")
        key_responsibilities_input = st.text_area("Key Responsibilities", placeholder="Enter each responsibility on a new line.")
        required_skills_input = st.text_area("Required Skills & Qualifications", placeholder="Enter each skill on a new line.")
        company_description_input = st.text_area("Company Description (Optional)", placeholder="Describe the company's mission and culture.")
        
        submitted = st.form_submit_button("✨ Generate with AI", use_container_width=True)

    if submitted:
        if not all([job_title_input, key_responsibilities_input, required_skills_input]):
            st.warning("Please fill in all required fields: Job Title, Responsibilities, and Skills.")
        else:
            payload = {
                "job_title_input": job_title_input,
                "key_responsibilities_input": key_responsibilities_input.split('\n'),
                "required_skills_input": required_skills_input.split('\n'),
                "company_description_input": company_description_input
            }
            with st.spinner("🤖 The AI is crafting the perfect job description..."):
                generated_content = generate_jd_from_api(payload)
                # Store the generated content in session state to use it after the rerun
                if generated_content:
                    st.session_state.generated_jd = generated_content
                else:
                    st.session_state.generated_jd = None # Clear if generation failed
    
    # This part runs after the form submission and after the page reruns
    if "generated_jd" in st.session_state and st.session_state.generated_jd:
        st.success("🎉 Job Description Generated Successfully!")
        st.markdown("---")
        st.header("Generated Preview")
        
        jd_preview_container = st.container(border=True)
        with jd_preview_container:
            display_jd(st.session_state.generated_jd)

        col1, col2 = st.columns(2)
        with col1:
             # Add an expiration date picker
            expires_in_days = st.number_input("Set Expiration (in days from today)", min_value=1, max_value=365, value=30)
        
        with col2:
            st.write("") # for vertical alignment
            st.write("") # for vertical alignment
            if st.button("💾 Save Job Description to Database", use_container_width=True, type="primary"):
                # Use the stored generated content to save
                expires_at_dt = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
                save_payload = {
                    "job_title": st.session_state.generated_jd.get("job_title_generated", "Untitled Job"),
                    "jd_content": st.session_state.generated_jd,
                    "expires_at": expires_at_dt.isoformat()
                }
                with st.spinner("Saving to database..."):
                    result = save_jd_to_db(save_payload)
                    if result:
                        st.success(f"Successfully saved Job Description with ID: {result.get('job_id')}")
                        # Clear the state to avoid re-showing the same JD
                        del st.session_state.generated_jd

# --- Page: Manage Existing Job Descriptions ---
def page_manage_jds():
    st.markdown('<p class="main-header">Manage Job Descriptions</p>', unsafe_allow_html=True)
    
    jd_list = get_all_jds()
    if not jd_list:
        st.info("No job descriptions found in the database. Go to the 'Create' page to add one!")
        return

    # Create a mapping from a display string to the ID
    jd_options = {f"{jd['job_title']} (ID: {jd['id']})": jd['id'] for jd in jd_list}
    selected_jd_display = st.selectbox("Select a Job Description to View or Edit", options=jd_options.keys())

    if selected_jd_display:
        selected_id = jd_options[selected_jd_display]
        
        # Fetch full details
        with st.spinner("Loading details..."):
            jd_details = get_jd_details(selected_id)

        if jd_details:
            _, edit_tab, delete_tab = st.tabs(["📄 View Details", "✏️ Edit JD", "🗑️ Danger Zone"])

            # --- View Tab ---
            expires_at_dt = date_parser.parse(jd_details['expires_at'])
            st.info(f"Status: **{jd_details['status'].upper()}** | Expires on: **{expires_at_dt.strftime('%Y-%m-%d')}**")
            display_jd(jd_details['jd_content'])

            # --- Edit Tab ---
            with edit_tab:
                with st.form("edit_form"):
                    st.subheader("Edit Job Details")

                    content_to_edit = jd_details['jd_content']

                    expires_at_dt = date_parser.parse(jd_details.get('expires_at'))
                    updated_expires_at = st.date_input("Expiration Date", value=expires_at_dt.date())

                    # Ensure we get a single date object for isoformat
                    if isinstance(updated_expires_at, tuple):
                        # If a tuple (date range), take the first date
                        expires_at_value = updated_expires_at[0] if updated_expires_at else None
                    else:
                        expires_at_value = updated_expires_at

                    st.markdown("---")

                    updated_title = st.text_input("Job Title", value=jd_details.get('job_title', ''))
                    updated_status = st.selectbox("Status", options=["active", "inactive"], index=0 if jd_details.get('status', '').lower() == "active" else 1)
                    updated_role_summary = st.text_area("Role Summary", value=content_to_edit.get('role_summary', ''))
                    updated_responsibilities = st.text_area("Key Responsibilities", value="\n".join(content_to_edit.get('key_responsibilities', [])), height=150)
                    updated_req_qual = st.text_area("Required Qualifications", value="\n".join(content_to_edit.get('required_qualifications', [])), height=150)
                    updated_pref_qual = st.text_area("Preferred Qualifications", value="\n".join(content_to_edit.get('preferred_qualifications', [])), height=100)

                    update_button = st.form_submit_button("💾 Update Job Description", use_container_width=True)

                    if update_button:
                        # Construct the payload for the API
                        update_payload = {
                            "job_title": updated_title,
                            "status": updated_status,
                            "expires_at": expires_at_value.isoformat() if expires_at_value is not None and hasattr(expires_at_value, "isoformat") else None,
                            "jd_content": {
                                "job_title_generated": updated_title,  # Ensure this is also updated
                                "company_summary": content_to_edit.get('company_summary', ''),  # Keep old value
                                "role_summary": updated_role_summary,
                                "key_responsibilities": updated_responsibilities.split('\n'),
                                "required_qualifications": updated_req_qual.split('\n'),
                                "preferred_qualifications": updated_pref_qual.split('\n'),
                                "benefits": content_to_edit.get('benefits', [])  # Keep old value
                            }
                        }
                        with st.spinner("Updating..."):
                            result = update_jd_in_db(selected_id, update_payload)
                            if result:
                                st.success("Update successful! The page will now reload.")
                                st.rerun()

            # --- Delete Tab ---
            with delete_tab:
                st.subheader("Delete Job Description")
                st.warning("⚠️ This action is permanent and cannot be undone.")

                confirm_text = f"I want to permanently delete job ID {selected_id}"
                confirmation_input = st.text_input(f"To confirm, please type: '{confirm_text}'")

                if confirmation_input == confirm_text:
                    if st.button("DELETE PERMANENTLY", type="primary", use_container_width=True):
                        with st.spinner("Deleting..."):
                            result = delete_jd_from_db(selected_id)
                            if result:
                                st.success("Job Description deleted successfully. The page will now reload.")
                                st.rerun()
                else:
                    st.info("Type the confirmation text to enable the delete button.")


# --- Main App Router ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Create New Job Description", "Manage Existing Job Descriptions"])

st.sidebar.markdown("---")
st.sidebar.info("This is an AI-powered HR tool to streamline the creation and management of job descriptions.")


if page == "Create New Job Description":
    page_create_jd()
elif page == "Manage Existing Job Descriptions":
    page_manage_jds()