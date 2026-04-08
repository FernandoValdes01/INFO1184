# ============================================================
# Tarea 2 - INFO1184 Inteligencia de Negocios
# Análisis de Agrupamiento Jerárquico Aglomerativo
# Dataset: Bank Marketing (UCI)
# Metodología: CRISP-DM (Fases 1 a 4)
# ============================================================
# SIN dependencia de factoextra - todo con ggplot2 y base R
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
# Objetivo: Segmentar clientes de un banco portugués según sus
# características demográficas, financieras y de contacto,
# para identificar perfiles que permitan optimizar campañas
# de marketing directo (depósitos a plazo).

# ============================================================
# --- Fase 2: Comprensión de los Datos ---
# ============================================================

# Cargar datos
bank <- read.csv("data/bank-full.csv", sep = ";", stringsAsFactors = TRUE)

cat("Dimensiones del dataset:", dim(bank), "\n")
cat("Estructura:\n")
str(bank)
cat("\nResumen estadístico:\n")
summary(bank)

# Distribución de la variable objetivo
cat("\nDistribución de la variable y (suscripción):\n")
print(table(bank$y))
print(prop.table(table(bank$y)))

# --- Fig 1: Distribución variable objetivo ---
png("fig_01_distribucion_y.png", width = 600, height = 450, res = 100)
ggplot(bank, aes(x = y, fill = y)) +
  geom_bar(width = 0.6) +
  geom_text(stat = "count", aes(label = after_stat(count)), vjust = -0.5, size = 4) +
  labs(title = "Distribución de Suscripción a Depósito a Plazo",
       x = "Suscripción", y = "Frecuencia") +
  theme_minimal(base_size = 12) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.1))) +
  scale_fill_manual(values = c("no" = "#e74c3c", "yes" = "#2ecc71")) +
  theme(legend.position = "none")
dev.off()

# --- Fig 2: Edad vs Balance ---
png("fig_02_edad_balance.png", width = 600, height = 400, res = 100)
ggplot(bank, aes(x = age, y = balance, color = y)) +
  geom_point(alpha = 0.2, size = 0.8) +
  labs(title = "Relación Edad vs Balance según Suscripción",
       x = "Edad", y = "Balance (EUR)", color = "Suscripción") +
  theme_minimal(base_size = 12) +
  scale_color_manual(values = c("no" = "#e74c3c", "yes" = "#2ecc71"))
dev.off()

# --- Fig 3: Boxplot balance por trabajo ---
png("fig_03_boxplot_balance_job.png", width = 800, height = 400, res = 100)
ggplot(bank, aes(x = reorder(job, balance, FUN = median), y = balance, fill = job)) +
  geom_boxplot(outlier.size = 0.5) +
  labs(title = "Balance por Tipo de Trabajo",
       x = "Trabajo", y = "Balance (EUR)") +
  theme_minimal(base_size = 11) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "none") +
  coord_cartesian(ylim = c(-2000, 10000))
dev.off()

# --- Fig 4: Matriz de correlaciones ---
vars_num <- bank %>% select(age, balance, duration, campaign, pdays, previous, day)
png("fig_04_correlaciones.png", width = 600, height = 600, res = 100)
corrplot(cor(vars_num), method = "color", type = "upper",
         addCoef.col = "black", number.cex = 0.7,
         tl.col = "black", tl.srt = 45,
         title = "Matriz de Correlaciones", mar = c(0, 0, 2, 0))
dev.off()

# ============================================================
# --- Fase 3: Preparación de los Datos ---
# ============================================================

bank_prep <- bank %>%
  mutate(
    default_num   = ifelse(default == "yes", 1, 0),
    housing_num   = ifelse(housing == "yes", 1, 0),
    loan_num      = ifelse(loan == "yes", 1, 0),
    y_num         = ifelse(y == "yes", 1, 0),
    education_num = case_when(
      education == "primary"   ~ 1,
      education == "secondary" ~ 2,
      education == "tertiary"  ~ 3,
      TRUE                     ~ 0
    )
  ) %>%
  select(age, balance, duration, campaign, pdays, previous,
         default_num, housing_num, loan_num, education_num)

