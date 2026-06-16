# Modelisation (dbt + DuckDB)

Modeles analytiques construits avec dbt. DuckDB lit directement les fichiers
Parquet de la couche Silver depuis MinIO (extension httpfs).

L'architecture cible mentionne Snowflake (entrepot payant) ; DuckDB est utilise
ici pour une execution locale et gratuite. Les modeles SQL restent portables.

## Structure

```
warehouse/dbt/
|-- dbt_project.yml
|-- profiles.yml              # adaptateur duckdb + acces MinIO
|-- models/
|   |-- staging/stg_trades.sql
|   `-- marts/
|       |-- fact_trades.sql
|       |-- dim_symbol.sql
|       `-- agg_stock_metrics.sql
`-- tests/schema.yml
```

## Modeles

| Modele | Type | Contenu |
| --- | --- | --- |
| `stg_trades` | vue | Staging des trades Silver (type) |
| `fact_trades` | table | Fait : un enregistrement par trade |
| `dim_symbol` | table | Dimension symbole |
| `agg_stock_metrics` | table | Metriques par symbole / jour (VWAP, volatilite, ...) |

## Environnement

dbt-core ne supporte pas Python 3.14 (version du projet). dbt est donc isole
dans un environnement virtuel Python 3.12 dedie.

```bash
uv venv --python 3.12 warehouse/dbt/.venv
VIRTUAL_ENV=warehouse/dbt/.venv uv pip install dbt-duckdb
```

## Lancer

```bash
cd warehouse/dbt
export S3_ENDPOINT_HOST=localhost:9000 S3_ACCESS_KEY=minioadmin S3_SECRET_KEY=minioadmin
export DBT_PROFILES_DIR="$(pwd)"

.venv/bin/dbt run     # materialise les 4 modeles
.venv/bin/dbt test    # execute les tests not_null / unique
```

## Tests

Tests dbt (`not_null`, `unique`) sur les cles et mesures critiques : non-nullite
des symboles et prix, unicite du symbole dans la dimension.
