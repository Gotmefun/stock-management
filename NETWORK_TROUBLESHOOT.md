# Network Troubleshooting Guide

## วิธีแก้ปัญหาการเชื่อมต่อจากมือถือ

### 1. ตรวจสอบ Windows IP (แนะนำ)
```cmd
# รันใน Command Prompt ของ Windows
ipconfig
# หา IP ของ WiFi adapter เช่น 192.168.1.100
```

### 2. Port Forwarding สำหรับ WSL2
```cmd
# รันใน PowerShell ของ Windows (Run as Administrator)
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=172.25.190.240
```

### 3. ตรวจสอบ Firewall
```cmd
# ปิด Windows Firewall ชั่วคราวเพื่อทดสอบ
netsh advfirewall set allprofiles state off
# เปิดกลับหลังทดสอบ
netsh advfirewall set allprofiles state on
```

### 4. ใช้ ngrok (วิธีที่ง่ายที่สุด)
```bash
# Install ngrok
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip

# Run tunnel
./ngrok http 8080
# จะได้ URL สาธารณะสำหรับทดสอบ
```

### 5. URLs สำหรับทดสอบ

**หลังจากหา Windows IP แล้ว (เช่น 192.168.1.100):**
- Desktop: http://192.168.1.100:8080
- Mobile: http://192.168.1.100:8080

**ถ้าใช้ ngrok:**
- ใช้ URL ที่ ngrok แสดง เช่น https://abc123.ngrok.io