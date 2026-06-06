"""Análisis reproducible de enfermedad cardíaca para INFO1184 TA05.

El script carga ``heart.csv``, limpia duplicados, genera tablas descriptivas,
entrena modelos de clasificación y aplica K-Means para segmentar pacientes.
Todas las salidas se guardan en ``salidas/`` y ``figuras/``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    silhouette_score,
)
from sklearn.inspection import permutation_importance
from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate,
    train_test_split,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

RANDOM_STATE = 1184
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "heart.csv"
FIG_DIR = BASE_DIR / "figuras"
OUT_DIR = BASE_DIR / "salidas"


VARIABLE_LABELS = {
    "age": "Edad del paciente",
    "sex": "Sexo biológico codificado: 1 hombre, 0 mujer",
    "cp": "Tipo de dolor torácico",
    "trestbps": "Presión arterial en reposo",
    "chol": "Colesterol sérico",
    "fbs": "Glucosa en ayunas mayor a 120 mg/dl",
    "restecg": "Resultado electrocardiográfico en reposo",
    "thalach": "Frecuencia cardíaca máxima alcanzada",
    "exang": "Angina inducida por ejercicio",
    "oldpeak": "Depresión ST inducida por ejercicio",
    "slope": "Pendiente del segmento ST",
    "ca": "Número de vasos principales coloreados",
    "thal": "Resultado de prueba thal",
    "target": "Presencia de enfermedad cardíaca: 1 sí, 0 no",
}

VARIABLE_TYPES = {
    "age": "Numérica",
    "sex": "Binaria",
    "cp": "Categórica codificada",
    "trestbps": "Numérica",
    "chol": "Numérica",
    "fbs": "Binaria",
    "restecg": "Categórica codificada",
    "thalach": "Numérica",
    "exang": "Binaria",
    "oldpeak": "Numérica",
    "slope": "Categórica codificada",
    "ca": "Categórica codificada",
    "thal": "Categórica codificada",
    "target": "Objetivo",
}

VARIABLE_USE = {
    "age": "Exploración, clasificación y clustering",
    "sex": "Exploración y clasificación",
    "cp": "Exploración y clasificación",
    "trestbps": "Exploración, clasificación y clustering",
    "chol": "Exploración, clasificación y clustering",
    "fbs": "Exploración y clasificación",
    "restecg": "Exploración y clasificación",
    "thalach": "Exploración, clasificación y clustering",
    "exang": "Exploración, clasificación y perfilado",
    "oldpeak": "Exploración, clasificación y clustering",
    "slope": "Exploración y clasificación",
    "ca": "Exploración y clasificación",
    "thal": "Exploración y clasificación",
    "target": "Variable objetivo y perfilado posterior",
}

NUMERIC_FOR_COMPARISON = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_FOR_COMPARISON = [
    "sex",
    "cp",
    "fbs",
    "restecg",
    "exang",
    "slope",
    "ca",
    "thal",
]
FEATURES = [col for col in VARIABLE_LABELS if col != "target"]
CLUSTER_FEATURES = ["age", "trestbps", "chol", "thalach", "oldpeak"]
KNN_VALUES = [3, 5, 7, 9, 11]


def validate_data_path() -> None:
    """Verifica que el archivo heart.csv exista antes de ejecutar."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "No se encontro heart.csv en TA/TA05. "
            "El dataset debe llamarse exactamente heart.csv."
        )


def save_csv(
    dataframe: pd.DataFrame, filename: str, index: bool = False
) -> None:
    """Guarda una tabla CSV dentro de la carpeta de salidas."""

    dataframe.to_csv(OUT_DIR / filename, index=index)


def round_frame(dataframe: pd.DataFrame, digits: int = 4) -> pd.DataFrame:
    """Redondea solo columnas numericas y conserva los textos."""

    result = dataframe.copy()
    numeric_cols = result.select_dtypes(include=[np.number]).columns
    result[numeric_cols] = result[numeric_cols].round(digits)
    return result


