# ============================================================
# Tarea 4 - INFO1184 Inteligencia de Negocios
# Análisis de datos y visualización
# Dataset: Boston (paquete MASS)
# Técnica: Análisis de Componentes Principales (PCA)
# Metodología: CRISP-DM (Fases 1 a 5)
# ============================================================

# Este script usa R base y MASS para que sea fácil de ejecutar,
# leer y explicar. Genera figuras PDF y tablas CSV en carpetas locales.

# ============================================================
# 0. Configuración inicial
# ============================================================

if (!requireNamespace("MASS", quietly = TRUE)) {
  stop("El paquete MASS es requerido para cargar el dataset Boston.")
}

library(MASS)

set.seed(1184)

dir_figuras <- "figuras"
dir_salidas <- "salidas"

dir.create(dir_figuras, showWarnings = FALSE)
dir.create(dir_salidas, showWarnings = FALSE)

guardar_csv <- function(tabla, nombre, filas = FALSE) {
  write.csv(tabla, file.path(dir_salidas, nombre), row.names = filas)
}

coeficientes_modelo <- function(modelo) {
  tabla <- as.data.frame(coef(summary(modelo)))
  tabla$termino <- rownames(tabla)
  rownames(tabla) <- NULL
  tabla <- tabla[, c("termino", setdiff(names(tabla), "termino"))]
  names(tabla) <- c("termino", "estimacion", "error_estandar", "valor_t", "p_valor")
  tabla
}

rmse <- function(real, predicho) {
  sqrt(mean((real - predicho)^2))
}

mae <- function(real, predicho) {
  mean(abs(real - predicho))
}

r2 <- function(real, predicho) {
  1 - sum((real - predicho)^2) / sum((real - mean(real))^2)
}

cat("\n============================================================\n")
cat("Tarea 4 - Análisis Boston con PCA\n")
cat("============================================================\n")

# ============================================================
# Fase 1: Comprensión del negocio
# ============================================================

# Objetivo general:
# Analizar el mercado habitacional de Boston para identificar patrones
# asociados al precio de viviendas, entorno urbano y tasa de criminalidad.
# La técnica central es PCA, apoyada con estadística descriptiva,
# visualizaciones y regresión lineal simple.

preguntas <- c(
  "1. ¿Hay valores atípicos en al menos dos variables?",
  "2. ¿Qué suburbios tienen las casas más baratas?",
  "3. ¿Cómo influye el tamaño de la casa en su precio?",
  "4. ¿Afecta la condición de limitar con el río Charles (chas) al valor de las casas?",
  "5. ¿Cuál es el impacto del estatus socioeconómico?",
  "6. ¿Es posible predecir la tasa de criminalidad?"
)

cat("\nFase 1: preguntas de investigación\n")
print(preguntas)

# ============================================================
# Fase 2: Comprensión de los datos
# ============================================================

data("Boston", package = "MASS")

boston <- Boston
boston$id_suburbio <- seq_len(nrow(boston))
boston$chas_factor <- factor(
  boston$chas,
  levels = c(0, 1),
  labels = c("No limita con río Charles", "Limita con río Charles")
)

vars_analisis <- c(
  "crim", "zn", "indus", "chas", "nox", "rm", "age", "dis",
  "rad", "tax", "ptratio", "black", "lstat", "medv"
)

diccionario <- data.frame(
  variable = vars_analisis,
  descripcion = c(
    "Tasa de criminalidad per cápita por suburbio",
    "Proporción de suelo residencial para lotes grandes",
    "Proporción de acres industriales no minoristas",
    "Indicador de límite con el río Charles: 1 si limita, 0 si no",
    "Concentración de óxidos nítricos",
    "Número promedio de habitaciones por vivienda",
    "Proporción de viviendas construidas antes de 1940",
    "Distancia ponderada a centros de empleo de Boston",
    "Índice de accesibilidad a autopistas radiales",
    "Tasa de impuesto a la propiedad",
    "Ratio alumno-profesor por localidad",
    "Variable histórica B del dataset original",
    "Porcentaje de población de menor estatus socioeconómico",
    "Valor mediano de viviendas en miles de dólares"
  )
)

guardar_csv(diccionario, "00_diccionario_variables.csv")

cat("\nFase 2: dimensiones del dataset\n")
print(dim(boston))

cat("\nEstructura del dataset\n")
str(boston)

cat("\nResumen estadístico\n")
print(summary(boston[vars_analisis]))

