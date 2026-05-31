import re
import unicodedata

try:
    from langdetect import DetectorFactory, detect_langs

    DetectorFactory.seed = 0
    HAS_LANGDETECT = True
except Exception:
    HAS_LANGDETECT = False


LANG_ALIASES = {
    "fil": "fil",
    "tl": "fil",
    "tagalog": "fil",
    "pt-br": "pt",
    "pt_br": "pt",
    "es-mx": "es",
    "es_mx": "es",
    "zh-cn": "zh",
    "zh_cn": "zh",
    "zh-tw": "zh",
    "zh_tw": "zh",
}

MARKET_OVERRIDES = {
    "PH_FIL": {"primary": ["fil", "tl"], "secondary": ["en"], "mixed_allowed": True},
    "PH_TL": {"primary": ["fil", "tl"], "secondary": ["en"], "mixed_allowed": True},
    "PH_EN": {"primary": ["en"], "secondary": ["fil", "tl"], "mixed_allowed": True},
    "US_EN": {"primary": ["en"], "secondary": ["es"], "mixed_allowed": True},
    "IN_HI": {"primary": ["hi"], "secondary": ["en"], "mixed_allowed": True},
    "ID_ID": {"primary": ["id"], "secondary": ["en"], "mixed_allowed": True},
    "BR_PT": {"primary": ["pt"], "secondary": ["en"], "mixed_allowed": True},
    "MX_ES": {"primary": ["es"], "secondary": ["en"], "mixed_allowed": True},
    "VN_VI": {"primary": ["vi"], "secondary": ["en"], "mixed_allowed": True},
    "TH_TH": {"primary": ["th"], "secondary": ["en"], "mixed_allowed": True},
    "JP_JA": {"primary": ["ja"], "secondary": ["en"], "mixed_allowed": True},
}

COUNTRY_SECONDARY_DEFAULTS = {
    "CA": {"en": ["fr"], "fr": ["en"]},
    "CH": {"de": ["fr", "it", "en"], "fr": ["de", "it", "en"], "it": ["de", "fr", "en"]},
    "BE": {"nl": ["fr", "en"], "fr": ["nl", "en"]},
    "SG": {"en": ["zh", "ms", "ta"], "zh": ["en"], "ms": ["en"], "ta": ["en"]},
}

DEFAULT_ENGLISH_WORDS = {
    "app", "apps", "free", "download", "android", "new", "best", "top", "pro", "lite",
    "game", "games", "sound", "sounds", "funny", "prank", "filter", "filters", "photo",
    "editor", "camera", "widget", "theme", "launcher", "control", "panel", "simulator",
    "music", "video", "voice", "changer", "keyboard", "vpn", "cleaner", "scanner",
    "tiktok", "snapchat", "instagram", "youtube", "facebook", "whatsapp", "google",
}

LANG_LEXICONS = {
    "fil": {
        "tunog", "nakakatawa", "nakakatawang", "para", "sa", "kaibigan", "kaibiganin",
        "laro", "libre", "gupit", "biro", "kalokohan", "aso", "pusa", "mukha", "kuha",
    },
    "es": {
        "de", "del", "la", "el", "los", "las", "para", "con", "sin", "gratis",
        "sonido", "sonidos", "broma", "bromas", "divertido", "divertidos", "juego",
        "juegos", "foto", "fotos", "editor", "camara", "filtro", "filtros", "centro",
        "maquina", "corte", "pelo", "cabello", "bocina", "bocinas", "risa", "risas",
        "gracioso", "graciosos", "graciosa", "graciosas", "choque", "choques", "pum"
    },
    "pt": {
        "de", "da", "do", "para", "com", "sem", "gratis", "som", "sons", "brincadeira",
        "foto", "fotos", "editor", "camera", "filtro", "filtros", "jogo", "jogos",
        "barulho", "barulhos", "maquina", "cortar", "corte", "cabelo", "peido", "peidos",
        "buzina", "buzinas", "risada", "risadas", "engracado", "engracada", "engracados",
        "choque", "choques", "pegadinha", "pegadinhas", "pum", "barbeador", "barbeiro",
        "simulador", "trote", "sirene", "arma", "armas", "vidro", "quebrado", "tosse",
        "porta", "campainha"
    },
    "vi": {
        "ung", "dung", "mien", "phi", "anh", "chinh", "sua", "tro", "choi", "am",
        "thanh", "vui", "nhon", "bo", "loc",
    },
    "id": {
        "aplikasi", "gratis", "suara", "lucu", "kamera", "foto", "filter", "permainan",
        "editor", "musik", "video",
    },
}

LANGDETECT_CONFUSION = {
    "no": ["en"],
    "da": ["en"],
    "it": ["en", "es"],
    "ro": ["en"],
    "sl": ["en"],
    "so": ["en"],
    "id": ["en"],
    "af": ["en"],
    "cy": ["en"],
    "sw": ["en"],
}


