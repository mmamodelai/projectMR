# Master Queue System - SMS Scheduler
**Date**: November 10, 2025  
**Status**: ✅ COMPLETE

## Overview

The **Master Queue System** transforms SMS scheduling from discrete batches into a continuous "river" or "flow" of messages. Think of it as a conveyor belt that keeps moving - you can add messages anytime, and they automatically slot into the queue with proper spacing.

## Key Features

### 1. 📊 Selection Counter
**Location**: Next to stats at top of Campaign Master View

**What It Shows**:
```
Total: 258 | APR: 136 | ... ✓ 15 selected
                            ↑ New counter!
```

- Updates in real-time as you select/deselect messages
- Blue bold text for easy visibility
- Helps you track bulk operations

### 2. 🎯 Two Scheduling Modes

#### Mode 1: 📅 **Use Target Time** (Classic Bullseye)
- Set specific target date/time
- Choose Bullseye position (Begins/Middle/Ends at)
- Perfect for campaign launches at specific times
- **Use Case**: "Launch at 5pm on Tuesday"

#### Mode 2: ➕ **Add to Current Queue** (NEW!)
- Finds last scheduled message
- Continues from there automatically
- No date/time selection needed!
- **Use Case**: "Just add these to the queue"

### 3. 🌊 Master Queue Logic

#### How It Works:

**Step 1**: Query database for last scheduled message
```python
SELECT scheduled_for FROM campaign_messages 
WHERE status = 'SCH' 
ORDER BY scheduled_for DESC 
LIMIT 1
```

**Step 2**: Continue from that time
```
Last scheduled: 2:13 PM
New messages start: 2:19 PM (last + 6 min random spacing)
```

**Step 3**: Apply spacing rules
- Random 5-7 minutes between messages
- Break every 8-10 messages (adds 10-15 min)
- Respect scheduling windows (9am-8pm)

**Step 4**: Handle overnight scheduling
```
Current time: 7:55 PM
Next message would be: 8:02 PM ❌
→ Jump to: 9:00 AM next day ✅
```

## Scheduling Window Rules

### Business Hours: 9am - 8pm (PST)

**Before 9am**:
```
Scheduled time: 8:30 AM
→ Adjusted to: 9:00 AM (same day)
```

**After 8pm**:
```
Scheduled time: 8:15 PM
→ Adjusted to: 9:00 AM (next day)
```

**During business hours**:
```
Scheduled time: 2:15 PM
→ No adjustment needed ✅
```

## Order Preservation

Messages are scheduled in the **exact order** they appear in your selection (top to bottom).

### Example: Scheduling by Dispensary

**1. Sort by Dispensary** (click header)
```
firehouse
firehouse
phenos
phenos
X1
X1
```

**2. Select a group** (Shift+click)
```
✓ firehouse - Alice
✓ firehouse - Bob
✓ firehouse - Carol
```

**3. Schedule them**
```
Alice   → 2:19 PM (first in list)
Bob     → 2:25 PM (second in list)
Carol   → 2:31 PM (third in list)
```

**Order is preserved!** Top message = earliest time, bottom message = latest time.

## Complete Workflow Example

### Scenario: Scheduling 3 waves of messages

**Wave 1: Product Feedback (11am Tuesday)**
1. Filter: `BT_Product_Feedback_v1`
2. Sort by: Dispensary
3. Select: All X1 messages (12 messages)
4. Right-click → Schedule
5. Mode: **Use Target Time**
6. Date: `11/12/2025` (shows "📅 Tuesday")
7. Time: `11:00 AM`
8. Position: `Begins at`
9. Click: **Schedule Messages**

**Result**:
```
11:00 AM - First X1 message
11:05 AM - Second X1 message
...
11:55 AM - Last X1 message (12 messages @ 5-7 min each)
```

---

**Wave 2: Engagement (add to queue)**
1. Filter: `BT_Engagement_v1`
2. Select: All phenos messages (8 messages)
3. Right-click → Schedule
4. Mode: **➕ Add to Current Queue**
5. Click: **Schedule Messages**

**Result** (automatically continues from Wave 1):
```
11:00 AM - First X1 message
...
11:55 AM - Last X1 message
12:02 PM - First phenos message ← Continues here!
12:08 PM - Second phenos message
...
12:50 PM - Last phenos message
```

---

