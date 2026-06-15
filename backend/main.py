from fastapi import FastAPI
import pickle
from contextlib import asynccontextmanager

from pydantic import BaseModel

import db
from serve import predict
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    with open("artifacts/model.pkl", "rb") as f:
        app.state.model = pickle.load(f)

    with open("artifacts/encoder.pkl", "rb") as f:
        app.state.encoder = pickle.load(f)

    with open("artifacts/scaler.pkl", "rb") as f:
        app.state.scaler = pickle.load(f)

    with open("artifacts/feature_names.json", "r") as f:
        app.state.feature_names = json.load(f)

    app.state.player_stats = db.fetch_all_player_stats()

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