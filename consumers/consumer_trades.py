"""
Consumer : stock.trades -> S3 Bronze (bronze/trades/date=YYYY-MM-DD/).

Usage :
    uv run python -m consumers.consumer_trades
"""

import os

from consumers.utils import consume_to_bronze

TOPIC = os.getenv("TOPIC_TRADES", "stock.trades")
DATASET = "trades"


def main() -> None:
    consume_to_bronze(TOPIC, DATASET)


if __name__ == "__main__":
    main()
