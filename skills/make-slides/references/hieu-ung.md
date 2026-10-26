# Hiệu ứng (animation) và chuyển trang (transition)

Mặc định của plugin: **mức phong phú** — mỗi slide nội dung có hiệu ứng xuất hiện theo mạch nói, chuyển trang đa dạng, dùng Morph cho các cặp slide liên tục. "Phong phú" không có nghĩa là lộn xộn: hiệu ứng phải phục vụ thứ tự trình bày.

Cài đặt bằng `scripts/makeslides.js` → `applyEffects(buf, PLAN)`. Mọi đối tượng cần hiệu ứng phải có `objectName` duy nhất trong slide.

## Danh mục
### Xuất hiện / nhấn mạnh (`eff`)
| Tên | Hiệu ứng PowerPoint | Hợp với |
|---|---|---|
| `appear` | Appear | Đáp án, ký hiệu nhỏ |
| `fade` | Fade | Chú thích, ảnh nền, mọi thứ cần nhẹ nhàng |
| `floatUp` | Float In | Phụ đề, đoạn văn ngắn, thẻ nội dung |
| `fly` (`dir`: up/down/left/right) | Fly In | Thẻ, cột so sánh, mũi tên quy trình |
| `zoom` | Zoom | Con số lớn, tiêu đề bìa, công thức |
| `wipe` (`dir`) | Wipe | Danh sách từng dòng, dòng thời gian, thanh tiến trình |
| `split` | Split | Trích dẫn, khẩu hiệu |
| `wheel` | Wheel | Biểu đồ tròn, vòng tròn số liệu |
| `pulse` | Pulse (nhấn mạnh) | Nhấn lại một con số/kết luận đã hiện |

Tuỳ chọn mỗi hiệu ứng: `dur` (ms, mặc định 600), `delay` (ms), `start`: `"click"` | `"with"` | `"after"`, `byPara: true` (hộp chữ hiện từng đoạn theo từng cú nhấp).

### Chuyển trang (`transition`)
| Tên | Dùng khi |
|---|---|
| `fadeBlack` | Slide bìa, slide kết thúc, chuyển phần lớn |
| `fade` | Mặc định an toàn |
| `push` (`u`/`d`/`l`/`r`) | Đi tiếp trong cùng một phần |
| `wipe` (`r`/`l`/`u`/`d`) | Dòng thời gian, quy trình |
| `cover` (`l`/`r`…) | Slide chi tiết phủ lên slide tổng quan |
| `split` | Slide chia phần, trích dẫn |
| `zoom` | Đi sâu vào một ý, slide số liệu |
| `circle` | Slide kết thúc, cảm ơn (bài kiểu cách) |
| `morph` | Hai slide liên tiếp chung đối tượng (đặt cùng objectName bắt đầu bằng `!!`). Cần PowerPoint 2019/365; bản cũ tự chuyển thành Fade |

## Mức hiệu ứng theo bối cảnh (`contexts.json` → `hieu_ung`)
| Mức | Bối cảnh | Cách làm |
|---|---|---|
| phong phú | học sinh/sinh viên, hội nghị, giảng dạy, hội thi | dùng đủ danh mục theo quy tắc dưới |
| vừa phải | tập huấn | ≤ 3 cú nhấp/slide; fade, wipe, fly, zoom; Morph có chọn lọc |
| tiết chế | công sở | ≤ 3 cú nhấp; chỉ fade, wipe (danh sách), zoom (số liệu chính); chuyển trang fade/push |
| nhẹ | online | fade, push, Morph đơn giản; dur ≤ 500; tránh wheel, split, chuỗi hiệu ứng dài |
| tối thiểu | bảo vệ đồ án | nội dung chính hiện sẵn, không đặt sau cú nhấp; chỉ chuyển trang fade/push, Morph cho sơ đồ |
| không | gửi đọc trước | không hiệu ứng xuất hiện; chuyển trang fade hoặc không |
| tự động | chiếu tự động | mọi slide `autoFirst: true`, các hiệu ứng `start: "after"`, `advanceAfter: 6000–10000`; gọi `MS.setLoop(buf)` để lặp vô hạn ở chế độ kiosk |

## Hiệu ứng chờ (trong lúc thuyết trình)
Sau khi nội dung của slide đã hiện hết, **điểm nhấn** được gắn một hiệu ứng nhỏ **lặp lại theo chu kỳ** cho đến khi rời slide, giúp slide không đứng yên và kéo mắt người xem về ý chính trong lúc người trình bày nói. Khai báo trong `PLAN[n].idle`; các bố cục trong `layouts.js` trả về sẵn gợi ý `idle`.

| Tên (`eff`) | Hiệu ứng | Hợp với |
|---|---|---|
| `inDam` | Thoáng in đậm rồi trở lại | Từ khoá trong câu thường (hộp chữ không đậm sẵn) |
| `inNghieng` | Thoáng in nghiêng rồi trở lại | Trích dẫn, thuật ngữ |
| `gachChan` | Gạch chân rồi biến mất | Từ khoá, kết luận |
| `doiMau` | Đổi sang màu nhấn rồi về (`color`) | Câu tuyên bố, lời cảm ơn |
| `rung` | Rung/lắc nhẹ | Huy hiệu thời gian, con số ngắn |
| `nay` | Nảy lên rồi rơi xuống | Chữ ngắn, con số, bài học sinh |
| `nhip` | Phóng nhẹ 6% rồi thu lại (nhịp thở) | Con số lớn, ô quan trọng, nút cuối quy trình |
| `mo` | Mờ thoáng rồi rõ lại | Số khổng lồ trang trí, ảnh nền |
| `xoay` | Xoay một vòng | Hình minh hoạ nhỏ (dùng rất ít) |

