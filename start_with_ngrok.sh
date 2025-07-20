#!/bin/bash
# Start Flask app with ngrok tunnel for mobile access

echo "🚀 Starting Inventory Management System with ngrok"
echo "================================================="

# Check if running in WSL
if grep -q Microsoft /proc/version; then
    echo "✅ Detected WSL environment"
else
    echo "ℹ️  Running on native Linux"
fi

# Start Flask app in background
echo "📱 Starting Flask application..."
cd "/mnt/e/My App/AAAAAAAAAA"
source venv/bin/activate

# Kill any existing processes
pkill -f "python.*app.py" 2>/dev/null || echo "No existing Flask processes"

# Start Flask app
python3 app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

echo "🌐 Starting ngrok tunnel..."

# Check if ngrok exists in current directory
if [ ! -f "./ngrok" ]; then
    echo "❌ ngrok not found in current directory"
    
    # Check if we have the tar file to extract
    if [ -f "ngrok-v3-stable-linux-amd64.tgz" ]; then
        echo "📦 Extracting ngrok from tar file..."
        tar -xzf ngrok-v3-stable-linux-amd64.tgz
        chmod +x ngrok
        echo "✅ ngrok extracted and ready"
    else
        echo "⚠️  No ngrok tar file found. Please ensure ngrok-v3-stable-linux-amd64.tgz exists"
        exit 1
    fi
fi

# Start ngrok tunnel
./ngrok http 8080 &
NGROK_PID=$!

echo ""
echo "🎯 Access URLs:"
echo "   💻 Local (Windows):  http://localhost:8080"
echo "   📱 Mobile (ngrok):   Check ngrok dashboard at http://localhost:4040"
echo ""
echo "👤 Login Credentials:"
echo "   Staff: username=staff, password=staff123"
echo "   Admin: username=admin, password=admin123"
echo ""
echo "⚠️  Press Ctrl+C to stop both Flask and ngrok"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $FLASK_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null
    pkill -f ngrok 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Handle Ctrl+C
trap cleanup SIGINT

# Wait for user to stop
echo "🔄 Services running... Press Ctrl+C to stop"
wait