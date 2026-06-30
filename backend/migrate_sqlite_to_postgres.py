#!/usr/bin/env python3
"""
Simple migration helper: copy data from local SQLite (`sql_app.db`) to a target Postgres `DATABASE_URL`.

Usage:
  Ensure your target Postgres URL is in the env var `DATABASE_URL`.
  Optionally set `SQLITE_URL` to point to the source sqlite file (default: sqlite:///./sql_app.db).

  1. Ensure target Postgres has the schema (run the app once with DATABASE_URL set so tables are created),
     or run Alembic migrations if available.
  2. Run: `python migrate_sqlite_to_postgres.py`

Notes: This script performs a best-effort row copy for known tables. Use with caution and backup data first.
"""
import os
from sqlalchemy import create_engine, MetaData, Table, select

SQLITE_URL = os.getenv('SQLITE_URL', 'sqlite:///./sql_app.db')
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise SystemExit('Set DATABASE_URL environment variable to target Postgres before running this script')

print(f"Source (sqlite): {SQLITE_URL}")
print(f"Target (postgres): {DATABASE_URL}")

src_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
dst_engine = create_engine(DATABASE_URL)

src_meta = MetaData()
dst_meta = MetaData()

print('Reflecting source metadata...')
src_meta.reflect(bind=src_engine)
print('Reflecting target metadata...')
dst_meta.reflect(bind=dst_engine)

# Tables to copy (order matters for FKs)
tables = [
    'users',
    'inventory_items',
    'daily_sales',
    'daily_expenses',
    'investments',
    'one_time_expenses'
]

for tname in tables:
    if tname not in src_meta.tables:
        print(f"Skipping {tname}: not present in source")
        continue
    if tname not in dst_meta.tables:
        print(f"Skipping {tname}: not present in target (create tables first)")
        continue

    src_table = Table(tname, src_meta, autoload_with=src_engine)
    dst_table = Table(tname, dst_meta, autoload_with=dst_engine)

    print(f"Copying table {tname}...")
    with src_engine.connect() as sconn, dst_engine.connect() as dconn:
        rows = sconn.execute(select(src_table)).fetchall()
        if not rows:
            print(f"  no rows in {tname}")
            continue
        dicts = [dict(r._mapping) for r in rows]
        # Remove sqlite-specific rowid keys if present
        for d in dicts:
            d.pop('rowid', None)
        try:
            dconn.execute(dst_table.insert(), dicts)
            print(f"  inserted {len(dicts)} rows into {tname}")
        except Exception as e:
            print(f"  failed to insert into {tname}: {e}")

print('Migration finished')
