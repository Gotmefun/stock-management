#!/usr/bin/env python3
"""
Test the deployed Google Apps Script Web App
ทดสอบ Apps Script ที่ deploy แล้วจาก web app URL
"""

import requests
import json
import base64

def test_apps_script_deployment():
    """ทดสอบ Google Apps Script ที่ deploy แล้ว"""
    
    # ใส่ Web App URL ที่ได้จาก deployment
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec"
    
    print("🧪 ทดสอบ Google Apps Script Web App")
    print("=" * 50)
    print(f"URL: {APPS_SCRIPT_URL}")
    
    # สร้างรูปทดสอบ (1x1 pixel PNG)
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    # ทดสอบทั้ง 3 สาขา
    test_cases = [
        {
            "branch_code": "CITY",
            "folder": "Check Stock Project/สาขาตัวเมือง",
            "filename": "test_city.png"
        },
        {
            "branch_code": "SCHOOL", 
            "folder": "Check Stock Project/สาขาหน้าโรงเรียน",
            "filename": "test_school.png"
        },
        {
            "branch_code": "PONGPAI",
            "folder": "Check Stock Project/สาขาโป่งไผ่", 
            "filename": "test_pongpai.png"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📁 ทดสอบ {test_case['branch_code']}")
        print(f"Folder: {test_case['folder']}")
        print(f"Filename: {test_case['filename']}")
        
        payload = {
            'imageData': f"data:image/png;base64,{test_image_data}",
            'filename': test_case['filename'],
            'folder': test_case['folder']
        }
        
        try:
            print("📤 ส่งข้อมูลไปยัง Apps Script...")
            
            response = requests.post(
                APPS_SCRIPT_URL,
                json=payload,
                timeout=30,
                headers={
                    'Content-Type': 'application/json'
                }
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"📄 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    
                    if result.get('success'):
                        print(f"✅ สำเร็จ! URL: {result.get('webViewLink')}")
                        results.append({
                            'branch': test_case['branch_code'],
                            'success': True,
                            'url': result.get('webViewLink'),
                            'fileId': result.get('fileId')
                        })
                    else:
                        print(f"❌ ล้มเหลว: {result.get('error')}")
                        results.append({
                            'branch': test_case['branch_code'],
                            'success': False,
                            'error': result.get('error')
                        })
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Error: {e}")
                    print(f"Response text: {response.text}")
                    results.append({
                        'branch': test_case['branch_code'],
                        'success': False,
                        'error': f'JSON decode error: {e}'
                    })
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                results.append({
                    'branch': test_case['branch_code'],
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}'
                })
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                'branch': test_case['branch_code'],
                'success': False,
                'error': str(e)
            })
        
        print("-" * 30)
    
    # สรุปผล
    print("\n📊 สรุปผลการทดสอบ:")
    print("=" * 50)
    
    success_count = 0
    for result in results:
        status = "✅ สำเร็จ" if result['success'] else "❌ ล้มเหลว"
        print(f"{result['branch']}: {status}")
        
        if result['success']:
            success_count += 1
            print(f"  URL: {result.get('url')}")
            print(f"  File ID: {result.get('fileId')}")
        else:
            print(f"  Error: {result.get('error')}")
    
    print(f"\nผลรวม: {success_count}/{len(test_cases)} สาขา ทำงานสำเร็จ")
    
    if success_count == len(test_cases):
        print("\n🎉 Google Apps Script ทำงานสมบูรณ์!")
        print("✅ ระบบพร้อมใช้งาน")
    else:
        print("\n⚠️ พบปัญหาบางส่วน")
        print("🔧 ตรวจสอบ Google Apps Script และ permissions")
    
    return results

def test_invalid_data():
    """ทดสอบกรณีส่งข้อมูลผิด"""
    
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec"
    
    print("\n🧪 ทดสอบกรณีข้อมูลผิด:")
    print("=" * 30)
    
    # Test cases for error handling
    error_test_cases = [
        {
            "name": "Missing imageData",
            "payload": {
                "filename": "test.png",
                "folder": "Check Stock Project/สาขาตัวเมือง"
            }
        },
        {
            "name": "Missing filename", 
            "payload": {
                "imageData": "data:image/png;base64,test",
                "folder": "Check Stock Project/สาขาตัวเมือง"
            }
        },
        {
            "name": "Missing folder",
            "payload": {
                "imageData": "data:image/png;base64,test",
                "filename": "test.png"
            }
        },
        {
            "name": "Invalid JSON",
            "payload": "invalid json"
        }
    ]
    
    for test_case in error_test_cases:
        print(f"\n📋 {test_case['name']}")
        
        try:
            if isinstance(test_case['payload'], str):
                # Test invalid JSON
                response = requests.post(
                    APPS_SCRIPT_URL,
                    data=test_case['payload'],
                    timeout=10
                )
            else:
                response = requests.post(
                    APPS_SCRIPT_URL,
                    json=test_case['payload'],
                    timeout=10
                )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get('success'):
                    print(f"✅ Error handled correctly: {result.get('error')}")
                else:
                    print(f"⚠️ Should have failed but succeeded")
            else:
                print(f"📊 HTTP {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    # ทดสอบการทำงานปกติ
    results = test_apps_script_deployment()
    
    # ทดสอบ error handling
    test_invalid_data()
    
    print("\n" + "="*50)
    print("🏁 การทดสอบเสร็จสิ้น")