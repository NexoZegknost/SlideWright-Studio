# Lịch sử phiên bản

Mỗi phiên bản là một commit gắn tag `vMAJOR.MINOR.PATCH` (bản thử nghiệm: `-beta.N`); số phiên bản cũng nằm trong `.claude-plugin/plugin.json`.

## 2.0.0-beta.4
- [Gemini app] Cỡ chữ tính theo px của Canvas (khung 1280 × 720): bảng px theo bối cảnh, quy đổi px = pt × 1,78. Bản trước để Gemini dùng nguyên số pt làm px nên chữ chỉ còn 13,5–16 pt khi xuất PowerPoint.
- [Gemini app] Mục "Cấm tuyệt đối": đóng khung chữ (thẻ, hộp, viền, đổ bóng), biểu tượng, nhãn trên tiêu đề, chữ in hoa cả dòng, dấu "•" "·" "|" và gạch nối ý, số phút/thời lượng trên slide, slide nguồn ảnh, phông ngoài cặp của phương án; SKILL.md thắng khi `references/` gợi ý ngược lại.
- [Gemini app] 11 bố cục không khung (bìa chữ lớn, câu hỏi lớn, chia đôi màu, câu thơ lớn, chữ số lớn, từ khoá lớn, ảnh tràn nửa, dòng chảy, đối lập, bảng gọn, kết); bộ 10 slide dùng ≥ 6 bố cục, ≥ 1/3 slide có yếu tố thị giác lớn.
- [Gemini app] Thiết kế sẵn cho Morph (khối màu xuyên suốt đổi vị trí, kích thước giữa các slide); bàn giao kèm ghi chú diễn giả, bảng hiệu ứng từng slide và cách bật Morph, hiệu ứng trong PowerPoint.
- [Gemini app] Tự kiểm tra 10 mục, ghi kết quả từng mục trong câu trả lời trước khi đưa bộ slide.
- [Gemini app] `references/vi-du.md` đổi sang ví dụ *Trao duyên*: dàn ý 10 bố cục, slide mẫu tính bằng px, bảng hiệu ứng mẫu, bảng sai → đúng lấy từ lần thử Canvas.

## 2.0.0-beta.3
- [Gemini app] Gemini app từ chối nạp skill có kèm script ("contains executable code or scripts, which are not supported in Gemini Chat"), nên bản 2.0.0-beta.2 không chạy được. Hai gói nay chỉ còn SKILL.md, tài liệu quy tắc (.md) và dữ liệu (.json); bỏ `dung_slide.py` và các script kiểm tra.
- [Gemini app] make-slides viết lại cho công cụ tạo slide có sẵn của Gemini: mục "Bắt buộc" (báo phiên bản ở câu đầu, đọc tệp đi kèm trước khi làm, không dùng mẫu mặc định của công cụ), bảng ràng buộc trình bày (mã màu của phương án, cỡ chữ theo bối cảnh, 12 bố cục, ảnh và nguồn ảnh, những điều tránh), danh sách tự kiểm tra thay cho script, cách tải về PowerPoint.
- [Gemini app] presentation-script viết lại: kịch bản trả về trong hội thoại theo số slide để dán vào ghi chú; tự ước lượng thời gian theo âm tiết và tốc độ nói của bối cảnh.
- [Gemini app] Ví dụ mẫu (few-shot) `references/vi-du.md` cho cả hai skill: dàn ý, slide hoàn chỉnh (bố cục, phông, cỡ, mã màu, đếm chữ, ghi chú), bảng thời gian, lời nói mẫu, hỏi đáp mẫu và bảng lỗi sai → đúng rút từ lần thử đề tài STEM; mô tả skill ghi rõ đầu vào và đầu ra.
- [Gemini app] `tools/build_gemini_app.py` dừng với LỖI khi gói có tệp thực thi (.py, .js, .sh…), mô tả quá 1024 ký tự hoặc còn chỗ `{{…}}` chưa thay.

