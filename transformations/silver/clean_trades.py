"""
Nettoyage Bronze -> Silver pour les trades.

Lecture  : bronze/trades/date=YYYY-MM-DD/*.jsonl
Écriture : silver/trades/date=YYYY-MM-DD/trades.parquet

Règles :
  - typage : symbol(str), price(float), volume(float)
  - normalisation timestamp epoch ms -> event_time (datetime UTC)
  - suppression des lignes sans symbol/price/timestamp (nulls critiques)
  - déduplication exacte sur (symbol, price, volume, timestamp)

Usage :
    uv run python -m transformations.silver.clean_trades            # date du jour (UTC)
    uv run python -m transformations.silver.clean_trades 2026-06-15
"""

import sys
from datetime import datetime, timezone

import pandas as pd

from consumers.utils import get_s3_client
from transformations.silver.utils import (
    normalize_timestamp,
    read_bronze,
    write_silver,
)

DATASET = "trades"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    # Typage
    df = df.copy()
    df["symbol"] = df["symbol"].astype("string")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce").astype("Int64")

    # Nulls critiques
    df = df.dropna(subset=["symbol", "price", "timestamp"])

    # Normalisation timestamp + déduplication
    df = normalize_timestamp(df, "timestamp")
    df = df.drop_duplicates(subset=["symbol", "price", "volume", "timestamp"])

    # Ordre stable
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    return df[["symbol", "price", "volume", "timestamp", "event_time"]]


def main(date: str | None = None) -> None:
    date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    s3 = get_s3_client()

    raw = read_bronze(s3, DATASET, date)
    print(f"📥 Bronze {DATASET} {date} : {len(raw)} lignes brutes")

    clean_df = clean(raw)
    key = write_silver(s3, DATASET, date, clean_df)

    if key:
        print(f"✨ Silver écrit : s3://datalake/{key} ({len(clean_df)} lignes nettoyées)")
    else:
        print("⚠️  Rien à écrire (aucune donnée Bronze pour cette date)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
