import os
import pandas as pd
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor


# ==============================================================
# CONFIGURACIÓN
# ==============================================================
MLFLOW_URI     = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000")
EXPERIMENT     = os.getenv("EXPERIMENT_NAME",     "energy-consumption-prediction")
PROCESSED_PATH = os.getenv("PROCESSED_PATH",      "/app/data/processed/")
MODEL_NAME     = os.getenv("MODEL_NAME",           "prediction-energy-model")

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


# ==============================================================
# FUNCIONES
# ==============================================================
def load_data():
    """Carga los artefactos generados por el data_service."""
    print("Cargando artefactos del data_service...")

    X_train = pd.read_csv(f"{PROCESSED_PATH}X_train.csv")
    X_test  = pd.read_csv(f"{PROCESSED_PATH}X_test.csv")
    y_train = pd.read_csv(f"{PROCESSED_PATH}y_train.csv").squeeze()
    y_test  = pd.read_csv(f"{PROCESSED_PATH}y_test.csv").squeeze()

    print(f"  X_train : {X_train.shape}")
    print(f"  X_test  : {X_test.shape}")
    print(f"  y_train : {y_train.shape}")
    print(f"  y_test  : {y_test.shape}")

    return X_train, X_test, y_train, y_test


def evaluate(y_true, y_pred) -> dict:
    """Calcula MAE, RMSE y R2."""
    return {
        "mae" : round(float(mean_absolute_error(y_true, y_pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 4),
        "r2"  : round(float(r2_score(y_true, y_pred)), 4)
    }


def train_and_log(model, model_name: str, params: dict,
                  X_train, X_test, y_train, y_test) -> dict:
    """
    Entrena un modelo, calcula métricas y registra en MLflow.
    Retorna un dict con nombre, run_id y métricas de test.
    """
    # Cierra cualquier corrida que haya quedado colgando por error
    if mlflow.active_run():
        mlflow.end_run()

    with mlflow.start_run(run_name=model_name) as run:
        run_id = run.info.run_id

        # Entrenamiento
        model.fit(X_train, y_train)

        y_pred_train = model.predict(X_train)
        y_pred_test  = model.predict(X_test)

        train_metrics = evaluate(y_train, y_pred_train)
        test_metrics  = evaluate(y_test,  y_pred_test)

        # Log parámetros
        mlflow.log_params(params)
        mlflow.log_param("model_name",  model_name)
        mlflow.log_param("train_size",  len(X_train))
        mlflow.log_param("test_size",   len(X_test))
        mlflow.log_param("features",    FEATURE_COLS)

        # Log métricas train
        mlflow.log_metric("train_mae",  train_metrics["mae"])
        mlflow.log_metric("train_rmse", train_metrics["rmse"])
        mlflow.log_metric("train_r2",   train_metrics["r2"])

        # Log métricas test
        mlflow.log_metric("test_mae",   test_metrics["mae"])
        mlflow.log_metric("test_rmse",  test_metrics["rmse"])
        mlflow.log_metric("test_r2",    test_metrics["r2"])

        # Registra el modelo en el Model Registry
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=MODEL_NAME
        )



    print(f"\n  {model_name}")
    print(f"    Train -> MAE: {train_metrics['mae']} | RMSE: {train_metrics['rmse']} | R2: {train_metrics['r2']}")
    print(f"    Test  -> MAE: {test_metrics['mae']}  | RMSE: {test_metrics['rmse']}  | R2: {test_metrics['r2']}")
    print(f"    Run ID: {run_id}")

    return {
        "model_name": model_name,
        "model"     : model,
        "run_id"    : run_id,
        "test_mae"  : test_metrics["mae"],
        "test_rmse" : test_metrics["rmse"],
        "test_r2"   : test_metrics["r2"]
    }


# ==============================================================
# PIPELINE DE ENTRENAMIENTO
# ==============================================================
def run_training():
    # Cierra cualquier corrida que haya quedado colgando globalmente antes de empezar
    while mlflow.active_run():
        mlflow.end_run()

    # 1. Conecta con MLflow
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXPERIMENT)
    print(f"MLflow URI   : {MLFLOW_URI}")
    print(f"Experimento  : {EXPERIMENT}")

    # 2. Carga datos
    X_train, X_test, y_train, y_test = load_data()

    # 3. Entrena los 3 modelos
    print("\nEntrenando modelos...")

    results = []

    results.append(train_and_log(
        model      = LinearRegression(),
        model_name = "LinearRegression",
        params     = {"fit_intercept": True},
        X_train=X_train, X_test=X_test,
        y_train=y_train, y_test=y_test
    ))

    results.append(train_and_log(
        model      = RandomForestRegressor(n_estimators=100, random_state=42),
        model_name = "RandomForest",
        params     = {"n_estimators": 100, "random_state": 42},
        X_train=X_train, X_test=X_test,
        y_train=y_train, y_test=y_test
    ))

    results.append(train_and_log(
        model      = XGBRegressor(n_estimators=100, learning_rate=0.1,
                                  random_state=42, verbosity=0),
        model_name = "XGBoost",
        params     = {"n_estimators": 100, "learning_rate": 0.1, "random_state": 42},
        X_train=X_train, X_test=X_test,
        y_train=y_train, y_test=y_test
    ))

    # 4. Resumen comparativo
    print("\n" + "="*55)
    print("COMPARACION DE MODELOS (test set)")
    print("="*55)
    print(f"{'Modelo':<22} {'MAE':>8} {'RMSE':>8} {'R2':>8}")
    print("-"*55)
    for r in results:
        print(f"{r['model_name']:<22} {r['test_mae']:>8} {r['test_rmse']:>8} {r['test_r2']:>8}")

    # 5. Identifica el mejor por MAE
    best = min(results, key=lambda r: r["test_mae"])
    print(f"\nMejor modelo : {best['model_name']} (MAE={best['test_mae']})")

    return results, best


if __name__ == "__main__":
    run_training()