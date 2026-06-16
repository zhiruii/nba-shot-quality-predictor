import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

st.title("NBA 2025-26 Shot Quality Predictor")
st.caption("Predicts the probability of an NBA shot going in based on shot characteristics and player shooting ability.")

st.subheader("Shot Location Reference")
st.caption("Use these reference coordinates when entering LOC_X and LOC_Y below. LOC_X: negative = left side, positive = right side.")

st.table({
    "Location": [
        "Restricted Area", "Block (left/right)", "Free Throw Line",
        "Elbow (left/right)", "Corner 3 (left/right)", "Wing 3 (left/right)", "Top of Key 3"
    ],
    "LOC_X": ["0", "±60", "0", "±150", "±220", "±185", "0"],
    "LOC_Y": [40, 50, 150, 100, 10, 170, 240],
})
