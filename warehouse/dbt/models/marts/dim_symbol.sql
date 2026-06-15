-- Dimension symbole : un enregistrement par symbole observé.
-- sector / company_name ne sont pas fournis par le flux Finnhub gratuit :
-- colonnes présentes (conformité au schéma de l'archi) mais nulles pour l'instant.

select
    symbol,
    cast(null as varchar)        as sector,
    cast(null as varchar)        as company_name,
    min(event_time)              as first_seen,
    max(event_time)              as last_seen,
    count(*)                     as trade_count
from {{ ref('stg_trades') }}
group by symbol
