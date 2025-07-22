# Supabase Database Setup Guide
## Smart Inventory Management System - Phase 1

This guide will help you set up the Supabase database for the Smart Inventory Management System.

## Prerequisites

1. Create a Supabase account at [supabase.com](https://supabase.com)
2. Have your Google Sheets data ready for migration

## Step 1: Create Supabase Project

1. Log in to your Supabase dashboard
2. Click "New project"
3. Choose your organization
4. Enter project details:
   - **Name**: Smart Inventory Management
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to your users
5. Click "Create new project"
6. Wait for the project to be ready (2-3 minutes)

## Step 2: Get Connection Details

From your Supabase project dashboard:

1. Go to **Settings** → **API**
2. Copy the following:
   - **Project URL** (starts with `https://xxx.supabase.co`)
   - **anon public** key (starts with `eyJ...`)
   - **service_role** key (starts with `eyJ...`) - Keep this secret!

## Step 3: Set Environment Variables

Add these to your `.env` file or deployment environment:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Step 4: Create Database Schema

1. Go to **SQL Editor** in your Supabase dashboard
2. Copy the contents of `database_schema.sql`
3. Paste and run the SQL commands
4. Verify that all tables are created in **Table Editor**

Expected tables:
- `users` - User authentication
- `products` - Product master data  
- `branches` - Store locations
- `inventory` - Current stock levels
- `sales` - Sales transactions
- `sale_items` - Sales line items
- `inventory_movements` - Stock movement history
- `stock_counts` - Stock counting records
- `alert_rules` - Alert configuration
- `alerts` - Active alerts

## Step 5: Run Data Migration (Optional)

If you have existing data in Google Sheets:

1. Install dependencies:
   ```bash
   pip install supabase pandas
   ```

2. Set up environment variables (from Step 3)

3. Run migration script:
   ```bash
   python migrate_from_sheets.py
   ```

This will:
- Import products from Google Sheets
- Import stock counting history  
- Create sample sales data for analytics
- Set up initial inventory levels

## Step 6: Test the Application

1. Update your application with the Supabase credentials
2. Start the Flask application:
   ```bash
   python app.py
   ```
3. Login as admin (username: `admin`, password: `Teeomega2014`)
4. Navigate to **Dashboard** to see the new analytics interface

## Security Setup (Production)

For production deployment:

### Row Level Security (RLS)

1. Go to **Authentication** → **Policies**
2. Enable RLS on all tables:

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE branches ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE sale_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_movements ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_counts ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
```

### Create Policies (Example for products table)

```sql
-- Allow authenticated users to read products
CREATE POLICY "Users can view products" ON products
FOR SELECT TO authenticated USING (true);

-- Allow admin users to modify products  
CREATE POLICY "Admins can modify products" ON products
FOR ALL TO authenticated 
USING (auth.jwt() ->> 'role' = 'admin');
```

## Features Available in Phase 1

✅ **Dashboard Analytics**
- Real-time sales metrics
- Product performance tracking
- Low stock alerts
- Branch-wise filtering

✅ **Database Schema**
- Complete normalized database structure
- Optimized for analytics and reporting
- Support for multi-branch operations

✅ **Data Migration**
- Import from Google Sheets
- Historical data preservation
- Sample data generation

✅ **Smart Alerts**
- Low stock monitoring
- Variance detection
- Configurable alert rules

## Next Steps (Phase 2)

- File upload system for product imports
- Purchase planning and EOQ calculations
- Advanced analytics and forecasting
- Mobile app integration

## Troubleshooting

### Common Issues

1. **Connection Error**: Check your URL and keys
2. **Table Not Found**: Ensure schema was created properly
3. **Permission Denied**: Verify RLS policies are configured
4. **Migration Failed**: Check Google Sheets API credentials

### Getting Help

- Check Supabase documentation: [docs.supabase.com](https://docs.supabase.com)
- Review error logs in Supabase dashboard
- Test queries in SQL Editor

## Environment Variables Summary

Required for production:

```bash
# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Google Sheets (if still using for some features)
PRODUCT_SHEET_ID=your-product-sheet-id
STOCK_SHEET_ID=your-stock-sheet-id

# Application
SECRET_KEY=your-secret-key
APPS_SCRIPT_URL=your-apps-script-url
```