import streamlit as st
import requests

FASTAPI_URL = "http://127.0.0.1:8000"

st.title("NBA 2025-26 Shot Predictor")

player_id = st.number_input("Player ID", value=2544)
shot_distance = st.number_input("Shot Distance (ft)", value=5)

if st.button("Predict"):
    response = requests.post(f"{FASTAPI_URL}/predict", json ={
        "SHOT_DISTANCE": shot_distance,
        "LOC_X": 0,
        "LOC_Y": 50,
        "MINUTES_REMAINING": 3,
        "SECONDS_REMAINING": 30,
        "PERIOD": 2,
        "SHOT_TYPE": "2PT Field Goal",
        "SHOT_ZONE_BASIC": "Restricted Area",
        "ACTION_TYPE": "Driving Layup",
        "PLAYER_ID": player_id

    })

    prob = response.json()
    st.write(f"Make probability: {prob:.1%}")