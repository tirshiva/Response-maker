import io
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import streamlit as st

# Set your Google Drive folder ID
FOLDER_ID = '1n82PnBOXUg7ubBHu0hctxn3B2ujB1jTG'
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_credentials():
    if hasattr(st, 'secrets') and 'gdrive' in st.secrets and 'service_account_json' in st.secrets['gdrive']:
        service_account_info = json.loads(st.secrets['gdrive']['service_account_json'])
        return service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    else:
        raise RuntimeError("Service account JSON not found in Streamlit secrets. Please add it to your secrets.")

credentials = get_credentials()
drive_service = build('drive', 'v3', credentials=credentials)

def list_templates_drive():
    """List all JSON template files in the Google Drive folder."""
    query = f"'{FOLDER_ID}' in parents and mimeType='application/json' and trashed=false"
    try:
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        return [f['name'] for f in results.get('files', [])]
    except Exception as e:
        try:
            st.error(f"Error accessing Google Drive (listing templates): {e}")
        except ImportError:
            print(f"Error accessing Google Drive (listing templates): {e}")
        return []

def download_template_drive(filename):
    """Download a template file's content from Google Drive as a string."""
    query = f"'{FOLDER_ID}' in parents and name='{filename}' and trashed=false"
    try:
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if not files:
            return None
        file_id = files[0]['id']
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh.read().decode('utf-8')
    except Exception as e:
        try:
            st.error(f"Error downloading template '{filename}': {e}")
        except ImportError:
            print(f"Error downloading template '{filename}': {e}")
        return None

def upload_template_drive(filename, file_content):
    """Upload or update a template file to Google Drive."""
    query = f"'{FOLDER_ID}' in parents and name='{filename}' and trashed=false"
    try:
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        media = MediaIoBaseUpload(io.BytesIO(file_content.encode('utf-8')), mimetype='application/json')
        if files:
            # Update existing file
            file_id = files[0]['id']
            drive_service.files().update(fileId=file_id, media_body=media).execute()
        else:
            # Upload new file
            file_metadata = {
                'name': filename,
                'parents': [FOLDER_ID],
                'mimeType': 'application/json'
            }
            drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    except Exception as e:
        try:
            st.error(f"Error uploading template '{filename}': {e}")
        except ImportError:
            print(f"Error uploading template '{filename}': {e}")
    st.rerun() 