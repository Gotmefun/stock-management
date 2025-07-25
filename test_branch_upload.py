#!/usr/bin/env python3
"""
Test script to verify branch-specific image upload to Google Drive
via Google Apps Script Web App URL
"""

import requests
import json
import base64
from datetime import datetime

def create_test_image():
    """Create a simple test image in base64 format"""
    # Create a simple red square image (1x1 pixel PNG)
    # This is a minimal PNG image encoded in base64
    test_image_data = """iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="""
    return f"data:image/png;base64,{test_image_data}"

def test_branch_upload(branch_code, branch_name):
    """Test image upload for a specific branch"""
    APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec"
    
    # Create test image
    image_data = create_test_image()
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_{branch_code}_{timestamp}.png"
    
    # Create folder path according to our mapping
    branch_mapping = {
        'CITY': 'สาขาตัวเมือง',
        'SCHOOL': 'สาขาหน้าโรงเรียน', 
        'PONGPAI': 'สาขาโป่งไผ่'
    }
    
    folder_name = branch_mapping.get(branch_code, 'สาขาตัวเมือง')
    folder = f'Check Stock Project/{folder_name}'
    
    payload = {
        'imageData': image_data,
        'filename': filename,
        'folder': folder
    }
    
    print(f"\n🧪 ทดสอบอัปโหลดสำหรับ {branch_name} ({branch_code})")
    print(f"📁 โฟลเดอร์: {folder}")
    print(f"📄 ไฟล์: {filename}")
    print(f"📤 ส่งข้อมูลไปยัง Google Apps Script...")
    
    try:
        response = requests.post(
            APPS_SCRIPT_URL,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📄 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print(f"✅ สำเร็จ! ลิงก์: {result.get('webViewLink')}")
                return result.get('webViewLink')
            else:
                print(f"❌ ล้มเหลว: {result.get('error')}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response text: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("🚀 ทดสอบระบบอัปโหลดรูปภาพตามสาขา")
    print("=" * 50)
    
    # Test all branches
    branches = [
        ('CITY', 'สาขาตัวเมือง'),
        ('SCHOOL', 'สาขาหน้าโรงเรียน'),
        ('PONGPAI', 'สาขาโป่งไผ่')
    ]
    
    results = {}
    
    for branch_code, branch_name in branches:
        result = test_branch_upload(branch_code, branch_name)
        results[branch_code] = result
        print("-" * 30)
    
    print("\n📊 สรุปผลการทดสอบ:")
    print("=" * 50)
    
    for branch_code, result in results.items():
        status = "✅ สำเร็จ" if result else "❌ ล้มเหลว"
        print(f"{branch_code}: {status}")
        if result:
            print(f"  ลิงก์: {result}")
    
    success_count = sum(1 for r in results.values() if r)
    print(f"\nผลรวม: {success_count}/{len(branches)} สาขา อัปโหลดสำเร็จ")
    
    if success_count == len(branches):
        print("\n🎉 ระบบทำงานสมบูรณ์แล้ว!")
    else:
        print("\n⚠️  มีปัญหาบางส่วน กรุณาตรวจสอบ Google Apps Script")

if __name__ == "__main__":
    main()