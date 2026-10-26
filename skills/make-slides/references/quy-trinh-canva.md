# Quy trình tạo bài thuyết trình trên Canva

Cần kết nối **Canva**. Tìm công cụ qua ToolSearch ("canva"); không có thì báo người dùng kết nối Canva và đề nghị làm bản .pptx thay thế. Đọc mô tả công cụ thực tế vì tên/tham số có thể đổi; gọi `help` của Canva khi cần.

## Phạm vi (quy trình rút gọn)
Áp dụng Bước 1–5, 7–9 của SKILL.md như PowerPoint. Ở Bước 6 và 10 **bỏ**: animation/transition chi tiết, nhúng phông, .ppsx — Canva tự xử lý. Vẫn giữ nguyên tắc phông (bài chính quy dùng serif/sans-serif). Cần hiệu ứng chi tiết hoặc .ppsx → đề nghị bản PowerPoint.

## Chọn công cụ tạo
- **Có `create-design`** → dùng nó (các công cụ `generate-design`, `generate-design-structured`, `request-outline-review` ghi rõ là LEGACY, không gọi khi đã có `create-design`).
  - `format: "Presentation"`, `brief`: chủ đề, mục đích, người nghe, phong cách, **mã màu hex**, phông có chân/không chân, "giữ đúng, đủ dấu tiếng Việt", "mỗi slide chỉ ý chính", "không ảnh người nước ngoài, không logo thương hiệu".
  - `outline.sections`: mỗi slide một `title` + `points` (ý chính ngắn). Viết đủ dấu, giữ nguyên số hiệu văn bản.
  - Nhiều bộ slide độc lập → gọi song song.
- **Người dùng muốn dùng brand kit** (logo, màu đơn vị) → `list-brand-kits`, rồi dùng công cụ legacy (create-design không áp được brand kit).

## Chờ kết quả
`create-design` trả `job_id` + `continuation_token`. Nếu không có widget tự theo dõi: gọi `get-create-design-async-job`, chờ đúng `polling_policy.wait_seconds` giữa các lần (thường 60–120 giây tổng). Trong sandbox, lệnh `sleep` đứng riêng bị chặn → chạy `sleep 45` với `run_in_background: true` rồi hỏi lại khi được báo xong.

## Kiểm tra chữ (bắt buộc — Canva AI hay làm sai tiếng Việt)
1. `read-design` với `fields: ["design_content"]` đọc toàn bộ chữ; dò từng dòng so với dàn ý.
2. Lỗi đã gặp thực tế: mất chữ **Đ → D** trong ký hiệu (BGDDT, GĐĐT); sai dấu (kíểm, đển, cà, tính→tỉnh, Móc→Mốc, Sý→Sỹ); **chữ vô nghĩa trên hình minh họa nhỏ** (Rẻ soát, Học lộc số, Ngôn lòng của tôi); ngắt dòng làm dính chữ.
3. Sửa: `read-design` với `open_transaction: true` + `page_indices` cần sửa để lấy `locator_id` → `edit-design` (`keep_open`) dùng `find_and_replace_text` (sửa một cụm) hoặc `replace_text` (thay cả hộp chữ). Mỗi lần sửa xem ảnh `thumbnail` trả về: kiểm tra xuống dòng mồ côi, tràn khung.
4. **Lưu (commit) cần người dùng đồng ý**: tóm tắt các chỗ đã sửa, hỏi một câu (AskUserQuestion) rồi mới `edit-design` với `finalize: "commit"`. Mọi transaction mở phải commit hoặc cancel.

## Xuất file
`get-export-formats` (nếu cần) → `export-design` với `type: "pptx"` hoặc `"pdf"`. Link tải **hết hạn sau vài giờ**; sandbox thường **không tải được** (export-download.canva.com bị chặn) → đưa link cho người dùng, kèm hướng dẫn tải lại trong Canva (Chia sẻ → Tải xuống → PowerPoint).

## Bàn giao
Link chỉnh sửa Canva (`edit_url` trong `design_metadata.urls`) + link tải (ghi rõ thời hạn), 1 câu tóm tắt, danh sách lỗi đã sửa, nhắc xem lướt lại các slide chưa kiểm bằng ảnh.
