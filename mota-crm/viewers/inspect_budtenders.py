from supabase import create_client
from collections import defaultdict
import json

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

data = sb.table('budtenders').select('id, first_name, last_name, phone, email, dispensary_name').execute().data

dup_phone = defaultdict(list)
dup_email = defaultdict(list)
blanks = []

for row in data:
    first = (row.get('first_name') or '').strip()
    last = (row.get('last_name') or '').strip()
    if not first or not last:
        blanks.append(row)
    phone_digits = ''.join(ch for ch in (row.get('phone') or '') if ch.isdigit())
    if phone_digits:
        dup_phone[phone_digits].append(row)
    email = (row.get('email') or '').lower()
    if email:
        dup_email[email].append(row)

dup_phone = {k: v for k, v in dup_phone.items() if len(v) > 1}
dup_email = {k: v for k, v in dup_email.items() if len(v) > 1}

print("BLANK FIRST/LAST NAMES:", len(blanks))
print(json.dumps(blanks, indent=2))

print("\nDUPLICATE PHONE NUMBERS:", len(dup_phone))
print(json.dumps({k: [(r['first_name'], r['last_name'], r['dispensary_name'], r['id']) for r in v] for k, v in dup_phone.items()}, indent=2))

print("\nDUPLICATE EMAILS:", len(dup_email))
print(json.dumps({k: [(r['first_name'], r['last_name'], r['dispensary_name'], r['id']) for r in v] for k, v in dup_email.items()}, indent=2))


