# Consumers (Kafka vers Bronze)

Consomme les topics Kafka et ecrit les donnees brutes dans le data lake MinIO,
couche Bronze.

```
Kafka  -->  consume_to_bronze (micro-batch)  -->  s3://datalake/bronze/...
```

## Structure

| Fichier | Role |
| --- | --- |
| `utils.py` | Client S3 (boto3), ecriture Bronze, boucle de consommation |
| `consumer_trades.py` | `stock.trades` vers `bronze/trades/` |
| `consumer_quotes.py` | `stock.quotes` vers `bronze/quotes/` |
| `consumer_candles.py` | `stock.candles` vers `bronze/candles/` |

## Couche Bronze

- Donnees brutes, fideles a la source, sans transformation.
- Format JSON Lines, un evenement par ligne.
- Partitionnement par date : `bronze/<dataset>/date=YYYY-MM-DD/<fichier>.jsonl`.
- Conversion en Parquet et typage reportes en couche Silver.

## Comportement

- Micro-batch : ecriture des qu'un lot de `BATCH_SIZE` messages est atteint, ou
  apres `BATCH_TIMEOUT_S` secondes d'inactivite.
- Offsets valides apres ecriture S3 reussie : livraison at-least-once.
- Mode `run_once` (utilise par Airflow) : draine les messages disponibles puis
  s'arrete.

## Configuration (.env)

| Variable | Defaut | Description |
| --- | --- | --- |
| `S3_ENDPOINT_URL` | `http://localhost:9000` | Endpoint MinIO |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | `minioadmin` | Identifiants MinIO |
| `S3_BUCKET` | `datalake` | Bucket du data lake |
| `CONSUMER_GROUP` | `finhub-consumers` | Groupe de consommateurs |
| `BATCH_SIZE` | `100` | Messages par fichier Bronze |
| `BATCH_TIMEOUT_S` | `10` | Delai max avant ecriture d'un lot partiel |

## Lancer

```bash
uv run python -m consumers.consumer_trades
```

Prerequis : Kafka et MinIO actifs.
