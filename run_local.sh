#!/bin/bash
# Start Flask app for local development only

echo "💻 Starting Inventory Management System (Local Only)"
echo "=================================================="

cd "/mnt/e/My App/AAAAAAAAAA"
source venv/bin/activate

echo "🚀 Starting Flask application..."
echo "📍 Local access: http://localhost:8080"
echo ""
echo "👤 Login Credentials:"
echo "   Staff: username=staff, password=staff123"
echo "   Admin: username=admin, password=admin123"
echo ""
echo "⚠️  Press Ctrl+C to stop server"
echo "=================================================="

# Start Flask app
python3 app.py