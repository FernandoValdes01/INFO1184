select
    vi.vino_id,
    vi.nombre as vino,
    vi.estilo,
    sum(dv.cantidad) as botellas_vendidas,
    sum(dv.subtotal) as ingresos_brutos
from {{ ref('stg_vino') }} vi
join {{ ref('stg_detalle_venta') }} dv
    on vi.vino_id = dv.vino_id
group by 1, 2, 3
