// mau.js — màu sắc cho SlideWright - Studio: chuyển đổi OKLCH, tương phản, kiểm tra phối màu, tạo bảng màu theo luật hài hoà.
// Quy tắc: references/phoi-mau.md
//
//   const C = require("./mau.js");
//   C.kiemTraCap("FFB547", "0A1931")   → [{muc, loai, noiDung}]   (rỗng = hợp)
//   C.kiemTraBangMau(S.c)              → cảnh báo cho cả bảng màu phong cách
//   C.taoBangMau({ hue: 265, chroma: 0.12, kieu: "tuong-dong", lechNhan: -40, nen: "lanh" }) → colors như styles.json

// ---------------------------------------------------------------- chuyển đổi
const hex2rgb = (h) => [0, 2, 4].map((i) => parseInt(h.replace("#", "").substr(i, 2), 16) / 255);
const rgb2hex = (c) => c.map((v) => Math.round(Math.max(0, Math.min(1, v)) * 255).toString(16).padStart(2, "0")).join("").toUpperCase();
const lin = (v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
const delin = (v) => (v <= 0.0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - 0.055);
function hex2oklch(h) {
  const [r, g, b] = hex2rgb(h).map(lin);
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  const L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s;
  const A = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s;
  const B = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;
  return { L, C: Math.hypot(A, B), H: ((Math.atan2(B, A) * 180) / Math.PI + 360) % 360 };
}
function oklch2rgb({ L, C, H }) {
  const a = C * Math.cos((H * Math.PI) / 180), b = C * Math.sin((H * Math.PI) / 180);
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3, s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3;
  return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s].map(delin);
}
// về hex, tự giảm sắc độ (chroma) nếu ra ngoài gam màu sRGB
function oklch2hex(o) {
  let c = o.C;
  for (let i = 0; i < 60; i++) {
    const rgb = oklch2rgb({ ...o, C: c });
    if (rgb.every((v) => v >= -0.001 && v <= 1.001)) return rgb2hex(rgb);
    c *= 0.95;
  }
  return rgb2hex(oklch2rgb({ ...o, C: 0 }));
}

// ---------------------------------------------------------------- đo
function lum(h) { const [r, g, b] = hex2rgb(h).map(lin); return 0.2126 * r + 0.7152 * g + 0.0722 * b; }
const contrast = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };
// sắc độ kiểu HSV (max - min) và góc màu RGB
function hsv(h) {
  const [r, g, b] = hex2rgb(h), mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
  let hue = 0;
  if (d) hue = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return { hue: (hue * 60 + 360) % 360, chroma: d, value: mx };
}
// Góc màu trên vòng thuần sắc của hoạ sĩ (đỏ – vàng – lam, RYB): ở đó cặp đối nhau là lam – cam, đỏ – lục, vàng – tím,
// đúng với cách nói "màu đối nhau" thông thường (vòng RGB lại cho đỏ đối lục lam).
const RGB2RYB = [[0, 0], [30, 60], [60, 120], [120, 180], [240, 240], [300, 300], [360, 360]];
function ryb(rgbHue) {
  for (let i = 1; i < RGB2RYB.length; i++) {
    const [a0, b0] = RGB2RYB[i - 1], [a1, b1] = RGB2RYB[i];
    if (rgbHue <= a1) return b0 + ((rgbHue - a0) * (b1 - b0)) / (a1 - a0);
  }
  return rgbHue;
}
const hueDist = (a, b) => { const d = Math.abs(a - b) % 360; return Math.min(d, 360 - d); };
const rybDist = (x, y) => hueDist(ryb(hsv(x).hue), ryb(hsv(y).hue));

