-- Message Feedback Table for Human-in-the-Loop AI Training
-- Stores human edits and reasoning for improving AI message generation

CREATE TABLE IF NOT EXISTS message_feedback (
    id BIGSERIAL PRIMARY KEY,
    
    -- Link to original campaign message
    campaign_message_id BIGINT REFERENCES campaign_messages(id) ON DELETE CASCADE,
    
    -- Original AI suggestion
    suggested_message TEXT NOT NULL,
    suggested_reasoning TEXT,
    suggested_strategy TEXT,
    
    -- Human decision
    action TEXT NOT NULL CHECK (action IN ('approved', 'edited', 'rejected')),
    
    -- If edited, what was sent instead
    final_message TEXT,
    
    -- Human reasoning (THIS IS GOLD for training!)
    human_reasoning TEXT NOT NULL,
    feedback_category TEXT,  -- e.g., 'tone_adjustment', 'vip_treatment', 'discount_change', 'timing_issue'
    
    -- Context
    customer_id TEXT,
    customer_segment TEXT,
    customer_ltv NUMERIC,
    days_since_visit INT,
    
    -- Metadata
    reviewed_by TEXT,  -- Who made the decision (e.g., 'Luis', 'Stephen')
    reviewed_at TIMESTAMPTZ DEFAULT NOW(),
    conductor_sent BOOLEAN DEFAULT FALSE,
    conductor_message_id BIGINT,
    
    -- For AI training
    training_weight NUMERIC DEFAULT 1.0,  -- Higher weight = more important example
    is_training_example BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_message_feedback_campaign_id ON message_feedback(campaign_message_id);
CREATE INDEX IF NOT EXISTS idx_message_feedback_action ON message_feedback(action);
CREATE INDEX IF NOT EXISTS idx_message_feedback_customer ON message_feedback(customer_id);
CREATE INDEX IF NOT EXISTS idx_message_feedback_training ON message_feedback(is_training_example);
CREATE INDEX IF NOT EXISTS idx_message_feedback_created ON message_feedback(created_at);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_message_feedback_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_message_feedback_modtime
    BEFORE UPDATE ON message_feedback
    FOR EACH ROW
    EXECUTE FUNCTION update_message_feedback_timestamp();

COMMENT ON TABLE message_feedback IS 'Stores human edits and reasoning for AI training - captures why humans override AI suggestions';
COMMENT ON COLUMN message_feedback.human_reasoning IS 'The most important field - captures human decision-making logic for AI learning';
COMMENT ON COLUMN message_feedback.training_weight IS 'Higher values = more important examples (e.g., VIP overrides might be weighted higher)';

