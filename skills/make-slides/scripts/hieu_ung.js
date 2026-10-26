// hieu_ung.js — thư viện hiệu ứng động (animation) của makeSlides, viết thẳng XML <p:timing> của PowerPoint.
// Bốn nhóm, đúng như khung Animation của PowerPoint:
//   MO_DAU   (Entrance, xanh lá)  — đối tượng xuất hiện
//   NHAN_MANH (Emphasis, vàng)    — đối tượng đang có trên slide được làm nổi lên khi người nói nhấp
//   CHO      (hiệu ứng chờ)       — tự phát, lặp mãi tới khi rời slide, biên độ nhỏ: nền trôi, đèn quét, hạt sáng bồng bềnh,
//                                   chữ nổi nhẹ, sóng chữ… — giữ mắt người xem ở lại slide mà không giành lời người nói
//   KET_THUC (Exit, đỏ)           — đối tượng rời slide (dọn sân khấu trước ý mới, thay nội dung tại chỗ)
// Tài liệu đầy đủ: references/hieu-ung.md
//
// PLAN của một slide (makeslides.applyEffects đọc):
//   { transition, autoFirst,
//     steps: [ [ {n, eff, dir, dur, delay, start:"click"|"with"|"after", byPara, theo:"chu"|"tu", khoang, mau, ti} ], … ],  // mỗi mảng = 1 cú nhấp
//     idle:  [ {n, eff, period, dur, delay, para, batDau:"vao"|"sau"|<số nhóm>, …} ],   // hiệu ứng chờ
//     ket:   [ {n, eff, dir, dur, start} ],                                            // cú nhấp cuối: hiệu ứng kết thúc
//     advanceAfter }
//   eff trong steps/ket tra ở MO_DAU ∪ NHAN_MANH ∪ KET_THUC; eff trong idle tra ở CHO.
//
// Luật cấu trúc (theo MS-OI29500 — PowerPoint báo "cần sửa chữa" nếu sai):
//   - cTn đánh số lại theo thứ tự tài liệu (1 = gốc, 2 = mainSeq).
//   - mỗi hiệu ứng trên cùng một hình nhận grpId riêng (0, 1, 2…); hiện theo đoạn dùng chung một grpId.
//   - bldP chỉ cho p:sp CÓ chữ thật (a:t), mỗi cặp (spid, grpId) một lần; ảnh/hình trơn/bảng không có bldP.
//   - "sau" (after) mở một <p:par> con mới như PowerPoint, không dồn hết vào một par.

const fs = require("fs");
const path = require("path");
const W = 10, H = 5.625;

// ---------------------------------------------------------------- khối dựng XML
let N = 0;
const nid = () => ++N;                       // số tạm, đánh lại ở cuối
const f4 = (v) => (+v).toFixed(4).replace(/\.?0+$/, "") || "0";
const tgt = (sp, p) => (p != null
  ? `<p:tgtEl><p:spTgt spid="${sp}"><p:txEl><p:pRg st="${p}" end="${p}"/></p:txEl></p:spTgt></p:tgtEl>`
  : `<p:tgtEl><p:spTgt spid="${sp}"/></p:tgtEl>`);
function cTn(o = {}) {
  const a = [`id="${nid()}"`];
  if (o.dur != null) a.push(`dur="${o.dur}"`);
  if (o.accel) a.push(`accel="${o.accel}"`);
  if (o.decel) a.push(`decel="${o.decel}"`);
  if (o.autoRev) a.push(`autoRev="1"`);
  if (o.repeat) a.push(`repeatCount="${o.repeat}"`);
  if (o.fill) a.push(`fill="${o.fill}"`);
  const st = o.delay ? `<p:stCondLst><p:cond delay="${Math.round(o.delay)}"/></p:stCondLst>` : "";
  return st ? `<p:cTn ${a.join(" ")}>${st}</p:cTn>` : `<p:cTn ${a.join(" ")}/>`;
}
const names = (...a) => `<p:attrNameLst>${a.map((x) => `<p:attrName>${x}</p:attrName>`).join("")}</p:attrNameLst>`;
const B = {
  set: (sp, p, attr, val, o = {}) =>
    `<p:set><p:cBhvr${o.override ? ' override="childStyle"' : ""}>${cTn({ dur: 1, fill: "hold", ...o })}${tgt(sp, p)}${names(attr)}</p:cBhvr><p:to><p:strVal val="${val}"/></p:to></p:set>`,
  vis: (sp, p, on, o = {}) => B.set(sp, p, "style.visibility", on ? "visible" : "hidden", o),
  // khung hình khoá: kf = [[0..1, giá trị]] — chuỗi là công thức (#ppt_y-0.01), số là fltVal
  anim: (sp, p, attr, kf, o = {}) =>
    `<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base">${cTn({ fill: "hold", ...o })}${tgt(sp, p)}${names(attr)}</p:cBhvr><p:tavLst>${kf
      .map(([t, v]) => `<p:tav tm="${Math.round(t * 100000)}"><p:val>${typeof v === "number" ? `<p:fltVal val="${v}"/>` : `<p:strVal val="${v}"/>`}</p:val></p:tav>`)
      .join("")}</p:tavLst></p:anim>`,
  fx: (sp, p, filter, transition, o = {}) =>
    `<p:animEffect transition="${transition}" filter="${filter}"><p:cBhvr>${cTn(o)}${tgt(sp, p)}</p:cBhvr></p:animEffect>`,
  scale: (sp, p, by, o = {}) =>
    `<p:animScale><p:cBhvr>${cTn({ fill: "hold", ...o })}${tgt(sp, p)}</p:cBhvr><p:by x="${Math.round(by * 1000)}" y="${Math.round(by * 1000)}"/></p:animScale>`,
  rot: (sp, p, deg, o = {}) =>
    `<p:animRot by="${Math.round(deg * 60000)}"><p:cBhvr>${cTn({ fill: "hold", ...o })}${tgt(sp, p)}${names("r")}</p:cBhvr></p:animRot>`,
  // dời tương đối (inch) theo đường thẳng; quỹ đạo tính theo phần khổ slide như PowerPoint
  motion: (sp, p, dx, dy, o = {}) =>
    `<p:animMotion origin="layout" path="M 0 0 L ${f4(dx / W)} ${f4(dy / H)} E" pathEditMode="relative" rAng="0" ptsTypes="AA"><p:cBhvr>${cTn({ fill: "hold", ...o })}${tgt(sp, p)}${names("ppt_x", "ppt_y")}</p:cBhvr><p:rCtr x="0" y="0"/></p:animMotion>`,
  color: (sp, p, attr, c, o = {}) =>
    `<p:animClr clrSpc="rgb" dir="cw"><p:cBhvr${attr === "style.color" ? ' override="childStyle"' : ""}>${cTn({ fill: "hold", ...o })}${tgt(sp, p)}${names(attr)}</p:cBhvr><p:to><a:srgbClr val="${c}"/></p:to></p:animClr>`,
  // "đệm" chu kỳ: giữ nguyên vị trí suốt `dur` để vòng lặp có khoảng nghỉ (không thay đổi gì trên màn hình)
  dem: (sp, dur) => B.anim(sp, null, "ppt_x", [[0, "#ppt_x"], [1, "#ppt_x"]], { dur, fill: "remove" }),
};

