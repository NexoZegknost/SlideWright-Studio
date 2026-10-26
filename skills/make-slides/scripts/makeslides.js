// makeslides.js — hậu xử lý file .pptx do pptxgenjs tạo:
//   1) chèn hiệu ứng chuyển trang (transition, kể cả Morph) và hiệu ứng xuất hiện/nhấn mạnh (animation)
//   2) nhúng phông (đủ 4 kiểu: thường, đậm, nghiêng, đậm nghiêng) từ assets/fonts
//   3) xuất bản .ppsx (mở là trình chiếu)
//
// Phụ thuộc: jszip (đi kèm pptxgenjs), fonteditor-core; công thức cần thêm mathjax-full@3, mathml2omml, sharp
//   →  npm install fonteditor-core jszip mathjax-full@3 mathml2omml sharp
//
// Dùng:
//   const MS = require("<plugin>/skills/make-slides/scripts/makeslides.js");
//   let buf = await pres.write({ outputType: "nodebuffer" });
//   buf = await MS.applyEffects(buf, PLAN);              // PLAN: xem cuối file
//   buf = await MS.embedFonts(buf, ["Playfair Display", "Montserrat"]);
//   await MS.save(buf, "Slide_ChuDe_18102026");          // ghi .pptx và .ppsx
//
// Quy ước: mọi đối tượng cần hiệu ứng phải có objectName (tên duy nhất trong slide).
// Morph: đối tượng muốn "biến hình" giữa 2 slide liên tiếp đặt objectName bắt đầu bằng "!!" và GIỐNG NHAU ở cả hai slide.

const fs = require("fs");
const path = require("path");
const JSZip = require("jszip");

const FONT_DIR = path.join(__dirname, "..", "assets", "fonts");
const FONT_FILES = JSON.parse(fs.readFileSync(path.join(FONT_DIR, "files.json"), "utf8"));

// ---------------------------------------------------------------- phông chữ
function ttfToEot(buf) {
  const { Font } = require("fonteditor-core");
  const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
  const out = Font.create(ab, { type: "ttf", hinting: true }).write({ type: "eot", toBuffer: true });
  return Buffer.from(out);
}

async function embedFonts(buf, families) {
  const zip = await JSZip.loadAsync(buf);
  let pres = await zip.file("ppt/presentation.xml").async("string");
  let rels = await zip.file("ppt/_rels/presentation.xml.rels").async("string");
  let ct = await zip.file("[Content_Types].xml").async("string");
  if (!ct.includes('Extension="fntdata"'))
    ct = ct.replace("<Types ", "<Types ").replace(/(<Types[^>]*>)/, `$1<Default Extension="fntdata" ContentType="application/x-fontdata"/>`);

  let n = 9000;
  const nodes = [];
  for (const fam of families) {
    const files = FONT_FILES[fam];
    if (!files) throw new Error(`Không có phông "${fam}" trong assets/fonts. Có: ${Object.keys(FONT_FILES).join(", ")}`);
    let node = `<p:embeddedFont><p:font typeface="${fam}"/>`;
    for (const slot of ["regular", "bold", "italic", "boldItalic"]) {
      if (!files[slot]) continue;
      const rid = `rIdFont${++n}`;
      zip.file(`ppt/fonts/font${n}.fntdata`, ttfToEot(fs.readFileSync(path.resolve(FONT_DIR, files[slot]))));
      rels = rels.replace("</Relationships>", `<Relationship Id="${rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/font${n}.fntdata"/></Relationships>`);
      node += `<p:${slot} r:id="${rid}"/>`;
    }
    nodes.push(node + `</p:embeddedFont>`);
  }
  // embeddedFontLst phải đứng sau notesSz (và sau smartTags nếu có), trước custShowLst/photoAlbum/custDataLst/kinsoku/defaultTextStyle
  pres = pres.replace(/<p:embeddedFontLst>[\s\S]*?<\/p:embeddedFontLst>/, "");
  const lst = `<p:embeddedFontLst>${nodes.join("")}</p:embeddedFontLst>`;
  if (/<p:notesSz[^>]*\/>/.test(pres)) pres = pres.replace(/(<p:notesSz[^>]*\/>)/, `$1${lst}`);
  else throw new Error("Không tìm thấy <p:notesSz> trong presentation.xml");
  // cho phép lưu phông khi người dùng sửa và lưu lại trong PowerPoint
  pres = pres.replace(/(<p:presentation\b[^>]*?)\s(?:embedTrueTypeFonts|saveSubsetFonts)="[^"]*"/g, "$1").replace(/(<p:presentation\b[^>]*?)\s(?:embedTrueTypeFonts|saveSubsetFonts)="[^"]*"/g, "$1");
  pres = pres.replace("<p:presentation ", '<p:presentation embedTrueTypeFonts="1" saveSubsetFonts="0" ');

  zip.file("ppt/presentation.xml", pres);
  zip.file("ppt/_rels/presentation.xml.rels", rels);
  zip.file("[Content_Types].xml", ct);
  return zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
}

