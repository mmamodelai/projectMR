#!/usr/bin/env python3
"""
Seed 20 suggested welcome texts for external budtenders.
Part of Conductor SMS System - SMSSUG (campaign suggestions only)

Usage:
    python SMSSUG/seed_budtender_suggestions.py --limit 20 --commit
    python SMSSUG/seed_budtender_suggestions.py --limit 20 --store "Phenos" --dry-run

Architecture:
    - Reads from Supabase `public.budtenders`
    - Generates welcome messages in owner voice (Luis)
    - Inserts into `public.campaign_messages` with status='suggested'
    - Does NOT touch conductor, modem, or scheduling
"""

import argparse
import datetime
import json
import re
from typing import Dict, List, Optional, Tuple
import csv
import os
from pathlib import Path

from supabase import create_client, Client

# NOTE: Reuse same Supabase project as existing tools for consistency
# If you centralize config later, import from a shared module.
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed suggested welcome texts for budtenders")
    parser.add_argument("--limit", type=int, default=20, help="Max number of suggestions to generate (ignored if --all)")
    parser.add_argument("--all", action="store_true", help="Process all budtenders (overrides --limit)")
    parser.add_argument("--store", type=str, default=None, help="Filter by dispensary_name")
    parser.add_argument("--random", action="store_true", help="Randomize selection order")
    parser.add_argument("--out", type=str, default=None, help="Output CSV path (defaults to SMSSUG/output/bt_suggestions_YYYYMMDD_HHMMSS.csv)")
    parser.add_argument("--from-csv", dest="from_csv", type=str, default=None, help="Optional: source CSV path (First Name, Last Name, Phone Number, Affiliation (Store Name))")
    # Postgres direct connection (fallback to avoid Cloudflare/REST)
    parser.add_argument("--use-postgres", action="store_true", help="Use direct Postgres connection for inserts")
    parser.add_argument("--pg-host", type=str, default=None, help="Postgres host (e.g., db.<ref>.supabase.co)")
    parser.add_argument("--pg-port", type=int, default=5432, help="Postgres port (default 5432)")
    parser.add_argument("--pg-db", type=str, default="postgres", help="Postgres database name (default postgres)")
    parser.add_argument("--pg-user", type=str, default="postgres", help="Postgres user (default postgres)")
    parser.add_argument("--pg-password", type=str, default=None, help="Postgres password")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--commit", action="store_true", help="Write suggestions to campaign_messages")
    group.add_argument("--dry-run", action="store_true", help="Preview only (default)")
    return parser.parse_args()


def normalize_us_phone_to_e164(raw_phone: Optional[str]) -> Optional[str]:
    """
    Normalize a US phone number to E.164 (+1XXXXXXXXXX).
    Returns None if invalid/unknown.
    """
    if not raw_phone:
        return None
    digits = re.sub(r"\D", "", raw_phone)
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return None


def build_welcome_message(first_name: str, dispensary_name: str, tshirt_size: Optional[str], front_logo: Optional[str], back_logo: Optional[str]) -> str:
    """
    Owner message per Luis' guide (ASCII only, no opt-in footer).
    """
    name = first_name.strip() if first_name else ""
    store = dispensary_name.strip() if dispensary_name else "your store"
    size = (tshirt_size or "").strip()
    front = (front_logo or "").strip()
    back = (back_logo or "").strip()
    def choose_article(word: str) -> str:
        if not word:
            return "a"
        return "an" if word.strip().lower()[:1] in {"a", "e", "i", "o", "u"} else "a"
    details = ""
    if size or front or back:
        article = choose_article(front)
        details = f"We have you down for a {size} t-shirt with {article} {front} logo on the front and {back} on the sleeve."
    lines = []
    lines.append(f"Hi {name}, it is Luis from MOTA.")
    lines.append("Thanks for signing up. I am excited to welcome you to MOTA's Budtender Program.")
    if details:
        lines.append("Please reply to confirm your welcome gift details:")
        lines.append(details)
    lines.append("Let me know if you want any changes.")
    lines.append("- Luis")
    return " ".join([s for s in lines if s.strip()])


