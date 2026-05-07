import os
import mlflow
from mlflow.tracking import MlflowClient


MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000")
MODEL_NAME = os.getenv("MODEL_NAME",           "prediction-energy-model")


def promote_best_model(run_id: str, metrics: dict) -> None:
    """
    Promueve un modelo específico (por run_id) a Production en MLflow.
    Archiva automáticamente la versión anterior.

    Flujo: None -> Staging -> Production
    """
    mlflow.set_tracking_uri(MLFLOW_URI)
    client = MlflowClient()

    # Busca la versión del modelo asociada al run_id
    all_versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    target       = next((v for v in all_versions if v.run_id == run_id), None)

    if not target:
        print(f"No se encontró versión del modelo para run_id: {run_id}")
        return

    version = target.version
    print(f"Modelo encontrado: {MODEL_NAME} v{version} (run_id={run_id})")

    # Staging
    client.transition_model_version_stage(
        name=MODEL_NAME, version=version, stage="Staging"
    )
    print(f"  v{version} -> Staging")

    # Production (archiva la versión anterior)
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=version,
        stage="Production",
        archive_existing_versions=True
    )
    print(f"  v{version} -> Production")

    # Agrega nota justificativa con métricas
    client.update_model_version(
        name=MODEL_NAME,
        version=version,
        description=(
            f"Promovido a Production. "
            f"MAE={metrics.get('test_mae')} | "
            f"RMSE={metrics.get('test_rmse')} | "
            f"R2={metrics.get('test_r2')}"
        )
    )
    print(f"  Nota justificativa agregada")
    print(f"\nModelo {MODEL_NAME} v{version} activo en Production")


if __name__ == "__main__":
    # Cuando se llama directamente, promueve la versión más reciente en Staging
    mlflow.set_tracking_uri(MLFLOW_URI)
    client   = MlflowClient()
    staging  = client.get_latest_versions(MODEL_NAME, stages=["Staging"])

    if not staging:
        print("No hay modelos en Staging para promover.")
    else:
        v = staging[0]
        promote_best_model(
            run_id=v.run_id,
            metrics={"test_mae": "N/A", "test_rmse": "N/A", "test_r2": "N/A"}
        )