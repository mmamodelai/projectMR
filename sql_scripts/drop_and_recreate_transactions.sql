-- ============================================================
-- DROP AND RECREATE transactions_blaze
-- ============================================================

-- Step 1: Drop existing table
DROP TABLE IF EXISTS public.transactions_blaze CASCADE;

-- Step 2: Recreate with UNIQUE constraint
CREATE TABLE public.transactions_blaze (
  id bigint NOT NULL DEFAULT nextval('transactions_blaze_id_seq'::regclass),
  transaction_id text NOT NULL UNIQUE,
  customer_id text,
  date timestamp with time zone NOT NULL,
  shop_location text,
  staff_name text,
  terminal text,
  payment_type text,
  total_amount numeric,
  total_tax numeric,
  discounts numeric,
  loyalty_points_earned numeric,
  loyalty_points_spent numeric,
  shop_id text,
  seller_id text,
  terminal_id text,
  blaze_status text,
  trans_type text,
  start_time timestamp with time zone,
  end_time timestamp with time zone,
  completed_time timestamp with time zone,
  blaze_created timestamp with time zone,
  blaze_modified timestamp with time zone,
  last_synced_at timestamp with time zone DEFAULT now(),
  sync_status text DEFAULT 'pending'::text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  trans_no text,
  queue_type text,
  note text,
  memo text,
  checkin_time timestamp with time zone,
  processed_time timestamp with time zone,
  waiting_time_ms integer,
  processing_time_ms integer,
  time_zone text,
  delivery_address jsonb,
  payment_received numeric,
  paid_amount numeric,
  balance numeric,
  credit_card_fee numeric,
  subtotal numeric,
  cart_data jsonb,
  payments_data jsonb,
  metrc_id bigint,
  metrc_sale_time timestamp with time zone,
  trace_submit_status text,
  compliance_id text,
  compliance_sale_time timestamp with time zone,
  consumer_type text,
  purchase_type text,
  sales_channel text,
  internal_sales_channel text,
  raw_data jsonb,
  CONSTRAINT transactions_blaze_pkey PRIMARY KEY (id),
  CONSTRAINT transactions_blaze_transaction_id_unique UNIQUE (transaction_id)
);

-- Step 3: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_customer_id 
ON transactions_blaze(customer_id);

CREATE INDEX IF NOT EXISTS idx_transactions_date 
ON transactions_blaze(date);

CREATE INDEX IF NOT EXISTS idx_transactions_created_at 
ON transactions_blaze(created_at);

