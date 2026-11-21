# Quy trình thiết kế slide trên Canva

Nhánh Canva **chỉ thiết kế trên Canva và bàn giao link chỉnh sửa**. Không xuất, không tải tệp về. Người dùng hỏi bản PowerPoint/PDF thì chỉ cách tải trong Canva (Chia sẻ → Tải xuống).

Cách làm là **kết hợp**:
1. Canva AI dựng khung từ bản yêu cầu và dàn ý. Canva chọn mẫu, phông, ảnh tốt hơn tự dựng.
2. Claude đọc thiết kế, kiểm tra bằng `scripts/kiem_tra_canva.py` và ảnh từng trang.
3. Claude sửa trực tiếp từng đối tượng theo chuẩn của plugin, rồi lưu khi người dùng đồng ý.

Cần kết nối **Canva**. Tìm công cụ qua ToolSearch ("canva"). Không có thì báo người dùng kết nối Canva và đề nghị bản PowerPoint. Tên và tham số công cụ có thể đổi: đọc mô tả thực tế, gọi `help` của Canva khi cần.

Áp dụng Bước 1–5 và 9 của SKILL.md như PowerPoint. Bước 6–8 và 10 làm theo tài liệu này.

## 1. Những gì làm được và không làm được qua công cụ
| Việc | Làm được | Cách |
|---|---|---|
| Dựng bộ slide từ yêu cầu + dàn ý | Có | `create-design` (`format: "Presentation"`, `outline`, `brand_kit_id` khi người dùng yêu cầu nhận diện) |
| Sửa chữ, cỡ, màu, đậm, nghiêng, căn, giãn dòng, danh sách | Có | `edit-design`: `find_and_replace_text`, `replace_text`, `format_text` |
| Di chuyển, đổi kích thước, xoay, xếp lớp, nhóm, xoá đối tượng | Có | `position_element`, `resize_element`, `rotate_element`, `layer_element`, `group_elements`, `delete_element` |
| Thêm chữ, hình vẽ, trang (có màu nền), đổi màu hình, viền | Có | `add_text`, `insert_shape`, `add_page`, `recolor_element`, `update_stroke_properties` |
| Thay hoặc chèn ảnh | Có, cần `asset_id` | ảnh tải lên Canva (`upload-asset-from-url`) hoặc ảnh Canva AI tạo (`generate-image`) |
| Ghi chú diễn giả | Có | `replace_speaker_notes` |
| **Đổi phông chữ** | **Không** | Chọn phông qua bản yêu cầu. Sai phông thì dựng lại hoặc nhờ người dùng đổi trong Canva |
| **Hiệu ứng, chuyển trang** | **Không** | Soạn bảng hiệu ứng đề xuất để người dùng làm trong Canva (mục 7) |
| Đổi màu ảnh nền | Không | Ảnh nền sai tông thì thay ảnh (`update_fill`) hoặc dựng lại |

## 2. Viết bản yêu cầu và dàn ý (quyết định 80% chất lượng)
**Bản yêu cầu (`brief`)** ghi đủ, rõ:
- chủ đề, mục đích, người nghe, bối cảnh trình chiếu (hội trường lớn → chữ to, ít chữ);
- **nền sáng hay tối, nêu thẳng** ("nền sáng màu ngà, không dùng nền xanh đậm"). Canva hay bỏ qua mã màu, nên phải tả màu bằng lời kèm mã hex;
- màu chủ đạo và màu nhấn đúng `references/phoi-mau.md`; nêu rõ **không** phối lam–cam, đỏ–lục, vàng–tím;
- phông: "tiêu đề phông có chân / không chân, nội dung không chân, không phông viết tay, không chữ in hoa toàn bộ cho đoạn nội dung" (bài chính quy);
- "giữ đúng, đủ dấu tiếng Việt; giữ nguyên ký hiệu văn bản có chữ Đ (BGDĐT, SGDĐT)";
- "mỗi slide chỉ chữ trong dàn ý, không thêm câu, không thêm nhãn; chữ nội dung tối thiểu 48px";
- "không biểu tượng/emoji trước chữ; không ảnh người nước ngoài; không logo thương hiệu".

