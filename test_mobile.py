#!/usr/bin/env python3
"""
Mobile Testing Server for Inventory Management System
รันเซิร์ฟเวอร์ทดสอบสำหรับมือถือ
"""

import os
import sys
import socket
from app import app, init_db

def get_local_ip():
    """Get local IP address"""
    # Use the actual WiFi IP from Windows
    return "192.168.1.59"

def main():
    """Run mobile testing server"""
    print("🧪 Mobile Testing Server for Inventory Management System")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Get IP addresses
    local_ip = get_local_ip()
    
    print(f"📱 Testing URLs:")
    print(f"   Local:     http://localhost:5000")
    print(f"   Network:   http://{local_ip}:5000")
    print()
    print(f"👤 Login Credentials:")
    print(f"   Staff:     username=staff, password=staff123")
    print(f"   Admin:     username=admin, password=admin123")
    print()
    print(f"📋 Testing Checklist:")
    print(f"   ✅ Login system")
    print(f"   ✅ Barcode scanning (camera)")
    print(f"   ✅ Stock counting")
    print(f"   ✅ Image capture")
    print(f"   ✅ Google Drive upload")
    print(f"   ✅ Admin reports")
    print()
    print(f"🔧 Press Ctrl+C to stop server")
    print("=" * 60)
    
    try:
        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=5000,  # Back to port 5000
            debug=False,  # Disable debug for testing
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == '__main__':
    main()