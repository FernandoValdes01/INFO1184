select
    (select count(*) from {{ ref('stg_feria') }}) as total_ferias,
    (select count(*) from {{ ref('stg_visitante') }}) as total_visitantes,
    (select count(*) from {{ ref('stg_venta') }}) as total_ventas,
    (select coalesce(sum(cantidad), 0) from {{ ref('stg_detalle_venta') }}) as botellas_vendidas,
    (select coalesce(sum(monto_neto), 0) from {{ ref('stg_venta') }}) as ingresos_totales,
    (select avg(monto_neto) from {{ ref('stg_venta') }}) as ticket_promedio,
    case
        when (select count(*) from {{ ref('stg_visitante') }}) = 0 then 0
        else round(
            100.0 * (
                select count(distinct visitante_id)
                from {{ ref('stg_venta') }}
                where visitante_id is not null
            ) / (select count(*) from {{ ref('stg_visitante') }}),
            2
        )
    end as tasa_conversion_visitante,
    case
        when (select count(*) from {{ ref('stg_visitante') }}) = 0 then 0
        else round(
            100.0 * (
                select count(*)
                from {{ ref('stg_visitante') }}
                where acepta_contacto
            ) / (select count(*) from {{ ref('stg_visitante') }}),
            2
        )
    end as tasa_optin_contacto
