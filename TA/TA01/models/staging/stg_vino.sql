select
    vino_id,
    nombre,
    estilo,
    variedad_uva,
    botella_ml,
    cast(costo_unitario as numeric) as costo_unitario,
    cast(precio_lista as numeric) as precio_lista,
    cast(graduacion as numeric) as graduacion
from {{ source('ta01_raw', 'vino') }}
