select
    i.inventario_id,
    i.feria_id,
    f.nombre as feria,
    i.vino_id,
    v.nombre as vino,
    i.botellas_planificadas,
    i.botellas_recibidas,
    i.botellas_vendidas,
    i.stock_cierre
from {{ ref('stg_inventario_feria') }} i
left join {{ ref('stg_feria') }} f
    on i.feria_id = f.feria_id
left join {{ ref('stg_vino') }} v
    on i.vino_id = v.vino_id
