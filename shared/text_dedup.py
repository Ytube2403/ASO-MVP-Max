from dataclasses import dataclass
import unicodedata

try:
    import snowballstemmer
except Exception:
    snowballstemmer = None


DEFAULT_DEDUP_POLICY = {
    "auto_merge_token_bag": False,
    "accent_fold_auto_merge_locales": [],
}

TEXT_DEDUP_LOG_COLUMNS = [
    "Table",
    "Action",
    "ClusterId",
    "DedupRule",
    "Confidence",
    "RemovedKeyword",
    "RemovedVolume",
    "KeptKeyword",
    "KeptVolume",
    "OriginalSection",
    "NormalizedKey",
    "BalancedScore",
    "Note",
]

SNOWBALL_LANGUAGES = {
    "ar": "arabic",
    "hy": "armenian",
    "eu": "basque",
    "ca": "catalan",
    "da": "danish",
    "nl": "dutch",
    "en": "english",
    "eo": "esperanto",
    "et": "estonian",
    "fi": "finnish",
    "fr": "french",
    "de": "german",
    "el": "greek",
    "hi": "hindi",
    "hu": "hungarian",
    "id": "indonesian",
    "ga": "irish",
    "it": "italian",
    "lt": "lithuanian",
    "ne": "nepali",
    "no": "norwegian",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
    "sr": "serbian",
    "es": "spanish",
    "sv": "swedish",
    "ta": "tamil",
    "tr": "turkish",
    "yi": "yiddish",
}

DICTIONARY_SEGMENTATION_SCRIPTS = {
    "Burmese",
    "Han",
    "Hiragana",
    "Japanese",
    "Katakana",
    "Khmer",
    "Lao",
    "Thai",
}

_STEMMER_CACHE = {}
_FALLBACK_INFLECTION_LANGUAGES = {"en", "es", "pt"}


def _policy(config=None):
    merged = dict(DEFAULT_DEDUP_POLICY)
    if config:
        merged.update(config.get("dedup_policy", config) or {})
    return merged


def _lang_code(language):
    language = str(language or "").strip().lower().replace("_", "-")
    if not language or "+" in language:
        return ""
    return language.split("-")[0]


def _default_language(config=None):
    market = str((config or {}).get("market", "") or "")
    if "_" in market:
        return _lang_code(market.split("_", 1)[1])
    return _lang_code(market)


def _char_script(char):
    code = ord(char)
    if 0x0041 <= code <= 0x024F or 0x1E00 <= code <= 0x1EFF:
        return "Latin"
    if 0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F:
        return "Arabic"
    if 0x0900 <= code <= 0x097F:
        return "Devanagari"
    if 0x0E00 <= code <= 0x0E7F:
        return "Thai"
    if 0x0E80 <= code <= 0x0EFF:
        return "Lao"
    if 0x1000 <= code <= 0x109F:
        return "Burmese"
    if 0x1780 <= code <= 0x17FF:
        return "Khmer"
    if 0x3040 <= code <= 0x309F:
        return "Hiragana"
    if 0x30A0 <= code <= 0x30FF or 0xFF65 <= code <= 0xFF9F:
        return "Katakana"
    if 0x4E00 <= code <= 0x9FFF:
        return "Han"
    if 0xAC00 <= code <= 0xD7AF:
        return "Hangul"
    if 0x0400 <= code <= 0x04FF:
        return "Cyrillic"
    if 0x0370 <= code <= 0x03FF:
        return "Greek"
    return ""


def script_profile(text):
    scripts = []
    for char in str(text or ""):
        script = _char_script(char)
        if script and script not in scripts:
            scripts.append(script)
    if ("Hiragana" in scripts or "Katakana" in scripts) and "Han" in scripts:
        scripts = [script for script in scripts if script != "Han"]
        if "Japanese" not in scripts:
            scripts.append("Japanese")
    return tuple(sorted(scripts))


