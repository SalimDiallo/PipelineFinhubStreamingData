# Orchestration (Airflow)

Orchestration du traitement batch de la pipeline. Le streaming temps reel
(Finnhub vers Kafka) tourne en continu hors Airflow ; Airflow planifie le reste.

```
DAG stock_pipeline (@hourly) :
consume_to_s3 --> transform_silver --> transform_gold --> dbt_build
```

## Structure

| Fichier | Role |
| --- | --- |
| `dags/stock_pipeline_dag.py` | DAG principal (4 taches enchainees) |
| `requirements.txt` | Dependances installees dans l'image Airflow |
| `docker-compose.yml` | Airflow LocalExecutor + Postgres |
| `plugins/` | Plugins Airflow |

## Taches

| Tache | Action |
| --- | --- |
| `consume_to_s3` | Draine les topics Kafka vers Bronze (mode batch) |
| `transform_silver` | Bronze vers Silver (nettoyage, Parquet) |
| `transform_gold` | Silver vers Gold (metriques) |
| `dbt_build` | Execute dbt run puis dbt test |

## Lancer

Prerequis : Kafka et MinIO actifs (Airflow les joint via les reseaux docker).

```bash
docker compose -f airflow/docker-compose.yml up airflow-init   # une fois
docker compose -f airflow/docker-compose.yml up -d
```

Interface : http://localhost:8082 (login airflow / airflow). Activer le DAG
`stock_pipeline` puis le declencher.

## Tester une tache isolee

```bash
docker compose -f airflow/docker-compose.yml exec airflow-scheduler \
  airflow tasks test stock_pipeline transform_silver 2026-06-15
```
