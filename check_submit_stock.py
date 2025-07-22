#!/usr/bin/env python3
"""
ตรวจสอบปัญหาการบันทึกข้อมูล Stock Counting
"""

import requests
import json

def test_submit_stock_api():
    """ทดสอบ API การบันทึกข้อมูล"""
    print("🧪 ทดสอบ API การบันทึกข้อมูล Stock Counting...")
    
    # ข้อมูลทดสอบ
    test_data = {
        "barcode": "#808",
        "product_name": "กระเป๋าสะพายข้าง โลโก้หน้ากวาง #808 คละสี",
        "quantity": 10,
        "branch": "สาขาหลัก", 
        "counter_name": "Test User"
    }
    
    print(f"📤 ส่งข้อมูล: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        # ทดสอบ API endpoint (จะได้ redirect เพราะไม่ได้ login)
        response = requests.post(
            "https://www.ptee88.com/submit_stock",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            allow_redirects=False,
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("✅ API endpoint ตอบสนอง (redirect to login)")
        elif response.status_code == 200:
            try:
                result = response.json()
                print(f"📊 Response Data: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except:
                print(f"📄 Response Text: {response.text[:200]}...")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

def check_form_validation():
    """แนะนำการตรวจสอบ Form Validation"""
    print("\n🔍 สาเหตุที่เป็นไปได้:")
    print("1. ❌ ไม่ได้กรอกข้อมูลครบถ้วน:")
    print("   - ชื่อผู้ตรวจนับสินค้า")
    print("   - บาร์โค้ด")  
    print("   - จำนวนคงเหลือ")
    print("   - สาขา")
    print("")
    print("2. ❌ ปัญหาฐานข้อมูล:")
    print("   - ตาราง stock_counts ไม่พร้อม")
    print("   - API Key หมดอายุ")
    print("   - ไม่พบสินค้าในฐานข้อมูล")
    print("")
    print("3. ❌ ปัญหาการอัพโหลดรูป:")
    print("   - credentials.json ไม่อัพโหลด")
    print("   - Google Drive API ล้มเหลว")

def show_solution():
    """แสดงวิธีแก้ไข"""
    print("\n💡 วิธีแก้ไข:")
    print("1. 🔧 ตรวจสอบใน Browser Developer Tools:")
    print("   - กด F12")
    print("   - ไปแท็บ Console")
    print("   - ดู Error messages")
    print("   - ไปแท็บ Network เพื่อดู API calls")
    print("")
    print("2. 🔑 อัพเดท Supabase API Key:")
    print("   - เข้า Supabase Dashboard")
    print("   - Project Settings > API")
    print("   - Copy anon public key ใหม่") 
    print("   - อัพเดทใน Render Environment Variables")
    print("")
    print("3. 📁 Upload credentials.json:")
    print("   - Render Dashboard > Environment")
    print("   - Add Environment File: credentials.json")
    print("   - Manual Deploy")
    print("")
    print("4. 🧪 ทดสอบทีละขั้นตอน:")
    print("   - สแกนบาร์โค้ด → ตรวจว่าแสดงชื่อสินค้า")
    print("   - กรอกข้อมูลครบ → ตรวจ required fields")  
    print("   - กดบันทึก → ดู Error ใน Console")

if __name__ == "__main__":
    print("🔧 การวินิจฉัยปัญหาการบันทึกข้อมูล")
    print("=" * 50)
    
    test_submit_stock_api()
    check_form_validation()  
    show_solution()
    
    print("\n" + "=" * 50)
    print("🚨 ขั้นตอนเร่งด่วน:")
    print("1. เข้า Supabase Dashboard")
    print("2. ไป Project Settings > API")  
    print("3. Copy anon public key ใหม่")
    print("4. อัพเดทใน Render Environment: SUPABASE_ANON_KEY")
    print("5. Deploy ใหม่ และทดสอบอีกครั้ง")