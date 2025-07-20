#!/usr/bin/env python3
"""
Simple Flask server สำหรับทดสอบบน Windows/WSL
"""

from flask import Flask, redirect, url_for
import socket

# Create simple test app
test_app = Flask(__name__)

@test_app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Test Server</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body style="padding: 20px; font-family: Arial;">
        <h1>🎉 Server Working!</h1>
        <p>เซิร์ฟเวอร์ทำงานแล้ว</p>
        <a href="/inventory" style="background: blue; color: white; padding: 10px; text-decoration: none;">
            ไปยังระบบ Inventory
        </a>
    </body>
    </html>
    """

@test_app.route('/inventory')
def inventory():
    return redirect('http://127.0.0.1:8080')

def get_all_ips():
    """Get all available IP addresses"""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

if __name__ == '__main__':
    local_ip = get_all_ips()
    
    print("🧪 Simple Test Server")
    print("=" * 40)
    print(f"Local:    http://127.0.0.1:3000")
    print(f"Network:  http://{local_ip}:3000")
    print("=" * 40)
    
    # Run on all interfaces, port 3000
    test_app.run(
        host='0.0.0.0',
        port=3000,
        debug=True
    )