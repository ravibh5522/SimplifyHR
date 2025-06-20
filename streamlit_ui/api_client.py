import requests
import streamlit as st

# Use a session object for potential performance benefits and to set headers once
session = requests.Session()
BASE_URL = "http://127.0.0.1:8085/api/jd" # Make sure this matches your Flask app's address

def generate_jd_from_api(payload: dict):
    """Calls the /generate endpoint."""
    try:
        response = session.post(f"{BASE_URL}/generate", json=payload, timeout=60)
        response.raise_for_status()  # Raises an exception for 4XX/5XX errors
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: Failed to connect or generate JD. Details: {e}")
        # Try to parse the error from the response if possible
        if e.response is not None:
            try:
                error_details = e.response.json()
                st.error(f"Backend Error Message: {error_details}")
            except Exception:
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
        if e.response is not None:
            try:
                error_details = e.response.json()
                st.error(f"Backend Error Message: {error_details}")
            except Exception:
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
        if e.response is not None:
            try:
                error_details = e.response.json()
                st.error(f"Backend Error Message: {error_details}")
            except Exception:
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