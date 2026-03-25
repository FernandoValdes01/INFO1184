select
    feria_id,
    alianza_id,
    canal_promocion,
    cast(aporte_estimado as numeric) as aporte_estimado
from {{ source('ta01_raw', 'feria_alianza') }}
