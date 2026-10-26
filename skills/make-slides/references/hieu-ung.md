# Hiệu ứng (animation) và chuyển trang (transition)

Thư viện: `scripts/hieu_ung.js` (danh mục + dựng `<p:timing>`), gọi qua `scripts/makeslides.js` → `applyEffects(buf, PLAN)`. In danh mục: `node scripts/hieu_ung.js`. Mọi đối tượng cần hiệu ứng phải có `objectName` duy nhất trong slide.

Bốn nhóm hiệu ứng, đúng như bảng Animation của PowerPoint:

| Nhóm | Khi nào chạy | Vai trò |
|---|---|---|
| **Mở đầu** (Entrance) | khi nhấp, hoặc tự chạy lúc vào slide | đưa nội dung vào theo đúng thứ tự nói |
| **Nhấn mạnh** (Emphasis) | khi nhấp | làm nổi một thứ đã có trên slide: phóng, đổi màu, làm nhạt phần đã nói |
| **Chờ** (idle) | tự phát, lặp tới khi rời slide | chuyển động nhỏ giữ mắt người xem ở lại slide trong lúc người nói giảng |
| **Kết thúc** (Exit) | khi nhấp (`ket`) hoặc trong một cú nhấp | dọn sân khấu trước ý mới, thay nội dung tại chỗ, hạ màn slide cuối |

## 1. PLAN của một slide
```js
PLAN[n] = {
  transition: "fade" | ["push", "u"],          // chuyển trang (mục 6)
  autoFirst: true,                             // nhóm đầu tự chạy khi vào slide
  steps: [                                     // mỗi mảng = một cú nhấp; trong mảng: "with" chạy cùng, "after" chạy nối
    [{ n: "title", eff: "riseWords" }, { n: "sub", eff: "floatUp", start: "after" }],
    [{ n: "v0", eff: "zoom" }, { n: "v1", eff: "dim", mau: "9A6A6C", start: "with" }],
  ],
  idle: [                                      // hiệu ứng chờ
    { n: "den", eff: "quet", period: 18000 },  // nền: chạy ngay khi vào slide
    { n: "v0", eff: "nhip", period: 9000 },    // nội dung: chạy sau cú nhấp cuối
  ],
  ket: [{ n: "big", eff: "sinkOut" }, { n: "sub", eff: "fadeOut", start: "with" }],  // cú nhấp cuối: kết thúc
  advanceAfter: 8000,                          // (chiếu tự động) tự sang slide sau
};
```
Tuỳ chọn chung của một hiệu ứng: `dur` (ms), `delay` (ms), `start` (`"click"` mặc định cho phần tử đầu nhóm, `"with"`, `"after"`), `dir`, `byPara: true` (hộp chữ hiện từng đoạn, mỗi đoạn một cú nhấp), `para` (chỉ một đoạn), `theo: "chu"|"tu"` (chạy lần lượt từng chữ cái / từng từ), `khoang` (ms giữa các chữ), `mau` (màu), `ti` (% phóng).

Bố cục trong `layouts.js` trả sẵn `steps` và `idle` gợi ý; sửa lại `r.steps`, `r.idle`, thêm `r.ket` trước khi đưa vào PLAN khi cần.

## 2. Mở đầu (`steps[].eff`)
| Tên | Hiệu ứng | Hợp với |
|---|---|---|
| `appear` | Hiện ngay | đáp án, ký hiệu nhỏ |
| `fade` | Mờ dần hiện | ảnh, chú thích, mọi thứ cần nhẹ |
| `floatUp` / `floatDown` | Nổi lên / hạ xuống (mờ + trôi 0,1) | phụ đề, đoạn ngắn, thẻ — mặc định tốt nhất |
| `fly` (`dir`) | Bay vào | thẻ, cột so sánh, khối màu |
| `zoom` | Phóng từ tâm | con số lớn, tiêu đề bìa |
| `expand` | Nở nhẹ từ 80% | câu tuyên bố, ảnh — dịu hơn `zoom` |
| `wipe` (`dir`) | Lau | danh sách, trục thời gian, đường kẻ |
| `split` | Tách từ giữa | trích dẫn, khẩu hiệu |
| `wheel` | Bánh xe | vòng tròn số liệu |
| `typewriter` | Gõ chữ từng chữ cái | câu hỏi gợi mở, mật mã, lời thoại |
| `riseWords` | Chữ nổi lên từng từ | tiêu đề bìa, câu hỏi lớn (≤ 12 từ) |
| `riseLetters` | Chữ nổi lên từng chữ cái | tiêu đề rất ngắn (≤ 4 từ) |

`theo` dùng được với mọi hiệu ứng mở đầu trên hộp chữ (ví dụ `{ eff: "fade", theo: "tu", khoang: 80 }`).

