from __future__ import annotations

import argparse
import csv
import subprocess
import tempfile
from pathlib import Path

from _common import DEFAULT_ENV_PATH, get_database_url, get_target_schema, load_env_file, run_psql


VENTA_COLUMNS = [
    "venta_id",
    "feria_id",
    "stand_id",
    "visitante_id",
    "fecha_hora",
    "medio_pago",
    "monto_bruto",
    "descuento",
    "monto_neto",
]

DETALLE_COLUMNS = [
    "detalle_venta_id",
    "venta_id",
    "vino_id",
    "cantidad",
    "precio_unitario",
    "subtotal",
]


def validate_csv_headers(csv_path: Path, expected_columns: list[str]) -> None:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            headers = next(reader)
        except StopIteration as exc:
            raise SystemExit(f"CSV vacío: {csv_path}") from exc

    if headers != expected_columns:
        raise SystemExit(
            f"Columnas inválidas en {csv_path.name}.\n"
            f"Esperadas: {expected_columns}\n"
            f"Recibidas: {headers}"
        )


def load_csv(database_url: str, schema_name: str, table_name: str, columns: list[str], csv_path: Path) -> None:
    column_list = ", ".join(f'"{column}"' for column in columns)
    escaped_path = str(csv_path.resolve()).replace("\\", "\\\\").replace("'", "''")
    copy_sql = (
        f'\\copy "{schema_name}"."{table_name}" ({column_list}) '
        f"FROM '{escaped_path}' WITH (FORMAT csv, HEADER true)"
    )
    subprocess.run(
        ["psql", database_url, "-v", "ON_ERROR_STOP=1", "-c", copy_sql],
        check=True,
        text=True,
    )


def count_rows(csv_path: Path) -> int:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Carga datos de venta y detalle_venta desde CSV hacia Neon/PostgreSQL."
    )
    parser.add_argument("--venta-csv", required=True, help="Ruta al CSV de venta.")
    parser.add_argument("--detalle-csv", required=True, help="Ruta al CSV de detalle_venta.")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_PATH), help="Ruta opcional al .env.")
    parser.add_argument("--schema", default=None, help="Schema destino. Por defecto usa TA01_PG_SCHEMA o public.")
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Trunca primero venta y detalle_venta. Usar con cuidado.",
    )
    args = parser.parse_args()

    venta_csv = Path(args.venta_csv).resolve()
    detalle_csv = Path(args.detalle_csv).resolve()
    env_file = Path(args.env_file).resolve()

    if not venta_csv.exists():
        raise SystemExit(f"No existe el archivo: {venta_csv}")
    if not detalle_csv.exists():
        raise SystemExit(f"No existe el archivo: {detalle_csv}")

    validate_csv_headers(venta_csv, VENTA_COLUMNS)
    validate_csv_headers(detalle_csv, DETALLE_COLUMNS)

    load_env_file(env_file)
    database_url = get_database_url()
    schema_name = get_target_schema(args.schema)

    if args.truncate:
        run_psql(database_url, sql=f'TRUNCATE TABLE "{schema_name}"."detalle_venta", "{schema_name}"."venta" CASCADE;')

    before_venta = run_psql(
        database_url,
        sql=f'SELECT COUNT(*) FROM "{schema_name}"."venta";',
        capture_output=True,
        tuples_only=True,
    )
    before_detalle = run_psql(
        database_url,
        sql=f'SELECT COUNT(*) FROM "{schema_name}"."detalle_venta";',
        capture_output=True,
        tuples_only=True,
    )

    print(f"venta antes: {before_venta}")
    print(f"detalle_venta antes: {before_detalle}")

    load_csv(database_url, schema_name, "venta", VENTA_COLUMNS, venta_csv)
    load_csv(database_url, schema_name, "detalle_venta", DETALLE_COLUMNS, detalle_csv)

    after_venta = run_psql(
        database_url,
        sql=f'SELECT COUNT(*) FROM "{schema_name}"."venta";',
        capture_output=True,
        tuples_only=True,
    )
    after_detalle = run_psql(
        database_url,
        sql=f'SELECT COUNT(*) FROM "{schema_name}"."detalle_venta";',
        capture_output=True,
        tuples_only=True,
    )

    print(f"venta CSV cargado: {count_rows(venta_csv)} filas")
    print(f"detalle_venta CSV cargado: {count_rows(detalle_csv)} filas")
    print(f"venta después: {after_venta}")
    print(f"detalle_venta después: {after_detalle}")


if __name__ == "__main__":
    main()
