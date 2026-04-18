# ============================================================
# Control 3 - INFO1184 - Pregunta 2
# K-Medias con R
# ============================================================

# --- Datos X en R^2, i=7 ---
x1 <- c(1.5, -1.88)
x2 <- c(26.5, 100.55)
x3 <- c(-1.5, -6.66)
x4 <- c(29.7, 89.66)
x5 <- c(3.1416, 2.7181)
x6 <- c(8.8, -7.5)
x7 <- c(-8.11, -7.56)

datos <- data.frame(
  X1 = c(1.5, 26.5, -1.5, 29.7, 3.1416, 8.8, -8.11),
  X2 = c(-1.88, 100.55, -6.66, 89.66, 2.7181, -7.5, -7.56)
)
rownames(datos) <- paste0("x", 1:7)

cat("=== Datos ===\n")
print(datos)

# --- a) Grafico de dispersion ---
pdf("dispersion.pdf", width = 7, height = 6)
plot(datos$X1, datos$X2,
     main = "Dispersion de los datos X",
     xlab = expression(X[1]), ylab = expression(X[2]),
     pch = 19, col = "black", cex = 1.3)
text(datos$X1, datos$X2, labels = rownames(datos),
     pos = 4, cex = 0.8, offset = 0.5)
grid()
dev.off()
cat("\n[OK] dispersion.pdf generado\n")

# --- b) K-medias con k=2 ---
set.seed(42)
km2 <- kmeans(datos, centers = 2, nstart = 25)
cat("\n=== K-Medias k=2 ===\n")
cat("Asignaciones:", km2$cluster, "\n")
cat("Centros:\n")
print(km2$centers)

# Grafico k=2
colores_k2 <- c("red", "blue")
pdf("kmeans_k2.pdf", width = 7, height = 6)
plot(datos$X1, datos$X2,
     main = "K-Medias con k=2",
     xlab = expression(X[1]), ylab = expression(X[2]),
     pch = 19, col = colores_k2[km2$cluster], cex = 1.3)
text(datos$X1, datos$X2, labels = rownames(datos),
     pos = 4, cex = 0.8, offset = 0.5)
# Marcar centros
points(km2$centers[,1], km2$centers[,2],
       pch = 4, col = colores_k2, cex = 2.5, lwd = 3)
points(km2$centers[,1], km2$centers[,2],
       pch = 1, col = colores_k2, cex = 3, lwd = 2)
legend("topleft",
       legend = c(paste("Cluster 1 (centro:", round(km2$centers[1,1],2), ",", round(km2$centers[1,2],2), ")"),
                  paste("Cluster 2 (centro:", round(km2$centers[2,1],2), ",", round(km2$centers[2,2],2), ")")),
       col = colores_k2, pch = 19, cex = 0.7)
grid()
dev.off()
cat("[OK] kmeans_k2.pdf generado\n")

# --- b) K-medias con k=3 ---
set.seed(42)
km3 <- kmeans(datos, centers = 3, nstart = 25)
cat("\n=== K-Medias k=3 ===\n")
cat("Asignaciones:", km3$cluster, "\n")
cat("Centros:\n")
print(km3$centers)

# Grafico k=3
colores_k3 <- c("red", "blue", "darkgreen")
pdf("kmeans_k3.pdf", width = 7, height = 6)
plot(datos$X1, datos$X2,
     main = "K-Medias con k=3",
     xlab = expression(X[1]), ylab = expression(X[2]),
     pch = 19, col = colores_k3[km3$cluster], cex = 1.3)
text(datos$X1, datos$X2, labels = rownames(datos),
     pos = 4, cex = 0.8, offset = 0.5)
# Marcar centros
points(km3$centers[,1], km3$centers[,2],
       pch = 4, col = colores_k3, cex = 2.5, lwd = 3)
points(km3$centers[,1], km3$centers[,2],
       pch = 1, col = colores_k3, cex = 3, lwd = 2)
legend("topleft",
       legend = c(paste("Cluster 1 (centro:", round(km3$centers[1,1],2), ",", round(km3$centers[1,2],2), ")"),
                  paste("Cluster 2 (centro:", round(km3$centers[2,1],2), ",", round(km3$centers[2,2],2), ")"),
                  paste("Cluster 3 (centro:", round(km3$centers[3,1],2), ",", round(km3$centers[3,2],2), ")")),
       col = colores_k3, pch = 19, cex = 0.7)
grid()
dev.off()
cat("[OK] kmeans_k3.pdf generado\n")

# --- c) Imprimir centros ---
cat("\n========================================\n")
cat("CENTROS para k=2:\n")
print(km2$centers)
cat("\nCENTROS para k=3:\n")
print(km3$centers)
cat("========================================\n")