**Dàn ý (`outline.sections`)**: mỗi slide một mục.
- `title`: đúng tiêu đề thông điệp sẽ hiện trên slide (≤ 12 từ, viết hoa đúng tên riêng).
- `points`: đúng những dòng sẽ hiện, ngắn, đủ dấu, giữ nguyên số hiệu văn bản và số liệu.
- `description`: **chỉ chứa nội dung sẽ lên slide** (ví dụ "Báo cáo sơ kết học kỳ I, năm học 2026–2027, Sở Giáo dục và Đào tạo"). **Không** ghi chỉ dẫn kiểu "Slide bìa:", "Slide kết: thông điệp chính…", vì Canva chép nguyên nhãn đó lên slide.
- Lưu đúng dàn ý đã gửi vào `dan_y.json` để đối chiếu ở mục 5.

Nhiều bộ slide độc lập thì gọi `create-design` song song. Nhiều bộ cho cùng một sự kiện thì dùng chung bản yêu cầu (màu, phông, phong cách).

## 3. Dựng và chờ
`create-design` trả `job_id` và `continuation_token`. Có widget tự theo dõi thì không tự hỏi. Nếu không có widget, gọi `get-create-design-async-job` và chờ đúng `polling_policy.wait_seconds`. Trong sandbox, chạy `sleep 45` (đặt thời gian chờ của lệnh) giữa các lần hỏi.

## 4. Đọc thiết kế đúng cách
- **Đọc có cấu trúc, không đọc kiểu gộp.** Gọi `read-design` với `open_transaction: true` và `fields: ["design_content", "thumbnails"]`. Bản gộp nối các dòng trong cùng một hộp (ra "bằnggiọng", "giáđể") làm báo nhầm lỗi dính chữ. Bản có cấu trúc giữ từng hộp chữ, toạ độ, cỡ, màu và `locator_id`.
- **Lưu dữ liệu cho script:** ghi phần `design_content` vào `canva.json`. Bộ dài thì chỉ cần giữ các trường: `index`, `width`, `height`, và với mỗi phần tử `locator_id`, `type`, `top`, `left`, `width`, `height`, `opacity`, `rotation`, `textRegions` (`characters`, `fontSize`, `color`, `fontWeight`, `lineHeight`, `letterSpacing`). Phần tử không phải chữ chỉ cần toạ độ.
- **Ảnh trang:** ảnh Canva lưu sẵn thường trắng hoặc chưa có. Ảnh thật chỉ có trong kết quả `edit-design` của trang vừa sửa. Muốn xem một trang chưa cần sửa, dùng thao tác **không làm đổi kích thước chữ**: `position_element` đặt lại đúng toạ độ cũ của một phần tử. **Không** dùng `format_text` (đổi độ đậm, cỡ) để "lấy ảnh", vì Canva tính lại khung hộp và có thể làm hẹp khung, lòi nét chữ (đã gặp với số "13").
- Quy đổi cỡ: trang 1920 × 1080px tương đương 960 × 540pt, nên **pt = px ÷ 2** (trang khác cỡ: pt = px × 960 ÷ bề rộng trang).

| pt | 12 | 16 | 20 | 24 | 28 | 32 | 40 |
|---|---|---|---|---|---|---|---|
| px (trang 1920) | 24 | 32 | 40 | 48 | 56 | 64 | 80 |

