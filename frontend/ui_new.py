import io
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests
import streamlit as st
from matplotlib.patches import Arc, Circle, Rectangle
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

FASTAPI_URL = "https://nba-shot-predictor-ggd6.onrender.com"

X_MIN, X_MAX = -250, 250
Y_MIN, Y_MAX = -47.5, 422.5

IMG_W = int(X_MAX - X_MIN)
IMG_H = int(Y_MAX - Y_MIN)

@st.cache_data
def court_image_bytes():
    fig = plt.figure(figsize=(IMG_W / 100, IMG_H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(X_MIN, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.axis("off")
    ax.set_facecolor("#f8f4ec")
    fig.patch.set_facecolor("#f8f4ec")

    color, lw = "#333333", 1.5
    # Hoop and backboard
    ax.add_patch(Circle((0, 0), 7.5, fill=False, color=color, lw=lw))
    ax.plot([-30, 30], [-7.5, -7.5], color=color, lw=lw)
    
    # Paint and free-throw circle
    ax.add_patch(Rectangle((-80, Y_MIN), 160, 190, fill=False, color=color, lw=lw))
    ax.add_patch(Rectangle((-60, Y_MIN), 120, 190, fill=False, color=color, lw=lw))
    ax.add_patch(Arc((0, 142.5), 120, 120, theta1=0, theta2=180, color=color, lw=lw))
    ax.add_patch(Arc((0, 142.5), 120, 120, theta1=180, theta2=360, color=color, lw=lw, linestyle="--"))
    
    # Restricted area arc
    ax.add_patch(Arc((0, 0), 80, 80, theta1=0, theta2=180, color=color, lw=lw))
    
    # Three-point line: corner segments + arc
    corner_y = math.sqrt(237.5**2 - 220**2)
    ax.plot([-220, -220], [Y_MIN, corner_y], color=color, lw=lw)
    ax.plot([220, 220], [Y_MIN, corner_y], color=color, lw=lw)
    theta = math.degrees(math.atan2(corner_y, 220))
    ax.add_patch(Arc((0, 0), 475, 475, theta1=theta, theta2=180 - theta, color=color, lw=lw))
   
    # Halfcourt line and center circle
    ax.plot([X_MIN, X_MAX], [Y_MAX, Y_MAX], color=color, lw=lw)
    ax.add_patch(Arc((0, Y_MAX), 120, 120, theta1=180, theta2=360, color=color, lw=lw))
    
    # Court boundary
    ax.add_patch(Rectangle((X_MIN, Y_MIN), IMG_W, IMG_H, fill=False, color=color, lw=2))

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    return buf.getvalue()


def data_to_pixel(loc_x, loc_y):
    px = (loc_x - X_MIN) / (X_MAX - X_MIN) * IMG_W
    py = (Y_MAX - loc_y) / (Y_MAX - Y_MIN) * IMG_H
    return px, py


def pixel_to_data(px, py, disp_w, disp_h):
    loc_x = px / disp_w * (X_MAX - X_MIN) + X_MIN
    loc_y = Y_MAX - py / disp_h * (Y_MAX - Y_MIN)
    return round(loc_x), round(loc_y)

def derive_shot(loc_x, loc_y):
    dist_tenths = math.hypot(loc_x, loc_y)
    distance_ft = int(dist_tenths // 10)
    if loc_y > Y_MAX:
        return distance_ft, "3PT Field Goal", "Backcourt"
    if loc_y <= 87.5 and loc_x <= -220:
        return distance_ft, "3PT Field Goal", "Left Corner 3"
    if loc_y <= 87.5 and loc_x >= 220:
        return distance_ft, "3PT Field Goal", "Right Corner 3"
    if loc_y > 87.5 and dist_tenths >= 237.5:
        return distance_ft, "3PT Field Goal", "Above the Break 3"
    if dist_tenths < 40:
        return distance_ft, "2PT Field Goal", "Restricted Area"
    if abs(loc_x) <= 80 and loc_y <= 138.5:
        return distance_ft, "2PT Field Goal", "In The Paint (Non-RA)"
    return distance_ft, "2PT Field Goal", "Mid-Range"

SHOT_TYPES = ["2PT Field Goal", "3PT Field Goal"]
SHOT_ZONES = [
    "Restricted Area", "In The Paint (Non-RA)", "Mid-Range",
    "Left Corner 3", "Right Corner 3", "Above the Break 3", "Backcourt",
]

if "loc_x" not in st.session_state:
    st.session_state.loc_x = 0
    st.session_state.loc_y = 150
    d, t, z = derive_shot(0, 150)
    st.session_state.shot_distance = d
    st.session_state.shot_type = t
    st.session_state.shot_zone = z

st.title("NBA Shot Quality Predictor")
st.caption("Predicts the probability of an NBA shot going in based on shot characteristics and player shooting ability.")

court_col, fields_col = st.columns([3, 2])

with court_col:
    img = Image.open(io.BytesIO(court_image_bytes())).convert("RGB")
    px, py = data_to_pixel(st.session_state.loc_x, st.session_state.loc_y)
    draw = ImageDraw.Draw(img)
    
    r = 7
    draw.ellipse([px - r, py - r, px + r, py + r], outline="#d9391f", width=3)
    draw.line([px - r - 4, py, px + r + 4, py], fill="#d9391f", width=1)
    draw.line([px, py - r - 4, px, py + r + 4], fill="#d9391f", width=1)
    
    click = streamlit_image_coordinates(img, key="court", cursor="crosshair", use_column_width="always")

    if click is not None:
        raw = (click["x"], click["y"])
        if st.session_state.get("last_click") != raw:
            st.session_state.last_click = raw
            loc_x, loc_y = pixel_to_data(click["x"], click["y"], click["width"], click["height"])
            st.session_state.loc_x = loc_x
            st.session_state.loc_y = loc_y
            d, t, z = derive_shot(loc_x, loc_y)
            st.session_state.shot_distance = d
            st.session_state.shot_type = t
            st.session_state.shot_zone = z
            st.rerun()

with fields_col:
    st.number_input("LOC_X (−250 left to 250 right)", min_value=-250, max_value=250, key="loc_x")
    st.number_input("LOC_Y (−47 baseline to 422 halfcourt)", min_value=-47, max_value=422, key="loc_y")
    st.number_input("Shot Distance (ft)", min_value=0, max_value=94, key="shot_distance")
    st.selectbox("Shot Type", SHOT_TYPES, key="shot_type")
    st.selectbox("Shot Zone", SHOT_ZONES, key="shot_zone")

st.divider()
st.subheader("Shot Details") 

action_type = st.selectbox("Action Type", [
    "Jump Shot", "Pullup Jump Shot", "Driving Layup", "Running Layup",
    "Step Back Jump Shot", "Turnaround Jump Shot", "Cutting Layup Shot",
    "Fadeaway Jump Shot", "Floating Jump Shot", "Layup", "Dunk",
    "Hook Shot", "Putback Dunk Shot",
])

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
        "SHOT_DISTANCE": st.session_state.shot_distance,
        "LOC_X": st.session_state.loc_x,
        "LOC_Y": st.session_state.loc_y,
        "MINUTES_REMAINING": minutes,
        "SECONDS_REMAINING": seconds,
        "PERIOD": period,
        "SHOT_TYPE": st.session_state.shot_type,
        "SHOT_ZONE_BASIC": st.session_state.shot_zone,
        "ACTION_TYPE": action_type,
        "FG_PCT": fg_pct,
        "FG3_PCT": fg3_pct,
    })
    prob = response.json()
    st.metric(label="Make Probability", value=f"{prob:.1%}")
