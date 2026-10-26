# Quy trình kỹ thuật — PowerPoint (.pptx + .ppsx)

## 0. Chuẩn bị
- Nếu môi trường có skill `pptx` (`anthropic-skills:pptx` hoặc `pptx`), **đọc SKILL.md của nó trước** và tuân thủ các lưu ý pptxgenjs, kiểm tra, render. Tài liệu này bổ sung, không thay thế.
- Cài phụ thuộc trong thư mục làm việc: `npm install fonteditor-core jszip mathjax-full@3 mathml2omml sharp opentype.js@1.3.4`; kiểm tra văn bản tiếng Việt: `pip install pyvi --break-system-packages` (tách từ ghép để không xuống dòng giữa từ) (pptxgenjs thường có sẵn; thiếu thì `npm install pptxgenjs`). Chạy script với `NODE_PATH=$PWD/node_modules:$(npm root -g)` (react, react-icons, sharp thường cài toàn cục).
- Thư viện bố cục: `scripts/layouts.js` (xem `bo-cuc.md`) — ưu tiên dùng thay vì tự đặt toạ độ.
- Thư viện của plugin: `${CLAUDE_PLUGIN_ROOT}/skills/make-slides/scripts/makeslides.js` (`applyEffects`, `embedFonts`, `save`, `installFontsForPreview`). Nếu biến `CLAUDE_PLUGIN_ROOT` không có, tìm tệp bằng `find / -path "*make-slides/scripts/makeslides.js" 2>/dev/null | head -1`.

## 1. Dựng bằng pptxgenjs (bộ slide có cấu trúc)
- `pres.layout = "LAYOUT_16x9"` (10" × 5,625") đặt **trước** khi thêm slide.
- THEME: phông tiêu đề/nội dung theo `phong-chu.md`, bảng màu theo `nguyen-tac-thiet-ke.md`. `pres.theme = { headFontFace, bodyFontFace }`.
- Ghi rõ `fontFace` cho từng hộp chữ dùng phông khác phông nội dung (tiêu đề, điểm nhấn).
- **Mọi đối tượng sẽ có hiệu ứng đều có `objectName` duy nhất** trong slide; đối tượng Morph đặt tên bắt đầu bằng `!!` và giống nhau ở hai slide liên tiếp (cùng loại hình).
- Danh sách cần hiện từng dòng: một hộp chữ, mỗi ý là một đoạn (`bullet: true`, `breakLine: true`).
- Lưu ý kỹ thuật: mã màu không có `#`; không dùng chung object tuỳ chọn; `isTextBox: true` cho mọi `addText`; ghi chú diễn giả dùng `slide.addNotes()`.

## 1b. Công thức — khối Equation gốc
Mọi công thức (vật lý, toán, hoá, kinh tế…) dựng bằng khối Equation của PowerPoint để hiển thị đúng và sửa được bằng *Equation Tools*:
```js
await MS.equation(slide, "I_C = \\beta I_B", { x: 0.6, y: 2, fontSize: 28, color: S.c.text, name: "eq1", align: "left" });
```
- Viết bằng LaTeX (MathJax): `\\frac{}{}`, `_{}`, `^{}`, `\\sqrt{}`, `\\approx`, `\\text{với }`; dấu thập phân kiểu Việt `237{,}7`.
- Gọi **trước** `pres.write`; `applyEffects` tự đổi ảnh giữ chỗ thành `<a14:m>` (OMML) kèm ảnh dự phòng cho trình xem cũ. Gắn hiệu ứng theo `name` như mọi đối tượng.
- Kích thước tự tính theo `fontSize`; trả về `{ name, w, h }` để đặt các khối khác. Bố cục `congThuc` dựng sẵn công thức + chú giải đại lượng.
- Trong bảng: ô bảng không chứa được equation → đưa công thức ra ngoài bảng (cột chữ ghi tên đại lượng, công thức đặt cạnh bằng `MS.equation`) hoặc tách slide `congThuc`.
- Giá trị đơn có đơn vị ("VCC = 12 V") viết bằng chữ thường, không cần equation.

## 2. Hậu xử lý (thứ tự bắt buộc)
```js
const MS = require(LIB);
let buf = await pres.write({ outputType: "nodebuffer" });
buf = await MS.applyEffects(buf, PLAN);                 // 1. công thức + hiệu ứng (xem hieu-ung.md)
buf = await MS.embedFonts(buf, ["Playfair Display", "Montserrat"]);  // 2. nhúng mọi họ phông đã dùng
await MS.save(buf, "Slide_<ChuDeKhongDau>_<ddmmyyyy>");  // 3. dọn gói (khai báo thừa) + ghi .pptx + .ppsx
```
- Nhúng phông làm file lớn thêm ~0,2–0,4 MB mỗi kiểu chữ. Chỉ nhúng họ phông thực sự dùng.

- Bối cảnh chiếu tự động: thêm `advanceAfter` cho mọi slide trong PLAN và `buf = await MS.setLoop(buf)` trước `embedFonts`.
- Bối cảnh có `so-trang-chan-trang`: đặt `slideNumber` và chân trang (tên đơn vị · ngày) trên layout (`defineSlideMaster`), không đặt từng slide.
- Bối cảnh có `xuat_kem: ["pdf"]`: sau khi lưu, chuyển .pptx → PDF bằng script `soffice` của skill pptx (đã `installFontsForPreview` để PDF đúng phông) và bàn giao kèm.