// ---------------------------------------------------------------- hiệu ứng
let ctn = 0;
const id = () => ++ctn;
const tgt = (sp, para) =>
  `<p:tgtEl><p:spTgt spid="${sp}">${para != null ? `<p:txEl><p:pRg st="${para}" end="${para}"/></p:txEl>` : ""}</p:spTgt></p:tgtEl>`;
const show = (sp, p) =>
  `<p:set><p:cBhvr><p:cTn id="${id()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>${tgt(sp, p)}<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>`;
const anim = (sp, p, attr, from, to, dur, extra = "") =>
  `<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="${id()}" dur="${dur}" fill="hold"${extra}/>${tgt(sp, p)}<p:attrNameLst><p:attrName>${attr}</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:strVal val="${from}"/></p:val></p:tav><p:tav tm="100000"><p:val><p:strVal val="${to}"/></p:val></p:tav></p:tavLst></p:anim>`;
const filt = (sp, p, filter, dur) =>
  `<p:animEffect transition="in" filter="${filter}"><p:cBhvr><p:cTn id="${id()}" dur="${dur}"/>${tgt(sp, p)}</p:cBhvr></p:animEffect>`;

const FLY = { up: ["#ppt_x", "1+#ppt_h/2", 4], down: ["#ppt_x", "0-#ppt_h/2", 1], left: ["0-#ppt_w/2", "#ppt_y", 8], right: ["1+#ppt_w/2", "#ppt_y", 2] };
const WIPE = { up: ["up", 1], down: ["down", 4], left: ["left", 8], right: ["right", 2] };

// Danh mục hiệu ứng. cls: entr (xuất hiện) | emph (nhấn mạnh)
const EFFECTS = {
  appear: { id: 1, cls: "entr", sub: () => 0, body: (sp, p) => show(sp, p) },
  fade: { id: 10, cls: "entr", sub: () => 0, body: (sp, p, d) => show(sp, p) + filt(sp, p, "fade", d) },
  fly: { id: 2, cls: "entr", sub: (o) => FLY[o.dir || "up"][2], body: (sp, p, d, o) => { const [x, y] = FLY[o.dir || "up"]; return show(sp, p) + anim(sp, p, "ppt_x", x, "#ppt_x", d) + anim(sp, p, "ppt_y", y, "#ppt_y", d); } },
  floatUp: { id: 42, cls: "entr", sub: () => 0, body: (sp, p, d) => show(sp, p) + filt(sp, p, "fade", d) + anim(sp, p, "ppt_y", "#ppt_y+0.1", "#ppt_y", d, ' decel="100000"') },
  zoom: { id: 53, cls: "entr", sub: () => 16, body: (sp, p, d) => show(sp, p) + anim(sp, p, "ppt_w", "0", "#ppt_w", d) + anim(sp, p, "ppt_h", "0", "#ppt_h", d) + filt(sp, p, "fade", d) },
  wipe: { id: 22, cls: "entr", sub: (o) => WIPE[o.dir || "left"][1], body: (sp, p, d, o) => show(sp, p) + filt(sp, p, `wipe(${WIPE[o.dir || "left"][0]})`, d) },
  split: { id: 16, cls: "entr", sub: () => 37, body: (sp, p, d) => show(sp, p) + filt(sp, p, "barn(outVertical)", d) },
  wheel: { id: 21, cls: "entr", sub: () => 1, body: (sp, p, d) => show(sp, p) + filt(sp, p, "wheel(1)", d) },
  pulse: { id: 26, cls: "emph", sub: () => 0, body: (sp, p, d) =>
    `<p:animScale><p:cBhvr><p:cTn id="${id()}" dur="${Math.round(d / 2)}" autoRev="1" fill="hold"/>${tgt(sp, p)}</p:cBhvr><p:by x="110000" y="110000"/></p:animScale>` },
};

