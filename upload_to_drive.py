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
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets'
]

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
        """Authenticate with Google Drive API - try OAuth2 first, then Service Account"""
        creds = None
        
        # Try OAuth2 authentication first for file uploads
        if self.credentials_file and os.path.exists(self.credentials_file):
            # Check if it's a service account file
            try:
                with open(self.credentials_file, 'r') as f:
                    import json
                    cred_data = json.load(f)
                    
                if cred_data.get('type') == 'service_account':
                    # Use service account (for Sheets only)
                    try:
                        creds = service_account.Credentials.from_service_account_file(
                            self.credentials_file, scopes=SCOPES)
                        print("Using service account authentication")
                    except Exception as e:
                        print(f"Service account authentication failed: {e}")
                else:
                    # Use OAuth2 for regular user account
                    if os.path.exists('token.json'):
                        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
                    
                    if not creds or not creds.valid:
                        if creds and creds.expired and creds.refresh_token:
                            creds.refresh(Request())
                        else:
                            flow = InstalledAppFlow.from_client_secrets_file(
                                self.credentials_file, SCOPES)
                            creds = flow.run_local_server(port=0)
                        
                        # Save credentials for future use
                        with open('token.json', 'w') as token:
                            token.write(creds.to_json())
                    
                    print("Using OAuth2 authentication")
                    
            except Exception as e:
                print(f"Authentication failed: {e}")
        
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
        print(f"upload_image_from_base64 called with filename: {filename}, folder_id: {folder_id}")
        
        if not self.service:
            print("Google Drive service not available")
            return None
        
        try:
            print(f"Original base64 data length: {len(base64_data)}")
            
            # Remove data URL prefix if present
            if base64_data.startswith('data:'):
                print("Removing data URL prefix")
                base64_data = base64_data.split(',')[1]
            
            print(f"Cleaned base64 data length: {len(base64_data)}")
            
            # Decode base64 data
            image_data = base64.b64decode(base64_data)
            print(f"Decoded image data length: {len(image_data)} bytes")
            
            # Create file metadata - upload to root first
            file_metadata = {
                'name': filename,
                'description': f'Stock count image uploaded on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            }
            
            # Try uploading to root first, then move to folder
            print("Uploading to root Drive folder first")
            
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
            
            print("Starting file upload...")
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink'
            ).execute()
            
            print(f"File uploaded successfully, ID: {file['id']}")
            
            # Make file publicly viewable (optional)
            print("Setting file permissions...")
            self.service.permissions().create(
                fileId=file['id'],
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
            
            print(f"Successfully uploaded: {filename} (ID: {file['id']})")
            print(f"View link: {file['webViewLink']}")
            
            # Try to move file to target folder if specified
            if folder_id:
                try:
                    print(f"Moving file to folder: {folder_id}")
                    
                    # Get current parents
                    file_details = self.service.files().get(
                        fileId=file['id'],
                        fields='parents'
                    ).execute()
                    
                    previous_parents = ",".join(file_details.get('parents'))
                    
                    # Move the file to the target folder
                    self.service.files().update(
                        fileId=file['id'],
                        addParents=folder_id,
                        removeParents=previous_parents,
                        fields='id,parents'
                    ).execute()
                    
                    print(f"File moved to folder successfully")
                    
                except Exception as move_error:
                    print(f"Failed to move file to folder: {move_error}")
                    # Continue anyway - file is uploaded to root
            
            return {
                'file_id': file['id'],
                'web_view_link': file['webViewLink'],
                'web_content_link': file.get('webContentLink', ''),
                'filename': filename
            }
            
        except Exception as e:
            print(f"Error uploading image: {e}")
            import traceback
            print("Full error traceback:")
            traceback.print_exc()
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
    
    def get_or_create_main_project_folder(self):
        """Get or create the main project folder"""
        if not self.service:
            return None
        
        try:
            # Search for existing folder
            results = self.service.files().list(
                q="name='check stock project' and mimeType='application/vnd.google-apps.folder'",
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                print(f"Found existing project folder: {folders[0]['id']}")
                return folders[0]['id']
            else:
                # Create new folder
                return self.create_folder('check stock project')
                
        except Exception as e:
            print(f"Error getting project folder: {e}")
            return None
    
    def get_or_create_inventory_folder(self):
        """Get or create the 'Pic Stock Counting' folder under 'Check Stock Project'"""
        if not self.service:
            return None
        
        try:
            # First, get the main project folder
            main_folder_id = self.get_or_create_main_project_folder()
            if not main_folder_id:
                print("Failed to get main project folder")
                return None
                
            print(f"Main project folder ID: {main_folder_id}")
            
            # Search for 'Pic Stock Counting' folder under the main project folder
            results = self.service.files().list(
                q=f"name='Pic Stock Counting' and parents in '{main_folder_id}' and mimeType='application/vnd.google-apps.folder'",
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                print(f"Found existing 'Pic Stock Counting' folder: {folders[0]['id']}")
                return folders[0]['id']
            else:
                print("Creating 'Pic Stock Counting' folder in main project folder")
                return self.create_folder('Pic Stock Counting', main_folder_id)
                
        except Exception as e:
            print(f"Error getting 'Pic Stock Counting' folder: {e}")
            return None
    
    def upload_csv_file(self, file_path, filename):
        """Upload CSV file to Google Drive in the main project folder"""
        folder_id = self.get_or_create_main_project_folder()
        return self.upload_file(file_path, folder_id)
    
    def get_or_create_stock_sheet(self):
        """Get or create Google Sheet for stock data"""
        main_folder_id = self.get_or_create_main_project_folder()
        if not main_folder_id:
            return None
        
        try:
            # Search for existing stock sheet
            results = self.service.files().list(
                q=f"name='Stock Data' and parents in '{main_folder_id}' and mimeType='application/vnd.google-apps.spreadsheet'",
                fields='files(id, name, webViewLink)'
            ).execute()
            
            sheets = results.get('files', [])
            
            if sheets:
                print(f"Found existing stock sheet: {sheets[0]['id']}")
                return {
                    'sheet_id': sheets[0]['id'],
                    'web_view_link': sheets[0]['webViewLink']
                }
            else:
                # Create new Google Sheet
                return self.create_stock_sheet(main_folder_id)
                
        except Exception as e:
            print(f"Error getting stock sheet: {e}")
            return None
    
    def create_stock_sheet(self, parent_folder_id):
        """Create a new Google Sheet for stock data"""
        if not self.service:
            return None
        
        try:
            # Create Google Sheet
            sheet_metadata = {
                'name': 'Stock Data',
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'parents': [parent_folder_id]
            }
            
            sheet = self.service.files().create(
                body=sheet_metadata,
                fields='id,webViewLink'
            ).execute()
            
            sheet_id = sheet['id']
            
            # Initialize sheet with headers
            self.initialize_sheet_headers(sheet_id)
            
            print(f"Created new stock sheet: {sheet_id}")
            return {
                'sheet_id': sheet_id,
                'web_view_link': sheet['webViewLink']
            }
            
        except Exception as e:
            print(f"Error creating stock sheet: {e}")
            return None
    
    def initialize_sheet_headers(self, sheet_id):
        """Initialize Google Sheet with headers"""
        try:
            # This would require Google Sheets API
            # For now, we'll just create the file
            # Headers: Date, Time, Barcode, Product Name, Quantity, Branch, User, Image URL
            print(f"Sheet {sheet_id} created - headers should be added manually or via Sheets API")
        except Exception as e:
            print(f"Error initializing sheet headers: {e}")
    
    def append_to_stock_sheet(self, stock_data):
        """Append stock data to Google Sheet"""
        sheet_info = self.get_or_create_stock_sheet()
        if not sheet_info:
            return False
        
        try:
            # This would require Google Sheets API to append data
            # For now, we'll just log the data
            print(f"Stock data logged: {stock_data}")
            print(f"Sheet URL: {sheet_info['web_view_link']}")
            return True
        except Exception as e:
            print(f"Error appending to sheet: {e}")
            return False
    
    def get_or_create_products_sheet(self):
        """Get or create Google Sheet for product master data"""
        main_folder_id = self.get_or_create_main_project_folder()
        if not main_folder_id:
            return None
        
        try:
            # Search for existing products sheet
            results = self.service.files().list(
                q=f"name='Product Master' and parents in '{main_folder_id}' and mimeType='application/vnd.google-apps.spreadsheet'",
                fields='files(id, name, webViewLink)'
            ).execute()
            
            sheets = results.get('files', [])
            
            if sheets:
                print(f"Found existing products sheet: {sheets[0]['id']}")
                return {
                    'sheet_id': sheets[0]['id'],
                    'web_view_link': sheets[0]['webViewLink']
                }
            else:
                # Create new Google Sheet for products
                return self.create_products_sheet(main_folder_id)
                
        except Exception as e:
            print(f"Error getting products sheet: {e}")
            return None
    
    def create_products_sheet(self, parent_folder_id):
        """Create a new Google Sheet for product master data"""
        if not self.service:
            return None
        
        try:
            # Create Google Sheet
            sheet_metadata = {
                'name': 'Product Master',
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'parents': [parent_folder_id]
            }
            
            sheet = self.service.files().create(
                body=sheet_metadata,
                fields='id,webViewLink'
            ).execute()
            
            sheet_id = sheet['id']
            
            print(f"Created new products sheet: {sheet_id}")
            return {
                'sheet_id': sheet_id,
                'web_view_link': sheet['webViewLink']
            }
            
        except Exception as e:
            print(f"Error creating products sheet: {e}")
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
    
    def get_or_create_main_project_folder(self):
        return "mock_project_folder_id"
    
    def get_or_create_stock_sheet(self):
        return {
            'sheet_id': 'mock_sheet_id',
            'web_view_link': 'https://docs.google.com/spreadsheets/d/mock_sheet_id'
        }
    
    def append_to_stock_sheet(self, stock_data):
        print(f"Mock: Stock data would be saved to Google Sheets: {stock_data}")
        return True
    
    def upload_csv_file(self, file_path, filename):
        """Mock CSV upload - just prints info"""
        print(f"Mock: CSV file would be uploaded: {filename}")
        return {
            'web_view_link': f'https://drive.google.com/file/d/mock_csv_id/{filename}'
        }

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