# MMSYS - MMS Sending System

**Status**: 🚧 In Development  
**Purpose**: Send long text messages as single-bubble MMS (no 160-char splits)  
**Architecture**: Direct HTTP POST to carrier MMSC endpoint

---

## 🎯 What This Does

Sends MMS messages directly through Mint Mobile's MMSC (Multimedia Messaging Service Center) endpoint, allowing:

- ✅ **Long messages** (500+ characters in ONE bubble)
- ✅ **No SMS splitting** (single message delivery)
- ✅ **Uses existing SIM** (no new accounts needed)
- ✅ **Completely separate** from Conductor SMS system

---

## 🏗️ How It Works

### Authentication
- **SIM card** provides authentication through data connection
- **No API keys needed** - carrier identifies you from your data session
- **Your phone number** automatically attached to MMS

### Technical Flow
```
1. Modem establishes TCP/IP connection (AT+CIPSTART)
2. Activate PDP context with Mint's "Wholesale" APN
3. Encode message in WAP/WSP format (binary)
4. HTTP POST to http://wholesale.mmsmvno.com/mms/wapenc:8080
5. Carrier responds with M-Send.conf (delivery confirmation)
```

---

## 📁 File Structure

```
MMSYS/
├── README.md                 # This file
├── mms_sender.py             # Core MMS sending engine
├── config.json               # Configuration (MMSC, APN, COM port)
├── test_mms.py               # Test script
├── test_mms.bat              # Windows launcher
└── docs/
    ├── WAP_ENCODING.md       # WAP/WSP encoding details
    └── TROUBLESHOOTING.md    # Common issues
```

---

## 🚀 Quick Start

### 1. Configuration
Edit `config.json`:
```json
{
  "modem": {
    "port": "COM24",
    "baudrate": 115200
  },
  "mms": {
    "mmsc": "http://wholesale.mmsmvno.com/mms/wapenc",
    "port": "8080",
    "apn": "Wholesale"
  }
}
```

### 2. Send MMS
```bash
python mms_sender.py +16199773020 "Your long message here..."
```

Or use the batch file:
```bash
.\test_mms.bat
```

---

## 🔧 Requirements

- Python 3.9+
- pyserial
- SIM7600G-H modem on COM24
- Active Mint Mobile SIM card
- **Conductor must be stopped** (to free COM port)

---

## ⚠️ Important Notes

1. **Conductor Conflict**: Stop Conductor before using MMSYS (both use COM24)
2. **Data Connection**: Requires active data/internet on SIM
3. **Carrier Limits**: Mint Mobile may have MMS size limits (~300KB typical)
4. **Testing**: Start with short messages, then increase length

---

## 🆚 MMSYS vs Conductor

| Feature | Conductor SMS | MMSYS MMS |
|---------|--------------|-----------|
| Message Type | SMS | MMS |
| Max Length | 160 chars/SMS | 1000+ chars |
| Delivery | Multiple bubbles | Single bubble |
| Speed | ~5 seconds | ~10 seconds |
| Complexity | Simple AT commands | WAP encoding + HTTP |
| Status | ✅ Production | 🚧 Development |

---

## 📝 Development Status

- [x] Project structure created
- [ ] WAP/WSP encoding implementation
- [ ] TCP/IP connection via AT commands
- [ ] HTTP POST to MMSC
- [ ] M-Send.conf parsing
- [ ] Error handling
- [ ] Testing with real messages
- [ ] Production ready

---

## 🤝 Integration with Conductor

MMSYS is **completely separate**. Future integration possibilities:

1. **Queue-based**: Conductor detects long messages → queues to MMSYS
2. **API**: MMSYS runs as service, Conductor calls it for long messages
3. **Auto-switch**: System automatically uses SMS or MMS based on length

---

**Created**: November 8, 2025  
**Version**: 0.1.0 (Initial Development)


