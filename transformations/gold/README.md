# Couche Gold — agrégations business Silver → Gold

Calcule les **métriques de marché** à partir du Silver propre (Parquet) et
produit des tables business-ready.

```
s3://datalake/silver/trades/date=YYYY-MM-DD/trades.parquet
        │  agrégations & métriques
        ▼
s3://datalake/gold/<table>/date=YYYY-MM-DD/<table>.parquet
```

## 📁 Fichiers

| Fichier | Rôle |
| --- | --- |
| `utils.py` | Lecture Silver, écriture Gold (Parquet snappy) |
| `agg_metrics.py` | Métriques agrégées (jour + fenêtres 5 min) |
| `features.py` | Features par trade (moyenne mobile, rendement, volatilité glissante) — optionnel ML |

## 🟡 Tables produites

### `gold/agg_stock_metrics` (1 ligne par symbole/jour)

| Colonne | Description |
| --- | --- |
| `symbol`, `date` | Clé |
| `avg_price` | Prix moyen du jour |
| `vwap` | Volume Weighted Average Price |
| `total_volume` | Volume total échangé |
| `volatility` | Écart-type des prix (population) |
| `daily_return_pct` | Variation % entre premier et dernier prix |
| `trade_count` | Nombre de trades |

### `gold/agg_5min` (1 ligne par symbole / fenêtre de 5 min)

| Colonne | Description |
| --- | --- |
| `symbol`, `event_time` | Clé (début de fenêtre) |
| `avg_price_5min` | Prix moyen sur la fenêtre |
| `vwap_5min` | VWAP sur la fenêtre |
| `volume_5min` | Volume sur la fenêtre |
| `pct_change` | Variation % vs fenêtre précédente |

### `gold/features` (1 ligne par trade — optionnel ML)

`moving_avg_10`, `price_return` (%), `rolling_vol_10` — calculés par symbole en
ordre temporel.

## ▶️ Lancer

```bash
uv run python -m transformations.gold.agg_metrics [YYYY-MM-DD]
uv run python -m transformations.gold.features    [YYYY-MM-DD]
```

## ✅ Statut

Validé sur données réelles (229 trades Silver) : `agg_stock_metrics` (2 symboles),
`agg_5min` (4 fenêtres, VWAP cohérent), `features` (229 lignes). Ces tables Gold
alimenteront Snowflake (Étape 4 : chargement + modélisation dbt).
