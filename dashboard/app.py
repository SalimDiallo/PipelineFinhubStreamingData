"""
Dashboard BI — Pipeline FinHub.

Lit les modèles dbt depuis DuckDB (finhub.duckdb) en lecture seule :
  - agg_stock_metrics : métriques par symbole/jour (VWAP, volatilité, ...)
  - fact_trades       : grain fin (un enregistrement par trade)
  - dim_symbol        : dimension symbole

Lancer :
    uv run streamlit run dashboard/app.py
"""

import os

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

# Chemin de la base DuckDB produite par dbt
DB_PATH = os.getenv(
    "DUCKDB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "warehouse", "dbt", "finhub.duckdb"),
)

# Palette sobre (niveaux de gris) cohérente avec le rapport
GRAYS = ["#2b2b2b", "#5a5a5a", "#888888", "#b5b5b5", "#d6d6d6"]

st.set_page_config(page_title="FinHub — Dashboard BI", layout="wide")


@st.cache_data(ttl=60)
def query(sql: str) -> pd.DataFrame:
    """Exécute une requête en lecture seule sur la base DuckDB."""
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        return con.execute(sql).df()
    finally:
        con.close()


# -------------------------
# En-tête
# -------------------------
st.title("FinHub — Dashboard BI")
st.caption(
    "Métriques de marché issues de la couche Gold (modèles dbt sur DuckDB). "
    "Données : Finnhub → Kafka → Data Lake → dbt."
)

try:
    metrics = query(
        "select symbol, date, avg_price, vwap, total_volume, volatility, "
        "daily_return_pct, trade_count from agg_stock_metrics order by trade_count desc"
    )
except Exception as e:  # base absente ou non construite
    st.error(
        "Impossible de lire la base DuckDB. Lancez d'abord la pipeline puis dbt "
        f"(`dbt run`). Détail : {e}"
    )
    st.stop()

if metrics.empty:
    st.warning("Aucune donnée. Exécutez la pipeline et `dbt run`.")
    st.stop()

# -------------------------
# Filtre
# -------------------------
symbols = sorted(metrics["symbol"].unique().tolist())
selected = st.sidebar.multiselect("Symboles", symbols, default=symbols)
metrics_f = metrics[metrics["symbol"].isin(selected)]

# -------------------------
# KPIs
# -------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Symboles suivis", metrics_f["symbol"].nunique())
c2.metric("Trades (total)", int(metrics_f["trade_count"].sum()))
c3.metric("Volume total", f"{metrics_f['total_volume'].sum():,.2f}")
c4.metric("Volatilité moyenne", f"{metrics_f['volatility'].mean():,.2f}")

st.divider()

# -------------------------
# Métriques par symbole
# -------------------------
left, right = st.columns(2)

with left:
    st.subheader("Nombre de trades par symbole")
    fig = px.bar(
        metrics_f.sort_values("trade_count"),
        x="trade_count",
        y="symbol",
        orientation="h",
        color_discrete_sequence=GRAYS,
    )
    fig.update_layout(showlegend=False, height=320, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Volatilité par symbole")
    fig = px.bar(
        metrics_f.sort_values("volatility"),
        x="volatility",
        y="symbol",
        orientation="h",
        color_discrete_sequence=GRAYS,
    )
    fig.update_layout(showlegend=False, height=320, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Évolution du prix (fact_trades)
# -------------------------
st.subheader("Évolution du prix dans le temps")
if selected:
    placeholders = ",".join(f"'{s}'" for s in selected)
    trades = query(
        "select symbol, event_time, price from fact_trades "
        f"where symbol in ({placeholders}) order by event_time"
    )
    if not trades.empty:
        fig = px.line(
            trades,
            x="event_time",
            y="price",
            color="symbol",
            color_discrete_sequence=GRAYS,
        )
        fig.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun trade pour les symboles sélectionnés.")

# -------------------------
# Tableau détaillé
# -------------------------
st.subheader("Métriques détaillées (agg_stock_metrics)")
st.dataframe(
    metrics_f.style.format(
        {
            "avg_price": "{:.2f}",
            "vwap": "{:.2f}",
            "total_volume": "{:.4f}",
            "volatility": "{:.2f}",
            "daily_return_pct": "{:.3f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)
