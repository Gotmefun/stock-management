# Project Structure Analysis - Inventory Management System

## 📋 โครงการระบบจัดการสินค้าคงคลัง

### 🏗️ สถาปัตยกรรมโครงการ

ระบบจัดการสินค้าคงคลังที่พัฒนาด้วย **Flask Framework** สำหรับธุรกิจขนาดเล็กในประเทศไทย

**เทคโนโลยีหลัก:**
- **Backend**: Python Flask + SQLite Database
- **Frontend**: HTML5 + JavaScript (Mobile-first)
- **Integration**: Google Drive API สำหรับจัดเก็บรูปภาพ
- **Mobile Support**: Camera + Barcode Scanning
- **Data Sync**: CSV และ Google Sheets

---

## 📁 โครงสร้างไฟล์และโฟลเดอร์

```
/mnt/e/My App/AAAAAAAAAA/
├── 🔧 Core Application Files
│   ├── app.py                    # แอปพลิเคชันหลัก Flask (332 บรรทัด)
│   ├── app_simple.py            # เวอร์ชันแบบง่าย
│   ├── run.py                   # ตัวรันแอปพร้อมตรวจสอบ dependencies
│   └── setup.py                 # สคริปต์ตั้งค่าและเริ่มต้น
│
├── 🗄️ Database Management
│   ├── init_db.py               # สร้าง schema และข้อมูลตัวอย่าง
│   ├── inventory.db             # ไฟล์ฐานข้อมูล SQLite
│   └── sync_sales.py            # ซิงค์ข้อมูลยอดขายจาก CSV/Sheets
│
├── 🎨 Templates (Frontend)
│   └── templates/
│       ├── index.html           # หน้าจอนับสต็อกสำหรับพนักงาน
│       ├── login.html           # หน้าล็อกอิน
│       ├── summary.html         # แดชบอร์ดผู้ดูแลระบบ
│       └── slow.html            # รายงานสินค้าขายช้า
│
├── 🎯 Static Assets
│   └── static/
│       ├── barcode.js           # JavaScript สำหรับสแกนบาร์โค้ด
│       └── favicon.ico          # ไอคอนเว็บไซต์
│
├── 🔗 Integration & Uploads
│   ├── upload_to_drive.py       # การเชื่อมต่อ Google Drive API
│   ├── uploads/                 # จัดเก็บรูปภาพในเครื่อง (สำรอง)
│   ├── credentials.json         # ข้อมูลรับรอง Google API
│   └── credentials.json.example # แม่แบบข้อมูลรับรอง
│
├── ⚙️ Configuration & Deployment
│   ├── requirements.txt         # รายการ Python dependencies
│   ├── gunicorn_config.py       # การตั้งค่าเซิร์ฟเวอร์ production
│   ├── start_production.sh      # สคริปต์เริ่มต้น production
│   └── .env.example            # แม่แบบตัวแปร environment
│
├── 📊 Sample Data
│   ├── sample_sales.csv         # ข้อมูลยอดขายตัวอย่าง
│   └── demo.html               # ไฟล์สาธิต
│
├── 📂 Directories
│   ├── backups/                 # โฟลเดอร์สำรองข้อมูล
│   ├── logs/                    # บันทึกการทำงานของระบบ
│   └── venv/                    # Python virtual environment
│
└── 📚 Documentation
    ├── README.md                # คู่มือภาษาไทยฉบับสมบูรณ์
    ├── PROJECT_STATUS.md        # สถานะความสำเร็จของโครงการ
    └── Project-structure.md     # เอกสารนี้
```

---

## ⚡ ฟังก์ชันหลักและคุณสมบัติ

### 👥 การจัดการผู้ใช้และการเข้าสู่ระบบ
- **ระบบบทบาท**: Admin และ Staff
- **ความปลอดภัย**: เข้ารหัสรหัสผ่านด้วย SHA256
- **จัดการ Session**: ใช้ Flask session
- **ป้องกันเส้นทาง**: Decorators สำหรับควบคุมการเข้าถึง

### 📦 การจัดการสต็อก
- **สแกนบาร์โค้ด**: ใช้กล้องมือถือผ่าน HTML5
- **ออกแบบสำหรับมือถือ**: เหมาะสำหรับสมาร์ทโฟน
- **รองรับหลายสาขา**: เลือกสาขาในการบันทึกสต็อก
- **บันทึกรูปภาพ**: ถ่ายรูปสินค้าผ่านกล้องมือถือ
- **ตรวจสอบแบบเรียลไทม์**: ค้นหาสินค้าด้วยบาร์โค้ด

### 📈 การวิเคราะห์ยอดขาย
- **วิเคราะห์สินค้าคงคลัง**: เปรียบเทียบสต็อกกับยอดขาย
- **ตรวจจับสินค้าขายช้า**: สินค้าที่ไม่มียอดขายใน 30 วัน
- **คำแนะนำการสั่งซื้อ**: จากความเร็วในการขาย
- **คำนวณวันคงเหลือ**: วิเคราะห์การหมุนเวียนสต็อก

---

## 🗃️ โครงสร้างฐานข้อมูล

### ตารางและความสัมพันธ์ (SQLite)

```sql
-- ตารางผู้ใช้
users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT (SHA256),
    role TEXT ('admin'|'staff')
)

-- ตารางสินค้า
products (
    barcode TEXT PRIMARY KEY,
    product_name TEXT
)

-- ตารางบันทึกสต็อก
stock_log (
    id INTEGER PRIMARY KEY,
    barcode TEXT → products.barcode,
    product_name TEXT,
    quantity INTEGER,
    branch TEXT,
    timestamp DATETIME,
    image_url TEXT,
    created_by_user_id INTEGER → users.id
)

-- ตารางยอดขาย
sales (
    id INTEGER PRIMARY KEY,
    barcode TEXT → products.barcode,
    quantity_sold INTEGER,
    date DATE
)
```

