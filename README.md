<p align="center">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="assets/branding/logo.png">
    <img src="assets/branding/logo.png" alt="Logo SlideWright - Studio" width="128" height="128">
  </picture>
</p>

<h1 align="center">SlideWright - Studio</h1>

Plugin cho Claude giúp tạo bài thuyết trình tiếng Việt chuyên nghiệp: dựng mới từ chủ đề hoặc tài liệu, nâng cấp bài có sẵn, và chuyển PDF thành PowerPoint giữ nguyên bản gốc. Gói plugin chứa hai skill: **makeSlides** (dựng slide) và **presentationScript** (kịch bản thuyết trình).

Phiên bản hiện tại: **2.0.0-beta.4** · [Lịch sử thay đổi](CHANGELOG.md)

## Tính năng

- **Ba chế độ:** tạo mới, nâng cấp bài có sẵn, chuyển PDF sang PowerPoint giữ nguyên nền, phông, màu và hình.
- **Ba đầu ra:** PowerPoint (`.pptx` và `.ppsx`, mặc định), Canva hoặc Gamma.
- **Phong cách theo đề tài và bối cảnh trình bày:** Claude đề xuất 3 phương án về màu, phông, texture, bố cục để bạn chọn.
- **Hiệu ứng và chuyển trang Morph:** hiệu ứng đủ bốn nhóm, cảnh morph xuyên suốt bài.
- **Chữ tiếng Việt chuẩn:** phông đủ dấu nhúng sẵn trong file, công thức là khối Equation gốc của PowerPoint.
- **Thiết kế trên Canva có kiểm soát:** Canva AI dựng khung, Claude kiểm tra cỡ chữ, chữ đè, khung hẹp, lệch chân chữ, màu, nội dung ngoài dàn ý, chính tả ngay trên thiết kế rồi sửa trực tiếp (thiết kế tĩnh, cần hiệu ứng thì dùng bản PowerPoint).
- **Kiểm soát văn bản toàn diện:** phông (nhúng, thiếu ký tự, đậm/nghiêng giả), mã chữ (NFD, TCVN3, ký tự ẩn), chính tả âm tiết tiếng Việt, dấu câu, viết hoa tên cơ quan, chữ hiển thị thật khi dựng; tự sửa phần không đổi câu chữ.
- **Kịch bản thuyết trình (presentationScript):** lời nói đầy đủ cho từng slide, khớp từng cú nhấp hiệu ứng, chia thời gian theo tổng thời lượng và tốc độ nói, chuẩn bị câu hỏi đáp dự kiến; ghi vào ghi chú diễn giả và xuất bản in Word kèm thẻ nhắc.
- **Tự kiểm tra trước khi bàn giao:** cỡ chữ, lượng chữ, xuống dòng, tràn khung, tương phản, phối màu và dấu hiệu slide do AI làm.

## Cài đặt

**Claude Code**

```
/plugin marketplace add NexoZegknost/SlideWright-Studio
/plugin install slidewright-studio@slidewright-studio
```

**Ứng dụng Claude (Cowork):** tải tệp `.plugin` ở mục Releases của kho này, mở tệp và bấm chấp nhận.

Sau khi cài, mở một phiên trò chuyện mới để plugin được nạp.

**Gemini CLI** (chỉ xuất PowerPoint, chưa hỗ trợ Canva và Gamma)

```
gemini extensions install https://github.com/NexoZegknost/SlideWright-Studio
cd ~/.gemini/extensions/slidewright-studio
npm install
pip install -r requirements.txt
```

Máy cần có Node.js 18+, Python 3, LibreOffice và poppler (`pdftoppm`). Nếu Gemini CLI chưa nạp skill, gõ `/settings`, tìm "Skills" và bật Agent Skills. Cập nhật bằng `gemini extensions update slidewright-studio`. Cách skill chạy trên Gemini được ghi trong `GEMINI.md`.

