# Nguyên tắc thiết kế slide ấn tượng

## Màu sắc
- Một màu chủ đạo chiếm 60–70% trọng lượng thị giác, 1–2 màu phụ, 1 màu nhấn sắc nét. Không chia đều màu.
- Chọn màu **theo chủ đề**: nếu đem bảng màu sang bài khác vẫn "hợp" thì chưa đủ đặc trưng.
- Độ tương phản cao: chữ tối trên nền sáng hoặc ngược lại; không chữ xám nhạt trên nền kem. Chữ thường ≥ 4.5:1, chữ ≥ 18pt (hoặc ≥ 14pt đậm) ≥ 3:1.
- **Cân bằng màu — không đơn sắc chìm**: trên nền đậm có sắc (xanh đậm, nâu, tím…), chữ nhấn **không** dùng một sắc nhạt hơn của chính màu nền (chữ xanh nhạt trên nền xanh đậm đọc được nhưng nhìn chìm, đơn điệu). Dùng trắng/ngà, hoặc màu nhấn lệch sắc ≥ 30° (thường là màu ấm trên nền lạnh và ngược lại). Màu nhấn của hình khối (thanh, biểu đồ) được phép cùng tông.
- Màu nhấn chiếm ≤ 10% diện tích; slide nền tối ≤ một nửa số slide (bìa, chia phần, tuyên bố, kết thúc); không quá 3 sắc màu chữ trong cả bài.
- `layouts.style()` tự cảnh báo bảng màu lỗi; `scripts/kiem_tra_slide.py` kiểm từng chữ trên nền thật của nó.
- Không mặc định nền be/kem; nền sáng mặc định là trắng.

### Bảng màu gợi ý (mã hex)
| Tên | Chủ đạo | Phụ | Nhấn | Hợp với |
|---|---|---|---|---|
| Lam đêm trang trọng | 1E2761 | CADCFC | F2B134 | Báo cáo hội nghị, lãnh đạo |
| Đỏ cờ – vàng | 9B1C1C | FFF4E0 | E8B23A | Lễ kỷ niệm, chính trị – xã hội |
| Xanh lúa miền Tây | 2C5F2D | 97BC62 | F4C430 | Giáo dục địa phương, nông nghiệp, môi trường |
| Phù sa – sen hồng | 7A3E2B | F6E7E1 | D9467A | Văn hoá, văn học, di sản |
| Ngọc lam học đường | 028090 | E6F4F1 | F96167 | Bài giảng, tập huấn |
| Than chì tối giản | 2B2D33 | F2F2F2 | 00A896 | Công nghệ, chuyển đổi số |
| San hô năng động | F96167 | F9E795 | 2F3C7E | Sự kiện, học sinh, phong trào |

## Phông chữ
Chọn theo `phong-chu.md` (danh mục phông đóng gói sẵn, nguyên tắc chính quy/kiểu cách, bộ ghép theo bối cảnh). Cỡ chữ: tiêu đề 32–44pt đậm · tiêu đề mục 20–24pt · nội dung 18–20pt (tối thiểu 16pt) · chú thích 12pt.

## Bố cục — luân phiên, không lặp
Dùng thư viện `bo-cuc.md` trước; danh sách dưới đây là các dạng cơ bản khi cần tự dựng.
- Hai cột: chữ trái, hình phải (hoặc ngược lại)
- Hàng ý ngắn ngăn bằng vạch mảnh (không biểu tượng)
- Lưới 2×2 / 2×3 thẻ nội dung
- Ảnh tràn nửa slide + chữ phủ
- Số liệu lớn (60–72pt) + nhãn nhỏ bên dưới
- So sánh hai cột (trước/sau, ưu/nhược)
- Dòng thời gian / quy trình có đánh số và mũi tên
- Trích dẫn lớn (câu nói, câu thơ được phép dùng) trên nền đậm
- Slide chia phần (section divider) nền đậm, số thứ tự lớn

## Motif thị giác
Chọn **một** yếu tố đặc trưng lặp lại xuyên suốt: khung ảnh bo góc lớn; vạch mảnh màu nhấn mở đầu mỗi cột; số thứ tự to mờ ở slide chia phần; hoạ tiết hình học nhẹ ở slide chia phần; một kiểu chú thích hình. Không dùng thanh màu/dải sọc ở mép làm motif; **không dùng biểu tượng trong vòng tròn** (dấu hiệu slide AI, xem `dau-hieu-ai.md`).

## Khoảng trắng
- Lề tối thiểu ~0,5 inch (1,27 cm).
- Khoảng cách giữa các khối đồng nhất (0,3" hoặc 0,5").
- Chừa chỗ thở — không lấp đầy mọi góc.

## Chữ trên slide
- Mỗi slide một thông điệp; ≤ 6 dòng; mỗi dòng ≤ ~12 từ.
- Chuyển đoạn văn dài thành: từ khoá in đậm, sơ đồ, số liệu hoặc ảnh thật (không thêm biểu tượng trước chữ).
- Công thức: khối Equation (`MS.equation`), không gõ bằng chữ.
- Phần giải thích chi tiết đưa vào **ghi chú diễn giả**.
- Căn trái nội dung; chỉ căn giữa tiêu đề và slide bìa/chia phần.

## Hình ảnh
- Ưu tiên ảnh thật, sắc nét, đúng ngữ cảnh Việt Nam khi phù hợp. Nếu có kết nối Unsplash, có thể dùng để tìm ảnh minh hoạ có giấy phép.
- Không dùng ảnh nhân vật có bản quyền (hoạt hình, phim), logo thương hiệu không thuộc người dùng.
- Biểu đồ: dùng biểu đồ gốc (native) khi có thể; có tiêu đề, nhãn số liệu, màu theo bảng màu.
