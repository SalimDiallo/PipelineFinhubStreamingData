# Stack Kafka

Broker **Kafka en mode KRaft** (sans Zookeeper, déprécié depuis Kafka 3.x),
image officielle `apache/kafka:3.9.0`, plus une **Kafka UI** pour la
visualisation.

## Lancer

```bash
docker compose -f kafka/docker-compose.yml up -d   # démarrer le broker + UI
bash kafka/create_topics.sh                         # créer les topics
```

## Endpoints

| Service | Adresse | Usage |
| --- | --- | --- |
| Broker (hôte) | `localhost:9092` | Producteurs/consommateurs Python |
| Broker (interne) | `kafka:29092` | Autres conteneurs du réseau docker |
| Kafka UI | http://localhost:8080 | Visualisation topics/messages |

## Topics

Créés par `create_topics.sh` (3 partitions, replication 1 — mono-nœud) :

- `stock.trades`
- `stock.quotes`
- `stock.candles`

La key des messages est le `symbol` → ordre garanti par symbole sur une
partition.

## Commandes utiles

```bash
# Lister les topics
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Lire un topic (key | value)
docker exec kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic stock.trades \
  --from-beginning --property print.key=true --property key.separator=" | "

# Nombre de messages par partition
docker exec kafka /opt/kafka/bin/kafka-get-offsets.sh \
  --bootstrap-server localhost:9092 --topic stock.trades
```

## Arrêter

```bash
docker compose -f kafka/docker-compose.yml down      # arrêter (garde les données)
docker compose -f kafka/docker-compose.yml down -v   # arrêter + effacer le volume
```

## Variables d'environnement du script

`create_topics.sh` accepte (avec valeurs par défaut) :
`KAFKA_CONTAINER=kafka`, `KAFKA_BOOTSTRAP=localhost:9092`,
`KAFKA_PARTITIONS=3`, `KAFKA_REPLICATION=1`,
`KAFKA_TOPICS_BIN=/opt/kafka/bin/kafka-topics.sh`.
