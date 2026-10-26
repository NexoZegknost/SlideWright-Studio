# Quy tắc phối màu

Áp dụng cho mọi bảng màu: phong cách có sẵn (`assets/styles.json`), bảng màu thương hiệu, bảng màu do `scripts/dinh_huong.js` sinh ra theo đề tài. Code kiểm: `scripts/mau.js` (khi dựng) và `scripts/kiem_tra_slide.py` (sau khi dựng).

## 1. Không phối hai màu đối nhau
Hai màu nằm đối diện trên vòng màu của hoạ sĩ (đỏ – vàng – lam): **lam – cam, đỏ – lục, vàng – tím** (và các cặp gần đối). Khi cả hai cùng tươi, đặt cạnh nhau hoặc chữ màu này trên nền màu kia, mép chữ "rung", nhoè, mỏi mắt. Riêng cặp đỏ – lục, người mù màu đỏ – lục (khoảng 8% nam giới) gần như không phân biệt được.
- Tiêu chí: lệch sắc ≥ 140° trên vòng RYB, cả hai màu có sắc (độ bão hoà ≥ 0,12) và ít nhất một màu tươi (≥ 0,35) → **cấm** với chữ trên nền, **cảnh báo** với mảng màu cạnh nhau và với hai màu nhấn cùng có trong một bài.
- Được phép khi một màu gần như trung tính: xanh than rất đậm, ngà, be, xám ngả xanh. Ví dụ xanh đêm `14213D` + vàng kim nhạt `D8C9A3` được; xanh đậm `0A1931` + hổ phách `FFB547` không được.
- Không dùng đỏ và lục để mã hoá đúng/sai, tăng/giảm. Dùng một màu nhấn và một màu trung tính (đậm/nhạt), hoặc thêm ký hiệu, nhãn chữ.

## 2. Các kiểu phối được dùng (theo thứ tự ưu tiên)
| Kiểu | Cách làm | Hợp với |
|---|---|---|
| **Đơn sắc** | Một sắc, nhiều độ sáng (đậm → nhạt) + trắng/xám | Bài trang trọng, học thuật, báo cáo số liệu |
| **Tương đồng** | 2–3 sắc kề nhau, lệch 30–60° (lam – lam lục – lục lam; đỏ son – cam đất – vàng đất) | Mặc định cho hầu hết đề tài |
| **Tương đồng + trung tính ấm/lạnh** | Bảng tương đồng + nền giấy ngà hoặc xám ngả lam | Khoa học xã hội, nhân văn (ấm); công nghệ, khoa học tự nhiên (lạnh) |
| **Tam giác dịu** | Ba sắc cách nhau ~120°, trong đó hai sắc đã hạ độ bão hoà | Sự kiện, thiếu nhi; dùng hạn chế |
| ~~Bổ túc / bổ túc chia~~ | Lam–cam, đỏ–lục, vàng–tím | **Không dùng** |

## 3. Tỉ lệ 60 – 30 – 10
- 60%: màu nền chủ đạo (thường trung tính: trắng, ngà, xám rất nhạt, hoặc màu đậm của slide mở phần).
- 30%: màu phụ cho khối cấu trúc (khối tiêu đề, cột, thẻ, mảng màu lớn).
- 10%: một màu nhấn cho điểm nhìn (con số, từ khoá, vạch nhấn). Không quá 3 sắc màu có sắc trong cả bài, chưa kể trung tính.

## 4. Chữ và nền
1. Tương phản WCAG: chữ thường ≥ 4,5:1; chữ ≥ 18pt hoặc ≥ 14pt đậm ≥ 3:1.
2. Trên nền đậm: chữ thường màu trắng; chữ nhấn là **trắng, ngà ấm** (mặc định cho bài trầm, học thuật: KHXH, nhân văn, lịch sử, sự kiện) hoặc một sắc **tương đồng, rất sáng** (ví dụ nền xanh đậm → xanh bạc hà) đạt **≥ 7:1**. Cấm:
   - **chữ tím, tím oải hương, tím hồng** trên nền tối — độ sáng cảm nhận của tím thấp, chữ bị chìm dù tỉ số tương phản trên giấy có vẻ đủ;
   - sắc nhạt hơn của chính màu nền (lệch < 30°, chữ chìm);
   - màu đối nhau với nền (cam, vàng cam trên nền lam).
3. Trên nền sáng: chữ nhấn là màu nhấn đã làm đậm đến khi đạt 4,6:1 (`accentText`). Không dùng chữ vàng hoặc màu nhạt trên nền trắng.
4. Kiểm cả ở dạng thang xám: bỏ màu đi mà vẫn đọc và phân biệt được thứ bậc → bảng màu ổn.

## 5. Màu theo lĩnh vực (gợi ý sắc chủ đạo; `assets/linh-vuc.json` ghi chi tiết)
| Lĩnh vực | Sắc chủ đạo | Nền | Ghi chú |
|---|---|---|---|
| Công nghệ, kỹ thuật, dữ liệu | lam – lam lục – chàm (lạnh) | trắng / xanh than đậm | nhấn lục bạc hà hoặc tím oải hương, không cam |
| Khoa học tự nhiên | lam lục – lục – lam | trắng, giấy kẻ ô | sạch, nhiều khoảng trắng |
| Khoa học xã hội | đỏ rượu – nâu đất – vàng đất, hoặc chàm – mận (ấm, trầm) | ngà, giấy | sắc trầm, độ bão hoà thấp |
| Nhân văn, văn học, triết | mận – tím than – nâu mực | ngà | ít màu, nhấn bằng chữ có chân |
| Kinh tế, quản lý | xanh than – lam thép | trắng | một màu nhấn duy nhất cho số liệu |
| Y sinh, sức khoẻ | lục lam – lục ngọc | trắng | dịu, tránh đỏ tươi diện rộng |
| Môi trường, nông nghiệp | lục – lục vàng – nâu đất | trắng ngà | tương đồng ấm |

## 6. Kiểm tra
- Khi dựng: `layouts.style()` / `brand()` / `dinhHuong()` tự cảnh báo bảng màu lỗi (`mau.kiemTraBangMau`).
- Sau khi dựng: `python3 scripts/kiem_tra_slide.py <file>.pptx` báo chữ trên nền đối nhau (LỖI), mảng màu đối nhau với nền và cặp màu đối nhau trong cả bài (CẢNH BÁO).

## Nguồn
- Tuts+ Web Design — Why You Should Avoid Vibrating Color Combinations (webdesign.tutsplus.com/why-you-should-avoid-vibrating-color-combinations--cms-25621a)
- Ethos3 — Color Rules for Presentation Design (ethos3.com/color-rules-for-presentation-design)
- Vision Australia — Creating accessible digital colour palettes with the 60-30-10 rule (visionaustralia.org)
- WCAG 2.2 — Contrast (Minimum) 1.4.3
