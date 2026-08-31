import csv
from pathlib import Path

from Service.text_utils import display_text, keyword_tokens, normalize_text, split_terms


PRIMARY_FIELDS = (
    "Name",
    "Slug",
    "Recipe Types",
    "Features",
    "Common Ingredients",
    "Ingredients",
    "Prep Time",
    "Cook Time",
    "Total Time",
    "SEO Title Tag",
    "SEO Meta Description",
    "Type",
    "The Question",
    "The Answer",
)

SPLIT_FIELDS = {
    "Recipe Types",
    "Features",
    "Common Ingredients",
    "Ingredients",
    "Prep Time",
    "Cook Time",
    "Total Time",
    "Type",
}


def _add_term(terms: dict[str, dict], value: str, source: str, kind: str) -> None:
    display = display_text(value)
    normalized = normalize_text(display)
    if not normalized or len(normalized) < 3:
        return

    current = terms.get(normalized)
    if current:
        current["sources"].add(source)
        current["kinds"].add(kind)
        current["count"] += 1
        return

    terms[normalized] = {
        "term": display,
        "normalized": normalized,
        "sources": {source},
        "kinds": {kind},
        "count": 1,
    }


def _iter_csv_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            yield row


def load_terms_from_csv_dir(csv_dir: Path) -> list[dict]:
    terms: dict[str, dict] = {}

    for path in sorted(csv_dir.glob("*.csv")):
        source = path.name
        for row in _iter_csv_rows(path):
            field_values: list[str] = []

            for field in PRIMARY_FIELDS:
                value = row.get(field, "")
                if not value:
                    continue

                if field == "Slug":
                    _add_term(terms, value.replace("-", " "), source, "slug")
                else:
                    _add_term(terms, value, source, field)

                field_values.append(value)

                if field in SPLIT_FIELDS:
                    for part in split_terms(value):
                        _add_term(terms, part, source, field)

            for token in keyword_tokens(field_values):
                _add_term(terms, token, source, "keyword")

    clean_terms = []
    for item in terms.values():
        clean_terms.append(
            {
                "term": item["term"],
                "normalized": item["normalized"],
                "sources": sorted(item["sources"]),
                "kinds": sorted(item["kinds"]),
                "count": item["count"],
            }
        )

    return sorted(clean_terms, key=lambda item: item["normalized"])
