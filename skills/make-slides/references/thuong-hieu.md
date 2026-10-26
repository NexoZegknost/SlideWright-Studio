# Bộ nhận diện thương hiệu đơn vị

Thư mục `assets/thuong-hieu/<ten>/` chứa logo, màu, hoạ tiết của một đơn vị cụ thể (người dùng cung cấp).

**Chỉ dùng khi người dùng yêu cầu** — ví dụ "báo cáo ở Bách khoa", "làm theo nhận diện Bách khoa", "có logo BK", "dùng tài nguyên của trường". Không tự dùng vì đề tài nhắc tới đơn vị, vì người trình bày học/làm ở đó hay vì bài trình bày tại đó; không gợi ý trong các phương án và không hỏi lại. Yêu cầu đã nêu trong cuộc trò chuyện thì áp dụng cho các bộ slide tiếp theo của cùng sự kiện/môn học.

Khi được yêu cầu, không dùng nguyên "phong cách thương hiệu" một cách máy móc: chạy `scripts/dinh_huong.js --thuong-hieu <ten>` để giữ màu chủ đạo + logo của đơn vị nhưng phối màu nhấn, phông, texture theo lĩnh vực của đề tài (bài công nghệ khác bài khoa học xã hội) — xem `dinh-huong-thiet-ke.md`. Phương án "Nhận diện gốc" vẫn có sẵn khi người dùng muốn đúng y bộ nhận diện.

## Thương hiệu có sẵn
| Tên | Đơn vị | Nguồn |
|---|---|---|
| `bk-hcmut` | Trường Đại học Bách khoa – ĐHQG-HCM | Bộ nhận diện thương hiệu, 04/2021 |

## Cấu trúc một thương hiệu
```
assets/thuong-hieu/<ten>/
  brand.json        màu, phông thay thế, tệp logo (tep_logo), quy tắc logo, hoạ tiết, "style" (dùng như một phong cách)
  logo/             logo PNG trong suốt: bản chuẩn, bản cho nền tối, logo ngang (logo + tên) tiếng Việt/Anh, sáng/tối
  hoa-tiet/         goc-*.png: trích nguyên từ tài liệu gốc; còn lại: sinh bằng scripts/hoa_tiet_tam_giac.py (có .svg)
  mau-tham-khao/    ảnh trang tài liệu gốc (bìa, quy cách logo, hoạ tiết, mẫu PowerPoint, banner) để xem khi thiết kế
```

## Dùng khi dựng PowerPoint
```js
const { L, brand, logo, hoaTiet, dauThuongHieu, setScale } = require(LIB_DIR + "/layouts.js");
const S = DH.apDung(DH.dinhHuong({ chuDe, thuongHieu: "bk-hcmut" }).phuongAn[0]);   // khuyến nghị: màu thương hiệu + phối theo lĩnh vực
// hoặc: const S = brand("bk-hcmut");   // nhận diện gốc
push(L.biaThuongHieu(pres, S, { title: "…", sub: "…", info: "…", lang: "vi" }, { dark: true }), "fadeBlack");
const r = L.baThe(pres, S, {...});      // slide nội dung bình thường
dauThuongHieu(r.slide, S);              // tuỳ chọn: logo ngang nhỏ góc dưới trái
logo(sl, S, { kieu: "don", dark: true, h: 0.8, align: "center", y: 0.4 });         // đặt logo tự chọn bản theo nền
hoaTiet(sl, S, "luoi-trang-dam-phai", { x: 0, y: 0, w: 10 });                       // hoạ tiết phủ slide nền tối
```
- Nhúng phông: `MS.embedFonts(buf, [S.head, S.body])` (Montserrat + Lexend thay cho Myriad Pro).
- Nhận diện gốc (`brand()`): nền tối xanh đậm `032B91`, chữ nhấn trên nền tối vàng `FBDD0F` (như banner của trường), chữ nhấn trên nền sáng xanh `0B5CAD`, hình khối xanh tươi `1488DB`, màu phụ lục lam `1FB5C9`. Đỏ cam của banner không dùng cạnh xanh (màu đối nhau — `phoi-mau.md`).
- Bối cảnh vẫn quyết định cỡ chữ, mật độ, mức hiệu ứng; thương hiệu chỉ quyết định màu, logo, hoạ tiết.

