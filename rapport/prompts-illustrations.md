# Prompts IA — Illustrations des workflows

Prompts destinés à un générateur d'images IA (Midjourney, DALL·E, Stable Diffusion,
Ideogram, etc.) pour produire les schémas de la pipeline FinHub.

**Style commun à respecter pour les 4 images** (cohérent avec le rapport sobre) :

> Technical architecture diagram, flat minimalist vector style, strictly
> monochrome grayscale palette (white background, light gray boxes, dark gray
> outlines and text), thin 1px connector lines with simple arrowheads, clean
> sans-serif labels, generous whitespace, no gradients, no 3D, no glossy effects,
> no decorative icons beyond simple line glyphs, professional engineering
> documentation look, 16:9, high resolution.

> Astuce : si l'outil supporte un paramètre de style/seed, réutiliser le même
> pour les 4 images afin de garantir l'homogénéité visuelle. Ajouter en négatif :
> `no color, no neon, no photorealism, no clutter, no handwriting`.

---

## 1. Workflow global (vue d'ensemble end-to-end)

```
Create a clean horizontal data engineering pipeline diagram, flat minimalist
vector style, strictly monochrome grayscale (white background, light gray boxes,
dark gray thin outlines and arrows, sans-serif labels), no color.

Show a single left-to-right flow of seven labeled stages connected by thin
arrows:
1) "Finnhub API" (cloud / source glyph) -- real-time stock market data
2) "Kafka" (message queue, three stacked partition bars) -- streaming buffer
3) "Bronze" (raw layer, document glyph) -- inside an S3 / data lake container
4) "Silver" (cleaned layer, table glyph) -- inside the same data lake container
5) "Gold" (business metrics, chart glyph) -- inside the same data lake container
6) "dbt / DuckDB" (analytics models, cube glyph)
7) "BI / Analytics" (dashboard glyph) -- final consumption

Group stages 3, 4, 5 inside one rounded rectangle labeled "Data Lake (MinIO / S3)".
Above the whole flow, a thin labeled band "Apache Airflow — batch orchestration"
spanning stages 3 to 6, with small downward ticks indicating it triggers them.
Label the first arrow "WebSocket", the second "produce (key = symbol)".
Title at top: "Real-Time Stock Market Data Pipeline".
Generous whitespace, no gradients, no 3D, engineering documentation look, 16:9.
```

---

## 2. Niveau Ingestion & Streaming (Étape 1 : Finnhub → Kafka)

```
Create a focused technical diagram of a streaming ingestion layer, flat
minimalist vector style, strictly monochrome grayscale (white background, light
gray boxes, dark gray thin outlines and arrows, sans-serif labels), no color.

Left to right:
- "Finnhub API" source node with a small WebSocket waveform glyph.
- An arrow labeled "WebSocket (real-time trades)" pointing to a box
  "Finnhub Client" containing two small sub-labels: "WebSocket stream" and
  "normalize event {symbol, price, volume, timestamp}".
- An arrow to a box "Kafka Producer" with sub-labels "key = symbol",
  "value = JSON", "acks = all".
- An arrow to a "Kafka Broker (KRaft mode)" cylinder showing three topics as
  stacked rows: "stock.trades", "stock.quotes", "stock.candles", each split into
  3 partition cells.

Show that messages with the same symbol map to the same partition (draw two
"AAPL" messages routing into the same partition cell with thin guide lines).
Small side note box: "Kafka UI — monitoring" connected by a dashed thin line to
the broker.
Title at top: "Step 1 — Ingestion & Streaming".
Generous whitespace, no gradients, no 3D, engineering documentation look, 16:9.
```

---

## 3. Niveau Data Lake (Étape 2 : Bronze → Silver → Gold)

```
Create a technical diagram of a medallion data lake architecture, flat
minimalist vector style, strictly monochrome grayscale (white background, light
gray boxes, dark gray thin outlines and arrows, sans-serif labels), no color.
Use only shades of gray to distinguish layers (lightest = Bronze, mid =
Silver, darkest header = Gold), never actual colors.

A "Kafka" cylinder on the left feeds three "Consumer" boxes
(trades / quotes / candles) via thin arrows.
Then three stacked horizontal layer bands, left to right:

- "BRONZE — raw" : glyph of stacked JSON documents, sub-label
  "JSON Lines, partitioned by date", path "bronze/<dataset>/date=YYYY-MM-DD/".
- arrow labeled "clean: dedup, typing, timestamps (UTC), null handling"
- "SILVER — cleaned" : glyph of a typed table, sub-label "Parquet (typed)".
- arrow labeled "aggregate"
- "GOLD — business" : glyph of a bar chart, sub-labels
  "agg_stock_metrics (VWAP, volatility, daily return)", "agg_5min", "features".

Wrap the three bands inside one large rounded rectangle labeled
"Data Lake — MinIO (S3 compatible)".
Title at top: "Step 2 — Storage: Bronze -> Silver -> Gold".
Generous whitespace, no gradients, no 3D, engineering documentation look, 16:9.
```

---

## 4. Niveau Orchestration & Modélisation (Étapes 3–4 : Airflow + dbt)

```
Create a technical diagram combining batch orchestration and analytics
modeling, flat minimalist vector style, strictly monochrome grayscale (white
background, light gray boxes, dark gray thin outlines and arrows, sans-serif
labels), no color.

Top section: an Apache Airflow DAG as a horizontal chain of four task nodes
(rounded rectangles) connected by thin arrows:
"consume_to_s3" -> "transform_silver" -> "transform_gold" -> "dbt_build".
Label above the chain: "DAG stock_pipeline — schedule @hourly".
Small note: "streaming Finnhub -> Kafka runs continuously, outside Airflow"
in a dashed box, separated from the DAG.

Bottom section: expand the "dbt_build" node into a dbt model lineage graph,
left to right:
- source "silver/trades (Parquet on MinIO)" cylinder
- "stg_trades" (view glyph)
- which fans out with thin arrows into three model boxes:
  "fact_trades", "dim_symbol", "agg_stock_metrics".
- a small side label "dbt tests: not_null, unique" attached with a dashed line.
- engine note at the bottom: "DuckDB + httpfs (reads S3/MinIO)".

Connect the top "dbt_build" node down to the bottom lineage with a thin arrow.
Title at top: "Steps 3 & 4 — Orchestration (Airflow) & Modeling (dbt)".
Generous whitespace, no gradients, no 3D, engineering documentation look, 16:9.
```

---

## Notes d'intégration LaTeX

Une fois les images générées (PNG/PDF), les placer dans `rapport/img/` et les
insérer avec :

```latex
\usepackage{graphicx}
...
\begin{figure}[h]
  \centering
  \includegraphics[width=\linewidth]{img/workflow-global.png}
  \caption{Vue d'ensemble de la pipeline.}
\end{figure}
```

Noms de fichiers suggérés :
`workflow-global`, `workflow-ingestion`, `workflow-datalake`,
`workflow-orchestration-dbt`.
```
