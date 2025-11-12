# ⚠️ CRITICAL: SQL Function Setup

## **ERROR: "Could not find the function public.schedule_approved_messages"**

### **WHAT HAPPENED:**
The scheduling buttons won't work until you deploy the SQL function to Supabase.

---

## **FIX (2 MINUTES):**

### **Step 1: Open Supabase SQL Editor**
1. Go to: https://kiwmwoqrguyrcpjytgte.supabase.co
2. Click: **SQL Editor** (left sidebar)
3. Click: **New Query**

### **Step 2: Run This SQL**

Copy and paste this ENTIRE block into the SQL editor:

```sql
-- =====================================================================
-- FLEXIBLE BATCH SCHEDULER
-- =====================================================================

DROP FUNCTION IF EXISTS schedule_approved_messages(integer);
DROP FUNCTION IF EXISTS schedule_approved_messages();

CREATE OR REPLACE FUNCTION schedule_approved_messages(batch_size integer DEFAULT 3)
RETURNS TABLE(scheduled_count int, next_send_time timestamptz)
LANGUAGE plpgsql
AS $$
DECLARE
    last_scheduled_time timestamptz;
    next_time timestamptz;
    random_delay_minutes int;
    msg RECORD;
    scheduled int := 0;
    actual_limit int;
BEGIN
    IF batch_size IS NULL OR batch_size <= 0 THEN
        actual_limit := 999999;
    ELSE
        actual_limit := batch_size;
    END IF;
    
    SELECT MAX(scheduled_for) INTO last_scheduled_time
    FROM campaign_messages
    WHERE status = 'SCH';
    
    IF last_scheduled_time IS NULL OR last_scheduled_time < NOW() THEN
        last_scheduled_time := NOW();
    END IF;
    
    FOR msg IN 
        SELECT id, phone_number, customer_name, message_content
        FROM campaign_messages
        WHERE status = 'APR'
        ORDER BY generated_at ASC
        LIMIT actual_limit
    LOOP
        random_delay_minutes := 5 + floor(random() * 3)::int;
        next_time := last_scheduled_time + (random_delay_minutes || ' minutes')::interval;
        
        WHILE NOT is_business_hours_pst(next_time) LOOP
            IF EXTRACT(DOW FROM (next_time AT TIME ZONE 'America/Los_Angeles')) = 0 THEN
                next_time := date_trunc('day', next_time AT TIME ZONE 'America/Los_Angeles') 
                           + interval '1 day' 
                           + interval '10 hours 15 minutes';
                next_time := next_time AT TIME ZONE 'America/Los_Angeles';
            ELSIF EXTRACT(DOW FROM (next_time AT TIME ZONE 'America/Los_Angeles')) = 6 THEN
                IF EXTRACT(HOUR FROM (next_time AT TIME ZONE 'America/Los_Angeles')) >= 21 THEN
                    next_time := date_trunc('day', next_time AT TIME ZONE 'America/Los_Angeles') 
                               + interval '2 days' 
                               + interval '10 hours 15 minutes';
                    next_time := next_time AT TIME ZONE 'America/Los_Angeles';
                ELSE
                    next_time := date_trunc('day', next_time AT TIME ZONE 'America/Los_Angeles') 
                               + interval '11 hours';
                    next_time := next_time AT TIME ZONE 'America/Los_Angeles';
                END IF;
            ELSE
                IF EXTRACT(HOUR FROM (next_time AT TIME ZONE 'America/Los_Angeles')) < 10 THEN
                    next_time := date_trunc('day', next_time AT TIME ZONE 'America/Los_Angeles') 
                               + interval '10 hours 15 minutes';
                    next_time := next_time AT TIME ZONE 'America/Los_Angeles';
                ELSE
                    next_time := date_trunc('day', next_time AT TIME ZONE 'America/Los_Angeles') 
                               + interval '1 day' 
                               + interval '10 hours 15 minutes';
                    next_time := next_time AT TIME ZONE 'America/Los_Angeles';
                END IF;
            END IF;
        END LOOP;
        
        UPDATE campaign_messages
        SET 
            status = 'SCH',
            scheduled_for = next_time,
            updated_at = NOW()
        WHERE id = msg.id;
        
        scheduled := scheduled + 1;
        last_scheduled_time := next_time;
    END LOOP;
    
    RETURN QUERY SELECT scheduled, last_scheduled_time;
END;
$$;

GRANT EXECUTE ON FUNCTION schedule_approved_messages(integer) TO authenticated, anon;
```

### **Step 3: Click "Run" (or press Ctrl+Enter)**

You should see: **Success. No rows returned**

---

## **TEST IT:**

1. Go back to SMS Viewer
2. Click **Campaign Master** or **Approved** tab
3. Type `3` in the box
4. Click **📅 Schedule**

Should work now!

---

## **TROUBLESHOOTING:**

**"Function is_business_hours_pst does not exist"**
- Run the full `sql_scripts/create_campaign_scheduler.sql` first
- It creates all the helper functions

**Still getting errors?**
- Contact Luis with the exact error message
- Screenshot the Supabase SQL Editor error

---

## **WHY THIS HAPPENS:**

SQL functions are server-side code that must be deployed to your Supabase instance.
They don't automatically sync with the Python code.

**One-time setup**, then it works forever!


