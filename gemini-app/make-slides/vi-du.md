# Ví dụ mẫu — make-slides bản Gemini app

Bắt chước **cấu trúc và mức chi tiết** của các ví dụ dưới đây. Nội dung trong ví dụ chỉ để minh hoạ định dạng: **không chép sang bài thật**.

Đề tài ví dụ: bài giảng Ngữ văn 10 *Trao duyên* (trích *Truyện Kiều*), bối cảnh **giảng dạy**: tiêu đề ≥ 64 px, nội dung ≥ 43 px, chữ phụ ≥ 32 px (khung Canvas 1280 × 720), `max_words` 30, `sec_per_slide` 120; 20 phút trình chiếu → 10 slide.
Lĩnh vực `nhan-van`, phương án 1 — dùng đúng mã màu và cặp phông `phong_goc` (Playfair Display + Lora) trong `assets/phuong-an.json`. Dưới đây gọi màu theo tên khoá (`dark`, `accent`…).

## 1. Dàn ý (Bước 3)

| # | Bố cục | Tiêu đề (nhận định) | Ý chính | Yếu tố thị giác |
|---|---|---|---|---|
| 1 | Bìa chữ lớn | Trao duyên | Trích *Truyện Kiều*, Nguyễn Du | khối `accent` đứng mép phải |
| 2 | Câu hỏi lớn | Khi phải chọn giữa tình và hiếu, em chọn gì? | Khởi động | câu hỏi chiếm cả slide |
| 3 | Dòng chảy | Một đêm, ba lần đổi giọng | nhờ cậy, trao kỷ vật, độc thoại | đường ngang 3 mốc |
| 4 | Câu thơ lớn | Kiều lạy em như lạy người ân | "Cậy em, em có chịu lời, / Ngồi lên cho chị lạy rồi sẽ thưa." | câu thơ cỡ lớn |
| 5 | Chia đôi màu | Kiều thuyết phục bằng lý trước, tình sau | gia biến, tình máu mủ, cái chết | nửa trái khối `dark` |
| 6 | Từ khoá lớn | Trao kỷ vật mà không trao được lòng | "của chung", "của tin" | hai từ khoá rất lớn so le |
| 7 | Ảnh tràn nửa | Kiều tự thấy mình là người đã khuất | hồn oan, dạ đài | ảnh đêm trăng tràn nửa trái |
| 8 | Đối lập | Lý trí nói "trao", tình cảm nói "giữ" | hai nửa `soft` và `light` | ranh giới màu |
| 9 | Bảng gọn | Ba chặng tâm trạng trong 34 câu thơ | đoạn, hướng tới ai, cảm xúc | kẻ ngang mảnh |
| 10 | Kết | Hi sinh vì người khác là vẻ đẹp của Kiều | viết đoạn văn 150 chữ | nền `dark` |

10 slide, 10 bố cục khác nhau; nền tối: slide 1, 10 và nửa slide 5 (dưới một nửa). Không slide nào có nhãn phía trên tiêu đề, không số phút.

## 2. Slide hoàn chỉnh (Bước 4–5)

### Slide 1 — Bìa chữ lớn
- **Nền:** `dark` phủ kín.
- **Khối xuyên suốt:** hình chữ nhật `accent`, rộng 180 px, cao hết slide, sát mép phải.
- **Tiêu đề:** "Trao duyên" — Playfair Display 140 px đậm, `light`, căn trái, đặt ở một phần ba dưới slide.
- **Phụ đề:** "Trích *Truyện Kiều*, Nguyễn Du" — Lora 43 px, `accentOnDark`, ngay dưới tiêu đề.
- **Không có:** nhãn "NGỮ VĂN LỚP 10 • ĐỌC HIỂU VĂN BẢN", dòng "Tiết 45 phút".
- **Ghi chú:** `[Mở] Hôm nay cô trò mình đọc một đoạn thơ mà Nguyễn Du viết như một đêm không ngủ. [Chuyển] Trước khi đọc, cô hỏi các em một câu.`