def normalize_text(text):
    """Build a display-independent Unicode key without deleting meaningful marks."""
    text = unicodedata.normalize("NFKC", str(text or "")).casefold().strip()
    out = []
    previous_was_space = False
    for char in text:
        category = unicodedata.category(char)
        if category[0] in {"L", "N", "M"} or char in {"\u200c", "\u200d"}:
            out.append(char)
            previous_was_space = False
        elif not previous_was_space:
            out.append(" ")
            previous_was_space = True
    return "".join(out).strip()


def _accent_fold_latin(text):
    folded = []
    last_script = ""
    for char in unicodedata.normalize("NFD", normalize_text(text)):
        script = _char_script(char)
        if script:
            last_script = script
        if unicodedata.category(char) == "Mn" and last_script == "Latin":
            continue
        folded.append(char)
    return unicodedata.normalize("NFC", "".join(folded))


class TokenizerAdapter:
    def tokenize(self, text, language=""):
        raise NotImplementedError

    def is_trusted(self, text, language=""):
        raise NotImplementedError


class UnicodeTokenizer(TokenizerAdapter):
    def tokenize(self, text, language=""):
        normalized = normalize_text(text)
        tokens = []
        current = []
        for char in normalized:
            category = unicodedata.category(char)
            if category[0] in {"L", "N", "M"} or char in {"\u200c", "\u200d"}:
                current.append(char)
            elif current:
                tokens.append("".join(current))
                current = []
        if current:
            tokens.append("".join(current))
        return tokens

    def is_trusted(self, text, language=""):
        scripts = set(script_profile(text))
        return not bool(scripts & DICTIONARY_SEGMENTATION_SCRIPTS)


DEFAULT_TOKENIZER = UnicodeTokenizer()


def _stemmer(language):
    code = _lang_code(language)
    algorithm = SNOWBALL_LANGUAGES.get(code)
    if not algorithm or snowballstemmer is None:
        return None
    if algorithm not in _STEMMER_CACHE:
        _STEMMER_CACHE[algorithm] = snowballstemmer.stemmer(algorithm)
    return _STEMMER_CACHE[algorithm]


def _fallback_stem_word(word, language):
    """Collapse common plural variants when the optional Snowball package is absent."""
    code = _lang_code(language)
    if code not in _FALLBACK_INFLECTION_LANGUAGES:
        return word

    if code == "pt":
        if len(word) > 3 and word.endswith("ões"):
            return word[:-3] + "ão"
        if len(word) > 3 and word.endswith("ns"):
            return word[:-2] + "m"
        if len(word) > 3 and word.endswith("s") and word[-2] in "aáâãeéêiíoóôõuú":
            return word[:-1]
        return word

    if code == "es":
        if len(word) > 3 and word.endswith("s") and word[-2] in "aáeéiíoóuú":
            return word[:-1]
        return word

    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def _fallback_stem_tokens(tokens, language):
    if _lang_code(language) not in _FALLBACK_INFLECTION_LANGUAGES:
        return ()
    return tuple(_fallback_stem_word(token, language) for token in tokens)


def _stem_tokens(tokens, language):
    stemmer = _stemmer(language)
    if not stemmer:
        return _fallback_stem_tokens(tokens, language)
    try:
        return tuple(stemmer.stemWords(list(tokens)))
    except Exception:
        return _fallback_stem_tokens(tokens, language)


@dataclass(frozen=True)
class DedupKeys:
    surface_key: str
    token_sequence_key: tuple
    stemmed_sequence_key: tuple
    stemmed_token_bag_key: tuple
    accent_fold_review_key: str
    script_profile: tuple
    language: str
    tokenization_trusted: bool


