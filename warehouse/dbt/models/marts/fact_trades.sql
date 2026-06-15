-- Table de faits : un enregistrement par trade.

select
    symbol,
    event_time,
    cast(event_time as date) as trade_date,
    price,
    volume,
    price * volume as notional
from {{ ref('stg_trades') }}
