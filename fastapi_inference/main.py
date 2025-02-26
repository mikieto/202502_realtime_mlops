# main.py
import os
from fastapi import FastAPI
from pydantic import BaseModel
import mlflow
import mlflow.xgboost
import numpy as np

# 1) Define request/response schema
class PredictRequest(BaseModel):
    trip_id_encoded: int
    current_stop_sequence: int
    day_of_week: int
    hour_of_day: int

class PredictResponse(BaseModel):
    predicted_travel_time: float

app = FastAPI()

# 2) Load model from MLflow or local artifact
# Option A: local model file path
# xgb_model = mlflow.xgboost.load_model("file:///app/model_artifacts")
# Option B: from MLflow tracking server
default_uri = "models:/MyXGBModel/Staging"  # fallback
model_uri = os.getenv("MODEL_URI", default_uri)  

print(f"Loading model from URI: {model_uri}")
xgb_model = mlflow.xgboost.load_model(model_uri)

@app.get("/")
def root():
    return {"message": "FastAPI for inference is running."}

# 3) /predict endpoint
@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # Convert input to numpy
    features = np.array([[req.trip_id_encoded,
                          req.current_stop_sequence,
                          req.day_of_week,
                          req.hour_of_day]], dtype=float)
    # Predict
    pred = xgb_model.predict(features)
    # Return as response
    return PredictResponse(predicted_travel_time=float(pred[0]))
