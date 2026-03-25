select
    degustacion_id,
    visitante_id,
    stand_id,
    vino_id,
    puntaje,
    intencion_compra,
    comentarios
from {{ source('ta01_raw', 'degustacion') }}
