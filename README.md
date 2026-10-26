<p align="center">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="assets/branding/logo.png">
    <img src="assets/branding/logo.png" alt="Logo SlideWright - Studio" width="128" height="128">
  </picture>
</p>

<h1 align="center">SlideWright - Studio</h1>

Plugin cho Claude giúp tạo bài thuyết trình tiếng Việt chuyên nghiệp: dựng mới từ chủ đề hoặc tài liệu, nâng cấp bài có sẵn, và chuyển PDF thành PowerPoint giữ nguyên bản gốc. Gói plugin chứa skill **makeSlides**.

Phiên bản hiện tại: **0.14.3** · [Lịch sử thay đổi](CHANGELOG.md)

## Tính năng

- **Ba chế độ:** tạo mới, nâng cấp bài có sẵn, chuyển PDF sang PowerPoint giữ nguyên nền, phông, màu và hình.
- **Ba đầu ra:** PowerPoint (`.pptx` và `.ppsx`, mặc định), Canva hoặc Gamma.
- **Phong cách theo đề tài và bối cảnh trình bày:** Claude đề xuất 3 phương án về màu, phông, texture, bố cục để bạn chọn.
- **Hiệu ứng và chuyển trang Morph:** hiệu ứng đủ bốn nhóm, cảnh morph xuyên suốt bài.
- **Chữ tiếng Việt chuẩn:** phông đủ dấu nhúng sẵn trong file, công thức là khối Equation gốc của PowerPoint.
- **Tự kiểm tra trước khi bàn giao:** cỡ chữ, lượng chữ, xuống dòng, tràn khung, tương phản, phối màu và dấu hiệu slide do AI làm.

## Cài đặt

**Claude Code**

```
/plugin marketplace add NexoZegknost/SlideWright-Studio
/plugin install slidewright-studio@slidewright-studio
```

**Ứng dụng Claude (Cowork):** tải tệp `.plugin` ở mục Releases của kho này, mở tệp và bấm chấp nhận.

Sau khi cài, mở một phiên trò chuyện mới để plugin được nạp.

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

**Quy trình:** nêu yêu cầu → chọn phong cách trong ba phương án → duyệt dàn ý → Claude dựng và tự kiểm tra → nhận file `.pptx` và `.ppsx` (hoặc link Canva, Gamma). Ở chế độ "làm luôn", hai bước chọn phong cách và duyệt dàn ý được bỏ qua.

## Lưu ý

- Hiệu ứng và Morph chỉ chạy khi trình chiếu trong PowerPoint; ảnh xem trước tĩnh không thể hiện chúng.
- Khi sửa và lưu lại trong PowerPoint, giữ tuỳ chọn *Embed fonts in the file* để phông không bị mất.
- Tài nguyên thương hiệu Trường Đại học Bách khoa – ĐHQG-HCM chỉ dùng khi bạn yêu cầu, cho báo cáo, thuyết trình tại trường hoặc khi được phép.
- Bộ phông đi kèm dùng giấy phép SIL Open Font License; tệp giấy phép nằm cạnh từng họ phông.
- Báo lỗi hoặc góp ý qua mục Issues của kho.