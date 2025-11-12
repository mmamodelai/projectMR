#!/usr/bin/env python3
"""
Modem Probe - Check SIM storage and optionally clear inbox
Part of Conductor SMS System

Usage:
    python modem_probe.py --report
    python modem_probe.py --clean    # deletes all SIM messages (AT+CMGD=1,4)

Architecture:
    Polling-based, connect/disconnect. Never hold the port longer than needed.
"""

import argparse
import json
import os
import sys
import time
import serial


CONFIG_FILE = "config.json"


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def send_at(ser: serial.Serial, command: str, timeout: float = 2.0) -> str:
    ser.reset_input_buffer()
    ser.write((command + "\r\n").encode())
    end = time.time() + timeout
    resp = ""
    while time.time() < end:
        time.sleep(0.05)
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            resp += chunk
            if "\nOK" in resp or "\nERROR" in resp:
                break
    return resp


def parse_cpms(resp: str):
    """Parse AT+CPMS? response and return (used, total) for SIM (SM)."""
    # Typical: +CPMS: "SM",u1,t1,"SM",u2,t2,"SM",u3,t3
    # We use first pair for SM inbox
    try:
        if "+CPMS:" not in resp:
            return None
        # Extract numbers after first "SM",
        # A simple approach: find first occurrence of '"SM",' then parse two ints
        part = resp.split('"SM",', 1)[1]
        nums = []
        cur = ""
        for ch in part:
            if ch.isdigit():
                cur += ch
            else:
                if cur:
                    nums.append(int(cur))
                    cur = ""
            if len(nums) >= 2:
                break
        if len(nums) >= 2:
            return nums[0], nums[1]
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true", help="Print CPMS and list SIM inbox")
    parser.add_argument("--clean", action="store_true", help="Delete all SIM messages (AT+CMGD=1,4)")
    parser.add_argument("--apply-settings", action="store_true", help="Force CNMI store-on-SIM and set CPMS to SM, then save (&W)")
    parser.add_argument("--check-unread", action="store_true", help="List only REC UNREAD from SIM (and ME fallback)")
    parser.add_argument("--reboot", action="store_true", help="Soft reboot modem (AT+CFUN=1,1) and exit")
    parser.add_argument("--info", action="store_true", help="Show MSISDN (CNUM), SMSC (CSCA), CSMS/CSMP settings")
    parser.add_argument("--send-sms", nargs=2, metavar=("PHONE","MESSAGE"), help="Send a test SMS via AT+CMGS")
    args = parser.parse_args()

    cfg = load_config()
    port = cfg["modem"]["port"]
    baud = cfg["modem"]["baudrate"]
    timeout = cfg["modem"]["timeout"]

    try:
        ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(0.3)
    except Exception as e:
        print(f"ERR_OPEN: {e}")
        sys.exit(2)

    try:
        print("CMD: AT")
        print(send_at(ser, "AT", 1.5))

        print("CMD: AT+CMGF=1")
        print(send_at(ser, "AT+CMGF=1", 1.5))

        print('CMD: AT+CSQ')
        print(send_at(ser, 'AT+CSQ', 1.5))

        print('CMD: AT+CREG?')
        print(send_at(ser, 'AT+CREG?', 1.5))

        print('CMD: AT+COPS?')
        print(send_at(ser, 'AT+COPS?', 2.0))

        print('CMD: AT+CPMS?')
        cpms = send_at(ser, 'AT+CPMS?', 2.0)
        print(cpms)
        pair = parse_cpms(cpms)
        if pair:
            used, total = pair
            print(f"CPMS_USED_TOTAL: {used}/{total}")
        else:
            print("CPMS_PARSE_FAIL")

        print('CMD: AT+CNMI?')
        print(send_at(ser, 'AT+CNMI?', 1.5))

        print('CMD: AT+CPMS="SM","SM","SM"')
        print(send_at(ser, 'AT+CPMS="SM","SM","SM"', 1.5))

        if args.report:
            print('CMD: AT+CMGL="ALL"')
            # Shorter timeout; listing can be long but we just need presence
            listing = send_at(ser, 'AT+CMGL="ALL"', 3.0)
            # Only show first ~500 chars to avoid console spam
            print(listing[:500])

            # Also check ME storage in case network routes there
            print('CMD: AT+CPMS="ME","ME","ME"')
            print(send_at(ser, 'AT+CPMS="ME","ME","ME"', 1.5))
            print('CMD: AT+CMGL="ALL" (ME)')
            listing_me = send_at(ser, 'AT+CMGL="ALL"', 3.0)
            print(listing_me[:500])

        if args.reboot:
            print('CMD: AT+CFUN=1,1 (reboot)')
            print(send_at(ser, 'AT+CFUN=1,1', 2.0))
            print('NOTE: Modem rebooting; wait ~10-15s before next command')
            return

        if args.apply_settings:
            print('CMD: AT+CMGF=1 (apply)')
            print(send_at(ser, 'AT+CMGF=1', 1.5))
            print('CMD: AT+CNMI=2,0,0,0,0 (apply)')
            print(send_at(ser, 'AT+CNMI=2,0,0,0,0', 1.5))
            print('CMD: AT+CPMS="SM","SM","SM" (apply)')
            print(send_at(ser, 'AT+CPMS="SM","SM","SM"', 1.5))
            print('CMD: AT&W (save)')
            print(send_at(ser, 'AT&W', 2.0))

        if args.info:
            print('CMD: AT+CNUM')
            print(send_at(ser, 'AT+CNUM', 2.0))
            print('CMD: AT+CSCA?')
            print(send_at(ser, 'AT+CSCA?', 2.0))
            print('CMD: AT+CSMS?')
            print(send_at(ser, 'AT+CSMS?', 2.0))
            print('CMD: AT+CSMP?')
            print(send_at(ser, 'AT+CSMP?', 2.0))

        if args.check_unread:
            print('CMD: AT+CPMS="SM","SM","SM" (check)')
            print(send_at(ser, 'AT+CPMS="SM","SM","SM"', 1.5))
            print('CMD: AT+CMGL="REC UNREAD" (SM)')
            out_sm = send_at(ser, 'AT+CMGL="REC UNREAD"', 3.0)
            print(out_sm[:800])
            print('CMD: AT+CPMS="ME","ME","ME" (check)')
            print(send_at(ser, 'AT+CPMS="ME","ME","ME"', 1.5))
            print('CMD: AT+CMGL="REC UNREAD" (ME)')
            out_me = send_at(ser, 'AT+CMGL="REC UNREAD"', 3.0)
            print(out_me[:800])

        if args.clean:
            print('CMD: AT+CMGD=1,4')
            print(send_at(ser, 'AT+CMGD=1,4', 2.5))

        if args.send_sms:
            phone, message = args.send_sms
            print(f'SEND: AT+CMGS to {phone}')
            ser.write((f'AT+CMGS="{phone}"\r\n').encode())
            time.sleep(0.5)
            ser.write((message + "\x1A").encode())
            # Wait up to 15s for OK
            end = time.time() + 15
            resp = ""
            while time.time() < end:
                time.sleep(0.1)
                if ser.in_waiting:
                    resp += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    if 'OK' in resp or 'ERROR' in resp:
                        break
            print(resp)

        print("DONE")
    finally:
        try:
            ser.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()


