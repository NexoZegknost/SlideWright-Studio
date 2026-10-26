# makeSlides (make-slides)

Plugin giúp Claude tạo **bài thuyết trình ấn tượng, đa chủ đề** bằng tiếng Việt (bài giảng, tập huấn, báo cáo hội nghị, lễ kỷ niệm, sự kiện, giới thiệu) từ chủ đề, dàn ý, văn bản dán vào hoặc tài liệu đính kèm (PDF, Word, ảnh, link).

## Quy trình chính (10 bước)
Gọi skill → **0** Chọn nhánh (tạo mới / nâng cấp / chuyển đổi PDF) và công cụ → **1** Xác định chủ đề, phong cách, bối cảnh, công cụ → **2** Nội dung (tải lên / tự tìm / cả hai) → **3** Lập dàn ý → **4** Người dùng duyệt dàn ý ⟲ → **5** Tìm material → **6** Thiết kế: viết nội dung → layout → animation → transition → **7** Tự kiểm tra (chính tả, xuống dòng, độ lớn, độ tập trung…) → **8** Gửi bản xem trước → **9** Người dùng kiểm tra ⟲ (cần sửa thì quay lại bước 6) → **10** Nhúng phông, xuất .pptx + .ppsx → Hoàn thành.

Gamma và Canva dùng quy trình rút gọn (bỏ hiệu ứng chi tiết, nhúng phông, .ppsx).

## Thành phần
Một skill duy nhất `make-slides` gồm ba nhánh, tự chọn theo yêu cầu:
| Nhánh | Dùng khi | Ví dụ câu lệnh |
|---|---|---|
| Tạo mới | Có chủ đề, dàn ý, báo cáo, kế hoạch, dự thảo | "Làm slide từ báo cáo này", "slide-canva cho 2 dự thảo này" |
| Nâng cấp | Có sẵn .pptx / Gamma / Canva, muốn đẹp hơn mà giữ nội dung | "Thiết kế lại file này cho ấn tượng hơn" |
| Chuyển đổi nguyên bản | Có PDF bài trình chiếu, muốn PowerPoint giữ nguyên nền, phông, màu, hình | "Chuyển PDF này sang PowerPoint, giữ nguyên, thêm hiệu ứng" |

Công cụ đầu ra: PowerPoint (mặc định, .pptx + .ppsx), Canva hoặc Gamma — chỉ cần nói "bằng Canva", "trên Gamma", "slide-pptx".

| Kèm theo | Công dụng |
|---|---|
| Kết nối Gamma, Canva | Tạo và xuất bài trình chiếu trên hai nền tảng; tự rà và sửa lỗi chính tả Canva sinh ra |
| Bộ phông | 19 họ phông đủ dấu tiếng Việt, giấy phép SIL OFL |
| `makeslides.js` | Chuyển trang (cả Morph), công thức bằng khối Equation gốc của PowerPoint, nhúng phông, xuất .ppsx; gắn hiệu ứng qua `hieu_ung.js` |
| `hieu_ung.js` | Thư viện hiệu ứng bốn nhóm: mở đầu (13, có chữ nổi theo từ/chữ cái), nhấn mạnh (9, có làm nhạt phần đã nói), chờ (17 hiệu ứng tự phát lặp tới hết slide: nền trôi, đèn quét, hạt sáng bồng bềnh, vòng xoay chậm, chữ nổi, sóng chữ…), kết thúc (8); dựng sẵn nền động, vầng sáng, hạt bụi; XML timing đúng chuẩn PowerPoint |
| `kiem_tra_bo_cuc.py` | Kiểm tra lệch khung trên bản dàn trang thật: đường kẻ chạm chân chữ, chữ tràn/sát mép khối màu, chữ chồng chữ, chữ đè logo, chữ/vật thể ra ngoài slide, lệch lề nhỏ, khoảng trống bất thường |
| `do_chu.js` | Đo chữ bằng phông thật (bề rộng, số dòng, chiều cao, chân chữ) để bố cục tự tính khung vừa nội dung |
| `assets/mau-hieu-ung/` | Bài mẫu "Hiệu ứng ánh đèn sân khấu" dùng đủ bốn nhóm hiệu ứng, kèm script vẽ tranh minh hoạ SVG |
| `layouts.js` | 31 bố cục (9 bố cục mở rộng: công thức, hình có chú thích, lưới Thuỵ Sĩ, trang báo, thang số…), không biểu tượng trước chữ, tự cảnh báo bảng màu |
| Bộ nhận diện thương hiệu | `assets/thuong-hieu/bk-hcmut`: logo, màu, hoạ tiết Trường ĐH Bách khoa – ĐHQG-HCM; chỉ dùng khi người dùng yêu cầu (ví dụ báo cáo ở Bách khoa) |
| `hoa_tiet_tam_giac.py` | Sinh hoạ tiết lưới tam giác (lưới nét, cụm góc, lục giác, dải) PNG + SVG theo bảng màu bất kỳ |
| `dinh_huong.js` + `linh-vuc.json` | Module định hướng: đề tài → lĩnh vực → 3 phương án phong cách (màu theo luật phối màu, phông, texture, bố cục, trình bày, hiệu ứng); trộn thương hiệu khi được yêu cầu |
| `mau.js` | Màu OKLCH, tạo bảng màu tương đồng/đơn sắc, kiểm tra màu đối nhau, tương phản, cùng tông |
| `hoa_tiet.py` | 16 kiểu texture (chấm, mạch, sóng, đồng mức, vòng đồng tâm, khối hình học, chữ thập, lưới phối cảnh, hạt sáng, giấy, kẻ ô, kẻ lề, lục giác, gạch chéo, quầng sáng, tam giác), chồng nhiều lớp |
| `kiem_tra_van_ban.py` | Kiểm tra và tự sửa văn bản: cỡ chữ ≥ 24pt, lượng chữ, giãn dòng, hài hoà cỡ, tràn khung, dòng mồ côi, xuống dòng giữ nghĩa (tách từ ghép bằng pyvi), tiêu đề 2 dòng trên ngắn dưới dài, tiêu đề đếm số sáo rỗng |
| `kiem_tra_slide.py` | Tự kiểm tra trước khi bàn giao: tương phản và cân bằng màu, dấu hiệu slide do AI làm, công thức gõ bằng chữ |
| `pdf_sang_pptx.py` | Chuyển PDF thành PowerPoint giữ nguyên bản gốc, chữ sửa được, ảnh trong suốt, hiệu ứng theo thứ tự đọc |
| `hoa_tiet_trong_dong.py` | Họa tiết vòng đồng tâm kiểu trống đồng cho phong cách Truyền thống |
| Hướng dẫn văn bản hành chính | Khung slide cho báo cáo, kế hoạch, dự thảo; giữ đúng số hiệu văn bản; rà lỗi dự thảo |

