# 🎯 SKILL: ASO Keyword Filter Trigger & Automation

**SKILL_ID:** `aso_keyword_filter_trigger`  
**VERSION:** 4.1  
**AUTHOR:** AI Assistant  
**SCOPE:** Tự động hóa việc nhận diện lệnh kích hoạt, định tuyến và chạy pipeline lọc từ khóa ASO dựa trên cấu trúc tên file CSV được gửi trong thư mục `d:\Antigravity\ASO-Project\ASO-MVP-Max`.
**RUNTIME:** Python 3.9+  

---

## 📥 TRIGGER CONDITIONS (Điều kiện kích hoạt)

Skill này được kích hoạt khi USER gửi yêu cầu trong chat chứa cụm từ khoá kích hoạt:
* **Cụm từ kích hoạt:** `Lọc từ khoá` hoặc `Lọc từ khóa` hoặc `Filter keywords`.
* **Tệp đính kèm:** Một tệp CSV chứa dữ liệu từ khoá thô, có cấu trúc đặt tên theo chuẩn:
  ```
  {AppName}_{Country}_{Language}.csv
  ```
  *Ví dụ:* `ARFilter_US_EN.csv`, `ControlWidget_BR_PT.csv`, `GameEmulator_US_EN.csv`, `PrankSounds_PH_FIL.csv`.

---

## 🔄 WORKFLOW STEPS FOR AGENT (Các bước Agent thực hiện)

Khi điều kiện kích hoạt được đáp ứng, Agent PHẢI thực hiện tuần tự các bước sau:

### Bước 1: Xác thực và Chuẩn bị tệp đầu vào
1. Nhận diện file CSV được gửi.
2. Kiểm tra cấu trúc tên file để trích xuất `AppName` và mã thị trường `Country_Language` (ví dụ: `ARFilter` và `US_EN`).
   * Nếu filename chỉ có locale như `US_EN.csv`, Agent phải truyền `--app <RegisteredAlias>`.
   * Alias app phải tồn tại trong `shared/app_registry.py`; app chưa đăng ký phải fail rõ ràng.
3. Xác định tháng chạy dạng `MMYYYY` (ví dụ `052026`).
4. Script điều phối sẽ tự động copy file CSV này vào thư mục lưu trữ chuẩn: `apps/[AppFolder]/Input/[Tháng]/` (ví dụ: `apps/AR_Filter/Input/052026/ARFilter_US_EN.csv`). File gốc không bị xóa.

