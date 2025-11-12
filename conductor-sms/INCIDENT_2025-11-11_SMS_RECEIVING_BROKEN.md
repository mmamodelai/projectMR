# 🚨 INCIDENT REPORT: SMS Receiving Broken (2025-11-11)

## **Summary**
Incoming SMS messages stopped working after MMS configuration was applied to modem. System was able to SEND but not RECEIVE SMS. Issue resolved by resetting modem to SMS defaults and enabling CSMS service.

---

## **Timeline**

### **Working Period**
- System was receiving incoming SMS successfully for months
- Last confirmed working incoming message: ID 997 at 09:33 AM (from +15102464162)
- Messages from multiple users were being received and processed

### **Breaking Change** (~10:00 AM - 3:00 PM)
- User attempted to configure modem for MMS capability
- Applied Mint Mobile MMS settings to modem:
  - APN: "Wholesale"
  - MMSC: http://wholesale.mmsmvno.com/mms/wapenc
  - MMS Port: 8080
  - APN Type: default,supl,mms,ia
- **These settings broke SMS receiving**

### **Symptoms**
- ✅ Outbound SMS: Working perfectly (500+ messages sent)
- ❌ Inbound SMS: Not working (messages not reaching modem)
- ✅ Modem network: Registered on Mint/T-Mobile
- ✅ Signal strength: Excellent (30/31)
- ❌ Modem storage: Always 0/23 (empty, no messages)

### **Troubleshooting Steps Taken**
1. Checked modem storage (ME and SM) - both empty
2. Verified network registration - working
3. Checked signal strength - excellent
4. Tested SMSC configuration - correct
5. Verified Conductor was running and polling
6. Tested with different phones/numbers
7. **User confirmed SIM works in phone** (critical diagnostic)

### **Root Cause Identified**
MMS configuration changed modem settings in a way that disabled SMS receiving:
- Network mode changes
- APN routing changes
- Service type modifications

### **Resolution** (4:18 PM)
1. **Reset modem to SMS defaults:**
   - `ATZ` (factory reset)
   - `AT+CMGF=1` (text mode)
   - `AT+CSCA="+12063130004",145` (T-Mobile SMSC)
   - `AT+CSCS="GSM"` (character set)
   - `AT+CSMP=17,167,0,0` (SMS parameters)
   - `AT+CPMS="ME","ME","ME"` (storage)
   - `AT+CNMI=1,1,0,0,0` (message indication)
   - `AT+CNMP=2` (auto network mode)
   - `AT+CGSMS=3` (prefer packet-switched)
   - `AT&W` (save configuration)

2. **Enabled SMS service explicitly:**
   - `AT+CSMS=0` (enable SMS service)
   - `AT&W` (save)

3. **Verified incoming working:**
   - Messages immediately started arriving
   - IDs 1111-1114 received successfully

---

## **Secondary Issue: RCS vs SMS**

### **Problem**
User's personal phone (Pixel 9 Pro) was sending RCS messages instead of SMS:
- RCS = Rich Communication Services (data-based messaging)
- RCS messages travel over internet/data, NOT cellular SMS network
- Modem can ONLY receive SMS, not RCS

### **Symptoms**
- Messages from user's Pixel didn't arrive
- Messages from other users DID arrive
- User tested from phone that sends SMS = worked
- User tested from Pixel with RCS = didn't work

### **Resolution**
User needs to disable RCS on Pixel 9 Pro:
1. Open Google Messages app
2. Profile icon → Messages settings → RCS chats
3. Toggle OFF "Enable RCS chats"
OR: Long-press send button and select "Send as SMS"

---

## **Key Learnings**

### **1. MMS Configuration Breaks SMS**
- MMS settings (APN, MMSC, etc.) are for **PHONES**, not USB modems
- Applying phone MMS configuration to modem breaks SMS receiving
- Modem SMS and phone MMS use different network pathways

### **2. CSMS Command is Critical**
- `AT+CSMS=0` explicitly enables SMS service on modem
- This command is NOT typically mentioned in basic SMS setup guides
- Without it, modem may accept commands but not receive messages
- Should be included in modem initialization

### **3. Modem vs Phone Behavior**
- **Phone:** Automatically handles SMS/MMS/RCS with complex carrier integration
- **Modem:** Simple device, needs explicit configuration for each service
- Cannot assume phone settings will work on modem

### **4. RCS is NOT SMS**
- RCS messages don't travel through SMS network
- SMS modems cannot receive RCS messages
- Users with modern Android phones (especially Pixels) default to RCS
- Testing must be done with actual SMS, not RCS

### **5. Diagnostic Strategy**
- ✅ Test SIM in phone = carrier/routing issue
- ✅ SIM works in phone = modem configuration issue
- Check both ME and SM storage (messages can go to either)
- Verify SEND works = network is fine, receive config is wrong

---

## **Correct Modem Configuration for SMS**

