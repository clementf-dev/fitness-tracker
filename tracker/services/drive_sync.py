"""
Google Drive synchronization service for automatic CSV import.
"""
import os
import io
import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from django.conf import settings


class DriveSync:
    """
    Synchronizes CSV files from Google Drive FitSync folder.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    FOLDER_NAME = 'FitSync'
    
    def __init__(self):
        self.service = None
        self.folder_id = None
        self.token_path = Path(settings.BASE_DIR) / 'drive_token.pickle'
        self.credentials_path = Path(settings.BASE_DIR) / 'credentials.json'
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API.
        Returns True if successful.
        """
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    print(f"Missing credentials.json at {self.credentials_path}")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token for future use
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
        return True
    
    def find_fitsync_folder(self) -> Optional[str]:
        """
        Find the FitSync folder in Google Drive.
        Returns folder ID or None.
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        query = f"name='{self.FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        if files:
            self.folder_id = files[0]['id']
            return self.folder_id
        
        return None
    
    def list_csv_files(self) -> List[dict]:
        """
        List CSV files in the FitSync folder.
        Returns list of file metadata.
        """
        if not self.folder_id:
            self.find_fitsync_folder()
        
        if not self.folder_id:
            return []
        
        query = f"'{self.folder_id}' in parents and mimeType='text/csv' and trashed=false"
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, modifiedTime)'
        ).execute()
        
        return results.get('files', [])
    
    def download_csv(self, file_id: str) -> str:
        """
        Download a CSV file content.
        Returns the CSV content as string.
        """
        if not self.service:
            if not self.authenticate():
                return ""
        
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        return fh.read().decode('utf-8')
    
    def check_for_updates(self, last_sync_time: Optional[datetime] = None) -> List[Tuple[str, str, str]]:
        """
        Check for updated CSV files since last sync.
        Returns list of (file_id, filename, content) tuples.
        """
        files = self.list_csv_files()
        updated_files = []
        
        for file in files:
            modified_time = datetime.fromisoformat(
                file['modifiedTime'].replace('Z', '+00:00')
            )
            
            # If no last sync or file was modified after last sync
            if not last_sync_time or modified_time > last_sync_time:
                content = self.download_csv(file['id'])
                updated_files.append((file['id'], file['name'], content))
        
        return updated_files


def sync_from_drive() -> dict:
    """
    Main sync function to be called from views or scheduler.
    Returns a dict with sync results.
    """
    from tracker.views.imports import import_weight_csv, import_steps_csv
    import csv
    
    syncer = DriveSync()
    
    if not syncer.authenticate():
        return {'success': False, 'error': 'Authentication failed'}
    
    try:
        updated_files = syncer.check_for_updates()
        results = {
            'success': True,
            'files_processed': 0,
            'weight_entries': 0,
            'steps_entries': 0
        }
        
        for file_id, filename, content in updated_files:
            io_string = io.StringIO(content)
            reader = csv.DictReader(io_string)
            
            if 'weight' in filename.lower():
                count = import_weight_csv(reader)
                results['weight_entries'] += count
            elif 'steps' in filename.lower():
                count = import_steps_csv(reader)
                results['steps_entries'] += count
            
            results['files_processed'] += 1
        
        return results
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
