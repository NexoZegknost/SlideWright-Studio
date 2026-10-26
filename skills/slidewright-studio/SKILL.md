---
name: slidewright-studio
description: Bộ công cụ trình chiếu tổng hợp duy nhất — tạo mới bài thuyết trình ấn tượng (bài giảng, báo cáo hội nghị, kế hoạch, tập huấn, lễ kỷ niệm, sự kiện…) từ chủ đề, dàn ý, văn bản hoặc tài liệu đính kèm (PDF, Word, ảnh, link); nâng cấp/thiết kế lại bài trình chiếu có sẵn (.pptx, Gamma, Canva); chuyển PDF bài trình chiếu thành PowerPoint giữ nguyên bản gốc (hình nền, phông, cỡ, màu chữ, hình ảnh) kèm hiệu ứng. Đầu ra PowerPoint (.pptx + .ppsx, hiệu ứng, Morph, phông tiếng Việt nhúng sẵn), Gamma hoặc Canva. LUÔN dùng skill này khi người dùng nhắc "SlideWright", "SlideWright - Studio", "makeSlides" (tên cũ), "tạo slide", "làm bài thuyết trình", "làm powerpoint", "slide báo cáo", "slide bài giảng", "trình chiếu", "slide-pptx", "slide-gamma", "slide-canva", "nâng cấp slide", "làm đẹp slide", "thiết kế lại slide", "chuyển PDF sang PowerPoint", "chuyển file này thành slide", hoặc muốn biến báo cáo/kế hoạch/dự thảo thành slide — kể cả khi không nói từ "skill".
---

# SlideWright - Studio — Bộ công cụ trình chiếu tổng hợp

Mục tiêu: bộ slide **có thông điệp rõ, bố cục đa dạng, màu có chủ đích, chữ ít mà đắt, hiệu ứng theo mạch nói**, dùng được ngay. Viết **tiếng Việt chuẩn, đủ dấu**, văn phong hợp bối cảnh. Đường dẫn `references/`, `scripts/`, `assets/` tính từ thư mục skill này (`${CLAUDE_PLUGIN_ROOT}/skills/slidewright-studio/`; không có biến thì `find / -path "*slidewright-studio/scripts/makeslides.js" 2>/dev/null | head -1`).

Tạo danh sách công việc (task list) theo các bước để người dùng theo dõi.

## Bước 0 — Chọn nhánh và công cụ
| Nhánh | Khi nào | Làm theo |
|---|---|---|
| **A. Tạo mới** | Có chủ đề, dàn ý, văn bản, tài liệu | Bước 1–10 dưới đây |
| **B. Nâng cấp** | Gửi .pptx / link Gamma / thiết kế Canva, muốn đẹp hơn, giữ nội dung | `references/nang-cap.md` + Bước 1, 6–10 |
| **C. Chuyển đổi nguyên bản** | Gửi PDF bài trình chiếu, muốn PowerPoint **giữ nguyên** hình nền, phông, cỡ, màu, bố cục, hình | `references/chuyen-doi-pdf.md` (script `scripts/pdf_sang_pptx.py`); bỏ qua chọn phong cách |
| **A + văn bản hành chính** | Nguồn là báo cáo, kế hoạch, dự thảo, hướng dẫn | Bước 1–10 + `references/van-ban-hanh-chinh.md` |

Công cụ đầu ra — đã nêu (gõ "slide-pptx", "bằng Canva", "trên Gamma", "/slide-canva"…) thì không hỏi lại:
| Công cụ | Tài liệu kỹ thuật | Bàn giao |
|---|---|---|
| PowerPoint (mặc định) | `references/quy-trinh-pptx.md` + skill `pptx` (nếu có) + `scripts/makeslides.js` | .pptx + .ppsx |
| Canva | `references/quy-trinh-canva.md` | link Canva + link tải PPTX/PDF |
| Gamma | `references/quy-trinh-gamma.md` | link Gamma + link tải |
Gamma/Canva chưa kết nối → báo một câu, gợi ý kết nối, đề nghị bản PowerPoint thay thế.

Người dùng gọi nhiều lệnh cùng lúc (ví dụ cả "slide-canva" và "nâng cấp" cho tài liệu mới) → chọn nhánh theo **đầu vào** (tài liệu mới = A, bài có sẵn = B) và công cụ theo lệnh công cụ đã gọi.

