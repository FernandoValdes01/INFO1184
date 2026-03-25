<# Trazabilidad de requerimientos - TA01

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

## Parte III - Evaluacion y esquema relacional

| Requerimiento | Donde se cumple |
| --- | --- |
| Crear una base de datos que responda al requerimiento | `schema.sql`, `generate_db.py`, `ta01_feria_vinos.db` |
| Definir el modelo fisico de la base de datos | `schema.sql` y `informe.md` -> `Parte III - Evaluacion y esquema relacional` -> `2. Modelo fisico de la base de datos` |
| Poblar la base de datos con 150 registros | `generate_db.py`, `ta01_feria_vinos.db`, `anexos/evidencia_bd.html`, `anexos/evidencia_bd.png` |
| Generar las relaciones propuestas en la parte II | `schema.sql` mediante `FOREIGN KEY`, mas validacion en `kpi_queries.sql` |
| Incluir evidencia en anexos | `informe.md` -> `Anexos`, `anexos/evidencia_bd.html`, `anexos/evidencia_bd.png`, `anexos/dashboard.png` |

## Parte IV - Visualizacion de datos

| Requerimiento | Donde se cumple |
| --- | --- |
| Construir tablero de mando y mostrar KPI | `dashboard.html`, `dashboard_data.js`, `exports/*.csv`, `informe.md` -> `Parte IV - Visualizacion de datos` |

## Archivos principales de la entrega

| Archivo | Rol |
| --- | --- |
| `informe.md` | Desarrollo completo de las partes I, II, III y IV |
| `doc.md` | Trazabilidad de todos los requerimientos |
| `schema.sql` | Modelo fisico y restricciones de la base |
| `generate_db.py` | Generacion automatica de la base, datos y archivos analiticos |
| `ta01_feria_vinos.db` | Base SQLite final |
| `kpi_queries.sql` | Consultas SQL de verificacion y KPI |
| `dashboard.html` | Tablero de mando local |
| `anexos/evidencia_bd.html` | Evidencia visual del modelo implementado |
