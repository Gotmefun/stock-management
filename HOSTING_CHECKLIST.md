# Hosting Checklist สำหรับระบบนับสต๊อก

## ✅ ใช้งานได้ครบทุกอย่าง
- ✅ บันทึกข้อมูลใน Google Sheets (Service Account)
- ✅ อัปโหลดรูปใน Google Drive (Apps Script)
- ✅ สแกนบาร์โค้ด
- ✅ ถ่ายรูป
- ✅ Login system

## ⚠️ สิ่งที่ต้องแก้เมื่อขึ้น Host

### 1. Environment Variables
```bash
# ไฟล์ .env ต้องมี:
SECRET_KEY=your-production-secret-key
PRODUCT_SHEET_ID=17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM
STOCK_SHEET_ID=1OaEqOS7I0_hN2Q1nc4isqPXXdjp7_i7ZAPJFhUr5X7k
APPS_SCRIPT_URL=https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec
```

### 2. ไฟล์ที่ต้องอัปโหลด
- `service_account.json` (สำคัญมาก!)
- `requirements.txt`
- โฟลเดอร์ `templates/` และ `static/`

### 3. Dependencies
```bash
pip install -r requirements.txt
```

### 4. Production Server
แทน `app.run()` ใช้ Gunicorn:
```python
if __name__ == '__main__':
    init_sheets()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
```

### 5. HTTPS
ถ้าใช้ HTTPS ต้องแก้ camera permissions ใน browser

## 🚀 ขั้นตอน Deploy

1. **Upload files:**
   - ไฟล์ Python ทั้งหมด
   - `service_account.json`
   - `templates/` และ `static/`

2. **Set Environment Variables**

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run:**
   ```bash
   python app.py
   ```

## ✅ ระบบพร้อมใช้งานครบทุก Function!