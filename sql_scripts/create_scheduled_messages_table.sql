-- Create scheduled_messages table
-- For scheduling SMS messages with specific send times

CREATE TABLE IF NOT EXISTS public.scheduled_messages (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    phone_number text NOT NULL,
    customer_name text,
    message_content text NOT NULL,
    scheduled_for timestamp with time zone NOT NULL,
    status text NOT NULL DEFAULT 'scheduled',
    campaign_message_id bigint,
    campaign_name text,
    sent_at timestamp with time zone,
    error_message text,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now())
);

-- Create index for efficient querying
CREATE INDEX IF NOT EXISTS idx_scheduled_messages_status_time 
    ON public.scheduled_messages(status, scheduled_for);

-- Create index for phone lookups
CREATE INDEX IF NOT EXISTS idx_scheduled_messages_phone 
    ON public.scheduled_messages(phone_number);

-- Enable RLS (if needed)
ALTER TABLE public.scheduled_messages ENABLE ROW LEVEL SECURITY;

-- Add policy for authenticated users
CREATE POLICY "Allow all operations for authenticated users" 
    ON public.scheduled_messages
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Add policy for anon users (API calls)
CREATE POLICY "Allow all operations for anon users" 
    ON public.scheduled_messages
    FOR ALL
    TO anon
    USING (true)
    WITH CHECK (true);

-- Comments
COMMENT ON TABLE public.scheduled_messages IS 'Scheduled SMS messages with specific send times';
COMMENT ON COLUMN public.scheduled_messages.scheduled_for IS 'When to send the message (UTC)';
COMMENT ON COLUMN public.scheduled_messages.status IS 'scheduled, sent, cancelled, failed';
COMMENT ON COLUMN public.scheduled_messages.message_content IS 'Message content (may include [BUBBLE] markers)';

