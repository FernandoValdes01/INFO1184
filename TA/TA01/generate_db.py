from __future__ import annotations

"""
Utilidad local e historica para regenerar el prototipo SQLite de TA01.

Este script no representa el flujo objetivo de analitica del subproyecto.
La implementacion objetivo pasa a PostgreSQL + dbt + Lightdash y las
credenciales del warehouse no se versionan en el repositorio.
"""

import csv
import json
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "ta01_feria_vinos.db"
SCHEMA_PATH = ROOT / "schema.sql"
LEGACY_DASHBOARD_JS_PATH = ROOT / "dashboard_data.js"
EVIDENCE_JS_PATH = ROOT / "anexos" / "db_evidence.js"
EXPORTS_DIR = ROOT / "exports"


def daterange(start_iso: str, end_iso: str) -> list[date]:
    start = date.fromisoformat(start_iso)
    end = date.fromisoformat(end_iso)
    days = (end - start).days
    return [start + timedelta(days=offset) for offset in range(days + 1)]


def write_js_assignment(path: Path, variable_name: str, payload: dict) -> None:
    path.write_text(
        f"window.{variable_name} = {json.dumps(payload, ensure_ascii=True, indent=2)};\n",
        encoding="utf-8",
    )


def write_legacy_dashboard_notice(path: Path) -> None:
    payload = {
        "status": "deprecated",
        "official_dashboard": "Lightdash",
        "project_directory_path": "/TA/TA01",
        "note": "El dashboard HTML/JS local fue descontinuado. El dashboard oficial debe construirse en Lightdash sobre dbt y PostgreSQL.",
    }
    write_js_assignment(path, "ta01DashboardDeprecated", payload)


