# Blaze API Credentials Verification Checklist

## What Owner Needs to Check in Blaze:

### **1. Partner Key Status**
- Partner Key: `30117b29cdcf44d7a7f4a766e8d398e7`
- Status: Is it promoted to production?
- Permissions: What endpoints does it have access to?

### **2. Dispensary Key Status**
- Dispensary Key: `48f5dd5e57234145a233c79e66285925`
- Status: Is it active?
- Linkage: Is it linked to the correct dispensary/location?

### **3. API Access Status**
- Is the API access active?
- Has it been approved by Blaze?
- Any pending approvals or restrictions?

### **4. Environment Status**
- Are these keys for production or development/staging?
- Should we be using different keys for production?

### **5. Key Generation Location**
- Where in Blaze were these keys generated?
- Settings → API → Partner Keys?
- Or Developer Portal?

### **6. Additional Info Needed**
- Dispensary ID (if separate from key)
- Shop ID (if multiple locations)
- Company ID (may be needed for some endpoints)

## Current Error:
"Invalid PARTNER or Developer API Key"

This suggests either:
- Keys not activated/promoted to production
- Wrong keys for production environment
- Access not yet approved

## Contact Blaze Support if Needed:
- Email: integrations@blaze.me
- Mention: "API authentication failing - need key verification"
