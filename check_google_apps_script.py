#!/usr/bin/env python3
"""
ตรวจสอบ Google Apps Script และแก้ไขให้เก็บในโฟลเดอร์ที่ถูกต้อง
"""

import requests
import json

def test_current_apps_script():
    """ทดสอบ Apps Script ปัจจุบัน"""
    print("🧪 ทดสอบ Google Apps Script ปัจจุบัน...")
    
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec"
    
    # สร้างรูปภาพทดสอบ
    test_image_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    payload = {
        'imageData': test_image_b64,
        'filename': 'test_stock_photo.png',
        'folder': 'Check Stock Project/Pic Stock Counting'  # เพิ่ม folder path
    }
    
    try:
        print(f"📤 ส่งไปยัง: {APPS_SCRIPT_URL}")
        print(f"📁 โฟลเดอร์เป้าหมาย: Check Stock Project/Pic Stock Counting")
        
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
                file_url = result.get('webViewLink')
                print(f"✅ อัพโหลดสำเร็จ!")
                print(f"🔗 URL: {file_url}")
                print(f"📁 File ID: {result.get('fileId')}")
                
                # ตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์ที่ถูกต้องหรือไม่
                if result.get('folderPath'):
                    print(f"📂 เก็บในโฟลเดอร์: {result.get('folderPath')}")
                    if 'Pic Stock Counting' in result.get('folderPath', ''):
                        print("✅ เก็บในโฟลเดอร์ที่ถูกต้อง")
                    else:
                        print("⚠️ เก็บในโฟลเดอร์ผิด - ต้องแก้ไข Apps Script")
                else:
                    print("⚠️ ไม่ทราบโฟลเดอร์ที่เก็บ")
                
                return True
            else:
                print(f"❌ อัพโหลดล้มเหลว: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def create_improved_apps_script():
    """สร้าง Google Apps Script ที่ปรับปรุงแล้ว"""
    print("\n📝 Google Apps Script ที่ปรับปรุงแล้ว:")
    print("=" * 60)
    
    script_code = '''
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var imageData = data.imageData;
    var filename = data.filename || 'stock_image.jpg';
    var folderPath = data.folder || 'Check Stock Project/Pic Stock Counting';
    
    console.log('Received request:', filename, folderPath);
    
    // Remove data URL prefix if present
    if (imageData.indexOf('data:') === 0) {
      imageData = imageData.split(',')[1];
    }
    
    // Convert base64 to blob
    var blob = Utilities.base64Decode(imageData);
    var file;
    
    // Get or create target folder
    var targetFolder = getOrCreateFolder(folderPath);
    
    if (filename.endsWith('.jpg') || filename.endsWith('.jpeg')) {
      file = targetFolder.createFile(Utilities.newBlob(blob, 'image/jpeg', filename));
    } else {
      file = targetFolder.createFile(Utilities.newBlob(blob, 'image/png', filename));
    }
    
    console.log('File created:', file.getId(), file.getName());
    
    return ContentService
      .createTextOutput(JSON.stringify({
        success: true,
        fileId: file.getId(),
        webViewLink: file.getUrl(),
        downloadLink: 'https://drive.google.com/uc?id=' + file.getId(),
        folderPath: folderPath,
        filename: filename
      }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.error('Error:', error.toString());
    return ContentService
      .createTextOutput(JSON.stringify({
        success: false,
        error: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function getOrCreateFolder(path) {
  var folders = path.split('/');
  var currentFolder = DriveApp.getRootFolder();
  
  for (var i = 0; i < folders.length; i++) {
    var folderName = folders[i].trim();
    if (folderName === '') continue;
    
    var subFolders = currentFolder.getFoldersByName(folderName);
    if (subFolders.hasNext()) {
      currentFolder = subFolders.next();
    } else {
      currentFolder = currentFolder.createFolder(folderName);
    }
  }
  
  return currentFolder;
}
'''
    
    print(script_code)
    print("=" * 60)
    print("\n🔧 วิธีอัพเดท Google Apps Script:")
    print("1. ไปที่: https://script.google.com")
    print("2. เลือกโปรเจค Apps Script ที่มีอยู่")
    print("3. แทนที่โค้ดด้วยโค้ดข้างต้น")
    print("4. Save และ Deploy ใหม่")
    print("5. Copy URL ใหม่ไปใส่ใน Render Environment Variables")

def show_fix_steps():
    """แสดงขั้นตอนแก้ไข"""
    print("\n🎯 สรุปปัญหาและการแก้ไข:")
    print("1. ✅ Google Apps Script ทำงานได้")
    print("2. ⚠️ แต่อาจเก็บไฟล์ในโฟลเดอร์ผิด") 
    print("3. ❌ หรือไม่ได้สร้างโฟลเดอร์ 'Pic Stock Counting'")
    
    print("\n🔧 วิธีแก้ไข:")
    print("1. อัพเดท Google Apps Script (ใช้โค้ดข้างต้น)")
    print("2. หรือ Upload credentials.json ใน Render")
    print("3. หรือ Authorize OAuth2 ที่ /auth/google")
    
    print("\n📋 ลำดับความสำคัญ:")
    print("1. 🥇 อัพเดท Apps Script (แนะนำ)")
    print("2. 🥈 Upload credentials.json") 
    print("3. 🥉 OAuth2 authorization")

if __name__ == "__main__":
    print("🔍 ตรวจสอบ Google Apps Script และการเก็บรูปภาพ")
    print("=" * 70)
    
    success = test_current_apps_script()
    
    if not success:
        create_improved_apps_script()
    
    show_fix_steps()