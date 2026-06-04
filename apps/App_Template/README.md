# 🛠️ ASO App Template — Hướng Dẫn Cấu Hình Ứng Dụng Mới

Thư mục mẫu này được thiết kế để giúp bạn dễ dàng thiết lập quy trình lọc từ khóa ASO cho bất kỳ ứng dụng mới nào mà không cần phải can thiệp trực tiếp vào mã nguồn của pipeline (khoảng 1500 dòng code).

Hệ thống được thiết kế theo hướng **tách biệt cấu hình và mã nguồn**: toàn bộ thông số cấu hình nằm trong file `app_config.py` và hồ sơ ứng dụng nằm trong file `App_Profile.json`.

Trước khi chạy lần đầu trên máy Windows mới, làm theo [hướng dẫn cài đặt đầy đủ](../../docs/SETUP_WINDOWS.md).

---

## 📁 Cấu trúc thư mục mẫu

```text
apps/App_Template/
├── README.md                      (Tài liệu hướng dẫn này)
├── app_config.py                  (Nơi điền từ khóa, thương hiệu đối thủ, trọng số điểm)
├── App_Profile.json               (Nơi điền mô tả hiện tại và đối thủ của app)
├── PROJECT_MEMORY.md              (Snapshot setup tự sinh sau mỗi lần chạy pipeline thành công)
├── run_pipeline.py                (Mã nguồn chạy 10 bước lọc - KHÔNG cần chỉnh sửa)
├── interactive_optimizer.html     (Giao diện Web tối ưu hóa từ khóa)
└── interactive_description_editor.html (Giao diện Web soạn thảo mô tả ASO)
```

---

## ⚙️ Các bước cấu hình ứng dụng mới

### Bước 1: Khai báo thông tin định danh và từ khóa trong `app_config.py`
Mở file `app_config.py` bằng bất kỳ trình soạn thảo mã nguồn nào và chỉnh sửa các mục sau:
1. **Thông tin cơ bản (Identity):** Cập nhật `app_id` (package id), `app_name`, `category` và thị trường mục tiêu mặc định (`market`).
2. **Bộ từ khóa chính (Semantic Groups):**
   * `intent_core_terms`: Các từ khóa chính thể hiện ý định tìm kiếm app (ví dụ: `photo editor`, `crop photo`).
   * `feature_terms`: Các tính năng chính (ví dụ: `retouch`, `filter`, `collage`).
   * `style_terms`: Các phong cách thiết kế, IP hoặc giao diện (ví dụ: `aesthetic`, `vintage`). LƯU Ý: Những từ này chỉ được phân bổ vào Full Description để tránh vi phạm bản quyền.
3. **Bộ lọc loại bỏ (Filters):**
   * `competitor_brands`: Thương hiệu đối thủ (sẽ bị loại khỏi các slot metadata chính để tránh bị quét vi phạm).
   * `noise_terms`: Các từ chung chung quá rộng (như `app`, `free`, `download`, `android`).
   * `typo_blacklist`: Từ viết sai chính tả hoặc từ vô nghĩa từ auto-suggest.

### Bước 2: Điền thông tin cửa hàng trong `App_Profile.json`
Mở file `App_Profile.json` và điền:
1. `app_identity`: ID, tên ứng dụng và danh mục.
2. `live_store_metadata`: Short Description hiện tại của bạn.
3. `suggested_competitors`: Danh sách từ 3-5 đối thủ cạnh tranh chính. Đối với mỗi đối thủ, điền `package_id`, `title`, `short_description` và một đoạn mô tả ngắn (`desc200`). Script sẽ quét thông tin này để tự động cộng điểm ưu tiên (`Competitor Boost`) cho các từ khóa mà đối thủ của bạn đang sử dụng hiệu quả.

Project Memory sẽ đọc trực tiếp `app_config.py` và `App_Profile.json` để hiển thị lại setup hiện tại trong Dashboard tab `Setup`, sheet `00_Project_Memory` và file `PROJECT_MEMORY.md`. Không cần nhập thêm dữ liệu riêng cho phần này.

### Bước 3: Đặt tên file dữ liệu đầu vào chuẩn
Lấy file CSV từ khoá thô từ Apptweak hoặc SensorTower về và lưu tên theo chuẩn:
`[AppName]_[Country]_[Language].csv` (Ví dụ: `MyNewApp_US_EN.csv`).

---

## 🚀 Cách chạy Lọc từ khóa

Nếu đang cấu hình app mới từ `App_Template`, mở terminal/powershell tại thư mục `ASO-MVP-Max/apps/App_Template` và chạy trực tiếp pipeline template:

```powershell
# Chạy ở chế độ tự động xuất Excel trực tiếp
python run_pipeline.py --csv C:\duong-dan-den\MyNewApp_US_EN.csv --market US_EN

# Chạy ở chế độ mở giao diện Web tương tác (để tự tay lựa chọn & viết mô tả)
python run_pipeline.py --csv C:\duong-dan-den\MyNewApp_US_EN.csv --market US_EN --interactive
```

