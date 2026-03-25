# ==========================================
# Control 1 - Pregunta 3
# Archivo: pregunta3.r
# ==========================================

# Cargar el dataset (reutilizando la logica de pregunta1.r)
archivo_csv <- if (file.exists("OnlineRetail2.csv")) {
  "OnlineRetail2.csv"
} else if (file.exists("CC01/OnlineRetail2.csv")) {
  "CC01/OnlineRetail2.csv"
} else {
  stop("No se encontro el archivo OnlineRetail2.csv")
}

df <- read.csv2(
  file = archivo_csv,
  header = TRUE,
  stringsAsFactors = FALSE
)

# a) Crear variable KPI: Revenue = Quantity * UnitPrice
df$Revenue <- df$Quantity * df$UnitPrice
cat("a) Variable Revenue creada (Quantity * UnitPrice)\n")
cat("Primeras 8 filas con Revenue:\n")
print(head(df[, c("InvoiceNo", "Description", "Quantity", "UnitPrice", "Revenue")], 8))

# b) KPI: Total generado por todas las ventas (suma de Revenue)
total_revenue <- sum(df$Revenue, na.rm = TRUE)
cat("\nb) Total generado por todas las ventas (Total Revenue):", total_revenue, "\n")

# c) KPI: Total de registros del dataset (total de transacciones)
total_registros <- nrow(df)
cat("\nc) Total de registros del dataset:", total_registros, "\n")

# d) KPI: Numero total de ventas reales (facturas unicas por InvoiceNo)
total_ventas_reales <- length(unique(df$InvoiceNo))
cat("\nd) Numero total de ventas reales (facturas unicas):", total_ventas_reales, "\n")

# e) Comparacion entre c) y d)
cat("\ne) Comparacion entre total de registros y ventas reales:\n")
cat("   Total de registros (c):", total_registros, "\n")
cat("   Ventas reales unicas (d):", total_ventas_reales, "\n")
cat("   Diferencia:", total_registros - total_ventas_reales, "\n")
cat("\n   Discusion: El total de registros (", total_registros, ") es mucho mayor que el\n")
cat("   numero de ventas reales (", total_ventas_reales, "). Esto se debe a que cada\n")
cat("   factura (InvoiceNo) puede contener multiples lineas de productos. Es decir,\n")
cat("   un mismo numero de factura aparece repetido en varias filas porque cada fila\n")
cat("   representa un producto distinto dentro de la misma venta. Por lo tanto, el\n")
cat("   total de registros cuenta lineas de detalle, mientras que las ventas reales\n")
cat("   cuentan transacciones comerciales unicas.\n")

# f) Ticket promedio por venta
# i) Usando numero de registros
ticket_por_registro <- total_revenue / total_registros
cat("\nf) Ticket promedio por venta:\n")
cat("   i) Usando numero de registros:", round(ticket_por_registro, 2), "\n")

# ii) Usando numero de ventas reales (facturas unicas)
ticket_por_venta_real <- total_revenue / total_ventas_reales
cat("   ii) Usando numero de ventas reales:", round(ticket_por_venta_real, 2), "\n")
cat("\n   El ticket promedio calculado con ventas reales es mayor porque divide el\n")
cat("   ingreso total entre un numero menor (facturas unicas vs lineas de detalle).\n")
cat("   El indicador ii) es mas representativo del valor promedio de cada transaccion\n")
cat("   comercial real del cliente.\n")
