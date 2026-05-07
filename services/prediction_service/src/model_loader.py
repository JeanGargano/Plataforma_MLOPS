import os
import mlflow
import mlflow.pyfunc


MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000")
MODEL_URI  = os.getenv("MODEL_URI", "models:/prediction-energy-model/Production")


def load_model():
    """
    Carga el modelo en estado Production desde MLflow Model Registry.
    Se ejecuta UNA SOLA VEZ al arrancar el servidor (lifespan).
    El modelo queda en memoria RAM para inferencia de baja latencia.
    """
    mlflow.set_tracking_uri(MLFLOW_URI)
    print(f"Conectando a MLflow: {MLFLOW_URI}")
    print(f"Cargando modelo   : {MODEL_URI}")

    model = mlflow.pyfunc.load_model(MODEL_URI)
    print("Modelo cargado correctamente en memoria.")
    return model