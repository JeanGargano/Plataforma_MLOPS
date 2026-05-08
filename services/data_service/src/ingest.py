import os
import pandas as pd
import numpy as np
import yaml


def load_params(path: str = "/app/params.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def ingest(params: dict) -> None:
    raw_path   = params["data"]["raw_path"]
    rename_map = params["ingest"]["rename_map"]
    cols_keep  = params["ingest"]["columns_keep"]

    print("Iniciando ingesta de datos...")
    print(f"Leyendo: {raw_path}")

    # 1. Carga el CSV original con columna date como datetime
    raw = pd.read_csv(raw_path, parse_dates=["date"])

    print(f"Shape original : {raw.shape}")
    print(f"Columnas       : {raw.columns.tolist()}")

    # 2. Selecciona solo las columnas necesarias
    df = raw[cols_keep].copy()

    # 3. Renombra columnas al español
    df = df.rename(columns=rename_map)

    # 4. Feature engineering desde la columna date
    df["hora"]             = df["date"].dt.hour
    df["dia_semana"]       = df["date"].dt.dayofweek   
    df["mes"]              = df["date"].dt.month
    df["es_fin_de_semana"] = df["date"].dt.dayofweek.isin([5, 6]).astype(int)

    # 5. Feature rango_termico (diferencia térmica sala vs exterior)
    bins   = params["preprocess"]["rango_termico_bins"]
    labels = params["preprocess"]["rango_termico_labels"]
    df["rango_termico"] = pd.cut(
        df["temperatura_sala"] - df["temperatura_exterior"],
        bins=bins,
        labels=labels
    ).astype(str)

    # 6. Elimina la columna date (ya se extrajeron los features)
    df = df.drop(columns=["date"])

    # 7. Sobreescribe el CSV con el dataset procesado listo
    df.to_csv(raw_path, index=False)

    target = params["preprocess"]["target_column"]
    print(f"\nDataset listo:")
    print(f"  Shape    : {df.shape}")
    print(f"  Columnas : {df.columns.tolist()}")
    print(f"  Target   : min={df[target].min():.2f} | "
          f"max={df[target].max():.2f} | "
          f"media={df[target].mean():.2f}")
    print(f"  Guardado en: {raw_path}")


if __name__ == "__main__":
    params = load_params()
    ingest(params)