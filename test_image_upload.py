#!/usr/bin/env python3
"""
ทดสอบการอัพโหลดรูปภาพและหาสาเหตุที่ไม่มีภาพใน Google Drive
"""

import os
import requests
import base64

def test_google_apps_script():
    """ทดสอบ Google Apps Script"""
    print("🧪 ทดสอบ Google Apps Script...")
    
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec"
    
    # สร้างรูปภาพทดสอบ (1x1 pixel red PNG)
    test_image_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    payload = {
        'imageData': test_image_b64,
        'filename': 'test_upload.png'
    }
    
    try:
        print(f"📤 ส่งข้อมูลไปยัง: {APPS_SCRIPT_URL}")
        response = requests.post(
            APPS_SCRIPT_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Text: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"📊 JSON Response: {result}")
                if result.get('url'):
                    print("✅ Apps Script ทำงานได้")
                    return result['url']
                else:
                    print("❌ Apps Script ไม่ส่ง URL กลับมา")
            except Exception as json_error:
                print(f"❌ JSON Parse Error: {json_error}")
                print("Response อาจไม่ใช่ JSON format")
        else:
            print("❌ Apps Script ไม่ตอบสนองปกติ")
            
    except requests.exceptions.Timeout:
        print("❌ Apps Script Timeout (มากกว่า 30 วินาที)")
    except Exception as e:
        print(f"❌ Apps Script Error: {e}")
    
    return None

def check_oauth_manager():
    """ตรวจสอบ OAuth Manager"""
    print("\n🔐 ตรวจสอบ OAuth Manager...")
    
    try:
        from oauth_manager import oauth_drive_manager
        
        if oauth_drive_manager.is_authorized():
            print("✅ OAuth2 authorized แล้ว")
            
            # ทดสอบสร้างโฟลเดอร์
            try:
                folder_id = oauth_drive_manager.get_or_create_folder_path('Check Stock Project/Pic Stock Counting')
                print(f"✅ สร้างโฟลเดอร์ได้: {folder_id}")
                
                # ทดสอบอัพโหลดรูป
                test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
                
                result = oauth_drive_manager.upload_image_from_base64(
                    test_image_b64,
                    'test_oauth_upload.png', 
                    folder_id
                )
                
                if result:
                    print(f"✅ OAuth2 อัพโหลดสำเร็จ: {result.get('web_view_link')}")
                    return True
                else:
                    print("❌ OAuth2 อัพโหลดล้มเหลว")
                    
            except Exception as oauth_error:
                print(f"❌ OAuth2 operation error: {oauth_error}")
        else:
            print("❌ OAuth2 ไม่ได้ authorized")
            print("   ต้องไป authorize ก่อนใน /auth/google")
            
    except ImportError as e:
        print(f"❌ ไม่สามารถ import oauth_manager: {e}")
    except Exception as e:
        print(f"❌ OAuth Manager Error: {e}")
    
    return False

def check_credentials_file():
    """ตรวจสอบไฟล์ credentials.json"""
    print("\n📁 ตรวจสอบไฟล์ credentials.json...")
    
    if os.path.exists('credentials.json'):
        print("✅ ไฟล์ credentials.json มีอยู่")
        try:
            import json
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
            
            if 'type' in creds and creds['type'] == 'service_account':
                print("✅ ไฟล์ credentials.json เป็น service account")
                print(f"   Project ID: {creds.get('project_id', 'N/A')}")
                print(f"   Client Email: {creds.get('client_email', 'N/A')}")
                return True
            else:
                print("❌ ไฟล์ credentials.json ไม่ใช่ service account")
        except Exception as e:
            print(f"❌ ไฟล์ credentials.json มีปัญหา: {e}")
    else:
        print("❌ ไฟล์ credentials.json ไม่มี")
        print("   ต้องอัพโหลดใน Render Environment")
    
    return False

def show_debugging_solution():
    """แสดงวิธีแก้ไขปัญหา"""
    print("\n💡 สาเหตุที่ภาพไม่อัพโหลด:")
    print("1. ❌ Google Apps Script ไม่ทำงาน")
    print("2. ❌ OAuth2 ไม่ได้ authorized") 
    print("3. ❌ credentials.json ไม่ได้อัพโหลด")
    print("4. ❌ ไม่มีสิทธิ์เข้าถึง Google Drive")
    
    print("\n🔧 วิธีแก้ไข:")
    print("1. 📁 Upload credentials.json:")
    print("   - Render Dashboard > Environment")
    print("   - Add Environment File: credentials.json")
    print("   - Copy เนื้อหาจากไฟล์ในเครื่อง")
    print("   - Deploy อีกครั้ง")
    
    print("\n2. 🔐 Authorize Google OAuth2:")
    print("   - ไปที่ www.ptee88.com/auth/google")
    print("   - Login ด้วย Google Account")
    print("   - อนุญาตสิทธิ์ Google Drive")
    
    print("\n3. 🧪 ทดสอบอัพโหลด:")
    print("   - ไปหน้า Stock Counting")
    print("   - ถ่ายรูปและบันทึก")
    print("   - ดู Console (F12) เพื่อดู Error")
    
    print("\n4. ✅ ตรวจสอบผลลัพธ์:")
    print("   - เช็ค Google Drive > Check Stock Project > Pic Stock Counting")
    print("   - เช็ค Render Logs ในกรณีมี Error")

if __name__ == "__main__":
    print("🔍 วิเคราะห์ปัญหาการอัพโหลดรูปภาพ")
    print("=" * 60)
    
    # ทดสอบทุกวิธีการอัพโหลด
    apps_script_ok = test_google_apps_script()
    oauth_ok = check_oauth_manager()
    creds_ok = check_credentials_file()
    
    print("\n" + "=" * 60)
    print("📊 สรุปผลการทดสอบ:")
    print(f"   📱 Google Apps Script: {'✅ ใช้ได้' if apps_script_ok else '❌ ไม่ใช้ได้'}")
    print(f"   🔐 OAuth2 Manager: {'✅ ใช้ได้' if oauth_ok else '❌ ไม่ใช้ได้'}")  
    print(f"   📁 Credentials File: {'✅ มี' if creds_ok else '❌ ไม่มี'}")
    
    if not any([apps_script_ok, oauth_ok, creds_ok]):
        print("\n🚨 ไม่มีวิธีอัพโหลดใดที่ใช้งานได้!")
        
    show_debugging_solution()