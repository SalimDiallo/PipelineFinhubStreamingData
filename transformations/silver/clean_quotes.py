"""
Nettoyage Bronze -> Silver pour les quotes (bid/ask).

Lecture  : bronze/quotes/date=YYYY-MM-DD/*.jsonl
Écriture : silver/quotes/date=YYYY-MM-DD/quotes.parquet

Règles :
  - typage : symbol(str), bid/ask/bidSize/askSize(float)
  - normalisation timestamp epoch ms -> event_time (datetime UTC)
  - suppression des lignes sans symbol/bid/ask/timestamp
  - déduplication sur (symbol, bid, ask, timestamp)

Usage :
    uv run python -m transformations.silver.clean_quotes [YYYY-MM-DD]
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

DATASET = "quotes"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["symbol"] = df["symbol"].astype("string")
    for col in ("bid", "ask", "bidSize", "askSize"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce").astype("Int64")

    df = df.dropna(subset=["symbol", "bid", "ask", "timestamp"])
    df = normalize_timestamp(df, "timestamp")
    df = df.drop_duplicates(subset=["symbol", "bid", "ask", "timestamp"])
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    cols = ["symbol", "bid", "ask", "bidSize", "askSize", "timestamp", "event_time"]
    return df[[c for c in cols if c in df.columns]]


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
