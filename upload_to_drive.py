#!/usr/bin/env python3
"""
Google Drive API Integration
Handles image uploads to Google Drive for inventory photos
"""

import os
import io
import base64
from datetime import datetime
import mimetypes

# For production use, install: pip install google-api-python-client google-auth-oauthlib
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveUploader:
    def __init__(self, credentials_file=None, service_account_file=None):
        """
        Initialize Google Drive uploader
        
        Args:
            credentials_file: Path to OAuth2 credentials file (credentials.json)
            service_account_file: Path to service account credentials file
        """
        self.service = None
        self.credentials_file = credentials_file
        self.service_account_file = service_account_file
        
        if not GOOGLE_DRIVE_AVAILABLE:
            print("Warning: Google Drive API not available. Install google-api-python-client")
            return
        
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Try service account authentication first
        if self.service_account_file and os.path.exists(self.service_account_file):
            try:
                creds = service_account.Credentials.from_service_account_file(
                    self.service_account_file, scopes=SCOPES)
                print("Using service account authentication")
            except Exception as e:
                print(f"Service account authentication failed: {e}")
        
        # Fall back to OAuth2 authentication
        if not creds and self.credentials_file:
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        print(f"Credentials file not found: {self.credentials_file}")
                        return
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
        
        if creds:
            self.service = build('drive', 'v3', credentials=creds)
            print("Google Drive API authenticated successfully")
        else:
            print("Failed to authenticate with Google Drive API")
    
    def create_folder(self, folder_name, parent_folder_id=None):
        """Create a folder in Google Drive"""
        if not self.service:
            return None
        
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            print(f"Created folder: {folder_name} (ID: {folder.get('id')})")
            return folder.get('id')
            
        except Exception as e:
            print(f"Error creating folder: {e}")
            return None
    
    def upload_image_from_base64(self, base64_data, filename, folder_id=None):
        """
        Upload image from base64 data to Google Drive
        
        Args:
            base64_data: Base64 encoded image data
            filename: Name for the uploaded file
            folder_id: ID of the folder to upload to
        
        Returns:
            Dictionary with file_id and web_view_link or None if failed
        """
        if not self.service:
            return None
        
        try:
            # Remove data URL prefix if present
            if base64_data.startswith('data:'):
                base64_data = base64_data.split(',')[1]
            
            # Decode base64 data
            image_data = base64.b64decode(base64_data)
            
            # Create file metadata
            file_metadata = {
                'name': filename,
                'description': f'Stock count image uploaded on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Determine MIME type
            mime_type = 'image/jpeg'  # Default to JPEG
            if filename.lower().endswith('.png'):
                mime_type = 'image/png'
            elif filename.lower().endswith('.gif'):
                mime_type = 'image/gif'
            
            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(image_data),
                mimetype=mime_type,
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink'
            ).execute()
            
            # Make file publicly viewable (optional)
            self.service.permissions().create(
                fileId=file['id'],
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
            
            print(f"Successfully uploaded: {filename} (ID: {file['id']})")
            
            return {
                'file_id': file['id'],
                'web_view_link': file['webViewLink'],
                'web_content_link': file.get('webContentLink', ''),
                'filename': filename
            }
            
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None
    
    def upload_file(self, file_path, folder_id=None):
        """Upload a file from local path to Google Drive"""
        if not self.service or not os.path.exists(file_path):
            return None
        
        try:
            filename = os.path.basename(file_path)
            
            file_metadata = {
                'name': filename,
                'description': f'File uploaded on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            media = MediaIoBaseUpload(
                open(file_path, 'rb'),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink'
            ).execute()
            
            print(f"Successfully uploaded: {filename} (ID: {file['id']})")
            
            return {
                'file_id': file['id'],
                'web_view_link': file['webViewLink'],
                'web_content_link': file.get('webContentLink', ''),
                'filename': filename
            }
            
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def get_or_create_inventory_folder(self):
        """Get or create the main inventory folder"""
        if not self.service:
            return None
        
        try:
            # Search for existing folder
            results = self.service.files().list(
                q="name='Inventory Photos' and mimeType='application/vnd.google-apps.folder'",
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                print(f"Found existing inventory folder: {folders[0]['id']}")
                return folders[0]['id']
            else:
                # Create new folder
                return self.create_folder('Inventory Photos')
                
        except Exception as e:
            print(f"Error getting inventory folder: {e}")
            return None

# Mock uploader for when Google Drive API is not available
class MockGoogleDriveUploader:
    def __init__(self, *args, **kwargs):
        print("Using mock Google Drive uploader (API not available)")
        self.service = None
    
    def upload_image_from_base64(self, base64_data, filename, folder_id=None):
        """Mock upload - saves to local uploads folder"""
        try:
            # Create uploads directory if it doesn't exist
            os.makedirs('uploads', exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join('uploads', filename)
            
            # Remove data URL prefix if present
            if base64_data.startswith('data:'):
                base64_data = base64_data.split(',')[1]
            
            # Decode and save image
            image_data = base64.b64decode(base64_data)
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            print(f"Mock upload: Saved {filename} to uploads folder")
            
            return {
                'file_id': f"mock_{timestamp}",
                'web_view_link': f"file://{os.path.abspath(file_path)}",
                'web_content_link': f"file://{os.path.abspath(file_path)}",
                'filename': filename
            }
            
        except Exception as e:
            print(f"Mock upload error: {e}")
            return None
    
    def get_or_create_inventory_folder(self):
        return "mock_folder_id"

# Factory function
def create_drive_uploader(credentials_file='credentials.json', service_account_file='service_account.json'):
    """
    Create a Google Drive uploader instance
    Falls back to mock uploader if Google Drive API is not available
    """
    if GOOGLE_DRIVE_AVAILABLE:
        return GoogleDriveUploader(credentials_file, service_account_file)
    else:
        return MockGoogleDriveUploader()

# Example usage and testing
if __name__ == '__main__':
    import sys
    
    # Test the uploader
    uploader = create_drive_uploader()
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if os.path.exists(test_file):
            result = uploader.upload_file(test_file)
            if result:
                print(f"Upload successful: {result['web_view_link']}")
            else:
                print("Upload failed")
        else:
            print(f"File not found: {test_file}")
    else:
        print("Usage: python upload_to_drive.py <file_path>")
        print("\nTo set up Google Drive API:")
        print("1. Go to Google Cloud Console")
        print("2. Create a new project or select existing")
        print("3. Enable Google Drive API")
        print("4. Create credentials (OAuth 2.0 or Service Account)")
        print("5. Download credentials.json or service_account.json")
        print("6. Install required packages: pip install google-api-python-client google-auth-oauthlib")