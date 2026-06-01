import html as html_lib
import json
import os
import re
import ssl
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from shared.keyword_filter.cache import atomic_write_json


PROFILE_STATUSES = {
    "CUSTOM",
    "GENERATED_FRESH",
    "GENERATED_STALE_FALLBACK",
    "EMPTY_FETCH_FAILED",
}


def empty_profile(config, status="EMPTY_FETCH_FAILED", error=""):
    return {
        "app_id": config.get("app_id", ""),
        "last_checked": datetime.now().isoformat(),
        "title": "",
        "short_description": "",
        "full_description": "",
        "competitors": [],
        "ProfileStatus": status,
        "ProfileError": str(error or "")[-1000:],
    }


def adapt_custom_profile(profile, config):
    if "schema_version" not in profile and "competitor_strategy" not in profile:
        adapted = dict(profile)
    else:
        adapted = {
            "app_id": profile.get("app_identity", {}).get("app_id", config.get("app_id", "")),
            "title": profile.get("app_identity", {}).get("title", ""),
            "short_description": profile.get("live_store_metadata", {}).get("short_description", ""),
            "full_description": profile.get("live_store_metadata", {}).get("full_description_digest", {}).get("one_sentence_summary", ""),
            "competitors": [],
            "last_checked": datetime.now().isoformat(),
        }
        for competitor in profile.get("competitor_strategy", {}).get("suggested_competitors", []):
            description = " ".join(competitor.get("overlap_keywords", []))
            if competitor.get("why_relevant"):
                description = f"{description} {competitor['why_relevant']}".strip()
            adapted["competitors"].append({
                "package_id": competitor.get("package_id", ""),
                "title": competitor.get("title", ""),
                "short_description": competitor.get("short_description") or competitor.get("why_relevant", ""),
                "desc200": competitor.get("desc200") or description[:200],
            })
    adapted["ProfileStatus"] = "CUSTOM"
    adapted["ProfileError"] = ""
    return adapted


def _read_json(path):
    with open(path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def _parse_description(page):
    match = re.search(r'data-g-id="description"[^>]*>(.+?)</div>', page, re.DOTALL)
    if match:
        text = re.sub(r"<[^>]+>", "\n", match.group(1))
        return html_lib.unescape(re.sub(r"\n+", "\n", text).strip())
    match = re.search(r'\[\[null,"([^"]{50,})"\s*\]\]', page)
    if match:
        return html_lib.unescape(match.group(1).replace("\\u003cbr\\u003e", "\n").replace("\\n", "\n"))
    return ""


def _parse_app_page(page, package_id=""):
    title = ""
    match = re.search(r'<meta property="og:title" content="([^"]+)"', page)
    if match:
        title = re.sub(r"\s*-\s*Apps on Google Play$", "", html_lib.unescape(match.group(1)))
    match = re.search(r'<meta name="(?:description|twitter:description)" content="([^"]+)"', page)
    short_description = html_lib.unescape(match.group(1)) if match else ""
    full_description = _parse_description(page)
    return {
        "package_id": package_id,
        "title": title,
        "short_description": short_description,
        "desc200": full_description[:200],
        "full_description": full_description,
    }


def _default_fetch(url, timeout=10):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    with urllib.request.urlopen(request, context=ssl.create_default_context(), timeout=timeout) as response:
        return response.read().decode("utf-8")


def scrape_profile(config, seed_query, fetcher=None):
    fetcher = fetcher or _default_fetch
    app_id = config["app_id"]
    own_page = fetcher(f"https://play.google.com/store/apps/details?id={app_id}&hl=en&gl=US")
    own = _parse_app_page(own_page, app_id)
    search_page = fetcher(f"https://play.google.com/store/search?q={urllib.parse.quote_plus(seed_query)}&c=apps&hl=en&gl=US")
    competitors = []
    seen = {app_id}
    for package_id in re.findall(r'href="/store/apps/details\?id=([a-zA-Z0-9._]+)"', search_page):
        if package_id in seen:
            continue
        seen.add(package_id)
        page = fetcher(f"https://play.google.com/store/apps/details?id={package_id}&hl=en&gl=US")
        parsed = _parse_app_page(page, package_id)
        parsed.pop("full_description", None)
        competitors.append(parsed)
        if len(competitors) >= 3:
            break
    return {
        "app_id": app_id,
        "last_checked": datetime.now().isoformat(),
        "title": own["title"],
        "short_description": own["short_description"],
        "full_description": own["full_description"],
        "competitors": competitors,
        "ProfileStatus": "GENERATED_FRESH",
        "ProfileError": "",
    }


def get_app_profile(config, seed_query, app_folder, ttl_days=14, fetcher=None):
    app_folder = os.path.abspath(app_folder)
    custom_path = os.path.join(app_folder, "App_Profile.json")
    generated_path = os.path.join(app_folder, ".cache", "profiles", "generated_profile.json")
    if os.path.exists(custom_path):
        try:
            return adapt_custom_profile(_read_json(custom_path), config)
        except Exception as exc:
            custom_error = f"Custom profile error: {type(exc).__name__}: {exc}"
        else:
            custom_error = ""
    else:
        custom_error = ""

    stale_profile = None
    if os.path.exists(generated_path):
        try:
            stale_profile = _read_json(generated_path)
            checked = datetime.fromisoformat(stale_profile.get("last_checked", "2000-01-01"))
            if datetime.now() - checked < timedelta(days=ttl_days):
                stale_profile["ProfileStatus"] = "GENERATED_FRESH"
                stale_profile["ProfileError"] = custom_error
                return stale_profile
        except Exception as exc:
            custom_error = f"{custom_error} Generated cache error: {type(exc).__name__}: {exc}".strip()
            stale_profile = None

    try:
        profile = scrape_profile(config, seed_query, fetcher=fetcher)
        atomic_write_json(generated_path, profile)
        return profile
    except Exception as exc:
        error = f"{custom_error} Fetch error: {type(exc).__name__}: {exc}".strip()
        if stale_profile is not None:
            stale_profile["ProfileStatus"] = "GENERATED_STALE_FALLBACK"
            stale_profile["ProfileError"] = error[-1000:]
            return stale_profile
        return empty_profile(config, error=error)
