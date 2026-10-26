// layouts.js — thư viện 32 bố cục slide của SlideWright - Studio (khổ 16:9, 10" × 5.625")
// Không đặt biểu tượng/emoji trước đoạn văn hay tiêu đề thẻ (dấu hiệu slide do AI làm) — xem references/dau-hieu-ai.md
// Mỗi hàm: L.<ten>(pres, S, c, o) → { slide, steps }
//   S = một phong cách trong assets/styles.json (đã qua L.style(key))
//   c = nội dung của slide (xem chú thích từng hàm)
//   o = tuỳ chọn (o.dark: nền đậm/sáng, o.flip: đảo trái/phải…)
//   steps = gợi ý hiệu ứng theo mạch nói, đưa thẳng vào PLAN của makeslides.applyEffects
// Mọi đối tượng có objectName để gắn hiệu ứng. Ảnh: truyền đường dẫn tệp; thiếu ảnh → khối giữ chỗ màu soft.
// Chi tiết cách chọn bố cục: references/bo-cuc.md

const path = require("path");
const D = require(path.join(__dirname, "do_chu.js"));   // đo chữ bằng phông thật: số dòng, chiều cao, chân chữ
const STYLES = require(path.join(__dirname, "..", "assets", "styles.json"));

const W = 10, H = 5.625, M = 0.6;          // khổ slide và lề
const CW = W - 2 * M;                      // bề rộng vùng nội dung
const GAP = 0.3;                           // khoảng cách chuẩn giữa các khối

function style(key, { headIndex = 0 } = {}) {
  const s = JSON.parse(JSON.stringify(STYLES[key]));
  if (!s) throw new Error(`Không có phong cách ${key}`);
  const pick = (v, i = 0) => (v ? v.split("|")[Math.min(i, v.split("|").length - 1)].replace("(nghiêng)", "").trim() : null);
  s.key = key;
  s.headItalic = /nghiêng/.test(s.fonts.head);
  s.head = pick(s.fonts.head, headIndex);
  s.body = pick(s.fonts.body);
  s.accentFont = pick(s.fonts.accent);
  s.c = s.colors;
  CUR = s;
  const w = checkPalette(s);
  if (w.length) console.warn(`[SlideWright] Bảng màu "${key}" cần xem lại:\n  - ` + w.join("\n  - "));
  return s;
}

// ---------- cỡ chữ theo bối cảnh: setScale(body_min) — chữ ≤ 22pt được nhân hệ số K (cỡ cơ sở của nội dung là 16pt)
// Mọi chữ nội dung ≥ bodyMin (đọc được ở cuối phòng); chữ phụ (nguồn, chú thích, thông tin, nhãn số) ≥ coPhu; tiêu đề ≥ 1,25 × bodyMin.
// Bố cục giữ nguyên khung → chữ to hơn thì phải ÍT CHỮ hơn: scripts/kiem_tra_van_ban.py báo tràn/mồ côi để rút gọn.
let K = 1, BODY_MIN = 0, CAP_MIN = 0;
const TEN_PHU = /^(source|info|contact|kicker|hint|by|lockup|brandmark|hchon|sec|!!sec|given|cap\d+|sn\d+|dn\d+|xl|yl|note|role|an\d+)$/;
const TEN_TIEU_DE = /^(title|statement|question)$/;
function setScale(bodyMin, { coPhu = 16 } = {}) { K = Math.max(0.9, Math.min(1.6, (bodyMin || 16) / 16)); BODY_MIN = bodyMin || 0; CAP_MIN = bodyMin ? coPhu : 0; return K; }
const sz = (n, name = "") => {
  if (!n) return n;
  if (TEN_TIEU_DE.test(name)) return Math.max(n, Math.ceil(BODY_MIN * 1.25));
  if (n > 22) return n;
  const v = Math.round(n * K);
  return TEN_PHU.test(name) ? Math.max(v, CAP_MIN) : Math.max(v, BODY_MIN);
};
// Đánh dấu điểm nhấn trong chữ bằng **…**: cụm đó được in đậm và đổi sang màu nhấn (tự chọn màu theo nền sáng/tối)
let CUR = null;
function hlColor(baseColor) {
  if (!CUR) return null;
  const light = baseColor && lum(baseColor) > 0.45; // chữ sáng → đang ở nền tối
  return light ? CUR.c.accentOnDark : CUR.c.accentText;
}
function splitHL(text, base) {
  if (typeof text !== "string" || !text.includes("**")) return null;
  const parts = text.split("**");
  return parts.map((s, i) => ({ text: s, options: { ...base, ...(i % 2 ? { bold: true, color: hlColor(base.color) || base.color } : {}) } })).filter((r) => r.text);
}
function AT(sl, content, opts) {
  const baseColor = opts.color;
  if (typeof content === "string") {
    const r = splitHL(content, { color: baseColor });
    if (r) content = r;
  }
  if (Array.isArray(content)) {
    content = content.flatMap((r) => {
      const o = { ...(r.options || {}) };
      if (o.fontSize) o.fontSize = sz(o.fontSize, opts.objectName);
      const runs = splitHL(r.text, { ...o, color: o.color || baseColor, breakLine: false });
      if (!runs) return [{ ...r, options: o }];
      if (o.breakLine) runs[runs.length - 1].options.breakLine = true;
      runs.slice(1).forEach((x) => { delete x.options.bullet; delete x.options.paraSpaceAfter; });
      return runs;
    });
    // "\n" trong một run: pptxgenjs ghi nguyên ký tự xuống dòng vào <a:t> (PowerPoint không ngắt dòng) → tách thành run có breakLine
    content = content.flatMap((r) => {
      if (typeof r.text !== "string" || !r.text.includes("\n")) return [r];
      const parts = r.text.split("\n");
      return parts.map((t, i) => ({ text: t, options: { ...(r.options || {}), ...(i < parts.length - 1 ? { breakLine: true } : {}) } }));
    });
  }
  return sl.addText(content, { ...opts, fontSize: sz(opts.fontSize, opts.objectName) });
}
// màu chữ đặt trên nền accent: trắng hoặc màu đậm, chọn cái tương phản hơn
function lum(h) { const f = (c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4); const [r, g, b] = [0, 2, 4].map((i) => f(parseInt(h.substr(i, 2), 16) / 255)); return 0.2126 * r + 0.7152 * g + 0.0722 * b; }
const contrast = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };
const onAccent = (S) => (contrast("FFFFFF", S.c.accent) >= contrast(S.c.dark, S.c.accent) ? "FFFFFF" : S.c.dark);

// ---------- tiện ích
// Mọi bố cục tạo slide qua đây: c.nen = đường dẫn texture PNG (ví dụ từ dinh_huong.taoTexture) → đặt dưới cùng, trước mọi đối tượng
// c.nenDong: true (hoặc {le, period}) → texture lớn hơn khổ slide và trôi chậm suốt slide (hiệu ứng chờ "troi", hieu_ung.js)
// c.cho: mảng hiệu ứng chờ bổ sung (ví dụ từ hieu_ung.hatBui/denSanKhau gọi trong hàm truoc(sl)) — gộp vào idle của bố cục
// c.truoc(sl): hàm vẽ thêm lớp trang trí ngay sau nền, trước nội dung (đèn, hạt sáng, vòng xoay…); trả về mảng idle nếu có
function addSlide(pres, c) {
  const sl = pres.addSlide();
  sl._cho = [];
  if (c && c.nen && c.nenDong) sl._cho.push(require(path.join(__dirname, "hieu_ung.js")).nenDong(sl, c.nen, typeof c.nenDong === "object" ? c.nenDong : {}));
  else if (c && c.nen) texture(sl, c.nen, {}, "nen");
  if (c && typeof c.truoc === "function") { const r = c.truoc(sl); if (Array.isArray(r)) sl._cho.push(...r); }
  if (c && Array.isArray(c.cho)) sl._cho.push(...c.cho);
  return sl;
}
const T = (o) => ({ isTextBox: true, margin: 0, valign: "top", ...o });
const bgOf = (S, o) => (o && o.dark ? S.c.dark : S.c.light);
const fg = (S, o) => (o && o.dark ? "FFFFFF" : S.c.text);
const sub = (S, o) => (o && o.dark ? S.c.accentOnDark : S.c.accentText);
const mut = (S, o) => (o && o.dark ? "D5D9E2" : S.c.muted);

function title(sl, S, text, o = {}, box = {}) {
  AT(sl, text, T({ objectName: "title", x: M, y: 0.45, w: CW, h: 0.85, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic,
    fontSize: 30, color: fg(S, o), valign: "bottom", fit: "shrink", ...box }));
}
function kicker(sl, S, text, o = {}, box = {}) {
  if (!text) return;
  AT(sl, text.toUpperCase(), T({ objectName: "kicker", x: M, y: 0.25, w: CW, h: 0.25, fontFace: S.body, bold: true, fontSize: 11, charSpacing: 2, color: sub(S, o), ...box }));
}
function image(sl, S, img, box, name = "img", rounding) {
  // img = đường dẫn, hoặc { duong, ten } (ten "!!…" để ảnh morph giữa hai slide — chuyen_trang.anh)
  if (img && typeof img === "object") { name = img.ten || name; img = img.duong; }
  if (img) sl.addImage({ objectName: name, path: img, ...box, sizing: { type: "cover", w: box.w, h: box.h }, ...(rounding ? { rounding: true } : {}) });
  else sl.addShape("rect", { objectName: name, ...box, fill: { color: S.c.soft }, line: { color: S.c.soft } });
}
function notes(sl, c) { if (c.notes) sl.addNotes(c.notes); }