// ---------------------------------------------------------------- MỞ ĐẦU (entrance)
const FLY = { up: ["#ppt_x", "1+#ppt_h/2", 4], down: ["#ppt_x", "0-#ppt_h/2", 1], left: ["0-#ppt_w/2", "#ppt_y", 8], right: ["1+#ppt_w/2", "#ppt_y", 2] };
const WIPE = { up: ["up", 1], down: ["down", 4], left: ["left", 8], right: ["right", 2] };
const MO_DAU = {
  appear:   { id: 1, mo: "Hiện ngay", body: (sp, p) => B.vis(sp, p, 1) },
  fade:     { id: 10, mo: "Mờ dần hiện", body: (sp, p, d) => B.vis(sp, p, 1) + B.fx(sp, p, "fade", "in", { dur: d }) },
  fly:      { id: 2, sub: (o) => FLY[o.dir || "up"][2], mo: "Bay vào (dir: up|down|left|right = phía bay tới)",
              body: (sp, p, d, o) => { const [x, y] = FLY[o.dir || "up"]; return B.vis(sp, p, 1) + B.anim(sp, p, "ppt_x", [[0, x], [1, "#ppt_x"]], { dur: d, decel: 30000 }) + B.anim(sp, p, "ppt_y", [[0, y], [1, "#ppt_y"]], { dur: d, decel: 30000 }); } },
  floatUp:  { id: 42, mo: "Nổi lên (mờ + trồi nhẹ từ dưới)", body: (sp, p, d) => B.vis(sp, p, 1) + B.fx(sp, p, "fade", "in", { dur: d }) + B.anim(sp, p, "ppt_y", [[0, "#ppt_y+0.1"], [1, "#ppt_y"]], { dur: d, decel: 100000 }) },
  floatDown:{ id: 47, mo: "Hạ xuống (mờ + trôi nhẹ từ trên)", body: (sp, p, d) => B.vis(sp, p, 1) + B.fx(sp, p, "fade", "in", { dur: d }) + B.anim(sp, p, "ppt_y", [[0, "#ppt_y-0.1"], [1, "#ppt_y"]], { dur: d, decel: 100000 }) },
  zoom:     { id: 53, sub: () => 16, mo: "Phóng từ tâm", body: (sp, p, d) => B.vis(sp, p, 1) + B.anim(sp, p, "ppt_w", [[0, "0"], [1, "#ppt_w"]], { dur: d }) + B.anim(sp, p, "ppt_h", [[0, "0"], [1, "#ppt_h"]], { dur: d }) + B.fx(sp, p, "fade", "in", { dur: d }) },
  expand:   { id: 55, mo: "Nở nhẹ (từ 80% + mờ) — dịu hơn zoom", body: (sp, p, d) => B.vis(sp, p, 1) + B.anim(sp, p, "ppt_w", [[0, "#ppt_w*0.8"], [1, "#ppt_w"]], { dur: d, decel: 100000 }) + B.anim(sp, p, "ppt_h", [[0, "#ppt_h*0.8"], [1, "#ppt_h"]], { dur: d, decel: 100000 }) + B.fx(sp, p, "fade", "in", { dur: d }) },
  wipe:     { id: 22, sub: (o) => WIPE[o.dir || "left"][1], mo: "Lau (dir = phía bắt đầu)", body: (sp, p, d, o) => B.vis(sp, p, 1) + B.fx(sp, p, `wipe(${WIPE[o.dir || "left"][0]})`, "in", { dur: d }) },
  split:    { id: 16, sub: () => 37, mo: "Tách từ giữa ra hai bên", body: (sp, p, d) => B.vis(sp, p, 1) + B.fx(sp, p, "barn(outVertical)", "in", { dur: d }) },
  wheel:    { id: 21, sub: () => 1, mo: "Bánh xe (quét tròn)", body: (sp, p, d) => B.vis(sp, p, 1) + B.fx(sp, p, "wheel(1)", "in", { dur: d }) },
  // chữ hiện dần theo từng chữ cái / từng từ
  typewriter: { id: 1, theo: "chu", khoang: 45, mo: "Gõ chữ — hiện từng chữ cái", body: (sp, p) => B.vis(sp, p, 1) },
  riseWords:  { id: 42, theo: "tu", khoang: 90, mo: "Chữ nổi lên từng từ", body: (sp, p, d) => MO_DAU.floatUp.body(sp, p, d) },
  riseLetters:{ id: 42, theo: "chu", khoang: 25, mo: "Chữ nổi lên từng chữ cái (tiêu đề ngắn)", body: (sp, p, d) => MO_DAU.floatUp.body(sp, p, d) },
};

