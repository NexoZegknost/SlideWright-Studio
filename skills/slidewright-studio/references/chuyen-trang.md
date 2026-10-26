# Chuyển trang: Morph là chủ đạo

Thư viện: `scripts/chuyen_trang.js` (gọi qua `PLAN[n].transition` của `makeslides.applyEffects`). In danh mục: `node scripts/chuyen_trang.js`.

Nguyên tắc: chuyển trang là **chuyển động liền mạch giữa hai slide**, không phải "lật trang". Mặc định mọi slide (trừ slide đầu) dùng **Morph** với một **cảnh morph** xuyên suốt bài. Chỉ dùng chuyển trang lướt (pan, push, wipe, reveal) khi đổi phần lớn hoặc hai slide không có gì chung. **Không dùng** chuyển trang cổ điển: lật 3D (flip, cube, gallery, prism, switch, doors, window…), cắt (cut), hoà tan/nhoè hạt (dissolve), ô cờ, rèm sáo, sọc ngẫu nhiên, xoáy, gợn sóng, tổ ong, xé vụn, lật trang… — `kiem_tra_hieu_ung.py` cảnh báo khi gặp.

## 1. Danh mục chuyển trang
| Tên | Chuyển động | Dùng khi |
|---|---|---|
| `morph` (`tuy`: `byObject` · `byWord` · `byChar`; `toc` ms, mặc định 1600) | đối tượng chung trôi, đổi cỡ, xoay, đổi màu; phần khác mờ chéo | **mặc định** cho mọi slide sau slide đầu |
| `fadeBlack` | mờ qua nền tối | slide đầu tiên, trước slide kết |
| `reveal` (`huong`: `l`/`r`) | slide cũ tối dần, slide mới trượt nhẹ vào | đổi phần lớn, trước câu hỏi lớn |
| `pan` (`huong`: `u`/`d`/`l`/`r`) | cả khung hình lia sang | đổi phần, đi tiếp theo trục thời gian |
| `push`, `cover`, `pull` (`huong`) | đẩy / phủ / kéo mở | slide chi tiết của một tổng quan |
| `wipe` (`huong`) | lau mềm mép | dòng thời gian, quy trình |
| `fade` | mờ chéo | slide không có cảnh chung |
| `zoom` | phóng nhẹ | đi sâu vào một ý (dùng ít) |

Cú pháp: `"morph"`, `["pan", "l"]`, hoặc `{ kieu: "morph", tuy: "byWord", toc: 1800 }`. Hằng số: `CT.MORPH`, `CT.MORPH_TU` (chữ trượt theo từ), `CT.MORPH_CHU` (theo ký tự). Mỗi chuyển trang có nhánh dự phòng (Fade/Push) cho PowerPoint cũ.

## 2. Cảnh morph — các thành phần làm Morph sinh động
Một cảnh là tập đối tượng trang trí tên `!!…` xuất hiện trên **mọi** slide, mỗi slide một **tư thế** theo vai. Morph nội suy giữa hai tư thế nên mỗi lần chuyển slide là một chuyển động.

```js
const CT = require(LIB + "chuyen_trang.js");
const canh = CT.canh(S, { motif: ["quyDao", "chuNen", "tienDo"], tong: soSlide, chu: "ánh đèn" });
L.baThe(pres, S, { ..., truoc: (sl) => canh.dat(sl, "noi-dung", { i: 6 }) });   // i = thứ tự slide
PLAN[6] = { transition: CT.MORPH, steps: r.steps, idle: r.idle };
```
Vai: `bia` · `noi-dung` (tự luân phiên biến thể k để khối đổi chỗ) · `nhan-manh` (câu tuyên bố, số liệu, câu hỏi) · `chia-phan` · `ket`. `toi: true` khi slide nền tối (mặc định bìa, chia phần, kết là tối).

| Motif | Thành phần | Chuyển động khi Morph | Hợp với |
|---|---|---|---|
| `quyDao` | 3 vầng tròn mờ | trôi giữa các góc, phình to ở bìa/chia phần, nép góc ở nội dung, tụ sau số liệu | mọi phong cách, mềm mại |
| `daiLua` | 1 băng màu chéo | xoay, kéo dãn từ dải lớn ở bìa → dựng đứng ở chia phần → mảnh như đường kẻ ở nội dung → phồng thành nền sau câu nhấn mạnh | công nghệ, kinh tế, sự kiện, bài trẻ |
| `manhHinh` | 4 mảnh hình nhỏ (tam giác, vuông, tròn, gạch) | bay sang chỗ mới và xoay 30–200° mỗi slide | học sinh, sinh động, sự kiện |
| `chuNen` | từ khoá khổng lồ rất mờ (`chu`) | trượt ngang qua từng slide (parallax), phình ở bìa/kết, dựng đứng ở chia phần | bài một chủ đề, nhân văn, nghệ thuật |
| `tienDo` | thanh tiến độ mảnh dưới chân | trườn dài theo vị trí slide trong bài | mọi bài (kín đáo) |

