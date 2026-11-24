"""Bibliographic discovery and local curation, separate from measured experiments."""

from contextlib import closing
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import unquote

import database
from paper_details import source_url

SNAPSHOT = database.PROJECT_DIR / "research_library.json"
STATUSES = ("Unreviewed", "Shortlisted", "Reviewed", "Excluded")
SCHEMA = """
CREATE TABLE IF NOT EXISTS research_library (
    source_id TEXT PRIMARY KEY, title TEXT NOT NULL, year INTEGER, authors TEXT,
    journal TEXT, paper_kind TEXT, topics TEXT NOT NULL DEFAULT '[]',
    provider TEXT NOT NULL, metadata_url TEXT, fetched_at TEXT,
    discovered_by TEXT NOT NULL DEFAULT '[]',
    review_status TEXT NOT NULL DEFAULT 'Unreviewed'
        CHECK(review_status IN ('Unreviewed','Shortlisted','Reviewed','Excluded')),
    review_notes TEXT NOT NULL DEFAULT '', revision INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS library_snapshots (path TEXT PRIMARY KEY, digest TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_library_year ON research_library(year);
CREATE INDEX IF NOT EXISTS idx_library_status ON research_library(review_status);
"""


def canonical_source(value):
    value = value.strip()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.I)
    value = re.sub(r"^doi:\s*", "", value, flags=re.I)
    value = unquote(value)
    return value.lower() if re.fullmatch(r"10\.\d{4,9}/\S+", value, re.I) else value


def validate_snapshot(payload):
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("Unsupported research-library snapshot format.")
    papers = payload.get("papers")
    if not isinstance(papers, list) or not papers:
        raise ValueError("The library snapshot must contain paper records.")
    clean, seen = [], set()
    for row in papers:
        if not isinstance(row, dict):
            raise ValueError("Each paper must be an object.")
        item = dict(row)
        for field in ("source_id", "title", "provider", "metadata_url", "fetched_at"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"Paper is missing {field}.")
        item["source_id"] = canonical_source(item["source_id"])
        if not re.fullmatch(r"10\.\d{4,9}/\S+", item["source_id"]):
            raise ValueError("Discovered papers must have a valid DOI.")
        if item["source_id"] in seen:
            raise ValueError("Duplicate DOI in library snapshot.")
        seen.add(item["source_id"])
        if not source_url(item["metadata_url"]):
            raise ValueError("Invalid metadata source URL.")
        if type(item.get("year")) is not int or not 1900 <= item["year"] <= 2100:
            raise ValueError("Invalid publication year.")
        for field in ("topics", "discovered_by"):
            if not isinstance(item.get(field), list) or not all(isinstance(x, str) for x in item[field]):
                raise ValueError(f"{field} must be a list of text values.")
        for field in ("authors", "journal", "paper_kind"):
            if not isinstance(item.get(field, ""), str):
                raise ValueError(f"{field} must be text.")
        clean.append(item)
    return clean


