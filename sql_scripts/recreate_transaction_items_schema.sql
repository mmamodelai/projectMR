-- ============================================================
-- RECREATE transaction_items_blaze - Clean Schema
-- ============================================================
-- Run this AFTER dropping the old table

CREATE TABLE public.transaction_items_blaze (
  id bigint NOT NULL DEFAULT nextval('transaction_items_blaze_id_seq'::regclass),
  transaction_id text NOT NULL,
  product_id text,
  product_sku text,
  product_name text,
  brand text,
  category text,
  quantity numeric,
  unit_price numeric,
  total_price numeric,
  cost numeric,
  discount numeric,
  tax numeric,
  calc_tax numeric,
  final_price numeric,
  tax_type text,
  tax_order text,
  excise_tax numeric,
  tax_result jsonb,
  tax_rate_details jsonb,
  discount_type text,
  calc_discount numeric,
  discount_notes text,
  status text,
  fulfilled boolean DEFAULT true,
  bundle boolean DEFAULT false,
  bundle_parent_id text,
  mix_matched boolean DEFAULT false,
  loyalty_accrual boolean DEFAULT true,
  order_item_id text,
  weight_key text,
  quantity_logs jsonb,
  raw_data jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT transaction_items_blaze_pkey PRIMARY KEY (id)
);

-- ============================================================
-- CREATE UNIQUE INDEX to prevent future duplicates
-- ============================================================
-- This prevents inserting the same transaction item twice
CREATE UNIQUE INDEX IF NOT EXISTS idx_transaction_items_unique 
ON transaction_items_blaze (transaction_id, product_id, quantity, unit_price) 
NULLS NOT DISTINCT;

-- ============================================================
-- Other indexes for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_transaction_items_transaction_id 
ON transaction_items_blaze(transaction_id);

CREATE INDEX IF NOT EXISTS idx_transaction_items_product_id 
ON transaction_items_blaze(product_id);

CREATE INDEX IF NOT EXISTS idx_transaction_items_created_at 
ON transaction_items_blaze(created_at);

