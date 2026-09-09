import pytest
from streamlit.testing.v1 import AppTest

import database
from paper_details import source_url


@pytest.fixture
def dataset(tmp_path):
    source = tmp_path / "data.csv"
    source.write_text(
        "source_title,source_doi,plastic_type,temperature_C,oil_yield_wt%\n"
        "Paper A,10.1000/a,PP,500,70\n"
        "Paper B,10.1000/b,HDPE,450,60\n", encoding="utf-8")
    path = tmp_path / "data.sqlite3"
    database.import_csv(source, path)
    return source, path


def test_annotation_survives_reimport_and_rejects_stale_save(dataset):
    source, path = dataset
    before = database.paper_details(path)[1]
    database.save_provenance(1, (" 12 ", "Table 2", "Manual transcription"), (None, None, None), path)
    with pytest.raises(ValueError, match="changed or was removed"):
        database.save_provenance(1, ("wrong", "", ""), (None, None, None), path)
    database.import_csv(source, path)
    after = database.paper_details(path)[1]
    assert after[0]["source_page"] == "12"
    assert after[0]["source_table"] == "Table 2"
    assert after[0]["extraction_method"] == "Manual transcription"
    for field in ("temperature_c", "oil_yield_wt_pct", "source_row", "paper_id"):
        assert after[0][field] == before[0][field]
    assert after[1]["source_page"] is None
    database.save_provenance(1, ("", "", ""), ("12", "Table 2", "Manual transcription"), path)
    assert database.paper_details(path)[1][0]["source_page"] is None


def test_source_links():
    assert source_url("10.1000/a") == "https://doi.org/10.1000/a"
    assert source_url("https://example.org/paper") == "https://example.org/paper"
    for value in (None, "javascript:alert(1)", "file:///private", "https://", "https://user:pass@example.org"):
        assert source_url(value) is None


def test_paper_form_saves_selected_experiment_and_reloads(dataset):
    _, path = dataset
    script = f"from paper_details import render\nrender({str(path)!r})"
    app = AppTest.from_string(script, default_timeout=15).run()
    app.selectbox(key="details_paper").select(1).run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 1
    app.text_input(key="page_1").input("7")
    app.text_input(key="table_1").input("Figure 4")
    app.text_area(key="method_1").input("Digitized plot")
    next(button for button in app.button if button.label == "Save provenance").click().run()
    assert not app.exception
    assert app.success[0].value.startswith("Provenance saved")
    app.selectbox(key="details_paper").select(2).run()
    assert app.text_input(key="page_2").value == ""
    fresh = AppTest.from_string(script, default_timeout=15).run()
    fresh.selectbox(key="details_paper").select(1).run()
    assert fresh.text_input(key="page_1").value == "7"
    assert fresh.text_input(key="table_1").value == "Figure 4"
    assert fresh.text_area(key="method_1").value == "Digitized plot"


def test_empty_database(tmp_path):
    path = tmp_path / "empty.sqlite3"
    database.initialize(path)
    app = AppTest.from_string(f"from paper_details import render\nrender({str(path)!r})",
                             default_timeout=15).run()
    assert not app.exception
    assert app.info[0].value == "No papers have been imported yet."
