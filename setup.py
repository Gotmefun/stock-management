#!/usr/bin/env python3
"""
Setup script for Inventory Management System
"""

import sqlite3
import os
import sys

def create_database():
    """Create and initialize the database"""
    print("Creating database...")
    
    # Import and run the Flask app initialization
    from app import init_db
    init_db()
    
    print("Database created successfully with sample data!")

def create_directories():
    """Create necessary directories"""
    directories = [
        'uploads',
        'templates',
        'static',
        'backups'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def display_setup_info():
    """Display setup information"""
    print("\n" + "="*60)
    print("INVENTORY MANAGEMENT SYSTEM SETUP COMPLETE")
    print("="*60)
    print("\n🎉 Setup completed successfully!\n")
    
    print("📁 Files created:")
    print("   - app.py (Main Flask application)")
    print("   - templates/ (HTML templates)")
    print("   - static/ (CSS, JS, images)")
    print("   - sync_sales.py (Sales data sync script)")
    print("   - upload_to_drive.py (Google Drive integration)")
    print("   - requirements.txt (Python dependencies)")
    print("   - inventory.db (SQLite database)")
    
    print("\n👥 Test Users:")
    print("   Admin: username=admin, password=admin123")
    print("   Staff: username=staff, password=staff123")
    
    print("\n📱 Sample Products (for testing):")
    print("   - 1234567890123: น้ำดื่ม 600ml")
    print("   - 2345678901234: ข้าวสาร 5kg")
    print("   - 3456789012345: นมถั่วเหลือง 250ml")
    print("   - 4567890123456: ขนมปังแผ่น")
    print("   - 5678901234567: ไข่ไก่ 10 ฟอง")
    
    print("\n🚀 To run the application:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Run the app: python app.py")
    print("   3. Open browser to: http://localhost:5000")
    
    print("\n📊 Sales Data Sync:")
    print("   - Generate sample: python sync_sales.py --sample")
    print("   - Sync from CSV: python sync_sales.py --csv sample_sales.csv")
    print("   - Sync from Google Sheets: python sync_sales.py --sheet-id YOUR_SHEET_ID")
    
    print("\n🖼️ Google Drive Setup (Optional):")
    print("   1. Go to Google Cloud Console")
    print("   2. Create project and enable Google Drive API")
    print("   3. Create credentials (OAuth 2.0 or Service Account)")
    print("   4. Download credentials.json or service_account.json")
    print("   5. Install: pip install google-api-python-client google-auth-oauthlib")
    
    print("\n🔧 Features:")
    print("   ✅ User authentication (admin/staff roles)")
    print("   ✅ Barcode scanning with html5-qrcode")
    print("   ✅ Mobile camera integration")
    print("   ✅ Multi-branch support")
    print("   ✅ Stock counting with photos")
    print("   ✅ Sales analysis reports")
    print("   ✅ Slow-moving inventory detection")
    print("   ✅ Google Drive photo uploads")
    print("   ✅ CSV/Google Sheets sales sync")
    
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print("Setting up Inventory Management System...")
    
    # Create necessary directories
    create_directories()
    
    # Create and initialize database
    create_database()
    
    # Display setup information
    display_setup_info()

if __name__ == '__main__':
    main()