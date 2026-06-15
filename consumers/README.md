# Étape 2 — Consumers Kafka → S3 Bronze

Cette couche consomme les topics Kafka et écrit les données **brutes** dans le
data lake **S3 / MinIO**, couche **Bronze**.

```
Kafka (stock.trades / quotes / candles)
        │  consume (group=finhub-consumers)
        ▼
  consume_to_bronze()   ── micro-batch (BATCH_SIZE / BATCH_TIMEOUT_S)
        │  put_object JSON Lines
        ▼
  s3://datalake/bronze/<dataset>/date=YYYY-MM-DD/<HHMMSS>-<uuid>.jsonl
```

## 📁 Fichiers

| Fichier | Rôle |
| --- | --- |
| `utils.py` | Config S3/Kafka (`.env`), client boto3, écriture Bronze, boucle `consume_to_bronze` |
| `consumer_trades.py` | `stock.trades` → `bronze/trades/` |
| `consumer_quotes.py` | `stock.quotes` → `bronze/quotes/` |
| `consumer_candles.py` | `stock.candles` → `bronze/candles/` |

## 🟤 Principe Bronze

- Données **brutes**, fidèles à la source : aucun nettoyage ni typage.
- Format **JSON Lines** (`.jsonl`), un événement par ligne.
- Partitionnement par **date** (`date=YYYY-MM-DD/`) pour faciliter les lectures
  incrémentales en Silver.
- La conversion en **Parquet** et le typage interviennent en Silver (Étape 2b).

## ⚙️ Comportement du consumer

- **Micro-batch** : flush dès `BATCH_SIZE` messages OU après `BATCH_TIMEOUT_S`
  secondes d'inactivité.
- **Offsets commités après écriture S3 réussie** (`enable_auto_commit=False`) →
  livraison **at-least-once** (pas de perte ; doublons possibles en cas de crash
  entre l'écriture et le commit, dédupliqués en Silver).
- `auto_offset_reset=earliest` : rejoue depuis le début si pas d'offset connu.

## ▶️ Lancer

```bash
# 1. Infra : Kafka (Étape 1) + MinIO
docker compose -f kafka/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml up -d

# 2. Produire des données (Étape 1)
SYMBOLS="BINANCE:BTCUSDT" uv run python -m ingestion.run_ingestion

# 3. Consommer vers Bronze (dans un autre terminal)
uv run python -m consumers.consumer_trades
```

Visualiser les objets : **MinIO Console → http://localhost:9001**
(login `minioadmin` / `minioadmin`), bucket `datalake`, préfixe `bronze/`.

## 🔧 Configuration (`.env`)

| Variable | Défaut | Description |
| --- | --- | --- |
| `S3_ENDPOINT_URL` | `http://localhost:9000` | Endpoint MinIO (API S3) |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | `minioadmin` | Identifiants MinIO |
| `S3_BUCKET` | `datalake` | Bucket du data lake |
| `CONSUMER_GROUP` | `finhub-consumers` | Groupe de consommateurs Kafka |
| `BATCH_SIZE` | `100` | Messages par objet Bronze |
| `BATCH_TIMEOUT_S` | `10` | Délai max avant flush d'un batch partiel |

## ✅ Statut

Chaîne **Kafka → S3 Bronze** validée de bout en bout : trades temps réel écrits
en JSONL partitionné par date dans MinIO. Prochaine sous-étape : nettoyage
Bronze → Silver (dédup, typage, timestamps) en Parquet.
