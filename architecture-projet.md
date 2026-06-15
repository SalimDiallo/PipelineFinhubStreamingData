```md
# Arborescence du projet
```

real-time-stock-pipeline/
│
├── ingestion/
│ ├── finnhub_client.py # Connexion à l’API Finnhub (REST/WebSocket)
│ ├── producer.py # Envoi des données vers Kafka
│ ├── config.py # Clés API et paramètres d’ingestion
│ └── schemas/ # Schémas JSON (optionnel Avro)
│ ├── trades.json
│ ├── quotes.json
│ └── candles.json
│
├── kafka/
│ ├── create_topics.sh # Script création des topics Kafka
│ ├── docker-compose.yml # Stack Kafka + Zookeeper
│ └── config/
│ └── server.properties
│
├── consumers/
│ ├── consumer_trades.py # Consommation Trades → S3 Bronze
│ ├── consumer_quotes.py
│ ├── consumer_candles.py
│ └── utils.py # Utilitaires (Parquet, timestamps…)
│
├── data_lake/
│ ├── bronze/ # Données brutes (raw)
│ ├── silver/ # Données nettoyées
│ └── gold/ # Données enrichies / prêtes business
│
├── transformations/
│ ├── silver/
│ │ ├── clean_trades.py # Déduplication et nettoyage trades
│ │ ├── clean_quotes.py
│ │ └── clean_candles.py
│ └── gold/
│ ├── agg_metrics.py # Agrégations (VWAP, moyennes, volumes…)
│ └── features.py # Création de features ML (optionnel)
│
├── airflow/
│ ├── dags/
│ │ └── stock_pipeline_dag.py # DAG principal Airflow
│ ├── plugins/
│ └── requirements.txt
│
├── warehouse/
│ ├── snowflake/
│ │ ├── schema.sql # Création des tables Snowflake
│ │ └── load.sql # Chargement COPY INTO
│ └── dbt/
│ ├── dbt_project.yml
│ ├── models/
│ │ ├── staging/
│ │ │ └── stg_trades.sql
│ │ ├── marts/
│ │ │ ├── fact_trades.sql
│ │ │ ├── dim_symbol.sql
│ │ │ └── agg_stock_metrics.sql
│ └── tests/
│ └── schema.yml
│
├── infra/
│ ├── docker-compose.yml # Déploiement de toute l’infra
│ ├── Dockerfile # Image projet
│ └── env/ # Variables d’environnement
│
├── monitoring/ (optionnel)
│ ├── prometheus.yml
│ └── grafana/
│
├── tests/
│ ├── test_ingestion.py
│ ├── test_transformations.py
│ └── test_pipeline.py
│
├── notebooks/ (exploration)
│ └── analysis.ipynb
│
├── requirements.txt
├── README.md
└── .env

```

```
