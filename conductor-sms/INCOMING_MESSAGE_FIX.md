# 🚨 INCOMING MESSAGE FIX - CNMI Setting Changed

## **PROBLEM:**
Messages from your cell phone not being received by Conductor.

## **ROOT CAUSE:**
CNMI was set to `1,1,0,0,0` which:
- Mode 1: Discard if link busy
- MT 1: Sends notifications to TE (Windows)
- **Windows may be intercepting messages before Conductor can read them**

## **FIX APPLIED:**
Changed CNMI to `2,0,0,0,0`:
- Mode 2: Buffer if busy, else forward
- MT 0: **Store messages on SIM/ME, NO forwarding to Windows**
- Messages stay on modem until Conductor reads them

## **CHANGES MADE:**
1. ✅ Updated `conductor_system.py` line 523: `AT+CNMI=2,0,0,0,0`
2. ✅ Saved to modem: `AT&W` (persists across restarts)
3. ✅ Restarted Conductor to apply new setting

## **VERIFICATION:**
```bash
# Check CNMI setting
python -c "import serial; s=serial.Serial('COM24',115200,timeout=5); s.write(b'AT+CNMI?\r\n'); import time; time.sleep(1); print(s.read_all().decode())"

# Should show: +CNMI: 2,0,0,0,0
```

## **TESTING:**
1. Send a test message from your cell phone
2. Wait 5-10 seconds (Conductor polls every 5s)
3. Check Telegraph (SMS Conductor DB) → All Messages tab
4. Message should appear as "unread"

## **IF STILL NOT WORKING:**
1. Check modem directly: `python EMERGENCY_MODEM_CHECK.py`
2. Verify messages are on modem: `AT+CMGL="ALL"`
3. Check logs: `Get-Content logs\conductor_system.log -Tail 50`

---

**Status**: ✅ CNMI changed to `2,0,0,0,0` - Testing now

