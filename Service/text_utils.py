import html
import re
from difflib import SequenceMatcher
from typing import Iterable


STOP_WORDS = {
    "and",
    "are",
    "for",
    "from",
    "into",
    "less",
    "more",
    "the",
    "this",
    "that",
    "with",
    "your",
}


def strip_html(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_text(value: str) -> str:
    value = strip_html(value).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def display_text(value: str) -> str:
    value = strip_html(value)
    value = re.sub(r"[-_]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def split_terms(value: str) -> list[str]:
    value = strip_html(value)
    parts = re.split(r"[;,|/]+|\s+-\s+", value)
    return [display_text(part) for part in parts if display_text(part)]


def keyword_tokens(values: Iterable[str]) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        normalized = normalize_text(value)
        for token in normalized.split():
            if len(token) > 2 and token not in STOP_WORDS:
                tokens.add(token)
    return tokens


def edit_distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (left_char != right_char)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    return previous[-1]


def fuzzy_score(query: str, candidate: str) -> float:
    if not query or not candidate:
        return 0.0

    if query == candidate:
        return 1.0

    sequence_score = SequenceMatcher(None, query, candidate).ratio()
    distance = edit_distance(query, candidate)
    distance_score = 1.0 - (distance / max(len(query), len(candidate)))

    if query[0] == candidate[0] and distance <= 2 and max(len(query), len(candidate)) <= 8:
        distance_score += 0.12

    if candidate.startswith(query) or query.startswith(candidate):
        sequence_score += 0.08

    return min(1.0, max(sequence_score, distance_score))

