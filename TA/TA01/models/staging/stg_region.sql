select
    region_id,
    nombre
from {{ source('ta01_raw', 'region') }}