// ---------------------------------------------------------------- NHẤN MẠNH (emphasis, chạy khi nhấp)
const NHAN_MANH = {
  pulse:     { id: 26, mo: "Nhịp: phóng 110% rồi về", body: (sp, p, d, o) => B.scale(sp, p, o.ti || 110, { dur: Math.round(d / 2), autoRev: 1 }) },
  grow:      { id: 6, mo: "Phóng to và GIỮ (ti: %, mặc định 115)", body: (sp, p, d, o) => B.scale(sp, p, o.ti || 115, { dur: d, decel: 50000 }) },
  fontColor: { id: 3, text: 1, mo: "Đổi màu chữ và giữ (mau)", body: (sp, p, d, o) => B.color(sp, p, "style.color", o.mau || "C9A227", { dur: d }) },
  dim:       { id: 3, text: 1, mo: "Làm nhạt chữ đã nói (mau: màu nhạt) — dồn chú ý sang ý mới", body: (sp, p, d, o) => B.color(sp, p, "style.color", o.mau || "9AA0A6", { dur: d }) },
  fillColor: { id: 1, mo: "Đổi màu nền khối và giữ (mau)", body: (sp, p, d, o) =>
    B.color(sp, p, "fillcolor", o.mau || "C9A227", { dur: d }) + B.set(sp, p, "fill.type", "solid", { dur: d }) + B.set(sp, p, "fill.on", "true", { dur: d }) },
  teeter:    { id: 32, mo: "Lắc nhẹ hai bên", body: (sp, p, d) => { const u = Math.round(d / 8); return [[3, 0, u], [-6, u, 2 * u], [6, 3 * u, 2 * u], [-6, 5 * u, 2 * u], [3, 7 * u, u]].map(([a, dl, du]) => B.rot(sp, p, a, { dur: du, delay: dl })).join(""); } },
  spin:      { id: 8, mo: "Xoay một vòng", body: (sp, p, d) => B.rot(sp, p, 360, { dur: d, accel: 20000, decel: 20000 }) },
  underline: { id: 18, text: 1, mo: "Gạch chân và giữ", body: (sp, p) => B.set(sp, p, "style.textDecorationUnderline", "true", { dur: "indefinite", override: 1 }) },
  bold:      { id: 15, text: 1, mo: "In đậm và giữ", body: (sp, p) => B.set(sp, p, "style.fontWeight", "bold", { dur: "indefinite", override: 1 }) },
};

// ---------------------------------------------------------------- KẾT THÚC (exit)
const hide = (sp, p, d) => B.vis(sp, p, 0, { delay: Math.max(0, d - 1) });
const OUT = { up: ["#ppt_x", "0-#ppt_h/2", 1], down: ["#ppt_x", "1+#ppt_h/2", 4], left: ["0-#ppt_w/2", "#ppt_y", 8], right: ["1+#ppt_w/2", "#ppt_y", 2] };
const KET_THUC = {
  disappear: { id: 1, mo: "Biến mất ngay", body: (sp, p) => B.vis(sp, p, 0) },
  fadeOut:   { id: 10, mo: "Mờ dần rồi tắt", body: (sp, p, d) => B.fx(sp, p, "fade", "out", { dur: d }) + hide(sp, p, d) },
  sinkOut:   { id: 42, mo: "Chìm xuống (mờ + trôi nhẹ xuống)", body: (sp, p, d) => B.fx(sp, p, "fade", "out", { dur: d }) + B.anim(sp, p, "ppt_y", [[0, "#ppt_y"], [1, "#ppt_y+0.1"]], { dur: d, accel: 100000 }) + hide(sp, p, d) },
  riseOut:   { id: 47, mo: "Bay hơi lên (mờ + trôi nhẹ lên)", body: (sp, p, d) => B.fx(sp, p, "fade", "out", { dur: d }) + B.anim(sp, p, "ppt_y", [[0, "#ppt_y"], [1, "#ppt_y-0.1"]], { dur: d, accel: 100000 }) + hide(sp, p, d) },
  flyOut:    { id: 2, sub: (o) => OUT[o.dir || "down"][2], mo: "Bay ra (dir = phía bay đi)", body: (sp, p, d, o) => { const [x, y] = OUT[o.dir || "down"]; return B.anim(sp, p, "ppt_x", [[0, "#ppt_x"], [1, x]], { dur: d, accel: 30000 }) + B.anim(sp, p, "ppt_y", [[0, "#ppt_y"], [1, y]], { dur: d, accel: 30000 }) + hide(sp, p, d); } },
  zoomOut:   { id: 53, sub: () => 32, mo: "Thu về tâm", body: (sp, p, d) => B.anim(sp, p, "ppt_w", [[0, "#ppt_w"], [1, "0"]], { dur: d }) + B.anim(sp, p, "ppt_h", [[0, "#ppt_h"], [1, "0"]], { dur: d }) + B.fx(sp, p, "fade", "out", { dur: d }) + hide(sp, p, d) },
  wipeOut:   { id: 22, sub: (o) => WIPE[o.dir || "right"][1], mo: "Lau đi (dir = phía lau về)", body: (sp, p, d, o) => B.fx(sp, p, `wipe(${WIPE[o.dir || "right"][0]})`, "out", { dur: d }) + hide(sp, p, d) },
  splitOut:  { id: 16, sub: () => 26, mo: "Khép vào giữa", body: (sp, p, d) => B.fx(sp, p, "barn(inVertical)", "out", { dur: d }) + hide(sp, p, d) },
};

