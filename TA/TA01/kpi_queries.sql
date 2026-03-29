PRAGMA foreign_keys = ON;

-- KPI 1: ingresos, ventas, visitantes y conversion de feria.
WITH compradores AS (
    SELECT DISTINCT visitante_id
    FROM venta
    WHERE visitante_id IS NOT NULL
)
SELECT
    (SELECT COUNT(*) FROM feria) AS total_ferias,
    (SELECT COUNT(*) FROM visitante) AS total_visitantes,
    (SELECT COUNT(*) FROM venta) AS total_ventas,
    (SELECT SUM(cantidad) FROM detalle_venta) AS botellas_vendidas,
    ROUND((SELECT SUM(monto_neto) FROM venta), 2) AS ingresos_totales,
    ROUND((SELECT AVG(monto_neto) FROM venta), 2) AS ticket_promedio,
    ROUND(
        100.0 * (SELECT COUNT(*) FROM compradores) / (SELECT COUNT(*) FROM visitante),
        2
    ) AS tasa_conversion_visitante
;

-- KPI 2: desempeno por feria.
WITH visitantes AS (
    SELECT feria_id, COUNT(*) AS visitantes
    FROM visitante
    GROUP BY feria_id
),
ventas AS (
    SELECT feria_id, COUNT(*) AS ventas, ROUND(SUM(monto_neto), 2) AS ingresos
    FROM venta
    GROUP BY feria_id
),
botellas AS (
    SELECT v.feria_id, SUM(d.cantidad) AS botellas
    FROM venta v
    JOIN detalle_venta d ON d.venta_id = v.venta_id
    GROUP BY v.feria_id
)
SELECT
    f.nombre AS feria,
    c.nombre AS ciudad,
    COALESCE(vis.visitantes, 0) AS visitantes,
    COALESCE(v.ventas, 0) AS ventas,
    COALESCE(v.ingresos, 0) AS ingresos,
    COALESCE(b.botellas, 0) AS botellas
FROM feria f
JOIN ciudad c ON c.ciudad_id = f.ciudad_id
LEFT JOIN visitantes vis ON vis.feria_id = f.feria_id
LEFT JOIN ventas v ON v.feria_id = f.feria_id
LEFT JOIN botellas b ON b.feria_id = f.feria_id
ORDER BY ingresos DESC
;

-- KPI 3: mix de vinos.
SELECT
    v.nombre AS vino,
    v.estilo,
    SUM(d.cantidad) AS botellas_vendidas,
    ROUND(SUM(d.subtotal), 2) AS ingresos_brutos
FROM vino v
JOIN detalle_venta d ON d.vino_id = v.vino_id
GROUP BY v.vino_id, v.nombre, v.estilo
ORDER BY botellas_vendidas DESC
;

-- KPI 4: ingreso por segmento.
SELECT
    s.nombre AS segmento,
    COUNT(DISTINCT vis.visitante_id) AS visitantes,
    COUNT(DISTINCT ve.venta_id) AS ventas,
    ROUND(COALESCE(SUM(ve.monto_neto), 0), 2) AS ingresos
FROM segmento_publico s
LEFT JOIN visitante vis ON vis.segmento_id = s.segmento_id
LEFT JOIN venta ve ON ve.visitante_id = vis.visitante_id
GROUP BY s.segmento_id, s.nombre
ORDER BY ingresos DESC, visitantes DESC
;

-- KPI 5: estado del inventario por feria y producto.
SELECT
    f.nombre AS feria,
    v.nombre AS vino,
    i.botellas_planificadas,
    i.botellas_recibidas,
    i.botellas_vendidas,
    i.stock_cierre
FROM inventario_feria i
JOIN feria f ON f.feria_id = i.feria_id
JOIN vino v ON v.vino_id = i.vino_id
ORDER BY f.feria_id, v.vino_id
;
