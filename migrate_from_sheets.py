#!/usr/bin/env python3
"""
Migration script to transfer data from Google Sheets to Supabase database
Phase 1: Smart Inventory Management System
"""

import os
import sys
import pandas as pd
from datetime import datetime
import hashlib
from supabase import create_client, Client
from sheets_manager import create_sheets_manager

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY', '')

# Google Sheets IDs
PRODUCT_SHEET_ID = os.environ.get('PRODUCT_SHEET_ID', '17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM')
STOCK_SHEET_ID = os.environ.get('STOCK_SHEET_ID', '1OaEqOS7I0_hN2Q1nc4isqPXXdjp7_i7ZAPJFhUr5X7k')

def create_supabase_client():
    """Create Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        sys.exit(1)
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def migrate_products(sheets_manager, supabase: Client):
    """Migrate products from Google Sheets to Supabase"""
    print("Migrating products...")
    
    try:
        # Get products from Google Sheets
        products_data = sheets_manager.get_all_products(PRODUCT_SHEET_ID)
        
        if not products_data:
            print("No products found in Google Sheets")
            return
        
        # Transform data for Supabase
        products_to_insert = []
        for product in products_data:
            product_record = {
                'sku': product.get('barcode', ''),  # Use barcode as SKU for now
                'barcode': product.get('barcode', ''),
                'name': product.get('name', ''),
                'description': f"Migrated from Google Sheets - {product.get('name', '')}",
                'category': 'General',  # Default category
                'is_active': True
            }
            products_to_insert.append(product_record)
        
        # Insert into Supabase
        result = supabase.table('products').insert(products_to_insert).execute()
        print(f"Successfully migrated {len(products_to_insert)} products")
        
        return result.data
        
    except Exception as e:
        print(f"Error migrating products: {e}")
        return None

def get_branch_mapping(supabase: Client):
    """Get branch ID mapping"""
    result = supabase.table('branches').select('id, name').execute()
    branch_map = {}
    for branch in result.data:
        branch_map[branch['name']] = branch['id']
    return branch_map

def get_product_mapping(supabase: Client):
    """Get product ID mapping"""
    result = supabase.table('products').select('id, barcode').execute()
    product_map = {}
    for product in result.data:
        if product['barcode']:
            product_map[product['barcode']] = product['id']
    return product_map

def get_user_mapping(supabase: Client):
    """Get user ID mapping"""
    result = supabase.table('users').select('id, username').execute()
    user_map = {}
    for user in result.data:
        user_map[user['username']] = user['id']
    return user_map

def migrate_stock_counts(sheets_manager, supabase: Client):
    """Migrate stock counting data from Google Sheets to Supabase"""
    print("Migrating stock counts...")
    
    try:
        # Get mappings
        branch_map = get_branch_mapping(supabase)
        product_map = get_product_mapping(supabase)
        user_map = get_user_mapping(supabase)
        
        print(f"Found {len(branch_map)} branches, {len(product_map)} products, {len(user_map)} users")
        
        # Get stock counting data from Google Sheets
        stock_data = sheets_manager.get_stock_summary(STOCK_SHEET_ID, PRODUCT_SHEET_ID)
        
        if not stock_data:
            print("No stock counting data found in Google Sheets")
            return
        
        # Transform data for Supabase
        stock_counts_to_insert = []
        inventory_to_upsert = []
        
        for record in stock_data:
            # Get IDs from mappings
            product_id = product_map.get(record.get('barcode'))
            branch_name = record.get('branch', 'สาขาหลัก')
            branch_id = branch_map.get(branch_name)
            
            if not product_id or not branch_id:
                print(f"Skipping record - Product ID: {product_id}, Branch ID: {branch_id}")
                continue
            
            # Stock count record
            stock_count_record = {
                'product_id': product_id,
                'branch_id': branch_id,
                'counted_quantity': int(record.get('quantity', 0)),
                'counter_name': record.get('counter_name', 'Unknown'),
                'counted_by': user_map.get('staff'),  # Default to staff user
                'image_url': record.get('image_url', ''),
                'counted_at': record.get('timestamp', datetime.now().isoformat())
            }
            stock_counts_to_insert.append(stock_count_record)
            
            # Update inventory
            inventory_record = {
                'product_id': product_id,
                'branch_id': branch_id,
                'quantity': int(record.get('quantity', 0)),
                'last_counted_at': record.get('timestamp', datetime.now().isoformat()),
                'last_counted_by': user_map.get('staff')
            }
            inventory_to_upsert.append(inventory_record)
        
        # Insert stock counts
        if stock_counts_to_insert:
            result = supabase.table('stock_counts').insert(stock_counts_to_insert).execute()
            print(f"Successfully migrated {len(stock_counts_to_insert)} stock count records")
        
        # Upsert inventory
        if inventory_to_upsert:
            for inv_record in inventory_to_upsert:
                try:
                    # Try to update existing record, if not exists, insert
                    existing = supabase.table('inventory').select('id').eq('product_id', inv_record['product_id']).eq('branch_id', inv_record['branch_id']).execute()
                    
                    if existing.data:
                        # Update existing
                        supabase.table('inventory').update(inv_record).eq('product_id', inv_record['product_id']).eq('branch_id', inv_record['branch_id']).execute()
                    else:
                        # Insert new
                        supabase.table('inventory').insert(inv_record).execute()
                except Exception as e:
                    print(f"Error upserting inventory record: {e}")
            
            print(f"Successfully updated {len(inventory_to_upsert)} inventory records")
        
    except Exception as e:
        print(f"Error migrating stock counts: {e}")

def create_sample_sales_data(supabase: Client):
    """Create sample sales data for analytics demonstration"""
    print("Creating sample sales data...")
    
    try:
        # Get some products and branches for sample data
        products = supabase.table('products').select('id, name, selling_price').limit(5).execute()
        branches = supabase.table('branches').select('id, name').execute()
        users = supabase.table('users').select('id').eq('role', 'admin').execute()
        
        if not products.data or not branches.data or not users.data:
            print("Insufficient data for sample creation")
            return
        
        # Create sample sales for the last 30 days
        import random
        from datetime import timedelta
        
        sales_to_insert = []
        sale_items_to_insert = []
        
        cashier_id = users.data[0]['id']
        
        for day in range(30):
            sale_date = datetime.now() - timedelta(days=day)
            
            # Create 1-3 sales per day
            for sale_num in range(random.randint(1, 3)):
                transaction_number = f"S{sale_date.strftime('%Y%m%d')}{sale_num:03d}"
                branch_id = random.choice(branches.data)['id']
                
                # Create sale
                sale_record = {
                    'transaction_number': transaction_number,
                    'transaction_date': sale_date.isoformat(),
                    'branch_id': branch_id,
                    'customer_name': f"Customer {random.randint(1, 100)}",
                    'subtotal': 0,
                    'total_amount': 0,
                    'payment_method': random.choice(['cash', 'card', 'transfer']),
                    'cashier_id': cashier_id,
                    'status': 'completed'
                }
                
                # Add random products to this sale
                num_items = random.randint(1, 4)
                sale_total = 0
                
                for _ in range(num_items):
                    product = random.choice(products.data)
                    quantity = random.randint(1, 5)
                    unit_price = float(product.get('selling_price', 100) or 100)
                    total_price = quantity * unit_price
                    sale_total += total_price
                    
                    sale_item = {
                        'transaction_number': transaction_number,  # We'll update with sale_id later
                        'product_id': product['id'],
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_price': total_price
                    }
                    sale_items_to_insert.append(sale_item)
                
                sale_record['subtotal'] = sale_total
                sale_record['total_amount'] = sale_total
                sales_to_insert.append(sale_record)
        
        # Insert sales
        sales_result = supabase.table('sales').insert(sales_to_insert).execute()
        print(f"Created {len(sales_result.data)} sample sales")
        
        # Update sale items with actual sale IDs
        sales_map = {sale['transaction_number']: sale['id'] for sale in sales_result.data}
        
        for item in sale_items_to_insert:
            item['sale_id'] = sales_map[item['transaction_number']]
            del item['transaction_number']
        
        # Insert sale items
        items_result = supabase.table('sale_items').insert(sale_items_to_insert).execute()
        print(f"Created {len(items_result.data)} sample sale items")
        
    except Exception as e:
        print(f"Error creating sample sales data: {e}")

def main():
    """Main migration function"""
    print("Starting migration from Google Sheets to Supabase...")
    
    # Initialize services
    supabase = create_supabase_client()
    sheets_manager = create_sheets_manager()
    
    if not sheets_manager:
        print("Error: Could not initialize Google Sheets manager")
        sys.exit(1)
    
    # Run migrations
    print("\n1. Migrating products...")
    products = migrate_products(sheets_manager, supabase)
    
    print("\n2. Migrating stock counting data...")
    migrate_stock_counts(sheets_manager, supabase)
    
    print("\n3. Creating sample sales data for analytics...")
    create_sample_sales_data(supabase)
    
    print("\nMigration completed successfully!")
    print("Your Smart Inventory Management System database is now ready.")

if __name__ == "__main__":
    main()