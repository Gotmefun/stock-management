#!/usr/bin/env python3
"""
Import สินค้าจริงจาก Google Sheets โดยไม่มี input()
"""

import os
from supabase import create_client
from sheets_manager import create_sheets_manager

# Configuration
SUPABASE_URL = "https://khiooiigrfrluvyobljq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q"
PRODUCT_SHEET_ID = "17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM"

def main():
    print("🚀 นำเข้าสินค้าจาก Google Sheets...")
    
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
    
    # Transform data
    products_to_insert = []
    for i, product in enumerate(products_data):
        barcode = product.get('barcode', '').strip()
        name = product.get('name', '').strip()
        
        if not barcode or not name:
            print(f"⚠️ Skip รายการที่ {i+1}: ไม่มี barcode หรือ name")
            continue
        
        product_record = {
            'sku': barcode,
            'barcode': barcode,
            'name': name,
            'description': f"สินค้าจริงจาก Google Sheets - {name}",
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
        print(f"📝 เตรียม: {barcode} - {name}")
    
    if not products_to_insert:
        print("❌ ไม่มีสินค้าที่ถูกต้องให้นำเข้า")
        return False
    
    # Insert into Supabase
    try:
        print(f"💾 บันทึกสินค้า {len(products_to_insert)} รายการลง Supabase...")
        result = supabase.table('products').insert(products_to_insert).execute()
        
        if result.data:
            print(f"✅ นำเข้าสินค้าสำเร็จ {len(result.data)} รายการ!")
            print("\n📋 สินค้าที่นำเข้า:")
            for product in result.data[:10]:
                print(f"   🏷️ {product['barcode']} - {product['name']}")
            
            if len(result.data) > 10:
                print(f"   ... และอีก {len(result.data) - 10} รายการ")
            
            print(f"\n🎯 ทดสอบบาร์โค้ดเหล่านี้:")
            for product in result.data[:5]:
                print(f"   📱 {product['barcode']}")
            
            return True
        else:
            print("❌ การนำเข้าล้มเหลว - ไม่มีข้อมูลกลับมา")
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
        print("3. ใช้บาร์โค้ดจริงจาก Google Sheets ได้เลย!")
    else:
        print("\n❌ การนำเข้าล้มเหลว กรุณาตรวจสอบ:")
        print("- รัน SQL ใน Supabase แล้วหรือยัง?")
        print("- Google Sheets มีข้อมูลหรือไม่?")
        print("- Supabase เชื่อมต่อได้หรือไม่?")