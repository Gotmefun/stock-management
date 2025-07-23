#!/usr/bin/env python3
"""
คู่มือการเซ็ตอัพ OAuth2 Google Drive สำหรับการอัพโหลดรูป
"""

import os
import json

def check_current_oauth_status():
    """ตรวจสอบสถานะ OAuth2 ปัจจุบัน"""
    print("🔍 ตรวจสอบสถานะ OAuth2 Google Drive ปัจจุบัน...")
    
    # ตรวจสอบไฟล์ credentials.json
    if os.path.exists('credentials.json'):
        print("✅ ไฟล์ credentials.json มีอยู่")
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
            print(f"   📧 Client ID: {creds.get('web', {}).get('client_id', 'N/A')[:20]}...")
            print(f"   🌐 Redirect URIs: {len(creds.get('web', {}).get('redirect_uris', []))} URIs")
        except Exception as e:
            print(f"   ❌ ไฟล์มีปัญหา: {e}")
    else:
        print("❌ ไม่พบไฟล์ credentials.json")
    
    # ตรวจสอบไฟล์ token
    if os.path.exists('drive_token.pickle'):
        print("✅ ไฟล์ drive_token.pickle มีอยู่")
        file_size = os.path.getsize('drive_token.pickle')
        print(f"   📦 ขนาด: {file_size} bytes")
    else:
        print("❌ ไม่พบไฟล์ drive_token.pickle")
    
    # ตรวจสอบ oauth_manager
    try:
        from oauth_manager import oauth_drive_manager
        is_authorized = oauth_drive_manager.is_authorized()
        print(f"🔐 OAuth2 Status: {'✅ Authorized' if is_authorized else '❌ Not Authorized'}")
        
        if is_authorized:
            print("   🎉 พร้อมใช้งาน OAuth2!")
            return True
        else:
            print("   ⚠️ ต้อง Authorize ก่อน")
            return False
            
    except ImportError:
        print("❌ ไม่สามารถ import oauth_manager")
        return False
    except Exception as e:
        print(f"❌ Error checking OAuth: {e}")
        return False

def show_oauth_setup_steps():
    """แสดงขั้นตอนการเซ็ตอัพ OAuth2"""
    print("\n🛠️ ขั้นตอนการเซ็ตอัพ OAuth2 Google Drive:")
    
    print("\n1. 📱 เตรียม Google Cloud Project:")
    print("   - ไป https://console.cloud.google.com/")
    print("   - เลือกโปรเจคที่มีอยู่ หรือ สร้างใหม่")
    print("   - Enable Google Drive API")
    
    print("\n2. 🔑 สร้าง OAuth2 Credentials:")
    print("   - APIs & Services → Credentials")
    print("   - Create Credentials → OAuth 2.0 Client IDs")
    print("   - Application type: Web application")
    print("   - Authorized redirect URIs:")
    print("     * https://www.ptee88.com/oauth2callback")
    print("     * http://localhost:8080/oauth2callback (สำหรับทดสอบ)")
    
    print("\n3. 📄 Download credentials.json:")
    print("   - Download JSON file")
    print("   - เปลี่ยนชื่อเป็น 'credentials.json'")
    print("   - วางไฟล์ใน project root")
    
    print("\n4. 🚀 Upload ไป Render:")
    print("   - Render Dashboard → ptee88 service")
    print("   - Environment → Add Environment File")
    print("   - File name: credentials.json")
    print("   - Copy เนื้อหาไฟล์มาใส่")
    print("   - Deploy service ใหม่")
    
    print("\n5. 🔐 Authorize ใน Production:")
    print("   - ไป https://www.ptee88.com/authorize_drive")
    print("   - Login ด้วย Google Account")
    print("   - อนุญาตสิทธิ์ Google Drive")
    print("   - ระบบจะ redirect กลับมาพร้อม token")

def show_oauth_testing_steps():
    """แสดงขั้นตอนการทดสอบ OAuth2"""
    print("\n🧪 ขั้นตอนการทดสอบ OAuth2:")
    
    print("\n1. 📡 ตรวจสอบ Authorization:")
    print("   - ไป https://www.ptee88.com/drive_status")
    print("   - ควรแสดง {\"authorized\": true}")
    
    print("\n2. 🖼️ ทดสอบอัพโหลดรูป:")
    print("   - ไปหน้า Stock Counting")
    print("   - ใส่บาร์โค้ด #808")
    print("   - ถ่ายรูปและบันทึก")
    print("   - ดู Console (F12) หา log")
    
    print("\n3. 📁 ตรวจสอบ Google Drive:")
    print("   - เข้า Google Drive")
    print("   - ไปโฟลเดอร์ 'Check Stock Project/Pic Stock Counting'")
    print("   - ควรมีไฟล์ .jpg ใหม่")
    
    print("\n4. 🔍 Debug หากมีปัญหา:")
    print("   - ดู Render Logs")
    print("   - ตรวจสอบ Browser Console")
    print("   - ลอง /authorize_drive ใหม่")

