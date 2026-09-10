from contextlib import closing
import io

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

import database
import search_index


HEADER = "source_title,source_doi,plastic_type,temperature_C,oil_yield_wt%,notes\n"
A = "Paper A,10.1000/a,PP,500,70,Run A\n"
B = "Uploaded paper,10.1000/b,HDPE,450,60,Run B\n"


class LocalTestEncoder:
    """Deterministic test vectors; real Chroma still stores and queries them."""
    def encode(self, texts, **kwargs):
        return np.array([[1.0, float('HDPE' in text), float('PP' in text)] for text in texts])


@pytest.fixture
def corpus(tmp_path):
    path = tmp_path / "data.sqlite3"
    raw = tmp_path / "texts"
    raw.mkdir()
    chroma = tmp_path / "index"
    database.import_csv(io.StringIO(HEADER + A), path)
    return dict(database_path=path, raw_texts_dir=raw, chroma_dir=chroma,
                model=LocalTestEncoder())


def test_uploaded_rows_searchable_after_rebuild(corpus):
    path = corpus['database_path']
    search_index.rebuild(**corpus)
    database.import_csv(io.StringIO(HEADER + A + B), path)
    with pytest.raises(ValueError, match="outdated"):
        search_index.search('HDPE', **corpus)
    search_index.rebuild(**corpus)
    results = search_index.search('HDPE', k=100, **corpus)
    assert results[0]['source_doi'] == '10.1000/b'
    assert results[0]['experiment_id'] == 2
    assert '60.0' in results[0]['text']
    assert len(results) == 2
    # Reimporting identical data changes timestamps, but not searchable content.
    database.import_csv(io.StringIO(HEADER + A + B), path)
    assert search_index.search('HDPE', **corpus)


def test_provenance_edits_and_removed_sources_are_reflected(corpus):
    path, raw = corpus['database_path'], corpus['raw_texts_dir']
    text = raw / 'paper.txt'
    text.write_text('Local reference material for PP pyrolysis.', encoding='utf-8')
    first = search_index.rebuild(**corpus)
    database.save_provenance(1, ('7', 'Table 2', 'Manual'), (None, None, None), path)
    with pytest.raises(ValueError, match="outdated"):
        search_index.search('PP', **corpus)
    second = search_index.rebuild(**corpus)
    assert second['collection'] != first['collection']
    assert any('source_page: 7' in row['text'] for row in search_index.search('PP', **corpus))
    text.unlink()
    with closing(database.connect(path)) as connection, connection:
        connection.execute('DELETE FROM experiments WHERE id=1')
    with pytest.raises(ValueError, match="outdated"):
        search_index.search('PP', **corpus)
    search_index.rebuild(**corpus)
    assert search_index.search('PP', **corpus) == []


def test_failed_rebuild_preserves_selected_index(corpus):
    search_index.rebuild(**corpus)
    before = (corpus['chroma_dir'] / 'active_index.json').read_bytes()

    class BrokenEncoder:
        def encode(self, *args, **kwargs):
            raise RuntimeError('embedding failed')

    with pytest.raises(RuntimeError, match='embedding failed'):
        search_index.rebuild(**{**corpus, 'model': BrokenEncoder()})
    assert (corpus['chroma_dir'] / 'active_index.json').read_bytes() == before
    assert search_index.search('PP', **corpus)


def test_source_change_during_build_cannot_publish(corpus):
    search_index.rebuild(**corpus)
    before = (corpus['chroma_dir'] / 'active_index.json').read_bytes()

    class ChangingEncoder(LocalTestEncoder):
        def encode(self, texts, **kwargs):
            database.save_provenance(1, ('9', '', ''), (None, None, None), corpus['database_path'])
            return super().encode(texts, **kwargs)

    with pytest.raises(RuntimeError, match='Sources changed'):
        search_index.rebuild(**{**corpus, 'model': ChangingEncoder()})
    assert (corpus['chroma_dir'] / 'active_index.json').read_bytes() == before
    with pytest.raises(ValueError, match='outdated'):
        search_index.search('PP', **corpus)


def test_missing_index_does_not_load_embedding_model(corpus, monkeypatch):
    def unexpected():
        pytest.fail('Embedding model should not load for an absent index')
    monkeypatch.setattr(search_index, 'get_model', unexpected)
    with pytest.raises(ValueError, match='missing or outdated'):
        search_index.search('PP', database_path=corpus['database_path'],
                            chroma_dir=corpus['chroma_dir'], raw_texts_dir=corpus['raw_texts_dir'])


def test_rebuild_button_updates_status_and_handles_errors(monkeypatch):
    state = {'current': False, 'chunks': 4}
    monkeypatch.setattr(search_index, 'status', lambda: state)
    monkeypatch.setattr(search_index, 'rebuild', lambda: state.update(current=True))
    app = AppTest.from_string('from search_index import render\nrender()', default_timeout=15).run()
    assert app.info
    app.button(key='rebuild_search_index').click().run()
    assert not app.exception and not app.info
    def fail():
        raise RuntimeError('test download failure')
    monkeypatch.setattr(search_index, 'rebuild', fail)
    app.button(key='rebuild_search_index').click().run()
    assert not app.exception
    assert 'Rebuild failed' in app.error[0].value
