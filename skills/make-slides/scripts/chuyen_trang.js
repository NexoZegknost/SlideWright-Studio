// chuyen_trang.js — bộ chuyển trang của makeSlides: Morph là chủ đạo, kèm vài chuyển trang lướt hiện đại để hoà nhịp.
// Không dùng chuyển trang cổ điển (lật 3D, cắt, hoà tan nhoè hạt, ô cờ, rèm sáo, xoáy…) — scripts/kiem_tra_hieu_ung.py cảnh báo nếu gặp.
//
// Hai phần:
//   1) xml(spec) — dựng <p:transition> (Morph, push, pan, wipe, reveal, fade…) có nhánh dự phòng cho PowerPoint cũ.
//   2) Cảnh morph (canh) — các đối tượng trang trí "!!tên" xuất hiện trên MỌI slide với TƯ THẾ khác nhau theo vai slide
//      (bìa, nội dung, nhấn mạnh, chia phần, kết). Morph nội suy vị trí, cỡ, góc xoay, màu → mỗi lần chuyển slide các
//      khối trôi, xoay, đổi màu như một chuyển động liền mạch thay vì "lật trang".
//
//   const CT = require(LIB + "chuyen_trang.js");
//   const canh = CT.canh(S, { motif: ["quyDao", "tienDo"], tong: 9 });          // tong = số slide (thanh tiến độ)
//   L.baThe(pres, S, { ..., truoc: (sl) => canh.dat(sl, "noi-dung", { i: 4 }) });  // i = số thứ tự slide (1…tong)
//   PLAN[4].transition = CT.MORPH;                                              // hoặc { kieu: "morph", tuy: "byWord", toc: 1800 }
//
// Tài liệu: references/chuyen-trang.md

const W = 10, H = 5.625;

// ---------------------------------------------------------------- 1. XML chuyển trang
const NS_MC = 'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"';
const NS_P14 = 'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main"';
const NS_P159 = 'xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main"';
const spd = (ms) => (ms >= 1000 ? "slow" : ms >= 700 ? "med" : "fast");
const alt = (req, ns, choice, fallback) => `<mc:AlternateContent ${NS_MC}><mc:Choice ${ns} Requires="${req}">${choice}</mc:Choice><mc:Fallback>${fallback}</mc:Fallback></mc:AlternateContent>`;
const p14t = (ms, inner) => `<p:transition spd="${spd(ms)}" ${NS_P14} p14:dur="${ms}">${inner}</p:transition>`;
const plain = (ms, inner) => `<p:transition spd="${spd(ms)}">${inner}</p:transition>`;
const SIDE = { u: "u", d: "d", l: "l", r: "r", len: "u", xuong: "d", trai: "l", phai: "r" };

