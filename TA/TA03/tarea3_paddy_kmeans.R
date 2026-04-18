# ============================================================
# Tarea 3 - INFO1184 Inteligencia de Negocios
# Análisis de Agrupamiento por K-Medias
# Dataset: Paddy Dataset (Cultivo de Arroz)
# Metodología: CRISP-DM (Fases 1 a 4)
# ============================================================

# --- Instalar paquetes si no están ---
paquetes <- c("dplyr", "ggplot2", "cluster", "corrplot", "tidyr", "gridExtra")
nuevos <- paquetes[!(paquetes %in% installed.packages()[,"Package"])]
if(length(nuevos)) install.packages(nuevos, dependencies = TRUE)

# Cargar librerías
library(dplyr)
library(ggplot2)
library(cluster)
library(corrplot)
library(tidyr)
library(gridExtra)

# ============================================================
# --- Fase 1: Comprensión del Negocio ---
# ============================================================
# Objetivo: Segmentar parcelas de cultivo de arroz (paddy) según
# sus condiciones agrícolas, climáticas y de rendimiento, para
# identificar perfiles productivos que permitan optimizar
# decisiones de siembra, fertilización y riego.

# ============================================================
# --- Fase 2: Comprensión de los Datos ---
# ============================================================

# Cargar datos
paddy <- read.csv("dataset/paddydataset.csv", stringsAsFactors = TRUE)

cat("Dimensiones del dataset:", dim(paddy), "\n")
cat("Estructura:\n")
str(paddy)
cat("\nResumen estadístico:\n")
summary(paddy)

# Limpiar nombres de columnas (quitar espacios)
colnames(paddy) <- trimws(colnames(paddy))

# Revisar valores faltantes
cat("\nValores faltantes por columna:\n")
print(colSums(is.na(paddy)))

# Variables categóricas
cat("\nDistribución de Agriblock:\n")
print(table(paddy$Agriblock))
cat("\nDistribución de Variety:\n")
print(table(paddy$Variety))
cat("\nDistribución de Soil.Types:\n")
print(table(paddy$Soil.Types))
cat("\nDistribución de Nursery:\n")
print(table(paddy$Nursery))

# --- Fig 1: Distribución del rendimiento de arroz ---
pdf("fig_01_distribucion_yield.pdf", width = 6, height = 4.5)
ggplot(paddy, aes(x = Paddy.yield.in.Kg.)) +
  geom_histogram(bins = 30, fill = "#2ecc71", color = "white", alpha = 0.8) +
  geom_vline(xintercept = mean(paddy$Paddy.yield.in.Kg.),
             linetype = "dashed", color = "red", linewidth = 0.8) +
  labs(title = "Distribución del Rendimiento de Arroz (Paddy Yield)",
       x = "Rendimiento (Kg)", y = "Frecuencia") +
  theme_minimal(base_size = 12) +
  annotate("text", x = mean(paddy$Paddy.yield.in.Kg.) + 500,
           y = Inf, vjust = 2,
           label = paste("Media =", round(mean(paddy$Paddy.yield.in.Kg.), 0), "Kg"),
           color = "red", size = 3.5, fontface = "bold")
dev.off()

# --- Fig 2: Rendimiento por variedad y tipo de suelo ---
pdf("fig_02_yield_variedad_suelo.pdf", width = 7, height = 4.5)
ggplot(paddy, aes(x = Variety, y = Paddy.yield.in.Kg., fill = Soil.Types)) +
  geom_boxplot(outlier.size = 0.8) +
  labs(title = "Rendimiento por Variedad de Arroz y Tipo de Suelo",
       x = "Variedad", y = "Rendimiento (Kg)", fill = "Tipo de Suelo") +
  theme_minimal(base_size = 12) +
  scale_fill_manual(values = c("alluvial" = "#3498db", "clay" = "#e67e22"))
dev.off()

# --- Fig 3: Rendimiento por bloque agrícola ---
pdf("fig_03_yield_agriblock.pdf", width = 8, height = 4)
ggplot(paddy, aes(x = reorder(Agriblock, Paddy.yield.in.Kg., FUN = median),
                  y = Paddy.yield.in.Kg., fill = Agriblock)) +
  geom_boxplot(outlier.size = 0.5) +
  labs(title = "Rendimiento por Bloque Agrícola",
       x = "Bloque Agrícola", y = "Rendimiento (Kg)") +
  theme_minimal(base_size = 11) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "none")
dev.off()

# --- Fig 4: Matriz de correlaciones ---
vars_num <- paddy %>%
  select(Hectares, Seedrate.in.Kg., LP_Mainfield.in.Tonnes.,
         Nursery.area..Cents., DAP_20days, Urea_40Days,
         Potassh_50Days, Micronutrients_70Days, Pest_60Day.in.ml.,
         Trash.in.bundles., Paddy.yield.in.Kg.)