Gợi ý theo lĩnh vực nằm trong `assets/linh-vuc.json` → `hieu_ung.canh_morph`. Mỗi bài chọn **1–2 motif chính + `tienDo`**; nhiều hơn sẽ rối.

### Đối tượng kể chuyện (morph có ý nghĩa)
Ngoài cảnh trang trí, mỗi bài nên có 2–3 khoảnh khắc morph **mang nội dung**: cùng một đối tượng `!!tên` chuyển vai giữa hai slide liền nhau.
- **Ảnh thu/phóng**: ảnh lớn ở slide A thành biểu tượng nhỏ cạnh số liệu ở slide B (`CT.anh(duong, "ao")` cho bố cục; slide B thêm ảnh cùng tên). Ví dụ mẫu: chiếc áo trong thí nghiệm thu về góc slide kết quả.
- **Ánh sáng/hình chủ đề di chuyển**: đèn rọi ở bìa thu về góc slide câu hỏi (`!!den`).
- **Số chia phần → huy hiệu**: `L.chiaPhan(pres, S, { num: 2, soMorph: true, ... })` rồi ở slide nội dung đầu phần `truoc: (sl) => CT.soPhan(sl, S, 2)` — số lớn co lại, bay lên góc phải thành huy hiệu.
- **Chữ trượt**: hai slide liên tiếp có tiêu đề gần giống nhau → `CT.MORPH_TU`, các từ chung trượt về chỗ mới.

### Theo mức hiệu ứng của bối cảnh
| Mức | Cảnh morph |
|---|---|
| phong phú | 1–2 motif + `tienDo`, 2–3 khoảnh khắc kể chuyện |
| vừa phải, tiết chế | 1 motif nhẹ (`quyDao` hoặc `tienDo`), Morph 1400–1600 ms |
| nhẹ (trực tuyến) | 1 motif, Morph ≤ 1400 ms, không `chuNen` (chữ lớn mờ dễ vỡ hình khi truyền) |
| tối thiểu (bảo vệ đồ án), không | chỉ `tienDo` hoặc không cảnh; Morph cho sơ đồ cần biến đổi |
| tự động | như phong phú, thời gian tự chuyển ≥ Morph + 3 s |

### Quy tắc
1. Đối tượng `!!…` **không gắn hiệu ứng mở đầu** ở slide đích (sẽ biến mất rồi hiện lại). Bố cục tự bỏ hiệu ứng mở đầu của ảnh khi ảnh mang tên `!!`.
2. Cảnh nằm **trên texture, dưới nội dung** (vẽ trong `c.truoc`); khối trang trí trong suốt 80–95% để chữ vẫn đạt tương phản.
3. Hai slide liền nhau phải **khác tư thế** (vai khác hoặc biến thể k khác) — nếu không Morph thành mờ chéo đơn thuần (`kiem_tra_hieu_ung.py` báo "morph tĩnh").
4. Không để khối trang trí đè lên đoạn văn: tư thế nội dung nằm ở góc/mép; kiểm bằng `kiem_tra_bo_cuc.py` (bỏ qua tên `!!`, nhưng vẫn kiểm chữ chồng chữ).
5. Tốc độ: Morph 1400–2000 ms; lướt 800–1000 ms; `fadeBlack`/`reveal` 1200–1500 ms.
6. Morph cần PowerPoint 2019 hoặc Microsoft 365; bản cũ tự lùi về Fade.

## 3. Tự kiểm tra
- `python3 scripts/kiem_tra_hieu_ung.py file.pptx` → hết LỖI: Morph có đối tượng chung, có chuyển động, không có chuyển trang cổ điển; hiệu ứng chạy đúng thứ tự như PowerPoint.
- `python3 scripts/xem_truoc_morph.py file.pptx --ra xem_morph` → ảnh động từng cặp và bảng khung `morph_tong.png`: xem khối có trôi/xoay/đổi màu hài hoà không, có đè chữ trong lúc chuyển không, đối tượng kể chuyện đi đúng đường không.