def deduplicate_by_phone(rows: List[Dict]) -> List[Dict]:
    """
    Keep the most recent record for each phone number (based on created_at if present).
    """
    latest_by_phone: Dict[str, Tuple[datetime.datetime, Dict]] = {}
    for r in rows:
        phone = r.get("phone")
        created_at_val = r.get("created_at")
        created_at = None
        if created_at_val:
            try:
                created_at = datetime.datetime.fromisoformat(str(created_at_val).replace("Z", "+00:00"))
            except Exception:
                created_at = None
        key = phone
        if key is None:
            continue
        prev = latest_by_phone.get(key)
        if prev is None:
            latest_by_phone[key] = (created_at or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc), r)
        else:
            prev_dt, _ = prev
            if (created_at or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)) >= prev_dt:
                latest_by_phone[key] = (created_at or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc), r)
    return [entry[1] for entry in latest_by_phone.values()]


def fetch_budtenders(sb: Client, store_filter: Optional[str], randomize: bool, hard_limit: int) -> List[Dict]:
    """
    Fetch budtenders from Supabase and return up to hard_limit valid rows with E.164 phones.
    """
    # Pull a reasonably large window, then filter/dedupe locally.
    # Using 500 as a safe upper bound to avoid heavy scans.
    q = sb.table("budtenders").select("*")
    if store_filter:
        q = q.ilike("dispensary_name", store_filter) if hasattr(q, "ilike") else q.eq("dispensary_name", store_filter)
    q = q.order("created_at", desc=True).limit(500)
    resp = q.execute()
    rows = resp.data or []

    # Normalize phones and filter invalid
    for r in rows:
        r["phone_e164"] = normalize_us_phone_to_e164(r.get("phone"))
    rows = [r for r in rows if r.get("phone_e164")]

    # Deduplicate by phone, most recent wins
    rows = deduplicate_by_phone(rows)

    # Optional randomization
    if randomize:
        import random
        random.shuffle(rows)

    return rows[:hard_limit]


def load_budtenders_from_csv(path: str) -> List[Dict]:
    """
    Load budtenders from a CSV export (owner merch sheet).
    Expected columns: First Name, Last Name, Phone Number, Affiliation (Store Name)
    """
    def sanitize_token(val: str, max_words: int = 3, max_len: int = 24) -> str:
        # ASCII only, letters/digits/spaces
        txt = re.sub(r"[^\x20-\x7E]", " ", val or "")
        txt = re.sub(r"[^A-Za-z0-9 ]+", " ", txt)
        txt = re.sub(r"\s+", " ", txt).strip()
        # trim to first N words and max length
        parts = txt.split(" ")
        txt = " ".join(parts[:max_words]).strip()
        if len(txt) > max_len:
            txt = txt[:max_len].rstrip()
        return txt
    def normalize_size(sz: str) -> str:
        s = (sz or "").strip().lower().replace("/", "")
        mapping = {
            "xs": "X-Small", "xsmall": "X-Small", "x-small": "X-Small",
            "s": "Small", "small": "Small",
            "m": "Medium", "medium": "Medium",
            "l": "Large", "large": "Large",
            "xl": "X-Large", "xlarge": "X-Large", "x-large": "X-Large",
            "xxl": "XX-Large", "2xl": "XX-Large",
            "xxxl": "3X-Large", "3xl": "3X-Large",
        }
        # try direct map
        if s in mapping:
            return mapping[s]
        # heuristics
        if "x-small" in s or "xs" in s:
            return "X-Small"
        if "x large" in s or "xl" in s:
            return "X-Large"
        if "xxl" in s or "2x" in s:
            return "XX-Large"
        if "3xl" in s or "3x" in s:
            return "3X-Large"
        if s.startswith("s"):
            return "Small"
        if s.startswith("m"):
            return "Medium"
        if s.startswith("l"):
            return "Large"
        return sanitize_token(sz, 2, 10) or "Medium"

    results: List[Dict] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            first_name = (row.get("First Name") or "").strip()
            last_name = (row.get("Last Name") or "").strip()
            phone_raw = (row.get("Phone Number") or "").strip()
            store = (row.get("Affiliation (Store Name)") or "").strip()
            tshirt = normalize_size(row.get("T-Shirt Size") or "")
            front_logo = sanitize_token(row.get("Front Logo Design") or "")
            back_logo = sanitize_token(row.get("Back Logo Design") or "")
            e164 = normalize_us_phone_to_e164(phone_raw)
            if not e164:
                continue
            results.append({
                "id": None,
                "first_name": first_name,
                "last_name": last_name,
                "phone": e164,
                "phone_e164": e164,
                "dispensary_name": store.strip(),
                "tshirt_size": tshirt,
                "front_logo": front_logo,
                "back_logo": back_logo,
                "created_at": None,
            })
    # Deduplicate by phone (keep last occurrence)
    dedup = {}
    for r in results:
        dedup[r["phone"]] = r
    return list(dedup.values())


