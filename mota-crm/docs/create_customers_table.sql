-- MoTa CRM Customer Intelligence Table
-- Migration: create_customers_table
-- Purpose: Store customer data from MEMBER_PERFORMANCE.csv for AI queries
-- Date: 2025-10-10

-- Drop table if exists (for clean re-creation during development)
DROP TABLE IF EXISTS customers CASCADE;

-- Create customers table
CREATE TABLE customers (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Identity
    member_id TEXT UNIQUE NOT NULL,
    name TEXT,
    phone TEXT,
    email TEXT,
    
    -- Loyalty Metrics
    loyalty_points DECIMAL(10, 2) DEFAULT 0,
    total_visits INTEGER DEFAULT 0,
    total_sales INTEGER DEFAULT 0,
    total_refunds INTEGER DEFAULT 0,
    
    -- Financial Metrics
    gross_sales DECIMAL(10, 2) DEFAULT 0,
    gross_refunds DECIMAL(10, 2) DEFAULT 0,
    avg_sale_value DECIMAL(10, 2) DEFAULT 0,
    lifetime_value DECIMAL(10, 2) DEFAULT 0,
    
    -- Customer Profile
    customer_type TEXT,
    member_group TEXT,
    marketing_source TEXT,
    state TEXT,
    zip_code TEXT,
    
    -- Important Dates
    date_joined DATE,
    last_visited DATE,
    
    -- Calculated Segments (updated by triggers or batch jobs)
    vip_status TEXT DEFAULT 'New',
    churn_risk TEXT DEFAULT 'Low',
    days_since_last_visit INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for fast AI queries
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_member_id ON customers(member_id);
CREATE INDEX idx_customers_vip_status ON customers(vip_status);
CREATE INDEX idx_customers_last_visited ON customers(last_visited);
CREATE INDEX idx_customers_state ON customers(state);
CREATE INDEX idx_customers_churn_risk ON customers(churn_risk);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate VIP status
CREATE OR REPLACE FUNCTION calculate_vip_status()
RETURNS TRIGGER AS $$
BEGIN
    NEW.vip_status = CASE
        WHEN NEW.total_visits >= 16 THEN 'VIP'
        WHEN NEW.total_visits BETWEEN 6 AND 15 THEN 'Regular'
        WHEN NEW.total_visits BETWEEN 2 AND 5 THEN 'Casual'
        ELSE 'New'
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-calculate VIP status on insert/update
CREATE TRIGGER calculate_customer_vip_status
    BEFORE INSERT OR UPDATE OF total_visits ON customers
    FOR EACH ROW
    EXECUTE FUNCTION calculate_vip_status();

-- Function to calculate churn risk and days since last visit
CREATE OR REPLACE FUNCTION calculate_churn_risk()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate days since last visit
    IF NEW.last_visited IS NOT NULL THEN
        NEW.days_since_last_visit = EXTRACT(DAY FROM NOW() - NEW.last_visited)::INTEGER;
        
        -- Calculate churn risk based on days
        NEW.churn_risk = CASE
            WHEN NEW.days_since_last_visit > 60 THEN 'High'
            WHEN NEW.days_since_last_visit BETWEEN 30 AND 60 THEN 'Medium'
            ELSE 'Low'
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-calculate churn risk on insert/update
CREATE TRIGGER calculate_customer_churn_risk
    BEFORE INSERT OR UPDATE OF last_visited ON customers
    FOR EACH ROW
    EXECUTE FUNCTION calculate_churn_risk();

-- Function to calculate lifetime value
CREATE OR REPLACE FUNCTION calculate_lifetime_value()
RETURNS TRIGGER AS $$
BEGIN
    NEW.lifetime_value = COALESCE(NEW.gross_sales, 0) - COALESCE(NEW.gross_refunds, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-calculate lifetime value
CREATE TRIGGER calculate_customer_lifetime_value
    BEFORE INSERT OR UPDATE OF gross_sales, gross_refunds ON customers
    FOR EACH ROW
    EXECUTE FUNCTION calculate_lifetime_value();

-- Create a view for AI-friendly queries
CREATE OR REPLACE VIEW customer_intelligence AS
SELECT 
    id,
    member_id,
    name,
    phone,
    email,
    loyalty_points,
    total_visits,
    vip_status,
    last_visited,
    days_since_last_visit,
    churn_risk,
    lifetime_value,
    avg_sale_value,
    state,
    zip_code,
    customer_type,
    date_joined
FROM customers
ORDER BY last_visited DESC;

-- Grant permissions (adjust based on your Supabase setup)
-- ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Create policy for service role access (Supabase)
-- CREATE POLICY "Enable read access for service role" ON customers
--     FOR SELECT
--     TO service_role
--     USING (true);

-- Comments for documentation
COMMENT ON TABLE customers IS 'Customer intelligence database from MoTa CRM data';
COMMENT ON COLUMN customers.member_id IS 'Unique member ID from CRM system';
COMMENT ON COLUMN customers.phone IS 'Customer phone number for SMS lookup';
COMMENT ON COLUMN customers.vip_status IS 'Auto-calculated: VIP (16+), Regular (6-15), Casual (2-5), New (1)';
COMMENT ON COLUMN customers.churn_risk IS 'Auto-calculated: High (60+ days), Medium (30-60), Low (<30)';
COMMENT ON COLUMN customers.days_since_last_visit IS 'Auto-calculated from last_visited date';
COMMENT ON COLUMN customers.lifetime_value IS 'Auto-calculated: gross_sales - gross_refunds';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Customers table created successfully!';
    RAISE NOTICE 'Indexes created for fast phone/member_id lookups';
    RAISE NOTICE 'Triggers configured for auto-calculation of VIP status, churn risk, and lifetime value';
    RAISE NOTICE 'Ready to import data from MEMBER_PERFORMANCE.csv';
END $$;

