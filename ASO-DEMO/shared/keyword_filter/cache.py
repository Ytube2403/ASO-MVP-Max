import hashlib
import json
import os
import re
import tempfile

from .version import FILTER_LOGIC_VERSION


def file_md5(path):
    try:
        digest = hashlib.md5()
        with open(path, "rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return ""


def config_hash(config):
    serialized = json.dumps(config or {}, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_selection_cache_meta(input_path, market, config=None):
    return {
        "filter_version": FILTER_LOGIC_VERSION,
        "app_id": str((config or {}).get("app_id", "")),
        "config_hash": config_hash(config or {}),
        "market": str(market or ""),
        "input_file": os.path.basename(str(input_path or "")),
        "input_hash": file_md5(input_path) if input_path else "",
    }


def _path_part(value, fallback):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "")).strip("._")
    return cleaned or fallback


def selection_cache_path(cache_root, config, input_path, market):
    meta = build_selection_cache_meta(input_path, market, config)
    app_part = _path_part(config.get("app_id") or config.get("category_slug"), "app")
    market_part = _path_part(market, "market")
    input_part = _path_part(meta["input_hash"][:16], "input")
    return os.path.join(cache_root, ".cache", "selected_keywords", app_part, market_part, f"{input_part}.json")


def atomic_write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    handle, temporary_path = tempfile.mkstemp(prefix=".tmp-", suffix=".json", dir=os.path.dirname(path))
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, indent=4, ensure_ascii=False)
        os.replace(temporary_path, path)
    except Exception:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)
        raise


def unwrap_selection_payload(payload):
    if isinstance(payload, dict) and isinstance(payload.get("selection"), dict):
        return payload.get("selection"), payload.get("_cache_meta", {})
    return payload, {}


def is_selection_cache_valid(payload, expected_meta):
    _, meta = unwrap_selection_payload(payload)
    return bool(meta) and all(str(meta.get(key, "")) == str(value or "") for key, value in expected_meta.items())


def wrap_selection_payload(selection, meta):
    if not isinstance(selection, dict):
        return selection
    wrapped = dict(selection)
    wrapped["_cache_meta"] = meta
    wrapped["selection"] = {key: value for key, value in selection.items() if key != "_cache_meta"}
    return wrapped
