\if :{?raw_schema}
\else
\set raw_schema public
\endif

CREATE SCHEMA IF NOT EXISTS :"raw_schema";
SET search_path TO :"raw_schema";

CREATE TABLE IF NOT EXISTS region (
    region_id integer PRIMARY KEY,
    nombre text NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ciudad (
    ciudad_id integer PRIMARY KEY,
    region_id integer NOT NULL REFERENCES region(region_id),
    nombre text NOT NULL,
    UNIQUE (region_id, nombre)
);

CREATE TABLE IF NOT EXISTS segmento_publico (
    segmento_id integer PRIMARY KEY,
    nombre text NOT NULL UNIQUE,
    descripcion text NOT NULL
);

CREATE TABLE IF NOT EXISTS vino (
    vino_id integer PRIMARY KEY,
    nombre text NOT NULL UNIQUE,
    estilo text NOT NULL CHECK (estilo IN ('Tinto', 'Blanco')),
    variedad_uva text NOT NULL,
    botella_ml integer NOT NULL CHECK (botella_ml > 0),
    costo_unitario numeric(12, 2) NOT NULL CHECK (costo_unitario > 0),
    precio_lista numeric(12, 2) NOT NULL CHECK (precio_lista > 0),
    graduacion numeric(4, 1) NOT NULL CHECK (graduacion > 0)
);

CREATE TABLE IF NOT EXISTS alianza (
    alianza_id integer PRIMARY KEY,
    nombre text NOT NULL UNIQUE,
    tipo text NOT NULL,
    contacto text NOT NULL,
    beneficio text NOT NULL
);

CREATE TABLE IF NOT EXISTS feria (
    feria_id integer PRIMARY KEY,
    ciudad_id integer NOT NULL REFERENCES ciudad(ciudad_id),
    nombre text NOT NULL UNIQUE,
    recinto text NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    aforo_estimado integer NOT NULL CHECK (aforo_estimado > 0),
    publico_objetivo text NOT NULL
);

CREATE TABLE IF NOT EXISTS feria_alianza (
    feria_id integer NOT NULL REFERENCES feria(feria_id),
    alianza_id integer NOT NULL REFERENCES alianza(alianza_id),
    canal_promocion text NOT NULL,
    aporte_estimado numeric(14, 2) NOT NULL CHECK (aporte_estimado >= 0),
    PRIMARY KEY (feria_id, alianza_id)
);

CREATE TABLE IF NOT EXISTS stand (
    stand_id integer PRIMARY KEY,
    feria_id integer NOT NULL REFERENCES feria(feria_id),
    codigo text NOT NULL UNIQUE,
    ubicacion text NOT NULL,
    tamano_m2 numeric(8, 2) NOT NULL CHECK (tamano_m2 > 0),
    costo_diario numeric(12, 2) NOT NULL CHECK (costo_diario > 0)
);

CREATE TABLE IF NOT EXISTS inventario_feria (
    inventario_id integer PRIMARY KEY,
    feria_id integer NOT NULL REFERENCES feria(feria_id),
    vino_id integer NOT NULL REFERENCES vino(vino_id),
    botellas_planificadas integer NOT NULL CHECK (botellas_planificadas >= 0),
    botellas_recibidas integer NOT NULL CHECK (botellas_recibidas >= 0),
    botellas_vendidas integer NOT NULL DEFAULT 0 CHECK (botellas_vendidas >= 0),
    stock_cierre integer NOT NULL DEFAULT 0 CHECK (stock_cierre >= 0),
    UNIQUE (feria_id, vino_id)
);

CREATE TABLE IF NOT EXISTS visitante (
    visitante_id integer PRIMARY KEY,
    feria_id integer NOT NULL REFERENCES feria(feria_id),
    segmento_id integer NOT NULL REFERENCES segmento_publico(segmento_id),
    ciudad_origen_id integer NOT NULL REFERENCES ciudad(ciudad_id),
    fecha_visita date NOT NULL,
    acepta_contacto boolean NOT NULL,
    interes_vino_id integer REFERENCES vino(vino_id)
);

CREATE TABLE IF NOT EXISTS degustacion (
    degustacion_id integer PRIMARY KEY,
    visitante_id integer NOT NULL REFERENCES visitante(visitante_id),
    stand_id integer NOT NULL REFERENCES stand(stand_id),
    vino_id integer NOT NULL REFERENCES vino(vino_id),
    puntaje integer NOT NULL CHECK (puntaje BETWEEN 1 AND 5),
    intencion_compra integer NOT NULL CHECK (intencion_compra BETWEEN 1 AND 5),
    comentarios text
);

CREATE TABLE IF NOT EXISTS venta (
    venta_id integer PRIMARY KEY,
    feria_id integer NOT NULL REFERENCES feria(feria_id),
    stand_id integer NOT NULL REFERENCES stand(stand_id),
    visitante_id integer REFERENCES visitante(visitante_id),
    fecha_hora timestamp without time zone NOT NULL,
    medio_pago text NOT NULL CHECK (medio_pago IN ('Tarjeta', 'Efectivo', 'Transferencia')),
    monto_bruto numeric(12, 2) NOT NULL CHECK (monto_bruto >= 0),
    descuento numeric(12, 2) NOT NULL CHECK (descuento >= 0),
    monto_neto numeric(12, 2) NOT NULL CHECK (monto_neto >= 0)
);

CREATE TABLE IF NOT EXISTS detalle_venta (
    detalle_venta_id integer PRIMARY KEY,
    venta_id integer NOT NULL REFERENCES venta(venta_id),
    vino_id integer NOT NULL REFERENCES vino(vino_id),
    cantidad integer NOT NULL CHECK (cantidad > 0),
    precio_unitario numeric(12, 2) NOT NULL CHECK (precio_unitario > 0),
    subtotal numeric(12, 2) NOT NULL CHECK (subtotal > 0)
);

CREATE INDEX IF NOT EXISTS idx_ciudad_region ON ciudad(region_id);
CREATE INDEX IF NOT EXISTS idx_feria_ciudad ON feria(ciudad_id);
CREATE INDEX IF NOT EXISTS idx_stand_feria ON stand(feria_id);
CREATE INDEX IF NOT EXISTS idx_inventario_feria ON inventario_feria(feria_id);
CREATE INDEX IF NOT EXISTS idx_visitante_feria ON visitante(feria_id);
CREATE INDEX IF NOT EXISTS idx_visitante_segmento ON visitante(segmento_id);
CREATE INDEX IF NOT EXISTS idx_degustacion_visitante ON degustacion(visitante_id);
CREATE INDEX IF NOT EXISTS idx_venta_feria ON venta(feria_id);
CREATE INDEX IF NOT EXISTS idx_detalle_venta_venta ON detalle_venta(venta_id);
