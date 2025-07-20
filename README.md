# 📱 Inventory Management System

ระบบจัดการสต๊อกและวิเคราะห์การขายสินค้าสำหรับธุรกิจขนาดเล็ก พัฒนาด้วย Flask, SQLite, และ HTML5

## ✨ คุณสมบัติหลัก

### 👥 ระบบผู้ใช้งาน
- **Admin** - เจ้าของกิจการ: ดูรายงาน, กรอกยอดขาย, จัดการระบบ
- **Staff** - พนักงาน: นับสต๊อกด้วยกล้องมือถือ, สแกนบาร์โค้ด

### 📱 การนับสต๊อก
- สแกนบาร์โค้ดด้วยกล้องมือถือ (html5-qrcode)
- ถ่ายภาพสินค้าขณะนับ
- รองรับหลายสาขา
- อัปโหลดภาพไป Google Drive อัตโนมัติ

### 📊 รายงานวิเคราะห์
- **รายงานสรุป**: วิเคราะห์สต๊อกเทียบกับยอดขาย
- **รายงานสินค้าไม่เคลื่อนไหว**: สินค้าที่ไม่มีการขาย 30 วัน
- คำแนะนำการสั่งซื้อสินค้า
- ส่งออกข้อมูลเป็น CSV

### 🔄 ซิงค์ยอดขาย
- อิมพอร์ตจาก Google Sheets
- อิมพอร์ตจากไฟล์ CSV
- ตรวจสอบความถูกต้องของข้อมูล

## 🚀 การติดตั้งและใช้งาน

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. ตั้งค่าระบบ
```bash
python setup.py
```

### 3. รันแอปพลิเคชัน
```bash
python app.py
```

### 4. เปิดเบราว์เซอร์
```
http://localhost:5000
```

## 👤 ข้อมูลผู้ใช้ทดสอบ

| บบทบาท | ชื่อผู้ใช้ | รหัสผ่าน |
|---------|-----------|----------|
| Admin   | admin     | admin123 |
| Staff   | staff     | staff123 |

## 📦 ข้อมูลสินค้าทดสอบ

| บาร์โค้ด        | ชื่อสินค้า |
|----------------|-----------|
| 1234567890123  | น้ำดื่ม 600ml |
| 2345678901234  | ข้าวสาร 5kg |
| 3456789012345  | นมถั่วเหลือง 250ml |
| 4567890123456  | ขนมปังแผ่น |
| 5678901234567  | ไข่ไก่ 10 ฟอง |

## 📁 โครงสร้างโปรเจค

```
inventory-management/
├── app.py                 # Flask application หลัก
├── setup.py              # Script ตั้งค่าระบบ
├── sync_sales.py         # Script ซิงค์ยอดขาย
├── upload_to_drive.py    # Google Drive API integration
├── requirements.txt      # Python dependencies
├── README.md            # เอกสารการใช้งาน
├── templates/           # HTML templates
│   ├── login.html       # หน้าล็อกอิน
│   ├── index.html       # หน้านับสต๊อก (staff)
│   ├── summary.html     # หน้ารายงานสรุป (admin)
│   └── slow.html        # หน้ารายงานสินค้าไม่เคลื่อนไหว (admin)
├── static/              # CSS, JS, images
│   └── barcode.js       # JavaScript สำหรับสแกนบาร์โค้ด
├── uploads/             # ไฟล์อัปโหลด (mock mode)
└── inventory.db         # SQLite database
```

## 🗄️ โครงสร้างฐานข้อมูล

### users
- `id` (Primary Key)
- `username` (Unique)
- `password` (SHA256 hash)
- `role` (admin/staff)

### products
- `barcode` (Primary Key)
- `product_name`

### stock_log
- `id` (Primary Key)
- `barcode` (Foreign Key)
- `product_name`
- `quantity`
- `branch`
- `timestamp`
- `image_url`
- `created_by_user_id` (Foreign Key)

### sales
- `id` (Primary Key)
- `barcode` (Foreign Key)
- `quantity_sold`
- `date`

## 📊 การซิงค์ยอดขาย

### สร้างไฟล์ CSV ตัวอย่าง
```bash
python sync_sales.py --sample
```

### ซิงค์จาก CSV
```bash
python sync_sales.py --csv sample_sales.csv
```

### ซิงค์จาก Google Sheets
```bash
python sync_sales.py --sheet-id YOUR_GOOGLE_SHEET_ID
```

### ตัวอย่างรูปแบบ CSV
```csv
barcode,quantity_sold,date
1234567890123,10,2024-01-15
2345678901234,5,2024-01-16
3456789012345,15,2024-01-17
```

