# Xác định bối cảnh trình bày

**Phong cách** (từ đề tài, xem `phong-cach.md`) quyết định *diện mạo*: phông, màu, motif.
**Bối cảnh** quyết định *cách trình bày*: cỡ chữ, mật độ chữ, nhịp slide, mức hiệu ứng, cấu trúc và các slide bắt buộc.
Hai yếu tố độc lập và kết hợp với nhau. Ví dụ đề tài triết học dùng phong cách Học thuật; trình bày khi bảo vệ đề tài thì theo bối cảnh "Bảo vệ đồ án"; trình bày trực tuyến thì theo bối cảnh "Online".

Thông số máy đọc được: `assets/contexts.json`.

## 1. Cách xác định bối cảnh
1. Suy ra từ yêu cầu và tài liệu: tư cách người trình bày (sinh viên, chuyên viên, giáo viên, báo cáo viên), người nghe (giảng viên, lãnh đạo, đại biểu, học sinh), địa điểm (lớp, phòng họp, hội trường, trực tuyến), hình thức (trực tiếp, gửi đọc, chiếu tự động).
2. Không suy ra được → hỏi **một câu** với các lựa chọn là tên 10 bối cảnh dưới đây (gộp chung lượt hỏi của Bước 1). Người dùng vắng mặt → chọn bối cảnh gần nhất với đề tài và ghi rõ.
3. Có hai bối cảnh (ví dụ hội thảo vừa trực tiếp vừa phát trực tuyến) → lấy **thông số chặt hơn** của từng mục (cỡ chữ lớn hơn, ít chữ hơn, hiệu ứng nhẹ hơn).
4. Bối cảnh có thể nâng mức trang trọng của phong cách: có lãnh đạo cấp trên hoặc hội đồng chấm thì nâng một bậc (xem `phong-cach.md` mục 3).

## 2. Mười bối cảnh

### 1. Học sinh, sinh viên thuyết trình trước lớp / hội trường (`hoc-sinh-sinh-vien`)
- Tình huống: báo cáo nhóm, thuyết trình môn học, sinh hoạt chủ đề; máy chiếu phòng học thường mờ và phòng sáng.
- Trình bày: chữ nội dung ≥ 24pt; tối đa 5 dòng hoặc 30 chữ mỗi slide; nhiều hình, sơ đồ; nền sáng tương phản cao, tránh chi tiết mảnh và chữ màu nhạt.
- Nhịp: khoảng 1 phút/slide. Nhóm nhiều người thì ghi tên người trình bày ở góc slide mỗi phần.
- Bắt buộc: bìa có tên đề tài, lớp, **thành viên nhóm và phân công**; mục lục; kết luận; slide "Cảm ơn – Hỏi đáp".
- Hiệu ứng: phong phú; có thể thêm câu hỏi tương tác với người nghe.

### 2. Họp, báo cáo tại công sở (`cong-so`)
- Tình huống: họp giao ban, báo cáo tiến độ, trình lãnh đạo xin ý kiến; phòng họp nhỏ, màn hình TV hoặc máy chiếu.
- Trình bày: **kết luận trước** — slide 2 là tóm tắt điều hành (3 ý chính + đề xuất cần quyết định); số liệu bằng biểu đồ, bảng ngắn; chữ ≥ 20pt; nền sáng.
- Nhịp: 1–1,5 phút/slide; bài 10–15 phút → 8–12 slide.
- Bắt buộc: bìa có tên đơn vị, người báo cáo, ngày; tóm tắt điều hành; slide **kiến nghị, đề xuất**; số trang và tên đơn vị ở chân trang (để lãnh đạo chỉ "slide số 5").
- Hiệu ứng: tiết chế — chỉ fade, wipe cho danh sách, zoom cho số liệu chính; chuyển trang fade/push. Mọi slide hiển thị đủ nội dung sau tối đa 3 cú nhấp.
- Xuất kèm: PDF để gửi sau cuộc họp.

### 3. Hội nghị, hội thảo, lễ (`hoi-nghi`)
- Tình huống: hội trường lớn, đông đại biểu, có chủ toạ, thời lượng cố định; màn LED hoặc máy chiếu lớn, người ngồi xa.
- Trình bày: chữ nội dung ≥ 28pt, tiêu đề ≥ 40pt; tối đa 4 dòng hoặc 20 chữ; ưu tiên số liệu lớn và ảnh ấn tượng; nền tối hoặc sáng đều được nhưng tương phản rất cao.
- Bắt buộc: bìa có tên hội nghị, đơn vị tổ chức, thời gian, địa điểm; **slide chờ** (chiếu trước giờ khai mạc, chỉ tên hội nghị); slide cảm ơn.
- Hiệu ứng: phong phú nhưng trang nghiêm (zoom số liệu, Morph, fadeBlack giữa các phần).

