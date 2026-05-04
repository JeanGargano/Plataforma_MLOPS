import os
import joblib
import pandas as pd
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from schemas      import PredictionInput, PredictionOutput, HealthResponse
from model_loader import load_model, MODEL_URI
from logger       import log_prediction


# Estado global del servidor
state = {
    "model"   : None,
    "scaler"  : None,
    "encoders": None,
}


# LIFESPAN — carga modelo y artefactos al arrancar el servidor
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carga modelo desde MLflow
    state["model"] = load_model()


# APP
app = FastAPI(
    title="Prediction Service — Energy Consumption",
    description="API REST para predicción de consumo de electrodomésticos",
    version="1.0.0",
    lifespan=lifespan
)


# ENDPOINTS
@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status        ="ok",
        model_loaded  =state["model"] is not None,
        modelo_version=MODEL_URI
    )


@app.post("/predict", response_model=PredictionOutput)
def predict(data: PredictionInput):
    if state["model"] is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")

    input_dict = data.model_dump()
    
    # 4. Predicción
    prediction = state["model"].predict(data)
    result     = round(float(prediction[0]), 4)

    # 5. Loguea para monitoreo de drift
    log_prediction(input_dict, result)

    return PredictionOutput(
        consumo_electrodomesticos=result,
        modelo_version           =MODEL_URI,
        unidad                   ="Wh"
    )