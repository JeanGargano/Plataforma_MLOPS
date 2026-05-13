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

reference = df[feature_cols].dropna().head(2000).copy()

rango_map = {
    "Bajo": 0,
    "Medio": 1,
    "Alto": 2
}

reference["rango_termico"] = reference["rango_termico"].map(rango_map)
reference["es_fin_de_semana"] = reference["es_fin_de_semana"].astype(int)
reference["rango_termico"] = reference["rango_termico"].astype(int)

os.makedirs("data/reference", exist_ok=True)
reference.to_csv("data/reference/reference.csv", index=False)

print(f"Reference generado: {len(reference)} filas")
print(reference.head(3))
print(reference.dtypes)