cat("\nValores faltantes por variable\n")
print(colSums(is.na(boston[vars_analisis])))

resumen_variables <- data.frame(
  variable = vars_analisis,
  n = NA_integer_,
  faltantes = NA_integer_,
  media = NA_real_,
  mediana = NA_real_,
  desviacion = NA_real_,
  minimo = NA_real_,
  maximo = NA_real_
)

for (i in seq_along(vars_analisis)) {
  variable <- vars_analisis[i]
  x <- boston[[variable]]
  resumen_variables$n[i] <- length(x)
  resumen_variables$faltantes[i] <- sum(is.na(x))
  resumen_variables$media[i] <- round(mean(x, na.rm = TRUE), 3)
  resumen_variables$mediana[i] <- round(median(x, na.rm = TRUE), 3)
  resumen_variables$desviacion[i] <- round(sd(x, na.rm = TRUE), 3)
  resumen_variables$minimo[i] <- round(min(x, na.rm = TRUE), 3)
  resumen_variables$maximo[i] <- round(max(x, na.rm = TRUE), 3)
}

guardar_csv(resumen_variables, "01_resumen_variables.csv")

# Matriz de correlaciones
cor_matriz <- cor(boston[vars_analisis])
guardar_csv(round(cor_matriz, 4), "02_matriz_correlaciones.csv", filas = TRUE)

pdf(file.path(dir_figuras, "fig_01_matriz_correlaciones.pdf"), width = 8, height = 7)
par(mar = c(7, 7, 4, 2))
image(
  1:ncol(cor_matriz),
  1:nrow(cor_matriz),
  t(cor_matriz[nrow(cor_matriz):1, ]),
  axes = FALSE,
  col = colorRampPalette(c("#b2182b", "white", "#2166ac"))(100),
  main = "Matriz de correlaciones - Boston",
  xlab = "",
  ylab = ""
)
axis(1, at = seq_along(vars_analisis), labels = vars_analisis, las = 2, cex.axis = 0.8)
axis(2, at = seq_along(vars_analisis), labels = rev(vars_analisis), las = 2, cex.axis = 0.8)
for (i in seq_along(vars_analisis)) {
  for (j in seq_along(vars_analisis)) {
    text(i, length(vars_analisis) - j + 1, round(cor_matriz[j, i], 2), cex = 0.55)
  }
}
dev.off()

# Pregunta 1: valores atípicos con regla IQR
vars_outliers <- setdiff(vars_analisis, "chas")
outliers_iqr <- data.frame()

for (variable in vars_outliers) {
  x <- boston[[variable]]
  q1 <- quantile(x, 0.25, na.rm = TRUE)
  q3 <- quantile(x, 0.75, na.rm = TRUE)
  rango_iqr <- IQR(x, na.rm = TRUE)
  limite_inferior <- q1 - 1.5 * rango_iqr
  limite_superior <- q3 + 1.5 * rango_iqr
  es_outlier <- x < limite_inferior | x > limite_superior

  outliers_iqr <- rbind(
    outliers_iqr,
    data.frame(
      variable = variable,
      limite_inferior = round(limite_inferior, 4),
      limite_superior = round(limite_superior, 4),
      n_outliers = sum(es_outlier, na.rm = TRUE),
      pct_outliers = round(mean(es_outlier, na.rm = TRUE) * 100, 2)
    )
  )
}

outliers_iqr <- outliers_iqr[order(-outliers_iqr$n_outliers, outliers_iqr$variable), ]
rownames(outliers_iqr) <- NULL
guardar_csv(outliers_iqr, "03_outliers_iqr.csv")

top_outliers <- head(outliers_iqr$variable[outliers_iqr$n_outliers > 0], 6)

pdf(file.path(dir_figuras, "fig_02_outliers_boxplot.pdf"), width = 8, height = 5)
par(mfrow = c(2, 3), mar = c(4, 4, 3, 1))
for (variable in top_outliers) {
  boxplot(
    boston[[variable]],
    main = paste("Outliers en", variable),
    ylab = "Valor",
    col = "#d9e8f5",
    border = "#2166ac",
    outline = TRUE
  )
}
dev.off()

# Pregunta 2: suburbios con casas más baratas
# Boston no entrega nombres reales de suburbios. Por eso se usa id_suburbio,
# que corresponde al número de fila de cada observación.
orden_baratos <- order(boston$medv)
suburbios_baratos <- boston[orden_baratos[1:10], c("id_suburbio", "medv", "rm", "lstat", "crim", "chas_factor")]
names(suburbios_baratos) <- c("id_suburbio", "medv", "rm", "lstat", "crim", "chas")
guardar_csv(suburbios_baratos, "04_suburbios_mas_baratos.csv")