## Hai điểm duyệt và chế độ "làm luôn"
Quy trình có hai điểm người dùng duyệt (dàn ý ở Bước 4, bản hoàn chỉnh ở Bước 9). **Bỏ qua cả hai** khi người dùng nói "xuất file hoàn chỉnh", "làm luôn", vắng mặt, hoặc gửi kèm nhiều tài liệu và yêu cầu kết quả cuối; khi đó tự chọn phương án đề xuất và ghi rõ ở đầu phần bàn giao những gì đã tự quyết. Riêng **chọn phong cách** khi thiết kế lại (nhánh B) vẫn hỏi một lần nếu người dùng đang có mặt, vì "đẹp, ấn tượng" là lựa chọn chủ quan.

## Bước 1 — Đề tài, bối cảnh, phong cách
1. **Đề tài** (bắt buộc) từ lời người dùng và tài liệu. Chỉ hỏi khi không có.
2. **Bối cảnh** theo `references/boi-canh.md` (10 bối cảnh); thông số (cỡ chữ tối thiểu, mật độ, nhịp, mức hiệu ứng, slide bắt buộc, đầu ra kèm) ở `assets/contexts.json`; số slide = thời lượng ÷ nhịp. **Bối cảnh thắng mặc định của phong cách.** Người dùng dặn "hiệu ứng đơn giản, phù hợp văn bản khoa học" → hạ mức hiệu ứng xuống *tiết chế* bất kể bối cảnh.
3. **Phong cách** (người dùng chọn) — dùng **module định hướng** `references/dinh-huong-thiet-ke.md`:
   `node scripts/dinh_huong.js --chu-de "<đề tài>" --mo-ta "<tóm tắt>" --boi-canh <bối cảnh> [--thuong-hieu <ten> nếu được yêu cầu] --phu-de "<phụ đề>" --xem-truoc xem-truoc.png`
   Module nhận diện lĩnh vực và dựng 3 phương án hoàn chỉnh (màu theo `references/phoi-mau.md` — không phối màu đối nhau như lam–cam, đỏ–lục; phông; texture; bố cục ưu tiên; cách trình bày). Kiểm tra lĩnh vực nhận diện có đúng không (đề tài lai → ép `--linh-vuc`), xem ảnh xem trước, gửi ảnh và hỏi bằng AskUserQuestion (đề xuất đặt đầu, ghi "(Đề xuất)", mỗi phương án một câu lý do); gộp mọi câu còn thiếu (bối cảnh, công cụ, giữ nhận diện cũ…) vào cùng lượt, tối đa 4 câu. Khi dựng: `S = DH.apDung(pa)`, texture `DH.taoTexture(pa, dir)` đưa vào bố cục qua `c.nen`. Muốn dùng nguyên phong cách có sẵn: `references/phong-cach.md` + `assets/styles.json` (ảnh xem trước bằng `scripts/xem_truoc_phong_cach.py`).
   - **Tài nguyên thương hiệu** (`references/thuong-hieu.md`, hiện có `bk-hcmut` — Trường ĐH Bách khoa ĐHQG-HCM): **chỉ dùng khi người dùng yêu cầu** (ví dụ "báo cáo ở Bách khoa", "dùng logo/tài nguyên BK"). Không tự dùng vì đề tài, trường của người trình bày hay nơi trình bày; không hỏi gợi ý. Khi được yêu cầu: truyền `--thuong-hieu bk-hcmut` cho module — màu thương hiệu làm chủ đạo, màu nhấn và texture theo lĩnh vực, logo đúng phiên bản theo nền.
   - **Nhiều bộ slide cho cùng một sự kiện** → dùng lại phong cách người dùng đã chọn cho bộ trước, không hỏi lại; nói rõ một câu.
   - Người dùng gửi **ảnh banner/bìa sự kiện** → dùng nguyên ảnh làm slide 1 (slide chờ), hỏi có lấy màu/họa tiết của banner cho cả bài không.