### **Critical Commands**
```
AT+CMGF=1                          # Text mode
AT+CSCA="+12063130004",145         # SMS center (T-Mobile)
AT+CSCS="GSM"                      # Character set
AT+CSMP=17,167,0,0                 # SMS parameters
AT+CPMS="ME","ME","ME"             # Storage location
AT+CNMI=1,1,0,0,0                  # Keep messages + notify
AT+CNMP=2                          # Auto network (2G/3G/4G)
AT+CGSMS=3                         # Prefer packet-switched SMS
AT+CSMS=0                          # ⭐ ENABLE SMS SERVICE
AT&W                               # Save all settings
```

### **What Each Setting Does**
- **CMGF=1:** Use text mode (not PDU binary mode)
- **CSCA:** SMS center phone number for routing
- **CSCS:** Character encoding for message content
- **CSMP:** How to format/encode SMS messages
- **CPMS:** Where to store incoming messages (ME = modem memory)
- **CNMI=1,1:** Keep messages in storage + send notification to PC
- **CNMP=2:** Allow any network type (auto-select)
- **CGSMS=3:** Use LTE/data for SMS when available, fallback to 2G/3G
- **CSMS=0:** **ENABLE SMS SERVICE** (critical!)
- **AT&W:** Save to non-volatile memory (persists across reboots)

---

## **What NOT to Do**

### **❌ Don't Apply Phone MMS Settings to Modem**
```
# These are for PHONES, not modems:
APN: Wholesale
MMSC: http://wholesale.mmsmvno.com/mms/wapenc
MMS Proxy: (blank)
MMS Port: 8080
APN Type: default,supl,mms,ia
```

### **❌ Don't Change CNMI Without Understanding**
- CNMI=1,1 = Keep messages, notify (WORKING)
- CNMI=2,1 = Buffer messages (seemed logical, but broke receiving)
- CNMI=2,0 = Forward to TE, don't store (causes auto-deletion)
- Stick with what works: **1,1,0,0,0**

### **❌ Don't Test with RCS-Enabled Phones**
- Modern Android phones default to RCS
- RCS messages won't reach SMS modem
- Always test with SMS-only or disable RCS

---

## **Prevention**

### **Before Making Modem Changes**
1. ✅ Document current working configuration
2. ✅ Test that current config is working
3. ✅ Create backup of working settings
4. ✅ Understand what each AT command does
5. ✅ Have rollback plan ready

### **Configuration Backup**
Run these commands and save output:
```
AT+CMGF?
AT+CSCA?
AT+CPMS?
AT+CNMI?
AT+CNMP?
AT+CGSMS?
AT+CSMS?
AT+CSMP?
AT+CSCS?
```

### **Testing Checklist**
- [ ] Send SMS from modem to phone (outbound test)
- [ ] Send SMS from phone to modem (inbound test)
- [ ] Check modem storage with `AT+CPMS?`
- [ ] Check for messages with `AT+CMGL="ALL"`
- [ ] Verify messages appear in database
- [ ] Test from multiple phones/carriers
- [ ] Ensure test phones are sending SMS not RCS

---

## **Files Modified**

### **Created**
- `RESET_MODEM_TO_SMS_DEFAULTS.py` - Script to restore working SMS config
- `CHECK_RECEIVE_SPECIFIC_SETTINGS.py` - Diagnostic script for receive issues
- `INCIDENT_2025-11-11_SMS_RECEIVING_BROKEN.md` - This document

### **Modified**
- `conductor_system.py` - Temporarily changed CNMI (reverted)
- Modem NVRAM - Reset and reconfigured

---

## **Impact**

### **Duration**
- Broken: ~6 hours (10:00 AM - 4:18 PM)
- Fixed: 4:18 PM (incoming messages immediately resumed)

### **Messages Affected**
- Unknown number of incoming messages were lost during outage
- Messages sent TO the modem during this period were not delivered
- No way to retrieve lost messages (carrier doesn't store them)

### **System Stats**
- Before: 501 total messages
- After fix: 608 total messages (107 new messages received)
- Incoming working: Yes (IDs 1111-1114+ confirmed)
- Outbound: Never stopped working

---

## **Recommendations**

### **Immediate**
1. ✅ Document this configuration as "known working"
2. ✅ Add CSMS=0 to conductor startup
3. ✅ Create modem config backup script
4. ✅ Add to troubleshooting guide

### **Future**
1. Consider modem configuration monitoring (alert if settings change)
2. Create automated modem config validation on startup
3. Add inbound message health check (alert if no messages for X hours)
4. Document MMS as "not supported" to prevent future attempts

---

## **Status**
- ✅ **RESOLVED** - SMS receiving working as of 4:18 PM
- ✅ Modem configured correctly
- ✅ Conductor running and processing messages
- ✅ Incoming messages confirmed working
- ⚠️ User needs to disable RCS on personal phone for testing

---

**Incident closed: 2025-11-11 4:30 PM**

**Root cause:** MMS configuration broke SMS receiving  
**Resolution:** Reset modem to SMS defaults + enable CSMS service  
**Prevention:** Document working config, don't apply phone MMS settings to modem