// Icon react-icons → PNG base64. ten dạng "fa6:FaBookOpen" hoặc "lu:LuLightbulb"
async function icon(ten, color = "FFFFFF", size = 256) {
  const [lib, name] = ten.split(":");
  const React = require("react"), RDS = require("react-dom/server"), sharp = require("sharp");
  const mod = require(`react-icons/${lib}`);
  if (!mod[name]) throw new Error(`Không có icon ${ten}`);
  const svg = RDS.renderToStaticMarkup(React.createElement(mod[name], { color: "#" + color, size }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

const L = {};

// 01 Bìa tối giản — c: {kicker, title, sub, info}
L.biaToiGian = (pres, S, c, o = { dark: true }) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  kicker(sl, S, c.kicker, o, { y: 1.15 });
  AT(sl, c.title, T({ objectName: "title", x: M, y: 1.6, w: 7.6, h: 1.8, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 44, color: fg(S, o), fit: "shrink", valign: "top" }));
  if (c.sub) AT(sl, c.sub, T({ objectName: "sub", x: M, y: 3.45, w: 7.6, h: 0.6, fontFace: S.body, fontSize: 18, color: sub(S, o) }));
  if (c.info) AT(sl, c.info, T({ objectName: "info", x: M, y: 4.75, w: CW, h: 0.35, fontFace: S.body, fontSize: 12, color: mut(S, o) }));
  notes(sl, c);
  return { slide: sl, steps: [[{ n: "title", eff: "floatUp" }, { n: "sub", eff: "fade", start: "after" }]], autoFirst: true };
};

// 02 Bìa ảnh tràn viền — c: {img, kicker, title, sub}
L.biaAnhTran = (pres, S, c) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.dark };
  image(sl, S, c.img, { x: 0, y: 0, w: W, h: H }, "bg");
  sl.addShape("rect", { objectName: "shade", x: 0, y: 2.6, w: W, h: H - 2.6, fill: { color: S.c.dark, transparency: 15 }, line: { color: S.c.dark, transparency: 100 } });
  kicker(sl, S, c.kicker, { dark: true }, { y: 2.95 });
  AT(sl, c.title, T({ objectName: "title", x: M, y: 3.25, w: CW, h: 1.2, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 40, color: "FFFFFF", fit: "shrink" }));
  if (c.sub) AT(sl, c.sub, T({ objectName: "sub", x: M, y: 4.5, w: CW, h: 0.5, fontFace: S.body, fontSize: 16, color: S.c.accentOnDark }));
  notes(sl, c);
  return { slide: sl, steps: [[{ n: "title", eff: "floatUp" }, { n: "sub", eff: "fade", start: "after" }]], autoFirst: true };
};

// 03 Bìa chia đôi — c: {img, kicker, title, sub, info}
L.biaChiaDoi = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  const left = o.flip ? 5.4 : 0;
  sl.addShape("rect", { objectName: "panel", x: left, y: 0, w: 4.6, h: H, fill: { color: S.c.dark }, line: { color: S.c.dark } });
  image(sl, S, c.img, { x: o.flip ? 0 : 4.6, y: 0, w: 5.4, h: H }, "img");
  const x = left + 0.5;
  kicker(sl, S, c.kicker, { dark: true }, { x, y: 1.2, w: 3.6 });
  AT(sl, c.title, T({ objectName: "title", x, y: 1.55, w: 3.6, h: 2.0, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 34, color: "FFFFFF", fit: "shrink" }));
  if (c.sub) AT(sl, c.sub, T({ objectName: "sub", x, y: 3.65, w: 3.6, h: 0.7, fontFace: S.body, fontSize: 15, color: S.c.accentOnDark }));
  if (c.info) AT(sl, c.info, T({ objectName: "info", x, y: 4.8, w: 3.6, h: 0.4, fontFace: S.body, fontSize: 11, color: "D5D9E2" }));
  notes(sl, c);
  return { slide: sl, steps: [[{ n: "img", eff: "fade" }, { n: "title", eff: "floatUp", start: "after" }, { n: "sub", eff: "fade", start: "after" }]], autoFirst: true };
};

// 04 Mục lục số lớn — c: {title, items:[...3–6]}
L.mucLuc = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  AT(sl, c.title || "Nội dung", T({ objectName: "title", x: M, y: 0.6, w: 3.0, h: 2.0, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 34, color: fg(S, o) }));
  const n = c.items.length, rowH = Math.min(0.78, 4.4 / n), y0 = (H - rowH * n) / 2;
  c.items.forEach((t, i) => {
    const y = y0 + i * rowH;
    AT(sl, String(i + 1).padStart(2, "0"), T({ objectName: `num${i}`, x: 4.0, y, w: 0.9, h: rowH, fontFace: S.head, bold: true, fontSize: 26, color: o.dark ? S.c.accentOnDark : S.c.accentText, valign: "middle" }));
    AT(sl, t, T({ objectName: `item${i}`, x: 4.95, y, w: 4.45, h: rowH, fontFace: S.body, fontSize: 18, color: fg(S, o), valign: "middle", fit: "shrink" }));
    if (i < n - 1) sl.addShape("line", { objectName: `ln${i}`, x: 4.0, y: y + rowH, w: 5.4, h: 0, line: { color: o.dark ? "3A4766" : "D9DCE3", width: 0.75 } });
  });
  notes(sl, c);
  return { slide: sl, steps: [c.items.flatMap((_, i) => [{ n: `num${i}`, eff: "fly", dir: "left", start: i ? "after" : "with", dur: 400 }, { n: `item${i}`, eff: "fly", dir: "left", dur: 400 }])] };
};

// 05 Chia phần — c: {num, title, sub}
L.chiaPhan = (pres, S, c, o = { dark: true }) => {
  const sl = addSlide(pres, c); sl.background = { color: o.dark ? S.c.dark : S.c.soft };
  // số lớn mờ nằm trọn trong lề phải (không sát/ra ngoài mép slide)
  AT(sl, String(c.num).padStart(2, "0"), T({ objectName: c.soMorph ? "!!so" : "bignum", x: W - M - 4.4, y: 0.3, w: 4.4, h: 3.4, fontFace: S.head, bold: true, fontSize: 200, color: o.dark ? "FFFFFF" : S.c.accent, transparency: o.dark ? 88 : 75, align: "right", valign: "top" }));
  const ts = 38, tl = Math.min(3, D.ngat(c.title, { face: S.head, size: ts, bold: true, w: 6.6 }).length), th = D.cao(tl, ts, D.heSo(S.head, true)) + 0.1;
  const yT = 3.85 - th;
  AT(sl, c.title, T({ objectName: "title", x: M, y: yT, w: 6.6, h: th, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: ts, color: fg(S, o), valign: "bottom", fit: "shrink" }));
  if (c.sub) AT(sl, c.sub, T({ objectName: "sub", x: M, y: 3.95, w: 6.6, h: 0.6, fontFace: S.body, fontSize: 16, color: sub(S, o) }));
  notes(sl, c);
  return { slide: sl, idle: [{ n: "bignum", eff: "mo", period: 7000, dur: 2000 }], steps: [[{ n: "bignum", eff: "fade", dur: 900 }, { n: "title", eff: "floatUp", start: "after" }, { n: "sub", eff: "fade", start: "after" }]], autoFirst: true };
};

// 06 Tuyên bố lớn — c: {statement, highlight?, by?}
L.tuyenBo = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  const runs = c.highlight && c.statement.includes(c.highlight)
    ? c.statement.split(c.highlight).flatMap((p, i, a) => (i < a.length - 1 ? [{ text: p }, { text: c.highlight, options: { color: sub(S, o) } }] : [{ text: p }])).filter((r) => r.text)
    : c.statement;
  AT(sl, runs, T({ objectName: "statement", x: 1.0, y: 1.2, w: 8.0, h: 2.8, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 36, color: fg(S, o), align: "center", valign: "middle", fit: "shrink" }));
  if (c.by) AT(sl, c.by, T({ objectName: "by", x: 1.0, y: 4.2, w: 8.0, h: 0.4, fontFace: S.body, fontSize: 14, color: mut(S, o), align: "center" }));
  notes(sl, c);
  return { slide: sl, idle: [{ n: "statement", eff: "doiMau", period: 12000, color: S.c.accentText }], steps: [[{ n: "statement", eff: "zoom", dur: 700 }]] };
};

// 07 Số liệu lớn — c: {kicker, value, label, context}
L.soLon = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  kicker(sl, S, c.kicker, o, { y: 0.9 });
  AT(sl, c.value, T({ objectName: "value", x: M, y: 1.2, w: 5.4, h: 2.3, fontFace: S.body, bold: true, fontSize: 110, color: o.dark ? S.c.accentOnDark : S.c.accentText, valign: "middle", fit: "shrink" }));
  AT(sl, c.label, T({ objectName: "label", x: M, y: 3.55, w: 5.2, h: 0.9, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 22, color: fg(S, o) }));
  if (c.context) {
    // khung ôm vừa nội dung (đo bằng phông thật), canh giữa theo khối số + nhãn — không để khung trống quá nửa
    const cs = sz(14, "context"), lines = D.ngat(c.context, { face: S.body, size: cs, w: 2.5 }).length;
    const hTxt = Math.min(2.6, D.cao(lines, cs, 1.2) + 0.05), hBox = hTxt + 0.5, yBox = Math.max(1.2, 2.85 - hBox / 2);
    sl.addShape("rect", { objectName: "ctxbox", x: 6.4, y: yBox, w: 3.0, h: hBox, fill: { color: o.dark ? S.c.soft : S.c.soft, transparency: o.dark ? 85 : 0 }, line: { color: o.dark ? S.c.accentOnDark : S.c.soft, width: 0.75 } });
    AT(sl, c.context, T({ objectName: "context", x: 6.65, y: yBox + 0.25, w: 2.5, h: hTxt, fontFace: S.body, fontSize: 14, color: o.dark ? "E6E8EE" : S.c.muted, valign: "middle", fit: "shrink" }));
  }
  notes(sl, c);
  return { slide: sl, idle: [{ n: "value", eff: "nhip", period: 9000 }], steps: [[{ n: "value", eff: "zoom" }, { n: "label", eff: "fade", start: "after" }], ...(c.context ? [[{ n: "ctxbox", eff: "fade" }, { n: "context", eff: "fade" }]] : [])] };
};