def build_dedup_keys(text, language="", policy=None, tokenizer=None):
    tokenizer = tokenizer or DEFAULT_TOKENIZER
    surface = normalize_text(text)
    trusted = tokenizer.is_trusted(surface, language)
    tokens = tuple(tokenizer.tokenize(surface, language))
    stems = _stem_tokens(tokens, language) if trusted else ()
    return DedupKeys(
        surface_key=surface,
        token_sequence_key=tokens if trusted else (),
        stemmed_sequence_key=stems,
        stemmed_token_bag_key=tuple(sorted(stems)) if stems else (),
        accent_fold_review_key=_accent_fold_latin(surface),
        script_profile=script_profile(surface),
        language=_lang_code(language),
        tokenization_trusted=trusted,
    )


def token_bag_key(text, language="", config=None):
    keys = build_dedup_keys(text, language or _default_language(config), config)
    if not keys.tokenization_trusted:
        return ""
    return " ".join(sorted(keys.token_sequence_key))


def _number(value, default=0.0):
    try:
        if value is None or str(value).strip() == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def winner_sort_key(record, original_index=0):
    rank = _number(record.get("Rank_numeric", record.get("Rank", 999)), 999)
    return (
        -_number(record.get("Volume"), 0),
        -_number(record.get("Max. Volume"), 0),
        -_number(record.get("BalancedScore"), 0),
        rank,
        -_number(record.get("KEI"), 0),
        original_index,
    )


def _language_for_record(record, default_language):
    detected = str(record.get("DetectedLanguage", "") or "")
    return detected if detected and detected.lower() != "unknown" else default_language


def _compatible_profiles(left, right):
    return not left or not right or left == right


def _auto_match(left, right, policy):
    if left.surface_key and left.surface_key == right.surface_key:
        return "surface_key", 1.0, left.surface_key
    accent_fold_locales = {
        _lang_code(locale)
        for locale in policy.get("accent_fold_auto_merge_locales", [])
    }
    if (
        left.accent_fold_review_key
        and left.accent_fold_review_key == right.accent_fold_review_key
        and left.language
        and left.language == right.language
        and left.language in accent_fold_locales
    ):
        return "accent_fold_allowlist", 0.90, left.accent_fold_review_key
    if not _compatible_profiles(left.script_profile, right.script_profile):
        return None
    if left.stemmed_sequence_key and left.stemmed_sequence_key == right.stemmed_sequence_key:
        return "stemmed_sequence_key", 0.95, " ".join(left.stemmed_sequence_key)
    if (
        policy.get("auto_merge_token_bag", False)
        and left.stemmed_token_bag_key
        and left.stemmed_token_bag_key == right.stemmed_token_bag_key
    ):
        return "stemmed_token_bag_key", 0.90, " ".join(left.stemmed_token_bag_key)
    return None


class _UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))

    def find(self, index):
        while self.parent[index] != index:
            self.parent[index] = self.parent[self.parent[index]]
            index = self.parent[index]
        return index

    def union(self, left, right):
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


@dataclass
class DedupResult:
    records: list
    log_entries: list


def _variant_text(records, indexes):
    ordered = sorted(indexes, key=lambda index: winner_sort_key(records[index], index))
    seen = []
    for index in ordered:
        keyword = str(records[index].get("Keyword", "") or "")
        if keyword and keyword not in seen:
            seen.append(keyword)
    return "; ".join(seen)


def _indexed_auto_groups(keys, policy):
    groups = {}
    accent_fold_locales = {
        _lang_code(locale)
        for locale in policy.get("accent_fold_auto_merge_locales", [])
    }
    for index, item in enumerate(keys):
        if item.surface_key:
            groups.setdefault(("surface", item.surface_key), []).append(index)
        if item.accent_fold_review_key and item.language in accent_fold_locales:
            groups.setdefault(("accent", item.language, item.accent_fold_review_key), []).append(index)
        if item.stemmed_sequence_key:
            groups.setdefault(("stem_sequence", item.stemmed_sequence_key), []).append(index)
        if policy.get("auto_merge_token_bag", False) and item.stemmed_token_bag_key:
            groups.setdefault(("stem_bag", item.stemmed_token_bag_key), []).append(index)
    return groups.values()


