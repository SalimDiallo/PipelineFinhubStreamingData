# Couche Silver — nettoyage Bronze → Silver

Lit les données **brutes** de la couche Bronze (JSON Lines) et produit des
données **propres et typées** en Parquet.

```
s3://datalake/bronze/<dataset>/date=YYYY-MM-DD/*.jsonl
        │  dédup + typage + timestamps + nulls
        ▼
s3://datalake/silver/<dataset>/date=YYYY-MM-DD/<dataset>.parquet
```

## 📁 Fichiers

| Fichier | Rôle |
| --- | --- |
| `utils.py` | Lecture Bronze (S3 → DataFrame), écriture Parquet Silver, normalisation timestamp |
| `clean_trades.py` | `bronze/trades` → `silver/trades` |
| `clean_quotes.py` | `bronze/quotes` → `silver/quotes` |
| `clean_candles.py` | `bronze/candles` → `silver/candles` |

## ⚪ Transformations appliquées

- **Typage** : `symbol` (string), montants (float64), `timestamp` (Int64).
- **Timestamps** : epoch ms → colonne `event_time` (datetime UTC), epoch conservé.
- **Nulls** : suppression des lignes sans champs critiques (ex. trades :
  `symbol`, `price`, `timestamp`).
- **Déduplication** :
  - trades : sur `(symbol, price, volume, timestamp)`
  - quotes : sur `(symbol, bid, ask, timestamp)`
  - candles : sur `(symbol, timestamp)` (garde la dernière reçue)
- **Tri** stable par `(symbol, timestamp)`.

## ▶️ Lancer

```bash
# Date du jour (UTC) par défaut
uv run python -m transformations.silver.clean_trades

# Date explicite
uv run python -m transformations.silver.clean_trades 2026-06-15
uv run python -m transformations.silver.clean_quotes 2026-06-15
uv run python -m transformations.silver.clean_candles 2026-06-15
```

## 📦 Format

Parquet (`pyarrow`, compression `snappy`) — colonnaire, compressé, typé.
Idéal pour les lectures analytiques (couche Gold, chargement Snowflake).

## ✅ Statut

`clean_trades` validé sur données réelles (343 brutes → 230 nettoyées,
0 doublon, 0 null, types corrects). `clean_quotes` / `clean_candles` validés en
test unitaire (dédup, nulls, typage) — pas de flux réel car premium Finnhub.