## Bước 2 — Nội dung
- **Người dùng tải nội dung lên**: đọc toàn bộ (docx → `markitdown`, cài `markitdown[docx]` nếu thiếu; PDF dài đọc theo trang); giữ chính xác số liệu, tên riêng, địa danh, số hiệu văn bản, trích dẫn. Với dự thảo/văn bản hành chính, ghi lại lỗi phát hiện được để báo cuối (xem `van-ban-hanh-chinh.md`).
- **Tự tìm nội dung** (chỉ có chủ đề): WebSearch/WebFetch, ưu tiên nguồn chính thống; ghi nguồn vào ghi chú diễn giả và slide "Tài liệu tham khảo".
- **Cả hai**: tài liệu làm xương sống, phần bổ sung đánh dấu rõ khi trình dàn ý.
- Không bịa số liệu, văn bản pháp quy, trích dẫn; thiếu thì để `[cần bổ sung]` và báo.

## Bước 3 — Dàn ý thông điệp
Đọc `references/noi-dung-slide.md` (slide chỉ giữ nội dung khái quát: từ khoá, con số, sơ đồ; 1–3 điểm nhấn; chi tiết vào ghi chú) và `references/dan-y-mau.md` (khung theo bối cảnh; văn bản hành chính dùng khung trong `van-ban-hanh-chinh.md`). Mỗi slide = một thông điệp, tiêu đề ≤ 12 từ. Ghi cho từng slide: tiêu đề · ý chính · bố cục · **vai** (bìa, nội dung, nhấn mạnh, chia phần, kết — quyết định tư thế cảnh morph) · hình ảnh · hiệu ứng.

## Bước 4 — Duyệt dàn ý ⟲
Gửi bảng `STT | Tiêu đề | Ý chính | Bố cục | Hình ảnh`, một dòng phong cách (tên + cặp phông + màu chủ đạo), một dòng bối cảnh (tên + số slide + nhịp + mức hiệu ứng), một dòng chuyển trang (cảnh morph đã chọn + 1–2 khoảnh khắc morph kể chuyện). Chờ xác nhận, trừ chế độ "làm luôn".

## Bước 5 — Material
- **Ảnh**: Unsplash (nếu kết nối) đúng ngữ cảnh, ưu tiên Việt Nam, ≥ 1600px cho ảnh tràn viền, ghi tác giả vào ghi chú; Canva/Gamma có thể tự tạo ảnh minh hoạ. Không lấy được ảnh (công cụ ảnh lỗi, mạng chặn) → **vẽ tranh minh hoạ phẳng bằng SVG** theo bảng màu của bài rồi xuất PNG bằng sharp (mẫu: `assets/mau-hieu-ung/illus.js` — sân khấu, chiếc áo, khán giả), không để khối giữ chỗ trống.
- **Không dùng biểu tượng/emoji trước đoạn văn, tiêu đề thẻ, gạch đầu dòng** (dấu hiệu slide AI). Điểm nhìn là chữ đậm, con số, ảnh thật, sơ đồ thật. Biểu tượng chỉ được dùng như một hình minh hoạ độc lập cỡ lớn khi không có ảnh/sơ đồ thay thế.
- **Công thức**: viết sẵn LaTeX cho mọi công thức để dựng bằng khối Equation (`MS.equation`, bố cục `congThuc`).
- **Biểu đồ**: biểu đồ gốc PowerPoint từ số liệu thật.
- **Họa tiết tự vẽ**: `scripts/hoa_tiet_trong_dong.py --color <hex>` (vòng đồng tâm kiểu trống đồng cho phong cách Truyền thống/hội nghị địa phương).
- Không dùng nhân vật có bản quyền, logo thương hiệu không thuộc người dùng, ảnh người thật không rõ nguồn.

