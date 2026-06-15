# TODO — finHubPipeline

## Étape 1 — Ingestion & Streaming ✅ TERMINÉE

- [x] Auditer l'existant (`finnhub_client.py`, deps)
- [x] Corriger dépendances : `websocket` (cassé) -> `websocket-client`, ajout `requests`, `python-dotenv`
- [x] `ingestion/config.py` — config centralisée (env, Kafka, symbols, topics)
- [x] `ingestion/finnhub_client.py` — fix import WebSocket + routage event, reconnect
- [x] `ingestion/producer.py` — producteur Kafka (key=symbol, value=JSON, acks=all)
- [x] `ingestion/schemas/{trades,quotes,candles}.json` (JSON Schema)
- [x] `ingestion/run_ingestion.py` — entrypoint (client -> producer)
- [x] Vérification : imports OK, config OK, routage/sérialisation OK (dry-run sans Kafka)

## Notes
- Finnhub free : WebSocket = `trade` uniquement. Pas de stream `quote`. `/stock/candle` = premium.
- Topics : `stock.trades`, `stock.quotes`, `stock.candles`. Key = symbol.
- Lancer : `uv run python -m ingestion.run_ingestion` (nécessite un broker Kafka actif).

## Stack Kafka ✅ TERMINÉE
- [x] `kafka/docker-compose.yml` — Kafka KRaft (apache/kafka:3.9.0) + Kafka UI
- [x] `kafka/create_topics.sh` — création idempotente des 3 topics
- [x] `kafka/README.md`
- [x] Vérifié bout en bout : 290 trades BTC live -> stock.trades (partition 0, key=symbol)

## Git
- [x] .gitignore + .env untracked, commit feat(ingestion) cfe0140
- [x] etape1 intégrée dans dev, branche feature/etape2 créée

## Étape 2 — Data Lake S3/MinIO (Bronze) — TERMINÉE (branche feature/etape2)
- [x] MinIO dans `infra/docker-compose.yml` (conforme archi) + bucket init auto
- [x] `consumers/utils.py` — client S3 boto3, partition par date, JSONL, boucle générique
- [x] `consumers/consumer_trades.py` — stock.trades -> bronze/trades/date=YYYY-MM-DD/
- [x] `consumers/consumer_quotes.py`, `consumer_candles.py`
- [x] `boto3` ajouté aux deps, config S3 dans .env / .env.example
- [x] Vérif bout en bout : flux live Finnhub -> Kafka -> consumer -> 3 objets JSONL dans MinIO
- [x] README consumers
- Format Bronze : JSON Lines brut (Parquet/typage -> Silver). Décision actée.

## Étape 2b — Silver — TERMINÉE (branche feature/etape2)
- [x] pandas + pyarrow ajoutés aux deps
- [x] transformations/silver/utils.py — read_bronze, write_silver (Parquet snappy), normalize_timestamp
- [x] clean_trades.py — validé sur réel (343 -> 230, 0 dup, 0 null, types OK)
- [x] clean_quotes.py / clean_candles.py — validés en test unitaire (dédup/nulls/typage)
- [x] README silver
- Silver = Parquet typé, partitionné par date, event_time UTC ajouté.

## Étape 2c — Gold — TERMINÉE (branche feature/etape2)
- [x] numpy ajouté aux deps
- [x] transformations/gold/utils.py — read_silver, write_gold
- [x] agg_metrics.py — agg_stock_metrics (VWAP, avg, volume, volatility, daily_return) + agg_5min (pct_change)
- [x] features.py — moving_avg_10, price_return, rolling_vol_10 (optionnel ML)
- [x] Fix bug vwap_5min (lambda mal aligné dans resample -> apply par fenêtre)
- [x] Nettoyé l'artefact TEST du Bronze, rejoué Silver+Gold
- [x] README gold
- [x] Validé sur réel (229 trades) : tables Gold cohérentes

## Étape 2 COMPLÈTE : Bronze + Silver + Gold dans le data lake MinIO

## Étape 3 — Orchestration Airflow — TERMINÉE (branche feature/etape3)
- [x] Modèle : DAG batch périodique (@hourly), streaming Finnhub->Kafka reste hors Airflow
- [x] Ajout mode run_once au consumer (drain batch puis stop)
- [x] airflow/dags/stock_pipeline_dag.py : consume_to_s3 -> silver -> gold -> load_snowflake
- [x] airflow/requirements.txt, plugins/, docker-compose.yml (LocalExecutor + Postgres)
- [x] load_snowflake = placeholder (Étape 4)
- [x] DAG validé par parsing (Airflow 2.10.3, venv py3.12 jetable) + callables validés sur réel
- [x] README airflow, .gitignore airflow/logs/

## Étape 4 — Modélisation dbt — TERMINÉE (branche feature/etape4)
- Décision : DuckDB + dbt-duckdb (gratuit/local) au lieu de Snowflake (payant)
- [x] dbt isolé en venv py3.12 (dbt-core ne supporte pas py3.14)
- [x] warehouse/dbt/ : dbt_project.yml, profiles.yml (duckdb + httpfs MinIO)
- [x] stg_trades + marts (fact_trades, dim_symbol, agg_stock_metrics) + tests
- [x] dbt run (4 modèles) + dbt test (11 tests) PASS en local
- [x] DAG : tâche dbt_build (run+test) remplace load_snowflake ; dbt-duckdb dans l'image Airflow
- [x] dbt_build validé via Airflow (PASS=4 run, PASS=11 test) contre MinIO
- [x] DAG complet validé : consume -> silver -> gold -> dbt_build

## Étape 5 — Infrastructure Docker — TERMINÉE (branche feature/etape5)
- [x] infra/Dockerfile : image finhub-pipeline (py3.14 + uv, ingestion/consumers/transformations)
- [x] infra/docker-compose.yml : MinIO + producer + consumer-trades conteneurisés (réseaux kafka/infra)
- [x] Makefile racine : make up/down/ps/topics/logs/clean (orchestre les 3 stacks)
- [x] .dockerignore
- [x] Image construite, producer+consumer démarrent et se connectent à Kafka+MinIO (validé)
- [!] Écriture MinIO bloquée par disque hôte plein (XMinioStorageFull) — limite env, pas un bug
- [x] README infra

## PROJET COMPLET : étapes 1->5 (ingestion, stockage, orchestration, modélisation, infra)

## Étapes suivantes
- Étape 3 : Airflow
- Étape 4 : Snowflake + dbt
- Étape 5 : Docker (infra globale)