## Quy tắc logo (theo bộ nhận diện)
1. Chỉ hai phiên bản: **chuẩn trên nền trắng** và **viền trắng trên nền tối**. Hàm `logo()` tự chọn theo `dark`.
2. Không đổi màu, không đơn sắc hoá, không kéo méo, không xoay, không thêm bóng đổ, không đặt lên ảnh rối; giữ khoảng trống quanh logo ≥ 1/4 chiều cao logo.
3. Tên trường cạnh logo dùng **tệp logo ngang**, không gõ lại bằng phông khác.
4. Mỗi slide tối đa một logo. Bìa: logo đơn giữa phía trên hoặc logo ngang góc trên trái. Slide nội dung: không bắt buộc; nếu dùng thì logo ngang nhỏ (`dauThuongHieu`).
5. Logo không phải "biểu tượng trước chữ" theo `dau-hieu-ai.md` — nhưng cũng không đặt logo làm hoa văn lặp lại.

## Hoạ tiết
Motif của trường: **mắt lưới tam giác ghép lục giác** (đồng dạng hình tổ ong của logo), luôn mờ dần để không ảnh hưởng chữ; dải xiên/dải cong xanh đậm + xanh tươi cho bìa, đầu – chân trang.

| Tệp (hoa-tiet/) | Dùng cho |
|---|---|
| `cum-sang-phai-tren`, `cum-sang-trai-duoi` | Góc slide nền trắng (bìa sáng, slide chia phần sáng) — giống phong bì, standee của trường |
| `cum-toi-phai-tren`, `cum-toi-trai-duoi` | Góc slide nền xanh đậm |
| `dai-sang-dau-trang`, `dai-sang-chan-trang` | Dải tam giác mỏng ở đầu/chân slide nội dung |
| `luoi-trang-dam-phai` | Lưới nét trắng phủ slide nền xanh (chữ đặt bên trái, nơi lưới mờ) |
| `luoi-xanh-dam-trai` | Lưới nét xanh phủ slide nền trắng (chữ đặt bên phải) |
| `luc-giac-luoi-trang`, `luc-giac-nhieu-mau` | Khối lục giác làm điểm nhìn ở slide chia phần, slide trích dẫn |
| `goc-luoi-tam-giac-nen-toi/nen-trang`, `goc-luoi-da-giac-nhieu-mau` | Ba motif nguyên bản trang 6 bộ nhận diện |
| `goc-dai-xien-bia-tren/duoi`, `goc-dai-cong-chan-trang` | Dải xiên bìa và dải cong chân trang nguyên bản |

Sáng tạo thêm: `python3 scripts/hoa_tiet_tam_giac.py --kieu cum|luoi|da-giac|dai ...` (xem `--help`), bảng màu tuỳ chọn `--bang "032B91:0.8,1488DB:0.6,FFFFFF:0.3"`. Lưu kết quả vào thư mục làm việc, không ghi vào plugin.

Quy tắc dùng hoạ tiết: mỗi slide tối đa một hoạ tiết; không đặt chữ lên phần hoạ tiết đậm nhất; slide nội dung nhiều chữ chỉ dùng dải đầu/chân hoặc không dùng; tránh lặp cùng một góc cụm tam giác ở mọi slide (đổi góc hoặc bỏ ở slide nội dung).

## Thêm thương hiệu mới
Khi người dùng gửi bộ nhận diện khác: đọc tài liệu, trích logo (PNG trong suốt, giữ nguyên màu), lấy màu theo RGB ghi trong tài liệu, lưu hoạ tiết, viết `brand.json` cùng cấu trúc, rồi đóng gói lại plugin. Không tự tạo biến thể logo mà tài liệu không cho phép.