### 4. Bảo vệ đồ án, luận văn, đề tài trước giảng viên / hội đồng (`bao-ve-do-an`)
- Tình huống: hội đồng chấm, giảng viên hướng dẫn; thường bị hỏi và yêu cầu lật lại slide cụ thể.
- Cấu trúc học thuật cố định: đặt vấn đề → mục tiêu, nhiệm vụ → cơ sở lý thuyết → phương pháp → kết quả → thảo luận → kết luận, hướng phát triển.
- Trình bày: chữ ≥ 20pt; được dày hơn (6 dòng, 45 chữ) nhưng vẫn ưu tiên sơ đồ, bảng, biểu đồ; trích dẫn nguồn ngay trên slide (cỡ 12pt) khi dùng số liệu, hình của người khác; nền sáng.
- Nhịp: khoảng 1 phút/slide; bài 15 phút → 13–16 slide.
- Bắt buộc: bìa có tên đề tài, người thực hiện, người hướng dẫn, đơn vị, năm; mục lục; **số trang trên mọi slide**; tài liệu tham khảo; cảm ơn – hỏi đáp; **phụ lục dự phòng** sau slide cảm ơn (chi tiết kỹ thuật, bảng số liệu đầy đủ để trả lời câu hỏi hội đồng).
- Hiệu ứng: **tối thiểu** — không đặt nội dung chính sau cú nhấp (khi lật lại slide, hội đồng phải thấy ngay toàn bộ); chỉ chuyển trang fade/push; dùng Morph cho sơ đồ phát triển dần nếu cần.
- Xuất kèm: PDF nộp hội đồng.

### 5. Giảng dạy trên lớp (`giang-day`)
- Tình huống: giáo viên dạy học sinh; phòng học sáng, có thể dùng TV hoặc máy chiếu.
- Cấu trúc theo tiến trình bài học (khởi động → mục tiêu → hình thành kiến thức → luyện tập → vận dụng → tổng kết → nhiệm vụ về nhà); khung chi tiết ở `dan-y-mau.md`.
- Trình bày: chữ ≥ 24pt (tiểu học ≥ 28pt); câu hỏi và đáp án tách cú nhấp; slide hoạt động ghi rõ nhiệm vụ, thời gian, sản phẩm.
- Nhịp: chậm, 2 phút/slide hoặc hơn (có hoạt động).
- Hiệu ứng: phong phú, phục vụ dạy học (đáp án hiện khi nhấp, nhấn mạnh từ khoá).

### 6. Tập huấn, bồi dưỡng, workshop (`tap-huan`)
- Tình huống: bồi dưỡng giáo viên, sinh hoạt chuyên môn liên trường, có thực hành.
- Trình bày: chữ ≥ 22pt; mỗi phần lý thuyết ngắn rồi đến **nhiệm vụ thực hành** (slide nhiệm vụ: yêu cầu – thời gian – sản phẩm – cách báo cáo); có đồng hồ đếm ngược hoặc ghi thời lượng.
- Bắt buộc: bìa có tên chuyên đề, đơn vị tổ chức; mục tiêu; chương trình buổi; slide nhiệm vụ nhóm; **mã QR hoặc đường dẫn tài liệu**; hỏi đáp.
- Hiệu ứng: vừa phải (wipe, fade, fly cho bước quy trình).
- Xuất kèm: PDF làm tài liệu phát tay.

### 7. Thuyết trình trực tuyến (`online`)
- Tình huống: Zoom, Google Meet, Teams; người xem trên laptop hoặc điện thoại; hình ảnh bị nén khi chia sẻ màn hình; dễ mất tập trung.
- Trình bày: tỉ lệ 16:9; chữ ≥ 24pt; tối đa 5 dòng; **tránh đặt nội dung ở góc trên bên phải** (thường bị khung camera che) và mép dưới (thanh điều khiển); tránh chữ mảnh, hoa văn nhỏ, chuyển màu (bị nén vỡ); nền đồng nhất.
- Nhịp: **nhanh hơn** — 30–60 giây/slide để giữ chú ý; tách một slide dày thành nhiều slide.
- Bắt buộc: bìa; **slide chờ trực tuyến** (tên buổi, giờ bắt đầu, hướng dẫn tắt micro); slide tương tác mỗi 5–7 phút (câu hỏi bình chọn, câu hỏi trả lời trong khung chat); hỏi đáp.
- Hiệu ứng: **nhẹ** — fade, push, Morph đơn giản; tránh hiệu ứng nhiều chi tiết, chạy dài (giật khi truyền hình ảnh).
- Xuất kèm: PDF gửi người tham dự.

