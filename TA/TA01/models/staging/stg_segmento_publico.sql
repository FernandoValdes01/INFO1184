select
    segmento_id,
    nombre,
    descripcion
from {{ source('ta01_raw', 'segmento_publico') }}
