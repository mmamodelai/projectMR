from supabase import create_client
from collections import defaultdict
from datetime import datetime

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

rows = sb.table('budtenders').select('*').execute().data

def normalize_phone(phone):
    return ''.join(ch for ch in (phone or '') if ch.isdigit())

def parse_dt(value):
    if not value:
        return datetime.min
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return datetime.min

# Build mapping id -> row
row_by_id = {row['id']: row for row in rows}

# Union-Find for clustering duplicates via phone/email
parent = {}

def find(x):
    parent.setdefault(x, x)
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[rb] = ra

phones = defaultdict(list)
emails = defaultdict(list)

for row in rows:
    rid = row['id']
    parent.setdefault(rid, rid)
    phone_key = normalize_phone(row.get('phone'))
    email_key = (row.get('email') or '').strip().lower()
    if phone_key:
        for other in phones[phone_key]:
            union(rid, other)
        phones[phone_key].append(rid)
    if email_key:
        for other in emails[email_key]:
            union(rid, other)
        emails[email_key].append(rid)

# Group by root
clusters = defaultdict(list)
for rid in parent:
    clusters[find(rid)].append(rid)

to_delete = []
keep_info = []

for root, members in clusters.items():
    if len(members) <= 1:
        continue
    # choose keeper by highest points -> latest updated -> lowest id
    def score(rid):
        row = row_by_id[rid]
        return (
            row.get('points', 0) or 0,
            parse_dt(row.get('updated_at')),
            -rid  # for deterministic order
        )
    keeper_id = max(members, key=score)
    keep_info.append((keeper_id, members))
    for rid in members:
        if rid != keeper_id:
            to_delete.append(rid)

# Delete duplicates
for rid in to_delete:
    print(f"Deleting duplicate budtender id={rid}")
    sb.table('budtenders').delete().eq('id', rid).execute()

# Normalize keeper phones to digits only
for keeper_id, members in keep_info:
    row = row_by_id[keeper_id]
    phone_digits = normalize_phone(row.get('phone'))
    if row.get('phone') != phone_digits:
        print(f"Normalizing phone for keeper id={keeper_id} to {phone_digits}")
        sb.table('budtenders').update({'phone': phone_digits}).eq('id', keeper_id).execute()

print(f"Removed {len(to_delete)} duplicates across {len(keep_info)} clusters")


