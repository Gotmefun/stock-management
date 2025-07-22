#!/usr/bin/env python3
"""
Script to populate Supabase with sample products and branches data
Run this after setting up your Supabase database
"""

import os
from supabase_manager import create_supabase_manager

def populate_sample_data():
    """Populate Supabase with sample products and ensure branches exist"""
    
    # Check if environment variables are set
    if not os.environ.get('SUPABASE_URL') or not os.environ.get('SUPABASE_ANON_KEY'):
        print("❌ Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables first!")
        print("📝 Edit your .env file with your actual Supabase credentials")
        return False
    
    try:
        supabase_manager = create_supabase_manager()
        if not supabase_manager:
            print("❌ Failed to create Supabase manager")
            return False
        
        print("🔄 Populating Supabase with sample data...")
        
        # Check if branches already exist
        existing_branches = supabase_manager.get_all_branches()
        if not existing_branches:
            print("ℹ️ Note: Branches should be automatically created by database schema")
        else:
            print(f"✅ Found {len(existing_branches)} branches")
        
        # Sample products data
        sample_products = [
            {
                'sku': 'P001',
                'barcode': '1234567890123',
                'name': 'เสื้อยืดสีขาว',
                'description': 'เสื้อยืดคอตตอน 100% สีขาว',
                'category': 'เสื้อผ้า',
                'brand': 'Brand A',
                'unit': 'pieces',
                'cost_price': 150.00,
                'selling_price': 250.00,
                'reorder_level': 10,
                'max_stock_level': 100
            },
            {
                'sku': 'P002',
                'barcode': '1234567890124',
                'name': 'กางเกงยีนส์',
                'description': 'กางเกงยีนส์ผู้ชาย ขายาว',
                'category': 'เสื้อผ้า',
                'brand': 'Brand B',
                'unit': 'pieces',
                'cost_price': 300.00,
                'selling_price': 499.00,
                'reorder_level': 5,
                'max_stock_level': 50
            },
            {
                'sku': 'P003',
                'barcode': '1234567890125',
                'name': 'รองเท้าผ้าใบ',
                'description': 'รองเท้าผ้าใบสีดำ ไซส์ 42',
                'category': 'รองเท้า',
                'brand': 'Brand C',
                'unit': 'pairs',
                'cost_price': 800.00,
                'selling_price': 1200.00,
                'reorder_level': 3,
                'max_stock_level': 30
            },
            {
                'sku': 'P004',
                'barcode': '1234567890126',
                'name': 'กระเป๋าสะพาย',
                'description': 'กระเป๋าสะพายข้างหนัง PU',
                'category': 'กระเป๋า',
                'brand': 'Brand D',
                'unit': 'pieces',
                'cost_price': 200.00,
                'selling_price': 350.00,
                'reorder_level': 8,
                'max_stock_level': 40
            },
            {
                'sku': 'P005',
                'barcode': '1234567890127',
                'name': 'นาฬิกาข้อมือ',
                'description': 'นาฬิกาข้อมือดิจิตอล กันน้ำ',
                'category': 'อุปกรณ์เสริม',
                'brand': 'Brand E',
                'unit': 'pieces',
                'cost_price': 450.00,
                'selling_price': 699.00,
                'reorder_level': 5,
                'max_stock_level': 25
            }
        ]
        
        # Add sample products
        added_count = 0
        for product_data in sample_products:
            # Check if product already exists
            existing_product = supabase_manager.get_product_by_barcode(product_data['barcode'])
            if existing_product:
                print(f"⏭️  Product {product_data['name']} already exists")
                continue
            
            result = supabase_manager.add_product(product_data)
            if result:
                print(f"✅ Added product: {product_data['name']} (Barcode: {product_data['barcode']})")
                added_count += 1
            else:
                print(f"❌ Failed to add product: {product_data['name']}")
        
        print(f"\n🎉 Successfully added {added_count} new products to Supabase!")
        
        # Show summary
        all_products = supabase_manager.get_all_products()
        all_branches = supabase_manager.get_all_branches()
        
        print(f"📊 Total products in database: {len(all_products)}")
        print(f"📊 Total branches in database: {len(all_branches)}")
        
        if all_branches:
            print("\n📍 Available branches:")
            for branch in all_branches:
                print(f"  - {branch['name']} (Code: {branch['code']})")
        
        print("\n🎯 Your stock counting system is now ready!")
        print("   You can scan these barcodes to test:")
        for product in sample_products:
            print(f"   - {product['barcode']} → {product['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Starting Supabase data population...")
    success = populate_sample_data()
    
    if success:
        print("\n✅ Setup complete! Your stock counting app is ready to use.")
    else:
        print("\n❌ Setup failed. Please check your Supabase configuration.")