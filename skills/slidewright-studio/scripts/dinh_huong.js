// dinh_huong.js — module định hướng thiết kế: đề tài → lĩnh vực → phong cách hoàn chỉnh
// (bảng màu theo luật phối màu, phông, texture, cách trình bày, bố cục ưu tiên, hiệu ứng), có thể trộn với
// bộ nhận diện thương hiệu khi người dùng YÊU CẦU (ví dụ báo cáo ở Bách khoa).
// Tài liệu: references/dinh-huong-thiet-ke.md · luật màu: references/phoi-mau.md · tri thức lĩnh vực: assets/linh-vuc.json
//
// Dùng trong script dựng bài:
//   const DH = require(LIB + "/dinh_huong.js");
//   const kq = DH.dinhHuong({ chuDe: "Thiết kế mạch khuếch đại dùng BJT", thuongHieu: "bk-hcmut", boiCanh: "hoc-sinh-sinh-vien" });
//   const pa = kq.phuongAn[0];                 // 0 = đề xuất; 1, 2 = phương án khác
//   const S = DH.apDung(pa);                   // phong cách dùng ngay với layouts.js (có S.brand nếu có thương hiệu)
//   const tex = DH.taoTexture(pa, "out/tex");  // { bia:[…], "chia-phan":[…], "noi-dung":[…], "nhan-manh":[…] } nhiều biến thể nhiều lớp
//   L.baThe(pres, S, { …, nen: DH.nen(tex, "noi-dung", k) })   // k = thứ tự slide nội dung → luân phiên biến thể
// Dòng lệnh (xem trước cho người dùng chọn):
//   node dinh_huong.js --chu-de "…" [--mo-ta "…"] [--thuong-hieu bk-hcmut] [--boi-canh hoc-sinh-sinh-vien] [--linh-vuc khoa-hoc-xa-hoi]
//                      [--xem-truoc xem-truoc.png] [--json]

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const C = require("./mau.js");

const ROOT = path.join(__dirname, "..");
const LV = JSON.parse(fs.readFileSync(path.join(ROOT, "assets", "linh-vuc.json"), "utf8"));
const STYLES = JSON.parse(fs.readFileSync(path.join(ROOT, "assets", "styles.json"), "utf8"));
const CTX = JSON.parse(fs.readFileSync(path.join(ROOT, "assets", "contexts.json"), "utf8"));
const FONTS = JSON.parse(fs.readFileSync(path.join(ROOT, "assets", "fonts", "files.json"), "utf8"));

