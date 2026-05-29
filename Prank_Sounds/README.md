# 🛠️ Prank Sounds ASO Pipeline — Hướng Dẫn Chạy & Cấu Hình

Thư mục này chứa pipeline thực tế cho nhóm app Prank Sounds. Có thể chạy trực tiếp bằng `run_pipeline.py` hoặc chạy qua orchestrator `ASO-DEMO/run_aso_filter.py` với file CSV có tên chứa `Prank`/`Pranky`.

Hệ thống được thiết kế theo hướng **tách biệt cấu hình và mã nguồn**: toàn bộ thông số cấu hình nằm trong file `app_config.py` và hồ sơ ứng dụng nằm trong file `App_Profile.json`.

---

## 📁 Cấu trúc thư mục

```text
Prank_Sounds/
├── README.md                      (Tài liệu hướng dẫn này)
├── app_config.py                  (Nơi điền từ khóa, thương hiệu đối thủ, trọng số điểm)
├── App_Profile.json               (Nơi điền mô tả hiện tại và đối thủ của app)
├── run_pipeline.py                (Mã nguồn chạy 10 bước lọc - KHÔNG cần chỉnh sửa)
├── interactive_optimizer.html     (Giao diện Web tối ưu hóa từ khóa)
└── interactive_description_editor.html (Giao diện Web soạn thảo mô tả ASO)
```

---

## ⚙️ Cấu hình Prank Sounds

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

### Bước 3: Đặt tên file dữ liệu đầu vào chuẩn
Lấy file CSV từ khoá thô từ Apptweak hoặc SensorTower về và lưu tên theo chuẩn:
`[AppName]_[Country]_[Language].csv` (Ví dụ: `PrankSounds_US_EN.csv`, `Pranky_PH_FIL.csv`).

---

## 🚀 Cách chạy Lọc từ khóa

Mở terminal/powershell tại thư mục `ASO-DEMO/Prank_Sounds` và chạy trực tiếp pipeline:

```powershell
# Chạy ở chế độ tự động xuất Excel trực tiếp
python run_pipeline.py --csv C:\duong-dan-den\PrankSounds_US_EN.csv --market US_EN

# Chạy ở chế độ mở giao diện Web tương tác (để tự tay lựa chọn & viết mô tả)
python run_pipeline.py --csv C:\duong-dan-den\PrankSounds_US_EN.csv --market US_EN --interactive
```

Hoặc chạy từ thư mục gốc `ASO-DEMO` qua orchestrator để tự archive input vào `Prank_Sounds/Input/[MMYYYY]/` và xuất output vào `Prank_Sounds/Output/[MMYYYY]/`:

```powershell
python run_aso_filter.py --csv C:\duong-dan-den\PrankSounds_US_EN.csv
python run_aso_filter.py --csv C:\duong-dan-den\Pranky_PH_FIL.csv --interactive
```

Kết quả sẽ được xuất thành một file Excel duy nhất chứa đầy đủ báo cáo, shortlist Top 30, danh sách Consider và lý do cụ thể loại/giữ từng từ khóa.

---

## Shared filter logic từ v3.5

Pipeline hiện sử dụng các module chung trong `ASO-DEMO/shared/`:

- `shared/language_detector.py`: detect ngôn ngữ theo market policy và phân nhóm `PRIMARY`, `SECONDARY`, `MIXED`, `FOREIGN`, `UNKNOWN`.
- `shared/keyword_filter.py`: lọc noise-only, irrelevant, naturalness, expansion score, bucket classification và selection cache metadata.

Quy tắc cần nhớ:

- `FOREIGN` vào `Language Mismatch Audit`.
- `UNKNOWN` vào `Manual Review`.
- `MIXED` vào `Consider Keywords` nếu market cho phép `mixed_allowed=True`.
- `SECONDARY` giữ ở `Consider Keywords`.
- Naturalness không hard-drop non-Latin/script khác bằng `LANGUAGE_BLEED`; ngôn ngữ do language detector xử lý.
- `selected_keywords.json` chỉ được dùng lại khi metadata market và input file khớp run hiện tại.
