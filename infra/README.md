# Étape 5 — Infrastructure (Docker)

Déploiement conteneurisé de toute la pipeline. L'infra est répartie en 3 stacks
Docker Compose, orchestrées par le `Makefile` à la racine.

| Stack | Fichier | Services |
| --- | --- | --- |
| Kafka | `kafka/docker-compose.yml` | Kafka (KRaft) + Kafka UI |
| Data lake + streaming | `infra/docker-compose.yml` | MinIO + producer + consumer-trades |
| Orchestration | `airflow/docker-compose.yml` | Airflow (webserver + scheduler) + Postgres |

## 🐳 Image projet (`infra/Dockerfile`)

Image `finhub-pipeline:latest` (Python 3.14 + uv) embarquant `ingestion/`,
`consumers/`, `transformations/`. Sert au **producteur** (`ingestion.run_ingestion`)
et aux **consumers** (`consumers.consumer_*`).

## ▶️ Démarrer toute l'infra

```bash
make up        # kafka -> topics -> minio/producer/consumer -> airflow
make ps        # état des conteneurs
make down      # tout arrêter
make clean     # arrêter + supprimer les volumes (DONNÉES PERDUES)
```

Détail des cibles : `make kafka`, `make topics`, `make infra`, `make airflow`,
`make airflow-init` (init DB Airflow, une fois), `make logs` (logs producteur).

## 🔌 Réseaux

Les conteneurs communiquent par les réseaux Docker partagés :
- `kafka:29092` (listener interne Kafka)
- `minio:9000` (API S3 interne)

Airflow rejoint `kafka_default` et `infra_default` en réseaux externes
(voir `airflow/docker-compose.yml`).

## 📍 Endpoints

| Service | URL |
| --- | --- |
| Kafka UI | http://localhost:8080 |
| MinIO Console | http://localhost:9001 (minioadmin/minioadmin) |
| Airflow | http://localhost:8082 (airflow/airflow) |

## ⚠️ Espace disque

MinIO refuse d'écrire (`XMinioStorageFull`) sous son seuil de sécurité. Si le
disque hôte est saturé, libérer de l'espace :

```bash
docker builder prune -af && docker image prune -af
```

## ✅ Statut

Image construite, producer et consumer conteneurisés démarrent et se connectent
à Kafka et MinIO via les réseaux internes (validé). Stacks orchestrées par le
Makefile.