def ensure_library(database_path=database.DEFAULT_DATABASE, snapshot_path=SNAPSHOT):
    """Add bundled metadata once per content revision; never modify experiments."""
    from literature_browser import ensure_database
    ensure_database(database_path)
    snapshot_path = Path(snapshot_path) if snapshot_path is not None else None
    raw = snapshot_path.read_bytes() if snapshot_path and snapshot_path.exists() else None
    digest = hashlib.sha256(raw).hexdigest() if raw is not None else None
    # Validate before any writes, including schema changes.
    papers = validate_snapshot(json.loads(raw)) if raw is not None else []
    with closing(database.connect(database_path)) as connection, connection:
        connection.executescript(SCHEMA)
        connection.execute("BEGIN IMMEDIATE")
        for paper in connection.execute("SELECT * FROM papers").fetchall():
            connection.execute(
                "INSERT OR IGNORE INTO research_library(source_id,title,year,authors,provider,paper_kind) "
                "VALUES(?,?,?,?,?,?)", (canonical_source(paper["doi"]), paper["title"], paper["year"],
                                       paper["authors"], "Existing experiment dataset", "Existing source"))
        if raw is None:
            return
        snapshot_key = str(snapshot_path.resolve())
        previous = connection.execute("SELECT digest FROM library_snapshots WHERE path=?", (snapshot_key,)).fetchone()
        if previous and previous[0] == digest:
            return
        for row in papers:
            connection.execute("""INSERT INTO research_library
                (source_id,title,year,authors,journal,paper_kind,topics,provider,metadata_url,fetched_at,discovered_by)
                VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(source_id) DO UPDATE SET
                title=excluded.title, year=excluded.year, authors=excluded.authors, journal=excluded.journal,
                paper_kind=excluded.paper_kind, topics=excluded.topics, provider=excluded.provider,
                metadata_url=excluded.metadata_url, fetched_at=excluded.fetched_at,
                discovered_by=excluded.discovered_by""",
                (row["source_id"], row["title"], row["year"], row.get("authors", ""), row.get("journal", ""),
                 row.get("paper_kind", "Journal article"), json.dumps(row["topics"]), row["provider"],
                 row["metadata_url"], row["fetched_at"], json.dumps(row["discovered_by"])))
        connection.execute("INSERT INTO library_snapshots(path,digest) VALUES(?,?) "
                           "ON CONFLICT(path) DO UPDATE SET digest=excluded.digest", (snapshot_key, digest))


def query_library(database_path=database.DEFAULT_DATABASE):
    with closing(database.connect(database_path)) as connection:
        rows = [dict(row) for row in connection.execute(
            "SELECT * FROM research_library ORDER BY year DESC, title, source_id")]
        counts = {}
        for row in connection.execute("SELECT p.doi, COUNT(e.id) AS n FROM papers p "
                                      "LEFT JOIN experiments e ON e.paper_id=p.id GROUP BY p.id"):
            key = canonical_source(row["doi"])
            counts[key] = counts.get(key, 0) + row["n"]
    for row in rows:
        row["topics"] = json.loads(row["topics"])
        row["discovered_by"] = json.loads(row["discovered_by"])
        row["experiment_count"] = counts.get(row["source_id"], 0)
    return rows


def filter_library(rows, text="", status="All", topic="All", year="All", kind="All", coverage="All"):
    terms = text.casefold().split()
    return [row for row in rows
            if all(term in " ".join(str(row.get(k) or "") for k in
                                    ("title", "authors", "source_id", "journal", "topics")).casefold() for term in terms)
            and (status == "All" or row["review_status"] == status)
            and (topic == "All" or topic in row["topics"])
            and (year == "All" or str(row["year"]) == str(year))
            and (kind == "All" or row["paper_kind"] == kind)
            and (coverage == "All" or (row["experiment_count"] > 0) == (coverage == "With experiments"))]


def save_review(source_id, status, notes, expected_revision, database_path=database.DEFAULT_DATABASE):
    if status not in STATUSES or not isinstance(notes, str) or len(notes) > 10000:
        raise ValueError("Choose a valid status and keep review notes under 10,000 characters.")
    with closing(database.connect(database_path)) as connection, connection:
        result = connection.execute("UPDATE research_library SET review_status=?,review_notes=?,revision=revision+1 "
                                    "WHERE source_id=? AND revision=?",
                                    (status, notes.strip(), source_id, expected_revision))
        if result.rowcount != 1:
            raise ValueError("This paper changed in another session. Reload its review before saving.")


def export_csv(rows):
    fields = ("source_id", "title", "year", "authors", "journal", "paper_kind", "topics",
              "review_status", "review_notes", "experiment_count", "provider", "metadata_url", "fetched_at")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fields)
    writer.writeheader()
    for row in rows:
        record = {}
        for key in fields:
            value = row.get(key)
            value = "; ".join(value) if isinstance(value, list) else str(value if value is not None else "")
            # Spreadsheet-safe export of publisher strings and local notes.
            record[key] = "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value
        writer.writerow(record)
    return output.getvalue().encode("utf-8-sig")


