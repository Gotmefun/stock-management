#!/usr/bin/env python3
"""
ลบข้อมูลทั้งหมดแล้วนำเข้าใหม่จาก Google Sheets ตามข้อมูลจริง
Column C = รหัสสินค้า (SKU)
Column D = บาร์โค้ด (Barcode) 
Column E = ชื่อสินค้า (Name)
"""

import os
from supabase import create_client
from sheets_manager import create_sheets_manager

# Configuration
SUPABASE_URL = "https://khiooiigrfrluvyobljq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q"
PRODUCT_SHEET_ID = "17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM"

def clear_all_products():
    """ลบสินค้าทั้งหมดใน Supabase"""
    print("🗑️ ลบสินค้าทั้งหมดใน Supabase...")
    
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    try:
        # ลบทุกรายการใน products table
        result = client.table('products').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("✅ ลบข้อมูลเก่าทั้งหมดแล้ว")
        return True
    except Exception as e:
        print(f"❌ ไม่สามารถลบข้อมูลได้: {e}")
        return False

def get_all_products_from_sheets():
    """ดึงข้อมูลทั้งหมดจาก Google Sheets Column C, D, E"""
    print("📊 ดึงข้อมูลจาก Google Sheets...")
    
    sheets_manager = create_sheets_manager()
    if not sheets_manager:
        print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
        return []
    
    try:
        # อ่านข้อมูลจาก Column C (รหัสสินค้า), D (บาร์โค้ด), E (ชื่อสินค้า)
        result = sheets_manager.sheets_service.spreadsheets().values().get(
            spreadsheetId=PRODUCT_SHEET_ID,
            range='C:E'
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
                
            if len(row) >= 3:
                sku = row[0].strip() if row[0] else ''
                barcode = row[1].strip() if row[1] else '' 
                name = row[2].strip() if row[2] else ''
                
                # เก็บทุกรายการที่มีบาร์โค้ดและชื่อสินค้า (ไม่จำเป็นต้องมี SKU)
                if barcode and name:
                    # ถ้าไม่มี SKU ให้ใช้บาร์โค้ดแทน
                    final_sku = sku if sku else barcode
                    
                    products.append({
                        'sku': final_sku,
                        'barcode': barcode,
                        'name': name
                    })
        
        print(f"✅ ข้อมูลที่ใช้ได้: {len(products)} รายการ")
        
        # แสดงตัวอย่าง 10 รายการแรก
        print("🔍 ตัวอย่างข้อมูล 10 รายการแรก:")
        for i, product in enumerate(products[:10]):
            print(f"   {i+1}. SKU: '{product['sku']}' | Barcode: '{product['barcode']}' | Name: '{product['name'][:40]}...'")
        
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
    
    # เตรียมข้อมูลสำหรับ Supabase
    products_to_insert = []
    for product in products_data:
        product_record = {
            'sku': product['sku'],
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
    
    # นำเข้าทีละ batch
    batch_size = 100
    total_inserted = 0
    
    try:
        for i in range(0, len(products_to_insert), batch_size):
            batch = products_to_insert[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            print(f"📤 Batch {batch_num}: {len(batch)} รายการ...")
            
            try:
                result = client.table('products').insert(batch).execute()
                if result.data:
                    total_inserted += len(result.data)
                    print(f"✅ สำเร็จ {len(result.data)} รายการ")
            except Exception as batch_error:
                print(f"❌ Error ใน batch {batch_num}: {batch_error}")
                # ลองทีละรายการ
                for product in batch:
                    try:
                        single_result = client.table('products').insert([product]).execute()
                        if single_result.data:
                            total_inserted += 1
                    except Exception as single_error:
                        print(f"⚠️ Skip: {product['barcode']} - {single_error}")
        
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
        
        print("📱 บาร์โค้ดสำหรับทดสอบ:")
        for i, product in enumerate(products.data, 1):
            print(f"   {i}. '{product['barcode']}' → {product['name'][:50]}...")
            
    except Exception as e:
        print(f"❌ ไม่สามารถดึงข้อมูลทดสอบได้: {e}")

def main():
    print("🔄 ลบและนำเข้าข้อมูลใหม่จาก Google Sheets")
    print("📋 โครงสร้างข้อมูล:")
    print("   Column C = รหัสสินค้า (SKU)")
    print("   Column D = บาร์โค้ด (Barcode) ← ใช้สำหรับค้นหา")
    print("   Column E = ชื่อสินค้า (Name)")
    print("")
    
    # Step 1: Clear existing data
    if not clear_all_products():
        return False
    
    # Step 2: Get data from Google Sheets  
    products_data = get_all_products_from_sheets()
    if not products_data:
        return False
    
    # Step 3: Import to Supabase
    success = import_to_supabase(products_data)
    
    if success:
        print("\n🎉 การนำเข้าเสร็จสิ้น!")
        show_sample_barcodes()
        print("\n📱 ตอนนี้สามารถทดสอบที่ www.ptee88.com ได้แล้ว")
        print("🔍 ใช้บาร์โค้ดจริงจาก Google Sheets ของคุณ")
    else:
        print("\n❌ การนำเข้าล้มเหลว")
    
    return success

if __name__ == "__main__":
    main()