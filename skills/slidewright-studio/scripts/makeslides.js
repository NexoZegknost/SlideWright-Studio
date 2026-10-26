// makeslides.js — hậu xử lý file .pptx do pptxgenjs tạo:
//   1) chèn hiệu ứng chuyển trang (transition, kể cả Morph) và hiệu ứng xuất hiện/nhấn mạnh (animation)
//   2) nhúng phông (đủ 4 kiểu: thường, đậm, nghiêng, đậm nghiêng) từ assets/fonts
//   3) xuất bản .ppsx (mở là trình chiếu)
//
// Phụ thuộc: jszip (đi kèm pptxgenjs), fonteditor-core; công thức cần thêm mathjax-full@3, mathml2omml, sharp
//   →  npm install fonteditor-core jszip mathjax-full@3 mathml2omml sharp
//
// Dùng:
//   const MS = require("<plugin>/skills/slidewright-studio/scripts/makeslides.js");
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
// Toàn bộ danh mục hiệu ứng (mở đầu, nhấn mạnh, chờ, kết thúc) và cách dựng <p:timing>: scripts/hieu_ung.js
const HU = require(path.join(__dirname, "hieu_ung.js"));

// Chuyển trang: scripts/chuyen_trang.js (Morph chủ đạo + lướt hiện đại; không dùng kiểu cổ điển)
const CT = require(path.join(__dirname, "chuyen_trang.js"));

/*
 PLAN = {
   1: { transition: "fade", steps: [ [ {n:"title", eff:"zoom"}, {n:"sub", eff:"floatUp", start:"after"} ] ], autoFirst: true },
   2: { transition: ["push","u"], steps: [ [{n:"card0",eff:"fly",dir:"up"},{n:"card0txt",eff:"fly",dir:"up"}], ... ] },
   3: { transition: "morph" },
 }
 transition: tên | [tên, hướng] | { kieu, huong, toc, tuy } — xem chuyen_trang.js. autoFirst: nhóm đầu tự chạy khi vào slide.
 idle: hiệu ứng chờ (tự phát, lặp tới hết slide) — [{n, eff:"quet"|"troi"|"chuNoi"|…, period, batDau:"vao"|"sau"}]
 ket:  cú nhấp cuối với hiệu ứng kết thúc — [{n, eff:"fadeOut"|"sinkOut"|…, start:"with"|"after"}]
 advanceAfter: số mili-giây tự chuyển sang slide sau (trình chiếu tự động).
 Danh mục và luật dùng: scripts/hieu_ung.js (node hieu_ung.js in danh mục), references/hieu-ung.md
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
    let ctx;
    try { ctx = HU.slideContext(xml); } catch (e) { throw new Error(`Slide ${num}: ${e.message}`); }
    const bind = (e, loai) => {
      const sp = ctx.ids[e.n];
      if (!sp) throw new Error(`Slide ${num}: không thấy đối tượng "${e.n}"${loai}. Có: ${Object.keys(ctx.ids).join(", ")}`);
      return { ...e, sp };
    };
    const tl = {
      autoFirst: plan.autoFirst,
      steps: (plan.steps || []).map((g) => g.map((e) => bind(e, ""))),
      idle: (plan.idle || []).map((e) => bind(e, " cho hiệu ứng chờ")),
      ket: (plan.ket || []).map((e) => bind(e, " cho hiệu ứng kết thúc")),
    };
    let trx;
    try { trx = CT.xml(plan.transition || "none"); } catch (e) { throw new Error(`Slide ${num}: ${e.message}`); }
    if (plan.advanceAfter) {
      // tự chuyển trang sau N mili-giây (trình chiếu tự động)
      if (!trx) trx = `<p:transition spd="med"><p:fade/></p:transition>`;
      trx = trx.replace(/<p:transition(?![^>]*advTm)/g, `<p:transition advTm="${plan.advanceAfter}"`);
    }
    let tim = "";
    try { tim = HU.timing(tl, ctx); } catch (e) { throw new Error(`Slide ${num}: ${e.message}`); }
    xml = xml.replace(/<p:transition[\s\S]*?<\/p:transition>|<p:transition[^>]*\/>|<p:timing>[\s\S]*?<\/p:timing>/g, "");
    if (!/<\/p:clrMapOvr>/.test(xml)) xml = xml.replace(/(<\/p:cSld>)/, `$1<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>`);
    xml = xml.replace(/<\/p:clrMapOvr>/, `</p:clrMapOvr>${trx + tim}`);
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

module.exports = { equation, applyEquations, ommlFromTex, cleanPackage, fixParagraphs, IDLE: Object.keys(HU.CHO), HIEU_UNG: HU, embedFonts, applyEffects, setLoop, toPpsx, save, installFontsForPreview, EFFECTS: [...Object.keys(HU.MO_DAU), ...Object.keys(HU.NHAN_MANH), ...Object.keys(HU.KET_THUC)], TRANSITIONS: CT.KIEU, CHUYEN_TRANG: CT, FONT_FILES };
