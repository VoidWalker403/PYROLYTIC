import io

from streamlit.testing.v1 import AppTest

import database
from chat_sources import capture_sources, linked_answer


def test_capture_groups_excerpts_and_preserves_record_snapshot(tmp_path):
    path = tmp_path / 'data.sqlite3'
    database.import_csv(io.StringIO(
        'source_title,source_doi,plastic_type,temperature_C,oil_yield_wt%\n'
        'Paper A,10.1000/a,PP,500,70\n'), path)
    chunk = {'source_doi': '10.1000/a', 'source_title': 'Paper A',
             'experiment_id': 1, 'text': 'Oil yield: 70%'}
    sources = capture_sources([chunk, chunk, {**chunk, 'text': 'Temperature: 500 C'}], path)
    assert len(sources) == 1
    assert len(sources[0]['excerpts']) == 2
    assert len(sources[0]['experiments']) == 1
    database.save_provenance(1, ('7', 'Table 1', 'Manual'), (None, None, None), path)
    assert sources[0]['experiments'][0]['source_page'] is None
    assert sources[0]['experiments'][0]['oil_yield_wt_pct'] == 70
    mismatched = capture_sources([{**chunk, 'source_doi': '10.1000/other'}], path)
    assert mismatched[0]['experiments'] == []


def test_only_known_safe_citations_get_links():
    sources = [{'doi': '10.1000/a'}, {'doi': 'project-background-note'},
               {'doi': 'javascript:alert(1)'}]
    content = ('Claim [SOURCE: 10.1000/a]. Unknown [SOURCE: 10.1000/made-up]. '
               '[SOURCE: project-background-note] [SOURCE: javascript:alert(1)]')
    result = linked_answer(content, sources)
    assert '[Source 1](<https://doi.org/10.1000/a>)' in result
    assert '[SOURCE: 10.1000/made-up]' in result
    assert '[SOURCE: project-background-note]' in result
    assert '(javascript:' not in result


def test_render_repeated_answer_and_unknown_citation():
    message = {'content': 'Result [SOURCE: 10.1000/a] [SOURCE: 10.1000/missing]',
               'sources': [{'doi': '10.1000/a', 'title': 'Paper A',
                            'excerpts': ['Reported oil yield 70%'], 'experiments': []}]}
    script = ("from chat_sources import render_answer\n"
              f"render_answer({message!r})\nrender_answer({message!r})")
    app = AppTest.from_string(script, default_timeout=15).run()
    assert not app.exception
    assert len(app.expander) == 2
    assert 'Cited in answer' in app.expander[0].label
    assert len(app.warning) == 2
    assert 'https://doi.org/10.1000/a' in app.markdown[0].value
    app.run()
    assert not app.exception and len(app.expander) == 2


def test_no_live_evidence_for_demo_or_empty_results():
    script = ("from chat_sources import render_answer\n"
              "render_answer({'content': 'Demo [SOURCE: 10.1000/demo]'})\n"
              "render_answer({'content': 'No evidence', 'sources': []})")
    app = AppTest.from_string(script, default_timeout=15).run()
    assert not app.exception
    assert not app.expander
    assert any('No source excerpts' in item.value for item in app.caption)