def build_campaign_records(budtenders: List[Dict]) -> List[Dict]:
    """
    Build records for `public.campaign_messages`.
    """
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    records: List[Dict] = []
    for bt in budtenders:
        first_name = (bt.get("first_name") or "").strip()
        last_name = (bt.get("last_name") or "").strip()
        phone = bt.get("phone_e164")
        dispensary_name = (bt.get("dispensary_name") or "").strip()
        customer_name = f"{first_name} {last_name}".strip()
        campaign_batch_id = f"BT_{(dispensary_name or 'Unknown').replace(' ', '')}_{today_str}"
        message_content = build_welcome_message(
            first_name or "there",
            dispensary_name or "your store",
            bt.get("tshirt_size"),
            bt.get("front_logo"),
            bt.get("back_logo"),
        )
        reasoning_payload = {
            "source": "budtenders",
            "dispensary_name": dispensary_name,
            "created_at": bt.get("created_at"),
            "budtender_id": bt.get("id"),
            "tshirt_size": bt.get("tshirt_size"),
            "front_logo": bt.get("front_logo"),
            "back_logo": bt.get("back_logo"),
        }
        rec = {
            "customer_id": str(bt.get("id")) if bt.get("id") is not None else None,
            "customer_name": customer_name or None,
            "phone_number": phone,
            "customer_segment": "external_budtender",
            "message_content": message_content,
            "strategy_type": "welcome",
            "status": "SUG",
            "campaign_name": "BT_Engagement_v1",
            "campaign_batch_id": campaign_batch_id,
            "generated_by": "system",
            "generation_cost": 0,
            "confidence": "high",
            "reasoning": json.dumps(reasoning_payload, ensure_ascii=False),
        }
        records.append(rec)
    return records


