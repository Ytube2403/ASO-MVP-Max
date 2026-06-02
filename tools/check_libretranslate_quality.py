import argparse
import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared.translation_service import TranslationService, normalize_source_language


CASES = [
    ("MX_ES", "es", "sonidos de broma", {"prank", "sound", "sounds"}),
    ("BR_PT-BR", "pt", "sons de peido", {"fart", "sound", "sounds"}),
    ("ID_ID", "id", "suara lucu", {"funny", "sound", "sounds"}),
    ("IN_HI", "hi", "मजेदार आवाज़", {"funny", "sound", "sounds", "voice"}),
    ("PH_FIL", "fil", "nakakatawang tunog", {"funny", "sound", "sounds"}),
    ("PH_FIL", "fil+en", "tunog prank", {"prank", "sound", "sounds"}),
]


def main():
    parser = argparse.ArgumentParser(description="Smoke-check LibreTranslate models used by ASO-MVP-Max")
    parser.add_argument(
        "--cache",
        default=os.path.join(PROJECT_ROOT, ".cache", "libretranslate_quality.sqlite3"),
        help="Dedicated SQLite cache path for quality checks",
    )
    args = parser.parse_args()

    failures = []
    print("Market      Source -> Resolved  Seconds  Input -> English")
    print("-" * 100)
    for market, source, text, expected_tokens in CASES:
        service = TranslationService(args.cache, market=market)
        started = time.monotonic()
        result = service.translate(text, source)
        elapsed = time.monotonic() - started
        resolved = normalize_source_language(source, market)
        translated = result.text.strip()
        print(f"{market:<11} {source:<8} -> {resolved:<8} {elapsed:>7.3f}  {text} -> {translated}")
        normalized = translated.lower()
        if result.status == "FAILED_RAW_FALLBACK":
            failures.append(f"{market}/{source}: {result.error}")
        elif not translated or normalized == text.lower():
            failures.append(f"{market}/{source}: output is empty or unchanged")
        elif not any(token in normalized for token in expected_tokens):
            failures.append(f"{market}/{source}: expected one of {sorted(expected_tokens)}, got {translated!r}")

    if failures:
        print("\nQuality smoke failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("\nLibreTranslate quality smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
