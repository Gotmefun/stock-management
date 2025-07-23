#!/usr/bin/env python3
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
        print("\n🎉 OAuth2 พร้อมใช้งาน!")
    else:
        print("\n❌ OAuth2 ยังไม่พร้อม")
        print("ไป https://www.ptee88.com/authorize_drive")
