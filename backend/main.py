from fastapi import FastAPI
import pickle
from contextlib import asynccontextmanager

import pandas as pd
from pydantic import BaseModel

from serve import predict
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    with open("model.pkl", "rb") as f:
        app.state.model = pickle.load(f)

    with open("encoder.pkl", "rb") as f:
        app.state.encoder = pickle.load(f)

    with open("scaler.pkl", "rb") as f:
        app.state.scaler = pickle.load(f)

    with open("feature_names.json", "r") as f:
        app.state.feature_names = json.load(f)

    player_df = pd.read_csv("player_stats.csv")
    app.state.player_stats = player_df.set_index("PLAYER_ID")[["FG_PCT", "FG3_PCT"]].to_dict(orient="index")

    yield

app = FastAPI(lifespan=lifespan)

class ShotFeatures(BaseModel):
    SHOT_DISTANCE: int
    LOC_X: int
    LOC_Y: int
    MINUTES_REMAINING: int
    SECONDS_REMAINING: int
    PERIOD: int
    SHOT_TYPE: str
    SHOT_ZONE_BASIC: str
    ACTION_TYPE: str
    PLAYER_ID: int
@app.post("/predict")
def predict_main(shot: ShotFeatures):
    shot_dict = shot.model_dump()
    return predict(app.state.model, app.state.encoder, app.state.scaler, shot_dict, player_stats=app.state.player_stats)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/model/info")
def model_info():
    return {
        "model": "LogisticRegression",
        "features": app.state.feature_names,
        "roc_auc": 0.654
    }