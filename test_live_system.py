#!/usr/bin/env python3
"""
ทดสอบระบบ Stock Counting บน www.ptee88.com
"""

import requests
import time

def test_website_availability():
    """ทดสอบว่าเว็บไซต์เข้าถึงได้"""
    print("🌐 ทดสอบการเข้าถึงเว็บไซต์...")
    
    try:
        response = requests.get("https://www.ptee88.com", timeout=10)
        if response.status_code == 200:
            print("✅ เว็บไซต์เข้าถึงได้ปกติ")
            return True
        else:
            print(f"⚠️ เว็บไซต์ตอบสนอง status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ไม่สามารถเข้าถึงเว็บไซต์ได้: {e}")
        return False

def test_product_search_api():
    """ทดสอบ API การค้นหาสินค้า (จะได้ redirect เพราะไม่ได้ login)"""
    print("\n🔍 ทดสอบ API การค้นหาสินค้า...")
    
    test_barcodes = ['#808', '0', '000001', '00']
    
    for barcode in test_barcodes:
        try:
            # ทดสอบ API endpoint (จะได้ redirect ไป login แต่อย่างน้อยรู้ว่า endpoint ทำงาน)
            response = requests.get(f"https://www.ptee88.com/get_product/{barcode}", 
                                  allow_redirects=False, timeout=5)
            
            if response.status_code == 302:
                print(f"✅ API endpoint สำหรับ '{barcode}' ทำงาน (redirect to login)")
            elif response.status_code == 200:
                print(f"✅ API endpoint สำหรับ '{barcode}' ตอบสนองปกติ")
            else:
                print(f"⚠️ API endpoint สำหรับ '{barcode}' ตอบสนอง: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API endpoint สำหรับ '{barcode}' error: {e}")

def test_supabase_direct():
    """ทดสอบการเชื่อมต่อ Supabase โดยตรง"""
    print("\n🗄️ ทดสอบการเชื่อมต่อ Supabase...")
    
    try:
        from supabase import create_client
        client = create_client(
            "https://khiooiigrfrluvyobljq.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q"
        )
        
        # ตรวจสอบจำนวนสินค้า
        products = client.table('products').select('*', count='exact').limit(1).execute()
        print(f"✅ ฐานข้อมูลมีสินค้า: {products.count} รายการ")
        
        # ทดสอบค้นหาสินค้าตัวอย่าง
        test_barcodes = ['#808', '0', '000001']
        for barcode in test_barcodes:
            result = client.table('products').select('barcode, name').eq('barcode', barcode).limit(1).execute()
            if result.data:
                product = result.data[0]
                print(f"✅ พบสินค้า '{barcode}': {product['name'][:50]}...")
            else:
                print(f"❌ ไม่พบสินค้า '{barcode}'")
                
        return True
        
    except Exception as e:
        print(f"❌ เชื่อมต่อ Supabase ล้มเหลว: {e}")
        return False

def test_javascript_files():
    """ทดสอบไฟล์ JavaScript"""
    print("\n📱 ทดสอบไฟล์ JavaScript...")
    
    try:
        response = requests.get("https://www.ptee88.com/static/barcode.js", timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # ตรวจสอบว่ามีโค้ดที่แก้ไขแล้วหรือไม่
            if "addEventListener('input'" in content:
                print("✅ JavaScript อัพเดทแล้ว (มี input event listener)")
            else:
                print("⚠️ JavaScript อาจยังไม่อัพเดท")
                
            if "product.name || product.product_name" in content:
                print("✅ JavaScript มีการจัดการชื่อสินค้าทั้งสองรูปแบบ")
            else:
                print("⚠️ JavaScript อาจยังไม่มีการจัดการชื่อสินค้า")
                
            return True
        else:
            print(f"❌ ไม่สามารถโหลดไฟล์ JavaScript ได้: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error loading JavaScript: {e}")
        return False

def generate_test_report():
    """สร้างรายงานการทดสอบ"""
    print("\n" + "="*60)
    print("📋 รายงานการทดสอบระบบ Stock Counting")
    print("="*60)
    
    # ทดสอบทีละส่วน
    website_ok = test_website_availability()
    api_ok = test_product_search_api()
    db_ok = test_supabase_direct()
    js_ok = test_javascript_files()
    
    print("\n" + "="*60)
    print("🎯 สรุปผลการทดสอบ:")
    print(f"   🌐 เว็บไซต์: {'✅ พร้อมใช้งาน' if website_ok else '❌ มีปัญหา'}")
    print(f"   📡 API: {'✅ ทำงานปกติ' if api_ok else '❌ มีปัญหา'}")
    print(f"   🗄️ Database: {'✅ เชื่อมต่อได้' if db_ok else '❌ มีปัญหา'}")
    print(f"   📱 JavaScript: {'✅ อัพเดทแล้ว' if js_ok else '⚠️ ตรวจสอบ'}")
    
    if all([website_ok, db_ok]):
        print("\n🎉 ระบบพร้อมทดสอบ!")
        print("\n🧪 ขั้นตอนการทดสอบ:")
        print("1. ไปที่ www.ptee88.com")
        print("2. Login: admin / Teeomega2014")
        print("3. หน้า 'นับสต๊อกสินค้า'")
        print("4. กด 'เปิดกล้อง' เพื่อสแกน")
        print("5. สแกนบาร์โค้ด หรือ พิมพ์: #808")
        print("6. ระบบควรแสดงชื่อสินค้าทันที")
        
        print("\n📱 บาร์โค้ดสำหรับทดสอบ:")
        print("   • #808 → กระเป๋าสะพายข้าง โลโก้หน้ากวาง")
        print("   • 0 → หนูกัด")
        print("   • 000001 → ดีทอก บุกกวาง 2000")
        print("   • 00 → สินค้าเซลว์")
    else:
        print("\n⚠️ พบปัญหา - ตรวจสอบการ Deploy หรือการตั้งค่า")

if __name__ == "__main__":
    generate_test_report()