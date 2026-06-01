# 🚀 ASO Keyword Filter Pipeline & Tracker (ASO-MVP) v4.0

Hệ thống tự động hóa nghiên cứu từ khóa, tối ưu hóa siêu dữ liệu (metadata), theo dõi chỉ số hiệu suất từ khóa và quản lý danh sách Master Keywords ASO dành cho các ứng dụng Android trên Google Play Store.

Hệ thống được thiết kế tối ưu cho việc cộng tác, chạy độc lập không phụ thuộc đường dẫn cứng (Portable), tích hợp công cụ đồng bộ hóa một chạm và bộ kiểm thử tự động.

---

## 🌟 Tính năng chính

### 1. Pipeline Lọc Từ Khóa ASO (v4.0)
* Chạy quy trình lọc 10 bước chuẩn hóa từ danh sách từ khóa thô (CSV từ AppTweak/SensorTower).
* Tích hợp cơ chế phân giải chính sách ngôn ngữ động theo thị trường thông qua [google_play_country_language_map.xlsx](file:///d:/Antigravity/ASO-Project/ASO-DEMO/google_play_country_language_map.xlsx).
* Phân loại tự động các từ khóa thành các nhóm: *Intent Core*, *Features*, *Styles*, *Visual*, *Noise*, *Competitors*, và phân bổ chúng vào các Bucket (*Metadata Shortlist*, *Consider*, *Generic Style Reserve*, *Language Mismatch*, *Manual Review*).
* Hỗ trợ **Interactive Mode** (`--interactive`) mở giao diện web trực quan để tự chọn từ khóa và soạn thảo mô tả ngắn/mô tả chi tiết ngay lập tức.
* Dùng hard-filter engine chung đã precompile matcher theo config, áp dụng đối xứng trên keyword raw và bản dịch `EN`.
* Dịch keyword qua shared translation service có SQLite WAL cache, TLS verification, retry và trạng thái audit nội bộ.
* Hỗ trợ chạy batch nhiều app/locale bằng manifest JSON với giới hạn concurrency.

### 2. Keyword Tracker Dashboard (Module A)
* Giao diện web SPA (Single Page Application) trực quan sử dụng Flask, Vanilla CSS và thư viện ECharts.
* Tự động quét cơ sở dữ liệu SQLite `keyword_tracker.db` để tính toán và hiển thị:
  * **ASO Power Score**: Điểm số sức mạnh tổng hợp của bộ từ khóa theo từng app/locale/tháng.
  * **Rank Tiers Distribution**: Phân bổ thứ hạng từ khóa (Top 3, Top 10, Top 30, Unranked).
  * **Movers**: Biến động từ khóa (Gainers tăng hạng, Losers giảm hạng, New xuất hiện, Lost mất dấu).
  * **Dual-axis Keyword Trend**: Biểu đồ so sánh tương quan xu hướng Volume và thứ hạng của từng từ khóa qua các tháng.

### 3. Master Keywords Export (Module B)
* Script gom tụ và làm sạch toàn bộ từ khóa từ mọi file CSV đầu vào lịch sử.
* Loại bỏ triệt để các từ khóa được gắn thẻ `irrelevant_intent` hoặc `noise_only` trong các file Excel báo cáo đầu ra.
* Xuất file Excel tổng hợp phân sheet theo từng Locale (quốc gia) dùng để nhập hàng loạt (batch import) vào AppTweak.

### 4. Công cụ đồng bộ một chạm (`Sync.bat`)
* Tập tin chạy tự động (Batch script) dành riêng cho người dùng không có nhiều kiến thức kỹ thuật (non-technical).
* Giao diện menu đơn giản để:
  * Cập nhật code mới nhất từ GitHub (`git pull`).
  * Lưu và đẩy code thay đổi lên GitHub (`git push`) với ghi chú tự động hoặc tùy chỉnh.
  * Xem trạng thái thay đổi hiện tại và thông tin commit gần nhất.
  * Hỗ trợ thiết lập môi trường lần đầu (Install Git, GitHub CLI, Clone repo).

---

## 📁 Cấu trúc thư mục dự án

```text
ASO-DEMO/
├── AR_Filter/               (Pipeline lọc từ khóa cho ứng dụng AR Filter)
├── App_Template/            (Thư mục mẫu để thiết lập cấu hình cho ứng dụng mới)
├── Control_Widget/          (Pipeline cho ứng dụng Control Widget)
├── Game_Emulator/           (Pipeline cho ứng dụng Game Emulator)
├── Prank_Sounds/            (Pipeline mới cho ứng dụng Prank Sounds)
│
├── shared/                  (Thư viện lõi dùng chung giữa các pipeline)
│   ├── language_detector.py (Logic phát hiện ngôn ngữ & phân loại theo market)
│   ├── keyword_filter/      (Package matcher, hard filter, classifier, validator, audit, cache & version)
│   ├── translation_service.py (Dịch EN dùng SQLite WAL cache, retry, rate limit & TLS verify)
│   ├── profile_service.py   (Custom/generated app profile cache & Google Play TLS verify)
│   ├── locale_parser.py     (Parser locale dùng chung)
│   ├── app_registry.py      (Registry alias app chính xác)
│   └── text_dedup.py        (Dedup Unicode indexed cho main shortlist & merge log)
│
├── tests/                   (Bộ kiểm thử tự động của dự án)
│   ├── test_language_detector.py
│   └── test_keyword_filter.py
│
├── Keyword_Tracker/         (Ứng dụng web Dashboard theo dõi chỉ số)
│   ├── run_dashboard.py     (API Server & Web launcher)
│   └── static/              (Giao diện Frontend HTML/CSS/JS + ECharts)
│
├── Docs_and_Templates/      (Các đặc tả thuật toán, thiết kế và từ điển tiếng Anh)
│   ├── ASO_Keyword_Planner_v4_0.md
│   └── english_words_10k.txt
│
├── Sync.bat                 (Công cụ đồng bộ một chạm cho người dùng)
├── run_aso_filter.py        (Bộ điều phối trung tâm định tuyến pipeline)
├── run_aso_batch.py         (Batch runner JSON cho nhiều app/locale)
├── export_master_keywords.py(Script xuất danh sách từ khóa Master sạch)
└── google_play_country_language_map.xlsx (Bản đồ phân phối ngôn ngữ quốc gia)
```

---

## 🛠️ Cài đặt & Chạy ứng dụng

### 1. Yêu cầu hệ thống
* Cài đặt Python phiên bản 3.9 trở lên.
* Cài đặt các thư viện phụ thuộc:
  ```powershell
  pip install flask openpyxl pandas langdetect snowballstemmer
  ```

### 2. Chạy Pipeline lọc từ khóa
Luôn sử dụng bộ điều phối trung tâm `run_aso_filter.py`. Đặt file CSV đầu vào (tên định dạng `AppName_Country_Language.csv`) tại thư mục bất kỳ và chạy:
```powershell
# Chạy chế độ tự động xuất Excel trực tiếp
python run_aso_filter.py --csv C:\duong_dan\ARFilter_US_EN.csv

# Chạy chế độ mở giao diện Web tương tác
python run_aso_filter.py --csv C:\duong_dan\ARFilter_US_EN.csv --interactive

# Filename chỉ có locale cần khai báo alias đã đăng ký
python run_aso_filter.py --csv C:\duong_dan\US_EN.csv --app Pranky
```

### 3. Chạy Dashboard theo dõi chỉ số
Mở terminal tại thư mục gốc và chạy:
```powershell
python Keyword_Tracker/run_dashboard.py
```
Ứng dụng sẽ tự động mở trình duyệt web tại địa chỉ `http://localhost:5000`.

### 4. Chạy batch nhiều app/locale
Tạo JSON manifest:
```json
{
  "jobs": [
    {"app": "Pranky", "csv": "path/to/Pranky_US_EN.csv"},
    {"app": "ARFilter", "csv": "path/to/ARFilter_BR_PT.csv"}
  ]
}
```

Chạy tối đa 3 locale song song:
```powershell
python run_aso_batch.py --manifest path\to\manifest.json --max-workers 3
```

### 5. Xuất Master Keywords
```powershell
# Xuất cho tất cả các ứng dụng có trong thư mục
python export_master_keywords.py --all
```
Kết quả sẽ xuất ra thư mục `Master_Keywords/`.

### 6. Chạy bộ kiểm thử tự động
Để đảm bảo code hoạt động tốt và không có lỗi sau khi chỉnh sửa:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

---

## ⚠️ Quy tắc phát triển (Quy định bắt buộc)
1. **Không sử dụng đường dẫn cứng (No Hardcoded Paths)**: Tất cả mã nguồn khi thêm mới hoặc chỉnh sửa phải dùng đường dẫn tương đối qua mô-đun `os.path` hoặc dựa trên `__file__`. Tuyệt đối không đưa đường dẫn tuyệt đối bắt đầu bằng chữ cái ổ đĩa (ví dụ: `C:\Users\...`) vào code chạy.
2. **Không bỏ qua kiểm thử**: Trước khi commit và đẩy mã nguồn lên GitHub, hãy chắc chắn chạy toàn bộ unit tests trong thư mục `tests/` và đảm bảo kết quả trả về `OK`.
3. **Đồng bộ hóa an toàn**: Luôn chạy `Sync.bat` (chọn cập nhật) trước khi tiến hành viết code để tránh xung đột mã nguồn.
