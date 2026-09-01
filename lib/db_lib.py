"""
db_lib.py

SQL Server connection and fast bulk-load helpers, shared by the notebook Parte 3
(schema + load) and every later notebook that reads from the warehouse
instead of a local CSV.

Why this exists (vs. the original MySQL notebook's approach): the old
project used MySQL's `LOAD DATA LOCAL INFILE` for speed, because
pandas.to_sql() with the default executemany was too slow for the
100k-170k-row QC tables (>1 min/table). SQL Server has no client-side
LOAD DATA equivalent, so the fast path here is pyodbc's documented
`fast_executemany` mode instead -- it batches parameters into a single
round-trip per chunk rather than one round-trip per row, which is the
actual source of the slowdown either way.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine


def _connection_string(server: str, database: str | None, driver: str) -> str:
    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        "Trusted_Connection=yes",   # the server is Windows-Authentication-only
        "TrustServerCertificate=yes",  # local dev instance, self-signed cert
    ]
    if database:
        parts.insert(1, f"DATABASE={database}")
    return ";".join(parts) + ";"


_USE_ENV_DEFAULT = "__use_env_default__"


def get_engine(database: str | None = _USE_ENV_DEFAULT) -> Engine:
    """Builds a SQLAlchemy engine for SQL Server with fast_executemany
    enabled. Reads SQLSERVER_HOST (default 'localhost') and SQLSERVER_DB
    from the environment/.env when `database` is left at its default;
    pass database=None explicitly to connect at the server level only (no
    DATABASE= clause -- used once, to CREATE DATABASE before it exists)."""
    server = os.environ.get("SQLSERVER_HOST", "localhost")
    driver = os.environ.get("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server")
    db_name = os.environ.get("SQLSERVER_DB", "ManufacturingPerformanceAnalytics") if database == _USE_ENV_DEFAULT else database
    odbc_str = _connection_string(server, db_name, driver)
    import urllib.parse
    quoted = urllib.parse.quote_plus(odbc_str)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quoted}", fast_executemany=True)

    @event.listens_for(engine, "before_cursor_execute")
    def _set_fast_executemany(conn, cursor, statement, parameters, context, executemany):
        if executemany:
            cursor.fast_executemany = True

    return engine


def create_database_if_missing(database: str) -> None:
    """Connects with no database selected and issues CREATE DATABASE if it
    doesn't already exist -- SQL Server can't run CREATE DATABASE inside an
    explicit transaction, so this uses an autocommit connection."""
    engine = get_engine(database=None)
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        exists = connection.execute(
            text("SELECT 1 FROM sys.databases WHERE name = :name"), {"name": database}
        ).fetchone()
        if not exists:
            connection.execute(text(f"CREATE DATABASE [{database}]"))
            print(f"Created database [{database}]")
        else:
            print(f"Database [{database}] already exists")
    engine.dispose()


def run_sql_script(engine: Engine, sql_text_block: str, label: str = "inline script") -> int:
    """Same GO-batch-splitting execution as `run_sql_file`, but takes the SQL text
    directly -- used by the single consolidated notebook, where every DDL script is
    authored as a string literal in the notebook itself (visible, in execution
    order) rather than read from a separate .sql file on disk."""
    lines_without_comments = "\n".join(
        line for line in sql_text_block.splitlines() if not line.strip().startswith("--")
    )
    batches = [b.strip() for b in _split_on_go(lines_without_comments) if b.strip()]
    with engine.begin() as connection:
        for batch in batches:
            connection.execute(text(batch))
    print(f"{len(batches)} batches executed ({label})")
    return len(batches)


def run_sql_file(engine: Engine, file_path: str | Path) -> int:
    """Reads a .sql file, splits it on standalone 'GO' batch separators
    (SQL Server's convention -- unlike MySQL's single ';'-per-statement
    files, T-SQL scripts batch on GO), strips full-line comments first, and
    executes each batch. Comments are stripped before splitting because a
    multi-line header comment with no GO inside it would otherwise silently
    swallow the first real statement if a naive "starts with --" check ran
    on the whole batch instead of line-by-line."""
    full_sql = Path(file_path).read_text(encoding="utf-8")
    return run_sql_script(engine, full_sql, label=Path(file_path).name)


def _split_on_go(sql_text: str) -> list[str]:
    """Splits on a line that is exactly 'GO' (case-insensitive, optional
    trailing whitespace) -- the standard T-SQL batch separator, which is a
    client-side convention (sqlcmd/SSMS), not real T-SQL syntax, so it must
    be split out before sending each batch over the DB-API connection."""
    batches, current = [], []
    for line in sql_text.splitlines():
        if line.strip().upper() == "GO":
            batches.append("\n".join(current))
            current = []
        else:
            current.append(line)
    if current:
        batches.append("\n".join(current))
    return batches


def load_dataframe(engine: Engine, df: pd.DataFrame, table_name: str,
                    chunksize: int = 2000, truncate_first: bool = True, schema: str = "dbo") -> float:
    """Loads a DataFrame into an existing SQL Server table via a raw pyodbc
    cursor with fast_executemany, truncating first so the notebook is
    safely re-runnable.

    This bypasses pandas.to_sql()/SQLAlchemy Core's insert path on purpose.
    pyodbc's fast_executemany pre-sizes each parameter's C buffer from the
    FIRST row of a batch, not from the target column's real width -- if a
    later row in the same batch has a longer string, the insert fails with
    'String data, right truncation' even though the NVARCHAR column is wide
    enough (a well-known pyodbc limitation, not a schema bug). Passing
    `cursor.setinputsizes(...)`, computed from this DataFrame's own actual
    max string length per column, forces a consistent buffer for every row
    in the batch regardless of ordering -- passing a `dtype=` to `to_sql`
    does NOT fix this, because pandas reflects the *existing* table's
    metadata when appending rather than using the given `dtype`.

    `schema` defaults to "dbo" (every existing caller's behavior, unchanged);
    pass schema="gold" (etc.) for a table created directly in a medallion
    schema -- see the notebook's Parte 3 (gold table DDL)."""
    import pyodbc

    if truncate_first:
        with engine.begin() as connection:
            connection.execute(text(f"TRUNCATE TABLE {schema}.{table_name}"))

    columns = list(df.columns)
    column_list_sql = ", ".join(f"[{c}]" for c in columns)
    placeholders = ", ".join("?" for _ in columns)
    insert_sql = f"INSERT INTO {schema}.{table_name} ({column_list_sql}) VALUES ({placeholders})"

    clean = df.astype(object).where(pd.notna(df), None)
    data = list(clean.itertuples(index=False, name=None))

    # pandas >= 3.0 infers a dedicated "str" dtype for text columns by
    # default (no longer "object") -- select_dtypes still recognizes it
    # under the "object"/"string" selectors for backward compatibility,
    # but a direct `dtype == object` or `str(dtype).startswith("string")`
    # check does NOT, so use select_dtypes here rather than either of those.
    text_columns = set(df.select_dtypes(include=["object", "string"]).columns)
    input_sizes = []
    for column in columns:
        if column in text_columns:
            max_len = df[column].dropna().astype(str).map(len).max()
            max_len = 1 if pd.isna(max_len) else int(max_len)
            input_sizes.append((pyodbc.SQL_WVARCHAR, max(max_len, 1), 0))
        else:
            input_sizes.append(None)

    raw_connection = engine.raw_connection()
    try:
        cursor = raw_connection.cursor()
        cursor.fast_executemany = True
        cursor.setinputsizes(input_sizes)
        start = time.perf_counter()
        for i in range(0, len(data), chunksize):
            cursor.executemany(insert_sql, data[i:i + chunksize])
        raw_connection.commit()
        elapsed = time.perf_counter() - start
    finally:
        raw_connection.close()

    print(f"  {table_name}: {len(df):,} rows loaded in {elapsed:.1f}s ({len(df) / max(elapsed, 1e-6):,.0f} rows/s)")
    return elapsed


def row_count(engine: Engine, table_name: str, schema: str = "dbo") -> int:
    with engine.connect() as connection:
        return connection.execute(text(f"SELECT COUNT(*) FROM {schema}.{table_name}")).scalar_one()