Nếu chạy từ thư mục gốc `ASO-MVP-Max`, dùng đường dẫn script đầy đủ:

```powershell
python apps\App_Template\run_pipeline.py --csv C:\duong-dan-den\MyNewApp_US_EN.csv --market US_EN
```

Kết quả sẽ tự động được xuất ra cùng thư mục với file CSV đầu vào, trừ khi truyền thêm `--output`. File Excel chứa đầy đủ báo cáo, shortlist Top 30, danh sách Consider, sheet `00_Project_Memory` và lý do cụ thể loại/giữ từng từ khóa. Pipeline cũng cập nhật `PROJECT_MEMORY.md` trong thư mục app để bàn giao hoặc audit setup.

---

## 📊 Các bước tiếp theo sau khi lọc

Sau khi chạy pipeline lọc từ khóa thành công, mở terminal tại thư mục gốc `ASO-MVP-Max` nếu muốn sử dụng thêm 2 công cụ bổ trợ:

### Xuất danh sách Master Keywords
Gộp tất cả keyword đã thu thập (từ mọi tháng) thành 1 danh sách sạch sau khi loại bỏ keyword không liên quan (`irrelevant_intent`, `noise_only`). Danh sách này dùng để nhập batch vào AppTweak mỗi tháng:
```powershell
# Xuất cho 1 app cụ thể
python export_master_keywords.py --app <TênApp>

# Xuất cho tất cả app
python export_master_keywords.py --all
```
Kết quả nằm trong thư mục `data/master_keywords/` dưới dạng Excel (mỗi sheet = 1 locale).

### Mở Keyword Tracker Dashboard
Theo dõi và so sánh hiệu suất keyword qua các tháng bằng giao diện web trực quan:
```powershell
python tracker/run_dashboard.py
```
Dashboard sẽ tự động mở trình duyệt tại `http://127.0.0.1:5000` với các biểu đồ ASO Power Score, bảng so sánh keyword chi tiết, danh sách biến động thứ hạng và tab `Setup` để xem Project Memory của app đang chọn.

---

## Shared platform logic v4.1

Template pipeline hien su dung cac module chung trong `ASO-MVP-Max/shared/`:

- `shared/language_detector.py`: detect ngon ngu theo market policy va phan nhom `PRIMARY`, `SECONDARY`, `MIXED`, `FOREIGN`, `UNKNOWN`.
- `shared/keyword_filter/`: package matcher precompiled, hard filter, classifier, validator, audit, cache va version.
- `shared/text_dedup.py`: dedup Unicode indexed `NFKC` + `casefold()`, stemming theo locale, va ghi `MergedVariants` cho main shortlist.
- `shared/translation_service.py`: dich EN voi SQLite WAL cache, retry, global rate limit va TLS verification.
- `shared/profile_service.py`: doc custom profile uu tien tuyet doi, generated cache atomic va stale fallback.
- `shared/project_memory.py`: tao setup overview cho Tracker tab `Setup`, sheet `00_Project_Memory` va `PROJECT_MEMORY.md`.
- `shared/locale_parser.py`: parse locale dung chung cho orchestrator, exporter, tracker va batch runner.

Quy tac quan trong:

- `FOREIGN` vao `Language Mismatch Audit`.
- `UNKNOWN` vao `Manual Review`.
- `MIXED` vao `Consider Keywords` neu market cho phep `mixed_allowed=True`.
- `SECONDARY` giu o `Consider Keywords`.
- Naturalness khong con drop non-Latin/script khac bang `LANGUAGE_BLEED`; ngon ngu do language detector xu ly.
- Selection cache chi duoc dung lai khi metadata `app_id`, market, input hash, config hash va engine version khop run hien tai.
- Low-volume keyword co the vao shortlist/Consider khi config v4.1 dat `exclude_low_tier_from_metadata_shortlist=False` va `max_low_tier_consider_keywords=999`.
- Truncation v4.1 bao ve complete token va singular/plural: `battery emoji`, `battery icon`, `prank sound`, `ar filter`, `control widget` khong bi hard-drop; prefix nghi ngo se vao `possible_truncated_keyword`/Manual Review.
- Hoan vi thu tu tu duoc giu nhu keyword doc lap khi `auto_merge_token_bag=False`.
- Dedup chi ap dung cho `01_Main_Keyword_Shortlist`. Cac sheet tinh nang/style chi sort theo uu tien thong thuong.
- Accent-fold va keyword chi gan giong duoc giu nhu keyword doc lap; khong con `ReviewVariants`.

Chay batch nhieu locale:

```powershell
python ..\..\run_aso_batch.py --manifest path\to\manifest.json --max-workers 3
```
