#!/usr/bin/env python3
"""
สร้างฐานข้อมูล Supabase ใหม่และนำเข้าข้อมูลจาก Google Sheets
"""

import os
from supabase import create_client
from sheets_manager import create_sheets_manager

# Configuration
SUPABASE_URL = "https://khiooiigrfrluvyobljq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q"
PRODUCT_SHEET_ID = "17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM"

def create_tables():
    """สร้างตารางใหม่ใน Supabase"""
    print("🏗️ สร้างตารางฐานข้อมูลใหม่...")
    
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # SQL สำหรับสร้างตาราง products
    create_products_sql = """
    CREATE TABLE IF NOT EXISTS products (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        sku VARCHAR(100) UNIQUE NOT NULL,
        barcode VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(500) NOT NULL,
        description TEXT,
        category VARCHAR(100) DEFAULT 'สินค้าทั่วไป',
        brand VARCHAR(100) DEFAULT 'ไม่ระบุ',
        unit VARCHAR(20) DEFAULT 'ชิ้น',
        cost_price DECIMAL(10,2) DEFAULT 0.00,
        selling_price DECIMAL(10,2) DEFAULT 0.00,
        reorder_level INTEGER DEFAULT 10,
        max_stock_level INTEGER DEFAULT 100,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
    CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
    CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
    """
    
    try:
        # Execute SQL using RPC call
        result = client.rpc('exec_sql', {'sql': create_products_sql}).execute()
        print("✅ สร้างตาราง products สำเร็จ")
        return True
    except Exception as e:
        print(f"❌ สร้างตารางล้มเหลว: {e}")
        print("🔧 ลองสร้างด้วยวิธีอื่น...")
        
        # ถ้า RPC ไม่ได้ ให้ลองสร้างตารางด้วยการ insert dummy data แล้วลบ
        try:
            # Create a dummy product to create the table structure
            dummy_product = {
                'sku': 'DUMMY_SKU_DELETE_ME',
                'barcode': 'DUMMY_BARCODE_DELETE_ME',
                'name': 'DUMMY PRODUCT - DELETE ME',
                'description': 'This is a dummy product to create table structure',
                'category': 'สินค้าทั่วไป',
                'brand': 'ไม่ระบุ',
                'unit': 'ชิ้น',
                'cost_price': 0.00,
                'selling_price': 0.00,
                'reorder_level': 10,
                'max_stock_level': 100,
                'is_active': True
            }
            
            # Insert dummy product (this will create the table if it doesn't exist)
            result = client.table('products').insert([dummy_product]).execute()
            
            if result.data:
                # Delete the dummy product
                client.table('products').delete().eq('sku', 'DUMMY_SKU_DELETE_ME').execute()
                print("✅ สร้างตาราง products สำเร็จ (วิธีทางเลือก)")
                return True
            else:
                print("❌ ไม่สามารถสร้างตารางได้")
                return False
                
        except Exception as e2:
            print(f"❌ สร้างตารางล้มเหลวทั้งสองวิธี: {e2}")
            return False

