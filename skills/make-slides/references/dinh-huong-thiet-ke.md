# Module định hướng thiết kế (`scripts/dinh_huong.js`)

Từ **đề tài** (và mô tả, bối cảnh, thương hiệu nếu được yêu cầu), module xác định **lĩnh vực**, rồi dựng **3 phương án phong cách hoàn chỉnh**: bảng màu theo luật phối màu (`phoi-mau.md`), phông, texture cho bìa/chia phần/nội dung, cách trình bày, bố cục ưu tiên và hạn chế, hiệu ứng. Tri thức theo lĩnh vực nằm ở `assets/linh-vuc.json` (12 lĩnh vực); texture sinh bằng `scripts/hoa_tiet.py`.

## Khi nào dùng
Bước 1 của mọi bài tạo mới (thay cho việc chọn tay 3 trong 11 phong cách): chạy module, xem tóm tắt + ảnh xem trước, gửi người dùng chọn. Bộ 11 phong cách có sẵn vẫn là một phương án trong 3 (khi không dùng thương hiệu).

```bash
node scripts/dinh_huong.js --chu-de "<đề tài>" [--mo-ta "<tóm tắt nội dung>"] [--boi-canh hoc-sinh-sinh-vien] \
    [--thuong-hieu bk-hcmut]  [--linh-vuc khoa-hoc-xa-hoi]  [--phu-de "<phụ đề>"] --xem-truoc xem-truoc.png
```
- `--thuong-hieu` **chỉ** khi người dùng yêu cầu dùng tài nguyên của đơn vị (xem `thuong-hieu.md`).
- `--linh-vuc` ép lĩnh vực khi đề tài lai (tóm tắt in "gần: …" để gợi ý).
- Kết quả in: lĩnh vực nhận diện (từ khoá khớp), mẫu người dùng đã gửi cho lĩnh vực đó, và với từng phương án: màu (mã + tên), phông, texture, bố cục, cách trình bày, cảnh báo.

## Dùng trong script dựng
```js
const DH = require(LIB + "/dinh_huong.js");
const kq = DH.dinhHuong({ chuDe, moTa, boiCanh, thuongHieu });   // thuongHieu: chỉ khi được yêu cầu
const pa = kq.phuongAn[i];                 // phương án người dùng chọn
const S = DH.apDung(pa);                   // dùng như style(): mọi bố cục layouts.js nhận S này (có S.brand nếu có thương hiệu)
const tex = DH.taoTexture(pa, "tex");      // { bia, "chia-phan", "noi-dung" } → PNG trong suốt
push(L.biaThuongHieu(pres, S, { title, sub, nen: tex.bia }, { dark: true }));   // có thương hiệu
push(L.biaToiGian(pres, S, { title, sub, nen: tex.bia }));                      // không thương hiệu
push(L.chiaPhan(pres, S, { num: 1, title, nen: tex["chia-phan"] }, { dark: true }));
push(L.baoChi(pres, S, { ..., nen: tex["noi-dung"] }));
```
- `c.nen` (mọi bố cục): texture đặt dưới cùng slide, trước mọi đối tượng.
- `DH.taoTexture` trả về **bộ texture** `{ bia:[…], "chia-phan":[…], "noi-dung":[…], "nhan-manh":[…] }`: mỗi vai có nhiều **biến thể**, mỗi biến thể là nhiều **lớp** chồng nhau (ví dụ quầng sáng + lưới phối cảnh + hạt sáng). Chọn bằng `DH.nen(tex, vai, k)` — k là thứ tự slide trong vai đó, tự luân phiên; biến thể rỗng = slide trơn để thở.