def export_dictionary() -> None:
    """Exporta el diccionario de variables usado en el informe."""

    dictionary = pd.DataFrame(
        {
            "variable": list(VARIABLE_LABELS.keys()),
            "descripcion": list(VARIABLE_LABELS.values()),
            "tipo_aproximado": [
                VARIABLE_TYPES[var] for var in VARIABLE_LABELS.keys()
            ],
            "uso_en_analisis": [
                VARIABLE_USE[var] for var in VARIABLE_LABELS.keys()
            ],
        }
    )
    save_csv(dictionary, "00_diccionario_variables.csv")


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina duplicados exactos y documenta la limpieza."""

    # Se eliminan duplicados antes de modelar para evitar que una misma fila
    # aparezca al mismo tiempo en entrenamiento y prueba.
    df_clean = df.drop_duplicates().reset_index(drop=True)
    cleaning = pd.DataFrame(
        {
            "indicador": [
                "filas_originales",
                "columnas_originales",
                "valores_faltantes",
                "duplicados_exactos",
                "filas_luego_de_eliminar_duplicados",
                "filas_removidas_pct",
            ],
            "valor": [
                len(df),
                df.shape[1],
                int(df.isna().sum().sum()),
                int(df.duplicated().sum()),
                len(df_clean),
                round(df.duplicated().sum() / len(df) * 100, 2),
            ],
        }
    )
    save_csv(cleaning, "03_duplicados_y_limpieza.csv")
    return df_clean


def export_descriptive_tables(
    df_original: pd.DataFrame, df: pd.DataFrame
) -> None:
    """Crea tablas CSV para entender y explorar los datos."""

    export_dictionary()

    summary_dataset = pd.DataFrame(
        {
            "indicador": [
                "filas_dataset_original",
                "columnas",
                "filas_dataset_depurado",
                "valores_faltantes_depurado",
                "proporcion_target_1_depurado",
            ],
            "valor": [
                len(df_original),
                df_original.shape[1],
                len(df),
                int(df.isna().sum().sum()),
                round(df["target"].mean(), 4),
            ],
        }
    )
    save_csv(summary_dataset, "01_resumen_dataset.csv")

    desc = df.describe().T.reset_index().rename(columns={"index": "variable"})
    desc.insert(1, "faltantes", df.isna().sum().values)
    save_csv(round_frame(desc, 3), "02_resumen_variables.csv")

    by_target = df.groupby("target")[NUMERIC_FOR_COMPARISON].agg(
        ["count", "mean", "median", "std"]
    )
    by_target.columns = [
        "_".join(col).strip() for col in by_target.columns.values
    ]
    save_csv(
        round_frame(by_target.reset_index(), 3), "04_resumen_por_target.csv"
    )

    means_by_target = df.groupby("target")[NUMERIC_FOR_COMPARISON].mean()
    comparison_rows = []
    for variable in NUMERIC_FOR_COMPARISON:
        mean_0 = means_by_target.loc[0, variable]
        mean_1 = means_by_target.loc[1, variable]
        if mean_1 > mean_0:
            direction = "mayor en target 1"
        else:
            direction = "menor en target 1"
        comparison_rows.append(
            {
                "variable": variable,
                "promedio_target_0": mean_0,
                "promedio_target_1": mean_1,
                "interpretacion_breve": direction,
            }
        )
    save_csv(
        round_frame(pd.DataFrame(comparison_rows), 3),
        "04b_comparacion_promedios_target.csv",
    )

    categorical_rows = []
    for variable in CATEGORICAL_FOR_COMPARISON:
        table = pd.crosstab(df[variable], df["target"], normalize="index")
        for category, row in table.iterrows():
            categorical_rows.append(
                {
                    "variable": variable,
                    "categoria": category,
                    "proporcion_target_0": row.get(0, 0),
                    "proporcion_target_1": row.get(1, 0),
                }
            )
    save_csv(
        round_frame(pd.DataFrame(categorical_rows), 4),
        "04c_resumen_categoricas_target.csv",
    )

    correlations = (
        df.corr(numeric_only=True)["target"]
        .drop("target")
        .sort_values(key=abs, ascending=False)
    )
    corr_table = correlations.reset_index()
    corr_table.columns = ["variable", "correlacion_con_target"]
    corr_table["descripcion"] = corr_table["variable"].map(VARIABLE_LABELS)
    corr_table["nota_interpretacion"] = (
        "Asociación exploratoria; no implica causalidad ni diagnóstico."
    )
    save_csv(round_frame(corr_table, 4), "05_correlaciones_con_target.csv")


def make_plots(df: pd.DataFrame) -> None:
    """Genera las figuras del análisis exploratorio."""

    sns.set_theme(style="whitegrid", palette="Set2")

    fig, ax = plt.subplots(figsize=(6, 4))
    target_counts = df["target"].value_counts().sort_index()
    sns.barplot(
        x=target_counts.index.astype(str), y=target_counts.values, ax=ax
    )
    ax.set_title("Distribución de presencia de enfermedad cardíaca")
    ax.set_xlabel("Target: 0 = no presenta, 1 = presenta")
    ax.set_ylabel("Cantidad de pacientes")
    for i, value in enumerate(target_counts.values):
        ax.text(i, value + 2, str(value), ha="center")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_01_distribucion_target.pdf")
    plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(11, 7))
    axes = axes.ravel()
    for ax, variable in zip(axes, NUMERIC_FOR_COMPARISON):
        sns.boxplot(data=df, x="target", y=variable, ax=ax)
        ax.set_title(variable)
        ax.set_xlabel("Target")
        ax.set_ylabel(variable)
    axes[-1].axis("off")
    fig.suptitle("Variables numéricas según presencia de enfermedad", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_02_variables_numericas_por_target.pdf")
    plt.close(fig)

    corr = df.corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr,
        cmap="RdBu_r",
        center=0,
        annot=True,
        fmt=".2f",
        linewidths=0.3,
        ax=ax,
    )
    ax.set_title("Matriz de correlación del dataset depurado")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_03_matriz_correlacion.pdf")
    plt.close(fig)

    selected_categories = ["cp", "exang", "thal", "ca"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    axes = axes.ravel()
    for ax, variable in zip(axes, selected_categories):
        prop = pd.crosstab(df[variable], df["target"], normalize="index")
        prop.plot(
            kind="bar", stacked=True, ax=ax, color=["#88CCEE", "#CC6677"]
        )
        ax.set_title(f"{variable} por target")
        ax.set_xlabel(variable)
        ax.set_ylabel("Proporción")
        ax.legend(title="target", loc="best")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_04_cp_exang_thal_por_target.pdf")
    plt.close(fig)


def build_models(knn_k: int = 7) -> dict[str, object]:
    """Construye los modelos usados en clasificación."""

    return {
        "Regresión logística": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=2000, random_state=RANDOM_STATE
                    ),
                ),
            ]
        ),
        f"KNN k={knn_k}": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", KNeighborsClassifier(n_neighbors=knn_k)),
            ]
        ),
        "Árbol de decisión": DecisionTreeClassifier(
            max_depth=4, random_state=RANDOM_STATE
        ),
    }


def validate_knn_k(x: pd.DataFrame, y: pd.Series) -> int:
    """Evalua varios valores de k y devuelve el mejor por F1 promedio."""

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    rows = []
    for k_value in KNN_VALUES:
        model = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", KNeighborsClassifier(n_neighbors=k_value)),
            ]
        )
        scores = cross_validate(
            model,
            x,
            y,
            cv=cv,
            scoring={"accuracy": "accuracy", "f1": "f1"},
        )
        rows.append(
            {
                "k": k_value,
                "accuracy_promedio": scores["test_accuracy"].mean(),
                "accuracy_desv": scores["test_accuracy"].std(),
                "f1_promedio": scores["test_f1"].mean(),
                "f1_desv": scores["test_f1"].std(),
            }
        )
    results = pd.DataFrame(rows).sort_values(
        ["f1_promedio", "accuracy_promedio"], ascending=False
    )
    save_csv(round_frame(results, 4), "13_validacion_knn_k.csv")
    return int(results.iloc[0]["k"])


def export_cross_validation(
    models: dict[str, object], x: pd.DataFrame, y: pd.Series
) -> None:
    """Exporta validación cruzada estratificada de los modelos."""

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    rows = []
    for name, model in models.items():
        scores = cross_validate(
            model,
            x,
            y,
            cv=cv,
            scoring={"accuracy": "accuracy", "f1": "f1"},
        )
        rows.append(
            {
                "modelo": name,
                "accuracy_promedio": scores["test_accuracy"].mean(),
                "accuracy_desv": scores["test_accuracy"].std(),
                "f1_promedio": scores["test_f1"].mean(),
                "f1_desv": scores["test_f1"].std(),
            }
        )
    save_csv(
        round_frame(pd.DataFrame(rows), 4),
        "12_validacion_cruzada_modelos.csv",
    )


def train_classifiers(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, str, np.ndarray, np.ndarray, pd.DataFrame]:
    """Entrena clasificadores simples y exporta sus métricas."""

    x = df[FEATURES]
    y = df["target"]
    best_knn_k = validate_knn_k(x, y)
    models = build_models(best_knn_k)
    export_cross_validation(models, x, y)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    rows = []
    predictions = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        predictions[name] = pred
        rows.append(
            {
                "modelo": name,
                "accuracy": accuracy_score(y_test, pred),
                "precision": precision_score(y_test, pred, zero_division=0),
                "recall": recall_score(y_test, pred, zero_division=0),
                "f1_score": f1_score(y_test, pred, zero_division=0),
            }
        )

    metrics = pd.DataFrame(rows).sort_values(
        ["f1_score", "accuracy"], ascending=False
    )
    save_csv(round_frame(metrics, 4), "06_metricas_clasificacion.csv")

    best_name = metrics.iloc[0]["modelo"]
    best_pred = predictions[best_name]
    matrix = confusion_matrix(y_test, best_pred)
    matrix_df = pd.DataFrame(
        matrix, index=["real_0", "real_1"], columns=["pred_0", "pred_1"]
    )
    save_csv(
        matrix_df.reset_index().rename(columns={"index": "clase_real"}),
        "07_matriz_confusion_mejor_modelo.csv",
    )

    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(matrix, display_labels=["No", "Sí"]).plot(
        ax=ax, cmap="Blues", colorbar=False, im_kw={"interpolation": "nearest"}
    )
    ax.grid(False)
    ax.set_title(f"Matriz de confusión: {best_name}")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_05_matriz_confusion_mejor_modelo.pdf")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    metrics_plot = metrics.melt(
        id_vars="modelo", var_name="metrica", value_name="valor"
    )
    sns.barplot(data=metrics_plot, x="modelo", y="valor", hue="metrica", ax=ax)
    ax.set_ylim(0, 1)
    ax.set_title("Comparación de modelos de clasificación")
    ax.set_xlabel("Modelo")
    ax.set_ylabel("Valor")
    ax.tick_params(axis="x", rotation=15)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_06_comparacion_modelos.pdf")
    plt.close(fig)

    importance = build_association_ranking(df)
    save_csv(round_frame(importance, 4), "08_ranking_asociacion_target.csv")
    export_permutation_importance(models[best_name], best_name, x_test, y_test)
    return metrics, best_name, y_test.to_numpy(), best_pred, importance


def build_association_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """Crea un ranking exploratorio de asociación con target."""

    correlations = (
        df[FEATURES + ["target"]]
        .corr(numeric_only=True)["target"]
        .drop("target")
    )
    ranking = pd.DataFrame(
        {
            "variable": FEATURES,
            "asociacion_absoluta": correlations.abs().reindex(FEATURES),
            "correlacion_con_target": correlations.reindex(FEATURES),
        }
    )
    ranking["descripcion"] = ranking["variable"].map(VARIABLE_LABELS)
    ranking["nota"] = "Ranking exploratorio; no es importancia interna de KNN."
    return ranking.sort_values("asociacion_absoluta", ascending=False)


def export_permutation_importance(
    model, model_name: str, x_test: pd.DataFrame, y_test: pd.Series
) -> None:
    """Calcula importancia por permutación para el mejor modelo."""

    result = permutation_importance(
        model,
        x_test,
        y_test,
        n_repeats=20,
        random_state=RANDOM_STATE,
        scoring="f1",
    )
    table = pd.DataFrame(
        {
            "modelo": model_name,
            "variable": FEATURES,
            "importancia_media_f1": result.importances_mean,
            "importancia_desv_f1": result.importances_std,
        }
    )
    table["descripcion"] = table["variable"].map(VARIABLE_LABELS)
    table = table.sort_values("importancia_media_f1", ascending=False)
    save_csv(round_frame(table, 4), "14_importancia_permutacion_modelo.csv")


def cluster_patients(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica K-Means sin usar la variable objetivo como entrada."""

    # Se usan solo variables continuas para que la distancia euclidiana de
    # K-Means no trate categorias codificadas como magnitudes continuas.
    x = df[CLUSTER_FEATURES]
    scaled = StandardScaler().fit_transform(x)

    rows = []
    for k in range(2, 9):
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=25)
        labels = model.fit_predict(scaled)
        rows.append(
            {
                "k": k,
                "inercia": model.inertia_,
                "silueta": silhouette_score(scaled, labels),
            }
        )
    cluster_metrics = pd.DataFrame(rows)
    save_csv(round_frame(cluster_metrics, 4), "09_metricas_clustering.csv")

    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(
        cluster_metrics["k"],
        cluster_metrics["inercia"],
        marker="o",
        color="#4477AA",
    )
    ax1.set_xlabel("Número de clusters k")
    ax1.set_ylabel("Inercia", color="#4477AA")
    ax2 = ax1.twinx()
    ax2.plot(
        cluster_metrics["k"],
        cluster_metrics["silueta"],
        marker="s",
        color="#CC6677",
    )
    ax2.set_ylabel("Coeficiente de silueta", color="#CC6677")
    ax1.set_title("Método del codo y silueta para K-Means")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_07_elbow_kmeans.pdf")
    plt.close(fig)

    best_k = int(
        cluster_metrics.sort_values("silueta", ascending=False).iloc[0]["k"]
    )
    kmeans = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=25)
    labels = kmeans.fit_predict(scaled)
    df_clustered = df.copy()
    df_clustered["cluster"] = labels

    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(scaled)
    fig, ax = plt.subplots(figsize=(7, 5))
    scatter = ax.scatter(
        coords[:, 0], coords[:, 1], c=labels, cmap="tab10", s=35, alpha=0.85
    )
    ax.set_title(f"Clusters K-Means proyectados con PCA (k={best_k})")
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0] * 100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1] * 100:.1f}%)")
    fig.colorbar(scatter, ax=ax, label="Cluster")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_08_clusters_pca.pdf")
    plt.close(fig)

    profiles = df_clustered.groupby("cluster").agg(
        n=("target", "size"),
        target_promedio=("target", "mean"),
        edad_media=("age", "mean"),
        colesterol_medio=("chol", "mean"),
        presion_media=("trestbps", "mean"),
        thalach_media=("thalach", "mean"),
        oldpeak_medio=("oldpeak", "mean"),
        exang_promedio=("exang", "mean"),
        cp_promedio=("cp", "mean"),
        thal_promedio=("thal", "mean"),
    )
    profiles = profiles.reset_index().sort_values("cluster")
    save_csv(round_frame(profiles, 3), "10_perfiles_clusters.csv")

    profile_plot = profiles.set_index("cluster")[
        [
            "target_promedio",
            "edad_media",
            "colesterol_medio",
            "presion_media",
            "thalach_media",
            "oldpeak_medio",
        ]
    ]
    profile_plot = profile_plot.rename(
        columns={
            "target_promedio": "Target promedio",
            "edad_media": "Edad media",
            "colesterol_medio": "Colesterol medio",
            "presion_media": "Presión media",
            "thalach_media": "Frecuencia máxima",
            "oldpeak_medio": "Oldpeak medio",
        }
    )
    profile_scaled = (profile_plot - profile_plot.mean()) / profile_plot.std(
        ddof=0
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.heatmap(
        profile_scaled, cmap="vlag", center=0, annot=True, fmt=".2f", ax=ax
    )
    ax.set_title("Perfiles relativos de clusters")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_09_perfiles_clusters.pdf")
    plt.close(fig)
    return cluster_metrics, profiles


def export_research_answers(
    df: pd.DataFrame,
    metrics: pd.DataFrame,
    best_model: str,
    importance: pd.DataFrame,
    cluster_metrics: pd.DataFrame,
    profiles: pd.DataFrame,
) -> None:
    """Exporta respuestas breves a las preguntas de investigación."""

    top_corr = (
        df.corr(numeric_only=True)["target"]
        .drop("target")
        .abs()
        .sort_values(ascending=False)
        .head(4)
    )
    best_cluster = cluster_metrics.sort_values(
        "silueta", ascending=False
    ).iloc[0]
    top_importance = (
        importance.dropna(subset=["asociacion_absoluta"])
        .head(4)["variable"]
        .tolist()
    )
    answers = pd.DataFrame(
        {
            "pregunta": [
                "Diferencias entre pacientes con y sin enfermedad",
                "Variables con mayor relación con target",
                "Predicción de enfermedad cardíaca",
                "Perfiles mediante clustering",
                "Comportamiento de modelos simples",
            ],
            "respuesta_sintesis": [
                (
                    "Los pacientes con target 1 tienden a presentar mayor "
                    "thalach y diferentes patrones en dolor torácico, "
                    "angina por ejercicio, oldpeak y thal; la edad, "
                    "presión y colesterol muestran diferencias más "
                    "moderadas."
                ),
                "Las mayores asociaciones lineales absolutas con target "
                "fueron: " + ", ".join(top_corr.index.tolist()) + ".",
                (
                    "Sí es posible construir modelos predictivos "
                    f"exploratorios; el mejor modelo fue {best_model} "
                    f"con F1={metrics.iloc[0]['f1_score']:.3f} y "
                    f"accuracy={metrics.iloc[0]['accuracy']:.3f}."
                ),
                (
                    "K-Means sugirió una segmentación exploratoria según "
                    "silueta "
                    f"con k={int(best_cluster['k'])}; los perfiles "
                    "difieren en edad, frecuencia cardíaca, oldpeak, "
                    "exang y proporción de target 1, pero la separación "
                    "es limitada."
                ),
                "Los modelos simples son útiles como línea base; las "
                "variables más asociadas a target fueron: "
                + ", ".join(top_importance)
                + ".",
            ],
        }
    )
    save_csv(answers, "11_respuestas_investigacion.csv")


def main() -> None:
    """Ejecuta todo el flujo de análisis."""

    validate_data_path()
    FIG_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)

    df_original = pd.read_csv(DATA_PATH)
    df = clean_dataset(df_original)
    export_descriptive_tables(df_original, df)
    make_plots(df)
    metrics, best_model, _, _, importance = train_classifiers(df)
    cluster_metrics, profiles = cluster_patients(df)
    export_research_answers(
        df, metrics, best_model, importance, cluster_metrics, profiles
    )

    print("Análisis TA05 completado")
    print(f"Dataset original: {df_original.shape[0]} filas")
    print(f"Dataset depurado: {df.shape[0]} filas")
    print(f"Mejor modelo: {best_model}")
    print(f"Figuras: {FIG_DIR}")
    print(f"Salidas: {OUT_DIR}")


if __name__ == "__main__":
    main()