### Slide 4 — Câu thơ lớn
- **Nền:** `light`.
- **Khối xuyên suốt:** vạch `accent` ngang, rộng 120 px, dày 10 px, ngay trên tiêu đề (cùng chỗ ở mọi slide nội dung).
- **Tiêu đề:** "Kiều lạy em như lạy người ân" — Playfair Display 64 px đậm, `text`, góc trên trái.
- **Câu thơ:** "Cậy em, em có chịu lời, / Ngồi lên cho chị lạy rồi sẽ thưa." — Lora 72 px nghiêng, `text`, hai dòng, chiếm giữa slide; vạch đứng mảnh `accent` bên trái câu thơ. Hai chữ "Cậy", "lạy" màu `accentText`.
- **Lời bình:** "Chị đổi vai thành người mắc nợ" — Lora 43 px, `muted`, dưới câu thơ.
- **Đếm chữ:** 28 ≤ 30. Không hộp quanh câu thơ, không dấu ngoặc kép trang trí khổng lồ.
- **Ghi chú:** `[Mở] Hai câu đầu, Kiều chưa nói việc gì đã lạy em. [Ý] "Cậy" là nhờ mà tin, "chịu" là nhận mà thiệt. [Nhấn] cậy, lạy. [Chuyển] Lạy rồi, Kiều mới bắt đầu giãi bày.`

### Slide 5 — Chia đôi màu
- **Nửa trái (0–560 px):** khối `dark` tràn mép trên, dưới, trái — chính là khối xuyên suốt, nay phủ nửa slide. Trong khối: "Lý trước, tình sau" — Playfair Display 72 px đậm, `light`.
- **Nửa phải:** nền `light`; tiêu đề "Kiều thuyết phục bằng lý trước, tình sau" — Playfair Display 64 px; ba ý Lora 43 px `text`, cách nhau bằng khoảng trắng 32 px, không biểu tượng đầu dòng:
  - Gia biến buộc phải bán mình
  - Em còn **tuổi xuân**
  - Chị chết cũng ngậm cười
- **Đếm chữ:** 28 ≤ 30.

## 3. Bảng hiệu ứng mẫu (Bước 7)

| Slide | Đối tượng | Hiệu ứng | Nhấp |
|---|---|---|---|
| 4 | Câu thơ dòng 1 | Xuất hiện dần | 1 |
| 4 | Câu thơ dòng 2 | Xuất hiện dần | 2 |
| 4 | Lời bình | Bay vào từ trái | 3 |
| 5 | Ba ý bên phải | Xuất hiện dần, từng đoạn | 1–3 |

Chuyển trang: Morph cho mọi slide — khối `accent`/`dark` đổi từ cột đứng (slide 1) sang vạch ngang (slide 4) sang nửa slide (slide 5).

## 4. Sai → đúng (các lỗi đã gặp)

| Sai | Đúng |
|---|---|
| Nhãn "II. ĐỌC HIỂU CHI TIẾT • 12 CÂU ĐẦU" trên tiêu đề | Bỏ nhãn; chỉ có tiêu đề nhận định |
| "Tiết 45 phút • Trình chiếu trọng tâm 20 phút", "KHỞI ĐỘNG (3 PHÚT)" | Không ghi thời lượng trên slide |
| Mỗi ý nằm trong một thẻ trắng bo góc có đổ bóng | Ý đặt trực tiếp trên nền, tách bằng khoảng trắng, vạch mảnh hoặc khối màu lớn |
| Biểu tượng trái tim, cái cân, sách, nốt nhạc trên mỗi thẻ | Không biểu tượng; dùng chữ lớn, chữ số lớn, màu |
| Số thứ tự trong vòng tròn nối bằng mũi tên | Dòng chảy: mốc là chữ đậm trên một đường mảnh |
| Tiêu đề 36 px, chữ thẻ 18 px (tức 27 pt và 13,5 pt khi xuất PowerPoint) | Tiêu đề ≥ 64 px, nội dung ≥ 43 px |
| "Nhờ cậy em – Trao kỷ vật – Nỗi đau tuyệt vọng" | Ba mốc tách riêng trên dòng chảy, không gạch nối |
| Dòng "NGỮ VĂN LỚP 10 • ĐỌC HIỂU VĂN BẢN" | Không chữ in hoa cả dòng, không dấu "•" |
| Phông Be Vietnam Pro cho nội dung | Đúng `phong_goc.body` của phương án (Lora) |
| Bốn slide liền nhau đều là tiêu đề + hàng 3–4 thẻ | Mỗi slide một bố cục khác slide trước; ≥ 6 bố cục cho 10 slide |
| Slide "Image Sources" với đường link ảnh | Không ghi nguồn ảnh trên slide |
| Ảnh không khớp nội dung câu thơ (sai loại đồ vật, nhạc cụ) | Ảnh đúng nội dung hoặc không dùng ảnh |
| Slide cuối chỉ "Cảm ơn quý Thầy Cô đã tham dự!" | Thông điệp chốt hoặc nhiệm vụ tiếp theo |
| Con số không nguồn ("Tiết kiệm 40–60% nước") | Nguồn trong ghi chú; không có nguồn thì bỏ con số |
| 12 slide cho 15 phút tập huấn | 900 giây ÷ 120 = 7–8 slide |