// ---------------------------------------------------------------- luật
const LUAT = {
  doiNhau: 140,       // lệch ≥ 140° trên vòng RYB = đối nhau/gần đối nhau (lam–cam, đỏ–lục, vàng–tím) → tránh
  cungTong: 30,       // chữ sáng có sắc lệch < 30° so với nền đậm có sắc = đơn sắc chìm
  sac: 0.12,          // dưới ngưỡng này coi như màu trung tính (trắng, xám, ngà, đen than) → không tính phối màu
  sacManh: 0.35,      // màu "tươi"
  timTu: 255, timDen: 335,   // dải tím – tím hồng (HSV): trên nền tối chữ tím có độ sáng cảm nhận thấp → chìm, cấm
  nenToi: 0.2,        // độ chói nền dưới ngưỡng này = nền tối
  tuongPhanToi: 7,    // chữ màu trên nền tối phải đạt 7:1 (chữ trắng/ngà luôn đạt)
};
const laNenToi = (h) => lum(h) < LUAT.nenToi;
const laTim = (h) => { const x = hsv(h); return x.chroma >= 0.15 && x.hue >= LUAT.timTu && x.hue <= LUAT.timDen; };
// Kiểm một cặp màu (fg trên bg, hoặc hai màu nhấn đứng cạnh nhau). vaiTro: "chu" (chữ trên nền) | "canh" (hai mảng cạnh nhau)
function kiemTraCap(a, b, { vaiTro = "chu", coChu = 16, dam = false } = {}) {
  const out = [], A = hsv(a), B = hsv(b);
  const coSac = A.chroma >= LUAT.sac && B.chroma >= LUAT.sac, tuoi = Math.max(A.chroma, B.chroma) >= LUAT.sacManh;
  if (coSac && tuoi && rybDist(a, b) >= LUAT.doiNhau)
    out.push({ muc: "LỖI", loai: "doi-nhau", noiDung: `${a} và ${b} là hai màu đối nhau (lệch ${Math.round(rybDist(a, b))}° trên vòng màu) — chọn màu tương đồng hoặc hạ một màu về trung tính` });
  if (vaiTro === "chu") {
    const cr = contrast(a, b), can = coChu >= 18 || (coChu >= 14 && dam) ? 3 : 4.5;
    if (cr < can) out.push({ muc: "LỖI", loai: "tuong-phan", noiDung: `${a} trên ${b} tương phản ${cr.toFixed(2)} < ${can}` });
    if (laNenToi(b) && laTim(a))
      out.push({ muc: "LỖI", loai: "tim-tren-nen-toi", noiDung: `chữ tím ${a} trên nền tối ${b} bị chìm — dùng trắng, ngà, hoặc màu sáng ấm/lục bạc hà đạt 7:1` });
    if (laNenToi(b) && A.chroma >= 0.12 && cr < LUAT.tuongPhanToi)
      out.push({ muc: "LỖI", loai: "tuong-phan-nen-toi", noiDung: `chữ màu ${a} trên nền tối ${b} chỉ đạt ${cr.toFixed(2)}:1 (cần ≥ ${LUAT.tuongPhanToi}:1) — sáng hơn hoặc dùng trắng/ngà` });
    if (A.chroma >= LUAT.sacManh && B.chroma >= LUAT.sac && hueDist(A.hue, B.hue) < LUAT.cungTong && A.value > B.value)
      out.push({ muc: "CẢNH BÁO", loai: "cung-tong", noiDung: `chữ ${a} cùng tông với nền ${b} — dùng trắng/ngà hoặc màu tương đồng lệch 30–90°` });
  }
  return out;
}
// Kiểm cả bảng màu phong cách (các khoá như styles.json)
function kiemTraBangMau(c) {
  const out = [];
  const cap = [["accentOnDark", "dark", "chu"], ["accentText", "light", "chu"], ["accentText", "soft", "chu"], ["text", "light", "chu"], ["text", "soft", "chu"], ["muted", "light", "chu"],
    ["accent", "dark", "canh"], ["accent", "accent2", "canh"], ["accentOnDark", "accent", "canh"], ["accent2", "dark", "canh"], ["accent3", "accent", "canh"], ["accent3", "accent2", "canh"]];
  for (const [x, y, v] of cap) if (c[x] && c[y]) for (const e of kiemTraCap(c[x], c[y], { vaiTro: v })) out.push({ ...e, cap: `${x}/${y}` });
  return out;
}

