# Nội dung trên slide: khái quát và tập trung điểm nhấn

Slide **không phải là bài nói**. Slide chỉ giữ phần khái quát, tổng quát hoá để người xem nhìn một lần là nắm ý, rồi **dồn sự chú ý vào người trình bày**. Mọi phần giải thích, dẫn chứng, ví dụ chi tiết nằm trong lời nói và **ghi chú diễn giả**.

## 1. Quy tắc khái quát hoá
1. **Một slide – một thông điệp**: tiêu đề là câu kết luận ngắn (≤ 12 từ).
2. **Từ khoá thay cho câu**: mỗi ý trên slide là cụm từ 2–7 chữ, bắt đầu bằng danh từ hoặc động từ mạnh ("Đọc mở rộng theo nhóm", không phải "Chúng ta cần tổ chức cho học sinh đọc mở rộng theo nhóm").
3. **Quy tắc ba**: tối đa 3 ý chính mỗi slide (tối đa 4–5 khi là các bước của quy trình). Nhiều hơn → tách slide hoặc gộp thành nhóm cấp cao hơn.
4. **Tổng quát hoá trước, chi tiết sau**: gộp các ý cùng loại dưới một khái niệm chung (ví dụ năm hoạt động cụ thể → "Ba nhóm giải pháp: Đọc · Hợp tác · Đánh giá"); chi tiết từng hoạt động đưa vào ghi chú.
5. **Con số thay cho đoạn văn**: số liệu trình bày bằng một con số lớn + nhãn ngắn hoặc biểu đồ; giải thích nằm trong lời nói.
6. **Hình ảnh và sơ đồ thay cho mô tả**: quan hệ, quy trình, so sánh → sơ đồ, mũi tên, hai cột.
7. **Giới hạn theo bối cảnh**: số dòng, số chữ tối đa lấy từ `contexts.json` (riêng bối cảnh *gửi đọc trước* được viết câu đầy đủ).
8. **Không chép nguyên văn tài liệu lên slide**. Ngoại lệ: trích dẫn, điều khoản văn bản, câu thơ — giữ nguyên văn, ngắn, ghi nguồn.

## 2. Điểm nhấn (highlight)
Mỗi slide có **đúng 1–3 điểm nhấn** — từ khoá, con số hoặc cụm từ mà người xem phải nhớ.
- Đánh dấu trong nội dung bằng `**…**` khi dùng `layouts.js`: cụm được tự in đậm và đổi sang màu nhấn đúng tương phản (nền sáng dùng `accentText`, nền tối dùng `accentOnDark`). Ví dụ: `"Học sinh **khám phá**"`.
- Điểm nhấn ưu tiên: **con số**, **động từ hành động**, **khái niệm then chốt**, **kết luận**.
- Không nhấn quá 3 cụm/slide và không nhấn cả câu — nhấn nhiều là không nhấn gì.
- Điểm nhấn trên slide phải trùng với từ khoá trong lời nói (ghi trong ghi chú diễn giả: "[Nhấn] khám phá").
- Điểm nhấn quan trọng nhất của slide được gắn **hiệu ứng chờ** (xem `hieu-ung.md` mục Hiệu ứng chờ).

## 3. Ghi chú diễn giả (bắt buộc với mọi slide nội dung)
Phần chi tiết bị lược khỏi slide chuyển vào ghi chú theo mẫu:
```
[Mở] Câu dẫn vào slide (1 câu).
[Nhấp 1] Ý 1 – giải thích, ví dụ, số liệu chi tiết.
[Nhấp 2] Ý 2 – …
[Nhấn] Từ khoá cần nhấn giọng.
[Chuyển] Câu nối sang slide sau.
```

