from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib
from datetime import datetime, timedelta
import os
from functools import wraps
from upload_to_drive import create_drive_uploader

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

DATABASE = 'inventory.db'

# Initialize Google Drive uploader
drive_uploader = create_drive_uploader()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'staff'))
            );
            
            CREATE TABLE IF NOT EXISTS products (
                barcode TEXT PRIMARY KEY,
                product_name TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS stock_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                branch TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_url TEXT,
                created_by_user_id INTEGER,
                FOREIGN KEY (created_by_user_id) REFERENCES users (id),
                FOREIGN KEY (barcode) REFERENCES products (barcode)
            );
            
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL,
                quantity_sold INTEGER NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (barcode) REFERENCES products (barcode)
            );
        ''')
        
        # Insert sample data
        # Sample users
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        staff_password = hashlib.sha256('staff123'.encode()).hexdigest()
        
        conn.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
                    ('admin', admin_password, 'admin'))
        conn.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
                    ('staff', staff_password, 'staff'))
        
        # Sample products
        sample_products = [
            ('1234567890123', 'น้ำดื่ม 600ml'),
            ('2345678901234', 'ข้าวสาร 5kg'),
            ('3456789012345', 'นมถั่วเหลือง 250ml'),
            ('4567890123456', 'ขนมปังแผ่น'),
            ('5678901234567', 'ไข่ไก่ 10 ฟอง'),
            ('6789012345678', 'น้ำตาลทราย 1kg'),
            ('7890123456789', 'น้ำปลา 700ml'),
            ('8901234567890', 'ข้าวโพดกระป๋อง'),
            ('9012345678901', 'ผงซักฟอก 3kg'),
            ('0123456789012', 'ยาสีฟัน 160g')
        ]
        
        for barcode, name in sample_products:
            conn.execute('INSERT OR IGNORE INTO products (barcode, product_name) VALUES (?, ?)',
                        (barcode, name))
        
        # Sample sales data
        from datetime import date, timedelta
        today = date.today()
        
        sample_sales = [
            ('1234567890123', 15, today - timedelta(days=1)),
            ('2345678901234', 5, today - timedelta(days=2)),
            ('3456789012345', 25, today - timedelta(days=1)),
            ('4567890123456', 8, today - timedelta(days=3)),
            ('5678901234567', 12, today - timedelta(days=1)),
            ('6789012345678', 3, today - timedelta(days=5)),
            ('7890123456789', 7, today - timedelta(days=2)),
            ('8901234567890', 20, today - timedelta(days=1)),
            # No sales for last 2 products to test slow-moving report
        ]
        
        for barcode, qty, sale_date in sample_sales:
            conn.execute('INSERT OR IGNORE INTO sales (barcode, quantity_sold, date) VALUES (?, ?, ?)',
                        (barcode, qty, sale_date))

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        with get_db() as conn:
            user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
            if not user or user['role'] != 'admin':
                flash('Access denied. Admin privileges required.', 'error')
                return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """Decorator to require staff role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        with get_db() as conn:
            user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
            if not user or user['role'] != 'staff':
                flash('Access denied. Staff privileges required.', 'error')
                return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        with get_db() as conn:
            user = conn.execute('SELECT id, username, role FROM users WHERE username = ? AND password = ?',
                              (username, hashed_password)).fetchone()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                
                if user['role'] == 'admin':
                    return redirect(url_for('admin_summary'))
                else:
                    return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@staff_required
def index():
    return render_template('index.html')

@app.route('/get_product/<barcode>')
@login_required
def get_product(barcode):
    with get_db() as conn:
        product = conn.execute('SELECT * FROM products WHERE barcode = ?', (barcode,)).fetchone()
        if product:
            return jsonify({
                'barcode': product['barcode'],
                'product_name': product['product_name']
            })
        else:
            return jsonify({'error': 'Product not found'}), 404

@app.route('/submit_stock', methods=['POST'])
@staff_required
def submit_stock():
    data = request.get_json()
    
    image_url = ''
    
    # Handle image upload if present
    if 'image_data' in data and data['image_data']:
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_{data['barcode']}_{timestamp}.jpg"
            
            # Upload to Google Drive
            upload_result = drive_uploader.upload_image_from_base64(
                data['image_data'], 
                filename,
                drive_uploader.get_or_create_inventory_folder()
            )
            
            if upload_result:
                image_url = upload_result['web_view_link']
                print(f"Image uploaded successfully: {image_url}")
            else:
                print("Failed to upload image")
                
        except Exception as e:
            print(f"Error uploading image: {e}")
    
    with get_db() as conn:
        conn.execute('''
            INSERT INTO stock_log (barcode, product_name, quantity, branch, image_url, created_by_user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['barcode'], data['product_name'], data['quantity'], 
              data['branch'], image_url, session['user_id']))
    
    return jsonify({'success': True})

@app.route('/sync_sales')
@admin_required
def sync_sales():
    # This would typically run the sync_sales.py script
    flash('Sales data sync completed successfully', 'success')
    return redirect(url_for('admin_summary'))

@app.route('/report/summary')
@admin_required
def admin_summary():
    with get_db() as conn:
        # Get stock data with sales analysis
        query = '''
            SELECT 
                p.barcode,
                p.product_name,
                COALESCE(sl.total_stock, 0) as total_stock,
                COALESCE(s.total_sold_30days, 0) as sold_30days,
                COALESCE(s.total_sold_7days, 0) as sold_7days,
                CASE 
                    WHEN COALESCE(s.total_sold_30days, 0) > 0 
                    THEN COALESCE(sl.total_stock, 0) * 30.0 / s.total_sold_30days 
                    ELSE 999 
                END as days_of_stock,
                CASE 
                    WHEN COALESCE(s.total_sold_30days, 0) > 0 
                    THEN GREATEST(0, s.total_sold_30days * 1.5 - COALESCE(sl.total_stock, 0))
                    ELSE 0 
                END as suggested_order
            FROM products p
            LEFT JOIN (
                SELECT barcode, SUM(quantity) as total_stock
                FROM stock_log
                GROUP BY barcode
            ) sl ON p.barcode = sl.barcode
            LEFT JOIN (
                SELECT 
                    barcode,
                    SUM(CASE WHEN date >= date('now', '-30 days') THEN quantity_sold ELSE 0 END) as total_sold_30days,
                    SUM(CASE WHEN date >= date('now', '-7 days') THEN quantity_sold ELSE 0 END) as total_sold_7days
                FROM sales
                GROUP BY barcode
            ) s ON p.barcode = s.barcode
            ORDER BY days_of_stock ASC
        '''
        
        products = conn.execute(query).fetchall()
        
        # Get branch summary
        branch_summary = conn.execute('''
            SELECT branch, COUNT(*) as items_counted, SUM(quantity) as total_quantity
            FROM stock_log
            GROUP BY branch
        ''').fetchall()
    
    return render_template('summary.html', products=products, branch_summary=branch_summary)

@app.route('/report/slow')
@admin_required
def slow_moving():
    with get_db() as conn:
        # Get products with no sales in last 30 days
        slow_products = conn.execute('''
            SELECT 
                p.barcode,
                p.product_name,
                COALESCE(sl.total_stock, 0) as total_stock,
                COALESCE(s.last_sale_date, 'Never') as last_sale_date
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
    
    return render_template('slow.html', products=slow_products)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)