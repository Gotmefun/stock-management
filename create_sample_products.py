#!/usr/bin/env python3
"""
สร้างสินค้าตัวอย่างใน Supabase เพื่อทดสอบการนับสต๊อก
Create sample products in Supabase for testing stock counting
"""

import os
from supabase import create_client
from datetime import datetime

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')

def create_supabase_client():
    """Create Supabase client"""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ กรุณาตั้งค่า SUPABASE_URL และ SUPABASE_ANON_KEY ใน environment variables")
        print("Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        return None
    
    try:
        return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ Supabase: {e}")
        print(f"Cannot connect to Supabase: {e}")
        return None

def create_sample_products(supabase):
    """สร้างสินค้าตัวอย่างใน Supabase"""
    print("📦 สร้างสินค้าตัวอย่าง...")
    
    # สินค้าตัวอย่างที่มีบาร์โค้ดง่ายๆ สำหรับทดสอบ
    sample_products = [
        {
            'sku': 'TEST001',
            'barcode': '1234567890123',
            'name': 'นมสด เมจิ 1000 มล.',
            'description': 'นมสดพาสเจอร์ไรส์ เมจิ 1000 มิลลิลิตร',
            'category': 'เครื่องดื่ม',
            'brand': 'เมจิ',
            'unit': 'กล่อง',
            'cost_price': 45.00,
            'selling_price': 59.00,
            'reorder_level': 20,
            'max_stock_level': 100,
            'is_active': True
        },
        {
            'sku': 'TEST002', 
            'barcode': '8851019991234',
            'name': 'ข้าวโอ๊ต เควกเกอร์ 500 กรัม',
            'description': 'ข้าวโอ๊ตสำหรับอาหารเช้า',
            'category': 'อาหารแห้ง',
            'brand': 'เควกเกอร์',
            'unit': 'กล่อง',
            'cost_price': 120.00,
            'selling_price': 149.00,
            'reorder_level': 10,
            'max_stock_level': 50,
            'is_active': True
        },
        {
            'sku': 'TEST003',
            'barcode': '8850999999999',
            'name': 'น้ำแร่ สิงห์ 600 มล.',
            'description': 'น้ำแร่ธรรมชาติ สิงห์ 600 มิลลิลิตร',
            'category': 'เครื่องดื่ม',
            'brand': 'สิงห์',
            'unit': 'ขวด',
            'cost_price': 8.00,
            'selling_price': 12.00,
            'reorder_level': 50,
            'max_stock_level': 200,
            'is_active': True
        },
        {
            'sku': 'TEST004',
            'barcode': '1111111111111',
            'name': 'ชาเขียว โออิชิ 500 มล.',
            'description': 'ชาเขียวพร้อมดื่ม โออิชิ 500 มิลลิลิตร',
            'category': 'เครื่องดื่ม',
            'brand': 'โออิชิ',
            'unit': 'ขวด',
            'cost_price': 15.00,
            'selling_price': 20.00,
            'reorder_level': 30,
            'max_stock_level': 120,
            'is_active': True
        },
        {
            'sku': 'TEST005',
            'barcode': '2222222222222',
            'name': 'บะหมี่กึ่งสำเร็จรูป มาม่า',
            'description': 'บะหมี่กึ่งสำเร็จรูป รสหมูต้ม',
            'category': 'อาหารกึ่งสำเร็จรูป',
            'brand': 'มาม่า',
            'unit': 'ซอง',
            'cost_price': 6.00,
            'selling_price': 9.00,
            'reorder_level': 100,
            'max_stock_level': 500,
            'is_active': True
        }
    ]
    
    try:
        # ลบสินค้าเดิมที่อาจมีอยู่
        print("🧹 ลบสินค้าทดสอบเดิม...")
        supabase.table('products').delete().in_('sku', ['TEST001', 'TEST002', 'TEST003', 'TEST004', 'TEST005']).execute()
        
        # เพิ่มสินค้าใหม่
        result = supabase.table('products').insert(sample_products).execute()
        
        if result.data:
            print(f"✅ สร้างสินค้าตัวอย่าง {len(result.data)} รายการสำเร็จ!")
            print("\n📋 สินค้าที่สร้าง:")
            for product in result.data:
                print(f"   🏷️ {product['barcode']} - {product['name']}")
            
            print(f"\n🎯 สามารถทดสอบสแกนบาร์โค้ดได้:")
            for product in sample_products:
                print(f"   📱 {product['barcode']} ({product['name']})")
                
            return True
        else:
            print("❌ ไม่สามารถสร้างสินค้าได้")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def setup_branches(supabase):
    """ตั้งค่าสาขาใน Supabase"""
    print("🏪 ตั้งค่าสาขา...")
    
    branches = [
        {'code': 'MAIN', 'name': 'สาขาหลัก', 'is_active': True},
        {'code': 'CITY', 'name': 'สาขาตัวเมือง', 'is_active': True},
        {'code': 'PONGPAI', 'name': 'สาขาโป่งไผ่', 'is_active': True},
        {'code': 'SCHOOL', 'name': 'สาขาหน้าโรงเรียน', 'is_active': True}
    ]
    
    try:
        # ลบสาขาเดิม
        supabase.table('branches').delete().in_('code', ['MAIN', 'CITY', 'PONGPAI', 'SCHOOL']).execute()
        
        # เพิ่มสาขาใหม่
        result = supabase.table('branches').insert(branches).execute()
        
        if result.data:
            print(f"✅ สร้างสาขา {len(result.data)} สาขาสำเร็จ!")
            for branch in result.data:
                print(f"   🏪 {branch['name']} ({branch['code']})")
            return True
        else:
            print("❌ ไม่สามารถสร้างสาขาได้")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 เริ่มตั้งค่าข้อมูลตัวอย่างสำหรับการทดสอบ...")
    print("Setting up sample data for testing...")
    
    # เชื่อมต่อ Supabase
    supabase = create_supabase_client()
    if not supabase:
        return False
    
    print(f"🔗 เชื่อมต่อกับ Supabase: {SUPABASE_URL}")
    
    # ตั้งค่าสาขา
    if not setup_branches(supabase):
        print("❌ ไม่สามารถตั้งค่าสาขาได้")
        return False
    
    # สร้างสินค้าตัวอย่าง
    if not create_sample_products(supabase):
        print("❌ ไม่สามารถสร้างสินค้าตัวอย่างได้")
        return False
    
    print("\n🎉 ตั้งค่าเสร็จสิ้น!")
    print("Setup completed!")
    print("\n📱 ตอนนี้สามารถทดสอบนับสต๊อกได้แล้ว:")
    print("You can now test stock counting with these barcodes:")
    print("   • 1234567890123 (นมสด เมจิ)")
    print("   • 8851019991234 (ข้าวโอ๊ต เควกเกอร์)")
    print("   • 8850999999999 (น้ำแร่ สิงห์)")
    print("   • 1111111111111 (ชาเขียว โออิชิ)")
    print("   • 2222222222222 (บะหมี่ มาม่า)")
    
    return True

if __name__ == "__main__":
    main()