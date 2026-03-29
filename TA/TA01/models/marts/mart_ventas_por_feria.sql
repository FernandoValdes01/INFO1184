with visitantes as (
    select
        feria_id,
        count(*) as visitantes
    from {{ ref('stg_visitante') }}
    group by 1
),
ventas as (
    select
        feria_id,
        count(*) as ventas,
        sum(monto_neto) as ingresos
    from {{ ref('stg_venta') }}
    group by 1
),
botellas as (
    select
        v.feria_id,
        sum(d.cantidad) as botellas_vendidas
    from {{ ref('stg_venta') }} v
    join {{ ref('stg_detalle_venta') }} d
        on v.venta_id = d.venta_id
    group by 1
)

select
    f.feria_id,
    f.nombre as feria,
    c.ciudad_id,
    c.nombre as ciudad,
    f.fecha_inicio,
    f.fecha_fin,
    coalesce(vis.visitantes, 0) as visitantes,
    coalesce(ven.ventas, 0) as ventas,
    coalesce(ven.ingresos, 0) as ingresos,
    coalesce(bot.botellas_vendidas, 0) as botellas_vendidas
from {{ ref('stg_feria') }} f
left join {{ ref('stg_ciudad') }} c
    on f.ciudad_id = c.ciudad_id
left join visitantes vis
    on f.feria_id = vis.feria_id
left join ventas ven
    on f.feria_id = ven.feria_id
left join botellas bot
    on f.feria_id = bot.feria_id
