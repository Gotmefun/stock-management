-- แก้ไขตาราง stock_counts ให้สมบูรณ์
-- รันใน Supabase SQL Editor

-- ลบตาราง stock_counts เดิม (ถ้ามี)
DROP TABLE IF EXISTS stock_counts CASCADE;

-- สร้างตาราง stock_counts ใหม่ให้สมบูรณ์
CREATE TABLE stock_counts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    barcode VARCHAR(100) NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    counted_quantity INTEGER NOT NULL DEFAULT 0,
    counter_name VARCHAR(100),
    image_url TEXT,
    notes TEXT,
    counted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- สร้าง indexes
CREATE INDEX idx_stock_counts_product ON stock_counts(product_id);
CREATE INDEX idx_stock_counts_branch ON stock_counts(branch_id);
CREATE INDEX idx_stock_counts_barcode ON stock_counts(barcode);
CREATE INDEX idx_stock_counts_counted_at ON stock_counts(counted_at);

-- Enable Row Level Security
ALTER TABLE stock_counts ENABLE ROW LEVEL SECURITY;

-- สร้าง policy
CREATE POLICY "Enable all access for stock_counts" ON stock_counts FOR ALL USING (true);

SELECT 'ตาราง stock_counts แก้ไขเรียบร้อยแล้ว' as status;