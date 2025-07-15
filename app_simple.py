#!/usr/bin/env python3
"""
Simple Flask App without external dependencies
For quick UI testing
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta, date
import os
import json
from functools import wraps
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cgi

DATABASE = 'inventory.db'

# Simple session storage
sessions = {}

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def check_session(session_id):
    """Check if session is valid"""
    return session_id in sessions

def login_required(func):
    """Decorator to require login"""
    def wrapper(self, *args, **kwargs):
        session_id = self.get_session_id()
        if not session_id or not check_session(session_id):
            self.redirect('/login')
            return
        return func(self, *args, **kwargs)
    return wrapper

def admin_required(func):
    """Decorator to require admin role"""
    def wrapper(self, *args, **kwargs):
        session_id = self.get_session_id()
        if not session_id or not check_session(session_id):
            self.redirect('/login')
            return
        
        user_data = sessions.get(session_id)
        if not user_data or user_data.get('role') != 'admin':
            self.send_error(403, 'Admin access required')
            return
        return func(self, *args, **kwargs)
    return wrapper

def staff_required(func):
    """Decorator to require staff role"""
    def wrapper(self, *args, **kwargs):
        session_id = self.get_session_id()
        if not session_id or not check_session(session_id):
            self.redirect('/login')
            return
        
        user_data = sessions.get(session_id)
        if not user_data or user_data.get('role') != 'staff':
            self.send_error(403, 'Staff access required')
            return
        return func(self, *args, **kwargs)
    return wrapper

class InventoryHandler(BaseHTTPRequestHandler):
    
    def get_session_id(self):
        """Get session ID from cookies"""
        cookie_header = self.headers.get('Cookie', '')
        for cookie in cookie_header.split(';'):
            if 'session_id=' in cookie:
                return cookie.split('session_id=')[1].strip()
        return None
    
    def set_session_cookie(self, session_id):
        """Set session cookie"""
        self.send_header('Set-Cookie', f'session_id={session_id}; Path=/')
    
    def redirect(self, location):
        """Send redirect response"""
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()
    
    def send_html(self, html_content):
        """Send HTML response"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.handle_index()
        elif path == '/login':
            self.handle_login_get()
        elif path == '/logout':
            self.handle_logout()
        elif path.startswith('/get_product/'):
            barcode = path.split('/')[-1]
            self.handle_get_product(barcode)
        elif path == '/report/summary':
            self.handle_summary()
        elif path == '/report/slow':
            self.handle_slow()
        elif path.startswith('/static/'):
            self.handle_static()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/login':
            self.handle_login_post()
        elif path == '/submit_stock':
            self.handle_submit_stock()
        else:
            self.send_error(404)
    
    def handle_login_get(self):
        """Show login form"""
        html = '''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>เข้าสู่ระบบ</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; padding: 20px; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .demo { background: #f8f9fa; padding: 15px; margin-top: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>เข้าสู่ระบบ</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="ชื่อผู้ใช้" required>
            <input type="password" name="password" placeholder="รหัสผ่าน" required>
            <button type="submit">เข้าสู่ระบบ</button>
        </form>
        <div class="demo">
            <h3>ข้อมูลทดสอบ:</h3>
            <p><strong>Admin:</strong> admin / admin123</p>
            <p><strong>Staff:</strong> staff / staff123</p>
        </div>
    </div>
</body>
</html>'''
        self.send_html(html)
    
    def handle_login_post(self):
        """Process login"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Parse form data
        params = {}
        for param in post_data.split('&'):
            key, value = param.split('=')
            params[key] = value.replace('+', ' ')
        
        username = params.get('username', '')
        password = params.get('password', '')
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        with get_db() as conn:
            user = conn.execute('SELECT id, username, role FROM users WHERE username = ? AND password = ?',
                              (username, hashed_password)).fetchone()
            
            if user:
                session_id = hashlib.md5(f"{user['id']}{datetime.now()}".encode()).hexdigest()
                sessions[session_id] = {
                    'user_id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
                
                self.send_response(302)
                self.set_session_cookie(session_id)
                if user['role'] == 'admin':
                    self.send_header('Location', '/report/summary')
                else:
                    self.send_header('Location', '/')
                self.end_headers()
            else:
                self.handle_login_get()  # Show login form again
    
    def handle_logout(self):
        """Handle logout"""
        session_id = self.get_session_id()
        if session_id and session_id in sessions:
            del sessions[session_id]
        
        self.send_response(302)
        self.send_header('Set-Cookie', 'session_id=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT')
        self.send_header('Location', '/login')
        self.end_headers()
    
    @staff_required
    def handle_index(self):
        """Show stock counting page"""
        session_id = self.get_session_id()
        user_data = sessions.get(session_id, {})
        
        html = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>นับสต๊อกสินค้า</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        input, select, button {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
        button {{ background: #007bff; color: white; border: none; cursor: pointer; }}
        button:hover {{ background: #0056b3; }}
        .logout {{ background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
        .barcode-input {{ font-size: 18px; font-weight: bold; }}
        .product-info {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 10px 0; display: none; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>นับสต๊อกสินค้า</h1>
        <div>
            <span>ผู้ใช้: {user_data.get('username', 'Unknown')}</span>
            <a href="/logout" class="logout">ออกจากระบบ</a>
        </div>
    </div>
    
    <div class="card">
        <h2>📱 สแกนบาร์โค้ด</h2>
        <p>กรอกบาร์โค้ดด้วยตนเอง (ในการทดสอบนี้)</p>
        <input type="text" id="barcode" class="barcode-input" placeholder="กรอกบาร์โค้ดที่นี่" onchange="fetchProduct()">
        
        <div id="product-info" class="product-info">
            <h3 id="product-name"></h3>
            <p>บาร์โค้ด: <span id="product-barcode"></span></p>
        </div>
    </div>
    
    <div class="card">
        <h2>📝 บันทึกข้อมูล</h2>
        <form onsubmit="submitStock(event)">
            <input type="number" id="quantity" placeholder="จำนวนคงเหลือ" required>
            <select id="branch" required>
                <option value="">เลือกสาขา</option>
                <option value="สาขาหลัก">สาขาหลัก</option>
                <option value="สาขา 1">สาขา 1</option>
                <option value="สาขา 2">สาขา 2</option>
                <option value="สาขา 3">สาขา 3</option>
            </select>
            <button type="submit">บันทึกข้อมูล</button>
        </form>
    </div>
    
    <div class="card">
        <h3>🔍 บาร์โค้ดทดสอบ:</h3>
        <p>1234567890123 - น้ำดื่ม 600ml</p>
        <p>2345678901234 - ข้าวสาร 5kg</p>
        <p>3456789012345 - นมถั่วเหลือง 250ml</p>
        <p>4567890123456 - ขนมปังแผ่น</p>
    </div>
    
    <script>
        function fetchProduct() {{
            const barcode = document.getElementById('barcode').value;
            if (!barcode) return;
            
            fetch('/get_product/' + barcode)
                .then(response => response.json())
                .then(data => {{
                    if (data.error) {{
                        alert('ไม่พบสินค้า: ' + barcode);
                        document.getElementById('product-info').style.display = 'none';
                    }} else {{
                        document.getElementById('product-name').textContent = data.product_name;
                        document.getElementById('product-barcode').textContent = data.barcode;
                        document.getElementById('product-info').style.display = 'block';
                    }}
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    alert('เกิดข้อผิดพลาด');
                }});
        }}
        
        function submitStock(event) {{
            event.preventDefault();
            
            const barcode = document.getElementById('barcode').value;
            const quantity = document.getElementById('quantity').value;
            const branch = document.getElementById('branch').value;
            const productName = document.getElementById('product-name').textContent;
            
            if (!barcode || !quantity || !branch || !productName) {{
                alert('กรุณากรอกข้อมูลให้ครบถ้วน');
                return;
            }}
            
            const data = {{
                barcode: barcode,
                product_name: productName,
                quantity: parseInt(quantity),
                branch: branch
            }};
            
            fetch('/submit_stock', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify(data)
            }})
            .then(response => response.json())
            .then(result => {{
                if (result.success) {{
                    alert('บันทึกข้อมูลสำเร็จ!');
                    document.getElementById('quantity').value = '';
                    document.getElementById('branch').value = '';
                    document.getElementById('barcode').value = '';
                    document.getElementById('product-info').style.display = 'none';
                }} else {{
                    alert('เกิดข้อผิดพลาด');
                }}
            }})
            .catch(error => {{
                console.error('Error:', error);
                alert('เกิดข้อผิดพลาด');
            }});
        }}
    </script>
</body>
</html>'''
        self.send_html(html)
    
    def handle_get_product(self, barcode):
        """Get product by barcode"""
        with get_db() as conn:
            product = conn.execute('SELECT * FROM products WHERE barcode = ?', (barcode,)).fetchone()
            if product:
                self.send_json({
                    'barcode': product['barcode'],
                    'product_name': product['product_name']
                })
            else:
                self.send_json({'error': 'Product not found'})
    
    def handle_submit_stock(self):
        """Submit stock data"""
        session_id = self.get_session_id()
        if not session_id or not check_session(session_id):
            self.send_json({'error': 'Not authenticated'})
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)
        
        user_data = sessions[session_id]
        
        with get_db() as conn:
            conn.execute('''
                INSERT INTO stock_log (barcode, product_name, quantity, branch, created_by_user_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['barcode'], data['product_name'], data['quantity'], 
                  data['branch'], user_data['user_id']))
        
        self.send_json({'success': True})
    
    @admin_required
    def handle_summary(self):
        """Show summary report"""
        with get_db() as conn:
            products = conn.execute('''
                SELECT 
                    p.barcode,
                    p.product_name,
                    COALESCE(sl.total_stock, 0) as total_stock,
                    COALESCE(s.total_sold_30days, 0) as sold_30days
                FROM products p
                LEFT JOIN (
                    SELECT barcode, SUM(quantity) as total_stock
                    FROM stock_log
                    GROUP BY barcode
                ) sl ON p.barcode = sl.barcode
                LEFT JOIN (
                    SELECT 
                        barcode,
                        SUM(CASE WHEN date >= date('now', '-30 days') THEN quantity_sold ELSE 0 END) as total_sold_30days
                    FROM sales
                    GROUP BY barcode
                ) s ON p.barcode = s.barcode
                ORDER BY p.product_name
            ''').fetchall()
        
        table_rows = ''
        for product in products:
            table_rows += f'''
                <tr>
                    <td>{product['barcode']}</td>
                    <td>{product['product_name']}</td>
                    <td>{product['total_stock']}</td>
                    <td>{product['sold_30days']}</td>
                </tr>
            '''
        
        html = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>รายงานสรุป</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; }}
        .nav {{ display: flex; gap: 10px; }}
        .nav a {{ background: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; }}
        .nav a.danger {{ background: #dc3545; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 รายงานสรุป</h1>
        <div class="nav">
            <a href="/report/slow">สินค้าไม่เคลื่อนไหว</a>
            <a href="/logout" class="danger">ออกจากระบบ</a>
        </div>
    </div>
    
    <div class="card">
        <h2>📈 วิเคราะห์สต๊อกและยอดขาย</h2>
        <table>
            <thead>
                <tr>
                    <th>บาร์โค้ด</th>
                    <th>ชื่อสินค้า</th>
                    <th>สต๊อกคงเหลือ</th>
                    <th>ขาย 30 วัน</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
</body>
</html>'''
        self.send_html(html)
    
    @admin_required
    def handle_slow(self):
        """Show slow moving report"""
        with get_db() as conn:
            products = conn.execute('''
                SELECT 
                    p.barcode,
                    p.product_name,
                    COALESCE(sl.total_stock, 0) as total_stock,
                    COALESCE(s.last_sale_date, 'ไม่เคยขาย') as last_sale_date
                FROM products p
                LEFT JOIN (
                    SELECT barcode, SUM(quantity) as total_stock
                    FROM stock_log
                    GROUP BY barcode
                ) sl ON p.barcode = sl.barcode
                LEFT JOIN (
                    SELECT barcode, MAX(date) as last_sale_date
                    FROM sales
                    GROUP BY barcode
                ) s ON p.barcode = s.barcode
                WHERE s.barcode IS NULL 
                   OR s.last_sale_date < date('now', '-30 days')
                ORDER BY p.product_name
            ''').fetchall()
        
        table_rows = ''
        for product in products:
            table_rows += f'''
                <tr>
                    <td>{product['barcode']}</td>
                    <td>{product['product_name']}</td>
                    <td>{product['total_stock']}</td>
                    <td>{product['last_sale_date']}</td>
                </tr>
            '''
        
        html = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>สินค้าไม่เคลื่อนไหว</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .header {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; }}
        .nav {{ display: flex; gap: 10px; }}
        .nav a {{ background: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; }}
        .nav a.danger {{ background: #dc3545; }}
        .alert {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #856404; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚠️ สินค้าไม่เคลื่อนไหว</h1>
        <div class="nav">
            <a href="/report/summary">รายงานสรุป</a>
            <a href="/logout" class="danger">ออกจากระบบ</a>
        </div>
    </div>
    
    <div class="alert">
        <strong>คำเตือน:</strong> สินค้าเหล่านี้ไม่มีการขายในช่วง 30 วันที่ผ่านมา
    </div>
    
    <div class="card">
        <h2>📋 รายการสินค้าไม่เคลื่อนไหว</h2>
        <table>
            <thead>
                <tr>
                    <th>บาร์โค้ด</th>
                    <th>ชื่อสินค้า</th>
                    <th>สต๊อกคงเหลือ</th>
                    <th>ขายครั้งล่าสุด</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
</body>
</html>'''
        self.send_html(html)
    
    def handle_static(self):
        """Handle static files (minimal CSS/JS)"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'/* Static files not implemented in simple version */')

def run_server():
    """Run the simple HTTP server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, InventoryHandler)
    print("🚀 เซิร์ฟเวอร์เริ่มทำงานแล้ว!")
    print("📱 เปิดเบราว์เซอร์ไปที่: http://localhost:8000")
    print("👥 บัญชีทดสอบ: admin/admin123, staff/staff123")
    print("🛑 กด Ctrl+C เพื่อหยุดเซิร์ฟเวอร์")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 เซิร์ฟเวอร์หยุดทำงาน")
        httpd.server_close()

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DATABASE):
        print("❌ ไม่พบฐานข้อมูล กรุณารัน: python3 init_db.py")
        exit(1)
    
    run_server()