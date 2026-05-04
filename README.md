# MLOps Energy Platform
### Plataforma MLOps para Predicción de Consumo Energético Residencial mediante Modelos de Machine Learning en Entornos Cloud

> Predice el consumo agregado de electrodomésticos de una vivienda residencial dado su contexto ambiental y temporal, con un pipeline MLOps completo: ingesta, preprocesamiento, entrenamiento, despliegue y recomendaciones con IA.


## Descripción del proyecto

Este proyecto implementa una plataforma MLOps completa que cubre el ciclo de vida de modelos de machine learning aplicados a la predicción de consumo energético residencial.

**¿Qué predice?**
El modelo predice el **consumo agregado de electrodomésticos** (`Appliances`) de una vivienda en Wh (vatios-hora), dado el contexto ambiental (temperaturas, humedad) y temporal (hora, día, mes) del momento.

**Dataset:** [KAG_energydata_complete.csv](https://www.kaggle.com/datasets/loveall/appliances-energy-prediction) — 19.735 registros de una vivienda residencial durante 4.5 meses con lecturas cada 10 minutos.

---


## Stack tecnológico

| Capa                    | Tecnología 
| Lenguaje                | Python 3.11 
| API REST                | FastAPI + Uvicorn 
| ML                      | scikit-learn, XGBoost 
| Experiment tracking     | MLflow 
| Versionamiento de datos | DVC + Azure Blob Storage 
| Contenedores            | Docker + Docker Compose 
| Gateway                 | Nginx 
| Monitoreo               | Prometheus + Grafana 
| IA Generativa           | Google Gemini API 


```

---

## Requisitos previos

Antes de comenzar asegúrate de tener instalado:

| Herramienta    | Versión mínima 
| Docker Desktop | 24.x 
| Docker Compose | 2.x 
| Git            | cualquiera 

Asegúrarse de que Docker Desktop esté corriendo antes de ejecutar cualquier comando.

---

## Configuración del entorno

**1. Clonar el repositorio**

git clone https://github.com/tu-usuario/mlops-energy-platform.git
cd mlops-energy-platform

**2. Crear el archivo `.env`**

**3. Completar las variables en el .env con la siguiente información**

# Azure Blob Storage (para DVC remote)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# Gemini API — obtén tu key en https://aistudio.google.com/
GEMINI_API_KEY=tu_gemini_api_key_aqui

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin123

# MLflow
MLFLOW_TRACKING_URI=http://mlflow-server:5000
EXPERIMENT_NAME=energy-consumption-prediction

# Modelo
MODEL_NAME=prediction-energy-model
MODEL_STAGE=Production

# Monitoreo
DRIFT_THRESHOLD=0.2
CHECK_INTERVAL_MINUTES=30

**4. Colocar el dataset en la carpeta correcta**

data/raw/KAG_energydata_complete.csv

> Descargar el dataset desde [Kaggle — Appliances Energy Prediction](https://www.kaggle.com/datasets/loveall/appliances-energy-prediction)

---

## Levantar el proyecto

Seguir este orden estrictamente. Cada paso depende del anterior.

### Paso 1 — Levantar MLflow Server

MLflow debe estar saludable antes de entrenar o desplegar cualquier modelo.

docker compose up mlflow-server -d

Abre la UI en el navegador:
http://localhost:5000

---

### Paso 2 — Correr el pipeline de datos

El `data_service` ejecuta `ingest → validate → preprocess` y termina (no queda corriendo).

docker compose --profile pipeline up data-service

Al finalizar verifica que se generaron los artefactos:
Debes ver estos 6 archivos:
```
X_train.csv
X_test.csv
y_train.csv
y_test.csv
scaler.pkl
encoders.pkl
```
---

### Paso 3 — Entrenar y registrar los modelos

El `training_service` entrena los 3 modelos (Regresión Lineal, Random Forest, XGBoost), los registra en MLflow y promueve el mejor a Production automáticamente.

docker compose up training-service -d

Una vez levantado, dispara el entrenamiento desde Postman o curl:

curl -X POST http://localhost:8003/train

Verificar en MLflow UI que aparecen los experimentos:
http://localhost:5000


### Paso 4 — Levantar todos los servicios

Con el modelo en Production, levantar el stack completo:

docker compose up -d

---

## Endpoints disponibles

### Prediction Service — `http://localhost:8001`

  GET  /health   Estado del servicio y modelo cargado 
  POST /predict  Predice consumo de electrodomésticos 
  GET  /docs     Documentación Swagger 

### Training Service — `http://localhost:8003`

  GET   /health    Estado del servicio 
  POST  /train     Entrena modelos y promueve el mejor 
  POST  /retrain   Reentrenamiento en background 

### Recommendation Service — `http://localhost:8002`

  GET     /health             Estado del servicio y Gemini key 
  POST    /recommendations    Genera recomendaciones con Gemini 

### Vía API Gateway — `http://localhost:80`

  POST    /api/predict          prediction-service /predict |
  GET     /api/health           prediction-service /health |
  POST    /api/recommendations  recommendation-service /recommendations |

---

---

## Servicios y puertos

| Servicio               | URL | Descripción |
| API Gateway            | `http://localhost:80`   | Punto de entrada único
| Prediction Service     | `http://localhost:8001` | API de predicción 
| Recommendation Service | `http://localhost:8002` | API de recomendaciones
| Training Service       | `http://localhost:8003` | API de entrenamiento 
| MLflow UI              | `http://localhost:5000` | Gestión ciclo de vida ML

---

### 1. Predecir consumo

```
POST http://localhost:8001/predict
Content-Type: application/json
```

```json
{
  "temperatura_sala": 20.5,
  "consumo_iluminacion": 30.0,
  "temperatura_exterior": 7.0,
  "humedad_exterior": 92.0,
  "temperatura_meteorologica": 6.6,
  "hora": 17,
  "dia_semana": 0,
  "mes": 1,
  "es_fin_de_semana": 0,
  "rango_termico": "Medio"
}
```

Respuesta esperada:
```json
{
  "consumo_electrodomesticos": 97.5,
  "modelo_version": "models:/prediction-energy-model/Production",
  "unidad": "Wh"
}
```
---

---

### 2. Obtener recomendaciones

Usa el `consumo_predicho` obtenido en el paso anterior:

```
POST http://localhost:8002/recommendations
Content-Type: application/json
```

```json
{
  "consumo_predicho": 97.5,
  "temperatura_sala": 20.5,
  "consumo_iluminacion": 30.0,
  "temperatura_exterior": 7.0,
  "humedad_exterior": 92.0,
  "temperatura_meteorologica": 6.6,
  "hora": 17,
  "dia_semana": 0,
  "mes": 1,
  "es_fin_de_semana": 0,
  "rango_termico": "Medio"
}
```

Respuesta esperada:
```json
{
  "recomendaciones": "1. [Optimizar calefacción]...\n2. [Iluminación]...\n3. [Horario]...",
  "consumo_predicho": 97.5,
  "nivel_consumo": "Medio"
}
```

---

### 3. Entrenar el modelo manualmente

```
POST http://localhost:8003/train
```

No requiere body. Respuesta esperada:
```json
{
  "status": "success",
  "best_model": "XGBoost",
  "run_id": "abc123...",
  "test_mae": 45.23,
  "test_rmse": 67.81,
  "test_r2": 0.76
}
```

> **Documentación Swagger** disponible en cada servicio en la ruta `/docs`
> Ejemplo: `http://localhost:8001/docs`