## 3. Nhấn mạnh (`steps[].eff`, chạy khi nhấp)
| Tên | Hiệu ứng | Dùng khi |
|---|---|---|
| `pulse` (`ti`) | Phóng 110% rồi về | nhắc lại con số/kết luận đã hiện |
| `grow` (`ti`) | Phóng to và giữ | chọn một ô trong nhiều ô |
| `fontColor` (`mau`) | Đổi màu chữ và giữ | từ khoá được nhắc tới |
| `dim` (`mau`) | Làm nhạt chữ đã nói | danh sách/các bước: bước mới hiện thì bước trước nhạt đi (cùng cú nhấp, `start: "with"`) |
| `fillColor` (`mau`) | Đổi màu khối và giữ | ô được chọn trong ma trận, bản đồ |
| `teeter` | Lắc nhẹ hai bên | cảnh báo, chỗ sai |
| `spin` | Xoay một vòng | biểu tượng chu trình |
| `underline`, `bold` | Gạch chân / in đậm và giữ | từ khoá trong câu |

Màu `dim`: lấy màu nhạt cùng tông nền (nền sáng: muted pha nền; nền tối: màu nền sáng thêm 25–30%), không dùng xám lạnh trên nền ấm.

## 4. Chờ (`idle`) — tự phát, nhỏ, lặp
Hiệu ứng chờ không phải để trang trí: chúng giữ mắt người xem ở lại slide trong lúc người nói giảng, và kéo mắt về điểm nhấn. Phải **đủ rõ để thấy** nhưng **không giành lời người nói**: biên độ nhỏ, nhịp chậm, có khoảng nghỉ.

### 4a. Nền (mặc định chạy ngay khi vào slide, `batDau: "vao"`)
| Tên | Chuyển động | Đối tượng | Mặc định |
|---|---|---|---|
| `troi` | trôi chậm qua lại | texture/ảnh nền **lớn hơn khổ slide** (`c.nenDong` hoặc `HU.nenDong`) | chu kỳ 24 s, lệch ±0,3" |
| `quet` | đèn quét ngang qua lại | vầng sáng PNG (`HU.anhSang` + `HU.denSanKhau`) | 16 s, quét 2,4" |
| `bong` | bồng bềnh lên xuống | hạt sáng/bụi (`HU.hatBui`) | 6–11 s, lệch pha |
| `lapLanh` | hạt nhỏ loé to rồi về | hạt sáng | 5 s, loé 0,9 s |
| `tho` | phóng 103–106% rồi thu | vầng sáng, khối trang trí, ảnh minh hoạ | 9–16 s |
| `xoayCham` | xoay rất chậm | vòng nét đứt (`HU.vongXoay`), hoạ tiết tròn | 90 s/vòng |

### 4b. Nội dung (mặc định chạy sau cú nhấp cuối, `batDau: "sau"`; `batDau: k` = sau nhóm thứ k)
| Tên | Chuyển động | Hợp với | Mặc định |
|---|---|---|---|
| `chuNoi` | chữ nổi lên khẽ rồi lắng | câu hỏi, tiêu đề đang chờ trả lời | 6 s, động 1,4 s |
| `songChu` | sóng chữ: từng chữ cái nhấp nhô lần lượt | câu kết, khẩu hiệu ngắn (≤ 40 ký tự) | 7 s |
| `nhip` | phóng 105% rồi về | con số lớn, ô quan trọng | 8 s |
| `nay` | nảy hai nhịp | con số ngắn, bài cho học sinh | 9 s |
| `mo` | mờ thoáng rồi rõ | số khổng lồ trang trí | 8 s |
| `doiMau` (`mau`) | chớp sang màu nhấn rồi về | câu tuyên bố | 10 s |
| `gachChan`, `inDam`, `inNghieng` | thoáng gạch chân / đậm / nghiêng | từ khoá, thuật ngữ | 12 s |
| `rung` | lắc khẽ | huy hiệu thời gian | 12 s |
| `xoay` | xoay một vòng rồi nghỉ | biểu tượng nhỏ | 12 s |

Tuỳ chọn: `period` (chu kỳ), `dur` (phần động trong chu kỳ), `delay`, `bien` (biên độ, inch), `ti`, `dx`/`dy`, `mau`, `batDau`.

