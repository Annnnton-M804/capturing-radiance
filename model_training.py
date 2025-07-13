#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive Model Training Script for Genshin “Capturing Radiance”

Workflow:
1. Prompt user for the path to a single wish-log Excel file
2. Load & clean the data:
   - Rename “time” → “timestamp” and parse as datetime
   - Compute primogem_cost = pull_number × 160
   - Flag 5★ non-UP vs UP pulls
3. Flag Capturing Radiance events by:
   a) remark contains “capturing radiance” or “捕获明光”
   b) every 4th non-UP → UP cycle among 5★ pulls
4. Build features: pull_number, is_not_up, failsafe_cycle
5. Train:
   • XGBClassifier (with scale_pos_weight for class imbalance)
   • XGBRegressor
6. Report ROC AUC & MAE
7. Save both models to disk
"""

import sys
import pandas as pd
from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, mean_absolute_error
import joblib

# Define which 5★ characters are considered non-UP
NON_UP_CHARS = {
    "Diluc", "Dehya", "Tighnari",
    "Yumemizuki mizuki", "Mona",
    "Jean", "Keqing", "Qiqi"
}


def main():
    # 1) Prompt for Excel file path
    path = input(
        "Enter full path to your wish-log Excel file\n"
        "(e.g. C:\\Users\\morridow\\Desktop\\wish_log.xlsx):\n"
    ).strip()
    print(f"▶ Loading data from: {path}")

    # 2) Load & clean
    df = pd.read_excel(path, engine='openpyxl')
    # Rename and parse timestamp
    if 'time' not in df.columns:
        print("❌ ERROR: the Excel file must have a 'time' column.")
        sys.exit(1)
    df = df.rename(columns={'time': 'timestamp'})
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Compute primogem_cost
    if 'pull_number' not in df.columns:
        print("❌ ERROR: the Excel file must have a 'pull_number' column.")
        sys.exit(1)
    df['primogem_cost'] = df['pull_number'] * 160
    # Flag 5★ non-UP vs UP
    df['is_not_up'] = (df['rarity'] == 5) & df['name'].isin(NON_UP_CHARS)
    df['is_up']     = (df['rarity'] == 5) & (~df['name'].isin(NON_UP_CHARS))

    # 3) Flag Capturing Radiance by remark
    print("▶ Flagging Radiance events from remarks...")
    df['is_fate_capture'] = df['remark'].fillna('').str.contains(
        r'capturing radiance|捕获明光',
        case=False,
        regex=True
    )

    # 4) Flag by non-UP → UP cycle logic
    print("▶ Applying non-UP → UP cycle logic...")
    df5 = df[df['rarity'] == 5].sort_values('timestamp').reset_index(drop=False)
    cycle_count    = 0
    waiting_not_up = False
    radiance_idxs  = []
    for _, row in df5.iterrows():
        if row['is_not_up']:
            waiting_not_up = True
        elif row['is_up'] and waiting_not_up:
            cycle_count += 1
            waiting_not_up = False
            if cycle_count % 4 == 0:
                radiance_idxs.append(row['index'])
    df.loc[radiance_idxs, 'is_fate_capture'] = True
    df['failsafe_cycle'] = df.index.isin(radiance_idxs).astype(int)

    # 5) Prepare features & targets
    print("▶ Preparing features and targets...")
    X = df[['pull_number', 'is_not_up', 'failsafe_cycle']].astype(int)
    y_cls = df['is_fate_capture'].astype(int)
    y_reg = df['primogem_cost']

    # 6) Compute class weight
    pos = y_cls.sum()
    neg = len(y_cls) - pos
    scale_pos_weight = (neg / pos) if pos > 0 else 1.0
    print(f"▶ scale_pos_weight = {scale_pos_weight:.1f} (neg={neg}, pos={pos})")

    # 7) Split data
    print("▶ Splitting into train/test sets...")
    Xc_tr, Xc_te, ytr_c, yte_c = train_test_split(
        X, y_cls, test_size=0.2, random_state=42, stratify=y_cls
    )
    Xr_tr, Xr_te, ytr_r, yte_r = train_test_split(
        X, y_reg, test_size=0.2, random_state=42
    )

    # 8) Train classifier
    print("▶ Training XGBoost classifier...")
    clf = XGBClassifier(
        use_label_encoder=False,
        eval_metric='logloss',
        scale_pos_weight=scale_pos_weight,
        n_jobs=-1
    )
    clf.fit(Xc_tr, ytr_c)
    if len(yte_c.unique()) == 2:
        prob = clf.predict_proba(Xc_te)[:, 1]
        auc = roc_auc_score(yte_c, prob)
        print(f"✔ Classifier ROC AUC: {auc:.4f}")
    else:
        acc = clf.score(Xc_te, yte_c)
        print(f"✔ Single-class test set; Accuracy: {acc:.4f}")

    # 9) Train regressor
    print("▶ Training XGBoost regressor...")
    reg = XGBRegressor(n_jobs=-1)
    reg.fit(Xr_tr, ytr_r)
    preds = reg.predict(Xr_te)
    mae = mean_absolute_error(yte_r, preds)
    print(f"✔ Regressor MAE: {mae:.1f} primogems")

    # 10) Save models
    print("▶ Saving models to disk...")
    joblib.dump(clf, 'cls_model.joblib')
    joblib.dump(reg, 'reg_model.joblib')
    print("✅ Models saved: cls_model.joblib, reg_model.joblib")


if __name__ == '__main__':
    main()