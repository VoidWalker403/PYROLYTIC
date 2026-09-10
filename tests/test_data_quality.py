import io

import pytest
from streamlit.testing.v1 import AppTest

import database
from data_quality import check_records


PAPERS = [{'id': 1, 'title': 'Paper', 'doi': '10.1000/a'}]


def record(**changes):
    row = dict(id=1, paper_id=1, plastic_type='PP', temperature_c=500,
               oil_yield_wt_pct=70, gas_yield_wt_pct=20, char_yield_wt_pct=10,
               confidence=1, reactor_type='batch', source_page='7', source_table=None,
               source_row=2, notes='', pct_pp=100, pct_ldpe=0, pct_hdpe=0,
               residence_time_min=30, feedstock_mass_g=5, heating_rate_c_min=10)
    row.update(changes)
    return row


def codes(row):
    return {item['Check'] for item in check_records(PAPERS, [row])}


def test_complete_record_and_tolerance_boundaries():
    assert not check_records(PAPERS, [record()])
    assert 'Yield total outside tolerance' not in codes(record(char_yield_wt_pct=15))
    assert 'Yield total outside tolerance' not in codes(record(char_yield_wt_pct=5))
    assert 'Yield total outside tolerance' in codes(record(char_yield_wt_pct=15.1))
    assert 'Yield total outside tolerance' in codes(record(char_yield_wt_pct=4.9))


def test_missing_yields_are_not_zero_or_complete():
    result = codes(record(gas_yield_wt_pct=None))
    assert 'Incomplete yield total' in result
    assert 'Yield total outside tolerance' not in result
    assert 'Reported yields already exceed 100%' in codes(record(oil_yield_wt_pct=90,
                                                               gas_yield_wt_pct=20, char_yield_wt_pct=None))


@pytest.mark.parametrize('changes, expected', [
    ({'oil_yield_wt_pct': 101}, 'Percentage out of range'),
    ({'confidence': -0.1}, 'Confidence out of range'),
    ({'feedstock_mass_g': -1}, 'Negative physical quantity'),
    ({'heating_rate_c_min': 0}, 'Zero physical quantity'),
    ({'temperature_c': float('inf')}, 'Non-finite or nonnumeric value'),
    ({'temperature_c': '500 C'}, 'Non-finite or nonnumeric value'),
    ({'temperature_c': 20}, 'Temperature / unit screening'),
    ({'pct_pp': 90}, 'Feedstock composition total'),
    ({'source_page': None}, 'Missing source location'),
    ({'notes': 'WAX mapped to oil_yield'}, 'Yield basis mapping'),
    ({'source_row': None}, 'Retained record'),
])
def test_review_rules(changes, expected):
    assert expected in codes(record(**changes))


def test_report_does_not_write_and_filters_and_navigation_work(tmp_path):
    path = tmp_path / 'data.sqlite3'
    database.import_csv(io.StringIO(
        'source_title,source_doi,plastic_type,temperature_C,oil_yield_wt%\n'
        'Paper,10.1000/a,PP,500,110\n'), path)
    before = path.read_bytes()
    script = f'from data_quality import render\nrender({str(path)!r})'
    app = AppTest.from_string(script, default_timeout=15).run()
    assert not app.exception
    app.selectbox(key='quality_severity').select('Invalid value').run()
    assert not app.exception
    assert set(app.dataframe[0].value['Check']) == {'Percentage out of range'}
    app.button(key='quality_open_experiment').click().run()
    assert not app.exception
    assert app.session_state['details_paper'] == 1
    assert app.session_state['details_experiment_1'] == 1
    assert path.read_bytes() == before


def test_empty_database(tmp_path):
    path = tmp_path / 'empty.sqlite3'
    database.initialize(path)
    app = AppTest.from_string(f'from data_quality import render\nrender({str(path)!r})',
                             default_timeout=15).run()
    assert not app.exception
    assert app.info[0].value == 'No experiments to check yet.'
