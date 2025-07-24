# 📝 Google Apps Script Deployment Guide

## 🎯 วัตถุประสงค์
สร้าง Google Apps Script ที่:
1. รับรูปภาพ base64 จาก web app (www.ptee88.com)
2. สร้างโฟลเดอร์ตามสาขา:
   - `Check Stock Project/สาขาตัวเมือง` (CITY)
   - `Check Stock Project/สาขาหน้าโรงเรียน` (SCHOOL)
   - `Check Stock Project/สาขาโป่งไผ่` (PONGPAI)
3. บันทึกรูปภาพใน Google Drive
4. ส่งลิงก์กลับไปให้ web app

## 🔧 ขั้นตอนการ Deploy

### 1. Copy โค้ดจากไฟล์ `google_apps_script_code.js`

### 2. วาง (Paste) ในโปรเจค Google Apps Script ของคุณ:
**URL**: https://script.google.com/u/0/home/projects/1JIvN9zr6cwkod5Uv7QZ_YFAetFyR7v0RHVuGJB43TsSyAIV0ZcoGqh-4/edit

### 3. ตั้งค่า Deployment:
1. กด **Deploy** → **New deployment**
2. เลือก **Type**: Web app
3. **Execute as**: Me
4. **Who has access**: Anyone
5. กด **Deploy**
6. Copy **Web app URL**

### 4. อัปเดต Web App URL ใน Production:
ใน Render.com Dashboard → Environment Variables:
```
APPS_SCRIPT_URL=<YOUR_NEW_WEB_APP_URL>
```

## 🧪 วิธีทดสอบ

### ทดสอบใน Apps Script Editor:
1. เรียกฟังก์ชัน `testFolderCreation()` - ทดสอบการสร้างโฟลเดอร์
2. เรียกฟังก์ชัน `testImageUpload()` - ทดสอบการอัปโหลดรูป

### ทดสอบจาก Web App:
1. เข้า www.ptee88.com
2. Login → เลือกสาขา → ถ่ายภาพ → บันทึก
3. ตรวจสอบใน Google Drive ว่ามีรูปในโฟลเดอร์ที่ถูกต้อง

## ✅ Features ใหม่

### 1. **Error Handling ที่ดีขึ้น**:
- ตรวจสอบ JSON parsing
- Validate required fields
- จัดการ MIME types หลายแบบ

### 2. **รองรับ Multiple Image Formats**:
- JPG/JPEG
- PNG  
- GIF
- WebP

### 3. **Folder Management**:
- สร้างโฟลเดอร์อัตโนมัติถ้ายังไม่มี
- รองรับโฟลเดอร์ซ้อนกัน
- ป้องกันไฟล์ชื่อซ้ำ

### 4. **Security**:
- Set file permissions เป็น public readable
- Unique filename สำหรับไฟล์ซ้ำ

### 5. **Testing Functions**:
- `testImageUpload()` - ทดสอบอัปโหลด
- `testFolderCreation()` - ทดสอบสร้างโฟลเดอร์  
- `cleanupTestFiles()` - ลบไฟล์ทดสอบ

## 🚨 สิ่งที่ต้องตรวจสอบ

### 1. **Permissions**:
แน่ใจว่า Apps Script มี permission:
- Google Drive API
- Access to create folders and files

### 2. **Web App Settings**:
- Execute as: **Me** (ไม่ใช่ User accessing the web app)
- Who has access: **Anyone**

### 3. **Environment Variables**:
ใน Render.com ต้องมี:
```
APPS_SCRIPT_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
```

## 🔍 Troubleshooting

### หากอัปโหลดไม่สำเร็จ:
1. ดู **Logs** ใน Apps Script Editor
2. ทดสอบด้วย `testImageUpload()`
3. ตรวจสอบ permissions

### หากโฟลเดอร์ไม่ถูกสร้าง:
1. ทดสอบด้วย `testFolderCreation()`
2. ตรวจสอบชื่อโฟลเดอร์ (รองรับภาษาไทย)
3. ตรวจสอบ Drive API permissions

## 📊 Expected Response Format

### Success Response:
```json
{
  "success": true,
  "fileId": "1ABC123...",
  "filename": "stock_123456_20250724.jpg",
  "webViewLink": "https://drive.google.com/file/d/.../view",
  "downloadLink": "https://drive.google.com/uc?id=...",
  "folder": "Check Stock Project/สาขาตัวเมือง",
  "folderId": "1XYZ789..."
}
```

### Error Response:
```json
{
  "success": false,
  "error": "Error description here",
  "stack": "Stack trace if available"
}
```