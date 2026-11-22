# Ví dụ mẫu — make-slides bản Gemini app

Bắt chước **cấu trúc và mức chi tiết** của các ví dụ dưới đây. Nội dung, giá tiền, số đo trong ví dụ chỉ để minh hoạ định dạng: **không chép sang bài thật**, số liệu thật phải lấy từ tài liệu người dùng hoặc nguồn tra cứu.

Đề tài ví dụ: *Tưới cây tự động bằng Arduino*, bối cảnh **tập huấn** (`body_min` 22, `title_min` 34, `max_words` 40, `sec_per_slide` 120), 15 phút → 8 slide.
Lĩnh vực `cong-nghe`, phương án 1: `dark` #012659 · `light` #FFFFFF · `soft` #EBF1F8 · `text` #102441 · `muted` #4F5C6F · `accent` #1596AC · `accent2` #A88DDF · `accentText` #067688 · `accentOnDark` #64F3D7 · phông Bricolage Grotesque (tiêu đề) + Lexend (nội dung).

## 1. Dàn ý (Bước 3)

| # | Bố cục | Tiêu đề (thông điệp) | Ý chính | Điểm nhấn |
|---|---|---|---|---|
| 1 | Bìa | Tưới cây tự động bằng Arduino | Dự án STEM 2 tiết cho THCS | — |
| 2 | Câu hỏi lớn | Kỳ nghỉ dài, ai tưới cây cho lớp? | Gợi mở từ tình huống thật | — |
| 3 | Dòng thời gian | Bốn phần trong 15 phút | Vấn đề → linh kiện → lắp ráp → tổ chức lớp | 4 mốc |
| 4 | Ý chính + điểm nhấn | Đất khô thì bơm tự bật | Đo → so ngưỡng → đóng relay | < 35% |
| 5 | Bảng | Năm linh kiện cho một nhóm | Tên, chức năng, giá | tổng chi phí |
| 6 | Hai cột | Hiệu chuẩn trước, cài ngưỡng sau | Đo đất khô / đất ướt → thay vào `map()` | đo thật |
| 7 | Nhóm ý | Mỗi học sinh giữ một vai | 4 vai, vai trưởng nhóm là chính | trưởng nhóm |
| 8 | Kết | Bắt đầu với một chậu cây của lớp | Nhiệm vụ cho buổi sau | — |

Nền tối: slide 1, 2, 8 (3/8, dưới một nửa). Không lặp một bố cục quá 2 slide liền nhau.

## 2. Slide hoàn chỉnh (Bước 4–5)

### Slide 1 — Bìa
- **Nền:** `dark` #012659. Một hình tròn lớn `accent` #1596AC, độ đục 20%, tràn mép phải, chiếm khoảng 1/3 slide.
- **Tiêu đề:** "Tưới cây tự động bằng Arduino" — Bricolage Grotesque 44pt đậm, #FFFFFF, căn trái, hai dòng: dòng trên ngắn hơn ("Tưới cây tự động" / "bằng Arduino").
- **Phụ đề:** "Dự án STEM 2 tiết cho học sinh THCS" — Lexend 24pt, `accentOnDark` #64F3D7.
- **Dòng thông tin:** "Tập huấn giáo viên STEM · Tháng 11/2026" — Lexend 16pt, #FFFFFF, sát chân slide.
- **Không có:** nhãn chữ in hoa phía trên tiêu đề, biểu tượng, gạch chân.
- **Ghi chú:** `[Mở] Chào thầy cô, giới thiệu bản thân một câu. [Ý] Hôm nay ta làm một hệ thống tưới cây mà học sinh lớp 8 tự lắp được trong hai tiết. [Chuyển] Bắt đầu từ một chuyện rất quen ở trường.`

