#!/usr/bin/env python3
"""
Debug Production Error 500 - Stock Counting Submit
"""

import requests
import json

def test_production_api():
    """ทดสอบ API ใน Production Environment"""
    print("🔧 Debug Production Error 500...")
    
    # สร้าง session เพื่อจำลอง browser
    session = requests.Session()
    
    try:
        # Step 1: ไปหน้าหลักก่อน
        print("1️⃣ เข้าหน้าหลัก...")
        home_response = session.get("https://www.ptee88.com", timeout=10)
        print(f"   Status: {home_response.status_code}")
        
        # Step 2: ทดสอบหน้า login
        print("2️⃣ ทดสอบหน้า login...")
        login_page = session.get("https://www.ptee88.com/login", timeout=10)
        print(f"   Status: {login_page.status_code}")
        
        # Step 3: ทดสอบ API get_product (ไม่ login จะ redirect)
        print("3️⃣ ทดสอบ API get_product...")
        product_response = session.get("https://www.ptee88.com/get_product/%23808", 
                                     allow_redirects=False, timeout=10)
        print(f"   Status: {product_response.status_code}")
        
        if product_response.status_code == 302:
            print("   ✅ API redirect ปกติ (ต้อง login)")
        
        # Step 4: ทดสอบ submit_stock API
        print("4️⃣ ทดสอบ submit_stock API...")
        test_data = {
            "barcode": "#808",
            "product_name": "Test Product",
            "quantity": 10,
            "branch": "สาขาหลัก",
            "counter_name": "Test User"
        }
        
        submit_response = session.post(
            "https://www.ptee88.com/submit_stock",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            allow_redirects=False,
            timeout=10
        )
        
        print(f"   Status: {submit_response.status_code}")
        
        if submit_response.status_code == 500:
            print("   ❌ Error 500 ยืนยัน!")
            print(f"   Response: {submit_response.text[:200]}...")
        elif submit_response.status_code == 302:
            print("   ⚠️ Redirect (ต้อง login)")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")

def check_common_500_causes():
    """ตรวจสอบสาเหตุทั่วไปของ Error 500"""
    print("\n🔍 สาเหตุที่เป็นไปได้ของ Error 500:")
    
    print("\n1. 🔑 Environment Variables:")
    print("   - SUPABASE_URL ไม่ถูกต้อง")
    print("   - SUPABASE_ANON_KEY ไม่ถูกต้อง (แก้แล้ว)")
    print("   - SECRET_KEY ไม่มี")
    
    print("\n2. 📦 Missing Dependencies:")
    print("   - supabase client ไม่ได้ติดตั้ง")
    print("   - python module import error")
    
    print("\n3. 🗄️ Database Issues:")
    print("   - ตาราง stock_counts ไม่มี")
    print("   - ตาราง branches ไม่มี") 
    print("   - Foreign key constraint error")
    
    print("\n4. 📁 File Issues:")
    print("   - credentials.json ไม่อัพโหลด")
    print("   - supabase_manager.py missing")
    
    print("\n5. 🔧 Code Issues:")
    print("   - Python syntax error")
    print("   - Import statement error")
    print("   - Function call error")

def show_debugging_steps():
    """แสดงขั้นตอนการ Debug"""
    print("\n🛠️ ขั้นตอนการแก้ไข Error 500:")
    
    print("\n1️⃣ ตรวจสอบ Render Logs:")
    print("   - Render Dashboard > Service ptee88")
    print("   - แท็บ 'Logs'")
    print("   - ดูว่ามี Error message อะไร")
    print("   - ดู Python traceback")
    
    print("\n2️⃣ ตรวจสอบ Environment Variables:")
    print("   - ตรวจสอบ SUPABASE_URL")
    print("   - ตรวจสอบ SUPABASE_ANON_KEY ใหม่")
    print("   - ตรวจสอบมี credentials.json หรือไม่")
    
    print("\n3️⃣ ตรวจสอบ Dependencies:")
    print("   - requirements.txt มี supabase>=2.0.0")
    print("   - Deploy log แสดง successful install")
    
    print("\n4️⃣ ตรวจสอบ Supabase Tables:")
    print("   - เข้า Supabase Dashboard")
    print("   - Table Editor > stock_counts table มีหรือไม่")
    print("   - Table Editor > branches table มีหรือไม่")
    
    print("\n5️⃣ Minimal Test:")
    print("   - แก้ไข submit_stock ให้ return ง่าย ๆ ก่อน")
    print("   - ทดสอบว่า API ตอบสนอง 200")
    print("   - ค่อย ๆ เพิ่ม functionality")

def create_simple_fix():
    """สร้างโค้ดแก้ไขชั่วคราว"""
    print("\n💡 แก้ไขชั่วคราว - Simplified submit_stock:")
    print("""
# แทนที่ submit_stock function ใน app.py ชั่วคราว:

@app.route('/submit_stock', methods=['POST'])
@staff_required
def submit_stock():
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        # Basic validation
        if not data or not data.get('barcode') or not data.get('quantity'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Simple success response (ไม่บันทึกจริง)
        return jsonify({
            'success': True, 
            'message': 'Test successful',
            'data': data
        })
        
    except Exception as e:
        print(f"Error in submit_stock: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500
""")

if __name__ == "__main__":
    print("🚨 Production Error 500 Debugging")
    print("=" * 50)
    
    test_production_api()
    check_common_500_causes()
    show_debugging_steps()
    create_simple_fix()
    
    print("\n" + "=" * 50)
    print("🎯 ขั้นตอนแรก - ดู Render Logs:")
    print("1. เข้า https://dashboard.render.com")
    print("2. เลือก Service 'ptee88'") 
    print("3. คลิกแท็บ 'Logs'")
    print("4. ลองกดบันทึกข้อมูลใหม่")
    print("5. ดู Error message ที่เพิ่มขึ้นใน Logs")
    print("6. แจ้งผม Error message ที่เจอ")