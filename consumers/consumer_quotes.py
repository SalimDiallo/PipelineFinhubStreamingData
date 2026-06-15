"""
Consumer : stock.quotes -> S3 Bronze (bronze/quotes/date=YYYY-MM-DD/).

Usage :
    uv run python -m consumers.consumer_quotes
"""

import os

from consumers.utils import consume_to_bronze

TOPIC = os.getenv("TOPIC_QUOTES", "stock.quotes")
DATASET = "quotes"


def main() -> None:
    consume_to_bronze(TOPIC, DATASET)


if __name__ == "__main__":
    main()
