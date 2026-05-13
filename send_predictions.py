import pandas as pd
import requests
import time

URL = "http://prediction-service:8001/predict"

df = pd.read_csv("data/reference/reference.csv")

# Tomar 60 filas diferentes
sample = df.sample(n=200, random_state=42)

for i, row in sample.iterrows():
    payload = {
        "temperatura_sala": float(row["temperatura_sala"]),
        "consumo_iluminacion": float(row["consumo_iluminacion"]),
        "temperatura_exterior": float(row["temperatura_exterior"]),
        "humedad_exterior": float(row["humedad_exterior"]),
        "temperatura_meteorologica": float(row["temperatura_meteorologica"]),
        "hora": int(row["hora"]),
        "dia_semana": int(row["dia_semana"]),
        "mes": int(row["mes"]),
        "es_fin_de_semana_enc": int(row["es_fin_de_semana"]),
        "rango_termico_enc": int(row["rango_termico"])
    }

    r = requests.post(URL, json=payload)
    print(i, r.status_code, r.text)
    time.sleep(0.1)