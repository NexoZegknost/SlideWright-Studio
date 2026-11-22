// phuong_an.js — tính sẵn 3 phương án phong cách cho từng lĩnh vực bằng module định hướng của make-slides,
// ghi ra JSON để bản Gemini app (không chạy mã) dùng thẳng.
// Dùng: node tools/phuong_an.js <tệp ra>
const fs = require("fs");
const path = require("path");
const SK = path.join(__dirname, "..", "skills", "make-slides");
const DH = require(path.join(SK, "scripts", "dinh_huong.js"));

const MAU = ["dark", "light", "soft", "text", "muted", "accent", "accent2", "accentText", "accentOnDark", "surfaceDark"];

const kq = { _ghi_chu: "Sinh tự động bởi tools/phuong_an.js từ assets/linh-vuc.json và scripts/dinh_huong.js — không sửa tay. Mỗi lĩnh vực: tu_khoa (so với đề tài viết không dấu) và 3 phương án; phương án đầu là đề xuất." };
for (const [ma, lv] of Object.entries(DH.LV)) {
  if (ma.startsWith("_")) continue;
  const r = DH.dinhHuong({ chuDe: lv.ten, linhVuc: ma });
  kq[ma] = {
    ten: lv.ten,
    tu_khoa: lv.tu_khoa || [],
    phuong_an: r.phuongAn.map((pa) => {
      const st = pa.style;
      const goc = { head: st.fonts.head, body: st.fonts.body };
      return {
        ten: pa.ten,
        ly_do: pa.lyDo,
        trinh_bay: pa.trinhBay,
        mau: Object.fromEntries(MAU.filter((k) => st.colors[k]).map((k) => [k, st.colors[k]])),
        phong_goc: goc,
        ty_le_nen_toi: pa.tyLeNenToi,
        muc_hieu_ung: (pa.hieuUng || {}).muc,
      };
    }),
  };
}
fs.writeFileSync(process.argv[2], JSON.stringify(kq, null, 1) + "\n");