### 8. Hội thi, cuộc thi, trình bày ý tưởng (`thi-pitch`)
- Tình huống: giáo viên dạy giỏi, sáng kiến kinh nghiệm, ý tưởng sáng tạo, khởi nghiệp; có ban giám khảo và giới hạn thời gian nghiêm ngặt.
- Trình bày: **mở đầu gây ấn tượng** (câu hỏi, con số, hình ảnh mạnh trong 30 giây đầu); sắp xếp nội dung **theo tiêu chí chấm** (nếu người dùng cung cấp thể lệ thì bám đúng thứ tự tiêu chí); kết thúc bằng thông điệp mạnh, dễ nhớ.
- Nhịp: nhanh, khoảng 45 giây/slide; tính đúng tổng thời gian cho phép, chừa 10% dự phòng.
- Hiệu ứng: phong phú, có chủ đích (Morph, zoom).

### 9. Gửi đọc trước / đăng tải (`doc-truoc`)
- Tình huống: gửi email, đăng lên website, nộp hồ sơ; không có người trình bày.
- Trình bày: slide phải **tự giải thích** — câu đầy đủ, tiêu đề là kết luận, có chú thích cho mọi biểu đồ; được dày hơn (≤ 10 dòng, chữ ≥ 14pt).
- Bắt buộc: bìa; tóm tắt; mục lục; số trang; nguồn số liệu.
- Hiệu ứng: **không dùng hiệu ứng xuất hiện** (nội dung phải thấy ngay); chuyển trang có thể giữ fade.
- Xuất kèm: **PDF là đầu ra chính**, .pptx kèm theo; không cần .ppsx.

### 10. Trình chiếu tự động (`trinh-chieu-tu-dong`)
- Tình huống: màn hình sảnh, gian trưng bày, chiếu trong giờ nghỉ, chiếu lặp tại sự kiện.
- Trình bày: rất ít chữ (≤ 3 dòng, ≤ 15 chữ), chữ ≥ 32pt; ảnh tràn viền; mỗi slide một thông điệp đọc được trong 3 giây.
- Nhịp: tự chuyển trang sau 6–10 giây mỗi slide; lặp vô hạn.
- Hiệu ứng: **tự động** — mọi hiệu ứng xuất hiện chạy sau slide trước (`autoFirst`, `start: "after"`), không cần nhấp; dùng `advanceAfter` và `MS.setLoop` (xem `hieu-ung.md`).

## 3. Bảng thông số nhanh
| Bối cảnh | Chữ nội dung tối thiểu | Tối đa/slide | Nhịp | Hiệu ứng | Xuất kèm |
|---|---|---|---|---|---|
| Học sinh, sinh viên | 24pt | 5 dòng · 30 chữ | 60 giây | phong phú | — |
| Công sở | 20pt | 6 dòng · 40 chữ | 90 giây | tiết chế | PDF |
| Hội nghị, hội thảo | 28pt | 4 dòng · 20 chữ | 75 giây | phong phú, trang nghiêm | — |
| Bảo vệ đồ án | 20pt | 6 dòng · 45 chữ | 60 giây | tối thiểu | PDF |
| Giảng dạy | 24pt (tiểu học 28pt) | 5 dòng · 30 chữ | ≥ 120 giây | phong phú | — |
| Tập huấn | 22pt | 6 dòng · 40 chữ | 120 giây | vừa phải | PDF |
| Online | 24pt | 5 dòng · 30 chữ | 30–60 giây | nhẹ | PDF |
| Hội thi, pitch | 24pt | 4 dòng · 25 chữ | 45 giây | phong phú | — |
| Gửi đọc trước | 14pt | 10 dòng · 90 chữ | — | không | PDF (chính) |
| Chiếu tự động | 32pt | 3 dòng · 15 chữ | 6–10 giây | tự động | — |

Số slide = thời lượng (giây) ÷ nhịp, làm tròn; cộng slide bìa, kết thúc và phụ lục dự phòng (nếu có).

## 4. Thứ tự ưu tiên khi các quy định mâu thuẫn
Bối cảnh (cỡ chữ, mật độ, hiệu ứng) **thắng** mặc định chung của skill và của phong cách. Ví dụ phong cách Sinh động vốn dùng hiệu ứng đủ danh mục, nhưng ở bối cảnh Bảo vệ đồ án thì hạ xuống mức tối thiểu.