## 5. Kiểm tra
```bash
python3 scripts/kiem_tra_canva.py canva.json --boi-canh <khoá> --bang-mau "#hex1,#hex2,#hex3" --dan-y dan_y.json
```
Script báo từng mục kèm `locator_id` để sửa ngay:
| Nhóm | Phát hiện |
|---|---|
| `co-chu` | chữ nội dung < cỡ tối thiểu của bối cảnh, tiêu đề < cỡ tiêu đề, chữ < 12pt; báo sẵn `font_size` cần đặt |
| `luong-chu` | quá số chữ/trang của bối cảnh; hộp chữ quá 4 dòng |
| `bo-cuc` | chữ đè chữ; hai khối chữ quá sát; **khung hẹp hơn chữ** (nét lòi/cắt); **các hộp ghép thành một dòng lệch chân chữ** (báo sẵn `top` cần đặt); lề trái lệch vài px; chữ ra ngoài hoặc sát mép trang; chữ xoay; chữ mờ; chữ chạm vạch/khối nhỏ |
| `mau` | màu chữ ngoài bảng màu (báo màu thay); cặp màu đối nhau; > 3 sắc màu chữ trên trang |
| `dan-y` | nhãn nội bộ bị chép lên slide (LỖI); câu Canva tự thêm; ý trong dàn ý bị thiếu |
| `chu` | chính tả âm tiết, dấu câu, viết hoa tên cơ quan, mã chữ (dùng bộ kiểm của `kiem_soat_van_ban.py`, giữ nguyên chỗ xuống dòng) |

Sau đó **xem ảnh từng trang**. Ảnh bắt được những gì script không thấy:
- màu ảnh nền: script không đọc được màu trong ảnh, nên cặp lam–cam giữa nền ảnh và chữ chỉ thấy qua ảnh; đếm số trang nền tối (≤ một nửa);
- chữ trên ảnh minh hoạ của Canva AI (thường vô nghĩa hoặc sai dấu);
- phông thực tế: có phải phông viết tay, có viết HOA toàn bộ che lỗi viết hoa không;
- vạch, khối trang trí chạm chân chữ (khối ảnh có viền trong suốt nên toạ độ không chính xác);
- tiêu đề bị Canva tách thành nhãn nhỏ cộng câu viết thường ("Đề mở" / "giúp học sinh…"): đọc liền còn đúng thông điệp không.

Lỗi tiếng Việt Canva AI hay mắc: mất chữ Đ trong ký hiệu (BGDDT); sai dấu (kíểm, đển, tính→tỉnh); viết thường tên cơ quan, tên môn học ("Sở giáo dục và đào tạo", "môn ngữ văn"); chữ vô nghĩa trên hình minh hoạ nhỏ.

## 6. Sửa
Một phiên sửa cho cả bộ. Sửa **từng trang**, mỗi lần `edit-design` (`finalize: "keep_open"`) xong thì so ảnh trước/sau và đọc lại `document` trả về rồi mới sửa tiếp trang đó.

**Đối tượng và bố cục**
- Lề an toàn ≥ 3% bề rộng trang (≈ 58px). Các khối cùng cột dùng **một** lề trái (căn theo khối lớn nhất).
- Các hộp ghép thành một dòng ("tăng | 13 | điểm phần trăm") đặt cùng chân chữ theo gợi ý `top` của script, khoảng cách ngang ≥ 12% cỡ chữ nhỏ hơn.
- Khung hẹp: `resize_element` (chỉ `width` với chữ) theo gợi ý, rồi xem ảnh.
- Vạch, khối trang trí cách chân chữ ≥ 15px; không để chữ chạm mép khối màu.
- Xoá nhãn nội bộ, câu tự thêm, khung trống bằng `delete_element`. Cần giữ bố cục thì thay chữ đúng dàn ý bằng `replace_text`.
- Ảnh: đúng ngữ cảnh, ưu tiên Việt Nam, không người nước ngoài, không logo lạ. Ảnh có chữ vô nghĩa thì thay (`update_fill`). Chỉ dùng logo, màu của đơn vị khi người dùng yêu cầu.
- Không thêm biểu tượng trước chữ, không vòng "VS", không thẻ bằng nhau hàng loạt (theo `references/dau-hieu-ai.md`).