// ---------------------------------------------------------------- CHỜ (idle — tự phát, lặp tới hết slide)
// nen: hiệu ứng nền, mặc định chạy NGAY khi vào slide (batDau "vao"); còn lại chạy sau khi nội dung cuối đã hiện.
// period: độ dài một chu kỳ (ms); dur: phần "động" trong chu kỳ; phần còn lại đứng yên → không gây rối mắt.
// bien: biên độ (inch) cho các hiệu ứng dời chỗ.
const ease = { accel: 50000, decel: 50000 };
const CHO = {
  // ----- nền: biên độ lớn nhưng RẤT chậm, đối tượng mờ/nằm dưới chữ
  troi:     { id: 0, cls: "path", nen: 1, period: 24000, mo: "Nền trôi chậm qua lại (texture/ảnh lớn hơn khổ slide — xem nenDong)",
              body: (sp, p, d, T, o) => B.motion(sp, p, o.dx ?? -0.3, o.dy ?? -0.18, { dur: Math.round(T / 2), autoRev: 1, ...ease }) },
  tho:      { id: 6, nen: 1, period: 9000, mo: "Thở: phóng 103–106% rồi thu lại, rất chậm (vầng sáng, khối trang trí)",
              body: (sp, p, d, T, o) => B.scale(sp, p, o.ti || 104, { dur: Math.round(T / 2), autoRev: 1, ...ease }) },
  xoayCham: { id: 8, nen: 1, period: 90000, mo: "Xoay rất chậm (vòng nét đứt, hoạ tiết tròn)", body: (sp, p, d, T, o) => B.rot(sp, p, o.chieu === -1 ? -360 : 360, { dur: T }) },
  quet:     { id: 0, cls: "path", nen: 1, period: 16000, mo: "Đèn quét: dời ngang qua lại (vầng sáng — xem denSanKhau)",
              body: (sp, p, d, T, o) => B.motion(sp, p, o.dx ?? 2.4, o.dy ?? 0, { dur: Math.round(T / 2), autoRev: 1, ...ease }) },
  bong:     { id: 0, cls: "path", nen: 1, period: 7000, mo: "Bồng bềnh: trôi lên xuống nhẹ (hạt sáng — xem hatBui)",
              body: (sp, p, d, T, o) => B.motion(sp, p, o.dx ?? 0, -(o.bien ?? 0.14), { dur: Math.round(T / 2), autoRev: 1, ...ease }) },
  lapLanh:  { id: 6, nen: 1, period: 5000, dur: 900, mo: "Lấp lánh: hạt nhỏ loé to rồi về",
              body: (sp, p, d, T, o) => { const a = d / T / 2, k = o.ti ? o.ti / 100 : 1.8; return ["ppt_w", "ppt_h"].map((at) => B.anim(sp, p, at, [[0, `#${at}`], [a, `#${at}*${k}`], [2 * a, `#${at}`], [1, `#${at}`]], { dur: T })).join(""); } },
  // ----- chữ / vật thể: biên độ nhỏ, có khoảng nghỉ dài
  chuNoi:   { id: 26, period: 6000, dur: 1400, mo: "Chữ nổi lên khẽ rồi lắng xuống",
              body: (sp, p, d, T, o) => { const a = d / T, b = f4((o.bien ?? 0.06) / H); return B.anim(sp, p, "ppt_y", [[0, "#ppt_y"], [a / 2, `#ppt_y-${b}`], [a, "#ppt_y"], [1, "#ppt_y"]], { dur: T }); } },
  songChu:  { id: 26, period: 7000, dur: 700, theo: "chu", khoang: 45, text: 1, mo: "Sóng chữ: từng chữ cái nhấp nhô lần lượt (tiêu đề ngắn)",
              body: (sp, p, d, T, o) => { const a = d / T, b = f4((o.bien ?? 0.05) / H); return B.anim(sp, p, "ppt_y", [[0, "#ppt_y"], [a / 2, `#ppt_y-${b}`], [a, "#ppt_y"], [1, "#ppt_y"]], { dur: T }); } },
  nhip:     { id: 26, period: 8000, dur: 900, mo: "Nhịp: phóng 105% rồi về",
              body: (sp, p, d, T, o) => { const a = d / T, k = (o.ti || 105) / 100; return ["ppt_w", "ppt_h"].map((at) => B.anim(sp, p, at, [[0, `#${at}`], [a / 2, `#${at}*${k}`], [a, `#${at}`], [1, `#${at}`]], { dur: T })).join(""); } },
  nay:      { id: 26, period: 9000, dur: 900, mo: "Nảy hai nhịp",
              body: (sp, p, d, T, o) => { const a = d / T, b = (o.bien ?? 0.12) / H; return B.anim(sp, p, "ppt_y", [[0, "#ppt_y"], [a * 0.3, `#ppt_y-${f4(b)}`], [a * 0.6, "#ppt_y"], [a * 0.8, `#ppt_y-${f4(b / 3)}`], [a, "#ppt_y"], [1, "#ppt_y"]], { dur: T }); } },
  mo:       { id: 9, period: 8000, dur: 2000, mo: "Mờ thoáng rồi rõ lại",
              body: (sp, p, d, T, o) => { const a = d / T; return B.anim(sp, p, "style.opacity", [[0, 1], [a / 2, o.toi ?? 0.45], [a, 1], [1, 1]], { dur: T }); } },
  doiMau:   { id: 19, text: 1, period: 10000, dur: 1200, mo: "Chữ chớp sang màu nhấn rồi về (mau)",
              body: (sp, p, d, T, o) => B.color(sp, p, "style.color", o.mau || o.color || "C9A227", { dur: Math.round(d / 2), autoRev: 1, fill: "remove" }) + B.dem(sp, T) },
  gachChan: { id: 18, text: 1, period: 12000, dur: 1500, mo: "Thoáng gạch chân", body: (sp, p, d, T) => B.set(sp, p, "style.textDecorationUnderline", "true", { dur: d, fill: "remove", override: 1 }) + B.dem(sp, T) },
  inDam:    { id: 15, text: 1, period: 12000, dur: 1500, mo: "Thoáng in đậm", body: (sp, p, d, T) => B.set(sp, p, "style.fontWeight", "bold", { dur: d, fill: "remove", override: 1 }) + B.dem(sp, T) },
  inNghieng:{ id: 16, text: 1, period: 12000, dur: 1500, mo: "Thoáng in nghiêng", body: (sp, p, d, T) => B.set(sp, p, "style.fontStyle", "italic", { dur: d, fill: "remove", override: 1 }) + B.dem(sp, T) },
  rung:     { id: 32, period: 12000, dur: 800, mo: "Lắc khẽ hai bên", body: (sp, p, d, T) => NHAN_MANH.teeter.body(sp, p, d).replace(/fill="hold"/g, 'fill="remove"') + B.dem(sp, T) },
  xoay:     { id: 8, period: 12000, dur: 1200, mo: "Xoay một vòng rồi nghỉ (biểu tượng nhỏ)", body: (sp, p, d, T) => B.rot(sp, p, 360, { dur: d, accel: 30000, decel: 30000, fill: "remove" }) + B.dem(sp, T) },
};

