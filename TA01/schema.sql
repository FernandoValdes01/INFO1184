PRAGMA foreign_keys = ON;

CREATE TABLE region (
    region_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE ciudad (
    ciudad_id INTEGER PRIMARY KEY,
    region_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    UNIQUE (region_id, nombre),
    FOREIGN KEY (region_id) REFERENCES region(region_id)
);

CREATE TABLE segmento_publico (
    segmento_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT NOT NULL
);

CREATE TABLE vino (
    vino_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    estilo TEXT NOT NULL CHECK (estilo IN ('Tinto', 'Blanco')),
    variedad_uva TEXT NOT NULL,
    botella_ml INTEGER NOT NULL CHECK (botella_ml > 0),
    costo_unitario NUMERIC NOT NULL CHECK (costo_unitario > 0),
    precio_lista NUMERIC NOT NULL CHECK (precio_lista > 0),
    graduacion NUMERIC NOT NULL CHECK (graduacion > 0)
);

CREATE TABLE alianza (
    alianza_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL,
    contacto TEXT NOT NULL,
    beneficio TEXT NOT NULL
);

CREATE TABLE feria (
    feria_id INTEGER PRIMARY KEY,
    ciudad_id INTEGER NOT NULL,
    nombre TEXT NOT NULL UNIQUE,
    recinto TEXT NOT NULL,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT NOT NULL,
    aforo_estimado INTEGER NOT NULL CHECK (aforo_estimado > 0),
    publico_objetivo TEXT NOT NULL,
    FOREIGN KEY (ciudad_id) REFERENCES ciudad(ciudad_id)
);

CREATE TABLE feria_alianza (
    feria_id INTEGER NOT NULL,
    alianza_id INTEGER NOT NULL,
    canal_promocion TEXT NOT NULL,
    aporte_estimado NUMERIC NOT NULL CHECK (aporte_estimado >= 0),
    PRIMARY KEY (feria_id, alianza_id),
    FOREIGN KEY (feria_id) REFERENCES feria(feria_id),
    FOREIGN KEY (alianza_id) REFERENCES alianza(alianza_id)
);

CREATE TABLE stand (
    stand_id INTEGER PRIMARY KEY,
    feria_id INTEGER NOT NULL,
    codigo TEXT NOT NULL UNIQUE,
    ubicacion TEXT NOT NULL,
    tamano_m2 NUMERIC NOT NULL CHECK (tamano_m2 > 0),
    costo_diario NUMERIC NOT NULL CHECK (costo_diario > 0),
    FOREIGN KEY (feria_id) REFERENCES feria(feria_id)
);

CREATE TABLE inventario_feria (
    inventario_id INTEGER PRIMARY KEY,
    feria_id INTEGER NOT NULL,
    vino_id INTEGER NOT NULL,
    botellas_planificadas INTEGER NOT NULL CHECK (botellas_planificadas >= 0),
    botellas_recibidas INTEGER NOT NULL CHECK (botellas_recibidas >= 0),
    botellas_vendidas INTEGER NOT NULL DEFAULT 0 CHECK (botellas_vendidas >= 0),
    stock_cierre INTEGER NOT NULL DEFAULT 0 CHECK (stock_cierre >= 0),
    UNIQUE (feria_id, vino_id),
    FOREIGN KEY (feria_id) REFERENCES feria(feria_id),
    FOREIGN KEY (vino_id) REFERENCES vino(vino_id)
);

CREATE TABLE visitante (
    visitante_id INTEGER PRIMARY KEY,
    feria_id INTEGER NOT NULL,
    segmento_id INTEGER NOT NULL,
    ciudad_origen_id INTEGER NOT NULL,
    fecha_visita TEXT NOT NULL,
    acepta_contacto INTEGER NOT NULL CHECK (acepta_contacto IN (0, 1)),
    interes_vino_id INTEGER,
    FOREIGN KEY (feria_id) REFERENCES feria(feria_id),
    FOREIGN KEY (segmento_id) REFERENCES segmento_publico(segmento_id),
    FOREIGN KEY (ciudad_origen_id) REFERENCES ciudad(ciudad_id),
    FOREIGN KEY (interes_vino_id) REFERENCES vino(vino_id)
);

CREATE TABLE degustacion (
    degustacion_id INTEGER PRIMARY KEY,
    visitante_id INTEGER NOT NULL,
    stand_id INTEGER NOT NULL,
    vino_id INTEGER NOT NULL,
    puntaje INTEGER NOT NULL CHECK (puntaje BETWEEN 1 AND 5),
    intencion_compra INTEGER NOT NULL CHECK (intencion_compra BETWEEN 1 AND 5),
    comentarios TEXT,
    FOREIGN KEY (visitante_id) REFERENCES visitante(visitante_id),
    FOREIGN KEY (stand_id) REFERENCES stand(stand_id),
    FOREIGN KEY (vino_id) REFERENCES vino(vino_id)
);

CREATE TABLE venta (
    venta_id INTEGER PRIMARY KEY,
    feria_id INTEGER NOT NULL,
    stand_id INTEGER NOT NULL,
    visitante_id INTEGER,
    fecha_hora TEXT NOT NULL,
    medio_pago TEXT NOT NULL CHECK (medio_pago IN ('Tarjeta', 'Efectivo', 'Transferencia')),
    monto_bruto NUMERIC NOT NULL CHECK (monto_bruto >= 0),
    descuento NUMERIC NOT NULL CHECK (descuento >= 0),
    monto_neto NUMERIC NOT NULL CHECK (monto_neto >= 0),
    FOREIGN KEY (feria_id) REFERENCES feria(feria_id),
    FOREIGN KEY (stand_id) REFERENCES stand(stand_id),
    FOREIGN KEY (visitante_id) REFERENCES visitante(visitante_id)
);

CREATE TABLE detalle_venta (
    detalle_venta_id INTEGER PRIMARY KEY,
    venta_id INTEGER NOT NULL,
    vino_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC NOT NULL CHECK (precio_unitario > 0),
    subtotal NUMERIC NOT NULL CHECK (subtotal > 0),
    FOREIGN KEY (venta_id) REFERENCES venta(venta_id),
    FOREIGN KEY (vino_id) REFERENCES vino(vino_id)
);

CREATE INDEX idx_ciudad_region ON ciudad(region_id);
CREATE INDEX idx_feria_ciudad ON feria(ciudad_id);
CREATE INDEX idx_stand_feria ON stand(feria_id);
CREATE INDEX idx_inventario_feria ON inventario_feria(feria_id);
CREATE INDEX idx_visitante_feria ON visitante(feria_id);
CREATE INDEX idx_visitante_segmento ON visitante(segmento_id);
CREATE INDEX idx_degustacion_visitante ON degustacion(visitante_id);
CREATE INDEX idx_venta_feria ON venta(feria_id);
CREATE INDEX idx_detalle_venta_venta ON detalle_venta(venta_id);