const KIEU = {
  none: () => "",
  // Morph — chủ đạo. tuy: byObject (mặc định) | byWord (chữ trượt theo từ) | byChar (chữ trượt theo ký tự)
  morph: ({ toc = 1600, tuy = "byObject" } = {}) =>
    alt("p159", NS_P159, `<p:transition spd="slow" ${NS_P14} p14:dur="${toc}"><p159:morph option="${tuy}"/></p:transition>`, plain(toc, "<p:fade/>")),
  // mờ chéo mượt — nền cho slide không có cảnh morph
  fade: ({ toc = 700 } = {}) => alt("p14", NS_P14, p14t(toc, "<p:fade/>"), plain(toc, "<p:fade/>")),
  // mờ qua nền tối — mở đầu, kết thúc, đổi phần lớn
  fadeBlack: ({ toc = 1200 } = {}) => alt("p14", NS_P14, p14t(toc, '<p:fade thruBlk="1"/>'), plain(toc, '<p:fade thruBlk="1"/>')),
  // lướt: cả slide trượt (pan — PowerPoint 2010+), đẩy (push), phủ (cover), kéo mở (pull)
  pan: ({ huong = "u", toc = 900 } = {}) => alt("p14", NS_P14, p14t(toc, `<p14:pan dir="${SIDE[huong] || "u"}"/>`), plain(toc, `<p:push dir="${SIDE[huong] || "u"}"/>`)),
  push: ({ huong = "u", toc = 900 } = {}) => alt("p14", NS_P14, p14t(toc, `<p:push dir="${SIDE[huong] || "u"}"/>`), plain(toc, `<p:push dir="${SIDE[huong] || "u"}"/>`)),
  cover: ({ huong = "l", toc = 900 } = {}) => alt("p14", NS_P14, p14t(toc, `<p:cover dir="${SIDE[huong] || "l"}"/>`), plain(toc, `<p:cover dir="${SIDE[huong] || "l"}"/>`)),
  pull: ({ huong = "l", toc = 900 } = {}) => alt("p14", NS_P14, p14t(toc, `<p:pull dir="${SIDE[huong] || "l"}"/>`), plain(toc, `<p:pull dir="${SIDE[huong] || "l"}"/>`)),
  // lau mềm mép
  wipe: ({ huong = "r", toc = 900 } = {}) => alt("p14", NS_P14, p14t(toc, `<p:wipe dir="${SIDE[huong] || "r"}"/>`), plain(toc, `<p:wipe dir="${SIDE[huong] || "r"}"/>`)),
  // hé lộ: slide cũ mờ dần sang tối rồi slide mới trượt nhẹ vào (Reveal, PowerPoint 2010+)
  reveal: ({ huong = "r", toc = 1400, toi = true } = {}) =>
    alt("p14", NS_P14, p14t(toc, `<p14:reveal${toi ? ' thruBlk="1"' : ""} dir="${huong === "l" || huong === "trai" ? "l" : "r"}"/>`), plain(toc, `<p:fade${toi ? ' thruBlk="1"' : ""}/>`)),
  // phóng nhẹ — đi sâu vào một ý
  zoom: ({ toc = 900 } = {}) => alt("p14", NS_P14, p14t(toc, "<p:zoom/>"), plain(toc, "<p:zoom/>")),
};
// spec: "morph" | ["push","u"] | { kieu, huong, toc, tuy, toi }
function xml(spec) {
  if (!spec) return "";
  let o = spec;
  if (typeof spec === "string") o = { kieu: spec };
  else if (Array.isArray(spec)) o = { kieu: spec[0], huong: spec[1], ...(spec[2] || {}) };
  const f = KIEU[o.kieu];
  if (!f) throw new Error(`Chuyển trang "${o.kieu}" không có. Có: ${Object.keys(KIEU).join(", ")}`);
  return f(o);
}
const MORPH = { kieu: "morph" }, MORPH_TU = { kieu: "morph", tuy: "byWord" }, MORPH_CHU = { kieu: "morph", tuy: "byChar" };

// ---------------------------------------------------------------- 2. cảnh morph
// Vai slide: bia | noi-dung | nhan-manh | chia-phan | ket. k: biến thể (slide nội dung liên tiếp dùng k khác nhau để khối di chuyển).
// Mỗi motif trả về danh sách hình {n, hinh, x, y, w, h, rot, mau, trong (độ trong %), vien}; tên tự thêm tiền tố "!!".
const VAI = ["bia", "noi-dung", "nhan-manh", "chia-phan", "ket"];
const mix = (a, b, t) => { const p = (h) => [0, 2, 4].map((i) => parseInt(h.substr(i, 2), 16)); const A = p(a), Bc = p(b); return A.map((v, i) => Math.round(v + (Bc[i] - v) * t).toString(16).padStart(2, "0")).join("").toUpperCase(); };

