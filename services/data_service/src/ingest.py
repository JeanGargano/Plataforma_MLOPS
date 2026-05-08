import os
import pandas as pd
import numpy as np
import yaml

def load_params(path: str = "/app/params.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def ingest(params: dict) -> None:
    raw_path   = params["data"]["raw_path"]
    
    print("Iniciando ingesta de datos...")
    print(f"Leyendo: {raw_path}")

    raw = pd.read_csv(raw_path)

    print(f"Shape original : {raw.shape}")
    print(f"Columnas       : {raw.columns.tolist()}")

    df = raw.copy()

    target = params["preprocess"]["target_column"]
    print(f"\nDataset listo:")
    print(f"  Shape    : {df.shape}")
    print(f"  Columnas : {df.columns.tolist()}")
    print(f"  Target   : min={df[target].min():.2f} | max={df[target].max():.2f} | media={df[target].mean():.2f}")
    print(f"  Guardado en: {raw_path}")

if __name__ == "__main__":
    params = load_params()
    ingest(params)
