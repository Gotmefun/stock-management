# PowerShell script สำหรับตั้งค่า Port Forwarding ใน WSL2
# รันใน PowerShell ด้วยสิทธิ์ Administrator

Write-Host "🔧 Setting up Port Forwarding for WSL2..." -ForegroundColor Green

# Remove existing port proxy if exists
netsh interface portproxy delete v4tov4 listenport=5000 listenaddress=0.0.0.0

# Add port forwarding rule
netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=172.25.190.240

Write-Host "✅ Port forwarding setup complete!" -ForegroundColor Green
Write-Host "📱 Your mobile can now access: http://192.168.1.59:5000" -ForegroundColor Cyan

# Show current port proxy rules
Write-Host "📋 Current port forwarding rules:" -ForegroundColor Yellow
netsh interface portproxy show all

Write-Host ""
Write-Host "🚀 Now run your Flask app in WSL and access it from mobile!" -ForegroundColor Green