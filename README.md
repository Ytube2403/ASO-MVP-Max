# ASO-MVP-Max Keyword Filter Pipeline & Tracker v4.0

Ban Max dung LibreTranslate self-host de dich keyword local. He thong ASO gom pipeline loc keyword, dashboard theo doi chi so va cong cu xuat Master Keywords.

## Cau truc thu muc

```text
ASO-MVP-Max/
|-- apps/                         # Workspace rieng cua tung app
|   |-- AR_Filter/
|   |-- Control_Widget/
|   |-- Game_Emulator/
|   |-- Prank_Sounds/
|   `-- App_Template/
|
|-- shared/                       # Engine dung chung bat buoc
|   |-- keyword_filter/           # Matcher, hard filter, classifier, validator, audit, cache
|   |-- app_registry.py           # Alias -> app folder -> runner -> config
|   |-- paths.py                  # Nguon path tap trung cho workspace
|   |-- locale_parser.py
|   |-- language_detector.py
|   |-- translation_service.py
|   |-- profile_service.py
|   `-- text_dedup.py
|
|-- tools/                        # Cong cu van hanh
|   |-- run_aso_batch.py
|   |-- export_master_keywords.py
|   |-- start_libretranslate.ps1
|   `-- check_libretranslate_quality.py
|
|-- tracker/                      # Dashboard Flask va SQLite local
|   |-- run_dashboard.py
|   `-- static/
|
|-- docs/                         # Dac ta, template, guide va tu dien
|   |-- ASO_Keyword_Planner_v4_0.md
|   |-- SETUP_WINDOWS.md
|   |-- README_File_Guide.md
|   `-- english_words_10k.txt
|
|-- .vscode/                      # Extension VS Code de xuat
|-- requirements.txt              # Python packages cho moi truong day du
|-- data/                         # Tai nguyen dung chung va output tong hop
|   |-- google_play_country_language_map.xlsx
|   `-- master_keywords/          # Generated, khong commit len Git
|
|-- releases/                     # Zip package local, khong commit len Git
|-- tests/                        # Regression test
|-- run_aso_filter.py             # Entrypoint chinh
|-- run_aso_batch.py              # Wrapper tuong thich cho tools/run_aso_batch.py
|-- export_master_keywords.py     # Wrapper tuong thich cho tools/export_master_keywords.py
`-- Sync.bat
```

## Nguyen tac

- Moi app giu `app_config.py`, `App_Profile.json`, `Input/`, `Output/` va runner rieng trong `apps/<AppName>/`.
- Logic loc, parser locale, dich, profile va dedup phai dung module trong `shared/`.
- Tai nguyen dung chung nam trong `data/`; tai lieu nam trong `docs/`.
- Lenh cu tai root van duoc giu de khong lam hong workflow hien co.

## Cai dat

Huong dan day du cho may Windows moi:

- [Checklist phan mem, extension va cong cu](docs/SETUP_WINDOWS.md)

Tao virtual environment va cai day du Python packages:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Kiem tra nhanh:

```powershell
python -c "import flask, langdetect, numpy, openpyxl, pandas, snowballstemmer; print('Python environment OK')"
```

## Chay LibreTranslate local

Pipeline dich keyword moi sang English bang LibreTranslate self-host. Mo mot terminal PowerShell rieng tai thu muc `ASO-MVP-Max`, sau do chay daily profile:

```powershell
.\tools\start_libretranslate.ps1
```

Helper tao `.venv-libretranslate`, cai LibreTranslate `1.9.6`, load cac model daily `en,es,pt,pb,id,hi,tl` va khoi dong service tai `http://127.0.0.1:5001` voi `2` thread. Giu terminal nay mo khi chay pipeline.

Khi can audit ngoai ngu rong hon:

```powershell
.\tools\start_libretranslate.ps1 -Profile extended
```

Chi dung `-Profile all` khi may du tai nguyen va that su can load tat ca model.

Kiem tra service:

```powershell
Invoke-RestMethod http://127.0.0.1:5001/health
python tools\check_libretranslate_quality.py
```

Neu can doi endpoint, dat bien moi truong truoc khi chay pipeline:

```powershell
$env:LIBRETRANSLATE_URL = "http://127.0.0.1:5001"
```

Neu endpoint da bat API key, dat them `$env:LIBRETRANSLATE_API_KEY`.

Neu muon dich lai toan bo keyword bang model moi, xoa cache local:

```powershell
Remove-Item .cache\translations.sqlite3*
```

## Chay pipeline

Luon uu tien orchestrator trung tam:

```powershell
python run_aso_filter.py --csv C:\duong_dan\ARFilter_US_EN.csv
python run_aso_filter.py --csv C:\duong_dan\ARFilter_US_EN.csv --interactive
python run_aso_filter.py --csv C:\duong_dan\US_EN.csv --app Pranky
```

Orchestrator archive CSV vao `apps/<AppName>/Input/<MMYYYY>/` va ghi workbook vao `apps/<AppName>/Output/<MMYYYY>/`.

## Chay dashboard

```powershell
python tracker/run_dashboard.py
```

Dashboard mo tai `http://localhost:5000`.

## Chay batch

Manifest mau:

```json
{
  "jobs": [
    {"app": "Pranky", "csv": "path/to/Pranky_US_EN.csv"},
    {"app": "ARFilter", "csv": "path/to/ARFilter_BR_PT.csv"}
  ]
}
```

```powershell
python run_aso_batch.py --manifest path\to\manifest.json
```

Khi cache LibreTranslate con trong, batch tu dong chay `1` locale moi luc. Khi cache da warm, mac dinh toi da `2` locale song song.

## Xuat Master Keywords

```powershell
python export_master_keywords.py --all
```

Ket qua nam trong `data/master_keywords/`.

## Kiem thu

```powershell
python -m unittest discover -s tests -v
python -m compileall -q .
```

## Tai lieu

- [Dac ta pipeline v4.0](docs/ASO_Keyword_Planner_v4_0.md)
- [Cai dat Windows day du](docs/SETUP_WINDOWS.md)
- [Huong dan cac file](docs/README_File_Guide.md)
- [Template app moi](apps/App_Template/README.md)
