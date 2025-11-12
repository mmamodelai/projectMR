# Budtender Campaign: Two-Tier Strategy

## Overview
The budtender CSV contains sign-ups from **April 2024 to November 2025**. Many older budtenders already received their t-shirts months ago, so we need **two different message types**.

## Date-Based Segmentation

### 🆕 NEW Budtenders (September 18, 2025 or later)
**Status**: Just signed up, haven't received t-shirts yet  
**Message Type**: T-shirt welcome & confirmation  
**Strategy**: `welcome`  
**Campaign**: `BT_Engagement_v1`

**Message Template**:
```
Hi {name}, it's Luis from MOTA. Thanks for signing up. 
I am excited to welcome you to MOTA's Budtender Program. 

Please reply to confirm your welcome gift details: 
We have you down for a {size} t-shirt with a {logo} logo 
on the front and {sleeve} on the sleeve. 

Let me know if you want any changes. - Luis
```

### 🕐 OLD Budtenders (September 14, 2025 or earlier)
**Status**: Already received t-shirts months ago  
**Message Type**: Product feedback & education  
**Strategy**: `product_feedback`  
**Campaign**: `BT_Product_Feedback_v1`

**Message Template**:
```
Hey {first_name},

It's Luis from MOTA!

Reaching out to see if you had a chance to try the joints 
we dropped at {dispensary}.

Our intention is for each staff member to try a broad 
selection of our flower; we're hoping each of you received 
1 joint of each of the 3-4 different strains we dropped off.

To help you better know our products, please click this link 
of Educational Material on MOTA FLOWER.

https://www.motarewards.com/educational

Hope you enjoy it and that you'll feel more confident 
recommending it.

I'd really appreciate feedback on the product; please reply 
to this text to let me know what you think.

-Luis
```

## Database Updates

### How It Works
1. Script reads `MOTA Merchandise BT Info SHEET 2` CSV
2. Parses timestamp column to identify OLD vs NEW
3. Updates `campaign_messages` table:
   - OLD: Replace message, change strategy to `product_feedback`
   - NEW: Keep original message (no changes)

### To Run
```bash
update_old_budtenders.bat
```

### What Gets Updated
For OLD budtenders only:
- `message_content` → New product feedback message
- `strategy_type` → `'product_feedback'`
- `campaign_name` → `'BT_Product_Feedback_v1'`
- `reasoning` → Preserved (dispensary name, etc.)

## Expected Results

From the CSV (349 total entries):
- **~230-240 OLD budtenders** (4/2024 - 9/14/2025) → Product feedback message
- **~54 NEW budtenders** (9/18/2025 - 11/2/2025) → T-shirt welcome message

## SMS Viewer Display
In the "First Texts" tab, you'll see both message types:
- Look for `strategy_type` to distinguish:
  - `welcome` = T-shirt welcome
  - `product_feedback` = Joints/feedback request

## Why This Matters
- **Avoids confusion**: Don't ask about t-shirts people got 6+ months ago
- **Re-engages OLD budtenders**: Shifts focus to product knowledge
- **Maintains relevance**: Each group gets appropriate message for their stage
- **Better conversion**: Context-appropriate messaging = higher response rates

## Files
- `update_old_budtender_messages.py` - Main update script
- `update_old_budtenders.bat` - Windows launcher
- `SMSSUG/notesforcampaign.md` - Source for new message template
- `SMSSUG/MOTA Merchandise BT Info SHEET 2 (Responses) - Form Responses 1 (1).csv` - Source data

---

**✅ EXECUTED SUCCESSFULLY - 2025-11-08**

**Final Results:**
- 🎯 300 OLD budtenders updated with product feedback message
- 🆕 46 NEW budtenders kept original t-shirt welcome message  
- ✅ 100% success rate (0 errors)
- 📊 Total messages in database: 346 budtender campaigns ready for approval

Last Updated: 2025-11-08  
Status: ✅ **COMPLETED**  
Impact: 300 message updates (87% of all budtender campaigns)

