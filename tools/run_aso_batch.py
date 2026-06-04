import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shared.app_registry import resolve_app
from shared.keyword_filter import atomic_write_json
from shared.locale_parser import extract_locale_from_filename
from shared.translation_preflight import check_libretranslate_health, translation_required_for_market
from shared.translation_service import translation_cache_count


def load_manifest(path):
    with open(path, "r", encoding="utf-8-sig") as file_handle:
        payload = json.load(file_handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise ValueError("Batch manifest must be an object with a jobs array")
    return payload


def validate_jobs(payload, project_root, manifest_path=""):
    manifest_dir = os.path.dirname(os.path.abspath(manifest_path)) if manifest_path else project_root
    validated = []
    errors = []
    for index, item in enumerate(payload.get("jobs", [])):
        label = f"jobs[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        app_alias = str(item.get("app", "") or "").strip()
        csv_value = str(item.get("csv", "") or "").strip()
        if not app_alias or not csv_value:
            errors.append(f"{label} requires app and csv")
            continue
        csv_path = csv_value if os.path.isabs(csv_value) else os.path.abspath(os.path.join(manifest_dir, csv_value))
        if not os.path.exists(csv_path):
            errors.append(f"{label} CSV does not exist: {csv_path}")
            continue
        try:
            app = resolve_app(app_alias, project_root)
        except KeyError as exc:
            errors.append(f"{label} {exc}")
            continue
        market = str(item.get("market", "") or "").strip().upper()
        detected_market = extract_locale_from_filename(csv_path)
        if not market:
            market = detected_market or ""
        if not market:
            errors.append(f"{label} CSV filename has no supported locale and no market override: {csv_path}")
            continue
        if detected_market and item.get("market") and market != detected_market:
            errors.append(f"{label} market override {market} does not match filename locale {detected_market}")
            continue
        validated.append({
            "index": index,
            "app": app_alias,
            "app_key": app["key"],
            "csv": csv_path,
            "market": market,
        })
    if errors:
        raise ValueError("; ".join(errors))
    if not validated:
        raise ValueError("Batch manifest contains no jobs")
    return validated


def _result_file(stdout):
    match = re.search(r"Result file:\s*(.+)", stdout or "")
    return match.group(1).strip() if match else ""


def execute_job(job, project_root, python_executable=None):
    started = time.monotonic()
    command = [
        python_executable or sys.executable,
        os.path.join(project_root, "run_aso_filter.py"),
        "--csv",
        job["csv"],
        "--app",
        job["app"],
    ]
    result = subprocess.run(
        command,
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    elapsed = round(time.monotonic() - started, 3)
    combined_error = (result.stderr or result.stdout or "")[-2000:]
    return {
        **job,
        "output": _result_file(result.stdout),
        "elapsed_seconds": elapsed,
        "status": "SUCCESS" if result.returncode == 0 else "FAILED",
        "exit_code": result.returncode,
        "error_excerpt": "" if result.returncode == 0 else combined_error,
    }


def effective_worker_count(project_root, max_workers=2, cold_cache_workers=1):
    cache_path = os.path.join(project_root, ".cache", "translations.sqlite3")
    cache_count = translation_cache_count(cache_path)
    cache_state = "WARM" if cache_count else "COLD"
    workers = max_workers if cache_count else cold_cache_workers
    return cache_state, cache_count, max(1, int(workers))


def ensure_translation_preflight(jobs, health_check_fn=None):
    markets = sorted({
        str(job.get("market", "") or "")
        for job in jobs
        if translation_required_for_market(job.get("market", ""))
    })
    if not markets:
        return {"required": False, "markets": [], "url": "", "error": ""}
    health_check_fn = health_check_fn or check_libretranslate_health
    ok, url, error = health_check_fn()
    if not ok:
        raise RuntimeError(
            "LibreTranslate is required before running ASO-MVP-Max markets "
            f"({', '.join(markets)}), but {url}/health is not reachable. "
            "Start it in a separate PowerShell terminal with: .\\tools\\start_libretranslate.ps1. "
            f"Health error: {error}"
        )
    return {"required": True, "markets": markets, "url": url, "error": ""}


def run_jobs(jobs, project_root, max_workers=2, executor_fn=None):
    executor_fn = executor_fn or (lambda job: execute_job(job, project_root))
    results = []
    with ThreadPoolExecutor(max_workers=max(1, int(max_workers))) as executor:
        futures = [executor.submit(executor_fn, job) for job in jobs]
        for future in as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda item: item["index"])


def main():
    parser = argparse.ArgumentParser(description="Run registered ASO app locales from a JSON manifest")
    parser.add_argument("--manifest", required=True, help="Path to JSON batch manifest")
    parser.add_argument("--max-workers", type=int, default=2, help="Maximum concurrent locale jobs with warm LibreTranslate cache")
    parser.add_argument("--cold-cache-workers", type=int, default=1, help="Concurrent locale jobs before LibreTranslate cache is populated")
    parser.add_argument("--report", default="", help="Optional JSON report path")
    args = parser.parse_args()

    project_root = PROJECT_ROOT
    manifest_path = os.path.abspath(args.manifest)
    try:
        jobs = validate_jobs(load_manifest(manifest_path), project_root, manifest_path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    try:
        preflight = ensure_translation_preflight(jobs)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if preflight["required"]:
        print(
            "LibreTranslate preflight OK: "
            f"{preflight['url']} for markets {', '.join(preflight['markets'])}."
        )
    cache_state, cache_count, effective_workers = effective_worker_count(
        project_root,
        max_workers=args.max_workers,
        cold_cache_workers=args.cold_cache_workers,
    )
    print(
        f"Translation cache: {cache_state} ({cache_count} LibreTranslate entries). "
        f"Running {effective_workers} locale job(s) concurrently."
    )
    results = run_jobs(jobs, project_root, max_workers=effective_workers)
    report_path = args.report or os.path.join(
        project_root,
        ".cache",
        "batch_reports",
        f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )
    report = {
        "generated_at": datetime.now().isoformat(),
        "cache_state": cache_state,
        "translation_cache_entries": cache_count,
        "requested_max_workers": max(1, int(args.max_workers)),
        "cold_cache_workers": max(1, int(args.cold_cache_workers)),
        "effective_workers": effective_workers,
        "jobs": results,
        "summary": {
            "total": len(results),
            "success": sum(item["status"] == "SUCCESS" for item in results),
            "failed": sum(item["status"] == "FAILED" for item in results),
        },
    }
    atomic_write_json(os.path.abspath(report_path), report)
    print(f"Batch report: {os.path.abspath(report_path)}")
    print(f"Summary: {report['summary']}")
    return 1 if report["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
