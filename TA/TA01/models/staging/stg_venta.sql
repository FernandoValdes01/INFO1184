select
    venta_id,
    feria_id,
    stand_id,
    visitante_id,
    cast(fecha_hora as timestamp) as fecha_hora,
    medio_pago,
    cast(monto_bruto as numeric) as monto_bruto,
    cast(descuento as numeric) as descuento,
    cast(monto_neto as numeric) as monto_neto
from {{ source('ta01_raw', 'venta') }}
