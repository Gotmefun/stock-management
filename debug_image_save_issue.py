#!/usr/bin/env python3
"""
หาสาเหตุที่รูปไม่บันทึกไป Google Drive
"""

import requests
import json

def test_google_apps_script_with_folder():
    """ทดสอบ Google Apps Script พร้อม folder parameter"""
    print("🔍 ทดสอบการส่งรูปไป Google Apps Script...")
    
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec"
    
    # รูปภาพ JPEG จริง (ขนาดเล็ก)
    test_jpeg_b64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2NjIpLCBxdWFsaXR5ID0gODAK/9sAQwAGBAUGBQQGBgUGBwcGCAoQCgoJCQoUDg0NDhQUExMUFBQUFBwYGRgWGBweFxoeIyAiJScuJyUdLCosKSUZKic8/9sAQwEHBwcKCAoTCgoTPC0VLS0rKyssLC0sKyssKy0sKy0sKy0sKy0sKys8PCs8PCs8Kys8PCs8PCs8Kys8PCs8PCs8/8AAEQgAAQABAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQAGBwgJCgv/xAC1EAACAQMDAgQDBQUEBAAAAX0BAgMABBEFEiExQQYTUWEHInEUMoGRoQgjQrHBFVLR8CQzYnKCCQoWFxgZGiUmJygpKjQ1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4eLj5OXm5+jp6vHy8/T19vf4+fr/xAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJCgv/xAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUkaGx0QoWJsHh8TMzUvBygpOjs+ElGv/EABoQAQEBAQEBAQAAAAAAAAAAAAECAwAEBv/aAAwDAQACEQMRAD8A3qKKKAP/2Q=="
    
    # ทดสอบทั้ง 3 แบบ
    test_cases = [
        {
            "name": "แบบมี folder parameter",
            "payload": {
                'imageData': test_jpeg_b64,
                'filename': 'test_with_folder.jpg',
                'folder': 'Check Stock Project/Pic Stock Counting'
            }
        },
        {
            "name": "แบบไม่มี folder parameter", 
            "payload": {
                'imageData': test_jpeg_b64,
                'filename': 'test_no_folder.jpg'
            }
        },
        {
            "name": "แบบ folder เป็น string ว่าง",
            "payload": {
                'imageData': test_jpeg_b64,
                'filename': 'test_empty_folder.jpg',
                'folder': ''
            }
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- ทดสอบที่ {i+1}: {test_case['name']} ---")
        
        try:
            print(f"📤 ส่งข้อมูล: {test_case['payload']['filename']}")
            if 'folder' in test_case['payload']:
                print(f"📁 Folder: '{test_case['payload']['folder']}'")
            
            response = requests.post(
                APPS_SCRIPT_URL,
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                results.append({
                    'test': test_case['name'],
                    'success': result.get('success', False),
                    'fileId': result.get('fileId', ''),
                    'url': result.get('webViewLink', ''),
                    'folderPath': result.get('folderPath', 'ไม่ระบุ')
                })
            else:
                print(f"❌ HTTP Error: {response.text}")
                results.append({
                    'test': test_case['name'],
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            results.append({
                'test': test_case['name'],
                'success': False,
                'error': str(e)
            })
    
    return results

def check_app_py_image_upload():
    """ตรวจสอบโค้ดในไฟล์ app.py"""
    print("\n🔍 ตรวจสอบการอัพโหลดรูปใน app.py...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ พบ APPS_SCRIPT_URL ใน app.py")
        
        # หาส่วน upload_via_apps_script function
        if "upload_via_apps_script" in content:
            print("✅ พบ function upload_via_apps_script")
            
            # ตรวจสอบว่ามีการส่ง folder parameter หรือไม่
            if "'folder': 'Check Stock Project/Pic Stock Counting'" in content:
                print("✅ มีการส่ง folder parameter")
            else:
                print("❌ ไม่มีการส่ง folder parameter")
                
        # ตรวจสอบส่วน submit_stock function
        if "submit_stock" in content:
            print("✅ พบ function submit_stock")
            
            # ตรวจสอบลำดับการอัพโหลด
            if "upload_via_apps_script" in content:
                print("✅ มีการเรียก upload_via_apps_script")
                
        return True
        
    except FileNotFoundError:
        print("❌ ไม่พบไฟล์ app.py")
        return False

def show_debug_steps():
    """แสดงขั้นตอนการ debug"""
    print("\n🛠️ ขั้นตอนการ debug ปัญหารูปไม่บันทึก:")
    
    print("\n1. 🧪 ทดสอบจริงในเว็บไซต์:")
    print("   - ไป www.ptee88.com")
    print("   - Login เข้าระบบ")
    print("   - ไปหน้า 'นับสต๊อกสินค้า'")
    print("   - ใส่บาร์โค้ด #808")
    print("   - เปิดกล้อง และถ่ายรูป")
    print("   - กด 'บันทึกข้อมูล'")
    
    print("\n2. 📱 ตรวจสอบ Browser Console:")
    print("   - กด F12 → Console tab")
    print("   - ดูว่ามี error หรือไม่")
    print("   - ดู Network tab → ดู request ไป /submit_stock")
    print("   - ตรวจสอบว่า image_data ถูกส่งหรือไม่")
    
    print("\n3. 🖥️ ตรวจสอบ Render Logs:")
    print("   - Render Dashboard → ptee88 service → Logs")
    print("   - ดูว่ามี error ตอน upload รูปหรือไม่")
    print("   - ดู response จาก Google Apps Script")
    
    print("\n4. 📁 ตรวจสอบ Google Drive:")
    print("   - เข้า Google Drive")
    print("   - ไปโฟลเดอร์ 'Check Stock Project'")
    print("   - ดูใน 'Pic Stock Counting'")
    print("   - ควรมีไฟล์ .jpg ใหม่")

def analyze_possible_causes():
    """วิเคราะห์สาเหตุที่เป็นไปได้"""
    print("\n⚠️ สาเหตุที่รูปอาจไม่บันทึก:")
    
    print("\n1. 🚫 Google Apps Script ปัญหา:")
    print("   - URL หมดอายุ หรือ เปลี่ยน")
    print("   - Script ไม่ได้ Deploy ใหม่")
    print("   - Permission ไม่เพียงพอ")
    
    print("\n2. 📁 ปัญหา Folder:")
    print("   - Apps Script ไม่สร้างโฟลเดอร์")
    print("   - เก็บในโฟลเดอร์ผิด")
    print("   - ชื่อโฟลเดอร์ผิด")
    
    print("\n3. 💾 ปัญหาข้อมูล:")
    print("   - รูปไม่ถูกส่งจาก Browser")
    print("   - Image data เสียหาย")
    print("   - File size ใหญ่เกินไป")
    
    print("\n4. 🔗 ปัญหาการเชื่อมต่อ:")
    print("   - Network timeout")
    print("   - Render → Google Script connection")
    print("   - CORS หรือ Security issues")

if __name__ == "__main__":
    print("🔍 วิเคราะห์ปัญหารูปไม่บันทึกไป Google Drive")
    print("=" * 70)
    
    # ทดสอบ Apps Script
    test_results = test_google_apps_script_with_folder()
    
    # ตรวจสอบโค้ด
    check_app_py_image_upload()
    
    print("\n" + "=" * 70)
    print("📊 สรุปผลการทดสอบ:")
    
    for result in test_results:
        status = "✅" if result['success'] else "❌"
        print(f"   {status} {result['test']}")
        if result['success']:
            print(f"      📁 Folder: {result['folderPath']}")
            print(f"      🔗 URL: {result['url'][:50]}...")
    
    analyze_possible_causes()
    show_debug_steps()
    
    print("\n🎯 สำคัญที่สุด:")
    print("1. ทดสอบถ่ายรูปจริงใน www.ptee88.com")
    print("2. ตรวจสอบ Console (F12) หา error")
    print("3. ดู Render Logs ว่ารูปถูกส่งไปหรือไม่")
    print("4. เช็ค Google Drive ว่ามีไฟล์ใหม่หรือไม่")