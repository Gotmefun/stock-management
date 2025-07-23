# 📁 คำแนะนำการตั้งค่า OAuth2 Google Drive

## ✅ สถานะปัจจุบัน
- ✅ ระบบ OAuth2 ถูกตั้งค่าเรียบร้อยแล้ว
- ✅ credentials.json พร้อมใช้งาน
- ✅ ระบบทำงานร่วมกับ Supabase
- ✅ ลบ Google Apps Script dependency แล้ว
- ❌ **ยังไม่ได้ authorize กับ Google Drive**

## 🚀 วิธีการ authorize OAuth2

### ขั้นตอนที่ 1: เปิด Flask Application
```bash
cd "/mnt/e/My App/AAAAAAAAAA"
python3 app.py
```

### ขั้นตอนที่ 2: เข้าสู่ระบบ
1. เปิดเบราว์เซอร์ไปที่: `http://127.0.0.1:8080`
2. Login ด้วย username/password

### ขั้นตอนที่ 3: Authorize Google Drive
1. ไปที่ URL: `http://127.0.0.1:8080/authorize_drive`
2. ระบบจะ redirect ไปหน้า Google OAuth
3. เลือก Google Account ที่ต้องการ
4. อนุญาตการเข้าถึง Google Drive
5. ระบบจะ redirect กลับมาหน้า stock counting

### ขั้นตอนที่ 4: ตรวจสอบการทำงาน
```bash
python3 test_oauth2_upload.py
```

## 📁 โฟลเดอร์ที่จะถูกสร้าง
```
My Drive/
└── Check Stock Project/
    └── Pic Stock Counting/
        ├── stock_123456_20250723_143022.jpg
        ├── stock_789012_20250723_143105.jpg
        └── ...
```

## 🔄 การทำงานของระบบ

### การบันทึกภาพ:
1. **OAuth2 authorized** → อัปโหลดไป Google Drive
2. **OAuth2 ไม่ authorized** → บันทึกในเครื่องเซิร์ฟเวอร์ (uploads/)

### การบันทึกข้อมูล:
1. **Supabase** (หลัก) → บันทึกข้อมูลและ URL ภาพ
2. **Google Sheets** (สำรอง) → fallback หาก Supabase ล้มเหลว

## 🛠️ ไฟล์ที่ได้รับการปรับปรุง
- `templates/index.html` - ลบ UI ที่ไม่จำเป็น
- `static/barcode.js` - ลบ functions ที่ไม่ใช้
- `app.py` - ปรับปรุงให้ใช้เฉพาะ OAuth2 Drive
- `submit_stock()` - ลำดับความสำคัญ: OAuth2 → Local Storage

## 📝 หมายเหตุ
- ระบบจะสร้างโฟลเดอร์อัตโนมัติหากยังไม่มี
- ภาพจะมีชื่อในรูปแบบ: `stock_{barcode}_{timestamp}.jpg`
- OAuth2 token จะถูกบันทึกในไฟล์ `drive_token.pickle`
- หากต้องการ re-authorize ให้ลบไฟล์ `drive_token.pickle` และทำใหม่

## 🎯 การใช้งานจริง
หลังจาก authorize แล้ว:
1. เข้าหน้านับสต๊อก
2. สแกนบาร์โค้ด
3. ถ่ายภาพสินค้า
4. กรอกข้อมูลและบันทึก
5. ภาพจะไปเก็บใน Google Drive อัตโนมัติ