def render(database_path=database.DEFAULT_DATABASE):
    import streamlit as st
    st.subheader("Research paper library")
    st.caption("Discover papers, shortlist useful studies, and keep local review notes. "
               "Bibliographic records are not extracted measurements or downloaded full texts.")
    if st.session_state.pop("library_saved_message", False):
        st.success("Review saved locally.")
    rows = query_library(database_path)
    text = st.text_input("Search title, author, DOI, journal or topic", key="library_search")
    controls = st.columns(3)
    status = controls[0].selectbox("Review status", ["All", *STATUSES], key="library_status")
    topic = controls[1].selectbox("Topic (from title)", ["All", *sorted({x for r in rows for x in r["topics"]})], key="library_topic")
    year = controls[2].selectbox("Publication year", ["All", *sorted({str(r["year"]) for r in rows if r["year"]}, reverse=True)], key="library_year")
    controls = st.columns(2)
    kind = controls[0].selectbox("Paper type", ["All", *sorted({r["paper_kind"] for r in rows if r["paper_kind"]})], key="library_kind")
    coverage = controls[1].selectbox("Extraction coverage", ["All", "With experiments", "Awaiting extraction"], key="library_coverage")
    filtered = filter_library(rows, text, status, topic, year, kind, coverage)
    st.write(f"Showing {len(filtered):,} of {len(rows):,} library records")
    st.caption("Discovery topics and review labels inferred from titles require your review. "
               "Use Import experiments for measurements after checking the paper and its units.")
    if not filtered:
        st.info("No papers match these filters. Try a broader search.")
        return
    st.download_button("Export filtered library (CSV)", export_csv(filtered), "pyrolytic-library.csv", "text/csv", key="library_export")
    pages = (len(filtered) + 49) // 50
    page_key = "library_page"
    if st.session_state.get(page_key, 1) > pages:
        st.session_state[page_key] = 1
    page = st.number_input("Results page", min_value=1, max_value=pages, step=1, key=page_key)
    visible = filtered[(page - 1) * 50:page * 50]
    st.dataframe([{"Title": r["title"], "Year": r["year"], "Journal": r["journal"],
                   "Status": r["review_status"], "Experiments": r["experiment_count"],
                   "Source": source_url(r["source_id"])} for r in visible],
                 column_config={"Source": st.column_config.LinkColumn("Source paper")},
                 hide_index=True, use_container_width=True)
    by_id = {r["source_id"]: r for r in visible}
    selected = st.selectbox("Paper to review (this page)", [None, *by_id],
                            format_func=lambda key: "Select a paper" if key is None else by_id[key]["title"],
                            key="library_selected")
    if selected is None:
        return
    row = by_id[selected]
    st.write(row["title"])
    st.text(f"{row['authors'] or 'Authors not recorded'}\n{row['journal'] or 'Journal not recorded'} · {row['year'] or 'Year unknown'}")
    link = source_url(selected)
    if link:
        st.link_button("Open publisher / DOI", link)
    if row["metadata_url"]:
        st.link_button("Inspect metadata source", row["metadata_url"])
    st.caption(f"Metadata: {row['provider']} | Retrieved: {row['fetched_at'] or 'Existing local dataset'} | "
               f"Extracted experiments: {row['experiment_count']}")
    token = hashlib.sha256(selected.encode()).hexdigest()[:16]
    baseline = f"library_baseline_{token}"
    if baseline not in st.session_state:
        st.session_state[baseline] = row["revision"]
    if st.button("Reload saved review", key=f"library_reload_{token}"):
        for key in (baseline, f"review_status_{token}", f"review_notes_{token}"):
            st.session_state.pop(key, None)
        st.rerun()
    with st.form(f"library_review_{token}"):
        new_status = st.selectbox("Set review status", STATUSES, index=STATUSES.index(row["review_status"]), key=f"review_status_{token}")
        notes = st.text_area("Review notes", value=row["review_notes"], max_chars=10000, key=f"review_notes_{token}",
                             help="Record suitability, access, extraction plans and limitations. Saved only in the local database.")
        if st.form_submit_button("Save paper review"):
            try:
                save_review(selected, new_status, notes, st.session_state[baseline], database_path)
            except (ValueError, sqlite3.Error) as error:
                st.error(str(error))
            else:
                st.session_state[baseline] += 1
                st.session_state["library_saved_message"] = True
                st.rerun()
