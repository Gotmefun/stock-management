# 📱 ระบบนับสต๊อกสินค้า (Stock Count System)

มาตรวจนับสินค้ากันเถอะ - ระบบนับสต๊อกที่ทันสมัย ใช้งานง่าย พัฒนาด้วย Flask + Google Sheets + Google Apps Script

## ✨ คุณสมบัติหลัก

### 📊 ข้อมูลเก็บใน Google Sheets
- **ไม่ต้องฐานข้อมูล** - ใช้ Google Sheets เป็นฐานข้อมูลหลัก
- **Product Master Sheet** - ข้อมูลสินค้าและบาร์โค้ด  
- **Stock Counting Data** - บันทึกการนับสต๊อกพร้อมรูปภาพ
- **Real-time sync** - ข้อมูลอัปเดตทันที

### 📸 อัปโหลดรูปผ่าน Google Apps Script
- **ไม่ต้อง OAuth2** - ใช้ Apps Script ง่ายกว่า
- **Auto upload** - อัปโหลดรูปไป Google Drive อัตโนมัติ
- **Folder organized** - จัดเก็บในโฟลเดอร์ "Check Stock Project/Pic Stock Counting"

### 📱 การนับสต๊อกบนมือถือ
- **สแกนบาร์โค้ด** ด้วยกล้องมือถือ (html5-qrcode)
- **ถ่ายภาพสินค้า** ขณะนับสต๊อก
- **รองรับหลายสาขา** - เลือกสาขาที่ต้องการนับ
- **ระบุผู้นับ** - บันทึกชื่อผู้ตรวจนับสินค้า

### 👥 ระบบผู้ใช้งาน
- **Admin** - ดูรายงาน, จัดการระบบ
- **Staff** - นับสต๊อกด้วยมือถือ

## 🚀 การติดตั้งและใช้งาน

### 1. Clone Repository
```bash
git clone https://github.com/Gotmefun/stock-management.git
cd stock-management
```

### 2. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 3. ตั้งค่า Google Services

#### Google Sheets (Service Account)
1. สร้าง Service Account ใน Google Cloud Console
2. ดาวน์โหลด `service_account.json`
3. วางไฟล์ในโฟลเดอร์โปรเจค
4. แชร์ Google Sheets ให้กับ Service Account email

#### Google Apps Script (สำหรับอัปโหลดรูป)
1. สร้าง Apps Script ใหม่ที่ https://script.google.com
2. ใส่โค้ดจากไฟล์ `APPS_SCRIPT_CODE.md`
3. Deploy เป็น Web App
4. Copy URL มาใส่ในไฟล์ `app.py`

### 4. ตั้งค่า Environment Variables
```bash
# สร้างไฟล์ .env
PRODUCT_SHEET_ID=your_product_sheet_id
STOCK_SHEET_ID=your_stock_sheet_id
APPS_SCRIPT_URL=your_apps_script_url
SECRET_KEY=your-secret-key
```

### 5. รันแอปพลิเคชัน
```bash
python app.py
```

### 6. เปิดเบราว์เซอร์
```
http://localhost:8080
```

## 📋 ข้อมูลผู้ใช้

| บทบาท | ชื่อผู้ใช้ | รหัสผ่าน |
|--------|-----------|----------|
| Admin  | admin     | admin123 |
| Staff  | staff     | staff123 |

## 📊 โครงสร้าง Google Sheets

### Product Master Sheet
| Column | หัวข้อ | ตัวอย่าง |
|--------|--------|----------|
| A | Row Number | 1, 2, 3... |
| B | Product ID | P001, P002... |
| C | Category | อาหาร, เครื่องดื่ม |
| **D** | **Barcode** | **8857128895016** |
| **E** | **Product Name** | **น้ำดื่ม 600ml** |

### Stock Counting Data
| Column | หัวข้อ |
|--------|--------|
| A | Timestamp |
| B | Barcode |
| C | Product Name |
| D | Quantity |
| E | Branch |
| F | User |
| G | Image URL |
| H | Created By |
| **I** | **ชื่อผู้ตรวจนับสินค้า** |

## 📁 โครงสร้างโปรเจค

```
stock-management/
├── app.py                    # Flask application หลัก
├── oauth_manager.py          # OAuth2 manager (fallback)
├── sheets_manager.py         # Google Sheets integration
├── upload_to_drive.py        # Google Drive API
├── requirements.txt          # Python dependencies
├── service_account.json      # Google Service Account (secret)
├── oauth2_credentials.json   # OAuth2 credentials (secret)
├── APPS_SCRIPT_CODE.md      # Apps Script source code
├── HOSTING_CHECKLIST.md     # Production deployment guide
├── templates/               # HTML templates
│   ├── login.html          # หน้าล็อกอิน
│   ├── index.html          # หน้านับสต๊อก (staff)
│   └── summary.html        # หน้ารายงาน (admin)
├── static/                 # CSS, JS, images
│   ├── barcode.js         # JavaScript สำหรับสแกนบาร์โค้ด
│   └── favicon.ico        # Site icon
└── uploads/               # Local backup (fallback)
```

