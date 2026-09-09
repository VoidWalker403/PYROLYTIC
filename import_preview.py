"""Review and explicitly apply a CSV snapshot after the app login gate."""

import csv
import hashlib
import io
import sqlite3

import streamlit as st

import database


def render_upload(data, database_path=database.DEFAULT_DATABASE):
    """Separate upload handling so review/save behavior can be tested in AppTest."""
    if len(data) > 5 * 1024 * 1024:
        st.error("Please use a CSV smaller than 5 MB.")
        return
    digest = hashlib.sha256(data).hexdigest()
    cache_key = "csv_import_preview"
    try:
        text = data.decode("utf-8-sig")
        cached = st.session_state.get(cache_key)
        if not cached or cached["digest"] != digest or cached["path"] != str(database_path):
            plan = database.preview_csv(io.StringIO(text), database_path)
            cached = {"digest": digest, "path": str(database_path), "plan": plan}
            st.session_state[cache_key] = cached
    except (UnicodeError, ValueError, csv.Error, sqlite3.Error) as error:
        st.session_state.pop(cache_key, None)
        st.error(f"Cannot preview this CSV: {error}")
        return
    plan = cached["plan"]
    st.write(f"New: {len(plan['new'])} · Matching: {len(plan['matching'])} · "
             f"Retained from earlier imports: {len(plan['retained'])}")
    st.caption("Matching records keep their IDs and annotations. Missing records remain in the database "
               "and charts, with no current CSV row. Changed measurements or notes create new records.")
    for key, label in (("new", "New experiments"), ("matching", "Matching experiments"),
                       ("retained", "Retained experiments absent from this CSV"),
                       ("title_changes", "Paper title changes")):
        with st.expander(f"{label} ({len(plan[key])})"):
            if plan[key]:
                st.dataframe(plan[key], hide_index=True, use_container_width=True)
            else:
                st.caption("None")
    st.caption("Saving updates only this local database. It does not change the source CSV, "
               "GitHub repository, or the chatbot search index. Rebuild the search index separately.")
    if st.button("Refresh preview", key="refresh_import_preview"):
        st.session_state.pop(cache_key, None)
        st.rerun()
    # Binding acknowledgement to both file and database state prevents stale approval.
    acknowledgement = f"review_import_{digest}_{plan['state']}"
    confirmed = st.checkbox("I reviewed these changes and want to import this CSV snapshot.",
                            key=acknowledgement)
    if st.button("Save import to local database", key="save_csv_import", disabled=not confirmed):
        try:
            database.import_csv(io.StringIO(text), database_path, expected_state=plan["state"])
        except (ValueError, csv.Error, sqlite3.Error) as error:
            st.error(str(error))
        else:
            st.session_state.pop(cache_key, None)
            st.session_state["csv_import_saved"] = True
            st.rerun()


def render(database_path=database.DEFAULT_DATABASE):
    st.subheader("Import experiments")
    st.caption("Upload a UTF-8 CSV using the dataset column names to preview a complete snapshot.")
    if st.session_state.pop("csv_import_saved", False):
        st.success("Import saved to the local database.")
    uploaded = st.file_uploader("CSV to review (up to 5 MB)", type=["csv"], key="import_csv_upload")
    if uploaded is not None:
        render_upload(uploaded.getvalue(), database_path)
    else:
        st.session_state.pop("csv_import_preview", None)
