# Dashboard BI (Streamlit)

Tableau de bord de visualisation des metriques de marche, branche sur les
modeles dbt (couche analytique) stockes dans DuckDB.

```
DuckDB (finhub.duckdb, lecture seule)
   |-- agg_stock_metrics   (VWAP, volatilite, daily_return, volume)
   |-- fact_trades         (grain fin : un enregistrement par trade)
   `-- dim_symbol
        -->  Streamlit + Plotly  -->  http://localhost:8501
```

## Lancer

Prerequis : les modeles dbt doivent etre construits (`dbt run`), le fichier
`warehouse/dbt/finhub.duckdb` doit exister.

```bash
make dashboard
# ou : uv run streamlit run dashboard/app.py
```

## Contenu

- Indicateurs cles : symboles suivis, total des trades, volume total, volatilite
  moyenne.
- Trades et volatilite par symbole (barres).
- Evolution du prix dans le temps (courbes, depuis `fact_trades`).
- Tableau detaille des metriques `agg_stock_metrics`.
- Filtre par symbole.

## Configuration

| Variable | Defaut | Description |
| --- | --- | --- |
| `DUCKDB_PATH` | `../warehouse/dbt/finhub.duckdb` | Chemin de la base DuckDB |

## Notes

- Lecture seule : n'interfere pas avec dbt run.
- Palette en niveaux de gris, coherente avec le rapport.
- Requetes mises en cache (60 s).
