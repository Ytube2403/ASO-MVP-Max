# Huong dan cau truc file ASO Keyword Filter v4.0

## Root

### `run_aso_filter.py`
Entrypoint chinh. Script parse locale, resolve alias qua `shared/app_registry.py`, archive CSV vao `apps/<AppName>/Input/<MMYYYY>/`, chay runner va ghi workbook vao `apps/<AppName>/Output/<MMYYYY>/`.

### `run_aso_batch.py`
Wrapper tuong thich cho `tools/run_aso_batch.py`. Chay nhieu locale tu JSON manifest, mac dinh toi da 3 job song song.

### `export_master_keywords.py`
Wrapper tuong thich cho `tools/export_master_keywords.py`. Quet input va workbook output cua app, tim sheet theo suffix `Dropped_Audit`, loai hard-drop va ghi workbook tong hop vao `data/master_keywords/`.

### `Sync.bat`
Cong cu pull, status va push mot cham cho nguoi dung Windows.

## `apps/`

Moi app co workspace rieng:

```text
apps/<AppName>/
|-- app_config.py
|-- App_Profile.json
|-- Input/<MMYYYY>/
|-- Output/<MMYYYY>/
`-- runner Python
```

App da dang ky:

- `apps/AR_Filter/`
- `apps/Control_Widget/`
- `apps/Game_Emulator/`
- `apps/Prank_Sounds/`
- `apps/App_Template/`

`AR_Filter`, `Control_Widget`, `Game_Emulator` dung runner `*_v4_0.py`. `Prank_Sounds` va `App_Template` dung `run_pipeline.py`.

## `shared/`

- `shared/paths.py`: nguon path tap trung cho `apps`, `docs`, `data` va `data/master_keywords`.
- `shared/app_registry.py`: map alias app chinh xac toi folder, runner va config.
- `shared/locale_parser.py`: parser locale dung chung cho orchestrator, exporter, tracker va batch.
- `shared/language_detector.py`: nhan dien ngon ngu theo market policy.
- `shared/keyword_filter/`: matcher precompiled, hard filter, classifier, validator, audit va cache atomic.
- `shared/text_dedup.py`: dedup Unicode cho `01_Main_Keyword_Shortlist`.
- `shared/translation_service.py`: dich EN, SQLite WAL cache, retry, rate limit va TLS verification.
- `shared/profile_service.py`: custom/generated profile cache va stale fallback.

## `tools/`

- `tools/run_aso_batch.py`: batch implementation.
- `tools/export_master_keywords.py`: Master Keywords exporter implementation.

Wrapper tai root duoc giu de cac lenh cu van chay.

## `tracker/`

- `tracker/run_dashboard.py`: Flask API va web launcher.
- `tracker/db_manager.py`: SQLite schema va query.
- `tracker/data_scanner.py`: quet CSV trong `apps/*/Input/`.
- `tracker/static/`: SPA HTML, CSS va JavaScript.

Database `tracker/keyword_tracker.db` la file local va khong commit len Git.

## `docs/`

- `docs/ASO_Keyword_Planner_v4_0.md`: dac ta logic pipeline.
- `docs/SETUP_WINDOWS.md`: checklist phan mem, extension, Python packages va cach kiem tra moi truong Windows.
- `docs/App_Config_Template.py`: template config.
- `docs/App_Profile_Template.json`: template profile.
- `docs/english_words_10k.txt`: whitelist tieng Anh.
- `docs/DESIGN.md`: design system cua dashboard.

## `data/`

- `data/google_play_country_language_map.xlsx`: mapping quoc gia va ngon ngu.
- `data/master_keywords/`: workbook Master Keywords generated, khong commit len Git.

## `tests/`

Regression test cho registry, parser locale, hard filter, dedup, translation, profile, exporter va batch runner.

## `releases/`

Chua zip package local. File zip bi ignore de repository source gon nhe.

## File setup tai root

- `requirements.txt`: danh sach Python packages cho moi truong pipeline day du.
- `.vscode/extensions.json`: de xuat extension VS Code cho Python, Pylance va CSV.
