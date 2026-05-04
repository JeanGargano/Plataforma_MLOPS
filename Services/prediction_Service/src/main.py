import os
import joblib
import pandas as pd
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from schemas      import PredictionInput, PredictionOutput, HealthResponse
from model_loader import load_model, MODEL_URI
from logger       import log_prediction


PROCESSED_PATH = os.getenv("PROCESSED_PATH", "/app/data/processed/")

# ==============================================================
# Estado global del servidor
# ==============================================================
state = {
    "model"   : None,
    "scaler"  : None,
    "encoders": None,
}

NUMERICAL_FEATURES = [
    "temperatura_sala",
    "consumo_iluminacion",
    "temperatura_exterior",
    "humedad_exterior",
    "temperatura_meteorologica",
    "hora",
    "dia_semana",
    "mes"
]

CATEGORICAL_FEATURES = ["es_fin_de_semana", "rango_termico"]


# ==============================================================
# LIFESPAN — carga modelo y artefactos al arrancar el servidor
# ==============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carga modelo desde MLflow
    state["model"] = load_model()

    # Carga scaler y encoders generados por el data_service
    state["scaler"]   = joblib.load(f"{PROCESSED_PATH}scaler.pkl")
    state["encoders"] = joblib.load(f"{PROCESSED_PATH}encoders.pkl")
    print("Scaler y encoders cargados.")

    yield

    # Cleanup al apagar
    state["model"]    = None
    state["scaler"]   = None
    state["encoders"] = None


# ==============================================================
# APP
# ==============================================================
app = FastAPI(
    title="Prediction Service — Energy Consumption",
    description="API REST para predicción de consumo de electrodomésticos",
    version="1.0.0",
    lifespan=lifespan
)


# ==============================================================
# ENDPOINTS
# ==============================================================
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

    # ----------------------------------------------------------
    # 1. Encoding de categóricas (igual que en preprocess.py)
    # ----------------------------------------------------------
    encoded = {}
    for col in CATEGORICAL_FEATURES:
        le  = state["encoders"][col]
        val = str(input_dict[col])

        # Si el valor no fue visto en entrenamiento, asigna clase más cercana
        if val not in le.classes_:
            val = le.classes_[0]

        encoded[f"{col}_enc"] = int(le.transform([val])[0])

    # ----------------------------------------------------------
    # 2. Construye DataFrame con el mismo orden de features
    # ----------------------------------------------------------
    row = {col: input_dict[col] for col in NUMERICAL_FEATURES}
    row.update(encoded)

    feature_cols = NUMERICAL_FEATURES + [f"{c}_enc" for c in CATEGORICAL_FEATURES]
    df_input     = pd.DataFrame([row])[feature_cols]

    # ----------------------------------------------------------
    # 3. Normalización con el scaler del data_service
    # ----------------------------------------------------------
    df_scaled                      = df_input.copy()
    df_scaled[NUMERICAL_FEATURES]  = state["scaler"].transform(df_input[NUMERICAL_FEATURES])

    # ----------------------------------------------------------
    # 4. Predicción
    # ----------------------------------------------------------
    prediction = state["model"].predict(df_scaled)
    result     = round(float(prediction[0]), 4)

    # ----------------------------------------------------------
    # 5. Loguea para monitoreo de drift
    # ----------------------------------------------------------
    log_prediction(input_dict, result)

    return PredictionOutput(
        consumo_electrodomesticos=result,
        modelo_version           =MODEL_URI,
        unidad                   ="Wh"
    )