// 08 Trích dẫn — c: {quote, by, role}
L.trichDan = (pres, S, c, o = { dark: true }) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  AT(sl, "“", T({ objectName: "mark", x: M, y: 0.1, w: 1.5, h: 1.8, fontFace: S.head, bold: true, fontSize: 150, color: o.dark ? S.c.accentOnDark : S.c.accent }));
  AT(sl, c.quote, T({ objectName: "quote", x: 1.4, y: 1.3, w: 7.6, h: 2.5, fontFace: S.head, italic: true, fontSize: 28, color: fg(S, o), valign: "middle", fit: "shrink" }));
  sl.addShape("rect", { objectName: "rule", x: 1.4, y: 4.05, w: 0.6, h: 0.05, fill: { color: o.dark ? S.c.accentOnDark : S.c.accent }, line: { color: o.dark ? S.c.accentOnDark : S.c.accent } });
  AT(sl, [{ text: c.by, options: { bold: true, breakLine: !!c.role } }, ...(c.role ? [{ text: c.role }] : [])], T({ objectName: "by", x: 1.4, y: 4.2, w: 7.6, h: 0.7, fontFace: S.body, fontSize: 14, color: mut(S, o) }));
  notes(sl, c);
  return { slide: sl, idle: [{ n: "mark", eff: "nhip", period: 10000 }], steps: [[{ n: "quote", eff: "split" }], [{ n: "by", eff: "fade" }]] };
};

// 09 Ảnh – chữ (ảnh tràn nửa slide) — c: {img, kicker, title, bullets[]} ; o.flip: ảnh bên phải
L.anhChu = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  const ix = o.flip ? 5.4 : 0, tx = o.flip ? M : 5.85;
  image(sl, S, c.img, { x: ix, y: 0, w: 4.6, h: H }, "img");
  kicker(sl, S, c.kicker, {}, { x: tx, y: 0.75, w: 3.55 });
  AT(sl, c.title, T({ objectName: "title", x: tx, y: 1.05, w: 3.6, h: 1.3, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 26, color: S.c.text, fit: "shrink" }));
  AT(sl, c.bullets.map((b, i) => ({ text: b, options: { bullet: { indent: Math.round(sz(16, "body") * 0.9) }, breakLine: i < c.bullets.length - 1 } })),
    T({ objectName: "body", x: tx, y: 2.55, w: 3.6, h: 2.4, fontFace: S.body, fontSize: 16, color: S.c.muted, paraSpaceAfter: 8, fit: "shrink" }));
  notes(sl, c);
  return { slide: sl, steps: [[{ n: "body", eff: "wipe", dir: "left", byPara: true }]] };
};

// 10 Chữ – ảnh khung bo góc (có bóng đổ) — c: {img, title, text, points[]}
L.chuAnhKhung = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.soft };
  title(sl, S, c.title, {}, { w: 4.6, h: 1.3, y: 0.7, valign: "top", fontSize: 28 });
  if (c.text) AT(sl, c.text, T({ objectName: "text", x: M, y: 2.05, w: 4.4, h: 1.0, fontFace: S.body, fontSize: 15, color: S.c.muted, fit: "shrink" }));
  (c.points || []).slice(0, 3).forEach((p, i) => {
    AT(sl, [{ text: p[0], options: { bold: true, color: S.c.text, breakLine: true } }, { text: p[1], options: { color: S.c.muted } }],
      T({ objectName: `pt${i}`, x: M + i * 1.5, y: 3.35, w: 1.35, h: 1.5, fontFace: S.body, fontSize: 12 }));
    sl.addShape("rect", { objectName: `ptbar${i}`, x: M + i * 1.5, y: 3.2, w: 0.35, h: 0.05, fill: { color: S.c.accent }, line: { color: S.c.accent } });
  });
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: "frame", x: 5.6, y: 0.6, w: 3.8, h: 4.4, rectRadius: 0.2, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" }, shadow: { type: "outer", blur: 12, offset: 4, angle: 90, color: "000000", opacity: 0.18 } });
  image(sl, S, c.img, { x: 5.75, y: 0.75, w: 3.5, h: 4.1 }, "img");
  notes(sl, c);
  return { slide: sl, steps: [[{ n: "frame", eff: "fade" }, { n: "img", eff: "fade" }], [0, 1, 2].filter((i) => (c.points || [])[i]).map((i) => ({ n: `pt${i}`, eff: "floatUp", start: i ? "after" : "with" }))] };
};

// 11 So sánh hai cột — c: {title, left:{label, items[]}, right:{label, items[]}}
// Không dùng vòng "VS" ở giữa: hai cột tự nói lên sự đối lập (sáng – tối), khoảng hở giữa hai cột là đủ.
L.soSanh = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  title(sl, S, c.title);
  // khối cao vừa nội dung (đo bằng phông thật), canh giữa theo chiều dọc vùng nội dung
  const bs = sz(15, "L"), ls = 20, wL = 3.95, wR = CW - 4.15;
  const need = (side, w) => D.cao(side.items.reduce((s, it) => s + D.ngat(it, { face: S.body, size: bs, w: w - 0.7 - 0.35 }).length, 0), bs, 1.25) + 0.12 * side.items.length;
  const hText = Math.max(need(c.left, wL), need(c.right, wR));
  const hBox = Math.min(3.5, 0.3 + 0.6 + 0.15 + hText + 0.35), y0 = 1.55 + Math.max(0, (3.5 - hBox) / 2) * 0.5;
  const col = (side, x, w, dark, name) => {
    sl.addShape("rect", { objectName: name + "box", x, y: y0, w, h: hBox, fill: { color: dark ? S.c.dark : S.c.soft }, line: { color: dark ? S.c.dark : S.c.soft } });
    AT(sl, side.label, T({ objectName: name + "lab", x: x + 0.35, y: y0 + 0.3, w: w - 0.7, h: 0.55, fontFace: S.head, bold: true, fontSize: ls, color: dark ? S.c.accentOnDark : S.c.accentText, valign: "middle" }));
    AT(sl, side.items.map((t, i) => ({ text: t, options: { bullet: { indent: Math.round(bs * 0.9) }, breakLine: i < side.items.length - 1 } })),
      T({ objectName: name, x: x + 0.35, y: y0 + 0.95, w: w - 0.7, h: hBox - 1.15, fontFace: S.body, fontSize: 15, color: dark ? "FFFFFF" : S.c.text, paraSpaceAfter: 8, fit: "shrink" }));
  };
  // bất đối xứng nhẹ: bên được nhấn (phải) rộng hơn
  col(c.left, M, wL, false, "L"); col(c.right, M + 4.15, wR, true, "R");
  notes(sl, c);
  return { slide: sl, idle: [], steps: [[{ n: "Lbox", eff: "fly", dir: "left" }, { n: "Llab", eff: "fly", dir: "left" }, { n: "L", eff: "fly", dir: "left" }], [{ n: "Rbox", eff: "fly", dir: "right" }, { n: "Rlab", eff: "fly", dir: "right" }, { n: "R", eff: "fly", dir: "right" }]] };
};

// 12 Ba cột ý — c: {title, cards:[{mark?, head, text, img?}] 2–4}
// Không biểu tượng trong vòng tròn. Mỗi cột mở bằng một vạch mảnh màu nhấn; `mark` (tuỳ chọn) là một cụm chữ/số
// ngắn in lớn làm điểm nhìn (ví dụ "IB ≈ 0", "92%"); `img` (tuỳ chọn) là ảnh thật đặt đầu cột.
L.baThe = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  title(sl, S, c.title);
  const n = c.cards.length, w = (CW - GAP * (n - 1)) / n, hasImg = c.cards.some((k) => k.img), hasMark = c.cards.some((k) => k.mark);
  // đo chiều cao nội dung cột cao nhất → canh cả hàng cột giữa vùng nội dung (không dồn lên trên, để trống phía dưới)
  const hs = sz(19, "ct"), bs = sz(15, "ct");
  const colH = (k) => 0.2 + (hasImg ? 1.5 : 0) + (hasMark ? 0.9 : 0) + D.cao(D.ngat(k.head, { face: S.body, size: hs, bold: true, w }).length, hs, 1.2) + 0.08 + D.cao(D.ngat(k.text || "", { face: S.body, size: bs, w }).length, bs, 1.2);
  const hMax = Math.max(...c.cards.map(colH)), top = 1.6, bottom = 5.0;
  const y0 = top + Math.max(0, (bottom - top - hMax) / 2) * 0.7;
  c.cards.forEach((k, i) => {
    const x = M + i * (w + GAP);
    let y = y0;
    sl.addShape("rect", { objectName: `card${i}`, x, y, w, h: 0.04, fill: { color: i === c.highlight ? S.c.accent : S.c.text }, line: { color: i === c.highlight ? S.c.accent : S.c.text, width: 0 } });
    y += 0.2;
    if (hasImg) { image(sl, S, k.img, { x, y, w, h: 1.35 }, `img${i}`); y += 1.5; }
    if (hasMark) {
      AT(sl, k.mark || "", T({ objectName: `mk${i}`, x, y, w, h: 0.8, fontFace: S.head, bold: true, fontSize: 30, color: i === c.highlight ? S.c.accentText : S.c.text, valign: "middle", fit: "shrink" }));
      y += 0.9;
    }
    AT(sl, [{ text: k.head, options: { bold: true, fontSize: 19, color: S.c.text, breakLine: true } }, { text: k.text, options: { fontSize: 15, color: S.c.muted } }],
      T({ objectName: `ct${i}`, x, y, w, h: Math.max(0.6, 5.1 - y), fontFace: S.body, paraSpaceAfter: 6, fit: "shrink" }));
  });
  notes(sl, c);
  const hl = c.highlight != null ? c.highlight : null;
  return { slide: sl, idle: hl != null && hasMark ? [{ n: `mk${hl}`, eff: "gachChan", period: 12000 }] : [],
    steps: c.cards.map((k, i) => [{ n: `card${i}`, eff: "wipe", dir: "left", dur: 400 }, ...(hasImg ? [{ n: `img${i}`, eff: "fade" }] : []), ...(hasMark ? [{ n: `mk${i}`, eff: "floatUp" }] : []), { n: `ct${i}`, eff: "floatUp" }]) };
};

