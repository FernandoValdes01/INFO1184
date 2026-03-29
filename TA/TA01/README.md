# TA01 - Guia de documentacion

Este subproyecto tiene dos lineas de documentacion claramente separadas para evitar mezclar la resolucion academica de la tarea con la guia tecnica de implementacion.

## Documentos principales

### 1. Documento academico

Archivo:

- `informe.md`

Uso:

- Responder lo solicitado en la Tarea 01
- Presentar la parte teorica del caso
- Desarrollar el analisis estrategico y del modelo de datos
- Justificar conceptualmente la solucion propuesta

### 2. Documento tecnico

Archivo:

- `README_dbt.md`

Uso:

- Explicar como ejecutar el proyecto
- Guiar la migracion desde SQLite a PostgreSQL/Neon
- Documentar la validacion, transformacion con dbt y uso de Lightdash
- Servir como referencia operativa para trabajar el repositorio

### 3. Documento de apoyo y trazabilidad

Archivo:

- `doc.md`

Uso:

- Explicar la estructura documental
- Relacionar requerimientos con secciones del informe
- Mostrar donde esta cada parte tecnica del proyecto

## Flujo de lectura recomendado

1. Para corregir la tarea o revisar respuestas academicas: leer `informe.md`.
2. Para ejecutar el trabajo o entender la implementacion: leer `README_dbt.md`.
3. Para ubicar rapidamente archivos y criterios de separacion: leer `doc.md`.

## Flujo tecnico vigente

El trabajo tecnico del subproyecto sigue esta arquitectura:

1. `SQLite` como fuente historica local
2. `PostgreSQL/Neon` como base raw de destino
3. `dbt` como capa de transformacion
4. `Lightdash` como capa oficial de visualizacion

La visualizacion oficial del proyecto se implementa exclusivamente en `Lightdash` sobre los modelos analiticos construidos con `dbt`.
