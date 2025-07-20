#!/bin/bash
# Production startup script for inventory management system

# Activate virtual environment
source venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

# Start gunicorn with configuration
echo "Starting inventory management system..."
gunicorn --config gunicorn_config.py app:app

# Alternative: Start with manual configuration
# gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 30 --log-level info app:app