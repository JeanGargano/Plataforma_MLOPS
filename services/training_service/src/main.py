import os
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from train   import run_training
from promote import promote_best_model


app = FastAPI(
    title="Training Service",
    description="Entrenamiento, promoción y evaluación de modelos de predicción energética",
    version="1.0.0"
)


class TrainResponse(BaseModel):
    status   : str
    best_model: str
    run_id   : str
    test_mae : float
    test_rmse: float
    test_r2  : float


# ==============================================================
# ENDPOINTS
# ==============================================================

@app.get("/health")
def health():
    return {"status": "ok", "service": "training-service"}


@app.post("/train", response_model=TrainResponse)
def train():
    """
    Lnza el pipealine de entrenamiento completo:
    entrena 3 modelos y promueve el mejor a Production.
    """
    results, best = run_training()

    promote_best_model(
        run_id=best["run_id"],
        metrics={
            "test_mae" : best["test_mae"],
            "test_rmse": best["test_rmse"],
            "test_r2"  : best["test_r2"]
        }
    )

    return TrainResponse(
        status    = "success",
        best_model= best["model_name"],
        run_id    = best["run_id"],
        test_mae  = best["test_mae"],
        test_rmse = best["test_rmse"],
        test_r2   = best["test_r2"]
    )


@app.post("/retrain")
def retrain(background_tasks: BackgroundTasks):
    """
    Disparado por el monitoring_service cuando detecta drift.
    Corre en background para no bloquear la respuesta.
    """
    from retrain import retrain as run_retrain
    background_tasks.add_task(run_retrain)
    return {"status": "reentrenamiento iniciado en background"}
