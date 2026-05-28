# 📖 Hướng Dẫn Giải Nghĩa Các File Trong Hệ Thống ASO Keyword Filter

Hệ thống ASO Keyword Filter được tổ chức thành các thư mục tài liệu, cấu hình mẫu, và mã nguồn thực thi. Dưới đây là giải thích chi tiết về tác dụng và chức năng của từng file/thư mục.

---

## 📂 Thư Mục Gốc (Root Directory)

### 1. [run_aso_filter.py](file:///c:/Users/VOLIO/Documents/ASO-DEMO/run_aso_filter.py)
* **Tác dụng:** **Bộ điều phối trung tâm (Orchestrator)**. 
* **Cách hoạt động:** Khi bạn chạy file này từ dòng lệnh với file CSV đầu vào, nó sẽ:
  1. Tự động nhận dạng tên ứng dụng (`ARFilter`, `ControlWidget` hoặc `GameEmulator`) và thị trường (`Market` như `US_EN`) từ tên file CSV.
  2. Di chuyển/sao chép file CSV đầu vào vào đúng thư mục lưu trữ (`Input/[Tháng]/`).
  3. Kích hoạt đúng script xử lý tương ứng của ứng dụng đó với các cờ cấu hình phù hợp.
  4. Xuất kết quả ra đúng thư mục (`Output/[Tháng]/`).

### 2. [SKILL_ASO_Keyword_Filter_Trigger.md](file:///c:/Users/VOLIO/Documents/ASO-DEMO/SKILL_ASO_Keyword_Filter_Trigger.md)
* **Tác dụng:** **Tài liệu hướng dẫn kích hoạt nhanh cho AI Agent**.
* **Nội dung:** Định nghĩa các điều kiện kích hoạt (Trigger Conditions), cấu trúc đặt tên file CSV chuẩn hóa và các bước thực hiện tuần tự để Agent tự động hóa việc nhận diện, điều phối và phân tích báo cáo lọc từ khóa cho người dùng.

---

## 📂 Thư Mục `Docs_and_Templates/` (Tài liệu & File mẫu)

### 3. [ASO_Keyword_Planner_v3_4.md](file:///c:/Users/VOLIO/Documents/ASO-DEMO/Docs_and_Templates/ASO_Keyword_Planner_v3_4.md)
* **Tác dụng:** **Tài liệu đặc tả quy trình lọc từ khoá phiên bản 3.4 (Mới nhất)**.
* **Nội dung:** Giải thích chi tiết quy trình 10 bước của ASO Keyword Planner: chuẩn hóa dữ liệu đầu vào (mã hóa UTF-8/BOM, ép kiểu và điền fallback), lọc cứng chặn đối thủ/typo/noise, phân tích chính sách ngôn ngữ thị trường (primary vs secondary), lọc độ tự nhiên ngôn ngữ, chấm điểm Relevancy và tính điểm cân bằng Balanced Score, phân nhóm quota cho Top 30 (25 Core Intent + 5 Broad Expansion) và 10 Consider (4 Platform-Style, 3 Secondary, 3 Overlap), cơ chế đa dạng hóa Word Overlap, và xuất duy nhất 01 file Excel tổng gồm các sheet quy chuẩn từ 00 đến 06 (hoặc 11).

### 4. [ASO_Pipeline_Universal_Template_v2.md](file:///c:/Users/VOLIO/Documents/ASO-DEMO/Docs_and_Templates/ASO_Pipeline_Universal_Template_v2.md)
* **Tác dụng:** **Tài liệu đặc tả quy trình lọc phiên bản 2.0**.
* **Nội dung:** Tài liệu tham khảo về quy trình cũ (9 bước), chủ yếu dùng để đối chiếu hoặc sử dụng khi chạy pipeline đơn giản trên các nền tảng chat web như Kimi Web.

### 5. [App_Config_Template.py](file:///c:/Users/VOLIO/Documents/ASO-DEMO/Docs_and_Templates/App_Config_Template.py)
* **Tác dụng:** **File mẫu cấu hình Python (`APP_CONFIG`)**.
* **Cách dùng:** Khi cấu hình cho một ứng dụng mới, lập trình viên sao chép cấu trúc từ file này để điền thông tin định danh, các từ khóa thương hiệu đối thủ cần chặn, từ khóa tính năng (features), phong cách (styles), và các tham số lọc/trọng số điểm cho ứng dụng đó.

### 6. [App_Profile_Template.json](file:///c:/Users/VOLIO/Documents/ASO-DEMO/Docs_and_Templates/App_Profile_Template.json)
* **Tác dụng:** **File mẫu cấu hình thông tin định danh ứng dụng dạng JSON**.
* **Nội dung:** Chứa các thẻ thông tin cơ bản của app như ID, tên, thị trường, phiên bản và các mô tả tóm tắt để phục vụ việc hiển thị hoặc cấu hình tích hợp.

### 7. [english_words_10k.txt](file:///c:/Users/VOLIO/Documents/ASO-DEMO/Docs_and_Templates/english_words_10k.txt)
* **Tác dụng:** **Từ điển 10,000 từ tiếng Anh thông dụng nhất**.
* **Cách dùng:** Dùng làm whitelist để kiểm tra và phân loại nhanh xem một từ khóa có phải là tiếng Anh chuẩn hay không (ở Bước 3 - Language Naturalness), tránh bị nhận diện sai ngôn ngữ bởi các thư viện nhận diện tự động.