## Bước 6 — Thiết kế (theo thứ tự)
1. **Viết nội dung slide** theo `noi-dung-slide.md`, rút gọn theo mật độ của bối cảnh; ghi chú diễn giả 3–5 câu/slide có thứ tự cú nhấp ("[Nhấp 1] …").
2. **Layout**: thư viện 32 bố cục ở `references/bo-cuc.md` (`scripts/layouts.js`, gọi `setScale(body_min)`), ưu tiên bố cục mở rộng 23–31 (bất đối xứng, thứ bậc chữ, chú thích hình) để bài không giống mẫu tải sẵn; mỗi bài ≥ 2 slide dựng riêng cho nội dung đặc thù — thiếu bố cục hợp thì tìm mẫu theo `references/mau-bo-cuc.md` (người dùng gửi mẫu → học cấu trúc theo mục 3 của tệp đó). Bổ sung theo `references/nguyen-tac-thiet-ke.md` — một màu chủ đạo, một motif xuyên suốt, không lặp bố cục quá 2 slide liên tiếp. Phông theo `references/phong-chu.md`: **bài chính quy chỉ dùng serif/sans-serif**; phông trang trí chỉ cho bài kiểu cách; **không dùng Be Vietnam Pro**.
   - **Màu**: chữ trên nền đậm dùng trắng/ngà hoặc `accentOnDark` (≥ 7:1); không chữ tím/tím oải hương trên nền tối, không chữ cùng tông nền đậm, không màu đối nhau. Nền tối ≤ một nửa số slide.
   - **Texture**: dùng tích cực theo bộ texture của phương án (`DH.taoTexture`): bìa, chia phần, nhấn mạnh nhiều lớp; slide nội dung luân phiên 2–3 biến thể nhẹ (`DH.nen(tex, "noi-dung", k)`), xen slide trơn để thở. Cùng bảng màu, độ dày nét, mật độ → nhiều mẫu nhưng chung phong cách. Có thể sáng tạo bộ mới bằng `scripts/hoa_tiet.py --lop` cho hoàn cảnh cụ thể (ảnh nền sự kiện, chủ đề đặc thù).
   - **Chữ**: viết theo mục 4 `references/noi-dung-slide.md` — ≥ 24pt, ≤ 30 chữ/slide, tiêu đề là thông điệp (không đếm số kiểu "Ba con số đáng chú ý"), tiêu đề 2 dòng thì dòng trên ngắn hơn.
   - **Công thức**: luôn là khối Equation (`MS.equation` / `congThuc`), không gõ bằng chữ, không để trong ô bảng.
   - **Tránh dấu hiệu AI** khi viết và dàn trang theo `references/dau-hieu-ai.md` (biểu tượng trước chữ, thẻ bằng nhau, "VS", nhãn "Điểm chính", tiêu đề chung chung, gạch ngang nối ý, từ sáo rỗng, lời kết sáo).
Mục 3–5 dưới đây chỉ áp dụng cho PowerPoint; Canva/Gamma tự xử lý hiệu ứng (xem tài liệu quy trình tương ứng).
3. **Animation** theo `references/hieu-ung.md` (thư viện `scripts/hieu_ung.js`), đủ bốn nhóm theo mức của bối cảnh:
   - *mở đầu*: thứ tự xuất hiện = thứ tự nói, ≤ 5 cú nhấp/slide; bìa và câu hỏi lớn dùng chữ nổi theo từ (`riseWords`);
   - *nhấn mạnh*: `dim` bước đã nói khi bước mới hiện, `pulse`/`grow`/`fontColor` cho con số, từ khoá;
   - *kết thúc*: thay nội dung tại chỗ, dọn sân khấu (`ket`), hạ màn slide cuối.
4. **Hiệu ứng chờ** (tự phát, nhỏ, lặp): nền động ở bìa/chia phần/câu hỏi/kết (`nenDong` trôi, đèn quét `denSanKhau`, hạt sáng `hatBui`, vòng xoay chậm) + ≤ 2 điểm nhấn nội dung/slide (`chuNoi`, `songChu`, `nhip`, `gachChan`…), chu kỳ nền 15–30 s, nội dung 6–15 s.
5. **Transition** theo `references/chuyen-trang.md` (`scripts/chuyen_trang.js`): **Morph cho mọi slide sau slide đầu** với một cảnh morph xuyên suốt (1–2 motif hợp lĩnh vực — `linh-vuc.json` → `canh_morph` — cộng thanh `tienDo`), vẽ trong `c.truoc` bằng `canh.dat(sl, vai, { i })`; thêm 2–3 khoảnh khắc morph kể chuyện (ảnh thu thành biểu tượng, số chia phần thành huy hiệu, ánh sáng di chuyển). Đổi phần lớn dùng `reveal`/`pan`; slide đầu `fadeBlack`. Không dùng chuyển trang cổ điển (lật 3D, cắt, hoà tan…). Mức của bối cảnh: tối thiểu/không hiệu ứng → chỉ `tienDo` hoặc không cảnh; trực tuyến → một motif, Morph ≤ 1400 ms.
6. **Dựng file**: chạy script dựng — `applyEffects` → `embedFonts` (mọi họ phông đã dùng) → `save` ra .pptx + .ppsx — rồi mới sang Bước 7. Mỗi lần sửa ở Bước 7 thì sửa trong script dựng và dựng lại, không sửa tay trên file.

