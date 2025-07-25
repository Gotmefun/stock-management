#!/usr/bin/env python3
"""
Test submit_stock endpoint to debug 500 error
"""

import requests
import json
import base64

def create_test_image():
    """Create a simple test image in base64 format"""
    test_image_data = """iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="""
    return f"data:image/png;base64,{test_image_data}"

def test_submit_stock():
    """Test the submit_stock endpoint"""
    
    # First, login to get session
    login_data = {
        'username': 'admin',
        'password': 'Teeomega2014'
    }
    
    print("🔐 Logging in...")
    session = requests.Session()
    
    # Login
    login_response = session.post('http://127.0.0.1:8081/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    # Test submit_stock
    print("\n📤 Testing submit_stock...")
    
    stock_data = {
        'barcode': '123456789',
        'quantity': 10,
        'branch': 'CITY',
        'product_name': 'Test Product',
        'counter_name': 'Test Counter',
        'image_data': create_test_image()
    }
    
    print(f"Sending data: {list(stock_data.keys())}")
    print(f"Branch: {stock_data['branch']}")
    print(f"Image data length: {len(stock_data['image_data'])}")
    
    try:
        response = session.post(
            'http://127.0.0.1:8081/submit_stock',
            json=stock_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response Text: {response.text}")
            
        if response.status_code == 200:
            print("✅ Success!")
        else:
            print(f"❌ Failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    test_submit_stock()