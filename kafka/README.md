# Stack Kafka

Broker Kafka en mode KRaft (sans ZooKeeper, deprecie depuis Kafka 3.x), image
officielle `apache/kafka`, accompagne d'une interface Kafka UI.

## Lancer

```bash
docker compose -f kafka/docker-compose.yml up -d
bash kafka/create_topics.sh
```

## Endpoints

| Service | Adresse | Usage |
| --- | --- | --- |
| Broker (hote) | `localhost:9092` | Producteurs / consommateurs locaux |
| Broker (interne) | `kafka:29092` | Autres conteneurs du reseau docker |
| Kafka UI | http://localhost:8080 | Visualisation des topics et messages |

## Topics

Crees par `create_topics.sh` (3 partitions, replication 1) :

- `stock.trades`
- `stock.quotes`
- `stock.candles`

La cle des messages est le `symbol`, ce qui garantit l'ordre par symbole sur une
partition.

## Commandes utiles

```bash
# Lister les topics
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 --list

# Lire un topic
docker exec kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic stock.trades \
  --from-beginning --property print.key=true

# Offsets par partition
docker exec kafka /opt/kafka/bin/kafka-get-offsets.sh \
  --bootstrap-server localhost:9092 --topic stock.trades
```

## Arreter

```bash
docker compose -f kafka/docker-compose.yml down       # garde les donnees
docker compose -f kafka/docker-compose.yml down -v    # supprime le volume
```
