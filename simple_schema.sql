-- Quick Database Setup for Testing Stock Counting

-- Create basic tables
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

CREATE TABLE IF NOT EXISTS inventory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    branch_id UUID REFERENCES branches(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,
    last_counted_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, branch_id)
);

CREATE TABLE IF NOT EXISTS stock_counts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    product_id UUID REFERENCES products(id),
    branch_id UUID REFERENCES branches(id),
    counted_quantity INTEGER NOT NULL,
    system_quantity INTEGER,
    variance INTEGER,
    counter_name VARCHAR(100) NOT NULL,
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

-- Insert sample products for testing
INSERT INTO products (sku, barcode, name, description, category, brand, unit, cost_price, selling_price, reorder_level, max_stock_level) VALUES 
('TEST001', '1234567890123', 'นมสด เมจิ 1000 มล.', 'นมสดพาสเจอร์ไรส์ เมจิ 1000 มิลลิลิตร', 'เครื่องดื่ม', 'เมจิ', 'กล่อง', 45.00, 59.00, 20, 100),
('TEST002', '8851019991234', 'ข้าวโอ๊ต เควกเกอร์ 500 กรัม', 'ข้าวโอ๊ตสำหรับอาหารเช้า', 'อาหารแห้ง', 'เควกเกอร์', 'กล่อง', 120.00, 149.00, 10, 50),
('TEST003', '8850999999999', 'น้ำแร่ สิงห์ 600 มล.', 'น้ำแร่ธรรมชาติ สิงห์ 600 มิลลิลิตร', 'เครื่องดื่ม', 'สิงห์', 'ขวด', 8.00, 12.00, 50, 200),
('TEST004', '1111111111111', 'ชาเขียว โออิชิ 500 มล.', 'ชาเขียวพร้อมดื่ม โออิชิ 500 มิลลิลิตร', 'เครื่องดื่ม', 'โออิชิ', 'ขวด', 15.00, 20.00, 30, 120),
('TEST005', '2222222222222', 'บะหมี่กึ่งสำเร็จรูป มาม่า', 'บะหมี่กึ่งสำเร็จรูป รสหมูต้ม', 'อาหารกึ่งสำเร็จรูป', 'มาม่า', 'ซอง', 6.00, 9.00, 100, 500)
ON CONFLICT (sku) DO NOTHING;