/*
 steps: mảng các "cú nhấp". Mỗi cú nhấp là mảng hiệu ứng chạy cùng lúc hoặc nối tiếp:
   { n: "objectName", eff: "fly", dir: "up", dur: 600, delay: 0, start: "click"|"with"|"after", byPara: true }
 - start: "click" (mặc định, phần tử đầu của nhóm), "with" (cùng lúc với phần tử trước), "after" (sau phần tử trước)
 - byPara: true → mỗi đoạn văn của hộp chữ hiện lần lượt theo từng cú nhấp (tự tách thành nhiều bước)
 - Nhóm đầu tiên có thể đặt auto: true để tự chạy khi vào slide (không cần nhấp)
*/
function timingXml(steps, paraCount, idle = [], isShape = () => true) {
  ctn = 2;
  // mở rộng byPara thành nhiều bước
  const expanded = [];
  for (const g of steps) {
    const bp = g.find((e) => e.byPara);
    if (bp) {
      for (let i = 0; i < paraCount(bp.sp); i++)
        expanded.push({ auto: g.auto && i === 0, items: [{ ...bp, para: i, start: "click" }] });
    } else expanded.push({ auto: g.auto, items: g });
  }
  if (!expanded.length && idle.length) expanded.push({ auto: true, items: [] });
  const clicks = expanded.map((g, gi) => {
    let t = 0, prevEnd = 0;
    const effs = g.items.map((e, i) => {
      const E = EFFECTS[e.eff];
      if (!E) throw new Error(`Hiệu ứng "${e.eff}" không có. Có: ${Object.keys(EFFECTS).join(", ")}`);
      const dur = e.dur || 600;
      const start = i === 0 ? (g.auto ? "after" : "click") : e.start || "with";
      const begin = start === "after" && i > 0 ? prevEnd : start === "with" ? t : 0;
      const delay = begin + (e.delay || 0);
      t = delay; prevEnd = delay + dur;
      const node = i === 0 ? (g.auto ? "afterEffect" : "clickEffect") : start === "after" ? "afterEffect" : "withEffect";
      return `<p:par><p:cTn id="${id()}" presetID="${E.id}" presetClass="${E.cls}" presetSubtype="${E.sub(e)}" fill="hold"${e.para != null ? ' grpId="0"' : ' grpId="0"'} nodeType="${node}"><p:stCondLst><p:cond delay="${delay}"/></p:stCondLst><p:childTnLst>${E.body(e.sp, e.para, dur, e)}</p:childTnLst></p:cTn></p:par>`;
    }).join("") + (gi === expanded.length - 1 ? idle.map((e) => idleXml(e, prevEnd)).join("") : "");
    return `<p:par><p:cTn id="${id()}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>${g.auto ? '<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>' : ""}</p:stCondLst><p:childTnLst><p:par><p:cTn id="${id()}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>${effs}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>`;
  }).join("");
  // bldLst: mỗi hình có hiệu ứng xuất hiện (trừ hình chỉ nhấn mạnh)
  const blds = new Map();
  // chỉ hình có khung chữ (p:sp) mới có bldP; ảnh, bảng, biểu đồ mà có bldP thì PowerPoint báo lỗi nội dung
  for (const g of expanded) for (const e of g.items) if (EFFECTS[e.eff].cls === "entr" && isShape(e.sp)) blds.set(e.sp, e.para != null ? "p" : "whole");
  const bld = [...blds].map(([sp, b]) => b === "p" ? `<p:bldP spid="${sp}" grpId="0" build="p"/>` : `<p:bldP spid="${sp}" grpId="0" animBg="1"/>`).join("");
  return `<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>${clicks}</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst><p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>${bld ? `<p:bldLst>${bld}</p:bldLst>` : ""}</p:timing>`;
}


