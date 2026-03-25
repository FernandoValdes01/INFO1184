# TA01 dbt project

Este subproyecto convierte `TA/TA01` en un proyecto dbt minimo y compatible con Lightdash para el caso de analitica de ferias de vino.

## Ubicacion del proyecto

- `dbt_project.yml` esta en `TA/TA01/dbt_project.yml`
- El `Project directory path` que se debe configurar en Lightdash es exactamente `/TA/TA01`

## Objetivo de la estructura

- `models/staging/`: reflejo liviano de las tablas operacionales cargadas en PostgreSQL
- `models/marts/`: agregaciones simples para KPI y exploracion en Lightdash
- `seeds/`: reservado para futuros seeds; no se usa para credenciales ni para el warehouse final
- `macros/`: reservado para extensiones futuras
- `tests/`: reservado para tests singulares futuros

## Configuracion esperada en Lightdash

1. Conectar Lightdash a este repositorio.
2. Configurar `Project directory path = /TA/TA01`.
3. Configurar el warehouse PostgreSQL desde la UI de Lightdash.
4. Usar el profile `info1184_ta01` dentro de la ejecucion administrada por Lightdash.

## Credenciales

No se versionan credenciales, secretos, host, usuario, password ni `dbname` en este repositorio. La conexion al warehouse debe hacerse desde la UI de Lightdash.

## Flujo de datos esperado

1. Cargar las tablas operacionales base en PostgreSQL.
2. Ejecutar dbt sobre `TA/TA01`.
3. Exponer los modelos `mart_*` en Lightdash para construir el dashboard oficial.

## Nota sobre SQLite y el dashboard anterior

- `ta01_feria_vinos.db` y `generate_db.py` quedan como referencia historica/local del prototipo academico.
- La base objetivo del subproyecto es PostgreSQL.
- `dashboard.html` y `dashboard_data.js` quedaron descontinuados como dashboard operativo; la visualizacion oficial pasa a Lightdash.

## Nota sobre materializacion

El proyecto usa `materialized: view` por defecto. Se eligio `view` en vez de `materialized_view` para mantener compatibilidad minima y predecible con dbt Core 1.11 + Postgres + Lightdash sin depender de materializaciones adicionales o comportamiento especifico del adapter.
