# Pipeline de données en temps réel

Ce projet consiste à concevoir une **pipeline de données en temps réel** exploitant les données du marché boursier. L'objectif était de récupérer des données financières en direct, de les traiter par étapes successives, puis de les mettre à disposition dans **Snowflake** pour des analyses rapides et fiables.

## Étape 1 — Ingestion & Streaming

- Récupération des données financières en direct via l'API **Finnhub**
- Diffusion en temps réel dans un topic **Kafka**

## Étape 2 — Stockage

- Mise en place d'un data lake **S3 (MinIO)** structuré en couches :  
  `Bronze → Silver → Gold`

## Étape 3 — Orchestration

- Automatisation du flux de bout en bout avec **Apache Airflow**

## Étape 4 — Transformation & Modélisation

- Application des règles métier
- Construction des modèles analytiques dans **Snowflake** à l'aide de **dbt**

## Étape 5 — Infrastructure

- Déploiement conteneurisé avec **Docker** pour garantir reproductibilité et scalabilité

---

Au final, ce projet m'a permis de mettre en œuvre une pipeline complète, du streaming en temps réel jusqu'à la modélisation analytique.
