# Trazabilidad de requerimientos - TA01

## Alcance actual del subproyecto

El contenido academico del caso se mantiene, pero la implementacion tecnica de analitica fue reorientada para un flujo objetivo con:

- PostgreSQL como base de datos objetivo
- dbt como capa de transformacion
- Lightdash como capa oficial de dashboard

La base `SQLite` y el dashboard HTML/JS quedan solo como referencia historica/local.

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

## Parte III - Implementacion tecnica alineada a PostgreSQL + dbt

| Requerimiento tecnico | Donde se cumple |
| --- | --- |
| Crear un proyecto dbt valido dentro de `TA/TA01` | `dbt_project.yml`, `packages.yml`, `README_dbt.md` |
| Dejar compatibilidad minima con dbt Core 1.11 | `dbt_project.yml` -> `require-dbt-version` |
| Definir rutas relativas correctas del proyecto | `dbt_project.yml` |
| Crear estructura `models`, `seeds`, `macros`, `tests` | `TA/TA01/models/`, `TA/TA01/seeds/`, `TA/TA01/macros/`, `TA/TA01/tests/` |
| Definir sources en base a las tablas reales de `schema.sql` | `models/staging/sources.yml` |
| Crear staging models `stg_*` por tabla base importante | `models/staging/stg_*.sql` |
| Documentar modelos y columnas con tests basicos | `models/staging/staging.yml`, `models/marts/marts.yml` |
| Crear marts simples a partir de los KPI existentes | `models/marts/mart_kpi_resumen.sql`, `models/marts/mart_ventas_por_feria.sql`, `models/marts/mart_ingresos_por_segmento.sql`, `models/marts/mart_mix_vinos.sql`, `models/marts/mart_estado_inventario.sql` |
| No versionar credenciales ni secretos | `README_dbt.md`, `.gitignore` |
| Preparar el proyecto para Lightdash | `README_dbt.md` y `dbt_project.yml` |

## Parte IV - Dashboard oficial y descontinuacion del dashboard local

| Requerimiento tecnico | Donde se cumple |
| --- | --- |
| Declarar que el dashboard oficial se construira en Lightdash | `README_dbt.md`, `informe.md`, `README.md` |
| Descontinuar el dashboard HTML/JS local | `dashboard.html`, `dashboard_data.js` |
| Mantener evidencia historica sin tratarla como dashboard vigente | `anexos/dashboard.png` y menciones en `README_dbt.md` / `informe.md` |

## Nota de migracion desde SQLite a PostgreSQL

| Tema | Estado final |
| --- | --- |
| Base local historica | `ta01_feria_vinos.db` y `generate_db.py` quedan como referencia local |
| Base objetivo | PostgreSQL |
| Transformacion | dbt en `TA/TA01` |
| Dashboard oficial | Lightdash |
| Path de proyecto en Lightdash | `/TA/TA01` |

## Archivos principales

| Archivo | Rol |
| --- | --- |
| `dbt_project.yml` | Configuracion raiz del proyecto dbt |
| `packages.yml` | Archivo minimo para `dbt deps` |
| `README_dbt.md` | Instrucciones para Lightdash y nota de migracion |
| `models/staging/sources.yml` | Definicion de sources |
| `models/staging/stg_*.sql` | Modelos staging por tabla base |
| `models/marts/mart_*.sql` | Marts simples para KPI y exploracion |
| `models/staging/staging.yml` | Documentacion y tests de staging |
| `models/marts/marts.yml` | Documentacion y tests de marts |
| `informe.md` | Informe academico actualizado al nuevo flujo tecnico |
| `generate_db.py` | Prototipo SQLite historico y exportador local |
