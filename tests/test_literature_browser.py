import io

import pytest
from streamlit.testing.v1 import AppTest

import database
import literature_browser


@pytest.mark.parametrize("temperatures", [[None], [500.0], [500.2, 500.8], [450.0, None, 550.0]])
def test_temperature_filter_handles_missing_constant_and_decimal_data(temperatures, tmp_path, monkeypatch):
    path = tmp_path / "data.sqlite3"
    source = "source_title,source_doi,plastic_type,temperature_C,notes\n" + "".join(
        f"Paper,10.1000/test,PP,{value if value is not None else ''},Run {i}\n"
        for i, value in enumerate(temperatures))
    database.import_csv(io.StringIO(source), path)
    rows = literature_browser.query_experiments(path)
    monkeypatch.setattr(literature_browser, "query_experiments", lambda: rows)
    app = AppTest.from_string("from literature_browser import render\nrender()", default_timeout=20).run()
    assert not app.exception
    assert len(app.dataframe[0].value) == len(temperatures)
