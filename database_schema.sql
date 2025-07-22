-- Smart Inventory Management System Database Schema
-- Phase 1: Core Tables for Dashboard & Analytics

-- Enable Row Level Security
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- Create enum types
CREATE TYPE user_role AS ENUM ('admin', 'staff');
CREATE TYPE transaction_type AS ENUM ('sale', 'purchase', 'adjustment', 'return');
CREATE TYPE movement_type AS ENUM ('in', 'out', 'adjustment');

-- Users table for authentication
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role user_role DEFAULT 'staff',
    email VARCHAR(100),
    full_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Products table - master product data
CREATE TABLE products (
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

-- Branches/Locations table
CREATE TABLE branches (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    manager_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory table - current stock levels per branch
CREATE TABLE inventory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,
    last_counted_at TIMESTAMP WITH TIME ZONE,
    last_counted_by UUID REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, branch_id)
);

-- Sales table - transaction records
CREATE TABLE sales (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    transaction_number VARCHAR(50) UNIQUE NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    branch_id UUID REFERENCES branches(id),
    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),
    subtotal DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0,
    payment_method VARCHAR(50),
    status VARCHAR(20) DEFAULT 'completed',
    cashier_id UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sales items table - line items for each sale
CREATE TABLE sale_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory movements table - track all stock changes
CREATE TABLE inventory_movements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    movement_type movement_type NOT NULL,
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10,2),
    reference_type VARCHAR(50), -- 'sale', 'purchase', 'adjustment', 'transfer', 'count'
    reference_id UUID, -- ID of the related transaction
    reason TEXT,
    performed_by UUID REFERENCES users(id),
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);

-- Stock counting records (from current system)
CREATE TABLE stock_counts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id),
    branch_id UUID REFERENCES branches(id),
    counted_quantity INTEGER NOT NULL,
    system_quantity INTEGER,
    variance INTEGER,
    counter_name VARCHAR(100) NOT NULL,
    counted_by UUID REFERENCES users(id),
    image_url TEXT,
    notes TEXT,
    counted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alert definitions for smart monitoring
CREATE TABLE alert_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rule_type VARCHAR(50) NOT NULL, -- 'low_stock', 'high_variance', 'no_sales', 'fast_moving'
    conditions JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Active alerts
CREATE TABLE alerts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    rule_id UUID REFERENCES alert_rules(id),
    product_id UUID REFERENCES products(id),
    branch_id UUID REFERENCES branches(id),
    severity VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    is_resolved BOOLEAN DEFAULT false,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_inventory_product_branch ON inventory(product_id, branch_id);
CREATE INDEX idx_sales_date ON sales(transaction_date);
CREATE INDEX idx_sales_branch ON sales(branch_id);
CREATE INDEX idx_sale_items_product ON sale_items(product_id);
CREATE INDEX idx_movements_product_branch ON inventory_movements(product_id, branch_id);
CREATE INDEX idx_movements_date ON inventory_movements(performed_at);
CREATE INDEX idx_stock_counts_product_branch ON stock_counts(product_id, branch_id);
CREATE INDEX idx_stock_counts_date ON stock_counts(counted_at);
CREATE INDEX idx_alerts_unresolved ON alerts(is_resolved) WHERE is_resolved = false;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_inventory_updated_at BEFORE UPDATE ON inventory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default branches (from current system)
INSERT INTO branches (code, name) VALUES 
('MAIN', 'สาขาหลัก'),
('CITY', 'สาขาตัวเมือง'),
('PONGPAI', 'สาขาโป่งไผ่'),
('SCHOOL', 'สาขาหน้าโรงเรียน');

-- Insert default users
INSERT INTO users (username, password_hash, role, full_name) VALUES 
('admin', '$2b$12$rQx7Vz.ZvZr8RKl4Nxs5/.X9k8Jt6vNz5Qw2Er9Ty1Uv3As6Df8Hi', 'admin', 'Administrator'),
('staff', '$2b$12$rQx7Vz.ZvZr8RKl4Nxs5/.X9k8Jt6vNz5Qw2Er9Ty1Uv3As6Df8Hi', 'staff', 'Staff User');

-- Insert sample alert rules
INSERT INTO alert_rules (name, description, rule_type, conditions) VALUES 
('Low Stock Alert', 'Alert when product stock is below reorder level', 'low_stock', '{"threshold_type": "reorder_level"}'),
('High Variance Alert', 'Alert when stock count variance exceeds threshold', 'high_variance', '{"variance_threshold": 10}'),
('No Sales Alert', 'Alert when product has no sales for specified days', 'no_sales', '{"days_threshold": 30}'),
('Fast Moving Alert', 'Alert for products with high turnover', 'fast_moving', '{"velocity_threshold": 100}');