import os
import joblib
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from schemas      import PredictionInput, PredictionOutput, HealthResponse
from model_loader import load_model, MODEL_URI
from logger       import log_prediction
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


PROCESSED_PATH = os.getenv("PROCESSED_PATH", "/app/data/processed/")

state = {
    "model"  : None,
    "scaler" : None,
}

FEATURE_COLS = [
    "temperatura_sala",
    "consumo_iluminacion",
    "temperatura_exterior",
    "humedad_exterior",
    "temperatura_meteorologica",
    "hora",
    "dia_semana",
    "mes",
    "es_fin_de_semana_enc",
    "rango_termico_enc"
]


# LIFESPAN
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carga modelo desde MLflow
    state["model"]  = load_model()

    # Carga scaler generado por el data_service
    state["scaler"] = joblib.load(f"{PROCESSED_PATH}scaler.pkl")
    print("Modelo y scaler cargados correctamente.")

    yield  # <-- servidor corriendo

    # Cleanup al apagar
    state["model"]  = None
    state["scaler"] = None


# APP
app = FastAPI(
    title="Prediction Service — Energy Consumption",
    description="API REST para predicción de consumo de electrodomésticos",
    version="1.0.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

    # 1. Construye DataFrame con el orden exacto de features
    df = pd.DataFrame([input_dict])[FEATURE_COLS]

    # 2. Aplica scaler (solo columnas numericas, igual que en preprocess.py)
    numerical_cols = [
        "temperatura_sala", "consumo_iluminacion", "temperatura_exterior",
        "humedad_exterior", "temperatura_meteorologica",
        "hora", "dia_semana", "mes"
    ]
    df[numerical_cols] = state["scaler"].transform(df[numerical_cols])

    # 3. Prediccion
    prediction = state["model"].predict(df)
    result     = round(float(prediction[0]), 4)

    # 4. Loguea para monitoreo de drift
    log_prediction(input_dict, result)

    return PredictionOutput(
        consumo_electrodomesticos=result,
        modelo_version           =MODEL_URI,
        unidad                   ="Wh"
    )