### Slide 4 — Ý chính + điểm nhấn
- **Nền:** `light` #FFFFFF.
- **Tiêu đề:** "Đất khô thì bơm tự bật" — Bricolage Grotesque 36pt đậm, `text` #102441, căn trái, sát mép trên.
- **Danh sách bên trái (Lexend 24pt, `text`, gạch đầu dòng màu `accent`):**
  - Cảm biến đo độ ẩm đất
  - Arduino so với **ngưỡng cài sẵn** *(in đậm, `accentText` #067688)*
  - Relay đóng mạch, bơm chạy
- **Khối bên phải:** nền `soft` #EBF1F8, con số "< 35%" Bricolage Grotesque 60pt đậm `accentText`, dưới là "độ ẩm thì bật bơm" Lexend 22pt `text`.
- **Đếm chữ:** khoảng 30 chữ cả slide ≤ 40. Ba ý dài 5–6 chữ, không cố làm cho bằng nhau.
- **Ghi chú:** `[Mở] Cả hệ thống chỉ làm ba việc nối nhau. [Ý 1] Cảm biến cắm vào đất, gửi giá trị về chân A0. [Ý 2] Arduino so giá trị đó với ngưỡng ta cài. [Ý 3] Khô hơn ngưỡng thì relay đóng, bơm chạy. [Nhấn] ngưỡng cài sẵn. [Chuyển] Muốn ngưỡng đúng thì phải hiệu chuẩn — đó là slide sau.` Nguồn ngưỡng 35%: ghi tài liệu đã dùng.

### Slide 5 — Bảng
- **Tiêu đề:** "Năm linh kiện cho một nhóm" — 36pt.
- **Bảng 4 cột × 6 hàng** (tiêu đề cột + 5 linh kiện), hàng đầu nền `dark` chữ trắng, các hàng xen `soft`/`light`, chữ Lexend 20pt (≥ `body_min` − 4 = 18).
- **Hàng tổng** in đậm `accentText`; **chân slide** Lexend 12pt `muted`: "Giá tham khảo tại <tên cửa hàng>, tháng 11/2026".
- Bảng quá 7 hàng → tách hai slide.

## 3. Sai → đúng (các lỗi đã gặp)

| Sai | Đúng |
|---|---|
| Nhãn "CẤU TRÚC BUỔI TẬP HUẤN" chữ in hoa nhỏ trên tiêu đề "Lộ trình nội dung" | Bỏ nhãn. Tiêu đề là thông điệp: "Bốn phần trong 15 phút" |
| Hàng 4 thẻ trắng bằng nhau, mỗi thẻ một biểu tượng, chữ trong thẻ 11pt | Dòng thời gian 4 mốc; hoặc khối không bằng nhau (khối đầu rộng hơn, nền `dark`); chữ ≥ 22pt |
| Tiêu đề "Đánh giá hiệu quả giải pháp" | "Tưới tự động giữ đất ẩm đều cả tuần" |
| Thanh màu cam đặt cạnh thanh xanh lam | Chỉ dùng `accent`, `accent2`, `muted` của phương án |
| Khung ảnh trống chỉ còn dòng mô tả ảnh | Không có ảnh hiển thị được thì đổi sang bố cục khác |
| "Tiết kiệm 40–60% nước" không ghi nguồn | Ghi nguồn ở chân slide và ghi chú; không có nguồn thì bỏ con số |
| Bảng ghi "cảm biến điện dung", slide sau ghi "khô ~850, ướt ~350" (dải của cảm biến điện trở) | "Đo giá trị đất khô và đất ướt của chính cảm biến, rồi thay vào `map()`" |
| Ảnh lấy từ trang A nhưng ghi nguồn trang B; slide nguồn đặt tên "Image Sources" | Ghi đúng trang lấy ảnh; slide "Nguồn tham khảo" |
| 12 slide cho 15 phút tập huấn | 900 giây ÷ 120 = 7–8 slide |
| Slide cuối chỉ "Cảm ơn quý Thầy Cô đã tham dự!" | Thông điệp chốt hoặc nhiệm vụ tiếp theo; lời cảm ơn để ở ghi chú hoặc dòng nhỏ |
