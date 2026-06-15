# Image du projet : producteur de streaming Finnhub -> Kafka et consumers.
# (Airflow et dbt ont leurs propres images ; voir airflow/docker-compose.yml.)

FROM python:3.14-slim

# uv pour une install rapide et reproductible
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Dépendances d'abord (cache de couche)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Code du projet
COPY ingestion/ ingestion/
COPY consumers/ consumers/
COPY transformations/ transformations/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Par défaut : lance le producteur de streaming.
# Surchargé dans docker-compose pour les consumers.
CMD ["python", "-m", "ingestion.run_ingestion"]
