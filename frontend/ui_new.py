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