## 🖼️ การตั้งค่า Google Drive API

### 1. สร้าง Google Cloud Project
1. ไปที่ [Google Cloud Console](https://console.cloud.google.com/)
2. สร้างโปรเจคใหม่
3. เปิดใช้งาน Google Drive API

### 2. สร้าง Credentials
**OAuth 2.0 (สำหรับ Desktop App):**
1. ไปที่ Credentials > Create Credentials > OAuth client ID
2. เลือก Desktop application
3. ดาวน์โหลด `credentials.json`

**Service Account (สำหรับ Server):**
1. ไปที่ Credentials > Create Credentials > Service account
2. สร้าง Key และดาวน์โหลด `service_account.json`

### 3. วางไฟล์ Credentials
```bash
# สำหรับ OAuth 2.0
cp credentials.json ./

# สำหรับ Service Account
cp service_account.json ./
```

### 4. ติดตั้ง Google API Libraries
```bash
pip install google-api-python-client google-auth-oauthlib
```

## 🔧 การปรับแต่ง

### เพิ่มสินค้าใหม่
```python
# เพิ่มใน app.py ส่วน init_db()
sample_products = [
    ('YOUR_BARCODE', 'ชื่อสินค้า'),
    # ...
]
```

### เพิ่มสาขาใหม่
แก้ไข `templates/index.html` ส่วน select branch:
```html
<select id="branch" name="branch" required>
    <option value="">เลือกสาขา</option>
    <option value="สาขาหลัก">สาขาหลัก</option>
    <option value="สาขา 1">สาขา 1</option>
    <option value="สาขา 2">สาขา 2</option>
    <option value="สาขาใหม่">สาขาใหม่</option>
</select>
```

### เปลี่ยน Secret Key
แก้ไข `app.py`:
```python
app.secret_key = 'your-strong-secret-key-here'
```

## 📱 การใช้งานบนมือถือ

### สแกนบาร์โค้ด
1. เปิดเบราว์เซอร์บนมือถือ
2. ล็อกอินด้วยบัญชี Staff
3. กดปุ่ม "เปิดกล้อง" ในส่วนสแกนบาร์โค้ด
4. นำกล้องส่องไปที่บาร์โค้ด

### ถ่ายภาพสินค้า
1. กดปุ่ม "เปิดกล้อง" ในส่วนถ่ายภาพ
2. กดปุ่ม "ถ่ายภาพ" เมื่อเฟรมเหมาะสม
3. กดปุ่ม "ถ่ายใหม่" หากต้องการถ่ายใหม่

## 🔐 ความปลอดภัย

### การแฮชรหัสผ่าน
ใช้ SHA256 สำหรับแฮชรหัสผ่าน:
```python
import hashlib
password_hash = hashlib.sha256(password.encode()).hexdigest()
```

### Session Management
ใช้ Flask session สำหรับจัดการการล็อกอิน

### Role-based Access Control
- `@staff_required` - เฉพาะ Staff
- `@admin_required` - เฉพาะ Admin

## 🐛 การแก้ไขปัญหา

### กล้องไม่ทำงาน
1. ตรวจสอบการอนุญาตเข้าถึงกล้อง
2. ใช้ HTTPS หรือ localhost
3. ลองเบราว์เซอร์อื่น

### Google Drive อัปโหลดไม่ได้
1. ตรวจสอบไฟล์ credentials
2. ตรวจสอบ API quota
3. ดูล็อกใน console

### ฐานข้อมูลขัดข้อง
```bash
# ลบฐานข้อมูลและสร้างใหม่
rm inventory.db
python setup.py
```

## 🤝 การพัฒนาต่อ

### เพิ่มฟีเจอร์ใหม่
1. Fork repository
2. สร้าง branch ใหม่
3. เพิ่มฟีเจอร์
4. ทดสอบ
5. Create pull request

### ไอเดียการพัฒนา
- [ ] Export รายงานเป็น PDF
- [ ] แจ้งเตือน Line/Discord
- [ ] ระบบสั่งซื้อสินค้าอัตโนมัติ
- [ ] Dashboard แบบ Real-time
- [ ] Multi-language support
- [ ] PWA (Progressive Web App)

## 📝 License

MIT License - ใช้งานได้อย่างอิสระ

## 👨‍💻 ผู้พัฒนา

พัฒนาโดย Claude AI Assistant
- ⚡ Flask + SQLite + HTML5
- 📱 Mobile-first design
- 🔒 Secure authentication
- 📊 Data analytics# stock-check-web
# stock-management