const DUR = { appear: 1, typewriter: 1, disappear: 1 };
const cls = (k) => (MO_DAU[k] ? "entr" : NHAN_MANH[k] ? "emph" : KET_THUC[k] ? "exit" : null);
const catalog = (k) => MO_DAU[k] || NHAN_MANH[k] || KET_THUC[k];
// tên cũ (0.12 trở về trước) vẫn chạy
const ALIAS = {};

// ---------------------------------------------------------------- dựng <p:timing>
// ctx: { paraCount(sp), isText(sp), letters(sp, para) }
function timing(plan, ctx) {
  N = 2;
  const grp = new Map();                       // sp → số grpId kế tiếp
  const builds = [];                           // [sp, grpId, byPara]
  const newGrp = (sp, byPara) => { const g = grp.get(sp) || 0; grp.set(sp, g + 1); if (ctx.isText(sp)) builds.push([sp, g, byPara]); return g; };

  // grpId cấp theo thứ tự thời gian: chờ-đầu-slide → các cú nhấp → chờ-sau → kết thúc
  const pre = new Map();
  (plan.idle || []).forEach((e, i) => { const C = CHO[e.eff]; if (C && (e.batDau != null ? e.batDau : C.nen ? "vao" : "sau") === "vao") pre.set(i, newGrp(e.sp, e.para != null)); });
  // 1) chuẩn hoá các nhóm nhấp; byPara → mỗi đoạn một cú nhấp, chung một grpId
  const groups = [];
  (plan.steps || []).forEach((g, gi) => {
    const bp = g.find((e) => e.byPara);
    if (bp) {
      const gid = newGrp(bp.sp, true), n = ctx.paraCount(bp.sp);
      for (let i = 0; i < n; i++) groups.push({ auto: gi === 0 && plan.autoFirst && i === 0, items: [{ ...bp, para: i, start: "click", grpId: gid }] });
    } else groups.push({ auto: gi === 0 && !!plan.autoFirst, items: g.map((e) => ({ ...e, grpId: newGrp(e.sp, e.para != null) })) });
  });
  // 2) hiệu ứng chờ: "vao" → nhóm tự chạy đầu slide; "sau"/số → cuối nhóm đó
  const idle = (plan.idle || []).map((e, i) => {
    const C = CHO[e.eff];
    if (!C) throw new Error(`Hiệu ứng chờ "${e.eff}" không có. Có: ${Object.keys(CHO).join(", ")}`);
    const bd = e.batDau != null ? e.batDau : C.nen ? "vao" : "sau";
    return { ...e, C, bd, grpId: pre.has(i) ? pre.get(i) : newGrp(e.sp, e.para != null) };
  });
  if (plan.ket && plan.ket.length) groups.push({ auto: false, items: plan.ket.map((e) => ({ ...e, grpId: newGrp(e.sp, e.para != null) })) });
  const vao = idle.filter((e) => e.bd === "vao");
  if (vao.length && !(groups[0] && groups[0].auto)) groups.unshift({ auto: true, items: [], idleOnly: true });
  const last = Math.max(0, groups.length - 1 - (plan.ket && plan.ket.length ? 1 : 0));
  const atGroup = (gi) => idle.filter((e) => (e.bd === "vao" ? gi === 0 : (e.bd === "sau" ? last : Math.min(+e.bd, last)) === gi));

  // 3) XML từng nhóm: các đoạn "with" chung một par; mỗi "after" mở par mới tại thời điểm kết thúc của hiệu ứng trước
  const effNode = (e, nodeType, delay) => {
    const k = ALIAS[e.eff] || e.eff, E = catalog(k);
    if (!E) throw new Error(`Hiệu ứng "${e.eff}" không có. Mở đầu: ${Object.keys(MO_DAU).join(", ")} · Nhấn mạnh: ${Object.keys(NHAN_MANH).join(", ")} · Kết thúc: ${Object.keys(KET_THUC).join(", ")}`);
    const d = DUR[k] || e.dur || (cls(k) === "emph" ? 800 : 600);
    const theo = e.theo !== undefined ? e.theo : E.theo;
    let it = "", spread = 0;
    if (theo && ctx.isText(e.sp)) {
      const gap = e.khoang || E.khoang || 50, nL = ctx.letters(e.sp, e.para, theo);
      spread = gap * Math.max(0, nL - 1);
      it = `<p:iterate type="${theo === "tu" ? "wd" : "lt"}">${d <= 1 ? `<p:tmAbs val="${gap}"/>` : `<p:tmPct val="${Math.round((gap / d) * 100000)}"/>`}</p:iterate>`;
    }
    const xml = `<p:par><p:cTn id="${nid()}" presetID="${E.id}" presetClass="${cls(k)}" presetSubtype="${E.sub ? E.sub(e) : 0}" fill="hold" grpId="${e.grpId}" nodeType="${nodeType}"><p:stCondLst><p:cond delay="${Math.round(delay)}"/></p:stCondLst>${it}<p:childTnLst>${E.body(e.sp, e.para, d, e)}</p:childTnLst></p:cTn></p:par>`;
    return { xml, len: delay + d + spread };
  };
  const idleNode = (e, nodeType, delay) => {
    const C = e.C, T = Math.max(e.period || C.period, (e.dur || C.dur || 0) + 400), d = e.dur || C.dur || T;
    let it = "";
    if (C.theo && ctx.isText(e.sp)) {
      const gap = e.khoang || C.khoang;
      it = `<p:iterate type="${C.theo === "tu" ? "wd" : "lt"}"><p:tmPct val="${Math.max(1, Math.round((gap / T) * 100000))}"/></p:iterate>`;
    }
    return `<p:par><p:cTn id="${nid()}" presetID="${C.id}" presetClass="${C.cls || "emph"}" presetSubtype="0" repeatCount="indefinite" fill="hold" grpId="${e.grpId}" nodeType="${nodeType}"><p:stCondLst><p:cond delay="${Math.round(delay)}"/></p:stCondLst>${it}<p:childTnLst>${C.body(e.sp, e.para, d, T, e)}</p:childTnLst></p:cTn></p:par>`;
  };
  const inner = (start, body) => `<p:par><p:cTn id="${nid()}" fill="hold"><p:stCondLst><p:cond delay="${Math.round(start)}"/></p:stCondLst><p:childTnLst>${body}</p:childTnLst></p:cTn></p:par>`;

  // PowerPoint hiểu "After Previous" = sau khi MỤC ĐỨNG TRƯỚC TRONG DANH SÁCH kết thúc. Hiệu ứng chờ lặp vô hạn không bao giờ
  // kết thúc → mọi mục "after" xếp sau nó sẽ không bao giờ chạy (lỗi 0.13.0: tiêu đề bìa không hiện). Vì vậy:
  //   - nhóm KHÔNG có hiệu ứng chờ: dựng như PowerPoint lưu (mỗi chuỗi "after" một par con);
  //   - nhóm CÓ hiệu ứng chờ: một par duy nhất, mọi mục là "With Previous" với độ trễ tuyệt đối; hiệu ứng chờ xếp CUỐI danh sách.
  const clicks = groups.map((g, gi) => {
    const segs = [];                           // [{start, nodes: []}]
    const id0 = atGroup(gi);
    const flat = id0.length > 0;
    let seg = null, prevEnd = 0, prevStart = 0;
    g.items.forEach((e, i) => {
      const start = i === 0 ? "first" : e.start || "with";
      const begin = i === 0 ? 0 : start === "after" ? prevEnd : prevStart;
      if (flat) {
        if (!seg) { seg = { start: 0, nodes: [] }; segs.push(seg); }
        const nodeType = i === 0 ? (g.auto ? "afterEffect" : "clickEffect") : "withEffect";
        const r = effNode(e, nodeType, begin + (e.delay || 0));
        seg.nodes.push(r.xml);
        prevStart = begin; prevEnd = Math.max(start === "with" ? prevEnd : 0, r.len);
      } else {
        if (i === 0 || start === "after") { seg = { start: begin, nodes: [] }; segs.push(seg); }
        const nodeType = i === 0 ? (g.auto ? "afterEffect" : "clickEffect") : start === "after" ? "afterEffect" : "withEffect";
        const r = effNode(e, nodeType, e.delay || 0);
        seg.nodes.push(r.xml);
        prevStart = seg.start; prevEnd = Math.max(start === "with" ? prevEnd : 0, seg.start + r.len);
      }
    });
    if (flat) {
      if (!segs.length) segs.push({ start: 0, nodes: [] });
      const s0 = segs[0], first = !s0.nodes.length;
      id0.forEach((e, i) => {
        const at = e.bd === "vao" ? e.delay || 0 : prevEnd + (e.delay ?? 1200);
        s0.nodes.push(idleNode(e, first && i === 0 ? (g.auto ? "afterEffect" : "clickEffect") : "withEffect", at));
      });
    }
    const body = segs.map((s) => inner(s.start, s.nodes.join(""))).join("");
    return `<p:par><p:cTn id="${nid()}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>${g.auto ? '<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>' : ""}</p:stCondLst><p:childTnLst>${body}</p:childTnLst></p:cTn></p:par>`;
  }).join("");
  if (!clicks) return "";

  const seen = new Set();
  const bld = builds.filter(([sp, g]) => !seen.has(sp + ":" + g) && seen.add(sp + ":" + g))
    .map(([sp, g, p]) => (p ? `<p:bldP spid="${sp}" grpId="${g}" build="p"/>` : `<p:bldP spid="${sp}" grpId="${g}" animBg="1"/>`)).join("");
  let xml = `<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>${clicks}</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst><p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>${bld ? `<p:bldLst>${bld}</p:bldLst>` : ""}</p:timing>`;
  // đánh số cTn theo thứ tự tài liệu (gốc = 1, mainSeq = 2 — khớp <p:tn val="2"/>)
  let k = 0;
  xml = xml.replace(/<p:cTn id="\d+"/g, () => `<p:cTn id="${++k}"`);
  return xml;
}