pdf(file.path(dir_figuras, "fig_03_suburbios_mas_baratos.pdf"), width = 8, height = 5)
barplot(
  rev(suburbios_baratos$medv),
  names.arg = paste0("ID ", rev(suburbios_baratos$id_suburbio)),
  horiz = TRUE,
  las = 1,
  col = "#7f7f7f",
  xlab = "MEDV: valor mediano (miles de dólares)",
  main = "10 observaciones con menor valor mediano de vivienda"
)
mtext("Boston no entrega nombres reales; se usa id_suburbio", side = 3, line = 0.3, cex = 0.85)
dev.off()

# Pregunta 3: tamaño de la casa y precio
cor_rm_medv <- cor(boston$rm, boston$medv)
modelo_rm_medv <- lm(medv ~ rm, data = boston)
guardar_csv(coeficientes_modelo(modelo_rm_medv), "05_modelo_rm_medv.csv")

pdf(file.path(dir_figuras, "fig_04_rm_vs_medv.pdf"), width = 7, height = 5)
plot(
  boston$rm,
  boston$medv,
  pch = 19,
  col = adjustcolor("#2166ac", alpha.f = 0.65),
  xlab = "RM: número promedio de habitaciones",
  ylab = "MEDV: valor mediano (miles de dólares)",
  main = "Relación entre habitaciones promedio y precio"
)
abline(modelo_rm_medv, col = "#b2182b", lwd = 2)
legend("topleft", legend = paste("Correlación =", round(cor_rm_medv, 3)), bty = "n")
dev.off()

# Pregunta 4: condición de limitar con el río Charles y precio
resumen_chas <- aggregate(
  medv ~ chas_factor,
  data = boston,
  FUN = function(x) c(n = length(x), media = mean(x), mediana = median(x), sd = sd(x))
)
resumen_chas <- data.frame(chas_factor = resumen_chas$chas_factor, resumen_chas$medv)
names(resumen_chas) <- c("chas", "n", "medv_media", "medv_mediana", "medv_sd")
resumen_chas$medv_media <- round(resumen_chas$medv_media, 3)
resumen_chas$medv_mediana <- round(resumen_chas$medv_mediana, 3)
resumen_chas$medv_sd <- round(resumen_chas$medv_sd, 3)

test_chas <- t.test(medv ~ chas_factor, data = boston)
modelo_chas_medv <- lm(medv ~ chas_factor, data = boston)

guardar_csv(resumen_chas, "06_resumen_chas_medv.csv")
guardar_csv(coeficientes_modelo(modelo_chas_medv), "07_modelo_chas_medv.csv")

pdf(file.path(dir_figuras, "fig_05_chas_vs_medv.pdf"), width = 7, height = 5)
boxplot(
  medv ~ chas_factor,
  data = boston,
  col = c("#c7c7c7", "#9ecae1"),
  xlab = "Límite con río Charles",
  ylab = "MEDV: valor mediano (miles de dólares)",
  main = "Precio de viviendas según límite con el río Charles"
)
stripchart(medv ~ chas_factor, data = boston, vertical = TRUE, method = "jitter", pch = 19,
           col = adjustcolor("#333333", alpha.f = 0.35), add = TRUE)
mtext(paste("p-value prueba t =", signif(test_chas$p.value, 3)), side = 3, line = 0.3, cex = 0.85)
dev.off()

# Pregunta 5: estatus socioeconómico y precio
cor_lstat_medv <- cor(boston$lstat, boston$medv)
modelo_lstat_medv <- lm(medv ~ lstat, data = boston)
guardar_csv(coeficientes_modelo(modelo_lstat_medv), "08_modelo_lstat_medv.csv")

pdf(file.path(dir_figuras, "fig_06_lstat_vs_medv.pdf"), width = 7, height = 5)
plot(
  boston$lstat,
  boston$medv,
  pch = 19,
  col = adjustcolor("#4d9221", alpha.f = 0.65),
  xlab = "LSTAT: porcentaje de menor estatus socioeconómico",
  ylab = "MEDV: valor mediano (miles de dólares)",
  main = "Estatus socioeconómico y precio de vivienda"
)
abline(modelo_lstat_medv, col = "#b2182b", lwd = 2)
legend("topright", legend = paste("Correlación =", round(cor_lstat_medv, 3)), bty = "n")
dev.off()

