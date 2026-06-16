# Ingestion et Streaming

Recupere les donnees de marche en temps reel depuis l'API Finnhub et les diffuse
dans Kafka. C'est le point d'entree de la pipeline.

```
Finnhub API  --WebSocket-->  FinnhubClient  --produce (key=symbol)-->  Kafka
```

## Structure

| Fichier | Role |
| --- | --- |
| `config.py` | Configuration centralisee, lue depuis `.env` |
| `finnhub_client.py` | Client Finnhub : WebSocket (trades) et REST (candles) |
| `producer.py` | Producteur Kafka (key = symbol, value = JSON) |
| `run_ingestion.py` | Point d'entree : relie le client au producteur |
| `schemas/` | Contrats des messages au format JSON Schema |

## Configuration (.env)

| Variable | Defaut | Description |
| --- | --- | --- |
| `FINNHUB_API_KEY` | (obligatoire) | Cle API Finnhub |
| `SYMBOLS` | `AAPL,MSFT,AMZN` | Symboles a suivre (separes par des virgules) |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Broker(s) Kafka |
| `TOPIC_TRADES` | `stock.trades` | Topic des trades |
| `TOPIC_QUOTES` | `stock.quotes` | Topic des quotes |
| `TOPIC_CANDLES` | `stock.candles` | Topic des candles |

## Fonctionnement

Le client ouvre une connexion WebSocket, s'abonne aux symboles et normalise
chaque trade en dictionnaire `{symbol, price, volume, timestamp, type}`. Le
producteur publie chaque evenement dans Kafka avec la cle `symbol` (ordre garanti
par symbole sur une partition), la valeur en JSON et les reglages `acks=all`,
`retries=3`, `linger_ms=50`.

## Lancer

```bash
uv run python -m ingestion.run_ingestion
```

Necessite un broker Kafka actif. Hors heures de marche, utiliser un symbole
crypto disponible 24/7 :

```bash
SYMBOLS="BINANCE:BTCUSDT" uv run python -m ingestion.run_ingestion
```

## Limites du plan gratuit Finnhub

Le WebSocket ne diffuse que les evenements `trade`. Les quotes et candles temps
reel necessitent un abonnement payant. Les topics et methodes correspondants
restent prets a l'emploi.