pdf("fig_04_correlaciones.pdf", width = 7, height = 7)
corrplot(cor(vars_num), method = "color", type = "upper",
         addCoef.col = "white", number.cex = 0.6,
         tl.col = "black", tl.srt = 45, tl.cex = 0.7,
         title = "Matriz de Correlaciones - Variables Agrícolas",
         mar = c(0, 0, 2, 0))
dev.off()

# ============================================================
# --- Fase 3: Preparación de los Datos ---
# ============================================================

# Seleccionar variables numéricas relevantes para clustering
paddy_prep <- paddy %>%
  select(
    Hectares,
    Seedrate.in.Kg.,
    LP_Mainfield.in.Tonnes.,
    DAP_20days,
    Urea_40Days,
    Potassh_50Days,
    Micronutrients_70Days,
    Pest_60Day.in.ml.,
    X30DRain..in.mm.,
    X30DAI.in.mm.,
    X30_50DRain..in.mm.,
    X30_50DAI.in.mm.,
    X51_70DRain.in.mm.,
    X51_70AI.in.mm.,
    Min.temp_D1_D30,
    Max.temp_D1_D30,
    Relative.Humidity_D1_D30,
    Relative.Humidity_D31_D60,
    Trash.in.bundles.,
    Paddy.yield.in.Kg.
  )

cat("\nDimensiones de datos preparados:", dim(paddy_prep), "\n")

# Estandarización z-score
paddy_scaled <- scale(paddy_prep)

cat("Medias (deben ser ~0):", round(colMeans(paddy_scaled), 4), "\n")
cat("SD (deben ser ~1):", round(apply(paddy_scaled, 2, sd), 4), "\n")

# ============================================================
# --- Fase 4: Modelado - K-Medias ---
# ============================================================

# --- Determinar número óptimo de clusters ---

# Método del codo (WSS)
set.seed(42)
wss <- sapply(2:10, function(k) {
  km <- kmeans(paddy_scaled, centers = k, nstart = 25, iter.max = 100)
  km$tot.withinss
})

# Coeficiente de silueta promedio
avg_sil <- sapply(2:10, function(k) {
  set.seed(42)
  km <- kmeans(paddy_scaled, centers = k, nstart = 25, iter.max = 100)
  mean(silhouette(km$cluster, dist(paddy_scaled))[, 3])
})

cat("\nSilueta promedio por k:\n")
for (k in 2:10) {
  cat(sprintf("  k = %d: %.4f\n", k, avg_sil[k - 1]))
}

# --- Fig 5: Codo + Silueta ---
df_elbow <- data.frame(k = 2:10, WSS = wss)
df_sil   <- data.frame(k = 2:10, Silueta = avg_sil)

k_opt <- which.max(avg_sil) + 1
cat("\nk óptimo según silueta:", k_opt, "\n")

p_elbow <- ggplot(df_elbow, aes(x = k, y = WSS)) +
  geom_line(color = "#3498db", linewidth = 1) +
  geom_point(color = "#3498db", size = 3) +
  geom_vline(xintercept = k_opt, linetype = "dashed", color = "red") +
  labs(title = "Método del Codo",
       x = "Número de Clusters (k)",
       y = "WSS (Within Sum of Squares)") +
  scale_x_continuous(breaks = 2:10) +
  theme_minimal(base_size = 11)

p_sil <- ggplot(df_sil, aes(x = k, y = Silueta)) +
  geom_line(color = "#e74c3c", linewidth = 1) +
  geom_point(color = "#e74c3c", size = 3) +
  geom_vline(xintercept = k_opt, linetype = "dashed", color = "red") +
  labs(title = "Coeficiente de Silueta",
       x = "Número de Clusters (k)",
       y = "Silueta Promedio") +
  scale_x_continuous(breaks = 2:10) +
  theme_minimal(base_size = 11)

pdf("fig_05_elbow_silhouette.pdf", width = 9, height = 4)
grid.arrange(p_elbow, p_sil, ncol = 2)
dev.off()

# --- Ejecutar K-Medias con k óptimo ---
set.seed(42)
km_final <- kmeans(paddy_scaled, centers = k_opt, nstart = 25, iter.max = 100)

cat("\nTamaño de clusters:\n")
print(table(km_final$cluster))

cat("\nWSS total:", km_final$tot.withinss, "\n")
cat("BSS / TSS:", round(km_final$betweenss / km_final$totss * 100, 2), "%\n")

# --- Fig 6: Clusters en PCA ---
pca_result <- prcomp(paddy_scaled)
pca_df <- data.frame(
  PC1 = pca_result$x[, 1],
  PC2 = pca_result$x[, 2],
  Cluster = as.factor(km_final$cluster)
)

var_exp <- summary(pca_result)$importance[2, 1:2] * 100

# Centroides proyectados en PCA
centroids_pca <- pca_df %>%
  group_by(Cluster) %>%
  summarise(PC1 = mean(PC1), PC2 = mean(PC2))

colores <- c("#e74c3c", "#2ecc71", "#3498db", "#f39c12", "#9b59b6",
             "#1abc9c", "#e67e22", "#34495e", "#16a085", "#c0392b")