**Gemini app** (gemini.google.com, ứng dụng Gemini trên Mac và điện thoại; dựng bằng công cụ slide của Gemini)

1. Ở mục Releases, tải hai tệp `slidewright-make-slides-gemini-app-<phiên bản>.zip` và `slidewright-presentation-script-gemini-app-<phiên bản>.zip`.
2. Trong Gemini, mở trang **Skills** → **Create** → **Upload**, chọn từng tệp .zip.
3. Lên bản mới: mở skill → **More** → **Replace skill**, chọn tệp .zip mới. Số phiên bản đang dùng ghi ở đầu nội dung skill.

Gemini app không nạp skill có kèm mã chạy được, nên bản này chỉ gồm chỉ dẫn và tệp quy tắc: Gemini dựng slide bằng công cụ có sẵn của nó theo đúng ràng buộc trình bày của SlideWright (màu theo lĩnh vực, cỡ chữ theo bối cảnh, bố cục, chống dấu hiệu AI). Tải về PowerPoint qua Google Slides; không có Morph, hiệu ứng theo cú nhấp, Canva, Gamma — cần các phần này thì dùng bản Claude hoặc Gemini CLI. Mẹo: mở đầu câu lệnh bằng "Dùng skill make-slides:".

## Yêu cầu

- **PowerPoint 2016 trở lên** để xem hiệu ứng; chuyển trang Morph cần PowerPoint 2019 hoặc Microsoft 365.
- **Node.js, Python 3 và LibreOffice** để dựng và kiểm tra slide; Claude tự chạy trong phiên. Danh sách lệnh cài thư viện nằm trong `skills/make-slides/references/quy-trinh-pptx.md`.
- **Kết nối Gamma hoặc Canva** (tuỳ chọn): chỉ khi chọn đầu ra tương ứng, đăng nhập bằng tài khoản của bạn.

## Cách dùng

Nói với Claude bằng ngôn ngữ tự nhiên; skill tự chạy khi bạn nhắc đến "tạo slide", "làm bài thuyết trình", "makeSlides", "nâng cấp slide", "chuyển PDF sang PowerPoint"… Muốn chọn công cụ thì nói thêm "bằng Canva", "trên Gamma" hoặc "bằng PowerPoint".

| Yêu cầu | Chế độ |
|---|---|
| "Làm slide báo cáo sơ kết học kỳ I môn Ngữ văn" (kèm file số liệu) | Tạo mới |
| "Thiết kế lại file này cho ấn tượng hơn" (kèm `.pptx`) | Nâng cấp |
| "Chuyển PDF này sang PowerPoint, giữ nguyên, thêm hiệu ứng xuất hiện" | Chuyển đổi nguyên bản |
| "Làm luôn, xuất file hoàn chỉnh" | Bỏ qua các bước duyệt |
| "Viết kịch bản thuyết trình 15 phút cho bộ slide này" (kèm `.pptx`) | Kịch bản thuyết trình |

**Quy trình:** nêu yêu cầu → chọn phong cách trong ba phương án → duyệt dàn ý → Claude dựng và tự kiểm tra → nhận file `.pptx` và `.ppsx` (hoặc link Canva, Gamma). Ở chế độ "làm luôn", hai bước chọn phong cách và duyệt dàn ý được bỏ qua.

## Lưu ý

- Hiệu ứng và Morph chỉ chạy khi trình chiếu trong PowerPoint; ảnh xem trước tĩnh không thể hiện chúng.
- Khi sửa và lưu lại trong PowerPoint, giữ tuỳ chọn *Embed fonts in the file* để phông không bị mất.
- Tài nguyên thương hiệu Trường Đại học Bách khoa – ĐHQG-HCM chỉ dùng khi bạn yêu cầu, cho báo cáo, thuyết trình tại trường hoặc khi được phép.
- Bộ phông đi kèm dùng giấy phép SIL Open Font License; tệp giấy phép nằm cạnh từng họ phông.
- Báo lỗi hoặc góp ý qua mục Issues của kho.