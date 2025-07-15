#!/usr/bin/env python3
"""
Database initialization script
"""

import sqlite3
import hashlib
from datetime import date, timedelta
import os

DATABASE = 'inventory.db'

def init_db():
    """Initialize database with tables and sample data"""
    conn = sqlite3.connect(DATABASE)
    conn.executescript('''
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS stock_log;
        DROP TABLE IF EXISTS sales;
        
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'staff'))
        );
        
        CREATE TABLE products (
            barcode TEXT PRIMARY KEY,
            product_name TEXT NOT NULL
        );
        
        CREATE TABLE stock_log (
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
        
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT NOT NULL,
            quantity_sold INTEGER NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (barcode) REFERENCES products (barcode)
        );
    ''')
    
    # Insert sample users
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    staff_password = hashlib.sha256('staff123'.encode()).hexdigest()
    
    conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                ('admin', admin_password, 'admin'))
    conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                ('staff', staff_password, 'staff'))
    
    # Insert sample products
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
        conn.execute('INSERT INTO products (barcode, product_name) VALUES (?, ?)',
                    (barcode, name))
    
    # Insert sample sales data
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
        # Products 9012345678901 and 0123456789012 have no sales (for slow-moving report)
    ]
    
    for barcode, qty, sale_date in sample_sales:
        conn.execute('INSERT INTO sales (barcode, quantity_sold, date) VALUES (?, ?, ?)',
                    (barcode, qty, sale_date))
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")
    print("Sample data created:")
    print("- Users: admin/admin123, staff/staff123")
    print("- Products: 10 sample items")
    print("- Sales: Sample sales data")

if __name__ == '__main__':
    # Create directories
    for directory in ['uploads', 'templates', 'static', 'backups']:
        os.makedirs(directory, exist_ok=True)
    
    init_db()