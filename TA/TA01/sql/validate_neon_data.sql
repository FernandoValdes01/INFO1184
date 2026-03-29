\if :{?raw_schema}
\else
\set raw_schema public
\endif

\echo '== Row counts =='
SELECT 'region' AS tabla, COUNT(*) AS registros FROM :"raw_schema".region
UNION ALL
SELECT 'ciudad', COUNT(*) FROM :"raw_schema".ciudad
UNION ALL
SELECT 'segmento_publico', COUNT(*) FROM :"raw_schema".segmento_publico
UNION ALL
SELECT 'vino', COUNT(*) FROM :"raw_schema".vino
UNION ALL
SELECT 'alianza', COUNT(*) FROM :"raw_schema".alianza
UNION ALL
SELECT 'feria', COUNT(*) FROM :"raw_schema".feria
UNION ALL
SELECT 'feria_alianza', COUNT(*) FROM :"raw_schema".feria_alianza
UNION ALL
SELECT 'stand', COUNT(*) FROM :"raw_schema".stand
UNION ALL
SELECT 'inventario_feria', COUNT(*) FROM :"raw_schema".inventario_feria
UNION ALL
SELECT 'visitante', COUNT(*) FROM :"raw_schema".visitante
UNION ALL
SELECT 'degustacion', COUNT(*) FROM :"raw_schema".degustacion
UNION ALL
SELECT 'venta', COUNT(*) FROM :"raw_schema".venta
UNION ALL
SELECT 'detalle_venta', COUNT(*) FROM :"raw_schema".detalle_venta
ORDER BY 1;

\echo '== Primary key null checks =='
SELECT 'region.region_id' AS check_name, COUNT(*) AS invalid_rows FROM :"raw_schema".region WHERE region_id IS NULL
UNION ALL
SELECT 'ciudad.ciudad_id', COUNT(*) FROM :"raw_schema".ciudad WHERE ciudad_id IS NULL
UNION ALL
SELECT 'segmento_publico.segmento_id', COUNT(*) FROM :"raw_schema".segmento_publico WHERE segmento_id IS NULL
UNION ALL
SELECT 'vino.vino_id', COUNT(*) FROM :"raw_schema".vino WHERE vino_id IS NULL
UNION ALL
SELECT 'alianza.alianza_id', COUNT(*) FROM :"raw_schema".alianza WHERE alianza_id IS NULL
UNION ALL
SELECT 'feria.feria_id', COUNT(*) FROM :"raw_schema".feria WHERE feria_id IS NULL
UNION ALL
SELECT 'stand.stand_id', COUNT(*) FROM :"raw_schema".stand WHERE stand_id IS NULL
UNION ALL
SELECT 'inventario_feria.inventario_id', COUNT(*) FROM :"raw_schema".inventario_feria WHERE inventario_id IS NULL
UNION ALL
SELECT 'visitante.visitante_id', COUNT(*) FROM :"raw_schema".visitante WHERE visitante_id IS NULL
UNION ALL
SELECT 'degustacion.degustacion_id', COUNT(*) FROM :"raw_schema".degustacion WHERE degustacion_id IS NULL
UNION ALL
SELECT 'venta.venta_id', COUNT(*) FROM :"raw_schema".venta WHERE venta_id IS NULL
UNION ALL
SELECT 'detalle_venta.detalle_venta_id', COUNT(*) FROM :"raw_schema".detalle_venta WHERE detalle_venta_id IS NULL
ORDER BY 1;

\echo '== Referential integrity spot checks =='
SELECT
    COUNT(*) AS visitantes_sin_feria
FROM :"raw_schema".visitante v
LEFT JOIN :"raw_schema".feria f ON v.feria_id = f.feria_id
WHERE f.feria_id IS NULL;

SELECT
    COUNT(*) AS ventas_sin_stand
FROM :"raw_schema".venta v
LEFT JOIN :"raw_schema".stand s ON v.stand_id = s.stand_id
WHERE s.stand_id IS NULL;

SELECT
    COUNT(*) AS detalles_sin_venta
FROM :"raw_schema".detalle_venta d
LEFT JOIN :"raw_schema".venta v ON d.venta_id = v.venta_id
WHERE v.venta_id IS NULL;
