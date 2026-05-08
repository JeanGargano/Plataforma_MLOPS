import os
import csv
import joblib
import numpy as np
from datetime import datetime


LOG_PATH      = os.getenv("LOG_PATH",      "/app/logs/predictions.csv")
PROCESSED_PATH= os.getenv("PROCESSED_PATH","/app/data/processed/")

# Columnas del log — deben coincidir con las features + metadata
LOG_COLUMNS = [
    "timestamp",
    "temperatura_sala",
    "consumo_iluminacion",
    "temperatura_exterior",
    "humedad_exterior",
    "temperatura_meteorologica",
    "hora",
    "dia_semana",
    "mes",
    "es_fin_de_semana",
    "rango_termico",
    "consumo_predicho"
]


def log_prediction(input_data: dict, prediction: float) -> None:
    """
    Loguea cada predicción en un CSV de producción.
    Este CSV es leído por el monitoring_service para detectar drift.
    """
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    file_exists = os.path.exists(LOG_PATH)

    row = {
        "timestamp"                : datetime.utcnow().isoformat(),
        "temperatura_sala"         : input_data.get("temperatura_sala"),
        "consumo_iluminacion"      : input_data.get("consumo_iluminacion"),
        "temperatura_exterior"     : input_data.get("temperatura_exterior"),
        "humedad_exterior"         : input_data.get("humedad_exterior"),
        "temperatura_meteorologica": input_data.get("temperatura_meteorologica"),
        "hora"                     : input_data.get("hora"),
        "dia_semana"               : input_data.get("dia_semana"),
        "mes"                      : input_data.get("mes"),
        "es_fin_de_semana" : input_data.get("es_fin_de_semana") or input_data.get("es_fin_de_semana_enc"),
        "rango_termico"    : input_data.get("rango_termico") or input_data.get("rango_termico_enc"),
        "consumo_predicho"         : round(prediction, 4)
    }

    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)