// 13 Hàng ý ngắn (4–5 ý) — c: {title, items:[{label, text}]}; o.dark: nền đậm
// Thay cho "hàng biểu tượng": các ý ngăn bằng vạch dọc mảnh, nhãn là chữ đậm lớn; không icon.
L.hangY = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  title(sl, S, c.title, o);
  const n = c.items.length, w = CW / n;
  c.items.forEach((k, i) => {
    const x = M + i * w;
    if (i) sl.addShape("line", { objectName: `vl${i}`, x, y: 1.75, w: 0, h: 2.9, line: { color: o.dark ? "3A4766" : "D9DCE3", width: 0.75 } });
    AT(sl, [{ text: k.label, options: { bold: true, fontSize: 20, color: fg(S, o), breakLine: !!k.text } }, ...(k.text ? [{ text: k.text, options: { fontSize: 14, color: mut(S, o) } }] : [])],
      T({ objectName: `it${i}`, x: x + (i ? 0.25 : 0), y: 1.8, w: w - 0.4, h: 2.8, fontFace: S.body, paraSpaceAfter: 6, fit: "shrink" }));
  });
  notes(sl, c);
  return { slide: sl, idle: [], steps: [c.items.flatMap((k, i) => [{ n: `it${i}`, eff: "fade", start: i ? "after" : "with", dur: 400 }])] };
};
L.hangIcon = (pres, S, c, o) => L.hangY(pres, S, { ...c, items: c.items.map(({ icon, ...r }) => r) }, o); // tên cũ, giữ để tương thích

// 14 Dòng thời gian — c: {title, events:[{time, text}] 3–6}
L.dongThoiGian = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  title(sl, S, c.title);
  const n = c.events.length, y = 3.15, x0 = M + 0.2, x1 = W - M - 0.2, step = (x1 - x0) / (n - 1 || 1);
  sl.addShape("line", { objectName: "axis", x: x0, y, w: x1 - x0, h: 0, line: { color: S.c.muted, width: 1.5 } });
  c.events.forEach((e, i) => {
    const cx = x0 + i * step, up = i % 2 === 0, bw = Math.min(2.0, step * 1.25);
    sl.addShape(pres.shapes.OVAL, { objectName: `dot${i}`, x: cx - 0.13, y: y - 0.13, w: 0.26, h: 0.26, fill: { color: S.c.accent }, line: { color: "FFFFFF", width: 2 } });
    AT(sl, [{ text: e.time, options: { bold: true, fontSize: 16, color: S.c.accentText, breakLine: true } }, { text: e.text, options: { fontSize: 13, color: S.c.text } }],
      T({ objectName: `ev${i}`, x: Math.max(M - 0.1, Math.min(cx - bw / 2, W - M - bw + 0.1)), y: up ? 1.6 : 3.45, w: bw, h: 1.35, fontFace: S.body, align: "center", valign: up ? "bottom" : "top", fit: "shrink" }));
  });
  notes(sl, c);
  return { slide: sl, idle: [{ n: `dot${c.events.length - 1}`, eff: "nhip", period: 8000 }], steps: [[{ n: "axis", eff: "wipe", dir: "left", dur: 800 }], ...c.events.map((_, i) => [{ n: `dot${i}`, eff: "zoom", dur: 300 }, { n: `ev${i}`, eff: "fade" }])] };
};

// 15 Biểu đồ + kết luận — c: {title, chart:{type, data, options}, takeaway, source}
L.bieuDo = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  title(sl, S, c.title);
  const type = { bar: pres.charts.BAR, line: pres.charts.LINE, pie: pres.charts.DOUGHNUT, doughnut: pres.charts.DOUGHNUT }[c.chart.type || "bar"];
  sl.addChart(type, c.chart.data, { objectName: "chart", x: M, y: 1.5, w: 5.6, h: 3.5, chartColors: [S.c.accent, S.c.dark, S.c.muted, S.c.accent2 || S.c.soft],
    showValue: true, dataLabelColor: S.c.text, dataLabelFontFace: S.body, dataLabelFontSize: sz(11, "cap0"), catAxisLabelFontSize: sz(11, "cap0"), valAxisLabelFontSize: sz(10, "cap0"), legendFontSize: sz(11, "cap0"), catAxisLabelColor: S.c.muted, valAxisLabelColor: S.c.muted,
    catAxisLabelFontFace: S.body, valAxisLabelFontFace: S.body, valGridLine: { color: "E3E6EB", size: 0.5 }, catGridLine: { style: "none" }, ...(c.chart.type === "bar" || !c.chart.type ? { valAxisMinVal: 0 } : {}), showLegend: (c.chart.data || []).length > 1, legendFontFace: S.body, legendPos: "b", ...(c.chart.options || {}) });
  // kết luận đứng cạnh biểu đồ: vạch dọc màu nhấn + câu kết luận cỡ lớn (không nhãn "Điểm chính", không hộp tối)
  sl.addShape("rect", { objectName: "tkbox", x: 6.6, y: 1.6, w: 0.05, h: 2.2, fill: { color: S.c.accent }, line: { color: S.c.accent, width: 0 } });
  AT(sl, c.takeaway, T({ objectName: "takeaway", x: 6.85, y: 1.55, w: 2.55, h: 3.3, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 20, color: S.c.text, fit: "shrink" }));
  if (c.source) AT(sl, "Nguồn: " + c.source, T({ objectName: "source", x: M, y: 5.12, w: 5.6, h: 0.3, fontFace: S.body, fontSize: 10, color: S.c.muted }));
  notes(sl, c);
  return { slide: sl, idle: [], steps: [[{ n: "chart", eff: "wipe", dir: "up", dur: 800 }], [{ n: "tkbox", eff: "wipe", dir: "down" }, { n: "takeaway", eff: "fade", start: "after" }]] };
};

// 16 Bento — c: {title, hero:{value,label}, tiles:[{head,text}] 3–4}
L.bento = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  title(sl, S, c.title);
  const y0 = 1.5, h = 3.55, g = 0.2;
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: "hero", x: M, y: y0, w: 3.9, h, rectRadius: 0.15, fill: { color: S.c.dark }, line: { color: S.c.dark } });
  AT(sl, [{ text: c.hero.value, options: { bold: true, fontSize: 64, color: S.c.accentOnDark, breakLine: true } }, { text: c.hero.label, options: { fontSize: 17, color: "FFFFFF" } }],
    T({ objectName: "herotxt", x: M + 0.35, y: y0 + 0.35, w: 3.2, h: h - 0.7, fontFace: S.body, valign: "bottom", fit: "shrink" }));
  const tw = (CW - 3.9 - g * 2) / 2, th = (h - g) / 2;
  c.tiles.slice(0, 4).forEach((t, i) => {
    const x = M + 3.9 + g + (i % 2) * (tw + g), y = y0 + Math.floor(i / 2) * (th + g);
    const wide = c.tiles.length === 3 && i === 2;
    const ww = wide ? tw * 2 + g : tw;
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: `tile${i}`, x, y, w: ww, h: th, rectRadius: 0.15, fill: { color: i === 1 ? S.c.accent : S.c.soft }, line: { color: i === 1 ? S.c.accent : S.c.soft } });
    AT(sl, [{ text: t.head, options: { bold: true, fontSize: 30, breakLine: true } }, { text: t.text, options: { fontSize: 13 } }],
      T({ objectName: `tt${i}`, x: x + 0.25, y: y + 0.22, w: ww - 0.5, h: th - 0.44, fontFace: S.body, color: i === 1 ? onAccent(S) : S.c.text, fit: "shrink" }));
  });
  notes(sl, c);
  return { slide: sl, idle: [{ n: "herotxt", eff: "nhip", period: 10000 }], steps: [[{ n: "hero", eff: "zoom" }, { n: "herotxt", eff: "zoom" }], c.tiles.slice(0, 4).flatMap((_, i) => [{ n: `tile${i}`, eff: "floatUp", start: i ? "after" : "with", dur: 400 }, { n: `tt${i}`, eff: "floatUp", dur: 400 }])] };
};

// 17 Lưới ảnh — c: {title, imgs:[3], caps:[3]}
L.luoiAnh = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  title(sl, S, c.title);
  const big = { x: M, y: 1.5, w: 5.0, h: 3.55 }, s1 = { x: M + 5.2, y: 1.5, w: 3.6, h: 1.68 }, s2 = { x: M + 5.2, y: 3.37, w: 3.6, h: 1.68 };
  [big, s1, s2].forEach((b, i) => {
    image(sl, S, (c.imgs || [])[i], b, `img${i}`);
    if ((c.caps || [])[i]) {
      sl.addShape("rect", { objectName: `capbg${i}`, x: b.x, y: b.y + b.h - 0.42, w: b.w, h: 0.42, fill: { color: S.c.dark, transparency: 25 }, line: { color: S.c.dark, transparency: 100 } });
      AT(sl, c.caps[i], T({ objectName: `cap${i}`, x: b.x + 0.15, y: b.y + b.h - 0.42, w: b.w - 0.3, h: 0.42, fontFace: S.body, fontSize: 12, color: "FFFFFF", valign: "middle" }));
    }
  });
  notes(sl, c);
  return { slide: sl, steps: [[0, 1, 2].map((i) => ({ n: `img${i}`, eff: "fade", start: i ? "after" : "with", dur: 500 }))] };
};

