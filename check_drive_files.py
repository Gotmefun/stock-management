#!/usr/bin/env python3
"""
ตรวจสอบไฟล์ใน Google Drive
Check files in Google Drive folder structure
"""

from upload_to_drive import create_drive_uploader

def check_drive_files():
    """ตรวจสอบไฟล์ทั้งหมดใน Google Drive"""
    print("กำลังเชื่อมต่อ Google Drive...")
    
    try:
        uploader = create_drive_uploader()
        
        if not uploader.service:
            print("❌ ไม่สามารถเชื่อมต่อ Google Drive ได้")
            return
        
        print("✅ เชื่อมต่อ Google Drive สำเร็จ")
        
        # ตรวจสอบโฟลเดอร์หลัก
        print("\n📁 ตรวจสอบโฟลเดอร์ 'check stock project'...")
        main_folder_id = uploader.get_or_create_main_project_folder()
        
        if main_folder_id:
            print(f"✅ พบโฟลเดอร์หลัก ID: {main_folder_id}")
            
            # ค้นหาไฟล์ Stock Data
            print("\n📊 ค้นหาไฟล์ 'Stock Data'...")
            results = uploader.service.files().list(
                q=f"name='Stock Data' and parents in '{main_folder_id}' and mimeType='application/vnd.google-apps.spreadsheet'",
                fields='files(id, name, webViewLink, createdTime, modifiedTime)'
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                print(f"✅ พบไฟล์ 'Stock Data' จำนวน {len(files)} ไฟล์:")
                for file in files:
                    print(f"   📄 ชื่อ: {file['name']}")
                    print(f"   🆔 ID: {file['id']}")
                    print(f"   🔗 ลิงก์: {file['webViewLink']}")
                    print(f"   📅 สร้างเมื่อ: {file['createdTime']}")
                    print(f"   ✏️  แก้ไขล่าสุด: {file['modifiedTime']}")
                    print()
            else:
                print("❌ ไม่พบไฟล์ 'Stock Data'")
                
                # แสดงไฟล์ทั้งหมดในโฟลเดอร์
                print("\n📋 ไฟล์ทั้งหมดในโฟลเดอร์ 'check stock project':")
                all_results = uploader.service.files().list(
                    q=f"parents in '{main_folder_id}'",
                    fields='files(id, name, mimeType, webViewLink)'
                ).execute()
                
                all_files = all_results.get('files', [])
                if all_files:
                    for file in all_files:
                        file_type = "📊" if "spreadsheet" in file['mimeType'] else "📁" if "folder" in file['mimeType'] else "📄"
                        print(f"   {file_type} {file['name']} ({file['mimeType']})")
                        if 'webViewLink' in file:
                            print(f"      🔗 {file['webViewLink']}")
                else:
                    print("   (ไม่มีไฟล์ในโฟลเดอร์)")
            
            # ตรวจสอบโฟลเดอร์ images
            print("\n🖼️  ตรวจสอบโฟลเดอร์ 'images'...")
            images_folder_id = uploader.get_or_create_inventory_folder()
            if images_folder_id:
                print(f"✅ พบโฟลเดอร์ images ID: {images_folder_id}")
                
                # นับจำนวนรูปภาพ
                image_results = uploader.service.files().list(
                    q=f"parents in '{images_folder_id}'",
                    fields='files(id, name)'
                ).execute()
                
                image_files = image_results.get('files', [])
                print(f"📸 จำนวนรูปภาพ: {len(image_files)} ไฟล์")
            
        else:
            print("❌ ไม่พบโฟลเดอร์หลัก")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == '__main__':
    check_drive_files()