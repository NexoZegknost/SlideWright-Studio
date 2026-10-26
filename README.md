# SlideWright Studio

Plugin cho Claude giúp tạo bài thuyết trình tiếng Việt chuyên nghiệp: dựng mới từ chủ đề hoặc tài liệu, nâng cấp bài có sẵn, và chuyển PDF thành PowerPoint giữ nguyên bản gốc. Plugin có tên kỹ thuật là `make-slides` (makeSlides).

Phiên bản hiện tại: **0.14.0-beta.2** (thử nghiệm) · bản ổn định: **0.13.0** · Lịch sử thay đổi: [CHANGELOG.md](CHANGELOG.md)

## Tính năng

- **Ba chế độ làm việc:** tạo mới, nâng cấp, chuyển PDF sang PowerPoint giữ nguyên nền, phông, màu và hình.
- **Ba đầu ra:** PowerPoint (`.pptx` và `.ppsx`, mặc định), Canva hoặc Gamma.
- **Định hướng phong cách theo đề tài:** tự nhận diện lĩnh vực (công nghệ, khoa học xã hội, hành chính, sư phạm, nghệ thuật…) và đề xuất 3 phương án về màu, phông, texture, bố cục.
- **Hiệu ứng đủ bốn nhóm:** mở đầu, nhấn mạnh, chờ (tự phát, lặp đến hết slide) và kết thúc.
- **Chuyển trang Morph làm chủ đạo:** cảnh morph xuyên suốt bài (vầng sáng trôi, băng màu xoay, mảnh hình bay, từ khoá trượt, thanh tiến độ) và các khoảnh khắc morph kể chuyện; chuyển trang lướt hiện đại cho chỗ đổi phần, không dùng kiểu cổ điển.
- **Chữ tiếng Việt chuẩn:** phông đủ dấu nhúng sẵn trong file, công thức là khối Equation gốc của PowerPoint.
- **Tự kiểm tra trước khi bàn giao:** cỡ chữ, lượng chữ, xuống dòng giữ nghĩa, tràn khung, lệch khung, tương phản và phối màu, dấu hiệu slide do AI làm; mô phỏng hiệu ứng theo đúng cách PowerPoint chạy và xem trước Morph bằng ảnh động.
- **Bối cảnh trình bày:** học sinh/sinh viên, công sở, hội nghị, bảo vệ đồ án, giảng dạy, tập huấn, trực tuyến, thi pitch, gửi đọc trước, trình chiếu tự động. Mỗi bối cảnh có cỡ chữ, mật độ nội dung và mức hiệu ứng riêng.
- **Văn bản hành chính:** khung slide cho báo cáo, kế hoạch, dự thảo; giữ đúng số hiệu văn bản.
- **Bộ nhận diện thương hiệu tuỳ chọn:** logo và hoạ tiết Trường Đại học Bách khoa – ĐHQG-HCM, chỉ dùng khi người dùng yêu cầu.

## Cài đặt

**Claude Code**

```
/plugin marketplace add NexoZegknost/SlideWright-Studio
/plugin install make-slides@slidewright-studio
```

**Ứng dụng Claude (Cowork):** tải tệp `.plugin` ở mục Releases của kho này, mở tệp và bấm chấp nhận.

Sau khi cài, mở một phiên trò chuyện mới để plugin được nạp.

## Yêu cầu

| Thành phần | Dùng cho |
|---|---|
| PowerPoint 2016 trở lên | Xem hiệu ứng; chuyển trang Morph cần PowerPoint 2019 hoặc Microsoft 365 (bản cũ hơn tự chuyển thành mờ dần) |
| Node.js, Python 3 | Môi trường chạy các script dựng và kiểm tra slide (Claude tự chạy trong phiên) |
| Thư viện Node: `pptxgenjs`, `jszip`, `fonteditor-core`, `mathjax-full@3`, `mathml2omml`, `sharp`, `opentype.js@1.3.4` | Dựng file, nhúng phông, công thức, đo chữ |
| Thư viện Python: `PyMuPDF`, `Pillow`, `pyvi` | Kiểm tra văn bản, kiểm tra bố cục, chuyển PDF |
| LibreOffice | Xuất ảnh xem trước và kiểm tra bố cục |
| Kết nối Gamma, Canva (tuỳ chọn) | Chỉ khi chọn đầu ra Canva hoặc Gamma; đăng nhập bằng tài khoản của bạn lần đầu, không cần khoá API |

Danh sách lệnh cài thư viện nằm trong `skills/make-slides/references/quy-trinh-pptx.md`.

## Cách dùng

