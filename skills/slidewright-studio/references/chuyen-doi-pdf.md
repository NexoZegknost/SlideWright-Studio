# Nhánh C — Chuyển PDF thành PowerPoint giữ nguyên bản gốc

Dùng khi người dùng gửi **PDF của một bài trình chiếu** (thường xuất từ PowerPoint/Canva/Gamma) và muốn có lại file PowerPoint **giữ nguyên hình nền, phông, cỡ chữ, màu chữ, cách trình bày, hình ảnh**, có thể kèm hiệu ứng xuất hiện. Không thiết kế lại, không rút gọn chữ, không đổi phong cách.

## 1. Kiểm tra PDF trước
```bash
pip install --break-system-packages -q pymupdf python-pptx
python3 -c "
import pymupdf as f; d=f.open('src.pdf'); print(len(d), d[0].rect)
for i,p in enumerate(d): print(i+1, 'ảnh', len(p.get_images()), 'nét vẽ', len(p.get_drawings()), 'chữ', len(p.get_text().strip()))
print({x[3] for p in d for x in p.get_fonts()})"
```
- **Có lớp chữ** (cột "chữ" > 0): dùng script bên dưới.
- **PDF quét / chữ đã thành ảnh** (chữ = 0): không dựng được chữ sửa được bằng script. Báo người dùng một câu và đề nghị: (a) mỗi trang thành một ảnh slide kèm hiệu ứng theo vùng, hoặc (b) nhận dạng chữ (OCR) rồi dựng lại; hỏi chọn.
- Kích thước trang 960×540 pt = 16:9; script tự đặt khổ slide đúng theo PDF.

## 2. Chạy script
```bash
python3 <skill>/scripts/pdf_sang_pptx.py src.pdf "Ten_file.pptx"        # có hiệu ứng
python3 <skill>/scripts/pdf_sang_pptx.py src.pdf out.pptx --no-anim      # không hiệu ứng
```
Script làm gì: nền = trang PDF đã xoá chữ và ảnh rời (giữ khung, bảng, cột biểu đồ vẽ bằng nét) · chữ = hộp văn bản đúng vị trí/phông/cỡ/màu/khoảng dòng · ảnh rời đặt lại đúng chỗ, giữ nền trong suốt (SMask, kể cả `/Matte` — nếu không xử lý sẽ ra **nền đen**) · hiệu ứng Fade theo thứ tự đọc: tiêu đề, phụ đề, số trang hiện sẵn; bìa và trang ít nội dung tự chạy; trang nội dung mỗi cú nhấp một khối (đề mục đi cùng lời giải thích, mỗi hàng bảng một cú nhấp) · chuyển trang Fade.

## 3. Phông chữ
- Script in ra danh sách họ phông dùng trong PDF. Phông nhúng trong PDF thường là **bản cắt gọn (subset)** — chỉ dùng để xem trước, không nhúng lại vào .pptx.
- Phông có sẵn trên Windows/Office (Verdana, Arial, Times New Roman, Calibri, Cambria…): giữ nguyên tên, không cần nhúng.
- Phông không có sẵn (Montserrat, Lexend…): nếu có trong `assets/fonts` thì nhúng bằng `MS.embedFonts` của `scripts/makeslides.js`; không có thì báo người dùng cài phông hoặc chấp nhận phông thay thế.
- Để xem trước đúng phông: trích phông từ PDF (`doc.extract_font(xref)`) vào `~/.fonts`, chạy `fc-cache -f`.

## 4. Kiểm tra bắt buộc
1. `validate.py` của skill pptx → PASSED.
2. Render .pptx → PDF bằng `soffice.py` rồi **so từng trang với PDF gốc**: tính tỉ lệ điểm ảnh khác biệt (PIL `ImageChops.difference`, ngưỡng 40) và ghép ảnh trên/dưới cho các trang lệch nhiều nhất để xem tận mắt. Lỗi hay gặp: ảnh nền đen (SMask), chữ lệch dòng khi khoảng dòng lạ, ký tự thiếu dấu do phông thay thế.
3. Đếm số cú nhấp mỗi slide và kiểm tra mọi `spid` trong `<p:timing>` đều tồn tại.

## 5. Bàn giao
Một file .pptx (thêm .ppsx bằng `MS.toPpsx` nếu người dùng muốn trình chiếu ngay). Nói rõ: khung bảng/cột biểu đồ nằm trong ảnh nền nên không chỉnh kích thước được, chữ vẫn sửa được; đề nghị dựng lại bảng thật nếu cần.
