from fastapi import FastAPI, Response
from prometheus_client import generate_latest, Gauge, Counter,CONTENT_TYPE_LATEST
from src.drift_detector import calculate_drift, CURRENT_PATH
from datetime import datetime, timedelta
import pandas as pd
import requests
import os
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="MLOps Monitoring Service")
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


# Declarar métricas para Prometheus (Data Drift)
DRIFT_SHARE_GAUGE = Gauge('dataset_drift_share', 'Proporción de columnas con data drift (0.0 a 1.0)')
HAS_DRIFT_GAUGE = Gauge('dataset_has_drift', '1 si hay drift general detectado, 0 si está normal')

# Declarar nuevas métricas para Prometheus (Comportamiento del Modelo)
PREDICTIONS_COUNT_GAUGE = Gauge('model_predictions_total', 'Total de predicciones recientes analizadas')
AVG_PREDICTION_GAUGE = Gauge('model_avg_prediction', 'Valor promedio del consumo predicho en la ventana actual')

# Metrica para contar reentrenamientos
MODEL_RETRAIN_COUNTER = Counter(
    "model_retraining_total",
    "Cantidad total de reentrenamientos ejecutados por detección de drift"
)

TRAINING_URL = os.environ.get("TRAINING_URL", "http://training-service:8003/train")
last_retraining_time = None
RETRAIN_COOLDOWN_MINUTES = 30

def trigger_retraining():
    global last_retraining_time

    now = datetime.utcnow()

    if last_retraining_time and now - last_retraining_time < timedelta(minutes=RETRAIN_COOLDOWN_MINUTES):
        print("Reentrenamiento omitido: cooldown activo.")
        return
    
    last_retraining_time = now

    try:
        print("Drift detectado. Lanzando reentrenamiento...")
        response = requests.post(TRAINING_URL, timeout=120)
        print(f"Respuesta training-service: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            MODEL_RETRAIN_COUNTER.inc()
    except Exception as e:
        print(f"Error lanzando reentrenamiento: {e}")

def update_metrics():
    print("Actualizando métricas para Prometheus...")
    
    # 1. Actualizar métricas de Drift
    drift_result = calculate_drift()
    if drift_result:
        share = float(drift_result.get('share_of_drifted_columns', 0.0))
        has_drift = 1.0 if drift_result.get('dataset_drift') else 0.0
        DRIFT_SHARE_GAUGE.set(share)
        HAS_DRIFT_GAUGE.set(has_drift)
        
        if has_drift == 1.0 and not drift_result.get("not_enough_data", False):
            trigger_retraining()
    else:
        DRIFT_SHARE_GAUGE.set(0.0)
        HAS_DRIFT_GAUGE.set(0.0)
        
    # 2. Actualizar métricas de Comportamiento del Modelo
    if os.path.exists(CURRENT_PATH):
        try:
            current_data = pd.read_csv(CURRENT_PATH)
            # Cantidad de predicciones (tráfico)
            PREDICTIONS_COUNT_GAUGE.set(len(current_data))
            
            # Promedio de la predicción (si existe la columna)
            if 'consumo_predicho' in current_data.columns:
                avg_pred = current_data['consumo_predicho'].mean()
                AVG_PREDICTION_GAUGE.set(float(avg_pred))
        except Exception as e:
            print(f"Error leyendo métricas del modelo: {e}")

@app.on_event("startup")
def startup_event():
    # Cuando levanta la API, llenamos las métricas una vez
    update_metrics()

@app.get("/metrics")
def get_metrics():
    # Se actualizan las métricas al vuelo si alguien las consulta
    # (En producción esto podría hacerse con un job cada X minutos)
    update_metrics()
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health_check():
    return {"status": "monitoring service is alive and looking for drift!"}