// ---------------------------------------------------------------- hiệu ứng chờ (lặp lại trong lúc thuyết trình)
// Mỗi hiệu ứng chờ là một hiệu ứng nhấn mạnh nhỏ, lặp mãi theo chu kỳ `period` (ms) cho đến khi rời slide.
// Đặt trong PLAN[n].idle = [{ n, eff, period, delay, para }]. Bắt đầu sau khi nội dung cuối cùng của slide đã hiện.
const clr = (c) => `<a:srgbClr val="${c}"/>`;
const setStyle = (sp, p, attr, val, dur) =>
  `<p:set><p:cBhvr override="childStyle"><p:cTn id="${id()}" dur="${dur}" fill="remove"/>${tgt(sp, p)}<p:attrNameLst><p:attrName>${attr}</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="${val}"/></p:to></p:set>`;
const IDLE = {
  // chữ: thoáng in đậm / in nghiêng / gạch chân rồi trở lại
  inDam: { id: 15, text: true, body: (sp, p, d) => setStyle(sp, p, "style.fontWeight", "bold", d) },
  inNghieng: { id: 16, text: true, body: (sp, p, d) => setStyle(sp, p, "style.fontStyle", "italic", d) },
  gachChan: { id: 18, text: true, body: (sp, p, d) => setStyle(sp, p, "style.textDecorationUnderline", "true", d) },
  // đổi màu chữ chớp sang màu nhấn rồi về
  doiMau: { id: 19, text: true, body: (sp, p, d, o) =>
    `<p:animClr clrSpc="rgb" dir="cw"><p:cBhvr override="childStyle"><p:cTn id="${id()}" dur="${Math.round(d / 2)}" autoRev="1" fill="remove"/>${tgt(sp, p)}<p:attrNameLst><p:attrName>style.color</p:attrName></p:attrNameLst></p:cBhvr><p:to>${clr(o.color || "C9A227")}</p:to></p:animClr>` },
  // chữ / hình rung nhẹ (lắc trái phải)
  rung: { id: 32, body: (sp, p, d) =>
    `<p:animRot by="180000"><p:cBhvr><p:cTn id="${id()}" dur="${Math.round(d / 8)}" autoRev="1" repeatCount="4000" fill="remove"/>${tgt(sp, p)}<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>` },
  // nảy lên rồi rơi xuống
  nay: { id: 0, body: (sp, p, d) =>
    `<p:animMotion origin="layout" path="M 0 0 L 0 -0.025 E" pathEditMode="relative" ptsTypes=""><p:cBhvr><p:cTn id="${id()}" dur="${Math.round(d / 4)}" decel="100000" autoRev="1" repeatCount="2000" fill="remove"/>${tgt(sp, p)}<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr></p:animMotion>` },
  // phóng nhẹ rồi thu lại (nhịp thở)
  nhip: { id: 26, body: (sp, p, d) =>
    `<p:animScale><p:cBhvr><p:cTn id="${id()}" dur="${Math.round(d / 2)}" autoRev="1" fill="remove"/>${tgt(sp, p)}</p:cBhvr><p:by x="106000" y="106000"/></p:animScale>` },
  // mờ thoáng rồi rõ lại
  mo: { id: 9, body: (sp, p, d) =>
    `<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="${id()}" dur="${Math.round(d / 2)}" autoRev="1" fill="remove"/>${tgt(sp, p)}<p:attrNameLst><p:attrName>style.opacity</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:fltVal val="1"/></p:val></p:tav><p:tav tm="100000"><p:val><p:fltVal val="0.45"/></p:val></p:tav></p:tavLst></p:anim>` },
  // xoay một vòng nhỏ (biểu tượng)
  xoay: { id: 8, body: (sp, p, d) =>
    `<p:animRot by="21600000"><p:cBhvr><p:cTn id="${id()}" dur="${d}" accel="30000" decel="30000" fill="remove"/>${tgt(sp, p)}<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>` },
};
// một hiệu ứng chờ: vùng chứa lặp mãi, mỗi chu kỳ dài `period`, hiệu ứng chạy `dur` ms đầu chu kỳ
function idleXml(e, startAt) {
  const E = IDLE[e.eff];
  if (!E) throw new Error(`Hiệu ứng chờ "${e.eff}" không có. Có: ${Object.keys(IDLE).join(", ")}`);
  const dur = e.dur || 900, period = Math.max(e.period || 8000, dur + 500);
  return `<p:par><p:cTn id="${id()}" presetID="${E.id}" presetClass="emph" presetSubtype="0" repeatCount="indefinite" fill="hold" grpId="1" nodeType="withEffect"><p:stCondLst><p:cond delay="${startAt + (e.delay || 1500)}"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="${id()}" dur="${period}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>${E.body(e.sp, e.para, dur, e)}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>`;
}