// 18 Quy trình mũi tên — c: {title, steps:[{head, text}] 3–5}
L.quyTrinh = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  title(sl, S, c.title);
  const n = c.steps.length, w = (CW + 0.25 * (n - 1)) / n;
  c.steps.forEach((s, i) => {
    const x = M + i * (w - 0.25);
    const fill = i === n - 1 ? S.c.accent : i % 2 ? S.c.dark : S.c.text;
    sl.addShape(i === 0 ? pres.shapes.PENTAGON : pres.shapes.CHEVRON, { objectName: `arr${i}`, x, y: 1.75, w, h: 0.95, fill: { color: fill }, line: { color: "FFFFFF", width: 1.5 } });
    AT(sl, `${String(i + 1).padStart(2, "0")}`, T({ objectName: `an${i}`, x: x + 0.35, y: 1.75, w: w - 0.7, h: 0.95, fontFace: S.head, bold: true, fontSize: 24, color: fill === S.c.accent ? onAccent(S) : "FFFFFF", align: "center", valign: "middle" }));
    AT(sl, [{ text: s.head, options: { bold: true, fontSize: 16, color: S.c.text, breakLine: true } }, { text: s.text, options: { fontSize: 13, color: S.c.muted } }],
      T({ objectName: `st${i}`, x: x + 0.15, y: 2.95, w: w - 0.45, h: 2.0, fontFace: S.body, fit: "shrink" }));
  });
  notes(sl, c);
  return { slide: sl, idle: [{ n: `arr${c.steps.length - 1}`, eff: "nhip", period: 10000 }], steps: c.steps.map((_, i) => [{ n: `arr${i}`, eff: "wipe", dir: "left" }, { n: `an${i}`, eff: "wipe", dir: "left" }, { n: `st${i}`, eff: "fade", start: "after" }]) };
};

// 19 Ma trận 2×2 — c: {title, xLabel, yLabel, cells:[{head,text}] x4 (trái-trên, phải-trên, trái-dưới, phải-dưới), highlight: index}
L.maTran = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  title(sl, S, c.title, {}, { w: 3.2, h: 1.6, y: 0.6, valign: "top", fontSize: 26 });
  if (c.note) AT(sl, c.note, T({ objectName: "note", x: M, y: 2.35, w: 3.0, h: 2.2, fontFace: S.body, fontSize: 14, color: S.c.muted, fit: "shrink" }));
  const gx = 4.3, gy = 0.75, cw = 2.5, ch = 2.05, g = 0.12;
  c.cells.forEach((k, i) => {
    const x = gx + (i % 2) * (cw + g), y = gy + Math.floor(i / 2) * (ch + g), hl = i === c.highlight;
    sl.addShape("rect", { objectName: `q${i}`, x, y, w: cw, h: ch, fill: { color: hl ? S.c.dark : S.c.soft }, line: { color: hl ? S.c.dark : S.c.soft } });
    AT(sl, [{ text: k.head, options: { bold: true, fontSize: 19, color: hl ? S.c.accentOnDark : S.c.text, breakLine: true } }, { text: k.text, options: { fontSize: 14, color: hl ? "FFFFFF" : S.c.muted } }],
      T({ objectName: `qt${i}`, x: x + 0.2, y: y + 0.2, w: cw - 0.4, h: ch - 0.4, fontFace: S.body, fit: "shrink" }));
  });
  if (c.xLabel) AT(sl, c.xLabel + "  →", T({ objectName: "xl", x: gx, y: gy + 2 * ch + g + 0.08, w: 2 * cw + g, h: 0.3, fontFace: S.body, fontSize: 11, color: S.c.muted, align: "right" }));
  if (c.yLabel) AT(sl, "↑  " + c.yLabel, T({ objectName: "yl", x: gx, y: gy - 0.32, w: 2 * cw + g, h: 0.28, fontFace: S.body, fontSize: 11, color: S.c.muted }));
  notes(sl, c);
  return { slide: sl, idle: c.highlight != null ? [{ n: `q${c.highlight}`, eff: "nhip", period: 10000 }] : [], steps: [[0, 1, 2, 3].flatMap((i) => [{ n: `q${i}`, eff: "zoom", start: i ? "after" : "with", dur: 350 }, { n: `qt${i}`, eff: "fade", dur: 350 }])] };
};

// 20 Bảng dữ liệu — c: {title, header[], rows[][], highlightRow, source}
L.bang = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  title(sl, S, c.title);
  const head = c.header.map((h, j) => ({ text: h, options: { bold: true, color: "FFFFFF", fill: { color: S.c.dark }, align: j ? "center" : "left" } }));
  const rows = c.rows.map((r, i) => r.map((v, j) => ({ text: String(v), options: { bold: i === c.highlightRow, color: i === c.highlightRow ? S.c.accentText : S.c.text, fill: { color: i === c.highlightRow ? S.c.soft : i % 2 ? "FFFFFF" : "F7F8FA" }, align: j ? "center" : "left" } })));
  const rh = Math.min(0.5, 3.3 / (rows.length + 1));
  sl.addTable([head, ...rows], { objectName: "table", x: M, y: 1.55, w: CW, colW: [CW * 0.4, ...c.header.slice(1).map(() => (CW * 0.6) / (c.header.length - 1))], rowH: Math.max(rh, 0.32 * K), fontFace: S.body, fontSize: sz(14),
    border: { type: "solid", pt: 0.5, color: "E3E6EB" }, margin: [0.05, 0.12, 0.05, 0.12], valign: "middle" });
  if (c.source) AT(sl, "Nguồn: " + c.source, T({ objectName: "source", x: M, y: 5.12, w: CW, h: 0.3, fontFace: S.body, fontSize: 10, color: S.c.muted }));
  notes(sl, c);
  return { slide: sl, steps: [[{ n: "table", eff: "fade" }]] };
};

// 21 Nhiệm vụ / hoạt động — c: {kicker, title, tasks[], time, product}
L.nhiemVu = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.soft };
  kicker(sl, S, c.kicker || "Hoạt động", {}, { y: 0.55 });
  title(sl, S, c.title, {}, { y: 0.8, h: 0.8, valign: "top", w: 6.2 });
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: "timebox", x: 7.3, y: 0.55, w: 2.1, h: 1.05, rectRadius: 0.5, fill: { color: S.c.accent }, line: { color: S.c.accent } });
  AT(sl, [{ text: c.time, options: { bold: true, fontSize: 26, breakLine: true } }, { text: "thời gian", options: { fontSize: 11 } }], T({ objectName: "time", x: 7.3, y: 0.6, w: 2.1, h: 0.95, fontFace: S.body, color: onAccent(S), align: "center", valign: "middle" }));
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: "taskbox", x: M, y: 1.85, w: 5.6, h: 3.2, rectRadius: 0.12, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" } });
  AT(sl, c.tasks.map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: i < c.tasks.length - 1 } })),
    T({ objectName: "tasks", x: M + 0.3, y: 2.1, w: 5.0, h: 2.75, fontFace: S.body, fontSize: 17, color: S.c.text, paraSpaceAfter: 10, fit: "shrink" }));
  sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: "prodbox", x: 6.5, y: 1.85, w: 2.9, h: 3.2, rectRadius: 0.12, fill: { color: S.c.dark }, line: { color: S.c.dark } });
  AT(sl, [{ text: "Sản phẩm", options: { bold: true, fontSize: 12, color: S.c.accentOnDark, breakLine: true } }, { text: c.product, options: { fontSize: 16, color: "FFFFFF" } }],
    T({ objectName: "prod", x: 6.75, y: 2.1, w: 2.4, h: 2.75, fontFace: S.body, paraSpaceAfter: 8, fit: "shrink" }));
  notes(sl, c);
  return { slide: sl, idle: [{ n: "timebox", eff: "rung", period: 15000 }], steps: [[{ n: "tasks", eff: "wipe", dir: "left", byPara: true }]] };
};

// 22 Kết thúc — c: {big, sub, contact}
L.ketThuc = (pres, S, c, o = { dark: true }) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  const deco = S.accentFont && S.muc !== "chinh-quy";
  AT(sl, c.big || "Trân trọng cảm ơn", T({ objectName: "big", x: M, y: 1.3, w: CW, h: 1.9, fontFace: deco ? S.accentFont : S.head, bold: !deco && !S.headItalic, italic: S.headItalic && !deco,
    fontSize: deco ? 66 : 48, color: o.dark ? S.c.accentOnDark : S.c.accentText, align: "center", valign: "middle", fit: "shrink" }));
  if (c.sub) AT(sl, c.sub, T({ objectName: "sub", x: M, y: 3.3, w: CW, h: 0.5, fontFace: S.body, fontSize: 18, color: fg(S, o), align: "center" }));
  if (c.contact) AT(sl, c.contact, T({ objectName: "contact", x: M, y: 4.6, w: CW, h: 0.4, fontFace: S.body, fontSize: 12, color: mut(S, o), align: "center" }));
  notes(sl, c);
  return { slide: sl, idle: [{ n: "big", eff: "doiMau", period: 8000, color: "FFFFFF" }], steps: [[{ n: "big", eff: "zoom", dur: 900 }, { n: "sub", eff: "fade", start: "after" }]], autoFirst: true };
};

// ================================================================ bố cục mở rộng (23–31)
// Rút từ dàn trang báo chí, áp phích Thuỵ Sĩ, bảng chú thích kỹ thuật — xem references/bo-cuc.md mục 2b và references/mau-bo-cuc.md

