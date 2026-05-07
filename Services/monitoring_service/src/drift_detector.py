import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
import os

# Configurar rutas dinámicas usando variables de entorno o ruta local como respaldo
BASE_DIR_LOCAL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REFERENCE_PATH = os.environ.get("REFERENCE_PATH", os.path.join(BASE_DIR_LOCAL, "Data", "reference", "reference.csv"))
CURRENT_PATH = os.environ.get("LOG_PATH", os.path.join(BASE_DIR_LOCAL, "Data", "logs", "predictions.csv"))

def calculate_drift():
    print(f"Buscando datos en:\nRef: {REFERENCE_PATH}\nLogs: {CURRENT_PATH}")
    
    if not os.path.exists(REFERENCE_PATH) or not os.path.exists(CURRENT_PATH):
        print("ERROR: Archivos CSV no encontrados.")
        return None

    # 1. Leer los datos
    reference_data = pd.read_csv(REFERENCE_PATH)
    current_data = pd.read_csv(CURRENT_PATH)

    # Quitar columnas que evidentemente no estaban en la referencia, como timestamp o la predicción (si solo evaluamos drift en los features)
    if 'timestamp' in current_data.columns:
        current_data = current_data.drop(columns=['timestamp'])
    if 'consumo_predicho' in current_data.columns and 'consumo_predicho' not in reference_data.columns:
        current_data = current_data.drop(columns=['consumo_predicho'])

    # 2. Configurar el reporte de Evidently
    drift_report = Report(metrics=[
        DataDriftPreset(),
    ])

    # 3. Calcular el reporte
    print("Calculando Data Drift con Evidently...")
    drift_report.run(reference_data=reference_data, current_data=current_data)
    
    # 4. Extraer resultados como diccionario
    report_dict = drift_report.as_dict()
    
    # Extraer la métrica principal (generalmente es el primer elemento)
    # Buscamos DatasetDriftMetric
    drift_result = None
    for metric in report_dict['metrics']:
        if metric['metric'] == 'DatasetDriftMetric':
            drift_result = metric['result']
            break
            
    if drift_result:
        porcentaje_drift = drift_result.get('share_of_drifted_columns', 0.0)
        hay_drift = drift_result.get('dataset_drift', False)
        
        print("\n=== REPORTE DE DATA DRIFT ===")
        print(f"¿Hay Drift estructural detectado?: {'SÍ 🚨' if hay_drift else 'NO ✅'}")
        print(f"Porcentaje de columnas con Drift: {porcentaje_drift * 100:.2f}%")
        print("=============================\n")
        
        return drift_result
        
    return None

if __name__ == "__main__":
    calculate_drift()