-- Table analytique : métriques par symbole et par jour.
-- Reproduit en SQL les agrégats de la couche Gold (VWAP, volatilité, etc.).

with trades as (
    select
        symbol,
        cast(event_time as date) as trade_date,
        event_time,
        price,
        volume
    from {{ ref('stg_trades') }}
),

ordered as (
    select
        *,
        first_value(price) over w  as first_price,
        last_value(price)  over w  as last_price
    from trades
    window w as (
        partition by symbol, trade_date
        order by event_time
        rows between unbounded preceding and unbounded following
    )
)

select
    symbol,
    trade_date as date,
    avg(price)                                          as avg_price,
    sum(price * volume) / nullif(sum(volume), 0)        as vwap,
    sum(volume)                                         as total_volume,
    stddev_pop(price)                                   as volatility,
    (max(last_price) - min(first_price))
        / nullif(min(first_price), 0) * 100             as daily_return_pct,
    count(*)                                            as trade_count
from ordered
group by symbol, trade_date
