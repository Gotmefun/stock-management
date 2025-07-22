#!/usr/bin/env python3
"""
Import จริงจาก Google Sheets Product Master Sheet เข้า Supabase
Import real products from Google Sheets to Supabase
"""

import os
from supabase import create_client
from sheets_manager import create_sheets_manager

# Configuration
SUPABASE_URL = "https://khiooiigrfrluvyobljq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q"
PRODUCT_SHEET_ID = "17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM"

def setup_supabase():
    """Setup Supabase client and tables"""
    print("🔗 เชื่อมต่อ Supabase...")
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Test connection
        result = client.table('products').select('count').execute()
        print("✅ เชื่อมต่อ Supabase สำเร็จ!")
        
        return client
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ Supabase: {e}")
        return None

def create_tables(supabase):
    """Create tables in Supabase"""
    print("🏗️ สร้างตารางใน Supabase...")
    
    sql_commands = [
        # Drop existing tables
        "DROP TABLE IF EXISTS stock_counts CASCADE;",
        "DROP TABLE IF EXISTS inventory CASCADE;", 
        "DROP TABLE IF EXISTS products CASCADE;",
        "DROP TABLE IF EXISTS branches CASCADE;",
        
        # Create products table
        """
        CREATE TABLE products (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            sku VARCHAR(50) UNIQUE NOT NULL,
            barcode VARCHAR(50) UNIQUE,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(100),
            brand VARCHAR(100),
            unit VARCHAR(20) DEFAULT 'pieces',
            cost_price DECIMAL(10,2),
            selling_price DECIMAL(10,2),
            reorder_level INTEGER DEFAULT 0,
            max_stock_level INTEGER,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create branches table
        """
        CREATE TABLE branches (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            code VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            address TEXT,
            phone VARCHAR(20),
            manager_name VARCHAR(100),
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create inventory table
        """
        CREATE TABLE inventory (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            product_id UUID REFERENCES products(id) ON DELETE CASCADE,
            branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
            quantity INTEGER DEFAULT 0,
            reserved_quantity INTEGER DEFAULT 0,
            last_counted_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(product_id, branch_id)
        );
        """,
        
        # Create stock_counts table
        """
        CREATE TABLE stock_counts (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            product_id UUID REFERENCES products(id),
            branch_id UUID REFERENCES branches(id),
            counted_quantity INTEGER NOT NULL,
            system_quantity INTEGER,
            variance INTEGER,
            counter_name VARCHAR(100) NOT NULL,
            image_url TEXT,
            notes TEXT,
            counted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Insert branches
        """
        INSERT INTO branches (code, name) VALUES 
        ('MAIN', 'สาขาหลัก'),
        ('CITY', 'สาขาตัวเมือง'),
        ('PONGPAI', 'สาขาโป่งไผ่'),
        ('SCHOOL', 'สาขาหน้าโรงเรียน');
        """
    ]
    
    for sql in sql_commands:
        try:
            if sql.strip():
                supabase.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ รันคำสั่ง SQL สำเร็จ")
        except Exception as e:
            print(f"⚠️ SQL Error: {e}")
    
    print("🏗️ สร้างตารางเสร็จสิ้น")

def import_products_from_sheets(supabase):
    """Import products from Google Sheets"""
    print("📊 นำเข้าสินค้าจาก Google Sheets...")
    
    try:
        sheets_manager = create_sheets_manager()
        if not sheets_manager:
            print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
            return False
        
        # Get products from Google Sheets
        print(f"📋 อ่านข้อมูลจาก Sheet ID: {PRODUCT_SHEET_ID}")
        products_data = sheets_manager.get_all_products(PRODUCT_SHEET_ID)
        
        if not products_data:
            print("❌ ไม่มีข้อมูลสินค้าใน Google Sheets")
            return False
        
        print(f"📦 พบสินค้า {len(products_data)} รายการ")
        
        # Transform and insert into Supabase
        products_to_insert = []
        for i, product in enumerate(products_data):
            barcode = product.get('barcode', '').strip()
            name = product.get('name', '').strip()
            
            if not barcode or not name:
                print(f"⚠️ Skip รายการที่ {i+1}: ไม่มี barcode หรือ name")
                continue
            
            product_record = {
                'sku': barcode,  # Use barcode as SKU
                'barcode': barcode,
                'name': name,
                'description': f"Imported from Google Sheets - {name}",
                'category': 'General',
                'brand': 'Unknown',
                'unit': 'pieces',
                'cost_price': 0.00,
                'selling_price': 0.00,
                'reorder_level': 10,
                'max_stock_level': 100,
                'is_active': True
            }
            
            products_to_insert.append(product_record)
            print(f"📝 เตรียม: {barcode} - {name}")
        
        if not products_to_insert:
            print("❌ ไม่มีสินค้าที่ถูกต้องให้นำเข้า")
            return False
        
        # Insert into Supabase
        print(f"💾 บันทึกสินค้า {len(products_to_insert)} รายการลง Supabase...")
        result = supabase.table('products').insert(products_to_insert).execute()
        
        if result.data:
            print(f"✅ นำเข้าสินค้าสำเร็จ {len(result.data)} รายการ!")
            print("\n📋 สินค้าที่นำเข้า:")
            for product in result.data[:10]:  # Show first 10
                print(f"   🏷️ {product['barcode']} - {product['name']}")
            
            if len(result.data) > 10:
                print(f"   ... และอีก {len(result.data) - 10} รายการ")
            
            return True
        else:
            print("❌ การนำเข้าล้มเหลว")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_product_search(supabase):
    """Test product search"""
    print("\n🔍 ทดสอบการค้นหาสินค้า...")
    
    try:
        # Get first few products for testing
        result = supabase.table('products').select('barcode, name').limit(5).execute()
        
        if result.data:
            print("✅ ทดสอบบาร์โค้ดเหล่านี้:")
            for product in result.data:
                print(f"   📱 {product['barcode']} → {product['name']}")
        else:
            print("❌ ไม่พบสินค้าสำหรับทดสอบ")
            
    except Exception as e:
        print(f"❌ การทดสอบล้มเหลว: {e}")

def main():
    """Main function"""
    print("🚀 เริ่มนำเข้าสินค้าจริงจาก Google Sheets เข้า Supabase...")
    
    # Setup Supabase
    supabase = setup_supabase()
    if not supabase:
        return False
    
    # Create tables (this will also work via SQL Editor)
    print("📋 คำแนะนำ: รันคำสั่ง SQL ต่อไปนี้ใน Supabase SQL Editor ก่อน:")
    print("=" * 60)
    print("ไปที่ Supabase Dashboard → SQL Editor → รันคำสั่งนี้:")
    print()
    print("""
-- ลบตารางเก่า
DROP TABLE IF EXISTS stock_counts CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS branches CASCADE;

-- สร้างตารางใหม่
CREATE TABLE products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    barcode VARCHAR(50) UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    brand VARCHAR(100),
    unit VARCHAR(20) DEFAULT 'pieces',
    cost_price DECIMAL(10,2),
    selling_price DECIMAL(10,2),
    reorder_level INTEGER DEFAULT 0,
    max_stock_level INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE branches (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    manager_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- เพิ่มสาขา
INSERT INTO branches (code, name) VALUES 
('MAIN', 'สาขาหลัก'),
('CITY', 'สาขาตัวเมือง'),
('PONGPAI', 'สาขาโป่งไผ่'),
('SCHOOL', 'สาขาหน้าโรงเรียน');
    """)
    print("=" * 60)
    
    input("กด Enter หลังจากรันคำสั่ง SQL แล้ว...")
    
    # Import products
    success = import_products_from_sheets(supabase)
    
    if success:
        # Test search
        test_product_search(supabase)
        
        print("\n🎉 การนำเข้าเสร็จสิ้น!")
        print("📱 ตอนนี้สามารถทดสอบการสแกนบาร์โค้ดได้แล้ว:")
        print("   1. Deploy ใหม่ใน Render")
        print("   2. ไปที่ www.ptee88.com")
        print("   3. ทดสอบการนับสต๊อกด้วยบาร์โค้ดจริง")
        
        return True
    else:
        print("❌ การนำเข้าล้มเหลว")
        return False

if __name__ == "__main__":
    main()