import streamlit as st
import requests

FASTAPI_URL = "https://nba-shot-predictor-ggd6.onrender.com"

st.title("NBA Shot Quality Predictor")
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

st.divider()
st.subheader("Shot Details")

col1, col2 = st.columns(2)
with col1:
    shot_type = st.selectbox("Shot Type", ["2PT Field Goal", "3PT Field Goal"])
    shot_zone = st.selectbox("Shot Zone", [
        "Restricted Area", "In The Paint (Non-RA)", "Mid-Range",
        "Left Corner 3", "Right Corner 3", "Above the Break 3", "Backcourt"
    ])
    action_type = st.selectbox("Action Type", [
        "Jump Shot", "Pullup Jump Shot", "Driving Layup", "Running Layup",
        "Step Back Jump Shot", "Turnaround Jump Shot", "Cutting Layup Shot",
        "Fadeaway Jump Shot", "Floating Jump Shot", "Layup", "Dunk",
        "Hook Shot", "Putback Dunk Shot"
    ])
with col2:
    shot_distance = st.number_input("Shot Distance (ft)", min_value=0, max_value=94, value=15)
    loc_x = st.number_input("LOC_X (−250 left to 250 right)", min_value=-250, max_value=250, value=0)
    loc_y = st.number_input("LOC_Y (0 at basket to 470 halfcourt)", min_value=0, max_value=470, value=150)

st.divider()
st.subheader("Game Situation")

col3, col4, col5 = st.columns(3)
with col3:
    period = st.number_input("Period", min_value=1, max_value=7, value=2)
with col4:
    minutes = st.number_input("Minutes Remaining", min_value=0, max_value=11, value=5)
with col5:
    seconds = st.number_input("Seconds Remaining", min_value=0, max_value=59, value=30)

st.divider()
st.subheader("Shooter Ability")
st.caption("Season averages. Elite FG%: ~54% | Average: ~46% | Poor: ~38%. Elite 3PT%: ~42% | Average: ~35% | Poor: ~28%.")

col6, col7 = st.columns(2)
with col6:
    fg_pct = st.number_input("FG% (0.00 – 1.00)", min_value=0.0, max_value=1.0, value=0.46, step=0.01, format="%.2f")
with col7:
    fg3_pct = st.number_input("3PT% (0.00 – 1.00)", min_value=0.0, max_value=1.0, value=0.35, step=0.01, format="%.2f")

st.divider()

if st.button("Predict", type="primary"):
    response = requests.post(f"{FASTAPI_URL}/predict", json={
        "SHOT_DISTANCE": shot_distance,
        "LOC_X": loc_x,
        "LOC_Y": loc_y,
        "MINUTES_REMAINING": minutes,
        "SECONDS_REMAINING": seconds,
        "PERIOD": period,
        "SHOT_TYPE": shot_type,
        "SHOT_ZONE_BASIC": shot_zone,
        "ACTION_TYPE": action_type,
        "FG_PCT": fg_pct,
        "FG3_PCT": fg3_pct,
    })
    prob = response.json()
    st.metric(label="Make Probability", value=f"{prob:.1%}")