## 2.0.0-beta.2
- [Gemini app] Bản mới cho Gemini app: mỗi skill một tệp .zip đính kèm bản phát hành (`tools/build_gemini_app.py`). make-slides dựng .pptx + .ppsx bằng python-pptx (`gemini-app/make-slides/scripts/dung_slide.py`: 12 loại slide, cảnh Morph xuyên suốt, hiệu ứng mờ dần theo cú nhấp, ghi chú diễn giả, `**cụm nhấn**`, cảnh báo tràn chữ); bảng màu theo lĩnh vực tính sẵn (`assets/phuong-an.json`); phông có sẵn của Office.
- [Claude] [Gemini CLI] [Gemini app] presentation-script: đọc đúng tiêu đề slide — bỏ qua chữ của cảnh Morph (`!!…`) và số phần, ký hiệu ngắn (trước đây bộ slide có cảnh Morph bị nhận nhầm tiêu đề).
- [Gemini app] presentation-script tìm `contexts.json` trong chính skill khi đứng riêng.
- Phát hành: bản thử đính kèm đúng nhánh (`--target`); tệp `.plugin` không còn chứa phần riêng của Gemini app.

## 2.0.0-beta.1
- ci(release): publish pre-release tags from their own branch
- feat(gemini): add Gemini CLI extension with PowerPoint output

## 1.1.0
Thêm skill thứ hai: **presentationScript** (`presentation-script`) — viết kịch bản thuyết trình cho bộ slide.
- Đầu vào: bộ slide do makeSlides tạo, `.pptx` bất kỳ, PDF bài trình chiếu, Canva/Gamma hoặc chỉ dàn ý; dùng chung bối cảnh trong `make-slides/assets/contexts.json`.
- `scripts/doc_slide.py`: đọc bộ slide thành `slide.json` (tiêu đề, chữ, ghi chú cũ, số cú nhấp, slide ẩn, vai slide), đề xuất thời lượng từng slide theo tổng thời gian, dựng ảnh thu nhỏ.
- Lời nói theo mẫu `[Mở] / [Nhấp n] / [Nhấn] / [Chuyển]`, mỗi cú nhấp đúng một nhịp; hướng dẫn văn nói, xưng hô theo bối cảnh, nhịp toàn bài, tốc độ nói (`references/viet-loi-noi.md`); chuẩn bị hỏi đáp theo người nghe (`references/hoi-dap.md`).
- `scripts/kiem_tra_kich_ban.py`: ước thời lượng theo âm tiết, so với mục tiêu; bắt slide thiếu lời, số nhịp lệch số cú nhấp, đọc lại nguyên văn slide, câu quá dài, thiếu câu mở/chuyển, từ nhấn không khớp, cụm sáo rỗng, Markdown/emoji, số liệu thiếu nguồn; kiểm tra mã chữ và chính tả âm tiết bằng bộ kiểm tra của makeSlides.
- `scripts/dung_kich_ban.py`: ghi lời nói vào ghi chú diễn giả (tệp mới, giữ dòng nguồn ảnh cũ, xuất kèm `.ppsx`) và dựng bản in Word A4.
- `scripts/ban_in.py`: bố cục bản in chuyên nghiệp — bìa có khối thông số, bảng phân bổ thời gian có hàng tiêu đề màu và dòng tổng, thẻ lời nói từng slide (thanh đầu, ảnh thu nhỏ, nhãn mốc treo lề, ô lưu ý), hỏi đáp đánh số, thẻ nhắc có đường cắt, đầu trang và chân trang "Trang x / y".

