import csv
from contextlib import closing

import pytest

import database


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["source_title", "source_doi", "plastic_type", "temperature_C", "oil_yield_wt%", "notes"])
        writer.writerows(rows)


A = ["Paper", "10.1000/example", "PP", "500", "70", "Run A"]
B = ["Paper", "10.1000/example", "PP", "500", "70", "Run B"]
C = ["Paper", "10.1000/example", "PP", "450", "65", "Run C"]


def test_reorder_insert_remove_and_correct_keep_annotations(tmp_path):
    source, path = tmp_path / "data.csv", tmp_path / "data.sqlite3"
    write_csv(source, [A, B])
    database.import_csv(source, path)
    database.save_provenance(1, ("12", "Table 1", "Manual"), (None, None, None), path)
    formatted_a = [*A[:3], "500.00", "70.0", A[-1]]
    write_csv(source, [C, B, formatted_a])
    database.import_csv(source, path)
    database.import_csv(source, path)
    rows = database.paper_details(path)[1]
    assert len(rows) == 3
    assert rows[0]["id"] == 1 and rows[0]["source_row"] == 4
    assert rows[0]["source_page"] == "12"
    assert rows[1]["notes"] == "Run B" and rows[1]["source_page"] is None
    corrected = [*A[:4], "71", A[-1]]
    write_csv(source, [B, corrected])
    database.import_csv(source, path)
    rows = database.paper_details(path)[1]
    assert len(rows) == 4
    assert rows[0]["source_row"] is None and rows[0]["source_page"] == "12"
    assert rows[-1]["oil_yield_wt_pct"] == 71 and rows[-1]["source_page"] is None


@pytest.mark.parametrize("bad_rows", [[A, A], [C, [*B[:3], "nan", *B[4:]]],
                                    [C, [*B[:3], "infinity", *B[4:]]],
                                    [C, [B[0], B[1], "", *B[3:]]]])
def test_invalid_import_leaves_records_unchanged(tmp_path, bad_rows):
    source, path = tmp_path / "data.csv", tmp_path / "data.sqlite3"
    write_csv(source, [A, B])
    database.import_csv(source, path)
    before = database.paper_details(path)
    write_csv(source, bad_rows)
    with pytest.raises(ValueError, match="Row"):
        database.import_csv(source, path)
    assert database.paper_details(path) == before


def test_legacy_database_migration_preserves_id_and_provenance(tmp_path):
    source, path = tmp_path / "data.csv", tmp_path / "legacy.sqlite3"
    with closing(database.connect(path)) as connection, connection:
        connection.executescript(database.SCHEMA)
        connection.execute("INSERT INTO papers (id, doi, title) VALUES (1, '10.1000/example', 'Paper')")
        connection.execute("""INSERT INTO experiments
            (id, paper_id, plastic_type, temperature_c, oil_yield_wt_pct, notes, source_row, source_page)
            VALUES (42, 1, 'PP', 500, 70, 'Run A', 2, '12')""")
    write_csv(source, [B, A])
    database.import_csv(source, path)
    rows = database.paper_details(path)[1]
    assert rows[0]["id"] == 42 and rows[0]["source_page"] == "12"
    assert rows[0]["source_row"] == 3 and rows[0]["import_key"]


def test_real_corpus_reversed_is_idempotent(tmp_path):
    path = tmp_path / "corpus.sqlite3"
    source = database.PROJECT_DIR / "pyrolysis_yields.csv"
    database.import_csv(source, path)
    before = {row["id"]: row["import_key"] for row in database.paper_details(path)[1]}
    with source.open(newline="", encoding="utf-8-sig") as file:
        rows = list(csv.reader(file))
    reversed_source = tmp_path / "reversed.csv"
    with reversed_source.open("w", newline="", encoding="utf-8") as file:
        csv.writer(file).writerows([rows[0], *reversed(rows[1:])])
    database.import_csv(reversed_source, path)
    after = {row["id"]: row["import_key"] for row in database.paper_details(path)[1]}
    assert before == after
    assert len(after) == len(rows) - 1
