# Couche Silver (nettoyage)

Lit les donnees brutes de la couche Bronze (JSON Lines) et produit des donnees
propres et typees en Parquet.

```
bronze/<dataset>/date=YYYY-MM-DD/*.jsonl
   -->  dedup + typage + timestamps + nulls
   -->  silver/<dataset>/date=YYYY-MM-DD/<dataset>.parquet
```

## Structure

| Fichier | Role |
| --- | --- |
| `utils.py` | Lecture Bronze, ecriture Parquet, normalisation des timestamps |
| `clean_trades.py` | `bronze/trades` vers `silver/trades` |
| `clean_quotes.py` | `bronze/quotes` vers `silver/quotes` |
| `clean_candles.py` | `bronze/candles` vers `silver/candles` |

## Transformations

- Typage des colonnes (symbol, montants, timestamp).
- Normalisation des timestamps : epoch ms vers `event_time` (datetime UTC).
- Suppression des lignes aux champs critiques manquants.
- Deduplication.

## Format

Parquet (pyarrow, compression snappy), partitionne par date.

## Lancer

```bash
uv run python -m transformations.silver.clean_trades [YYYY-MM-DD]
uv run python -m transformations.silver.clean_quotes [YYYY-MM-DD]
uv run python -m transformations.silver.clean_candles [YYYY-MM-DD]
```

Sans argument, la date du jour (UTC) est utilisee.