## 1.0.0
Bản ổn định đầu tiên. Nhánh Canva được làm lại hoàn chỉnh: chỉ thiết kế trên Canva, bàn giao link, không xuất tệp.
- Viết lại `references/quy-trinh-canva.md`:
  - bảng việc làm được / không làm được qua công cụ Canva (không đổi phông, không đặt hiệu ứng qua công cụ);
  - cách viết bản yêu cầu và dàn ý để Canva không bỏ qua màu, không chép nhãn nội bộ, không tự thêm nội dung;
  - đọc thiết kế có cấu trúc (tránh báo nhầm dính chữ), lấy ảnh trang thật mà không làm đổi khung chữ, bảng quy đổi px ↔ pt;
  - quy tắc sửa đối tượng (lề, căn chân chữ, khung chữ, vạch trang trí, ảnh), văn bản (cỡ, lượng chữ, độ đục, màu, viết hoa, ghi chú diễn giả) và phông;
  - nhánh Canva chỉ thiết kế tĩnh: công cụ Canva không đặt được hiệu ứng, cần hiệu ứng thì làm bản PowerPoint;
  - lưu một lần sau khi người dùng đồng ý; bàn giao link chỉnh sửa.
- Thêm `scripts/kiem_tra_canva.py`: kiểm tra thiết kế Canva từ dữ liệu `read-design` — cỡ chữ quy ra pt, lượng chữ, chữ đè chữ, khối chữ quá sát, khung hẹp hơn chữ, hộp ghép một dòng lệch chân chữ, lề lệch, chữ sát mép, chữ mờ/xoay, màu ngoài bảng màu và cặp màu đối nhau, nhãn nội bộ và câu tự thêm so với dàn ý, chính tả/dấu câu/viết hoa theo từng hộp chữ; mỗi mục kèm `locator_id` và giá trị gợi ý.
- SKILL.md: Canva bàn giao link chỉnh sửa (không hiệu ứng, không xuất tệp); Bước 7 kiểm tra Canva bằng script mới.
- Bổ sung sau lần thử bộ slide tiếng Nhật (màu hồng pastel):
  - phát hiện phông dùng chung cho chữ Nhật/Trung và chữ Việt (mất dấu tiếng Việt, chữ Hán ra ô vuông) và quy trình tạo lại hộp chữ để khôi phục dấu;
  - bắt chữ sai dấu so với dàn ý ("tiêng" → "tiếng", "nãm" → "năm");
  - cảnh báo dòng có thể ngắt thêm khi tăng cỡ chữ mà không nới khung; chữ trang trí (mờ, xoay) không bị tính lỗi cỡ chữ mà nhắc kiểm tra chính tả và tên sách/thương hiệu thật;
  - bản yêu cầu cho bài có chữ nước ngoài: chữ Việt phải dùng phông đủ dấu;
  - phông chữ Nhật chỉ có một phần dấu tiếng Việt làm chữ to nhỏ lệch ("ế" to hơn): tạo lại toàn bộ hộp chữ Việt dùng phông đó, không chờ ảnh.
- Thêm mô tả cho marketplace; sơ đồ quy trình ghi đúng nhánh Canva chỉ bàn giao link chỉnh sửa.

## 0.15.1
- Thêm `displayName` (SlideWright - Studio) và `icon` (assets/branding/logo.png) vào `plugin.json`, để plugin cài từ marketplace hiện đúng tên và logo.

## 0.15.0
- Thêm module kiểm soát văn bản toàn diện `scripts/kiem_soat_van_ban.py` (tài liệu: `references/kiem-soat-van-ban.md`), gồm bảy nhóm:
  - **phông**: phông bị loại hoặc mã cũ, phông chưa nhúng, phông thiếu ký tự (đọc bảng mã), đậm/nghiêng giả, quá 3 họ phông, phông trang trí sai chỗ hoặc trong bài chính quy, phông ngoài cặp phông của phong cách;
  - **mã chữ**: Unicode tổ hợp (NFD), ký tự ẩn, ký tự hỏng, chữ TCVN3, Ð thay Đ, ký hiệu văn bản thiếu Đ;
  - **chính tả**: phân tích âm tiết tiếng Việt (vần không hợp lệ, dấu sai vị trí, vần tắc sai dấu, luật c/k – g/gh – ng/ngh), lẫn kiểu bỏ dấu cũ/mới, lặp hư từ, Markdown/LaTeX hoặc chữ giữ chỗ còn sót;
  - **dấu câu, viết hoa**: khoảng trắng, ngoặc lệch cặp, gạch đầu dòng gõ tay, tiêu đề có dấu chấm, chữ HOA toàn bộ, Viết Hoa Mỗi Chữ, tên cơ quan viết hoa sai hoặc chỉ có dạng viết tắt;
  - **hiển thị**: Tự co chữ, chữ < 12pt, chữ ra ngoài slide, chữ không xuống dòng tràn khung, chữ xoay/dọc/WordArt, hiệu ứng chữ, gạch chân, liên kết hỏng, mã ngôn ngữ vi-VN, chữ biểu đồ/bảng nhỏ, ghi chú diễn giả;
  - **dựng thử** (`--hien-thi`): dựng bằng LibreOffice, đọc phông thật của từng đoạn chữ để phát hiện phông bị thay và chữ rơi sang phông dự phòng.
