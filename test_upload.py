#!/usr/bin/env python3
"""
Test Google Drive upload functionality
"""

from upload_to_drive import create_drive_uploader
import base64

def test_simple_upload():
    """Test uploading a simple text file"""
    try:
        uploader = create_drive_uploader()
        print(f"Uploader type: {type(uploader)}")
        
        # Test getting folders
        main_folder = uploader.get_or_create_main_project_folder()
        print(f"Main folder ID: {main_folder}")
        
        inventory_folder = uploader.get_or_create_inventory_folder()
        print(f"Inventory folder ID: {inventory_folder}")
        
        # Test creating a simple base64 image (1x1 pixel red dot)
        # This is a minimal valid JPEG
        red_dot_b64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/fQ=="
        
        print("Testing image upload...")
        result = uploader.upload_image_from_base64(
            red_dot_b64,
            "test_image.jpg",
            inventory_folder
        )
        
        print(f"Upload result: {result}")
        
        if result:
            print("SUCCESS: Image uploaded successfully!")
            print(f"File ID: {result['file_id']}")
            print(f"View Link: {result['web_view_link']}")
        else:
            print("FAILED: Image upload failed")
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple_upload()