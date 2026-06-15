"""
DAG d'orchestration de la pipeline (Étape 3).

Le streaming Finnhub -> Kafka tourne en continu HORS Airflow (process
run_ingestion). Ce DAG orchestre le traitement **batch** périodique :

    consume_to_s3 -> transform_silver -> transform_gold -> load_snowflake

Chaque tâche réutilise directement les modules du projet (consumers /
transformations). `consume_to_s3` draine le topic en mode batch (run_once).

`load_snowflake` est un placeholder tant que l'Étape 4 (Snowflake) n'est pas
en place.
"""

from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.operators.python import PythonOperator

DATASETS = ["trades", "quotes", "candles"]


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# -------------------------
# Callables des tâches
# -------------------------
def consume_to_s3() -> None:
    """Draine les topics Kafka vers la couche Bronze (mode batch)."""
    import os

    from consumers.utils import consume_to_bronze

    topics = {
        "trades": os.getenv("TOPIC_TRADES", "stock.trades"),
        "quotes": os.getenv("TOPIC_QUOTES", "stock.quotes"),
        "candles": os.getenv("TOPIC_CANDLES", "stock.candles"),
    }
    for dataset, topic in topics.items():
        consume_to_bronze(topic, dataset, run_once=True)


def transform_silver() -> None:
    """Nettoyage Bronze -> Silver pour la date du jour."""
    from transformations.silver import clean_candles, clean_quotes, clean_trades

    date = _today()
    clean_trades.main(date)
    clean_quotes.main(date)
    clean_candles.main(date)


def transform_gold() -> None:
    """Agrégations Silver -> Gold pour la date du jour."""
    from transformations.gold import agg_metrics, features

    date = _today()
    agg_metrics.main(date)
    features.main(date)


def dbt_build() -> None:
    """
    Modélisation analytique : dbt run + dbt test (Étape 4).

    dbt-duckdb est installé dans l'image Airflow (_PIP_ADDITIONAL_REQUIREMENTS).
    Les modèles lisent les Parquet Silver depuis MinIO via DuckDB (httpfs).

    En local hors Airflow, dbt tourne dans son venv isolé warehouse/dbt/.venv
    (Python 3.12, car dbt-core ne supporte pas encore Python 3.14).
    """
    import os
    import subprocess
    import sys

    dbt_dir = "/opt/project/warehouse/dbt"

    env = os.environ.copy()
    env["DBT_PROFILES_DIR"] = dbt_dir
    # La base DuckDB est écrite dans /tmp (warehouse/dbt monté en lecture seule
    # côté image, et évite de polluer le repo).
    env["DBT_DUCKDB_PATH"] = "/tmp/finhub.duckdb"
    # DuckDB httpfs attend host:port (sans schéma) ; déduit de S3_ENDPOINT_URL
    endpoint = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
    env["S3_ENDPOINT_HOST"] = endpoint.replace("http://", "").replace("https://", "")

    for cmd in (["run"], ["test"]):
        subprocess.run(
            [sys.executable, "-m", "dbt.cli.main", *cmd],
            cwd=dbt_dir,
            env=env,
            check=True,
        )


# -------------------------
# Définition du DAG
# -------------------------
default_args = {
    "owner": "finhub",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="stock_pipeline",
    description="Batch : Kafka -> Bronze -> Silver -> Gold -> dbt (DuckDB)",
    default_args=default_args,
    start_date=datetime(2026, 6, 1),
    schedule="@hourly",
    catchup=False,
    tags=["finhub", "etl"],
) as dag:
    t_consume = PythonOperator(task_id="consume_to_s3", python_callable=consume_to_s3)
    t_silver = PythonOperator(task_id="transform_silver", python_callable=transform_silver)
    t_gold = PythonOperator(task_id="transform_gold", python_callable=transform_gold)
    t_dbt = PythonOperator(task_id="dbt_build", python_callable=dbt_build)

    t_consume >> t_silver >> t_gold >> t_dbt
