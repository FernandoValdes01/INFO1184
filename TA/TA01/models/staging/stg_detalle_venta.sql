select
    detalle_venta_id,
    venta_id,
    vino_id,
    cantidad,
    cast(precio_unitario as numeric) as precio_unitario,
    cast(subtotal as numeric) as subtotal
from {{ source('ta01_raw', 'detalle_venta') }}