## 4. Văn bản đọc được và hài hoà (kiểm bằng `scripts/kiem_tra_van_ban.py`)
1. **Cỡ chữ**: chữ nội dung **≥ 24pt** (bối cảnh có `body_min` cao hơn thì theo bối cảnh); chữ phụ (nguồn, chú thích, nhãn) ≥ 16pt; tiêu đề ≥ 1,25 × chữ nội dung và cùng cỡ trong cả bài; ≤ 4 cỡ chữ mỗi slide. `layouts.setScale(body_min)` tự nâng mọi chữ lên mức tối thiểu — khung giữ nguyên nên **phải bớt chữ**, không thu nhỏ chữ.
2. **Lượng chữ**: ≤ 30 chữ nội dung mỗi slide (bối cảnh thuyết trình), mỗi ý ≤ 2 dòng, mỗi khung ≤ 5 dòng. Thừa chữ → chuyển vào ghi chú diễn giả.
3. **Giãn dòng**: 90–140% cho đoạn, 85–115% cho tiêu đề.
4. **Xuống dòng phải giữ nghĩa** (dù tự động hay chủ ý):
   - không tách từ ghép qua hai dòng (hành | vi, học | tập, sinh | viên);
   - không để dòng kết thúc bằng hư từ (của, và, với, các, những, cho, để, khi, từ, là, mỗi…) — hư từ đứng **đầu** dòng sau;
   - không tách số – đơn vị, ký hiệu – số (12 V, 2 mA, CV 7991): nối bằng khoảng trắng không ngắt `\u00A0`;
   - ngắt chủ ý (xuống dòng bằng tay) chỉ đặt ở ranh giới cụm từ hoặc sau dấu câu, không làm câu đổi nhịp, đổi nghĩa.
5. **Tiêu đề hai dòng**: dòng trên **ngắn hơn**, dòng dưới dài hơn ("Mạng xã hội / và hành vi học tập của sinh viên"), điểm ngắt ở ranh giới cụm. Không tìm được điểm ngắt đẹp → viết lại tiêu đề.
6. **Không để dòng quá ngắn**: dòng cuối đoạn chỉ còn 1 chữ (hoặc ≤ 2 chữ, < 20% bề rộng), dòng ngắn lọt giữa đoạn. Khắc phục theo thứ tự: giảm cỡ chữ (không dưới mức tối thiểu) → rút gọn câu → kéo dài câu cho dòng cuối đầy hơn.
7. **Tiêu đề không sáo rỗng kiểu đếm số**: tránh "Ba phương pháp…", "Ba con số đáng chú ý", "4 phần trong lộ trình", "Những điểm nổi bật". Viết thông điệp: "Sinh viên dành gần ba giờ mỗi ngày cho mạng xã hội", "Tụ CE nâng độ lợi lên 50 lần".

Chạy: `python3 scripts/kiem_tra_van_ban.py <file>.pptx --sua <file>_sua.pptx` — tự sửa phần sửa được mà không đổi câu chữ (giảm cỡ trong giới hạn, chèn ngắt dòng đúng ranh giới cụm cho tiêu đề, nối số – đơn vị), rồi báo phần còn lại kèm gợi ý số chữ cần bớt/thêm. Sửa nội dung trong script dựng, dựng lại, chạy lại đến khi hết LỖI.

## 5. Tự kiểm tra
- [ ] Người xem đọc hết chữ trên slide trong ≤ 5 giây (bối cảnh trình bày trực tiếp).
- [ ] `kiem_tra_van_ban.py` hết LỖI: cỡ ≥ 24pt, ≤ 30 chữ, không dòng mồ côi, không tách từ ghép, tiêu đề 2 dòng trên ngắn dưới dài.
- [ ] Không còn câu dài hơn một dòng ở phần nội dung (trừ trích dẫn).
- [ ] Mỗi slide có 1–3 điểm nhấn, không quá.
- [ ] Mọi nội dung đã lược đều có trong ghi chú diễn giả.

## Ví dụ chuyển đổi
| Văn bản gốc | Trên slide |
|---|---|
| "Trong năm học qua, nhờ việc đổi mới kiểm tra đánh giá theo hướng phát triển năng lực, tỉ lệ học sinh đạt yêu cầu môn Ngữ văn đã tăng từ 86% lên 92%." | Số lớn **92%** · nhãn "đạt yêu cầu môn Ngữ văn" · dòng nhỏ "+6 điểm % so với năm trước" |
| "Giáo viên cần tổ chức cho học sinh đọc theo nhóm, mỗi nhóm chọn một tác phẩm cùng thể loại, trình bày sản phẩm bằng sơ đồ và được phản hồi theo tiêu chí." | Tiêu đề "Đọc mở rộng theo nhóm" · 3 ý: "Chọn **một tác phẩm**" · "Trình bày bằng **sơ đồ**" · "Phản hồi theo **tiêu chí**" |