const boDau = (s) => (s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d").replace(/Đ/g, "D").toLowerCase();

// ---------------------------------------------------------------- 1. nhận diện lĩnh vực
function nhanDienLinhVuc(text, ep) {
  if (ep && LV[ep]) return { key: ep, diem: 99, khop: ["(chỉ định)"] };
  const t = " " + boDau(text).replace(/[^a-z0-9/ ]+/g, " ").replace(/\s+/g, " ") + " ";
  const kq = [];
  for (const [k, v] of Object.entries(LV)) {
    if (k.startsWith("_")) continue;
    const khop = (v.tu_khoa || []).filter((w) => t.includes(" " + w + " ") || (w.length > 6 && t.includes(w)));
    // cụm nhiều chữ nặng ký hơn một chữ
    const diem = khop.reduce((s, w) => s + (w.includes(" ") ? 2 : 1), 0);
    kq.push({ key: k, diem, khop });
  }
  kq.sort((a, b) => b.diem - a.diem);
  return kq[0].diem ? { ...kq[0], khac: kq.filter((x) => x.diem).slice(1, 3) } : { key: "da-nang", diem: 0, khop: [], khac: [] };
}

// ---------------------------------------------------------------- 2. bảng màu
function bangMau(cfg, anchor) {
  // thử lần lượt các độ lệch cho tới khi bảng màu không còn lỗi phối màu
  const thu = [0, 10, -10, 20, -20];
  let best = null;
  for (const d of thu) {
    const o = { ...cfg, lechNhan: (cfg.lechNhan || 0) + d };
    if (anchor) o.mauChu = anchor;
    const colors = C.taoBangMau(o);
    const loi = C.kiemTraBangMau(colors).filter((e) => e.muc === "LỖI");
    if (!best || loi.length < best.loi.length) best = { colors, loi };
    if (!loi.length) break;
  }
  return best;
}

// ---------------------------------------------------------------- 3. dựng một phương án
function phuongAn({ ten, lv, mauCfg, phong, texture, preset, brand, boiCanh, lyDo }) {
  let colors, canhBao = [];
  if (preset) {
    colors = { ...STYLES[preset].colors };
    if (!colors.accent2) colors.accent2 = colors.accent;
    phong = { head: STYLES[preset].fonts.head.split("|")[0].replace("(nghiêng)", "").trim(), body: STYLES[preset].fonts.body, accent: STYLES[preset].fonts.accent ? STYLES[preset].fonts.accent.split("|")[0].trim() : null };
  } else if (!mauCfg && brand) {
    colors = { ...brand.style.colors };
  } else {
    const r = bangMau(mauCfg, brand ? brand.style.colors.dark : null);
    colors = r.colors; canhBao = r.loi.map((e) => e.noiDung);
  }
  for (const f of [phong.head, phong.body, phong.accent].filter(Boolean)) if (!FONTS[f]) canhBao.push(`phông ${f} không có trong gói`);
  const ctx = boiCanh && CTX[boiCanh];
  return {
    ten, linhVuc: lv.ten, lyDo,
    style: { ten, muc: "chinh-quy", fonts: { head: phong.head, body: phong.body, accent: phong.accent || null }, colors },
    thuongHieu: brand ? brand._ten : null,
    boTexture: texture || {},
    boCuc: { uuTien: lv.bo_cuc_uu_tien, hanChe: lv.bo_cuc_han_che },
    trinhBay: lv.trinh_bay,
    tyLeNenToi: lv.ty_le_nen_toi,
    hieuUng: { ...lv.hieu_ung, muc: ctx ? ctx.hieu_ung : "phong-phu" },
    coChu: ctx ? { body_min: ctx.body_min, title_min: ctx.title_min } : null,
    canhBao,
  };
}

// ---------------------------------------------------------------- 4. hàm chính
// o: { chuDe, moTa, linhVuc (ép), thuongHieu (CHỈ khi người dùng yêu cầu), boiCanh, phongCach (ép preset) }
function dinhHuong(o = {}) {
  const nd = nhanDienLinhVuc(`${o.chuDe || ""} ${o.moTa || ""}`, o.linhVuc);
  const lv = LV[nd.key];
  let brand = null, th = null;
  if (o.thuongHieu) {
    brand = JSON.parse(fs.readFileSync(path.join(ROOT, "assets", "thuong-hieu", o.thuongHieu, "brand.json"), "utf8"));
    brand._ten = o.thuongHieu;
    th = (lv.thuong_hieu || {})[o.thuongHieu] || {};
  }
  const base = { ...lv.mau, ...(th ? { lechNhan: th.lechNhan ?? lv.mau.lechNhan, lechPhu: th.lechPhu ?? lv.mau.lechPhu, cNhan: th.cNhan ?? lv.mau.cNhan, nen: th.nen ?? lv.mau.nen, kieu: th.kieu ?? lv.mau.kieu, darkL: th.darkL, darkCmax: th.darkCmax } : {}) };
  // bộ texture: mỗi vai nhiều biến thể, mỗi biến thể nhiều lớp; có thương hiệu → chồng thêm lớp motif của đơn vị
  const ghepTH = (bo) => {
    const out = JSON.parse(JSON.stringify(bo));
    const lop = (th && th.lop_thuong_hieu) || {};
    for (const [vai, layers] of Object.entries(lop)) if (out[vai]) out[vai] = out[vai].map((v) => (v.length ? [...v, ...layers] : v));
    return out;
  };
  const tex = ghepTH(lv.bo_texture);
  const texBT = ghepTH({ ...lv.bo_texture, ...(lv.bo_texture_bien_the || {}) });
  const uniq = (x) => x;
  const nhanTH = brand ? ` + nhận diện ${brand.ten_tat || brand.ten}` : "";
  const pa = [];
  pa.push(phuongAn({ ten: `${lv.ten}${nhanTH}`, lv, mauCfg: base, phong: lv.phong, texture: uniq(tex), brand, boiCanh: o.boiCanh,
    lyDo: brand ? (th.ghi_chu || "Giữ màu chủ đạo của thương hiệu, phối màu nhấn tương đồng theo lĩnh vực.") : `Bảng màu ${{ "tuong-dong": "tương đồng", "don-sac": "đơn sắc" }[base.kieu] || base.kieu} theo lĩnh vực ${lv.ten.toLowerCase()}, phông ${lv.phong.head} + ${lv.phong.body}.` }));
  // biến thể: không thương hiệu → bảng màu biến thể của lĩnh vực; có thương hiệu → cấu hình biến thể riêng (mặc định đơn sắc theo màu thương hiệu)
  const bt = brand ? { ...base, ...((th && th.bien_the) || { kieu: "don-sac" }) } : { ...base, ...(lv.mau_bien_the || {}) };
  if (brand) { delete bt.hue; if (bt.kieu === "don-sac") { bt.lechNhan = 0; bt.lechPhu = 0; } }
  pa.push(phuongAn({ ten: `${lv.ten} – biến thể${nhanTH}`, lv, mauCfg: bt, phong: lv.phong, texture: uniq(texBT), brand, boiCanh: o.boiCanh,
    lyDo: (brand ? th && th.bien_the && th.bien_the.ghi_chu : lv.mau_bien_the && lv.mau_bien_the.ghi_chu) || "Cùng lĩnh vực, đổi kiểu phối và texture." }));
  if (brand) {
    pa.push(phuongAn({ ten: `Nhận diện gốc ${brand.ten_tat || brand.ten}`, lv, mauCfg: null, preset: null, phong: brand.style.fonts, texture: uniq(tex), brand, boiCanh: o.boiCanh, lyDo: "Màu đúng bộ nhận diện của đơn vị, ít sáng tạo nhất." }));
  } else {
    const preset = o.phongCach || lv.phong_cach_goc[0];
    pa.push(phuongAn({ ten: STYLES[preset].ten, lv, preset, texture: uniq(tex), boiCanh: o.boiCanh, lyDo: `Phong cách có sẵn "${STYLES[preset].ten}" hợp với lĩnh vực này.` }));
  }
  pa[0].nhan = "Đề xuất";
  pa.forEach((p) => { const loi = C.kiemTraBangMau(p.style.colors).filter((e) => e.muc === "LỖI"); p.canhBao.push(...loi.map((e) => e.noiDung)); p.canhBao = [...new Set(p.canhBao)]; });
  // mẫu người dùng đã gửi cho lĩnh vực này (assets/mau-theo-de-tai/<lĩnh vực>/): học bố cục, nhịp, cách dùng màu từ đây trước
  const mauDir = path.join(ROOT, "assets", "mau-theo-de-tai", nd.key);
  const mauThamKhao = fs.existsSync(mauDir) ? fs.readdirSync(mauDir).filter((f) => !f.startsWith(".")).map((f) => path.join(mauDir, f)) : [];
  return { linhVuc: { key: nd.key, ten: lv.ten, tuKhoaKhop: nd.khop, khac: (nd.khac || []).map((x) => x.key) }, thuongHieu: o.thuongHieu || null, mauThamKhao, phuongAn: pa };
}

// ---------------------------------------------------------------- 5. áp dụng
// Trả về phong cách S dùng với layouts.js (key, head, body, c…); có thương hiệu thì kèm S.brand (logo, hoạ tiết).
function apDung(pa) {
  const LAY = require("./layouts.js");
  let S;
  if (pa.thuongHieu) S = LAY.brand(pa.thuongHieu);
  else S = {};
  Object.assign(S, JSON.parse(JSON.stringify(pa.style)));
  S.key = "dinh-huong"; S.headItalic = false; S.head = S.fonts.head; S.body = S.fonts.body; S.accentFont = S.fonts.accent; S.c = S.colors;
  S.dinhHuong = { boCuc: pa.boCuc, trinhBay: pa.trinhBay, hieuUng: pa.hieuUng, tyLeNenToi: pa.tyLeNenToi };
  LAY.setCurrent && LAY.setCurrent(S);
  const w = LAY.checkPalette(S);
  if (w.length) console.warn("[SlideWright] Bảng màu định hướng cần xem lại:\n  - " + w.join("\n  - "));
  return S;
}

// Sinh bộ texture PNG (mỗi biến thể là các lớp chồng nhau, scripts/hoa_tiet.py --lop).
// Trả về { bia: [png…], "chia-phan": […], "noi-dung": […], "nhan-manh": […] }; biến thể rỗng → null (slide để trơn).
const MAU_LOP = (c) => ({ "toi-nhan": c.accentOnDark, "toi-trang": "FFFFFF", "toi-phu": c.accent, "sang-nhan": c.accent, "sang-phu": c.accent2 || c.accent, "sang-mo": c.muted });
function taoTexture(pa, outdir, { w = 2400, h = 1350, seed = 11 } = {}) {
  fs.mkdirSync(outdir, { recursive: true });
  const c = pa.style.colors, M = MAU_LOP(c), out = {};
  for (const [vai, bienThe] of Object.entries(pa.boTexture || {})) {
    out[vai] = bienThe.map((layers, i) => {
      if (!layers || !layers.length) return null;
      const lop = layers.map((L) => {
        const o = { ...L, mau: M[L.mau] || L.mau };
        if (L.kieu === "tam-giac-cum") o.bang = `${c.accentOnDark}:0.3,${c.accent}:0.45,FFFFFF:0.1,${c.surfaceDark || c.accent}:0.5`;
        return o;
      });
      const file = path.join(outdir, `${vai}-${i + 1}`);
      execFileSync("python3", [path.join(__dirname, "hoa_tiet.py"), "--lop", JSON.stringify(lop), "--w", String(w), "--h", String(h), "--seed", String(seed + i * 13), "--out", file], { stdio: "pipe" });
      return file + ".png";
    });
  }
  return out;
}
// Chọn texture cho slide thứ i của một vai (luân phiên biến thể) → đường dẫn hoặc null
function nen(tex, vai, i = 0) { const v = (tex && tex[vai]) || []; return v.length ? v[i % v.length] : null; }

// Ảnh xem trước các phương án (bìa + nội dung, có texture và logo) để người dùng chọn
function xemTruoc(kq, { chuDe, phuDe = "", out = "xem-truoc-dinh-huong.png", tmp = "/tmp/makeslides-dinh-huong" } = {}) {
  const spec = {}, keys = [];
  kq.phuongAn.forEach((p, i) => {
    const k = `dh${i}`; keys.push(k);
    const tex = taoTexture(p, path.join(tmp, k), { w: 1280, h: 720 });
    let logo = null;
    if (p.thuongHieu) {
      const B = JSON.parse(fs.readFileSync(path.join(ROOT, "assets", "thuong-hieu", p.thuongHieu, "brand.json"), "utf8"));
      logo = path.join(ROOT, "assets", "thuong-hieu", p.thuongHieu, "logo", B.tep_logo.ngang_vi_nen_toi);
    }
    spec[k] = { ...p.style, ten: p.ten, xem_truoc: { texture_bia: nen(tex, "bia"), texture_noi_dung: (tex["noi-dung"] || []).find(Boolean), logo_bia: logo } };
  });
  fs.mkdirSync(tmp, { recursive: true });
  const sp = path.join(tmp, "spec.json");
  fs.writeFileSync(sp, JSON.stringify(spec));
  execFileSync("python3", [path.join(__dirname, "xem_truoc_phong_cach.py"), "--title", chuDe, "--sub", phuDe, "--styles", keys.join(","), "--labels", kq.phuongAn.map((p, i) => (i ? `Phương án ${i + 1}` : "Đề xuất")).join(","), "--spec", sp, "--out", out], { stdio: "pipe" });
  return out;
}

function tomTat(kq) {
  const L = [`Lĩnh vực: ${kq.linhVuc.ten}${kq.linhVuc.tuKhoaKhop.length ? " (khớp: " + kq.linhVuc.tuKhoaKhop.slice(0, 5).join(", ") + ")" : ""}${kq.linhVuc.khac.length ? " · gần: " + kq.linhVuc.khac.join(", ") + " (ép bằng --linh-vuc nếu cần)" : ""}${kq.thuongHieu ? " · thương hiệu: " + kq.thuongHieu : ""}`];
  if (kq.mauThamKhao.length) L.push(`Mẫu người dùng đã gửi cho lĩnh vực này: ${kq.mauThamKhao.map((f) => path.basename(f)).join(", ")}`);
  kq.phuongAn.forEach((p, i) => {
    const c = p.style.colors;
    L.push(`\n${i ? "Phương án " + (i + 1) : "Đề xuất"}: ${p.ten}`);
    L.push(`  Lý do: ${p.lyDo}`);
    L.push(`  Màu: chủ đạo ${c.dark} (${C.moTa(c.dark)}), nhấn ${c.accent} (${C.moTa(c.accent)}), phụ ${c.accent2} (${C.moTa(c.accent2)}), chữ nhấn nền tối ${c.accentOnDark} (${C.moTa(c.accentOnDark)}), nền ${c.light}/${c.soft}`);
    L.push(`  Phông: ${p.style.fonts.head} + ${p.style.fonts.body}${p.style.fonts.accent ? " + " + p.style.fonts.accent : ""}`);
    L.push(`  Texture: ${Object.entries(p.boTexture).map(([vai, bt]) => `${vai}: ${bt.map((v) => (v.length ? v.map((x) => x.kieu).join("+") : "trơn")).join(" | ")}`).join(" · ")}`);
    L.push(`  Bố cục ưu tiên: ${p.boCuc.uuTien.join(", ")}${p.boCuc.hanChe.length ? " · hạn chế: " + p.boCuc.hanChe.join(", ") : ""}`);
    L.push(`  Trình bày: ${p.trinhBay}`);
    if (p.canhBao.length) L.push(`  Cảnh báo: ${p.canhBao.join("; ")}`);
  });
  return L.join("\n");
}

module.exports = { dinhHuong, apDung, taoTexture, nen, xemTruoc, tomTat, nhanDienLinhVuc, LV };

if (require.main === module) {
  const arg = (k, d) => { const i = process.argv.indexOf("--" + k); return i > 0 ? process.argv[i + 1] : d; };
  const kq = dinhHuong({ chuDe: arg("chu-de", ""), moTa: arg("mo-ta", ""), thuongHieu: arg("thuong-hieu"), boiCanh: arg("boi-canh"), linhVuc: arg("linh-vuc"), phongCach: arg("phong-cach") });
  if (process.argv.includes("--json")) console.log(JSON.stringify(kq, null, 1));
  else console.log(tomTat(kq));
  const xt = arg("xem-truoc");
  if (xt) console.log("\nẢnh xem trước:", xemTruoc(kq, { chuDe: arg("chu-de", ""), phuDe: arg("phu-de", ""), out: xt }));
}
