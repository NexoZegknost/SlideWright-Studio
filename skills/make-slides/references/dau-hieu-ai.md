# Dấu hiệu slide do AI làm — nhận diện và loại bỏ

Người xem nhận ra slide "do AI làm" qua những khuôn lặp lại: biểu tượng trong vòng tròn trước mỗi ý, ba thẻ bằng nhau, nhãn "Điểm chính", gạch ngang nối ý, từ sáo rỗng. Mỗi dấu hiệu riêng lẻ có thể vô hại; gộp lại chúng làm bài mất giọng của người trình bày. Rà theo bảng dưới **ở Bước 6 khi viết** và **ở Bước 7 bằng script**:

```bash
python3 scripts/kiem_tra_slide.py Slide_X.pptx      # LỖI phải sửa hết; CẢNH BÁO xem từng mục và quyết định
```

## 1. Hình ảnh và bố cục
| Dấu hiệu | Thay bằng |
|---|---|
| **Biểu tượng/emoji đứng trước đoạn văn, tiêu đề thẻ, gạch đầu dòng** (cấm) | Chữ đậm làm nhãn; một con số/cụm chữ in lớn (`mark` của `baThe`); ảnh thật; hoặc không gì cả |
| Biểu tượng trắng trong vòng tròn màu nhấn | Bỏ. Nếu thật cần hình: ảnh chụp, sơ đồ, ảnh chụp màn hình |
| Ba (bốn) thẻ bo góc bằng nhau, có bóng, xếp hàng ngang | Cột không nền ngăn bằng vạch mảnh (`baThe` mới); bố cục bất đối xứng (`bento`, `luoiThuySy`, `thangSo`) |
| Vòng tròn "VS" giữa hai cột | Hai cột khác nền, khác độ rộng tự tạo đối lập (`soSanh`) |
| Mũi tên chevron cho mọi quy trình | `buocDoc` (bước xếp dọc), `dongThoiGian`, hoặc sơ đồ thật |
| Nhãn khuôn mẫu: "Điểm chính", "Key takeaway", "Lưu ý", "Tóm lại" trên hộp tối | Câu kết luận tự đứng, cỡ lớn, cạnh biểu đồ (`bieuDo` mới) |
| Nhãn chữ in hoa nhỏ + vạch màu ngắn phía trên mọi tiêu đề | Chỉ dùng kicker ở bìa/slide mở phần khi có thông tin thật (tên môn, tên hội nghị) |
| Số "01 02 03" khổng lồ mờ ở mọi slide | Chỉ ở slide chia phần; slide nội dung dùng số nhỏ |
| Cùng một bố cục 3 slide liên tiếp; mọi slide cùng mật độ | Đổi bố cục theo loại nội dung; xen slide một ý (tuyên bố, số lớn, câu hỏi) |
| Gradient tím–xanh, ánh neon, ảnh 3D bóng loáng, ảnh AI quá bão hoà | Màu phẳng của phong cách; ảnh thật, ánh sáng tự nhiên |
| Mọi thứ căn giữa | Căn trái nội dung; căn giữa chỉ cho bìa, tuyên bố, số liệu |

## 2. Chữ
| Dấu hiệu | Thay bằng |
|---|---|
| Tiêu đề chung chung: "Giới thiệu", "Nội dung", "Tổng quan", "Kết luận" | Câu thông điệp: "Chỉ vùng tích cực mới khuếch đại", "Tụ CE nâng độ lợi lên 50 lần" |
| Tiêu đề đếm số sáo rỗng: "Ba phương pháp…", "Ba con số đáng chú ý", "4 phần trong lộ trình", "5 điểm nổi bật" | Nói luôn điều phát hiện/kết luận; con số đặt trong nội dung, không làm tiêu đề |
| Mọi tiêu đề dạng "A: B" | Đa dạng: câu khẳng định, câu hỏi, một cụm từ |
| Gạch ngang " – " nối ý ở khắp nơi | Dấu phẩy, dấu chấm, xuống dòng. Giữ "–" cho khoảng số (2025–2026) |
| Ba gạch đầu dòng dài đúng bằng nhau, cùng bắt đầu bằng động từ | Hai hoặc bốn ý; độ dài khác nhau; có ý là một câu trọn vẹn |
| "Không chỉ… mà còn…", "Hãy cùng…", "Trong bối cảnh…", "ngày càng…" | Nói thẳng ý chính |
| Từ sáo rỗng: toàn diện, nâng tầm, bứt phá, đột phá, hành trình, kỷ nguyên mới, chìa khoá vàng, tối ưu hoá, giải pháp tối ưu, đóng vai trò quan trọng, mang lại hiệu quả | Động từ cụ thể + con số/bằng chứng ("giảm 20% sai số", "dùng trong 3 tiết") |
| Khẳng định mơ hồ: "nhiều", "đáng kể", "hiệu quả cao" | Số liệu thật hoặc ví dụ cụ thể; thiếu thì `[cần bổ sung]` |
| Lời kết "Cảm ơn quý vị đã lắng nghe", "Cảm ơn – Hỏi đáp" làm chữ chính | Slide cuối mang thông điệp cần nhớ hoặc lời mời hành động; lời cảm ơn, liên hệ để nhỏ. (Bài hành chính, lễ tiết có thể giữ "Trân trọng cảm ơn" theo thông lệ) |
| Câu mở "Trong thời đại 4.0…", "Thế giới đang thay đổi…" | Mở bằng câu hỏi, tình huống, con số của chính đề tài |
| Ký hiệu ✓ ✔ ➤ → ★ ● ■ gõ tay đầu dòng | Gạch đầu dòng chuẩn của PowerPoint (`bullet`) hoặc đánh số |

## 3. Công thức
Công thức gõ bằng chữ thường ("IC = β·IB", "(VCC − VC) / IC") là dấu hiệu làm vội và hiển thị sai trên máy khác. **Mọi công thức dùng khối Equation gốc của PowerPoint** qua `MS.equation(slide, "<LaTeX>", {...})` (xem `quy-trinh-pptx.md` §1b) hoặc bố cục `congThuc`. Giá trị đơn lẻ có đơn vị ("VCC = 12 V") được viết bằng chữ.

## 4. Tự hỏi trước khi bàn giao
1. Bỏ hết biểu tượng, slide có mất thông tin không? Không mất → bỏ.
2. Đổi tên đề tài, slide này dùng được cho bài khác không? Được → chưa đủ cụ thể.
3. Người trình bày có nói được câu tiêu đề này thành lời tự nhiên không?
4. Có chỗ nào nhìn giống mẫu tải sẵn hơn là bài của người này?
