#!/usr/bin/env python3
"""
แก้ไขโครงสร้าง SKU ให้แยกจาก Barcode
ใน Google Sheets มี รหัสสินค้า อยู่ Column C, Barcode อยู่ Column D, ชื่อสินค้า Column E
"""

import os
from supabase import create_client
from sheets_manager import create_sheets_manager

# Configuration
SUPABASE_URL = "https://khiooiigrfrluvyobljq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q"
PRODUCT_SHEET_ID = "17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM"

def get_correct_product_data():
    """ดึงข้อมูลที่ถูกต้องจาก Google Sheets: รหัสสินค้า(C), บาร์โค้ด(D), ชื่อ(E)"""
    print("📊 ดึงข้อมูลที่ถูกต้องจาก Google Sheets...")
    
    sheets_manager = create_sheets_manager()
    if not sheets_manager:
        print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
        return []
    
    try:
        # อ่านข้อมูลจาก Column C, D, E
        result = sheets_manager.sheets_service.spreadsheets().values().get(
            spreadsheetId=PRODUCT_SHEET_ID,
            range='C:E'  # รหัสสินค้า(C), บาร์โค้ด(D), ชื่อ(E)
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("❌ ไม่มีข้อมูลใน Google Sheets")
            return []
        
        print(f"📋 พบข้อมูล {len(values)} แถว")
        print("🔍 ตัวอย่างข้อมูล 5 แถวแรก:")
        
        products = []
        for i, row in enumerate(values):
            if i == 0:  # Skip header
                if len(row) >= 3:
                    print(f"Header: รหัสสินค้า='{row[0]}' | บาร์โค้ด='{row[1]}' | ชื่อ='{row[2]}'")
                continue
            
            if len(row) >= 3:
                sku = row[0].strip() if row[0] else ''
                barcode = row[1].strip() if row[1] else ''
                name = row[2].strip() if row[2] else ''
                
                if i <= 5:  # Show first 5 data rows
                    print(f"Row {i}: รหัส='{sku}' | บาร์โค้ด='{barcode}' | ชื่อ='{name[:30]}...'")
                
                if sku and barcode and name:
                    products.append({
                        'sku': sku,
                        'barcode': barcode, 
                        'name': name
                    })
            
        print(f"✅ ข้อมูลที่ใช้ได้: {len(products)} รายการ")
        return products
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return []

def recreate_products_table():
    """สร้างตาราง products ใหม่พร้อมข้อมูลที่ถูกต้อง"""
    print("🔄 สร้างตาราง products ใหม่...")
    
    # Get correct data
    products_data = get_correct_product_data()
    if not products_data:
        print("❌ ไม่มีข้อมูลที่ถูกต้อง")
        return False
    
    # Connect to Supabase
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    try:
        print("🗑️ ลบข้อมูลเก่า...")
        # Clear existing products (cascade will handle related tables)
        client.table('products').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("✅ ลบข้อมูลเก่าสำเร็จ")
        
        # Prepare new data with correct SKU structure
        products_to_insert = []
        for i, product in enumerate(products_data):
            product_record = {
                'sku': product['sku'],  # รหัสสินค้าจริงจาก Column C
                'barcode': product['barcode'],  # บาร์โค้ดจาก Column D
                'name': product['name'],  # ชื่อจาก Column E
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
            
            if i < 10:
                print(f"📝 เตรียม: SKU='{product['sku']}' | Barcode='{product['barcode']}' | Name='{product['name'][:30]}...'")
        
        # Insert in batches
        print(f"💾 บันทึก {len(products_to_insert)} รายการ...")
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(products_to_insert), batch_size):
            batch = products_to_insert[i:i + batch_size]
            print(f"📤 Batch {i//batch_size + 1}: {len(batch)} รายการ...")
            
            try:
                result = client.table('products').insert(batch).execute()
                if result.data:
                    total_inserted += len(result.data)
                    print(f"✅ สำเร็จ {len(result.data)} รายการ")
            except Exception as batch_error:
                print(f"❌ Error ใน batch: {batch_error}")
                # Try individual inserts
                for product in batch:
                    try:
                        single_result = client.table('products').insert([product]).execute()
                        if single_result.data:
                            total_inserted += 1
                    except:
                        pass
        
        print(f"🎉 บันทึกสำเร็จทั้งหมด {total_inserted} รายการ!")
        
        # Verify the fix
        print("🔍 ตรวจสอบข้อมูลหลังแก้ไข:")
        test_products = client.table('products').select('sku, barcode, name').limit(5).execute()
        
        for product in test_products.data:
            print(f"✅ SKU: '{product['sku']}' | Barcode: '{product['barcode']}' | Name: '{product['name'][:30]}...'")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🛠️ แก้ไขโครงสร้าง SKU vs Barcode...")
    print("📋 Google Sheets Structure:")
    print("   Column C = รหัสสินค้า (SKU)")  
    print("   Column D = บาร์โค้ด (Barcode)")
    print("   Column E = ชื่อสินค้า (Name)")
    print("")
    
    success = recreate_products_table()
    
    if success:
        print("\n🎉 แก้ไขเสร็จสิ้น!")
        print("✅ SKU = รหัสสินค้าจริง (Column C)")
        print("✅ Barcode = บาร์โค้ดแยกต่างหาก (Column D)")
        print("📱 ตอนนี้สามารถค้นหาด้วยบาร์โค้ดได้ถูกต้องแล้ว")
    else:
        print("\n❌ การแก้ไขล้มเหลว")

if __name__ == "__main__":
    main()