// 23 Công thức trung tâm (async) — c: {title, tex, terms:[{tex, text}] 2–4, note}
// Công thức là khối Equation gốc của PowerPoint (makeslides.equation). Dưới công thức: chú giải từng đại lượng.
L.congThuc = async (pres, S, c, o = {}) => {
  const MS = require(path.join(__dirname, "makeslides.js"));
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  title(sl, S, c.title, o);
  const eq = await MS.equation(sl, c.tex, { x: M, y: 1.75, fontSize: c.size || 40, color: fg(S, o), name: "eq" });   // cách tiêu đề ≥ 0,4"
  const terms = (c.terms || []).slice(0, 4), n = terms.length;
  if (n) {
    const y0 = Math.max(3.05, 1.55 + eq.h + 0.25), w = (CW - GAP * (n - 1)) / n;
    sl.addShape("line", { objectName: "rule", x: M, y: y0, w: CW, h: 0, line: { color: o.dark ? "3A4766" : "D9DCE3", width: 0.75 } });
    for (let i = 0; i < n; i++) {
      const x = M + i * (w + GAP);
      await MS.equation(sl, terms[i].tex, { x, y: y0 + 0.15, fontSize: 22, color: o.dark ? S.c.accentOnDark : S.c.accentText, name: `sym${i}` });
      AT(sl, terms[i].text, T({ objectName: `tx${i}`, x, y: y0 + 0.75, w, h: 5.15 - y0 - 0.75, fontFace: S.body, fontSize: 14, color: mut(S, o), fit: "shrink" }));
    }
  }
  if (c.note) AT(sl, c.note, T({ objectName: "note", x: M + eq.w + 0.4, y: 1.6, w: Math.max(2.2, CW - eq.w - 0.4), h: 1.2, fontFace: S.body, fontSize: 14, color: mut(S, o), valign: "middle", fit: "shrink" }));
  notes(sl, c);
  return { slide: sl, idle: [], steps: [[{ n: "eq", eff: "fade", dur: 800 }], ...(n ? [[{ n: "rule", eff: "wipe", dir: "left" }, ...terms.flatMap((_, i) => [{ n: `sym${i}`, eff: "fade", start: "after", dur: 300 }, { n: `tx${i}`, eff: "fade", dur: 300 }])]] : [])] };
};

// 24 Chữ khổng lồ tràn mép — c: {word, title, text}; o.dark
// Một từ/cụm 1–2 từ in cực lớn, cắt tràn mép phải-dưới làm hình nền chữ; tiêu đề và đoạn ngắn ở góc trên trái.
L.chuKhongLo = (pres, S, c, o = { dark: true }) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  AT(sl, c.word, T({ objectName: "word", x: 1.2, y: 1.9, w: 11, h: 4.6, fontFace: S.head, bold: true, fontSize: 230, color: o.dark ? "FFFFFF" : S.c.accent, transparency: o.dark ? 85 : 80, valign: "top" }));
  AT(sl, c.title, T({ objectName: "title", x: M, y: 0.6, w: 5.6, h: 1.4, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 34, color: fg(S, o), fit: "shrink" }));
  if (c.text) AT(sl, c.text, T({ objectName: "text", x: M, y: 2.1, w: 4.2, h: 1.4, fontFace: S.body, fontSize: 16, color: mut(S, o), fit: "shrink" }));
  notes(sl, c);
  return { slide: sl, idle: [], steps: [[{ n: "word", eff: "fade", dur: 1200 }, { n: "title", eff: "floatUp", start: "after" }, ...(c.text ? [{ n: "text", eff: "fade", start: "after" }] : [])]], autoFirst: true };
};

// 25 Thang số — c: {title, items:[{value, label}] 3–4} — số quan trọng nhất to nhất, các số sau nhỏ dần (thứ bậc rõ)
L.thangSo = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  title(sl, S, c.title, o);
  const items = c.items.slice(0, 4), m = items.length, sizes = [96, 56, 44, 40];
  const widths = [CW * (m <= 2 ? 0.55 : 0.4), ...Array(m - 1).fill((CW * (m <= 2 ? 0.45 : 0.6)) / Math.max(1, m - 1))];   // cột phụ đủ rộng cho nhãn ≥ 24pt
  // cỡ số: lớn nhất mà vẫn vừa một dòng trong cột (đo bằng phông thật)
  const sv = items.map((k, i) => D.vuaCo(String(k.value), { face: S.head, bold: true, size: sizes[i], w: widths[i] - 0.3, dong: 1, min: 28 }));
  const hv = Math.max(...sv.map((s) => D.dinh(s, S.head) + D.chan(s, S.head))) + 0.05;          // cao khối số = đỉnh + chân chữ lớn nhất
  const ls = items.map((k, i) => sz(i ? 13 : 16, "l" + i));
  const hl = Math.max(...items.map((k, i) => D.cao(D.ngat(k.label, { face: S.body, size: ls[i], w: widths[i] - 0.25 }).length, ls[i], 1.2)));
  const gap = Math.max(0.12, (0.12 * sv[0]) / 72 + 0.04);                                       // vạch cách chân chữ ≥ 6pt
  const blockH = hv + gap + 0.14 + hl, top = 1.45, bottom = 5.0;
  const yv = top + Math.max(0, (bottom - top - blockH) / 2);                                     // canh giữa vùng nội dung
  const base = yv + hv;
  let x = M;
  items.forEach((k, i) => {
    const w = widths[i];
    AT(sl, k.value, T({ objectName: `v${i}`, x, y: yv, w, h: hv, fontFace: S.head, bold: true, fontSize: sv[i], color: i ? fg(S, o) : (o.dark ? S.c.accentOnDark : S.c.accentText), valign: "bottom" }));
    sl.addShape("line", { objectName: `b${i}`, x, y: base + gap, w: w - 0.25, h: 0, line: { color: i ? (o.dark ? "3A4766" : "C9CED8") : S.c.accent, width: i ? 0.75 : 2.5 } });
    AT(sl, k.label, T({ objectName: `l${i}`, x, y: base + gap + 0.14, w: w - 0.25, h: hl + 0.1, fontFace: S.body, fontSize: i ? 13 : 16, color: mut(S, o) }));
    x += w;
  });
  notes(sl, c);
  return { slide: sl, idle: [{ n: "v0", eff: "nhip", period: 10000 }], steps: items.map((_, i) => [{ n: `v${i}`, eff: i ? "fade" : "zoom" }, { n: `b${i}`, eff: "wipe", dir: "left", start: "with" }, { n: `l${i}`, eff: "fade", start: "after", dur: 300 }]) };
};

// 26 Trang báo — c: {kicker, title, lead, body, pull, by} — dàn kiểu tạp chí: tiêu đề serif lớn, đoạn dẫn, thân bài 2 cột, trích dẫn kéo ra lề phải
L.baoChi = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  kicker(sl, S, c.kicker, {}, { y: 0.4, w: 6.2 });
  AT(sl, c.title, T({ objectName: "title", x: M, y: 0.68, w: 6.1, h: 1.35, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 32, color: S.c.text, valign: "top", fit: "shrink" }));
  if (c.lead) AT(sl, c.lead, T({ objectName: "lead", x: M, y: 2.1, w: 6.1, h: 0.9, fontFace: S.body, fontSize: 17, color: S.c.text, fit: "shrink" }));
  const body = Array.isArray(c.body) ? c.body : [c.body || ""], half = Math.ceil(body.length / 2);
  [body.slice(0, half), body.slice(half)].forEach((col, j) => {
    if (col.length) AT(sl, col.map((t, i) => ({ text: t, options: { breakLine: i < col.length - 1 } })), T({ objectName: `col${j}`, x: M + j * 3.15, y: 3.15, w: 2.95, h: 1.95, fontFace: S.body, fontSize: 13, color: S.c.muted, paraSpaceAfter: 6, fit: "shrink" }));
  });
  sl.addShape("line", { objectName: "vrule", x: 7.05, y: 0.7, w: 0, h: 4.4, line: { color: "D9DCE3", width: 0.75 } });
  if (c.pull) AT(sl, [{ text: c.pull, options: { breakLine: !!c.by } }, ...(c.by ? [{ text: c.by, options: { fontSize: 12, italic: false, color: S.c.muted, fontFace: S.body } }] : [])],
    T({ objectName: "pull", x: 7.3, y: 0.7, w: 2.1, h: 4.4, fontFace: S.head, italic: true, fontSize: 21, color: S.c.accentText, valign: "middle", paraSpaceAfter: 10, fit: "shrink" }));
  notes(sl, c);
  return { slide: sl, idle: [], steps: [[{ n: "lead", eff: "fade" }], [{ n: "col0", eff: "fade" }, ...(body.length > 1 ? [{ n: "col1", eff: "fade", start: "after" }] : [])], ...(c.pull ? [[{ n: "pull", eff: "floatUp" }]] : [])] };
};

// 27 Ảnh – khối chồng lớp — c: {img, kicker, title, text}; o.flip
// Ảnh lớn lệch một bên, khối màu đậm đè lên mép ảnh tạo chiều sâu; chữ nằm trên khối.
L.anhLopKhoi = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  const ix = o.flip ? 0 : 3.6, bx = o.flip ? 5.2 : M;
  image(sl, S, c.img, { x: ix, y: 0, w: 6.4, h: 4.55 }, "img");
  // đo tiêu đề và đoạn chữ bằng phông thật → khung vừa nội dung, đoạn chữ nối ngay dưới tiêu đề, cả cụm nằm trong khối
  const ts = sz(24, "title"), xs = sz(14, "text");
  const th = D.cao(D.ngat(c.title, { face: S.head, size: ts, bold: true, w: 3.5 }).length, ts, 1.2) + 0.08;
  const xh = c.text ? D.cao(D.ngat(c.text, { face: S.body, size: xs, w: 3.5 }).length, xs, 1.2) + 0.08 : 0;
  const bh = Math.max(2.75, 0.55 + th + 0.1 + xh + 0.3), by = Math.min(2.35, H - 0.15 - bh), ty = by + 0.55, xy = ty + th + 0.1;
  sl.addShape("rect", { objectName: "block", x: bx, y: by, w: 4.2, h: bh, fill: { color: S.c.dark }, line: { color: S.c.dark } });
  AT(sl, c.title, T({ objectName: "title", x: bx + 0.35, y: ty, w: 3.5, h: th, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 24, color: "FFFFFF", fit: "shrink" }));
  if (c.text) AT(sl, c.text, T({ objectName: "text", x: bx + 0.35, y: xy, w: 3.5, h: xh, fontFace: S.body, fontSize: 14, color: S.c.accentOnDark || "E6E8EE", fit: "shrink" }));
  kicker(sl, S, c.kicker, { dark: true }, { x: bx + 0.35, y: by + 0.25, w: 3.5 });
  notes(sl, c);
  return { slide: sl, idle: [], steps: [[{ n: "block", eff: "fly", dir: o.flip ? "right" : "left" }, { n: "title", eff: "fade", start: "after" }, ...(c.text ? [{ n: "text", eff: "fade", start: "after" }] : [])]] };
};

