#!/usr/bin/env python3
"""
Test image upload with debug logging
ทดสอบการอัปโหลดรูปพร้อม debug logs หลัง manual deploy
"""

import requests
import json
import time

def test_with_debug_logs():
    """ทดสอบการอัปโหลดพร้อม debug logs"""
    
    BASE_URL = "https://www.ptee88.com"
    
    print("🔍 Testing Image Upload with Debug Logs")
    print("=" * 50)
    print(f"🌐 URL: {BASE_URL}")
    print(f"🕐 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
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
    
    # Test image upload with CITY branch
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    stock_data = {
        'barcode': f'DEBUGLOG{int(time.time())}',
        'quantity': 7,
        'branch': 'CITY',  # ทดสอบ CITY branch
        'product_name': 'Debug Log Test Product',
        'counter_name': 'Debug Logger',
        'image_data': f'data:image/png;base64,{test_image_data}'
    }
    
    print(f"\n📤 ส่งข้อมูลทดสอบ:")
    print(f"  Branch: {stock_data['branch']} (should map to สาขาตัวเมือง)")
    print(f"  Barcode: {stock_data['barcode']}")
    print(f"  Image data: {len(stock_data['image_data'])} characters")
    
    try:
        print("\n🔄 Sending request to /submit_stock...")
        
        response = session.post(
            f'{BASE_URL}/submit_stock',
            json=stock_data,
            headers={'Content-Type': 'application/json'},
            timeout=90  # เพิ่ม timeout สำหรับ debug
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\n📄 Production Response:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                if result.get('success'):
                    print("\n✅ Production upload successful!")
                    
                    saved_to = result.get('saved_to', {})
                    print(f"\n💾 Data saved to:")
                    print(f"  - Supabase: {saved_to.get('supabase', False)}")
                    print(f"  - Google Sheets: {saved_to.get('sheets', False)}")
                    
                    # เช็คว่ามี image URL ใน response หรือไม่
                    if 'image_url' in result:
                        print(f"\n📷 Image URL in response: {result['image_url']}")
                    else:
                        print(f"\n⚠️  No image_url in production response")
                        print("🔍 This means image_url was not captured from Apps Script")
                    
                    return True
                    
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"\n❌ Production upload failed: {error_msg}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON decode error: {e}")
                print(f"Response text: {response.text}")
                return False
                
        else:
            print(f"\n❌ HTTP error: {response.status_code}")
            print(f"Response text: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"\n❌ Request exception: {e}")
        return False

def check_google_drive():
    """ตรวจสอบว่ารูปไปที่ Google Drive หรือไม่"""
    
    print(f"\n🔍 Manual Check Required:")
    print("=" * 30)
    print("📂 กรุณาตรวจสอบ Google Drive manually:")
    print("1. เข้า Google Drive")
    print("2. หา folder: Check Stock Project")
    print("3. เข้าไปใน: สาขาตัวเมือง")
    print("4. ดูว่ามีไฟล์รูป debug_* หรือ stock_* ใหม่หรือไม่")
    print("")
    print("📅 ไฟล์ที่ควรจะเห็น:")
    print(f"   - debug_city_{int(time.time())}.png (จากการทดสอบก่อนหน้า)")
    print(f"   - stock_DEBUGLOG{int(time.time())}_*.jpg (จากการทดสอบนี้)")

def main():
    """Main testing function"""
    
    print("🧪 Debug Logging Test for Image Upload")
    print("🚨 This test requires manual deploy first!")
    print("=" * 60)
    
    # Test production upload
    success = test_with_debug_logs()
    
    # Manual check instructions
    check_google_drive()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Debug Test Summary:")
    print("=" * 60)
    
    if success:
        print("✅ Production request successful")
        print("🔍 Check server logs in Render.com for detailed debug info")
        print("👁️  Look for these debug messages:")
        print("   - '=== APPS SCRIPT RESPONSE ==='")
        print("   - 'Returned image_url: ...'")
        print("   - 'Branch mapping: CITY -> ...'")
    else:
        print("❌ Production request failed")
        print("🔧 Check Render.com deployment status")
    
    print("\n📋 Next Steps:")
    print("1. Check Render.com logs for debug output")
    print("2. Verify Google Drive has new images")
    print("3. Check if image_url is being captured")
    print("4. Verify Supabase gets image_url")
    
    print(f"\n🏁 Debug test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()