## 3. Tự kiểm tra
1. `markitdown file.pptx` → chính tả, dấu, thứ tự, chữ giữ chỗ còn sót.
2. `python <skill pptx>/scripts/office/validate.py file.pptx` → phải PASSED.
2a. `python3 scripts/kiem_tra_van_ban.py file.pptx --sua file_sua.pptx` → văn bản (cỡ ≥ 24pt, lượng chữ, giãn dòng, xuống dòng giữ nghĩa, tiêu đề 2 dòng trên ngắn dưới dài, dòng mồ côi); bàn giao bản đã sửa khi hết LỖI.
2d. `python3 scripts/kiem_tra_hieu_ung.py file.pptx` → hết LỖI (hiệu ứng chạy đúng như PowerPoint, Morph, chuyển trang); `python3 scripts/xem_truoc_morph.py file.pptx --ra xem_morph` để xem Morph.
2c. `python3 scripts/kiem_tra_bo_cuc.py file.pptx --anh kiem_tra` → hết LỖI và CẢNH BÁO (văn bản/vật thể lệch khung, đường kẻ chạm chữ, chữ tràn khối màu, ra ngoài slide).
2b. `python3 scripts/kiem_tra_slide.py file.pptx` → hết LỖI; xem từng CẢNH BÁO (màu, dấu hiệu AI theo `dau-hieu-ai.md`, công thức dạng chữ).
3. Render ảnh: gọi `MS.installFontsForPreview([...])` trước để LibreOffice có phông, rồi chuyển PDF → ảnh (`soffice` qua script của skill pptx, `pdftoppm -r 100`). Xem **từng slide**: tràn chữ, xuống dòng xấu (từ/cụm từ bị tách, chữ mồ côi một từ ở dòng cuối tiêu đề), cỡ chữ đủ lớn, tương phản, độ tập trung (mỗi slide một điểm nhìn chính), lệch lề.
4. Hiệu ứng: kiểm tra XML (mỗi slide trong PLAN có `<p:timing>` / `<p:transition>`). Ảnh render không hiện hiệu ứng.
5. Sửa trong script → dựng lại → render lại các slide đã sửa.

## 4. Bàn giao
Gửi cả hai tệp: `.ppsx` (mở là trình chiếu ngay) và `.pptx` (để chỉnh sửa). Ghi chú cho người dùng: nếu sửa và lưu lại trong PowerPoint, giữ tuỳ chọn *File → Options → Save → Embed fonts in the file* (đã bật sẵn) để phông đi theo tệp.

## Nâng cấp file .pptx có sẵn
- Đọc nội dung bằng `markitdown`, tạo ảnh lưới thu nhỏ để xem hiện trạng.
- Giữ nguyên nội dung và thứ tự (trừ khi người dùng cho phép rút gọn); dựng lại theo thiết kế mới.
- Đặt tên file mới có hậu tố `_nang_cap`, không ghi đè file gốc.

## Kinh nghiệm dựng thực tế (đã kiểm chứng)
- **Layout có chân trang** (`defineSlideMaster` với footer + slideNumber) chỉ dùng cho slide nội dung. Slide có khối màu phủ cả chiều cao (mục lục, bìa phụ) dùng layout **không chân trang** riêng, nếu không chân trang bị che lộ một nửa.
- **Morph**: theo `references/chuyen-trang.md` — cảnh morph `CT.canh(...)` trên mọi slide, `transition: CT.MORPH`; số chia phần → huy hiệu bằng `L.chiaPhan(..., { soMorph: true })` + `CT.soPhan(sl, S, n)` ở slide nội dung đầu phần.
- **Xuống dòng**: dùng ` ` giữa ký hiệu–số (`CV 7991`); rút gọn hoặc giảm cỡ khi tiêu đề thẻ tách 1–2 từ xuống dòng; kiểm tra lại sau mỗi lần sửa bằng ảnh render.
- **Họa tiết trên nền tối**: dùng bản mờ (`_dim`, ~45%) đặt lệch phải, tràn mép; chữ không đè lên phần đậm nhất của họa tiết.
- **Thanh tỉ lệ 100%** vẽ bằng `RECTANGLE` nối tiếp (rộng = tổng × %), nhãn % chỉ đặt khi đoạn ≥ 8% → tránh nhãn chồng nhau của biểu đồ stacked.
- **Biểu đồ tròn/vành khuyên**: hiện giá trị (`showValue`) thay vì `showPercent` khi % đã ghi đúng một chữ số thập phân ở chú thích (tránh làm tròn lệch 26% vs 26,4%).
- Ảnh từ người dùng (banner hội nghị là ảnh chụp màn hình) → cắt bỏ viền 5–6 px rồi đặt `sizing: cover`.
- **Kiểm tra sau dựng**: đếm cú nhấp/slide và sự có mặt của `<p:transition>` bằng `unzip -p … slideN.xml | grep -c clickEffect`.
