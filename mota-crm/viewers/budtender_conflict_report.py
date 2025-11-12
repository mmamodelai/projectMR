from supabase import create_client
from collections import defaultdict

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

rows = sb.table('budtenders').select('id, first_name, last_name, phone, email, dispensary_name, created_at, updated_at').execute().data

def normalize_phone(phone):
    return ''.join(ch for ch in (phone or '') if ch.isdigit())

phone_dupes = defaultdict(list)
email_dupes = defaultdict(list)

for row in rows:
    phone_key = normalize_phone(row.get('phone'))
    email_key = (row.get('email') or '').strip().lower()
    if phone_key:
        phone_dupes[phone_key].append(row)
    if email_key:
        email_dupes[email_key].append(row)

phone_dupes = {k: v for k, v in phone_dupes.items() if len(v) > 1}
email_dupes = {k: v for k, v in email_dupes.items() if len(v) > 1}

def print_group(header, key, entries):
    print(f"\n=== {header}: {key} ({len(entries)} records) ===")
    print(f"{'ID':<6} {'First':<15} {'Last':<15} {'Dispensary':<20} {'Phone':<12} {'Email':<30} {'Updated'}")
    for r in entries:
        print(f"{r['id']:<6} {r.get('first_name','')[:14]:<15} {r.get('last_name','')[:14]:<15} {r.get('dispensary_name','')[:19]:<20} {normalize_phone(r.get('phone')):<12} {r.get('email','')[:29]:<30} {r.get('updated_at','')[:19]}")

if phone_dupes:
    print("PHONE CONFLICTS:")
    for phone, entries in phone_dupes.items():
        print_group('Phone', phone, entries)
else:
    print("No duplicate phones found")

if email_dupes:
    print("\nEMAIL CONFLICTS:")
    for email, entries in email_dupes.items():
        print_group('Email', email, entries)
else:
    print("\nNo duplicate emails found")


