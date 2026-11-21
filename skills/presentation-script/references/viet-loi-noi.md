# Viết lời nói cho bài thuyết trình

Lời nói là thứ người nghe nhận được; slide chỉ là điểm tựa cho mắt. Kịch bản viết để **nói ra thành tiếng**, không phải để đọc.

## 1. Ngôn ngữ nói, không phải văn viết
1. **Câu ngắn**: 12–25 âm tiết mỗi câu; quá 35 âm tiết thì tách (người nói hết hơi, người nghe mất mạch).
2. **Chủ ngữ rõ, động từ mạnh**: "Năm nay toàn tỉnh tăng 12 trường đạt chuẩn", không phải "Việc gia tăng số lượng trường đạt chuẩn đã được ghi nhận".
3. **Số liệu nói được**: làm tròn khi chi tiết không cần ("gần 3.000 học sinh" thay cho "2.987 học sinh"); một câu không quá hai con số; số lớn đi kèm so sánh ("tức là cứ 10 em thì có 7 em").
4. **Viết tắt đọc thành lời** ở lần đầu: "Sở Giáo dục và Đào tạo", sau đó mới "Sở"; ký hiệu văn bản đọc rõ số hiệu ("Công văn số 1234 của Bộ").
5. **Không đọc lại slide**. Slide ghi từ khoá, lời nói giải thích, cho ví dụ, nói ý nghĩa. Được nhắc đúng từ khoá in đậm trên slide (để người nghe khớp mắt – tai), không đọc nguyên câu.
6. **Xưng hô theo bối cảnh**:
   | Bối cảnh | Mở lời | Xưng – gọi |
   |---|---|---|
   | công sở, hội nghị, lễ | "Kính thưa…" (một lần, đầu bài; đủ thứ bậc khách mời người dùng cung cấp) | tôi – quý vị đại biểu / các đồng chí |
   | tập huấn | chào ngắn, giới thiệu bản thân một câu | tôi – thầy cô / anh chị |
   | giảng dạy | câu hỏi hoặc tình huống | cô/thầy – các em |
   | học sinh, sinh viên, bảo vệ | "Kính thưa hội đồng / thầy cô…" | em/chúng em – thầy cô |
   | thi, pitch | câu móc (con số, câu hỏi, câu chuyện ngắn) trong 15 giây đầu | chúng tôi – ban giám khảo |
   Không lặp "Kính thưa" ở giữa bài.

## 2. Cấu trúc từng slide
```
[Mở]    1 câu dẫn: vì sao slide này quan trọng / nối từ ý trước.
[Nhấp n] mỗi cú nhấp trên slide = một nhịp lời nói, nói KHI nội dung đó hiện ra.
[Nhấn]  1–3 từ khoá trùng điểm nhấn trên slide; nhấn giọng, có thể dừng ngắn trước.
[Chuyển] 1 câu nối sang slide sau (câu hỏi, hệ quả, "vậy làm thế nào để…").
```
- Số nhịp **bằng đúng** số cú nhấp của slide (đọc từ `slide.json`). Slide không có hiệu ứng: một nhịp duy nhất.
- Chèn chỉ dẫn diễn xuất trong ngoặc vuông khi cần, ngắn: `[Dừng]` (2 giây), `[Nhìn khán giả]`, `[Chậm]`, `[Hỏi]` (hỏi khán giả, chờ trả lời). Tối đa 2 chỉ dẫn mỗi slide.
- Câu chuyển không lặp một kiểu ("Tiếp theo…", "Sau đây…" liên tục). Ưu tiên câu chuyển mang nội dung: "Con số này đặt ra một câu hỏi: vì sao vùng sâu vẫn thấp hơn?"

## 3. Nhịp toàn bài
- **Mở đầu (≈ 10%)**: chào – lý do – lời hứa của bài ("Sau 15 phút, quý vị sẽ thấy ba việc cần làm ngay"). Không mở bằng xin lỗi hay "em xin phép trình bày".
- **Thân bài (≈ 80%)**: mỗi phần lớn có câu chốt khi kết thúc phần; sau 3–4 slide nặng số liệu có một câu tóm hoặc ví dụ đời thường.
- **Kết (≈ 10%)**: nhắc lại 1–3 thông điệp, kiến nghị/lời kêu gọi cụ thể, cảm ơn một câu. Không kết bằng "Bài trình bày của tôi đến đây là hết".
- Tổng thời lượng lệch mục tiêu tối đa ±5%. Dài hơn: cắt ví dụ phụ, gộp nhịp, đưa chi tiết sang hỏi đáp. Ngắn hơn: thêm ví dụ, câu chuyện, câu hỏi tương tác — không thêm số liệu không có nguồn.

## 4. Tốc độ và thời lượng
- Mặc định 130 âm tiết/phút (khoảng hơi chậm hơn nói chuyện thường); hội nghị, giảng dạy 120; pitch 145. Người dùng nói "tôi nói nhanh/chậm" → chỉnh `toc_do` ±15.
- Thời lượng mỗi slide lấy từ `giay_de_xuat` của `doc_slide.py` (bìa 30 s, chia phần 15 s, kết 20 s, phần còn lại chia theo số cú nhấp và lượng chữ); người dùng giao thời gian từng phần thì theo người dùng.
- Ước tính: âm tiết ÷ tốc độ + 2 s mỗi `[Dừng]` + 0,5 s mỗi cú nhấp. Con số tính theo cách đọc (2025 ≈ 7 âm tiết).

## 5. Tránh dấu hiệu văn AI
Không dùng: "Hãy cùng khám phá", "hành trình", "không chỉ… mà còn…" lặp lại, "đóng vai trò quan trọng", "chìa khoá", "bức tranh toàn cảnh", "trong bối cảnh hiện nay", "một cách hiệu quả", ba tính từ liền nhau, câu hỏi tu từ ở mọi slide, lời kết "Xin chân thành cảm ơn quý vị đã lắng nghe" kèm lời chúc dài. Viết như người trình bày thật sẽ nói: cụ thể, có tên người, tên trường, con số, việc đã làm.

## 6. Trung thực với nguồn
- Mọi số liệu, tên văn bản, trích dẫn trong lời nói phải có trong tài liệu người dùng hoặc nguồn đã tra; thiếu thì ghi `[cần bổ sung]` và báo.
- Không tự thêm kết quả, thành tích, cam kết thay người trình bày.
- Ví dụ minh hoạ tự nghĩ ra (tình huống giả định) phải nói rõ là giả định: "Giả sử một lớp có 40 em…".
