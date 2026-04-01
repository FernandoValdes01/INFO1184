# ============================================================
# Control 2 - INFO1184 - Pregunta 2
# Agrupamiento Aglomerativo Jerarquico con R
# Datos: X = [23.11, -3.33, 1.30, 29.20, -1.57, 34.10,
#             -8.90, -3.40, 9.09, 3.03]
# Norma L1 (Manhattan)
# ============================================================
# INSTRUCCION: Ejecutar desde RStudio o terminal con:
#   Rscript pregunta2.R
# Las imagenes se guardaran en la carpeta "Imagenes/".
# ============================================================

# --- Crear carpeta Imagenes si no existe ---
if (!dir.exists("Imagenes")) {
  dir.create("Imagenes")
  cat("Carpeta 'Imagenes' creada.\n")
}

# --- Datos ---
X <- c(23.11, -3.33, 1.30, 29.20, -1.57, 34.10, -8.90, -3.40, 9.09, 3.03)
names(X) <- paste0("x", 1:10)

# Etiquetas con valores para mejor lectura
labels_val <- paste0("x", 1:10, "(", X, ")")

# Calcular matriz de distancias L1 (Manhattan)
d <- dist(X, method = "manhattan")

# ============================================================
# a) Dendrograma basico
# ============================================================
hc_single <- hclust(d, method = "single")

png("Imagenes/dendro_basico.png", width = 900, height = 600, res = 120)
plot(hc_single, labels = labels_val, main = "Dendrograma - Single Linkage (L1)",
     xlab = "Datos", ylab = "Distancia L1 (Manhattan)", hang = -1,
     cex = 0.8, col = "darkblue")
dev.off()
cat("Guardado: Imagenes/dendro_basico.png\n")

# ============================================================
# b) Particiones k=2 y k=3
# ============================================================

# --- k=2 ---
png("Imagenes/dendro_k2.png", width = 900, height = 600, res = 120)
plot(hc_single, labels = labels_val, main = "Dendrograma Single Linkage - Particion k=2",
     xlab = "Datos", ylab = "Distancia L1 (Manhattan)", hang = -1, cex = 0.8)
rect.hclust(hc_single, k = 2, border = c("red", "blue"))
legend("topright", legend = c("Cluster 1", "Cluster 2"),
       fill = c("red", "blue"), cex = 0.8)
dev.off()
cat("Guardado: Imagenes/dendro_k2.png\n")

# --- k=3 ---
png("Imagenes/dendro_k3.png", width = 900, height = 600, res = 120)
plot(hc_single, labels = labels_val, main = "Dendrograma Single Linkage - Particion k=3",
     xlab = "Datos", ylab = "Distancia L1 (Manhattan)", hang = -1, cex = 0.8)
rect.hclust(hc_single, k = 3, border = c("red", "blue", "green"))
legend("topright", legend = c("Cluster 1", "Cluster 2", "Cluster 3"),
       fill = c("red", "blue", "green"), cex = 0.8)
dev.off()
cat("Guardado: Imagenes/dendro_k3.png\n")

# Mostrar asignaciones
cat("\n=== Asignacion de clusters k=2 ===\n")
clusters_k2 <- cutree(hc_single, k = 2)
for (i in 1:length(X)) {
  cat(sprintf("  x%d = %6.2f -> Cluster %d\n", i, X[i], clusters_k2[i]))
}

cat("\n=== Asignacion de clusters k=3 ===\n")
clusters_k3 <- cutree(hc_single, k = 3)
for (i in 1:length(X)) {
  cat(sprintf("  x%d = %6.2f -> Cluster %d\n", i, X[i], clusters_k3[i]))
}

# ============================================================
# c) Tres dendrogramas: single, complete, average
# ============================================================

hc_complete <- hclust(d, method = "complete")
hc_average  <- hclust(d, method = "average")

# 1) Single Linkage
png("Imagenes/dendro_single.png", width = 900, height = 600, res = 120)
plot(hc_single, labels = labels_val,
     main = "1) Single Linkage (Enlace Simple)",
     xlab = "Datos", ylab = "Distancia L1", hang = -1, cex = 0.8)
rect.hclust(hc_single, k = 2, border = c("red", "blue"))
dev.off()
cat("Guardado: Imagenes/dendro_single.png\n")

# 2) Complete Linkage
png("Imagenes/dendro_complete.png", width = 900, height = 600, res = 120)
plot(hc_complete, labels = labels_val,
     main = "2) Complete Linkage (Enlace Completo)",
     xlab = "Datos", ylab = "Distancia L1", hang = -1, cex = 0.8)
rect.hclust(hc_complete, k = 2, border = c("red", "blue"))
dev.off()
cat("Guardado: Imagenes/dendro_complete.png\n")

# 3) Average Linkage
png("Imagenes/dendro_average.png", width = 900, height = 600, res = 120)
plot(hc_average, labels = labels_val,
     main = "3) Average Linkage (Enlace Promedio)",
     xlab = "Datos", ylab = "Distancia L1", hang = -1, cex = 0.8)
rect.hclust(hc_average, k = 2, border = c("red", "blue"))
dev.off()
cat("Guardado: Imagenes/dendro_average.png\n")

# Comparativa en una sola imagen
png("Imagenes/dendro_comparacion.png", width = 1200, height = 500, res = 120)
par(mfrow = c(1, 3), mar = c(5, 4, 3, 1))

plot(hc_single, labels = labels_val, main = "Single Linkage",
     xlab = "", ylab = "Distancia L1", hang = -1, cex = 0.65)
rect.hclust(hc_single, k = 2, border = c("red", "blue"))

plot(hc_complete, labels = labels_val, main = "Complete Linkage",
     xlab = "", ylab = "Distancia L1", hang = -1, cex = 0.65)
rect.hclust(hc_complete, k = 2, border = c("red", "blue"))

plot(hc_average, labels = labels_val, main = "Average Linkage",
     xlab = "", ylab = "Distancia L1", hang = -1, cex = 0.65)
rect.hclust(hc_average, k = 2, border = c("red", "blue"))

dev.off()
cat("Guardado: Imagenes/dendro_comparacion.png\n")

cat("\n=== Orden de fusion - Single ===\n")
print(hc_single$merge)
cat("Alturas:", hc_single$height, "\n")

cat("\n=== Orden de fusion - Complete ===\n")
print(hc_complete$merge)
cat("Alturas:", hc_complete$height, "\n")

cat("\n=== Orden de fusion - Average ===\n")
print(hc_average$merge)
cat("Alturas:", hc_average$height, "\n")

cat("\n*** Script ejecutado exitosamente ***\n")
cat("Directorio de trabajo:", getwd(), "\n")
cat("Imagenes generadas en carpeta 'Imagenes/':\n")
print(list.files("Imagenes", pattern = "dendro_.*\\.png"))