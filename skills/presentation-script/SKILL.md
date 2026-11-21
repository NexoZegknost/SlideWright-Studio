---
name: presentation-script
description: Viết kịch bản thuyết trình tiếng Việt cho một bộ slide — lời nói đầy đủ từng slide khớp từng cú nhấp hiệu ứng, phân bổ thời gian theo tổng thời lượng và tốc độ nói, câu mở – câu chuyển – từ nhấn, chuẩn bị câu hỏi đáp dự kiến kèm gợi ý trả lời, thẻ nhắc. Đầu ra là bộ slide có ghi chú diễn giả (Presenter View) và bản in kịch bản Word. Dùng cho bộ slide do makeSlides tạo, .pptx bất kỳ, PDF bài trình chiếu, Canva/Gamma, hoặc chỉ có dàn ý. LUÔN dùng skill này khi người dùng nhắc "presentationScript", "kịch bản thuyết trình", "viết lời thuyết trình", "lời nói cho slide", "viết ghi chú diễn giả", "speaker notes", "lời dẫn cho từng slide", "tập thuyết trình", "chuẩn bị hỏi đáp", "câu hỏi hội đồng có thể hỏi", "thuyết trình trong 10/15/20 phút nói gì" — kể cả khi không nói từ "skill".
---

# presentationScript — Kịch bản thuyết trình

Mục tiêu: người trình bày cầm kịch bản là **nói được ngay, đúng giờ, khớp từng cú nhấp**, không đọc lại slide, không bị bất ngờ khi hỏi đáp. Viết **tiếng Việt chuẩn, đủ dấu, văn nói**. Đường dẫn `references/`, `scripts/` tính từ thư mục skill này (`${CLAUDE_PLUGIN_ROOT}/skills/presentation-script/`; không có biến thì `find / -path "*presentation-script/scripts/doc_slide.py" 2>/dev/null | head -1`). Bối cảnh và thông số dùng chung với skill `make-slides` (`../make-slides/assets/contexts.json`).

Tạo danh sách công việc (task list) theo các bước để người dùng theo dõi.

## Bước 0 — Đầu vào
| Có gì | Làm |
|---|---|
| `.pptx` (do makeSlides hoặc nguồn khác) | `doc_slide.py` đọc trực tiếp |
| PDF bài trình chiếu | đọc từng trang (skill pdf-reading), tự lập `slide.json` theo mục 1 `references/dinh-dang-kich-ban.md`, `so_nhap` = 0; chỉ xuất bản in Word |
| Canva / Gamma | Canva: `read-design` lấy chữ từng trang; Gamma: tải bản PPTX rồi như `.pptx`. Không ghi ngược ghi chú lên Canva/Gamma — xuất bản in Word, nhắc người dùng dán ghi chú nếu cần |
| Chỉ có dàn ý / chưa có slide | viết kịch bản theo dàn ý; đề nghị làm slide bằng makeSlides sau, hoặc trước nếu người dùng muốn khớp cú nhấp |
| Vừa dựng xong bằng makeSlides trong phiên | dùng luôn tệp .pptx đó và bối cảnh, thời lượng đã chốt; không hỏi lại |

Cần biết (hỏi gộp một lượt bằng AskUserQuestion, tối đa 4 câu, chỉ hỏi cái chưa có): **tổng thời lượng**, **bối cảnh / người nghe**, **người trình bày xưng hô thế nào** (vai, đơn vị), **thành phần khách mời** cần chào (hội nghị, lễ). Người dùng vắng mặt hoặc nói "làm luôn" → lấy `sec_per_slide` của bối cảnh, ghi rõ ở phần bàn giao những gì đã tự quyết.

## Bước 1 — Đọc bộ slide
```
python3 scripts/doc_slide.py bai.pptx --ra slide.json --phut <phút> --boi-canh <khoá> --anh anh_slide
```
In bảng: vai slide, số cú nhấp, thời lượng đề xuất. Đọc kỹ `chu` và `ghi_chu` cũ từng slide (ghi chú của makeSlides đã có ý chi tiết, nguồn, thứ tự cú nhấp — dùng làm xương sống). Đọc thêm tài liệu nguồn người dùng gửi để có ví dụ, số liệu; không bịa.

## Bước 2 — Khung bài nói
Theo mục 3 `references/viet-loi-noi.md`: chốt câu mở bài (lời hứa của bài), thông điệp chốt cuối mỗi phần, lời kết + kiến nghị. Phân bổ thời gian: dùng `giay_de_xuat`, chỉnh theo trọng tâm (slide kết luận, kiến nghị được thêm giờ; slide minh hoạ bớt). Tổng phải bằng thời lượng mục tiêu.

