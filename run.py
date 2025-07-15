#!/usr/bin/env python3
"""
Run the inventory management system
"""

import os
import sys

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import pandas
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def main():
    print("🚀 Starting Inventory Management System...")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists('inventory.db'):
        print("⚠️  Database not found. Creating...")
        os.system('python3 init_db.py')
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Import and run the Flask app
    try:
        from app import app
        print("🌐 Starting web server...")
        print("📱 Open your browser to: http://localhost:5000")
        print("👥 Test users: admin/admin123, staff/staff123")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()