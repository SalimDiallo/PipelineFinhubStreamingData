# Dashboard BI — Streamlit

Tableau de bord de visualisation des métriques de marché, branché sur les
modèles dbt (couche Gold) stockés dans DuckDB.

```
DuckDB (finhub.duckdb, lecture seule)
   ├── agg_stock_metrics   (VWAP, volatilité, daily_return, volume)
   ├── fact_trades         (grain fin : un enregistrement par trade)
   └── dim_symbol
        │
        ▼
   Streamlit + Plotly  →  http://localhost:8501
```

## ▶️ Lancer

Prérequis : les modèles dbt doivent être construits (`dbt run`) — le fichier
`warehouse/dbt/finhub.duckdb` doit exister.

```bash
uv run streamlit run dashboard/app.py
```

Le dashboard s'ouvre sur http://localhost:8501.

## 📊 Contenu

- **KPIs** : nombre de symboles, total de trades, volume total, volatilité moyenne.
- **Trades par symbole** et **volatilité par symbole** (barres).
- **Évolution du prix** dans le temps (courbes, depuis `fact_trades`).
- **Tableau détaillé** des métriques `agg_stock_metrics`.
- **Filtre** par symbole (barre latérale).

## 🔧 Configuration

| Variable | Défaut | Description |
| --- | --- | --- |
| `DUCKDB_PATH` | `../warehouse/dbt/finhub.duckdb` | Chemin de la base DuckDB |

## Notes

- Lecture **read-only** : n'interfère pas avec `dbt run` (pas de verrou en écriture).
- Palette en niveaux de gris, cohérente avec le rapport du projet.
- Les requêtes sont mises en cache (60 s) pour la réactivité.
