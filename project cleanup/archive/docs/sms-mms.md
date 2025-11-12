Excellent — you’re really close to the truth here, and this SIM7600G-H dongle (by XYGStudy) is actually capable of MMS, but what’s biting you right now isn’t hardware — it’s how the AT command layer handles SMS concatenation and data vs. MMS.

Let’s unpack what’s happening and how to fix or work around it.

🧠 Why your long texts “get messed up”

When you send an SMS longer than ~160 characters, GSM modems (like the SIM7600G-H) must split it into multiple “segments” using Concatenated SMS (CSMS), where the message is sent in parts with headers that tell the recipient to reassemble them.

👉 The SIM7600G-H supports this only if you enable text mode concatenation or use PDU mode properly.
If not set, texts over 160 characters will:

Get split mid-sentence,

Arrive garbled, or

Fail after 1 part (the classic 150-char cutoff you’re seeing).

So your “fucked up texts” are caused by message segmentation, not by T-Mobile or the modem’s data connection.

✅ Step 1: Enable concatenated SMS (fix long messages)

If you’re using AT commands, you can fix this by enabling the relevant settings.

AT command setup (for SIM7600G-H)
AT+CMGF=1                # Text mode
AT+CSCS="GSM"            # Character set
AT+CSMP=17,167,0,240     # Enable concatenated SMS and 7-bit GSM alphabet


Then you can send long texts normally:

AT+CMGS="+1XXXXXXXXXX"
> This is a very long text that should be automatically split and reassembled by the phone...
<Ctrl+Z>


If you’re using a tool like Gammu, minicom, or NowSMS, make sure “Long SMS (concatenation)” is enabled in its config.

🛰️ Step 2: MMS — what’s possible and how

Here’s where things get interesting.

The SIM7600G-H (like your EXVIST + EC25-A) can send MMS, but not directly via one AT command.
MMS is basically:

A special SMS notifying the MMSC server that you’re sending multimedia

A data (HTTP POST) to the MMSC URL (using your carrier’s APN)

So for T-Mobile, the MMS parameters are:

Setting	Value
APN	fast.t-mobile.com
MMSC	http://mms.msg.eng.t-mobile.com/mms/wapenc
MMS Proxy	none (or empty)
MMS Port	80
⚙️ How to send MMS via SIM7600G-H

You need software that handles both layers:

Opens a data session via the APN above

Wraps your image/video/text in an MMS envelope (multipart HTTP)

Posts it to the MMSC endpoint

On Linux, the most common open-source tools for this are:

Gammu (with MMS extensions)

NowSMS Lite

Kannel (SMS/MMS gateway)

For example, with Gammu, you can configure:

[gammu]
device = /dev/ttyUSB2
connection = at115200
sendsms = yes
mms = yes

[gammu-smsd]
service = files


Then set the APN and MMSC in /etc/gammurc, and it’ll handle SMS and MMS correctly.

⚠️ Key takeaways
Function	Works	Notes
SMS (<160 chars)	✅	Works out of the box
Long SMS (>160 chars)	✅ with AT+CSMP=17,167,0,240 or proper software	Needed to concatenate
MMS (with pictures/media)	⚙️ Possible with extra software	Requires MMSC setup + data session
Voice calls	✅ Optional	Some firmwares support it
GNSS (GPS)	✅	Needs separate antenna
💡 Real-world recommendation

If your goal is:

Sending and receiving long texts and picture messages on a PC

Using a T-Mobile SIM

With a simple USB dongle

Then your SIM7600G-H is an excellent choice — you just need to:

Turn on concatenated SMS (see AT commands above)

Use software that can handle MMS if you want to go beyond text

Confirm your plan allows MMS (some data-only SIMs block it)

If you tell me:

Whether you’re using Windows, Linux, or Raspberry Pi, and

Which tool (if any) you’re using to send texts (AT commands, Gammu, custom script, etc.),

I can show you exactly how to enable concatenated SMS and configure MMS on your system — step by step.