**ความสัมพันธ์:**
- หนึ่งต่อหลาย: Users → Stock_Log (ติดตามผู้นับสต็อก)
- หนึ่งต่อหลาย: Products → Stock_Log (หลายรายการสต็อกต่อสินค้า)
- หนึ่งต่อหลาย: Products → Sales (หลายรายการขายต่อสินค้า)

---

## 🌐 API Endpoints และ Routes

### 🔐 Authentication Routes
- `GET/POST /login` - เข้าสู่ระบบ
- `GET /logout` - ออกจากระบบ

### 📱 Application Routes
- `GET /` - แดชบอร์ดพนักงาน (นับสต็อก)
- `GET /get_product/<barcode>` - API ค้นหาสินค้า
- `POST /submit_stock` - ส่งข้อมูลการนับสต็อก

### 👨‍💼 Admin Routes
- `GET /report/summary` - แดชบอร์ดวิเคราะห์สต็อก
- `GET /report/slow` - รายงานสินค้าขายช้า
- `GET /sync_sales` - ซิงค์ข้อมูลยอดขาย

### 🎯 Static Routes
- `GET /favicon.ico` - ไอคอนเว็บไซต์

---

## 🎨 โครงสร้าง Templates

### 💻 User Interface Templates
- **login.html**: หน้าล็อกอินพร้อม gradient background
- **index.html**: หน้าพนักงานพร้อมเครื่องสแกนบาร์โค้ด
- **summary.html**: แดชบอร์ดผู้ดูแลพร้อมตารางวิเคราะห์
- **slow.html**: รายงานสินค้าขายช้า

### 📱 คุณสมบัติ UI
- **รองรับภาษาไทย**: ข้อความทั้งหมดเป็นภาษาไทย
- **เหมาะสำหรับมือถือ**: ปุ่มกดง่าย สำหรับสัมผัส
- **ผลตอบรับเรียลไทม์**: แจ้งเตือนและอัปเดตสถานะ
- **เชื่อมต่อกล้อง**: HTML5 getUserMedia API

---

## 🔧 Dependencies และ Requirements

### 📦 Core Dependencies
```
Flask==2.3.3                    # Web framework
pandas==2.1.1                   # การประมวลผลข้อมูล
google-api-python-client==2.103.0 # Google Drive API
google-auth-oauthlib==1.0.0     # การยืนยันตัวตน Google
gunicorn==21.2.0                # เซิร์ฟเวอร์ production
```

### 🌐 Frontend Libraries
- html5-qrcode@2.3.8 (CDN) - สแกนบาร์โค้ด
- CSS Grid/Flexbox - เลย์เอาต์ที่ยืดหยุ่น
- Vanilla JavaScript - ไม่ใช้เฟรมเวิร์กหนัก

---

## 🔒 คุณสมบัติด้านความปลอดภัย

### 🛡️ การยืนยันตัวตนและการอนุญาต
- **ความปลอดภัยรหัสผ่าน**: เข้ารหัส SHA256
- **จัดการ Session**: Flask sessions พร้อม secret key
- **การเข้าถึงตามบทบาท**: `@admin_required`, `@staff_required`
- **ป้องกันเส้นทาง**: เส้นทางสำคัญทั้งหมดได้รับการป้องกัน

### 🔐 ความปลอดภัยข้อมูล
- **ป้องกัน SQL injection**: ใช้ parameterized queries
- **ตรวจสอบข้อมูลนำเข้า**: ฝั่งไคลเอนต์และเซิร์ฟเวอร์
- **ความปลอดภัยการอัปโหลด**: เข้ารหัส Base64 สำหรับรูปภาพ

---

## 🚀 การติดตั้งและใช้งาน

### 🔧 Development Mode
```bash
python app.py
# เข้าถึงที่ http://127.0.0.1:5000
```

### 🏭 Production Mode
```bash
./start_production.sh
# หรือ
gunicorn --config gunicorn_config.py app:app
```

### 👤 ข้อมูลเข้าสู่ระบบ
**Staff:**
- Username: `staff`
- Password: `staff123`

**Admin:**
- Username: `admin`
- Password: `admin123`

---

## 📊 สรุปการประเมินโครงการ

ระบบจัดการสินค้าคงคลังที่ **พร้อมใช้งานจริง** สำหรับธุรกิจขนาดเล็กในประเทศไทย โดยมีจุดเด่น:

### ✅ จุดแข็ง
- **แนวทางการพัฒนาแบบมืออาชีพ**: แยกส่วนงานชัดเจน, จัดการข้อผิดพลาดอย่างเหมาะสม
- **ออกแบบสำหรับมือถือเป็นหลัก**: เหมาะสำหรับสมาร์ทโฟนพร้อมการเชื่อมต่อกล้อง
- **ออกแบบให้ขยายได้**: การเข้าถึงตามบทบาท, รองรับหลายสาขา
- **ความสามารถในการเชื่อมต่อ**: Google Drive, Google Sheets, นำเข้า CSV
- **เอกสารครอบคลุม**: README ภาษาไทยรายละเอียดพร้อมคำแนะนำการติดตั้ง

### 🎯 เป้าหมายการใช้งาน
ระบบนี้แก้ไขปัญหาการจัดการสินค้าคงคลังในโลกแห่งความเป็นจริงด้วยเทคโนโลยีเว็บสมัยใหม่ พร้อมรักษาความเรียบง่ายสำหรับผู้ประกอบการธุรกิจขนาดเล็ก

**โครงการนี้สาธิตการพัฒนาแอปพลิเคชันเว็บแบบเต็มรูปแบบที่ใช้งานได้จริงสำหรับธุรกิจไทย**