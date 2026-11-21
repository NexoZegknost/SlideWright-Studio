# Kiểm soát văn bản — `scripts/kiem_soat_van_ban.py`

Đây là module kiểm tra mọi thứ thuộc về chữ trên slide và cách chữ hiển thị: phông, mã chữ, chính tả, dấu câu, viết hoa, các thuộc tính hiển thị, và kết quả dựng thật. Thêm `--day-du` thì module gộp luôn kết quả của `kiem_tra_van_ban.py` (cỡ chữ, lượng chữ, xuống dòng, tràn khung) và `kiem_tra_slide.py` (màu, dấu hiệu AI, công thức), nên chỉ cần đọc một báo cáo.

## 1. Cách chạy
```bash
python3 scripts/kiem_soat_van_ban.py Slide.pptx --phong-cach <khoá> --boi-canh <khoá> --hien-thi --day-du
python3 scripts/kiem_soat_van_ban.py Slide.pptx --day-du --sua Slide_sua.pptx    # tự sửa phần an toàn rồi kiểm lại
```
| Tuỳ chọn | Tác dụng |
|---|---|
| `--phong-cach <khoá>` | Khoá trong `assets/styles.json`. Lấy mức trang trọng và cặp phông của phong cách, rồi báo phông nằm ngoài cặp này |
| `--muc chinh-quy \| ban-chinh-quy \| kieu-cach` | Đặt mức trang trọng khi không dùng phong cách có sẵn (ví dụ phương án của `dinh_huong.js`). `chinh-quy` gặp phông trang trí là báo LỖI |
| `--boi-canh <khoá>` | Khoá trong `assets/contexts.json`, quyết định cỡ chữ tối thiểu và số chữ tối đa |
| `--hien-thi` | Dựng thử bằng LibreOffice với phông của gói, rồi đọc phông thật của từng đoạn chữ trong PDF (cần PyMuPDF) |
| `--day-du` | Gộp thêm hai script kiểm tra chữ và màu. Đi cùng `--sua` thì chạy luôn phần tự sửa cỡ chữ và xuống dòng của `kiem_tra_van_ban.py` |
| `--chi phong,chinh-ta,…` | Chỉ in các nhóm được nêu |
| `--json` | In kết quả dạng JSON |
| `--bo-qua-ghi-chu` | Không kiểm tra ghi chú diễn giả |

Mã thoát 1 nghĩa là còn LỖI. CẢNH BÁO thì xem từng mục rồi quyết định, GỢI Ý để tham khảo. Mục có dấu `(tự sửa được: --sua)` là mục module tự sửa được.