def normalize_lang_code(lang):
    lang = str(lang or "").strip().lower().replace("_", "-")
    if not lang:
        return ""
    if lang in LANG_ALIASES:
        return LANG_ALIASES[lang]
    return LANG_ALIASES.get(lang.split("-")[0], lang.split("-")[0])


def lang_match(left, right):
    return normalize_lang_code(left) == normalize_lang_code(right)


def parse_market(market):
    market = str(market or "US_EN").strip()
    if "_" in market:
        country, lang = market.split("_", 1)
        return country.upper(), normalize_lang_code(lang)
    return market.upper(), "en"


def _dedupe_langs(langs):
    out = []
    for lang in langs:
        norm = normalize_lang_code(lang)
        if norm and norm not in out:
            out.append(norm)
    return out


def get_market_language_policy(market, config=None):
    country, target_lang = parse_market(market)
    market_key = f"{country}_{target_lang.upper()}"

    if market_key in MARKET_OVERRIDES:
        policy = MARKET_OVERRIDES[market_key]
        return {
            "primary": _dedupe_langs(policy["primary"]),
            "secondary": _dedupe_langs(policy.get("secondary", [])),
            "mixed_allowed": bool(policy.get("mixed_allowed", True)),
        }

    explicit = (config or {}).get("market_language_policy", {})
    explicit_primary = _dedupe_langs(explicit.get("primary_languages", []))
    explicit_secondary = _dedupe_langs(explicit.get("secondary_languages", []))

    if target_lang in explicit_primary:
        return {
            "primary": explicit_primary,
            "secondary": [lang for lang in explicit_secondary if lang not in explicit_primary],
            "mixed_allowed": explicit.get("mixed_language_action", "manual_review") != "drop",
        }

    country_defaults = COUNTRY_SECONDARY_DEFAULTS.get(country, {})
    secondary = country_defaults.get(target_lang)
    if secondary is None:
        secondary = ["en"] if target_lang != "en" else []

    return {
        "primary": _dedupe_langs([target_lang]),
        "secondary": [lang for lang in _dedupe_langs(secondary) if lang != target_lang],
        "mixed_allowed": True,
    }


def _strip_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def _latin_tokens(text):
    normalized = _strip_accents(text.lower())
    return [tok for tok in re.split(r"[^a-z0-9]+", normalized) if tok]


def _unicode_tokens(text):
    tokens = []
    current = []
    for char in str(text).lower():
        cat = unicodedata.category(char)
        if cat.startswith("L") or cat.startswith("N"):
            current.append(char)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return tokens


def _script_languages(text):
    langs = set()
    for char in str(text):
        code = ord(char)
        if 0x0E00 <= code <= 0x0E7F:
            langs.add("th")
        elif 0x3040 <= code <= 0x30FF:
            langs.add("ja")
        elif 0x4E00 <= code <= 0x9FFF:
            langs.add("zh")
        elif 0xAC00 <= code <= 0xD7AF:
            langs.add("ko")
        elif 0x0600 <= code <= 0x06FF:
            langs.add("ar")
        elif 0x0400 <= code <= 0x04FF:
            langs.add("ru")
        elif 0x0900 <= code <= 0x097F:
            langs.add("hi")
    if "ja" in langs and "zh" in langs:
        langs.discard("zh")
    return langs


def _get_root_word(word):
    word = word.lower()
    if len(word) > 4:
        for suffix in ("ing", "est"):
            if word.endswith(suffix):
                return word[: -len(suffix)]
        for suffix in ("ed", "es", "er"):
            if word.endswith(suffix):
                return word[: -len(suffix)]
    if len(word) > 3 and word.endswith("s"):
        return word[:-1]
    return word


def _build_english_words(config=None, english_vocab=None):
    words = set(DEFAULT_ENGLISH_WORDS)
    if english_vocab:
        words.update(str(w).lower() for w in english_vocab if w)
    for key in ("intent_core_words", "intent_core_terms", "feature_terms", "style_terms", "visual_terms", "noise_terms"):
        for term in (config or {}).get(key, []):
            for token in _latin_tokens(str(term)):
                words.add(token)
    return words


def _classify_by_policy(lang, policy):
    if any(lang_match(lang, p) for p in policy["primary"]):
        return normalize_lang_code(lang), "PRIMARY"
    if any(lang_match(lang, s) for s in policy["secondary"]):
        return normalize_lang_code(lang), "SECONDARY"
    return normalize_lang_code(lang), "FOREIGN"


