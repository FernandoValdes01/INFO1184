select
    stand_id,
    feria_id,
    codigo,
    ubicacion,
    cast(tamano_m2 as numeric) as tamano_m2,
    cast(costo_diario as numeric) as costo_diario
from {{ source('ta01_raw', 'stand') }}
