window.dbEvidence = {
  "generated_at": "2026-03-28T22:51:32",
  "total_records": 458,
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
      "registros": 114
    },
    {
      "tabla": "degustacion",
      "registros": 114
    },
    {
      "tabla": "venta",
      "registros": 66
    },
    {
      "tabla": "detalle_venta",
      "registros": 95
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
      "feria": "Festival del Vino Talca 2026",
      "ciudad": "Talca",
      "visitantes": 26,
      "ventas": 16,
      "ingresos": 684647.9,
      "botellas": 74
    },
    {
      "feria": "Muestra Enologica Concepcion 2026",
      "ciudad": "Concepcion",
      "visitantes": 24,
      "ventas": 14,
      "ingresos": 569395.2,
      "botellas": 64
    },
    {
      "feria": "ExpoVino Santiago 2026",
      "ciudad": "Santiago",
      "visitantes": 20,
      "ventas": 12,
      "ingresos": 494777.92,
      "botellas": 55
    },
    {
      "feria": "Feria del Pacifico 2026",
      "ciudad": "Vina del Mar",
      "visitantes": 16,
      "ventas": 9,
      "ingresos": 347921.68,
      "botellas": 41
    },
    {
      "feria": "Feria del Valle Curico 2026",
      "ciudad": "Curico",
      "visitantes": 15,
      "ventas": 8,
      "ingresos": 290279.92,
      "botellas": 37
    },
    {
      "feria": "Expo Sabores Temuco 2026",
      "ciudad": "Temuco",
      "visitantes": 13,
      "ventas": 7,
      "ingresos": 251587.32,
      "botellas": 34
    }
  ],
  "sample_sales": [
    {
      "venta_id": 1,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-18T11:07",
      "medio_pago": "Tarjeta",
      "monto_neto": 69652.8
    },
    {
      "venta_id": 2,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-19T12:18",
      "medio_pago": "Efectivo",
      "monto_neto": 34531.84
    },
    {
      "venta_id": 3,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-20T13:29",
      "medio_pago": "Transferencia",
      "monto_neto": 28336
    },
    {
      "venta_id": 4,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-18T14:40",
      "medio_pago": "Tarjeta",
      "monto_neto": 19936
    },
    {
      "venta_id": 5,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-19T15:51",
      "medio_pago": "Efectivo",
      "monto_neto": 29904
    },
    {
      "venta_id": 6,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-20T16:02",
      "medio_pago": "Transferencia",
      "monto_neto": 75801.6
    },
    {
      "venta_id": 7,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-18T17:13",
      "medio_pago": "Tarjeta",
      "monto_neto": 29904
    },
    {
      "venta_id": 8,
      "feria": "ExpoVino Santiago 2026",
      "fecha_hora": "2026-04-19T18:24",
      "medio_pago": "Efectivo",
      "monto_neto": 29120
    }
  ]
};
