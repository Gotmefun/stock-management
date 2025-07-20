#!/bin/bash
# Start ngrok tunnel for mobile testing

echo "🌐 Starting ngrok tunnel for mobile testing..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found. Please install ngrok:"
    echo "   Download from: https://ngrok.com/download"
    echo "   Or install via: sudo snap install ngrok"
    exit 1
fi

echo "📱 Starting Flask app in background..."
cd "/mnt/e/My App/AAAAAAAAAA"
source venv/bin/activate
python3 test_mobile.py &
FLASK_PID=$!

sleep 3

echo "🌍 Creating ngrok tunnel..."
ngrok http 8080 &
NGROK_PID=$!

echo "🎯 Access your app from anywhere using the ngrok URL"
echo "⚠️  Press Ctrl+C to stop both servers"

# Cleanup function
cleanup() {
    echo "🛑 Stopping servers..."
    kill $FLASK_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT

# Wait for user interrupt
wait