def create_oauth_test_script():
    """สร้าง script ทดสอบ OAuth2"""
    print("\n📝 สร้าง OAuth2 test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
ทดสอบการอัพโหลดรูปผ่าน OAuth2 Google Drive
"""

def test_oauth_upload():
    """ทดสอบอัพโหลดรูปด้วย OAuth2"""
    print("🧪 ทดสอบ OAuth2 Google Drive...")
    
    try:
        from oauth_manager import oauth_drive_manager
        
        if not oauth_drive_manager.is_authorized():
            print("❌ OAuth2 ไม่ได้ authorized")
            print("   ไป https://www.ptee88.com/authorize_drive")
            return False
        
        print("✅ OAuth2 authorized แล้ว")
        
        # ทดสอบสร้างโฟลเดอร์
        print("📁 สร้างโฟลเดอร์...")
        folder_id = oauth_drive_manager.get_or_create_folder_path('Check Stock Project/Pic Stock Counting')
        print(f"✅ Folder ID: {folder_id}")
        
        # ทดสอบอัพโหลดรูป
        print("🖼️ อัพโหลดรูปทดสอบ...")
        import base64
        
        # รูป JPEG ขนาดเล็ก
        test_jpeg = "/9j/4AAQSkZJRgABAQEAYABgAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2NjIpLCBxdWFsaXR5ID0gODAK/9sAQwAGBAUGBQQGBgUGBwcGCAoQCgoJCQoUDg0NDhQUExMUFBQUFBwYGRgWGBweFxoeIyAiJScuJyUdLCosKSUZKic8/9sAQwEHBwcKCAoTCgoTPC0VLS0rKyssLC0sKyssKy0sKy0sKy0sKy0sKys8PCs8PCs8Kys8PCs8PCs8Kys8PCs8PCs8/8AAEQgAAQABAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQAGBwgJCgv/xAC1EAACAQMDAgQDBQUEBAAAAX0BAgMABBEFEiExQQYTUWEHInEUMoGRoQgjQrHBFVLR8CQzYnKCCQoWFxgZGiUmJygpKjQ1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4eLj5OXm5+jp6vHy8/T19vf4+fr/xAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJCgv/xAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUkaGx0QoWJsHh8TMzUvBygpOjs+ElGv/EABoQAQEBAQEBAQAAAAAAAAAAAAECAwAEBv/aAAwDAQACEQMRAD8A3qKKKAP/2Q=="
        
        result = oauth_drive_manager.upload_image_from_base64(
            test_jpeg, 
            'oauth_test.jpg',
            folder_id
        )
        
        if result:
            print(f"✅ อัพโหลดสำเร็จ!")
            print(f"🔗 URL: {result['web_view_link']}")
            print(f"📁 File ID: {result['id']}")
            return True
        else:
            print("❌ อัพโหลดล้มเหลว")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 ทดสอบ OAuth2 Google Drive")
    print("=" * 50)
    
    success = test_oauth_upload()
    
    if success:
        print("\\n🎉 OAuth2 พร้อมใช้งาน!")
    else:
        print("\\n❌ OAuth2 ยังไม่พร้อม")
        print("ไป https://www.ptee88.com/authorize_drive")
'''
    
    with open('test_oauth2_upload.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ สร้างไฟล์ test_oauth2_upload.py แล้ว")

def show_priority_steps():
    """แสดงลำดับความสำคัญ"""
    print("\n🎯 ลำดับความสำคัญในการแก้ไข:")
    
    print("\n🥇 ขั้นตอนที่ 1 - เซ็ตอัพ credentials.json:")
    print("   1. Download credentials.json จาก Google Cloud Console")
    print("   2. Upload ไป Render Environment Files")
    print("   3. Deploy service ใหม่")
    
    print("\n🥈 ขั้นตอนที่ 2 - Authorize OAuth2:")
    print("   1. ไป https://www.ptee88.com/authorize_drive")
    print("   2. Login และอนุญาตสิทธิ์")
    print("   3. ตรวจสอบที่ /drive_status")
    
    print("\n🥉 ขั้นตอนที่ 3 - ทดสอบ:")
    print("   1. ทดสอบอัพโหลดรูป")
    print("   2. ตรวจสอบใน Google Drive")
    print("   3. แก้ไขปัญหาที่เหลือ")

if __name__ == "__main__":
    print("🔧 คู่มือเซ็ตอัพ OAuth2 Google Drive")
    print("=" * 70)
    
    # ตรวจสอบสถานะปัจจุบัน
    is_ready = check_current_oauth_status()
    
    if is_ready:
        print("\n🎉 OAuth2 พร้อมใช้งานแล้ว!")
        print("ลองทดสอบถ่ายรูปใน www.ptee88.com ดู")
    else:
        show_oauth_setup_steps()
        show_oauth_testing_steps()
        create_oauth_test_script()
        show_priority_steps()
    
    print("\n" + "=" * 70)
    print("📞 หากต้องการความช่วยเหลือ:")
    print("1. ตรวจสอบ Render Logs")
    print("2. ดู Browser Console (F12)")
    print("3. ลอง authorize_drive ใหม่")