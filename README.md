# FinHub Streaming Data Pipeline

Pipeline de donnees en temps reel exploitant les donnees du marche boursier, de
l'ingestion jusqu'a la modelisation analytique et la restitution.

```
Finnhub API  -->  Kafka  -->  Data Lake (Bronze / Silver / Gold)  -->  dbt  -->  Dashboard BI
```

## Architecture

| Etape | Composant | Role |
| --- | --- | --- |
| 1 | Ingestion | Client Finnhub WebSocket vers producteur Kafka |
| 2 | Stockage | Consumers vers Bronze ; transformations Silver et Gold |
| 3 | Orchestration | DAG Apache Airflow (traitement batch) |
| 4 | Modelisation | Modeles dbt (fait, dimension, agregats) sur DuckDB |
| 5 | Infrastructure | Conteneurisation Docker et orchestration des stacks |
| - | Restitution | Dashboard BI (Streamlit) |

## Arborescence

```
finHubPipeline/
|-- ingestion/          # Finnhub -> Kafka
|-- kafka/              # stack Kafka (KRaft) + creation des topics
|-- consumers/          # Kafka -> Bronze
|-- transformations/
|   |-- silver/         # nettoyage -> Parquet type
|   `-- gold/           # metriques (VWAP, volatilite, ...)
|-- airflow/            # DAG d'orchestration + stack Airflow
|-- warehouse/dbt/      # modeles dbt (DuckDB)
|-- infra/              # Dockerfile + MinIO + services conteneurises
|-- dashboard/          # tableau de bord BI (Streamlit)
|-- rapport/            # rapport technique (LaTeX) + prompts d'illustrations
|-- Makefile            # orchestration de toute l'infra
`-- pyproject.toml      # dependances (uv)
```

Chaque dossier contient son propre README detaille.

## Pile technologique

Python (>= 3.14), uv, Apache Kafka (KRaft), MinIO (S3), pandas / pyarrow,
Apache Airflow, dbt + DuckDB, Streamlit / Plotly, Docker.

## Demarrage rapide

### 1. Configuration

```bash
cp .env.example .env
# renseigner FINNHUB_API_KEY dans .env
```

### 2. Infrastructure

```bash
make up        # Kafka + topics + MinIO + producer/consumer + Airflow
make ps        # etat des conteneurs
```

### 3. Traitement

Le streaming Finnhub vers Kafka alimente le data lake en continu. Le DAG Airflow
`stock_pipeline` (planifie @hourly) enchaine ensuite :

```
consume_to_s3 -> transform_silver -> transform_gold -> dbt_build
```

Interface Airflow : http://localhost:8082 (airflow / airflow).

### 4. Dashboard

```bash
make dashboard     # http://localhost:8501
```

## Endpoints

| Service | URL | Identifiants |
| --- | --- | --- |
| Kafka UI | http://localhost:8080 | - |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| Airflow | http://localhost:8082 | airflow / airflow |
| Dashboard BI | http://localhost:8501 | - |

## Couches du data lake

- Bronze : donnees brutes (JSON Lines), partitionnees par date.
- Silver : donnees nettoyees et typees (Parquet) ; deduplication, normalisation
  des timestamps, gestion des nulls.
- Gold : metriques business (VWAP, volatilite, rendement, volume agrege).

## Documentation

- `rapport/rapport.tex` : rapport technique complet du projet.
- READMEs par section : `ingestion/`, `kafka/`, `consumers/`,
  `transformations/silver/`, `transformations/gold/`, `airflow/`,
  `warehouse/dbt/`, `infra/`, `dashboard/`.

## Limites connues

- Plan Finnhub gratuit : seul le flux des trades est diffuse en temps reel.
- DuckDB local remplace Snowflake (payant) ; les modeles SQL restent portables.
- dbt est isole dans un environnement Python 3.12 (incompatibilite Python 3.14).
