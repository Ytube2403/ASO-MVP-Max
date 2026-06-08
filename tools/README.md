# Tools

- `run_aso_batch.py`: execute registered app and locale jobs from a JSON manifest.
- `export_master_keywords.py`: generate clean master keyword workbooks.
- `warm_ai_keyword_cache.py`: pre-run DeepSeek AI classification into `.cache/ai_keyword_analysis.sqlite3` without creating workbooks.
- `start_libretranslate.ps1`: start the Max local translation service with daily, extended or all model profiles.
- `check_libretranslate_quality.py`: run a manual quality smoke check against the Max local models.

The root scripts with the same names remain as compatibility entrypoints.
