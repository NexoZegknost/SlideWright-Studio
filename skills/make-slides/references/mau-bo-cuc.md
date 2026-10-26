# Tìm mẫu bố cục và học từ mẫu người dùng gửi

Thư viện `layouts.js` là điểm xuất phát, không phải giới hạn. Mỗi bài nên có **ít nhất 2 slide dựng riêng** cho nội dung đặc thù (sơ đồ mạch, bản đồ, ảnh tư liệu, công thức), không ép mọi thứ vào bố cục có sẵn.

## 1. Khi nào tìm mẫu
- Nội dung không khớp bố cục nào trong `bo-cuc.md` (ví dụ: so sánh 3 phương án theo 5 tiêu chí, quy trình rẽ nhánh, sơ đồ tổ chức).
- Bài có 2 slide liên tiếp phải dùng cùng một bố cục.
- Người dùng muốn "lạ hơn", "sáng tạo hơn", hoặc nêu một phong cách tham chiếu (tạp chí, áp phích, Thuỵ Sĩ, tối giản Nhật…).

Tìm bằng WebSearch/WebFetch với từ khoá tiếng Anh theo **dạng nội dung**, không theo chủ đề: `"slide layout" annotated diagram`, `editorial presentation layout pull quote`, `swiss grid presentation`, `data slide one number hierarchy`. Đọc nguyên tắc dàn trang (lưới, thứ bậc cỡ chữ, khoảng trắng, điểm nhìn), **không sao chép** mẫu, logo, hình minh hoạ của người khác.

## 2. Nguồn tham khảo
| Nguồn | Học được gì |
|---|---|
| Slidesgo — Presentation Design Trends 2026 (slidesgo.com/slidesgo-school/ai-presentations/presentation-design-trends-2026) | Bố cục bất đối xứng có chiều sâu; chữ hình học cỡ lớn; kể chuyện bằng dữ liệu (một biểu đồ một kết luận, chú thích tại điểm đổi chiều); tiếp cận (chữ ≥ 24pt, tương phản 4.5:1) |
| Swiper Studio — Bold Typography Templates (studio.swiperjs.com/blog/15-bold-typography-templates) | Lưới Thuỵ Sĩ (bất đối xứng, nhiều trắng, một màu nhấn); trang báo (tiêu đề serif đậm, cột, trích dẫn kéo ra); thứ bậc số liệu kiểu áp phích (số chính rất lớn, số phụ nhỏ dần); dấu ngoặc kép khổng lồ làm hình |
| 2Slides — Can AI make slides that don't look AI-generated (2slides.com/blog/can-ai-make-slides-that-dont-look-ai-generated) | Danh sách dấu hiệu "slide AI" (xem `dau-hieu-ai.md`) |
| Made Good Designs — Slide Layout Ideas (madegooddesigns.com/slide-layout-ideas) | Bố cục chữ – ảnh, lưới, số lớn |
| Deckary — Professional Slide Types (deckary.com/blog/pillar-slide-types-guide) | Tiêu đề hành động, slide tư vấn (consulting) |
| StudioMeyer — Bento Grid Layouts (studiomeyer.io/en/blog/bento-grid-layouts) | Lưới bento: một ô chính, các ô phụ khác kích thước |
| Sách: *Slide:ology* (Nancy Duarte), *Presentation Zen* (Garr Reynolds), *Grid Systems* (Josef Müller-Brockmann) | Một ý một slide, khoảng trắng, lưới cột |

## 3. Học từ mẫu người dùng gửi (ảnh, PDF, .pptx)
1. **Đọc mẫu**: .pptx → render lưới ảnh (soffice → pdftoppm) và đọc XML để lấy toạ độ, cỡ chữ, màu; PDF/ảnh → xem từng trang.
2. **Mô tả cấu trúc**, không chép trang trí: lưới (số cột, lề), vị trí điểm nhìn, thứ bậc cỡ chữ (tỉ lệ tiêu đề : nội dung : chú thích), tỉ lệ chữ/ảnh/khoảng trắng, cách nhấn (màu, cỡ, đậm), nhịp sáng – tối.
3. **Viết thành hàm bố cục** cùng chuẩn `layouts.js`: `L.<ten>(pres, S, c, o) → { slide, steps, idle }`, lấy màu và phông từ phong cách `S` (không cứng mã màu của mẫu, trừ khi người dùng muốn giữ nhận diện), đặt `objectName` cho mọi đối tượng, chữ nhấn dùng `accentText`/`accentOnDark`.
4. Lưu hàm vào thư mục làm việc (ví dụ `bo_cuc_rieng.js`, `Object.assign(L, require("./bo_cuc_rieng.js"))`), dựng thử 1 slide, render, chạy `kiem_tra_slide.py`.
5. Báo người dùng: bố cục mới học được gì từ mẫu; đề nghị đưa vào plugin (cập nhật `layouts.js` + bảng ở `bo-cuc.md`) để dùng lâu dài.
6. Không bê nguyên mẫu có bản quyền (template trả phí, nhận diện thương hiệu khác) vào plugin; chỉ đưa cấu trúc đã trừu tượng hoá.
