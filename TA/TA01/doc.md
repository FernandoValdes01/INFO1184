# Trazabilidad de requerimientos - TA01

## Estado final del subproyecto

El subproyecto TA01 queda alineado al siguiente flujo oficial:

1. SQLite local como referencia historica
2. Neon / PostgreSQL como base raw definitiva
3. dbt como capa de transformacion
4. Lightdash como dashboard oficial

## Parte I - Estrategia y cuadro de mando integral

| Requerimiento | Donde se cumple |
| --- | --- |
| Describir la vision de la empresa | `informe.md` -> `Parte I - Estrategia y cuadro de mando integral` -> `1. Vision de la empresa` |
| Describir el foco de la empresa | `informe.md` -> `Parte I - Estrategia y cuadro de mando integral` -> `2. Foco de la empresa` |
| Analizar, discutir y elaborar cinco procesos estrategicos segun cinco perspectivas | `informe.md` -> `Parte I - Estrategia y cuadro de mando integral` -> `3. Cinco procesos estrategicos por perspectiva` |
| Construir mapa estrategico con perspectivas y flujos | `informe.md` -> `Parte I - Estrategia y cuadro de mando integral` -> `4. Mapa estrategico del negocio` |
| Elaborar matriz 3M con al menos tres medidas, tres metas y tres medios por perspectiva | `informe.md` -> `Parte I - Estrategia y cuadro de mando integral` -> `5. Matriz 3M` |

## Parte II - Analisis y modelo de datos

| Requerimiento | Donde se cumple |
| --- | --- |
| Identificar los procesos mas importantes para el requerimiento | `informe.md` -> `Parte II - Analisis y modelo de datos` -> `1. Procesos mas importantes para el requerimiento` |
| Identificar las entidades | `informe.md` -> `Parte II - Analisis y modelo de datos` -> `2. Entidades identificadas` |
| Describir los esquemas de los datos | `informe.md` -> `Parte II - Analisis y modelo de datos` -> `3. Esquemas de datos y descripcion` |
| Crear esquema entidad relacion con cardinalidades y atributos | `informe.md` -> `Parte II - Analisis y modelo de datos` -> `4. Esquema entidad relacion` |
| Identificar el subconjunto de relaciones necesario para cada proceso | `informe.md` -> `Parte II - Analisis y modelo de datos` -> `5. Subconjunto de relaciones por proceso` |

## Parte III - Implementacion real hacia Neon / PostgreSQL

| Requerimiento tecnico | Donde se cumple |
| --- | --- |
| DDL PostgreSQL limpio e idempotente | `sql/schema_postgres.sql` |
| Carga real desde SQLite a Neon/PostgreSQL | `scripts/migrate_to_neon.py` |
| Validacion de datos cargados | `scripts/validate_neon.py`, `sql/validate_neon_data.sql` |
| Variables de entorno sin credenciales versionadas | `.env.example`, `.gitignore`, `README_dbt.md` |
| Proyecto dbt compatible con Lightdash | `dbt_project.yml`, `packages.yml`, `models/staging/`, `models/marts/` |
| Sources dbt alineadas a tablas reales en Neon | `models/staging/sources.yml` |
| Staging models sobre tablas raw | `models/staging/stg_*.sql` |
| Marts listos para Lightdash | `models/marts/mart_*.sql` |
| Documentacion de ejecucion completa | `README_dbt.md` |

## Parte IV - Visualizacion final

| Requerimiento tecnico | Donde se cumple |
| --- | --- |
| Dashboard oficial en Lightdash | `README_dbt.md`, `informe.md`, `README.md` |
| Dashboard HTML/JS local descontinuado | `dashboard.html`, `dashboard_data.js` |
| Evidencia historica conservada sin usarla como flujo oficial | `anexos/dashboard.png` |

## Flujo oficial del proyecto

| Capa | Activo principal |
| --- | --- |
| Fuente local historica | `ta01_feria_vinos.db`, `generate_db.py` |
| Carga a Neon | `sql/schema_postgres.sql`, `scripts/migrate_to_neon.py` |
| Validacion | `scripts/validate_neon.py`, `sql/validate_neon_data.sql` |
| Transformacion | `dbt_project.yml`, `models/staging/`, `models/marts/` |
| Dashboard | Lightdash con `Project directory path = /TA/TA01` |

## Componentes obsoletos / deprecated

| Componente | Estado |
| --- | --- |
| `dashboard.html` | Conservado solo como aviso de deprecacion |
| `dashboard_data.js` | Conservado solo como stub de deprecacion |
| `anexos/dashboard.png` | Evidencia historica, no flujo vigente |

## Archivos principales

| Archivo | Rol |
| --- | --- |
| `README_dbt.md` | Guia operativa completa de migracion y uso |
| `sql/schema_postgres.sql` | Esquema raw definitivo para Neon/PostgreSQL |
| `scripts/migrate_to_neon.py` | Carga idempotente desde SQLite |
| `scripts/validate_neon.py` | Validacion de destino |
| `sql/validate_neon_data.sql` | Queries manuales de validacion |
| `dbt_project.yml` | Configuracion raiz del proyecto dbt |
| `models/staging/sources.yml` | Sources alineadas a Neon |
| `models/marts/mart_*.sql` | Vistas analiticas para Lightdash |
