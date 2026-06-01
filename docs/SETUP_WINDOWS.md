# Huong dan cai dat day du tren Windows

Tai lieu nay danh cho may Windows moi. Muc tieu la chay day du pipeline ASO, workbook Excel, dashboard, batch runner, dedup theo ngon ngu va cong cu dong bo Git.

## 1. Checklist nhanh

### Bat buoc de chay pipeline

| Cong cu | Muc dich | Ghi chu |
|---|---|---|
| Windows 10/11 64-bit | Moi truong chay | PowerShell co san trong Windows |
| [Python](https://www.python.org/downloads/windows/) 3.11+ 64-bit | Chay pipeline va test | Khi cai dat, dam bao lenh `python` hoat dong trong terminal |
| Python packages trong `requirements.txt` | Xu ly CSV, Excel, dashboard, detect ngon ngu va stemming | Cai bang `python -m pip install -r requirements.txt` |
| Trinh duyet web hien dai | Mo dashboard va interactive selector | Microsoft Edge hoac Google Chrome deu duoc |
| Microsoft Excel hoac [LibreOffice Calc](https://www.libreoffice.org/download/download-libreoffice/) | Mo va review workbook `.xlsx` | Excel duoc khuyen nghi de xem format chinh xac nhat |

### Bat buoc neu clone, pull hoac push source code

| Cong cu | Muc dich | Ghi chu |
|---|---|---|
| [Git for Windows](https://git-scm.com/install/windows) | Clone, pull, commit va push | `Sync.bat` can Git |
| [GitHub CLI](https://cli.github.com/) | Dang nhap GitHub tu terminal | `Sync.bat` dung lenh `gh auth login` |

### Khuyen nghi cho viec chinh sua code va CSV

| Cong cu | Muc dich |
|---|---|
| [Visual Studio Code](https://code.visualstudio.com/docs/setup/windows) | Sua config, JSON, Python va CSV |
| Extension [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) | Chon interpreter, debug va chay test |
| Extension [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) | IntelliSense va kiem tra code Python |
| Extension [Rainbow CSV](https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv) | Xem CSV theo cot, lint va filter nhanh |

Khi mo workspace bang VS Code, file `.vscode/extensions.json` se de xuat ba extension tren.

## 2. Nhung thu khong can cai rieng

- Khong can Node.js, npm, Java, Docker hoac database server.
- SQLite da nam trong Python standard library. Pipeline dung SQLite cho translation cache va tracker database local.
- PowerShell va Microsoft Edge thuong da co san tren Windows.
- AppTweak hoac Sensor Tower chi la nguon xuat CSV. Pipeline khong bat buoc cai extension hay SDK cua cac dich vu nay.

## 3. Cai dat tu dau

Mo PowerShell tai thu muc `ASO-MVP`:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Neu PowerShell chan script activate:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

## 4. Y nghia cua Python packages

| Package | Vai tro | Muc do |
|---|---|---|
| `numpy` | Tinh diem normalize va vector numeric | Bat buoc |
| `pandas` | Doc CSV, DataFrame va xu ly keyword | Bat buoc |
| `openpyxl` | Doc va ghi workbook Excel `.xlsx` | Bat buoc |
| `flask` | Chay Keyword Tracker Dashboard local | Bat buoc neu dung dashboard |
| `langdetect` | Fallback detect ngon ngu cho keyword kho | Khuyen nghi manh |
| `snowballstemmer` | Gom bien the so it/so nhieu theo locale | Khuyen nghi manh de dedup day du |

Pipeline co fallback bao thu khi thieu `langdetect` hoac `snowballstemmer`, nhung mot moi truong hoan chinh nen cai du ca hai. Neu thieu `snowballstemmer`, test Snowball se hien `skipped` va dedup chi dung fallback noi bo.

## 5. Kiem tra moi truong

Sau khi cai packages:

```powershell
python -c "import flask, langdetect, numpy, openpyxl, pandas, snowballstemmer; print('Python environment OK')"
python -m unittest discover -s tests -v
python -m compileall -q .
```

Test suite phai ket thuc bang `OK` va khong con dong Snowball `skipped`.

## 6. Dang nhap GitHub cho Sync.bat

Chi can neu dung `Sync.bat` hoac tu dong pull/push:

```powershell
git --version
gh --version
gh auth login --web --git-protocol https
gh auth status
```

## 7. Chay thu pipeline

Tu thu muc `ASO-MVP`:

```powershell
python run_aso_filter.py --csv C:\duong_dan\Pranky_US_EN.csv
python tracker\run_dashboard.py
```

Dashboard mo tai `http://localhost:5000`.

## 8. Ket noi mang

- Can internet neu pipeline dich keyword moi sang English hoac refresh profile tu Google Play.
- Co the chay offline neu da co `App_Profile.json` va translation cache phu hop.
- Neu dung GitHub clone, pull hoac push thi can internet va quyen truy cap repository.

## 9. Xu ly loi nhanh

### `ModuleNotFoundError`

Kiem tra da activate dung `.venv`, sau do cai lai:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Test Snowball bi `skipped`

```powershell
python -m pip install snowballstemmer
python -m unittest tests.test_text_dedup -v
```

### Lenh `python` hoac `git` khong tim thay

Dong va mo lai terminal sau khi cai dat. Neu van loi, kiem tra bien moi truong `PATH`.

### Workbook dang mo nen khong ghi de duoc

Dong file `.xlsx` trong Excel hoac truyen `--output` voi ten file moi.
