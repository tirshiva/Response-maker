import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# Set your service account file and folder ID
SERVICE_ACCOUNT_FILE = 'sellers-responses-c029d3bdaf57.json'
FOLDER_ID = '1n82PnBOXUg7ubBHu0hctxn3B2ujB1jTG'
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

def list_templates_drive():
    """List all JSON template files in the Google Drive folder."""
    query = f"'{FOLDER_ID}' in parents and mimeType='application/json' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return [f['name'] for f in results.get('files', [])]

def download_template_drive(filename):
    """Download a template file's content from Google Drive as a string."""
    query = f"'{FOLDER_ID}' in parents and name='{filename}' and trashed=false"
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

def upload_template_drive(filename, file_content):
    """Upload or update a template file to Google Drive."""
    # Check if file exists
    query = f"'{FOLDER_ID}' in parents and name='{filename}' and trashed=false"
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