const MOTIF = {
  // Quỹ đạo: ba vầng tròn mờ trôi giữa các góc, phình to ở bìa/chia phần, thu nhỏ nép góc ở slide nội dung, tụ sau số liệu ở slide nhấn mạnh.
  quyDao: {
    mo: "Ba vầng tròn mờ trôi, phình, thu theo vai slide — hợp mọi phong cách, mềm mại",
    tuThe(vai, k, C, toi) {
      const c1 = toi ? C.accentOnDark : C.accent, c2 = toi ? C.accent : (C.accent2 || C.accent), c3 = toi ? "FFFFFF" : C.dark;
      const t1 = toi ? (vai === "nhan-manh" ? 91 : 86) : 84, t2 = toi ? 82 : 86, t3 = toi ? 88 : 90;
      const P = {
        bia:         [[6.0, -1.6, 5.8], [7.9, 3.1, 2.9], [5.3, 4.2, 1.1]],
        "chia-phan": [[-3.2, -1.8, 8.4], [7.7, 0.35, 2.2], [8.7, 4.25, 0.85]],
        "nhan-manh": [[-0.9, 0.5, 4.8], [8.2, 3.9, 1.05], [8.85, 0.55, 0.6]],
        ket:         [[W / 2 - 3.3, H / 2 - 3.3, 6.6], [-0.9, -0.9, 2.4], [8.6, 4.0, 1.3]],
        nd: [
          [[8.25, -1.25, 2.9], [9.15, 4.55, 1.3], [7.75, 5.0, 0.5]],
          [[-1.9, 4.3, 2.9], [8.85, -0.6, 1.5], [0.25, 0.18, 0.5]],
          [[8.45, 3.55, 3.0], [-0.75, -0.75, 1.7], [9.3, 0.42, 0.45]],
          [[-1.2, -1.4, 2.8], [8.7, 4.35, 1.4], [9.25, 0.3, 0.5]],
        ],
      };
      const p = vai === "noi-dung" ? P.nd[k % P.nd.length] : P[vai];
      return p.map(([x, y, d], i) => ({ n: `o${i + 1}`, hinh: "ellipse", x, y, w: d, h: d, mau: [c1, c2, c3][i], trong: [t1, t2, t3][i] }));
    },
  },
  // Dải lụa: một băng màu chéo quét qua slide — nằm ngang dưới chân bìa, dựng đứng ở chia phần, mảnh như đường kẻ ở nội dung,
  // phồng thành nền sau câu nhấn mạnh. Morph xoay + kéo dãn băng → cảm giác lụa bay.
  daiLua: {
    mo: "Băng màu chéo xoay, kéo dãn, mỏng thành đường kẻ — năng động, hợp bài trẻ, công nghệ, sự kiện",
    tuThe(vai, k, C, toi) {
      const m = toi ? C.accentOnDark : C.accent;
      const P = {
        bia:         { x: -2.0, y: 4.35, w: 14.0, h: 0.95, rot: -9, trong: toi ? 78 : 70 },
        "chia-phan": { x: 7.1, y: -1.4, w: 1.5, h: 8.6, rot: 14, trong: toi ? 80 : 74 },
        "nhan-manh": { x: -1.0, y: H / 2 - 1.25, w: 12.0, h: 2.5, rot: -4, trong: toi ? 90 : 88 },
        ket:         { x: -2.0, y: 0.25, w: 14.0, h: 0.8, rot: 7, trong: toi ? 78 : 72 },
        nd: [
          { x: 0.6, y: 0.3, w: 1.1, h: 0.07, rot: 0, trong: 0 },
          { x: W - 1.7, y: 0.3, w: 1.1, h: 0.07, rot: 0, trong: 0 },
          { x: 0.6, y: H - 0.38, w: 1.1, h: 0.07, rot: 0, trong: 0 },
        ],
      };
      const p = vai === "noi-dung" ? P.nd[k % P.nd.length] : P[vai];
      return [{ n: "dai", hinh: "rect", mau: m, ...p }];
    },
  },
  // Mảnh hình: tam giác, vuông, tròn, gạch nhỏ — bay sang vị trí mới và xoay mỗi lần chuyển slide (sinh động, bài cho học sinh, sự kiện)
  manhHinh: {
    mo: "Bốn mảnh hình nhỏ bay và xoay sang chỗ mới mỗi slide — vui, sinh động",
    tuThe(vai, k, C, toi) {
      const m = [toi ? C.accentOnDark : C.accent, toi ? "FFFFFF" : C.dark, toi ? C.accent : (C.accent2 || C.accent), toi ? C.accentOnDark : C.accent];
      const hinh = ["triangle", "rect", "ellipse", "rect"];
      const S = [[0.42, 0.42], [0.3, 0.3], [0.26, 0.26], [0.6, 0.07]];
      const P = {
        bia:         [[8.6, 0.6, 15], [9.1, 1.6, 30], [7.9, 4.6, 0], [8.3, 5.0, -20]],
        "chia-phan": [[0.55, 0.5, 200], [1.4, 4.7, 75], [9.2, 0.6, 0], [8.4, 4.9, 25]],
        "nhan-manh": [[0.6, 0.55, 330], [9.0, 4.85, 120], [0.75, 4.75, 0], [8.7, 0.5, -35]],
        ket:         [[4.6, 0.35, 180], [5.6, 4.95, 220], [3.9, 4.9, 0], [5.4, 0.45, 40]],
        nd: [
          [[9.35, 0.25, 40], [9.45, 5.05, 135], [0.18, 5.12, 0], [9.0, 0.38, 0]],
          [[0.15, 0.2, 260], [9.4, 0.25, 210], [9.5, 5.1, 0], [0.5, 5.2, 45]],
          [[9.35, 5.0, 120], [0.2, 0.25, 300], [9.45, 0.3, 0], [0.4, 5.2, -15]],
        ],
      };
      const p = vai === "noi-dung" ? P.nd[k % P.nd.length] : P[vai];
      return p.map(([x, y, rot], i) => ({ n: `m${i + 1}`, hinh: hinh[i], x, y, w: S[i][0], h: S[i][1], rot, mau: m[i], trong: i === 1 ? 35 : 10 }));
    },
  },
  // Chữ nền khổng lồ: một từ khoá của bài (canh(S, { chu: "…" })) cỡ 110–220pt, rất mờ, trượt ngang qua từng slide như lớp
  // nền chuyển động chậm hơn nội dung (parallax); phình to ở bìa và kết, dựng đứng ở chia phần.
  chuNen: {
    mo: "Từ khoá khổng lồ mờ trượt ngang qua các slide (parallax) — ấn tượng, hợp bìa/kết và bài một chủ đề",
    tuThe(vai, k, C, toi, { chu = "" } = {}) {
      if (!chu) return [];
      const m = toi ? "FFFFFF" : C.dark;
      const P = {
        bia:         { x: -0.4, y: 3.55, w: 16, h: 2.4, co: 170, rot: 0, trong: toi ? 92 : 93 },
        "chia-phan": { x: -4.2, y: 1.6, w: 11, h: 2.2, co: 150, rot: -90, trong: toi ? 92 : 93 },
        "nhan-manh": { x: 2.6, y: 4.0, w: 16, h: 2.2, co: 150, rot: 0, trong: toi ? 94 : 95 },
        ket:         { x: -0.2, y: 3.4, w: 16, h: 2.4, co: 170, rot: 0, trong: toi ? 92 : 93 },
        nd: [0, 1, 2, 3].map((j) => ({ x: 1.2 - j * 2.6, y: 4.3, w: 16, h: 2.0, co: 120, rot: 0, trong: toi ? 94 : 95 })),
      };
      const p = vai === "noi-dung" ? P.nd[k % P.nd.length] : P[vai];
      return [{ n: "chu", chu, mau: m, ...p }];
    },
  },
  // Thanh tiến độ mảnh dưới chân slide: dài dần theo vị trí slide trong bài → mỗi lần chuyển, thanh trườn tới.
  tienDo: {
    mo: "Thanh tiến độ mảnh dưới chân slide, trườn dài theo bài — kín đáo, hợp mọi bài",
    tuThe(vai, k, C, toi, { i = 1, tong = 1 } = {}) {
      const t = tong > 1 ? (i - 1) / (tong - 1) : 1, w = Math.max(0.06, W * t);
      return [
        { n: "tdNen", hinh: "rect", x: 0, y: H - 0.06, w: W, h: 0.06, mau: toi ? "FFFFFF" : C.dark, trong: toi ? 88 : 92 },
        { n: "td", hinh: "rect", x: 0, y: H - 0.06, w, h: 0.06, mau: toi ? C.accentOnDark : C.accent, trong: 0 },
      ];
    },
  },
};

