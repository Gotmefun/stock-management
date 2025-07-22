-- สร้างตารางเพิ่มเติมสำหรับระบบ Stock Counting
-- รันใน Supabase SQL Editor

-- 1. ตาราง stock_counts สำหรับเก็บข้อมูลการนับสต๊อก
CREATE TABLE IF NOT EXISTS stock_counts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    counted_quantity INTEGER NOT NULL DEFAULT 0,
    counter_name VARCHAR(100),
    image_url TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. ตาราง inventory สำหรับเก็บข้อมูลคงเหลือ
CREATE TABLE IF NOT EXISTS inventory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    current_quantity INTEGER DEFAULT 0,
    minimum_quantity INTEGER DEFAULT 0,
    maximum_quantity INTEGER DEFAULT 100,
    last_counted_at TIMESTAMP WITH TIME ZONE,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint เพื่อป้องกันข้อมูลซ้ำ
    UNIQUE(product_id, branch_id)
);

-- 3. ตาราง sales สำหรับเก็บข้อมูลการขาย
CREATE TABLE IF NOT EXISTS sales (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    quantity_sold INTEGER NOT NULL DEFAULT 0,
    unit_price DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    sale_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- สร้าง indexes เพื่อความเร็ว
CREATE INDEX IF NOT EXISTS idx_stock_counts_product ON stock_counts(product_id);
CREATE INDEX IF NOT EXISTS idx_stock_counts_branch ON stock_counts(branch_id);
CREATE INDEX IF NOT EXISTS idx_stock_counts_created ON stock_counts(created_at);

CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_branch ON inventory(branch_id);

CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_branch ON sales(branch_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);

-- Enable Row Level Security
ALTER TABLE stock_counts ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;

-- สร้าง policies
CREATE POLICY "Enable all access for stock_counts" ON stock_counts FOR ALL USING (true);
CREATE POLICY "Enable all access for inventory" ON inventory FOR ALL USING (true);
CREATE POLICY "Enable all access for sales" ON sales FOR ALL USING (true);

-- Insert sample data for inventory
INSERT INTO inventory (product_id, branch_id, current_quantity, minimum_quantity, maximum_quantity)
SELECT 
    p.id as product_id,
    b.id as branch_id,
    0 as current_quantity,
    p.reorder_level as minimum_quantity,
    p.max_stock_level as maximum_quantity
FROM products p
CROSS JOIN branches b
ON CONFLICT (product_id, branch_id) DO NOTHING;

SELECT 'ตารางเพิ่มเติมสำหรับระบบ Stock Counting ถูกสร้างสำเร็จแล้ว' as status;