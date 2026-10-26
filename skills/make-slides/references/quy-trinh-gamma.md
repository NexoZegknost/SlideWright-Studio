# Quy trình tạo bài thuyết trình trên Gamma

Cần kết nối **Gamma** (công cụ `generate`, `get_themes`, `get_folders`, `get_generation_status`, `export_gamma`…). Nếu công cụ chưa có: tìm qua ToolSearch ("gamma"); vẫn không có thì báo người dùng kết nối Gamma và đề nghị xuất .pptx thay thế.

## Phạm vi (quy trình rút gọn)
Áp dụng Bước 1–5, 7–9 của SKILL.md như PowerPoint. Ở Bước 6 và 10 **bỏ**: thiết kế animation/transition chi tiết, nhúng phông, xuất .ppsx — Gamma tự xử lý hiệu ứng và phông trên nền tảng của nó. Vẫn giữ nguyên tắc phông: bài chính quy chọn theme/phông serif hoặc sans-serif; phông trang trí chỉ cho bài kiểu cách (xem `phong-chu.md`). Nếu người dùng cần hiệu ứng chi tiết hoặc .ppsx → đề nghị làm bản PowerPoint.

## Các bước
1. **Chuẩn bị nội dung đầu vào** từ dàn ý đã chốt: viết dạng markdown, mỗi slide bắt đầu bằng tiêu đề, ngăn cách các thẻ (card) bằng dòng `---`. Ghi nội dung đầy đủ, tiếng Việt có dấu; số liệu chính xác.
2. **Chọn chủ đề (theme)**: gọi `get_themes` với từ khoá phong cách (vd. "professional", "minimal", "vibrant", "dark"); chọn theme có tông màu khớp bảng màu đã chọn. Chỉ truyền theme khi người dùng có yêu cầu phong cách hoặc đã chốt ở Bước 1 của skill.
3. **Gọi `generate`** với:
   - định dạng: presentation
   - nội dung: markdown ở bước 1
   - số thẻ: bằng số slide trong dàn ý
   - ngôn ngữ: tiếng Việt
   - chỉ dẫn bổ sung: người nghe, giọng điệu, mật độ chữ ("ngắn gọn, nhiều hình ảnh"), phong cách ảnh
   - giữ nội dung gốc (không để Gamma tự viết lại số liệu) khi người dùng đã cung cấp nội dung chi tiết
   - Chỉ thêm tham số tuỳ chọn khi người dùng yêu cầu hoặc ngữ cảnh ngụ ý rõ; Gamma có mặc định tốt.
4. **Chờ kết quả**: gọi `get_generation_status` cho tới khi hoàn tất; lấy link.
5. **Xuất file** nếu người dùng cần: `export_gamma` → PPTX hoặc PDF → `get_export_status` để lấy link tải.
6. **Chỉnh sửa**: nếu có `edit_gamma`, dùng để sửa từng trang bằng chỉ dẫn ngôn ngữ tự nhiên (không thêm được trang mới). Nếu không có, hướng dẫn người dùng sửa trực tiếp trong trình soạn thảo Gamma.

## Lưu ý
- Mỗi lần tạo tiêu tốn credit Gamma; vượt giới hạn gói (số thẻ, credit) thì báo đúng giới hạn nào, không hứa hẹn con số.
- Gamma có thể tự sinh ảnh minh hoạ; với nội dung giáo dục/hành chính, yêu cầu ảnh trang nhã, phù hợp bối cảnh Việt Nam.
- Bàn giao: link Gamma + (nếu có) link tải PPTX/PDF, kèm 1 câu tóm tắt.
