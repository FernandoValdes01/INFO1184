# ==========================================
# Control 1 - Pregunta 1
# Archivo: pregunta1.r
# ==========================================

# Este bloque busca el archivo CSV en la carpeta actual o dentro de CC01.
archivo_csv <- if (file.exists("OnlineRetail2.csv")) {
  "OnlineRetail2.csv"
} else if (file.exists("CC01/OnlineRetail2.csv")) {
  "CC01/OnlineRetail2.csv"
} else {
  stop("No se encontro el archivo OnlineRetail2.csv")
}

# a) Cargar el archivo OnlineRetail2.csv usando los parametros adecuados.
df <- read.csv2(
  file = archivo_csv,
  header = TRUE,
  stringsAsFactors = FALSE
)

# b) Mostrar la estructura del dataset.
# str() permite ver el nombre de las variables, su tipo y algunos valores de ejemplo.
cat("Estructura del dataset:\n")
str(df)

# Descripcion breve de los tipos de variables presentes en el dataset.
cat("\nDescripcion de los tipos de variables:\n")
cat("- InvoiceNo: character (identificador de factura)\n")
cat("- StockCode: character (codigo del producto)\n")
cat("- Description: character (descripcion del producto)\n")
cat("- Quantity: integer (cantidad vendida)\n")
cat("- InvoiceDate: character (fecha y hora de la transaccion)\n")
cat("- UnitPrice: numeric (precio unitario)\n")
cat("- CustomerID: integer (identificador del cliente)\n")
cat("- Country: character (pais)\n")

# c) Indicar la dimension del dataset.
cat("\nDimension del dataset:\n")
cat("Filas:", nrow(df), "\n")
cat("Columnas:", ncol(df), "\n")

# d) Imprimir las 8 primeras filas del dataset.
cat("\nPrimeras 8 filas del dataset:\n")
print(head(df, 8))
