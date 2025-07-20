#!/usr/bin/env python3
"""
Google Sheets API Integration
Handles stock data storage in Google Sheets
"""

import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

class SheetsManager:
    def __init__(self, credentials_file='credentials.json'):
        """Initialize Google Sheets manager with service account credentials"""
        self.credentials_file = credentials_file
        self.sheets_service = None
        self.drive_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google APIs using Service Account"""
        if not os.path.exists(self.credentials_file):
            print(f"Credentials file not found: {self.credentials_file}")
            return
        
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES)
            
            self.sheets_service = build('sheets', 'v4', credentials=creds)
            self.drive_service = build('drive', 'v3', credentials=creds)
            print("Google Sheets API authenticated successfully")
            
        except Exception as e:
            print(f"Authentication failed: {e}")
    
    def get_product_by_barcode(self, barcode, sheet_id):
        """Get product info from Google Sheets by barcode"""
        if not self.sheets_service:
            print("Sheets service not available")
            return None
        
        try:
            # Read all product data from columns D and E
            range_name = 'Sheet1!D:E'  # Barcode in D, Product Name in E
            print(f"Reading from sheet {sheet_id}, range {range_name}")
            
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            rows = result.get('values', [])
            print(f"Retrieved {len(rows)} rows from sheet")
            
            if rows:
                print(f"First few rows: {rows[:3]}")
            
            # Skip header row and search for barcode
            for i, row in enumerate(rows[1:], 1):
                if len(row) >= 2:
                    print(f"Row {i}: {row[0]} vs {barcode}")
                    if row[0] == barcode:
                        print(f"Found match at row {i}")
                        return {
                            'barcode': row[0],
                            'product_name': row[1]
                        }
            
            print(f"No match found for barcode: {barcode}")
            return None
            
        except Exception as e:
            print(f"Error getting product: {e}")
            return None
    
    def add_stock_record(self, stock_data, sheet_id):
        """Add stock record to Google Sheets"""
        if not self.sheets_service:
            return False
        
        try:
            # Prepare data row
            current_time = datetime.now()
            row_data = [
                current_time.strftime('%Y-%m-%d'),
                current_time.strftime('%H:%M:%S'),
                stock_data['barcode'],
                stock_data['product_name'],
                stock_data['quantity'],
                stock_data['branch'],
                stock_data.get('user', 'Unknown'),
                stock_data.get('image_url', ''),
                stock_data.get('counter_name', 'Unknown')  # ชื่อผู้ตรวจนับสินค้า in column I
            ]
            
            # Append to sheet
            range_name = 'Sheet1!A:I'  # Extended to column I
            body = {
                'values': [row_data]
            }
            
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Stock record added successfully: {result.get('updates').get('updatedCells')} cells updated")
            return True
            
        except Exception as e:
            print(f"Error adding stock record: {e}")
            return False
    
    def get_all_products(self, sheet_id):
        """Get all products from Google Sheets"""
        if not self.sheets_service:
            return []
        
        try:
            range_name = 'Sheet1!D:E'  # Barcode in D, Product Name in E
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            rows = result.get('values', [])
            products = []
            
            # Skip header row
            for row in rows[1:]:
                if len(row) >= 2:
                    products.append({
                        'barcode': row[0],
                        'product_name': row[1]
                    })
            
            return products
            
        except Exception as e:
            print(f"Error getting products: {e}")
            return []
    
    def get_stock_summary(self, stock_sheet_id, product_sheet_id):
        """Get stock summary from Google Sheets"""
        if not self.sheets_service:
            return []
        
        try:
            # Get all stock records
            stock_range = 'Sheet1!A:H'
            stock_result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=stock_sheet_id,
                range=stock_range
            ).execute()
            
            stock_rows = stock_result.get('values', [])
            
            # Calculate totals by barcode
            stock_summary = {}
            for row in stock_rows[1:]:  # Skip header
                if len(row) >= 5:
                    barcode = row[2]
                    quantity = int(row[4]) if row[4].isdigit() else 0
                    
                    if barcode in stock_summary:
                        stock_summary[barcode]['total_stock'] += quantity
                    else:
                        stock_summary[barcode] = {
                            'barcode': barcode,
                            'product_name': row[3],
                            'total_stock': quantity
                        }
            
            return list(stock_summary.values())
            
        except Exception as e:
            print(f"Error getting stock summary: {e}")
            return []
    
    def initialize_product_sheet_headers(self, sheet_id):
        """Initialize Product Master sheet with headers"""
        if not self.sheets_service:
            return False
        
        try:
            headers = [['Barcode', 'Product Name']]
            
            body = {
                'values': headers
            }
            
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='Sheet1!D1:E1',  # Headers in columns D and E
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Product sheet headers initialized: {result.get('updatedCells')} cells updated")
            return True
            
        except Exception as e:
            print(f"Error initializing product sheet headers: {e}")
            return False
    
    def initialize_stock_sheet_headers(self, sheet_id):
        """Initialize Stock Counting sheet with headers"""
        if not self.sheets_service:
            return False
        
        try:
            headers = [['Date', 'Time', 'Barcode', 'Product Name', 'Quantity', 'Branch', 'User', 'Image URL', 'ชื่อผู้ตรวจนับสินค้า']]
            
            body = {
                'values': headers
            }
            
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='Sheet1!A1:I1',  # Extended to column I
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Stock sheet headers initialized: {result.get('updatedCells')} cells updated")
            return True
            
        except Exception as e:
            print(f"Error initializing stock sheet headers: {e}")
            return False
    
    def add_sample_products(self, sheet_id):
        """Add sample products to Product Master sheet"""
        if not self.sheets_service:
            return False
        
        try:
            sample_products = [
                ['1234567890123', 'น้ำดื่ม 600ml'],
                ['2345678901234', 'ข้าวสาร 5kg'],
                ['3456789012345', 'นมถั่วเหลือง 250ml'],
                ['4567890123456', 'ขนมปังแผ่น'],
                ['5678901234567', 'ไข่ไก่ 10 ฟอง'],
                ['6789012345678', 'น้ำตาลทราย 1kg'],
                ['7890123456789', 'น้ำปลา 700ml'],
                ['8901234567890', 'ข้าวโพดกระป๋อง'],
                ['9012345678901', 'ผงซักฟอก 3kg'],
                ['0123456789012', 'ยาสีฟัน 160g']
            ]
            
            body = {
                'values': sample_products
            }
            
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range='Sheet1!D:E',  # Append to columns D and E
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Sample products added: {result.get('updates').get('updatedCells')} cells updated")
            return True
            
        except Exception as e:
            print(f"Error adding sample products: {e}")
            return False

def create_sheets_manager(credentials_file='credentials.json'):
    """Factory function to create SheetsManager instance"""
    return SheetsManager(credentials_file)

# Example usage
if __name__ == '__main__':
    # Test the sheets manager
    manager = create_sheets_manager()
    
    # You would need to provide actual sheet IDs from your Google Sheets
    product_sheet_id = 'YOUR_PRODUCT_SHEET_ID'
    stock_sheet_id = 'YOUR_STOCK_SHEET_ID'
    
    print("Sheets manager initialized successfully")