cat("\nFase 2 completada: EDA y respuestas 1 a 5 preparadas.\n")

# ============================================================
# Fase 3: Preparación de los datos
# ============================================================

# PCA requiere variables comparables, por eso se estandarizan con z-score.
# Se mantiene chas como variable binaria 0/1 dentro del conjunto numérico.
pca_data <- boston[, vars_analisis]
pca_scaled <- scale(pca_data)

revision_escalado <- data.frame(
  variable = vars_analisis,
  media_escalada = round(colMeans(pca_scaled), 4),
  sd_escalada = round(apply(pca_scaled, 2, sd), 4)
)
guardar_csv(revision_escalado, "09_revision_escalado_pca.csv")

cat("\nFase 3: revisión de datos estandarizados para PCA\n")
print(revision_escalado)

# ============================================================
# Fase 4: Modelado con PCA
# ============================================================

pca_boston <- prcomp(pca_data, center = TRUE, scale. = TRUE)

varianza <- pca_boston$sdev^2 / sum(pca_boston$sdev^2)
pca_varianza <- data.frame(
  componente = paste0("PC", seq_along(varianza)),
  varianza = round(varianza, 4),
  varianza_pct = round(varianza * 100, 2),
  varianza_acumulada_pct = round(cumsum(varianza) * 100, 2)
)
guardar_csv(pca_varianza, "10_pca_varianza_explicada.csv")

pca_cargas <- as.data.frame(pca_boston$rotation)
pca_cargas$variable <- rownames(pca_cargas)
pca_cargas$abs_PC1 <- abs(pca_cargas$PC1)
pca_cargas$abs_PC2 <- abs(pca_cargas$PC2)
pca_cargas$importancia_PC1_PC2 <- sqrt(pca_cargas$PC1^2 + pca_cargas$PC2^2)
pca_cargas <- pca_cargas[, c(
  "variable", "PC1", "PC2", "abs_PC1", "abs_PC2", "importancia_PC1_PC2",
  paste0("PC", 3:ncol(pca_boston$rotation))
)]
pca_cargas_redondeadas <- pca_cargas
pca_cargas_redondeadas[, -1] <- round(pca_cargas_redondeadas[, -1], 4)
guardar_csv(pca_cargas_redondeadas, "11_pca_cargas_variables.csv")

pdf(file.path(dir_figuras, "fig_07_pca_varianza_explicada.pdf"), width = 8, height = 5)
bar_centros <- barplot(
  pca_varianza$varianza_pct[1:10],
  names.arg = pca_varianza$componente[1:10],
  col = "#2166ac",
  ylim = c(0, 100),
  ylab = "Porcentaje de varianza",
  xlab = "Componente principal",
  main = "Varianza explicada por componentes principales"
)
lines(bar_centros, pca_varianza$varianza_acumulada_pct[1:10], type = "b", pch = 19, col = "#b2182b", lwd = 2)
legend("right", legend = c("Varianza individual", "Varianza acumulada"),
       fill = c("#2166ac", NA), border = c("#2166ac", NA),
       lty = c(NA, 1), pch = c(NA, 19), col = c("#2166ac", "#b2182b"), bty = "n")
dev.off()

scores_pca <- as.data.frame(pca_boston$x[, 1:2])
scores_pca$id_suburbio <- boston$id_suburbio
scores_pca$medv <- boston$medv
scores_pca$crim <- boston$crim
scores_pca$chas <- boston$chas_factor

cargas_pca <- pca_boston$rotation[, 1:2]
escala_flechas <- min(
  max(abs(scores_pca$PC1)) / max(abs(cargas_pca[, 1])),
  max(abs(scores_pca$PC2)) / max(abs(cargas_pca[, 2]))
) * 0.70

colores_medv <- colorRampPalette(c("#d9f0d3", "#00441b"))(100)
grupos_color <- cut(scores_pca$medv, breaks = 100, include.lowest = TRUE, labels = FALSE)

