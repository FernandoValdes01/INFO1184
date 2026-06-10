# Árboles de Decisión para Problemas de Clasificación

## ¿Qué es un Árbol de Decisión?

Un **árbol de decisión** es un modelo de aprendizaje supervisado que representa decisiones y sus posibles consecuencias en forma de árbol. En problemas de **clasificación**, se utiliza para predecir a qué categoría o clase pertenece una nueva observación, basándose en un conjunto de atributos o características.

Su estructura es jerárquica y puede leerse como una serie de preguntas anidadas del tipo "¿El valor de X es mayor que Y?", hasta llegar a una respuesta final (la clase predicha).

---

## Estructura del Árbol

```
                  [Nodo Raíz]
                 /           \
         [Nodo Interno]   [Nodo Interno]
           /     \            /     \
        [Hoja]  [Hoja]    [Hoja]  [Hoja]
        Clase A  Clase B  Clase B  Clase C
```

| Componente | Descripción |
|---|---|
| **Nodo Raíz** | El atributo más importante; primera división del conjunto de datos |
| **Nodos Internos** | Condiciones o preguntas sobre un atributo |
| **Ramas** | Resultados posibles de cada condición (Sí / No, o rangos) |
| **Nodos Hoja** | Clase final asignada a las observaciones que llegan a ese punto |

---

## ¿Cómo Aprende un Árbol de Decisión?

El algoritmo construye el árbol de forma recursiva, dividiendo el conjunto de datos en subconjuntos más puros en términos de clase. Para elegir el mejor atributo en cada división, utiliza **criterios de impureza**:

### 1. Índice de Gini (usado en CART)

Mide la probabilidad de clasificar incorrectamente un elemento elegido al azar.

$$Gini = 1 - \sum_{i=1}^{k} p_i^2$$

donde $p_i$ es la proporción de elementos de la clase $i$ en el nodo. Un Gini de **0** significa un nodo perfectamente puro (solo una clase).

### 2. Entropía e Información Ganada (usada en ID3 / C4.5)

La **entropía** mide el desorden o mezcla de clases en un nodo:

$$H = -\sum_{i=1}^{k} p_i \log_2(p_i)$$

La **ganancia de información** mide cuánto reduce la entropía al dividir por un atributo:

$$IG = H(\text{padre}) - \sum_j \frac{|hijo_j|}{|padre|} \cdot H(hijo_j)$$

Se elige el atributo que **maximiza** la ganancia de información.

### 3. Reducción de Varianza

Utilizado principalmente para variables continuas; minimiza la varianza dentro de cada subconjunto resultante.

---

## Algoritmos Principales

| Algoritmo | Criterio | Tipo de Variables | Características |
|---|---|---|---|
| **ID3** | Ganancia de información | Categóricas | Simple, no maneja valores nulos |
| **C4.5** | Ratio de ganancia | Categóricas y continuas | Mejora de ID3, maneja valores faltantes |
| **CART** | Índice de Gini | Ambas | Genera árboles binarios, muy usado en sklearn |
| **CHAID** | Chi-cuadrado | Categóricas | Multirama, útil en marketing |

---

## Proceso Paso a Paso

1. **Cargar el dataset** con las características (X) y las etiquetas de clase (y).
2. **Calcular la impureza** del nodo actual (Gini o Entropía).
3. **Evaluar cada atributo** y su punto de corte posible.
4. **Seleccionar el mejor atributo** que minimice la impureza (o maximice la ganancia).
5. **Dividir el nodo** en subnodos según ese atributo.
6. **Repetir recursivamente** para cada subnodo.
7. **Detener** cuando se cumpla un criterio de parada (profundidad máxima, mínimo de muestras, nodo puro).

---

## Ventajas y Desventajas

### ✅ Ventajas

- **Interpretable y visual**: se puede graficar y explicar fácilmente.
- **No requiere normalización** de los datos.
- **Maneja variables categóricas y numéricas** sin transformaciones previas.
- **Identifica automáticamente** las características más importantes.
- **Rápido de entrenar** en conjuntos de datos medianos.

### ❌ Desventajas

- **Sobreajuste (overfitting)**: tiende a memorizar el conjunto de entrenamiento si no se poda.
- **Inestabilidad**: pequeños cambios en los datos pueden generar árboles muy diferentes.
- **Sesgo hacia atributos con muchos valores**: puede favorecer variables con alta cardinalidad.
- **Fronteras de decisión rectangulares**: no captura bien relaciones diagonales o no lineales complejas.

---

## Técnicas para Controlar el Sobreajuste

### Prepoda (Early Stopping)

Parámetros que limitan el crecimiento del árbol durante el entrenamiento:

- `max_depth`: profundidad máxima del árbol.
- `min_samples_split`: mínimo de muestras para dividir un nodo.
- `min_samples_leaf`: mínimo de muestras en un nodo hoja.

### Postpoda (Pruning)

Después de construir el árbol completo, se eliminan ramas que no mejoran la generalización. La técnica más común es el **Reduced Error Pruning** y el **Cost Complexity Pruning** (parámetro `ccp_alpha` en scikit-learn).

---

## Implementación en Python (scikit-learn)

```python
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt

# 1. Dividir datos
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 2. Crear y entrenar el modelo
clf = DecisionTreeClassifier(
    criterion='gini',       # 'gini' o 'entropy'
    max_depth=5,            # Controla sobreajuste
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42
)
clf.fit(X_train, y_train)

# 3. Evaluar
y_pred = clf.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred))

# 4. Visualizar el árbol
plt.figure(figsize=(20, 10))
plot_tree(clf, feature_names=feature_names, class_names=class_names, filled=True)
plt.title("Árbol de Decisión")
plt.show()
```

---

## Métricas de Evaluación para Clasificación

| Métrica | Descripción |
|---|---|
| **Accuracy** | Proporción de predicciones correctas |
| **Precisión** | De los predichos como clase X, ¿cuántos lo son realmente? |
| **Recall (Sensibilidad)** | De los reales de clase X, ¿cuántos fueron detectados? |
| **F1-Score** | Media armónica entre Precisión y Recall |
| **Matriz de Confusión** | Tabla que muestra TP, FP, TN, FN por clase |

---

## Extensiones y Variantes

Los árboles de decisión son la base de métodos más avanzados:

- **Random Forest**: múltiples árboles entrenados con subconjuntos aleatorios; reduce la varianza.
- **Gradient Boosting (XGBoost, LightGBM)**: árboles construidos secuencialmente corrigiendo errores del anterior.
- **AdaBoost**: pondera las muestras mal clasificadas para que el siguiente árbol las corrija.
- **Extra Trees**: similar a Random Forest pero con divisiones aleatorias; más rápido.

---

## Ejemplo de Aplicaciones Reales

| Área | Aplicación |
|---|---|
| Medicina | Diagnóstico de enfermedades (maligno / benigno) |
| Finanzas | Aprobación de créditos (riesgo alto / bajo) |
| Marketing | Segmentación de clientes |
| Recursos Humanos | Predicción de renuncia de empleados |
| Ciberseguridad | Detección de correos spam o intrusiones |

---

## Conclusión

Los árboles de decisión son una herramienta fundamental en el aprendizaje automático para clasificación. Su principal fortaleza es la **interpretabilidad**: es posible explicar con precisión por qué el modelo toma una decisión. Aunque pueden sufrir de sobreajuste, técnicas de poda y el uso de ensambles (Random Forest, Gradient Boosting) los convierten en la base de algunos de los métodos más potentes de la actualidad.

---

*Elaborado como material de investigación sobre métodos de clasificación en Machine Learning.*
