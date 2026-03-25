select
    alianza_id,
    nombre,
    tipo,
    contacto,
    beneficio
from {{ source('ta01_raw', 'alianza') }}
