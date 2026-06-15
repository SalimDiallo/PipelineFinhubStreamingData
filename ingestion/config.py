"""
Configuration centralisée de l'ingestion.

Toutes les variables sensibles / d'environnement sont lues ici depuis le `.env`
afin que le reste du code ne dépende jamais directement de `os.getenv`.
"""

import os

from dotenv import load_dotenv

load_dotenv()


# -------------------------
# Finnhub
# -------------------------
FINNHUB_API_KEY: str | None = os.getenv("FINNHUB_API_KEY")

# Symboles à suivre en temps réel (ex: "AAPL,MSFT,BINANCE:BTCUSDT")
SYMBOLS: list[str] = [
    s.strip()
    for s in os.getenv("SYMBOLS", "AAPL,MSFT,AMZN").split(",")
    if s.strip()
]


# -------------------------
# Kafka
# -------------------------
KAFKA_BOOTSTRAP_SERVERS: list[str] = [
    s.strip()
    for s in os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
    if s.strip()
]

# Topic par type d'événement. La key des messages est toujours `symbol`.
TOPIC_TRADES: str = os.getenv("TOPIC_TRADES", "stock.trades")
TOPIC_QUOTES: str = os.getenv("TOPIC_QUOTES", "stock.quotes")
TOPIC_CANDLES: str = os.getenv("TOPIC_CANDLES", "stock.candles")

# Mapping type d'événement Finnhub -> topic Kafka
TOPIC_BY_EVENT_TYPE: dict[str, str] = {
    "trade": TOPIC_TRADES,
    "quote": TOPIC_QUOTES,
    "candle": TOPIC_CANDLES,
}


def validate() -> None:
    """Vérifie que la configuration minimale est présente."""
    if not FINNHUB_API_KEY:
        raise ValueError(
            "FINNHUB_API_KEY manquante. Renseignez-la dans le fichier .env"
        )
    if not SYMBOLS:
        raise ValueError("Aucun symbole configuré (variable SYMBOLS vide)")
