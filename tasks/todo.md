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

## Étapes suivantes
- Étape 2 : Data Lake S3/MinIO (Bronze/Silver/Gold) — consumers Kafka -> S3
- Étape 3 : Airflow
- Étape 4 : Snowflake + dbt
- Étape 5 : Docker (infra globale)