### 4c. Đối tượng nền động dựng sẵn (`const HU = require(".../hieu_ung.js")`)
```js
// texture trôi: chỉ cần thêm nenDong vào nội dung slide của bố cục
L.hoiDap(pres, S, { ..., nen: DH.nen(tex, "nhan-manh", 0), nenDong: { le: 0.35, period: 26000 } });
// đèn sân khấu + bụi sáng: vẽ trong c.truoc(sl) (nằm trên nền, dưới nội dung), trả về mảng idle
const den = await HU.anhSang("anh/den.png", { mau: S.c.accentOnDark, hinh: "chum", manh: 0.42 });   // hinh: tron | chum | dai
L.ketThuc(pres, S, { big: "…", truoc: (sl) => [
  HU.denSanKhau(sl, den, { x: 1.7, y: -0.15, w: 3.6, h: 4.4, dx: 2.9, period: 18000 }),
  ...HU.hatBui(sl, { so: 14, mau: S.c.accentOnDark, vung: { x: 2, y: 0.6, w: 6, h: 3.4 } }),
  HU.vongXoay(sl, { x: 7.2, y: 2.8, d: 2.6, mau: S.c.accent }),
] });
```
Tên đối tượng dựng sẵn (`nen`, `den`, `hat0…`, `vong`) được các script kiểm tra coi là lớp nền.

### 4d. Quy tắc hiệu ứng chờ
1. **Mỗi slide tối đa: 1 nhóm nền + 1–2 đối tượng nội dung.** Nhiều hạt sáng tính là một nhóm nền.
2. **Nền chậm, nội dung có nghỉ**: nền 15–30 s/chu kỳ, chuyển động liên tục nhưng biên độ nhỏ so với khổ slide; nội dung 6–15 s/chu kỳ, phần động ≤ 1/4 chu kỳ.
3. **Không làm khó đọc**: không cho chữ đang được đọc chuyển động liên tục; vầng sáng quét qua chữ phải đủ nhạt để chữ vẫn đạt tương phản; hạt sáng đặt tránh vùng đoạn văn.
4. **Nội dung chờ chỉ chạy khi đã hiện xong** (`batDau: "sau"` hoặc số nhóm) — không cho chữ nhấp nhô khi còn nội dung chưa hiện.
5. **Nhất quán**: cùng loại slide dùng cùng hiệu ứng chờ (mọi slide bìa/kết cùng đèn quét, mọi câu hỏi cùng `chuNoi`).
6. Theo bối cảnh:

| Mức hiệu ứng của bối cảnh | Nền | Nội dung |
|---|---|---|
| phong phú | bật (troi, quet, bong, lapLanh, tho, xoayCham) | 1–2 đối tượng, cả danh mục |
| vừa phải | troi, tho chậm | 1 đối tượng: `nhip`, `chuNoi`, `gachChan`, `doiMau` |
| tiết chế (công sở) | chỉ `troi` rất chậm ở bìa/kết | slide số liệu chính: `nhip` hoặc `gachChan`, chu kỳ ≥ 12 s |
| nhẹ (online) | tắt (chuyển động nền làm nén hình kém) | `doiMau`, `gachChan`, `inDam` |
| tối thiểu, không | tắt | tắt |
| tự động | bật nhẹ | `period` ≤ thời gian tự chuyển slide |

7. Phong cách chính quy: ưu tiên `troi`, `tho`, `nhip`, `gachChan`, `doiMau`, `chuNoi`; hạn chế `nay`, `xoay`, `songChu`. Phong cách sinh động, thiếu nhi: dùng thoải mái `nay`, `songChu`, `lapLanh`.

## 5. Kết thúc (`ket` hoặc trong `steps`)
| Tên | Hiệu ứng | Dùng khi |
|---|---|---|
| `fadeOut` | mờ dần rồi tắt | mặc định |
| `sinkOut` / `riseOut` | chìm xuống / bay hơi lên | câu kết, lời đáp đã xong |
| `flyOut` (`dir`) | bay ra | thẻ bị loại, phương án bị gạt |
| `zoomOut` | thu về tâm | vòng tròn, con số tạm |
| `wipeOut` (`dir`), `splitOut` | lau đi / khép lại | dải chữ, trích dẫn |
| `disappear` | biến mất ngay | thay đáp án tại chỗ |

Cách dùng: (1) **thay tại chỗ** — trong cùng cú nhấp, đối tượng cũ `fadeOut` + đối tượng mới `fade` `start: "with"`; (2) **dọn sân khấu** — `ket` ở slide có nhiều lớp trước khi sang ý mới; (3) **hạ màn** slide cuối: chữ `sinkOut`, vầng sáng `fadeOut` dài hơn (1,5 s). Đối tượng đã có hiệu ứng chờ vẫn được kết thúc bình thường.