def _classify_latin_tokens(tokens, policy, config=None, english_vocab=None):
    english_words = _build_english_words(config, english_vocab)
    token_langs = []
    lexicon_order = _dedupe_langs(policy.get("primary", []) + policy.get("secondary", []) + list(LANG_LEXICONS.keys()))

    # Determine search order for language lexicons: check policy's primary languages first
    primary_langs = policy.get("primary", [])
    other_langs = [l for l in LANG_LEXICONS if l not in primary_langs]
    check_order = primary_langs + other_langs

    for token in tokens:
        root = _get_root_word(token)
        primary_matched = None
        for lang in policy.get("primary", []):
            lexicon = LANG_LEXICONS.get(lang, set())
            if token in lexicon or root in lexicon:
                primary_matched = lang
                break
        if primary_matched:
            token_langs.append(primary_matched)
            continue
        if token in english_words or root in english_words:
            token_langs.append("en")
            continue
        matched = None
        for lang in check_order:
            lexicon = LANG_LEXICONS.get(lang, set())
            if token in lexicon or root in lexicon:
                matched = lang
                break
        if matched:
            token_langs.append(matched)

    if not token_langs:
        return None

    unique_langs = _dedupe_langs(token_langs)
    if len(unique_langs) == 1 and len(token_langs) == len(tokens):
        return _classify_by_policy(unique_langs[0], policy)

    primary_hits = [lang for lang in unique_langs if any(lang_match(lang, p) for p in policy["primary"])]
    secondary_hits = [lang for lang in unique_langs if any(lang_match(lang, s) for s in policy["secondary"])]
    if primary_hits and secondary_hits:
        if len(token_langs) >= max(1, len(tokens) - 1):
            return "+".join(_dedupe_langs(primary_hits + secondary_hits)), "MIXED"

    if len(unique_langs) == 1 and len(token_langs) >= max(1, len(tokens) - 1):
        return _classify_by_policy(unique_langs[0], policy)

    counts = {}
    for lang in token_langs:
        counts[lang] = counts.get(lang, 0) + 1
    dominant_lang, dominant_count = max(counts.items(), key=lambda item: item[1])
    if dominant_count >= max(2, len(token_langs) - 1):
        return _classify_by_policy(dominant_lang, policy)

    return None


def _detect_with_langdetect(text, policy, word_count):
    if not HAS_LANGDETECT:
        return None
    try:
        langs = detect_langs(text)
    except Exception:
        return None
    if not langs:
        return None

    best_lang = normalize_lang_code(langs[0].lang)
    prob = langs[0].prob

    if any(lang_match(best_lang, p) for p in policy["primary"]):
        return best_lang, "PRIMARY"
    if any(lang_match(best_lang, s) for s in policy["secondary"]):
        return best_lang, "SECONDARY"

    if word_count <= 3 and best_lang in LANGDETECT_CONFUSION:
        for candidate in LANGDETECT_CONFUSION[best_lang]:
            if any(lang_match(candidate, p) for p in policy["primary"]):
                return normalize_lang_code(candidate), "PRIMARY"
            if any(lang_match(candidate, s) for s in policy["secondary"]):
                return normalize_lang_code(candidate), "SECONDARY"

    min_prob = 0.85 if word_count <= 2 else 0.7 if word_count <= 3 else 0.6
    if prob >= min_prob:
        return best_lang, "FOREIGN"
    return None


def detect_keyword_language(keyword, market_lang, config=None, english_vocab=None):
    text = str(keyword or "").strip()
    policy = get_market_language_policy(market_lang or (config or {}).get("market", "US_EN"), config)

    if not text:
        return "unknown", "UNKNOWN"

    scripts = _script_languages(text)
    latin_tokens = _latin_tokens(text)
    unicode_tokens = _unicode_tokens(text)
    token_count = len(unicode_tokens) or len(latin_tokens)

    if scripts and not latin_tokens:
        if len(scripts) == 1:
            return _classify_by_policy(next(iter(scripts)), policy)
        return "+".join(sorted(scripts)), "MIXED" if policy["mixed_allowed"] else "UNKNOWN"

    if scripts and latin_tokens:
        latin_result = _classify_latin_tokens(latin_tokens, policy, config, english_vocab)
        script_lang = next(iter(scripts)) if len(scripts) == 1 else None
        if script_lang and latin_result:
            latin_lang, latin_group = latin_result
            script_lang, script_group = _classify_by_policy(script_lang, policy)
            if {latin_group, script_group} <= {"PRIMARY", "SECONDARY"}:
                return "+".join(_dedupe_langs([script_lang, latin_lang])), "MIXED"
        return _detect_with_langdetect(text, policy, token_count) or ("unknown", "UNKNOWN")

    latin_result = _classify_latin_tokens(latin_tokens, policy, config, english_vocab)
    if latin_result:
        return latin_result

    detected = _detect_with_langdetect(text, policy, token_count)
    if detected:
        return detected

    return "unknown", "UNKNOWN"
