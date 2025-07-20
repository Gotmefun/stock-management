#!/bin/bash
# Simple mobile access setup without ngrok

echo "📱 Setting up mobile access (Simple Method)"
echo "============================================"

cd "/mnt/e/My App/AAAAAAAAAA"
source venv/bin/activate

# Kill existing processes
pkill -f "python.*app.py" 2>/dev/null || echo "No existing Flask processes"

echo "🚀 Starting Flask on all interfaces..."

# Modify app.py temporarily to run on 0.0.0.0
cat > temp_mobile_app.py << 'EOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/mnt/e/My App/AAAAAAAAAA')

from app import app, init_db

if __name__ == '__main__':
    init_db()
    print("🌐 Mobile access server starting...")
    print("📱 Mobile URL: http://192.168.1.59:8080")
    print("💻 Local URL:  http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
EOF

# Run the mobile version
python3 temp_mobile_app.py