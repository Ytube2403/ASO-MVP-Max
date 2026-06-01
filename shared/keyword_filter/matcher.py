import re
import unicodedata
from functools import lru_cache

from .audit import AuditMatch


def normalize_filter_text(text):
    text = str(text or "").lower().strip()
    text = "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    text = re.sub(r"[-_]+", " ", text)
    text = re.sub(r"[^\w\s]+", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text):
    return [token for token in normalize_filter_text(text).split() if token]


class CompiledTermMatcher:
    def __init__(self, terms):
        self.patterns = [
            (str(term), _term_pattern(str(term)))
            for term in terms or []
            if normalize_filter_text(term)
        ]

    def find(self, text, rule="term", source="raw"):
        normalized = normalize_filter_text(text)
        for term, pattern in self.patterns:
            if pattern and pattern.search(normalized):
                return AuditMatch(rule=rule, term=term, source=source)
        return None


def compile_terms(terms):
    return CompiledTermMatcher(terms)


@lru_cache(maxsize=8192)
def _term_pattern(term):
    normalized = normalize_filter_text(term)
    if not normalized:
        return None
    return re.compile(r"(?<!\w)" + re.escape(normalized) + r"(?!\w)", re.UNICODE)


def has_term(text, terms):
    return bool(find_term(text, terms))


def find_term(text, terms, rule="term", source="raw"):
    matcher = terms if isinstance(terms, CompiledTermMatcher) else compile_terms(terms)
    return matcher.find(text, rule=rule, source=source)


def row_texts(value):
    if hasattr(value, "get") and not isinstance(value, str):
        candidates = [("raw", value.get("Keyword", "")), ("EN", value.get("EN", ""))]
    else:
        candidates = [("raw", value)]

    output = []
    seen = {}
    for source, text in candidates:
        normalized = normalize_filter_text(text)
        if not normalized:
            continue
        if normalized in seen:
            existing_source, existing_text = output[seen[normalized]]
            output[seen[normalized]] = ("raw+EN", existing_text)
            continue
        seen[normalized] = len(output)
        output.append((source, text))
    return output


def find_any_term(value, terms, rule="term"):
    for source, text in row_texts(value):
        match = find_term(text, terms, rule=rule, source=source)
        if match:
            return match
    return None


def has_any_term(value, terms):
    return bool(find_any_term(value, terms))