def _union_auto_matches(keys, policy, union_find):
    seen_pairs = set()
    for indexes in _indexed_auto_groups(keys, policy):
        representatives = []
        for index in indexes:
            matched = False
            for representative in representatives:
                pair = (min(index, representative), max(index, representative))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                if _auto_match(keys[representative], keys[index], policy):
                    union_find.union(representative, index)
                    matched = True
                    break
            if not matched:
                representatives.append(index)


def _log_entry(
    table,
    action,
    cluster_id,
    rule,
    confidence,
    kept,
    other,
    normalized_key,
    note,
):
    return {
        "Table": table,
        "Action": action,
        "ClusterId": cluster_id,
        "DedupRule": rule,
        "Confidence": round(float(confidence), 4),
        "RemovedKeyword": other.get("Keyword", ""),
        "RemovedVolume": other.get("Volume", 0),
        "KeptKeyword": kept.get("Keyword", ""),
        "KeptVolume": kept.get("Volume", 0),
        "OriginalSection": other.get("Bucket", other.get("Section", "")),
        "NormalizedKey": normalized_key,
        "BalancedScore": other.get("BalancedScore", 0),
        "Note": note,
    }


def deduplicate_candidates(records, sheet_name, language="", policy=None, tokenizer=None):
    policy = _policy(policy)
    records = [dict(record) for record in records]
    default_language = _lang_code(language)
    keys = [
        build_dedup_keys(
            record.get("Keyword", ""),
            _language_for_record(record, default_language),
            policy,
            tokenizer,
        )
        for record in records
    ]
    union_find = _UnionFind(len(records))

    _union_auto_matches(keys, policy, union_find)

    clusters = {}
    for index in range(len(records)):
        clusters.setdefault(union_find.find(index), []).append(index)

    winners = []
    log_entries = []
    for cluster_number, indexes in enumerate(clusters.values(), start=1):
        winner_index = min(indexes, key=lambda index: winner_sort_key(records[index], index))
        winner = records[winner_index]
        winner["MergedVariants"] = _variant_text(records, [i for i in indexes if i != winner_index])
        winners.append(winner)
        cluster_id = f"{sheet_name}:{cluster_number:04d}"
        for index in indexes:
            if index == winner_index:
                continue
            match = _auto_match(keys[winner_index], keys[index], policy)
            rule, confidence, normalized_key = match or ("cluster_match", 0.90, keys[winner_index].surface_key)
            log_entries.append(
                _log_entry(
                    sheet_name,
                    "PRUNED",
                    cluster_id,
                    rule,
                    confidence,
                    winner,
                    records[index],
                    normalized_key,
                    "Keyword remains in All Candidates pool",
                )
            )

    return DedupResult(winners, log_entries)


def prepare_dataframe(df, sheet_name, config=None, language=""):
    """Deduplicate a pandas DataFrame while keeping pandas optional in shared logic."""
    if df is None or df.empty:
        return df.copy(), []
    result = deduplicate_candidates(
        df.to_dict("records"),
        sheet_name,
        language or _default_language(config),
        config,
    )
    import pandas as pd

    prepared = pd.DataFrame(result.records)
    for column in df.columns:
        if column not in prepared.columns:
            prepared[column] = ""
    return prepared, result.log_entries


def normalize_log_entries(entries):
    """Fill required fields for any legacy pruning records still emitted by runners."""
    normalized = []
    for entry in entries:
        normalized_entry = dict(entry)
        normalized_entry.setdefault("Action", "PRUNED")
        normalized_entry.setdefault("ClusterId", "")
        normalized_entry.setdefault("DedupRule", "legacy_normalized_key")
        normalized_entry.setdefault("Confidence", 1.0)
        normalized_entry.setdefault("RemovedVolume", normalized_entry.get("Volume", ""))
        normalized_entry.setdefault("KeptVolume", "")
        normalized_entry.setdefault("OriginalSection", normalized_entry.get("Table", ""))
        normalized_entry.setdefault("Note", "")
        normalized.append(normalized_entry)
    return normalized
