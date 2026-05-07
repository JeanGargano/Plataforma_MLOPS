import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Rutas robustas relativas a la ubicación de este script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, "Data", "raw", "KAG_energydata_complete.csv")
REFERENCE_PATH = os.path.join(BASE_DIR, "Data", "reference", "reference.csv")
LOG_PATH = os.path.join(BASE_DIR, "Data", "logs", "predictions.csv")

def prepare_mock_data():
    print("Cargando dataset crudo original...")
    if not os.path.exists(RAW_DATA_PATH):
        print(f"ERROR: No se encontrÃ³ el dataset original en {RAW_DATA_PATH}")
        return
        
    df = pd.read_csv(RAW_DATA_PATH)
    
    # Renombrar columnas para igualar el schema que espera el modelo
    # Esto es una suposiciÃ³n basada en un dataset tÃpico de Kaggle appliances
    df = df.rename(columns={
        "Temperature": "temperatura_sala",
        "Lighting": "consumo_iluminacion",
        "T_out": "temperatura_exterior",
        "RH_out": "humedad_exterior",
        "T_met": "temperatura_meteorologica",
        "Appliances": "consumo_real"
    })
    
    # Crear variables simuladas si no existen
    if "hora" not in df.columns:
        df["hora"] = np.random.randint(0, 24, size=len(df))
    if "dia_semana" not in df.columns:
        df["dia_semana"] = np.random.randint(0, 7, size=len(df))
    if "mes" not in df.columns:
        df["mes"] = np.random.randint(1, 13, size=len(df))
    if "es_fin_de_semana" not in df.columns:
        df["es_fin_de_semana"] = df["dia_semana"].apply(lambda x: 1 if x >= 5 else 0)
    if "rango_termico" not in df.columns:
        df["rango_termico"] = np.random.choice(["Bajo", "Medio", "Alto"], size=len(df))
        
    columnas_deseadas = [
        "temperatura_sala", "consumo_iluminacion", "temperatura_exterior", 
        "humedad_exterior", "temperatura_meteorologica", "hora", 
        "dia_semana", "mes", "es_fin_de_semana", "rango_termico"
    ]
    
    # Asegurar que todas las columnas existan, rellenar numÃ©ricas faltantes con random normal
    for col in columnas_deseadas:
        if col not in df.columns:
            df[col] = np.random.normal(loc=15.0, scale=5.0, size=len(df))
            
    reference_df = df[columnas_deseadas].copy()
    
    # 1. Crear el dataset de Referencia (Base normal y sana)
    # Tomamos las primeras 2000 filas
    ref_final = reference_df.iloc[:2000]
    ref_final.to_csv(REFERENCE_PATH, index=False)
    print(f"âœ… Reference dataset guardado en {REFERENCE_PATH} ({len(ref_final)} filas)")
    
    # 2. Crear los Logs simulados (current dataset) CON DRIFT INYECTADO
    # Tomamos otras 500 filas
    current_df = reference_df.iloc[2000:2500].copy()
    
    # InyecciÃ³n brutal de Drift en la temperatura exterior y humedad (Simulando fallo de sensor o cambio de estaciÃ³n abrupto)
    current_df["temperatura_exterior"] = current_df["temperatura_exterior"] * 1.8 + 15
    current_df["humedad_exterior"] = current_df["humedad_exterior"] * 0.5
    
    # Agregamos metadatos del log
    now = datetime.utcnow()
    current_df["timestamp"] = [(now - timedelta(minutes=i*10)).isoformat() for i in range(len(current_df))]
    current_df["consumo_predicho"] = np.random.normal(loc=300, scale=50, size=len(current_df))
    
    # Ordenar columnas como el logger
    orden_logs = ["timestamp"] + columnas_deseadas + ["consumo_predicho"]
    current_df = current_df[orden_logs]
    
    current_df.to_csv(LOG_PATH, index=False)
    print(f"âœ… Mock Logs inyectados con Drift guardados en {LOG_PATH} ({len(current_df)} filas)")

if __name__ == "__main__":
    prepare_mock_data()
