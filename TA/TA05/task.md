# Análisis de Enfermedad Cardíaca mediante Técnicas de Data Science

## Descripción del proyecto

Este proyecto corresponde a la Tarea 5 de la asignatura INFO1184 - Inteligencia de Negocios.

El objetivo principal es analizar un conjunto de datos relacionado con la salud, específicamente sobre enfermedad cardíaca, utilizando técnicas de análisis de datos en Python. El estudio busca identificar patrones, relaciones entre variables clínicas y demográficas, y evaluar si es posible predecir la presencia de enfermedad cardíaca en pacientes.

El dataset utilizado corresponde a Heart Disease Dataset, disponible en Kaggle:

https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset

Este conjunto de datos contiene información médica de pacientes, incluyendo edad, sexo, presión arterial, colesterol, frecuencia cardíaca máxima, entre otras variables. Además, posee una variable objetivo llamada `target`, que indica si el paciente presenta o no enfermedad cardíaca.

---

## Pregunta de investigación principal

¿Qué variables clínicas y demográficas se relacionan más con la presencia de enfermedad cardíaca en los pacientes del dataset?

---

## Preguntas de investigación secundarias

1. ¿Qué diferencias existen entre pacientes con y sin enfermedad cardíaca según edad, colesterol, presión arterial y frecuencia cardíaca máxima?

2. ¿Qué variables parecen tener mayor relación con la presencia de enfermedad cardíaca?

3. ¿Es posible predecir la presencia de enfermedad cardíaca utilizando variables clínicas del paciente?

4. ¿Se pueden identificar perfiles de pacientes mediante técnicas de clustering?

5. ¿Qué tan bien se comportan modelos de clasificación simples para detectar pacientes con posible enfermedad cardíaca?

---

## Objetivo general

Analizar el dataset de enfermedad cardíaca mediante técnicas de análisis exploratorio, visualización, clasificación y clustering, con el fin de identificar patrones relevantes asociados a la presencia de enfermedad cardíaca.

---

## Objetivos específicos

- Realizar una limpieza y revisión inicial del dataset.
- Analizar estadísticamente las variables clínicas y demográficas.
- Visualizar la distribución de las variables más relevantes.
- Comparar pacientes con y sin enfermedad cardíaca.
- Aplicar técnicas de clasificación para predecir la variable `target`.
- Aplicar clustering para identificar posibles perfiles de pacientes.
- Interpretar los resultados obtenidos desde una perspectiva de salud y análisis de datos.

---

## Descripción del dataset

El dataset contiene registros de pacientes y variables asociadas a su condición cardiovascular.

Algunas de las variables principales son:

| Variable | Descripción |
|---|---|
| age | Edad del paciente |
| sex | Sexo del paciente |
| cp | Tipo de dolor en el pecho |
| trestbps | Presión arterial en reposo |
| chol | Colesterol sérico |
| fbs | Glucosa en ayunas mayor a 120 mg/dl |
| restecg | Resultado electrocardiográfico en reposo |
| thalach | Frecuencia cardíaca máxima alcanzada |
| exang | Angina inducida por ejercicio |
| oldpeak | Depresión del ST inducida por ejercicio |
| slope | Pendiente del segmento ST |
| ca | Número de vasos principales coloreados por fluoroscopía |
| thal | Resultado de prueba thal |
| target | Presencia de enfermedad cardíaca |

La variable `target` representa la clase principal del análisis:

- `0`: No presenta enfermedad cardíaca.
- `1`: Presenta enfermedad cardíaca.

---

## Metodología

La metodología utilizada en el proyecto sigue una estructura básica de análisis de datos:

### 1. Carga de datos

Se importa el dataset en Python utilizando la librería `pandas`.

### 2. Exploración inicial

Se revisan:

- Cantidad de filas y columnas.
- Tipos de datos.
- Valores nulos.
- Valores duplicados.
- Estadísticas descriptivas.

### 3. Limpieza de datos

Se realiza una revisión de posibles problemas en el dataset, tales como:

- Datos faltantes.
- Registros duplicados.
- Variables mal codificadas.
- Valores atípicos.

### 4. Análisis exploratorio de datos

Se analizan las variables mediante:

- Tablas descriptivas.
- Histogramas.
- Boxplots.
- Gráficos de barras.
- Matriz de correlación.

### 5. Visualización de patrones

Se comparan variables relevantes según la presencia o ausencia de enfermedad cardíaca.

Ejemplos:

- Edad vs enfermedad cardíaca.
- Colesterol vs enfermedad cardíaca.
- Presión arterial vs enfermedad cardíaca.
- Frecuencia cardíaca máxima vs enfermedad cardíaca.

### 6. Modelo de clasificación

Se aplican modelos de clasificación para predecir la variable `target`.

Modelos sugeridos:

- K-Nearest Neighbors
- Regresión logística
- Árbol de decisión

Se evalúan los modelos mediante:

- Accuracy
- Matriz de confusión
- Precision
- Recall
- F1-score

### 7. Clustering

Se aplica K-Means para segmentar pacientes según sus características clínicas.

Pasos considerados:

- Selección de variables numéricas.
- Escalamiento de datos con `StandardScaler`.
- Método del codo para estimar el número de clusters.
- Aplicación de K-Means.
- Interpretación de los grupos obtenidos.

### 8. Interpretación de resultados

Se interpretan los resultados obtenidos en función de las preguntas de investigación planteadas.

---

## Tecnologías utilizadas

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Jupyter Notebook / Google Colab
- LaTeX para el informe final

---

## Estructura del proyecto

```txt
proyecto-heart-disease/
│
├── data/
│   └── heart.csv
│
├── notebooks/
│   └── analisis_heart_disease.ipynb
│
├── src/
│   └── analisis.py
│
├── img/
│   ├── matriz_correlacion.png
│   ├── distribucion_edad.png
│   ├── matriz_confusion.png
│   └── clusters_kmeans.png
│
├── informe/
│   └── informe_heart_disease.pdf
│
├── README.md
└── requirements.txt