## 6. Chuyển trang (`transition`)
| Tên | Dùng khi |
|---|---|
| `fadeBlack` | bìa, kết thúc, chuyển phần lớn |
| `fade` | mặc định an toàn |
| `push` (`u`/`d`/`l`/`r`) | đi tiếp trong cùng một phần |
| `wipe`, `cover` | dòng thời gian, slide chi tiết phủ lên tổng quan |
| `split`, `zoom`, `circle` | chia phần, đi sâu một ý, kết thúc (bài kiểu cách) |
| `morph` | hai slide liên tiếp chung đối tượng (cùng objectName bắt đầu `!!`); PowerPoint 2019/365, bản cũ tự lùi về Fade |

## 7. Mức hiệu ứng theo bối cảnh (`contexts.json` → `hieu_ung`)
| Mức | Bối cảnh | Cách làm |
|---|---|---|
| phong phú | học sinh/sinh viên, hội nghị, giảng dạy, hội thi | đủ bốn nhóm theo các quy tắc ở đây |
| vừa phải | tập huấn | ≤ 3 cú nhấp/slide; fade, floatUp, wipe, fly, zoom, dim; Morph có chọn lọc |
| tiết chế | công sở | ≤ 3 cú nhấp; fade, wipe (danh sách), zoom (số liệu chính); chuyển trang fade/push |
| nhẹ | online | fade, push, Morph đơn giản; dur ≤ 500; tránh wheel, split, chuỗi dài, hiệu ứng theo chữ cái |
| tối thiểu | bảo vệ đồ án | nội dung chính hiện sẵn; chỉ chuyển trang fade/push, Morph cho sơ đồ |
| không | gửi đọc trước | không hiệu ứng; chuyển trang fade hoặc không |
| tự động | chiếu tự động | mọi slide `autoFirst`, hiệu ứng `start: "after"`, `advanceAfter: 6000–10000`, `MS.setLoop(buf)` |

## 8. Quy tắc dàn dựng
1. **Theo mạch nói**: thứ tự xuất hiện = thứ tự nói. Tiêu đề slide nội dung không cần hiệu ứng (đã có chuyển trang), trừ bìa, câu hỏi, câu tuyên bố.
2. **≤ 5 cú nhấp/slide**; bìa, chia phần, câu hỏi dùng `autoFirst`.
3. **Nhất quán theo loại slide** (mọi danh sách `floatUp` theo đoạn, mọi số liệu `zoom`, mọi bước trước `dim`).
4. **Một khoảnh khắc lớn mỗi phần**: hiệu ứng theo chữ (`riseWords`, `songChu`) và đèn quét chỉ ở bìa, câu hỏi lớn, kết — dùng khắp nơi sẽ mất tác dụng.
5. Chuyển trang: một kiểu trong một phần, kiểu khác giữa các phần; Morph cho 2–4 cặp slide mỗi bài.
6. Ghi thứ tự cú nhấp vào ghi chú diễn giả ("[Nhấp 1] …").

## 9. Cấu trúc XML (để không bị PowerPoint báo "cần sửa chữa")
`hieu_ung.js` tự tuân thủ; khi sửa tay giữ đúng:
- `cTn` đánh số theo thứ tự tài liệu, gốc = 1, mainSeq = 2 (điều kiện tự chạy `<p:tn val="2"/>` trỏ vào đây).
- Mỗi hiệu ứng trên một hình có `grpId` riêng (0, 1, 2…); hiện theo đoạn dùng chung một `grpId`.
- `bldP` chỉ cho `p:sp` **có chữ thật**, mỗi cặp (spid, grpId) một lần (MS-OI29500, ghi chú về bldP); ảnh, hình trơn, bảng, biểu đồ không có `bldP`.
- "Sau hiệu ứng trước" mở một `<p:par>` con mới bắt đầu ở thời điểm kết thúc, như PowerPoint lưu.
- Hiệu ứng chờ: nút preset có `repeatCount="indefinite"` (lặp tới hết slide); khoảng nghỉ tạo bằng khung hình khoá hoặc hành vi đệm giữ nguyên vị trí.
- Chữ theo chữ cái/từ: `<p:iterate type="lt|wd">` đặt sau `stCondLst` của nút preset.

## 10. Kiểm tra
Ảnh render (LibreOffice) **không thể hiện hiệu ứng**. Kiểm tra: `validate.py` PASSED; đọc lại `<p:timing>` của vài slide (số cú nhấp, `delay="indefinite"` = một cú nhấp, `repeatCount="indefinite"` = hiệu ứng chờ, `presetClass="exit"` ở cú nhấp cuối); mọi tên trong PLAN tồn tại (applyEffects báo lỗi nếu thiếu). Nhắc người dùng xem ở chế độ trình chiếu PowerPoint 2016 trở lên (hiệu ứng chờ, Morph không chạy trên Google Slides/Keynote).

Mẫu minh hoạ đủ bốn nhóm: `assets/mau-hieu-ung/` (bài "Hiệu ứng ánh đèn sân khấu", script dựng kèm).
