#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database Layer:
Create a local SQLite database and set up the wish_logs table with indexes.
"""

import sqlite3

DB_FILE = 'wish_logs.db'

def init_db():
    # Connect to (or create) the SQLite database file
    conn = sqlite3.connect(DB_FILE)
    cur  = conn.cursor()

    # Create table to store each pull
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wish_logs (
        pull_id         INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id      TEXT    NOT NULL,
        banner_id       TEXT    NOT NULL,
        pull_number     INTEGER NOT NULL,
        rarity          INTEGER NOT NULL,
        character       TEXT,
        is_fate_capture BOOLEAN DEFAULT 0,
        primogem_cost   INTEGER,
        timestamp       TEXT    NOT NULL,
        is_up           BOOLEAN,
        is_not_up       BOOLEAN
    );
    """)

    # Add indexes for faster queries on pity and not-up flags
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pity   ON wish_logs(pull_number);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_not_up ON wish_logs(is_not_up);")

    conn.commit()
    conn.close()
    print(f"✅ Initialized SQLite database at '{DB_FILE}'")

if __name__ == '__main__':
    init_db()