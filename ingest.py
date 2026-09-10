"""Build live search from SQLite and optional raw_texts/*.txt files."""

import database
from search_index import rebuild


def main():
    if not database.DEFAULT_DATABASE.exists():
        database.import_csv(database.PROJECT_DIR / "pyrolysis_yields.csv")
    result = rebuild()
    print(f"Indexed {result['chunks']} chunks from SQLite and local texts.")


if __name__ == "__main__":
    main()
