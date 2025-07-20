#!/usr/bin/env python3
"""
OAuth2 Manager for Google Drive uploads
"""

import os
import json
from datetime import datetime
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import base64
import io

# OAuth2 scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]

class OAuth2DriveManager:
    def __init__(self, credentials_file='oauth2_credentials.json'):
        self.credentials_file = credentials_file
        self.token_file = 'drive_token.pickle'
        self.drive_service = None
        self.credentials = None
        
    def get_authorization_url(self):
        """Get authorization URL for OAuth2 flow"""
        if not os.path.exists(self.credentials_file):
            raise Exception(f"OAuth2 credentials file not found: {self.credentials_file}")
        
        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=SCOPES,
            redirect_uri='http://127.0.0.1:8080/oauth2callback'
        )
        
        auth_url, state = flow.authorization_url(prompt='consent')
        
        # Store flow state and credentials info for later use
        flow_data = {
            'client_config': flow.client_config,
            'redirect_uri': flow.redirect_uri,
            'scopes': SCOPES,
            'state': state
        }
        
        with open('oauth_flow_data.json', 'w') as f:
            json.dump(flow_data, f)
            
        return auth_url
    
    def handle_oauth_callback(self, authorization_code):
        """Handle OAuth2 callback with authorization code"""
        try:
            print(f"=== OAuth2 Callback Debug ===")
            print(f"Authorization code: {authorization_code[:20]}...")
            print(f"Token file path: {self.token_file}")
            print(f"Current working directory: {os.getcwd()}")
            
            # Check if flow data exists
            if not os.path.exists('oauth_flow_data.json'):
                print("ERROR: oauth_flow_data.json not found!")
                return False
                
            # Load flow data
            print("Loading flow data...")
            with open('oauth_flow_data.json', 'r') as f:
                flow_data = json.load(f)
            print(f"Flow data loaded: {list(flow_data.keys())}")
            
            # Recreate flow
            print("Recreating OAuth flow...")
            flow = Flow.from_client_config(
                flow_data['client_config'],
                scopes=flow_data['scopes'],
                redirect_uri=flow_data['redirect_uri']
            )
            print("Flow recreated successfully")
            
            # Fetch token
            print("Fetching token with authorization code...")
            flow.fetch_token(code=authorization_code)
            print("Token fetched successfully")
            print(f"Credentials type: {type(flow.credentials)}")
            print(f"Credentials valid: {flow.credentials.valid}")
            print(f"Credentials expired: {flow.credentials.expired}")
            
            # Save credentials
            print(f"Saving credentials to: {self.token_file}")
            with open(self.token_file, 'wb') as f:
                pickle.dump(flow.credentials, f)
            print("Credentials saved successfully")
            
            # Verify file was created
            if os.path.exists(self.token_file):
                file_size = os.path.getsize(self.token_file)
                print(f"Token file created successfully, size: {file_size} bytes")
            else:
                print("ERROR: Token file was not created!")
                return False
            
            # Clean up
            if os.path.exists('oauth_flow_data.json'):
                os.remove('oauth_flow_data.json')
                print("Flow data cleaned up")
                
            print("OAuth2 authorization successful!")
            return True
            
        except Exception as e:
            print(f"OAuth2 callback error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_credentials(self):
        """Load saved credentials"""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as f:
                self.credentials = pickle.load(f)
        
        # Refresh if expired
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                # Save refreshed credentials
                with open(self.token_file, 'wb') as f:
                    pickle.dump(self.credentials, f)
            except Exception as e:
                print(f"Failed to refresh credentials: {e}")
                self.credentials = None
        
        if self.credentials and self.credentials.valid:
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            return True
        
        return False
    
    def is_authorized(self):
        """Check if user is authorized"""
        return self.load_credentials()
    
    def upload_image_from_base64(self, base64_data, filename, folder_id=None):
        """Upload image from base64 data to Google Drive"""
        if not self.drive_service:
            if not self.load_credentials():
                raise Exception("Not authorized. Please complete OAuth2 flow first.")
        
        try:
            print(f"OAuth2: Uploading {filename}")
            
            # Remove data URL prefix if present
            if base64_data.startswith('data:'):
                base64_data = base64_data.split(',')[1]
            
            # Decode base64 data
            image_data = base64.b64decode(base64_data)
            print(f"Image data length: {len(image_data)} bytes")
            
            # Create file metadata
            file_metadata = {
                'name': filename,
                'description': f'Stock count image uploaded on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
                print(f"Uploading to folder: {folder_id}")
            
            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(image_data),
                mimetype='image/jpeg',
                resumable=True
            )
            
            # Upload file
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink'
            ).execute()
            
            print(f"Upload successful! File ID: {file['id']}")
            
            # Make file publicly viewable
            try:
                self.drive_service.permissions().create(
                    fileId=file['id'],
                    body={'role': 'reader', 'type': 'anyone'}
                ).execute()
                print("File made publicly viewable")
            except Exception as perm_error:
                print(f"Failed to set permissions: {perm_error}")
            
            return {
                'file_id': file['id'],
                'web_view_link': file['webViewLink'],
                'web_content_link': file.get('webContentLink', ''),
                'filename': filename
            }
            
        except Exception as e:
            print(f"Upload error: {e}")
            return None
    
    def find_folder_by_name(self, folder_name, parent_id=None):
        """Find folder by name"""
        if not self.drive_service:
            return None
        
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                query += f" and parents in '{parent_id}'"
            
            results = self.drive_service.files().list(
                q=query,
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            if folders:
                return folders[0]['id']
            
            return None
            
        except Exception as e:
            print(f"Error finding folder: {e}")
            return None
    
    def create_folder(self, folder_name, parent_id=None):
        """Create folder in Google Drive"""
        if not self.drive_service:
            return None
        
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.drive_service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            print(f"Created folder: {folder_name} (ID: {folder.get('id')})")
            return folder.get('id')
            
        except Exception as e:
            print(f"Error creating folder: {e}")
            return None
    
    def get_or_create_folder_path(self, folder_path):
        """Get or create folder path like 'Check Stock Project/Pic Stock Counting'"""
        if not self.drive_service:
            return None
        
        try:
            folder_names = folder_path.split('/')
            current_parent = None
            
            for folder_name in folder_names:
                folder_id = self.find_folder_by_name(folder_name, current_parent)
                
                if not folder_id:
                    folder_id = self.create_folder(folder_name, current_parent)
                
                if not folder_id:
                    print(f"Failed to create/find folder: {folder_name}")
                    return None
                
                current_parent = folder_id
                print(f"Folder '{folder_name}' ID: {folder_id}")
            
            return current_parent
            
        except Exception as e:
            print(f"Error with folder path: {e}")
            return None

# Global instance
oauth_drive_manager = OAuth2DriveManager()