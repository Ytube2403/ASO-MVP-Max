import os
import ssl
import urllib.request

from shared.translation_service import DEFAULT_BASE_URL


def translation_required_for_market(market):
    if str(os.environ.get("ASO_SKIP_TRANSLATION_PREFLIGHT", "")).strip().lower() in {"1", "true", "yes"}:
        return False
    return True


def libretranslate_url():
    return str(os.environ.get("LIBRETRANSLATE_URL") or DEFAULT_BASE_URL).rstrip("/")


def check_libretranslate_health(base_url=None, timeout=3):
    url = str(base_url or libretranslate_url()).rstrip("/")
    request = urllib.request.Request(f"{url}/health")
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            response.read()
        return True, url, ""
    except Exception as exc:
        return False, url, f"{type(exc).__name__}: {exc}"


def require_translation_service_for_market(market, timeout=3):
    if not translation_required_for_market(market):
        return True
    ok, url, error = check_libretranslate_health(timeout=timeout)
    if ok:
        return True
    raise RuntimeError(
        f"LibreTranslate is required before running market {market}, but {url}/health is not reachable. "
        "Start it in a separate PowerShell terminal with: .\\tools\\start_libretranslate.ps1. "
        f"Health error: {error}"
    )
