import os
import hashlib
import pandas as pd
import yaml
import joblib
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split


def load_params(path: str = "/app/params.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def encode_categoricals(df: pd.DataFrame, params: dict):
    """
    Label Encoding para features categóricas:
      - es_fin_de_semana : 0 / 1  (ya es numérico, solo se incluye)
      - rango_termico    : Bajo / Medio / Alto -> 0 / 1 / 2
    """
    df       = df.copy()
    encoders = {}

    for col in params["preprocess"]["categorical_features"]:
        le = LabelEncoder()
        df[f"{col}_enc"] = le.fit_transform(df[col].astype(str))
        encoders[col]    = le
        mapping = dict(zip(le.classes_, le.transform(le.classes_)))
        print(f"  Encoding '{col}': {mapping}")

    return df, encoders


def preprocess(params: dict) -> None:
    raw_path       = params["data"]["raw_path"]
    processed_path = params["data"]["processed_path"]
    target_col     = params["preprocess"]["target_column"]
    random_state   = params["preprocess"]["random_state"]
    test_size      = params["preprocess"]["test_size"]
    shuffle        = params["split"]["shuffle"]

    os.makedirs(processed_path, exist_ok=True)

    print("Cargando dataset...")
    df = pd.read_csv(raw_path)

    # ----------------------------------------------------------
    # 1. Limpieza básica
    # ----------------------------------------------------------
    filas_inicial = len(df)
    df = df.dropna()
    df = df[df[target_col] > params["validate"]["min_consumo"]]
    df = df[df[target_col] < params["validate"]["max_consumo"]]
    print(f"Limpieza: {filas_inicial} -> {len(df)} filas "
          f"({filas_inicial - len(df)} eliminadas)")

    # ----------------------------------------------------------
    # 2. Encoding de categóricas
    # ----------------------------------------------------------
    print("Aplicando encoding...")
    df, encoders = encode_categoricals(df, params)

    # Features finales
    numerical_features  = params["preprocess"]["numerical_features"]
    categorical_encoded = [f"{c}_enc" for c in params["preprocess"]["categorical_features"]]
    feature_cols        = numerical_features + categorical_encoded

    X = df[feature_cols]
    y = df[target_col]

    print(f"Features del modelo ({len(feature_cols)}): {feature_cols}")

    # ----------------------------------------------------------
    # 3. Split temporal sin shuffle (serie de tiempo)
    # ----------------------------------------------------------
    n       = len(X)
    n_test  = int(n * test_size)
    n_train = n - n_test

    X_train = X.iloc[:n_train]
    X_test  = X.iloc[n_train:]
    y_train = y.iloc[:n_train]
    y_test  = y.iloc[n_train:]

    X_train = X_train.reset_index(drop=True)
    X_test  = X_test.reset_index(drop=True)
    y_train = y_train.reset_index(drop=True)
    y_test  = y_test.reset_index(drop=True)

    print(f"Split temporal: train={len(X_train)} | test={len(X_test)}")

    # ----------------------------------------------------------
    # 4. Normalización con MinMaxScaler
    #    fit solo en train, transform en test
    # ----------------------------------------------------------
    scaler = MinMaxScaler()

    X_train_scaled = X_train.copy()
    X_test_scaled  = X_test.copy()

    X_train_scaled[numerical_features] = scaler.fit_transform(X_train[numerical_features])
    X_test_scaled[numerical_features]  = scaler.transform(X_test[numerical_features])

    print("Normalización MinMaxScaler aplicada")

    # ----------------------------------------------------------
    # 5. Guarda artefactos
    # ----------------------------------------------------------
    X_train_scaled.to_csv(f"{processed_path}X_train.csv", index=False)
    X_test_scaled.to_csv(f"{processed_path}X_test.csv",   index=False)
    y_train.to_csv(f"{processed_path}y_train.csv",        index=False)
    y_test.to_csv(f"{processed_path}y_test.csv",          index=False)

    # Scaler y encoders los usará el prediction_service
    joblib.dump(scaler,   f"{processed_path}scaler.pkl")
    joblib.dump(encoders, f"{processed_path}encoders.pkl")

    # ----------------------------------------------------------
    # 6. Hash reproducibilidad (R4.2)
    # ----------------------------------------------------------
    hash_val = hashlib.md5(X_train_scaled.to_json().encode()).hexdigest()

    print(f"\nArtefactos guardados en : {processed_path}")
    print(f"Hash reproducibilidad   : {hash_val}")
    print(f"Artefactos              : X_train, X_test, y_train, y_test, scaler.pkl, encoders.pkl")


if __name__ == "__main__":
    params = load_params()
    preprocess(params)