// ---------------------------------------------------------------- đọc slide XML
function slideContext(xml) {
  const ids = {};
  for (const m of xml.matchAll(/<p:cNvPr id="(\d+)" name="([^"]*)"/g)) {
    if (ids[m[2]] && ids[m[2]] !== m[1]) throw new Error(`objectName "${m[2]}" bị trùng`);
    ids[m[2]] = m[1];
  }
  const spBlock = (sp) => { const m = xml.match(new RegExp(`<p:sp>\\s*<p:nvSpPr>\\s*<p:cNvPr id="${sp}"[\\s\\S]*?<\\/p:sp>`)); return m ? m[0] : null; };
  const paras = (sp) => { const b = spBlock(sp); return b ? b.match(/<a:p>[\s\S]*?<\/a:p>|<a:p\s[\s\S]*?<\/a:p>/g) || [] : []; };
  const plain = (s) => (s.match(/<a:t>([^<]*)<\/a:t>/g) || []).map((t) => t.slice(5, -6)).join("");
  return {
    ids,
    isText: (sp) => { const b = spBlock(sp); return !!b && !/a14:m|<m:oMath/.test(b) && /<a:t>[^<]*\S[^<]*<\/a:t>/.test(b); },
    paraCount: (sp) => Math.max(1, paras(sp).length),
    letters: (sp, para, theo) => {
      const ps = paras(sp), t = para != null ? plain(ps[para] || "") : ps.map(plain).join(" ");
      return theo === "tu" ? t.split(/\s+/).filter(Boolean).length : [...t].length;
    },
  };
}

