# ============================================
# Control 1 - INFO1184
# Dataset: OnlineRetail2.csv
# ============================================

# Limpiar entorno
rm(list = ls())

# --------------------------------------------
# Pregunta 1
# --------------------------------------------

# a) Cargar archivo CSV con separador ";"
df <- read.csv(
  "OnlineRetail2.csv",
  sep = ";",
  header = TRUE,
  stringsAsFactors = FALSE
)

# Corrección importante:
# UnitPrice viene como texto y con coma decimal, por ejemplo "2,55".
# Se reemplaza la coma por punto y luego se convierte a numérico.
df$UnitPrice <- as.numeric(gsub(",", ".", df$UnitPrice))

# Si quieres convertir InvoiceDate a fecha/hora, puedes hacerlo así:
# df$InvoiceDate <- as.POSIXct(df$InvoiceDate, format = "%d-%m-%Y %H:%M")

# b) Mostrar estructura del dataset
str(df)

# Descripción de tipos de variables:
# - InvoiceNo   : carácter
# - StockCode   : carácter
# - Description : carácter
# - Quantity    : entero
# - InvoiceDate : carácter
# - UnitPrice   : numérico
# - CustomerID  : entero
# - Country     : carácter

# c) Dimensión del dataset
dim(df)

# También por separado
n_filas <- nrow(df)
n_columnas <- ncol(df)

cat("Número de filas:", n_filas, "\n")
cat("Número de columnas:", n_columnas, "\n")

# d) Imprimir las 8 primeras filas
head(df, 8)


# --------------------------------------------
# Pregunta 2
# --------------------------------------------

# a) Definición de KPI (para el informe)
# Un KPI (Key Performance Indicator) es un indicador clave de desempeño
# que permite medir cuantitativamente el cumplimiento de un objetivo.
# En Inteligencia de Negocios es importante porque ayuda a monitorear
# resultados, detectar problemas, evaluar rendimiento y apoyar la toma
# de decisiones basadas en datos.

# b) Tres KPI propuestos para este dataset:
# 1. Revenue total: total de ingresos generados
# 2. Número de ventas reales: cantidad de facturas únicas
# 3. Ticket promedio por venta: ingreso promedio por factura


# --------------------------------------------
# Pregunta 3
# --------------------------------------------

# a) Crear nueva variable KPI llamada Revenue
df$Revenue <- df$Quantity * df$UnitPrice

# Verificar estructura actualizada
str(df)

# b) KPI: total generado por todas las ventas
total_ventas <- sum(df$Revenue, na.rm = TRUE)
cat("Total generado por todas las ventas (Revenue total):", total_ventas, "\n")

# c) KPI: total de registros del dataset respecto al total de transacciones
total_registros <- nrow(df)
cat("Total de registros del dataset:", total_registros, "\n")

# d) KPI: número total de ventas reales usando InvoiceNo
ventas_reales <- length(unique(df$InvoiceNo))
cat("Número total de ventas reales (facturas únicas):", ventas_reales, "\n")

# e) Comparación entre c y d
cat("\nComparación:\n")
cat("- Total de registros:", total_registros, "\n")
cat("- Total de ventas reales:", ventas_reales, "\n")
cat("Diferencia:", total_registros - ventas_reales, "\n")

# Explicación:
# El total de registros corresponde al número de filas del dataset.
# Cada fila representa una línea de detalle de producto dentro de una factura.
# En cambio, las ventas reales corresponden al número de facturas únicas
# (InvoiceNo). Por eso el número de registros es mayor que el número de
# ventas reales.

# f) Calcular ticket promedio por venta
# i) Considerando número de registros
ticket_promedio_por_registro <- total_ventas / total_registros
cat("\nTicket promedio considerando número de registros:", ticket_promedio_por_registro, "\n")

# ii) Considerando número de ventas reales
ticket_promedio_por_venta_real <- total_ventas / ventas_reales
cat("Ticket promedio considerando ventas reales:", ticket_promedio_por_venta_real, "\n")


# --------------------------------------------
# Resumen final
# --------------------------------------------
cat("\n========== RESUMEN ==========\n")
cat("Dimensión del dataset:", nrow(df), "filas y", ncol(df), "columnas\n")
cat("Revenue total:", total_ventas, "\n")
cat("Total registros:", total_registros, "\n")
cat("Ventas reales (InvoiceNo únicos):", ventas_reales, "\n")
cat("Ticket promedio por registro:", ticket_promedio_por_registro, "\n")
cat("Ticket promedio por venta real:", ticket_promedio_por_venta_real, "\n")