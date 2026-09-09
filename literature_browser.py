"""Data access and rendering helpers for the Streamlit literature browser."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

import database


def ensure_database(database_path: str | Path = database.DEFAULT_DATABASE) -> None:
    """Create the local index from the portable CSV when needed."""
    path = Path(database_path)
    if not path.exists():
        database.import_csv(database.PROJECT_DIR / "pyrolysis_yields.csv", path)


def query_experiments(database_path: str | Path = database.DEFAULT_DATABASE) -> list[dict]:
    ensure_database(database_path)
    with database.connect(database_path) as connection:
        rows = connection.execute(
            """SELECT e.id, p.title, p.doi, e.plastic_type, e.temperature_c,
                      e.residence_time_min, e.catalyst, e.reactor_type,
                      e.oil_yield_wt_pct, e.gas_yield_wt_pct, e.char_yield_wt_pct,
                      e.confidence, e.source_row, e.source_page, e.source_table,
                      e.extraction_method, e.notes
               FROM experiments e JOIN papers p ON p.id = e.paper_id
               ORDER BY e.id"""
        ).fetchall()
    return [dict(row) for row in rows]


def render() -> None:
    """Render a compact, filterable literature browser."""
    st.subheader("Literature browser")
    st.caption("Filter extracted experiments and inspect their source provenance.")
    rows = query_experiments()
    if not rows:
        st.info("No experiment records are available yet. Run `python database.py` to import the CSV.")
        return

    plastic_types = sorted({row["plastic_type"] for row in rows if row["plastic_type"]})
    reactor_types = sorted({row["reactor_type"] for row in rows if row["reactor_type"]})
    catalysts = sorted({row["catalyst"] for row in rows if row["catalyst"]})
    temperatures = [row["temperature_c"] for row in rows if row["temperature_c"] is not None]
    minimum, maximum = int(min(temperatures)), int(max(temperatures))

    controls = st.columns(4)
    selected_plastic = controls[0].selectbox("Plastic", ["All"] + plastic_types, key="browser_plastic")
    selected_reactor = controls[1].selectbox("Reactor", ["All"] + reactor_types, key="browser_reactor")
    selected_catalyst = controls[2].selectbox("Catalyst", ["All"] + catalysts, key="browser_catalyst")
    selected_temperature = controls[3].slider(
        "Temperature (°C)", minimum, maximum, (minimum, maximum), key="browser_temperature"
    )

    filtered = [
        row for row in rows
        if (selected_plastic == "All" or row["plastic_type"] == selected_plastic)
        and (selected_reactor == "All" or row["reactor_type"] == selected_reactor)
        and (selected_catalyst == "All" or row["catalyst"] == selected_catalyst)
        and (row["temperature_c"] is None or selected_temperature[0] <= row["temperature_c"] <= selected_temperature[1])
    ]
    st.write(f"Showing {len(filtered)} of {len(rows)} experiments")
    st.dataframe(
        [
            {
                "Plastic": row["plastic_type"],
                "Temp (°C)": row["temperature_c"],
                "Oil (%)": row["oil_yield_wt_pct"],
                "Gas (%)": row["gas_yield_wt_pct"],
                "Char (%)": row["char_yield_wt_pct"],
                "Catalyst": row["catalyst"],
                "Reactor": row["reactor_type"],
                "Confidence": row["confidence"],
                "Paper": row["title"],
                "DOI": row["doi"],
            }
            for row in filtered
        ],
        use_container_width=True,
        hide_index=True,
    )

    if filtered:
        options = {f"{row['id']}: {row['title'][:70]}": row for row in filtered}
        selected = st.selectbox("Inspect provenance", ["Select an experiment"] + list(options), key="browser_provenance")
        if selected != "Select an experiment":
            row = options[selected]
            st.json({
                "DOI": row["doi"],
                "source_row": row["source_row"],
                "source_page": row["source_page"],
                "source_table": row["source_table"],
                "extraction_method": row["extraction_method"],
                "notes": row["notes"],
            })
