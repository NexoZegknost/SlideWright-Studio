# Thư viện bố cục (layout)

32 bố cục dựng sẵn trong `scripts/layouts.js`, tổng hợp từ các nguyên tắc thiết kế slide được giới thiết kế dùng phổ biến (tiêu đề hành động, lưới, bento, số liệu lớn, ảnh tràn viền, bố cục bất đối xứng). Đây là bố cục tự thiết kế, không sao chép mẫu của ai. Bảng xem trước: `assets/bo-cuc-sang-trong.jpg` (phong cách Sang trọng, cỡ chữ chuẩn) và `assets/bo-cuc-su-pham.jpg` (phong cách Sư phạm, cỡ chữ bối cảnh giảng dạy 24pt).

## 1. Nguyên tắc rút ra từ các mẫu đẹp
1. **Tiêu đề hành động**: tiêu đề nói kết luận, không nói chủ đề ("Tỉ lệ đạt yêu cầu tăng đều qua ba năm", không phải "Kết quả").
2. **Một điểm nhìn chính**: mỗi slide có đúng một yếu tố lớn nhất (con số, ảnh, câu tuyên bố, biểu đồ); mọi thứ khác nhỏ hơn rõ rệt.
3. **Lưới nhất quán**: lề 0,6", khoảng cách chuẩn 0,3" (lưới bento 0,2"); tiêu đề nội dung luôn cùng vị trí (y 0,45", cao 0,85").
4. **Tương phản kích thước mạnh**: số lớn 64–110pt, tiêu đề 30–44pt, nội dung 15–18pt (nhân hệ số theo bối cảnh), chú thích 10–12pt.
5. **Nhịp sáng – tối**: bìa, chia phần, trích dẫn, kết thúc dùng nền đậm; slide nội dung dùng nền sáng hoặc nền soft. Không để quá 3 slide nội dung liên tiếp cùng nền.
6. **Bố cục bất đối xứng có chủ đích**: chia 46/54 hoặc 40/60 thay vì 50/50 khi một bên là ảnh; khối lớn bên trái, chi tiết bên phải.
7. **Bento cho dữ liệu nhiều tầng**: một ô "anh hùng" chiếm diện tích lớn nhất cho số liệu quan trọng nhất, 3–4 ô nhỏ cho số phụ; chỉ một ô dùng màu nhấn.
8. **Ảnh làm chủ**: ảnh tràn viền hoặc tràn nửa slide, không viền mảnh; chữ đặt trên lớp phủ màu đậm (độ trong 15–25%) khi chồng lên ảnh.
9. **Một biểu đồ, một kết luận**: biểu đồ đi kèm một câu kết luận cỡ lớn đứng cạnh (không nhãn "Điểm chính"); trục cột bắt đầu từ 0; ghi nguồn.
10. **Lặp lại có hệ thống**: các slide cùng loại dùng cùng bố cục và cùng hiệu ứng; đổi bố cục giữa các loại slide để tạo nhịp.
11. **Không biểu tượng trước chữ**: không đặt icon/emoji trước đoạn văn, tiêu đề thẻ, gạch đầu dòng; không icon trong vòng tròn; không vòng "VS". Điểm nhìn là chữ, con số, ảnh thật, sơ đồ thật (xem `dau-hieu-ai.md`).
12. **Công thức là khối Equation**: mọi công thức dựng bằng `MS.equation` hoặc bố cục `congThuc`, không gõ bằng chữ.
13. **Mỗi bài ≥ 2 slide dựng riêng** cho nội dung đặc thù; khi thư viện không có bố cục hợp, tìm mẫu theo `mau-bo-cuc.md`.

## 2. Danh mục bố cục
| # | Hàm | Dùng cho | Nội dung `c` | Ghi chú |
|---|---|---|---|---|
| 01 | `biaToiGian` | Bìa mọi phong cách chính quy | kicker, title, sub, info | Nền đậm, căn trái |
| 02 | `biaAnhTran` | Bìa có ảnh mạnh (sự kiện, văn hoá, chuyên đề) | img, kicker, title, sub | Ảnh toàn slide, lớp phủ dưới |
| 03 | `biaChiaDoi` | Bìa bài giảng, báo cáo có ảnh minh hoạ | img, kicker, title, sub, info | Panel màu 46% + ảnh; `o.flip` đảo bên |
| 04 | `mucLuc` | Mục lục 3–6 phần | title, items[] | Số thứ tự lớn màu nhấn, đường kẻ mảnh |
| 05 | `chiaPhan` | Mở đầu mỗi phần | num, title, sub | Số khổng lồ mờ góc phải |
| 06 | `tuyenBo` | Câu thông điệp, khẩu hiệu, kết luận lớn | statement, highlight, by | Cụm `highlight` đổi màu nhấn |
| 07 | `soLon` | Một con số quan trọng | kicker, value, label, context | Số 110pt + hộp giải thích |
| 08 | `trichDan` | Trích dẫn, câu thơ, lời Bác, lời chuyên gia | quote, by, role | Dấu ngoặc kép lớn, nghiêng |
| 09 | `anhChu` | Một ý có ảnh minh hoạ, 3 gạch đầu dòng | img, kicker, title, bullets[] | Ảnh tràn nửa slide; `o.flip` |
| 10 | `chuAnhKhung` | Giới thiệu mô hình, địa điểm, sản phẩm + 3 chỉ số nhỏ | img, title, text, points[[số, nhãn]] | Ảnh trong khung trắng có bóng đổ |
| 11 | `soSanh` | Trước/sau, cũ/mới, ưu/nhược | title, left{label, items}, right{label, items} | Hai khối khác nền, khác độ rộng; bên phải (cái mới) nền đậm; không "VS" |
| 12 | `baThe` | 2–4 trụ cột, giải pháp, đặc điểm | title, cards[{mark?, head, text, img?}], highlight | Cột không nền, mở bằng vạch mảnh; `mark` là cụm chữ/số in lớn; không biểu tượng |
| 13 | `hangY` (tên cũ `hangIcon`) | Tóm tắt 4–5 khái niệm ngắn | title, items[{label, text}] | Ngăn bằng vạch dọc mảnh, căn trái; `o.dark` cho nền đậm |
| 14 | `dongThoiGian` | Mốc thời gian, lộ trình, lịch sử | title, events[{time, text}] 3–6 | Nhãn so le trên/dưới trục |
| 15 | `bieuDo` | Số liệu theo thời gian/nhóm | title, chart{type, data}, takeaway, source | Biểu đồ gốc PowerPoint + câu kết luận cỡ lớn có vạch nhấn |
| 16 | `bento` | Tổng quan nhiều chỉ số | title, hero{value, label}, tiles[{head, text}] 3–4 | Ô lớn trái, ô thứ 2 màu nhấn |
| 17 | `luoiAnh` | Hình ảnh hoạt động, minh chứng | title, imgs[3], caps[3] | 1 ảnh lớn + 2 ảnh nhỏ, chú thích phủ |
| 18 | `quyTrinh` | Quy trình 3–5 bước có thứ tự | title, steps[{head, text}] | Mũi tên chevron — dùng tiết kiệm (≤ 1 lần/bài), ưu tiên `buocDoc` |
| 19 | `maTran` | Phân loại 2 tiêu chí, ưu tiên | title, note, xLabel, yLabel, cells[4], highlight | Ô được chọn nền đậm |
| 20 | `bang` | Bảng ≤ 5 cột × 7 dòng | title, header[], rows[][], highlightRow, source | Dòng cần nhấn tô màu, số căn giữa |
| 21 | `nhiemVu` | Hoạt động học tập, nhiệm vụ nhóm, thực hành | kicker, title, tasks[], time, product | Huy hiệu thời gian, khối sản phẩm |
| 22 | `ketThuc` | Thông điệp cuối, cảm ơn, liên hệ | big, sub, contact | `big` nên là thông điệp cần nhớ; lời cảm ơn để ở `sub`. Bài kiểu cách tự dùng phông trang trí |

### 2b. Bố cục mở rộng (23–32) — sáng tạo hơn, ít "mẫu tải sẵn"
| # | Hàm | Dùng cho | Nội dung `c` | Ghi chú |
|---|---|---|---|---|
| 23 | `congThuc` (**async**, `await`) | Công thức trọng tâm + chú giải từng đại lượng | title, tex (LaTeX), terms[{tex, text}] 2–4, note, size | Khối Equation gốc của PowerPoint; ký hiệu ở chú giải cũng là equation |
| 24 | `chuKhongLo` | Mở phần, khái niệm then chốt, slide gây ấn tượng | word, title, text | Một từ cỡ 230pt mờ, tràn mép phải-dưới; tiêu đề góc trên trái |
| 25 | `thangSo` | 3–4 con số có thứ bậc | title, items[{value, label}] | Số chính 96pt, các số sau nhỏ dần trên cùng đường chân |
| 26 | `baoChi` | Phân tích, nghiên cứu, câu chuyện có trích dẫn | kicker, title, lead, body[], pull, by | Dàn trang tạp chí: đoạn dẫn, thân 2 cột, trích dẫn kéo ra lề phải |
| 27 | `anhLopKhoi` | Giới thiệu nơi chốn, sản phẩm, hoạt động có ảnh tốt | img, kicker, title, text | Ảnh lớn lệch một bên, khối đậm đè mép ảnh tạo chiều sâu; `o.flip` |
| 28 | `hinhChuThich` | Sơ đồ mạch, hình kỹ thuật, bản đồ, ảnh cần chỉ chi tiết | title, img, imgW, callouts[{px, py, text}] 2–5 | Điểm trên hình nối chú thích đánh số bằng đường dẫn mảnh; px, py từ 0–1 |
| 29 | `hoiDap` | Câu hỏi gợi mở, kiểm tra nhanh, khởi động | kicker, question, answer, hint | Câu hỏi rất lớn; lời đáp hiện sau cú nhấp |
| 30 | `luoiThuySy` | Thông điệp + 3 dữ kiện | title, facts[{value, label}] 3, text | Lưới 12 cột: tiêu đề lớn góc dưới trái, dữ kiện xếp dọc cột phải |
| 31 | `buocDoc` | Quy trình 3–5 bước (thay chevron) | title, sub, steps[{head, text}] | Khối tiêu đề đậm 1/3 trái, bước xếp dọc, số bước nhỏ |
| 32 | `biaThuongHieu` | Bìa theo bộ nhận diện đơn vị (cần `S = brand(...)`) | title, sub, info, lang | Logo đơn giữa trên, cụm tam giác hai góc, logo ngang ở chân; xem `thuong-hieu.md` |

Bối cảnh bảo vệ đồ án, công sở: dùng thêm `bang`, `bieuDo`, `soSanh`, `buocDoc`, `hinhChuThich`, `congThuc`. Giảng dạy: `nhiemVu`, `hoiDap`, `baThe`, `anhChu`, `congThuc`. Hội nghị: `soLon`, `thangSo`, `bento`, `biaAnhTran`, `luoiAnh`, `luoiThuySy`. Văn hoá, nghiên cứu: `baoChi`, `trichDan`, `anhLopKhoi`.

## 3. Cách dùng
```js
const { L, style, setScale } = require(LIB_DIR + "/layouts.js");
const MS = require(LIB_DIR + "/makeslides.js");
const S = style("su-pham");                 // phong cách (Bước 1); style("su-pham", { headIndex: 1 }) chọn phông tiêu đề thứ hai
setScale(ctx.body_min);                       // cỡ chữ theo bối cảnh (contexts.json), gọi trước khi dựng
const pres = new pptxgen(); pres.layout = "LAYOUT_16x9";
const plan = {}; let n = 0;
const push = (r, transition) => { plan[++n] = { transition, steps: r.steps, autoFirst: r.autoFirst, idle: r.idle, ket: r.ket }; };
push(L.biaToiGian(pres, S, { title: "…", sub: "…" }), "fadeBlack");
push(L.baThe(pres, S, { title: "…", cards: [{ mark: "92%", head: "…", text: "…" }], highlight: 0 }), "fade");
push(await L.congThuc(pres, S, { title: "…", tex: "A_v = -\\frac{R_C}{r_e}", terms: [{ tex: "R_C", text: "…" }] }), ["push", "l"]);
let buf = await pres.write({ outputType: "nodebuffer" });
buf = await MS.applyEffects(buf, plan);   // steps gợi ý sẵn theo bố cục; chỉnh theo mức hiệu ứng của bối cảnh
```
- Đánh dấu điểm nhấn trong mọi chuỗi chữ bằng `**…**` (tự in đậm + màu nhấn).
- `idle` mỗi bố cục trả về là gợi ý hiệu ứng chờ cho điểm nhấn; giữ, chỉnh hoặc bỏ theo mức của bối cảnh (`hieu-ung.md`).
- `steps` mỗi bố cục trả về là gợi ý mức phong phú. Bối cảnh tiết chế/tối thiểu/không: rút gọn hoặc bỏ `steps` (xem `hieu-ung.md`).
- **Không dùng biểu tượng trước chữ.** Hàm `icon()` chỉ còn cho hình minh hoạ độc lập cỡ lớn (ví dụ sơ đồ tự vẽ cần một ký hiệu thiết bị), không đặt cạnh tiêu đề/đoạn văn.
- Nền động và lớp trang trí có hiệu ứng chờ: thêm vào nội dung slide `nenDong: true` (texture `nen` trôi chậm), `truoc: (sl) => [...]` (vẽ đèn, hạt sáng, vòng xoay bằng `hieu_ung.js`, trả về mảng idle) hoặc `cho: [...]`; bố cục tự gộp vào `idle`.
- Bố cục tự lọc gợi ý hiệu ứng: phần tuỳ chọn (sub, text, info…) không có thì tự bỏ khỏi `steps`/`idle`.
- Ảnh: đường dẫn tệp cục bộ (tải từ Unsplash hoặc ảnh người dùng gửi). Thiếu ảnh → khối giữ chỗ màu soft (phải thay trước khi bàn giao).
- Không ghép quá 2 bố cục giống nhau liên tiếp. Bố cục chưa có trong thư viện → tìm mẫu và tự dựng theo `mau-bo-cuc.md`, đặt `objectName` cho mọi đối tượng.

## 4. Kiểm tra sau khi dựng
Chạy `python3 scripts/kiem_tra_slide.py <file>.pptx` (màu, dấu hiệu AI, công thức dạng chữ). `fit: "shrink"` chỉ có tác dụng khi người dùng mở và sửa trong PowerPoint; ảnh kiểm tra không co chữ. Vì vậy **luôn render và xem từng slide**: chữ tràn khung thì rút gọn nội dung hoặc chuyển sang bố cục chứa được nhiều chữ hơn, không giảm cỡ chữ dưới mức tối thiểu của bối cảnh.

## Nguồn tham khảo nguyên tắc
- Made Good Designs — 15 Slide Layout Ideas for Clean Presentations (madegooddesigns.com/slide-layout-ideas)
- Deckary — Presentation Design: The Complete Guide to Professional Slide Types (deckary.com/blog/pillar-slide-types-guide)
- StudioMeyer — Bento Grid Layouts (studiomeyer.io/en/blog/bento-grid-layouts)
- Slidesgo — Presentation Design Trends 2026 (slidesgo.com/slidesgo-school/ai-presentations/presentation-design-trends-2026)
- Beautiful.ai — Presentation Design Trends (beautiful.ai/blog)
- Swiper Studio — Bold Typography Templates (studio.swiperjs.com/blog/15-bold-typography-templates)
- Thêm nguồn và quy trình học mẫu: `mau-bo-cuc.md`
