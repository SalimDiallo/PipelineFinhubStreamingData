"""
Utilitaires partagés par les transformations Bronze -> Silver.

Silver = données **nettoyées** :
  - déduplication
  - typage des colonnes
  - normalisation des timestamps (epoch ms -> datetime UTC)
  - gestion des valeurs nulles

Lecture  : bronze/<dataset>/date=YYYY-MM-DD/*.jsonl  (JSON Lines brut)
Écriture : silver/<dataset>/date=YYYY-MM-DD/<dataset>.parquet  (Parquet typé)
"""

import io
import json

import pandas as pd

from consumers.utils import S3_BUCKET, get_s3_client


def _list_keys(s3, prefix: str) -> list[str]:
    """Liste toutes les clés sous un préfixe (paginé)."""
    keys: list[str] = []
    token = None
    while True:
        kwargs = {"Bucket": S3_BUCKET, "Prefix": prefix}
        if token:
            kwargs["ContinuationToken"] = token
        resp = s3.list_objects_v2(**kwargs)
        keys.extend(o["Key"] for o in resp.get("Contents", []))
        if not resp.get("IsTruncated"):
            break
        token = resp["NextContinuationToken"]
    return keys


def read_bronze(s3, dataset: str, date: str) -> pd.DataFrame:
    """
    Charge tous les fichiers JSONL d'une partition Bronze dans un DataFrame.
    `date` au format YYYY-MM-DD. Retourne un DataFrame vide si rien à lire.
    """
    prefix = f"bronze/{dataset}/date={date}/"
    keys = [k for k in _list_keys(s3, prefix) if k.endswith(".jsonl")]

    records: list[dict] = []
    for key in keys:
        body = s3.get_object(Bucket=S3_BUCKET, Key=key)["Body"].read().decode("utf-8")
        for line in body.splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return pd.DataFrame(records)


def write_silver(s3, dataset: str, date: str, df: pd.DataFrame) -> str | None:
    """
    Écrit un DataFrame typé en Parquet dans la couche Silver.
    Retourne la clé S3 écrite, ou None si le DataFrame est vide.
    """
    if df.empty:
        return None

    buf = io.BytesIO()
    df.to_parquet(buf, engine="pyarrow", index=False, compression="snappy")
    buf.seek(0)

    key = f"silver/{dataset}/date={date}/{dataset}.parquet"
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=buf.getvalue())
    return key


def normalize_timestamp(df: pd.DataFrame, col: str = "timestamp") -> pd.DataFrame:
    """
    Convertit une colonne epoch (millisecondes) en datetime UTC.
    Ajoute `event_time` (datetime) et conserve l'epoch d'origine.
    """
    df = df.copy()
    df["event_time"] = pd.to_datetime(df[col], unit="ms", utc=True)
    return df
