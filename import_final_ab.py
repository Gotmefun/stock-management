#!/usr/bin/env python3
"""
นำเข้าสินค้าจาก Google Sheets โครงสร้างใหม่ (เวอร์ชันสุดท้าย)
Column A = Barcode (บาร์โค้ด)
Column B = Product Name (ชื่อสินค้า)
"""

import os
from supabase import create_client
from sheets_manager import create_sheets_manager

# Configuration
SUPABASE_URL = "https://khiooiigrfrluvyobljq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q"
PRODUCT_SHEET_ID = "17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM"

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
        skipped = 0
        
        for i, row in enumerate(values):
            if i == 0:  # Skip header row
                continue
            
            # ตรวจสอบว่ามีข้อมูลใน column A และ B
            if len(row) >= 2:
                barcode = str(row[0]).strip() if row[0] else ''
                name = str(row[1]).strip() if row[1] else ''
                
                # เก็บเฉพาะรายการที่มีบาร์โค้ดและชื่อสินค้า และไม่ใช่ header
                if barcode and name and barcode.lower() not in ['barcode', 'บาร์โค้ด']:
                    # ตัดชื่อสินค้าไม่เกิน 500 ตัวอักษร
                    if len(name) > 500:
                        name = name[:497] + "..."
                    
                    products.append({
                        'barcode': barcode,
                        'name': name
                    })
                else:
                    skipped += 1
            else:
                skipped += 1
        
        print(f"✅ ข้อมูลที่ใช้ได้: {len(products)} รายการ")
        print(f"⚠️ ข้าม: {skipped} รายการ")
        
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
    batch_size = 20  # ลดขนาด batch เพื่อป้องกัน error
    total_inserted = 0
    errors = 0
    
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
                print(f"❌ Error ใน batch {batch_num}: {str(batch_error)[:100]}...")
                errors += len(batch)
                # ลองทีละรายการ
                for product_data in products_to_insert:
                    try:
                        single_result = client.table('products').insert([product_data]).execute()
                        if single_result.data:
                            total_inserted += 1
                            errors -= 1
                    except Exception as single_error:
                        # ข้าม error เงียบ ๆ เพื่อไม่ให้ log เยอะเกินไป
                        pass
            
            # แสดงความคืบหน้า
            if batch_num % 10 == 0 or batch_num == (len(products_data) + batch_size - 1) // batch_size:
                progress = (batch_num * batch_size) / len(products_data) * 100
                print(f"📊 ความคืบหน้า: {progress:.1f}% ({total_inserted} รายการ)")
        
        print(f"🎉 นำเข้าเสร็จสิ้น! สำเร็จ {total_inserted} รายการ, Error {errors} รายการ")
        return total_inserted > 0
        
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
    print("🔄 นำเข้าข้อมูลจาก Google Sheets (เวอร์ชันสุดท้าย)")
    print("📋 โครงสร้างข้อมูล:")
    print("   Column A = บาร์โค้ด (Barcode) ← ใช้สำหรับค้นหา")
    print("   Column B = ชื่อสินค้า (Product Name)")
    print("")
    
    # Step 1: Get data from Google Sheets  
    products_data = get_products_from_sheets()
    if not products_data:
        return False
    
    # Step 2: Import to Supabase
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