Chỉ cần nói với Claude bằng ngôn ngữ tự nhiên; skill tự chạy khi bạn nhắc đến "tạo slide", "làm bài thuyết trình", "làm PowerPoint", "makeSlides", "nâng cấp slide", "chuyển PDF sang PowerPoint"… Muốn chọn công cụ thì nói thêm "bằng Canva", "trên Gamma" hoặc "bằng PowerPoint".

### Ví dụ

| Yêu cầu | Chế độ |
|---|---|
| "Làm slide báo cáo sơ kết học kỳ I môn Ngữ văn" (kèm file số liệu) | Tạo mới |
| "Slide bài giảng về hiệu ứng ánh đèn sân khấu trong tâm lý học, cho sinh viên" | Tạo mới |
| "Làm slide báo cáo ở Bách khoa, dùng tài nguyên BK" | Tạo mới với thương hiệu |
| "Thiết kế lại file này cho ấn tượng hơn" (kèm `.pptx`) | Nâng cấp |
| "Chuyển PDF này sang PowerPoint, giữ nguyên, thêm hiệu ứng xuất hiện" | Chuyển đổi nguyên bản |
| "Slide Canva cho hai dự thảo kế hoạch này" (kèm hai file Word) | Tạo mới, đầu ra Canva |
| "Làm luôn, xuất file hoàn chỉnh" | Bỏ qua các bước duyệt, Claude tự chọn phương án đề xuất |

### Quy trình làm việc

1. **Nêu yêu cầu:** đề tài hoặc tài liệu đính kèm (Word, PDF, ảnh, link), công cụ đầu ra nếu có.
2. **Chọn phong cách:** Claude gửi ảnh xem trước ba phương án để bạn chọn.
3. **Duyệt dàn ý:** bảng gồm tiêu đề, ý chính, bố cục, hình ảnh của từng slide; bạn xác nhận hoặc yêu cầu sửa.
4. **Claude dựng và tự kiểm tra:** theo dõi tiến độ qua danh sách công việc.
5. **Nhận bản hoàn chỉnh:** file `.pptx` và `.ppsx` (hoặc link Canva, Gamma), kèm tóm tắt hiệu ứng chính. Cần sửa thì nêu yêu cầu, Claude chỉnh và gửi lại.

Ở chế độ "làm luôn", bước 2 và 3 được bỏ qua.

## Nguyên tắc thiết kế

- Chữ nội dung từ 24 pt trở lên, tối đa 30 chữ mỗi slide; tiêu đề là thông điệp, không dùng tiêu đề đếm số sáo rỗng.
- Xuống dòng không tách từ ghép; tiêu đề hai dòng thì dòng trên ngắn hơn; không để dòng mồ côi.
- Không phối hai màu đối nhau (lam–cam, đỏ–lục, vàng–tím); không chữ tím trên nền tối; chữ màu trên nền tối đạt tương phản từ 7:1.
- Không biểu tượng hoặc emoji trước đoạn văn, không nhãn khuôn mẫu kiểu "Điểm chính".
- Bài chính quy chỉ dùng phông có chân hoặc không chân; phông trang trí chỉ cho bài kiểu cách. Không dùng Be Vietnam Pro.
- Hiệu ứng theo mạch nói của người trình bày; hiệu ứng chờ nhỏ, chậm, có khoảng nghỉ.

## Lưu ý

- Hiệu ứng, hiệu ứng chờ và Morph chỉ chạy khi trình chiếu trong PowerPoint; ảnh xem trước tĩnh không thể hiện chúng (Morph có bản xem trước bằng ảnh động gần đúng).
- Bản beta dùng để thử nghiệm; báo lỗi hoặc góp ý qua mục Issues của kho.
- Khi sửa và lưu lại trong PowerPoint, giữ tuỳ chọn *Embed fonts in the file* (đã bật sẵn) để phông không bị mất.
- Tài nguyên thương hiệu Bách khoa thuộc Trường Đại học Bách khoa – ĐHQG-HCM; chỉ dùng cho báo cáo, thuyết trình tại trường hoặc khi được phép.
- Bộ phông đi kèm (19 họ) dùng giấy phép SIL Open Font License; tệp giấy phép nằm cạnh từng họ phông.

## Phát hành phiên bản

1. Sửa mã và cập nhật `CHANGELOG.md`.
2. Tăng `version` trong `.claude-plugin/plugin.json` theo quy tắc semver (bản thử nghiệm thêm hậu tố `-beta.N`).
3. Commit, gắn tag `vX.Y.Z` và đẩy lên kho: `git push --follow-tags`.
4. Tạo Release trên GitHub từ tag và đính kèm tệp `.plugin`; bản beta đánh dấu *Set as a pre-release*.
