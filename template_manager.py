import json
import streamlit as st
from drive_manager import list_templates_drive, download_template_drive, upload_template_drive

@st.cache_data(ttl=60)
def list_templates():
    """List all template JSON files from Google Drive (cached)."""
    return list_templates_drive()

@st.cache_data(ttl=60)
def load_template(filename):
    """Load a template JSON file from Google Drive and return its contents as a dict (cached)."""
    content = download_template_drive(filename)
    if content is None:
        return None
    return json.loads(content)

def save_template(filename, template_data):
    """Save a template JSON file to Google Drive and clear cache."""
    file_content = json.dumps(template_data, indent=2)
    upload_template_drive(filename, file_content)
    st.cache_data.clear()

def clear_template_cache():
    st.cache_data.clear() 