# ==========================================
# Control 1 - Pregunta 2
# Archivo: pregunta2.r
# ==========================================

# a) Definicion de KPI y su importancia en Inteligencia de Negocios
#
# Un KPI (Key Performance Indicator) es una metrica cuantificable que permite
# medir el rendimiento de un proceso, area o estrategia de negocio en relacion
# con un objetivo especifico. Los KPI traducen datos operacionales en indicadores
# concretos que facilitan la toma de decisiones.
#
# Su importancia en Inteligencia de Negocios radica en que permiten:
# - Monitorear el desempeno del negocio de forma objetiva y medible.
# - Identificar tendencias, oportunidades y problemas a tiempo.
# - Alinear las acciones operativas con los objetivos estrategicos.
# - Facilitar la toma de decisiones basada en datos (data-driven).
# - Evaluar si las estrategias implementadas estan generando los resultados esperados.
#
# En el contexto de BI, los KPI son el puente entre los datos crudos y la
# informacion accionable para la gestion empresarial.

# b) Tres KPI formulados para el dataset OnlineRetail2
#
# KPI 1: Revenue (Ingreso por transaccion)
#   Formula: Revenue = Quantity * UnitPrice
#   Objetivo: Medir el ingreso generado por cada linea de venta.
#   Utilidad: Permite identificar que productos y transacciones generan
#   mayor valor monetario para la empresa.
#
# KPI 2: Ticket Promedio por Venta
#   Formula: Ticket Promedio = Total Revenue / Numero de ventas unicas
#   Objetivo: Medir el ingreso promedio que genera cada factura (venta).
#   Utilidad: Permite evaluar el valor promedio de cada transaccion comercial,
#   lo que ayuda a definir estrategias de upselling o cross-selling.
#
# KPI 3: Numero de Clientes Unicos
#   Formula: Clientes Unicos = length(unique(CustomerID))
#   Objetivo: Medir la base de clientes activos en el periodo.
#   Utilidad: Permite evaluar el alcance comercial de la empresa y monitorear
#   la retencion y captacion de clientes a lo largo del tiempo.
