import sqlite3

import database


def test_import_is_repeatable_and_preserves_provenance(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text(
        "source_title,source_doi,plastic_type,temperature_C,oil_yield_wt%,confidence,notes\n"
        "Paper A,10.1000/example,PP,500,70.0,1.0,Table 2\n", encoding="utf-8")
    db_path = tmp_path / "pyrolytic.sqlite3"
    assert database.import_csv(csv_path, db_path) == (1, 1)
    assert database.import_csv(csv_path, db_path) == (1, 1)
    assert database.summarize(db_path) == {"papers": 1, "experiments": 1}
    with database.connect(db_path) as connection:
        row = connection.execute(
            "SELECT p.doi, e.temperature_c, e.oil_yield_wt_pct, e.source_row "
            "FROM papers p JOIN experiments e ON e.paper_id = p.id").fetchone()
    assert dict(row) == {"doi": "10.1000/example", "temperature_c": 500.0,
                         "oil_yield_wt_pct": 70.0, "source_row": 2}


def test_foreign_keys_are_enabled(tmp_path):
    db_path = tmp_path / "pyrolytic.sqlite3"
    database.initialize(db_path)
    with database.connect(db_path) as connection:
        try:
            connection.execute("INSERT INTO experiments (paper_id, plastic_type, source_row) VALUES (999, 'PP', 2)")
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("orphan experiment row was accepted")