## Bước 7 — Tự kiểm tra (bắt buộc)
Chạy theo thứ tự trên file vừa dựng: `kiem_tra_van_ban.py` → `kiem_tra_slide.py` → `kiem_tra_bo_cuc.py` → `kiem_tra_hieu_ung.py` → `xem_truoc_morph.py` → `validate.py` của skill pptx → render và xem ảnh. Có lỗi thì sửa script dựng, dựng lại và chạy lại từ đầu. Bản `_sua` do `kiem_tra_van_ban.py --sua` tạo chỉ để tham khảo cỡ chữ nên dùng; số liệu đó phải đưa ngược vào script dựng.
- [ ] **Chính tả** tiếng Việt, dấu thanh, viết hoa tên riêng, địa danh; chữ **Đ** trong ký hiệu văn bản (BGDĐT, SGDĐT) — đặc biệt với Canva/Gamma.
- [ ] **Xuống dòng**: không tách từ/cụm từ (số – đơn vị, ký hiệu – số, họ – tên), không mồ côi một từ ở dòng cuối tiêu đề/thẻ, không tràn khung.
- [ ] **Cỡ chữ và mật độ** đúng `contexts.json`; chú thích ≥ 12pt.
- [ ] **Script tự kiểm**: `python3 scripts/kiem_tra_slide.py <file>.pptx` → hết **LỖI**; xem và xử lý từng **CẢNH BÁO**:
  - *màu*: tương phản ≥ 4.5:1 (chữ lớn 3:1), không hai màu đối nhau (lam–cam, đỏ–lục, vàng–tím), không chữ cùng tông nền đậm, nhịp sáng – tối, ≤ 3 sắc màu chữ;
  - *dấu hiệu AI*: emoji/biểu tượng trước chữ, icon trong vòng tròn, "VS", nhãn khuôn mẫu, tiêu đề chung chung hoặc dạng "A: B" hàng loạt, từ sáo rỗng, gạch ngang nối ý, ba ý dài bằng nhau, bố cục lặp, lời kết sáo;
  - *công thức dạng chữ* → chuyển sang khối Equation.
- [ ] **Văn bản**: `python3 scripts/kiem_tra_van_ban.py <file>.pptx --sua <file>_sua.pptx` → hết **LỖI** (cỡ ≥ 24pt, ≤ 30 chữ/slide, giãn dòng, hài hoà cỡ, tràn khung, dòng mồ côi, tách từ ghép/hư từ cuối dòng, tiêu đề 2 dòng trên ngắn dưới dài, tiêu đề đếm số sáo rỗng) — quy tắc ở mục 4 `references/noi-dung-slide.md`. Phần không tự sửa được: rút gọn/kéo dài nội dung trong script dựng rồi dựng lại.
- [ ] **Hiệu ứng và chuyển trang**: `python3 scripts/kiem_tra_hieu_ung.py <file>.pptx` → hết **LỖI** (mô phỏng đúng cách PowerPoint chạy: không đối tượng nào bị kẹt không hiện; Morph có đối tượng chung và có chuyển động; không chuyển trang cổ điển). Xem `python3 scripts/xem_truoc_morph.py <file>.pptx --ra xem_morph` → mở `morph_tong.png`, kiểm khối trôi hài hoà, không đè chữ.
- [ ] **Bố cục (lệch khung)**: `python3 scripts/kiem_tra_bo_cuc.py <file>.pptx --anh kiem_tra` → hết **LỖI** và **CẢNH BÁO** (đo trên bản dàn trang thật: đường kẻ chạm chân chữ, chữ tràn/sát mép khối màu, chữ chồng chữ, chữ đè logo, chữ/vật thể ra ngoài slide, lệch lề nhỏ, khoảng trống bất thường, khối màu quá rộng so với chữ). Sửa ở bố cục (đo bằng `scripts/do_chu.js`), không dịch tay từng đối tượng.
- [ ] **Đọc lại bằng mắt** theo mục 4 của `references/dau-hieu-ai.md` (bỏ biểu tượng có mất gì không, đổi đề tài slide còn dùng được không).
- [ ] **Slide bắt buộc** của bối cảnh có đủ (slide chờ hội nghị, kiến nghị cho công sở…).
- [ ] **Độ tập trung**: một điểm nhìn chính, ≥ 1 yếu tố thị giác, khoảng trắng đủ, chân trang không bị che.
- [ ] **Nội dung**: số liệu khớp nguồn; đủ slide; có ghi chú diễn giả.
- [ ] **Hiệu ứng (đọc lại bằng mắt)**: đúng mạch nói, ghi chú diễn giả có thứ tự cú nhấp, hiệu ứng chờ đúng mức bối cảnh (nền ≤ 1 nhóm, nội dung ≤ 2 đối tượng).
- [ ] **Ảnh**: ảnh nội dung có mô tả (altText) và nguồn/tác giả trong ghi chú.
- [ ] **Phông**: đúng nguyên tắc; mọi họ phông đã nhúng (PowerPoint).
- [ ] PowerPoint: render từng slide (`installFontsForPreview` → soffice → pdftoppm), **xem từng ảnh**, ghép lưới để so; `validate.py` PASSED. Canva: đọc lại toàn bộ chữ bằng `read-design` và sửa lỗi theo `quy-trinh-canva.md`.
Sửa đến khi đạt.

