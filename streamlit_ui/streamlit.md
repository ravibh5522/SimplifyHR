Excellent choice! Streamlit is perfect for creating beautiful, data-driven web apps for this kind of purpose quickly.

Here is a complete, production-ready Streamlit UI that interacts with your Flask API. It includes the requested red (`#d72638`) and white theme, a sidebar for navigation, and tabs for managing JDs.

### **Project Structure**

First, let's organize the files for the UI part of your project.

```
ai_hr_project/
├── JdGen/                  # Your Flask API backend folder
└── streamlit_ui/           # New folder for the Streamlit UI
    ├── .streamlit/
    │   └── config.toml     # Theming file
    ├── api_client.py       # Helper functions to call your API
    ├── app.py              # The main Streamlit application
    └── requirements.txt    # Python dependencies for the UI
```

---

### **Step 1: Create the Theme File (`.streamlit/config.toml`)**

This file will define our custom red and white theme.

**File: `streamlit_ui/.streamlit/config.toml`**
```toml
[theme]
# The red color you requested
primaryColor="#FFFFFF"
backgroundColor="#d72638"
secondaryBackgroundColor="#A41D2C" # A slightly darker red for sidebar/widgets

# White text color
textColor="#FFFFFF"

# Font
font="sans serif"

[server]
# This can help if you run into cross-origin issues, though usually not needed for this setup
# enableCORS = false
```

---

### **Step 2: Create the API Client (`api_client.py`)**

This is a best practice. It centralizes all your API calls, making the main `app.py` much cleaner and easier to manage.

**File: `streamlit_ui/api_client.py`**
```python
import requests
import streamlit as st

# Use a session object for potential performance benefits and to set headers once
session = requests.Session()
BASE_URL = "http://127.0.0.1:8080/api/jd" # Make sure this matches your Flask app's address

def generate_jd_from_api(payload: dict):
    """Calls the /generate endpoint."""
    try:
        response = session.post(f"{BASE_URL}/generate", json=payload, timeout=60)
        response.raise_for_status()  # Raises an exception for 4XX/5XX errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: Failed to connect or generate JD. Details: {e}")
        # Try to parse the error from the response if possible
        try:
            error_details = e.response.json()
            st.error(f"Backend Error Message: {error_details}")
        except:
            pass
        return None

def save_jd_to_db(payload: dict):
    """Calls the POST / endpoint to create a new JD."""
    try:
        response = session.post(BASE_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: Failed to save JD. Details: {e}")
        try:
            error_details = e.response.json()
            st.error(f"Backend Error Message: {error_details}")
        except:
            pass
        return None

def get_all_jds():
    """Calls the GET / endpoint to list all JDs."""
    try:
        response = session.get(BASE_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: Failed to retrieve job descriptions. Is the backend server running?")
        return []

def get_jd_details(job_id: int):
    """Calls the GET /{job_id} endpoint."""
    try:
        response = session.get(f"{BASE_URL}/{job_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: Failed to retrieve JD details. Details: {e}")
        return None

def update_jd_in_db(job_id: int, payload: dict):
    """Calls the PUT /{job_id} endpoint."""
    try:
        response = session.put(f"{BASE_URL}/{job_id}", json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: Failed to update JD. Details: {e}")
        try:
            error_details = e.response.json()
            st.error(f"Backend Error Message: {error_details}")
        except:
            pass
        return None

def delete_jd_from_db(job_id: int):
    """Calls the DELETE /{job_id} endpoint."""
    try:
        response = session.delete(f"{BASE_URL}/{job_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: Failed to delete JD. Details: {e}")
        return None
```

---

### **Step 3: Create the Main Streamlit App (`app.py`)**

This is where the magic happens. The code is heavily commented to explain each part.

**File: `streamlit_ui/app.py`**
```python
import streamlit as st
from api_client import (
    generate_jd_from_api,
    save_jd_to_db,
    get_all_jds,
    get_jd_details,
    update_jd_in_db,
    delete_jd_from_db,
)
from datetime import datetime, timedelta, UTC

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
                expires_at_dt = datetime.now(UTC) + timedelta(days=expires_in_days)
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
            view_tab, edit_tab, delete_tab = st.tabs(["📄 View Details", "✏️ Edit JD", "🗑️ Danger Zone"])

            # --- View Tab ---
            with view_tab:
                st.info(f"Status: **{jd_details['status'].upper()}** | Expires on: **{datetime.fromisoformat(jd_details['expires_at']).strftime('%Y-%m-%d')}**")
                display_jd(jd_details['jd_content'])
            
            # --- Edit Tab ---
            with edit_tab:
                with st.form("edit_form"):
                    st.subheader("Edit Job Details")
                    
                    # Using the keys from your Pydantic schema
                    content_to_edit = jd_details['jd_content']
                    
                    updated_title = st.text_input("Job Title", value=jd_details.get('job_title', ''))
                    updated_status = st.selectbox("Status", options=["active", "inactive"], index=0 if jd_details.get('status') == 'active' else 1)
                    updated_expires_at = st.date_input("Expiration Date", value=datetime.fromisoformat(jd_details.get('expires_at')))
                    
                    st.markdown("---")
                    
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
                            "expires_at": updated_expires_at.isoformat(),
                            "jd_content": {
                                "job_title_generated": updated_title, # Ensure this is also updated
                                "company_summary": content_to_edit.get('company_summary', ''), # Keep old value
                                "role_summary": updated_role_summary,
                                "key_responsibilities": updated_responsibilities.split('\n'),
                                "required_qualifications": updated_req_qual.split('\n'),
                                "preferred_qualifications": updated_pref_qual.split('\n'),
                                "benefits": content_to_edit.get('benefits', []) # Keep old value
                            }
                        }
                        with st.spinner("Updating..."):
                            result = update_jd_in_db(selected_id, update_payload)
                            if result:
                                st.success("Update successful! The page will now reload.")
                                # Rerun to reflect changes immediately
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
```

---

### **Step 4: Create the Requirements File (`requirements.txt`)**

This file lists the Python packages your Streamlit UI needs.

**File: `streamlit_ui/requirements.txt`**
```
streamlit
requests
```

---

### **How to Run Your Application**

1.  **Start the Flask API Backend:**
    *   Open a terminal.
    *   Navigate to your `JdGen` folder.
    *   Run your Flask app: `python run.py`
    *   Keep this terminal running.

2.  **Start the Streamlit UI:**
    *   Open a **new, separate** terminal.
    *   Navigate to your `streamlit_ui` folder.
    *   Install the required packages: `pip install -r requirements.txt`
    *   Run the Streamlit app: `streamlit run app.py`

Your browser should open a new tab with your beautiful, red-themed AI HR Assistant! You can now generate, save, view, edit, and delete job descriptions through a user-friendly interface.