#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Streamlit App:
- Load the trained XGBoost models for Radiance probability and gem-cost estimation
- Let the user input:
    • current pull number (pity count)
    • number of consecutive NOT-UP 5★ pulls
- Derive the failsafe feature: True if the user has already gone through three NOT-UP→UP cycles
- Display:
    • Predicted chance of Capturing Radiance
    • Estimated additional primogems needed
"""

import streamlit as st
import joblib
import numpy as np

# Load saved models
clf = joblib.load('cls_model.joblib')
reg = joblib.load('reg_model.joblib')

st.title("Genshin Capturing Radiance Predictor")

# 1) User inputs
pity = st.slider(
    "Current Pull Number (Pity count)",
    min_value=0, max_value=90, value=45
)

loss_streak = st.number_input(
    "Consecutive NOT-UP 5★ Pulls",
    min_value=0, max_value=6, value=0, step=1
)

# 2) Compute features
# is_not_up: whether last pull was a non-UP 5★
is_not_up = 1 if loss_streak > 0 else 0
# failsafe: completed three full NOT-UP→UP cycles implies loss_streak ≥ 3*2 = 6
failsafe = 1 if loss_streak >= 6 else 0

# 3) Run prediction when button is clicked
if st.button("Predict Radiance Chance and Gem Cost"):
    features = np.array([[pity, is_not_up, failsafe]])
    prob = clf.predict_proba(features)[0, 1]
    cost = reg.predict(features)[0]

    st.markdown(f"**Chance of Capturing Radiance:** {prob:.2%}")
    st.markdown(f"**Estimated Additional Primogems Needed:** {cost:.0f}")

st.write("---")
st.write("**Notes:**")
st.write("- **Pity** = pulls since your last 5★.")
st.write("- **Consecutive NOT-UP** counts how many of your last pulls were 5★ non-UP hits.")
st.write("- **Failsafe** is triggered after three full rotations of NOT-UP → UP (i.e. 6 non-UP pulls), guaranteeing Radiance on the next UP.")