Tuỳ chọn: `period` (chu kỳ lặp, ms; mặc định 8000), `dur` (độ dài hiệu ứng, mặc định 900), `delay` (chờ sau nội dung cuối, mặc định 1500), `para` (chỉ một đoạn của hộp chữ), `color` (cho `doiMau`).
```js
PLAN[7] = { transition: "zoom", steps: [...], idle: [{ n: "value", eff: "nhip", period: 9000 }] };
```

Quy tắc:
1. **Chỉ gắn cho điểm nhấn** (con số, từ khoá, biểu tượng, ô được chọn) — không gắn cho đoạn văn đang đọc, tiêu đề hay ảnh lớn.
2. **Tối đa 2 đối tượng chờ mỗi slide**; nhiều biểu tượng cùng loại thì so le `delay` (ví dụ 1500, 5500, 9500) để chúng lần lượt chuyển động, không cùng lúc.
3. **Chu kỳ 7–15 giây**: đủ để kéo mắt mà không gây rối. Không dưới 6 giây.
4. Hiệu ứng chữ (`inDam`, `inNghieng`, `gachChan`, `doiMau`) chỉ dùng cho hộp chữ; hiệu ứng chuyển động (`rung`, `nay`, `nhip`, `mo`, `xoay`) dùng cho mọi hình.
5. Theo bối cảnh:

| Mức hiệu ứng của bối cảnh | Hiệu ứng chờ |
|---|---|
| phong phú | Bật: 1–2 đối tượng/slide, dùng cả danh mục, chu kỳ 7–10 giây |
| vừa phải | Bật: 1 đối tượng/slide, ưu tiên `nhip`, `gachChan`, `doiMau`, chu kỳ 10–12 giây |
| tiết chế (công sở) | Chỉ slide số liệu chính và slide kết luận: `nhip` hoặc `gachChan`, chu kỳ ≥ 12 giây |
| nhẹ (online) | Chỉ `doiMau`, `gachChan`, `inDam` (không chuyển động — tránh giật khi truyền hình) |
| tối thiểu (bảo vệ đồ án), không (gửi đọc trước) | Tắt |
| tự động | Bật nhẹ, `period` ≤ thời gian tự chuyển slide |

6. Phong cách chính quy (Học thuật, Hành chính, Sang trọng): ưu tiên `gachChan`, `doiMau`, `nhip`, `inDam`; hạn chế `nay`, `xoay`. Phong cách Sinh động, Thiếu nhi: dùng thoải mái `nay`, `rung`.
7. Hiệu ứng chờ chỉ chạy trong PowerPoint (bản Windows/Mac 2016 trở lên). Ảnh kiểm tra không thể hiện; nhắc người dùng xem thử ở chế độ trình chiếu.

## Quy tắc dàn dựng
1. **Theo mạch nói**: thứ tự xuất hiện = thứ tự người trình bày nói. Tiêu đề không cần hiệu ứng (đã có chuyển trang), trừ slide bìa.
2. **Một slide ≤ 5 cú nhấp**; slide bìa và slide chia phần dùng `autoFirst: true` (tự chạy).
3. **Nhất quán theo loại slide**: cùng loại slide dùng cùng kiểu hiệu ứng (ví dụ mọi danh sách đều `wipe` từ trái, mọi số liệu đều `zoom`).
4. **Chuyển trang theo cấu trúc**: trong một phần dùng một kiểu (`push`), giữa các phần dùng kiểu khác (`fadeBlack` hoặc `split`). Không đổi chuyển trang ở mỗi slide.
5. **Morph** là điểm nhấn mạnh nhất: dùng cho 2–4 cặp slide mỗi bài (ví dụ vòng tròn ở slide tổng quan phóng lớn thành nền cho slide số liệu; ảnh nhỏ phóng thành ảnh tràn viền).
6. Bài **chính quy**: ưu tiên `fade`, `floatUp`, `wipe`, `zoom`, `push`, `fade`/`morph`; tránh `wheel`, `circle`. Bài **kiểu cách / học sinh**: dùng thoải mái cả danh mục.
7. Ghi thứ tự cú nhấp vào ghi chú diễn giả (ví dụ "[Nhấp 1] Ý thứ nhất…").

## Mẫu PLAN
```js
const PLAN = {
  1: { transition: "fadeBlack", autoFirst: true,
       steps: [[{ n: "title", eff: "zoom" }, { n: "sub", eff: "floatUp", start: "after" }]] },
  2: { transition: ["push", "u"],
       steps: [[{ n: "list", eff: "wipe", dir: "left", byPara: true }],
               [{ n: "!!circle", eff: "pulse" }]] },
  3: { transition: "morph",
       steps: [[{ n: "stat", eff: "zoom" }], [{ n: "lab", eff: "fly", dir: "right" }]] },
};
```

## Kiểm tra
Ảnh render bằng LibreOffice **không thể hiện hiệu ứng**. Kiểm tra bằng cách đọc lại XML: mỗi slide trong PLAN có `<p:timing>`/`<p:transition>`, số cú nhấp đúng dự kiến; chạy `validate.py` của skill pptx. Nhắc người dùng xem thử chế độ trình chiếu trong PowerPoint.
