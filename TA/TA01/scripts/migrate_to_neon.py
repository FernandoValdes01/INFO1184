from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from _common import (
    DEFAULT_ENV_PATH,
    DEFAULT_SCHEMA_SQL,
    DEFAULT_SQLITE_PATH,
    TABLE_ORDER,
    export_sqlite_table_to_csv,
    get_database_url,
    get_target_schema,
    load_env_file,
    postgres_table_counts,
    run_psql,
    sqlite_table_counts,
    truncate_postgres_tables,
)


def load_csv_into_postgres(database_url: str, schema_name: str, table_name: str, columns: list[str], csv_path: Path) -> None:
    column_list = ", ".join(f'"{column}"' for column in columns)
    escaped_path = str(csv_path).replace("\\", "\\\\").replace("'", "''")
    copy_sql = (
        f'\\copy "{schema_name}"."{table_name}" ({column_list}) '
        f"FROM '{escaped_path}' WITH (FORMAT csv, HEADER true)"
    )
    subprocess.run(
        ["psql", database_url, "-v", "ON_ERROR_STOP=1", "-c", copy_sql],
        check=True,
        text=True,
    )


def compare_counts(source_counts: dict[str, int], target_counts: dict[str, int]) -> None:
    mismatches = []
    for table_name in TABLE_ORDER:
        source_value = source_counts[table_name]
        target_value = target_counts.get(table_name, -1)
        status = "OK" if source_value == target_value else "MISMATCH"
        print(f"{table_name}: sqlite={source_value} postgres={target_value} [{status}]")
        if source_value != target_value:
            mismatches.append(table_name)

    if mismatches:
        raise SystemExit(f"Row count validation failed for: {', '.join(mismatches)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate TA01 raw data from SQLite to Neon/PostgreSQL.")
    parser.add_argument("--sqlite-path", default=str(DEFAULT_SQLITE_PATH), help="Path to the SQLite source database.")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_PATH), help="Optional .env file with the Neon connection string.")
    parser.add_argument("--schema", default=None, help="Target PostgreSQL schema. Defaults to TA01_PG_SCHEMA or public.")
    parser.add_argument("--skip-schema", action="store_true", help="Skip applying sql/schema_postgres.sql.")
    parser.add_argument("--skip-validate", action="store_true", help="Skip row count validation after load.")
    parser.add_argument("--keep-temp-csv", action="store_true", help="Keep the temporary exported CSV files.")
    args = parser.parse_args()

    sqlite_path = Path(args.sqlite_path).resolve()
    env_file = Path(args.env_file).resolve()
    if not sqlite_path.exists():
        raise SystemExit(f"SQLite source not found: {sqlite_path}")

    load_env_file(env_file)
    database_url = get_database_url()
    schema_name = get_target_schema(args.schema)

    if not args.skip_schema:
        print(f"Applying PostgreSQL schema into {schema_name}...")
        run_psql(
            database_url,
            sql_file=DEFAULT_SCHEMA_SQL,
            variables={"raw_schema": schema_name},
        )

    source_counts = sqlite_table_counts(sqlite_path)
    temp_dir = Path(tempfile.mkdtemp(prefix="ta01_neon_load_"))

    try:
        print(f"Exporting SQLite tables to temporary CSV files in {temp_dir}...")
        exported = {}
        for table_name in TABLE_ORDER:
            csv_path = temp_dir / f"{table_name}.csv"
            exported[table_name] = (csv_path, export_sqlite_table_to_csv(sqlite_path, table_name, csv_path))

        print(f"Truncating destination tables in {schema_name}...")
        truncate_postgres_tables(database_url, schema_name)

        print("Loading data into Neon/PostgreSQL...")
        for table_name in TABLE_ORDER:
            csv_path, columns = exported[table_name]
            load_csv_into_postgres(database_url, schema_name, table_name, columns, csv_path)
            print(f"Loaded {table_name}")

        if not args.skip_validate:
            print("Validating row counts...")
            target_counts = postgres_table_counts(database_url, schema_name)
            compare_counts(source_counts, target_counts)
    finally:
        if args.keep_temp_csv:
            print(f"Temporary CSV files preserved at: {temp_dir}")
        else:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
