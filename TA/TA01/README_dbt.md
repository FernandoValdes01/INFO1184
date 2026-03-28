# TA01 - Documentacion tecnica y guia operativa

Este documento corresponde a la documentacion tecnica del subproyecto `TA01`. Su objetivo no es responder las preguntas teoricas de la tarea, sino explicar como esta implementado el trabajo y como debe ejecutarse.

La documentacion academica queda en `informe.md`. Aqui se documenta el flujo tecnico real del proyecto.

## 1. Objetivo tecnico del subproyecto

La solucion implementada para `TA01` trabaja con la siguiente arquitectura:

1. `SQLite` como fuente historica local de referencia
2. `PostgreSQL/Neon` como base raw de destino
3. `dbt` como capa de transformacion
4. `Lightdash` como herramienta oficial de visualizacion

La visualizacion oficial del proyecto se implementa en `Lightdash` a partir de los `marts` construidos por `dbt`.

## 2. Cuando usar este documento

Este archivo debe leerse cuando se necesita:

- entender el flujo tecnico del proyecto
- preparar variables de entorno
- migrar datos desde SQLite hacia PostgreSQL/Neon
- validar la carga
- ejecutar dbt
- conectar el proyecto con Lightdash

Si lo que se necesita es revisar la respuesta academica de la tarea, el documento correcto es `informe.md`.

## 3. Estructura tecnica relevante

| Recurso | Funcion |
| --- | --- |
| `ta01_feria_vinos.db` | Base historica local en SQLite |
| `generate_db.py` | Generacion de la base local de referencia |
| `sql/schema_postgres.sql` | Esquema raw para PostgreSQL/Neon |
| `scripts/migrate_to_neon.py` | Migracion de datos desde SQLite |
| `scripts/validate_neon.py` | Validacion automatica de la carga |
| `sql/validate_neon_data.sql` | Validacion manual con SQL |
| `dbt_project.yml` | Configuracion general de dbt |
| `models/staging/` | Modelos de staging sobre tablas raw |
| `models/marts/` | Modelos analiticos para Lightdash |
| `packages.yml` | Dependencias dbt del proyecto |

## 4. Ubicacion del proyecto

- Directorio del subproyecto: `TA/TA01`
- Archivo raiz de dbt: `TA/TA01/dbt_project.yml`
- En Lightdash se debe usar `Project directory path = /TA/TA01`

## 5. Flujo tecnico oficial

El procedimiento correcto de trabajo es el siguiente:

1. Usar `SQLite` solo como fuente local de referencia.
2. Crear el esquema raw en `PostgreSQL/Neon`.
3. Migrar las tablas desde SQLite hacia la base destino.
4. Validar que la migracion quedo consistente.
5. Ejecutar `dbt` para construir `stg_*` y `mart_*`.
6. Consumir los `marts` desde `Lightdash`.

## 6. Variables de entorno

Las credenciales no deben quedar versionadas en el repositorio. Se usa `.env.example` como referencia y `.env` como archivo local.

Variables soportadas:

- `NEON_DATABASE_URL` o `DATABASE_URL`
- `TA01_PG_SCHEMA`

Ejemplo minimo:

```env
NEON_DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
TA01_PG_SCHEMA=public
```

## 7. Paso a paso de ejecucion

### 7.1 Crear el esquema raw en PostgreSQL/Neon

Opcion directa con `psql`:

```bash
cd TA/TA01
psql "$NEON_DATABASE_URL" -v ON_ERROR_STOP=1 -v raw_schema=public -f sql/schema_postgres.sql
```

Opcion recomendada dentro del flujo completo:

```bash
cd TA/TA01
python3 scripts/migrate_to_neon.py
```

El script de migracion puede crear el esquema, exportar temporalmente los datos desde SQLite, truncar tablas destino y recargarlas en un orden seguro.

### 7.2 Migrar los datos desde SQLite

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

### 7.3 Validar la migracion

Validacion automatica:

```bash
cd TA/TA01
python3 scripts/validate_neon.py
```

Validacion SQL manual:

```bash
cd TA/TA01
psql "$NEON_DATABASE_URL" -v ON_ERROR_STOP=1 -v raw_schema=public -f sql/validate_neon_data.sql
```

La validacion revisa:

- conteo por tabla
- nulos en llaves primarias
- integridad referencial basica
- comparacion de conteos entre SQLite y PostgreSQL

### 7.4 Ejecutar dbt

Configuracion declarada en `dbt_project.yml`:

- `profile: info1184_ta01`
- `model-paths: ["models"]`
- `seed-paths: ["seeds"]`
- `macro-paths: ["macros"]`
- `test-paths: ["tests"]`
- `materialized: view` por defecto

Comandos de trabajo:

```bash
dbt deps --project-dir TA/TA01
dbt run --project-dir TA/TA01
dbt test --project-dir TA/TA01
```

## 8. Integracion con Lightdash

La configuracion esperada en Lightdash es:

1. Repositorio: este repositorio
2. `Project directory path = /TA/TA01`
3. Warehouse: `PostgreSQL/Neon`
4. Target schema: el mismo schema usado en la migracion raw y en dbt

Las `sources` de dbt usan `schema: "{{ target.schema }}"`. Por eso el schema configurado en el target de dbt debe coincidir con el schema real donde quedaron cargadas las tablas raw.

## 9. Diferencia entre base de referencia y base objetivo

La base `SQLite` definida por `schema.sql` se mantiene como referencia del prototipo original. La implementacion operativa actual usa `sql/schema_postgres.sql` porque la base objetivo del trabajo es `PostgreSQL/Neon`.

Los cambios principales son:

- `TEXT` de SQLite se mantiene como `text`
- algunas fechas pasan a `date`
- `venta.fecha_hora` pasa a `timestamp without time zone`
- montos y costos quedan tipados con `numeric`
- `visitante.acepta_contacto` pasa de `0/1` a `boolean`

Esta adaptacion permite que la capa raw quede mejor tipada y que `dbt` trabaje sobre tipos mas claros y estables.

## 10. Nota sobre carpetas declaradas por dbt

`seeds/`, `macros/` y `tests/` siguen declaradas en `dbt_project.yml` porque forman parte de la estructura esperada por dbt, aunque hoy no sean carpetas operativas del flujo. Se dejaron como convencion del proyecto y como espacio natural para crecimiento futuro.