## Nguyên tắc thiết kế (0.13.0)
- Chữ nội dung ≥ 24pt, ≤ 30 chữ/slide; xuống dòng không tách từ ghép; tiêu đề 2 dòng thì dòng trên ngắn hơn; không tiêu đề đếm số sáo rỗng.
- Không chữ tím trên nền tối; chữ màu trên nền tối ≥ 7:1.
- Texture nhiều lớp, nhiều biến thể trong một bài, chung bảng màu.
- Không phối hai màu đối nhau (lam–cam, đỏ–lục, vàng–tím); ưu tiên phối tương đồng, đơn sắc, tỉ lệ 60–30–10.
- Phong cách (màu, phông, texture, bố cục) định hướng theo lĩnh vực của đề tài.
- Không biểu tượng/emoji trước đoạn văn, không icon trong vòng tròn, không vòng "VS", không nhãn "Điểm chính".
- Không chữ sáng cùng tông với nền đậm (ví dụ chữ xanh nhạt trên nền xanh đậm).
- Công thức luôn là khối Equation, sửa được trong PowerPoint.
- Không dùng phông Be Vietnam Pro.
- Hiệu ứng đủ bốn nhóm theo mạch nói; hiệu ứng chờ nhỏ, chậm, có khoảng nghỉ — nền ≤ 1 nhóm, điểm nhấn ≤ 2 đối tượng mỗi slide.
- Văn bản và vật thể không lệch khung: khung tính theo chữ đo bằng phông thật, kiểm tra lại trên bản dàn trang.

## Nguyên tắc phông chữ
- Bài **chính quy, nghiêm túc** chỉ dùng phông có chân hoặc không chân: Noto Serif Display, Playfair Display, Lora, Noto Serif, Montserrat, Lexend, Bricolage Grotesque…
- Bài **kiểu cách**, WordArt mới dùng phông trang trí: Great Vibes, Allura, Style Script, Beau Rivage, WindSong, Dancing Script…

## Cài đặt & kết nối
- Gamma và Canva đăng nhập bằng tài khoản của bạn khi dùng lần đầu, không cần khoá API. Gamma tính credit theo gói.
- Morph cần PowerPoint 2019 hoặc Microsoft 365; bản cũ hơn tự chuyển thành hiệu ứng mờ dần.
- Khi sửa và lưu lại trong PowerPoint, giữ tuỳ chọn *Embed fonts in the file* (đã bật sẵn).

## Ví dụ sử dụng
- "Làm slide báo cáo sơ kết học kỳ I môn Ngữ văn" (kèm file số liệu)
- "slide-canva: thiết kế 2 bài trình chiếu cho 2 dự thảo kế hoạch này" (kèm 2 file Word)
- "Rà soát lại file trình chiếu này, thiết kế lại cho ấn tượng hơn" (kèm .pptx)
- "Chuyển file PDF này sang PowerPoint, giữ nguyên hình nền, phông, màu, thêm hiệu ứng xuất hiện"
- "Lễ kỷ niệm Ngày Nhà giáo Việt Nam 20/11" (phong cách kiểu cách)
