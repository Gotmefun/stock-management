#!/usr/bin/env python3
"""
Debug การอัพโหลดภาพจริงจากการถ่ายใน Stock Counting
"""

import requests
import json

def test_real_stock_photo_upload():
    """ทดสอบการอัพโหลดภาพจริงแบบที่ระบบใช้"""
    print("📸 ทดสอบการอัพโหลดภาพ Stock Counting จริง...")
    
    # จำลองข้อมูลที่ส่งจาก Stock Counting form
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec"
    
    # สร้างภาพ JPEG ขนาดเล็ก (จำลองการถ่ายจากกล้อง)
    # ใช้ base64 ของภาพ JPEG 1x1 pixel สีแดง
    test_jpeg_b64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2NjIpLCBxdWFsaXR5ID0gODAK/9sAQwAGBAUGBQQGBgUGBwcGCAoQCgoJCQoUDg0NDhQUExMUFBQUFBwYGRgWGBweFxoeIyAiJScuJyUdLCosKSUZKic8/9sAQwEHBwcKCAoTCgoTPC0VLS0rKyssLC0sKyssKy0sKy0sKy0sKy0sKys8PCs8PCs8Kys8PCs8PCs8Kys8PCs8PCs8/8AAEQgAAQABAwEiAAIRAQMRAf/EAB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQAGBwgJCgv/xAC1EAACAQMDAgQDBQUEBAAAAX0BAgMABBEFEiExQQYTUWEHInEUMoGRoQgjQrHBFVLR8CQzYnKCCQoWFxgZGiUmJygpKjQ1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4eLj5OXm5+jp6vHy8/T19vf4+fr/xAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJCgv/xAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUkaGx0QoWJsHh8CMzUvBygpOjs+ElGv/EABoQAQEBAQEBAQAAAAAAAAAAAAECAwAEBv/aAAwDAQACEQMRAD8A3qKKKAP/2Q=="
    
    # จำลองข้อมูลที่ส่งจากฟอร์ม
    payload = {
        'imageData': test_jpeg_b64,
        'filename': 'stock_#808_20250722_120000.jpg',  # รูปแบบไฟล์ที่แอพใช้
        'folder': 'Check Stock Project/Pic Stock Counting'
    }
    
    try:
        print(f"📤 ส่งภาพ JPEG: {payload['filename']}")
        print(f"📁 โฟลเดอร์: {payload['folder']}")
        print(f"🖼️ รูปแบบข้อมูล: {payload['imageData'][:50]}...")
        
        response = requests.post(
            APPS_SCRIPT_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("✅ อัพโหลดสำเร็จ!")
                print(f"🔗 URL: {result.get('webViewLink')}")
                print(f"📁 File ID: {result.get('fileId')}")
                print(f"📂 โฟลเดอร์: {result.get('folderPath', 'ไม่ระบุ')}")
                return True
            else:
                print(f"❌ อัพโหลดล้มเหลว: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def check_stock_counting_process():
    """ตรวจสอบกระบวนการ Stock Counting ทั้งหมด"""
    print("\n🔍 ตรวจสอบกระบวนการ Stock Counting...")
    
    print("1. 📱 การถ่ายภาพ:")
    print("   - ใช้กล้องในเบราว์เซอร์")
    print("   - สร้าง Canvas และแปลงเป็น base64")
    print("   - รูปแบบ: data:image/jpeg;base64,...")
    
    print("\n2. 📤 การส่งข้อมูล:")
    print("   - JavaScript ส่ง POST ไปยัง /submit_stock")
    print("   - รวมข้อมูล: barcode, quantity, branch, image_data")
    print("   - Python รับข้อมูลและประมวลผล")
    
    print("\n3. 🖼️ การอัพโหลดรูป:")
    print("   - ลองส่งไป Google Apps Script ก่อน")
    print("   - ถ้าล้มเหลว ลอง OAuth2 Google Drive")
    print("   - สุดท้าย เก็บ local ในเซิร์ฟเวอร์")
    
    print("\n4. 💾 การบันทึกข้อมูล:")
    print("   - เก็บใน Supabase stock_counts table")
    print("   - เก็บ image_url ที่ได้จากการอัพโหลด")
    print("   - สำรองใน Google Sheets")

def show_debugging_steps():
    """แสดงขั้นตอนการแก้ไข"""
    print("\n🛠️ ขั้นตอนการ Debug:")
    
    print("\n1. 🧪 ทดสอบการถ่ายรูปจริง:")
    print("   - ไปที่ www.ptee88.com")
    print("   - Login และไปหน้า Stock Counting") 
    print("   - กรอกข้อมูล: บาร์โค้ด #808, จำนวน 5")
    print("   - กด 'เปิดกล้อง' และถ่ายรูปจริง")
    print("   - กด 'บันทึกข้อมูล'")
    
    print("\n2. 📱 ตรวจสอบใน Browser:")
    print("   - กด F12 → แท็บ Console")
    print("   - ดู Error messages")
    print("   - แท็บ Network → ดู /submit_stock request")
    print("   - ตรวจสอบ Response Status")
    
    print("\n3. 🔍 ตรวจสอบใน Render Logs:")
    print("   - Render Dashboard → Service ptee88 → Logs")
    print("   - ดูว่ามี Error ขณะอัพโหลดรูปหรือไม่")
    print("   - ดูว่า Apps Script ตอบสนองอย่างไร")
    
    print("\n4. 📁 ตรวจสอบ Google Drive:")
    print("   - ดูใน 'Check Stock Project/Pic Stock Counting'")
    print("   - ภาพควรมีชื่อรูปแบบ: stock_[barcode]_[timestamp].jpg")
    print("   - ถ้าไม่มี = การอัพโหลดล้มเหลว")

def identify_possible_issues():
    """ระบุปัญหาที่เป็นไปได้"""
    print("\n⚠️ ปัญหาที่เป็นไปได้:")
    
    print("\n1. 📱 ปัญหาการถ่ายภาพ:")
    print("   - ไม่ได้ถ่ายรูปจริง (เฉพาะการพิมพ์บาร์โค้ด)")
    print("   - Camera permission ถูกปฏิเสธ")
    print("   - JavaScript error ขณะสร้าง Canvas")
    
    print("\n2. 🔗 ปัญหาการส่งข้อมูล:")
    print("   - Image data ไม่ได้ส่งไปใน payload")
    print("   - Server error ขณะประมวลผล")
    print("   - Network timeout")
    
    print("\n3. 📤 ปัญหา Google Apps Script:")
    print("   - Apps Script error หรือ timeout")
    print("   - Permission ไม่เพียงพอ")
    print("   - Folder path ไม่ถูกต้อง")
    
    print("\n4. 💾 ปัญหาการบันทึก:")
    print("   - ข้อมูลบันทึกแต่รูปไม่อัพโหลด")
    print("   - Image URL ว่าง แต่ข้อมูลอื่นถูกต้อง")

if __name__ == "__main__":
    print("🔍 Debug การอัพโหลดภาพจริงจาก Stock Counting")
    print("=" * 70)
    
    # ทดสอบการอัพโหลด JPEG
    success = test_real_stock_photo_upload()
    
    check_stock_counting_process()
    identify_possible_issues()
    show_debugging_steps()
    
    print("\n" + "=" * 70)
    print("🎯 ขั้นตอนสำคัญ:")
    print("1. ทดสอบถ่ายรูปจริงที่ www.ptee88.com")
    print("2. ตรวจสอบ Console (F12) หา Error")
    print("3. ดู Render Logs หา Error message")  
    print("4. ตรวจสอบ Google Drive หารูป .jpg ใหม่")
    
    if success:
        print("\n✅ การทดสอบ JPEG upload สำเร็จ - ตอนนี้ลองถ่ายรูปจริงดู!")
    else:
        print("\n❌ การทดสอบล้มเหลว - ต้องแก้ไข Apps Script หรือใช้ credentials.json")