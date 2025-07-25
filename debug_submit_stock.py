#!/usr/bin/env python3
"""
Debug submit_stock by checking if product exists
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_manager import create_supabase_manager
from sheets_manager import create_sheets_manager

def debug_product_lookup():
    """Debug product lookup"""
    
    # Test Supabase
    print("🔍 Testing Supabase product lookup...")
    try:
        supabase_manager = create_supabase_manager()
        if supabase_manager:
            product = supabase_manager.get_product_by_barcode('123456789')
            print(f"Supabase product result: {product}")
            
            # Check branches
            branches = supabase_manager.get_all_branches()
            print(f"Available branches: {branches}")
            
            # Try to find branch
            branch = supabase_manager.get_branch_by_name('CITY')
            print(f"Branch CITY result: {branch}")
        else:
            print("❌ Supabase manager not available")
    except Exception as e:
        print(f"❌ Supabase error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Google Sheets  
    print("📊 Testing Google Sheets product lookup...")
    try:
        sheets_manager = create_sheets_manager()
        if sheets_manager:
            PRODUCT_SHEET_ID = os.environ.get('PRODUCT_SHEET_ID', '17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM')
            product = sheets_manager.get_product_by_barcode('123456789', PRODUCT_SHEET_ID)
            print(f"Sheets product result: {product}")
            
            # Get all products to see what's available
            all_products = sheets_manager.get_all_products(PRODUCT_SHEET_ID)
            print(f"Total products in sheet: {len(all_products) if all_products else 0}")
            if all_products and len(all_products) > 0:
                print(f"First product example: {all_products[0]}")
        else:
            print("❌ Sheets manager not available")
    except Exception as e:
        print(f"❌ Sheets error: {e}")

if __name__ == "__main__":
    debug_product_lookup()