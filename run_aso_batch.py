import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from shared.app_registry import resolve_app
from shared.keyword_filter import atomic_write_json
from shared.locale_parser import extract_locale_from_filename


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


def run_jobs(jobs, project_root, max_workers=3, executor_fn=None):
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
    parser.add_argument("--max-workers", type=int, default=3, help="Maximum concurrent locale jobs")
    parser.add_argument("--report", default="", help="Optional JSON report path")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.abspath(__file__))
    manifest_path = os.path.abspath(args.manifest)
    try:
        jobs = validate_jobs(load_manifest(manifest_path), project_root, manifest_path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    results = run_jobs(jobs, project_root, max_workers=args.max_workers)
    report_path = args.report or os.path.join(
        project_root,
        ".cache",
        "batch_reports",
        f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    )
    report = {
        "generated_at": datetime.now().isoformat(),
        "max_workers": max(1, int(args.max_workers)),
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
