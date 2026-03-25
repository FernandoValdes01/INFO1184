from __future__ import annotations

import csv
import os
import sqlite3
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "ta01_feria_vinos.db"
DEFAULT_ENV_PATH = PROJECT_ROOT / ".env"
DEFAULT_SCHEMA_SQL = PROJECT_ROOT / "sql" / "schema_postgres.sql"
DEFAULT_VALIDATION_SQL = PROJECT_ROOT / "sql" / "validate_neon_data.sql"

TABLE_ORDER = [
    "region",
    "ciudad",
    "segmento_publico",
    "vino",
    "alianza",
    "feria",
    "feria_alianza",
    "stand",
    "inventario_feria",
    "visitante",
    "degustacion",
    "venta",
    "detalle_venta",
]


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def get_database_url() -> str:
    database_url = os.environ.get("NEON_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            "Missing NEON_DATABASE_URL or DATABASE_URL. "
            "Copy TA/TA01/.env.example to .env and set the connection string."
        )
    return database_url


def get_target_schema(explicit_schema: str | None = None) -> str:
    return sanitize_identifier(explicit_schema or os.environ.get("TA01_PG_SCHEMA", "public"))


def sanitize_identifier(value: str) -> str:
    if not value:
        raise SystemExit("Schema/table name cannot be empty.")
    if not value.replace("_", "").isalnum():
        raise SystemExit(f"Invalid identifier: {value!r}")
    return value


def sqlite_connection(sqlite_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn


def sqlite_table_columns(sqlite_path: Path, table_name: str) -> list[str]:
    with sqlite_connection(sqlite_path) as conn:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [row["name"] for row in rows]


def sqlite_table_counts(sqlite_path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    with sqlite_connection(sqlite_path) as conn:
        for table_name in TABLE_ORDER:
            counts[table_name] = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    return counts


def export_sqlite_table_to_csv(sqlite_path: Path, table_name: str, destination: Path) -> list[str]:
    columns = sqlite_table_columns(sqlite_path, table_name)
    with sqlite_connection(sqlite_path) as conn, destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        query = f"SELECT {', '.join(columns)} FROM {table_name}"
        for row in conn.execute(query):
            values = []
            for column in columns:
                value = row[column]
                if table_name == "visitante" and column == "acepta_contacto":
                    values.append("true" if value else "false")
                else:
                    values.append(value)
            writer.writerow(values)
    return columns


def run_psql(
    database_url: str,
    *,
    sql: str | None = None,
    sql_file: Path | None = None,
    variables: dict[str, str] | None = None,
    capture_output: bool = False,
    tuples_only: bool = False,
) -> str:
    command = ["psql", database_url, "-v", "ON_ERROR_STOP=1"]
    if tuples_only:
        command.append("-At")
    for key, value in (variables or {}).items():
        command.extend(["-v", f"{key}={value}"])
    if sql_file:
        command.extend(["-f", str(sql_file)])
    elif sql is not None:
        command.extend(["-c", sql])
    else:
        raise ValueError("Either sql or sql_file must be provided.")

    result = subprocess.run(
        command,
        check=True,
        text=True,
        capture_output=capture_output,
    )
    if capture_output:
        return result.stdout.strip()
    return ""


def postgres_table_counts(database_url: str, schema_name: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table_name in TABLE_ORDER:
        sql = f'SELECT COUNT(*) FROM "{schema_name}"."{table_name}";'
        output = run_psql(database_url, sql=sql, capture_output=True, tuples_only=True)
        counts[table_name] = int(output)
    return counts


def truncate_postgres_tables(database_url: str, schema_name: str) -> None:
    tables = ", ".join(f'"{schema_name}"."{table_name}"' for table_name in reversed(TABLE_ORDER))
    run_psql(database_url, sql=f"TRUNCATE TABLE {tables} CASCADE;")
