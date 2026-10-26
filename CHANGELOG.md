# Lịch sử phiên bản

Mỗi phiên bản là một commit gắn tag `vMAJOR.MINOR.PATCH` (bản thử nghiệm: `-beta.N`); số phiên bản cũng nằm trong `.claude-plugin/plugin.json`.

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
