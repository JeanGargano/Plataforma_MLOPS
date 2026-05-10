import pandas as pd
import os

df = pd.read_csv("data/raw/KAG_energydata_complete.csv")

feature_cols = [
    "temperatura_sala",
    "consumo_iluminacion",
    "temperatura_exterior",
    "humedad_exterior",
    "temperatura_meteorologica",
    "hora",
    "dia_semana",
    "mes",
    "es_fin_de_semana",
    "rango_termico"
]

reference = df[feature_cols].dropna().head(2000)

os.makedirs("data/reference", exist_ok=True)
reference.to_csv("data/reference/reference.csv", index=False)

print(f"Reference generado: {len(reference)} filas")
print(reference.head(3))