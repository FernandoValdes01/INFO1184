select
    inventario_id,
    feria_id,
    vino_id,
    botellas_planificadas,
    botellas_recibidas,
    botellas_vendidas,
    stock_cierre
from {{ source('ta01_raw', 'inventario_feria') }}