// 28 Hình có chú thích — c: {title, img, imgW?, callouts:[{px, py, text}] 2–5} (px, py: vị trí điểm trên ảnh, 0–1)
// Sơ đồ/ảnh kỹ thuật ở trái; số thứ tự nhỏ đặt ngay trên chi tiết, chú thích cùng số xếp bên phải (không kẻ đường dẫn cắt ngang hình).
L.hinhChuThich = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  title(sl, S, c.title);
  const box = { x: M, y: 1.45, w: c.imgW || 4.4, h: 3.7 };
  if (c.img) sl.addImage({ objectName: "img", path: c.img, ...box, sizing: { type: "contain", w: box.w, h: box.h } });
  else image(sl, S, null, box, "img");
  const n = c.callouts.length, lx = box.x + box.w + 0.45, lw = W - M - lx, rowH = Math.min(0.95, 3.7 / n);
  c.callouts.forEach((k, i) => {
    const px = box.x + k.px * box.w, py = box.y + k.py * box.h, ly = box.y + i * rowH, d = 0.26;
    // số thứ tự đặt ngay trên hình (không kẻ đường dẫn cắt ngang hình), danh sách chú thích cùng số ở bên phải
    sl.addShape(pres.shapes.OVAL, { objectName: `dot${i}`, x: px - d / 2, y: py - d / 2, w: d, h: d, fill: { color: S.c.accent }, line: { color: "FFFFFF", width: 1.25 } });
    AT(sl, String(i + 1), T({ objectName: `dn${i}`, x: px - d / 2, y: py - d / 2, w: d, h: d, fontFace: S.body, bold: true, fontSize: 11, color: onAccent(S), align: "center", valign: "middle" }));
    AT(sl, [{ text: String(i + 1) + "   ", options: { bold: true, color: S.c.accentText } }, { text: k.text }],
      T({ objectName: `cl${i}`, x: lx, y: ly, w: lw, h: rowH - 0.05, fontFace: S.body, fontSize: 14, color: S.c.text, valign: "top", fit: "shrink" }));
  });
  notes(sl, c);
  return { slide: sl, idle: [], steps: [[{ n: "img", eff: "fade" }], ...c.callouts.map((_, i) => [{ n: `dot${i}`, eff: "zoom", dur: 250 }, { n: `dn${i}`, eff: "zoom", dur: 250 }, { n: `cl${i}`, eff: "fade", start: "after", dur: 300 }])] };
};

// 29 Câu hỏi – lời đáp — c: {kicker, question, answer, hint}; o.dark
// Câu hỏi in rất lớn, căn trái, chiếm nửa trên; lời đáp hiện sau cú nhấp dưới một vạch mảnh.
L.hoiDap = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  // đo câu hỏi → cả cụm (nhãn, câu hỏi, gợi ý, vạch, lời đáp) canh giữa theo chiều dọc, không để khoảng trống lớn
  const qs = 38, ql = D.ngat(c.question, { face: S.head, size: qs, bold: true, w: CW }).length, qh = D.cao(ql, qs, D.heSo(S.head, true)) + 0.1;
  const as = sz(20, "answer"), ah = c.answer ? D.cao(D.ngat(c.answer, { face: S.body, size: as, w: CW }).length, as, 1.2) + 0.1 : 0;
  const hh = c.hint ? 0.5 : 0, kh = c.kicker ? 0.4 : 0;
  const blockH = kh + qh + (hh ? 0.15 + hh : 0) + (c.answer ? 0.35 + 0.25 + ah : 0);
  let y = Math.max(0.5, (H - blockH) / 2 - 0.1);
  if (c.kicker) { kicker(sl, S, c.kicker, o, { y }); y += kh; }
  AT(sl, c.question, T({ objectName: "question", x: M, y, w: CW, h: qh, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: qs, color: fg(S, o), valign: "top" }));
  y += qh;
  if (c.hint) { y += 0.15; AT(sl, c.hint, T({ objectName: "hint", x: M, y, w: CW, h: hh, fontFace: S.body, fontSize: 14, color: mut(S, o) })); y += hh; }
  if (c.answer) {
    y += 0.35;
    sl.addShape("line", { objectName: "rule", x: M, y, w: CW, h: 0, line: { color: o.dark ? S.c.accentOnDark : S.c.accent, width: 1.5 } });
    y += 0.25;
    AT(sl, c.answer, T({ objectName: "answer", x: M, y, w: CW, h: ah, fontFace: S.body, fontSize: 20, color: o.dark ? S.c.accentOnDark : S.c.accentText }));
  }
  notes(sl, c);
  return { slide: sl, idle: [], steps: c.answer ? [[{ n: "rule", eff: "wipe", dir: "left" }, { n: "answer", eff: "floatUp", start: "after" }]] : [] };
};

// 30 Lưới Thuỵ Sĩ — c: {title, facts:[{value, label}] 3, text}
// Lưới 12 cột chặt: tiêu đề rất lớn ở góc dưới trái (7 cột), ba dữ kiện xếp dọc ở cột phải ngăn bằng vạch mảnh.
L.luoiThuySy = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: bgOf(S, o) };
  const col = CW / 12;
  AT(sl, c.title, T({ objectName: "title", x: M, y: 2.2, w: col * 7, h: 2.9, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 40, color: fg(S, o), valign: "bottom", fit: "shrink" }));
  if (c.text) AT(sl, c.text, T({ objectName: "text", x: M, y: 0.6, w: col * 5, h: 1.4, fontFace: S.body, fontSize: 14, color: mut(S, o), fit: "shrink" }));
  const fx = M + col * 8, fw = col * 4, fh = 4.5 / 3;
  (c.facts || []).slice(0, 3).forEach((k, i) => {
    const y = 0.6 + i * fh;
    sl.addShape("line", { objectName: `fl${i}`, x: fx, y, w: fw, h: 0, line: { color: i ? (o.dark ? "3A4766" : "C9CED8") : (o.dark ? S.c.accentOnDark : S.c.accent), width: i ? 0.75 : 2 } });
    AT(sl, [{ text: k.value, options: { bold: true, fontSize: 30, fontFace: S.head, color: fg(S, o), breakLine: true } }, { text: k.label, options: { fontSize: 13, color: mut(S, o) } }],
      T({ objectName: `f${i}`, x: fx, y: y + 0.1, w: fw, h: fh - 0.2, fontFace: S.body, fit: "shrink" }));
  });
  notes(sl, c);
  return { slide: sl, idle: [], steps: [[{ n: "title", eff: "floatUp" }], (c.facts || []).slice(0, 3).flatMap((_, i) => [{ n: `fl${i}`, eff: "wipe", dir: "left", start: i ? "after" : "with", dur: 300 }, { n: `f${i}`, eff: "fade", dur: 300 }])] };
};

// 31 Các bước dọc — c: {title, sub, steps:[{head, text}] 3–5}
// Thay cho mũi tên chevron: khối tiêu đề đậm 1/3 trái; các bước xếp dọc bên phải, số bước nhỏ kiểu đơn cách, ngăn bằng vạch mảnh.
L.buocDoc = (pres, S, c, o = {}) => {
  const sl = addSlide(pres, c); sl.background = { color: S.c.light };
  sl.addShape("rect", { objectName: "panel", x: 0, y: 0, w: 3.5, h: H, fill: { color: S.c.dark }, line: { color: S.c.dark } });
  AT(sl, c.title, T({ objectName: "title", x: M, y: 0.6, w: 2.5, h: 2.6, fontFace: S.head, bold: !S.headItalic, italic: S.headItalic, fontSize: 28, color: "FFFFFF", fit: "shrink" }));
  if (c.sub) AT(sl, c.sub, T({ objectName: "sub", x: M, y: 3.4, w: 2.5, h: 1.5, fontFace: S.body, fontSize: 14, color: S.c.accentOnDark, fit: "shrink" }));
  const n = c.steps.length, x = 4.0, w = W - M - x, rh = 4.6 / n;
  c.steps.forEach((s, i) => {
    const y = 0.5 + i * rh;
    if (i) sl.addShape("line", { objectName: `sl${i}`, x, y, w, h: 0, line: { color: "D9DCE3", width: 0.75 } });
    AT(sl, String(i + 1).padStart(2, "0"), T({ objectName: `sn${i}`, x, y: y + 0.12, w: 0.6, h: 0.4, fontFace: S.accentFont && S.muc === "chinh-quy" ? S.accentFont : S.body, bold: true, fontSize: 14, color: S.c.accentText }));
    AT(sl, [{ text: s.head, options: { bold: true, fontSize: 17, color: S.c.text, breakLine: !!s.text } }, ...(s.text ? [{ text: s.text, options: { fontSize: 13, color: S.c.muted } }] : [])],
      T({ objectName: `st${i}`, x: x + 0.7, y: y + 0.1, w: w - 0.7, h: rh - 0.15, fontFace: S.body, fit: "shrink" }));
  });
  notes(sl, c);
  return { slide: sl, idle: [], steps: c.steps.map((_, i) => [{ n: `sn${i}`, eff: "fade", dur: 300 }, { n: `st${i}`, eff: "floatUp", start: "with" }]) };
};


