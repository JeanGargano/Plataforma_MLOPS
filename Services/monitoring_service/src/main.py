from fastapi import FastAPI, Response
from prometheus_client import generate_latest, Gauge, CONTENT_TYPE_LATEST
from src.drift_detector import calculate_drift, CURRENT_PATH
import pandas as pd
import os

app = FastAPI(title="MLOps Monitoring Service")

# Declarar métricas para Prometheus (Data Drift)
DRIFT_SHARE_GAUGE = Gauge('dataset_drift_share', 'Proporción de columnas con data drift (0.0 a 1.0)')
HAS_DRIFT_GAUGE = Gauge('dataset_has_drift', '1 si hay drift general detectado, 0 si está normal')

# Declarar nuevas métricas para Prometheus (Comportamiento del Modelo)
PREDICTIONS_COUNT_GAUGE = Gauge('model_predictions_total', 'Total de predicciones recientes analizadas')
AVG_PREDICTION_GAUGE = Gauge('model_avg_prediction', 'Valor promedio del consumo predicho en la ventana actual')

def update_metrics():
    print("Actualizando métricas para Prometheus...")
    
    # 1. Actualizar métricas de Drift
    drift_result = calculate_drift()
    if drift_result:
        share = float(drift_result.get('share_of_drifted_columns', 0.0))
        has_drift = 1.0 if drift_result.get('dataset_drift') else 0.0
        DRIFT_SHARE_GAUGE.set(share)
        HAS_DRIFT_GAUGE.set(has_drift)
        
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