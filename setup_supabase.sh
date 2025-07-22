#!/bin/bash

# Supabase Setup Script for Smart Inventory Management System
# Phase 1: Database initialization and data migration

echo "🚀 Starting Supabase setup for Smart Inventory Management System..."

# Check if Supabase CLI is available
if [ ! -f "./supabase" ]; then
    echo "❌ Supabase CLI not found. Please run the installation first."
    exit 1
fi

# Check if environment variables are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "❌ Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables"
    echo "You can get these from your Supabase project dashboard:"
    echo "1. Go to Settings → API"
    echo "2. Copy Project URL and anon public key"
    echo ""
    echo "Example:"
    echo "export SUPABASE_URL='https://your-project.supabase.co'"
    echo "export SUPABASE_ANON_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'"
    exit 1
fi

echo "✅ Environment variables found"
echo "📊 Supabase URL: $SUPABASE_URL"

# Check if we can connect to Supabase
echo "🔍 Testing Supabase connection..."
python3 -c "
import os
try:
    from supabase import create_client
    client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_ANON_KEY'])
    print('✅ Successfully connected to Supabase')
except Exception as e:
    print(f'❌ Failed to connect to Supabase: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Cannot connect to Supabase. Please check your credentials."
    exit 1
fi

# Initialize Supabase project locally
echo "🏗️ Initializing local Supabase project..."
./supabase init --name "smart-inventory"

# Generate types (optional)
echo "📝 Generating TypeScript types..."
./supabase gen types typescript --project-id $(basename $SUPABASE_URL .supabase.co) > types/supabase.ts 2>/dev/null || echo "⚠️ Could not generate types (this is optional)"

echo "🗄️ Setting up database schema..."
echo "Please run the following SQL in your Supabase dashboard:"
echo "1. Go to SQL Editor in your Supabase dashboard"
echo "2. Copy and paste the contents of database_schema.sql"
echo "3. Execute the SQL commands"
echo ""
echo "📄 Database schema file: database_schema.sql"

# Check if migration should be run
read -p "🤔 Do you want to migrate data from Google Sheets? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 Running data migration from Google Sheets..."
    python3 migrate_from_sheets.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Data migration completed successfully!"
    else
        echo "❌ Data migration failed. Please check the error messages above."
    fi
else
    echo "⏭️ Skipping data migration"
fi

echo ""
echo "🎉 Supabase setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Verify your database schema in Supabase dashboard"
echo "2. Set up Row Level Security policies (see SUPABASE_SETUP.md)"
echo "3. Test the application with: python3 app.py"
echo "4. Access the new dashboard at: /dashboard"
echo ""
echo "📚 For detailed instructions, see: SUPABASE_SETUP.md"