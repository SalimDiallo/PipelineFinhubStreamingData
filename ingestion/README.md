# Étape 1 — Ingestion & Streaming

Cette couche récupère des données de marché en **temps réel** depuis l'API
**Finnhub** et les diffuse dans **Kafka**. C'est le point d'entrée de toute la
pipeline : `Finnhub → Kafka → S3 Bronze → Silver → Gold → Snowflake`.

```
┌──────────┐   WebSocket    ┌─────────────────┐   produce (key=symbol)   ┌─────────┐
│ Finnhub  │ ─────────────► │ FinnhubClient   │ ───────────────────────► │  Kafka  │
│   API    │   trades       │ (normalisation) │   value=JSON             │ topics  │
└──────────┘                └─────────────────┘                          └─────────┘
                                     │
                                     ▼
                            MarketDataProducer
```

---

## 📁 Structure

```
ingestion/
├── config.py            # Configuration centralisée (lue depuis .env)
├── finnhub_client.py    # Client Finnhub : WebSocket (trades) + REST (candles)
├── producer.py          # Producteur Kafka (key=symbol, value=JSON)
├── run_ingestion.py     # Point d'entrée : branche le client au producteur
├── schemas/             # Contrats des messages (JSON Schema)
│   ├── trades.json
│   ├── quotes.json
│   └── candles.json
└── README.md
```

---

## ⚙️ Configuration (`config.py`)

Toute la configuration vient du fichier `.env` à la racine. Aucun autre module
n'appelle `os.getenv` directement — tout passe par `config.py`.

| Variable | Défaut | Description |
| --- | --- | --- |
| `FINNHUB_API_KEY` | _(obligatoire)_ | Clé API Finnhub |
| `SYMBOLS` | `AAPL,MSFT,AMZN` | Symboles à suivre (séparés par des virgules) |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Broker(s) Kafka |
| `TOPIC_TRADES` | `stock.trades` | Topic des trades |
| `TOPIC_QUOTES` | `stock.quotes` | Topic des quotes (plan payant) |
| `TOPIC_CANDLES` | `stock.candles` | Topic des candles (plan payant) |

`config.validate()` vérifie que la clé API et au moins un symbole sont présents
avant de démarrer.

---

## 🔌 Client Finnhub (`finnhub_client.py`)

Deux modes d'accès aux données :

### WebSocket (temps réel) — `start_stream(symbols, on_message)`

Ouvre une connexion `wss://ws.finnhub.io`, s'abonne à chaque symbole, et appelle
`on_message(event)` pour **chaque trade reçu**. Les événements sont normalisés
en dictionnaires :

```python
{
  "symbol": "AAPL",
  "price": 189.23,
  "volume": 100,
  "timestamp": 1710001234,   # epoch (ms)
  "type": "trade"
}
```

Détails d'implémentation :

- Les messages de type `ping` (sans champ `data`) sont **ignorés**.
- `run_forever(reconnect=5)` gère la **reconnexion automatique** (5 s) en cas de
  coupure réseau.
- Méthode **bloquante** : à lancer dans son propre process/thread.

### REST (historique) — `get_candles(symbol, resolution, start, end)`

Récupère des chandeliers OHLC via `/stock/candle`. ⚠️ Cet endpoint est
**premium** sur Finnhub : conservé pour un usage futur avec un plan payant.

---

## 📤 Producteur Kafka (`producer.py`)

`MarketDataProducer` publie chaque événement dans Kafka :

- **key = `symbol`** → tous les événements d'un même symbole vont sur la **même
  partition**, ce qui garantit l'**ordre par symbole**.
- **value = JSON** de l'événement complet.
- **topic** déterminé par le `type` de l'événement (`trade`/`quote`/`candle`)
  via `config.TOPIC_BY_EVENT_TYPE`.

Réglages de fiabilité / débit :

| Paramètre | Valeur | Effet |
| --- | --- | --- |
| `acks` | `all` | Attend l'accusé de toutes les répliques (durabilité) |
| `retries` | `3` | Réessaie en cas d'échec transitoire |
| `linger_ms` | `50` | Micro-batching pour améliorer le débit |

`close()` fait un `flush()` puis ferme proprement le producteur (aucun message
perdu en mémoire).

---

## 🚀 Point d'entrée (`run_ingestion.py`)

Branche le client au producteur : chaque trade reçu du WebSocket est envoyé à
Kafka, puis loggué en console. Gère `Ctrl+C` (KeyboardInterrupt) pour fermer le
producteur proprement.

```bash
# Nécessite un broker Kafka actif (localhost:9092 par défaut)
uv run python -m ingestion.run_ingestion
```

Sortie attendue :

```
🚀 Démarrage de l'ingestion Finnhub -> Kafka
   Symboles : AAPL, MSFT, AMZN
   Kafka    : localhost:9092
   Topic trades : stock.trades
🔌 Connexion WebSocket établie
   ➜ abonnement à AAPL
📈 AAPL | 189.23 x100 @ 1710001234
```

---

## 📐 Schémas (`schemas/`)

Contrats des messages au format **JSON Schema (draft 2020-12)**. Ils documentent
la structure attendue de chaque type d'événement et pourront servir à valider
les messages (ou à migrer vers Avro + Schema Registry plus tard).

| Fichier | Type | Champs clés |
| --- | --- | --- |
| `trades.json` | `trade` | symbol, price, volume, timestamp |
| `quotes.json` | `quote` | symbol, bid, ask, bidSize, askSize, timestamp |
| `candles.json` | `candle` | symbol, open, high, low, close, volume, timestamp |

---

## ⚠️ Limites du plan gratuit Finnhub

- Le **WebSocket ne diffuse que les `trade`**. Il n'y a **pas de stream `quote`**
  en temps réel sur le plan gratuit.
- L'endpoint REST **`/stock/candle` est premium**.

Conclusion : aujourd'hui le flux temps réel alimente concrètement
**`stock.trades`**. Les topics/méthodes `quotes` et `candles` sont prêts pour
une éventuelle montée en plan payant.

---

## 🧱 Dépendances

| Paquet | Rôle |
| --- | --- |
| `websocket-client` | Connexion WebSocket (`WebSocketApp`) |
| `kafka-python` | Producteur Kafka |
| `requests` | Appels REST Finnhub |
| `python-dotenv` | Chargement du `.env` |

> Note : utiliser `websocket-client` (et **pas** le paquet `websocket`, abandonné
> et dépourvu de `WebSocketApp`).

---

## ▶️ Démarrage complet (de bout en bout)

```bash
# 1. Lancer le broker Kafka (mode KRaft, sans Zookeeper)
docker compose -f kafka/docker-compose.yml up -d

# 2. Créer les topics (stock.trades / quotes / candles)
bash kafka/create_topics.sh

# 3. Lancer l'ingestion temps réel
uv run python -m ingestion.run_ingestion

# (Marchés actions fermés ? Tester avec un symbole crypto 24/7 :)
SYMBOLS="BINANCE:BTCUSDT" uv run python -m ingestion.run_ingestion
```

Visualiser les messages : **Kafka UI → http://localhost:8080** (topic `stock.trades`),
ou en ligne de commande :

```bash
docker exec kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic stock.trades \
  --from-beginning --property print.key=true
```

Arrêter la stack : `docker compose -f kafka/docker-compose.yml down`
(ajouter `-v` pour effacer aussi les données).

---

## ✅ Statut

Chaîne **Finnhub → Kafka** validée de bout en bout : trades temps réel reçus du
WebSocket et produits dans `stock.trades` (key=symbol, value=JSON). La couche
suivante (Étape 2) consommera ces topics vers le data lake S3/MinIO.
