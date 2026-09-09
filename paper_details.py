"""Paper records and provenance editing, rendered after the app login gate."""

import re
import sqlite3
from urllib.parse import quote, urlsplit

import streamlit as st

import database


def source_url(identifier):
    """Accept web sources and bare DOIs; never render active non-web schemes."""
    value = (identifier or "").strip()
    if re.match(r"^10\.\d{4,9}/\S+$", value):
        return "https://doi.org/" + quote(value, safe="/():;")
    try:
        parsed = urlsplit(value)
        if (parsed.scheme in {"http", "https"} and parsed.hostname
                and not parsed.username and not parsed.password
                and not any(char.isspace() for char in value)):
            return value
    except ValueError:
        pass
    return None


def render(database_path=database.DEFAULT_DATABASE):
    st.subheader("Paper details")
    st.caption("Open a source, review its complete experiments, and record where each value came from.")
    papers, experiments = database.paper_details(database_path)
    if not papers:
        st.info("No papers have been imported yet.")
        return
    by_id = {paper["id"]: paper for paper in papers}
    paper_id = st.selectbox(
        "Choose a paper", [None, *by_id],
        format_func=lambda key: "Select a paper" if key is None else by_id[key]["title"],
        key="details_paper")
    if paper_id is None:
        return
    paper = by_id[paper_id]
    st.write(paper["title"])
    st.caption(f"Authors: {paper['authors'] or 'Not recorded'} | Year: {paper['year'] or 'Not recorded'}")
    st.text(paper["doi"])
    link = source_url(paper["doi"])
    if link:
        st.link_button("Open source paper", link)
    open_link = source_url(paper["open_access_url"])
    if open_link:
        st.link_button("Open access copy", open_link)
    if paper["notes"]:
        st.text(paper["notes"])
    records = [row for row in experiments if row["paper_id"] == paper_id]
    st.caption(f"{len(records)} experiments in this paper. Blank fields mean not recorded.")
    if not records:
        return
    st.dataframe(records, hide_index=True, use_container_width=True)
    by_experiment = {row["id"]: row for row in records}
    experiment_id = st.selectbox(
        "Experiment to annotate", list(by_experiment),
        format_func=lambda key: f"Experiment {key} · CSV row {by_experiment[key]['source_row']}",
        key=f"details_experiment_{paper_id}")
    row = by_experiment[experiment_id]
    st.caption("These annotations are saved locally. They are not published to GitHub or written to the CSV.")
    fields = ("source_page", "source_table", "extraction_method")
    # Keep the values originally shown with the form to detect concurrent edits.
    baseline_key = f"provenance_baseline_{experiment_id}"
    if baseline_key not in st.session_state:
        st.session_state[baseline_key] = tuple(row[field] for field in fields)
    with st.form(f"provenance_form_{experiment_id}"):
        page = st.text_input("Page(s)", value=row["source_page"] or "",
                             key=f"page_{experiment_id}", max_chars=1000)
        table = st.text_input("Table or figure", value=row["source_table"] or "",
                              key=f"table_{experiment_id}", max_chars=1000)
        method = st.text_area("Extraction method", value=row["extraction_method"] or "",
                              key=f"method_{experiment_id}", max_chars=1000,
                              help="For example: manually transcribed from Table 2; digitized from Figure 3.")
        if st.form_submit_button("Save provenance"):
            try:
                database.save_provenance(experiment_id, (page, table, method),
                                         st.session_state[baseline_key], database_path)
            except (ValueError, sqlite3.Error) as error:
                st.error(str(error))
            else:
                st.session_state[baseline_key] = tuple(value.strip() or None for value in (page, table, method))
                st.success("Provenance saved. The experiment measurements are unchanged.")
