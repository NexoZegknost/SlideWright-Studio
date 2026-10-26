# Nhánh B — Nâng cấp, thiết kế lại bài trình chiếu có sẵn

Dùng khi người dùng gửi file .pptx, link Gamma hoặc thiết kế Canva và muốn "làm đẹp", "thiết kế lại", "ấn tượng hơn" mà **giữ nguyên nội dung**.

1. **Xác định nguồn**: .pptx đính kèm, link Gamma, hay link/thiết kế Canva. Không có nguồn → hỏi người dùng gửi file hoặc link.
2. **Kiểm tra có phải bản do chính Claude làm trước đó trong cuộc trò chuyện không** (`cmp` với file đã xuất). Nếu trùng, dựng lại từ script cũ thay vì phân tích lại; nếu người dùng đã sửa tay, lấy nội dung đã sửa làm chuẩn.
3. **Đọc toàn bộ nguồn**: .pptx → `markitdown` + ảnh lưới thu nhỏ (render soffice → pdftoppm); Gamma → `read_gamma`; Canva → `read-design`.
4. **Chẩn đoán ngắn** 3–5 gạch: chữ quá nhiều, bố cục lặp, màu thiếu nhất quán, ảnh mờ, lỗi chính tả, xuống dòng xấu…
5. **Chọn phong cách mới** theo Bước 1 của SKILL.md (3 phương án + ảnh xem trước bằng chính nội dung). Hỏi gộp một lượt: phong cách; có giữ yếu tố nhận diện cũ (ảnh bìa hội nghị, màu đơn vị) hay theo hẳn phong cách mới; được rút gọn chữ không.
6. **Dựng lại** theo Bước 3–7 của SKILL.md, **giữ nguyên nội dung, số liệu, thứ tự** (được thêm slide chuyển phần, tách slide quá dày). Nâng cấp thường đáng làm:
   - slide chuyển phần nền đậm, số La Mã/số thứ tự lớn; Morph số đó thành huy hiệu nhỏ ở slide nội dung đầu tiên của phần (`objectName` `!!sec` ở cả hai slide);
   - mỗi slide một kiểu bố cục khác nhau (số lớn + thanh tỉ lệ, biểu đồ + trục mốc, cột so sánh, lộ trình nhiều chặng…);
   - một họa tiết xuyên suốt (ví dụ `scripts/hoa_tiet_trong_dong.py` cho phong cách Truyền thống);
   - hiệu ứng chờ cho 1–3 con số chủ chốt của cả bài.
7. **Không ghi đè file gốc** — tên file mới có hậu tố `_nang_cap`. Bàn giao .pptx + .ppsx kèm 1 câu nêu thay đổi chính.