def write_csv(out_path: str, records: List[Dict]) -> str:
    """
    Write suggestions to CSV, organized by store (sorted).
    """
    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
    # Sort by store then name
    sorted_records = sorted(
        records,
        key=lambda r: (
            (json.loads(r.get("reasoning") or "{}").get("dispensary_name") or "").lower(),
            (r.get("customer_name") or "").lower(),
        ),
    )
    fieldnames = [
        "dispensary_name",
        "customer_name",
        "phone_number",
        "campaign_name",
        "campaign_batch_id",
        "strategy_type",
        "status",
        "message_content",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in sorted_records:
            why = {}
            try:
                why = json.loads(r.get("reasoning") or "{}")
            except Exception:
                why = {}
            w.writerow({
                "dispensary_name": why.get("dispensary_name") or "",
                "customer_name": r.get("customer_name") or "",
                "phone_number": r.get("phone_number") or "",
                "campaign_name": r.get("campaign_name") or "",
                "campaign_batch_id": r.get("campaign_batch_id") or "",
                "strategy_type": r.get("strategy_type") or "",
                "status": r.get("status") or "",
                "message_content": r.get("message_content") or "",
            })
    return out_path


def filter_out_existing(sb: Client, candidates: List[Dict]) -> List[Dict]:
    """
    Avoid inserting duplicates for the same phone + campaign_name + strategy_type today.
    """
    if not candidates:
        return []
    phones = list({c["phone_number"] for c in candidates if c.get("phone_number")})
    if not phones:
        return []
    # Pull existing suggestions for these phones today
    today = datetime.datetime.now(datetime.timezone.utc).date()
    # Supabase doesn't support complex IN+date filters in one roundtrip easily; fetch by phones and filter client-side.
    chunks: List[List[str]] = []
    step = 200
    for i in range(0, len(phones), step):
        chunks.append(phones[i : i + step])
    existing: List[Dict] = []
    for ch in chunks:
        resp = (
            sb.table("campaign_messages")
            .select("phone_number, campaign_name, strategy_type, generated_at")
            .in_("phone_number", ch)
            .eq("campaign_name", "BT_Engagement_v1")
            .eq("strategy_type", "welcome")
            .order("generated_at", desc=True)
            .execute()
        )
        existing.extend(resp.data or [])
    def is_same_day(ts: Optional[str]) -> bool:
        if not ts:
            return False
        try:
            dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            return False
        return dt.date() == today
    existing_today = {(e.get("phone_number")) for e in existing if is_same_day(e.get("generated_at"))}
    return [c for c in candidates if c.get("phone_number") not in existing_today]


def main() -> None:
    args = parse_args()
    dry_run = not args.commit if not args.dry_run else True
    fetch_limit = 0 if args.all else max(1, args.limit)

    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Source selection: CSV fallback or Supabase
    if args.from_csv:
        budtenders = load_budtenders_from_csv(args.from_csv)
        if not args.all and fetch_limit > 0:
            budtenders = budtenders[:fetch_limit]
    else:
        budtenders = fetch_budtenders(sb, args.store, args.random, fetch_limit if fetch_limit > 0 else 2000)
    records = build_campaign_records(budtenders)
    try:
        records = filter_out_existing(sb, records)
    except Exception as e:
        # Supabase may be temporarily unavailable (e.g., 522). Proceed without de-dup filter.
        print(f"WARNING: Skipping Supabase duplicate filter due to error: {e}")

    print("=" * 60)
    print(f"Prepared {len(records)} suggested welcome messages")
    if args.store:
        print(f"Store filter: {args.store}")
    print(f"Dry run: {'YES' if dry_run else 'NO (will insert)'}")
    print("=" * 60)
    for i, r in enumerate(records, start=1):
        preview = {
            "phone_number": r["phone_number"],
            "customer_name": r.get("customer_name"),
            "campaign_batch_id": r["campaign_batch_id"],
            "message_content": r["message_content"][:120] + ("..." if len(r["message_content"]) > 120 else ""),
            "status": r["status"],
        }
        print(f"[{i}] {json.dumps(preview, ensure_ascii=False)}")

    # Write CSV (always)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    default_path = os.path.join("SMSSUG", "output", f"bt_suggestions_{ts}.csv")
    out_path = args.out or default_path
    csv_path = write_csv(out_path, records)
    print(f"\nCSV written: {csv_path}")

    if dry_run or not records:
        print("\nNo changes written (dry-run). Use --commit to insert.")
        return

    # Insert in batches to avoid payload limits
    inserted = 0
    batch_size = 200
    if args.use_postgres:
        try:
            import psycopg2
            import psycopg2.extras as _extras
        except Exception as e:
            raise SystemExit(f"psycopg2 is required for --use-postgres. Please install psycopg2-binary. Error: {e}")
        if not args.pg_host or not args.pg_password:
            raise SystemExit("--pg-host and --pg-password are required for --use-postgres")
        conn = psycopg2.connect(
            host=args.pg_host,
            port=args.pg_port,
            dbname=args.pg_db,
            user=args.pg_user,
            password=args.pg_password,
            sslmode="require",
        )
        try:
            with conn:
                with conn.cursor() as cur:
                    for i in range(0, len(records), batch_size):
                        batch = records[i : i + batch_size]
                        params = []
                        for r in batch:
                            params.append((
                                r.get("customer_id"),
                                r.get("customer_name"),
                                r.get("phone_number"),
                                r.get("customer_segment"),
                                r.get("message_content"),
                                r.get("strategy_type"),
                                r.get("status"),
                                r.get("campaign_name"),
                                r.get("campaign_batch_id"),
                                r.get("generated_by"),
                                r.get("generation_cost"),
                                r.get("confidence"),
                                _extras.Json(json.loads(r.get("reasoning") or "{}")),
                            ))
                        cur.executemany(
                            """
                            INSERT INTO public.campaign_messages
                            (customer_id, customer_name, phone_number, customer_segment, message_content,
                             strategy_type, status, campaign_name, campaign_batch_id, generated_by,
                             generation_cost, confidence, reasoning)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                            """,
                            params,
                        )
                        inserted += len(batch)
            print(f"\nSUCCESS: Inserted {inserted} suggested messages into public.campaign_messages via Postgres")
        finally:
            try:
                conn.close()
            except Exception:
                pass
    else:
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            resp = sb.table("campaign_messages").insert(batch).execute()
            if isinstance(resp.data, list):
                inserted += len(resp.data)
            else:
                # Fallback: assume all batch inserted if API doesn't return rows
                inserted += len(batch)
        print(f"\nSUCCESS: Inserted {inserted} suggested messages into public.campaign_messages")


if __name__ == "__main__":
    main()


