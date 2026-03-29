# Estructura y trazabilidad documental - TA01

Este archivo normaliza la documentacion del subproyecto `TA01`, deja explicito que existen dos tipos de documentacion con objetivos distintos y fija a `Lightdash` como unica solucion oficial de visualizacion.

## 1. Tipos de documentacion del proyecto

### Documentacion academica

Corresponde al material que responde lo solicitado en la Tarea 01. Aqui deben quedar la parte teorica, el analisis del caso, la justificacion del modelo de datos y la explicacion conceptual del trabajo.

Documento principal:

- `informe.md`

### Documentacion tecnica

Corresponde al material que sirve para ejecutar, mantener y entender la implementacion del proyecto. Aqui deben quedar los pasos operativos, los archivos del flujo de datos, las herramientas usadas y las instrucciones para correr el trabajo.

Documento principal:

- `README_dbt.md`

## 2. Como debe leerse esta documentacion

Si el lector necesita revisar la entrega academica y verificar que la tarea esta respondida, debe partir por `informe.md`.

Si el lector necesita ejecutar la solucion, revisar el flujo SQLite -> PostgreSQL/Neon -> dbt -> Lightdash, o entender como se trabaja tecnicamente el proyecto, debe partir por `README_dbt.md`.

Este archivo `doc.md` funciona como puente entre ambos mundos: explica la separacion documental y deja trazabilidad entre los requerimientos y los archivos del repositorio.

## 3. Distribucion de contenidos

| Tipo de contenido | Documento correcto | Motivo |
| --- | --- | --- |
| Vision del negocio | `informe.md` | Es una respuesta conceptual solicitada por la tarea. |
| Foco estrategico | `informe.md` | Forma parte del analisis academico del caso. |
| Procesos estrategicos | `informe.md` | Responde directamente preguntas de estrategia y gestion. |
| Mapa estrategico | `informe.md` | Es parte del desarrollo teorico de la tarea. |
| Matriz 3M | `informe.md` | Corresponde a la resolucion academica del caso. |
| Identificacion de procesos, entidades y relaciones | `informe.md` | Explica el razonamiento del modelo de datos. |
| Esquema entidad relacion | `informe.md` | Presenta la solucion conceptual pedida en la tarea. |
| Flujo tecnico del proyecto | `README_dbt.md` | Sirve para guiar la implementacion real. |
| Migracion a Neon/PostgreSQL | `README_dbt.md` | Es una instruccion operativa. |
| Validacion de datos | `README_dbt.md` | Es parte del procedimiento tecnico. |
| Ejecucion de dbt | `README_dbt.md` | Es documentacion de uso del proyecto. |
| Integracion con Lightdash | `README_dbt.md` | Explica el despliegue del dashboard final. |

## 4. Trazabilidad de la entrega academica

### Parte I - Estrategia y cuadro de mando integral

| Requerimiento | Se responde en |
| --- | --- |
| Vision de la empresa | `informe.md` -> `Parte I` -> `1. Vision de la empresa` |
| Foco de la empresa | `informe.md` -> `Parte I` -> `2. Foco de la empresa` |
| Cinco procesos estrategicos por perspectiva | `informe.md` -> `Parte I` -> `3. Cinco procesos estrategicos por perspectiva` |
| Mapa estrategico | `informe.md` -> `Parte I` -> `4. Mapa estrategico del negocio` |
| Matriz 3M | `informe.md` -> `Parte I` -> `5. Matriz 3M` |

### Parte II - Analisis y modelo de datos

| Requerimiento | Se responde en |
| --- | --- |
| Procesos mas importantes del requerimiento | `informe.md` -> `Parte II` -> `1. Procesos mas importantes para el requerimiento` |
| Entidades identificadas | `informe.md` -> `Parte II` -> `2. Entidades identificadas` |
| Esquemas de datos y descripcion | `informe.md` -> `Parte II` -> `3. Esquemas de datos y descripcion` |
| Esquema entidad relacion | `informe.md` -> `Parte II` -> `4. Esquema entidad relacion` |
| Subconjunto de relaciones por proceso | `informe.md` -> `Parte II` -> `5. Subconjunto de relaciones por proceso` |

### Parte III - Implementacion y soporte tecnico

Esta parte tiene una doble lectura:

- `informe.md` explica la logica de implementacion y justifica el cambio de arquitectura.
- `README_dbt.md` explica como ejecutar esa implementacion en la practica.

| Necesidad | Documento recomendado |
| --- | --- |
| Entender por que se usa PostgreSQL/Neon, dbt y Lightdash | `informe.md` |
| Crear el esquema raw y migrar datos | `README_dbt.md` |
| Validar la carga | `README_dbt.md` |
| Ejecutar modelos dbt | `README_dbt.md` |
| Configurar Lightdash | `README_dbt.md` |

## 5. Archivos tecnicos principales

| Archivo | Rol tecnico |
| --- | --- |
| `README_dbt.md` | Guia operativa principal del proyecto |
| `sql/schema_postgres.sql` | DDL idempotente para PostgreSQL/Neon |
| `scripts/migrate_to_neon.py` | Migracion desde SQLite hacia PostgreSQL/Neon |
| `scripts/validate_neon.py` | Validacion automatica de la carga |
| `sql/validate_neon_data.sql` | Validacion manual por SQL |
| `dbt_project.yml` | Configuracion del proyecto dbt |
| `models/staging/sources.yml` | Declaracion de fuentes raw |
| `models/staging/stg_*.sql` | Capa de staging |
| `models/marts/mart_*.sql` | Capa analitica consumida por Lightdash |

## 6. Criterio de separacion adoptado

La regla aplicada para normalizar la documentacion es la siguiente:

- Si el contenido responde una pregunta de la Tarea 01, va en `informe.md`.
- Si el contenido sirve para ejecutar o mantener la solucion, va en `README_dbt.md`.
- Si el contenido sirve para ubicar al lector y explicar donde esta cada cosa, va en `doc.md`.
