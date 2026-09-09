"""SQLite storage for PyroLytic literature and experiment records."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sqlite3
from contextlib import closing
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE = PROJECT_DIR / "pyrolytic.sqlite3"

# Source-row positions are provenance, never record identity. Notes distinguish
# replicate runs with otherwise identical measurements in the published dataset.
IMPORT_FIELDS = (
    ("plastic_type", "plastic_type", False), ("pct_PP", "pct_pp", True),
    ("pct_LDPE", "pct_ldpe", True), ("pct_HDPE", "pct_hdpe", True),
    ("temperature_C", "temperature_c", True), ("residence_time_min", "residence_time_min", True),
    ("feedstock_mass_g", "feedstock_mass_g", True), ("reactor_fill_pct", "reactor_fill_pct", True),
    ("heating_rate_C_min", "heating_rate_c_min", True), ("catalyst", "catalyst", False),
    ("oil_yield_wt%", "oil_yield_wt_pct", True), ("gas_yield_wt%", "gas_yield_wt_pct", True),
    ("char_yield_wt%", "char_yield_wt_pct", True), ("reactor_type", "reactor_type", False),
    ("confidence", "confidence", True), ("notes", "notes", False),
)


def _identity(doi, values):
    serialized = json.dumps([doi, *values], ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY,
    doi TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    year INTEGER,
    authors TEXT,
    open_access_url TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY,
    paper_id INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    plastic_type TEXT NOT NULL,
    pct_pp REAL, pct_ldpe REAL, pct_hdpe REAL,
    temperature_c REAL, residence_time_min REAL, feedstock_mass_g REAL,
    reactor_fill_pct REAL, heating_rate_c_min REAL, catalyst TEXT,
    oil_yield_wt_pct REAL, gas_yield_wt_pct REAL, char_yield_wt_pct REAL,
    reactor_type TEXT, confidence REAL, notes TEXT, source_row INTEGER,
    source_page TEXT, source_table TEXT, extraction_method TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(paper_id, source_row)
);
CREATE INDEX IF NOT EXISTS idx_experiments_plastic_type ON experiments(plastic_type);
CREATE INDEX IF NOT EXISTS idx_experiments_temperature ON experiments(temperature_c);
CREATE INDEX IF NOT EXISTS idx_experiments_paper ON experiments(paper_id);
"""