// Chuyển trang. spd: slow|med|fast. Morph cần PowerPoint 2019/365; bản cũ tự lùi về Fade.
const TRANSITIONS = {
  none: () => "",
  fade: () => `<p:transition spd="med"><p:fade/></p:transition>`,
  fadeBlack: () => `<p:transition spd="slow"><p:fade thruBlk="1"/></p:transition>`,
  push: (d = "u") => `<p:transition spd="med"><p:push dir="${d}"/></p:transition>`,
  wipe: (d = "r") => `<p:transition spd="med"><p:wipe dir="${d}"/></p:transition>`,
  cover: (d = "l") => `<p:transition spd="med"><p:cover dir="${d}"/></p:transition>`,
  split: () => `<p:transition spd="med"><p:split orient="vert" dir="out"/></p:transition>`,
  zoom: () => `<p:transition spd="med"><p:zoom/></p:transition>`,
  circle: () => `<p:transition spd="med"><p:circle/></p:transition>`,
  morph: () =>
    `<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"><mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159"><p:transition spd="slow" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" p14:dur="1500"><p159:morph option="byObject"/></p:transition></mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>`,
};

/*
 PLAN = {
   1: { transition: "fade", steps: [ [ {n:"title", eff:"zoom"}, {n:"sub", eff:"floatUp", start:"after"} ] ], autoFirst: true },
   2: { transition: ["push","u"], steps: [ [{n:"card0",eff:"fly",dir:"up"},{n:"card0txt",eff:"fly",dir:"up"}], ... ] },
   3: { transition: "morph" },
 }
 transition: tên hoặc [tên, hướng]. autoFirst: nhóm đầu tự chạy khi vào slide.
 advanceAfter: số mili-giây tự chuyển sang slide sau (trình chiếu tự động).
*/
// pptxgenjs chèn <a:pPr> cho mọi run trong một đoạn (khi trộn chữ thường + chữ nhấn) → run sau ghi đè dấu đầu dòng.
// Giữ lại đúng một <a:pPr> đầu đoạn.
function fixParagraphs(xml) {
  return xml.replace(/<a:p>([\s\S]*?)<\/a:p>/g, (m, inner) => {
    let first = true;
    const out = inner.replace(/<a:pPr\b[^>]*\/>|<a:pPr\b[^>]*>[\s\S]*?<\/a:pPr>/g, (pp, off) => {
      if (first && off === 0) { first = false; return pp; }
      first = false; return "";
    });
    return `<a:p>${out}</a:p>`;
  });
}