- `--day-du` gộp `kiem_tra_van_ban.py` và `kiem_tra_slide.py` vào một báo cáo; `--sua` tự sửa phần không đổi câu chữ (NFC, ký tự ẩn, khoảng trắng, phông bị loại, vi-VN), đi cùng `--day-du` thì chạy luôn phần tự sửa cỡ chữ và xuống dòng.
- Thêm `assets/fonts/phan-loai.json` (phân loại họ phông và giới hạn dùng phông trang trí).
- Bước 7 của quy trình chạy module này đầu tiên; nhánh nâng cấp dùng nó để chẩn đoán lỗi chữ của bài gốc.

## 0.14.3
- Thêm quy trình phát hành tự động bằng GitHub Actions (`.github/workflows/release.yml`): đẩy commit có tiêu đề bắt đầu bằng `chore(release):` thì tự tạo tag `vX.Y.Z`, đóng gói tệp `.plugin` và đăng bản phát hành lên mục Releases, ghi chú lấy từ mục tương ứng trong CHANGELOG.
- Số phiên bản có hậu tố (ví dụ `-beta.1`) tự được đánh dấu là bản thử nghiệm.

## 0.14.2
- Rút gọn README, chỉ giữ tính năng, cài đặt, yêu cầu, cách dùng và các lưu ý chính.

## 0.14.1
- Bộ nhận diện SlideWright - Studio trong `assets/branding/`: logo nền sáng và nền tối (SVG, PNG 512 px và 128 px), ảnh xem trước kho GitHub 1280×640.
- README hiển thị logo theo chế độ sáng/tối của GitHub; manifest plugin bổ sung `homepage` và `repository`.

## 0.14.0
Bản ổn định, gộp các bản thử nghiệm 0.14.0-beta.1 → beta.3:
- Gói plugin đổi tên thành **SlideWright - Studio** (`slidewright-studio`); skill bên trong vẫn là **makeSlides** (`make-slides`). Người dùng bản cũ cần gỡ `make-slides` rồi cài `slidewright-studio`.
- Sửa lỗi hiệu ứng không hiện khi trình chiếu (After Previous bị kẹt sau hiệu ứng chờ lặp vô hạn).
- Bộ chuyển trang lấy Morph làm chủ đạo: cảnh morph (vầng tròn trôi, băng màu, mảnh hình, từ khoá nền, thanh tiến độ), morph kể chuyện (ảnh thành biểu tượng, số chia phần thành huy hiệu), chuyển trang lướt hiện đại; bỏ kiểu cổ điển.
- Tự kiểm tra hiệu ứng theo cách PowerPoint chạy (`kiem_tra_hieu_ung.py`) và xem trước Morph bằng ảnh động (`xem_truoc_morph.py`).
- Hoàn thiện quy trình: bước dựng file trước tự kiểm tra, thứ tự chạy script kiểm tra, vai slide và cảnh morph trong dàn ý.

## 0.14.0-beta.3
- Đổi tên gói plugin thành **SlideWright - Studio** (tên kỹ thuật `slidewright-studio`, trước đây `make-slides`) ở manifest, marketplace và README. Skill bên trong giữ nguyên tên **makeSlides** (`make-slides`), cách gọi và script không đổi.
- **Cần cài lại**: gỡ plugin `make-slides` cũ rồi cài `slidewright-studio`; lệnh cài mới: `/plugin install slidewright-studio@slidewright-studio`.

