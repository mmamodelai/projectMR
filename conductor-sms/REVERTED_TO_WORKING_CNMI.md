# ✅ REVERTED TO WORKING CNMI SETTING

## **PROBLEM:**
Changed CNMI to `2,0,0,0,0` but messages still not coming in.

## **ROOT CAUSE:**
Checked the **OLD WORKING VERSION** (`C:\Dev\smscondutorui 2\ConductorV4.1\conductor-sms\conductor_system.py`):
- **Old working version uses**: `AT+CNMI=1,1,0,0,0`
- **Comment in old version**: "CRITICAL FIX: Mode 1,1 = Keep messages in storage + notify on arrival. This prevents auto-deletion of messages before Conductor can read them! Previously was 2,0 which caused messages to be auto-deleted"

## **FIX APPLIED:**
Reverted CNMI back to `1,1,0,0,0` (the working setting):
- Mode 1: Discard indication if link busy
- MT 1: **Keep messages in storage + notify on arrival**
- This prevents auto-deletion before Conductor can read them

## **CHANGES MADE:**
1. ✅ Updated `conductor_system.py` line 523: `AT+CNMI=1,1,0,0,0`
2. ✅ Saved to modem: `AT&W` (persists across restarts)
3. ✅ Restarted Conductor to apply new setting

## **VERIFICATION:**
```bash
# Check CNMI setting
python -c "import serial; s=serial.Serial('COM24',115200,timeout=5); s.write(b'AT+CNMI?\r\n'); import time; time.sleep(1); print(s.read_all().decode())"

# Should show: +CNMI: 1,1,0,0,0
```

## **TESTING:**
1. Send a test message from your cell phone
2. Wait 5-10 seconds (Conductor polls every 5s)
3. Check Telegraph (SMS Conductor DB) → All Messages tab
4. Message should appear as "unread"

---

**Status**: ✅ CNMI reverted to `1,1,0,0,0` (working version) - Testing now

