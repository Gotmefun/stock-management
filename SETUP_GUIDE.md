# 🚀 Setup Guide - Inventory Management System

## 📋 การตั้งค่าและการใช้งาน

### 🖥️ **สำหรับการใช้งานบนคอมพิวเตอร์ (Local)**

```bash
# วิธีที่ 1: รันด้วย script
./run_local.sh

# วิธีที่ 2: รันด้วยคำสั่งปกติ
cd "/mnt/e/My App/AAAAAAAAAA"
source venv/bin/activate
python app.py
```

**เข้าถึงได้ที่:** http://localhost:5000

---

### 📱 **สำหรับการใช้งานบนมือถือ (ผ่าน ngrok)**

```bash
# รัน Flask + ngrok พร้อมกัน
./start_with_ngrok.sh
```

**ขั้นตอน:**
1. รันคำสั่งข้างต้น
2. เปิดเบราว์เซอร์ไปที่ http://localhost:4040
3. ดู Public URL ที่ ngrok สร้างให้ (เช่น https://abc123.ngrok.io)
4. เปิดมือถือ เข้า URL ที่ได้จาก ngrok

---

## 👤 **ข้อมูลการเข้าสู่ระบบ**

| บทบาท | Username | Password |
|---------|----------|----------|
| พนักงาน | `staff` | `staff123` |
| ผู้ดูแลระบบ | `admin` | `admin123` |

---

## 🔧 **การใช้งานแต่ละโหมด**

### 💻 **โหมด Local (Windows/Linux)**
- ✅ เหมาะสำหรับการพัฒนาและทดสอบ
- ✅ เร็วและเสถียร
- ✅ ไม่ต้องอาศัยอินเทอร์เน็ต
- ❌ เข้าถึงได้เฉพาะในเครื่อง

### 📱 **โหมด ngrok (Mobile)**
- ✅ เข้าถึงได้จากทุกที่ที่มีอินเทอร์เน็ต
- ✅ เหมาะสำหรับทดสอบบนมือถือ
- ✅ SSL/HTTPS support
- ❌ ต้องมีอินเทอร์เน็ต
- ❌ URL เปลี่ยนทุกครั้งที่รัน (ยกเว้น paid plan)

---

## 🎯 **แนะนำการใช้งาน**

### 🔄 **สำหรับการพัฒนา (Development):**
```bash
./run_local.sh
# เข้าถึง: http://localhost:5000
```

### 🧪 **สำหรับการทดสอบบนมือถือ:**
```bash
./start_with_ngrok.sh
# ดู URL จาก ngrok dashboard: http://localhost:4040
```

### 🏭 **สำหรับ Production:**
```bash
./start_production.sh
# หรือ
gunicorn --config gunicorn_config.py app:app
```

---

## 📂 **ไฟล์สำคัญ**

| ไฟล์ | จุดประสงค์ |
|------|------------|
| `app.py` | แอปพลิเคชันหลัก |
| `run_local.sh` | รันโหมด local |
| `start_with_ngrok.sh` | รันโหมด ngrok |
| `start_production.sh` | รันโหมด production |
| `requirements.txt` | Python dependencies |
| `gunicorn_config.py` | การตั้งค่า production server |

---

## 🛠️ **การแก้ปัญหา**

### ❗ **ถ้า port ถูกใช้งาน:**
```bash
# หยุด process ที่ใช้ port 5000
pkill -f "python.*app.py"
# หรือ
lsof -ti:5000 | xargs kill -9
```

### ❗ **ถ้า ngrok ไม่ทำงาน:**
```bash
# Download ngrok ใหม่
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip
chmod +x ngrok
```

### ❗ **ถ้าเข้าไม่ได้จากมือถือ:**
1. ตรวจสอบว่า ngrok รันอยู่
2. เช็ค URL จาก http://localhost:4040
3. ใช้ HTTPS URL (ไม่ใช่ HTTP)

---

**✅ ตอนนี้ระบบพร้อมใช้งานทั้งบนคอมพิวเตอร์และมือถือแล้ว!**