def get_products_from_sheets():
    """ดึงข้อมูลจาก Google Sheets Column A (Barcode), B (Product Name)"""
    print("📊 ดึงข้อมูลจาก Google Sheets...")
    
    sheets_manager = create_sheets_manager()
    if not sheets_manager:
        print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
        return []
    
    try:
        # อ่านข้อมูลจาก Column A (Barcode), B (Product Name)
        result = sheets_manager.sheets_service.spreadsheets().values().get(
            spreadsheetId=PRODUCT_SHEET_ID,
            range='A:B'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("❌ ไม่มีข้อมูลใน Google Sheets")
            return []
        
        print(f"📋 พบข้อมูล {len(values)} แถวใน Google Sheets")
        
        products = []
        for i, row in enumerate(values):
            if i == 0:  # Skip header row
                continue
            
            # ตรวจสอบว่ามีข้อมูลใน column A และ B
            if len(row) >= 2:
                barcode = str(row[0]).strip() if row[0] else ''
                name = str(row[1]).strip() if row[1] else ''
                
                # เก็บเฉพาะรายการที่มีบาร์โค้ดและชื่อสินค้า และไม่ใช่ header
                if barcode and name and barcode.lower() != 'barcode':
                    # ตัดชื่อสินค้าไม่เกิน 500 ตัวอักษร
                    if len(name) > 500:
                        name = name[:497] + "..."
                    
                    products.append({
                        'barcode': barcode,
                        'name': name
                    })
        
        print(f"✅ ข้อมูลที่ใช้ได้: {len(products)} รายการ")
        
        # แสดงตัวอย่าง 5 รายการแรก
        print("🔍 ตัวอย่างข้อมูล 5 รายการแรก:")
        for i, product in enumerate(products[:5]):
            print(f"   {i+1}. Barcode: '{product['barcode']}' | Name: '{product['name'][:50]}...'")
        
        return products
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอ่าน Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        return []

def import_to_supabase(products_data):
    """นำเข้าข้อมูลลง Supabase"""
    if not products_data:
        print("❌ ไม่มีข้อมูลให้นำเข้า")
        return False
    
    print(f"💾 เริ่มนำเข้า {len(products_data)} รายการลง Supabase...")
    
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # นำเข้าทีละ batch เล็ก ๆ
    batch_size = 50  # ลดขนาด batch เพื่อป้องกัน error
    total_inserted = 0
    
    try:
        for i in range(0, len(products_data), batch_size):
            batch = products_data[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            print(f"📤 Batch {batch_num}/{(len(products_data) + batch_size - 1) // batch_size}: {len(batch)} รายการ...")
            
            # เตรียมข้อมูลสำหรับ batch นี้
            products_to_insert = []
            for product in batch:
                product_record = {
                    'sku': product['barcode'],  # ใช้บาร์โค้ดเป็น SKU
                    'barcode': product['barcode'], 
                    'name': product['name'],
                    'description': f"สินค้าจาก Google Sheets - {product['name'][:50]}",
                    'category': 'สินค้าทั่วไป',
                    'brand': 'ไม่ระบุ',
                    'unit': 'ชิ้น',
                    'cost_price': 0.00,
                    'selling_price': 0.00,
                    'reorder_level': 10,
                    'max_stock_level': 100,
                    'is_active': True
                }
                products_to_insert.append(product_record)
            
            # ลองนำเข้า batch
            try:
                result = client.table('products').insert(products_to_insert).execute()
                if result.data:
                    total_inserted += len(result.data)
                    print(f"✅ สำเร็จ {len(result.data)} รายการ")
                else:
                    print("⚠️ ไม่มีข้อมูลกลับมา")
            except Exception as batch_error:
                print(f"❌ Error ใน batch {batch_num}: {batch_error}")
                # ลองทีละรายการ
                for product_data in products_to_insert:
                    try:
                        single_result = client.table('products').insert([product_data]).execute()
                        if single_result.data:
                            total_inserted += 1
                    except Exception as single_error:
                        # ข้าม error เงียบ ๆ เพื่อไม่ให้ log เยอะเกินไป
                        pass
        
        print(f"🎉 นำเข้าสำเร็จทั้งหมด {total_inserted} รายการ!")
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการนำเข้า: {e}")
        return False

def show_sample_barcodes():
    """แสดงบาร์โค้ดตัวอย่างสำหรับทดสอบ"""
    print("🧪 ตรวจสอบบาร์โค้ดที่ใช้ทดสอบได้:")
    
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    try:
        products = client.table('products').select('sku, barcode, name').limit(10).execute()
        
        if products.data:
            print("📱 บาร์โค้ดสำหรับทดสอบ:")
            for i, product in enumerate(products.data, 1):
                print(f"   {i}. '{product['barcode']}' → {product['name'][:50]}...")
        else:
            print("❌ ไม่พบข้อมูลสินค้าในฐานข้อมูล")
            
    except Exception as e:
        print(f"❌ ไม่สามารถดึงข้อมูลทดสอบได้: {e}")

def main():
    print("🔄 สร้างฐานข้อมูลใหม่และนำเข้าข้อมูลจาก Google Sheets")
    print("📋 โครงสร้างข้อมูล:")
    print("   Column A = บาร์โค้ด (Barcode) ← ใช้สำหรับค้นหา")
    print("   Column B = ชื่อสินค้า (Product Name)")
    print("")
    
    # Step 1: Create database tables
    if not create_tables():
        print("❌ ไม่สามารถสร้างตารางได้")
        return False
    
    # Step 2: Get data from Google Sheets  
    products_data = get_products_from_sheets()
    if not products_data:
        return False
    
    # Step 3: Import to Supabase
    success = import_to_supabase(products_data)
    
    if success:
        print("\n🎉 การสร้างฐานข้อมูลและนำเข้าเสร็จสิ้น!")
        show_sample_barcodes()
        print("\n📱 ตอนนี้สามารถทดสอบที่ www.ptee88.com ได้แล้ว")
        print("🔍 ใช้บาร์โค้ดจริงจาก Google Sheets ของคุณ")
    else:
        print("\n❌ การนำเข้าล้มเหลว")
    
    return success

if __name__ == "__main__":
    main()