def connect(path: str | Path = DEFAULT_DATABASE) -> sqlite3.Connection:
    connection = sqlite3.connect(Path(path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize(path: str | Path = DEFAULT_DATABASE) -> None:
    with closing(connect(path)) as connection, connection:
        connection.executescript(SCHEMA)
        connection.execute("BEGIN IMMEDIATE")
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(experiments)")}
        if "import_key" not in columns:
            connection.execute("ALTER TABLE experiments ADD COLUMN import_key TEXT")
        pending = connection.execute(
            "SELECT e.*, p.doi FROM experiments e JOIN papers p ON p.id=e.paper_id "
            "WHERE e.import_key IS NULL").fetchall()
        keys = {row[0] for row in connection.execute(
            "SELECT import_key FROM experiments WHERE import_key IS NOT NULL")}
        for row in pending:
            values = [(_number(str(row[column])) if numeric and row[column] is not None
                       else _text(row[column])) for _, column, numeric in IMPORT_FIELDS]
            key = _identity(_text(row["doi"]), values)
            if key in keys:
                raise ValueError("Existing database contains indistinguishable experiments; "
                                 "add distinct run identifiers in their notes before importing.")
            keys.add(key)
            connection.execute("UPDATE experiments SET import_key=? WHERE id=?", (key, row["id"]))
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_experiments_import_key "
                           "ON experiments(import_key)")


def _number(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Numeric values must be finite, or blank when unknown.")
    return 0.0 if number == 0 else number


def _text(value: str | None) -> str | None:
    value = value.strip() if value is not None else ""
    return value or None


def import_csv(csv_path: str | Path, database_path: str | Path = DEFAULT_DATABASE) -> tuple[int, int]:
    """Merge a CSV snapshot by content; keep omitted records and annotations.

    Changes to imported experiment content create new records. We deliberately
    do not guess which old experiment a corrected measurement should replace.
    """
    prepared = []
    seen = set()
    with Path(csv_path).open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"source_doi", "source_title", "plastic_type"}
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
        for source_row, row in enumerate(reader, start=2):
            try:
                doi, title = _text(row.get("source_doi")), _text(row.get("source_title"))
                if not doi or not title or not _text(row.get("plastic_type")):
                    raise ValueError("source_doi, source_title, and plastic_type are required")
                if None in row:
                    raise ValueError("too many CSV columns")
                values = tuple((_number(row.get(csv_name)) if numeric else _text(row.get(csv_name)))
                               for csv_name, _, numeric in IMPORT_FIELDS)
                key = _identity(doi, values)
                if key in seen:
                    raise ValueError("indistinguishable duplicate; add a distinct run identifier in notes")
                seen.add(key)
                prepared.append((source_row, doi, title, values, key))
            except ValueError as error:
                raise ValueError(f"Row {source_row}: {error}") from error
    initialize(database_path)
    columns = ", ".join(column for _, column, _ in IMPORT_FIELDS)
    placeholders = ", ".join("?" for _ in range(len(IMPORT_FIELDS) + 3))
    with closing(connect(database_path)) as connection, connection:
        connection.execute("BEGIN IMMEDIATE")
        # Release old row positions before assigning the new snapshot's positions.
        # Omitted records remain available, but no longer claim a current CSV row.
        connection.execute("UPDATE experiments SET source_row=NULL")
        for source_row, doi, title, values, key in prepared:
            connection.execute(
                """INSERT INTO papers (doi, title) VALUES (?, ?)
                ON CONFLICT(doi) DO UPDATE SET title=excluded.title,
                updated_at=CURRENT_TIMESTAMP""", (doi, title))
            paper_id = connection.execute("SELECT id FROM papers WHERE doi=?", (doi,)).fetchone()[0]
            connection.execute(
                f"""INSERT INTO experiments (paper_id, {columns}, source_row, import_key)
                VALUES ({placeholders}) ON CONFLICT(import_key) DO UPDATE SET
                source_row=excluded.source_row, updated_at=CURRENT_TIMESTAMP""",
                (paper_id, *values, source_row, key))
    return len(prepared), len(prepared)


def paper_details(path: str | Path = DEFAULT_DATABASE) -> tuple[list[dict], list[dict]]:
    """Read full paper and experiment records without changing the database."""
    with closing(connect(path)) as connection:
        papers = [dict(row) for row in connection.execute("SELECT * FROM papers ORDER BY title, id")]
        experiments = [dict(row) for row in connection.execute("SELECT * FROM experiments ORDER BY id")]
    return papers, experiments


def save_provenance(experiment_id: int, values: tuple, expected: tuple,
                    path: str | Path = DEFAULT_DATABASE) -> None:
    """Save only provenance, rejecting edits made against an outdated record."""
    if len(values) != 3 or len(expected) != 3:
        raise ValueError("Provide page, table, and extraction method.")
    if any(value is not None and (not isinstance(value, str) or len(value) > 1000)
           for value in values):
        raise ValueError("Provenance fields must be text of at most 1,000 characters.")
    cleaned = tuple(_text(value) for value in values)
    with closing(connect(path)) as connection, connection:
        result = connection.execute(
            """UPDATE experiments SET source_page=?, source_table=?, extraction_method=?,
            updated_at=CURRENT_TIMESTAMP WHERE id=? AND source_page IS ?
            AND source_table IS ? AND extraction_method IS ?""",
            (*cleaned, experiment_id, *expected))
        if result.rowcount != 1:
            raise ValueError("This experiment changed or was removed. Reload the page before editing again.")


def summarize(path: str | Path = DEFAULT_DATABASE) -> dict[str, int]:
    initialize(path)
    with connect(path) as connection:
        return {
            "papers": connection.execute("SELECT COUNT(*) FROM papers").fetchone()[0],
            "experiments": connection.execute("SELECT COUNT(*) FROM experiments").fetchone()[0],
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import PyroLytic CSV into SQLite.")
    parser.add_argument("csv_path", nargs="?", default=PROJECT_DIR / "pyrolysis_yields.csv")
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    args = parser.parse_args()
    imported = import_csv(args.csv_path, args.database)
    print(f"Imported {imported[1]} experiments from {imported[0]} source rows.")
    print(summarize(args.database))
