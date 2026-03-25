# TA01 analytics project

Este subproyecto define el flujo oficial de analitica para TA01 con la siguiente arquitectura:

1. Fuente historica local: `ta01_feria_vinos.db` y `generate_db.py`
2. Carga operativa: Neon / PostgreSQL
3. Transformacion: dbt en `TA/TA01`
4. Visualizacion final: Lightdash

El dashboard HTML/JS local ya no forma parte del flujo oficial.

## Ubicacion del proyecto

- `dbt_project.yml` esta en `TA/TA01/dbt_project.yml`
- En Lightdash se debe configurar `Project directory path = /TA/TA01`

## Flujo oficial del proyecto

1. Usar SQLite solo como fuente historica/local de referencia.
2. Crear el esquema raw en Neon/PostgreSQL.
3. Migrar las tablas raw desde SQLite a Neon/PostgreSQL.
4. Validar que los conteos y relaciones basicas quedaron correctos.
5. Ejecutar dbt para construir `stg_*` y `mart_*`.
6. Conectar Lightdash al proyecto dbt y construir el dashboard oficial.

## Estructura relevante

- `sql/schema_postgres.sql`: DDL PostgreSQL limpio e idempotente
- `sql/validate_neon_data.sql`: consultas de validacion en destino
- `scripts/migrate_to_neon.py`: carga desde SQLite hacia Neon/PostgreSQL
- `scripts/validate_neon.py`: validacion del destino
- `models/staging/`: capa staging dbt sobre tablas raw
- `models/marts/`: capa mart lista para Lightdash

## Variables de entorno

No se versionan credenciales. Usa `.env.example` como referencia y crea un `.env` local no versionado.

Variables soportadas:

- `NEON_DATABASE_URL` o `DATABASE_URL`
- `TA01_PG_SCHEMA`

Ejemplo minimo:

```env
NEON_DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
TA01_PG_SCHEMA=public
```

## Paso a paso

### 1. Crear el esquema en Neon/PostgreSQL

Opcion directa con `psql`:

```bash
cd TA/TA01
psql "$NEON_DATABASE_URL" -v ON_ERROR_STOP=1 -v raw_schema=public -f sql/schema_postgres.sql
```

Opcion recomendada dentro del flujo completo:

```bash
python3 scripts/migrate_to_neon.py
```

Ese script aplica el esquema si hace falta, exporta cada tabla desde SQLite a CSV temporal, trunca las tablas destino y recarga los datos en orden seguro.

### 2. Migrar los datos desde SQLite a Neon

```bash
cd TA/TA01
python3 scripts/migrate_to_neon.py
```

Opciones utiles:

```bash
python3 scripts/migrate_to_neon.py --schema analytics_raw
python3 scripts/migrate_to_neon.py --skip-schema
python3 scripts/migrate_to_neon.py --keep-temp-csv
```

### 3. Validar que la migracion quedo correcta

Validacion automatica con comparacion contra SQLite:

```bash
cd TA/TA01
python3 scripts/validate_neon.py
```

Validacion SQL directa:

```bash
psql "$NEON_DATABASE_URL" -v ON_ERROR_STOP=1 -v raw_schema=public -f sql/validate_neon_data.sql
```

La validacion revisa:

- conteo por tabla
- nulos en llaves primarias
- chequeos basicos de integridad referencial
- comparacion de conteos entre SQLite y PostgreSQL

### 4. Correr dbt

El proyecto usa:

- `profile: info1184_ta01`
- `model-paths: ["models"]`
- `seed-paths: ["seeds"]`
- `macro-paths: ["macros"]`
- `test-paths: ["tests"]`
- `materialized: view` por defecto

Una vez configurado el warehouse desde Lightdash o desde tu entorno dbt:

```bash
dbt deps --project-dir TA/TA01
dbt run --project-dir TA/TA01
dbt test --project-dir TA/TA01
```

## Integracion con Lightdash

Configura Lightdash asi:

1. Repositorio: este repositorio
2. `Project directory path = /TA/TA01`
3. Warehouse: Neon / PostgreSQL desde la UI de Lightdash
4. Target schema: el mismo schema usado en la migracion raw y en dbt

Las `sources` de dbt apuntan a `schema: "{{ target.schema }}"`, por lo que el schema configurado en el target de dbt debe coincidir con el schema real donde cargaste las tablas raw en Neon.

## Diferencias entre SQLite y PostgreSQL

`schema.sql` se mantiene como referencia del prototipo local, pero la migracion real usa `sql/schema_postgres.sql`. Los cambios principales son:

- `TEXT` de SQLite se mantiene como `text` en PostgreSQL
- fechas de `feria` y `visitante` pasan a `date`
- `venta.fecha_hora` pasa a `timestamp without time zone`
- montos y costos pasan a `numeric(p, s)` explicitos
- `visitante.acepta_contacto` pasa de entero `0/1` a `boolean`
- se mantiene la misma estructura logica, nombres de tablas y llaves

Se hizo asi para que la capa raw quede tipada correctamente en PostgreSQL y la capa dbt pueda trabajar sobre tipos mas claros y estables.

## Componentes obsoletos / deprecated

- `dashboard.html`
- `dashboard_data.js`
- `anexos/dashboard.png`

Esos archivos se conservan solo como referencia historica o evidencia academica. El dashboard oficial del proyecto debe construirse en Lightdash.

## Nota sobre carpetas vacias

`seeds/`, `macros/` y `tests/` no forman parte del flujo operativo actual y fueron removidas como placeholders vacios. Sus rutas siguen declaradas en `dbt_project.yml` porque son convenciones validas de dbt y podran reutilizarse si el proyecto crece, pero no se mantuvieron carpetas vacias artificiales en el repo.