**Wave 3: Late Afternoon (more to queue)**
1. Select: Another 5 messages
2. Right-click → Schedule
3. Mode: **➕ Add to Current Queue**
4. Click: **Schedule Messages**

**Result** (keeps flowing):
```
... (previous messages)
12:50 PM - Last phenos message
12:56 PM - New message 1 ← Continues!
1:03 PM  - New message 2
...
1:25 PM  - New message 5
```

---

**If you keep adding throughout the day, and it reaches 8pm:**
```
7:55 PM - Message X
8:02 PM - Would be next ❌
→ 9:00 AM (next day) - Message Y ✅ (jumps overnight!)
9:06 AM - Message Z
```

## Master Queue Benefits

### 1. 🎯 **Flexibility**
- Schedule some messages at specific times
- Add others to the queue later
- Mix and match both modes

### 2. 🌊 **Flow/River Concept**
- Continuous stream of messages
- Natural spacing (5-7 min random)
- Professional appearance

### 3. 📅 **Automatic Scheduling**
- No manual time calculations
- Respects business hours
- Handles overnight automatically

### 4. 🔄 **Order Control**
- Sort by any column (dispensary, campaign, name)
- Selection order = scheduling order
- Keep groups together

### 5. ⚡ **Speed**
- No need to pick times for every message
- Just "add to queue" and go
- Queue manages itself

## Tips & Best Practices

### 1. **Use Target Time for Launch Campaigns**
```
New product launch at 2pm? → Use Target Time mode
Want to end campaign at 5pm? → Use "Ends at" position
```

### 2. **Use Add to Queue for Ongoing Communications**
```
Daily customer outreach? → Add to Queue
Follow-ups and reminders? → Add to Queue
Continuous engagement? → Add to Queue
```

### 3. **Group by Dispensary**
```
Sort by Dispensary → Select one location → Schedule
All messages from that location stay together in queue!
```

### 4. **Monitor Your Queue**
```
Check "Scheduled" tab to see your queue
See exact times for all messages
Adjust if needed (right-click → Roll Back)
```

### 5. **Start Fresh Each Week**
```
Monday morning: Set first batch with Target Time (9am)
Rest of week: Add to Queue as needed
Queue naturally flows throughout the week!
```

## Troubleshooting

### Issue: "Queue starts too late"
**Solution**: Set first message with Target Time, then add rest to queue

### Issue: "Messages scheduled overnight"
**Expected**: If queue reaches 8pm, it continues at 9am next day automatically

### Issue: "Order seems wrong"
**Check**: Selection order in tree (top to bottom)
**Fix**: Re-sort by desired column, reselect in correct order

### Issue: "Want to insert message in middle of queue"
**Workaround**: 
1. Roll back messages after insertion point
2. Add new message to queue
3. Re-add rolled back messages

## Technical Details

### Database Query (Find Last Scheduled)
```python
bt_supabase.table('campaign_messages')
    .select('scheduled_for')
    .eq('status', 'SCH')
    .order('scheduled_for', desc=True)
    .limit(1)
    .execute()
```

### Time Window Check
```python
def next_valid_time(dt):
    """Ensure time is within 9am-8pm window"""
    hour = dt.hour
    if hour < 9:
        dt = dt.replace(hour=9, minute=0)  # Jump to 9am
    elif hour >= 20:
        dt = dt + timedelta(days=1)         # Next day
        dt = dt.replace(hour=9, minute=0)   # at 9am
    return dt
```

### Spacing Logic
```python
for i in range(num_messages):
    schedule_times.append(current_time)
    
    spacing = random.randint(5, 7)  # Random 5-7 min
    
    # Break every 8-10 messages
    if (i + 1) % random.randint(8, 10) == 0:
        spacing += random.randint(10, 15)  # Extra 10-15 min
    
    current_time += timedelta(minutes=spacing)
    current_time = next_valid_time(current_time)  # Check windows
```

## Future Enhancements

### Possible Additions:
1. **Queue Preview**: Visual timeline showing all scheduled messages
2. **Queue Stats**: "Queue ends at 4:30 PM" / "12 messages in queue"
3. **Pause Queue**: Temporarily hold scheduling
4. **Priority Insert**: Add message to front of queue
5. **Queue Templates**: Save common scheduling patterns

---

**Last Updated**: November 10, 2025  
**Version**: v3.0 (Master Queue System)  
**Status**: ✅ PRODUCTION READY

