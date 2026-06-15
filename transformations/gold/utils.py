"""
Utilitaires partagés par les transformations Silver -> Gold.

Gold = données **business-ready** : agrégations et métriques de marché
calculées à partir du Silver (Parquet propre).

Lecture  : silver/<dataset>/date=YYYY-MM-DD/<dataset>.parquet
Écriture : gold/<name>/date=YYYY-MM-DD/<name>.parquet
"""

import io

import pandas as pd

from consumers.utils import S3_BUCKET, get_s3_client


def read_silver(s3, dataset: str, date: str) -> pd.DataFrame:
    """Charge une partition Silver (Parquet) dans un DataFrame."""
    key = f"silver/{dataset}/date={date}/{dataset}.parquet"
    try:
        body = s3.get_object(Bucket=S3_BUCKET, Key=key)["Body"].read()
    except s3.exceptions.NoSuchKey:
        return pd.DataFrame()
    return pd.read_parquet(io.BytesIO(body), engine="pyarrow")


def write_gold(s3, name: str, date: str, df: pd.DataFrame) -> str | None:
    """Écrit un DataFrame Gold en Parquet. Retourne la clé S3 ou None si vide."""
    if df.empty:
        return None

    buf = io.BytesIO()
    df.to_parquet(buf, engine="pyarrow", index=False, compression="snappy")
    buf.seek(0)

    key = f"gold/{name}/date={date}/{name}.parquet"
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=buf.getvalue())
    return key