function canh(S, { motif = ["quyDao", "tienDo"], tong = 1, chu = "" } = {}) {
  const C = S.c || S.colors;
  const dem = {};
  return {
    motif,
    // vẽ cảnh lên slide sl (gọi ngay sau nền: c.truoc). o: { i: số thứ tự slide, k: biến thể (mặc định tự tăng theo vai), toi: nền tối? }
    dat(sl, vai, o = {}) {
      if (!VAI.includes(vai)) throw new Error(`Vai "${vai}" không có. Có: ${VAI.join(", ")}`);
      const k = o.k != null ? o.k : (dem[vai] = (dem[vai] ?? -1) + 1);
      const toi = o.toi != null ? o.toi : ["bia", "chia-phan", "ket"].includes(vai);
      for (const m of motif) {
        const M = MOTIF[m];
        if (!M) throw new Error(`Motif "${m}" không có. Có: ${Object.keys(MOTIF).join(", ")}`);
        for (const s of M.tuThe(vai, k, C, toi, { i: o.i, tong, chu })) {
          if (s.chu) {
            sl.addText(s.chu, { objectName: "!!" + s.n, x: s.x, y: s.y, w: s.w, h: s.h, rotate: s.rot || 0, margin: 0, fontFace: S.head, bold: true,
              fontSize: s.co, color: s.mau, transparency: s.trong, valign: "top", wrap: false, altText: "chu-nen" });
            continue;
          }
          sl.addShape(s.hinh, {
            objectName: "!!" + s.n, x: s.x, y: s.y, w: s.w, h: s.h, rotate: s.rot || 0,
            fill: { color: s.mau, transparency: s.trong || 0 }, line: { color: s.mau, transparency: 100 },
          });
        }
      }
      return [];   // trả mảng idle (chỗ để gắn hiệu ứng chờ cho cảnh nếu cần)
    },
  };
}

