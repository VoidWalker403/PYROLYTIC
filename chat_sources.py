"""Persist and render the evidence supplied to a live answer."""

from copy import deepcopy
import re
from urllib.parse import quote

import streamlit as st

import database
from paper_details import source_url

MARKER = re.compile(r"\[SOURCE:\s*([^\]\n]+)\]")


def capture_sources(chunks, database_path=database.DEFAULT_DATABASE):
    """Group retrieved excerpts by source and snapshot related experiment records."""
    if not chunks:
        return []
    papers, records = database.paper_details(database_path)
    by_paper = {paper['id']: paper for paper in papers}
    by_id = {row['id']: row for row in records}
    grouped = {}
    for chunk in chunks:
        doi = chunk.get('source_doi') or 'Unidentified source'
        source = grouped.setdefault(doi, {'doi': doi, 'title': chunk.get('source_title') or doi,
                                         'excerpts': [], 'experiments': []})
        excerpt = chunk.get('text', '')
        if excerpt not in source['excerpts']:
            source['excerpts'].append(excerpt)
        row = by_id.get(chunk.get('experiment_id'))
        if (row and by_paper[row['paper_id']]['doi'] == doi
                and not any(existing['id'] == row['id'] for existing in source['experiments'])):
            source['experiments'].append(deepcopy(row))
    return list(grouped.values())


def linked_answer(answer, sources):
    """Link only citations matching sources actually supplied to the model."""
    known = {source['doi']: (index, source_url(source['doi']))
             for index, source in enumerate(sources, 1)}
    def replace(match):
        found = known.get(match.group(1).strip())
        if not found or not found[1]:
            return match.group(0)
        index, url = found
        url = quote(url, safe='/:?=&%#@+;,-._~')
        return f'[Source {index}](<{url}>)'
    return MARKER.sub(replace, answer)


def render_answer(message):
    sources = message.get('sources', [])
    content = message['content']
    st.markdown(linked_answer(content, sources))
    if 'sources' not in message:
        return  # Existing/demo messages have no live retrieval evidence.
    known = {source['doi'] for source in sources}
    cited = {match.group(1).strip() for match in MARKER.finditer(content)}
    if cited - known:
        st.warning('This answer cites a source that was not supplied by retrieval. Check the claim independently.')
    if not sources:
        st.caption('No source excerpts were retrieved for this answer.')
        return
    st.caption('Sources supplied to this answer. A matching citation does not by itself verify a claim. '
               'Records below were captured for this request and may differ from later database edits.')
    for index, source in enumerate(sources, 1):
        label = 'Cited in answer' if source['doi'] in cited else 'Retrieved context'
        with st.expander(f"Source {index} · {label} · {source['title']}"):
            st.text(source['doi'])
            url = source_url(source['doi'])
            if url:
                st.link_button('Open source paper', url)
            for row in source['experiments']:
                st.write(f"Experiment {row['id']} · {row['plastic_type']}")
                fields = [(column.replace('_', ' '), row[column]) for _, column, _ in database.IMPORT_FIELDS]
                fields += [(label, row[key]) for label, key in
                           [('Source page', 'source_page'), ('Source table / figure', 'source_table'),
                            ('Extraction method', 'extraction_method'), ('CSV row', 'source_row')]]
                st.dataframe([{'Field': label, 'Value': str(value) if value is not None else 'Not recorded'}
                              for label, value in fields], hide_index=True, use_container_width=True)
            st.write('Retrieved excerpts')
            for excerpt in source['excerpts']:
                st.text(excerpt)
