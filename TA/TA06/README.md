# TA06 - INFO1184

Analisis de Neurofibromatosis Tipo 1 usando arbol de decision para clasificar casos esporadicos y familiares. El trabajo sigue CRISP-DM y genera figuras reproducibles para el informe en LaTeX.

## Integrantes

- Juan Muñoz
- Vicente Rivera
- Fernando Valdés

Docente: Marcos Lévano Humacto.

## Estructura

```text
TA06/
├── informe.tex
├── informe.pdf
├── nf1_analisis.py
├── dataset-uci.xlsx
├── figuras/
│   ├── arbol_decision.png
│   ├── matriz_confusion.png
│   ├── curva_roc.png
│   ├── importancia_features.png
│   ├── distribucion_clases.png
│   └── prevalencia_sintomas.png
└── README.md
```

## Requisitos

- Python 3.10 o superior.
- Dependencias: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `openpyxl`.
- Para compilar el PDF localmente: `pdflatex` incluido en TeX Live o MiKTeX.

Si usas `uv`, no es necesario crear un entorno manual.

## Regenerar Analisis Y Figuras

Desde `TA06/`, ejecutar:

```bash
uv run --with pandas --with numpy --with scikit-learn --with matplotlib --with seaborn --with openpyxl python nf1_analisis.py
```

El script carga `dataset-uci.xlsx`, hoja `Dataset`, entrena el arbol de decision y actualiza automaticamente las figuras en `figuras/`.

## Compilar Informe

Desde `TA06/`, ejecutar dos veces:

```bash
pdflatex -interaction=nonstopmode informe.tex
pdflatex -interaction=nonstopmode informe.tex
```

Si `pdflatex` no esta instalado localmente, se puede compilar en Overleaf subiendo `informe.tex` y la carpeta `figuras/` completa.

## Resultados Clave

- Registros analizados: 296.
- Objetivo: `Case Type`, donde `0 = esporadico` y `1 = familiar`.
- Casos esporadicos: 161.
- Casos familiares: 135.
- Pacientes con tumores: 82.
- Faltantes: solo en variables de edad.
- Modelo: arbol de decision con Gini, profundidad maxima 3, minimo de 15 muestras por hoja y clases balanceadas.
- Test: accuracy 0,473; precision 0,447; recall 0,618; F1 0,519; AUC-ROC 0,521.
- Validacion cruzada: accuracy media 0,524; F1 media 0,549; AUC-ROC media 0,528.
- Variables mas relevantes: edad al primer diagnostico, nodulos de Lisch, glioma optico y edad de la madre.

## Nota Metodologica

Los resultados son exploratorios y no constituyen diagnostico medico. El rendimiento predictivo es limitado, por lo que el arbol se interpreta principalmente como herramienta academica e interpretable. Para mejorar desempeno se podrian evaluar Random Forest, XGBoost o Gradient Boosting con validacion externa.