## Bước 3 — Viết lời nói từng slide
Viết `kich_ban.json` theo mục 2 `references/dinh-dang-kich-ban.md` và toàn bộ `references/viet-loi-noi.md`:
- `[Mở]` 1 câu → `nhip` **đúng bằng số cú nhấp** → `[Nhấn]` 1–3 từ khoá có trên slide → `[Chuyển]` 1 câu mang nội dung.
- Lượng chữ mỗi slide ≈ `giay × toc_do ÷ 60` âm tiết (trừ hao cú nhấp và `[Dừng]`).
- Văn nói: câu ≤ 25 âm tiết, số liệu nói được, không đọc lại câu trên slide, xưng hô đúng bối cảnh, không cụm sáo rỗng.
- Giữ chính xác số liệu, tên riêng, số hiệu văn bản; thiếu thì `[cần bổ sung]`.

## Bước 4 — Hỏi đáp dự kiến
Theo `references/hoi-dap.md`: 5–10 câu (bảo vệ, thi: 8–12), trả lời trước – giải thích sau, 30–60 giây mỗi câu, ghi nguồn và slide dự phòng. Câu cần slide phụ lục mà bộ slide chưa có → ghi vào phần bàn giao, đề nghị thêm bằng makeSlides.

## Bước 5 — Tự kiểm tra (bắt buộc)
```
python3 scripts/kiem_tra_kich_ban.py kich_ban.json --slide slide.json
```
Hết **LỖI** (slide thiếu lời, số nhịp ≠ số cú nhấp, tổng giờ lệch > 10%, hỏi đáp thiếu trả lời, mã chữ hỏng/NFD/ký tự ẩn); xem từng **CẢNH BÁO** (lệch giờ từng slide, đọc lại slide, câu quá dài, thiếu câu mở/chuyển, từ nhấn không khớp, cụm sáo rỗng, Markdown/emoji, `[cần bổ sung]`, số liệu thiếu nguồn, chính tả âm tiết — dùng chung bộ kiểm tra của `make-slides/scripts/kiem_soat_van_ban.py`). Bộ kiểm tra không tra từ điển: vẫn đọc lại để bắt từ đúng cấu tạo nhưng sai nghĩa. Sửa trong `kich_ban.json` rồi chạy lại. Sau đó **đọc to trong đầu** lời từng slide: có tự nhiên như người đó nói không, có đúng vai xưng hô không.

## Bước 6 — Dựng đầu ra
```
python3 scripts/dung_kich_ban.py kich_ban.json --slide slide.json \
    --pptx bai.pptx --ra-pptx <ten>_kich_ban.pptx --ppsx \
    --ra-docx KichBan_<ChuDeKhongDau>_<ddmmyyyy>.docx
```
- Ghi chú diễn giả theo đúng mẫu của makeSlides; dòng nguồn ảnh/tác giả cũ được giữ; bản gốc không bị ghi đè.
- Kiểm tra lại: mở `<ten>_kich_ban.pptx` bằng python-pptx, đối chiếu ghi chú 2–3 slide với `kich_ban.json`; render bản Word (soffice → pdftoppm), xem trang đầu, một trang lời nói và trang thẻ nhắc.

## Bước 7 — Bàn giao
Gửi bằng SendUserFile: `.pptx` (+ `.ppsx`) có ghi chú, bản in Word. Nội dung bàn giao, ngắn gọn:
- tổng thời lượng ước tính so với mục tiêu, tốc độ nói đã dùng;
- những gì đã tự quyết (xưng hô, phân bổ giờ, khách mời);
- chỗ `[cần bổ sung]`, câu hỏi chưa có dữ liệu trả lời, slide dự phòng nên thêm;
- cách dùng: Presenter View (Alt+F5 / Slide Show → Presenter View) để thấy ghi chú; tập một lượt có bấm giờ, nói nhanh/chậm hơn thì báo để chỉnh `toc_do`.

## Những điều tránh
- Đọc lại nguyên câu trên slide; nhịp lời nói lệch với cú nhấp.
- Văn viết, câu dài, chuỗi số liệu liền nhau; "Kính thưa" lặp giữa bài.
- Bịa số liệu, thành tích, trích dẫn, văn bản; tự thêm cam kết thay người trình bày.
- Sửa nội dung slide (skill này chỉ ghi ghi chú — cần sửa slide thì chuyển sang makeSlides, báo người dùng).
- Ghi đè bộ slide gốc của người dùng.
