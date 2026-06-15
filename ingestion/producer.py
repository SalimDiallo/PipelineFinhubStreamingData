"""
Producteur Kafka pour les événements de marché.

- key   : `symbol` (garantit l'ordre par symbole sur une même partition)
- value : JSON brut de l'événement
- topic : déterminé par le type d'événement (trade/quote/candle)
"""

import json
from typing import Optional

from kafka import KafkaProducer

from ingestion import config


class MarketDataProducer:
    def __init__(self, bootstrap_servers: Optional[list[str]] = None):
        self.bootstrap_servers = bootstrap_servers or config.KAFKA_BOOTSTRAP_SERVERS
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",          # attendre l'accusé de toutes les répliques
            retries=3,
            linger_ms=50,        # micro-batching pour le débit
        )

    def send(self, event: dict) -> None:
        """
        Envoie un événement vers le topic correspondant à son type.
        La key est le `symbol` de l'événement.
        """
        event_type = event.get("type", "trade")
        topic = config.TOPIC_BY_EVENT_TYPE.get(event_type)
        if topic is None:
            print(f"⚠️  Type d'événement inconnu, ignoré: {event_type}")
            return

        symbol = event.get("symbol")
        self.producer.send(topic, key=symbol, value=event)

    def flush(self) -> None:
        self.producer.flush()

    def close(self) -> None:
        self.producer.flush()
        self.producer.close()
