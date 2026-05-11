from fastapi import FastAPI
import pickle
from contextlib import asynccontextmanager

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
@app.post("/predict")
def predict_main(shot: ShotFeatures):
    shot_dict = shot.model_dump()
    return predict(app.state.model, app.state.encoder, app.state.scaler, shot_dict)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/model/info")
def model_info():
    return {
        "model": "LogisticRegression",
        "features": app.state.feature_names,
        "roc_auc": 0.65
    }