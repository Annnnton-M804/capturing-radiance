#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Initialize the SQLite database and create indexes dynamically
based on detected column names in the wish_logs table.
"""

import sqlite3

DB_FILE = 'wish_logs.db'

def init_db():
    # Connect to the SQLite database (creates file if not exists)
    conn = sqlite3.connect(DB_FILE)
    cur  = conn.cursor()

    # 1) Ensure the table exists (dummy structure if needed)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wish_logs (
      dummy_col INTEGER
    );
    """)

    # 2) Retrieve actual column names from wish_logs
    cur.execute("PRAGMA table_info(wish_logs);")
    cols = [row[1] for row in cur.fetchall()]

    # 3) Define possible names for pity and non-up flags
    pity_candidates    = ['pull_number', 'pity_number', 'within_pity', 'within pity']
    non_up_candidates  = ['is_not_up', 'non_up', 'not_up']

    # 4) Select the first matching column name for each category
    pity_col   = next((c for c in pity_candidates if c in cols), None)
    non_up_col = next((c for c in non_up_candidates if c in cols), None)

    # 5) Drop old indexes if they exist to avoid conflicts
    cur.execute("DROP INDEX IF EXISTS idx_pity;")
    cur.execute("DROP INDEX IF EXISTS idx_non_up;")

    # 6) Create new indexes on the detected columns
    if pity_col:
        cur.execute(f"CREATE INDEX IF NOT EXISTS idx_pity ON wish_logs({pity_col});")
        print(f"✅ Created index idx_pity on column '{pity_col}'")
    else:
        print("⚠️  No pity-like column found; idx_pity skipped.")

    if non_up_col:
        cur.execute(f"CREATE INDEX IF NOT EXISTS idx_non_up ON wish_logs({non_up_col});")
        print(f"✅ Created index idx_non_up on column '{non_up_col}'")
    else:
        print("⚠️  No non-UP flag column found; idx_non_up skipped.")

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print(f"🎉 Database initialized and indexes created in '{DB_FILE}'")

if __name__ == '__main__':
    init_db()