FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY src/ src/

# Puerto para la API y métricas de Prometheus
EXPOSE 8004

# Levantar el servidor FastAPI
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8004"]
