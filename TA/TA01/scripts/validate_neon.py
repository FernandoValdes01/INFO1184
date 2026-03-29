from __future__ import annotations

import argparse
from pathlib import Path

from _common import (
    DEFAULT_ENV_PATH,
    DEFAULT_SQLITE_PATH,
    DEFAULT_VALIDATION_SQL,
    get_database_url,
    get_target_schema,
    load_env_file,
    postgres_table_counts,
    run_psql,
    sqlite_table_counts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate TA01 data loaded into Neon/PostgreSQL.")
    parser.add_argument("--sqlite-path", default=str(DEFAULT_SQLITE_PATH), help="Optional SQLite source to compare counts.")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_PATH), help="Optional .env file with the Neon connection string.")
    parser.add_argument("--schema", default=None, help="Target PostgreSQL schema. Defaults to TA01_PG_SCHEMA or public.")
    parser.add_argument("--skip-count-compare", action="store_true", help="Run SQL validation only.")
    args = parser.parse_args()

    load_env_file(Path(args.env_file).resolve())
    database_url = get_database_url()
    schema_name = get_target_schema(args.schema)

    print(f"Running SQL validation for schema {schema_name}...")
    run_psql(
        database_url,
        sql_file=DEFAULT_VALIDATION_SQL,
        variables={"raw_schema": schema_name},
    )

    if not args.skip_count_compare:
        sqlite_path = Path(args.sqlite_path).resolve()
        if not sqlite_path.exists():
            raise SystemExit(f"SQLite source not found for count comparison: {sqlite_path}")

        source_counts = sqlite_table_counts(sqlite_path)
        target_counts = postgres_table_counts(database_url, schema_name)

        mismatches = []
        print("Comparing source and destination row counts...")
        for table_name, source_value in source_counts.items():
            target_value = target_counts[table_name]
            status = "OK" if source_value == target_value else "MISMATCH"
            print(f"{table_name}: sqlite={source_value} postgres={target_value} [{status}]")
            if source_value != target_value:
                mismatches.append(table_name)

        if mismatches:
            raise SystemExit(f"Count validation failed for: {', '.join(mismatches)}")


if __name__ == "__main__":
    main()
