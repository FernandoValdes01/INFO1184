# ============================================================
# Control 4 - INFO1184
# Analisis de k-means para datos de vino (k = 2..15)
# ============================================================

set.seed(101)

wine <- read.csv("wine/wine.data", header = FALSE)

colnames(wine) <- c(
  "Class", "Alcohol", "MalicAcid", "Ash", "AlcalinityAsh", "Magnesium",
  "TotalPhenols", "Flavanoids", "NonflavanoidPhenols", "Proanthocyanins",
  "ColorIntensity", "Hue", "OD280_OD315", "Proline"
)

X_raw <- wine[, -1]
X <- scale(X_raw)

unscale_center <- function(center_scaled, x_scaled, x_raw) {
  attrs <- attributes(x_scaled)
  sweep(
    sweep(center_scaled, 2, attrs$`scaled:scale`, `*`),
    2,
    attrs$`scaled:center`,
    `+`
  )
}

ks <- 2:15
models <- vector("list", length(ks))
names(models) <- ks

metrics <- data.frame(
  k = ks,
  WSS = NA_real_,
  min_centroid_dist = NA_real_,
  mean_centroid_dist = NA_real_,
  min_cluster_size = NA_integer_,
  stringsAsFactors = FALSE
)

for (i in seq_along(ks)) {
  k <- ks[i]
  km <- kmeans(X, centers = k, nstart = 100, iter.max = 200)
  models[[as.character(k)]] <- km

  d <- as.matrix(dist(km$centers))
  d[d == 0] <- NA

  metrics$WSS[i] <- km$tot.withinss
  metrics$min_centroid_dist[i] <- min(d, na.rm = TRUE)
  metrics$mean_centroid_dist[i] <- mean(d, na.rm = TRUE)
  metrics$min_cluster_size[i] <- min(km$size)
}

metrics$WSS_drop <- c(NA, -diff(metrics$WSS))
metrics$WSS_drop_pct <- c(NA, 100 * (-diff(metrics$WSS) / metrics$WSS[-nrow(metrics)]))

write.csv(metrics, "cc4_metricas_k2_k15.csv", row.names = FALSE)

# Centroides para k = 3 (escala original para interpretacion)
km3 <- models[["3"]]
centers_k3_raw <- unscale_center(km3$centers, X, X_raw)
centers_k3_raw <- data.frame(cluster = paste0("C", 1:nrow(centers_k3_raw)), centers_k3_raw)
write.csv(centers_k3_raw, "cc4_centroides_k3_escala_original.csv", row.names = FALSE)

# ============================
# Graficos
# ============================

# 1) Metodo del codo (Pregunta 2)
pdf("cc4_elbow_wss.pdf", width = 7, height = 5)
plot(
  metrics$k, metrics$WSS,
  type = "b", pch = 19, col = "steelblue4", lwd = 2,
  xlab = "Número de clusters (k)",
  ylab = "WSS total",
  main = "Método del codo (k-means sobre wine estandarizado)"
)
abline(v = 3, lty = 2, lwd = 2, col = "firebrick")
text(3.15, max(metrics$WSS) * 0.95, "k = 3", col = "firebrick", pos = 4)
grid()
dev.off()

# 2) Diagnosticos basados en centroides (Pregunta 1)
pdf("cc4_diagnostico_dist_centroides.pdf", width = 7, height = 5)
plot(
  metrics$k, metrics$min_centroid_dist,
  type = "b", pch = 19, col = "darkgreen", lwd = 2,
  xlab = "Número de clusters (k)",
  ylab = "Distancia mínima entre centroides",
  main = "Separación mínima entre centroides"
)
abline(v = 3, lty = 2, lwd = 2, col = "firebrick")
grid()
dev.off()

pdf("cc4_diagnostico_tamano_cluster.pdf", width = 7, height = 5)
plot(
  metrics$k, metrics$min_cluster_size,
  type = "b", pch = 19, col = "darkorange3", lwd = 2,
  xlab = "Número de clusters (k)",
  ylab = "Tamaño del cluster más pequeño",
  main = "Fragmentación de grupos al aumentar k"
)
abline(v = 3, lty = 2, lwd = 2, col = "firebrick")
grid()
dev.off()

# 3) Visualizacion PCA para k seleccionados
pca <- prcomp(X, center = FALSE, scale. = FALSE)
scores <- pca$x[, 1:2]

project_centers <- function(centers_scaled, pca_obj) {
  centers_scaled %*% pca_obj$rotation[, 1:2]
}

k_show <- c(2, 3, 4, 7)

pdf("cc4_pca_k2_k3_k4_k7.pdf", width = 10, height = 8)
par(mfrow = c(2, 2), mar = c(4, 4, 3, 1))

for (k in k_show) {
  km <- models[[as.character(k)]]
  cols <- rainbow(k)

  plot(
    scores[, 1], scores[, 2],
    col = cols[km$cluster], pch = 19,
    xlab = "PC1", ylab = "PC2",
    main = paste("PCA + k-means (k =", k, ")")
  )

  centers_pc <- project_centers(km$centers, pca)
  points(centers_pc[, 1], centers_pc[, 2], pch = 8, cex = 2, lwd = 2)
  text(centers_pc[, 1], centers_pc[, 2], labels = paste0("C", 1:k), pos = 3, cex = 0.8)
  grid()
}

dev.off()

cat("Archivos generados:\n")
cat("- cc4_metricas_k2_k15.csv\n")
cat("- cc4_centroides_k3_escala_original.csv\n")
cat("- cc4_elbow_wss.pdf\n")
cat("- cc4_diagnostico_dist_centroides.pdf\n")
cat("- cc4_diagnostico_tamano_cluster.pdf\n")
cat("- cc4_pca_k2_k3_k4_k7.pdf\n")
