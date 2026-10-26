# Lịch sử phiên bản

Mỗi phiên bản là một commit gắn tag `vMAJOR.MINOR.PATCH` (bản thử nghiệm: `-beta.N`); số phiên bản cũng nằm trong `.claude-plugin/plugin.json`.

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
