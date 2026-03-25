window.dbEvidence = {
  "generated_at": "2026-03-25T17:59:18",
  "total_records": 345,
  "table_counts": [
    {
      "tabla": "region",
      "registros": 5
    },
    {
      "tabla": "ciudad",
      "registros": 10
    },
    {
      "tabla": "segmento_publico",
      "registros": 6
    },
    {
      "tabla": "vino",
      "registros": 2
    },
    {
      "tabla": "alianza",
      "registros": 4
    },
    {
      "tabla": "feria",
      "registros": 6
    },
    {
      "tabla": "feria_alianza",
      "registros": 12
    },
    {
      "tabla": "stand",
      "registros": 12
    },
    {
      "tabla": "inventario_feria",
      "registros": 12
    },
    {
      "tabla": "visitante",
      "registros": 84
    },
    {
      "tabla": "degustacion",
      "registros": 84
    },
    {
      "tabla": "venta",
      "registros": 48
    },
    {
      "tabla": "detalle_venta",
      "registros": 60
    }
  ],
  "schema_excerpt": [
    {
      "name": "detalle_venta",
      "sql": "CREATE TABLE detalle_venta (\n    detalle_venta_id INTEGER PRIMARY KEY,\n    venta_id INTEGER NOT NULL,\n    vino_id INTEGER NOT NULL,\n    cantidad INTEGER NOT NULL CHECK (cantidad > 0),\n    precio_unitario NUMERIC NOT NULL CHECK (precio_unitario > 0),\n    subtotal NUMERIC NOT NULL CHECK (subtotal > 0),\n    FOREIGN KEY (venta_id) REFERENCES venta(venta_id),\n    FOREIGN KEY (vino_id) REFERENCES vino(vino_id)\n)"
    },
    {
      "name": "feria",
      "sql": "CREATE TABLE feria (\n    feria_id INTEGER PRIMARY KEY,\n    ciudad_id INTEGER NOT NULL,\n    nombre TEXT NOT NULL UNIQUE,\n    recinto TEXT NOT NULL,\n    fecha_inicio TEXT NOT NULL,\n    fecha_fin TEXT NOT NULL,\n    aforo_estimado INTEGER NOT NULL CHECK (aforo_estimado > 0),\n    publico_objetivo TEXT NOT NULL,\n    FOREIGN KEY (ciudad_id) REFERENCES ciudad(ciudad_id)\n)"
    },
    {
      "name": "venta",
      "sql": "CREATE TABLE venta (\n    venta_id INTEGER PRIMARY KEY,\n    feria_id INTEGER NOT NULL,\n    stand_id INTEGER NOT NULL,\n    visitante_id INTEGER,\n    fecha_hora TEXT NOT NULL,\n    medio_pago TEXT NOT NULL CHECK (medio_pago IN ('Tarjeta', 'Efectivo', 'Transferencia')),\n    monto_bruto NUMERIC NOT NULL CHECK (monto_bruto >= 0),\n    descuento NUMERIC NOT NULL CHECK (descuento >= 0),\n    monto_neto NUMERIC NOT NULL CHECK (monto_neto >= 0),\n    FOREIGN KEY (feria_id) REFERENCES feria(feria_id),\n    FOREIGN KEY (stand_id) REFERENCES stand(stand_id),\n    FOREIGN KEY (visitante_id) REFERENCES visitante(visitante_id)\n)"
    },
    {
      "name": "visitante",
      "sql": "CREATE TABLE visitante (\n    visitante_id INTEGER PRIMARY KEY,\n    feria_id INTEGER NOT NULL,\n    segmento_id INTEGER NOT NULL,\n    ciudad_origen_id INTEGER NOT NULL,\n    fecha_visita TEXT NOT NULL,\n    acepta_contacto INTEGER NOT NULL CHECK (acepta_contacto IN (0, 1)),\n    interes_vino_id INTEGER,\n    FOREIGN KEY (feria_id) REFERENCES feria(feria_id),\n    FOREIGN KEY (segmento_id) REFERENCES segmento_publico(segmento_id),\n    FOREIGN KEY (ciudad_origen_id) REFERENCES ciudad(ciudad_id),\n    FOREIGN KEY (interes_vino_id) REFERENCES vino(vino_id)\n)"
    }
  ],
  "fair_summary": [
    {
      "feria": "ExpoVino Santiago 2026",
      "ciudad": "Santiago",
      "visitantes": 14,
      "ventas": 8,
      "ingresos": 296654.0,
      "botellas": 36
    },
    {
      "feria": "Muestra Enologica Concepcion 2026",
      "ciudad": "Concepcion",
      "visitantes": 14,
      "ventas": 8,
      "ingresos": 296654.0,
      "botellas": 36
    },
    {
      "feria": "Festival del Vino Talca 2026",
      "ciudad": "Talca",
      "visitantes": 14,
      "ventas": 8,
      "ingresos": 296654.0,
      "botellas": 36
    },
    {
      "feria": "Feria del Pacifico 2026",
      "ciudad": "Vina del Mar",
      "visitantes": 14,
      "ventas": 8,
      "ingresos": 293980.0,
      "botellas": 36
    },
    {
      "feria": "Feria del Valle Curico 2026",
      "ciudad": "Curico",
      "visitantes": 14,
      "ventas": 8,
      "ingresos": 293980.0,
      "botellas": 36
    },
    {
      "feria": "Expo Sabores Temuco 2026",
      "ciudad": "Temuco",
      "visitantes": 14,
      "ventas": 8,
      "ingresos": 293980.0,
      "botellas": 36
    }
  ],
  "sample_sales": [
    {
      "venta_id": 1,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-18T12:00",
      "medio_pago": "Tarjeta",
      "monto_neto": 46552
    },
    {
      "venta_id": 2,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-19T13:00",
      "medio_pago": "Efectivo",
      "monto_neto": 26700
    },
    {
      "venta_id": 3,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-20T14:00",
      "medio_pago": "Transferencia",
      "monto_neto": 32800
    },
    {
      "venta_id": 4,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-18T15:00",
      "medio_pago": "Tarjeta",
      "monto_neto": 42275
    },
    {
      "venta_id": 5,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-19T16:00",
      "medio_pago": "Efectivo",
      "monto_neto": 46552
    },
    {
      "venta_id": 6,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-20T17:00",
      "medio_pago": "Transferencia",
      "monto_neto": 26700
    },
    {
      "venta_id": 7,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-18T18:00",
      "medio_pago": "Tarjeta",
      "monto_neto": 32800
    },
    {
      "venta_id": 8,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-19T19:00",
      "medio_pago": "Efectivo",
      "monto_neto": 42275
    }
  ]
};
