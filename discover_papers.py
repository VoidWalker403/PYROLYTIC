"""Collect public Crossref bibliographic records, never experimental measurements."""

import argparse
from datetime import date, datetime, timezone
import html
import json
import os
from pathlib import Path
import re
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

QUERIES = (
    "plastic waste pyrolysis", "polyethylene pyrolysis", "polypropylene pyrolysis",
    "catalytic plastic pyrolysis", "polystyrene pyrolysis", "mixed plastic pyrolysis",
    "plastic pyrolysis kinetics", "plastic pyrolysis life cycle techno economic",
)
SELECT = "DOI,title,author,published,container-title,type,URL,update-to"


def plain(value):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(value))).strip()


def classify(title):
    """Transparent title keywords; these are discovery aids, not expert labels."""
    text = title.casefold()
    tags = []
    for tag, pattern in (
        ("Polyethylene", r"polyethylene|\b[hl]dpe\b|\blldpe\b"),
        ("Polypropylene", r"polypropylene|\bpp\b"),
        ("Polystyrene", r"polystyrene|\bps\b"),
        ("Mixed plastics", r"mix|municipal"),
        ("Catalysis", r"cataly|zeolite"),
        ("Kinetics", r"kinetic|activation energy"),
        ("Microwave", r"microwave"),
        ("Sustainability / economics", r"life.cycle|economic|environmental|sustainab"),
    ):
        if re.search(pattern, text):
            tags.append(tag)
    return tags or ["General plastic pyrolysis"]


def normalize_work(work, query, fetched_at, until):
    titles = work.get("title") or []
    title = plain(titles[0]) if titles else ""
    doi = str(work.get("DOI", "")).strip().lower()
    journals = work.get("container-title") or []
    journal = plain(journals[0]) if journals else ""
    # Search is fuzzy. Require both topic terms in the title and skip notices/news.
    if (work.get("type") != "journal-article" or not re.fullmatch(r"10\.\d{4,9}/\S+", doi)
            or not re.search(r"pyroly", title, re.I)
            or not re.search(r"plastic|polyethylene|polypropylene|polystyrene|polyolefin|\b(?:HDPE|LDPE|LLDPE|PP|PS|PET|PVC)\b", title, re.I)
            or re.search(r"retract|corrigend|erratum|correction|editorial", title, re.I)
            or not journal or "C&EN" in journal or work.get("update-to")):
        return None
    dates = work.get("published", {}).get("date-parts", [[]])[0]
    if not dates or not 1900 <= dates[0] <= until.year:
        return None
    if date(*(dates + [1] * (3 - len(dates)))) > until:
        return None
    authors = "; ".join(plain(" ".join(filter(None, (a.get("given"), a.get("family"))))
                        or a.get("name", "")) for a in work.get("author", []))
    return dict(source_id=doi, title=title, year=dates[0], authors=authors,
                journal=journal, paper_kind="Review (title)" if re.search(r"review|state.of.the.art", title, re.I)
                else "Journal article", topics=classify(title),
                metadata_url="https://api.crossref.org/works/" + doi,
                provider="Crossref", fetched_at=fetched_at, discovered_by=[query])


def fetch_works(query, rows, until, *, opener=urlopen, sleeper=time.sleep):
    params = urlencode({"query.title": query, "rows": rows,
                        "filter": f"type:journal-article,until-pub-date:{until}", "select": SELECT})
    request = Request("https://api.crossref.org/works?" + params,
                      headers={"User-Agent": "PyroLytic-Library/1.0 (public metadata research tool)"})
    for attempt in range(3):
        try:
            with opener(request, timeout=30) as response:
                return json.load(response)["message"]["items"]
        except (HTTPError, URLError, TimeoutError) as error:
            if isinstance(error, HTTPError) and error.code not in {429, 500, 502, 503, 504}:
                raise
            if attempt == 2:
                raise
            sleeper(2 ** (attempt + 1))


def discover(rows=100, until=None):
    if not 1 <= rows <= 1000:
        raise ValueError("Rows per query must be between 1 and 1000.")
    until = until or date.today()
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    records, counts = {}, {}
    for query in QUERIES:
        works = fetch_works(query, rows, until)
        counts[query] = len(works)
        for work in works:
            record = normalize_work(work, query, fetched_at, until)
            if record:
                key = record["source_id"]
                if key in records:
                    records[key]["discovered_by"].append(query)
                else:
                    records[key] = record
        print(f"{query}: {len(works)} results; {len(records)} unique eligible papers", flush=True)
        time.sleep(1)
    if not records:
        raise ValueError("No eligible papers returned; the existing snapshot is unchanged.")
    return {"schema_version": 1, "provider": "Crossref", "fetched_at": fetched_at,
            "until": until.isoformat(), "queries": counts,
            "selection": "Title contains pyrolysis and a plastic/polymer term; journal articles only; notices excluded. Metadata only, pending human review.",
            "papers": sorted(records.values(), key=lambda row: (-(row["year"]), row["title"]))}


def write_snapshot(payload, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                     delete=False, suffix=".json") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = handle.name
    try:
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=100, help="Results per topic (1–1000)")
    parser.add_argument("--until", type=date.fromisoformat, default=date.today())
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "research_library.json")
    parser.add_argument("--import-library", action="store_true", help="Merge into the local library after fetching")
    args = parser.parse_args()
    payload = discover(args.rows, args.until)
    write_snapshot(payload, args.output)
    print(f"Saved {len(payload['papers'])} papers to {args.output}")
    if args.import_library:
        from research_library import ensure_library
        ensure_library(snapshot_path=args.output)
        print("Merged library metadata; existing curation and experiments preserved.")


if __name__ == "__main__":
    main()