---

## 📂 Thư Mục Mẫu Cho Ứng Dụng Mới (`App_Template/`)

Thư mục này là mô hình mẫu hoàn chỉnh giúp cấu hình và triển khai quy trình lọc từ khóa cho bất kỳ ứng dụng mới nào một cách dễ dàng và nhanh chóng:

### 8. [README.md](file:///c:/Users/VOLIO/Documents/ASO-DEMO/App_Template/README.md)
* **Tác dụng:** **Tài liệu hướng dẫn cấu hình nhanh**. Giải thích cấu trúc thư mục mẫu và các bước thiết lập từ khóa, chạy lệnh chạy pipeline cho ứng dụng mới.

### 9. [app_config.py](file:///c:/Users/VOLIO/Documents/ASO-DEMO/App_Template/app_config.py)
* **Tác dụng:** **File cấu hình từ khóa riêng của app**. Nơi điền các từ khóa cốt lõi (core intent), tính năng (features), phong cách (styles), thương hiệu đối thủ (competitor brands), và từ nhiễu (noise) của ứng dụng mới.

### 10. [App_Profile.json](file:///c:/Users/VOLIO/Documents/ASO-DEMO/App_Template/App_Profile.json)
* **Tác dụng:** **Hồ sơ định vị và đối thủ cạnh tranh của app**. Cung cấp thông tin mô tả cửa hàng và danh sách 3-5 đối thủ cạnh tranh chính để script phân tích, tự động tối ưu hóa từ khóa.

### 11. [run_pipeline.py](file:///c:/Users/VOLIO/Documents/ASO-DEMO/App_Template/run_pipeline.py)
* **Tác dụng:** **Script thực thi pipeline lọc từ khóa tự động**. Được liên kết động để đọc thông tin từ `app_config.py` và `App_Profile.json` trong cùng thư mục để thực hiện quy trình lọc 10 bước mà bạn không cần phải sửa bất kỳ dòng code xử lý nào.

### 12. `interactive_optimizer.html` & `interactive_description_editor.html`
* **Tác dụng:** Giao diện Web tương tác và bảng viết mô tả được tích hợp sẵn dành cho ứng dụng mới của bạn.

---


## 📂 Các Thư Mục Ứng Dụng (`AR_Filter/`, `Control_Widget/`, `Game_Emulator/`)

Mỗi thư mục ứng dụng đại diện cho một app cụ thể và chứa các file mã nguồn, giao diện điều chỉnh tương ứng:

### 13. `run_[tên_app]_v3_4.py` (Ví dụ: `run_ar_filter_v3_4.py`)
* **Tác dụng:** **Script xử lý nghiệp vụ chính**.
* **Nội dung:** Chứa toàn bộ mã nguồn cài đặt 10 bước của quy trình ASO Keyword Planner v3.4. Script này sẽ thực hiện đọc CSV đầu vào, chuẩn hóa, tính điểm, lọc trùng lặp và ghi dữ liệu ra file Excel đầu ra có định dạng nhiều sheet chuyên nghiệp.

### 14. `App_Profile.json`
* **Tác dụng:** **Hồ sơ cấu hình thực tế của ứng dụng**.
* **Nội dung:** Chứa cấu hình cụ thể về từ khóa và thông tin đã được thiết lập sẵn cho ứng dụng đó (được script xử lý đọc trực tiếp khi chạy).

### 15. `interactive_optimizer.html`
* **Tác dụng:** **Giao diện Web tương tác tối ưu hóa từ khóa**.
* **Cách hoạt động:** Khi chạy script python ở chế độ interactive (`--interactive` hoặc `-i`), giao diện này sẽ được mở lên trên trình duyệt, cho phép người dùng xem trực quan danh sách từ khóa, chỉnh sửa thủ công, kiểm tra độ trùng lặp và xem trước (preview) phân bổ từ khóa vào metadata.

### 16. `interactive_description_editor.html`
* **Tác dụng:** **Giao diện Web tương tác soạn thảo mô tả (Description Editor)**.
* **Cách hoạt động:** Cung cấp trình soạn thảo trực quan giúp người viết nội dung ASO chèn các từ khóa đã lọc vào mô tả ứng dụng (Title, Subtitle, Short & Full Description) và tự động đếm ký tự, kiểm tra mật độ từ khóa (keyword density) trực tiếp.

### 17. Thư mục `Input/` và `Output/`
* **Input/**: Nơi lưu trữ tự động các file CSV thô đầu vào do người dùng cung cấp (sắp xếp theo thư mục tháng dạng `MMYYYY`).
* **Output/**: Nơi xuất ra file Excel kết quả tổng hợp sau khi lọc (`ASO_Keyword_Planner_[AppName]_[Market].xlsx`) sắp xếp theo thư mục tháng.

### 18. [DESIGN.md](file:///c:/Users/VOLIO/Documents/ASO-DEMO/Docs_and_Templates/DESIGN.md)
* **Tác dụng**: **Tài liệu hệ thống thiết kế (Design System Spec)**.
* **Nội dung**: Định nghĩa các token thiết kế chuẩn như bảng màu (primary, gradients, glassmorphism), kiểu chữ (display, body, mono), bo góc, khoảng cách và các thành phần giao diện mẫu để duy trì tính nhất quán thẩm mỹ cao cấp cho toàn bộ slide ảnh, slide PowerPoint và giao diện tương tác.

