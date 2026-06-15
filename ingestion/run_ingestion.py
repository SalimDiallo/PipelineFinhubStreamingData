"""
Point d'entrée de l'ingestion temps réel : Finnhub WebSocket -> Kafka.

Usage :
    uv run python -m ingestion.run_ingestion

Configuration via .env (voir ingestion/config.py) :
    FINNHUB_API_KEY, SYMBOLS, KAFKA_BOOTSTRAP_SERVERS, TOPIC_*
"""

from ingestion import config
from ingestion.finnhub_client import FinnhubClient
from ingestion.producer import MarketDataProducer


def main() -> None:
    config.validate()

    print("🚀 Démarrage de l'ingestion Finnhub -> Kafka")
    print(f"   Symboles : {', '.join(config.SYMBOLS)}")
    print(f"   Kafka    : {', '.join(config.KAFKA_BOOTSTRAP_SERVERS)}")
    print(f"   Topic trades : {config.TOPIC_TRADES}")

    client = FinnhubClient()
    producer = MarketDataProducer()

    def on_event(event: dict) -> None:
        producer.send(event)
        print(
            f"📈 {event['symbol']} | {event['price']} "
            f"x{event['volume']} @ {event['timestamp']}"
        )

    try:
        client.start_stream(config.SYMBOLS, on_event)
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt demandé")
    finally:
        producer.close()
        print("✅ Producteur Kafka fermé proprement")


if __name__ == "__main__":
    main()
