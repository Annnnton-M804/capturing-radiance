#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Loading & Cleaning:
- Read raw wish logs from Excel files in data/*.xlsx
- Rename columns to match our processing logic
- Parse the timestamp column to datetime
- Compute primogem_cost as pull_number × 160 gems
- Flag is_not_up (5★ non-UP) and is_up (5★ UP)
- Write the cleaned data into a local SQLite database

Additionally provides a helper to load and clean a single Excel file
for downstream modeling without touching the database.
"""

import glob
import pandas as pd
import sqlite3

DB_FILE = 'wish_logs.db'
NON_UP_CHARS = {
    "Diluc", "Dehya", "Tighnari",
    "Yumemizuki mizuki", "Mona",
    "Jean", "Keqing", "Qiqi"
}


def load_and_clean():
  
    excel_files = glob.glob('C:/Users/morridow/Desktop/Genshin wish logger_20250713_053717.xlsx')
    if not excel_files:
        print("❌ No Excel files found in data/")
        return

    frames = []
    for path in excel_files:
        print(f"🔄 Reading file: {path}")
        df = pd.read_excel(path, engine='openpyxl')

        # 1) Rename columns
        df = df.rename(columns={
            'time':         'timestamp',
            'name':         'name',
            'type':         'item_type',
            'rarity':       'rarity',
            'pull_number':  'pull_id',
            'within pity':  'pity_number',
            'remark':       'remark'
        })

        # 2) Parse timestamp
        if 'timestamp' not in df.columns:
            raise ValueError(f"Missing 'time' column in {path}")
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # 3) Compute primogem_cost = pull_id × 160
        df['primogem_cost'] = df['pull_id'] * 160

        # 4) Flag 5★ non-UP vs UP
        df['is_not_up'] = (df['rarity'] == 5) & df['name'].isin(NON_UP_CHARS)
        df['is_up']     = (df['rarity'] == 5) & (~df['name'].isin(NON_UP_CHARS))

        frames.append(df)

    # 5) Concatenate and write to SQLite
    all_data = pd.concat(frames, ignore_index=True)
    print(f"ℹ️ Loaded {len(all_data)} records. Writing to SQLite…")
    conn = sqlite3.connect(DB_FILE)
    all_data.to_sql('wish_logs', conn, if_exists='replace', index=False)
    conn.close()
    print(f"✅ Data written to '{DB_FILE}', table 'wish_logs'.")


def load_and_clean_excel(path: str) -> pd.DataFrame:
    """
    Reads a single wish-log Excel file, cleans it,
    and returns a DataFrame ready for modeling:
      - timestamp (datetime)
      - pull_number (int)
      - rarity (int)
      - name (str)
      - remark (str)
      - primogem_cost (int)
      - is_not_up (bool)
      - is_up (bool)
    """
    print(f"▶ Loading single Excel: {path}")
    df = pd.read_excel(path, engine='openpyxl')

    # 1) Rename and parse timestamp
    if 'time' not in df.columns:
        raise ValueError(f"Missing 'time' column in {path}")
    df = df.rename(columns={'time': 'timestamp'})
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # 2) Compute cost
    df['primogem_cost'] = df['pull_number'] * 160

    # 3) Flag non-UP vs UP
    df['is_not_up'] = (df['rarity'] == 5) & df['name'].isin(NON_UP_CHARS)
    df['is_up']     = (df['rarity'] == 5) & (~df['name'].isin(NON_UP_CHARS))

    return df


if __name__ == '__main__':
    load_and_clean()