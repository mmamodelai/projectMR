# Campaign Message Template: Product Feedback (OLD Budtenders)

**Target Audience**: Budtenders who signed up BEFORE 9/14/2025 (already received merch)  
**Purpose**: Follow-up on product samples, gather feedback, offer educational materials  
**Format**: Multi-bubble SMS (8 separate messages for clean display)  
**iPhone Limit**: 150 chars per bubble (NOT 160 - tested on iPhone)

---

## Message Bubbles (send as 8 separate SMS)

### Bubble 1: Greeting + Context
```
Hi {first_name}: Its Mota Luis, reaching out to see if you had a chance to try out the Fatty Joints we dropped at {dispensary}.
```
**Length**: 119 chars ✓

---

### Bubble 2: Intent
```
My intention is for you to try a broad selection of our flower; hoping you tried each strain.
```
**Length**: 93 chars ✓

---

### Bubble 3: Offer to Resupply
```
If you didn't get all the samples, text me back; we'll pack some specifically for you.
```
**Length**: 86 chars ✓

---

### Bubble 4: Educational Material Intro
```
To help you better know our products, click this link to Mota Education Materials; organized by Flower, Vapes & Concentrates:
```
**Length**: 125 chars ✓ (removed "please" to shorten)

---

### Bubble 5: Link (standalone for easy clicking)
```
https://www.motarewards.com/educational
```
**Length**: 39 chars ✓

---

### Bubble 6: Hope Statement
```
Hope you enjoy the Fatty Joints & feel more confident recommending MOTA Flower.
```
**Length**: 79 chars ✓ (removed "that you'll" to shorten)

---

### Bubble 7: Feedback Request
```
I'd appreciate feedback on the joint samples; let me know what you think.
```
**Length**: 73 chars ✓ (removed "please" to shorten)

---

### Bubble 8: Additional Product Sampling (OPTIMIZED for iPhone)
```
Text back if you'd like to try other products; we'll bring them through the right channels.
```
**Length**: 91 chars ✓ (SHORTENED from 127 to avoid iPhone split)

---

## Implementation Notes

- **Each bubble = separate SMS**: Prevents awkward mid-sentence breaks
- **All bubbles under 160 chars**: Ensures clean single-bubble display
- **Link isolated**: Makes it easy to tap without extra text
- **Natural pauses**: Each bubble contains a complete thought
- **Variables**: Replace `{first_name}` and `{dispensary}` with actual values

---

## Next Steps

- [x] Test with real budtenders (Luis Bobadilla - ✓)
- [x] Create separate template for NEW budtenders (see below)
- [ ] Monitor response rates
- [ ] Collect feedback for AI training

---
---

# Campaign Message Template: T-Shirt Welcome (NEW Budtenders)

**Target Audience**: Budtenders who signed up on/after 9/18/2025 (need merch)  
**Purpose**: Welcome to program, confirm t-shirt details  
**Format**: Multi-bubble SMS (3 separate messages for clean display)  
**iPhone Limit**: 150 chars per bubble (NOT 160 - tested on iPhone)

---

## Message Bubbles (send as 3 separate SMS)

### Bubble 1: Greeting + Welcome + Confirmation Prompt
```
Hi {first_name},

Its Mota-Luis

Welcome to MOTA's Budtender Program!

Please reply to confirm your welcome gift details:
```
**Length**: 134 chars ✓

---

### Bubble 2: T-Shirt Details
```
We have you down for a {size} t-shirt with a {logo} logo on the front and {dispensary} on the sleeve.
```
**Length**: ~97 chars ✓ (varies by size/logo/dispensary)

---

### Bubble 3: Change Request
```
Let me know if you want any changes.
```
**Length**: 36 chars ✓

---

## Implementation Notes

- **3 bubbles = 3 separate SMS**: Clean, easy to read
- **Natural line breaks in Bubble 1**: Creates visual spacing
- **All bubbles under 150 chars**: iPhone-optimized
- **Removed "I'm excited for you"**: More professional, concise
- **Variables**: Replace `{first_name}`, `{size}`, `{logo}`, `{dispensary}` with actual values

---

## Database Format

When storing in `campaign_messages.message_content`, use `[BUBBLE]` markers:

```
Hi {first_name},

Its Mota-Luis

Welcome to MOTA's Budtender Program!

Please reply to confirm your welcome gift details:

[BUBBLE]

We have you down for a {size} t-shirt with a {logo} logo on the front and {dispensary} on the sleeve.

[BUBBLE]

Let me know if you want any changes.
```

The sending system will split on `[BUBBLE]` and send each as a separate SMS.