dibujar_biplot_pca <- function(nombre_archivo, variables, titulo) {
  pdf(file.path(dir_figuras, nombre_archivo), width = 8, height = 5.4)
  par(mar = c(4.5, 4.8, 3, 1))
  plot(
    scores_pca$PC1,
    scores_pca$PC2,
    pch = 19,
    col = adjustcolor(colores_medv[grupos_color], alpha.f = 0.72),
    xlab = paste0("PC1 (", pca_varianza$varianza_pct[1], "% varianza)"),
    ylab = paste0("PC2 (", pca_varianza$varianza_pct[2], "% varianza)"),
    main = titulo
  )
  abline(h = 0, v = 0, col = "gray70", lty = 2)
  for (variable in variables) {
    arrows(0, 0, cargas_pca[variable, 1] * escala_flechas,
           cargas_pca[variable, 2] * escala_flechas,
           length = 0.08, col = "#b2182b", lwd = 1.2)
    text(cargas_pca[variable, 1] * escala_flechas * 1.14,
         cargas_pca[variable, 2] * escala_flechas * 1.14,
         labels = variable, col = "#222222", cex = 0.78)
  }
  legend("topright", legend = c("MEDV bajo", "MEDV alto"),
         col = c("#d9f0d3", "#00441b"), pch = 19, bty = "n")
  dev.off()
}

dibujar_biplot_pca(
  "fig_08_pca_biplot_simple.pdf",
  c("indus", "nox", "tax", "rad", "lstat", "medv", "rm", "chas"),
  "Biplot PCA simplificado - Boston"
)

dibujar_biplot_pca(
  "fig_08_pca_biplot.pdf",
  rownames(cargas_pca),
  "Biplot PCA completo - Boston"
)

cat("\nFase 4 completada: PCA generado.\n")

# ============================================================
# Fase 5: Evaluación y predicción de criminalidad
# ============================================================

# Para responder la pregunta 6, crim es la variable objetivo. El PCA
# predictivo se calcula solo con las otras variables; luego se entrena una
# regresión lineal sobre log1p(crim), lo que reduce asimetría y outliers.
vars_predictoras_crim <- setdiff(vars_analisis, "crim")
datos_modelo <- boston[, c("crim", vars_predictoras_crim)]

idx_train <- sample(seq_len(nrow(datos_modelo)), size = floor(0.70 * nrow(datos_modelo)))
train <- datos_modelo[idx_train, ]
test <- datos_modelo[-idx_train, ]

train_x <- train[, vars_predictoras_crim]
test_x <- test[, vars_predictoras_crim]

pca_pred <- prcomp(train_x, center = TRUE, scale. = TRUE)
varianza_pred <- pca_pred$sdev^2 / sum(pca_pred$sdev^2)
n_componentes <- which(cumsum(varianza_pred) >= 0.80)[1]
pc_modelo <- paste0("PC", seq_len(n_componentes))

train_pcs <- as.data.frame(pca_pred$x[, pc_modelo, drop = FALSE])
train_pcs$log_crim <- log1p(train$crim)

test_pcs <- as.data.frame(predict(pca_pred, newdata = test_x)[, pc_modelo, drop = FALSE])

modelo_crim <- lm(log_crim ~ ., data = train_pcs)
pred_log_crim <- predict(modelo_crim, newdata = test_pcs)
pred_crim <- pmax(0, expm1(pred_log_crim))

real_crim <- test$crim
real_log_crim <- log1p(real_crim)
pred_baseline <- rep(mean(train$crim), length(real_crim))

rmse_modelo <- rmse(real_crim, pred_crim)
mae_modelo <- mae(real_crim, pred_crim)
r2_original <- r2(real_crim, pred_crim)
r2_log <- r2(real_log_crim, pred_log_crim)
rmse_baseline <- rmse(real_crim, pred_baseline)
mejora_rmse_pct <- (1 - rmse_modelo / rmse_baseline) * 100

metricas_crim <- data.frame(
  modelo = "Regresión lineal con PCA",
  target = "log1p(crim)",
  n_train = nrow(train),
  n_test = nrow(test),
  n_componentes_pca = n_componentes,
  varianza_pca_pct = round(sum(varianza_pred[seq_len(n_componentes)]) * 100, 2),
  rmse_crim = round(rmse_modelo, 4),
  mae_crim = round(mae_modelo, 4),
  r2_crim_original = round(r2_original, 4),
  r2_log_crim = round(r2_log, 4),
  rmse_baseline = round(rmse_baseline, 4),
  mejora_rmse_pct = round(mejora_rmse_pct, 2)
)

guardar_csv(metricas_crim, "12_metricas_prediccion_crim.csv")
guardar_csv(coeficientes_modelo(modelo_crim), "13_modelo_pca_crim.csv")

predicciones_crim <- data.frame(
  crim_real = round(real_crim, 4),
  crim_predicho = round(pred_crim, 4),
  log_crim_real = round(real_log_crim, 4),
  log_crim_predicho = round(pred_log_crim, 4)
)
guardar_csv(predicciones_crim, "14_predicciones_crim_test.csv")

