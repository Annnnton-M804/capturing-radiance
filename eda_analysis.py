#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exploratory Data Analysis (corrected Radiance logic):
- Load wish_log data from SQLite
- Flag Capturing Radiance events by:
    1. remark contains “capturing radiance” or “捕获明光” (case-insensitive)
    2. every 4th non-UP → UP cycle among 5★ pulls
- Compute and print:
    • total 5★ pulls
    • NOT-UP vs UP counts & rates
    • total Capturing Radiance events
- Plot:
    1. Histogram of 5★ pity distribution
    2. Scatter of pity vs. primogem cost, colored by UP vs NOT-UP
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_FILE = 'wish_logs.db'

def run_eda():
    # 1. Load full table
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM wish_logs;", conn, parse_dates=['timestamp'])
    conn.close()

    # 2. Initialize the Radiance flag
    df['is_fate_capture'] = False

    # Method 1: explicit remark detection (English OR Chinese)
    remark_mask = df['remark'] \
        .fillna('') \
        .str.contains(r'capturing radiance|捕获明光', case=False, regex=True)
    df.loc[remark_mask, 'is_fate_capture'] = True

    # Method 2: non-UP → UP cycle logic
    df5 = df[df['rarity'] == 5].sort_values('timestamp')
    cycle_count    = 0
    waiting_not_up = False
    failsafe_idxs  = []

    for idx, row in df5.iterrows():
        if row['is_not_up']:
            # mark that we saw a non-UP, now awaiting the UP
            waiting_not_up = True

        elif row['is_up'] and waiting_not_up:
            # complete one non-UP → UP cycle
            cycle_count    += 1
            waiting_not_up = False

            # **only** every 4th such cycle is an actual Radiance trigger
            if cycle_count % 4 == 0:
                failsafe_idxs.append(idx)

    # apply the cycle-based flags
    df.loc[failsafe_idxs, 'is_fate_capture'] = True

    # 3. Compute summary statistics
    total_5   = len(df5)
    not_up_ct = df5['is_not_up'].sum()
    up_ct     = df5['is_up'].sum()
    # count Radiance only among actual 5★ pulls
    rad_ct    = df5.index.isin(failsafe_idxs).sum() + remark_mask[df5.index].sum()

    print("=== 5★ Pull Summary ===")
    print(f"Total 5★ pulls:            {total_5}")
    print(f"  – NOT-UP pulls:          {not_up_ct} ({not_up_ct/total_5:.2%})")
    print(f"  – UP pulls:              {up_ct} ({up_ct/total_5:.2%})")
    print(f"Capturing Radiance events: {rad_ct}")

    # 4. Plotting
    colors = df5['is_up'].map({True: 'C1', False: 'C0'})  # C1=UP, C0=NOT-UP

    plt.figure(figsize=(8,4))
    plt.hist(df5['pull_number'], bins=30, edgecolor='black', alpha=0.7)
    plt.xlabel("Pull Number (Pity)")
    plt.ylabel("Count")
    plt.title("Distribution of 5★ Pulls")
    plt.tight_layout()
    plt.show()

   
if __name__ == '__main__':
    run_eda()