# 📖 Hướng Dẫn Giải Nghĩa Các File Trong Hệ Thống ASO Keyword Filter

Hệ thống ASO Keyword Filter được tổ chức thành các thư mục tài liệu, cấu hình mẫu, và mã nguồn thực thi. Dưới đây là giải thích chi tiết về tác dụng và chức năng của từng file/thư mục.

---

## 📂 Thư Mục Gốc (Root Directory)

### 1. [run_aso_filter.py](file:///d:/Antigravity/ASO-Project/ASO-DEMO/run_aso_filter.py)
* **Tác dụng:** **Bộ điều phối trung tâm (Orchestrator)**. 
* **Cách hoạt động:** Khi bạn chạy file này từ dòng lệnh với file CSV đầu vào, nó sẽ:
  1. Tự động nhận dạng tên ứng dụng (`ARFilter`, `ControlWidget` hoặc `GameEmulator`) và thị trường (`Market` như `US_EN`) từ tên file CSV.
  2. Di chuyển/sao chép file CSV đầu vào vào đúng thư mục lưu trữ (`Input/[Tháng]/`).
  3. Kích hoạt đúng script xử lý tương ứng của ứng dụng đó với các cờ cấu hình phù hợp.
  4. Xuất kết quả ra đúng thư mục (`Output/[Tháng]/`).

### 2. [SKILL_ASO_Keyword_Filter_Trigger.md](file:///d:/Antigravity/ASO-Project/ASO-DEMO/SKILL_ASO_Keyword_Filter_Trigger.md)
* **Tác dụng:** **Tài liệu hướng dẫn kích hoạt nhanh cho AI Agent**.
* **Nội dung:** Định nghĩa các điều kiện kích hoạt (Trigger Conditions), cấu trúc đặt tên file CSV chuẩn hóa và các bước thực hiện tuần tự để Agent tự động hóa việc nhận diện, điều phối và phân tích báo cáo lọc từ khóa cho người dùng.

### 3. [export_master_keywords.py](file:///d:/Antigravity/ASO-Project/ASO-DEMO/export_master_keywords.py)
* **Tác dụng:** **Script xuất danh sách Master Keywords (Module B - Độc lập)**.
* **Cách hoạt động:** Quét toàn bộ các từ khóa thu thập được trong thư mục `Input/` của app, đối chiếu với danh sách bị loại bỏ trong sheet `04_Dropped_Audit` của thư mục `Output/` để loại bỏ các từ khóa không liên quan (`irrelevant_intent` hoặc `noise_only`). Kết quả xuất ra tệp Excel riêng biệt cho từng app lưu trong thư mục `Master_Keywords/` phân chia theo từng locale làm các sheet riêng lẻ.

---

## 📂 Thư Mục `Docs_and_Templates/` (Tài liệu & File mẫu)

### 4. [ASO_Keyword_Planner_v3_4.md](file:///d:/Antigravity/ASO-Project/ASO-DEMO/Docs_and_Templates/ASO_Keyword_Planner_v3_4.md)
* **Tác dụng:** **Tài liệu đặc tả quy trình lọc từ khoá phiên bản 3.4 (Mới nhất)**.
* **Nội dung:** Giải thích chi tiết quy trình 10 bước của ASO Keyword Planner: chuẩn hóa dữ liệu đầu vào, lọc cứng chặn đối thủ/typo/noise, phân tích chính sách ngôn ngữ thị trường, lọc độ tự nhiên ngôn ngữ, chấm điểm Relevancy và tính điểm cân bằng Balanced Score, phân nhóm quota cho Top 30 và 10 Consider, cơ chế đa dạng hóa Word Overlap, và xuất duy nhất 01 file Excel tổng gồm các sheet quy chuẩn từ 00 đến 12.

### 5. [App_Config_Template.py](file:///d:/Antigravity/ASO-Project/ASO-DEMO/Docs_and_Templates/App_Config_Template.py)
* **Tác dụng:** **File mẫu cấu hình Python (`APP_CONFIG`)**.
* **Cách dùng:** Khi cấu hình cho một ứng dụng mới, sao chép cấu trúc từ file này để điền thông tin định danh, các từ khóa thương hiệu đối thủ cần chặn, từ khóa tính năng (features), phong cách (styles), và các tham số lọc/trọng số điểm cho ứng dụng đó.

### 6. [App_Profile_Template.json](file:///d:/Antigravity/ASO-Project/ASO-DEMO/Docs_and_Templates/App_Profile_Template.json)
* **Tác dụng:** **File mẫu cấu hình thông tin định danh ứng dụng dạng JSON**.
* **Nội dung:** Chứa các thẻ thông tin cơ bản của app như ID, tên, thị trường, phiên bản và các mô tả tóm tắt để phục vụ việc hiển thị hoặc cấu hình tích hợp.

### 7. [english_words_10k.txt](file:///d:/Antigravity/ASO-Project/ASO-DEMO/Docs_and_Templates/english_words_10k.txt)
* **Tác dụng:** **Từ điển 10,000 từ tiếng Anh thông dụng nhất**.
* **Cách dùng:** Dùng làm whitelist để kiểm tra và phân loại nhanh xem một từ khóa có phải là tiếng Anh chuẩn hay không (ở Bước 3 - Language Naturalness).