## 0.14.0-beta.2
- Quy trình: thêm bước dựng file trước tự kiểm tra, thứ tự chạy các script kiểm tra, vai slide và cảnh morph trong dàn ý, xem trước Morph khi gửi bản duyệt, lời nhắc khi bàn giao.
- Cảnh morph theo mức hiệu ứng của bối cảnh; bổ sung phụ thuộc Python cho các script kiểm tra.

## 0.14.0-beta.1
**Sửa lỗi**
- Một số thành phần không hiện khi trình chiếu (tiêu đề, phụ đề ở bìa; câu hỏi; chữ ở slide kết): PowerPoint chạy mục "After Previous" sau khi mục đứng trước kết thúc, mà hiệu ứng chờ lặp vô hạn không bao giờ kết thúc. Nhóm nhấp có hiệu ứng chờ nay được dựng thành danh sách With Previous với độ trễ tuyệt đối, hiệu ứng chờ luôn xếp cuối.
- Bố cục dòng thời gian chỉ gắn hiệu ứng chờ cho mốc mới nhất (≤ 2 đối tượng chờ mỗi slide).

**Bộ chuyển trang mới**
- `chuyen_trang.js`: Morph là chủ đạo (theo đối tượng, theo từ, theo ký tự) cùng các chuyển trang lướt hiện đại (pan, push, cover, pull, wipe, reveal, fadeBlack, fade, zoom), có nhánh dự phòng cho PowerPoint cũ; bỏ các kiểu cổ điển.
- Cảnh morph: `quyDao` (vầng tròn trôi), `daiLua` (băng màu xoay, kéo dãn), `manhHinh` (mảnh hình bay xoay), `chuNen` (từ khoá khổng lồ trượt kiểu parallax), `tienDo` (thanh tiến độ); đặt tư thế theo vai slide.
- Morph kể chuyện: ảnh thu thành biểu tượng (`CT.anh`), số chia phần thành huy hiệu (`soMorph` + `CT.soPhan`).
- Gợi ý chuyển trang và cảnh morph theo lĩnh vực trong `linh-vuc.json`.

**Tự kiểm tra**
- `kiem_tra_hieu_ung.py`: mô phỏng cách PowerPoint chạy danh sách hiệu ứng, báo đối tượng không bao giờ hiện, thời điểm lệch, số cú nhấp, đối tượng chờ; kiểm Morph (đối tượng chung, chuyển động, xung đột với hiệu ứng mở đầu) và chuyển trang cổ điển.
- `xem_truoc_morph.py`: ảnh động và bảng khung cho từng chuyển trang Morph.
- `kiem_tra_bo_cuc.py` bỏ qua khối trang trí của cảnh morph (kể cả hình xoay).

**Bài mẫu** `assets/mau-hieu-ung/` dùng cảnh morph vầng sáng, chữ nền "ánh đèn", thanh tiến độ, đèn rọi thu về góc và chiếc áo thu thành biểu tượng.

## 0.13.0
- Thêm `scripts/hieu_ung.js`: hiệu ứng 4 nhóm (mở đầu, nhấn mạnh, chờ, kết thúc), nền động, đèn quét, hạt sáng; dựng timing theo đúng chuẩn PowerPoint.
- Thêm `scripts/kiem_tra_bo_cuc.py`: kiểm tra chữ và vật thể lệch khung trên bản dàn trang thật.
- Thêm `scripts/do_chu.js`: đo chữ bằng phông thật để bố cục tự tính khung vừa nội dung.
- Sửa nhiều bố cục (chia phần, so sánh, ba thẻ, thang số, hỏi đáp, số lớn, ảnh lớp khối); sửa xuống dòng trong câu có chữ nhấn màu.
- Bài mẫu `assets/mau-hieu-ung/` (Hiệu ứng ánh đèn sân khấu); viết lại `references/hieu-ung.md`.

## 0.12.0
- Phiên bản gốc lưu vào kho (xem commit `v0.12.0`).
