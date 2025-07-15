#!/usr/bin/env python3
"""
Sales Synchronization Script
Syncs sales data from Google Sheets (CSV) to SQLite database
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime, date
import sys
import argparse

DATABASE = 'inventory.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def sync_from_csv(csv_file_path):
    """Sync sales data from CSV file"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        
        # Validate required columns
        required_columns = ['barcode', 'quantity_sold', 'date']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Clean and validate data
        df['barcode'] = df['barcode'].astype(str).str.strip()
        df['quantity_sold'] = pd.to_numeric(df['quantity_sold'], errors='coerce')
        
        # Parse dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
        
        # Remove rows with invalid data
        df = df.dropna(subset=['barcode', 'quantity_sold', 'date'])
        df = df[df['quantity_sold'] > 0]
        
        # Connect to database
        with get_db() as conn:
            # Clear existing sales data (optional - depends on your sync strategy)
            # conn.execute('DELETE FROM sales')
            
            # Insert new sales data
            inserted_count = 0
            for _, row in df.iterrows():
                try:
                    conn.execute('''
                        INSERT INTO sales (barcode, quantity_sold, date)
                        VALUES (?, ?, ?)
                    ''', (row['barcode'], int(row['quantity_sold']), row['date']))
                    inserted_count += 1
                except sqlite3.IntegrityError as e:
                    print(f"Warning: Skipping duplicate or invalid record: {row['barcode']} - {e}")
                    continue
            
            print(f"Successfully synced {inserted_count} sales records from {csv_file_path}")
            
    except Exception as e:
        print(f"Error syncing sales data: {e}")
        return False
    
    return True

def sync_from_google_sheets(sheet_id, sheet_name="Sales"):
    """Sync sales data from Google Sheets"""
    try:
        # Construct Google Sheets CSV export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        
        # Read directly from Google Sheets
        df = pd.read_csv(csv_url)
        
        # Process the data similar to CSV sync
        required_columns = ['barcode', 'quantity_sold', 'date']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        df['barcode'] = df['barcode'].astype(str).str.strip()
        df['quantity_sold'] = pd.to_numeric(df['quantity_sold'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
        
        df = df.dropna(subset=['barcode', 'quantity_sold', 'date'])
        df = df[df['quantity_sold'] > 0]
        
        with get_db() as conn:
            inserted_count = 0
            for _, row in df.iterrows():
                try:
                    conn.execute('''
                        INSERT INTO sales (barcode, quantity_sold, date)
                        VALUES (?, ?, ?)
                    ''', (row['barcode'], int(row['quantity_sold']), row['date']))
                    inserted_count += 1
                except sqlite3.IntegrityError as e:
                    print(f"Warning: Skipping duplicate or invalid record: {row['barcode']} - {e}")
                    continue
            
            print(f"Successfully synced {inserted_count} sales records from Google Sheets")
            
    except Exception as e:
        print(f"Error syncing from Google Sheets: {e}")
        return False
    
    return True

def validate_products():
    """Validate that all sales have corresponding products"""
    with get_db() as conn:
        # Find sales records without corresponding products
        orphan_sales = conn.execute('''
            SELECT DISTINCT s.barcode, COUNT(*) as count
            FROM sales s
            LEFT JOIN products p ON s.barcode = p.barcode
            WHERE p.barcode IS NULL
            GROUP BY s.barcode
        ''').fetchall()
        
        if orphan_sales:
            print("Warning: Found sales records without corresponding products:")
            for sale in orphan_sales:
                print(f"  Barcode: {sale['barcode']} ({sale['count']} sales records)")
            
            # Optionally create missing products
            response = input("Create missing products? (y/n): ").strip().lower()
            if response == 'y':
                for sale in orphan_sales:
                    product_name = input(f"Enter product name for barcode {sale['barcode']}: ").strip()
                    if product_name:
                        conn.execute('''
                            INSERT OR IGNORE INTO products (barcode, product_name)
                            VALUES (?, ?)
                        ''', (sale['barcode'], product_name))
                        print(f"Created product: {product_name}")

def generate_sample_csv():
    """Generate sample CSV file for testing"""
    sample_data = {
        'barcode': ['1234567890123', '2345678901234', '3456789012345', '4567890123456', '5678901234567'],
        'quantity_sold': [10, 5, 15, 8, 12],
        'date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('sample_sales.csv', index=False)
    print("Generated sample_sales.csv")

def main():
    parser = argparse.ArgumentParser(description='Sync sales data to inventory database')
    parser.add_argument('--csv', type=str, help='Path to CSV file')
    parser.add_argument('--sheet-id', type=str, help='Google Sheets document ID')
    parser.add_argument('--sheet-name', type=str, default='Sales', help='Google Sheets sheet name')
    parser.add_argument('--validate', action='store_true', help='Validate products after sync')
    parser.add_argument('--sample', action='store_true', help='Generate sample CSV file')
    parser.add_argument('--clear', action='store_true', help='Clear existing sales data before sync')
    
    args = parser.parse_args()
    
    if args.sample:
        generate_sample_csv()
        return
    
    if args.clear:
        with get_db() as conn:
            conn.execute('DELETE FROM sales')
            print("Cleared existing sales data")
    
    success = False
    
    if args.csv:
        if not os.path.exists(args.csv):
            print(f"Error: CSV file not found: {args.csv}")
            return
        success = sync_from_csv(args.csv)
    
    elif args.sheet_id:
        success = sync_from_google_sheets(args.sheet_id, args.sheet_name)
    
    else:
        print("Error: Please specify either --csv or --sheet-id")
        parser.print_help()
        return
    
    if success and args.validate:
        validate_products()

if __name__ == '__main__':
    main()