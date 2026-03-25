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
## a) revenue = quantity * unit price
df$UnitPrice <- as.numeric(gsub(",", ".", df$UnitPrice))
df$Revenue <- df$Quantity * df$UnitPrice

## b) monto generado por todas las ventas  
total_ventas <- sum(df$Revenue, na.rm = TRUE)
print(total_ventas)

## c) total de registros dataset
nro_registros <- nrow(df)
print(nro_registros)

## d) nro total de ventas
nro_ventas <- length(unique(df$InvoiceNo))
print(nro_ventas)

## e) comparación entre c y d
cat("\nComparación:\n")
cat("- Total de registros:", nro_registros, "\n")
cat("- Total de ventas reales:", nro_ventas, "\n")
cat("Diferencia:", nro_registros - nro_ventas, "\n")

# El total de registros corresponde al número de filas del dataset.
# Cada fila representa una línea de detalle dentro de una factura.
# En una misma factura pueden existir varias líneas de productos,
# por eso hay muchos registros asociados a un mismo InvoiceNo.

## f)
### i)
ticket_promedio_por_registro <- total_ventas / nro_registros
print(ticket_promedio_por_registro)

### ii)
ticket_promedio_por_venta_real <- total_ventas / nro_ventas
print(ticket_promedio_por_venta_real)

