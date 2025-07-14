#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
predict_console.py

Automatically forecast your next “Capturing Radiance” chance by scanning
the first Excel wish‐log found under data/*.xlsx.

Logic:
1. Load & clean the Excel via data_loader.load_and_clean_excel
2. Isolate all 5★ pulls in chronological order
3. Identify the last Radiance event by checking 'capture radiance' in remark
   and record which character was pulled (that is the featured UP)
4. For the pulls *after* that Radiance event, count how many consecutive
   non-UP 5★ pulls occurred before the first UP
5. If there are ≥3 consecutive non-UP pulls, the next UP is guaranteed Radiance
   (100%); otherwise the base override chance is 0.018%
6. Also compute current pity, pulls until next 5★, and gems needed
"""

import glob
from data_loader import load_and_clean_excel

def main():
    # 1) Find the first Excel file
    files = glob.glob('C:/Users/morridow/Desktop/Genshin wish logger_20250713_053717.xlsx')
    if not files:
        print("ERROR: No Excel files found in data/*.xlsx")
        return
    path = files[0]
    print(f"Using file: {path}")

    # 2) Load and clean
    df = load_and_clean_excel(path)

    # 3) Filter to 5★ pulls and sort by time
    df5 = df[df['rarity'] == 5].sort_values('timestamp').reset_index(drop=True)

    # 4) Find the last Radiance event by remark
    rad_mask = df5['remark'].fillna('').str.contains('capture radiance', case=False)
    if not rad_mask.any():
        print("No previous Radiance event found in remarks.")
        # Without a prior Radiance, no UP is yet defined
        # Assume the featured UP is the most recent 5★ pulled
        up_name = df5['name'].iloc[-1]
        last_rad_pos = -1
    else:
        # the name of the character at the last Radiance event
        last_rad_idx = df5[rad_mask].index.max()
        up_name = df5.loc[last_rad_idx, 'name']
        last_rad_pos = last_rad_idx
        print(f"Detected last Radiance on {up_name} (row {last_rad_idx}).")

    # 5) Consider only pulls *after* that Radiance event
    recent = df5.iloc[last_rad_pos+1 :].reset_index(drop=True)

    # 6) Count consecutive non-UP pulls at the start of recent
    consec_non_up = 0
    for _, row in recent.iterrows():
        if row['name'] != up_name:
            consec_non_up += 1
        else:
            break

    # 7) Decide Radiance probability
    if consec_non_up >= 3:
        radiance_chance = 1.0
        guaranteed = True
    else:
        radiance_chance = 0.00018  # 0.018%
        guaranteed = False
 #  8) Current pity and pulls/gems until next 5★
    current_pity   = int(df['within pity'].iloc[-1])
    pulls_to_next5 = max(90- current_pity,0)
    gems_needed    = pulls_to_next5 * 160

    # 9) Output forecast
    print("\n=== Next Capturing Radiance Forecast ===")
    print(f"- Featured UP character:               {up_name}")
    print(f"- Consecutive non-UP pulls since last Radiance: {consec_non_up}")
    print(f"- Radiance chance on next UP:          {radiance_chance:.2%}")
    print(f"- Next UP guaranteed Radiance?         {'Yes' if guaranteed else 'No'}")
    print(f"- Current pity:                        {current_pity}")
    print(f"- Pulls until next 5★:                 {pulls_to_next5}")
    print(f"- Primogems needed:                    {gems_needed}")

if __name__ == '__main__':
    main()
