select
    feria_id,
    ciudad_id,
    nombre,
    recinto,
    cast(fecha_inicio as date) as fecha_inicio,
    cast(fecha_fin as date) as fecha_fin,
    aforo_estimado,
    publico_objetivo
from {{ source('ta01_raw', 'feria') }}
