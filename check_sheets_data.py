#!/usr/bin/env python3
"""
ตรวจสอบข้อมูลจริงใน Google Sheets
"""

from sheets_manager import create_sheets_manager

PRODUCT_SHEET_ID = "17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM"

def main():
    print("🔍 ตรวจสอบข้อมูลใน Google Sheets...")
    
    sheets_manager = create_sheets_manager()
    if not sheets_manager:
        print("❌ ไม่สามารถเชื่อมต่อ Google Sheets ได้")
        return
    
    try:
        # Check raw data in first 10 rows
        print("📋 ข้อมูล 10 แถวแรก (A1:Z10):")
        
        result = sheets_manager.sheets_service.spreadsheets().values().get(
            spreadsheetId=PRODUCT_SHEET_ID,
            range='A1:Z10'
        ).execute()
        
        values = result.get('values', [])
        
        for i, row in enumerate(values):
            print(f"Row {i+1}: {row}")
        
        print("\n" + "="*50)
        
        # Check what columns D and E contain
        print("🔍 ตรวจสอบ Column D และ E (บาร์โค้ดและชื่อสินค้า):")
        
        result_de = sheets_manager.sheets_service.spreadsheets().values().get(
            spreadsheetId=PRODUCT_SHEET_ID,
            range='D1:E20'
        ).execute()
        
        values_de = result_de.get('values', [])
        
        for i, row in enumerate(values_de):
            if len(row) >= 2:
                barcode = row[0] if len(row) > 0 else ''
                name = row[1] if len(row) > 1 else ''
                print(f"Row {i+1}: Barcode='{barcode}', Name='{name}'")
            elif len(row) == 1:
                print(f"Row {i+1}: Only column D='{row[0]}'")
            else:
                print(f"Row {i+1}: Empty row")
        
        print("\n" + "="*50)
        
        # Test the current method
        print("🧪 ทดสอบ get_all_products() ปัจจุบัน:")
        products = sheets_manager.get_all_products(PRODUCT_SHEET_ID)
        print(f"📦 พบสินค้า {len(products)} รายการ")
        
        for i, product in enumerate(products[:5]):
            print(f"Product {i+1}: {product}")
            if i >= 4:  # Show only first 5
                break
                
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()