// ---------------------------------------------------------------- dựng đối tượng nền động (pptxgenjs)
// Ảnh/texture lớn hơn khổ slide `le` inch mỗi phía rồi trôi chậm → không bao giờ lộ mép.
function nenDong(sl, file, { le = 0.35, name = "nen", period = 24000, dx, dy } = {}) {
  sl.addImage({ path: file, x: -le, y: -le, w: W + 2 * le, h: H + 2 * le, objectName: name, altText: "hoa-tiet:nen-dong" });
  return { n: name, eff: "troi", period, dx: dx ?? -le * 0.85, dy: dy ?? -le * 0.5 };
}

// Ảnh vầng sáng PNG (nền trong suốt) — hinh: "tron" (đèn rọi tròn), "chum" (chùm đèn sân khấu từ trên xuống), "dai" (dải sáng chéo)
async function anhSang(file, { mau = "FFF3D6", hinh = "tron", manh = 0.55, w = 1200, h = 1200 } = {}) {
  const sharp = require("sharp");
  const c = "#" + mau;
  let svg;
  if (hinh === "chum") {
    svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><defs>
      <linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${c}" stop-opacity="${manh}"/><stop offset="0.75" stop-color="${c}" stop-opacity="${manh * 0.35}"/><stop offset="1" stop-color="${c}" stop-opacity="0"/></linearGradient>
      <radialGradient id="r" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="${c}" stop-opacity="${manh * 0.9}"/><stop offset="1" stop-color="${c}" stop-opacity="0"/></radialGradient>
      <filter id="b"><feGaussianBlur stdDeviation="${w / 40}"/></filter></defs>
      <polygon points="${w * 0.42},0 ${w * 0.58},0 ${w * 0.9},${h * 0.86} ${w * 0.1},${h * 0.86}" fill="url(#g)" filter="url(#b)"/>
      <ellipse cx="${w / 2}" cy="${h * 0.86}" rx="${w * 0.42}" ry="${h * 0.09}" fill="url(#r)" filter="url(#b)"/></svg>`;
  } else if (hinh === "dai") {
    svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="${c}" stop-opacity="0"/><stop offset="0.5" stop-color="${c}" stop-opacity="${manh}"/><stop offset="1" stop-color="${c}" stop-opacity="0"/></linearGradient><filter id="b"><feGaussianBlur stdDeviation="${w / 60}"/></filter></defs>
      <rect x="${w * 0.3}" y="-${h * 0.2}" width="${w * 0.4}" height="${h * 1.4}" fill="url(#g)" transform="rotate(18 ${w / 2} ${h / 2})" filter="url(#b)"/></svg>`;
  } else {
    svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><defs><radialGradient id="r" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="${c}" stop-opacity="${manh}"/><stop offset="0.45" stop-color="${c}" stop-opacity="${manh * 0.45}"/><stop offset="1" stop-color="${c}" stop-opacity="0"/></radialGradient></defs><rect width="${w}" height="${h}" fill="url(#r)"/></svg>`;
  }
  fs.mkdirSync(path.dirname(path.resolve(file)), { recursive: true });
  await sharp(Buffer.from(svg)).png().toFile(file);
  return file;
}

// Đèn sân khấu quét chậm: thêm ảnh vầng sáng vào slide, trả về mục idle "quet"
function denSanKhau(sl, file, { x = 1.0, y = -0.2, w = 4.2, h = 4.6, name = "den", dx = 2.4, dy = 0, period = 16000, delay = 0 } = {}) {
  sl.addImage({ path: file, x, y, w, h, objectName: name, altText: "hoa-tiet:anh-sang" });
  return { n: name, eff: "quet", dx, dy, period, delay };
}

// Hạt sáng/bụi lơ lửng: các chấm tròn mờ, mỗi hạt bồng bềnh lệch pha; một số hạt lấp lánh
function hatBui(sl, { so = 10, mau = "FFFFFF", vung = { x: 0.4, y: 0.4, w: W - 0.8, h: H - 0.8 }, co = [0.05, 0.14], trong = [55, 80], seed = 7, name = "hat", lapLanh = 0.3, period = [6000, 11000] } = {}) {
  let s = seed;
  const rnd = () => ((s = (s * 9301 + 49297) % 233280) / 233280);
  const out = [];
  for (let i = 0; i < so; i++) {
    const d = co[0] + rnd() * (co[1] - co[0]);
    const x = vung.x + rnd() * (vung.w - d), y = vung.y + rnd() * (vung.h - d), tr = Math.round(trong[0] + rnd() * (trong[1] - trong[0]));
    sl.addShape("ellipse", { objectName: `${name}${i}`, x, y, w: d, h: d, fill: { color: mau, transparency: tr }, line: { color: mau, transparency: 100 } });
    const T = Math.round(period[0] + rnd() * (period[1] - period[0]));
    out.push(rnd() < lapLanh
      ? { n: `${name}${i}`, eff: "lapLanh", period: T, delay: Math.round(rnd() * T) }
      : { n: `${name}${i}`, eff: "bong", period: T, bien: 0.08 + rnd() * 0.14, dx: (rnd() - 0.5) * 0.12, delay: Math.round(rnd() * T * 0.6) });
  }
  return out;
}

// Vòng nét đứt xoay rất chậm (trang trí góc, quanh số lớn/ảnh tròn)
function vongXoay(sl, { x, y, d = 2.4, mau = "FFFFFF", trong = 70, day = 1.25, name = "vong", period = 90000, chieu = 1, dash = "dash" } = {}) {
  sl.addShape("ellipse", { objectName: name, x, y, w: d, h: d, fill: { color: mau, transparency: 100 }, line: { color: mau, width: day, transparency: trong, dashType: dash } });
  return { n: name, eff: "xoayCham", period, chieu };
}

const moTa = (cat) => Object.fromEntries(Object.entries(cat).map(([k, v]) => [k, v.mo]));
module.exports = {
  timing, slideContext, MO_DAU, NHAN_MANH, KET_THUC, CHO, nenDong, anhSang, denSanKhau, hatBui, vongXoay,
  DANH_MUC: { moDau: moTa(MO_DAU), nhanManh: moTa(NHAN_MANH), cho: moTa(CHO), ketThuc: moTa(KET_THUC) },
};

if (require.main === module) {
  // node hieu_ung.js → in danh mục
  for (const [k, v] of Object.entries(module.exports.DANH_MUC)) { console.log(`\n== ${k}`); for (const [n, m] of Object.entries(v)) console.log(`  ${n.padEnd(12)} ${m}`); }
}
