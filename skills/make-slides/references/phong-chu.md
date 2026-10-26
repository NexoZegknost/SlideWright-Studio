# Phông chữ — chọn theo phong cách và bối cảnh

Toàn bộ phông nằm trong `assets/fonts/` (bản tĩnh, đủ dấu tiếng Việt, giấy phép SIL OFL — được phép nhúng và phân phối kèm). Danh sách tệp theo họ phông: `assets/fonts/files.json`. Chỉ dùng tên họ phông đúng như cột "Họ phông" dưới đây (PowerPoint khớp theo tên này).

## Nguyên tắc cốt lõi
1. **Bài chính quy, nghiêm túc** (báo cáo, hội nghị, văn bản chỉ đạo, tập huấn, bài giảng): **chỉ dùng phông có chân (serif) và không chân (sans-serif)**. Tuyệt đối không dùng phông trang trí/viết tay, kể cả cho điểm nhấn.
2. **Bài cần kiểu cách** (lễ kỷ niệm, tri ân, sự kiện, văn nghệ, giới thiệu, thiệp, WordArt): được dùng **phông trang trí** — nhưng chỉ cho tiêu đề lớn, chữ nghệ thuật, lời đề tặng, câu trích ngắn (1–8 từ, cỡ ≥ 32pt). Nội dung vẫn dùng serif/sans.
3. Mỗi bài tối đa **2 họ phông chính + 1 phông điểm nhấn**.
4. **Không dùng Be Vietnam Pro** (đã loại khỏi gói theo yêu cầu của người dùng). Cần chữ không chân trung tính → Montserrat; cần chữ dễ đọc, gọn → Lexend. Bài nâng cấp/chuyển đổi có sẵn Be Vietnam Pro → đổi sang Montserrat, trừ nhánh C (giữ nguyên bản gốc).
5. Nhúng **mọi** họ phông đã dùng (`embedFonts`) để hiển thị đúng trên máy không cài phông.

## Danh mục phông

### Có chân (serif) — trang trọng, văn chương
| Họ phông | Kiểu có | Đặc điểm | Dùng cho |
|---|---|---|---|
| Noto Serif Display | thường/đậm/nghiêng/đậm nghiêng | Tương phản nét cao, sang trọng | Tiêu đề báo cáo, hội nghị, bìa |
| Playfair Display | thường/đậm/nghiêng/đậm nghiêng | Cổ điển, giàu chất văn; **số kiểu cổ (old-style)** | Tiêu đề bài Ngữ văn, văn hoá, di sản. Không dùng cho con số |
| Lora | thường/đậm/nghiêng/đậm nghiêng | Serif dễ đọc ở cỡ nhỏ | Nội dung dài, trích đoạn văn bản |
| Noto Serif | thường/đậm | Serif trung tính, rõ ràng | Nội dung văn bản hành chính, tài liệu chính thức |

### Không chân (sans-serif) — hiện đại, rõ ràng
| Họ phông | Kiểu có | Đặc điểm | Dùng cho |
|---|---|---|---|
| Montserrat | thường/đậm/nghiêng/đậm nghiêng | Hình học, chắc chắn, số đẹp | Nội dung mặc định cho hầu hết bài; con số lớn |
| Lexend | thường/đậm | Tối ưu khả năng đọc | Bài giảng cho học sinh, chữ nội dung cần đọc nhanh |
| Bricolage Grotesque | thường/đậm | Cá tính, hiện đại | Tiêu đề bài công nghệ, chuyển đổi số, đổi mới |
| Nunito | thường/đậm | Bo tròn, thân thiện | Bài giảng tiểu học/THCS, sinh hoạt tập thể |
| Montserrat Alternates | thường/đậm/nghiêng | Biến thể vui của Montserrat | Tiêu đề bài học sinh, phong trào (bán chính quy) |
| Space Mono | thường/đậm/nghiêng | Đơn cách (monospace) | Số liệu, mã, nhãn kỹ thuật ngắn — không dùng cho đoạn văn |

### Trưng bày (display) — đậm, vui, nổi bật
| Họ phông | Kiểu có | Dùng cho |
|---|---|---|
| Rowdies | thường/đậm | Tiêu đề sự kiện học sinh, trò chơi, khởi động |
| Baloo 2 | thường/đậm | Tiêu đề bài giảng tiểu học, tròn và dày |

### Trang trí / viết tay — CHỈ cho bài kiểu cách, WordArt
| Họ phông | Độ dễ đọc | Dùng cho |
|---|---|---|
| Dancing Script (thường/đậm) | Khá | Tiêu đề phụ mềm mại, lời chào, chữ ký |
| Pangolin | Tốt | Chữ viết tay vui cho bài thiếu nhi (có thể dùng cho câu ngắn) |
| Great Vibes | Trung bình | Tiêu đề lễ trao giải, tri ân, "Trân trọng cảm ơn" |
| Allura | Trung bình | Lời đề tặng, câu thơ ngắn |
| Style Script | Trung bình | Tiêu đề bìa sự kiện văn hoá |
| Beau Rivage | Thấp | Chữ nghệ thuật cỡ rất lớn (≥ 48pt), 1–3 từ |
| WindSong | Thấp | Chữ nghệ thuật cỡ rất lớn (≥ 48pt), 1–3 từ |

Với phông viết tay: không viết HOA toàn bộ, không dùng cho số liệu, luôn đặt trên nền tương phản mạnh.

## Bộ ghép theo phong cách
Cặp phông của từng phong cách nằm trong `phong-cach.md` và `assets/styles.json`. Chỉ đổi phông khi người dùng yêu cầu hoặc nội dung đặc thù (ví dụ cần phông đơn cách cho mã nguồn), và vẫn giữ đúng mức trang trọng.

## Tìm thêm phông khi cần
Nếu không phông nào phù hợp (ví dụ cần chữ thư pháp Việt, chữ kiểu cổ động), tìm thêm trên Google Fonts (kho `github.com/google/fonts`, thư mục `ofl/<tên>`; tải qua `raw.githubusercontent.com/google/fonts/main/ofl/...`). Chỉ nhận phông khi đạt đủ:
- Đủ bộ chữ tiếng Việt (kiểm tra bằng fontTools: mọi ký tự ă â đ ê ô ơ ư và 5 dấu thanh hoa/thường đều có trong cmap) **và** dựng chữ mẫu để xem dấu không chồng/lệch.
- `OS/2.fsType` = 0 (cho phép cài đặt/nhúng) và giấy phép OFL/Apache.
- Phông biến thiên (variable) phải tách bản tĩnh Regular/Bold bằng `fontTools.varLib.instancer` và đặt lại tên (nameID 1, 2, 4, 6) trước khi nhúng.
Đặt phông mới vào thư mục làm việc (không sửa thư mục plugin) và truyền đường dẫn tệp cho `embedFonts` qua `MS.FONT_FILES[tên] = {regular, bold}` (đường dẫn tuyệt đối).