// ---------------------------------------------------------------- công thức (khối Equation gốc của PowerPoint)
// LaTeX → MathML (MathJax) → OMML (mathml2omml) đặt trong <a14:m> — PowerPoint 2010+ hiển thị và sửa được như Insert › Equation.
// Kèm ảnh dự phòng (mc:Fallback) cho trình xem cũ / LibreOffice, giống cách PowerPoint tự lưu.
// Phụ thuộc: npm install mathjax-full@3 mathml2omml sharp
// Dùng (trước pres.write):  await MS.equation(slide, "A_v = -\\frac{R_C}{r_e}", { x, y, fontSize: 28, color: "0A1931", name: "eq1" })
// applyEffects tự chuyển ảnh giữ chỗ thành khối equation; có thể gắn hiệu ứng theo `name` như mọi đối tượng.
const EQ = new Map();
let MJ = null;
function mathjaxDoc() {
  if (MJ) return MJ;
  const { mathjax } = require("mathjax-full/js/mathjax.js");
  const { TeX } = require("mathjax-full/js/input/tex.js");
  const { SVG } = require("mathjax-full/js/output/svg.js");
  const { liteAdaptor } = require("mathjax-full/js/adaptors/liteAdaptor.js");
  const { RegisterHTMLHandler } = require("mathjax-full/js/handlers/html.js");
  const { AllPackages } = require("mathjax-full/js/input/tex/AllPackages.js");
  const { SerializedMmlVisitor } = require("mathjax-full/js/core/MmlTree/SerializedMmlVisitor.js");
  const { STATE } = require("mathjax-full/js/core/MathItem.js");
  const adaptor = liteAdaptor(); RegisterHTMLHandler(adaptor);
  const doc = mathjax.document("", { InputJax: new TeX({ packages: AllPackages }), OutputJax: new SVG({ fontCache: "none" }) });
  MJ = { doc, adaptor, mml: (tex, display) => new SerializedMmlVisitor().visitTree(doc.convert(tex, { display, end: STATE.CONVERT })) };
  return MJ;
}
const xesc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
function ommlFromTex(tex, { fontSize = 24, color = "000000", bold = false } = {}) {
  const { mml2omml } = require("mathml2omml");
  let o = mml2omml(mathjaxDoc().mml(tex, true));
  const rpr = (italic) => `<a:rPr lang="vi-VN" sz="${Math.round(fontSize * 100)}" b="${bold ? 1 : 0}" i="${italic ? 1 : 0}"><a:solidFill><a:srgbClr val="${color}"/></a:solidFill><a:latin typeface="Cambria Math" panose="02040503050406030204" pitchFamily="18" charset="0"/><a:cs typeface="Cambria Math" panose="02040503050406030204" pitchFamily="18" charset="0"/></a:rPr>`;
  o = o.replace(/\s+xmlns:w="[^"]*"/g, "").replace(/<m:oMath[^>]*>/, "<m:oMath>").replace(/<\/?w:[^>]*>/g, "");
  // a:rPr cho từng run (chữ thường trong \text{} không nghiêng)
  o = o.replace(/<m:r>(<m:rPr>[\s\S]*?<\/m:rPr>)?(?=<m:t)/g, (m, rp) => `<m:r>${rp || ""}${rpr(!(rp && rp.includes("m:nor")))}`);
  // ctrlPr mang màu cho gạch phân số, dấu căn, ngoặc…
  o = o.replace(/<m:ctrlPr\/>/g, `<m:ctrlPr>${rpr(true)}</m:ctrlPr>`);
  o = o.replace(/<m:(\w+)Pr\/>/g, (m, t) => (t === "r" || t === "ctrl" ? m : `<m:${t}Pr><m:ctrlPr>${rpr(true)}</m:ctrlPr></m:${t}Pr>`));
  o = o.replace(/(<m:(f|rad|nary|d|acc|bar|func|eqArr|limLow|limUpp|groupChr|box|borderBox|sPre|sSub|sSup|sSubSup|m)Pr>)([\s\S]*?)(<\/m:\2Pr>)/g,
    (m, a, t, inner, z) => (inner.includes("<m:ctrlPr") ? m : `${a}${inner}<m:ctrlPr>${rpr(true)}</m:ctrlPr>${z}`));
  return o;
}
async function equation(slide, tex, o = {}) {
  const sharp = require("sharp");
  const fontSize = o.fontSize || 24, color = (o.color || "000000").replace("#", "");
  const { doc, adaptor } = mathjaxDoc();
  let svg = adaptor.innerHTML(doc.convert(tex, { display: true, em: 16, ex: 8 }));
  const ex = (a) => parseFloat((svg.match(new RegExp(`${a}="([\\d.]+)ex"`)) || [])[1] || 0);
  const wIn = ex("width") * 0.5 * fontSize / 72, hIn = ex("height") * 0.5 * fontSize / 72;
  const DPI = 300;
  svg = svg.replace(/currentColor/g, "#" + color).replace(/width="[\d.]+ex"/, `width="${Math.ceil(wIn * DPI)}"`).replace(/height="[\d.]+ex"/, `height="${Math.ceil(hIn * DPI)}"`).replace(/style="[^"]*"/, "");
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  const k = EQ.size + 1, name = o.name || `eq${k}`;
  // khung luôn bằng kích thước tự nhiên của công thức (khung lớn hơn làm LibreOffice kéo giãn công thức);
  // o.w / o.h chỉ dùng để căn công thức trong ô: ngang theo o.align, dọc ở giữa
  const w = wIn + 0.1, h = hIn + 0.1;
  const x = (o.x || 0) + (o.w ? (o.align === "center" ? (o.w - w) / 2 : o.align === "right" ? o.w - w : 0) : 0);
  const y = (o.y || 0) + (o.h ? (o.h - h) / 2 : 0);
  EQ.set(String(k), { tex, omml: ommlFromTex(tex, { fontSize, color, bold: o.bold }), align: o.align || "left", fontSize });
  slide.addImage({ data: "image/png;base64," + png.toString("base64"), x, y, w, h, objectName: name, altText: `makeslides-eq:${k}` });
  return { name, w, h };
}
function applyEquations(xml) {
  return xml.replace(/<p:pic>((?:(?!<\/p:pic>)[\s\S])*?descr="makeslides-eq:(\d+)"[\s\S]*?)<\/p:pic>/g, (whole, inner, k) => {
    const e = EQ.get(k);
    if (!e) return whole;
    const [, id, name] = inner.match(/<p:cNvPr id="(\d+)" name="([^"]*)"/);
    const xfrm = (inner.match(/<a:xfrm[\s\S]*?<\/a:xfrm>/) || [""])[0];
    const jc = { left: "left", center: "center", right: "right" }[e.align] || "left";
    const algn = { left: "l", center: "ctr", right: "r" }[e.align] || "l";
    const fallback = whole.replace(/descr="makeslides-eq:\d+"/, `descr="${xesc(e.tex)}"`);
    const sp = `<p:sp><p:nvSpPr><p:cNvPr id="${id}" name="${name}" descr="${xesc(e.tex)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr>${xfrm}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>` +
      `<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="${algn}"/>` +
      `<a14:m><m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><m:oMathParaPr><m:jc m:val="${jc}"/></m:oMathParaPr>${e.omml}</m:oMathPara></a14:m>` +
      `<a:endParaRPr lang="vi-VN" sz="${Math.round(e.fontSize * 100)}"/></a:p></p:txBody></p:sp>`;
    return `<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"><mc:Choice xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main" Requires="a14">${sp}</mc:Choice><mc:Fallback>${fallback}</mc:Fallback></mc:AlternateContent>`;
  });
}

