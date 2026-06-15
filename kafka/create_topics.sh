#!/usr/bin/env bash
#
# Crée les topics Kafka du projet (idempotent : --if-not-exists).
# Suppose que la stack tourne : docker compose -f kafka/docker-compose.yml up -d
#
# Usage :
#   bash kafka/create_topics.sh

set -euo pipefail

CONTAINER="${KAFKA_CONTAINER:-kafka}"
BOOTSTRAP="${KAFKA_BOOTSTRAP:-localhost:9092}"
PARTITIONS="${KAFKA_PARTITIONS:-3}"
REPLICATION="${KAFKA_REPLICATION:-1}"
KAFKA_TOPICS_BIN="${KAFKA_TOPICS_BIN:-/opt/kafka/bin/kafka-topics.sh}"

# Topics du projet (voir details-projet.md)
TOPICS=("stock.trades" "stock.quotes" "stock.candles")

echo "🛠️  Création des topics sur ${CONTAINER} (${BOOTSTRAP})"

for topic in "${TOPICS[@]}"; do
  docker exec "${CONTAINER}" "${KAFKA_TOPICS_BIN}" \
    --bootstrap-server "${BOOTSTRAP}" \
    --create --if-not-exists \
    --topic "${topic}" \
    --partitions "${PARTITIONS}" \
    --replication-factor "${REPLICATION}"
  echo "   ✅ ${topic} (partitions=${PARTITIONS}, replication=${REPLICATION})"
done

echo ""
echo "📋 Topics existants :"
docker exec "${CONTAINER}" "${KAFKA_TOPICS_BIN}" \
  --bootstrap-server "${BOOTSTRAP}" --list
