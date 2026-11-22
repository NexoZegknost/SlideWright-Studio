# Ví dụ mẫu — presentation-script bản Gemini app

Bắt chước **cấu trúc, độ dài và giọng văn nói** của ví dụ. Nội dung chỉ để minh hoạ, không chép sang bài thật.

Bối cảnh ví dụ: tập huấn giáo viên, 15 phút, 8 slide, tốc độ 125 âm tiết/phút, người trình bày xưng "tôi", gọi người nghe là "thầy cô".

## 1. Bảng phân bổ thời gian

| Slide | Tiêu đề | Số nhịp | Giây | Cộng dồn |
|---|---|---|---|---|
| 1 | Tưới cây tự động bằng Arduino | 0 | 30 | 0:30 |
| 2 | Kỳ nghỉ dài, ai tưới cây cho lớp? | 1 | 60 | 1:30 |
| 3 | Bốn phần trong 15 phút | 4 | 60 | 2:30 |
| 4 | Đất khô thì bơm tự bật | 3 | 70 | 3:40 |
| … | … | … | … | … |
| 8 | Bắt đầu với một chậu cây của lớp | 1 | 90 | 15:00 |

Tổng 900 giây, khớp 15 phút.

## 2. Lời nói một slide

**Slide 4 — Đất khô thì bơm tự bật** · 70 giây · khoảng 135 âm tiết (135 ÷ 125 × 60 ≈ 65 giây, cộng 2 giây `[Dừng]` và thao tác chuyển ý)

[Mở] Thầy cô có thể hình dung cả hệ thống này chỉ làm đúng ba việc, việc này nối việc kia.

[Ý 1] Việc thứ nhất: cảm biến cắm xuống đất, đo độ ẩm và gửi một con số về chân A0 của Arduino. Đất càng khô, con số này càng lớn.

[Ý 2] Việc thứ hai: Arduino đem con số đó so với một ngưỡng mà mình cài sẵn trong chương trình. Ở đây tôi để ngưỡng ba mươi lăm phần trăm. [Dừng]

[Ý 3] Việc thứ ba: hễ đất khô hơn ngưỡng, Arduino bật relay, relay đóng mạch và bơm chạy. Đất đủ ẩm thì bơm tự tắt.

[Nhấn] ngưỡng cài sẵn

[Chuyển] Nhưng ngưỡng ba mươi lăm phần trăm chỉ đúng khi cảm biến đã được hiệu chuẩn — và đó là việc học sinh hay bỏ qua nhất.

*Vì sao đạt:* số nhịp `[Ý]` = 3 = số ý xuất hiện trên slide; không đọc lại nguyên câu trên slide mà giải thích thêm; câu ngắn (≤ 25 âm tiết); số liệu đọc thành lời ("ba mươi lăm phần trăm"); câu chuyển mang nội dung của slide sau.

**Slide 1 — Tưới cây tự động bằng Arduino** · 30 giây

[Mở] Kính chào quý thầy cô. Tôi là <họ tên>, giáo viên Công nghệ trường <tên trường>.

[Chuyển] Hôm nay tôi chia sẻ một dự án học sinh lớp tám tự lắp được trong hai tiết, bắt đầu từ một chuyện rất quen ở trường mình.

## 3. Hỏi đáp mẫu

**Hỏi:** Trường không có phòng thí nghiệm riêng thì làm dự án này thế nào?
**Trả lời (40 giây):** Vẫn làm được ngay trong lớp học. Cả bộ thiết bị nằm gọn trong một hộp nhựa, chạy bằng pin, không cần ổ điện. Chậu cây đặt ở bậu cửa sổ là đủ. Điều duy nhất cần chuẩn bị là một lần hiệu chuẩn cảm biến với đất thật của chậu cây đó.
**Dùng slide:** 5, 6. **Nguồn:** kinh nghiệm triển khai, không có số liệu cần dẫn.

## 4. Thẻ nhắc

| Slide | Từ khoá | Câu chuyển |
|---|---|---|
| 4 | đo · so ngưỡng · bật bơm | Ngưỡng chỉ đúng khi đã hiệu chuẩn |

## 5. Sai → đúng

| Sai | Đúng |
|---|---|
| "Slide này nói về nguyên lý hoạt động vòng kín của hệ thống." | Vào thẳng nội dung: "Cả hệ thống chỉ làm đúng ba việc…" |
| Đọc lại nguyên văn: "Thu thập tín hiệu, xử lý và so sánh, thực thi đóng ngắt." | Giải thích bằng lời nói thường, mỗi ý một nhịp |
| "Kính thưa quý thầy cô" ở giữa bài | Chỉ ở lời mở và lời kết |
| "Tiết kiệm 40–60% nước" không có nguồn | Ghi nguồn; không có thì `[cần bổ sung nguồn]` |