pdf("fig_06_clusters_pca.pdf", width = 7, height = 5)
ggplot(pca_df, aes(x = PC1, y = PC2, color = Cluster)) +
  geom_point(alpha = 0.5, size = 1.5) +
  stat_ellipse(level = 0.90, linewidth = 0.8) +
  geom_point(data = centroids_pca, aes(x = PC1, y = PC2),
             shape = 4, size = 5, stroke = 2, color = "black") +
  labs(
    title = paste0("K-Medias (k = ", k_opt, ") - Proyección PCA"),
    x = paste0("PC1 (", round(var_exp[1], 1), "% varianza)"),
    y = paste0("PC2 (", round(var_exp[2], 1), "% varianza)")
  ) +
  scale_color_manual(values = colores[1:k_opt]) +
  theme_minimal(base_size = 12) +
  theme(legend.position = "bottom")
dev.off()

# --- Perfiles de clusters ---
paddy_prep$cluster <- as.factor(km_final$cluster)

cat("\n--- Perfiles de Clusters ---\n")
perfiles <- paddy_prep %>%
  group_by(cluster) %>%
  summarise(
    n                = n(),
    hectareas_media  = round(mean(Hectares), 1),
    seedrate_media   = round(mean(Seedrate.in.Kg.), 1),
    dap_media        = round(mean(DAP_20days), 1),
    urea_media       = round(mean(Urea_40Days), 1),
    potasio_media    = round(mean(Potassh_50Days), 1),
    pest_media       = round(mean(Pest_60Day.in.ml.), 0),
    lluvia_30d       = round(mean(X30DRain..in.mm.), 1),
    temp_min         = round(mean(Min.temp_D1_D30), 1),
    temp_max         = round(mean(Max.temp_D1_D30), 1),
    humedad          = round(mean(Relative.Humidity_D1_D30), 1),
    trash_media      = round(mean(Trash.in.bundles.), 0),
    yield_media      = round(mean(Paddy.yield.in.Kg.), 0)
  )
print(as.data.frame(perfiles))

# --- Fig 7: Comparación de perfiles ---
perfiles_long <- perfiles %>%
  select(cluster, yield_media, urea_media, potasio_media, pest_media) %>%
  pivot_longer(cols = -cluster, names_to = "variable", values_to = "valor")

pdf("fig_07_perfiles_clusters.pdf", width = 8, height = 5)
ggplot(perfiles_long, aes(x = variable, y = valor, fill = cluster)) +
  geom_bar(stat = "identity", position = "dodge") +
  labs(title = "Comparación de Perfiles por Cluster",
       x = "Variable", y = "Valor", fill = "Cluster") +
  theme_minimal(base_size = 12) +
  theme(axis.text.x = element_text(angle = 30, hjust = 1)) +
  scale_fill_manual(values = colores[1:k_opt])
dev.off()

# --- Fig 8: Gráfico de silueta ---
sil <- silhouette(km_final$cluster, dist(paddy_scaled))
sil_df <- data.frame(
  obs     = 1:nrow(sil),
  cluster = as.factor(sil[, 1]),
  width   = sil[, 3]
)

sil_df <- sil_df %>%
  arrange(cluster, width) %>%
  mutate(orden = row_number())

sil_promedio <- round(mean(sil_df$width), 4)
cat("\nSilueta promedio final:", sil_promedio, "\n")

pdf("fig_08_silueta_final.pdf", width = 7, height = 5)
ggplot(sil_df, aes(x = orden, y = width, fill = cluster)) +
  geom_bar(stat = "identity", width = 1) +
  geom_hline(yintercept = sil_promedio, linetype = "dashed",
             color = "red", linewidth = 0.8) +
  annotate("text",
           x = nrow(sil_df) * 0.85, y = sil_promedio + 0.03,
           label = paste("Promedio =", sil_promedio),
           color = "red", size = 4, fontface = "bold") +
  labs(
    title = paste0("Gráfico de Silueta (k = ", k_opt, ")"),
    x = "Observaciones (ordenadas por cluster)",
    y = "Ancho de Silueta",
    fill = "Cluster"
  ) +
  scale_fill_manual(values = colores[1:k_opt]) +
  theme_minimal(base_size = 12) +
  coord_flip()
dev.off()

# --- Fig 9: Rendimiento por cluster ---
pdf("fig_09_yield_por_cluster.pdf", width = 6, height = 4.5)
ggplot(paddy_prep, aes(x = cluster, y = Paddy.yield.in.Kg., fill = cluster)) +
  geom_boxplot() +
  labs(title = "Rendimiento de Arroz por Cluster",
       x = "Cluster", y = "Rendimiento (Kg)") +
  theme_minimal(base_size = 12) +
  scale_fill_manual(values = colores[1:k_opt]) +
  theme(legend.position = "none")
dev.off()

cat("\n--- Análisis completado exitosamente ---\n")
cat("Se generaron 9 figuras PDF en el directorio de trabajo.\n")
