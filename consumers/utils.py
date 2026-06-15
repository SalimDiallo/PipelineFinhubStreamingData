"""
Utilitaires partagés par les consumers Kafka -> S3 Bronze.

- Configuration S3/MinIO et Kafka lue depuis le `.env`
- Client S3 (boto3) compatible MinIO
- Écriture des micro-batchs en JSON Lines, partitionnés par date :
      bronze/<dataset>/date=YYYY-MM-DD/<timestamp>-<uuid>.jsonl

La couche Bronze conserve les données **brutes** (aucune transformation).
Le typage / la conversion en Parquet interviennent en Silver.
"""

import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.client import Config
from dotenv import load_dotenv
from kafka import KafkaConsumer

load_dotenv()


# -------------------------
# Configuration
# -------------------------
KAFKA_BOOTSTRAP_SERVERS: list[str] = [
    s.strip()
    for s in os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
    if s.strip()
]
CONSUMER_GROUP: str = os.getenv("CONSUMER_GROUP", "finhub-consumers")
BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))
BATCH_TIMEOUT_S: int = int(os.getenv("BATCH_TIMEOUT_S", "10"))

S3_ENDPOINT_URL: str = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET: str = os.getenv("S3_BUCKET", "datalake")


# -------------------------
# Client S3 / MinIO
# -------------------------
def get_s3_client():
    """Client boto3 configuré pour MinIO (S3-compatible)."""
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket(s3, bucket: str = S3_BUCKET) -> None:
    """Crée le bucket s'il n'existe pas (idempotent)."""
    existing = {b["Name"] for b in s3.list_buckets().get("Buckets", [])}
    if bucket not in existing:
        s3.create_bucket(Bucket=bucket)


# -------------------------
# Écriture Bronze
# -------------------------
def bronze_key(dataset: str, ts: datetime | None = None) -> str:
    """
    Construit la clé S3 d'un objet Bronze, partitionné par date :
        bronze/<dataset>/date=YYYY-MM-DD/<HHMMSS>-<uuid8>.jsonl
    """
    ts = ts or datetime.now(timezone.utc)
    date_part = ts.strftime("%Y-%m-%d")
    file_part = f"{ts.strftime('%H%M%S')}-{uuid.uuid4().hex[:8]}.jsonl"
    return f"bronze/{dataset}/date={date_part}/{file_part}"


def write_batch_jsonl(s3, dataset: str, records: list[dict]) -> str | None:
    """
    Écrit un batch d'événements en JSON Lines dans S3 Bronze.
    Retourne la clé de l'objet écrit, ou None si le batch est vide.
    """
    if not records:
        return None

    body = "\n".join(json.dumps(r) for r in records).encode("utf-8")
    key = bronze_key(dataset)
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=body, ContentType="application/x-ndjson")
    return key


# -------------------------
# Boucle de consommation générique
# -------------------------
def consume_to_bronze(topic: str, dataset: str, run_once: bool = False) -> int:
    """
    Consomme un topic Kafka et écrit les messages en S3 Bronze par micro-batch.

    Un batch est flush dès que `BATCH_SIZE` messages sont accumulés OU après
    `BATCH_TIMEOUT_S` secondes d'inactivité. Les offsets ne sont commités
    qu'après écriture réussie dans S3 (livraison at-least-once).

    - run_once=False (défaut) : streaming continu (Ctrl+C pour arrêter).
    - run_once=True : draine les messages disponibles puis s'arrête (mode batch,
      utilisé par Airflow). Retourne le nombre total de messages écrits.
    """
    s3 = get_s3_client()
    ensure_bucket(s3)

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=CONSUMER_GROUP,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=BATCH_TIMEOUT_S * 1000,
    )

    print(f"🟤 Consumer Bronze démarré | topic={topic} -> dataset={dataset}")
    print(f"   bucket s3://{S3_BUCKET} | batch={BATCH_SIZE} timeout={BATCH_TIMEOUT_S}s")

    # Force l'assignation des partitions avant la boucle batch : rejoindre le
    # groupe peut déclencher un rebalance plus long que consumer_timeout_ms.
    # Les messages éventuellement déjà renvoyés par ce poll sont traités ici.
    initial = consumer.poll(timeout_ms=3000)

    batch: list[dict] = []
    total = 0

    def flush() -> None:
        nonlocal batch, total
        if not batch:
            return
        key = write_batch_jsonl(s3, dataset, batch)
        consumer.commit()
        total += len(batch)
        print(f"   💾 {len(batch)} messages -> s3://{S3_BUCKET}/{key} (total={total})")
        batch = []

    # Amorce le batch avec les messages déjà retournés par le poll initial
    for records in initial.values():
        for message in records:
            batch.append(message.value)
            if len(batch) >= BATCH_SIZE:
                flush()

    try:
        while True:
            got_message = bool(initial)
            initial = {}  # ne compte qu'une fois
            # consumer_timeout_ms fait sortir l'itérateur après inactivité
            for message in consumer:
                got_message = True
                batch.append(message.value)
                if len(batch) >= BATCH_SIZE:
                    flush()
            # Timeout atteint : flush du batch partiel
            flush()
            if run_once:
                # Mode batch : on s'arrête une fois le topic drainé
                break
            if not got_message:
                # Aucun message sur cette fenêtre, on reboucle (poll suivant)
                continue
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt demandé")
    finally:
        flush()
        consumer.close()
        print(f"✅ Consumer fermé | {total} messages écrits au total")

    return total
