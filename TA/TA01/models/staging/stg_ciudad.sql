select
    ciudad_id,
    region_id,
    nombre
from {{ source('ta01_raw', 'ciudad') }}