## 🛠️ ส่วนประกอบเทคนิค

### Backend (Python Flask)
- **Flask** - Web framework
- **Google Sheets API** - ฐานข้อมูลหลัก
- **Google Drive API** - อัปโหลดรูป (fallback)
- **Service Account** authentication

### Frontend (HTML5 + JavaScript)
- **html5-qrcode** - สแกนบาร์โค้ด
- **Camera API** - ถ่ายภาพ
- **Responsive design** - ใช้งานบนมือถือ

### Google Services Integration
- **Google Sheets** - ฐานข้อมูล
- **Google Apps Script** - อัปโหลดรูป (หลัก)
- **Google Drive** - เก็บรูปภาพ

## 📱 การใช้งานบนมือถือ

### การนับสต๊อก (Staff)
1. **เข้าสู่ระบบ** ด้วยบัญชี Staff
2. **สแกนบาร์โค้ด** หรือกรอกด้วยมือ
3. **กรอกข้อมูล:**
   - ชื่อผู้ตรวจนับสินค้า
   - จำนวนคงเหลือ
   - สาขา
4. **ถ่ายภาพสินค้า**
5. **บันทึกข้อมูล** - ส่งไป Google Sheets + Drive

### การดูรายงาน (Admin)
1. **เข้าสู่ระบบ** ด้วยบัญชี Admin
2. **ดูรายงานสรุป** - สต๊อกทั้งหมดแยกตามสาขา
3. **ดูรายการสินค้า** - ข้อมูลจาก Product Master

## 🚀 Production Deployment

### Environment Variables
```bash
SECRET_KEY=production-secret-key
PRODUCT_SHEET_ID=your_actual_product_sheet_id
STOCK_SHEET_ID=your_actual_stock_sheet_id
APPS_SCRIPT_URL=your_apps_script_deployment_url
```

### Required Files
- `service_account.json` (Google Service Account)
- `requirements.txt`
- `app.py` และไฟล์ Python อื่นๆ
- โฟลเดอร์ `templates/` และ `static/`

### Server Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

## 🔐 ความปลอดภัย

### Files ที่ไม่ควร commit
- `service_account.json` - Google Service Account credentials
- `oauth2_credentials.json` - OAuth2 client secrets
- `drive_token.pickle` - OAuth2 access token
- `.env` - Environment variables

### Authentication
- **Password hashing** - SHA256
- **Session management** - Flask sessions
- **Role-based access** - Admin/Staff permissions

## 🐛 การแก้ไขปัญหา

### กล้องไม่ทำงาน
1. อนุญาตเข้าถึงกล้องในเบราว์เซอร์
2. ใช้ HTTPS หรือ localhost
3. ลองเบราว์เซอร์อื่น (Chrome แนะนำ)

### รูปอัปโหลดไม่ได้
1. ตรวจสอบ Apps Script URL
2. ดู Console logs ในเบราว์เซอร์
3. ตรวจสอบ Apps Script permissions

### Google Sheets ไม่อัปเดต
1. ตรวจสอบ Service Account permissions
2. แชร์ Sheet ให้กับ Service Account email
3. ตรวจสอบ Sheet ID ในไฟล์ config

## 🤝 การพัฒนาต่อ

### ไอเดียฟีเจอร์ใหม่
- [ ] ระบบแจ้งเตือน Line/Discord
- [ ] Export รายงานเป็น PDF
- [ ] Dashboard real-time
- [ ] PWA (ใช้งาน offline ได้)
- [ ] Multi-language support
- [ ] QR Code generator

### Architecture Improvements
- [ ] Redis caching
- [ ] PostgreSQL database
- [ ] Docker containerization
- [ ] CI/CD pipeline

## 📝 License

MIT License - ใช้งานได้อย่างอิสระ

## 👨‍💻 ผู้พัฒนา

พัฒนาโดย **Claude AI Assistant** 
- 🚀 Modern web technologies
- 📱 Mobile-first design  
- 🔒 Secure authentication
- ☁️ Cloud integration

---

⭐ **Star this repository** หากโปรเจคนี้มีประโยชน์!

📧 **Issues & Questions**: สร้าง Issue ใน GitHub repository