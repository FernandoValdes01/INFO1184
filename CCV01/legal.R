# Pregunta 1
# a) cargar archivo
df <- read.csv(
  "~/Nextcloud/informatica/7mo-Semestre/inteligencia-de-negocios/control1/OnlineRetail2.csv",
  sep = ";",
  header = TRUE,
  stringsAsFactors = FALSE
)

# b) estructura dataset y variables presentes
str(df)

# c) dimensión dataset
dim(df)

# d) primeras 8 filas del dataset
head(df, 8)

# Pregunta 3

## a) Revenue = Quantity * UnitPrice
df$UnitPrice <- as.numeric(gsub(",", ".", df$UnitPrice))
df$Revenue <- df$Quantity * df$UnitPrice

## b) monto total generado por todas las ventas
total_ventas <- sum(df$Revenue, na.rm = TRUE)
cat("Total generado por todas las ventas:", total_ventas, "\n")

## c) total de registros del dataset
nro_registros <- nrow(df)
cat("Total de registros del dataset:", nro_registros, "\n")

## d) total de ventas reales usando InvoiceNo
nro_ventas <- length(unique(df$InvoiceNo))
cat("Total de ventas reales:", nro_ventas, "\n")

## e) comparación entre c y d
diferencia <- nro_registros - nro_ventas
registros_por_venta <- nro_registros / nro_ventas

cat("\nComparación entre registros y ventas reales:\n")
cat("Total de registros:", nro_registros, "\n")
cat("Total de ventas reales:", nro_ventas, "\n")
cat("Diferencia:", diferencia, "\n")
cat("Promedio de registros por venta:", registros_por_venta, "\n")

# Interpretación:
# El total de registros corresponde al número de filas del dataset.
# Cada fila representa una línea de detalle de una factura.
# El total de ventas reales se obtiene con los InvoiceNo únicos.
# Como una factura puede incluir varios productos, normalmente
# el número de registros es mayor que el número de ventas reales.

## f) ticket promedio por venta

### i) considerando número de registros
ticket_promedio_por_registro <- total_ventas / nro_registros
cat("\nTicket promedio por registro:", ticket_promedio_por_registro, "\n")

### ii) considerando número de ventas reales
ticket_promedio_por_venta_real <- total_ventas / nro_ventas
cat("Ticket promedio por venta real:", ticket_promedio_por_venta_real, "\n")

