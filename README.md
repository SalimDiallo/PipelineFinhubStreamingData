# 🚀 Pipeline de données en temps réel

## 🎯 Objectif

Concevoir une pipeline de données en temps réel pour exploiter des données du marché boursier, depuis l’ingestion jusqu’à la mise à disposition dans un data warehouse pour analyse.

---

## 🧩 1. Ingestion & Streaming

### Source : Finnhub API

### Données récupérées

#### Trades (transactions en temps réel)

```json
{
  "symbol": "AAPL",
  "price": 189.23,
  "volume": 100,
  "timestamp": 1710001234
}
```

#### Quotes (bid/ask)

```json
{
  "symbol": "AAPL",
  "bid": 189.2,
  "ask": 189.25,
  "bidSize": 500,
  "askSize": 400,
  "timestamp": 1710001234
}
```

#### Candles (OHLC)

```json
{
  "symbol": "AAPL",
  "open": 188.5,
  "high": 190.0,
  "low": 187.8,
  "close": 189.2,
  "volume": 1500000,
  "timestamp": 1710001200
}
```

### Streaming avec Kafka

**Topics :**

- `stock.trades`
- `stock.quotes`
- `stock.candles`

**Key :**

- `symbol`

**Value :**

- JSON brut provenant de l’API

---

## 🪵 2. Data Lake (S3 / MinIO)

### Architecture : Bronze → Silver → Gold

### 🟤 Bronze (Raw)

- Données brutes depuis Kafka
- Aucun traitement

**Structure :**

```
/bronze/trades/date=YYYY-MM-DD/
/bronze/quotes/date=YYYY-MM-DD/
```

**Format :**

- JSON / Parquet

---

### ⚪ Silver (Clean)

**Transformations :**

- Suppression des doublons
- Normalisation des timestamps
- Typage des colonnes
- Gestion des valeurs nulles

**Exemple :**

| symbol | price | volume | timestamp           |
| ------ | ----- | ------ | ------------------- |
| AAPL   | 189.2 | 100    | 2026-06-15 10:00:00 |

---

### 🟡 Gold (Business-ready)

**Données enrichies :**

- Moyennes mobiles
- Volume agrégé
- Variation %

**Exemple :**

| symbol | avg_price_5min | volume_5min | pct_change |
| ------ | -------------- | ----------- | ---------- |

---

## ⚙️ 3. Orchestration (Airflow)

### DAG global

```
Fetch API → Kafka → S3 Bronze
→ Silver → Gold → Snowflake
```

### Tasks :

- `fetch_stock_data`
- `produce_to_kafka`
- `consume_to_s3`
- `transform_silver`
- `transform_gold`
- `load_snowflake`

---

## 🧠 4. Transformation & Modélisation

### Data Warehouse : Snowflake

### Modélisation avec dbt

#### Table de faits : `fact_trades`

| symbol | timestamp | price | volume |

---

#### Dimension : `dim_symbol`

| symbol | sector | company_name |

---

#### Table analytique : `agg_stock_metrics`

| symbol | date | avg_price | total_volume | volatility |

---

### Métriques calculées :

- VWAP (Volume Weighted Average Price)
- Moving Average
- Volatility
- Daily Return

---

## 🐳 5. Infrastructure (Docker)

### Services conteneurisés :

- Kafka + Zookeeper
- Airflow
- MinIO
- dbt
- Producteurs / consommateurs Python

---

## 🔄 Flux global

```
Finnhub API
   ↓
Kafka
   ↓
S3 Bronze
   ↓
S3 Silver
   ↓
S3 Gold
   ↓
Snowflake
   ↓
BI / Dashboard / ML
```

---

## 💡 Améliorations possibles

- Schema Registry (Avro)
- Kafka Streams / Spark Streaming
- Data Quality (Great Expectations)
- Monitoring (Prometheus, Grafana)
- CI/CD (GitHub Actions)

---
