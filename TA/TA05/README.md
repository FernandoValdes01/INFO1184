# TA05 - INFO1184

Analisis de enfermedad cardiaca usando Python, clasificacion supervisada y clustering no supervisado.

## Integrantes

- Juan Munoz
- Vicente Rivera
- Fernando Valdes

Docente: Marcos Levano Humacto.

## Archivos principales

- `Tarea 5 INFO1184.pdf`: enunciado original de la tarea.
- `task.md`: definicion del proyecto, preguntas y metodologia esperada.
- `heart.csv`: dataset utilizado.
- `pyproject.toml`: dependencias del proyecto para `uv`.
- `main.py`: script Python reproducible.
- `main.tex`: informe en LaTeX.
- `figuras/`: graficos PDF generados por el script.
- `salidas/`: tablas CSV generadas por el script.

## Requisitos

- Python 3.10 o superior.
- `uv` instalado.

Las dependencias estan declaradas en `pyproject.toml` y se instalan automaticamente al ejecutar con `uv`.

## Como regenerar resultados

Desde la carpeta `TA05`, ejecutar:

```bash
uv run main.py
```

Esto crea o actualiza:

- `figuras/fig_01_distribucion_target.pdf` a `figuras/fig_09_perfiles_clusters.pdf`.
- `salidas/00_diccionario_variables.csv` a `salidas/11_respuestas_investigacion.csv`.

## Como compilar en LaTeX / Overleaf

1. Crear un proyecto nuevo en Overleaf o latex.com.
2. Subir `main.tex`.
3. Subir la carpeta completa `figuras/` manteniendo el mismo nombre.
4. Opcionalmente subir `main.py`, `pyproject.toml`, `heart.csv`, `salidas/` y este `README.md` como evidencia.
5. Seleccionar `main.tex` como archivo principal.
6. Usar compilador `pdfLaTeX`.
7. Compilar dos veces para actualizar referencias cruzadas.

## Resultados clave

- Dataset original: 1025 registros y 14 variables.
- Valores faltantes: 0.
- Duplicados exactos: 723.
- Dataset depurado para modelamiento: 302 registros.
- Variables mas asociadas a `target`: `exang`, `cp`, `oldpeak`, `thalach` y `ca`.
- Mejor modelo: KNN con `k=7`, accuracy 0,803 y F1-score 0,835.
- Clustering: K-Means selecciono `k=2` segun silueta, con separacion moderada-baja.
