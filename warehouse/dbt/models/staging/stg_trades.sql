-- Staging des trades : lit les Parquet Silver depuis MinIO via DuckDB httpfs.
-- Une vue : pas de matérialisation lourde, typage déjà fait en Silver.

with source as (
    select *
    from read_parquet('s3://datalake/silver/trades/*/trades.parquet')
)

select
    cast(symbol as varchar)        as symbol,
    cast(price as double)          as price,
    cast(volume as double)         as volume,
    cast(timestamp as bigint)      as event_ts_ms,
    cast(event_time as timestamp)  as event_time
from source
