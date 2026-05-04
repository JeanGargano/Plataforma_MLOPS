# ==============================================================
# DATA SERVICE — Dockerfile
# Imagen base liviana, solo lo necesario para el pipeline
# ==============================================================

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY params.yaml .
COPY dvc.yaml .

COPY src/ ./src/

CMD ["sh", "-c", "python src/ingest.py && python src/validate.py && python src/preprocess.py"]
