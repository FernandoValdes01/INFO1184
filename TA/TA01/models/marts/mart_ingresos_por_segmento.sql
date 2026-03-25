select
    s.segmento_id,
    s.nombre as segmento,
    count(distinct v.visitante_id) as visitantes,
    count(distinct ve.venta_id) as ventas,
    coalesce(sum(ve.monto_neto), 0) as ingresos
from {{ ref('stg_segmento_publico') }} s
left join {{ ref('stg_visitante') }} v
    on s.segmento_id = v.segmento_id
left join {{ ref('stg_venta') }} ve
    on v.visitante_id = ve.visitante_id
group by 1, 2
