import json
from pathlib import Path
from typing import Any

from Service.csv_loader import load_terms_from_csv_dir
from Service.embeddings import dot_product, embed_query, embed_texts
from Service.text_utils import fuzzy_score, normalize_text


class SearchIndex:
    def __init__(self, index_path: Path):
        self.index_path = index_path
        self.terms: list[dict[str, Any]] = []
        self._by_normalized: dict[str, dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        if not self.index_path.exists():
            self.terms = []
            self._by_normalized = {}
            return

        with self.index_path.open("r", encoding="utf-8") as index_file:
            payload = json.load(index_file)

        self.terms = payload.get("terms", [])
        self._by_normalized = {item["normalized"]: item for item in self.terms}

    def embedded_terms_count(self) -> int:
        return sum(1 for item in self.terms if item.get("embedding"))

    def rebuild_from_csv_dir(self, csv_dir: Path) -> dict[str, int | str | None]:
        terms = load_terms_from_csv_dir(csv_dir)
        embedding_error = None

        try:
            embeddings = embed_texts([item["normalized"] for item in terms])
            for item, vector in zip(terms, embeddings):
                item["embedding"] = vector
        except Exception as error:
            embedding_error = str(error)
            for item in terms:
                item["embedding"] = []

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with self.index_path.open("w", encoding="utf-8") as index_file:
            json.dump({"terms": terms}, index_file)

        self.terms = terms
        self._by_normalized = {item["normalized"]: item for item in self.terms}
        return {
            "terms": len(self.terms),
            "embeddings": "created" if embedding_error is None else "skipped",
            "embedding_error": embedding_error,
        }

    def search(self, query: str) -> dict[str, str | None]:
        normalized_query = normalize_text(query)
        if not normalized_query:
            return {"query": query, "match": None}

        exact = self._by_normalized.get(normalized_query)
        if exact:
            return {"query": query, "match": exact["term"]}

        phrase_match = self._best_phrase_match(normalized_query)
        if phrase_match:
            return {"query": query, "match": phrase_match["term"]}

        fuzzy_match = self._best_fuzzy_match(normalized_query)
        if fuzzy_match:
            return {"query": query, "match": fuzzy_match["term"]}

        embedding_match = self._best_embedding_match(normalized_query)
        if embedding_match:
            return {"query": query, "match": embedding_match["term"]}

        return {"query": query, "match": None}

    def _best_phrase_match(self, normalized_query: str) -> dict[str, Any] | None:
        query_words = normalized_query.split()
        if len(query_words) < 2:
            return None

        best_item = None
        best_score = 0.0

        for item in self.terms:
            candidate = item["normalized"]
            candidate_words = candidate.split()
            if len(candidate_words) < 2:
                continue

            kinds = set(item.get("kinds", []))
            if not kinds.intersection({"Name", "SEO Title Tag", "slug"}):
                continue

            score = self._phrase_prefix_score(query_words, candidate_words)
            if score > best_score:
                best_item = item
                best_score = score

        if best_item and best_score >= 0.72:
            return best_item
        return None

    def _phrase_prefix_score(
        self, query_words: list[str], candidate_words: list[str]
    ) -> float:
        if len(query_words) > len(candidate_words):
            return 0.0

        scores = []
        for query_word, candidate_word in zip(query_words, candidate_words):
            if candidate_word.startswith(query_word):
                scores.append(1.0)
            else:
                scores.append(fuzzy_score(query_word, candidate_word))

        coverage = len(query_words) / len(candidate_words)
        return (sum(scores) / len(scores)) * 0.85 + coverage * 0.15

    def _best_fuzzy_match(self, normalized_query: str) -> dict[str, Any] | None:
        best_item = None
        best_score = 0.0

        for item in self.terms:
            candidate = item["normalized"]
            if abs(len(candidate) - len(normalized_query)) > 8:
                continue

            score = fuzzy_score(normalized_query, candidate)
            if len(normalized_query) <= 5 and candidate[0] != normalized_query[0]:
                score *= 0.8
            score += min(int(item.get("count", 1)), 50) / 1000
            if score > best_score:
                best_item = item
                best_score = score

        threshold = 0.70 if len(normalized_query) <= 5 else 0.78
        if best_item and best_score >= threshold:
            return best_item
        return None

    def _best_embedding_match(self, normalized_query: str) -> dict[str, Any] | None:
        if not self.terms:
            return None

        try:
            query_vector = embed_query(normalized_query)
        except Exception:
            return None
        best_item = None
        best_score = -1.0

        for item in self.terms:
            vector = item.get("embedding")
            if not vector:
                continue
            score = dot_product(query_vector, vector)
            if score > best_score:
                best_score = score
                best_item = item

        if best_item and best_score >= 0.72:
            return best_item
        return None
