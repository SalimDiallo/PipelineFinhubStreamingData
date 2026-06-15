"""
Consumer : stock.candles -> S3 Bronze (bronze/candles/date=YYYY-MM-DD/).

Usage :
    uv run python -m consumers.consumer_candles
"""

import os

from consumers.utils import consume_to_bronze

TOPIC = os.getenv("TOPIC_CANDLES", "stock.candles")
DATASET = "candles"


def main() -> None:
    consume_to_bronze(TOPIC, DATASET)


if __name__ == "__main__":
    main()