### 8. [DESIGN.md](file:///d:/Antigravity/ASO-Project/ASO-DEMO/Docs_and_Templates/DESIGN.md)
* **Tác dụng**: **Tài liệu hệ thống thiết kế (Design System Spec)**.
* **Nội dung**: Định nghĩa các token thiết kế chuẩn như bảng màu (primary, gradients, glassmorphism), kiểu chữ, bo góc, khoảng cách để duy trì tính nhất quán thẩm mỹ cao cấp cho toàn bộ slide và giao diện tương tác.

---

## 📂 Thư Mục Mẫu Cho Ứng Dụng Mới (`App_Template/`)

### 9. [README.md](file:///d:/Antigravity/ASO-Project/ASO-DEMO/App_Template/README.md)
* **Tác dụng:** **Tài liệu hướng dẫn cấu hình nhanh**. Giải thích cấu trúc thư mục mẫu và các bước thiết lập từ khóa, chạy lệnh chạy pipeline cho ứng dụng mới.

### 10. [app_config.py](file:///d:/Antigravity/ASO-Project/ASO-DEMO/App_Template/app_config.py)
* **Tác dụng:** **File cấu hình từ khóa riêng của app**. Nơi điền các từ khóa cốt lõi (core intent), tính năng (features), phong cách (styles), thương hiệu đối thủ, và từ nhiễu.

### 11. [App_Profile.json](file:///d:/Antigravity/ASO-Project/ASO-DEMO/App_Template/App_Profile.json)
* **Tác dụng:** **Hồ sơ định vị và đối thủ cạnh tranh của app**. Cung cấp thông tin mô tả cửa hàng và danh sách đối thủ cạnh tranh chính.

### 12. [run_pipeline.py](file:///d:/Antigravity/ASO-Project/ASO-DEMO/App_Template/run_pipeline.py)
* **Tác dụng:** **Script thực thi pipeline lọc từ khóa tự động**. Được liên kết động để đọc thông tin cấu hình và thực hiện quy trình lọc 10 bước.

### 13. `interactive_optimizer.html` & `interactive_description_editor.html`
* **Tác dụng:** Giao diện Web tương tác và bảng viết mô tả được tích hợp sẵn dành cho ứng dụng mới.

---

## 📂 Các Thư Mục Ứng Dụng (`AR_Filter/`, `Control_Widget/`, `Game_Emulator/`)

### 14. `run_[tên_app]_v3_4.py` (Ví dụ: `run_ar_filter_v3_4.py`)
* **Tác dụng:** **Script xử lý nghiệp vụ chính**. Chứa toàn bộ mã nguồn cài đặt 10 bước của quy trình ASO Keyword Planner v3.4.

### 15. `App_Profile.json`
* **Tác dụng:** **Hồ sơ cấu hình thực tế của ứng dụng** (được script xử lý đọc trực tiếp khi chạy).

### 16. `interactive_optimizer.html`
* **Tác dụng:** **Giao diện Web tương tác tối ưu hóa từ khóa**. Cho phép người dùng xem trực quan danh sách từ khóa, chỉnh sửa thủ công, kiểm tra độ trùng lặp và xem trước phân bổ từ khóa vào metadata.

### 17. `interactive_description_editor.html`
* **Tác dụng:** **Giao diện Web tương tác soạn thảo mô tả (Description Editor)**. Cung cấp trình soạn thảo trực quan giúp người viết nội dung ASO chèn các từ khóa và tự động kiểm tra mật độ từ khóa.

### 18. Thư mục `Input/` và `Output/`
* **Input/**: Nơi lưu trữ tự động các file CSV thô đầu vào (sắp xếp theo thư mục tháng dạng `MMYYYY`).
* **Output/**: Nơi xuất ra file Excel kết quả tổng hợp sau khi lọc (sắp xếp theo thư mục tháng).

---

## 📂 Thư Mục Đối Soát Keyword & Master Keywords (Mới)

### 19. Thư mục [Keyword_Tracker/](file:///d:/Antigravity/ASO-Project/ASO-DEMO/Keyword_Tracker)
* **Tác dụng:** **Hệ thống theo dõi và so sánh từ khóa hàng tháng (Module A)**.
* **Các file bên trong:**
  * **[run_dashboard.py](file:///d:/Antigravity/ASO-Project/ASO-DEMO/Keyword_Tracker/run_dashboard.py)**: Khởi động Flask server tại `http://127.0.0.1:5000` và tự động mở trình duyệt. Tích hợp tính năng xuất báo cáo Excel nâng cao đối sánh 2 tháng.
  * **[db_manager.py](file:///d:/Antigravity/ASO-Project/ASO-DEMO/Keyword_Tracker/db_manager.py)**: Quản lý kết nối cơ sở dữ liệu SQLite `keyword_tracker.db`, các bảng `keyword_data` (lưu trữ chỉ số), `import_log` (theo dõi hash file) và truy vấn tính toán ASO Power Score.
  * **[data_scanner.py](file:///d:/Antigravity/ASO-Project/ASO-DEMO/Keyword_Tracker/data_scanner.py)**: Quét tự động thư mục dự án để tìm file CSV mới, tính MD5 hash so khớp và import dữ liệu mới vào DB.
  * **Thư mục static/**: Chứa giao diện SPA (HTML/CSS/JS) sử dụng ECharts để vẽ biểu đồ so sánh xu hướng ASO Power Score, phân bổ Rank Tiers, và Movers biến động thứ hạng.

### 20. Thư mục [Master_Keywords/](file:///d:/Antigravity/ASO-Project/ASO-DEMO/Master_Keywords)
* **Tác dụng:** Thư mục chứa các tệp Excel đầu ra của Module B (danh sách keyword sạch sau lọc dùng để import vào AppTweak, phân sheet theo locale).
