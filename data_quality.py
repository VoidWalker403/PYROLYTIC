"""Read-only screening rules for imported experimental data."""

import math

import streamlit as st

import database
from paper_details import source_url

YIELDS = ('oil_yield_wt_pct', 'gas_yield_wt_pct', 'char_yield_wt_pct')
MIXTURE = ('pct_pp', 'pct_ldpe', 'pct_hdpe')


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def check_records(papers, records, yield_tolerance=5.0):
    """Return review findings. Missing measurements are never treated as zero."""
    by_paper = {paper['id']: paper for paper in papers}
    findings = []
    for row in records:
        paper = by_paper.get(row['paper_id'], {})
        def add(severity, code, fields, detail):
            findings.append({'Experiment': row['id'], 'Paper ID': row['paper_id'],
                             'Paper': paper.get('title', 'Unknown paper'),
                             'DOI': paper.get('doi', ''), 'Severity': severity,
                             'Check': code, 'Fields': fields, 'Finding': detail})
        missing = [label for field, label in (
            ('temperature_c', 'temperature'), ('oil_yield_wt_pct', 'oil yield'),
            ('confidence', 'confidence'), ('reactor_type', 'reactor type')) if row.get(field) in (None, '')]
        if missing:
            add('Missing information', 'Missing core fields', ', '.join(missing),
                'Not reported or not extracted; check the original source.')
        if not row.get('source_page') and not row.get('source_table'):
            add('Missing information', 'Missing source location', 'Page / table',
                'Record a page, table, or figure to make this extraction traceable.')
        for _, field, numeric in database.IMPORT_FIELDS:
            value = row.get(field)
            if not numeric or value is None:
                continue
            if not _finite(value):
                add('Invalid value', 'Non-finite or nonnumeric value', field, 'Use a finite number or leave unknown values blank.')
            elif field in (*YIELDS, *MIXTURE, 'reactor_fill_pct') and not 0 <= value <= 100:
                add('Invalid value', 'Percentage out of range', field, f'{value:g}; expected 0–100%.')
            elif field == 'confidence' and not 0 <= value <= 1:
                add('Invalid value', 'Confidence out of range', field, f'{value:g}; expected 0–1.')
            elif field in ('residence_time_min', 'feedstock_mass_g', 'heating_rate_c_min') and value < 0:
                add('Invalid value', 'Negative physical quantity', field, f'{value:g}; review the value and unit.')
            elif field in ('feedstock_mass_g', 'heating_rate_c_min') and value == 0:
                add('Review', 'Zero physical quantity', field, 'Check whether zero means unknown or was actually reported.')
        yields = [row.get(field) for field in YIELDS]
        valid_yields = [value for value in yields if _finite(value) and 0 <= value <= 100]
        if len(valid_yields) == 3:
            total = sum(valid_yields)
            if abs(total - 100) > yield_tolerance:
                add('Review', 'Yield total outside tolerance', 'Oil + gas + char',
                    f'Total {total:g} wt%; more than {yield_tolerance:g} percentage points from 100. '
                    'Check measurement basis, rounding, and extraction; do not rescale automatically.')
        elif any(value is None for value in yields):
            add('Missing information', 'Incomplete yield total', 'Oil + gas + char',
                'At least one yield is unknown, so a complete total cannot be checked.')
            if sum(valid_yields) > 100 + yield_tolerance:
                add('Review', 'Reported yields already exceed 100%', 'Available yields',
                    f'Known yields total {sum(valid_yields):g} wt% before missing components are included.')
        mixture = [row.get(field) for field in MIXTURE]
        if all(_finite(value) and 0 <= value <= 100 for value in mixture):
            total = sum(mixture)
            if abs(total - 100) > 1:
                add('Review', 'Feedstock composition total', 'PP + LDPE + HDPE',
                    f'Total {total:g}%; check whether other polymers are present or the composition is incomplete.')
        temperature = row.get('temperature_c')
        if _finite(temperature) and not 100 <= temperature <= 1200:
            add('Review', 'Temperature / unit screening', 'Temperature (°C)',
                f'{temperature:g} °C is outside this tool\'s 100–1200 °C screening band. '
                'Check the source and conversion; this is a heuristic, not a physical validity limit.')
        notes = (row.get('notes') or '').lower()
        if 'wax' in notes and 'mapped' in notes:
            add('Review', 'Yield basis mapping', 'Oil yield / notes',
                'Notes mention wax mapped to oil yield. Review comparability before pooling these values.')
        if row.get('source_row') is None:
            add('Review', 'Retained record', 'CSV membership',
                'Absent from the latest CSV but still included in the database, charts, and search index.')
    return findings


def _open_experiment(paper_id, experiment_id):
    st.session_state['details_paper'] = paper_id
    st.session_state[f'details_experiment_{paper_id}'] = experiment_id


def render(database_path=database.DEFAULT_DATABASE):
    st.subheader('Data quality')
    st.caption('Screening findings for review. No data is corrected or removed automatically.')
    papers, records = database.paper_details(database_path)
    if not records:
        st.info('No experiments to check yet.')
        return
    findings = check_records(papers, records)
    affected = len({finding['Experiment'] for finding in findings})
    st.write(f'{len(findings)} findings across {affected} of {len(records)} experiments')
    st.caption('Yield-total tolerance: ±5 percentage points. Composition tolerance: ±1 point. '
               'Expected units: °C, minutes, grams, °C/min, and wt%. '
               'Original units are not stored separately, so unit consistency requires checking the paper.')
    if not findings:
        st.success('No findings under the current screening rules. This does not establish scientific validity.')
        return
    severity = st.selectbox('Quality finding severity',
        ['All', 'Invalid value', 'Review', 'Missing information'], key='quality_severity')
    selected = [row for row in findings if severity == 'All' or row['Severity'] == severity]
    check = st.selectbox('Quality check', ['All', *sorted({row['Check'] for row in selected})], key='quality_check')
    selected = [row for row in selected if check == 'All' or row['Check'] == check]
    if not selected:
        st.info('No findings match these filters.')
        return
    st.dataframe([{key: value for key, value in row.items() if key != 'Paper ID'} for row in selected],
                 hide_index=True, use_container_width=True)
    index = st.selectbox('Finding to inspect', range(len(selected)),
                         format_func=lambda i: f"Experiment {selected[i]['Experiment']} · {selected[i]['Check']}",
                         key='quality_finding')
    finding = selected[index]
    st.text(finding['Finding'])
    url = source_url(finding['DOI'])
    if url:
        st.link_button('Open original source', url)
    st.button('Show experiment in Paper details', key='quality_open_experiment',
              on_click=_open_experiment, args=(finding['Paper ID'], finding['Experiment']))
    st.caption('The button selects the paper and experiment in the Paper details section above.')
