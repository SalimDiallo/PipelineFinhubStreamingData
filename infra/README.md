# Infrastructure (Docker)

Deploiement conteneurise de la pipeline. L'infrastructure est repartie en trois
stacks Docker Compose, orchestrees par le Makefile a la racine.

| Stack | Fichier | Services |
| --- | --- | --- |
| Kafka | `kafka/docker-compose.yml` | Kafka (KRaft) + Kafka UI |
| Data lake | `infra/docker-compose.yml` | MinIO + producer + consumer-trades |
| Orchestration | `airflow/docker-compose.yml` | Airflow + Postgres |

## Image du projet

`infra/Dockerfile` construit l'image `finhub-pipeline` (Python 3.14 + uv)
embarquant `ingestion`, `consumers` et `transformations`. Elle sert au
producteur et aux consumers.

## Demarrer toute l'infra

```bash
make up        # kafka -> topics -> minio/producer/consumer -> airflow
make ps        # etat des conteneurs
make down      # tout arreter
make clean     # tout arreter et supprimer les volumes (donnees perdues)
```

Autres cibles : `make kafka`, `make topics`, `make infra`, `make airflow`,
`make airflow-init`, `make dashboard`, `make logs`.

## Reseaux

Les conteneurs communiquent par les reseaux docker partages, via les listeners
internes (`kafka:29092`, `minio:9000`), plus fiables que la passerelle de l'hote.

## Endpoints

| Service | URL |
| --- | --- |
| Kafka UI | http://localhost:8080 |
| MinIO Console | http://localhost:9001 (minioadmin / minioadmin) |
| Airflow | http://localhost:8082 (airflow / airflow) |
| Dashboard BI | http://localhost:8501 |

## Espace disque

MinIO refuse d'ecrire (`XMinioStorageFull`) sous son seuil de securite. En cas de
disque sature :

```bash
docker builder prune -af && docker image prune -af
```
