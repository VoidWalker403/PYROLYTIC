"""SQLite storage for PyroLytic literature and experiment records."""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE = PROJECT_DIR / "pyrolytic.sqlite3"

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
    with connect(path) as connection:
        connection.executescript(SCHEMA)


def _number(value: str | None) -> float | None:
    return None if value is None or not value.strip() else float(value)


def _text(value: str | None) -> str | None:
    value = value.strip() if value is not None else ""
    return value or None


def import_csv(csv_path: str | Path, database_path: str | Path = DEFAULT_DATABASE) -> tuple[int, int]:
    """Import the dataset idempotently; return (source rows, experiment rows)."""
    initialize(database_path)
    paper_rows = 0
    experiment_rows = 0
    with Path(csv_path).open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"source_doi", "source_title", "plastic_type"}
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
        with connect(database_path) as connection:
            for source_row, row in enumerate(reader, start=2):
                doi, title = _text(row.get("source_doi")), _text(row.get("source_title"))
                if not doi or not title:
                    raise ValueError(f"Row {source_row} needs source_doi and source_title")
                connection.execute(
                    """INSERT INTO papers (doi, title) VALUES (?, ?)
                    ON CONFLICT(doi) DO UPDATE SET title=excluded.title,
                    updated_at=CURRENT_TIMESTAMP""", (doi, title))
                paper_id = connection.execute("SELECT id FROM papers WHERE doi = ?", (doi,)).fetchone()["id"]
                paper_rows += 1
                values = (
                    paper_id, _text(row.get("plastic_type")), _number(row.get("pct_PP")),
                    _number(row.get("pct_LDPE")), _number(row.get("pct_HDPE")),
                    _number(row.get("temperature_C")), _number(row.get("residence_time_min")),
                    _number(row.get("feedstock_mass_g")), _number(row.get("reactor_fill_pct")),
                    _number(row.get("heating_rate_C_min")), _text(row.get("catalyst")),
                    _number(row.get("oil_yield_wt%")), _number(row.get("gas_yield_wt%")),
                    _number(row.get("char_yield_wt%")), _text(row.get("reactor_type")),
                    _number(row.get("confidence")), _text(row.get("notes")), source_row)
                connection.execute(
                    """INSERT INTO experiments (
                    paper_id, plastic_type, pct_pp, pct_ldpe, pct_hdpe,
                    temperature_c, residence_time_min, feedstock_mass_g,
                    reactor_fill_pct, heating_rate_c_min, catalyst,
                    oil_yield_wt_pct, gas_yield_wt_pct, char_yield_wt_pct,
                    reactor_type, confidence, notes, source_row)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(paper_id, source_row) DO UPDATE SET
                    plastic_type=excluded.plastic_type, temperature_c=excluded.temperature_c,
                    oil_yield_wt_pct=excluded.oil_yield_wt_pct,
                    gas_yield_wt_pct=excluded.gas_yield_wt_pct,
                    char_yield_wt_pct=excluded.char_yield_wt_pct,
                    confidence=excluded.confidence, notes=excluded.notes,
                    updated_at=CURRENT_TIMESTAMP""", values)
                experiment_rows += 1
    return paper_rows, experiment_rows


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