async function applyEffects(buf, PLAN) {
  const zip = await JSZip.loadAsync(buf);
  for (const f of Object.keys(zip.files).filter((f) => /^ppt\/slides\/slide\d+\.xml$/.test(f)))
    zip.file(f, applyEquations(fixParagraphs(await zip.file(f).async("string"))));
  for (const [num, plan] of Object.entries(PLAN)) {
    const p = `ppt/slides/slide${num}.xml`;
    if (!zip.file(p)) throw new Error(`Không có slide ${num}`);
    let xml = await zip.file(p).async("string");
    const ids = {};
    for (const m of xml.matchAll(/<p:cNvPr id="(\d+)" name="([^"]*)"/g)) {
      if (ids[m[2]] && ids[m[2]] !== m[1]) throw new Error(`Slide ${num}: objectName "${m[2]}" bị trùng`);
      ids[m[2]] = m[1];
    }
    const paraCount = (sp) => {
      const re = new RegExp(`<p:cNvPr id="${sp}"[\\s\\S]*?<\\/p:sp>`);
      const m = xml.match(re);
      return m ? (m[0].match(/<a:p>|<a:p /g) || []).length : 1;
    };
    const steps = (plan.steps || []).map((g, gi) => {
      const items = g.map((e) => {
        const sp = ids[e.n];
        if (!sp) throw new Error(`Slide ${num}: không thấy đối tượng "${e.n}". Có: ${Object.keys(ids).join(", ")}`);
        return { ...e, sp };
      });
      items.auto = gi === 0 && plan.autoFirst;
      return items;
    });
    const tr = Array.isArray(plan.transition) ? TRANSITIONS[plan.transition[0]](plan.transition[1]) : (TRANSITIONS[plan.transition || "none"] || (() => { throw new Error(`Chuyển trang "${plan.transition}" không có`); }))();
    let trx = tr;
    if (plan.advanceAfter) {
      // tự chuyển trang sau N mili-giây (trình chiếu tự động)
      if (!trx) trx = `<p:transition spd="med"><p:fade/></p:transition>`;
      trx = trx.replace(/<p:transition(?![^>]*advTm)/g, `<p:transition advTm="${plan.advanceAfter}"`);
    }
    const idle = (plan.idle || []).map((e) => {
      const sp = ids[e.n];
      if (!sp) throw new Error(`Slide ${num}: không thấy đối tượng "${e.n}" cho hiệu ứng chờ`);
      return { ...e, sp };
    });
    const isShape = (sp) => new RegExp(`<p:sp>\\s*<p:nvSpPr>\\s*<p:cNvPr id="${sp}"`).test(xml);
    const extra = trx + (steps.length || idle.length ? timingXml(steps, paraCount, idle, isShape) : "");
    xml = xml.replace(/<p:transition[\s\S]*?<\/p:transition>|<p:transition[^>]*\/>|<p:timing>[\s\S]*?<\/p:timing>/g, "");
    if (!/<\/p:clrMapOvr>/.test(xml)) xml = xml.replace(/(<\/p:cSld>)/, `$1<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>`);
    xml = xml.replace(/<\/p:clrMapOvr>/, `</p:clrMapOvr>${extra}`);
    zip.file(p, xml);
  }
  return zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
}

