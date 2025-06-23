import json
from drive_manager import list_templates_drive, download_template_drive, upload_template_drive

def list_templates():
    """List all template JSON files from Google Drive."""
    return list_templates_drive()

def load_template(filename):
    """Load a template JSON file from Google Drive and return its contents as a dict."""
    content = download_template_drive(filename)
    if content is None:
        return None
    return json.loads(content)

def save_template(filename, template_data):
    """Save a template JSON file to Google Drive."""
    file_content = json.dumps(template_data, indent=2)
    upload_template_drive(filename, file_content) 