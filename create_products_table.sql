-- สร้างตาราง products ใหม่ใน Supabase
-- รันใน Supabase SQL Editor

DROP TABLE IF EXISTS products CASCADE;

CREATE TABLE products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    barcode VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'สินค้าทั่วไป',
    brand VARCHAR(100) DEFAULT 'ไม่ระบุ',
    unit VARCHAR(20) DEFAULT 'ชิ้น',
    cost_price DECIMAL(10,2) DEFAULT 0.00,
    selling_price DECIMAL(10,2) DEFAULT 0.00,
    reorder_level INTEGER DEFAULT 10,
    max_stock_level INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- สร้าง indexes เพื่อความเร็ว
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_name ON products(name);

-- Enable Row Level Security (RLS)
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- สร้าง policy เพื่อให้สามารถเข้าถึงข้อมูลได้
CREATE POLICY "Enable read access for all users" ON products FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON products FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON products FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON products FOR DELETE USING (true);

-- แสดงผลลัพธ์
SELECT 'ตาราง products ถูกสร้างสำเร็จแล้ว' as status;