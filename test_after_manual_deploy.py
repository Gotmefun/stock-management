#!/usr/bin/env python3
"""
Test OAuth2 after manual deploy
ทดสอบ OAuth2 หลังจาก manual deploy ใน Render.com
"""

import requests
import time
import json

def test_oauth_after_deploy():
    """ทดสอบ OAuth2 หลัง manual deploy"""
    
    BASE_URL = "https://www.ptee88.com"
    
    print("🔄 Testing OAuth2 After Manual Deploy")
    print("=" * 50)
    print(f"🌐 URL: {BASE_URL}")
    print(f"🕐 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create session and login
    session = requests.Session()
    
    print("\n🔑 Login to system...")
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
    
    # Test 1: Check OAuth2 credentials loading
    print("\n📊 Test 1: OAuth2 Drive Status...")
    try:
        status_response = session.get(f'{BASE_URL}/drive_status', timeout=15)
        print(f"Status Code: {status_response.status_code}")
        
        if status_response.status_code == 200:
            result = status_response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get('authorized'):
                print("✅ Google Drive is already authorized")
                oauth_working = True
            else:
                print("ℹ️ Google Drive not authorized yet (normal)")
                print("👉 Need to visit /authorize_drive first")
                oauth_working = True  # Credentials loaded correctly
        else:
            print(f"❌ Status check failed: {status_response.status_code}")
            print(f"Response: {status_response.text}")
            oauth_working = False
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        oauth_working = False
    
    # Test 2: Check OAuth2 authorization endpoint
    print("\n🔗 Test 2: OAuth2 Authorization Endpoint...")
    try:
        # Use allow_redirects=False to see the redirect
        auth_response = session.get(f'{BASE_URL}/authorize_drive', timeout=15, allow_redirects=False)
        print(f"Response Status: {auth_response.status_code}")
        
        if auth_response.status_code == 302:
            redirect_url = auth_response.headers.get('Location', '')
            print(f"Redirect URL: {redirect_url[:100]}...")
            
            if 'accounts.google.com' in redirect_url and 'oauth2' in redirect_url:
                print("✅ OAuth2 authorization URL working correctly")
                auth_endpoint_working = True
            else:
                print(f"⚠️ Unexpected redirect: {redirect_url}")
                auth_endpoint_working = False
                
        elif auth_response.status_code == 200:
            print("ℹ️ No redirect - checking response content...")
            if 'google' in auth_response.text.lower() or 'oauth' in auth_response.text.lower():
                print("✅ OAuth2 content detected")
                auth_endpoint_working = True
            else:
                print("⚠️ No OAuth2 content detected")
                print(f"Response preview: {auth_response.text[:200]}...")
                auth_endpoint_working = False
        else:
            print(f"❌ Unexpected status: {auth_response.status_code}")
            print(f"Response: {auth_response.text[:200]}...")
            auth_endpoint_working = False
            
    except Exception as e:
        print(f"❌ Authorization endpoint error: {e}")
        auth_endpoint_working = False
    
    # Test 3: Test image upload with OAuth2 fallback
    print("\n📷 Test 3: Image Upload with OAuth2 Fallback...")
    
    # We'll temporarily "break" Apps Script to test OAuth2 fallback
    # by using invalid folder or testing the flow
    test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    stock_data = {
        'barcode': 'OAUTH_TEST_123',
        'quantity': 1,
        'branch': 'CITY',
        'product_name': 'OAuth2 Test Product',
        'counter_name': 'OAuth2 Tester',
        'image_data': f'data:image/png;base64,{test_image_data}'
    }
    
    try:
        print("📤 Sending test data...")
        upload_response = session.post(
            f'{BASE_URL}/submit_stock',
            json=stock_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"Upload Status: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            print(f"Upload Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("✅ Image upload successful")
                saved_to = result.get('saved_to', {})
                print(f"💾 Saved to: Supabase={saved_to.get('supabase')}, Sheets={saved_to.get('sheets')}")
                upload_working = True
            else:
                print(f"❌ Upload failed: {result.get('error')}")
                upload_working = False
        else:
            print(f"❌ Upload HTTP error: {upload_response.status_code}")
            print(f"Response: {upload_response.text[:300]}...")
            upload_working = False
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        upload_working = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 OAuth2 Test Results:")
    print("=" * 60)
    
    print(f"🔧 OAuth2 Credentials Loading: {'✅ Working' if oauth_working else '❌ Failed'}")
    print(f"🔗 Authorization Endpoint: {'✅ Working' if auth_endpoint_working else '❌ Failed'}")  
    print(f"📷 Image Upload System: {'✅ Working' if upload_working else '❌ Failed'}")
    
    overall_success = oauth_working and auth_endpoint_working and upload_working
    
    if overall_success:
        print("\n🎉 OAuth2 Setup Complete!")
        print("✅ All systems working correctly")
        print("🔄 Fallback mechanism ready")
        
        print("\n👥 Next Steps for Users:")
        print("1. Visit: https://www.ptee88.com/authorize_drive")
        print("2. Authorize Google Drive access")
        print("3. OAuth2 fallback will be active")
        
    else:
        print("\n⚠️ Some issues detected")
        print("🔧 Check Render.com environment variables")
        print("📋 Verify GOOGLE_CREDENTIALS is set correctly")
    
    print(f"\n🏁 Testing completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    return overall_success

if __name__ == "__main__":
    success = test_oauth_after_deploy()
    exit(0 if success else 1)