# Mẫu theo đề tài (người dùng gửi)

Mỗi lĩnh vực một thư mục, đúng khoá trong `assets/linh-vuc.json` (`cong-nghe`, `khoa-hoc-tu-nhien`, `khoa-hoc-xa-hoi`, `nhan-van`, `lich-su-van-hoa`, `kinh-te-quan-ly`, `y-sinh`, `moi-truong-nong-nghiep`, `giao-duc-day-hoc`, `hanh-chinh`, `su-kien-nghe-thuat`, `da-nang`).

Trong mỗi thư mục:
- ảnh lưới/ảnh trang của mẫu (`<ten-mau>.jpg`), không lưu tệp gốc có bản quyền;
- `<ten-mau>.json`: những gì học được — lưới, vị trí điểm nhìn, thứ bậc cỡ chữ, cách dùng màu (vai trò từng màu, không chép mã màu nhận diện của người khác), texture, nhịp sáng – tối, bố cục tương ứng trong `layouts.js` hoặc hàm bố cục mới đã viết.

`scripts/dinh_huong.js` liệt kê các mẫu này trong kết quả (`mauThamKhao`) để Claude xem trước khi thiết kế bài cùng lĩnh vực. Quy trình học mẫu: `references/mau-bo-cuc.md` mục 3.
