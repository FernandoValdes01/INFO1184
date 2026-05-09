# TA04 - INFO1184

Analisis del dataset `Boston` usando la metodologia CRISP-DM y Analisis de Componentes Principales (PCA).

## Integrantes

- Vicente Rivera
- Juan Muñoz
- Fernando Valdes

Docente: Marcos Levano Humacto.

## Archivos principales

- `Tarea 4 INFO1184.pdf`: enunciado original de la tarea.
- `tarea4_boston_pca.R`: script R completo, simple y reproducible.
- `main.tex`: informe en LaTeX listo para compilar en latex.com/Overleaf.
- `TA_4_INFO1184_Informe.tex`: archivo auxiliar que carga `main.tex`.
- `figuras/`: graficos PDF generados por el script R.
- `salidas/`: tablas CSV generadas por el script R.

## Requisitos

- R instalado.
- Paquete `MASS`, usado para cargar `data("Boston")`.

El script fue escrito con R base y `MASS`. No requiere `dplyr`, `ggplot2`, `tidyr` ni paquetes externos adicionales.

## Como regenerar resultados

Desde la carpeta `TA04`, ejecutar:

```bash
Rscript tarea4_boston_pca.R
```

Esto crea o actualiza:

- `figuras/fig_01_matriz_correlaciones.pdf` a `figuras/fig_09_prediccion_crim.pdf`, incluyendo el biplot simplificado `fig_08_pca_biplot_simple.pdf`.
- `salidas/00_diccionario_variables.csv` a `salidas/15_respuestas_investigacion.csv`.

## Como compilar en latex.com / Overleaf

1. Crear un proyecto nuevo en latex.com/Overleaf.
2. Subir `main.tex`.
3. Subir la carpeta completa `figuras/` manteniendo el mismo nombre.
4. Opcionalmente subir `tarea4_boston_pca.R`, `salidas/` y este `README.md` como evidencia.
5. Seleccionar `main.tex` como archivo principal.
6. Usar compilador `pdfLaTeX`.
7. Compilar dos veces para actualizar referencias cruzadas de figuras y tablas.

No se necesita archivo `.bib`, porque las referencias estan integradas en el mismo `.tex`.

## Resultados clave

- Dataset: 506 observaciones y 14 variables originales.
- Valores faltantes: 0 en todas las variables.
- Outliers principales por IQR: `black` (77), `zn` (68) y `crim` (66).
- Suburbios mas baratos: IDs 399 y 406, ambos con `medv = 5`.
- Relacion `rm` vs `medv`: correlacion 0,695; pendiente 9,102.
- Efecto rio Charles: diferencia media de 6,346 miles de dolares a favor de zonas que limitan con el rio.
- Relacion `lstat` vs `medv`: correlacion -0,738; pendiente -0,950.
- PCA: los cinco primeros componentes explican 80,58% de la varianza.
- Prediccion de criminalidad: regresion con 5 componentes principales, `R2 log = 0,8119` y mejora de RMSE de 11,85% frente al promedio base.

## Nombre sugerido para entrega

Segun la pauta del curso, el PDF final debe seguir el formato:

```text
TA_4_INFO1184_Nombre_Apellido.pdf
```

Ejemplo:

```text
TA_4_INFO1184_Fernando_Valdes.pdf
```
