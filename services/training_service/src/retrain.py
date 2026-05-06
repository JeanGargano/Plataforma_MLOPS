import os
from train   import run_training
from promote import promote_best_model


def retrain():
    """
    Pipeline completo de reentrenamiento.
    Disparado automáticamente por el monitoring_service
    cuando detecta drift superior al umbral configurado.

    Flujo:
      1. Reentrena los 3 modelos con los datos actuales
      2. Selecciona el mejor por MAE
      3. Promueve a Production automáticamente
    """
    print("="*55)
    print("REENTRENAMIENTO AUTOMATICO INICIADO")
    print("="*55)

    # 1. Entrena y obtiene resultados
    results, best = run_training()

    # 2. Promueve el mejor modelo
    print("\nPromoviendo mejor modelo a Production...")
    promote_best_model(
        run_id=best["run_id"],
        metrics={
            "test_mae" : best["test_mae"],
            "test_rmse": best["test_rmse"],
            "test_r2"  : best["test_r2"]
        }
    )

    print("\nReentrenamiento completado exitosamente.")
    return best


if __name__ == "__main__":
    retrain()