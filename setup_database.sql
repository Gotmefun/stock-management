-- Quick setup for Stock Counting System
-- Run this in Supabase SQL Editor

-- Create branches table
CREATE TABLE IF NOT EXISTS branches (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    manager_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    barcode VARCHAR(50) UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    brand VARCHAR(100),
    unit VARCHAR(20) DEFAULT 'pieces',
    cost_price DECIMAL(10,2),
    selling_price DECIMAL(10,2),
    reorder_level INTEGER DEFAULT 0,
    max_stock_level INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,
    last_counted_at TIMESTAMP WITH TIME ZONE,
    last_counted_by VARCHAR(100),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, branch_id)
);

-- Create stock_counts table
CREATE TABLE IF NOT EXISTS stock_counts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id),
    branch_id UUID REFERENCES branches(id),
    counted_quantity INTEGER NOT NULL,
    system_quantity INTEGER,
    variance INTEGER,
    counter_name VARCHAR(100) NOT NULL,
    counted_by VARCHAR(100),
    image_url TEXT,
    notes TEXT,
    counted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default branches
INSERT INTO branches (code, name) VALUES 
('MAIN', 'สาขาหลัก'),
('CITY', 'สาขาตัวเมือง'),
('PONGPAI', 'สาขาโป่งไผ่'),
('SCHOOL', 'สาขาหน้าโรงเรียน')
ON CONFLICT (code) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_inventory_product_branch ON inventory(product_id, branch_id);
CREATE INDEX IF NOT EXISTS idx_stock_counts_product_branch ON stock_counts(product_id, branch_id);
CREATE INDEX IF NOT EXISTS idx_stock_counts_date ON stock_counts(counted_at);