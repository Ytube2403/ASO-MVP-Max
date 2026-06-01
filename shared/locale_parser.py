import os
import re


LOCALE_SUFFIX = re.compile(
    r"(?:^|_)(?P<country>[A-Za-z]{2})[_-](?P<language>[A-Za-z]{2,3}(?:-[A-Za-z]{2})?)(?:_Output|_master)?$",
    re.IGNORECASE,
)


def canonicalize_locale(country, language):
    return f"{str(country).upper()}_{str(language).upper()}"


def extract_locale_from_filename(filename, default=None):
    base = os.path.splitext(os.path.basename(str(filename or "")))[0]
    match = LOCALE_SUFFIX.search(base)
    if not match:
        return default
    return canonicalize_locale(match.group("country"), match.group("language"))


def split_app_and_locale(filename):
    base = os.path.splitext(os.path.basename(str(filename or "")))[0]
    match = LOCALE_SUFFIX.search(base)
    if not match:
        return None, None
    app_name = base[:match.start()].rstrip("_")
    return app_name or None, canonicalize_locale(match.group("country"), match.group("language"))
