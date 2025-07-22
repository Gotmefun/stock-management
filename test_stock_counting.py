#!/usr/bin/env python3
"""
ทดสอบระบบนับสต๊อกสินค้า - ทดสอบการค้นหาสินค้าด้วยบาร์โค้ด
"""

from supabase_manager import create_supabase_manager
import requests

def test_supabase_search():
    """ทดสอบการค้นหาจาก Supabase โดยตรง"""
    print("🔍 ทดสอบการค้นหาสินค้าใน Supabase...")
    
    supabase_manager = create_supabase_manager()
    if not supabase_manager:
        print("❌ ไม่สามารถเชื่อมต่อ Supabase ได้")
        return False
    
    # ทดสอบด้วยบาร์โค้ดที่มีจริงในฐานข้อมูล
    test_barcodes = ['#808', '0', '00', '000', '000001']
    
    for barcode in test_barcodes:
        try:
            print(f"\n🔍 ค้นหาบาร์โค้ด: '{barcode}'")
            product = supabase_manager.get_product_by_barcode(barcode)
            
            if product:
                print(f"✅ พบสินค้า:")
                print(f"   ID: {product.get('id')}")
                print(f"   ชื่อ: {product.get('name', '')[:60]}...")
                print(f"   บาร์โค้ด: {product.get('barcode')}")
                print(f"   SKU: {product.get('sku')}")
            else:
                print(f"❌ ไม่พบสินค้าสำหรับบาร์โค้ด '{barcode}'")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True

def test_webapp_api():
    """ทดสอบ API endpoint ของเว็บแอป"""
    print("\n🌐 ทดสอบ API Endpoint...")
    
    base_url = "https://ptee88.com"  # หรือ http://localhost:5000 ถ้าทดสอบ local
    
    # ทดสอบด้วยบาร์โค้ดที่มีจริง
    test_barcodes = ['#808', '0', '00']
    
    for barcode in test_barcodes:
        try:
            print(f"\n📡 ทดสอบ API สำหรับบาร์โค้ด: '{barcode}'")
            
            # ต้องจำลองการ login ก่อน หรือใช้ API โดยตรง
            url = f"{base_url}/get_product/{barcode}"
            
            # ถ้าไม่ได้ login จะได้ redirect, แต่เราสามารถเช็คได้ว่า endpoint ตอบสนอง
            response = requests.get(url, allow_redirects=False)
            
            if response.status_code == 302:
                print("✅ API endpoint ตอบสนอง (redirect to login - ปกติ)")
            elif response.status_code == 200:
                print("✅ API endpoint ตอบสนอง")
                try:
                    data = response.json()
                    print(f"   ข้อมูลสินค้า: {data}")
                except:
                    print("   (ได้ HTML response - อาจต้อง login)")
            else:
                print(f"⚠️ API response: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")

def show_available_products():
    """แสดงสินค้าที่มีในฐานข้อมูลสำหรับทดสอบ"""
    print("\n📋 รายการสินค้าสำหรับทดสอบ:")
    
    supabase_manager = create_supabase_manager()
    if not supabase_manager:
        return
    
    try:
        from supabase import create_client
        client = create_client(
            "https://khiooiigrfrluvyobljq.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q"
        )
        
        products = client.table('products').select('barcode, name').limit(10).execute()
        
        print("🧪 บาร์โค้ดสำหรับทดสอบการสแกน:")
        for i, product in enumerate(products.data, 1):
            print(f"   {i}. '{product['barcode']}' → {product['name'][:50]}...")
            
        print(f"\n📊 รวมสินค้าในฐานข้อมูล: {len(products.data)} รายการ (แสดง 10 รายการแรก)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🧪 ทดสอบระบบ Stock Counting")
    print("=" * 60)
    
    # 1. ทดสอบการค้นหาใน Supabase
    test_supabase_search()
    
    # 2. แสดงสินค้าที่มีสำหรับทดสอบ
    show_available_products()
    
    # 3. ทดสอบ Web API (optional)
    # test_webapp_api()
    
    print("\n" + "=" * 60)
    print("🎯 วิธีทดสอบบนเว็บไซต์:")
    print("1. ไปที่ www.ptee88.com")
    print("2. Login ด้วย username: admin, password: Teeomega2014")
    print("3. ไปหน้า Stock Counting")  
    print("4. ใช้บาร์โค้ดใดก็ได้จากรายการข้างต้น")
    print("5. ระบบควรแสดงชื่อสินค้าที่ถูกต้อง")

if __name__ == "__main__":
    main()