**Văn bản**
- Cỡ: đặt `font_size` theo bảng ở mục 4 cho đủ cỡ tối thiểu của bối cảnh. Tăng cỡ làm chữ dài ra: kiểm tra xuống dòng, mồ côi một từ, tràn khung bằng ảnh và chạy lại script.
- Lượng chữ: ≤ số chữ của bối cảnh. Phần dư đưa vào ghi chú diễn giả.
- Độ đục chữ 100% (`update_opacity`), màu chữ đủ tương phản: trắng/ngà trên nền đậm, đậm trên nền sáng.
- Màu nhấn của chữ (số liệu, từ khoá) đổi về bảng màu bằng `format_text` → `color`.
- Viết hoa: sửa chữ gốc dù phông đang hiển thị HOA toàn bộ (đổi phông sẽ lộ lỗi). Tên cơ quan viết đầy đủ, đúng hoa ("Sở Giáo dục và Đào tạo").
- Đoạn nội dung căn trái; chỉ căn giữa tiêu đề bìa, slide số liệu lớn.
- Ghi chú diễn giả 3–5 câu/slide có thứ tự cú nhấp, kèm bảng hiệu ứng nếu có (`replace_speaker_notes`).

**Phông**: không đổi được qua công cụ. Bài chính quy mà Canva dùng phông viết tay hoặc trang trí cho nội dung → dựng lại với bản yêu cầu ghi rõ hơn, hoặc ghi vào phần bàn giao để người dùng đổi trong Canva (chọn chữ → ô tên phông).

Sửa xong: đọc lại có cấu trúc, chạy lại script đến khi hết LỖI, xem ảnh mọi trang đã sửa.

## 7. Hiệu ứng (người dùng làm trong Canva theo bảng đề xuất)
Công cụ không đặt được hiệu ứng. Plugin **soạn bảng hiệu ứng đề xuất** theo `references/hieu-ung.md` và mức của bối cảnh, đưa vào phần bàn giao:

| Trang | Đối tượng | Hiệu ứng xuất hiện | Thứ tự | Chuyển sang trang sau |
|---|---|---|---|---|
| 1 | Tiêu đề / dòng phụ | Rise (Nổi lên) / Fade | 1 / 2 | Match and move |
| 3 | Số "13" → ba dòng năm học | Pop / Rise lần lượt | 1 → 4 | Match and move |

Nguyên tắc:
- Thứ tự xuất hiện = thứ tự nói; ≤ 5 bước mỗi trang; chữ nội dung dùng hiệu ứng nhẹ (Fade, Rise, Pan), không dùng hiệu ứng nhảy/rung cho bài chính quy.
- Một kiểu chuyển trang xuyên suốt. **Match and move** của Canva tương tự Morph: chỉ chạy đẹp khi hai trang liền nhau có **cùng đối tượng** (cùng thanh màu, cùng ảnh, cùng số) ở vị trí khác nhau. Khi sửa ở mục 6, giữ các đối tượng nối tiếp này (motif của cảnh morph theo `references/chuyen-trang.md`).
- Mức tiết chế hoặc không hiệu ứng: chỉ chuyển trang Fade/Dissolve, không hiệu ứng đối tượng.

Hướng dẫn kèm cho người dùng: chọn đối tượng → **Chuyển động** trên thanh công cụ → chọn hiệu ứng; chuyển trang thì bấm vào khoảng giữa hai trang ở thanh trang bên dưới → chọn kiểu chuyển cảnh. Tên trong giao diện tiếng Việt có thể khác tên tiếng Anh trong bảng.

## 8. Lưu
Lưu (`finalize: "commit"`) cần người dùng đồng ý. Tóm tắt các chỗ đã sửa theo trang, gửi ảnh trước/sau của các trang thay đổi nhiều, hỏi **một lần** (AskUserQuestion). Không đồng ý thì `cancel`. Mọi phiên mở phải được lưu hoặc huỷ. Chế độ "làm luôn" vẫn phải hỏi trước khi lưu.

## 9. Bàn giao
- Link chỉnh sửa Canva (`design_metadata.urls.edit_url`).
- 1–2 câu tóm tắt: số trang, phong cách, màu chủ đạo.
- Các chỗ đã sửa và các giới hạn còn lại (phông không đổi được, ảnh nền giữ nguyên tông…).
- Bảng hiệu ứng đề xuất (mục 7) và cách đặt trong Canva.
- Lỗi phát hiện trong tài liệu nguồn (nếu có).
