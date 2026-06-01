# TA05 - INFO1184

Análisis de enfermedad cardíaca usando Python, clasificación supervisada y clustering no supervisado. El trabajo sigue una metodología paso a paso y genera evidencias reproducibles para el informe en LaTeX.

## Integrantes

- Juan Muñoz
- Vicente Rivera
- Fernando Valdés

Docente: Marcos Lévano Humacto.

## Estructura del proyecto

```text
TA05/
├── heart.csv
├── main.py
├── main.tex
├── pyproject.toml
├── uv.lock
├── README.md
├── task.md
├── figuras/
└── salidas/
```

## Archivos principales

- `Tarea 5 INFO1184.pdf`: enunciado original de la tarea.
- `task.md`: descripción del proyecto, preguntas y metodología esperada.
- `heart.csv`: dataset utilizado. Debe llamarse exactamente `heart.csv` y estar en esta carpeta.
- `pyproject.toml`: dependencias del proyecto para `uv`.
- `main.py`: script Python reproducible.
- `main.tex`: informe académico en LaTeX.
- `figuras/`: gráficos PDF generados por el script.
- `salidas/`: tablas CSV generadas por el script.

## Requisitos

- Python 3.10 o superior.
- `uv` instalado.
- Acceso al repositorio o carpeta del grupo para revisión docente.

Las dependencias están declaradas en `pyproject.toml` y se sincronizan con `uv`.

## Cómo regenerar resultados

Desde la carpeta `TA05`, ejecutar:

```bash
uv sync
uv run python main.py
```

Esto crea o actualiza:

- `figuras/fig_01_distribucion_target.pdf` a `figuras/fig_09_perfiles_clusters.pdf`.
- `salidas/00_diccionario_variables.csv` a `salidas/14_importancia_permutacion_modelo.csv`.

## Cómo compilar el informe

Opción recomendada en Overleaf:

1. Crear un proyecto nuevo en Overleaf.
2. Subir `main.tex`.
3. Subir la carpeta completa `figuras/` manteniendo el mismo nombre.
4. Opcionalmente subir `main.py`, `pyproject.toml`, `heart.csv`, `salidas/` y este `README.md` como evidencia.
5. Seleccionar `main.tex` como archivo principal.
6. Usar compilador `pdfLaTeX`.
7. Compilar dos veces para actualizar referencias cruzadas.

También puede compilarse localmente con una distribución de LaTeX como TeX Live o MiKTeX.

## Resultados clave

- Dataset original: 1025 registros y 14 variables.
- Valores faltantes: 0.
- Duplicados exactos: 723.
- Dataset depurado para modelamiento: 302 registros.
- Variables con mayor asociación exploratoria con `target`: `exang`, `cp`, `oldpeak`, `thalach` y `ca`.
- Mejor modelo en el split final: KNN con `k=9`, accuracy 0,803 y F1-score 0,832.
- Validación cruzada: regresión logística y KNN tuvieron desempeños promedio muy cercanos.
- Clustering: K-Means seleccionó `k=2` según silueta, con separación limitada.

## Nota metodológica

Los resultados son exploratorios y no constituyen diagnóstico médico. La eliminación de duplicados fue necesaria para reducir fuga de información entre entrenamiento y prueba, pero también redujo el tamaño efectivo del dataset, por lo que las métricas deben interpretarse con prudencia.