pdf(file.path(dir_figuras, "fig_09_prediccion_crim.pdf"), width = 7, height = 5)
plot(
  real_log_crim,
  pred_log_crim,
  pch = 19,
  col = adjustcolor("#2166ac", alpha.f = 0.70),
  xlab = "Criminalidad real transformada: log1p(crim)",
  ylab = "Criminalidad predicha transformada",
  main = "Predicción de criminalidad con PCA"
)
abline(0, 1, col = "#b2182b", lwd = 2)
legend("topleft", legend = paste("R2 log =", round(r2_log, 3)), bty = "n")
dev.off()

# Síntesis de respuestas de investigación
top2_outliers <- head(outliers_iqr[outliers_iqr$n_outliers > 0, ], 2)
outliers_sin_black <- outliers_iqr[outliers_iqr$variable != "black" & outliers_iqr$n_outliers > 0, ]
coef_rm <- coef(modelo_rm_medv)["rm"]
coef_lstat <- coef(modelo_lstat_medv)["lstat"]
diferencia_chas <- resumen_chas$medv_media[resumen_chas$chas == "Limita con río Charles"] -
  resumen_chas$medv_media[resumen_chas$chas == "No limita con río Charles"]

if (r2_log >= 0.50 && mejora_rmse_pct > 0) {
  respuesta_crim <- "Sí, el modelo con PCA muestra capacidad predictiva razonable sobre log1p(crim)."
} else if (mejora_rmse_pct > 0) {
  respuesta_crim <- "Parcialmente, el modelo mejora al promedio base, pero su capacidad predictiva es limitada."
} else {
  respuesta_crim <- "No de forma confiable con este modelo simple; no mejora el promedio base."
}

respuestas <- data.frame(
  pregunta = c(
    "1. Valores atípicos",
    "2. Suburbios más baratos",
    "3. Tamaño de casa y precio",
    "4. Límite con río Charles y precio",
    "5. Estatus socioeconómico",
    "6. Predicción de criminalidad"
  ),
  respuesta = c(
    paste0(
      "Sí. Las dos variables con más outliers por IQR son ",
      top2_outliers$variable[1], " (", top2_outliers$n_outliers[1], ") y ",
      top2_outliers$variable[2], " (", top2_outliers$n_outliers[2], "). ",
      "Sin depender de black, también destacan ", outliers_sin_black$variable[1],
      " (", outliers_sin_black$n_outliers[1], ") y ", outliers_sin_black$variable[2],
      " (", outliers_sin_black$n_outliers[2], ")."
    ),
    paste0(
      "El dataset no entrega nombres reales de suburbios. Se reportan observaciones/IDs; ",
      "los registros más baratos están en ",
      "04_suburbios_mas_baratos.csv; el menor MEDV observado es ",
      min(suburbios_baratos$medv), " miles de dólares."
    ),
    paste0(
      "La relación es positiva: correlación rm-medv = ", round(cor_rm_medv, 3),
      "; cada habitación promedio adicional se asocia a ", round(coef_rm, 3),
      " miles de dólares más en MEDV."
    ),
    paste0(
      "Los sectores que limitan con el río Charles tienen una media de MEDV ",
      round(diferencia_chas, 3), " miles de dólares mayor que las que no limitan; p-value = ",
      signif(test_chas$p.value, 3), ". chas es binaria y no mide distancia exacta."
    ),
    paste0(
      "El impacto es negativo: correlación lstat-medv = ", round(cor_lstat_medv, 3),
      "; cada punto adicional en LSTAT se asocia a ", round(coef_lstat, 3),
      " miles de dólares menos en MEDV."
    ),
    paste0(
      respuesta_crim,
      " R2 log = ", round(r2_log, 3),
      ", mejora RMSE vs base = ", round(mejora_rmse_pct, 2), "%.",
      " Es un resultado académico, no un modelo listo para despliegue."
    )
  )
)

guardar_csv(respuestas, "15_respuestas_investigacion.csv")

cat("\nFase 5 completada: evaluación y respuestas consolidadas.\n")
cat("\n--- Respuestas de investigación ---\n")
print(respuestas)

cat("\n--- Archivos generados ---\n")
cat("Figuras PDF en:", dir_figuras, "\n")
cat("Tablas CSV en:", dir_salidas, "\n")
cat("\nAnálisis completado exitosamente.\n")