def export_csv(path: Path, rows: list[sqlite3.Row]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow([row[key] for key in row.keys()])


def main() -> None:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_JS_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    regions = [
        (1, "Metropolitana"),
        (2, "Valparaiso"),
        (3, "Biobio"),
        (4, "Maule"),
        (5, "La Araucania"),
    ]
    ciudades = [
        (1, 1, "Santiago"),
        (2, 1, "Providencia"),
        (3, 2, "Valparaiso"),
        (4, 2, "Vina del Mar"),
        (5, 3, "Concepcion"),
        (6, 3, "Los Angeles"),
        (7, 4, "Talca"),
        (8, 4, "Curico"),
        (9, 5, "Temuco"),
        (10, 5, "Pucon"),
    ]
    segmentos = [
        (1, "Consumidor general", "Visitantes atraidos por degustaciones y compra inmediata."),
        (2, "Turista enologico", "Publico que busca experiencias locales y regalo premium."),
        (3, "Restaurante", "Comprador institucional enfocado en cartas y maridajes."),
        (4, "Hotel boutique", "Canal que compra volumen medio para atencion de huespedes."),
        (5, "Tienda especializada", "Revendedor con interes en etiquetas de nicho."),
        (6, "Club de vinos", "Comunidad que privilegia suscripciones y recompra mensual."),
    ]
    vinos = [
        (1, "Reserva Andes Carmenere", "Tinto", "Carmenere", 750, 4250, 8900, 13.5),
        (2, "Costa Blanca Sauvignon", "Blanco", "Sauvignon Blanc", 750, 3900, 8200, 12.5),
    ]
    alianzas = [
        (1, "Ruta del Vino Central", "Promocion territorial", "Paula Rojas", "Difusion digital y base de contactos del circuito."),
        (2, "Asociacion Gastronomica de Chile", "Canal horeca", "Matias Perez", "Acceso a restaurantes y demostraciones guiadas."),
        (3, "Red de Hoteles Boutique", "Turismo", "Valentina Diaz", "Venta cruzada con paquetes de estadia y degustacion."),
        (4, "Camara de Comercio Regional", "Relacion institucional", "Felipe Soto", "Gestion de ferias locales y auspicios."),
    ]
    ferias = [
        (1, 1, "ExpoVino Santiago 2026", "Estacion Mapocho", "2026-04-18", "2026-04-20", 1800, "Consumidor general y club de vinos"),
        (2, 4, "Feria del Pacifico 2026", "Casino de Vina", "2026-05-15", "2026-05-17", 1400, "Turistas y tiendas especializadas"),
        (3, 5, "Muestra Enologica Concepcion 2026", "Centro SurActivo", "2026-06-12", "2026-06-14", 1300, "Publico general y restaurantes"),
        (4, 8, "Feria del Valle Curico 2026", "Centro de Eventos Curico", "2026-08-07", "2026-08-09", 1200, "Turismo interno y horeca"),
        (5, 7, "Festival del Vino Talca 2026", "Alameda de Talca", "2026-09-11", "2026-09-13", 1500, "Consumidor general y hoteles"),
        (6, 9, "Expo Sabores Temuco 2026", "Centro Cultural Temuco", "2026-11-06", "2026-11-08", 1100, "Turistas y revendedores regionales"),
    ]

    conn.executemany("INSERT INTO region VALUES (?, ?)", regions)
    conn.executemany("INSERT INTO ciudad VALUES (?, ?, ?)", ciudades)
    conn.executemany("INSERT INTO segmento_publico VALUES (?, ?, ?)", segmentos)
    conn.executemany("INSERT INTO vino VALUES (?, ?, ?, ?, ?, ?, ?, ?)", vinos)
    conn.executemany("INSERT INTO alianza VALUES (?, ?, ?, ?, ?)", alianzas)
    conn.executemany("INSERT INTO feria VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ferias)

    ferias_alianzas = []
    for feria_id, *_ in ferias:
        base = (feria_id - 1) % len(alianzas) + 1
        combo = {base, ((feria_id + 1) % len(alianzas)) + 1}
        canales = ["Redes sociales", "Invitacion corporativa"]
        for offset, alianza_id in enumerate(sorted(combo)):
            aporte = 900000 + feria_id * 75000 + offset * 125000
            ferias_alianzas.append((feria_id, alianza_id, canales[offset], aporte))
    conn.executemany(
        "INSERT INTO feria_alianza (feria_id, alianza_id, canal_promocion, aporte_estimado) VALUES (?, ?, ?, ?)",
        ferias_alianzas,
    )

    stands = []
    stand_id = 1
    for feria_id, *_ in ferias:
        stands.append((stand_id, feria_id, f"F{feria_id:02d}-A", "Isla degustacion", 18.0, 145000))
        stand_id += 1
        stands.append((stand_id, feria_id, f"F{feria_id:02d}-B", "Isla ventas", 16.0, 138000))
        stand_id += 1
    conn.executemany(
        "INSERT INTO stand (stand_id, feria_id, codigo, ubicacion, tamano_m2, costo_diario) VALUES (?, ?, ?, ?, ?, ?)",
        stands,
    )

    inventarios = []
    inventario_id = 1
    for feria_id, *_ in ferias:
        for vino_id, _, estilo, *_rest in vinos:
            base_plan = 185 if estilo == "Tinto" else 170
            planificadas = base_plan + feria_id * 12
            recibidas = planificadas - 8
            inventarios.append((inventario_id, feria_id, vino_id, planificadas, recibidas, 0, recibidas))
            inventario_id += 1
    conn.executemany(
        """
        INSERT INTO inventario_feria (
            inventario_id, feria_id, vino_id, botellas_planificadas, botellas_recibidas,
            botellas_vendidas, stock_cierre
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        inventarios,
    )

    city_ids = [row[0] for row in ciudades]
    fair_stands = defaultdict(list)
    for row in stands:
        fair_stands[row[1]].append(row[0])

    visitors_by_fair: dict[int, list[int]] = defaultdict(list)
    visitantes = []
    degustaciones = []
    visitante_id = 1
    degustacion_id = 1
    comments = [
        "Solicita informacion de recompra.",
        "Interes alto en promociones por caja.",
        "Prefiere compra inmediata en feria.",
        "Valora la alianza gastronomica.",
        "Consulta por despacho nacional.",
    ]

    for feria in ferias:
        feria_id, _, _, _, fecha_inicio, fecha_fin, *_ = feria
        fechas = daterange(fecha_inicio, fecha_fin)
        tasting_stand, sales_stand = fair_stands[feria_id]

        for idx in range(14):
            segmento_id = ((feria_id + idx - 1) % len(segmentos)) + 1
            ciudad_origen_id = city_ids[(feria_id * 3 + idx) % len(city_ids)]
            fecha_visita = fechas[idx % len(fechas)].isoformat()
            acepta_contacto = 0 if idx % 4 == 0 else 1
            interes_vino_id = 1 if segmento_id in (1, 3, 5, 6) else 2
            if idx % 5 == 0:
                interes_vino_id = 2 if interes_vino_id == 1 else 1

            visitantes.append(
                (
                    visitante_id,
                    feria_id,
                    segmento_id,
                    ciudad_origen_id,
                    fecha_visita,
                    acepta_contacto,
                    interes_vino_id,
                )
            )
            visitors_by_fair[feria_id].append(visitante_id)

            puntaje = 3 + ((idx + feria_id) % 3)
            intencion = 2 + ((idx * 2 + feria_id) % 4)
            degustaciones.append(
                (
                    degustacion_id,
                    visitante_id,
                    tasting_stand if idx % 3 != 0 else sales_stand,
                    interes_vino_id,
                    puntaje,
                    intencion,
                    comments[(idx + feria_id) % len(comments)],
                )
            )

            visitante_id += 1
            degustacion_id += 1

    conn.executemany(
        """
        INSERT INTO visitante (
            visitante_id, feria_id, segmento_id, ciudad_origen_id, fecha_visita,
            acepta_contacto, interes_vino_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        visitantes,
    )
    conn.executemany(
        """
        INSERT INTO degustacion (
            degustacion_id, visitante_id, stand_id, vino_id, puntaje, intencion_compra, comentarios
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        degustaciones,
    )

    wine_price = {row[0]: row[6] for row in vinos}
    sold_totals: dict[tuple[int, int], int] = defaultdict(int)
    ventas = []
    detalles = []
    venta_id = 1
    detalle_id = 1
    payment_methods = ["Tarjeta", "Efectivo", "Transferencia"]

    for feria in ferias:
        feria_id, _, _, _, fecha_inicio, fecha_fin, *_ = feria
        fechas = daterange(fecha_inicio, fecha_fin)
        sales_stand = fair_stands[feria_id][1]
        linked_visitors = visitors_by_fair[feria_id]

        for sale_idx in range(8):
            visitor_ref = linked_visitors[sale_idx] if sale_idx % 3 != 0 else None
            sale_date = fechas[sale_idx % len(fechas)]
            sale_timestamp = datetime.combine(
                sale_date, datetime.min.time()
            ) + timedelta(hours=12 + sale_idx)

            primary_wine = 1 if (sale_idx + feria_id) % 2 == 0 else 2
            secondary_wine = 2 if primary_wine == 1 else 1

            items: list[tuple[int, int]] = []
            if sale_idx % 4 == 0:
                items.append((primary_wine, 4 + (sale_idx % 2)))
                items.append((secondary_wine, 2))
            else:
                items.append((primary_wine, 2 + (sale_idx % 4)))

            gross_amount = 0.0
            for wine_id, quantity in items:
                gross_amount += wine_price[wine_id] * quantity

            total_qty = sum(quantity for _, quantity in items)
            discount_rate = 0.08 if len(items) > 1 else (0.05 if total_qty >= 5 else 0.0)
            discount_amount = round(gross_amount * discount_rate, 2)
            net_amount = round(gross_amount - discount_amount, 2)

            ventas.append(
                (
                    venta_id,
                    feria_id,
                    sales_stand,
                    visitor_ref,
                    sale_timestamp.isoformat(timespec="minutes"),
                    payment_methods[sale_idx % len(payment_methods)],
                    round(gross_amount, 2),
                    discount_amount,
                    net_amount,
                )
            )

            for wine_id, quantity in items:
                subtotal = round(wine_price[wine_id] * quantity, 2)
                detalles.append(
                    (
                        detalle_id,
                        venta_id,
                        wine_id,
                        quantity,
                        wine_price[wine_id],
                        subtotal,
                    )
                )
                sold_totals[(feria_id, wine_id)] += quantity
                detalle_id += 1

            venta_id += 1

    conn.executemany(
        """
        INSERT INTO venta (
            venta_id, feria_id, stand_id, visitante_id, fecha_hora, medio_pago,
            monto_bruto, descuento, monto_neto
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ventas,
    )
    conn.executemany(
        """
        INSERT INTO detalle_venta (
            detalle_venta_id, venta_id, vino_id, cantidad, precio_unitario, subtotal
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        detalles,
    )

    for (feria_id, vino_id), sold in sold_totals.items():
        conn.execute(
            """
            UPDATE inventario_feria
            SET botellas_vendidas = ?, stock_cierre = botellas_recibidas - ?
            WHERE feria_id = ? AND vino_id = ?
            """,
            (sold, sold, feria_id, vino_id),
        )

    conn.commit()

    fair_summary = conn.execute(
        """
        WITH visitor_cte AS (
            SELECT feria_id, COUNT(*) AS visitantes
            FROM visitante
            GROUP BY feria_id
        ),
        sales_cte AS (
            SELECT feria_id, COUNT(*) AS ventas, ROUND(SUM(monto_neto), 2) AS ingresos
            FROM venta
            GROUP BY feria_id
        ),
        bottle_cte AS (
            SELECT v.feria_id, SUM(d.cantidad) AS botellas
            FROM venta v
            JOIN detalle_venta d ON d.venta_id = v.venta_id
            GROUP BY v.feria_id
        )
        SELECT
            f.nombre AS feria,
            c.nombre AS ciudad,
            COALESCE(vc.visitantes, 0) AS visitantes,
            COALESCE(sc.ventas, 0) AS ventas,
            COALESCE(sc.ingresos, 0) AS ingresos,
            COALESCE(bc.botellas, 0) AS botellas
        FROM feria f
        JOIN ciudad c ON c.ciudad_id = f.ciudad_id
        LEFT JOIN visitor_cte vc ON vc.feria_id = f.feria_id
        LEFT JOIN sales_cte sc ON sc.feria_id = f.feria_id
        LEFT JOIN bottle_cte bc ON bc.feria_id = f.feria_id
        ORDER BY ingresos DESC
        """
    ).fetchall()

    segment_summary = conn.execute(
        """
        SELECT
            s.nombre AS segmento,
            COUNT(DISTINCT vis.visitante_id) AS visitantes,
            COUNT(DISTINCT ve.venta_id) AS ventas,
            ROUND(COALESCE(SUM(ve.monto_neto), 0), 2) AS ingresos
        FROM segmento_publico s
        LEFT JOIN visitante vis ON vis.segmento_id = s.segmento_id
        LEFT JOIN venta ve ON ve.visitante_id = vis.visitante_id
        GROUP BY s.segmento_id, s.nombre
        ORDER BY ingresos DESC, visitantes DESC
        """
    ).fetchall()

    wine_summary = conn.execute(
        """
        SELECT
            v.nombre AS vino,
            v.estilo AS estilo,
            SUM(d.cantidad) AS botellas,
            ROUND(SUM(d.subtotal), 2) AS ingresos_brutos
        FROM vino v
        JOIN detalle_venta d ON d.vino_id = v.vino_id
        GROUP BY v.vino_id, v.nombre, v.estilo
        ORDER BY botellas DESC
        """
    ).fetchall()

    write_legacy_dashboard_notice(LEGACY_DASHBOARD_JS_PATH)

    table_counts = conn.execute(
        """
        SELECT 'region' AS tabla, COUNT(*) AS registros FROM region
        UNION ALL SELECT 'ciudad', COUNT(*) FROM ciudad
        UNION ALL SELECT 'segmento_publico', COUNT(*) FROM segmento_publico
        UNION ALL SELECT 'vino', COUNT(*) FROM vino
        UNION ALL SELECT 'alianza', COUNT(*) FROM alianza
        UNION ALL SELECT 'feria', COUNT(*) FROM feria
        UNION ALL SELECT 'feria_alianza', COUNT(*) FROM feria_alianza
        UNION ALL SELECT 'stand', COUNT(*) FROM stand
        UNION ALL SELECT 'inventario_feria', COUNT(*) FROM inventario_feria
        UNION ALL SELECT 'visitante', COUNT(*) FROM visitante
        UNION ALL SELECT 'degustacion', COUNT(*) FROM degustacion
        UNION ALL SELECT 'venta', COUNT(*) FROM venta
        UNION ALL SELECT 'detalle_venta', COUNT(*) FROM detalle_venta
        """
    ).fetchall()

    sample_sales = conn.execute(
        """
        SELECT
            ve.venta_id,
            f.nombre AS feria,
            ve.fecha_hora,
            ve.medio_pago,
            ve.monto_neto
        FROM venta ve
        JOIN feria f ON f.feria_id = ve.feria_id
        ORDER BY ve.venta_id
        LIMIT 8
        """
    ).fetchall()

    evidence_payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_records": sum(row["registros"] for row in table_counts),
        "table_counts": [dict(row) for row in table_counts],
        "schema_excerpt": conn.execute(
            """
            SELECT name, sql
            FROM sqlite_master
            WHERE type = 'table'
            AND name IN ('feria', 'visitante', 'venta', 'detalle_venta')
            ORDER BY name
            """
        ).fetchall(),
        "fair_summary": [dict(row) for row in fair_summary],
        "sample_sales": [dict(row) for row in sample_sales],
    }
    evidence_payload["schema_excerpt"] = [
        {"name": row["name"], "sql": row["sql"]} for row in evidence_payload["schema_excerpt"]
    ]
    write_js_assignment(EVIDENCE_JS_PATH, "dbEvidence", evidence_payload)

    export_csv(EXPORTS_DIR / "ventas_por_feria.csv", fair_summary)
    export_csv(EXPORTS_DIR / "ventas_por_segmento.csv", segment_summary)
    export_csv(EXPORTS_DIR / "mix_vinos.csv", wine_summary)

    conn.close()


if __name__ == "__main__":
    main()
