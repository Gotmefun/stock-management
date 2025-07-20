#!/usr/bin/env python3
"""
Test Google Sheets API connection
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

# Service account credentials
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def test_sheets_access():
    try:
        # Authenticate
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        service = build('sheets', 'v4', credentials=creds)
        
        # Test 1: Get spreadsheet metadata
        spreadsheet_id = '17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM'
        
        print("Test 1: Getting spreadsheet metadata...")
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        print(f"✓ Spreadsheet title: {sheet_metadata.get('properties', {}).get('title', 'Unknown')}")
        
        # List all sheets
        sheets = sheet_metadata.get('sheets', [])
        print(f"✓ Available sheets:")
        for sheet in sheets:
            title = sheet.get('properties', {}).get('title', 'Unknown')
            sheet_id = sheet.get('properties', {}).get('sheetId', 'Unknown')
            print(f"  - {title} (ID: {sheet_id})")
        
        # Test 2: Try to read a small range
        print("\nTest 2: Reading range Sheet1!A1:E1...")
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!A1:E1'
        ).execute()
        values = result.get('values', [])
        print(f"✓ Read data: {values}")
        
        # Test 3: Try to read D:E columns
        print("\nTest 3: Reading range Sheet1!D:E...")
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!D:E'
        ).execute()
        values = result.get('values', [])
        print(f"✓ D:E columns have {len(values)} rows")
        if values:
            print(f"  First row: {values[0]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    test_sheets_access()