## 2. Các nhóm kiểm tra
| Nhóm | Phát hiện | Mức |
|---|---|---|
| **phông** | Be Vietnam Pro; phông mã cũ (.VnTime, VNI-…) | LỖI |
| | Phông của gói chưa nhúng; phông ngoài gói chưa nhúng | LỖI |
| | Phông thiếu ký tự (đọc bảng mã của tệp phông) | LỖI |
| | Phông trang trí trong bài chính quy | LỖI |
| | Đậm hoặc nghiêng giả (họ phông không có kiểu đó) | CẢNH BÁO |
| | Quá 3 họ phông; tiêu đề không cùng họ phông; nội dung quá 2 họ; một đoạn trộn 3 phông trở lên | CẢNH BÁO |
| | Phông trang trí quá dài, quá nhỏ, viết HOA, dùng cho con số; Playfair Display cho số lớn | CẢNH BÁO |
| | Space Mono, Rowdies, Baloo 2 dùng cho đoạn văn | CẢNH BÁO |
| **mã chữ** | Unicode tổ hợp (NFD); ký tự ẩn (zero-width, soft hyphen, BOM, ký tự điều khiển) | LỖI, tự sửa |
| | Chữ Ð (Eth) thay cho Đ | LỖI, tự sửa |
| | Ký tự hỏng �; chữ mã TCVN3 chưa chuyển; ký hiệu văn bản thiếu Đ (BGDDT, GD&DT) | LỖI |
| **chính tả** | Hai dấu thanh trong một âm tiết; Markdown sót (`**`, `#`, `` ` ``); LaTeX sót (`$…$`, `\frac`) | LỖI |
| | Âm tiết không có trong tiếng Việt; dấu đặt sai chỗ (cưú → cứu); vần tắc thiếu dấu hoặc mang sai dấu (tiêt, cảp) | CẢNH BÁO |
| | Sai luật c/k, g/gh, ng/ngh, qu; lặp hư từ (của của); chữ giữ chỗ còn sót ([cần bổ sung], Lorem ipsum) | CẢNH BÁO |
| | Lẫn kiểu bỏ dấu cũ và mới (hoà/hòa, tuỳ/tùy) | CẢNH BÁO |
| | Lẫn kỹ/kĩ, lý/lí | GỢI Ý |
| **dấu câu** | Hai khoảng trắng; khoảng trắng trước dấu câu hoặc sát trong ngoặc; thiếu khoảng trắng sau dấu phẩy | CẢNH BÁO, tự sửa |
| | Dấu câu lặp; ngoặc lệch cặp; tiêu đề có dấu chấm cuối; gạch đầu dòng gõ tay | CẢNH BÁO |
| | Ngoặc kép thẳng; lẫn "..." và "…"; khoảng số dùng gạch nối (10-20); ký tự tab; dòng trống làm khoảng cách | GỢI Ý |
| **viết hoa** | Đoạn nội dung viết HOA toàn bộ; Viết Hoa Mỗi Chữ kiểu tiếng Anh | CẢNH BÁO |
| | Tên cơ quan viết hoa sai (sở giáo dục và đào tạo → Sở Giáo dục và Đào tạo); cả bài chỉ có dạng viết tắt (UBND, Sở GDĐT) | CẢNH BÁO |
| | Đầu đoạn viết thường | GỢI Ý |
| **hiển thị** | Tự co chữ làm chữ nội dung thực tế nhỏ hơn mức tối thiểu; chữ < 12pt; hộp chữ ra ngoài slide; tắt xuống dòng làm chữ tràn ra ngoài slide | LỖI |
| | Bật Tự co chữ trên khung đang tràn (PowerPoint sẽ thu chữ khi mở); chữ xoay hoặc chữ dọc; WordArt uốn; nén hoặc giãn chữ quá mức; bóng, viền, phát sáng | CẢNH BÁO |
| | Gạch chân không phải liên kết; chữ mờ; căn đều hai bên; căn giữa đoạn dài; chữ biểu đồ < 12pt hoặc để cỡ mặc định; chữ bảng nhỏ; thiếu ghi chú diễn giả | CẢNH BÁO |
| | Liên kết không có đích | LỖI |
| | Mã ngôn ngữ khác vi-VN, làm PowerPoint gạch đỏ chính tả khi sửa | GỢI Ý, tự sửa |
| | m2/m3 chưa viết chỉ số trên; khung giữ chỗ trống; hộp chữ bị ẩn; đường dẫn dài hiện nguyên | GỢI Ý |
| **dựng thử** | Phông khai báo nhưng bản dựng không dùng (bị thay); chữ rơi sang phông dự phòng (ghi rõ đoạn chữ) | CẢNH BÁO |

Ghi chú về phần chính tả:
- Bộ kiểm tra chính tả phân tích từng âm tiết: âm đầu, vần, vị trí dấu thanh. Nó không tra từ điển, nên không bắt được từ đúng cấu tạo nhưng sai nghĩa (đển, tính → tỉnh). Những lỗi này vẫn phải đọc lại bằng mắt.
- Từ viết hoa chữ đầu (tên riêng, địa danh dân tộc như Đắk Lắk, Krông Pa) chỉ được báo ở mức GỢI Ý. Chữ viết tắt toàn HOA được bỏ qua.
- Thử trên khoảng 14.650 âm tiết trong tài liệu của plugin, bộ kiểm tra chỉ báo 3 mục, và cả 3 đều là ví dụ lỗi cố ý (kíểm, tiêt, phưong).

## 3. Tự sửa (`--sua`) làm gì
Phần tự sửa chỉ đụng tới những gì không làm đổi câu chữ:
- chuẩn hoá Unicode dựng sẵn (NFC), bỏ ký tự ẩn, đổi Ð thành Đ;
- gộp khoảng trắng thừa, kể cả khoảng trắng kép vắt qua hai run;
- bỏ khoảng trắng đầu và cuối đoạn, trước dấu câu, sát trong ngoặc;
- thêm khoảng trắng sau dấu phẩy và dấu chấm phẩy;
- đổi phông bị loại sang phông thay thế (Be Vietnam Pro → Montserrat), cả trong theme, master và layout;
- gắn `lang="vi-VN"` cho đoạn chữ tiếng Việt, cả trong ghi chú diễn giả.

Chính tả, viết hoa, phông, cỡ chữ và ký hiệu văn bản chỉ được báo kèm gợi ý. Với bài do Claude dựng, sửa trong script dựng rồi dựng lại. Với tài liệu gốc của người dùng, báo lỗi để họ quyết định.

## 4. Đưa vào quy trình
- **Nhánh A (tạo mới):** chạy ở đầu Bước 7 với `--phong-cach`/`--muc`, `--boi-canh`, `--hien-thi`, `--day-du`. Sau đó chạy `kiem_tra_bo_cuc.py` và `kiem_tra_hieu_ung.py`.
- **Nhánh B (nâng cấp):** chạy trên bài gốc trước khi thiết kế lại để biết lỗi chữ có sẵn (mã TCVN3, NFD, phông lạ, chính tả), ghi vào phần báo lỗi tài liệu nguồn, rồi chạy lại trên bản nâng cấp.
- **Nhánh C (chuyển PDF):** chạy với `--chi ma-chu,chinh-ta,phong,dung-thu` để biết chữ trích ra có hỏng mã hay thiếu phông không. Không sửa nội dung bản gốc.
- **Canva:** dùng `scripts/kiem_tra_canva.py` trên dữ liệu `read-design` (gọi lại bộ kiểm chính tả, dấu câu, viết hoa, mã chữ của module này trên từng hộp chữ), không cần tải tệp. Xem `quy-trinh-canva.md`.
- **Gamma:** tải bản PPTX về rồi chạy `--chi ma-chu,chinh-ta,dau-cau,viet-hoa`.

## 5. Mở rộng
- Thêm phông vào gói: khai báo trong `assets/fonts/files.json` và phân loại trong `assets/fonts/phan-loai.json` (`loai`, `min_pt`, `max_tu`, `khong_so`, `khong_doan`, `khong_hoa`, `ban_chinh_quy`).
- Thêm tên cơ quan cần viết hoa đúng: danh sách `CO_QUAN`. Thêm dạng viết tắt: `VIET_TAT`.
- Âm tiết hợp lệ nhưng ngoài vần chuẩn (địa danh, từ dân tộc): thêm vào `NGOAI_LE`.