// ================================================================ bộ nhận diện thương hiệu (assets/thuong-hieu/<ten>/)
// CHỈ dùng khi bài thuộc về đơn vị đó hoặc người dùng yêu cầu — xem references/thuong-hieu.md
const fs = require("fs");
const BRAND_DIR = path.join(__dirname, "..", "assets", "thuong-hieu");
function pngSize(f) { const b = fs.readFileSync(f); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }
// S = brand("bk-hcmut")  → phong cách lấy màu/phông từ brand.json, kèm S.brand (đường dẫn logo, hoạ tiết, quy tắc)
function brand(ten, { base } = {}) {
  const dir = path.join(BRAND_DIR, ten);
  const B = JSON.parse(fs.readFileSync(path.join(dir, "brand.json"), "utf8"));
  const s = base ? JSON.parse(JSON.stringify(STYLES[base])) : {};
  Object.assign(s, JSON.parse(JSON.stringify(B.style)));
  s.key = "thuong-hieu:" + ten;
  s.headItalic = false; s.head = s.fonts.head; s.body = s.fonts.body; s.accentFont = s.fonts.accent || null; s.c = s.colors;
  s.brand = { ten, dir, data: B, logo: (f) => path.join(dir, "logo", f), hoaTiet: (f) => path.join(dir, "hoa-tiet", f.endsWith(".png") ? f : f + ".png") };
  CUR = s;
  const w = checkPalette(s);
  if (w.length) console.warn(`[SlideWright] Bảng màu thương hiệu "${ten}" cần xem lại:\n  - ` + w.join("\n  - "));
  return s;
}
// Đặt logo đúng phiên bản theo nền: o = {kieu: "don"|"ngang", lang: "vi"|"en", dark, x, y, h, w, align: "left"|"center"|"right", name}
// Logo giữ đúng tỉ lệ (chỉ cho h hoặc w); nền tối tự dùng bản viền trắng.
function logo(sl, S, o = {}) {
  if (!S.brand) throw new Error("logo(): phong cách không có thương hiệu — dùng brand(<ten>)");
  const key = (o.kieu === "ngang" ? `ngang_${o.lang || "vi"}` : "don") + (o.dark ? "_nen_toi" : "");
  const f = (S.brand.data.tep_logo || {})[key];
  if (!f) throw new Error(`logo(): thương hiệu ${S.brand.ten} không có tệp "${key}" trong brand.json → tep_logo`);
  const file = S.brand.logo(f), { w: pw, h: ph } = pngSize(file);
  let h = o.h, w = o.w;
  if (h && !w) w = h * pw / ph; else if (w && !h) h = w * ph / pw; else if (!w && !h) { h = 0.5; w = h * pw / ph; }
  let x = o.x != null ? o.x : M;
  if (o.align === "center") x = (W - w) / 2; else if (o.align === "right") x = W - M - w;
  sl.addImage({ path: file, x, y: o.y != null ? o.y : 0.3, w, h, objectName: o.name || "logo", altText: "Logo " + S.brand.data.ten });
  return { x, y: o.y, w, h };
}
// Hoạ tiết thương hiệu: tên tệp trong hoa-tiet/ (không cần .png); box mặc định phủ cả slide.
// Hình thêm sau sẽ nằm trên: gọi hoaTiet trước khi thêm chữ nếu tự dựng slide; với bố cục có sẵn chỉ phủ hoạ tiết rất mờ (lưới nét).
function hoaTiet(sl, S, ten, box = {}, name = "motif") {
  const file = S.brand.hoaTiet(ten), { w: pw, h: ph } = pngSize(file);
  let w = box.w, h = box.h;
  if (w && !h) h = w * ph / pw; else if (h && !w) w = h * pw / ph; else if (!w && !h) { w = W; h = H; }
  sl.addImage({ path: file, x: box.x || 0, y: box.y || 0, w, h, objectName: name, altText: "hoa-tiet:" + ten });
}

// 32 Bìa thương hiệu — c: {title, sub, info, lang}; o.dark (mặc định nền xanh đậm)
// Logo đơn ở giữa phía trên, hoạ tiết cụm tam giác ở hai góc, tên trường (logo ngang) ở chân. Cần S = brand(...)
L.biaThuongHieu = (pres, S, c, o = { dark: true }) => {
  const sl = addSlide(pres, c); sl.background = { color: o.dark ? S.c.dark : S.c.light };
  if (!c.nen) {   // không có texture riêng (từ dinh_huong) → dùng cụm tam giác của bộ nhận diện
    hoaTiet(sl, S, o.dark ? "cum-toi-phai-tren" : "cum-sang-phai-tren", { x: W - 5.2, y: 0, w: 5.2 }, "motifA");
    hoaTiet(sl, S, o.dark ? "cum-toi-trai-duoi" : "cum-sang-trai-duoi", { x: 0, y: H - 3.18, w: 5.2 }, "motifB");
  }
  logo(sl, S, { kieu: "don", dark: o.dark, h: 0.85, y: 0.45, align: "center", name: "logo" });
  AT(sl, c.title, T({ objectName: "title", x: 1.0, y: 1.55, w: 8.0, h: 1.6, fontFace: S.head, bold: true, fontSize: 38, color: o.dark ? "FFFFFF" : S.c.dark, align: "center", valign: "middle", fit: "shrink" }));
  if (c.sub) AT(sl, c.sub, T({ objectName: "sub", x: 1.0, y: 3.2, w: 8.0, h: 0.55, fontFace: S.body, fontSize: 18, color: o.dark ? S.c.accentOnDark : S.c.accentText, align: "center" }));
  if (c.info) AT(sl, c.info, T({ objectName: "info", x: 1.0, y: 3.85, w: 8.0, h: 0.4, fontFace: S.body, fontSize: 12, color: o.dark ? "D5DCF0" : S.c.muted, align: "center" }));
  logo(sl, S, { kieu: "ngang", lang: c.lang || "vi", dark: o.dark, h: 0.36, y: H - 0.72, align: "center", name: "lockup" });
  notes(sl, c);
  return { slide: sl, steps: [[{ n: "title", eff: "floatUp" }, { n: "sub", eff: "fade", start: "after" }]], autoFirst: true };
};

// Texture/hoạ tiết bất kỳ (PNG trong suốt, ví dụ từ dinh_huong.taoTexture): phủ cả slide hoặc theo box.
// Gọi TRƯỚC khi thêm chữ nếu tự dựng slide (hình thêm sau nằm trên). Với bố cục có sẵn, texture phủ lên trên → chỉ dùng loại rất mờ.
function texture(sl, file, box = {}, name = "texture") {
  if (!file) return;
  const { w: pw, h: ph } = pngSize(file);
  let w = box.w, h = box.h;
  if (w && !h) h = w * ph / pw; else if (h && !w) w = h * pw / ph; else if (!w && !h) { w = W; h = H; }
  sl.addImage({ path: file, x: box.x || 0, y: box.y || 0, w, h, objectName: name, altText: "hoa-tiet:" + path.basename(file) });
}
// Đặt phong cách hiện hành (để chữ nhấn **…** lấy đúng màu) — dùng khi tự tạo S, ví dụ từ dinh_huong.apDung
function setCurrent(S) { CUR = S; return S; }

// Dấu thương hiệu cho slide nội dung: logo ngang nhỏ ở góc dưới trái (không che nội dung). o.dark cho nền tối.
function dauThuongHieu(sl, S, o = {}) { return logo(sl, S, { kieu: "ngang", lang: o.lang || "vi", dark: o.dark, h: 0.24, x: M, y: H - 0.38, name: o.name || "brandmark" }); }

// ---------------------------------------------------------------- lọc gợi ý hiệu ứng theo đối tượng thật có trên slide
// (bố cục có phần tuỳ chọn như sub, text, info: không có thì bỏ khỏi steps/idle, tránh lỗi "không thấy đối tượng")
function prune(r) {
  const names = new Set((r.slide._slideObjects || []).map((x) => x.options && x.options.objectName).filter(Boolean));
  if (!names.size) { r.idle = [...(r.slide._cho || []), ...(r.idle || [])]; return r; }
  const ok = (e) => names.has(e.n);
  r.steps = (r.steps || []).map((g) => g.filter(ok)).filter((g) => g.length);
  r.idle = [...(r.slide._cho || []), ...(r.idle || [])].filter(ok);
  if (r.ket) r.ket = r.ket.filter(ok);
  return r;
}
for (const k of Object.keys(L)) {
  const f = L[k];
  L[k] = (...a) => { const r = f(...a); return r && typeof r.then === "function" ? r.then(prune) : prune(r); };
}

// ---------------------------------------------------------------- kiểm tra cân bằng màu của phong cách
// Chữ màu sáng cùng tông với nền đậm (ví dụ chữ xanh nhạt trên nền xanh đậm) đọc được nhưng nhìn đơn điệu, "chìm":
// cảnh báo khi hai màu cùng có sắc độ (chroma ≥ 0.12, chữ ≥ 0.35) và lệch sắc (hue) < 30°.
function hueChroma(h) {
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.substr(i, 2), 16) / 255), mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
  let hue = 0;
  if (d) hue = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return [(hue * 60 + 360) % 360, d];
}
function sameHue(fgc, bgc) {
  const [h1, c1] = hueChroma(fgc), [h2, c2] = hueChroma(bgc), dh = Math.min(Math.abs(h1 - h2), 360 - Math.abs(h1 - h2));
  return c1 >= 0.35 && c2 >= 0.12 && dh < 30;
}
function checkPalette(S) {
  const c = S.c, warn = [];
  // màu đối nhau (lam–cam, đỏ–lục, vàng–tím…) và các luật phối màu khác: scripts/mau.js, references/phoi-mau.md
  for (const e of require(path.join(__dirname, "mau.js")).kiemTraBangMau(c)) if (e.loai === "doi-nhau") warn.push(`${e.cap}: ${e.noiDung}`);
  const pairs = [["accentOnDark", "dark", 4.5], ["accentText", "light", 4.5], ["accentText", "soft", 4.5], ["text", "soft", 7], ["muted", "light", 4.5], ["text", "light", 7]];
  for (const [a, b, min] of pairs) {
    if (!c[a] || !c[b]) continue;
    const cr = contrast(c[a], c[b]);
    if (cr < min) warn.push(`${a} ${c[a]} trên ${b} ${c[b]}: tương phản ${cr.toFixed(2)} < ${min}`);
    if (sameHue(c[a], c[b])) warn.push(`${a} ${c[a]} trên ${b} ${c[b]}: cùng tông màu (chữ sáng cùng sắc với nền) — đổi sang màu nhấn khác sắc hoặc trắng/ngà`);
  }
  return warn;
}

module.exports = { L, style, brand, logo, hoaTiet, texture, setCurrent, dauThuongHieu, icon, setScale, contrast, onAccent, sameHue, checkPalette, W, H, M, CW, GAP, LIST: Object.keys(L) };
