FROM python:3.12-slim

WORKDIR /app

# Dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY pipeline/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Code source
COPY pipeline/ ./pipeline/
COPY run_pipeline.py .
COPY test_pipeline.py .

# Dossier de sortie des fiches (monté en volume)
RUN mkdir -p /app/fiches

# Variables d'environnement (la clé API sera passée au run)
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

ENTRYPOINT ["python", "run_pipeline.py"]
