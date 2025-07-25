#!/usr/bin/env python3
"""
Final production test for www.ptee88.com
ทดสอบระบบอัปโหลดรูปภาพใน production
"""

import requests
import json
import base64
import time

def test_production_login_and_upload():
    """ทดสอบ login และอัปโหลดรูปใน production"""
    
    BASE_URL = "https://www.ptee88.com"
    
    print("🌐 ทดสอบระบบ Production")
    print("=" * 50)
    print(f"URL: {BASE_URL}")
    
    # Create session
    session = requests.Session()
    
    # 1. Test login
    print("\n🔐 ทดสอบ Login...")
    login_data = {
        'username': 'admin',
        'password': 'Teeomega2014'
    }
    
    try:
        login_response = session.post(f'{BASE_URL}/login', data=login_data, timeout=30)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return False
            
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # 2. Test image upload
    print("\n📷 ทดสอบ Image Upload...")
    
    # Create test image (red pixel)
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    test_cases = [
        {
            "branch": "CITY",
            "branch_name": "สาขาตัวเมือง"
        },
        {
            "branch": "SCHOOL", 
            "branch_name": "สาขาหน้าโรงเรียน"
        },
        {
            "branch": "PONGPAI",
            "branch_name": "สาขาโป่งไผ่"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📁 ทดสอบ {i}/{len(test_cases)}: {test_case['branch_name']} ({test_case['branch']})")
        
        stock_data = {
            'barcode': f'TEST{i}23456789',
            'quantity': 10 + i,
            'branch': test_case['branch'],
            'product_name': f'Test Product {test_case["branch"]}',
            'counter_name': 'Production Test',
            'image_data': f'data:image/png;base64,{test_image_data}'
        }
        
        try:
            print("📤 ส่งข้อมูลไปยัง /submit_stock...")
            
            response = session.post(
                f'{BASE_URL}/submit_stock',
                json=stock_data,
                headers={'Content-Type': 'application/json'},
                timeout=60  # เพิ่ม timeout สำหรับ production
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"📄 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    
                    if result.get('success'):
                        print(f"✅ สำเร็จ! ข้อมูลถูกบันทึก")
                        results.append({
                            'branch': test_case['branch'],
                            'success': True,
                            'saved_to': result.get('saved_to', {})
                        })
                    else:
                        print(f"❌ บันทึกล้มเหลว: {result.get('error')}")
                        results.append({
                            'branch': test_case['branch'],
                            'success': False,
                            'error': result.get('error')
                        })
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Error: {e}")
                    print(f"Response text: {response.text}")
                    results.append({
                        'branch': test_case['branch'],
                        'success': False,
                        'error': f'JSON decode error: {e}'
                    })
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                results.append({
                    'branch': test_case['branch'],
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                })
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                'branch': test_case['branch'],
                'success': False,
                'error': str(e)
            })
        
        # Delay between requests
        if i < len(test_cases):
            print("⏱️ รอ 3 วินาที...")
            time.sleep(3)
        
        print("-" * 40)
    
    # Summary
    print("\n📊 สรุปผลการทดสอบ Production:")
    print("=" * 50)
    
    success_count = 0
    for result in results:
        status = "✅ สำเร็จ" if result['success'] else "❌ ล้มเหลว"
        print(f"{result['branch']}: {status}")
        
        if result['success']:
            success_count += 1
            saved_to = result.get('saved_to', {})
            if saved_to:
                print(f"  บันทึกใน: Supabase={saved_to.get('supabase', False)}, Sheets={saved_to.get('sheets', False)}")
        else:
            print(f"  Error: {result.get('error')}")
    
    print(f"\nผลรวม: {success_count}/{len(test_cases)} สาขา ทำงานสำเร็จ")
    
    if success_count == len(test_cases):
        print("\n🎉 Production System ทำงานสมบูรณ์!")
        print("✅ ระบบพร้อมใช้งานจริง")
        print("📱 URL: https://www.ptee88.com")
    else:
        print("\n⚠️ พบปัญหาใน Production")
        print("🔧 ตรวจสอบ Render.com logs และ environment variables")
    
    return success_count == len(test_cases)

def test_direct_apps_script():
    """ทดสอบ Google Apps Script โดยตรง"""
    
    print("\n🔧 ทดสอบ Google Apps Script โดยตรง:")
    print("=" * 40)
    
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec"
    
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    payload = {
        'imageData': f"data:image/png;base64,{test_image_data}",
        'filename': 'production_test.png',
        'folder': 'Check Stock Project/สาขาตัวเมือง'
    }
    
    try:
        response = requests.post(
            APPS_SCRIPT_URL,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Apps Script ทำงานปกติ")
                print(f"📄 File ID: {result.get('fileId')}")
                print(f"🔗 URL: {result.get('webViewLink')}")
            else:
                print(f"❌ Apps Script Error: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 เริ่มทดสอบ Production Final")
    print("🕐 " + time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Test Apps Script first
    test_direct_apps_script()
    
    # Test full production workflow
    success = test_production_login_and_upload()
    
    print("\n" + "="*60)
    if success:
        print("🏆 ระบบทำงานสมบูรณ์! พร้อมใช้งานจริง")
        print("🌐 https://www.ptee88.com")
    else:
        print("🔧 ต้องตรวจสอบและแก้ไขปัญหา")
    
    print("🏁 การทดสอบเสร็จสิ้น")
    print("🕐 " + time.strftime("%Y-%m-%d %H:%M:%S"))