// ---------------------------------------------------------------- tạo bảng màu
// kieu: "don-sac" (một sắc, nhiều độ sáng) | "tuong-dong" (các sắc kề nhau 30–60°) | "tuong-dong-am" … ; nen: "lanh" | "am" | "trung-tinh"
// hue: góc OKLCH của màu chủ đạo (hoặc truyền mauChu: hex để neo theo thương hiệu)
function taoBangMau(o = {}) {
  const goc = o.mauChu ? hex2oklch(o.mauChu) : { L: 0.3, C: o.chroma || 0.12, H: o.hue == null ? 260 : o.hue };
  const H = goc.H, Cc = Math.max(0.04, Math.min(goc.C, 0.2));
  const lech = o.lechNhan != null ? o.lechNhan : o.kieu === "don-sac" ? 0 : -40;   // độ lệch sắc của màu nhấn so với màu chủ đạo
  const lech2 = o.lechPhu != null ? o.lechPhu : o.kieu === "don-sac" ? 0 : lech > 0 ? -30 : 30;
  const nenH = o.nen === "am" ? 75 : o.nen === "lanh" ? H : H;
  const nenC = o.nen === "am" ? 0.018 : o.nen === "trung-tinh" ? 0.004 : 0.012;
  const c = {};
  // màu chủ đạo: giữ nguyên màu thương hiệu, hoặc (khi lĩnh vực cần trầm hơn) cùng sắc nhưng đậm/trầm hơn: o.darkL, o.darkCmax
  if (o.mauChu && hex2oklch(o.mauChu).L < 0.5 && !o.darkL) c.dark = o.mauChu.toUpperCase();
  else c.dark = oklch2hex({ L: o.darkL || o.dDark || 0.28, C: Math.min(o.mauChu ? hex2oklch(o.mauChu).C : Cc, o.darkCmax || 0.13), H });
  c.light = o.nen === "am" ? oklch2hex({ L: 0.985, C: 0.008, H: 80 }) : "FFFFFF";
  c.soft = oklch2hex({ L: 0.955, C: nenC, H: nenH });
  c.text = oklch2hex({ L: 0.26, C: Math.min(Cc, 0.06), H });
  c.muted = oklch2hex({ L: 0.47, C: Math.min(Cc, 0.035), H });
  const nh = (H + lech + 360) % 360;
  c.accent = oklch2hex({ L: o.lNhan || 0.62, C: o.cNhan || 0.15, H: nh });
  c.accent2 = oklch2hex({ L: 0.7, C: (o.cNhan || 0.15) * 0.8, H: (H + lech2 + 360) % 360 });
  // chữ nhấn trên nền sáng: tối dần đến khi đạt 4.6:1 với light và soft
  let L = 0.55;
  do { c.accentText = oklch2hex({ L, C: o.cNhan || 0.15, H: nh }); L -= 0.01; } while (Math.min(contrast(c.accentText, c.light), contrast(c.accentText, c.soft)) < 4.6 && L > 0.2);
  // chữ nhấn trên nền đậm: sắc tương đồng lệch 35–80° (không cùng tông, không đối nhau), đủ sáng; không đạt → ngà/trắng ngả sắc
  // chữ nhấn trên nền đậm. o.chuNhanToi: "nga" (ngà ấm — mặc định cho bài trầm, học thuật) | "trang" | "tuong-dong" (sắc tương đồng sáng)
  // Luật: không tím/tím hồng, không cùng tông nền, không đối nhau, tương phản ≥ 7:1.
  const NGA = oklch2hex({ L: 0.93, C: 0.045, H: 85 });
  c.accentOnDark = null;
  if (o.chuNhanToi === "nga") c.accentOnDark = NGA;
  else if (o.chuNhanToi === "trang") c.accentOnDark = "FFFFFF";
  else {
    const sgn = lech >= 0 ? 1 : -1, thu = [];
    for (const d of [40, 45, 50, 55, 60, 70, 80, 90]) thu.push((H + sgn * d + 360) % 360);
    for (const d of [40, 45, 50, 55, 60, 70, 80, 90]) thu.push((H - sgn * d + 360) % 360);
    for (const hh of thu) {
      for (const [LL, cc] of [[0.88, 0.13], [0.9, 0.1], [0.92, 0.08]]) {
        const cand = oklch2hex({ L: LL, C: cc, H: hh });
        if (!kiemTraCap(cand, c.dark).length && hueDist(hsv(cand).hue, hsv(c.dark).hue) >= 45) { c.accentOnDark = cand; break; }
      }
      if (c.accentOnDark) break;
    }
  }
  if (o.kieu === "don-sac" && o.chuNhanToi !== "tuong-dong") c.accentOnDark = o.chuNhanToi === "trang" ? "FFFFFF" : NGA;
  if (!c.accentOnDark) c.accentOnDark = NGA;
  c.surfaceDark = oklch2hex({ L: 0.36, C: Math.min(Cc, 0.12), H });
  return c;
}

// Mô tả ngắn một màu (đặt tên gợi nhớ khi trình bày phương án)
function moTa(h) {
  if (!h) return "—";
  const { hue, chroma, value } = hsv(h);
  if (chroma < 0.08) return value > 0.9 ? "trắng" : value > 0.6 ? "xám nhạt" : value > 0.3 ? "xám" : "đen than";
  if (chroma < 0.25 && value > 0.85 && hue >= 25 && hue <= 70) return "ngà";
  const names = [[15, "đỏ"], [40, "cam"], [65, "vàng"], [90, "vàng chanh"], [150, "lục"], [190, "lục lam"], [245, "lam"], [275, "chàm"], [320, "tím"], [345, "tím hồng"], [360, "đỏ"]];
  const n = names.find(([a]) => hue <= a)[1];
  return (value < 0.45 ? n + " đậm" : value > 0.85 && chroma < 0.4 ? n + " nhạt" : n);
}

module.exports = { laTim, laNenToi, hex2oklch, oklch2hex, contrast, hsv, ryb, rybDist, hueDist, LUAT, kiemTraCap, kiemTraBangMau, taoBangMau, moTa };