# Muestreo (el clustering jerárquico necesita matriz n x n)
set.seed(42)
sample_size <- 2000
bank_sample <- bank_prep[sample(nrow(bank_prep), sample_size), ]

# Estandarización z-score
bank_scaled <- scale(bank_sample)

cat("\nDimensiones muestra escalada:", dim(bank_scaled), "\n")
cat("Medias (deben ser ~0):", round(colMeans(bank_scaled), 4), "\n")
cat("SD (deben ser ~1):", round(apply(bank_scaled, 2, sd), 4), "\n")

# ============================================================
# --- Fase 4: Modelado ---
# ============================================================

# Matriz de distancias euclidiana
dist_matrix <- dist(bank_scaled, method = "euclidean")

# Clustering jerárquico con distintos métodos
hc_ward     <- hclust(dist_matrix, method = "ward.D2")
hc_complete <- hclust(dist_matrix, method = "complete")
hc_average  <- hclust(dist_matrix, method = "average")

# --- Fig 5: Dendrograma Ward ---
png("fig_05_dendrograma_ward.png", width = 900, height = 500, res = 100)
plot(hc_ward, labels = FALSE, hang = -1,
     main = "Dendrograma - Método Ward.D2",
     xlab = "Observaciones", ylab = "Distancia")
rect.hclust(hc_ward, k = 4, border = c("#e74c3c", "#2ecc71", "#3498db", "#f39c12"))
dev.off()

# --- Determinar número óptimo de clusters ---

# Método del codo (WSS)
wss <- sapply(2:10, function(k) {
  clusters_k <- cutree(hc_ward, k = k)
  sum(sapply(1:k, function(i) {
    members <- bank_scaled[clusters_k == i, , drop = FALSE]
    sum(scale(members, scale = FALSE)^2)
  }))
})

# Coeficiente de silueta promedio
avg_sil <- sapply(2:10, function(k) {
  clusters_k <- cutree(hc_ward, k = k)
  mean(silhouette(clusters_k, dist_matrix)[, 3])
})

cat("\nSilueta promedio por k:\n")
for (k in 2:10) {
  cat(sprintf("  k = %d: %.4f\n", k, avg_sil[k - 1]))
}

# --- Fig 6: Codo + Silueta ---
df_elbow <- data.frame(k = 2:10, WSS = wss)
df_sil   <- data.frame(k = 2:10, Silueta = avg_sil)

p_elbow <- ggplot(df_elbow, aes(x = k, y = WSS)) +
  geom_line(color = "#3498db", linewidth = 1) +
  geom_point(color = "#3498db", size = 3) +
  geom_vline(xintercept = 4, linetype = "dashed", color = "red") +
  labs(title = "Método del Codo", x = "Número de Clusters (k)",
       y = "WSS (Within Sum of Squares)") +
  scale_x_continuous(breaks = 2:10) +
  theme_minimal(base_size = 11)

p_sil <- ggplot(df_sil, aes(x = k, y = Silueta)) +
  geom_line(color = "#e74c3c", linewidth = 1) +
  geom_point(color = "#e74c3c", size = 3) +
  geom_vline(xintercept = 4, linetype = "dashed", color = "red") +
  labs(title = "Coeficiente de Silueta", x = "Número de Clusters (k)",
       y = "Silueta Promedio") +
  scale_x_continuous(breaks = 2:10) +
  theme_minimal(base_size = 11)

png("fig_06_elbow_silhouette.png", width = 900, height = 400, res = 100)
grid.arrange(p_elbow, p_sil, ncol = 2)
dev.off()

# --- Corte final: k = 4 ---
k_opt <- 4
clusters_final <- cutree(hc_ward, k = k_opt)

# --- Fig 7: Clusters en PCA (SIN factoextra, con prcomp + ggplot2) ---
pca_result <- prcomp(bank_scaled)
pca_df <- data.frame(
  PC1 = pca_result$x[, 1],
  PC2 = pca_result$x[, 2],
  Cluster = as.factor(clusters_final)
)

