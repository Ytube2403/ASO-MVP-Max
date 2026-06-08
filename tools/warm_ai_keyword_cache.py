import argparse
import importlib.util
import json
import os
import sys

import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared import ai_keyword_classifier
from shared.app_registry import registered_aliases, resolve_app


def _load_python_config(config_path):
    spec = importlib.util.spec_from_file_location("warm_ai_app_config", config_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load app config: {config_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    config = getattr(module, "APP_CONFIG", None)
    if not isinstance(config, dict):
        raise RuntimeError(f"APP_CONFIG dict not found in {config_path}")
    return dict(config)


def _load_app_profile(app_folder):
    profile_path = os.path.join(app_folder, "App_Profile.json")
    if not os.path.exists(profile_path):
        return {}
    with open(profile_path, "r", encoding="utf-8") as profile_file:
        return json.load(profile_file)


def _read_csv(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    if "Keyword" not in frame.columns:
        raise ValueError("Input CSV must contain a Keyword column")
    if "Volume" not in frame.columns:
        frame["Volume"] = 0
    if "Rank" not in frame.columns:
        frame["Rank"] = ""
    return frame


def _resolve_cache_path(config, explicit_cache_path):
    if explicit_cache_path:
        cache_path = explicit_cache_path
    else:
        classifier_config = (config.get("ai_keyword_classifier", {}) or {})
        cache_path = classifier_config.get("cache_path") or ".cache/ai_keyword_analysis.sqlite3"
    if not os.path.isabs(cache_path):
        cache_path = os.path.join(PROJECT_ROOT, cache_path)
    return cache_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Warm the DeepSeek AI keyword classification cache without creating workbooks."
    )
    parser.add_argument("--csv", required=True, help="Path to input CSV containing at least a Keyword column.")
    parser.add_argument(
        "--app",
        required=True,
        help="Registered app alias, for example ARFilter, PrankSounds, ControlWidget.",
    )
    parser.add_argument("--market", default="", help="Optional market override, for example VN_VI or US_EN.")
    parser.add_argument("--cache-path", default="", help="Optional SQLite cache override.")
    args = parser.parse_args(argv)

    try:
        app = resolve_app(args.app, PROJECT_ROOT)
    except KeyError as exc:
        aliases = ", ".join(registered_aliases())
        raise SystemExit(f"{exc}\nKnown aliases: {aliases}") from exc

    config = _load_python_config(app["config_path"])
    if args.market:
        config["market"] = args.market
    market = args.market or config.get("market", "")
    app_folder = os.path.join(PROJECT_ROOT, *app["folder"].split("/"))
    app_profile = _load_app_profile(app_folder)
    frame = _read_csv(args.csv)
    cache_path = _resolve_cache_path(config, args.cache_path)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    result = ai_keyword_classifier.analyze_dataframe(
        frame,
        config,
        app_profile=app_profile,
        cache_path=cache_path,
        market=market,
    )

    print("Warm AI keyword cache completed.")
    print(f"app={app['key']}")
    print(f"market={market}")
    print(f"rows={len(frame)}")
    print(f"cache_path={cache_path}")
    print("AIStatus summary:")
    for status, count in result["AIStatus"].value_counts().sort_index().items():
        print(f"  {status}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
