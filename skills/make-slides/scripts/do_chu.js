// do_chu.js — đo chữ bằng chính phông của gói (opentype.js) để bố cục tự tính chỗ: bề rộng, số dòng, chiều cao khối chữ,
// phần chân chữ (descender) — tránh đường kẻ chạm chân chữ, khung quá cao hoặc quá thấp so với nội dung.
// Phụ thuộc: npm install opentype.js@1.3.4 (không có thì dùng ước lượng 0,55 em/ký tự).
//   const D = require("./do_chu.js");
//   D.rong("2,8 giờ", { face: "Lora", size: 57, bold: true })          → bề rộng (inch)
//   D.ngat("Tắt thông báo khi tự học…", { face, size, w: 8.2 })        → ["dòng 1", "dòng 2"]
//   D.cao(lines.length, size, 1.2)                                     → chiều cao khối (inch)
//   D.chan(size, face)                                                → độ sâu chân chữ dưới đường cơ sở (inch)
const path = require("path");
const fs = require("fs");
const FONT_DIR = path.join(__dirname, "..", "assets", "fonts");
const FILES = JSON.parse(fs.readFileSync(path.join(FONT_DIR, "files.json"), "utf8"));
let OT = null;
try { OT = require("opentype.js"); } catch (e) { OT = null; }
const cache = {};
function font(face, bold, italic) {
  const f = FILES[face];
  if (!OT || !f) return null;
  const slot = bold && italic ? "boldItalic" : bold ? "bold" : italic ? "italic" : "regular";
  const p = path.join(FONT_DIR, f[slot] || f[bold ? "bold" : "regular"] || f.regular);
  if (!cache[p]) { try { cache[p] = OT.loadSync(p); } catch (e) { cache[p] = null; } }
  return cache[p];
}
function rong(text, { face = "Montserrat", size = 18, bold = false, italic = false } = {}) {
  const f = font(face, bold, italic);
  const t = String(text).replace(/\*\*/g, "");
  if (!f) return (t.length * 0.55 * size) / 72;
  return f.getAdvanceWidth(t, size, { kerning: true }) / 72;
}
// ngắt dòng tham lam như PowerPoint (ngắt ở khoảng trắng thường; khoảng trắng không ngắt giữ dính)
function ngat(text, o = {}) {
  const w = o.w || 8.8, out = [];
  for (const para of String(text).split("\n")) {
    const words = para.split(" ");
    let cur = "";
    for (const wd of words) {
      const tryLine = cur ? cur + " " + wd : wd;
      if (cur && rong(tryLine, o) > w) { out.push(cur); cur = wd; } else cur = tryLine;
    }
    out.push(cur);
  }
  return out;
}
const cao = (nLines, size, gian = 1.2) => (nLines * size * gian) / 72;
function chan(size, face = "Montserrat") { const f = font(face); return ((f ? -f.descender / f.unitsPerEm : 0.27) * size) / 72; }
function dinh(size, face = "Montserrat") { const f = font(face); return ((f ? f.ascender / f.unitsPerEm : 0.95) * size) / 72; }
// hệ số dòng thật của phông (đỉnh + chân chữ) / em — PowerPoint giãn dòng 100% theo đúng tỉ lệ này (Lora ≈ 1,28; Montserrat ≈ 1,22)
function heSo(face = "Montserrat", bold = false) { const f = font(face, bold); return f ? (f.ascender - f.descender) / f.unitsPerEm : 1.2; }
// cỡ lớn nhất ≤ maxSize để text vừa w trong tối đa n dòng
function vuaCo(text, o = {}) {
  let s = o.size || 40;
  while (s > (o.min || 10) && ngat(text, { ...o, size: s }).length > (o.dong || 1)) s -= 1;
  return s;
}
module.exports = { rong, ngat, cao, chan, dinh, vuaCo, heSo, coSan: !!OT };
