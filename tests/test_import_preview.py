import io

import pytest
from streamlit.testing.v1 import AppTest

import database


HEADER = "source_title,source_doi,plastic_type,temperature_C,oil_yield_wt%,notes\n"
A = "Paper,10.1000/a,PP,500,70,Run A\n"
B = "Paper,10.1000/a,PP,450,60,Run B\n"
C = "Other,10.1000/c,HDPE,400,65,Run C\n"


@pytest.fixture
def path(tmp_path):
    path = tmp_path / "data.sqlite3"
    database.import_csv(io.StringIO(HEADER + A + B), path)
    return path


def test_preview_readonly_and_matches_applied_changes(path):
    before = path.read_bytes()
    text = HEADER + A.replace("Paper,", "Renamed paper,") + C
    plan = database.preview_csv(io.StringIO(text), path)
    assert path.read_bytes() == before
    assert [len(plan[key]) for key in ("new", "matching", "retained", "title_changes")] == [1, 1, 1, 1]
    database.import_csv(io.StringIO(text), path, expected_state=plan["state"])
    papers, rows = database.paper_details(path)
    assert len(rows) == 3
    assert rows[0]["source_row"] == 2
    assert rows[1]["source_row"] is None
    assert papers[0]["title"] in {"Other", "Renamed paper"}
    assert any(paper["doi"] == "10.1000/a" and paper["title"] == "Renamed paper" for paper in papers)


def test_stale_preview_rejected_without_partial_changes(path):
    text = HEADER + C
    plan = database.preview_csv(io.StringIO(text), path)
    database.save_provenance(1, ("7", "Table 3", "Manual"), (None, None, None), path)
    before = database.paper_details(path)
    with pytest.raises(ValueError, match="changed since this preview"):
        database.import_csv(io.StringIO(text), path, expected_state=plan["state"])
    assert database.paper_details(path) == before


@pytest.mark.parametrize("text", [HEADER, HEADER + A + A, "source_title,source_title\nA,A\n"])
def test_invalid_preview_leaves_database_unchanged(path, text):
    before = path.read_bytes()
    with pytest.raises(ValueError):
        database.preview_csv(io.StringIO(text), path)
    assert path.read_bytes() == before


def test_ui_requires_review_and_saves_exact_upload(path):
    payload = (HEADER + A + C).encode()
    script = ("from import_preview import render_upload\n"
              f"render_upload({payload!r}, {str(path)!r})")
    before = database.paper_details(path)
    app = AppTest.from_string(script, default_timeout=15).run()
    assert not app.exception
    assert app.button(key="save_csv_import").disabled
    assert database.paper_details(path) == before
    app.checkbox[0].check().run()
    app.button(key="save_csv_import").click().run()
    assert not app.exception
    assert len(database.paper_details(path)[1]) == 3
    assert app.button(key="save_csv_import").disabled


def test_ui_stale_preview_requires_refresh(path):
    script = ("from import_preview import render_upload\n"
              f"render_upload({(HEADER + A + C).encode()!r}, {str(path)!r})")
    app = AppTest.from_string(script, default_timeout=15).run()
    app.checkbox[0].check().run()
    database.save_provenance(1, ("9", "", ""), (None, None, None), path)
    app.button(key="save_csv_import").click().run()
    assert not app.exception
    assert "changed since this preview" in app.error[0].value
    assert len(database.paper_details(path)[1]) == 2
    app.button(key="refresh_import_preview").click().run()
    assert app.button(key="save_csv_import").disabled


@pytest.mark.parametrize("payload", [b"bad csv", b"\xff", (HEADER + "x" * 150000).encode()],
                         ids=["missing_columns", "invalid_utf8", "oversized_field"])
def test_ui_invalid_upload_has_no_save_control(path, payload):
    app = AppTest.from_string(
        f"from import_preview import render_upload\nrender_upload({payload!r}, {str(path)!r})",
        default_timeout=15).run()
    assert not app.exception
    assert app.error
    assert not app.button
