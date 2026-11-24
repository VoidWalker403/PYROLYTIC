from datetime import date
import io
import json

import pytest
from streamlit.testing.v1 import AppTest

import database
import discover_papers
import research_library as library


def paper(doi="10.1000/new", title="Catalytic pyrolysis of polypropylene"):
    return dict(source_id=doi, title=title, year=2024, authors="Example Author", journal="Test Journal",
                paper_kind="Journal article", topics=["Catalysis", "Polypropylene"],
                provider="Crossref", metadata_url="https://api.crossref.org/works/" + doi,
                fetched_at="2026-09-25T00:00:00+00:00", discovered_by=["plastic pyrolysis"])


def write_snapshot(path, papers):
    path.write_text(json.dumps({"schema_version": 1, "papers": papers}), encoding="utf-8")


@pytest.fixture
def corpus(tmp_path):
    db = tmp_path / "research.sqlite3"
    database.import_csv(io.StringIO("source_title,source_doi,plastic_type,temperature_C,oil_yield_wt%\n"
                                   "Existing,https://doi.org/10.1000/EXISTING,PP,500,70\n"), db)
    snapshot = tmp_path / "library.json"
    write_snapshot(snapshot, [paper(), paper("10.1000/existing")])
    return db, snapshot


def test_merge_deduplicates_doi_and_preserves_all_experiments_and_reviews(corpus):
    db, snapshot = corpus
    before = database.paper_details(db)
    library.ensure_library(db, snapshot)
    assert len(library.query_library(db)) == 2
    existing = next(r for r in library.query_library(db) if r["source_id"] == "10.1000/existing")
    assert existing["experiment_count"] == 1
    library.save_review("10.1000/new", "Shortlisted", "Check Table 3", 0, db)
    library.ensure_library(db, snapshot)
    write_snapshot(snapshot, [paper(title="Updated metadata title"), paper("10.1000/another")])
    library.ensure_library(db, snapshot)
    rows = library.query_library(db)
    assert len(rows) == 3  # omitted papers remain available
    saved = next(r for r in rows if r["source_id"] == "10.1000/new")
    assert (saved["review_status"], saved["review_notes"], saved["revision"]) == ("Shortlisted", "Check Table 3", 1)
    assert saved["title"] == "Updated metadata title"
    assert database.paper_details(db) == before


def test_invalid_snapshot_is_atomic_and_stale_reviews_are_rejected(corpus):
    db, snapshot = corpus
    library.ensure_library(db, snapshot)
    before = library.query_library(db)
    write_snapshot(snapshot, [paper("10.1000/valid"), paper("bad-doi")])
    with pytest.raises(ValueError, match="valid DOI"):
        library.ensure_library(db, snapshot)
    assert library.query_library(db) == before
    library.save_review("10.1000/new", "Reviewed", "Original", 0, db)
    with pytest.raises(ValueError, match="another session"):
        library.save_review("10.1000/new", "Excluded", "Stale", 0, db)
    with pytest.raises(ValueError):
        library.save_review("10.1000/new", "Invented", "", 1, db)


def test_filters_export_and_formula_protection(corpus):
    db, snapshot = corpus
    library.ensure_library(db, snapshot)
    rows = library.query_library(db)
    assert len(library.filter_library(rows, text="polypropylene Example", year="2024", topic="Catalysis")) == 2
    assert len(library.filter_library(rows, coverage="Awaiting extraction")) == 1
    assert len(library.filter_library(rows, coverage="With experiments")) == 1
    assert not library.filter_library(rows, text="no matching phrase")
    rows[0]["review_notes"] = "  =HYPERLINK(\"https://example.com\")"
    output = library.export_csv(rows).decode("utf-8-sig")
    assert "'  =HYPERLINK" in output
    assert "experiment_count" in output


def test_ui_search_review_persistence_and_empty_results(corpus):
    db, snapshot = corpus
    library.ensure_library(db, snapshot)
    script = f"from research_library import render\nrender({str(db)!r})"
    app = AppTest.from_string(script, default_timeout=20).run()
    assert not app.exception
    app.selectbox(key="library_selected").select("10.1000/new").run()
    next(s for s in app.selectbox if s.label == "Set review status").select("Shortlisted")
    app.text_area[0].input("Read the original tables")
    next(b for b in app.button if b.label == "Save paper review").click().run()
    assert not app.exception
    assert "Shortlisted" in app.dataframe[0].value["Status"].tolist()
    fresh = AppTest.from_string(script, default_timeout=20).run()
    fresh.selectbox(key="library_status").select("Shortlisted").run()
    assert len(fresh.dataframe[0].value) == 1
    fresh.selectbox(key="library_selected").select("10.1000/new").run()
    assert fresh.text_area[0].value == "Read the original tables"
    fresh.text_input(key="library_search").input("nothing matches this").run()
    assert not fresh.exception
    assert "No papers match" in fresh.info[0].value


def test_snapshot_duplicate_alias_and_unsafe_url_rejected():
    with pytest.raises(ValueError, match="Duplicate DOI"):
        library.validate_snapshot({"schema_version": 1, "papers": [paper(), paper("https://doi.org/10.1000/NEW")]})
    bad = paper()
    bad["metadata_url"] = "javascript:alert(1)"
    with pytest.raises(ValueError, match="URL"):
        library.validate_snapshot({"schema_version": 1, "papers": [bad]})


def work(title="Catalytic pyrolysis of polypropylene"):
    return {"DOI": "10.1000/NEW", "title": [title], "container-title": ["Journal &amp; Science"],
            "type": "journal-article", "published": {"date-parts": [[2024, 5, 2]]},
            "author": [{"given": "Ada", "family": "Example"}]}


def test_discovery_filters_and_metadata_provenance():
    row = discover_papers.normalize_work(work(), "query", "timestamp", date(2026, 9, 25))
    assert row["source_id"] == "10.1000/new"
    assert row["authors"] == "Ada Example"
    assert row["journal"] == "Journal & Science"
    assert "Polypropylene" in row["topics"]
    for title in ("Biomass pyrolysis", "Plastic recycling", "Retraction: pyrolysis of plastic"):
        assert discover_papers.normalize_work(work(title), "q", "t", date.today()) is None
    future = work()
    future["published"]["date-parts"] = [[2026, 12, 1]]
    assert discover_papers.normalize_work(future, "q", "t", date(2026, 9, 25)) is None


def test_discovery_retry_is_bounded():
    from urllib.error import HTTPError
    attempts, sleeps = [], []
    def fail(*args, **kwargs):
        attempts.append(1)
        raise HTTPError("https://api.crossref.org", 429, "throttled", {}, None)
    with pytest.raises(HTTPError):
        discover_papers.fetch_works("plastic", 5, date.today(), opener=fail, sleeper=sleeps.append)
    assert len(attempts) == 3 and sleeps == [2, 4]
