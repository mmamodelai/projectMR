#!/usr/bin/env python3
"""
CSV → SQL seeder for campaign_messages
Reads SMSSUG/output/bt_suggestions_*.csv and writes INSERT statements
to load into Supabase via SQL editor (bypasses REST/Cloudflare and 5432).
"""

import argparse
import csv
import json
import os
from pathlib import Path
from datetime import datetime


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert BT suggestions CSV to SQL seed file")
    p.add_argument("--csv", required=True, help="Path to SMSSUG/output/bt_suggestions_*.csv")
    p.add_argument("--out", required=True, help="Path to write SQL file (base path if --split > 0)")
    p.add_argument("--split", type=int, default=0, help="Max rows per file; if >0, creates chunked files with _partN suffix")
    p.add_argument("--multi", action="store_true", help="Use multi-row INSERT VALUES per file/chunk")
    return p.parse_args()


def sql_escape(value: str) -> str:
    if value is None:
        return ""
    return value.replace("'", "''")


def main():
    args = parse_args()
    src_csv = Path(args.csv)
    out_base = Path(args.out)
    out_base.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    with open(src_csv, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            rows.append(row)

    now_ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    def chunk_write(chunk_rows, index: int, total_files: int):
        out_sql = out_base
        if args.split > 0:
            stem = out_base.stem
            suffix = out_base.suffix or ".sql"
            out_sql = out_base.with_name(f"{stem}_part{index+1}of{total_files}{suffix}")
        with open(out_sql, "w", encoding="utf-8", newline="") as f:
            f.write("-- Seed campaign_messages from {}\n".format(src_csv.name))
            f.write("-- Generated at {}\n".format(now_ts))
            f.write("BEGIN;\n")
            if args.multi:
                f.write(
                    "INSERT INTO public.campaign_messages "
                    "(customer_name, phone_number, message_content, strategy_type, status, "
                    "campaign_name, campaign_batch_id, generated_by, reasoning)\nVALUES\n"
                )
            first_val = True
            for r in chunk_rows:
                disp = (r.get("dispensary_name") or "").strip()
                customer_name = (r.get("customer_name") or "").strip()
                phone = (r.get("phone_number") or "").strip()
                campaign_name = (r.get("campaign_name") or "").strip()
                campaign_batch_id = (r.get("campaign_batch_id") or "").strip()
                strategy_type = (r.get("strategy_type") or "").strip()
                status = (r.get("status") or "").strip()
                message_content = (r.get("message_content") or "").strip()

                reasoning = {
                    "dispensary_name": disp,
                    "source_csv": src_csv.name,
                }
                reasoning_json = json.dumps(reasoning, ensure_ascii=False)

                esc_customer = sql_escape(customer_name)
                esc_phone = sql_escape(phone)
                esc_msg = sql_escape(message_content)
                esc_strategy = sql_escape(strategy_type)
                esc_status = sql_escape(status)
                esc_camp = sql_escape(campaign_name)
                esc_batch = sql_escape(campaign_batch_id)
                esc_reason = sql_escape(reasoning_json)

                if args.multi:
                    f.write(
                        ("" if first_val else ",") +
                        "('{customer}', '{phone}', '{msg}', '{strategy}', '{status}', "
                        "'{camp}', '{batch}', 'SMSSUG/csv_import', '{reason}'::jsonb)\n".format(
                            customer=esc_customer,
                            phone=esc_phone,
                            msg=esc_msg,
                            strategy=esc_strategy,
                            status=esc_status,
                            camp=esc_camp,
                            batch=esc_batch,
                            reason=esc_reason,
                        )
                    )
                    first_val = False
                else:
                    f.write(
                        "INSERT INTO public.campaign_messages "
                        "(customer_name, phone_number, message_content, strategy_type, status, "
                        "campaign_name, campaign_batch_id, generated_by, reasoning) "
                        "VALUES "
                        "('{customer}', '{phone}', '{msg}', '{strategy}', '{status}', "
                        "'{camp}', '{batch}', 'SMSSUG/csv_import', '{reason}'::jsonb);\n".format(
                            customer=esc_customer,
                            phone=esc_phone,
                            msg=esc_msg,
                            strategy=esc_strategy,
                            status=esc_status,
                            camp=esc_camp,
                            batch=esc_batch,
                            reason=esc_reason,
                        )
                    )
            if args.multi:
                f.write(";\n")
            f.write("COMMIT;\n")
        return out_sql

    if args.split and args.split > 0:
        files = []
        total = len(rows)
        chunks = [rows[i:i+args.split] for i in range(0, total, args.split)]
        for idx, chunk in enumerate(chunks):
            out_sql = chunk_write(chunk, idx, len(chunks))
            files.append(out_sql)
        print("SQL seeds written:")
        for fp in files:
            print(str(fp))
    else:
        out_sql = chunk_write(rows, 0, 1)
        print(f"SQL seed written: {out_sql}")


if __name__ == "__main__":
    main()


