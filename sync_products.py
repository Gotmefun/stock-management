#!/usr/bin/env python3
"""
Sync product data from Google Sheets to local SQLite database
"""

import sqlite3
import os
from upload_to_drive import create_drive_uploader

# For Google Sheets API
try:
    from googleapiclient.discovery import build
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

DATABASE = 'inventory.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def sync_products_from_sheet():
    """Sync products from Google Sheets to local database"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        print("Google Sheets API not available. Please install google-api-python-client")
        return False
    
    try:
        # Use service account directly for Sheets API
        from google.oauth2 import service_account
        
        SERVICE_ACCOUNT_FILE = 'service_account.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # Use existing Product Master sheet
        sheet_id = "1OaEqOS7I0_hN2Q1nc4isqPXXdjp7_i7ZAPJFhUr5X7k"
        
        # Build Sheets service
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        # Read data from sheet
        range_name = 'Sheet1!D:E'  # Column D=Barcode, E=Product Name
        
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print('No data found in products sheet')
            return False
        
        # Update local database
        with get_db() as conn:
            # Clear existing products
            conn.execute('DELETE FROM products')
            
            # Insert products from sheet (skip header row)
            for i, row in enumerate(values[1:], 1):
                if len(row) >= 2:
                    barcode = row[0].strip()
                    product_name = row[1].strip()
                    
                    if barcode and product_name:
                        conn.execute(
                            'INSERT OR REPLACE INTO products (barcode, product_name) VALUES (?, ?)',
                            (barcode, product_name)
                        )
                        print(f"Added: {barcode} - {product_name}")
        
        print(f"Successfully synced {len(values)-1} products from Google Sheets")
        return True
        
    except Exception as e:
        print(f"Error syncing products: {e}")
        return False

def export_current_products_to_sheet():
    """Export current products from local database to Google Sheets"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        print("Google Sheets API not available. Please install google-api-python-client")
        return False
    
    try:
        # Get current products from database
        with get_db() as conn:
            products = conn.execute('SELECT barcode, product_name FROM products ORDER BY product_name').fetchall()
        
        if not products:
            print("No products found in local database")
            return False
        
        # Use service account directly for Sheets API
        from google.oauth2 import service_account
        
        SERVICE_ACCOUNT_FILE = 'service_account.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # Use existing Product Master sheet
        sheet_id = "1OaEqOS7I0_hN2Q1nc4isqPXXdjp7_i7ZAPJFhUr5X7k"
        
        # Build Sheets service
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        # Prepare data for sheet (use columns D and E)
        values = [['Barcode', 'Product Name']]  # Header row
        for product in products:
            values.append([product['barcode'], product['product_name']])
        
        # Update sheet columns D and E
        
        # Clear existing content in columns D:E
        sheets_service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range='Sheet1!D:E'
        ).execute()
        
        # Write new data to columns D:E
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='Sheet1!D1',
            valueInputOption='RAW',
            body={'values': values}
        ).execute()
        
        print(f"Successfully exported {len(products)} products to Google Sheets")
        print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
        return True
        
    except Exception as e:
        print(f"Error exporting products: {e}")
        return False

def show_menu():
    """Show menu options"""
    print("\n=== Product Data Management ===")
    print("1. Sync products FROM Google Sheets TO local database")
    print("2. Export products FROM local database TO Google Sheets")
    print("3. View current products in local database")
    print("4. Exit")

def view_current_products():
    """Display current products in local database"""
    try:
        with get_db() as conn:
            products = conn.execute('SELECT barcode, product_name FROM products ORDER BY product_name').fetchall()
        
        if not products:
            print("No products found in local database")
            return
        
        print(f"\nCurrent products in database ({len(products)} items):")
        print("-" * 60)
        for product in products:
            print(f"{product['barcode']:15} | {product['product_name']}")
        
    except Exception as e:
        print(f"Error viewing products: {e}")

if __name__ == '__main__':
    print("Product Data Sync Tool")
    print("Make sure you have set up Google Drive/Sheets API credentials")
    
    while True:
        show_menu()
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            print("\nSyncing products from Google Sheets...")
            if sync_products_from_sheet():
                print("✓ Sync completed successfully")
            else:
                print("✗ Sync failed")
                
        elif choice == '2':
            print("\nExporting products to Google Sheets...")
            if export_current_products_to_sheet():
                print("✓ Export completed successfully")
            else:
                print("✗ Export failed")
                
        elif choice == '3':
            view_current_products()
            
        elif choice == '4':
            print("Goodbye!")
            break
            
        else:
            print("Invalid option. Please try again.")