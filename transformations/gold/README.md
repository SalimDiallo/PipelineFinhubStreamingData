# Couche Gold (metriques business)

Calcule les metriques de marche a partir de la couche Silver et produit des
tables pretes pour l'analyse.

```
silver/trades/...  -->  agregations  -->  gold/<table>/date=YYYY-MM-DD/<table>.parquet
```

## Structure

| Fichier | Role |
| --- | --- |
| `utils.py` | Lecture Silver, ecriture Gold (Parquet) |
| `agg_metrics.py` | Metriques agregees (jour et fenetres 5 minutes) |
| `features.py` | Features par trade (moyenne mobile, rendement, volatilite) |

## Tables produites

### gold/agg_stock_metrics (par symbole / jour)

`symbol`, `date`, `avg_price`, `vwap`, `total_volume`, `volatility`,
`daily_return_pct`, `trade_count`.

### gold/agg_5min (par fenetre de 5 minutes)

`symbol`, `event_time`, `avg_price_5min`, `vwap_5min`, `volume_5min`,
`pct_change`.

### gold/features (par trade)

`moving_avg_10`, `price_return`, `rolling_vol_10`, calcules par symbole en ordre
temporel.

## Lancer

```bash
uv run python -m transformations.gold.agg_metrics [YYYY-MM-DD]
uv run python -m transformations.gold.features    [YYYY-MM-DD]
```