### Bước 2: Kích hoạt Pipeline điều phối
Chạy bộ điều phối trung tâm [run_aso_filter.py](file:///d:/Antigravity/ASO-Project/ASO-MVP-Max/run_aso_filter.py) bằng Powershell/Terminal. Mặc định chạy chế độ không tương tác (headless):
```powershell
python d:\Antigravity\ASO-Project\ASO-MVP-Max\run_aso_filter.py --csv d:\Antigravity\ASO-Project\ASO-MVP-Max\<Ten_File_CSV>
```
*Lưu ý:* Nếu người dùng muốn mở giao diện Web UI tương tác để chỉnh sửa thủ công, hãy thêm cờ `--interactive` (hoặc `-i`):
```powershell
python d:\Antigravity\ASO-Project\ASO-MVP-Max\run_aso_filter.py --csv d:\Antigravity\ASO-Project\ASO-MVP-Max\<Ten_File_CSV> --interactive
```

### Bước 3: Phân tích & Trình bày kết quả cho USER
Sau khi script hoàn thành thành công:
1. Đọc tóm tắt kết quả từ log đầu ra.
2. Hiển thị báo cáo kết quả tóm tắt cho người dùng dưới dạng bảng Markdown:
   * Tổng số từ khóa thô (Total Raw).
   * Số lượng từ khóa sạch (After Clean).
   * Số lượng từ khóa tính năng (Features) và phong cách (Styles).
3. Gửi đường dẫn trực tiếp đến file Excel kết quả ở thư mục con tương ứng để người dùng có thể nhấp vào và mở ngay lập tức.
   * *Ví dụ link AR Filter:* [ARFilter_US-EN_Output.xlsx](file:///d:/Antigravity/ASO-Project/ASO-MVP-Max/apps/AR_Filter/Output/052026/ARFilter_US-EN_Output.xlsx)
   * *Ví dụ link Control Widget:* [ControlWidget_US-EN_Output.xlsx](file:///d:/Antigravity/ASO-Project/ASO-MVP-Max/apps/Control_Widget/Output/052026/ControlWidget_US-EN_Output.xlsx)
   * *Ví dụ link Game Emulator:* [GameEmulator_US-EN_Output.xlsx](file:///d:/Antigravity/ASO-Project/ASO-MVP-Max/apps/Game_Emulator/Output/052026/GameEmulator_US-EN_Output.xlsx)
   * *Ví dụ link Prank Sounds:* [PrankSounds_PH-FIL_Output.xlsx](file:///d:/Antigravity/ASO-Project/ASO-MVP-Max/apps/Prank_Sounds/Output/052026/PrankSounds_PH-FIL_Output.xlsx)

### Ghi chu logic v4.1
Pipeline hien dung shared logic:
- `shared/language_detector.py` cho `detect_keyword_language` va co che hoan doi `LANG_COUNTRY` sang `COUNTRY_LANG` trong `parse_market`.
- `shared/keyword_filter/` cho matcher precompiled, hard filter raw + EN, classification, validator, audit va selection cache metadata. Keyword volume thap (Volume <= 5) khong bi auto-drop ma nhan diem VolumeN bang 0.
- Truncation logic trong `shared/keyword_filter/` da harden: complete token va singular/plural nhu `emoji`, `icon`, `sound`, `filter`, `widget` khong bi hard-drop; prefix thieu anchor vao `possible_truncated_keyword` va Manual Review.
- `shared/text_dedup.py` cho indexed Unicode `NFKC` + `casefold()`, stemming theo locale, va `MergedVariants` trong main shortlist. Cac hoan vi tu duoc giu lai khi tat option gop token bag (`auto_merge_token_bag = False`).
- `shared/translation_service.py` cho dich EN voi SQLite WAL cache, retry, global rate limit va TLS verification.
- `shared/profile_service.py` cho custom/generated profile, atomic cache va stale fallback.
- `shared/project_memory.py` cho Project Memory read-only tu `app_config.py` + `App_Profile.json`, render ra Dashboard tab `Setup`, sheet `00_Project_Memory` va `PROJECT_MEMORY.md`.
- `shared/app_registry.py` cho routing alias app chinh xac; app chua dang ky phai fail ro rang.

Khi doc ket qua, can hieu bucket ngon ngu nhu sau:
- `FOREIGN` -> `Language Mismatch Audit`.
- `UNKNOWN` -> `Manual Review`.
- `MIXED` -> `Consider Keywords` neu market policy cho phep mixed language, nguoc lai `Manual Review`.
- `SECONDARY` -> `Consider Keywords`.

Vi du `PH_FIL`: `tunog prank` la mixed Filipino/English hop le nen vao `Consider Keywords`; `sonidos de broma` la foreign nen vao `Language Mismatch Audit`.

### Bước 4 (Tùy chọn): Hướng dẫn tiện ích mở rộng
Sau khi pipeline hoàn tất, Agent có thể gợi ý thêm cho USER các tiện ích bổ trợ:
* **Keyword Tracker Dashboard:** Mở dashboard theo dõi và so sánh hiệu suất keyword qua các tháng bằng lệnh:
  ```powershell
  python d:\Antigravity\ASO-Project\ASO-MVP-Max\tracker\run_dashboard.py
  ```
* **Master Keywords Export:** Xuất danh sách master keywords sạch (đã lọc bỏ irrelevant/noise) dùng để nhập vào AppTweak:
  ```powershell
  python d:\Antigravity\ASO-Project\ASO-MVP-Max\export_master_keywords.py --all
  ```

---

## ⚠️ RULES FOR AGENT (Quy tắc bắt buộc)
1. **Không chạy thủ công từng bước:** Luôn sử dụng bộ điều phối trung tâm [run_aso_filter.py](file:///d:/Antigravity/ASO-Project/ASO-MVP-Max/run_aso_filter.py).
2. **Không tìm kiếm ngoài thư mục làm việc:** Tất cả các thao tác và ghi file Excel/JSON phải được thực hiện hoàn toàn bên trong thư mục [ASO-MVP-Max](file:///d:/Antigravity/ASO-Project/ASO-MVP-Max).
3. **Độ tin cậy:** Đảm bảo không tự động mở giao diện Web UI tương tác trừ khi được người dùng yêu cầu rõ ràng hoặc chạy kèm cờ `--interactive`.
