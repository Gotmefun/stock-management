#!/usr/bin/env python3
"""
Debug image upload issue
ตรวจสอบปัญหาการอัปโหลดรูปภาพ
"""

import requests
import json
import base64
import time

def test_apps_script_directly():
    """ทดสอบ Google Apps Script โดยตรง"""
    
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec"
    
    print("🔧 ทดสอบ Google Apps Script โดยตรง")
    print("=" * 50)
    print(f"URL: {APPS_SCRIPT_URL}")
    
    # สร้างรูปทดสอบ
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    # ทดสอบ CITY folder
    payload = {
        'imageData': f"data:image/png;base64,{test_image_data}",
        'filename': f'debug_city_{int(time.time())}.png',
        'folder': 'Check Stock Project/สาขาตัวเมือง'
    }
    
    print(f"📁 ทดสอบโฟลเดอร์: {payload['folder']}")
    print(f"📄 ไฟล์: {payload['filename']}")
    
    try:
        response = requests.post(
            APPS_SCRIPT_URL,
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"📄 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get('success'):
                    print(f"✅ Apps Script ทำงานปกติ")
                    print(f"🔗 Google Drive URL: {result.get('webViewLink')}")
                    print(f"📂 โฟลเดอร์: {result.get('folder')}")
                    return True, result.get('webViewLink')
                else:
                    print(f"❌ Apps Script Error: {result.get('error')}")
                    return False, None
            except json.JSONDecodeError as e:
                print(f"❌ JSON Error: {e}")
                print(f"Response text: {response.text}")
                return False, None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None

def test_production_upload():
    """ทดสอบการอัปโหลดผ่าน production"""
    
    BASE_URL = "https://www.ptee88.com"
    
    print("\n🌐 ทดสอบการอัปโหลดผ่าน Production")
    print("=" * 50)
    
    # Login
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'Teeomega2014'
    }
    
    try:
        login_response = session.post(f'{BASE_URL}/login', data=login_data, timeout=30)
        if login_response.status_code != 200:
            print("❌ Login failed")
            return False
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # ทดสอบอัปโหลดรูป
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    stock_data = {
        'barcode': f'DEBUG{int(time.time())}',
        'quantity': 5,
        'branch': 'CITY',  # ใช้ CITY code
        'product_name': 'Debug Test Product',
        'counter_name': 'Debug Tester',
        'image_data': f'data:image/png;base64,{test_image_data}'
    }
    
    print(f"📤 ส่งข้อมูล:")
    print(f"  Branch: {stock_data['branch']}")
    print(f"  Barcode: {stock_data['barcode']}")
    print(f"  Image data length: {len(stock_data['image_data'])}")
    
    try:
        response = session.post(
            f'{BASE_URL}/submit_stock',
            json=stock_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"📄 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get('success'):
                    print("✅ Production upload successful")
                    saved_to = result.get('saved_to', {})
                    print(f"💾 บันทึกใน:")
                    print(f"  - Supabase: {saved_to.get('supabase', False)}")
                    print(f"  - Sheets: {saved_to.get('sheets', False)}")
                    return True
                else:
                    print(f"❌ Upload failed: {result.get('error')}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON Error: {e}")
                print(f"Response text: {response.text}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_supabase_data():
    """ตรวจสอบข้อมูลใน Supabase"""
    
    print("\n💾 ตรวจสอบข้อมูลใน Supabase")
    print("=" * 30)
    
    # เรียก API เพื่อดูข้อมูลล่าสุด
    BASE_URL = "https://www.ptee88.com"
    
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': 'Teeomega2014'
    }
    
    try:
        # Login
        login_response = session.post(f'{BASE_URL}/login', data=login_data, timeout=30)
        if login_response.status_code != 200:
            print("❌ Login failed")
            return
        
        # ดูข้อมูลผ่าน dashboard หรือ API
        dashboard_response = session.get(f'{BASE_URL}/dashboard', timeout=30)
        if dashboard_response.status_code == 200:
            print("✅ สามารถเข้าถึง Dashboard ได้")
            # ตรวจสอบว่ามีข้อมูลรูปภาพหรือไม่
            if 'image_url' in dashboard_response.text.lower():
                print("📷 พบข้อมูล image_url ใน Dashboard")
            else:
                print("⚠️ ไม่พบข้อมูล image_url ใน Dashboard")
        else:
            print(f"⚠️ Dashboard access issue: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"❌ Supabase check error: {e}")

def main():
    """Main debugging function"""
    
    print("🔍 Debug Image Upload Issue")
    print("🕐 " + time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    print("🎯 ปัญหาที่พบ:")
    print("1. Supabase เก็บข้อมูลได้ แต่ไม่เก็บรูป")
    print("2. รูปไม่ไปที่ Google Drive โฟลเดอร์ CITY")
    print("")
    
    # Test 1: Apps Script
    print("=" * 60)
    apps_script_success, drive_url = test_apps_script_directly()
    
    # Test 2: Production Upload
    print("=" * 60)
    production_success = test_production_upload()
    
    # Test 3: Supabase Data
    print("=" * 60)
    check_supabase_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 สรุปการตรวจสอบ:")
    print("=" * 60)
    
    print(f"🔧 Google Apps Script: {'✅ ทำงาน' if apps_script_success else '❌ มีปัญหา'}")
    if drive_url:
        print(f"   Google Drive URL: {drive_url}")
        
    print(f"🌐 Production Upload: {'✅ ทำงาน' if production_success else '❌ มีปัญหา'}")
    
    print("\n🔍 สาเหตุที่เป็นไปได้:")
    
    if apps_script_success and not production_success:
        print("⚠️ Apps Script ทำงาน แต่ Production ไม่ทำงาน")
        print("   → ตรวจสอบ Environment Variables ใน Render.com")
        print("   → ตรวจสอบ APPS_SCRIPT_URL")
        
    elif not apps_script_success:
        print("⚠️ Google Apps Script มีปัญหา")
        print("   → ตรวจสอบ Google Apps Script code")
        print("   → ตรวจสอบ permissions")
        
    else:
        print("🎯 ระบบทำงานปกติ - อาจเป็นปัญหาชั่วคราว")
    
    print("\n🛠️ แนวทางแก้ไข:")
    print("1. ตรวจสอบ Google Apps Script logs")
    print("2. ตรวจสอบ Render.com deployment logs") 
    print("3. ตรวจสอบ APPS_SCRIPT_URL ใน Environment Variables")
    print("4. ทดสอบ manual deploy อีกครั้ง")
    
    print(f"\n🏁 Debug completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()