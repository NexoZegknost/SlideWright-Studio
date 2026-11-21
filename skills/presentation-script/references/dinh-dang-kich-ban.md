# Định dạng `kich_ban.json` và đầu ra

## 1. `slide.json` (do `scripts/doc_slide.py` tạo — chỉ đọc)
```json
{
  "nguon": "/…/bai.pptx", "boi_canh": "cong-so", "thoi_luong_phut": 15, "toc_do": 130,
  "slides": [
    { "so": 1, "tieu_de": "…", "vai": "bia|noi-dung|chia-phan|ket", "chu": "toàn bộ chữ trên slide",
      "so_am_tiet": 42, "so_nhap": 3, "an": false, "ghi_chu": "ghi chú hiện có", "giay_de_xuat": 60,
      "anh": "/…/anh_slide/slide-01.png" }
  ]
}
```
`vai` là ước đoán từ tiêu đề và vị trí — sửa lại trong kịch bản nếu sai.

## 2. `kich_ban.json` (Claude viết)
```json
{
  "tieu_de": "Báo cáo sơ kết học kỳ I môn Ngữ văn",
  "nguoi_trinh_bay": "…", "su_kien": "…", "thoi_gian_dia_diem": "…",
  "boi_canh": "cong-so", "thoi_luong_phut": 15, "toc_do": 130,
  "chuan_bi": ["Thử máy chiếu và bút chuyển trang", "Mở sẵn tệp .ppsx"],
  "slides": [
    {
      "so": 2, "tieu_de": "Tỷ lệ đạt chuẩn tăng 8 điểm", "giay": 75,
      "mo": "Bắt đầu từ con số mà chúng ta quan tâm nhất.",
      "nhip": ["Lời nói khi cú nhấp 1 hiện ra.", "Lời nói khi cú nhấp 2 hiện ra. [Dừng]"],
      "nhan": ["8 điểm"],
      "chuyen": "Vậy điều gì tạo ra mức tăng này?",
      "luu_y": "Chỉ tay vào cột năm 2025.",
      "the_nhac": ["8 điểm", "vùng sâu còn thấp"]
    }
  ],
  "hoi_dap": [
    { "hoi": "…", "tra_loi": "…", "nguon": "Báo cáo số …", "slide_du_phong": 14 }
  ]
}
```
- `so` khớp số slide trong bộ slide; mọi slide không ẩn đều phải có mục.
- `nhip`: số phần tử = `so_nhap` của slide (slide không hiệu ứng: 1 phần tử).
- `nhan`: 1–3 cụm, có mặt nguyên văn trên slide và trong lời nói (bản in tự in đậm).
- `the_nhac` (tuỳ chọn): từ khoá in trên thẻ nhắc; bỏ trống thì dùng `nhan`.
- `chuan_bi`, `nguoi_trinh_bay`, `su_kien`, `thoi_gian_dia_diem` tuỳ chọn.

## 3. Đầu ra
| Tệp | Lệnh | Nội dung |
|---|---|---|
| `<tên>_kich_ban.pptx` (+ `.ppsx`) | `dung_kich_ban.py … --pptx bai.pptx --ppsx` | ghi chú diễn giả theo mẫu `[Mở] / [Nhấp n] / [Nhấn] / [Chuyển] / [Lưu ý]`; giữ lại dòng nguồn ảnh, tác giả có sẵn trong ghi chú cũ; không ghi đè bản gốc; phông nhúng và hiệu ứng giữ nguyên |
| `KichBan_<ChuDeKhongDau>_<ddmmyyyy>.docx` | `dung_kich_ban.py … --ra-docx` | A4, Times New Roman 13: thông tin chung, chuẩn bị, bảng phân bổ thời gian (mốc bắt đầu), lời nói từng slide kèm ảnh thu nhỏ và mốc giờ, hỏi đáp dự kiến, trang thẻ nhắc; số trang ở chân trang |

Bản in dùng để tập và cầm tay; ghi chú trong PowerPoint dùng ở chế độ Presenter View.