# Porcentaje de varianza explicada
var_exp <- summary(pca_result)$importance[2, 1:2] * 100

# Centroides por cluster
centroids <- pca_df %>%
  group_by(Cluster) %>%
  summarise(PC1 = mean(PC1), PC2 = mean(PC2))

png("fig_07_clusters_pca.png", width = 700, height = 500, res = 100)
ggplot(pca_df, aes(x = PC1, y = PC2, color = Cluster)) +
  geom_point(alpha = 0.5, size = 1.5) +
  stat_ellipse(level = 0.90, linewidth = 0.8) +
  geom_point(data = centroids, aes(x = PC1, y = PC2),
             shape = 4, size = 5, stroke = 2, color = "black") +
  labs(
    title = paste0("Clusters Jerárquicos (k = ", k_opt, ") - Proyección PCA"),
    x = paste0("PC1 (", round(var_exp[1], 1), "% varianza)"),
    y = paste0("PC2 (", round(var_exp[2], 1), "% varianza)")
  ) +
  scale_color_manual(values = c("#e74c3c", "#2ecc71", "#3498db", "#f39c12")) +
  theme_minimal(base_size = 12) +
  theme(legend.position = "bottom")
dev.off()

# --- Perfiles de clusters ---
bank_sample$cluster <- as.factor(clusters_final)

cat("\n--- Perfiles de Clusters ---\n")
perfiles <- bank_sample %>%
  group_by(cluster) %>%
  summarise(
    n              = n(),
    edad_media     = round(mean(age), 1),
    balance_medio  = round(mean(balance), 0),
    duracion_media = round(mean(duration), 0),
    campania_media = round(mean(campaign), 1),
    pdays_media    = round(mean(pdays), 0),
    previous_media = round(mean(previous), 1),
    pct_default    = round(mean(default_num) * 100, 1),
    pct_housing    = round(mean(housing_num) * 100, 1),
    pct_loan       = round(mean(loan_num) * 100, 1),
    edu_media      = round(mean(education_num), 1)
  )
print(as.data.frame(perfiles))

# --- Fig 8: Comparación de perfiles ---
perfiles_long <- perfiles %>%
  select(cluster, edad_media, balance_medio, duracion_media, campania_media) %>%
  pivot_longer(cols = -cluster, names_to = "variable", values_to = "valor")

png("fig_08_perfiles_clusters.png", width = 800, height = 500, res = 100)
ggplot(perfiles_long, aes(x = variable, y = valor, fill = cluster)) +
  geom_bar(stat = "identity", position = "dodge") +
  labs(title = "Comparación de Perfiles por Cluster",
       x = "Variable", y = "Valor", fill = "Cluster") +
  theme_minimal(base_size = 12) +
  theme(axis.text.x = element_text(angle = 30, hjust = 1)) +
  scale_fill_manual(values = c("#e74c3c", "#2ecc71", "#3498db", "#f39c12"))
dev.off()

# --- Fig 9: Gráfico de silueta (SIN factoextra, con ggplot2) ---
sil <- silhouette(clusters_final, dist_matrix)
sil_df <- data.frame(
  obs      = 1:nrow(sil),
  cluster  = as.factor(sil[, 1]),
  neighbor = sil[, 2],
  width    = sil[, 3]
)

# Ordenar por cluster y luego por ancho de silueta
sil_df <- sil_df %>%
  arrange(cluster, width) %>%
  mutate(orden = row_number())

sil_promedio <- round(mean(sil_df$width), 4)
cat("\nSilueta promedio final:", sil_promedio, "\n")

png("fig_09_silueta_final.png", width = 700, height = 500, res = 100)
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
  scale_fill_manual(values = c("#e74c3c", "#2ecc71", "#3498db", "#f39c12")) +
  theme_minimal(base_size = 12) +
  coord_flip()
dev.off()

cat("\n--- Análisis completado exitosamente ---\n")
cat("Se generaron 9 figuras PNG en el directorio de trabajo.\n")
cat("Figuras: fig_01 a fig_09\n")
