"""
Création de features (Gold, optionnel ML) à partir des trades Silver.

Lecture  : silver/trades/date=YYYY-MM-DD/trades.parquet
Écriture : gold/features/date=YYYY-MM-DD/features.parquet

Features par trade (calculées par symbole, ordre temporel) :
  - moving_avg_10 : moyenne mobile du prix sur 10 trades
  - price_return  : rendement vs trade précédent (%)
  - rolling_vol_10 : volatilité glissante (écart-type des prix sur 10 trades)

Usage :
    uv run python -m transformations.gold.features [YYYY-MM-DD]
"""

import sys
from datetime import datetime, timezone

import pandas as pd

from consumers.utils import get_s3_client
from transformations.gold.utils import read_silver, write_gold


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.sort_values(["symbol", "timestamp"]).copy()
    grp = df.groupby("symbol", observed=True)["price"]

    df["moving_avg_10"] = grp.transform(lambda s: s.rolling(10, min_periods=1).mean())
    df["price_return"] = grp.transform(lambda s: s.pct_change() * 100)
    df["rolling_vol_10"] = grp.transform(
        lambda s: s.rolling(10, min_periods=1).std(ddof=0)
    )

    return df[
        [
            "symbol",
            "event_time",
            "price",
            "volume",
            "moving_avg_10",
            "price_return",
            "rolling_vol_10",
        ]
    ]


def main(date: str | None = None) -> None:
    date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    s3 = get_s3_client()

    silver = read_silver(s3, "trades", date)
    print(f"📥 Silver trades {date} : {len(silver)} lignes")
    if silver.empty:
        print("⚠️  Aucune donnée Silver pour cette date")
        return

    feats = build_features(silver)
    key = write_gold(s3, "features", date, feats)
    print(f"🟡 Gold features écrit : s3://datalake/{key} ({len(feats)} lignes)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
