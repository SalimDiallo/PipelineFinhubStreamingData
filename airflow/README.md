# Étape 3 — Orchestration (Airflow)

Orchestration du traitement **batch** de la pipeline. Le streaming temps réel
(Finnhub → Kafka) tourne **en continu hors Airflow** ; Airflow planifie le reste.

```
(continu, hors Airflow)  Finnhub WS ──► Kafka
                                          │
        ┌──────────── DAG stock_pipeline (@hourly) ────────────┐
        │  consume_to_s3 → transform_silver → transform_gold → load_snowflake
        └───────────────────────────────────────────────────────┘
            Kafka→Bronze    Bronze→Silver    Silver→Gold    (Étape 4)
```

## 📁 Fichiers

| Fichier | Rôle |
| --- | --- |
| `dags/stock_pipeline_dag.py` | DAG principal (4 tâches enchaînées) |
| `requirements.txt` | Deps installées dans l'image Airflow |
| `docker-compose.yml` | Airflow LocalExecutor + Postgres |
| `plugins/` | Plugins Airflow (vide pour l'instant) |

## 🔀 Tâches du DAG

| Task | Action | Module appelé |
| --- | --- | --- |
| `consume_to_s3` | Draine les topics Kafka → Bronze (mode batch `run_once`) | `consumers.utils.consume_to_bronze` |
| `transform_silver` | Bronze → Silver (nettoyage, Parquet) | `transformations.silver.clean_*` |
| `transform_gold` | Silver → Gold (métriques) | `transformations.gold.agg_metrics`, `features` |
| `load_snowflake` | Chargement Gold → Snowflake | *placeholder (Étape 4)* |

Dépendances : `consume_to_s3 >> transform_silver >> transform_gold >> load_snowflake`.

## ▶️ Lancer Airflow

Prérequis : Kafka et MinIO en route (étapes 1-2). Airflow les joint via
`host.docker.internal`.

```bash
# 1. Init (DB + utilisateur admin) — une fois
docker compose -f airflow/docker-compose.yml up airflow-init

# 2. Démarrer webserver + scheduler
docker compose -f airflow/docker-compose.yml up -d
```

UI : **http://localhost:8081** (login `airflow` / `airflow`). Activer le DAG
`stock_pipeline` puis le déclencher manuellement ou attendre le tick horaire.

> Le code projet est monté dans `/opt/project` (sur le `PYTHONPATH`) pour que
> les DAGs importent `consumers` et `transformations`.

## ✅ Statut

- DAG **validé par parsing** (Airflow 2.10.3) : 4 tâches, ordre topologique
  correct, schedule `@hourly`.
- Logique des tâches **validée de bout en bout** sur données réelles
  (drain batch → Bronze → Silver → Gold).
- `load_snowflake` est un placeholder jusqu'à l'Étape 4.

Le streaming `ingestion.run_ingestion` reste à lancer séparément (process
continu), ou à conteneuriser à l'Étape 5.