// Trình chiếu lặp vô hạn, chế độ kiosk (dùng cho bối cảnh trình chiếu tự động; kết hợp advanceAfter ở mọi slide)
async function setLoop(buf, { kiosk = true } = {}) {
  const z = await JSZip.loadAsync(buf);
  let x = await z.file("ppt/presProps.xml").async("string");
  x = x.replace(/<p:showPr[\s\S]*?<\/p:showPr>|<p:showPr[^>]*\/>/, "");
  const show = `<p:showPr loop="1" showNarration="1">${kiosk ? '<p:kiosk/>' : '<p:present/>'}<p:sldAll/></p:showPr>`;
  if (/<p:presentationPr([^>]*)\/>/.test(x)) x = x.replace(/<p:presentationPr([^>]*)\/>/, `<p:presentationPr$1>${show}</p:presentationPr>`);
  else x = x.replace(/(<p:presentationPr[^>]*>)/, `$1${show}`);
  z.file("ppt/presProps.xml", x);
  return z.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
}

// ---------------------------------------------------------------- xuất
async function toPpsx(buf) {
  const z = await JSZip.loadAsync(buf);
  let ct = await z.file("[Content_Types].xml").async("string");
  ct = ct.replace("presentationml.presentation.main+xml", "presentationml.slideshow.main+xml");
  z.file("[Content_Types].xml", ct);
  return z.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
}

// Xoá khai báo [Content_Types] trỏ tới phần không tồn tại (pptxgenjs để lại slideMaster2..N) — PowerPoint có thể báo "cần sửa chữa"
async function cleanPackage(buf) {
  const z = await JSZip.loadAsync(buf);
  let ct = await z.file("[Content_Types].xml").async("string");
  ct = ct.replace(/<Override [^>]*PartName="\/([^"]+)"[^>]*\/>/g, (m, part) => (z.file(part) ? m : ""));
  z.file("[Content_Types].xml", ct);
  return z.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
}

async function save(buf, baseName) {
  buf = await cleanPackage(buf);
  fs.writeFileSync(`${baseName}.pptx`, buf);
  fs.writeFileSync(`${baseName}.ppsx`, await toPpsx(buf));
  return [`${baseName}.pptx`, `${baseName}.ppsx`];
}

// Cài phông vào ~/.fonts để LibreOffice render ảnh kiểm tra đúng phông
function installFontsForPreview(families) {
  const dst = path.join(require("os").homedir(), ".fonts", "makeslides");
  fs.mkdirSync(dst, { recursive: true });
  for (const fam of families) for (const f of Object.values(FONT_FILES[fam] || {})) fs.copyFileSync(path.resolve(FONT_DIR, f), path.join(dst, path.basename(f)));
  try { require("child_process").execSync("fc-cache -f " + dst); } catch (e) {}
}

module.exports = { equation, applyEquations, ommlFromTex, cleanPackage, fixParagraphs, IDLE: Object.keys(IDLE), embedFonts, applyEffects, setLoop, toPpsx, save, installFontsForPreview, EFFECTS: Object.keys(EFFECTS), TRANSITIONS: Object.keys(TRANSITIONS), FONT_FILES };
