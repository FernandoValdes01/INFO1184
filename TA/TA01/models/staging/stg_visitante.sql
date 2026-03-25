select
    visitante_id,
    feria_id,
    segmento_id,
    ciudad_origen_id,
    cast(fecha_visita as date) as fecha_visita,
    case
        when cast(acepta_contacto as text) in ('1', 't', 'true', 'TRUE') then true
        else false
    end as acepta_contacto,
    interes_vino_id
from {{ source('ta01_raw', 'visitante') }}