## Bước 8–9 — Bản xem trước và người dùng kiểm tra ⟲
Gửi file/link kèm 1–2 câu và danh sách hiệu ứng chính; với PowerPoint gửi kèm ảnh lưới các slide và `morph_tong.png` (xem trước Morph), nhắc rằng hiệu ứng thật chỉ thấy khi trình chiếu. Cần sửa → quay lại Bước 6 (hoặc 3 nếu sửa nội dung lớn). Chế độ "làm luôn" → coi bản đã tự kiểm là bản cuối.

## Bước 10 — Xuất và bàn giao
- **PowerPoint**: bàn giao bản đã dựng ở Bước 6 và qua Bước 7 (**.pptx + .ppsx**); thêm PDF khi bối cảnh yêu cầu; chiếu tự động thêm `setLoop`. Tên `Slide_<ChuDeKhongDau>_<ddmmyyyy>`; bản nâng cấp thêm hậu tố `_nang_cap`, không ghi đè bản gốc.
- **Canva/Gamma**: link chỉnh sửa + link tải (ghi thời hạn), xem tài liệu tương ứng.
- Gửi file bằng SendUserFile. Nội dung bàn giao, ngắn gọn:
  - số slide, phong cách, cặp phông;
  - hiệu ứng chính;
  - những gì đã tự quyết;
  - giới hạn còn lại (ví dụ khung bảng nằm trong ảnh nền);
  - lỗi phát hiện trong tài liệu nguồn.
- Nhắc người dùng ba điều: hiệu ứng và Morph chỉ chạy ở chế độ trình chiếu PowerPoint (Morph cần 2019/365, bản cũ tự lùi về mờ dần; Google Slides/Keynote không chạy); khi sửa và lưu lại thì giữ tuỳ chọn *Embed fonts in the file*; muốn thêm slide thì giữ tên đối tượng `!!…` của cảnh morph.

## Những điều tránh
- Gạch chân/đường kẻ dưới tiêu đề; dải màu trang trí đứng yên chạy dọc/ngang mép slide (thanh tiến độ mảnh và băng màu của cảnh morph là ngoại lệ vì chúng chuyển động theo bài).
- Biểu tượng/emoji trước đoạn văn và tiêu đề thẻ; biểu tượng trong vòng tròn; vòng "VS".
- Chữ sáng cùng tông với nền đậm (chữ xanh nhạt trên nền xanh đậm); hai màu đối nhau trong cùng bài (lam–cam, đỏ–lục, vàng–tím).
- Dùng logo, màu, hoạ tiết của một đơn vị khi người dùng không yêu cầu.
- Công thức gõ bằng chữ thường hoặc đặt trong ô bảng.
- Phông Be Vietnam Pro.
- Căn giữa đoạn văn nội dung (chỉ căn giữa tiêu đề, bìa, slide số liệu).
- Phông trang trí trong bài chính quy; quá 3 họ phông.
- Hiệu ứng không theo mạch nói; đổi kiểu chuyển trang ở mọi slide; chuyển trang cổ điển; mục "After Previous" xếp sau hiệu ứng chờ lặp vô hạn (dùng `hieu_ung.js`, đừng sửa tay timing).
- Bịa trích dẫn, số liệu, văn bản pháp quy; tự sửa nội dung văn bản gốc của người dùng (chỉ báo lỗi).
