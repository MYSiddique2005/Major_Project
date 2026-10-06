"""The enterprise knowledge base and its retrieval.

Entries are short passages about this company's data and rules (app/knowledge/content.py).
Retrieval is lexical: BM25 over each entry's title, keywords and text. The collection is a few dozen
passages written in the same vocabulary users ask in, so keyword ranking finds the right passage
without an embedding model or a second external service.
"""
import math
import re
from collections import Counter
from dataclasses import dataclass, field

CATEGORIES = ("schema", "definition", "rule", "workflow", "access", "data")

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    "a an and are as at be by can do does for from has have how i in is it its me my of on or our that the "
    "their there this to was we what when which who why will with you your".split()
)
_SUFFIXES = ("ing", "ed", "es", "s")
TITLE_WEIGHT, KEYWORD_WEIGHT = 3, 2
K1, B = 1.5, 0.75


def tokenize(text: str) -> list[str]:
    """Lower-case words without stopwords, with plural and verb endings removed (orders -> order)."""
    tokens = []
    for word in _WORD.findall(text.lower()):
        if word in _STOPWORDS:
            continue
        for suffix in _SUFFIXES:
            if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                word = word[: -len(suffix)]
                break
        tokens.append(word)
    return tokens


@dataclass(frozen=True)
class Entry:
    id: str
    title: str
    category: str
    text: str
    keywords: str = ""  # other words people use for the same thing

    def summary(self) -> dict:
        return {"id": self.id, "title": self.title, "category": self.category}


@dataclass(frozen=True)
class Match:
    entry: Entry
    score: float


@dataclass
class KnowledgeBase:
    entries: list[Entry]
    _terms: list[Counter] = field(init=False, repr=False)
    _lengths: list[int] = field(init=False, repr=False)
    _document_frequency: Counter = field(init=False, repr=False)

    def __post_init__(self) -> None:
        ids = [entry.id for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("Knowledge entry ids must be unique")
        self._terms = [
            Counter(
                tokenize(entry.title) * TITLE_WEIGHT + tokenize(entry.keywords) * KEYWORD_WEIGHT + tokenize(entry.text)
            )
            for entry in self.entries
        ]
        self._lengths = [sum(terms.values()) for terms in self._terms]
        self._document_frequency = Counter(term for terms in self._terms for term in terms)

    def get(self, entry_id: str) -> Entry | None:
        return next((entry for entry in self.entries if entry.id == entry_id), None)

    def search(self, query: str, limit: int = 4, category: str | None = None) -> list[Match]:
        """The entries most relevant to `query`, best first. Entries sharing no word with it are left out."""
        query_terms = set(tokenize(query))
        count = len(self.entries)
        average_length = sum(self._lengths) / count if count else 0
        matches = []
        for entry, terms, length in zip(self.entries, self._terms, self._lengths):
            if category and entry.category != category:
                continue
            score = 0.0
            for term in query_terms:
                frequency = terms.get(term, 0)
                if not frequency:
                    continue
                containing = self._document_frequency[term]
                inverse = math.log(1 + (count - containing + 0.5) / (containing + 0.5))
                score += inverse * frequency * (K1 + 1) / (frequency + K1 * (1 - B + B * length / average_length))
            if score > 0:
                matches.append(Match(entry, round(score, 3)))
        matches.sort(key=lambda match: match.score, reverse=True)
        return matches[:limit]
