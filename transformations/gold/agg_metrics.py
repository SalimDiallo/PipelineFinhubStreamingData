"""
Agrégations Silver -> Gold sur les trades.

Lecture  : silver/trades/date=YYYY-MM-DD/trades.parquet
Écriture :
    gold/agg_stock_metrics/date=YYYY-MM-DD/agg_stock_metrics.parquet  (par symbole/jour)
    gold/agg_5min/date=YYYY-MM-DD/agg_5min.parquet                    (fenêtres 5 min)

Métriques (cf. details-projet.md) :
  - VWAP (Volume Weighted Average Price)
  - avg_price (moyenne), total_volume
  - volatility (écart-type des prix)
  - daily_return (variation entre premier et dernier prix du jour)
  - par fenêtre 5 min : avg_price_5min, volume_5min, pct_change

Usage :
    uv run python -m transformations.gold.agg_metrics [YYYY-MM-DD]
"""

import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from consumers.utils import get_s3_client
from transformations.gold.utils import read_silver, write_gold


def _vwap(prices: pd.Series, volumes: pd.Series) -> float:
    total_vol = volumes.sum()
    if total_vol == 0:
        return float(prices.mean())
    return float((prices * volumes).sum() / total_vol)


def daily_metrics(df: pd.DataFrame, date: str) -> pd.DataFrame:
    """Une ligne par symbole : métriques agrégées sur la journée."""
    rows = []
    for symbol, g in df.sort_values("timestamp").groupby("symbol", observed=True):
        first_price = g["price"].iloc[0]
        last_price = g["price"].iloc[-1]
        daily_return = (
            (last_price - first_price) / first_price * 100 if first_price else np.nan
        )
        rows.append(
            {
                "symbol": symbol,
                "date": date,
                "avg_price": float(g["price"].mean()),
                "vwap": _vwap(g["price"], g["volume"]),
                "total_volume": float(g["volume"].sum()),
                "volatility": float(g["price"].std(ddof=0)),
                "daily_return_pct": daily_return,
                "trade_count": int(len(g)),
            }
        )
    return pd.DataFrame(rows)


def _window_agg(window: pd.DataFrame) -> pd.Series:
    return pd.Series(
        {
            "avg_price_5min": window["price"].mean(),
            "volume_5min": window["volume"].sum(),
            "vwap_5min": _vwap(window["price"], window["volume"]),
        }
    )


def window_5min(df: pd.DataFrame) -> pd.DataFrame:
    """Agrégations par fenêtre de 5 minutes et par symbole."""
    df = df.set_index("event_time").sort_index()
    out = []
    for symbol, g in df.groupby("symbol", observed=True):
        # apply sur chaque fenêtre : price et volume restent alignés
        agg = g.resample("5min").apply(_window_agg)
        agg = agg.dropna(subset=["avg_price_5min"])
        # variation % du prix moyen d'une fenêtre à la suivante
        agg["pct_change"] = agg["avg_price_5min"].pct_change() * 100
        agg["symbol"] = symbol
        out.append(agg.reset_index())

    if not out:
        return pd.DataFrame()
    result = pd.concat(out, ignore_index=True)
    cols = ["symbol", "event_time", "avg_price_5min", "vwap_5min", "volume_5min", "pct_change"]
    return result[cols]


def main(date: str | None = None) -> None:
    date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    s3 = get_s3_client()

    silver = read_silver(s3, "trades", date)
    print(f"📥 Silver trades {date} : {len(silver)} lignes")
    if silver.empty:
        print("⚠️  Aucune donnée Silver pour cette date")
        return

    daily = daily_metrics(silver, date)
    k1 = write_gold(s3, "agg_stock_metrics", date, daily)
    print(f"🟡 Gold écrit : s3://datalake/{k1} ({len(daily)} symboles)")

    win = window_5min(silver)
    k2 = write_gold(s3, "agg_5min", date, win)
    print(f"🟡 Gold écrit : s3://datalake/{k2} ({len(win)} fenêtres 5min)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
