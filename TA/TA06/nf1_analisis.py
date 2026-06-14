"""
Analisis reproducible para TA06 - INFO1184.

Dataset: Neurofibromatosis Type 1 (NF1) - Clinical Symptoms of
Familial and Sporadic Cases, UCI Machine Learning Repository.

Objetivo principal: clasificar el tipo de caso de NF1:
0 = esporadico, 1 = familiar.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier, plot_tree


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset-uci.xlsx"
FIG_DIR = BASE_DIR / "figuras"
RANDOM_STATE = 1184


def preparar_directorios() -> None:
    """Crea la carpeta de figuras si no existe."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def cargar_datos() -> pd.DataFrame:
    """Carga el dataset desde la hoja Dataset del archivo Excel local."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"No se encontro {DATA_PATH}. Descargue el Excel UCI y guardelo como dataset-uci.xlsx."
        )

    df = pd.read_excel(DATA_PATH, sheet_name="Dataset")
    primera_columna = df.columns[0]
    if str(primera_columna).startswith("Unnamed"):
        df = df.rename(columns={primera_columna: "ID"})

    df.columns = [str(col).strip() for col in df.columns]
    return df


def describir_datos(df: pd.DataFrame) -> None:
    """Imprime una sintesis inicial de comprension de datos."""
    print("\n=== COMPRENSION DE LOS DATOS ===")
    print(f"Filas: {df.shape[0]}")
    print(f"Columnas: {df.shape[1]}")
    print("\nColumnas:")
    for columna in df.columns:
        print(f"- {columna}")

    print("\nValores faltantes por columna:")
    print(df.isna().sum().to_string())
    print(f"\nDuplicados exactos: {df.duplicated().sum()}")


def construir_matrices(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, list[str], list[str]]:
    """Separa variable objetivo y predictores para clasificacion."""
    target = "Case Type"
    if target not in df.columns:
        raise ValueError("El dataset no contiene la columna objetivo 'Case Type'.")

    df_modelo = df.copy()
    if "ID" in df_modelo.columns:
        df_modelo = df_modelo.drop(columns=["ID"])

    y = df_modelo[target].astype(int)
    X = df_modelo.drop(columns=[target])

    variables_edad = [
        "Age of Mother",
        "Age of Father",
        "Age at First Diagnosis",
    ]
    variables_edad = [col for col in variables_edad if col in X.columns]
    variables_binarias = [col for col in X.columns if col not in variables_edad]

    for columna in X.columns:
        X[columna] = pd.to_numeric(X[columna], errors="coerce")

    return X, y, variables_edad, variables_binarias


def graficar_distribucion_clases(y: pd.Series) -> None:
    """Grafica el balance de casos esporadicos y familiares."""
    conteos = y.map({0: "Esporádico", 1: "Familiar"}).value_counts().reindex(
        ["Esporádico", "Familiar"]
    )

    plt.figure(figsize=(7, 4.5))
    ax = sns.barplot(
        x=conteos.index,
        y=conteos.values,
        hue=conteos.index,
        palette=["#5DADE2", "#AF7AC5"],
        legend=False,
    )
    ax.set_title("Distribución de clases: tipo de caso NF1")
    ax.set_xlabel("Clase")
    ax.set_ylabel("Número de pacientes")
    for i, valor in enumerate(conteos.values):
        ax.text(i, valor + 2, str(int(valor)), ha="center", fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "distribucion_clases.png", dpi=300)
    plt.close()


def graficar_prevalencia_sintomas(df: pd.DataFrame) -> pd.DataFrame:
    """Grafica prevalencia de síntomas binarios por tipo de caso."""
    excluir = {"ID", "Case Type", "Age of Mother", "Age of Father", "Age at First Diagnosis"}
    sintomas = [col for col in df.columns if col not in excluir]
    datos = df.copy()
    datos["Tipo de caso"] = datos["Case Type"].map({0: "Esporádico", 1: "Familiar"})

    prevalencia = (
        datos.groupby("Tipo de caso")[sintomas]
        .mean(numeric_only=True)
        .T.rename_axis("Sintoma")
        .reset_index()
    )
    prevalencia_larga = prevalencia.melt(
        id_vars="Sintoma", var_name="Tipo de caso", value_name="Prevalencia"
    )
    orden = (
        prevalencia_larga.groupby("Sintoma")["Prevalencia"].mean().sort_values(ascending=False).index
    )

    plt.figure(figsize=(10, 6.5))
    ax = sns.barplot(
        data=prevalencia_larga,
        y="Sintoma",
        x="Prevalencia",
        hue="Tipo de caso",
        order=orden,
        palette=["#5DADE2", "#AF7AC5"],
    )
    ax.set_title("Prevalencia de síntomas y tumores por tipo de caso")
    ax.set_xlabel("Proporción de pacientes con presencia del indicador")
    ax.set_ylabel("")
    ax.set_xlim(0, 1)
    ax.legend(title="Tipo de caso", loc="lower right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "prevalencia_sintomas.png", dpi=300)
    plt.close()

    return prevalencia


def entrenar_y_evaluar(
    X: pd.DataFrame,
    y: pd.Series,
    variables_edad: list[str],
) -> dict[str, object]:
    """Entrena el árbol de decisión y calcula métricas de evaluación."""
    preprocesador = ColumnTransformer(
        transformers=[("edad", SimpleImputer(strategy="median"), variables_edad)],
        remainder="passthrough",
        verbose_feature_names_out=False,
    )

    modelo = DecisionTreeClassifier(
        criterion="gini",
        max_depth=3,
        min_samples_split=2,
        min_samples_leaf=15,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocesamiento", preprocesador),
            ("arbol", modelo),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    metricas = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "auc": roc_auc_score(y_test, y_prob),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_resultados = cross_validate(
        pipeline,
        X,
        y,
        cv=cv,
        scoring=["accuracy", "precision", "recall", "f1", "roc_auc"],
    )

    print("\n=== MODELADO Y EVALUACION ===")
    print("Modelo: DecisionTreeClassifier(criterion='gini', max_depth=3, min_samples_leaf=15, class_weight='balanced')")
    print("\nMétricas en conjunto de prueba:")
    for nombre, valor in metricas.items():
        print(f"{nombre}: {valor:.4f}")

    print("\nReporte de clasificacion:")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["Esporádico", "Familiar"],
            zero_division=0,
        )
    )

    print("Validación cruzada estratificada de 5 pliegues:")
    for clave in ["test_accuracy", "test_precision", "test_recall", "test_f1", "test_roc_auc"]:
        print(f"{clave}: media={cv_resultados[clave].mean():.4f}, desv={cv_resultados[clave].std():.4f}")

    return {
        "pipeline": pipeline,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "y_pred": y_pred,
        "y_prob": y_prob,
        "metricas": metricas,
        "cv": cv_resultados,
    }


def graficar_matriz_confusion(y_test: pd.Series, y_pred: np.ndarray) -> None:
    """Guarda matriz de confusión del árbol de decisión."""
    etiquetas = ["Esporádico", "Familiar"]
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        square=True,
        linewidths=1.2,
        linecolor="white",
        xticklabels=etiquetas,
        yticklabels=etiquetas,
        annot_kws={"fontsize": 16, "fontweight": "bold"},
        ax=ax,
    )
    ax.set_title("Matriz de confusión del árbol de decisión", pad=12)
    ax.set_xlabel("Clase predicha")
    ax.set_ylabel("Clase real")
    ax.tick_params(axis="x", rotation=0)
    ax.tick_params(axis="y", rotation=0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "matriz_confusion.png", dpi=300)
    plt.close()


def graficar_curva_roc(y_test: pd.Series, y_prob: np.ndarray) -> None:
    """Guarda curva ROC del clasificador."""
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(6.5, 5))
    plt.plot(fpr, tpr, color="#2E86C1", lw=2, label=f"AUC = {roc_auc:.3f}")
    plt.plot([0, 1], [0, 1], color="gray", linestyle="--", label="Azar")
    plt.xlabel("Tasa de falsos positivos")
    plt.ylabel("Tasa de verdaderos positivos")
    plt.title("Curva ROC - Clasificación familiar vs. esporádica")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "curva_roc.png", dpi=300)
    plt.close()


def graficar_arbol(pipeline: Pipeline, feature_names: list[str]) -> None:
    """Guarda una visualizacion interpretable del arbol entrenado."""
    arbol = pipeline.named_steps["arbol"]
    plt.figure(figsize=(18, 10))
    plot_tree(
        arbol,
        feature_names=feature_names,
        class_names=["Esporádico", "Familiar"],
        filled=True,
        rounded=True,
        impurity=True,
        proportion=True,
        fontsize=8,
    )
    plt.title("Árbol de decisión para tipo de caso NF1")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "arbol_decision.png", dpi=300)
    plt.close()


def graficar_importancia_features(pipeline: Pipeline, feature_names: list[str]) -> pd.DataFrame:
    """Guarda grafico de importancia de variables."""
    importancias = pipeline.named_steps["arbol"].feature_importances_
    tabla = pd.DataFrame({"Variable": feature_names, "Importancia": importancias})
    tabla = tabla.sort_values("Importancia", ascending=False)
    tabla_plot = tabla.head(12)

    plt.figure(figsize=(9, 5.5))
    ax = sns.barplot(data=tabla_plot, x="Importancia", y="Variable", color="#45B39D")
    ax.set_title("Importancia de variables en el árbol de decisión")
    ax.set_xlabel("Importancia relativa")
    ax.set_ylabel("")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "importancia_features.png", dpi=300)
    plt.close()
    return tabla


def imprimir_resumen_final(
    df: pd.DataFrame,
    y: pd.Series,
    resultados: dict[str, object],
    importancias: pd.DataFrame,
) -> None:
    """Imprime resumen interpretativo de resultados."""
    metricas = resultados["metricas"]
    cv = resultados["cv"]
    top_importancias = importancias.head(5)

    print("\n=== RESUMEN FINAL ===")
    print(f"Dataset usado: {DATA_PATH.name}")
    print(f"Registros analizados: {len(df)}")
    print(f"Clase 0 esporadica: {(y == 0).sum()} casos")
    print(f"Clase 1 familiar: {(y == 1).sum()} casos")
    print(f"Pacientes con tumores: {int(df['Tumour Case'].sum())}")
    print(f"Pacientes sin tumores: {int((df['Tumour Case'] == 0).sum())}")
    print(
        "Métricas test: "
        f"accuracy={metricas['accuracy']:.4f}, precision={metricas['precision']:.4f}, "
        f"recall={metricas['recall']:.4f}, f1={metricas['f1']:.4f}, auc={metricas['auc']:.4f}"
    )
    print(
        "Validación cruzada: "
        f"accuracy media={cv['test_accuracy'].mean():.4f}, "
        f"f1 media={cv['test_f1'].mean():.4f}, "
        f"auc media={cv['test_roc_auc'].mean():.4f}"
    )
    print("Variables mas importantes:")
    for _, fila in top_importancias.iterrows():
        print(f"- {fila['Variable']}: {fila['Importancia']:.4f}")
    print(f"\nFiguras guardadas en: {FIG_DIR}")


def main() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    preparar_directorios()
    df = cargar_datos()
    describir_datos(df)

    X, y, variables_edad, _ = construir_matrices(df)
    graficar_distribucion_clases(y)
    graficar_prevalencia_sintomas(df)

    resultados = entrenar_y_evaluar(X, y, variables_edad)
    feature_names = list(resultados["pipeline"].named_steps["preprocesamiento"].get_feature_names_out())

    graficar_matriz_confusion(resultados["y_test"], resultados["y_pred"])
    graficar_curva_roc(resultados["y_test"], resultados["y_prob"])
    graficar_arbol(resultados["pipeline"], feature_names)
    importancias = graficar_importancia_features(resultados["pipeline"], feature_names)

    imprimir_resumen_final(df, y, resultados, importancias)


if __name__ == "__main__":
    main()