## Dùng texture tích cực nhưng có hệ thống
- Bìa, slide chia phần, slide nhấn mạnh (tuyên bố, trích dẫn, kết thúc): luôn có texture nhiều lớp.
- Slide nội dung: texture nhẹ, luân phiên 2–3 biến thể; khoảng 1/3 slide để trơn; chữ không đặt lên phần đậm nhất của texture.
- **Nhiều mẫu, một phong cách**: mọi texture trong bài dùng chung bảng màu của phương án (vai màu `toi-nhan`, `toi-trang`, `toi-phu`, `sang-nhan`, `sang-phu`, `sang-mo`), cùng độ dày nét và mật độ; bìa và slide nhấn mạnh có thể chung một lớp (ví dụ cùng quầng sáng).
- **Sáng tạo mẫu mới theo hoàn cảnh**: `python3 scripts/hoa_tiet.py --lop '[...]'` ghép tự do 16 kiểu (chấm, mạch, sóng, đồng mức, vòng đồng tâm, khối hình học, chữ thập, lưới phối cảnh, hạt sáng, giấy, kẻ ô, kẻ lề, lục giác, gạch chéo, quầng sáng, tam giác). Ví dụ hội thảo môi trường ngoài trời → đồng mức + sóng + quầng sáng xanh lục; bài thiên văn → hạt sáng + vòng đồng tâm; bảo vệ đồ án cơ khí → lưới phối cảnh + chữ thập. Lưu ý: texture chỉ là nền — không thay ảnh thật, sơ đồ thật.
- `S.dinhHuong` mang theo bố cục ưu tiên/hạn chế, cách trình bày, tỉ lệ slide nền tối, hiệu ứng — dùng khi lập dàn ý (cột *Bố cục*) và khi đặt PLAN.
- Phông của phương án phải được nhúng: `MS.embedFonts(buf, [S.head, S.body, S.accentFont].filter(Boolean))`.

## Cách module phối màu
1. Màu chủ đạo: theo sắc của lĩnh vực (`mau.hue`), hoặc **giữ màu thương hiệu** khi có thương hiệu (lĩnh vực trầm như KHXH, nhân văn được hạ về cùng sắc nhưng đậm, trầm hơn — logo vẫn đúng màu gốc).
2. Chữ nhấn trên nền đậm theo `chuNhanToi` của lĩnh vực: ngà ấm (bài trầm, học thuật), trắng, hoặc sắc tương đồng rất sáng ≥ 7:1 — **không bao giờ tím** (chữ tím trên nền tối bị chìm).
3. Màu nhấn, màu phụ: lệch sắc trong vùng **tương đồng** (`lechNhan`, `lechPhu`, |lệch| ≤ 90°) theo lĩnh vực — công nghệ lệch về lục lam/bạc hà, KHXH lệch về chàm – mận trầm, môi trường lệch về lục…
4. Chữ nhấn trên nền sáng: màu nhấn làm đậm đến 4,6:1.
5. Mọi bảng màu qua `mau.kiemTraBangMau`; lỗi thì tự xoay độ lệch và thử lại; còn lỗi thì in cảnh báo.

## Ba phương án
| Không có thương hiệu | Có thương hiệu (được yêu cầu) |
|---|---|
| 1. Đề xuất: bảng màu sinh theo lĩnh vực | 1. Đề xuất: màu thương hiệu + màu nhấn theo lĩnh vực, texture lĩnh vực + motif thương hiệu |
| 2. Biến thể lĩnh vực (kiểu phối/texture khác) | 2. Biến thể: đơn sắc theo màu thương hiệu |
| 3. Phong cách có sẵn hợp lĩnh vực (`styles.json`) | 3. Nhận diện gốc của đơn vị |

Ví dụ: "Thiết kế mạch BJT" + Bách khoa → xanh đậm BK, nhấn lục lam, chữ nhấn bạc hà, phông Bricolage/Lexend/Space Mono, cụm tam giác BK ở bìa, mạch – lục giác – lưới chấm. "Tác động của mạng xã hội…" + Bách khoa → xanh mực trầm cùng sắc BK, nhấn chàm – mận, nền giấy ngà, phông Lora/Montserrat, lưới tam giác BK rất mờ, gạch chéo, vân giấy, bố cục trang báo – trích dẫn.

## Thêm hiểu biết mới
- **Mẫu người dùng gửi**: học theo `mau-bo-cuc.md` mục 3, lưu ảnh + ghi chú vào `assets/mau-theo-de-tai/<lĩnh vực>/`; nếu mẫu cho thấy cách phối màu/texture khác cho lĩnh vực, cập nhật mục lĩnh vực trong `linh-vuc.json` (sắc chủ đạo, độ lệch, texture, bố cục) rồi đóng gói lại plugin.
- **Lĩnh vực mới**: thêm một mục vào `linh-vuc.json` cùng cấu trúc (từ khoá không dấu, màu, phông có trong gói, texture, bố cục, trình bày, hiệu ứng, cấu hình khi có thương hiệu).
