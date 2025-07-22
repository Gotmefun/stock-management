# 🚀 Quick Start - ใช้งานหน้านับสต๊อกทันที

## วิธีใช้งานด่วน (ใช้ Google Sheets)

ตอนนี้ระบบสามารถใช้งานได้ทันทีด้วย Google Sheets ที่มีอยู่แล้ว:

### 1. เริ่มใช้งาน
```bash
python3 app.py
```

### 2. เข้าสู่ระบบ
- ไปที่: http://127.0.0.1:8080
- Username: `staff` Password: `staff123` (สำหรับพนักงาน)
- Username: `admin` Password: `Teeomega2014` (สำหรับแอดมิน)

### 3. ทดสอบการนับสต๊อก
หน้านับสต๊อกจะค้นหาสินค้าจากข้อมูลใน Google Sheets:
- **Product Master Sheet**: คอลัมน์ D (Barcode) และ E (Product Name)
- **Stock Counting Data**: บันทึกผลการนับ

### 4. บาร์โค้ดทดสอบ
สินค้าที่มีในระบบปัจจุบัน (จาก Google Sheets):
- ดูได้ที่ Google Sheets Product Master
- หรือเพิ่มสินค้าใหม่ในคอลัมน์ D และ E

---

## 🔧 อัพเกรดเป็น Supabase (แนะนำ)

สำหรับประสิทธิภาพและฟีเจอร์ครบครัน:

### Step 1: ตั้งค่า Supabase Project
1. ไปที่ [supabase.com](https://supabase.com)
2. สร้างโปรเจคใหม่: "Smart Inventory Management"  
3. คัดลอก Project URL และ anon key

### Step 2: ตั้งค่า Environment Variables
```bash
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIs..."
```

### Step 3: สร้างฐานข้อมูล
1. ไปที่ SQL Editor ใน Supabase
2. คัดลอก + รันไฟล์: `database_schema.sql`

### Step 4: สร้างสินค้าตัวอย่าง
```bash
python3 create_sample_products.py
```

### Step 5: รีสตาร์ทแอป
```bash
python3 app.py
```

---

## 📱 การใช้งานหน้านับสต๊อก

### ฟีเจอร์ที่ใช้ได้:
1. **สแกนบาร์โค้ด** - กล้องสแกนบาร์โค้ด
2. **ค้นหาสินค้า** - พิมพ์บาร์โค้ดได้
3. **ถ่ายรูปสินค้า** - อัพโหลดรูปไปยัง Google Drive
4. **บันทึกผลการนับ** - บันทึกลง Google Sheets หรือ Supabase

### ฟิลด์ข้อมูล:
- **ชื่อผู้ตรวจนับ**: ระบุชื่อผู้นับ
- **บาร์โค้ด**: สแกนหรือพิมพ์
- **จำนวนคงเหลือ**: ผลการนับจริง
- **สาขา**: เลือกสาขาที่นับ
- **รูปภาพ**: ถ่ายรูปสินค้า (ทางเลือก)

---

## 🔍 การแก้ไขปัญหา

### ปัญหา: "Product not found"
**วิธีแก้:**
1. ตรวจสอบว่ามีสินค้าใน Google Sheets หรือไม่
2. ตรวจสอบบาร์โค้ดใน column D ของ Product Master Sheet
3. ถ้าใช้ Supabase ให้ตรวจสอบว่ามีข้อมูลในตาราง products

### ปัญหา: "Supabase manager not available"
**วิธีแก้:**
```bash
export SUPABASE_URL="your-url"
export SUPABASE_ANON_KEY="your-key"
```

### ปัญหา: การอัพโหลดรูป
**วิธีแก้:**
1. ตรวจสอบ Google Apps Script URL
2. ตรวจสอบ Google Drive API credentials

---

## 📊 ฟีเจอร์พิเศษ (เมื่อใช้ Supabase)

### Admin Dashboard (/dashboard)
- 📈 กราฟยอดขายรายวัน
- 📦 สถิติสินค้าและสต๊อก  
- ⚠️ การแจ้งเตือนสต๊อกต่ำ
- 🏪 กรองข้อมูลตามสาขา

### Smart Alerts
- สินค้าใกล้หมด
- ความแตกต่างการนับสต๊อก
- สินค้าขายดี/ขายไม่ดี

### Analytics
- ยอดขายแยกตามสาขา
- ประสิทธิภาพสินค้า
- ประวัติการเคลื่อนไหวสต๊อก

---

## 🎯 บาร์โค้ดทดสอบ (เมื่อใช้ Supabase)

สินค้าตัวอย่างที่สร้างโดย `create_sample_products.py`:

- `1234567890123` - นมสด เมจิ 1000 มล.
- `8851019991234` - ข้าวโอ๊ต เควกเกอร์ 500 กรัม  
- `8850999999999` - น้ำแร่ สิงห์ 600 มล.
- `1111111111111` - ชาเขียว โออิชิ 500 มล.
- `2222222222222` - บะหมี่กึ่งสำเร็จรูป มาม่า

---

## 🚀 Production Deployment

ดูรายละเอียดได้ที่:
- `SUPABASE_SETUP.md` - คู่มือ Supabase แบบละเอียด
- `HOSTING_CHECKLIST.md` - Deploy ขึ้น Render.com