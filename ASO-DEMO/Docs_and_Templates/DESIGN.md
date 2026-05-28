---
version: 1.2.0
name: Google Material Design Light Theme System
description: Hệ thống thiết kế chuẩn Google Light Theme tối ưu hóa giao diện slide và công cụ ASO Keyword Filter.
colors:
  bg-base: "#f8f9fa"        # Màu nền sáng nhẹ Google (Grey 100)
  bg-surface: "#ffffff"     # Màu nền card chính (White)
  text-primary: "#202124"   # Màu chữ chính tối (Google Charcoal)
  text-secondary: "#5f6368" # Màu chữ phụ/mô tả (Google Slate)
  accent-blue: "#1a73e8"    # Xanh dương chính Google Blue
  accent-red: "#ea4335"     # Đỏ Google Red
  accent-yellow: "#fbbc05"  # Vàng Google Yellow
  accent-green: "#34a853"   # Xanh lá Google Green
  bg-accent-soft: "#e8f0fe" # Nền xanh mờ (Blue 50)
  border-color: "#dadce0"   # Đường viền phân cách chuẩn Google
  bg-code: "#f1f3f4"        # Nền khối lệnh (Grey 200)
typography:
  fontFamily:
    display: "'Google Sans', 'Product Sans', 'Plus Jakarta Sans', sans-serif"
    body: "'Roboto', 'Plus Jakarta Sans', sans-serif"
    mono: "'JetBrains Mono', 'Consolas', monospace"
  fontSize:
    display-huge: "80px"
    display-title: "44px"
    display-subtitle: "20px"
    card-title: "24px"
    body-large: "20px"
    body-regular: "16px"
    code-block: "15px"
rounded:
  sm: "4px"
  md: "8px"
  lg: "16px"
  full: "9999px"
spacing:
  slide-padding: "70px"
  gap-grid: "24px"
  card-padding: "32px"
  content-gap: "16px"
components:
  viewport:
    background: "#eef2f3"
  deck-stage:
    width: "1920px"
    height: "1080px"
    aspect-ratio: "16/9"
    background: "{colors.bg-base}"
  card-material:
    background: "{colors.bg-surface}"
    border: "1px solid {colors.border-color}"
    border-radius: "{rounded.lg}"
    box-shadow: "0 1px 3px rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)"
  pre-light:
    background: "{colors.bg-code}"
    border: "1px solid {colors.border-color}"
    border-radius: "{rounded.md}"
    font-family: "{typography.fontFamily.mono}"
    color: "#202124"
---

# Quy Chuẩn Thiết Kế Google Material Design (Light Theme)

## 1. Overview (Tổng quan)
Hệ thống thiết kế mới này chuyển hoàn toàn từ giao diện tối sang **Giao diện sáng Material Design (Google Light Theme)**. Mục tiêu là mang lại cảm giác thân thiện, sạch sẽ, thoáng đãng như các sản phẩm của Google (Drive, Slides, Console). Điều này khắc phục tình trạng khó đọc chữ, lệch layout bằng cách phân bổ thông tin thưa hơn trên nền sáng, tận dụng hệ 4 màu chủ đạo Google để nhận diện tính năng và phân loại từ khóa.

---

## 2. Colors (Bảng màu Google)
- **Nền chính (`bg-base`):** Màu xám nhạt `#f8f9fa` giúp giảm lóa mắt khi xem slide trên nền trắng, tạo sự khác biệt giữa khung slide stage và bên ngoài.
- **Thẻ nội dung (`bg-surface`):** Màu trắng tinh khiết `#ffffff` làm nổi bật nội dung bên trong.
- **Bốn màu nhấn thương hiệu:**
  - **Google Blue (`accent-blue` - `#1a73e8`):** Dùng cho tiêu đề chính, các nút điều hướng cốt lõi và nhóm **Core Intent**.
  - **Google Green (`accent-green` - `#34a853`):** Dùng cho mã nguồn ví dụ, các đề xuất cài đặt chuẩn.
  - **Google Yellow (`accent-yellow` - `#fbbc05`):** Dùng cho các cảnh báo, danh sách **Consider**.
  - **Google Red (`accent-red` - `#ea4335`):** Dùng cho các brand đối thủ cần chặn (competitor brands), lỗi hoặc từ khóa nhiễu.

---

## 3. Typography (Kiểu chữ)
- **Display Font (`Google Sans` / `Plus Jakarta Sans`):** Phông chữ không chân tròn trịa đặc trưng của Google, tạo cảm giác chuyên nghiệp, gọn gàng và dễ tiếp cận.
- **Body Font (`Roboto` / `Plus Jakarta Sans`):** Giữ độ rõ nét tối đa cho các đoạn văn bản dài, gạch đầu dòng, thuyết minh.
- **Monospace Font (`JetBrains Mono` / `Consolas`):** Giữ tỷ lệ cố định cho cấu trúc mã nguồn.

---

## 4. Layout & Division (Phân bổ layout tránh tràn chữ)
Để khắc phục hoàn toàn lỗi tràn chữ và lệch layout, hệ slide được chia nhỏ từ 7 slide lên **10 slide**:
- **Quy trình 10 bước** được chia đôi làm 2 slide (Mỗi slide chứa 5 bước).
- **Cơ cấu đầu ra** được chia thành 2 slide độc lập: 1 slide dành cho Top 30 shortlist chính, 1 slide dành cho 10 Consider.
- **Chuẩn dữ liệu đầu vào** được tách biệt: 1 slide hướng dẫn đặt tên file CSV và 1 slide đặc tả các cột dữ liệu bắt buộc.

---

## 5. Visual Illustrations (Hình ảnh minh họa)
Mỗi slide phải chứa ít nhất một thành phần trực quan:
- Sơ đồ trục thời gian (timeline path/roadmaps) cho các bước quy trình.
- Cấu trúc thư mục dạng cây (file tree) trực quan cho việc đặt tên file CSV.
- Bảng lưới mô phỏng (data grid mockups) cho cấu trúc cột dữ liệu.
- Biểu đồ phân bổ hình bánh (doughnut chart) cho quota từ khóa.
- Khung giả lập trình viết mã (editor layout mockup) cho file config.

---

## 6. Do's and Don'ts (Nên và Không nên)

### Nên làm (Do's)
- **Do:** Sử dụng đúng mã màu của Google để nhấn mạnh nội dung.
- **Do:** Đảm bảo khoảng cách lề tối thiểu 70px và khoảng trống giữa các card ít nhất 24px để tạo độ thoáng.
- **Do:** Dùng phông chữ sáng màu trên nền tối đối với khối code, và chữ tối trên nền sáng đối với nội dung thường.

### Không nên làm (Don'ts)
- **Don't:** Không nhét quá 5 thẻ con trên cùng một lưới hiển thị của slide stage 16:9.
- **Don't:** Không sử dụng các tông màu tối sậm làm nền card trên giao diện Light Theme này.
- **Don't:** Không dùng font có chân (Serif) làm chữ nội dung.
