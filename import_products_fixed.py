#!/usr/bin/env python3
"""
Import สินค้าจริงจาก Google Sheets เข้า Supabase (แก้ไขแล้ว)
"""

import os
from supabase import create_client
from sheets_manager import create_sheets_manager

# Configuration
SUPABASE_URL = "https://khiooiigrfrluvyobljq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q"
PRODUCT_SHEET_ID = "17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM"

def main():
    print("🚀 นำเข้าสินค้าจาก Google Sheets (แก้ไขแล้ว)...")
    
    # Connect to Supabase
    print("🔗 เชื่อมต่อ Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # Connect to Google Sheets
    print("📊 เชื่อมต่อ Google Sheets...")
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
    
    # Transform data (แก้ไข key ให้ถูกต้อง)
    products_to_insert = []
    success_count = 0
    skip_count = 0
    
    for i, product in enumerate(products_data):
        barcode = product.get('barcode', '').strip()
        # เปลี่ยนจาก 'name' เป็น 'product_name' 
        name = product.get('product_name', '').strip()
        
        if not barcode or not name:
            skip_count += 1
            if i < 10:  # แสดงเฉพาะ 10 รายการแรกที่ skip
                print(f"⚠️ Skip รายการที่ {i+1}: barcode='{barcode}', name='{name}'")
            continue
        
        # Skip header row
        if barcode.lower() == 'barcode' and name.lower() == 'product name':
            skip_count += 1
            continue
        
        product_record = {
            'sku': barcode,
            'barcode': barcode,
            'name': name,
            'description': f"สินค้าจาก Google Sheets - {name[:50]}...",
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
        success_count += 1
        
        if success_count <= 10:
            print(f"📝 เตรียม: {barcode} - {name[:50]}...")
    
    print(f"✅ เตรียมข้อมูล: {success_count} รายการ, Skip: {skip_count} รายการ")
    
    if not products_to_insert:
        print("❌ ไม่มีสินค้าที่ถูกต้องให้นำเข้า")
        return False
    
    # Insert into Supabase (ทีละ batch เพื่อป้องกัน error)
    try:
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(products_to_insert), batch_size):
            batch = products_to_insert[i:i + batch_size]
            print(f"💾 บันทึก batch {i//batch_size + 1}: {len(batch)} รายการ...")
            
            try:
                result = supabase.table('products').insert(batch).execute()
                
                if result.data:
                    total_inserted += len(result.data)
                    print(f"✅ บันทึกสำเร็จ {len(result.data)} รายการ")
                else:
                    print("❌ ไม่มีข้อมูลกลับมา")
                    
            except Exception as batch_error:
                print(f"❌ Error ใน batch นี้: {batch_error}")
                # ลองทีละรายการ
                for product in batch:
                    try:
                        single_result = supabase.table('products').insert([product]).execute()
                        if single_result.data:
                            total_inserted += 1
                    except Exception as single_error:
                        print(f"⚠️ Skip: {product['barcode']} - {single_error}")
        
        if total_inserted > 0:
            print(f"\n🎉 นำเข้าสำเร็จทั้งหมด {total_inserted} รายการ!")
            
            # แสดงตัวอย่างบาร์โค้ดสำหรับทดสอบ
            print(f"\n🎯 บาร์โค้ดสำหรับทดสอบ:")
            test_products = supabase.table('products').select('barcode, name').limit(10).execute()
            for product in test_products.data:
                print(f"   📱 {product['barcode']} → {product['name'][:30]}...")
            
            return True
        else:
            print("❌ การนำเข้าล้มเหลว - ไม่มีข้อมูลที่บันทึกได้")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการนำเข้า: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 เสร็จสิ้น! ตอนนี้:")
        print("1. Deploy ใหม่ใน Render (Clear cache)")
        print("2. ทดสอบที่ www.ptee88.com")
        print("3. ใช้บาร์โค้ดจริงจากสินค้าได้เลย!")
    else:
        print("\n❌ การนำเข้าล้มเหลว กรุณาตรวจสอบ:")
        print("- รัน SQL ใน Supabase แล้วหรือยัง?")
        print("- Google Sheets มีข้อมูลหรือไม่?")
        print("- Supabase เชื่อมต่อได้หรือไม่?")