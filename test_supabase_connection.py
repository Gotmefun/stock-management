#!/usr/bin/env python3
"""
ทดสอบการเชื่อมต่อ Supabase
"""

from supabase import create_client

# Configuration
SUPABASE_URL = "https://khiooiigrfrluvyobljq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtoaW9vaWlncmZybHV2eW9ibGpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTMxMjAxNDYsImV4cCI6MjA2ODY5NjE0Nn0.M9mwVk8WnEQfb2l7-NOdnrmJqSThYf2TqJK1ahnsx-Q"

def test_connection():
    print("🔗 ทดสอบการเชื่อมต่อ Supabase...")
    print(f"URL: {SUPABASE_URL}")
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # ทดสอบการเชื่อมต่อด้วยการดึงข้อมูลจากตาราง
        result = client.table('products').select('*').limit(1).execute()
        
        if result.data is not None:
            print("✅ เชื่อมต่อ Supabase สำเร็จ!")
            print(f"📊 พบข้อมูลในตาราง products: {len(result.data)} รายการ")
            return True
        else:
            print("⚠️ เชื่อมต่อได้แต่ไม่พบข้อมูล")
            return False
            
    except Exception as e:
        print(f"❌ เชื่อมต่อ Supabase ล้มเหลว: {e}")
        return False

if __name__ == "__main__":
    test_connection()