// Số phần thu thành huy hiệu: slide chia phần dựng bằng L.chiaPhan(..., { soMorph: true, ... }) (số lớn tên "!!so");
// slide nội dung ĐẦU của phần gọi soPhan(sl, S, so) → số lớn co lại, bay lên góc phải thành huy hiệu nhỏ.
function soPhan(sl, S, so, { x = 8.75, y = 0.5, w = 0.75, h = 0.45, toi = false } = {}) {
  const C = S.c || S.colors;
  sl.addText(String(so).padStart(2, "0"), { objectName: "!!so", x, y, w, h, margin: 0, fontFace: S.head, bold: true, fontSize: 22,
    color: toi ? C.accentOnDark : C.accentText, align: "right", valign: "top" });
  return [];
}

// Ảnh morph: cùng một ảnh trên hai slide liên tiếp với khung khác nhau (nhỏ → tràn viền, góc trái → góc phải…).
// Trả về đối tượng ảnh cho layouts.js (tham số img của bố cục): { duong, ten } — ten bắt đầu bằng "!!".
const anh = (duong, ten = "anh") => ({ duong, ten: ten.startsWith("!!") ? ten : "!!" + ten });

module.exports = { xml, KIEU: Object.keys(KIEU), MORPH, MORPH_TU, MORPH_CHU, canh, anh, soPhan, MOTIF: Object.fromEntries(Object.entries(MOTIF).map(([k, v]) => [k, v.mo])), VAI };

if (require.main === module) {
  console.log("Chuyển trang:", Object.keys(KIEU).join(", "));
  for (const [k, v] of Object.entries(MOTIF)) console.log(`  motif ${k.padEnd(9)} ${v.mo}`);
}
