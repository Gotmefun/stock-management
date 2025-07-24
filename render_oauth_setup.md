# 🔐 Render.com OAuth2 Setup Guide

## 📋 Environment Variables ที่ต้องเพิ่มใน Render.com Dashboard

### 1. เข้า Render.com Dashboard:
- URL: https://dashboard.render.com
- เลือก service: **ptee88.com**
- ไปที่ **Environment** tab

### 2. เพิ่ม Environment Variable ใหม่:

```bash
# Google OAuth2 Credentials
GOOGLE_CREDENTIALS={"web":{"client_id":"YOUR_CLIENT_ID","project_id":"YOUR_PROJECT_ID","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"YOUR_CLIENT_SECRET","redirect_uris":["http://127.0.0.1:8080/oauth2callback","http://localhost:8080/oauth2callback","http://127.0.0.1:8081/oauth2callback","http://127.0.0.1:8080/authorize_drive","http://localhost:8080/authorize_drive","https://stock-management-1-wfiy.onrender.com/","https://www.ptee88.com/oauth2callback"],"javascript_origins":["http://127.0.0.1:8080","http://localhost:8080"]}}
```

**Note**: Replace `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET` with actual values from your Google Cloud Console OAuth2 credentials.

### 3. ตรวจสอบ Environment Variables ที่มีอยู่แล้ว:

```bash
✅ SUPABASE_URL=https://khiooiigrfrluvyobljq.supabase.co
✅ SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
✅ SECRET_KEY=ptee88-super-secret-key-2024
✅ PRODUCT_SHEET_ID=17fQBTqiUG6tFH-67its-iaKDV2ef4HLJ9S3BGKTVSdM
✅ STOCK_SHEET_ID=1OaEqOS7I0_hN2Q1nc4isqPXXdjp7_i7ZAPJFhUr5X7k
✅ APPS_SCRIPT_URL=https://script.google.com/macros/s/AKfycbxaVXe5bMs7tw8n5iUZ_l4D4aeGJk-bEFT-QNpTe87XXGRvwhBCB4go9u9e9ddJ364/exec
🆕 GOOGLE_CREDENTIALS={"web":{"client_id":"YOUR_CLIENT_ID",...}}
```

## 🔄 ลำดับการอัปโหลดรูปภาพ

### Primary: Google Apps Script
1. ✅ ส่งรูปไปยัง Apps Script Web App URL
2. ✅ สร้างโฟลเดอร์ตามสาขา (CITY/SCHOOL/PONGPAI)
3. ✅ บันทึกใน Google Drive
4. ✅ ส่งลิงก์กลับมา

### Fallback: OAuth2 Google Drive (ใหม่!)
1. 🔄 ถ้า Apps Script ล้มเหลว → ใช้ OAuth2
2. 🔄 ผู้ใช้ต้อง authorize ครั้งแรก
3. 🔄 บันทึกใน Google Drive ผ่าน API โดยตรง
4. 🔄 ส่งลิงก์กลับมา

### Last Resort: Local Storage
1. 💾 ถ้าทั้งสองวิธีล้มเหลว → เก็บ local
2. 💾 บันทึกใน uploads/ folder
3. 💾 ส่งลิงก์ local กลับมา

## 🧪 การทดสอบ OAuth2

### 1. Authorization Flow:
- เข้า: https://www.ptee88.com/authorize_drive
- Login Google Account
- Grant permissions
- Redirect กลับมาที่ /oauth2callback

### 2. Check Authorization Status:
- API: https://www.ptee88.com/drive_status
- Response: `{"authorized": true/false, "message": "..."}`

## 🔧 Redirect URIs ที่ได้ Configure:

```
✅ http://127.0.0.1:8080/oauth2callback     (Local dev)
✅ http://localhost:8080/oauth2callback     (Local dev)  
✅ http://127.0.0.1:8081/oauth2callback     (Local dev port 8081)
✅ http://127.0.0.1:8080/authorize_drive    (Local auth)
✅ http://localhost:8080/authorize_drive    (Local auth)
✅ https://stock-management-1-wfiy.onrender.com/  (Old render URL)
✅ https://www.ptee88.com/oauth2callback    (Production)
```

## 🚨 Security Notes:

1. **Client Secret**: อยู่ใน Environment Variable แล้ว ✅
2. **Redirect URIs**: จำกัดเฉพาะ domains ที่อนุญาต ✅
3. **Scopes**: จำกัดเฉพาะ Google Drive ✅
4. **Token Storage**: เก็บใน session/pickle file ✅

## 📊 Expected Benefits:

1. **ความน่าเชื่อถือสูงขึ้น**: มี fallback mechanism
2. **ไม่พึ่ง Apps Script เพียงอย่างเดียว**: มี backup plan
3. **ควบคุมได้มากขึ้น**: ใช้ Google Drive API โดยตรง
4. **Debug ง่ายขึ้น**: สามารถดู error logs ได้ชัดเจน